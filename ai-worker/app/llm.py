import json
import re
from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

import openai
from pydantic import BaseModel

from app.config import get_settings
from app.errors import ApiError
from app.tracing import Tracer

T = TypeVar("T", bound=BaseModel)
# LLM 서버 장애: 잠시 후 다시 시도할 문제
LLM_DOWN_ERRORS = (openai.APIConnectionError, openai.APITimeoutError, openai.RateLimitError,
                   openai.InternalServerError)
# 키·권한·모델명·요청 형식 오류: 모든 요청이 똑같이 실패하므로 즉시 중단할 문제
LLM_CONFIG_ERRORS = (openai.AuthenticationError, openai.PermissionDeniedError, openai.NotFoundError,
                     openai.BadRequestError)
_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.S)


@dataclass
class LLMResult:
    text: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class LLMClient(Protocol):
    model: str

    def complete(self, system: str, user: str) -> LLMResult: ...


class OpenAICompatClient:
    def __init__(self, base_url: str, api_key: str, model: str, json_mode: str = "none",
                 timeout: float = 60.0):
        from openai import OpenAI

        # max_retries: 429·5xx·연결 오류를 지수 백오프로 재시도
        self._client = OpenAI(base_url=base_url, api_key=api_key or "none", timeout=timeout, max_retries=3)
        self.model = model
        self._json_mode = json_mode

    def complete(self, system: str, user: str) -> LLMResult:
        kwargs = {"response_format": {"type": "json_object"}} if self._json_mode == "json_object" else {}
        resp = self._client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            **kwargs,
        )
        usage = resp.usage
        return LLMResult(
            text=resp.choices[0].message.content or "",
            model=resp.model or self.model,
            input_tokens=getattr(usage, "prompt_tokens", None),
            output_tokens=getattr(usage, "completion_tokens", None),
        )


class FakeLLM:
    """테스트·smoke용. 큐에 넣은 응답을 순서대로 돌려주고, 비면 프롬프트 종류에 맞는 기본 응답을 준다."""

    model = "fake-llm"

    def __init__(self, responses: list[str] | None = None):
        self._responses = list(responses or [])
        self.calls: list[tuple[str, str]] = []

    def queue(self, *texts: str) -> None:
        self._responses.extend(texts)

    def complete(self, system: str, user: str) -> LLMResult:
        self.calls.append((system, user))
        text = self._responses.pop(0) if self._responses else self._default(system, user)
        return LLMResult(text=text, model=self.model, input_tokens=len(user) // 4, output_tokens=len(text) // 4)

    @staticmethod
    def _default(system: str, user: str = "") -> str:
        if '"headline"' in system:
            groups = re.findall(r"^- ([^:\n]+): ", user, flags=re.M)  # 분야 카드로 쓸 분야
            return json.dumps({"headline": "테스트 헤드라인", "today": "오늘 문장입니다.",
                               "categories": [{"name": g, "summary": f"{g} 한 줄", "detail": f"{g} 설명"}
                                              for g in groups]}, ensure_ascii=False)
        if '"one_liner"' in system:
            return json.dumps({"one_liner": "테스트 저장소", "overview": "테스트용 개요입니다.",
                               "features": ["테스트: 기능 설명"], "cautions": [], "categories": ["테스트"]},
                              ensure_ascii=False)
        return json.dumps({
            "category": "model", "importance": 3, "relevance": 3, "summary_ko": "테스트 요약입니다.",
            "entities": [{"name": "TestModel", "type": "model"}],
        }, ensure_ascii=False)


def get_llm() -> LLMClient:
    s = get_settings()
    if s.llm_provider == "fake":
        return FakeLLM()
    if not (s.llm_base_url and s.llm_model):
        raise ApiError(503, "LLM_NOT_CONFIGURED", "LLM_BASE_URL, LLM_MODEL이 설정되지 않았습니다")
    return OpenAICompatClient(s.llm_base_url, s.llm_api_key, s.llm_model, s.llm_json_mode, s.llm_timeout_s)


def extract_json(text: str) -> dict:
    match = _FENCE.search(text)
    candidate = match.group(1) if match else text
    start, end = candidate.find("{"), candidate.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("응답에서 JSON 객체를 찾을 수 없습니다")
    obj = json.loads(candidate[start:end + 1])
    if not isinstance(obj, dict):
        raise ValueError("JSON 최상위 값이 객체가 아닙니다")
    return obj


class LLMOutputError(Exception):
    pass


@dataclass
class JsonCompletion(Generic[T]):
    value: T
    result: LLMResult
    trace_id: str | None
    attempts: int


def complete_json(llm: LLMClient, system: str, user: str, schema: type[T], *, tracer: Tracer,
                  name: str) -> JsonCompletion[T]:
    prompt = user
    last_error: Exception | None = None
    for attempt in (1, 2):
        with tracer.generation(name=name, model=llm.model, input={"system": system, "user": prompt},
                               metadata={"attempt": attempt}) as gen:
            result = llm.complete(system, prompt)
            gen.end(output=result.text, input_tokens=result.input_tokens, output_tokens=result.output_tokens)
        try:
            value = schema.model_validate(extract_json(result.text))
            return JsonCompletion(value, result, gen.trace_id, attempt)
        except ValueError as e:  # json.JSONDecodeError, pydantic.ValidationError 모두 ValueError
            last_error = e
            prompt = f"{user}\n\n[이전 응답 오류]\n{e}\n스키마에 맞는 JSON 객체 하나만 출력하세요."
    raise LLMOutputError(str(last_error))
