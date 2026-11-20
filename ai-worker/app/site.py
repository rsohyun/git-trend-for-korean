"""공개 사이트 (D48): vault의 저장소 노트와 날짜별 스냅샷을 읽어 site/index.html 하나를 만든다.

데이터는 페이지 안에 JSON으로 넣고, 화면 전환·검색·필터는 브라우저 스크립트가 처리한다.
"""
import json
import re
from pathlib import Path

from app.config import get_settings
from app.gittrend import DAYS_DIR, REPOS_DIR, _env, _note_prop

NO_CAUTION = "README에 명시된 주의사항 없음"  # repo_note.md.j2가 주의사항이 없을 때 쓰는 문구
_ROW = re.compile(r"^\| (\d{4}-\d{2}-\d{2}) \|(.*)$", flags=re.M)
_RANK = re.compile(r"(\d+)위(?: \(\+([\d,]+)\))?")


def _section(text: str, title: str) -> str:
    m = re.search(rf"^## {re.escape(title)}\n(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
    return m.group(1).strip() if m else ""


def _bullets(block: str) -> list[str]:
    return [line[2:].strip() for line in block.splitlines() if line.startswith("- ") and line[2:].strip() != NO_CAUTION]


def _rank(cell: str) -> dict | None:
    m = _RANK.match(cell.strip())
    if not m:
        return None
    return {"rank": int(m.group(1)), "gain": int(m.group(2).replace(",", "")) if m.group(2) else None}


def _date_prop(text: str, key: str) -> str | None:
    """등장 0인 노트는 날짜가 빈 값이다."""
    value = _note_prop(text, key)
    return str(value) if value else None


def parse_note(text: str) -> dict:
    history = []
    for date, rest in _ROW.findall(text):
        cells = [c.strip() for c in rest.strip().strip("|").split("|")]
        if len(cells) < 4:  # gittrend 시기 형식(칸 3개). 전환 때 지웠지만 손으로 되살린 노트 대비
            continue
        stars = cells[3].replace(",", "")
        history.append({"date": date, "daily": _rank(cells[0]), "weekly": _rank(cells[1]),
                        "monthly": _rank(cells[2]), "stars": int(stars) if stars.isdigit() else None})
    return {
        "name": _note_prop(text, "repo"), "language": _note_prop(text, "language") or None,
        "stars": _note_prop(text, "stars"), "summary": _note_prop(text, "summary"),
        "categories": _note_prop(text, "categories") or [],
        "first_seen": _date_prop(text, "first_seen"), "last_seen": _date_prop(text, "last_seen"),
        "appearances": _note_prop(text, "appearances"), "overview": _section(text, "개요"),
        "features": _bullets(_section(text, "주요 기능")), "cautions": _bullets(_section(text, "참고·주의")),
        "history": history,
    }


def site_data(vault: Path) -> dict:
    repos = [parse_note(p.read_text(encoding="utf-8")) for p in sorted((vault / REPOS_DIR).glob("*.md"))]
    days = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted((vault / DAYS_DIR).glob("*.json"))}
    return {"repos": [r for r in repos if r["name"]], "days": days}


def build_site(vault: Path | None = None, out_dir: Path | None = None) -> dict:
    s = get_settings()
    vault = vault or Path(s.vault_root)
    out_dir = out_dir or Path(s.site_dir)
    data = site_data(vault)
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")  # </script>로 스크립트가 끊기지 않게
    html = _env().get_template("site.html.j2").render(data_json=payload, site_url=s.site_url)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8", newline="\n")
    (out_dir / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8", newline="\n")
    return {"repos": len(data["repos"]), "days": len(data["days"]), "bytes": len(html.encode())}
