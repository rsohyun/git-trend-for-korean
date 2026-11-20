[한국어](README.md) | **English**

# git-trend-for-korean

> An automation project that collects GitHub's official trending repositories and developers every day, summarizes the READMEs of notable repositories in Korean, and delivers the results through a website, Obsidian notes, and email.

🔗 **Site: https://gittrendforkorean-site.vercel.app**

- **Official GitHub trending collection**: Automatically collects the Repositories (Today · This week · This month) and Developers (This week · This month) lists every day.
- **Korean README summaries**: Summarizes the README of each newly appearing repository in Korean using an LLM (Gemini). A repository that has already been summarized is not processed again.
- **Per-repository history**: Creates an Obsidian note for each repository and appends the date and appearance record every time it shows up on trending again.
- **NEW badges**: Marks repositories and developers that were not on the previous day's trending list.
- **Serverless automation**: Runs everything from data collection to website deployment with GitHub Actions and Vercel, with no server to operate.

> Note: summaries and the site are in **Korean**.

## 💡 Background

As AI and the open-source ecosystem evolve rapidly, new tools and projects appear every day. GitHub Trending in particular is a useful source for seeing which technologies and repositories developers are paying attention to right now.

However, most repositories on the trending list are described in English. Understanding a project's purpose and main features meant opening each README and translating it, or summarizing it separately with an LLM. And even when I found an interesting repository, unless I recorded it somewhere, it was hard to notice when it appeared again or to compare it with past trends.

I wanted more than a quick way to learn about new technologies and services: I needed an environment where I could keep tracking the projects I care about and build up a record over time. So I built an automated system that covers everything from collecting GitHub trending data to Korean summaries, history tracking, and sharing the results.

## 🎯 The Solution

GitHub's official trending data is collected automatically every day, and the README of each newly appearing repository is summarized in Korean. The results are available through three channels:

- **Website**: Daily lists of trending repositories and developers, with NEW markers and Korean summaries, available to anyone
- **Obsidian notes**: Per-repository summaries and trending history accumulated over time, so projects of interest can be searched and past records revisited
- **Email**: The day's key trending information delivered every morning, so new technologies and projects can be checked without visiting the site

## 🚀 Benefits

- **Better accessibility**: Quickly understand a project's purpose and main features in Korean without reading each English README
- **Trend tracking**: Follow how notable technologies and projects change over time through daily trending records and NEW markers
- **Knowledge building**: Keep a continuous record of per-repository summaries and appearance history as a personal tech archive
- **Efficient access**: Check the information you need the way you prefer, on the website or by email
- **Minimal running cost**: Collection, processing, and deployment are automated with GitHub Actions and Vercel, with no server to build

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
