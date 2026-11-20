from contextlib import contextmanager
from typing import Iterator, Protocol

from app.config import get_settings


class GenerationHandle(Protocol):
    trace_id: str | None

    def end(self, *, output: str, input_tokens: int | None, output_tokens: int | None) -> None: ...


class Tracer(Protocol):
    def generation(self, *, name: str, model: str, input: dict,
                   metadata: dict | None = None) -> Iterator[GenerationHandle]: ...


class _NoopHandle:
    trace_id = None

    def end(self, *, output, input_tokens, output_tokens) -> None:
        pass


class NoopTracer:
    @contextmanager
    def generation(self, *, name, model, input, metadata=None):
        yield _NoopHandle()


class _LangfuseHandle:
    def __init__(self, observation, trace_id):
        self._observation = observation
        self.trace_id = trace_id

    def end(self, *, output, input_tokens, output_tokens) -> None:
        self._observation.update(
            output=output, usage_details={"input": input_tokens or 0, "output": output_tokens or 0}
        )


class LangfuseTracer:
    """langfuse v3 SDK. LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY / LANGFUSE_HOST 환경변수를 읽는다."""

    def __init__(self):
        from langfuse import get_client

        self._client = get_client()

    @contextmanager
    def generation(self, *, name, model, input, metadata=None):
        with self._client.start_as_current_generation(
            name=name, model=model, input=input, metadata=metadata or {}
        ) as observation:
            yield _LangfuseHandle(observation, self._client.get_current_trace_id())


def get_tracer() -> Tracer:
    s = get_settings()
    if s.langfuse_public_key and s.langfuse_secret_key:
        return LangfuseTracer()
    return NoopTracer()
