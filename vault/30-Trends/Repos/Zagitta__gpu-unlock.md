---
repo: Zagitta/gpu-unlock
url: https://github.com/Zagitta/gpu-unlock
language: C
stars: 14010
summary: "소비자용 Nvidia 30 시리즈 그래픽 카드의 FP/BF16 연산 발행 속도를 프로페셔널 수준으로 해제해 주는 리눅스 커널 모듈입니다."
main_category: "GPU 최적화"
categories: ["GPU 최적화", "리눅스", "개발자 도구"]
first_seen: 
last_seen: 
appearances: 0
tags: [ai-trend, repo]
---
# Zagitta/gpu-unlock

> 소비자용 Nvidia 30 시리즈 그래픽 카드의 FP/BF16 연산 발행 속도를 프로페셔널 수준으로 해제해 주는 리눅스 커널 모듈입니다.

## 개요
이 도구는 리눅스 커널 모듈 형태로 GPU의 FP/BF16 명령 발행률을 높입니다. 소비자 카드에 적용된 인위적 제한을 제거해 연산 성능을 두 배 정도 향상합니다. 설치 후 부트 로더 커맨드라인에 옵션을 추가하고 재부팅하면, initramfs 단계에서 모듈이 실행되어 NVIDIA 드라이버가 바인딩되기 전에 속도 선택자를 설정합니다. 부팅 후 `lspci`나 `journalctl`로 적용 여부를 확인할 수 있습니다.

## 주요 기능
- 속도 선택자 자동 설정: 부팅 시 GPU의 SS0와 SS1 레지스터를 프로페셔널 수준으로 기록합니다.
- 드라이버 독립 실행: NVIDIA 드라이버 버전에 맞춰 패치를 할 필요 없이 모듈만 로드하면 됩니다.
- 다중 카드 지원: `gpu_unlock.targets` 옵션으로 전체 또는 선택한 PCI 주소의 카드만 해제할 수 있습니다.
- 재부팅 및 재개 자동 복구: suspend·resume 시에도 동일한 해제가 자동으로 재적용됩니다.
- 배포판 자동 감지 설치: `make install` 명령이 Debian/Ubuntu, Arch, Fedora 등 주요 배포판에 맞는 패키지를 생성합니다.

## 참고·주의
- 루트 권한과 부트 로더 커맨드라인 수정이 필요합니다.
- GPU가 약간 더 뜨거워질 수 있으며, 이는 표준 스로틀링에 의해 제어됩니다.
- 현재 GA100/GA102/GA103/GA104/GA106 및 RTX 4090만 지원합니다.
- 윈도우에서는 동작하지 않으며, 사용 시 제조사 보증이 영향을 받을 수 있습니다.

## 등장 기록
| 날짜 | Today | Week | Month | ★ |
|---|---|---|---|---|
