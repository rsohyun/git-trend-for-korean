---
repo: google-research/harness2
url: https://github.com/google-research/harness2
language: Python
stars: 20409
summary: "Harness²는 모델 가중치를 고정한 채 에이전트의 프롬프트·도구·메모리 등을 재귀적으로 최적화해 주는 프레임워크입니다."
main_category: "AI 에이전트"
categories: ["AI 에이전트", "벤치마크", "개발자 도구"]
first_seen: 
last_seen: 
appearances: 0
tags: [ai-trend, repo]
---
# google-research/harness2

> Harness²는 모델 가중치를 고정한 채 에이전트의 프롬프트·도구·메모리 등을 재귀적으로 최적화해 주는 프레임워크입니다.

## 개요
이 프레임워크는 에이전트가 수행하는 작업에 맞춰 프롬프트와 도구 설정 등을 자동으로 개선합니다. 기존 하니스 설계에 없던 새로운 과제에 직면했을 때도 성능 저하를 최소화하도록 설계되었습니다. 사용자는 Linux에 Python 3.12와 uv를 설치하고 패키지를 설치한 뒤, 원하는 벤치마크를 설정하고 harness2 명령으로 재귀적 정제 과정을 실행하면 결과 보고서를 얻을 수 있습니다. 내부적으로는 제안‑탐색‑합성 단계와 지속적인 개선 하니스를 결합해 작업 수준과 전체 수준의 재귀를 수행합니다.

## 주요 기능
- 재귀적 하니스 정제: Propose–Probe–Compose 단계로 작업별 하니스를 자동 개선
- 하니스 레벨 재귀: 채택된 하니스와 증거 기반 교훈을 저장해 다음 작업에 활용
- 병렬·순차 재귀 모드: 넓게 탐색하거나 깊게 정제하는 두 가지 스케일링 옵션 제공
- 플러그인형 구성 요소: 시스템 프롬프트·가드레일·메모리·도구 가이드·서브에이전트·스킬·스크립트·플러그인 8가지 요소를 자유롭게 편집
- 다중 벤치마크 지원: JobBench, LAB, WorkBuddy‑Bench 등 실제 업무 시나리오에 바로 적용
- 데모 실행 가능: 모델 인증 없이 로컬에서 재귀 모드와 편집기를 체험할 수 있음

## 참고·주의
- Linux와 Python 3.12, uv가 필요합니다.
- 모델 기반 벤치마크는 Google Cloud Vertex AI 인증 및 API 비용이 발생합니다.
- LAB 벤치마크는 Pandoc·Poppler, WorkBuddy‑Bench는 Docker가 필요합니다.
- Codex 실행기는 네트워크 접근이 제한되지 않아 보안에 유의해야 합니다.

## 등장 기록
| 날짜 | Today | Week | Month | ★ |
|---|---|---|---|---|
