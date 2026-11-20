**한국어** | [English](README.en.md)

# git-trend-for-korean

> 매일 GitHub 공식 트렌딩 저장소를 수집해 README를 한국어로 요약하고, 웹사이트·Obsidian 노트·메일로 정리하는 자동화 프로젝트.

🔗 **사이트: https://gittrendforkorean-site.vercel.app**

- **GitHub 공식 트렌딩** Repositories(Today·This week·This month)와 Developers(This week·This month)를 매일 수집합니다.
- 처음 등장한 저장소는 README를 **LLM(Gemini)으로 한국어 요약**합니다. 한 번 요약한 저장소는 다시 요약하지 않습니다.
- 저장소마다 Obsidian 노트 1개를 만들고, 다시 등장하면 그 노트의 등장 기록에 한 줄씩 쌓습니다.
- 전날 없던 저장소·개발자에는 **NEW**를 표시합니다.
- 서버 없이 **GitHub Actions + Vercel**만으로 매일 실행·배포됩니다.

## 💡 개발 배경

새로운 AI 도구와 오픈소스는 GitHub 트렌딩에서 먼저 눈에 띄는 경우가 많습니다. 하지만 트렌딩 페이지는 영어 한 줄 설명뿐이라, 저장소가 무엇을 하는지 알려면 README를 하나씩 열어 읽어야 했습니다. 목록도 매일 바뀌어서 며칠 전에 본 저장소를 다시 찾기 어려웠습니다.

## 🎯 해결 방법

매일 아침 트렌딩 목록을 자동으로 수집해, 새로 등장한 저장소의 README를 한국어로 요약합니다. 결과는 세 곳에 남습니다.

- **웹사이트**: 날짜별 트렌딩 목록과 한국어 요약을 누구나 볼 수 있게 공개
- **Obsidian 노트**: 저장소별 요약과 등장 기록을 쌓아 나중에 검색·복습
- **메일**: 출근 전에 그날 목록을 받아 보기

## 🚀 기대 효과

- **빠른 파악**: README를 직접 읽지 않아도 저장소의 용도를 한국어로 확인
- **기록 축적**: 날짜별 스냅샷과 저장소 노트가 쌓여 지난 트렌드를 다시 볼 수 있음
- **운영 비용 최소화**: 서버 없이 GitHub Actions와 Vercel 무료 범위에서 동작

## 동작 흐름

```
GitHub Actions (매일 08:07 KST, 실패 대비 08:37·10:17·12:17 재시도)
  → github.com/trending 수집 (Repositories 3기간 + Developers 2기간)
  → 처음 본 저장소: GitHub API로 README 조회 → Gemini로 한국어 요약
  → vault/30-Trends/Repos/ 노트 생성·갱신, .trending-days/YYYY-MM-DD.json 저장
  → site/index.html 생성 → 커밋·푸시 → Vercel 자동 배포
  → Gmail로 그날 목록 발송
```

## 기술 스택

| 영역 | 사용 기술 |
|------|-----------|
| 수집·요약 | Python 3.12, httpx, Jinja2 |
| LLM | Gemini (OpenAI 호환 API) |
| 실행 | GitHub Actions (cron) |
| 배포 | Vercel (정적 사이트) |
| 기록 | Obsidian 볼트 (Markdown) |
| 품질 | pytest, ruff, gitleaks (pre-commit) |

## 구조

| 경로 | 내용 |
|------|------|
| `ai-worker/app/trending.py` | GitHub 트렌딩 페이지 수집·파싱 |
| `ai-worker/app/gittrend.py` | 요약, 노트·일별 데이터 생성 |
| `ai-worker/app/site.py` | 정적 사이트 생성 |
| `ai-worker/app/cli.py` | Actions에서 쓰는 명령 (`gittrend`, `site`, `send-mail`) |
| `ai-worker/prompts/`, `ai-worker/templates/` | LLM 프롬프트, 노트·메일·사이트 템플릿 |
| `site/` | 배포되는 사이트 |
| `vault/30-Trends/Repos/` | 저장소별 요약 노트 (Obsidian에서 열 수 있는 Markdown) |
| `vault/30-Trends/.trending-days/` | 날짜별 트렌딩 스냅샷 (JSON) |

## 직접 실행하기

### GitHub Actions

저장소를 포크한 뒤 아래 값을 설정하면 `.github/workflows/gittrend-daily.yml`이 매일 실행됩니다. Actions 화면에서 수동 실행도 됩니다.

| 종류 | 이름 | 용도 |
|------|------|------|
| Secret | `GEMINI_API_KEY` | README 요약 |
| Secret | `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `MAIL_TO` | 메일 발송 |
| Variable | `SITE_URL` | 메일 속 링크 (비우면 GitHub로 연결) |

### 로컬

```bash
cp .env.example .env    # AI_WORKER_TOKEN(아무 값), LLM_*, GITHUB_TOKEN 채우기
set -a; . ./.env; set +a   # .env 값을 환경변수로 불러오기
cd ai-worker
pip install -e .
python -m app.cli gittrend --mail-out mail.json   # 수집·요약·사이트 생성
python -m app.cli site                            # 저장된 데이터로 사이트만 다시 생성
```

`LLM_PROVIDER=fake`로 두면 LLM을 호출하지 않고 가짜 요약으로 동작합니다.

### 테스트

```bash
cd ai-worker
pip install -e ".[dev]"
pytest -q
ruff check .
```

## 참고와 주의

- 트렌딩은 GitHub 페이지를 파싱해 가져오므로, GitHub가 페이지 구조를 바꾸면 수집이 실패할 수 있습니다.
- GitHub 예약 실행은 늦거나 빠지는 경우가 있어 여러 시각에 걸어 두고, 그날 이미 실행했으면 건너뜁니다.
- LLM 요청 한도에 걸리면 기다렸다가 다시 시도하고, 끝내 실패한 저장소는 GitHub 설명으로 대신 표시합니다.
