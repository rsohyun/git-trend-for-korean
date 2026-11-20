import re
from pathlib import Path

from app.config import get_settings
from app.errors import ApiError

_VERSION = re.compile(r"^[a-z0-9-]+$")


def load_prompt(version: str) -> str:
    path = Path(get_settings().prompts_dir) / f"{version}.md"
    if not _VERSION.match(version) or not path.is_file():
        raise ApiError(422, "PROMPT_NOT_FOUND", f"프롬프트 '{version}'가 없습니다")
    return path.read_text(encoding="utf-8")
