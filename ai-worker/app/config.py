from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).resolve().parents[2]  # 컨테이너: /app, CI: 저장소 루트
_WORKER = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    ai_worker_token: str
    llm_provider: str = "openai_compat"  # openai_compat | fake
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    llm_json_mode: str = "none"  # none | json_object
    llm_timeout_s: float = 60.0
    github_token: str = ""  # 없으면 비인증 요청 (시간당 60회)
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    vault_root: str = str(_ROOT / "vault")
    site_dir: str = str(_ROOT / "site")  # 공개 사이트 출력 위치 (D48)
    site_url: str = ""  # 메일의 사이트 링크. 비면 GitHub로 연결
    prompts_dir: str = str(_WORKER / "prompts")
    templates_dir: str = str(_WORKER / "templates")


@lru_cache
def get_settings() -> Settings:
    return Settings()
