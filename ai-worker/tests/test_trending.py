from pathlib import Path

import httpx
import pytest

from app.errors import ApiError
from app.trending import fetch_trending, parse_developers, parse_repos

FIX = Path(__file__).parent / "fixtures"
REPOS_HTML = (FIX / "trending_weekly.html").read_text(encoding="utf-8")
DEVS_HTML = (FIX / "trending_developers_monthly.html").read_text(encoding="utf-8")


def _client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_parse_repos_reads_rows_in_page_order():
    repos = parse_repos(REPOS_HTML)
    assert len(repos) == 16
    assert repos[0] == {"full_name": "Nutlope/hallmark",
                        "description": "Anti-AI-slop design skill for Claude Code, Cursor, and Codex.",
                        "language": "CSS", "stars": 46985, "rank": 1, "gain": 8765}
    assert [r["rank"] for r in repos] == list(range(1, 17))


def test_parse_repos_handles_missing_description_and_language():
    by = {r["full_name"]: r for r in parse_repos(REPOS_HTML)}
    assert by["pingdotgg/t3code"]["description"] is None and by["pingdotgg/t3code"]["language"] == "TypeScript"
    assert by["multica-ai/andrej-karpathy-skills"]["language"] is None


def test_parse_developers_reads_profile_and_popular_repo():
    devs = parse_developers(DEVS_HTML)
    assert len(devs) == 25
    assert devs[0]["login"] == "pbakaus" and devs[0]["name"] == "Paul Bakaus" and devs[0]["rank"] == 1
    assert devs[0]["repo"] == "pbakaus/impeccable"
    assert devs[0]["repo_description"].startswith("The design vocabulary")
    assert devs[0]["avatar"] == "https://avatars.githubusercontent.com/u/43004?s=96&v=4"


def test_fetch_trending_requests_five_pages_and_caps_developers():
    seen = []

    def handler(request):
        seen.append(f"{request.url.path}?{request.url.query.decode()}")
        return httpx.Response(200, text=DEVS_HTML if request.url.path.endswith("/developers") else REPOS_HTML)

    data = fetch_trending(_client(handler))
    assert set(data["repos"]) == {"daily", "weekly", "monthly"} and len(data["repos"]["weekly"]) == 16
    assert set(data["developers"]) == {"weekly", "monthly"} and len(data["developers"]["weekly"]) == 10
    assert sorted(seen) == sorted(["/trending?since=daily", "/trending?since=weekly", "/trending?since=monthly",
                                   "/trending/developers?since=weekly", "/trending/developers?since=monthly"])


def test_empty_page_raises():
    with pytest.raises(ApiError) as e:
        fetch_trending(_client(lambda r: httpx.Response(200, text="<html></html>")))
    assert e.value.status == 502 and e.value.code == "TRENDING_UNAVAILABLE"


def test_http_error_raises():
    with pytest.raises(ApiError) as e:
        fetch_trending(_client(lambda r: httpx.Response(503)))
    assert e.value.code == "TRENDING_UNAVAILABLE"


def test_developer_without_popular_repo_does_not_swallow_next_row():
    rows = DEVS_HTML.split('<article class="Box-row d-flex"')
    first = rows[1]
    no_repo = first[:first.index("<article>")] + first[first.index("</article>") + len("</article>"):]
    devs = parse_developers('<article class="Box-row d-flex"' + no_repo + '<article class="Box-row d-flex"' + rows[2])
    assert [d["login"] for d in devs] == ["pbakaus", "morluto"]
    assert devs[0]["repo"] is None and devs[0]["repo_description"] is None and devs[1]["repo"]
