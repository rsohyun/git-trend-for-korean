from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.errors import ApiError, api_error_handler, unhandled_error_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    s = get_settings()
    if s.langfuse_public_key and s.langfuse_secret_key:
        from langfuse import get_client

        get_client().flush()


app = FastAPI(title="ai-worker", version="0.1.0", lifespan=lifespan)
app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)


@app.get("/health")
def health() -> dict:
    s = get_settings()
    llm = "ok" if s.llm_provider == "fake" or (s.llm_base_url and s.llm_model) else "error"
    return {"status": "ok" if llm == "ok" else "degraded", "llm": llm, "version": app.version}


from app import gittrend  # noqa: E402

app.include_router(gittrend.router)
