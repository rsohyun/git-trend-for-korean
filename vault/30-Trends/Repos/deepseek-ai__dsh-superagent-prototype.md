---
repo: deepseek-ai/dsh-superagent-prototype
url: https://github.com/deepseek-ai/dsh-superagent-prototype
language: TypeScript
stars: 15837
summary: "dsh-superagent는 하나의 GitHub 저장소를 대상으로 자동으로 코드를 작성·수정하고 풀 리퀘스트를 생성하는 프로액티브 코딩 에이전트입니다."
main_category: "AI 에이전트"
categories: ["AI 에이전트", "개발자 도구"]
first_seen: 
last_seen: 
appearances: 0
tags: [ai-trend, repo]
---
# deepseek-ai/dsh-superagent-prototype

> dsh-superagent는 하나의 GitHub 저장소를 대상으로 자동으로 코드를 작성·수정하고 풀 리퀘스트를 생성하는 프로액티브 코딩 에이전트입니다.

## 개요
이 도구는 GitHub(및 선택적으로 Feishu) 이벤트를 실시간으로 감지해 작업 요청이 들어오면 에이전트 세션을 열어 코드를 작성합니다. 사용자는 DeepSeek Harness 환경에 설치 후 에이전트에게 SETUP.md를 따라 설정을 진행하도록 요청하면 됩니다. 설정이 완료되면 에이전트에게 작업을 지시하면 자동으로 작업 항목을 만들고, 코드를 구현해 풀 리퀘스트를 생성해 원래 대화에 결과를 반환합니다. 연구용 프로토타입이므로 버그가 있을 수 있으며, 실제 운영 환경에 바로 적용하기 전에 검토가 필요합니다.

## 주요 기능
- 자동 작업 생성: 요청에 따라 작업 항목을 열고 코드를 작성해 풀 리퀘스트를 자동으로 생성합니다.
- GitHub·Feishu 연동: 저장소 이벤트와 메신저 메시지를 실시간으로 감지해 에이전트가 반응합니다.
- 웹 패널 표시: 현재 진행 중인 작업과 필요한 조치를 시각적으로 확인할 수 있습니다.
- 프롬프트 기반 제어: 사전 정의된 프롬프트로 에이전트의 행동 방식을 조정합니다.
- 단계별 설정 지원: 에이전트가 SETUP.md를 따라 설치·구성 과정을 안내합니다.

## 참고·주의
- 연구용 프로토타입이며 버그가 있을 수 있어 프로덕션에 바로 사용하면 안 됩니다.
- DeepSeek Harness 환경이 필요합니다.
- Node.js와 pnpm이 사전 설치되어 있어야 합니다.

## 등장 기록
| 날짜 | Today | Week | Month | ★ |
|---|---|---|---|---|
