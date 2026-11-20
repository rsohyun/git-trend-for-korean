---
repo: doobidoo/mcp-memory-service
url: https://github.com/doobidoo/mcp-memory-service
language: 
stars: 
summary: "AI 에이전트와 클로드(Claude)가 대화 내용을 잊지 않고 기억할 수 있도록 돕는 오픈소스 영구 기억 장치입니다."
main_category: "AI 에이전트"
categories: ["AI 에이전트", "로컬 AI", "개발자 도구"]
first_seen: 
last_seen: 
appearances: 0
tags: [ai-trend, repo]
---
# doobidoo/mcp-memory-service

> AI 에이전트와 클로드(Claude)가 대화 내용을 잊지 않고 기억할 수 있도록 돕는 오픈소스 영구 기억 장치입니다.

## 개요
AI 도구가 대화를 마칠 때마다 이전 맥락을 잃어버리는 문제를 해결합니다. 사용자는 이 서비스를 직접 설치하고 실행하여 여러 에이전트와 대화 세션 사이에서 기억을 공유할 수 있습니다. 지식 그래프를 활용해 인과 관계를 파악하고, 로컬 환경에서 빠르게 관련 맥락을 불러옵니다.

## 주요 기능
- 프레임워크 독립형 REST API: MCP 클라이언트 라이브러리 없이 다양한 HTTP 클라이언트에서 연동할 수 있습니다.
- 지식 그래프: 단순한 사실 저장을 넘어 원인과 결과 같은 인과 관계를 에이전트끼리 공유합니다.
- 에이전트별 태그 기능: 요청 헤더로 에이전트 ID를 지정해 기억을 체계적으로 분류하고 검색합니다.
- 실시간 이벤트 알림: 에이전트가 기억을 저장하거나 삭제할 때 실시간으로 변경 사항을 수신합니다.
- 로컬 임베딩 처리: ONNX를 사용해 데이터가 외부 인프라로 유출되지 않고 로컬에서 안전하게 처리됩니다.

## 참고·주의
- README에 명시된 주의사항 없음

## 등장 기록
| 날짜 | Today | Week | Month | ★ |
|---|---|---|---|---|
