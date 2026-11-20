---
repo: google/elephant-goldfish-model
url: https://github.com/google/elephant-goldfish-model
language: Python
stars: 20456
summary: "AI 코딩 에이전트를 위한 설계·리뷰 플러그인으로, 프로젝트 컨텍스트를 바탕으로 사양을 초안하고 별도 서브에이전트가 검토해 줍니다."
main_category: "AI 에이전트"
categories: ["AI 에이전트", "개발자 도구", "소프트웨어 설계"]
first_seen: 2026-11-14
last_seen: 2026-11-17
appearances: 4
tags: [ai-trend, repo]
---
# google/elephant-goldfish-model

> AI 코딩 에이전트를 위한 설계·리뷰 플러그인으로, 프로젝트 컨텍스트를 바탕으로 사양을 초안하고 별도 서브에이전트가 검토해 줍니다.

## 개요
Elephant‑Goldfish Model은 AI 코딩 에이전트용 플러그인으로 설계 초안과 리뷰를 자동화합니다. 설계 단계에서 프로젝트 컨텍스트를 활용해 사양을 초안하고, 별도 서브에이전트가 가정·리스크를 찾아냅니다. 플러그인을 설치하고 세션을 시작한 뒤, Brainstorm·Draft·Review 등 스킬을 차례로 실행하면 design_draft.md 등 문서가 생성됩니다. 사용자는 리뷰 결과를 반영해 설계를 확정하고 구현을 진행합니다.

## 주요 기능
- Brainstorm: 아이디어를 탐색하고 개념 요약을 작성합니다.
- Draft: 개념 요약을 설계 문서로 변환하고 단계별 피드백을 받습니다.
- Review: 독립 서브에이전트가 설계 초안을 검토해 가정·리스크를 찾아냅니다.
- Resolve: 리뷰 결과를 반영해 설계를 수정하고 최종안을 확정합니다.
- Bootstrap: 기존 코드베이스에 대한 문서를 자동 생성·업데이트합니다.
- Drift report: 현재 소스와 문서 차이를 비교해 최신 상태를 파악합니다.

## 참고·주의
- 리뷰 기능은 서브에이전트를 생성할 수 있는 환경에서만 동작합니다.
- 공식 Google 제품이 아니며, Apache 2.0 라이선스에 따라 사용합니다.

## 등장 기록
| 날짜 | Today | Week | Month | ★ |
|---|---|---|---|---|
| 2026-11-14 | – | 5위 (+5,560) | – | 18,663 |
| 2026-11-15 | – | 5위 (+5,539) | – | 19,232 |
| 2026-11-16 | – | 9위 (+5,060) | – | 19,831 |
| 2026-11-17 | – | 9위 (+4,249) | – | 20,456 |
