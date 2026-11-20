from fastapi import Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str, detail: dict | None = None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.detail = detail or {}


def _body(code: str, message: str, detail: dict) -> dict:
    return {"error": {"code": code, "message": message, "detail": detail}}


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(status_code=exc.status, content=_body(exc.code, exc.message, exc.detail))


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500, content=_body("INTERNAL_ERROR", "예상하지 못한 오류", {"type": type(exc).__name__})
    )
