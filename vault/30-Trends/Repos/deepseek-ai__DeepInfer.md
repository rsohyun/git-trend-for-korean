---
repo: deepseek-ai/DeepInfer
url: https://github.com/deepseek-ai/DeepInfer
language: Python
stars: 24223
summary: "DeepInfer는 DeepSeek 모델을 대규모로 고성능 오프라인 추론할 수 있게 해 주는 프레임워크입니다."
main_category: "AI 인프라"
categories: ["AI 인프라", "고성능 컴퓨팅", "머신러닝 프레임워크"]
first_seen: 
last_seen: 
appearances: 0
tags: [ai-trend, repo]
---
# deepseek-ai/DeepInfer

> DeepInfer는 DeepSeek 모델을 대규모로 고성능 오프라인 추론할 수 있게 해 주는 프레임워크입니다.

## 개요
DeepInfer는 DeepSeek‑V4.1‑Flash 모델을 대상으로 대규모 서비스 수준의 추론을 제공하는 프레임워크입니다. 기존 추론 엔진의 지연과 배치 효율 문제를 최적화된 커널과 비동기 스케줄러로 해결합니다. 리눅스 환경에서 GCC·Python·CUDA(또는 Ascend)와 함께 소스 빌드 후, 예제 스크립트를 실행하면 모델이 로드되어 즉시 텍스트를 생성합니다. 배치 구성에 관계없이 동일한 결과를 보장하고, 구조화된 출력도 지원합니다.

## 주요 기능
- 최적화 커널: FlashMLA·DeepGEMM·DeepEP 등으로 추론 속도를 높입니다.
- 비동기 배치 스케줄링: CPU 배치 준비와 디바이스 실행을 겹쳐 지연을 최소화합니다.
- 배치 불변 추론: 배치 크기와 구성을 바꿔도 결과가 동일합니다.
- 결정적 샘플링: 동일 입력·시드로 언제든 동일한 텍스트를 생성합니다.
- 구조화된 출력: 정규식·JSON 스키마·EBNF 문법에 맞는 텍스트를 강제합니다.

## 참고·주의
- Linux 운영체제에서만 동작합니다.
- NVIDIA SM100 GPU 또는 Huawei Ascend 950 NPU가 필요합니다.
- GCC 13 이상, Python 3.12, CUDA 13(NVIDIA) 또는 CANN 9.2(Ascend) 환경이 요구됩니다.
- KV 캐시 시스템 등 일부 서비스 구성 요소는 별도로 구현해야 합니다.

## 등장 기록
| 날짜 | Today | Week | Month | ★ |
|---|---|---|---|---|
