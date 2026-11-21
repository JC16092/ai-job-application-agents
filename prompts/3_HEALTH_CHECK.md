# Prompt 3: 5-minute health check (the manager session schedules this as a recurring cron)

Replace every `<...>` with the real value before scheduling.

```
Job-agent health check.
1) If <KIT_FOLDER>/job-agent/.paused_for_limit exists, do nothing.
2) Call get_usage. If the 5-hour limit is at 90% or more, create .paused_for_limit, stop every job-<site> session with stop_session, set office/state.json to all paused, and tell me.
3) Otherwise call list_sessions {linked:true}. For each of these sessions: <job-site name = local_id>, <job-site name = local_id>, ...
   if a session has had no activity for 15 minutes or more, send it this message:
   "GO from the boss. Resume applying in continuous mode. Re-read job-agent/PORTAL_BRIEF.md and profile.json. Always fill the tracker source with your portal name. Search at human pace. Never bypass Cloudflare/CAPTCHA. After each pass, keep going: run a background sleep of about 3 minutes and then do the next pass, without ending your turn to wait for me."
   Do NOT restart any session on my HOLD list: <list the sites blocked by Cloudflare, if any>.
   Busy sessions are fine: do not re-send within 15 minutes of activity.
Report only if something needs me.
```

Notes
- When the 5-hour limit resets, delete `job-agent/.paused_for_limit`, restore `office/state.json`, and restart the sessions with the GO message.
- Cloudflare: when a site shows "verify you are human", add it to the HOLD list. Tick the check yourself in the signed-in Chrome profile, then tell the manager to restart that site.
