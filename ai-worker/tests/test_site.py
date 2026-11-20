import json
from pathlib import Path

from app.config import get_settings
from app.site import build_site, parse_note

NOTE = """---
repo: acme/rea
language: Python
stars: 2000
summary: "리버스 엔지니어링 </script> MCP"
categories: ["보안", "MCP"]
first_seen: 2099-01-01
last_seen: 2099-01-02
appearances: 2
---
# acme/rea

## 개요
에이전트가 바이너리를 분석합니다.

## 주요 기능
- 디컴파일: Ghidra 연동

## 참고·주의
- README에 명시된 주의사항 없음

## 등장 기록
| 날짜 | Today | Week | Month | ★ |
|---|---|---|---|---|
| 2099-01-01 | 1위 (+7,000) | – | – | 1,000 |
| 2099-01-02 | – | 3위 (+12,000) | 5위 (+40,000) | 2,000 |
"""
ZERO_NOTE = NOTE.split("## 등장 기록")[0].replace("first_seen: 2099-01-01", "first_seen: ").replace(
    "last_seen: 2099-01-02", "last_seen: ").replace("appearances: 2", "appearances: 0") + """## 등장 기록
| 날짜 | Today | Week | Month | ★ |
|---|---|---|---|---|
"""


def test_parse_note_reads_sections_and_history():
    r = parse_note(NOTE)
    assert r["name"] == "acme/rea" and r["categories"] == ["보안", "MCP"] and r["appearances"] == 2
    assert r["features"] == ["디컴파일: Ghidra 연동"] and r["cautions"] == []
    assert r["overview"] == "에이전트가 바이너리를 분석합니다."
    assert r["history"] == [
        {"date": "2099-01-01", "daily": {"rank": 1, "gain": 7000}, "weekly": None, "monthly": None, "stars": 1000},
        {"date": "2099-01-02", "daily": None, "weekly": {"rank": 3, "gain": 12000},
         "monthly": {"rank": 5, "gain": 40000}, "stars": 2000},
    ]


def test_parse_note_empty_seen_dates_are_none():
    r = parse_note(ZERO_NOTE)
    assert r["first_seen"] is None and r["last_seen"] is None and r["appearances"] == 0 and r["history"] == []


def test_build_site_embeds_notes_and_snapshots(tmp_path):
    vault = Path(get_settings().vault_root)
    (vault / "30-Trends/Repos").mkdir(parents=True)
    (vault / "30-Trends/Repos/acme__rea.md").write_text(NOTE, encoding="utf-8")
    (vault / "30-Trends/.trending-days").mkdir(parents=True)
    repo = {"name": "acme/rea", "rank": 1, "gain": 7000, "stars": 1000, "language": "Python", "is_new": True,
            "summary": "x", "categories": []}
    dev = {"login": "pbakaus", "name": "Paul Bakaus", "rank": 1, "avatar": "https://avatars.githubusercontent.com/u/1",
           "repo": "acme/rea", "repo_summary": "x", "is_new": False}
    snap = {"date": "2099-01-01", "collected_at": "2099-01-01T14:20+09:00",
            "repos": {"daily": [repo], "weekly": [], "monthly": []}, "developers": {"weekly": [dev], "monthly": []}}
    (vault / "30-Trends/.trending-days/2099-01-01.json").write_text(json.dumps(snap), encoding="utf-8")
    out = tmp_path / "site"
    assert build_site(out_dir=out)["days"] == 1
    html = (out / "index.html").read_text(encoding="utf-8")
    assert html.count("</script>") == 2  # 요약 속 </script>가 데이터 스크립트를 끊지 않는다
    assert '"2099-01-01"' in html and "리버스 엔지니어링" in html and "noindex" in html
    assert '"pbakaus"' in html and "<title>Github 트렌딩</title>" in html
    assert '<meta property="og:title" content="Github 트렌딩">' in html and "데일리" not in html
    assert "${" in html and "{%" not in html  # 스크립트는 Jinja가 건드리지 않음
    assert (out / "robots.txt").read_text() == "User-agent: *\nDisallow: /\n"
