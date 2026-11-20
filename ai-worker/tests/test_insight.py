import json

from app.insight import build_insight, top_groups, week_stats
from app.llm import FakeLLM
from app.tracing import NoopTracer


def _repo(name, rank, gain, cats=("AI 에이전트",), key="week"):
    return {"full_name": name, key: {"rank": rank, "gain": gain}, "language": "Python", "categories": list(cats),
            "summary": f"{name} 요약", "description": None}


WEEK = [_repo("a/one", 1, 40000), _repo("b/two", 2, 12000, ("GPU 최적화",)), _repo("c/three", 3, 9000, ()),
        _repo("d/four", 4, None), _repo("e/five", 5, 100, ("보안",)), _repo("f/six", 6, 50, ("UI 디자인",))]
TODAY = [_repo("t/day", 1, 5000, key="today")]


def test_stats_and_top_three_groups():
    assert week_stats(WEEK) == {"count": 6, "total_gain": 61150, "leader": {"name": "a/one", "gain": 40000}}
    assert top_groups(WEEK) == [{"name": "AI 에이전트", "repos": ["a/one", "d/four"]},
                                {"name": "GPU 최적화", "repos": ["b/two"]}, {"name": "보안", "repos": ["e/five"]}]


def test_build_insight_writes_card_text_for_the_chosen_groups():
    llm = FakeLLM()
    ins, warning = build_insight(WEEK, TODAY, llm, NoopTracer())
    assert warning is None and ins["headline"] == "테스트 헤드라인" and ins["today"] == "오늘 문장입니다."
    assert [c["name"] for c in ins["categories"]] == ["AI 에이전트", "GPU 최적화", "보안"]
    assert ins["groups"] == top_groups(WEEK)
    prompt = llm.calls[0][1]
    assert "- AI 에이전트: a/one, d/four\n- GPU 최적화: b/two\n- 보안: e/five" in prompt
    assert "1. t/day | +5000 | AI 에이전트 | t/day 요약" in prompt


def test_wrong_category_names_are_retried_then_fall_back_to_cards_without_text():
    bad = json.dumps({"headline": "h", "today": "t",
                      "categories": [{"name": "엉뚱한 분야", "summary": "s", "detail": "d"}]}, ensure_ascii=False)
    llm = FakeLLM([bad, bad])
    ins, warning = build_insight(WEEK, TODAY, llm, NoopTracer())
    assert len(llm.calls) == 2 and "categories의 name은" in llm.calls[1][1]
    assert ins == {"stats": week_stats(WEEK), "groups": top_groups(WEEK)}
    assert warning == "최근 7일 인사이트 생성 실패: LLMOutputError"


def test_no_llm_call_when_llm_is_down_or_week_empty():
    llm = FakeLLM()
    assert build_insight(WEEK, TODAY, llm, NoopTracer(), use_llm=False)[0].keys() == {"stats", "groups"}
    assert build_insight([], TODAY, llm, NoopTracer()) == (None, None) and llm.calls == []
