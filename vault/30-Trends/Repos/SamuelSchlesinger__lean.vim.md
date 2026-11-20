---
repo: SamuelSchlesinger/lean.vim
url: https://github.com/SamuelSchlesinger/lean.vim
language: 
stars: 
summary: "Vim 9 환경에서 Neovim이나 외부 도구 없이 Lean 4 언어를 직접 다룰 수 있게 해 주는 플러그인입니다."
main_category: "개발자 도구"
categories: ["개발자 도구", "기기 유틸"]
first_seen: 
last_seen: 
appearances: 0
tags: [ai-trend, repo]
---
# SamuelSchlesinger/lean.vim

> Vim 9 환경에서 Neovim이나 외부 도구 없이 Lean 4 언어를 직접 다룰 수 있게 해 주는 플러그인입니다.

## 개요
이 도구는 Vim 9 환경에서 Lean 4 언어 서버와 직접 연동하여 별도의 외부 프로그램 없이 수학 정형화와 프로그래밍을 할 수 있게 돕습니다. Neovim 중심의 기존 도구와 달리 Vim에 내장된 기능만으로 동작하도록 만들어졌습니다. 사용자는 플러그인을 설치하고 `.lean` 파일을 열기만 하면 코드 자동 완성, 인라인 힌트, 상태 정보 창(infoview) 등의 기능을 바로 이용할 수 있습니다.

## 주요 기능
- 내장 언어 서버 연동: 외부 LSP 클라이언트나 Neovim 없이 Vim의 작업과 채널 기능만으로 Lean 언어 서버를 직접 실행합니다.
- 실시간 정보 창: 현재 증명 목표와 진단 메시지를 보여 주는 전용 창을 열어 코드를 작성하면서 결과를 바로 확인할 수 있습니다.
- 유니코드 기호 입력: 특수 기호 단축키를 지원하여 수학 기호와 Lean 유니코드 문자를 편리하게 입력할 수 있습니다.
- 코드 자동 완성 및 힌트: 입력 중인 코드에 맞추어 완성 목록을 띄우고 인라인 힌트를 화면에 보여 줍니다.
- 다양한 편집 도구: 정의 이동, 참조 찾기, 이름 변경, 코드 액션 실행 등의 기능을 명령어와 단축키로 제공합니다.

## 참고·주의
- Vim 9.2 또는 `uri_encode()` 등을 지원하는 최신 Vim 9.1 버전이 필요합니다.
- 시스템 환경 변수 `PATH`에 Lean 4와 `lake`가 설치되어 있어야 합니다.

## 등장 기록
| 날짜 | Today | Week | Month | ★ |
|---|---|---|---|---|
