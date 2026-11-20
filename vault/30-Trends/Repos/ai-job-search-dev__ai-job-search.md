---
repo: ai-job-search-dev/ai-job-search
url: https://github.com/ai-job-search-dev/ai-job-search
language: Python
stars: 66609
summary: "Claude Code 기반 AI가 구인 공고를 평가하고, 맞춤형 이력서·자소서를 작성해 면접 준비까지 도와주는 로컬 구직 자동화 프레임워크입니다."
main_category: "AI 에이전트"
categories: ["AI 에이전트", "취업 도구", "로컬 AI"]
first_seen: 
last_seen: 
appearances: 0
tags: [ai-trend, repo]
---
# ai-job-search-dev/ai-job-search

> Claude Code 기반 AI가 구인 공고를 평가하고, 맞춤형 이력서·자소서를 작성해 면접 준비까지 도와주는 로컬 구직 자동화 프레임워크입니다.

## 개요
이 도구는 로컬에서 실행되는 AI 구직 어시스턴트로, 프로필을 설정하면 여러 구인 포털을 자동으로 스크랩하고 적합도를 평가합니다. 평가 결과를 바탕으로 LaTeX 기반 맞춤형 이력서와 커버레터를 자동 생성하고, 인터뷰 대비 피드백까지 제공합니다. 사용자는 레포를 포크·클론 후 프로필을 입력하고, `/scrape` 로 채용 정보를 수집한 뒤 `/apply` 로 지원서를 완성하면 됩니다. 내부적으로 Claude Code가 텍스트 생성·평가를 담당하고, 파이프라인은 Python과 Bun 스크립트로 연결됩니다.

## 주요 기능
- 프로필 설정: 문서 폴더 자동 스캔·CV 입력으로 개인 이력 데이터를 손쉽게 구성합니다.
- 구인 포털 스크래핑: 여러 채용 사이트를 검색·중복 제거·적합도 순으로 정렬합니다.
- 맞춤형 지원서 작성: AI가 평가 점수를 기반으로 LaTeX 이력서와 커버레터를 자동 생성합니다.
- 면접 준비 지원: 리뷰 에이전트가 초안에 피드백을 제공하고 수정된 최종 문서를 출력합니다.
- 급여 벤치마킹(옵션): 시장 급여 정보를 참고해 기대 연봉을 제시합니다.

## 참고·주의
- Claude Code 사용을 위해 유료 구독 또는 Anthropic API 크레딧이 필요합니다.
- Python 3.10+, Bun, LaTeX(lualatex·xelatex) 등 여러 의존성을 사전에 설치해야 합니다.
- 프로필 데이터가 Git 추적 파일에 저장되므로 공개 포크 시 개인 정보가 노출될 수 있습니다.

## 등장 기록
| 날짜 | Today | Week | Month | ★ |
|---|---|---|---|---|
