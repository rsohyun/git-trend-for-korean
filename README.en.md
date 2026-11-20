[한국어](README.md) | **English**

# git-trend-for-korean

> Collects GitHub's official trending repositories every day, summarizes each README in Korean, and publishes the results to a website, Obsidian notes, and email.

🔗 **Site: https://gittrendforkorean-site.vercel.app**

- Collects **GitHub's official trending** Repositories (Today · This week · This month) and Developers (This week · This month) every day.
- Newly seen repositories get their README **summarized in Korean by an LLM (Gemini)**. A repository is never summarized twice.
- One Obsidian note per repository; each later appearance is added as one line to that note's history.
- Repositories and developers that were not on the previous day's list are marked **NEW**.
- Runs and deploys daily with **GitHub Actions + Vercel** only, no server.

> Note: summaries and the site are in **Korean**.

## 💡 Background

New AI tools and open-source projects often show up first on GitHub Trending. But the trending page only gives a one-line English description, so finding out what a repository actually does meant opening and reading each README. The list also changes every day, which made it hard to find a repository I had seen a few days earlier.

## 🎯 The Solution

Every morning the trending lists are collected automatically, and the README of each newly seen repository is summarized in Korean. The results go to three places:

- **Website**: public daily trending lists with Korean summaries
- **Obsidian notes**: per-repository summaries and appearance history, searchable later
- **Email**: the day's list, delivered before work

## 🚀 Benefits

- **Quick understanding**: see what a repository is for in Korean without reading its README
- **Accumulated history**: daily snapshots and repository notes make past trends easy to revisit
- **Minimal running cost**: no server; runs within the free tiers of GitHub Actions and Vercel

## How it works

```
GitHub Actions (daily 08:07 KST, retries at 08:37 · 10:17 · 12:17 if missed)
  → scrape github.com/trending (Repositories × 3 periods + Developers × 2 periods)
  → for new repositories: fetch README via GitHub API → summarize in Korean with Gemini
  → create/update notes in vault/30-Trends/Repos/, save .trending-days/YYYY-MM-DD.json
  → build site/index.html → commit & push → Vercel auto-deploy
  → send the day's list via Gmail
```

## Tech stack

| Area | Technology |
|------|------------|
| Collection & summary | Python 3.12, httpx, Jinja2 |
| LLM | Gemini (OpenAI-compatible API) |
| Scheduling | GitHub Actions (cron) |
| Hosting | Vercel (static site) |
| Notes | Obsidian vault (Markdown) |
| Quality | pytest, ruff, gitleaks (pre-commit) |

## Layout

| Path | Contents |
|------|----------|
| `ai-worker/app/trending.py` | Scrapes and parses GitHub trending pages |
| `ai-worker/app/gittrend.py` | Summaries, notes, daily data |
| `ai-worker/app/site.py` | Static site generation |
| `ai-worker/app/cli.py` | Commands used by Actions (`gittrend`, `site`, `send-mail`) |
| `ai-worker/prompts/`, `ai-worker/templates/` | LLM prompts; note, email and site templates |
| `site/` | The deployed site |
| `vault/30-Trends/Repos/` | Per-repository summary notes (Markdown, opens in Obsidian) |
| `vault/30-Trends/.trending-days/` | Daily trending snapshots (JSON) |

## Running it yourself

### GitHub Actions

Fork the repository and set the values below; `.github/workflows/gittrend-daily.yml` then runs daily. It can also be run manually from the Actions tab.

| Kind | Name | Purpose |
|------|------|---------|
| Secret | `GEMINI_API_KEY` | README summaries |
| Secret | `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `MAIL_TO` | Sending email |
| Variable | `SITE_URL` | Links in the email (falls back to GitHub if empty) |

### Locally

```bash
cp .env.example .env    # fill AI_WORKER_TOKEN (any value), LLM_*, GITHUB_TOKEN
set -a; . ./.env; set +a   # export .env values
cd ai-worker
pip install -e .
python -m app.cli gittrend --mail-out mail.json   # collect, summarize, build site
python -m app.cli site                            # rebuild the site from saved data only
```

With `LLM_PROVIDER=fake`, no LLM is called and placeholder summaries are used.

### Tests

```bash
cd ai-worker
pip install -e ".[dev]"
pytest -q
ruff check .
```

## Notes

- Trending data is scraped from GitHub's HTML, so collection can break if GitHub changes the page layout.
- GitHub scheduled runs are sometimes late or skipped, so the workflow is scheduled at several times and skips if the day's run already succeeded.
- When the LLM rate limit is hit, the run waits and retries; repositories that still fail fall back to their GitHub description.
