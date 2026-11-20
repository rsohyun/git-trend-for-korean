from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


def _protected_app():
    from app.auth import require_token
    from app.errors import ApiError, api_error_handler

    app = FastAPI()
    app.add_exception_handler(ApiError, api_error_handler)

    @app.get("/p", dependencies=[Depends(require_token)])
    def p():
        return {"ok": True}

    return TestClient(app)


def test_health_reports_llm(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "llm": "ok", "version": "0.1.0"}


def test_protected_route_rejects_missing_token():
    r = _protected_app().get("/p")
    assert r.status_code == 401
    assert r.json() == {"error": {"code": "UNAUTHORIZED", "message": "내부 토큰이 없거나 올바르지 않습니다", "detail": {}}}


def test_protected_route_rejects_wrong_token():
    assert _protected_app().get("/p", headers={"X-Internal-Token": "wrong"}).status_code == 401


def test_protected_route_accepts_correct_token(auth):
    r = _protected_app().get("/p", headers=auth)
    assert r.status_code == 200 and r.json() == {"ok": True}
