# Prompt 2: start the agent team (paste everything below into Claude Code)

You are the manager of my job-application team. The working folder is this starter kit. Do not do the job applications yourself: start one separate session per job site and keep them running.

1. Check `job-agent/profile.json` has no `FILL_ME` left and `mode` is what I want (`dry_run` or `live`). If not, stop and tell me.
2. Check the tools are installed (`node --version`, `soffice --version`, `pdfinfo -v`, `python3 -c "import openpyxl"`) and that `npm install` has been run (a `node_modules` folder exists). If anything is missing, tell me the exact command to run.
3. Load the session tool (ToolSearch `select:mcp__ccd_session__start_session`) and start ONE session per job site in my search_criteria.json `portals` (for example SEEK, Indeed, Glassdoor, Jora, Zapid), same working folder, no worktree. Name them `job-<site>`. Give each this prompt, with `<SITE>` filled in:

   > You are the <SITE> agent. Read job-agent/PORTAL_BRIEF.md first and follow it exactly, then job-agent/profile.json, job-agent/search_criteria.json and .claude/agents/job-applier.md. Work in continuous mode: after each pass with nothing new, run a background sleep of about 180 seconds and do the next pass, without ending your turn to wait for me. Fill the tracker `source` with "<SITE>" on every row. Search at human pace. Never bypass Cloudflare/CAPTCHA: stop and report instead.

4. Write down each session's `local_...` id. Then set up the health check: create a recurring cron (every 5 minutes) with the prompt in `prompts/3_HEALTH_CHECK.md`, replacing the placeholders with the real session ids. (Cron lives only while this session stays open and expires after 7 days; tell me that.)
5. Create `office/state.json` with `{"paused": [], "running": ["<site>", ...], "note": "", "interview": null}`. Offer to start the live dashboard (`office/server.py`, port 8790).
6. Tell me in a few lines what is running and what I should expect: "Ready - needs user click" items waiting for me, Cloudflare checks I must tick myself, and that nothing is submitted while `mode` is `dry_run`.

Whenever a site's agent reports it is blocked (for example Cloudflare), tell me, mark it paused in `office/state.json`, and do NOT restart it until I say I have cleared the check.
