import pytest
from fastapi.testclient import TestClient

TEST_TOKEN = "test-token"


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("AI_WORKER_TOKEN", TEST_TOKEN)
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("VAULT_ROOT", str(tmp_path / "vault"))
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    from app.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client():
    from app.main import app

    return TestClient(app)


@pytest.fixture
def auth():
    return {"X-Internal-Token": TEST_TOKEN}


@pytest.fixture
def fake_llm():
    from app.llm import FakeLLM, get_llm
    from app.main import app

    fake = FakeLLM()
    app.dependency_overrides[get_llm] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_llm, None)


@pytest.fixture(autouse=True)
def sleeps(monkeypatch):
    """요약 간격·한도 대기를 실제로 기다리지 않고 기록만 한다."""
    calls = []
    monkeypatch.setattr("app.gittrend.sleep", calls.append)
    return calls
