---
repo: seedds/nxnative
url: https://github.com/seedds/nxnative
language: Objective-C
stars: 10994
summary: "Switch 게임을 iPhone·iPad·Mac에서 네이티브로 실행할 수 있게 NSP 폴더를 서명되지 않은 IPA로 변환해 주는 도구입니다."
main_category: "게임"
categories: ["게임", "기기 유틸", "개발자 도구"]
first_seen: 
last_seen: 
appearances: 0
tags: [ai-trend, repo]
---
# seedds/nxnative

> Switch 게임을 iPhone·iPad·Mac에서 네이티브로 실행할 수 있게 NSP 폴더를 서명되지 않은 IPA로 변환해 주는 도구입니다.

## 개요
nxnative은 Nintendo Switch용 NSP 파일과 prod.keys를 입력받아 iOS·iPadOS·macOS용 IPA 패키지를 생성합니다. 게임 코드를 그대로 Apple 칩에서 실행하고, Switch 그래픽스를 Metal API로 재구성해 에뮬레이터 없이 동작합니다. 스크립트를 실행하면 변환된 IPA가 생성되며, 이를 사이드로드하면 해당 게임을 iPhone·iPad·Mac에서 실행할 수 있습니다. iOS 26 이상, A17 Pro 이상 iPhone 또는 M1 이상 iPad가 필요하고, 최신 기기에서만 BC 압축 텍스처를 지원합니다.

## 주요 기능
- NSP→IPA 변환: NSP 폴더와 prod.keys만으로 iOS용 서명되지 않은 IPA를 자동 생성합니다.
- NSO 리라이터: Switch 실행 파일(NSO)을 Apple 환경에 맞게 재작성해 네이티브 실행을 가능하게 합니다.
- Horizon HLE 호스트: Switch 커널 서비스와 동기화 동작을 모방해 게임이 정상적으로 동작하도록 지원합니다.
- NVN→Metal 그래픽 레이어: Switch 전용 NVN 그래픽 API를 Metal으로 변환해 화면을 렌더링합니다.
- 셰이더 변환 파이프라인: Maxwell 셰이더를 SPIR‑V로 변환한 뒤 Metal Shading Language으로 컴파일합니다.
- 다양한 게임 지원: 현재 Mario Kart 8 Deluxe, Zelda 시리즈 등 다수의 Switch 타이틀을 실행할 수 있습니다.

## 참고·주의
- iOS 26 이상, A17 Pro 이상 iPhone 또는 M1 이상 iPad가 필요합니다.
- Nintendo prod.keys 파일이 필요하며, 이는 법적 제약이 있을 수 있습니다.
- IPA를 사이드로드하려면 개발자 계정 또는 탈옥이 필요합니다.
- Nintendo와 공식적인 연관이 없으며, 사용 시 저작권 및 약관을 확인해야 합니다.

## 등장 기록
| 날짜 | Today | Week | Month | ★ |
|---|---|---|---|---|
