"""일간 GitHub 트렌딩 알림 (D38, D53): GitHub 공식 트렌딩 저장소·개발자 목록을 노트·스냅샷·메일로 정리한다.

처음 보는 저장소만 README를 요약해 노트를 만들고, 이미 노트가 있는 저장소는 등장 기록에 한 줄만 추가한다 (D40).
"""
import json
import re
from datetime import datetime
from pathlib import Path
from time import sleep

import httpx
import openai
from fastapi import APIRouter, Depends
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field

from app.auth import require_token
from app.config import get_settings
from app.github import GitHubClient, get_github_client
from app.llm import LLM_CONFIG_ERRORS, LLM_DOWN_ERRORS, LLMClient, complete_json, get_llm
from app.prompts import load_prompt
from app.timeutil import KST, today_kst
from app.tracing import Tracer, get_tracer
from app.trending import DEV_PERIODS, PERIODS, fetch_trending, get_trending_client

SUMMARY_ORDER = ("weekly", "daily", "monthly")  # 무료 한도에 걸리면 사이트 기본 탭(This week)이 먼저 요약되게
SUMMARY_PROMPT = "repo-detail-v3"
MAX_README_CHARS = 8000
# Gemini 무료 등급은 분당 요청 수 한도가 있다. 요약 사이를 띄우고, 걸리면 1분 넘게 기다렸다 다시 시도한다.
# 다시 시도해도 걸리면 하루 한도로 보고 남은 요약을 다음 실행으로 넘긴다
SUMMARY_INTERVAL_S = 10
RATE_LIMIT_WAIT_S = 70
RATE_LIMIT_RETRIES = 2
REPOS_DIR = "30-Trends/Repos"
DAYS_DIR = "30-Trends/.trending-days"  # 날짜별 목록 스냅샷, 사이트 날짜별 화면의 원본 (D49)
_SAFE_NAME = re.compile(r"^[A-Za-z0-9-]+/[A-Za-z0-9._-]+$")  # 외부 값으로 파일 경로를 만들기 때문에 검사

router = APIRouter(dependencies=[Depends(require_token)])


class RepoDetail(BaseModel):
    one_liner: str = Field(min_length=1, max_length=300)
    overview: str = Field(min_length=1, max_length=1500)
    features: list[str] = Field(min_length=1, max_length=7)
    cautions: list[str] = Field(default_factory=list, max_length=5)
    categories: list[str] = Field(min_length=1, max_length=3)


def _rank(entry: dict | None) -> str:
    if not entry:
        return "–"
    return f"{entry['rank']}위" + (f" (+{entry['gain']:,})" if entry["gain"] is not None else "")


def _number(value) -> str:
    return "—" if value is None else f"{value:,}"


def history_row(repo: dict, today) -> str:
    return (f"| {today} | {_rank(repo['daily'])} | {_rank(repo['weekly'])} | {_rank(repo['monthly'])} "
            f"| {_number(repo['stars'])} |")


def _env() -> Environment:
    env = Environment(loader=FileSystemLoader(get_settings().templates_dir), trim_blocks=True, lstrip_blocks=True,
                      keep_trailing_newline=True, autoescape=lambda name: name.endswith(".html.j2"))
    env.filters["num"] = _number
    env.filters["rank"] = _rank
    env.filters["yaml"] = lambda value: json.dumps(value, ensure_ascii=False)  # JSON 값은 그대로 YAML 값이 된다
    return env


def _note_prop(text: str, key: str):
    """노트 frontmatter에서 템플릿이 JSON으로 쓴 값(summary, categories)을 읽는다."""
    m = re.search(rf"^{key}: (.+)$", text, flags=re.M)
    try:
        return json.loads(m.group(1)) if m else None
    except ValueError:  # 사람이 노트를 고쳐 JSON이 아니게 된 경우
        return m.group(1)


def merge(repo_lists: dict) -> list[dict]:
    """기간별 목록을 저장소 이름으로 합친다. 순서는 SUMMARY_ORDER(요약 순서)를 따른다."""
    merged: dict[str, dict] = {}
    for period in SUMMARY_ORDER:
        for item in repo_lists[period]:
            repo = merged.setdefault(item["full_name"], {
                "full_name": item["full_name"], "description": item["description"], "language": item["language"],
                "stars": item["stars"], "daily": None, "weekly": None, "monthly": None})
            repo[period] = {"rank": item["rank"], "gain": item["gain"]}
    return list(merged.values())


def _read_note(text: str, repo: dict) -> None:
    repo["summary"] = _note_prop(text, "summary")
    repo["categories"] = _note_prop(text, "categories") or []


def record_appearance(path: Path, repo: dict, today) -> None:
    """등장 기록을 추가하고, 메일에 쓸 요약·카테고리를 노트에서 읽어 repo에 채운다."""
    text = path.read_text(encoding="utf-8")
    _read_note(text, repo)
    if f"\n| {today} |" in text:  # 같은 날 재실행
        return
    text = re.sub(r"^first_seen: *$", f"first_seen: {today}", text, count=1, flags=re.M)  # 등장 0인 노트
    text = re.sub(r"^last_seen: .*$", f"last_seen: {today}", text, count=1, flags=re.M)
    text = re.sub(r"^appearances: (\d+)$", lambda m: f"appearances: {int(m.group(1)) + 1}", text, count=1,
                  flags=re.M)
    if repo["stars"] is not None:
        text = re.sub(r"^stars: .*$", f"stars: {repo['stars']}", text, count=1, flags=re.M)
    # shortcut: 등장 기록 표가 파일 맨 끝에 있다고 가정. 노트를 직접 고쳐 순서가 바뀌면 표 밖에 붙는다
    path.write_text(text.rstrip("\n") + "\n" + history_row(repo, today) + "\n", encoding="utf-8", newline="\n")


def previous_snapshot(days_dir: Path, today) -> dict | None:
    """오늘보다 앞선 날짜 중 가장 최근 스냅샷. NEW 판정 기준."""
    earlier = sorted(p for p in days_dir.glob("*.json") if p.stem < today.isoformat())
    return json.loads(earlier[-1].read_text(encoding="utf-8")) if earlier else None


def write_snapshot(path: Path, repo_lists: dict, dev_lists: dict, today, prev: dict | None) -> dict:
    """NEW를 판정해 각 항목의 is_new에 채우고 그날 목록을 저장한다.

    직전 스냅샷의 같은 목록에 없던 이름이 NEW다. 직전 스냅샷이 없으면(첫날) NEW 없음.
    같은 날 재실행은 덮어쓰되, 앞선 실행에서 NEW였던 항목은 NEW로 남긴다.
    """
    try:
        same_day = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        same_day = None

    def mark(items, group, period, item_key, snap_key):
        before = {e[snap_key] for e in prev[group].get(period, [])} if prev else set()
        was_new = {e[snap_key] for e in same_day[group].get(period, []) if e["is_new"]} if same_day else set()
        for e in items:
            e["is_new"] = (prev is not None and e[item_key] not in before) or e[item_key] in was_new

    for period, items in repo_lists.items():
        mark(items, "repos", period, "full_name", "name")
    for period, items in dev_lists.items():
        mark(items, "developers", period, "login", "login")
    snapshot = {
        "date": today.isoformat(), "collected_at": datetime.now(KST).isoformat(timespec="minutes"),
        "repos": {p: [{"name": r["full_name"], "rank": r["rank"], "gain": r["gain"], "stars": r["stars"],
                       "language": r["language"], "is_new": r["is_new"], "summary": r["summary"] or r["description"],
                       "categories": r["categories"]} for r in items] for p, items in repo_lists.items()},
        "developers": {p: [{k: d[k] for k in ("login", "name", "rank", "avatar", "repo", "repo_summary", "is_new")}
                           for d in items] for p, items in dev_lists.items()},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return snapshot


def _summarize(repo: dict, gh: GitHubClient, llm: LLMClient, tracer: Tracer) -> dict:
    readme = gh.readme(repo["full_name"]) or ""
    user = (f"저장소: {repo['full_name']}\n소개 문구: {repo.get('description') or '(없음)'}\n\n"
            f"README:\n{readme[:MAX_README_CHARS] or '(README 없음)'}")
    c = complete_json(llm, load_prompt(SUMMARY_PROMPT), user, RepoDetail, tracer=tracer, name="repo-detail")
    return c.value.model_dump()


def _summarize_waiting(repo: dict, gh: GitHubClient, llm: LLMClient, tracer: Tracer) -> dict:
    for _ in range(RATE_LIMIT_RETRIES):
        try:
            return _summarize(repo, gh, llm, tracer)
        except openai.RateLimitError:
            sleep(RATE_LIMIT_WAIT_S)
    return _summarize(repo, gh, llm, tracer)


def build_daily(http: httpx.Client, gh: GitHubClient, llm: LLMClient, tracer: Tracer, today) -> dict:
    data = fetch_trending(http)
    repos = merge(data["repos"])
    listed = {r["full_name"] for r in repos}
    for d in (d for p in DEV_PERIODS for d in data["developers"][p]):  # 대표 저장소로만 본 저장소: 노트만, 등장 아님
        if d["repo"] and d["repo"] not in listed:
            listed.add(d["repo"])
            repos.append({"full_name": d["repo"], "description": d["repo_description"], "language": None,
                          "stars": None, "daily": None, "weekly": None, "monthly": None, "dev_only": True})
    vault = Path(get_settings().vault_root)
    notes_dir = vault / REPOS_DIR
    notes_dir.mkdir(parents=True, exist_ok=True)
    env = _env()
    warnings: list[str] = []
    written: list[str] = []
    llm_down = False
    summarized = 0
    for repo in repos:
        repo.update(detail=None, summary=None, categories=[], new_note=False)
        if not _SAFE_NAME.match(repo["full_name"]):
            warnings.append(f"저장소 이름 형식 오류로 건너뜀: {repo['full_name']!r}")
            continue
        path = notes_dir / f"{repo['full_name'].replace('/', '__')}.md"
        if path.exists():
            if repo.get("dev_only"):
                _read_note(path.read_text(encoding="utf-8"), repo)
            else:
                record_appearance(path, repo, today)
            continue
        repo["new_note"] = True
        if llm_down:
            continue
        if summarized:
            sleep(SUMMARY_INTERVAL_S)
        summarized += 1
        try:
            repo["detail"] = _summarize_waiting(repo, gh, llm, tracer)
        except LLM_DOWN_ERRORS + LLM_CONFIG_ERRORS as e:  # 연결·설정 문제는 나머지도 똑같이 실패
            llm_down = True
            warnings.append(f"LLM 연결 실패({type(e).__name__}): 남은 저장소 요약을 생략했습니다")
            continue
        except Exception as e:  # 노트를 만들지 않으면 다음 실행에서 다시 신규로 시도된다
            warnings.append(f"{repo['full_name']} 요약 실패: {type(e).__name__}")
            continue
        repo["summary"] = repo["detail"]["one_liner"]
        repo["categories"] = repo["detail"]["categories"]
        row = None if repo.get("dev_only") else history_row(repo, today)
        path.write_text(env.get_template("repo_note.md.j2").render(r=repo, today=today, row=row),
                        encoding="utf-8", newline="\n")
        written.append(path.relative_to(vault).as_posix())

    by_name = {r["full_name"]: r for r in repos if _SAFE_NAME.match(r["full_name"])}
    repo_lists = {p: [{**by_name[i["full_name"]], "rank": i["rank"], "gain": i["gain"]}
                      for i in data["repos"][p] if i["full_name"] in by_name] for p in PERIODS}
    dev_lists = {p: [{**d, "repo_summary": (by_name.get(d["repo"]) or {}).get("summary") or d["repo_description"]}
                     for d in data["developers"][p]] for p in DEV_PERIODS}
    days_dir = vault / DAYS_DIR
    write_snapshot(days_dir / f"{today}.json", repo_lists, dev_lists, today, previous_snapshot(days_dir, today))
    week_list, today_list = repo_lists["weekly"], repo_lists["daily"]
    new_count = len({r["full_name"] for r in week_list + today_list if r["is_new"]})
    email_html = env.get_template("gittrend_email.html.j2").render(
        week_list=week_list, today_list=today_list, repos=repos, today=today, site_url=get_settings().site_url,
        weekday="월화수목금토일"[today.weekday()], collected_at=datetime.now(KST).strftime("%H:%M"),
        new_count=new_count, warnings=warnings)
    return {"date": today.isoformat(), "repo_count": sum(not r.get("dev_only") for r in repos),
            "new_count": new_count, "written": written, "warnings": warnings, "email_html": email_html}


@router.post("/gittrend/daily")
def gittrend_daily(http: httpx.Client = Depends(get_trending_client), gh: GitHubClient = Depends(get_github_client),
                   llm: LLMClient = Depends(get_llm), tracer: Tracer = Depends(get_tracer)) -> dict:
    return build_daily(http, gh, llm, tracer, today_kst())
