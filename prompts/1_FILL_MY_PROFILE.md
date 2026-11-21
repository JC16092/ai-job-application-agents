# Prompt 1: build my profile (paste everything below into Claude Code)

You are setting up my job-application agent team. The working folder is this starter kit. Do these steps in order and do NOT invent any fact about me.

1. Read `README.md`, `job-agent/profile.json`, `job-agent/search_criteria.json` and `.claude/agents/job-applier.md`.
2. Interview me, a few questions at a time, to fill `job-agent/profile.json`. Ask for: full name and the short name for documents; suburb, phone, and a job-only email; my work rights (the exact honest wording, and what I must never claim); my availability (days/times I can and cannot work, hours cap if any, notice period); every job I have had (title, employer, place, dates, and what I really did); education; certificates, licences and checks I actually hold (First Aid, RSA, driver's licence, police check, WWCC, etc.); languages; systems and skills I can prove; and things I do NOT have (so jobs needing them get skipped).
3. If I give you a resume, read it and propose entries, but ask me to confirm each one. Never add anything I did not confirm. Round experience DOWN when unsure.
4. Draft `career_summary`, `cover_experience_paragraph`, `cover_strength_bullets` and any `keyword_skills` lines (each with a `match` list of ad keywords) using ONLY my confirmed facts. Show them to me and wait for my approval before saving.
5. Ask how I want standard form questions answered (currently employed, pay expectation, transport, lifting limit, police check, willing to relocate, etc.) and fill `form_answers`. Leave sensitive ones (like Aboriginal/Torres Strait Islander status) as "NOT APPROVED to answer".
6. Fill `job-agent/search_criteria.json`: the kinds of roles I want, my suburb and maximum distance, my minimum hourly rate, job types, which job sites to use, and my notify email.
7. Remove every `FILL_ME` and every `EXAMPLE` entry you did not replace. Keep `"mode": "dry_run"`.
8. Show me a short summary of the final profile and ask me to read it once more. Tell me clearly that every claim on every application will come from this file.
9. Remind me of the next step: run `npm install`, make sure Chrome is signed in to the job sites, then use `prompts/2_START_THE_TEAM.md`.
