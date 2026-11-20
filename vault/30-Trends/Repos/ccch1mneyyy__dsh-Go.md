---
repo: ccch1mneyyy/dsh-Go
url: https://github.com/ccch1mneyyy/dsh-Go
language: Dart
stars: 6934
summary: "Android 기기에서 DeepSeek Harness를 실행하고, 로컬 엔진 또는 원격 PC를 제어할 수 있게 해 주는 앱입니다."
main_category: "AI 에이전트"
categories: ["AI 에이전트", "모바일 앱", "개발자 도구"]
first_seen: 
last_seen: 
appearances: 0
tags: [ai-trend, repo]
---
# ccch1mneyyy/dsh-Go

> Android 기기에서 DeepSeek Harness를 실행하고, 로컬 엔진 또는 원격 PC를 제어할 수 있게 해 주는 앱입니다.

## 개요
DSH Go는 DeepSeek Harness의 Android 클라이언트로, 스마트폰에 Ubuntu·Node.js·DSH 환경을 내장합니다. 별도 Root나 Termux 없이도 로컬에서 모델을 실행하거나, SSH·DSHarness Remote를 통해 PC·서버의 DSH에 연결해 사용할 수 있습니다. APK를 설치하고 앱을 실행해 환경을 선택·설정하면 채팅 UI에서 모델과 대화하고, 결과를 공유하거나 화면 조작까지 할 수 있습니다. 내부적으로는 PRoot 기반 호환 레이어로 Linux 환경을 제공하며, 원격 연결 시 SSH 터널을 이용합니다.

## 주요 기능
- 로컬 실행: 스마트폰에 Ubuntu·Node.js·DSH를 설치해 모델 요청을 직접 처리합니다.
- 원격 연결: SSH 또는 DSHarness Remote를 통해 PC·서버의 DSH에 한 번에 전환합니다.
- 대화 및 도구: 이미지 전송·음성 입력·플러그인 카드·폼 등 다양한 도구와 함께 채팅할 수 있습니다.
- 화면 조작: 접근성·ADB·Shizuku 권한을 부여하면 앱이 화면을 읽고 터치·입력을 자동으로 수행합니다.
- 공유·복원: 대화 내용을 공유 카드로 만들고, 암호화된 링크로 브라우저에서 재생할 수 있습니다.
- 테마·다중 언어: 6가지 테마 색상·아이콘·다크모드와 한국어·영어 UI를 지원합니다.

## 참고·주의
- Android 8.0(API 26) 이상, arm64(또는 x86_64) 전용 APK가 필요합니다.
- 이전 테스트 버전을 설치한 경우, 새 버전은 직접 덮어쓰기 못하고 먼저 삭제해야 합니다. 삭제 시 대화·설정·Linux 환경이 모두 초기화됩니다.
- 원격 연결 시 현재 이미지 첨부만 지원하고, 웹 페이지는 앱 내에서 열 수 없습니다.
- 화면 조작 기능은 접근성·ADB·Shizuku 등 추가 권한이 필요하며, 민감한 정보가 모델에 전송될 수 있습니다.
- 모델 요청은 사용자가 직접 설정한 외부 제공자에게 전송됩니다.

## 등장 기록
| 날짜 | Today | Week | Month | ★ |
|---|---|---|---|---|
