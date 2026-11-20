"""GitHub 공식 트렌딩 수집 (D53): github.com/trending 페이지 HTML에서 저장소·개발자 목록을 읽는다.

공식 API가 없어 페이지를 읽는다.
# shortcut: 정규식 파싱은 2026-11-04 GitHub HTML 기준. 페이지 구조가 바뀌면 0개가 되어 실행이 실패한다
"""
import html
import re

import httpx

from app.errors import ApiError

TRENDING_URL = "https://github.com/trending"
PERIODS = ("daily", "weekly", "monthly")
DEV_PERIODS = ("weekly", "monthly")
DEV_LIMIT = 10

_REPO_ROW = re.compile(r'<article class="Box-row">(.*?)</article>', re.S)
_DEV_ROW = re.compile(r'<article class="Box-row d-flex" id="pa-([^"]+)">(.*?)(?=<article class="Box-row d-flex"|\Z)', re.S)
_REPO_NAME = re.compile(r'<h2 class="h3[^"]*">\s*<a [^>]*href="/([^"/]+/[^"/]+)"')
_DESC = re.compile(r'<p class="col-9[^"]*">(.*?)</p>', re.S)
_LANG = re.compile(r'itemprop="programmingLanguage">(.*?)</span>', re.S)
_STARS = re.compile(r'href="/[^"/]+/[^"/]+/stargazers"[^>]*>.*?</svg>\s*([\d,]+)', re.S)
_GAIN = re.compile(r"([\d,]+) stars (?:today|this week|this month)")
_DEV_RANK = re.compile(r'href="#pa-[^"]+"[^>]*>(\d+)</a>')
_DEV_NAME = re.compile(r'<h1 class="h3 lh-condensed"\s*>\s*<a [^>]*>(.*?)</a>', re.S)
_AVATAR = re.compile(r'<img class="rounded avatar-user" src="([^"]+)"')
_DEV_REPO = re.compile(r'<h1 class="h4 lh-condensed">\s*<a [^>]*href="/([^"/]+/[^"/]+)"', re.S)
_DEV_REPO_DESC = re.compile(r'<div class="f6 color-fg-muted mt-1">(.*?)</div>', re.S)


def get_trending_client() -> httpx.Client:
    return httpx.Client(timeout=30, headers={"User-Agent": "git-trend-for-korean"})


def _text(m: re.Match | None) -> str | None:
    if not m:
        return None
    text = " ".join(html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).split())
    return text or None


def _num(m: re.Match | None) -> int | None:
    return int(m.group(1).replace(",", "")) if m else None


def parse_repos(page: str) -> list[dict]:
    repos = []
    for row in _REPO_ROW.findall(page):
        name = _REPO_NAME.search(row)
        if not name:
            continue
        repos.append({"full_name": name.group(1), "description": _text(_DESC.search(row)),
                      "language": _text(_LANG.search(row)), "stars": _num(_STARS.search(row)),
                      "rank": len(repos) + 1, "gain": _num(_GAIN.search(row))})
    return repos


def parse_developers(page: str) -> list[dict]:
    devs = []
    for login, row in _DEV_ROW.findall(page):
        repo = _DEV_REPO.search(row)
        avatar = _AVATAR.search(row)
        devs.append({"login": login, "name": _text(_DEV_NAME.search(row)) or login,
                     "avatar": html.unescape(avatar.group(1)) if avatar else None,
                     "rank": _num(_DEV_RANK.search(row)) or len(devs) + 1,
                     "repo": repo.group(1) if repo else None,
                     "repo_description": _text(_DEV_REPO_DESC.search(row)) if repo else None})
    return devs


def _get(client: httpx.Client, path: str, since: str, parse) -> list[dict]:
    try:
        r = client.get(f"{TRENDING_URL}{path}", params={"since": since})
        r.raise_for_status()
        items = parse(r.text)
    except httpx.HTTPError as e:
        raise ApiError(502, "TRENDING_UNAVAILABLE", f"GitHub 트렌딩 {path or '/'} {since} 목록을 가져오지 못했습니다",
                       {"type": type(e).__name__}) from e
    if not items:  # 페이지 구조가 바뀌었을 가능성이 크다. 빈 목록을 커밋하면 NEW 판정이 망가진다
        raise ApiError(502, "TRENDING_UNAVAILABLE", f"GitHub 트렌딩 {path or '/'} {since} 목록이 비어 있습니다",
                       {"since": since})
    return items


def fetch_trending(client: httpx.Client) -> dict:
    return {"repos": {p: _get(client, "", p, parse_repos) for p in PERIODS},
            "developers": {p: _get(client, "/developers", p, parse_developers)[:DEV_LIMIT] for p in DEV_PERIODS}}
