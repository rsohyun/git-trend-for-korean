from contextlib import contextmanager
from typing import Literal

import pytest
from pydantic import BaseModel, Field

from app.errors import ApiError
from app.llm import FakeLLM, LLMOutputError, complete_json, extract_json
from app.prompts import load_prompt
from app.tracing import NoopTracer


class Out(BaseModel):
    category: Literal["model", "tool"]
    importance: int = Field(ge=1, le=5)


class RecordingTracer:
    def __init__(self):
        self.ended = []

    @contextmanager
    def generation(self, *, name, model, input, metadata=None):
        tracer = self

        class Handle:
            trace_id = "trace-1"

            def end(self, *, output, input_tokens, output_tokens):
                tracer.ended.append((name, metadata, output))

        yield Handle()


def test_extract_json_from_fenced_block_with_prose():
    text = '분석 결과입니다.\n```json\n{"category": "model", "importance": 4}\n```\n이상입니다.'
    assert extract_json(text) == {"category": "model", "importance": 4}


def test_extract_json_from_surrounding_prose():
    assert extract_json('결과: {"a": {"b": 1}} 끝') == {"a": {"b": 1}}


def test_extract_json_rejects_text_without_object():
    with pytest.raises(ValueError):
        extract_json("JSON 없음")


def test_complete_json_returns_validated_value_and_trace():
    llm = FakeLLM(['{"category": "tool", "importance": 2}'])
    tracer = RecordingTracer()
    c = complete_json(llm, "sys", "user", Out, tracer=tracer, name="t")
    assert c.value == Out(category="tool", importance=2)
    assert (c.trace_id, c.attempts) == ("trace-1", 1)
    assert tracer.ended == [("t", {"attempt": 1}, '{"category": "tool", "importance": 2}')]


def test_complete_json_retries_once_with_error_feedback():
    llm = FakeLLM(['{"category": "model", "importance": 6}', '{"category": "model", "importance": 5}'])
    c = complete_json(llm, "sys", "user", Out, tracer=NoopTracer(), name="t")
    assert c.value.importance == 5 and c.attempts == 2
    assert "[이전 응답 오류]" in llm.calls[1][1]


def test_complete_json_raises_after_two_invalid_outputs():
    llm = FakeLLM(["not json", '{"category": "x", "importance": 1}'])
    with pytest.raises(LLMOutputError):
        complete_json(llm, "sys", "user", Out, tracer=NoopTracer(), name="t")


def test_load_prompt_reads_file_and_rejects_unknown():
    assert "one_liner" in load_prompt("repo-detail-v3")
    with pytest.raises(ApiError) as e:
        load_prompt("../secret")
    assert e.value.code == "PROMPT_NOT_FOUND"
