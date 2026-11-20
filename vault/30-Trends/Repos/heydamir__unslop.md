---
repo: heydamir/unslop
url: https://github.com/heydamir/unslop
language: JavaScript
stars: 6321
summary: "Claude와 Codex용 스킬로, 진동코드된 AI 느낌 UI를 제품에 맞는 디자인 인터페이스로 바꿔 줍니다."
main_category: "AI 에이전트"
categories: ["AI 에이전트", "디자인 자동화", "프론트엔드"]
first_seen: 
last_seen: 
appearances: 0
tags: [ai-trend, repo]
---
# heydamir/unslop

> Claude와 Codex용 스킬로, 진동코드된 AI 느낌 UI를 제품에 맞는 디자인 인터페이스로 바꿔 줍니다.

## 개요
unslop은 Claude Code와 Codex에서 동작하는 스킬로, AI가 만든 듯한 과도한 그라디언트·이모지·불균형 UI를 찾아냅니다. 이런 '슬롭'을 감지하고 제품의 방향성에 맞춰 색상·간격·타이포·레이아웃 등을 단계별로 정리해 디자인을 깔끔하게 고칩니다. 사용자는 스킬을 설치하고 `/unslop` 혹은 `$unslop` 명령에 대상 페이지를 입력하면, 스킬이 화면을 감사하고 방향을 제시한 뒤 자동으로 수정하거나 스토리 비디오를 생성합니다. 필요 시 Playwright와 ffmpeg, 이미지 생성 서비스와 연동해 영상과 그래픽을 추가로 만들 수 있습니다.

## 주요 기능
- 감사: 화면의 슬롭 요소(그라디언트, 이모지, 불균형 등)를 자동으로 찾아 목록화합니다.
- 방향 설정: 제품의 캐릭터와 핵심 순간을 기반으로 디자인 방향을 제시합니다.
- 단계별 정리: 간격·색상·아이콘·텍스트·타입·레이아웃·시각·모션 순으로 UI를 개선합니다.
- 이미지 생성 연동: 필요 시 이미지 서비스(MCP 서버)와 연결해 맞춤 그래픽을 생성합니다.
- 스토리 비디오: Playwright와 ffmpeg를 이용해 10초 이하의 화면 변환 영상을 자동으로 만들고 저장합니다.

## 참고·주의
- Node.js 환경과 Playwright, Chromium 설치가 필요합니다.
- ffmpeg가 PATH에 있어야 스토리 비디오를 만들 수 있습니다.
- 이미지 생성 서비스는 별도 API 키가 필요하며 사용량에 따라 비용이 발생할 수 있습니다.
- Claude Code 또는 Codex 환경이 필요합니다.

## 등장 기록
| 날짜 | Today | Week | Month | ★ |
|---|---|---|---|---|
