import json
from datetime import date
from pathlib import Path

import httpx
import pytest

from app.config import get_settings
from app.github import GitHubClient

DETAIL = ('{"one_liner": "리버스 엔지니어링 MCP", "overview": "에이전트가 바이너리를 분석합니다.", '
          '"features": ["디컴파일: Ghidra 연동"], "cautions": ["Node.js 필요"], "categories": ["보안", "MCP"]}')
DAY1, DAY2 = date(2026, 11, 5), date(2026, 11, 6)
_UNIT = {"daily": "today", "weekly": "this week", "monthly": "this month"}


def _repos_html(period: str, items: list[tuple]) -> str:
    """parse_repos가 읽는 부분만 담은 GitHub 트렌딩 저장소 HTML. items: (이름, 증가량, 누적 스타)"""
    return "".join(
        f'<article class="Box-row"><h2 class="h3 lh-condensed"><a href="/{n}" class="Link">{n}</a></h2>'
        f'<p class="col-9 color-fg-muted my-1">{n} 설명</p><span itemprop="programmingLanguage">Python</span>'
        f'<a href="/{n}/stargazers" class="Link"><svg></svg> {stars:,}</a> {gain:,} stars {_UNIT[period]}</article>'
        for n, gain, stars in items)


def _devs_html(items: list[tuple]) -> str:
    """items: (아이디, 대표 저장소, 저장소 설명)"""
    return "".join(
        f'<article class="Box-row d-flex" id="pa-{login}"><a href="#pa-{login}" class="Link">{i}</a>'
        f'<img class="rounded avatar-user" src="https://avatars.githubusercontent.com/{login}?s=96&amp;v=4" />'
        f'<h1 class="h3 lh-condensed"><a href="/{login}" class="Link">{login.title()}</a></h1>'
        f'<article><h1 class="h4 lh-condensed"><a href="/{repo}" class="Link">{repo}</a></h1>'
        f'<div class="f6 color-fg-muted mt-1">{desc}</div></article></article>'
        for i, (login, repo, desc) in enumerate(items, 1))


LISTS = {
    "daily": [("acme/rea", 7000, 1000), ("acme/tv", 4000, 2000)],
    "weekly": [("acme/tv", 37000, 2000), ("acme/weekonly", 13000, 3000)],
    "monthly": [("acme/tv", 90000, 2000)],
}
DEVS = {"weekly": [("alice", "alice/devonly", "앨리스의 대표 저장소")], "monthly": [("bob", "acme/rea", "rea 소개")]}


@pytest.fixture
def fakes():
    from app.github import get_github_client
    from app.main import app
    from app.trending import get_trending_client

    state = {"lists": {k: list(v) for k, v in LISTS.items()}, "devs": dict(DEVS), "status": 200, "readme_calls": []}

    def trending(request):
        if state["status"] != 200:
            return httpx.Response(state["status"])
        since = request.url.params["since"]
        if request.url.path.endswith("/developers"):
            return httpx.Response(200, text=_devs_html(state["devs"][since]))
        return httpx.Response(200, text=_repos_html(since, state["lists"][since]))

    def github(request):
        name = "/".join(request.url.path.split("/")[2:4])
        state["readme_calls"].append(name)
        return httpx.Response(200, text=f"# {name} README") if name != "acme/weekonly" else httpx.Response(404)

    gh = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(github)))
    app.dependency_overrides[get_trending_client] = lambda: httpx.Client(transport=httpx.MockTransport(trending))
    app.dependency_overrides[get_github_client] = lambda: gh
    yield state
    app.dependency_overrides.pop(get_trending_client, None)
    app.dependency_overrides.pop(get_github_client, None)


def _rate_limit_error():
    import openai
    return openai.RateLimitError("quota", response=httpx.Response(429, request=httpx.Request("POST", "http://x")),
                                 body=None)


@pytest.fixture
def on_day(monkeypatch):
    def set_day(d):
        monkeypatch.setattr("app.gittrend.today_kst", lambda: d)
    set_day(DAY1)
    return set_day


def _post(client, auth):
    return client.post("/gittrend/daily", json={}, headers=auth)


def _notes() -> Path:
    return Path(get_settings().vault_root) / "30-Trends/Repos"


def _snap(d) -> dict:
    path = Path(get_settings().vault_root) / f"30-Trends/.trending-days/{d}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_first_run_writes_notes_and_snapshot_without_new_marks(client, auth, fake_llm, fakes, on_day):
    fake_llm.queue(DETAIL)  # 요약 순서: weekly → daily → monthly → 개발자 대표 저장소. 첫 번째는 acme/tv
    body = _post(client, auth).json()
    assert body["date"] == "2026-11-05" and body["repo_count"] == 3 and body["warnings"] == []
    assert body["new_count"] == 0  # 직전 스냅샷이 없으면 NEW 없음
    tv = (_notes() / "acme__tv.md").read_text(encoding="utf-8")
    assert "> 리버스 엔지니어링 MCP" in tv and "appearances: 1\n" in tv
    assert tv.rstrip().endswith("| 2026-11-05 | 2위 (+4,000) | 1위 (+37,000) | 1위 (+90,000) | 2,000 |")
    dev = (_notes() / "alice__devonly.md").read_text(encoding="utf-8")
    assert "appearances: 0\n" in dev and "first_seen: \n" in dev and "| 2026-" not in dev
    assert "소개 문구: acme/tv 설명" in fake_llm.calls[0][1] and "acme/tv README" in fake_llm.calls[0][1]
    assert "소개 문구: 앨리스의 대표 저장소" in fake_llm.calls[-1][1]
    snap = _snap("2026-11-05")
    assert set(snap) == {"date", "collected_at", "repos", "developers"}
    assert [e["name"] for e in snap["repos"]["daily"]] == ["acme/rea", "acme/tv"]
    assert snap["repos"]["weekly"][1] == {"name": "acme/weekonly", "rank": 2, "gain": 13000, "stars": 3000,
                                          "language": "Python", "is_new": False, "summary": "테스트 저장소",
                                          "categories": ["테스트"]}
    assert snap["developers"]["weekly"] == [{"login": "alice", "name": "Alice", "rank": 1,
                                             "avatar": "https://avatars.githubusercontent.com/alice?s=96&v=4",
                                             "repo": "alice/devonly", "repo_summary": "테스트 저장소",
                                             "is_new": False}]
    assert not any(e["is_new"] for p in snap["repos"].values() for e in p)
    html = body["email_html"]
    week_part = html[html.index("📈 This Week"):html.index("🔥 Today")]
    today_part = html[html.index("🔥 Today"):html.index("🆕 새로 정리한")]
    assert week_part.index("acme/tv") < week_part.index("acme/weekonly") and "+37,000" in week_part
    assert today_part.index("acme/rea") < today_part.index("acme/tv") and "acme/weekonly" not in today_part
    assert "GitHub Trending" in html and "gittrend" not in html and "NEW</span>" not in html


def test_next_day_marks_new_per_list(client, auth, fake_llm, fakes, on_day):
    _post(client, auth)
    on_day(DAY2)
    fakes["lists"]["weekly"].append(("acme/rea", 9000, 1100))  # rea는 daily에는 어제도 있었지만 weekly는 처음
    fakes["lists"]["daily"].append(("acme/fresh", 500, 50))
    fakes["devs"]["weekly"] = [("alice", "alice/devonly", "앨리스"), ("carol", "carol/x", "캐럴")]
    body = _post(client, auth).json()
    snap = _snap("2026-11-06")
    new = {p: [e["name"] for e in snap["repos"][p] if e["is_new"]] for p in snap["repos"]}
    assert new == {"daily": ["acme/fresh"], "weekly": ["acme/rea"], "monthly": []}
    assert [d["login"] for d in snap["developers"]["weekly"] if d["is_new"]] == ["carol"]
    assert body["new_count"] == 2
    assert body["email_html"].count("NEW</span>") == 2 and "#FFF8D6" in body["email_html"]


def test_same_day_rerun_keeps_new_and_single_history_row(client, auth, fake_llm, fakes, on_day):
    _post(client, auth)
    on_day(DAY2)
    fakes["lists"]["daily"].append(("acme/fresh", 500, 50))
    _post(client, auth)
    _post(client, auth)
    snap = _snap("2026-11-06")
    assert [e["name"] for e in snap["repos"]["daily"] if e["is_new"]] == ["acme/fresh"]
    tv = (_notes() / "acme__tv.md").read_text(encoding="utf-8")
    assert tv.count("| 2026-11-06 |") == 1 and "appearances: 2\n" in tv and "last_seen: 2026-11-06\n" in tv


def test_existing_note_gets_history_row_without_llm(client, auth, fake_llm, fakes, on_day):
    fake_llm.queue(DETAIL)
    _post(client, auth)
    calls = len(fake_llm.calls)
    on_day(DAY2)
    body = _post(client, auth).json()
    assert len(fake_llm.calls) == calls and body["written"] == []
    assert "리버스 엔지니어링 MCP" in body["email_html"]  # 재등장 저장소도 노트에서 요약을 읽는다


def test_dev_repo_note_counts_once_it_enters_a_repo_list(client, auth, fake_llm, fakes, on_day):
    _post(client, auth)
    on_day(DAY2)
    fakes["lists"]["daily"].append(("alice/devonly", 300, 40))
    _post(client, auth)
    dev = (_notes() / "alice__devonly.md").read_text(encoding="utf-8")
    assert "appearances: 1\n" in dev and "first_seen: 2026-11-06\n" in dev


def test_summary_failure_keeps_repo_with_github_description(client, auth, fake_llm, fakes, on_day):
    fakes["lists"] = {"daily": [("acme/rea", 7000, 1000)], "weekly": [("acme/rea", 9000, 1000)],
                      "monthly": [("acme/rea", 9000, 1000)]}
    fakes["devs"] = {"weekly": [("bob", "acme/rea", "rea")], "monthly": [("bob", "acme/rea", "rea")]}
    fake_llm.queue("이상한 응답", "또 이상한 응답")
    body = _post(client, auth).json()
    assert body["warnings"] == ["acme/rea 요약 실패: LLMOutputError"] and body["written"] == []
    assert not (_notes() / "acme__rea.md").exists()
    assert _snap("2026-11-05")["repos"]["daily"][0]["summary"] == "acme/rea 설명"
    assert _snap("2026-11-05")["developers"]["weekly"][0]["repo_summary"] == "rea"
    assert "acme/rea 설명" in body["email_html"]


def test_mail_links_to_site_when_site_url_set(client, auth, fake_llm, fakes, on_day, monkeypatch):
    monkeypatch.setenv("SITE_URL", "https://example.vercel.app")
    get_settings.cache_clear()
    html = _post(client, auth).json()["email_html"]
    assert 'href="https://example.vercel.app/#/repo/acme/rea"' in html
    assert "https://example.vercel.app/#/day/2026-11-05" in html and "웹에서 보기" in html


def test_unsafe_repo_name_is_skipped(client, auth, fake_llm, fakes, on_day):
    fakes["lists"]["daily"] = [("acme/bad name", 1, 1)] + fakes["lists"]["daily"]
    body = _post(client, auth).json()
    assert "형식 오류" in body["warnings"][0]
    assert "acme/bad name" not in [e["name"] for e in _snap("2026-11-05")["repos"]["daily"]]


def test_trending_failure_returns_502(client, auth, fake_llm, fakes, on_day):
    fakes["status"] = 503
    r = _post(client, auth)
    assert r.status_code == 502 and r.json()["error"]["code"] == "TRENDING_UNAVAILABLE"
    assert not _notes().exists() or not list(_notes().glob("*.md"))


def _merged(**periods):
    base = {"full_name": "acme/rea", "description": "acme/rea 설명", "language": "Python", "stars": 311440,
            "daily": None, "weekly": None, "monthly": None, "detail": json.loads(DETAIL)}
    return base | periods


def test_history_row_has_month_column():
    from app.gittrend import history_row

    repo = _merged(daily={"rank": 3, "gain": 1164}, monthly={"rank": 12, "gain": 20000})
    assert history_row(repo, date(2026, 11, 5)) == "| 2026-11-05 | 3위 (+1,164) | – | 12위 (+20,000) | 311,440 |"


def test_zero_appearance_note_gets_first_seen_on_first_appearance(tmp_path):
    from app.gittrend import _env, record_appearance

    path = tmp_path / "acme__rea.md"
    path.write_text(_env().get_template("repo_note.md.j2").render(r=_merged(), today=date(2026, 11, 4), row=None),
                    encoding="utf-8")
    note = path.read_text(encoding="utf-8")
    assert "appearances: 0\n" in note and "first_seen: \n" in note and "last_seen: \n" in note
    assert note.rstrip().endswith("| 날짜 | Today | Week | Month | ★ |\n|---|---|---|---|---|")
    record_appearance(path, _merged(weekly={"rank": 2, "gain": 900}), date(2026, 11, 5))
    note = path.read_text(encoding="utf-8")
    assert "appearances: 1\n" in note and "first_seen: 2026-11-05\n" in note and "last_seen: 2026-11-05\n" in note
    assert note.rstrip().endswith("| 2026-11-05 | – | 2위 (+900) | – | 311,440 |")


def test_llm_quota_error_skips_remaining_summaries_but_keeps_repos(client, auth, fakes, on_day, sleeps):
    from app.gittrend import RATE_LIMIT_RETRIES, RATE_LIMIT_WAIT_S
    from app.llm import get_llm
    from app.main import app

    class QuotaLLM:
        model = "quota"
        calls = 0

        def complete(self, system, user):
            QuotaLLM.calls += 1
            raise _rate_limit_error()

    app.dependency_overrides[get_llm] = lambda: QuotaLLM()
    try:
        body = _post(client, auth).json()
    finally:
        app.dependency_overrides.pop(get_llm, None)
    # 기다렸다 다시 시도해도 실패하면(하루 한도) 남은 요약은 시도하지 않는다
    assert QuotaLLM.calls == RATE_LIMIT_RETRIES + 1 and body["written"] == []
    assert sleeps.count(RATE_LIMIT_WAIT_S) == RATE_LIMIT_RETRIES
    assert body["warnings"] == ["LLM 연결 실패(RateLimitError): 남은 저장소 요약을 생략했습니다"]
    snap = _snap("2026-11-05")
    assert [e["summary"] for e in snap["repos"]["weekly"]] == ["acme/tv 설명", "acme/weekonly 설명"]
    assert snap["developers"]["weekly"][0]["repo_summary"] == "앨리스의 대표 저장소"
    assert "acme/weekonly 설명" in body["email_html"]
    assert body["email_html"].count("요약 실패, 다음 실행에서 다시 시도") == 4  # tv, weekonly, rea, alice/devonly


def test_rate_limit_waits_and_retries_then_summarizes_all(client, auth, fakes, on_day, sleeps):
    from app.gittrend import RATE_LIMIT_WAIT_S, SUMMARY_INTERVAL_S
    from app.llm import FakeLLM, get_llm
    from app.main import app

    class PerMinuteLLM(FakeLLM):  # 첫 호출만 분당 한도에 걸린다
        def complete(self, system, user):
            if not self.calls:
                self.calls.append((system, user))
                raise _rate_limit_error()
            return super().complete(system, user)

    llm = PerMinuteLLM()
    app.dependency_overrides[get_llm] = lambda: llm
    try:
        body = _post(client, auth).json()
    finally:
        app.dependency_overrides.pop(get_llm, None)
    assert body["warnings"] == [] and len(body["written"]) == 4  # tv, weekonly, rea, alice/devonly
    assert sleeps.count(RATE_LIMIT_WAIT_S) == 1
    assert sleeps.count(SUMMARY_INTERVAL_S) == len(body["written"]) - 1  # 요약 사이마다 한 번씩
