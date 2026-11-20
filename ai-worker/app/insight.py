"""최근 트렌드 인사이트 (D51): 코드가 숫자와 분야 묶음을 만들고, LLM은 그 위에 짧은 문장만 쓴다.

This Week 목록 → 헤드라인 + 분야 카드 3개(한 줄 설명, 펼치면 자세한 설명), Today 목록 → 1~2문장. 호출은 한 번.
"""
from pydantic import BaseModel, Field, model_validator

from app.llm import LLMClient, complete_json
from app.prompts import load_prompt
from app.tracing import Tracer

PROMPT = "week-insight-v3"
CARDS = 3  # 분야 카드 수


class Category(BaseModel):
    name: str = Field(min_length=1)
    summary: str = Field(min_length=1, max_length=80)  # 카드에 보이는 한 줄
    detail: str = Field(min_length=1, max_length=400)  # 펼쳤을 때 보이는 설명


class Insight(BaseModel):
    headline: str = Field(min_length=1, max_length=100)
    categories: list[Category] = Field(min_length=1, max_length=CARDS)
    today: str = Field(min_length=1, max_length=250)


def _schema(names: list[str]) -> type[Insight]:
    """categories는 코드가 고른 분야를 빠짐없이, 이름 그대로 써야 한다. 어기면 검증 실패로 다시 요청한다."""

    class Checked(Insight):
        @model_validator(mode="after")
        def _same_groups(self):
            if sorted(c.name for c in self.categories) != sorted(names):
                raise ValueError(f"categories의 name은 {names}를 하나씩 그대로 써야 합니다")
            return self

    return Checked


def week_stats(week: list[dict]) -> dict:
    return {"count": len(week), "total_gain": sum(r["week"]["gain"] or 0 for r in week),
            "leader": {"name": week[0]["full_name"], "gain": week[0]["week"]["gain"]}}


def top_groups(week: list[dict]) -> list[dict]:
    """대표 카테고리별 저장소(순위 순). 저장소가 많은 분야부터 CARDS개, 카테고리 없는 저장소는 뺀다."""
    groups: dict[str, list[str]] = {}
    for r in week:
        if r["categories"]:
            groups.setdefault(r["categories"][0], []).append(r["full_name"])
    ranked = sorted(groups.items(), key=lambda g: -len(g[1]))[:CARDS]  # 동률은 먼저 나온(순위 높은) 분야
    return [{"name": c, "repos": names} for c, names in ranked]


def _lines(items: list[dict], key: str) -> str:
    return "\n".join(f"{r[key]['rank']}. {r['full_name']} | +{r[key]['gain'] or 0} | "
                     f"{', '.join(r['categories']) or '-'} | {r['summary'] or r['description'] or '-'}" for r in items)


def _user(stats: dict, groups: list[dict], week: list[dict], today_list: list[dict]) -> str:
    leader = stats["leader"]
    return (f"Week 1위: {leader['name']} (+{leader['gain'] or 0})\n\n"
            "분야 카드로 쓸 분야 (분야: 저장소, 순위 순):\n" +
            "\n".join(f"- {g['name']}: {', '.join(g['repos'])}" for g in groups) +
            "\n\nWeek 목록 (순위. 이름 | 최근 7일 스타 증가 | 카테고리 | 요약):\n" + _lines(week, "week") +
            "\n\nToday 목록 (순위. 이름 | 최근 24시간 스타 증가 | 카테고리 | 요약):\n" + _lines(today_list, "today"))


def build_insight(week: list[dict], today_list: list[dict], llm: LLMClient, tracer: Tracer,
                  use_llm: bool = True) -> tuple[dict | None, str | None]:
    """(인사이트, 경고)를 돌려준다. 문장 생성에 실패해도 숫자와 분야 묶음은 남긴다."""
    if not week:
        return None, None
    base = {"stats": week_stats(week), "groups": top_groups(week)}
    if not use_llm or not base["groups"]:
        return base, None  # LLM 연결 실패 경고는 이미 남았다
    try:
        c = complete_json(llm, load_prompt(PROMPT), _user(base["stats"], base["groups"], week, today_list),
                          _schema([g["name"] for g in base["groups"]]), tracer=tracer, name="week-insight")
    except Exception as e:  # 인사이트 때문에 발송·배포가 멈추면 안 된다
        return base, f"최근 7일 인사이트 생성 실패: {type(e).__name__}"
    return base | c.value.model_dump(), None
