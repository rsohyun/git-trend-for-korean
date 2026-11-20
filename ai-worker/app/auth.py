import hmac

from fastapi import Header

from app.config import get_settings
from app.errors import ApiError


def require_token(x_internal_token: str | None = Header(default=None)) -> None:
    expected = get_settings().ai_worker_token
    if not x_internal_token or not hmac.compare_digest(x_internal_token, expected):
        raise ApiError(401, "UNAUTHORIZED", "내부 토큰이 없거나 올바르지 않습니다")
