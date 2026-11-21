# AI Job Application Agents

A team of AI agents that search job sites, tailor a one-page resume and cover letter for each role, fill in the application in **your own signed-in browser**, and log everything in a spreadsheet — one agent per job site, all running at once. You stay the boss: anything sensitive stops and waits for you.

Built to run in the **Claude desktop app** (Code tab) together with the **Claude in Chrome** browser extension.

> **This repository contains no personal details.** You fill in your own facts in template files, and the agents are only ever allowed to use those facts — they never invent experience, certificates, or answers.

![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)

## What it does
- 🔍 Searches the job sites you choose (e.g. SEEK, Indeed, Glassdoor, Jora, Zapid)
- 📝 Builds a tailored one-page resume + cover letter PDF per job from your verified profile
- 🖱️ Fills the application in your own signed-in browser — you press **Submit** on anything it can't safely confirm
- 📊 Logs every application, skip and reason in a spreadsheet, with an optional live dashboard
- 🛑 Honest by design: unknown answer = skip & flag; never bypasses CAPTCHAs; one application per company

## What you need (~20 min to set up)
1. **Claude desktop app** with the **Code** tab, on a paid plan (Pro works; five agents use a lot of the allowance, so expect to hit weekly limits faster).
2. **Chrome** with the **Claude in Chrome** extension, connected to Claude. Use a Chrome profile just for job hunting, signed in to your own accounts on the sites you want to use.
3. A **Mac** with these installed (one-time):
   ```bash
   brew install node poppler && brew install --cask libreoffice
   pip3 install openpyxl
   ```

## Setup
1. Clone this repo and open the folder as your working folder in the Claude **Code** tab:
   ```bash
   git clone https://github.com/JC16092/ai-job-application-agents.git
   ```
2. Copy the two template files to their real names and fill them with **your true details**:
   ```bash
   cp job-agent/profile.example.json         job-agent/profile.json
   cp job-agent/search_criteria.example.json job-agent/search_criteria.json
   ```
   (Or paste `prompts/1_FILL_MY_PROFILE.md` into Claude and it will build both files for you by asking questions.) Everything on every application comes from `profile.json` — read it carefully.
3. Install the resume builder once:
   ```bash
   npm install
   ```
4. Paste `prompts/2_START_THE_TEAM.md` into Claude to start one agent per site plus a health check. `prompts/3_HEALTH_CHECK.md` is the periodic check you can re-run.

**It starts in `"mode": "dry_run"`** (the default in your profile): agents prepare everything and log `Prepared (dry-run)` but submit nothing. Check a few resumes in `job-agent/output/`, then switch `"mode"` to `"live"` in `job-agent/profile.json` when you're happy.

## What each part is
| File / folder | What it does |
|---|---|
| `job-agent/profile.example.json` | Template for your verified facts + approved answers. Copy to `profile.json` — the **only** source of truth. |
| `job-agent/search_criteria.example.json` | Template for roles, area, pay floor and which sites to use. Copy to `search_criteria.json`. |
| `job-agent/PORTAL_BRIEF.md` | Rules every agent re-reads (pacing, CAPTCHA handling, honesty). Add your own updates at the bottom. |
| `.claude/agents/job-applier.md` | The agent's instructions and hard limits. |
| `job-agent/make_job.py`, `build_docs.js` | Build a tailored one-page resume + cover letter PDF per job from your profile. |
| `job-agent/tracker_add.py`, `tracker_update.py`, `dedupe.py` | Claim a job before applying (blocks duplicates and the same company twice), then record the result. |
| `job-agent/score_job.py` | Scores each candidate so agents apply to the best-fit, newest roles first. |
| `Job_Applications_Tracker.xlsx` | The log (ships blank). Don't keep it open in Excel while agents run — open a copy instead. |
| `office/` | Optional live dashboard (run `office/Start_Office.command`) showing each agent working. |
| `prompts/` | The three prompts you paste into Claude. |
| `job-agent/certificates/` | Drop your certificate PDFs here for uploads (git-ignored, so they're never committed). |

## Rules the agents follow (and you should keep)
- **Never invent** experience, certificates, licences or answers; unknown = skip and log `Needs Review`.
- **Never** pay, give bank / TFN / ID / passport details, accept offers, or agree interview times.
- **Never** solve CAPTCHAs or bypass Cloudflare "verify you are human" — the agent stops that site and tells you; you tick the check yourself in that Chrome profile.
- **One application per company.** The tracker blocks repeats.
- **Employer replies** that need a decision come to you first.

## Good to know
- **Be honest in `profile.json`.** The agents write exactly what you give them; false claims can lose you a job later.
- **Job sites may block fast automation.** Indeed and Glassdoor often show Cloudflare checks if searches come too fast. The kit paces itself, but expect the occasional "needs your click".
- **You still press Submit** on anything the agent can't confirm (parked as `Ready - needs user click`).
- **Usage limits:** if the 5-hour limit nears 90%, the health check pauses the agents; restart them when it resets.
- Your filled `profile.json`, `search_criteria.json`, generated PDFs/DOCX, your real tracker and certificate files are all **git-ignored**, so you won't accidentally publish your own data.
- Review `job-agent/output/run_*.md` for what each agent applied to, skipped and why.

## ⚠️ Disclaimer
This tool automates interactions with third-party job sites using your own accounts. **Some job sites' terms of service restrict automated access or applying — use this at your own risk** and check each site's terms yourself. You are responsible for everything submitted under your name, so always keep it truthful. The software is provided "as is", without warranty of any kind (see [LICENSE](LICENSE)). This project is independent and is not affiliated with or endorsed by SEEK, Indeed, Glassdoor, Jora, Zapid, Anthropic, or any job site.

## License
MIT © 2026 Jaykumar Chauhan. See [LICENSE](LICENSE).

---
*Built with [Claude Code](https://claude.com/claude-code).*
