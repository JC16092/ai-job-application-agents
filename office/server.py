#!/usr/bin/env python3
"""Live data for the job-agent office page.

Serves office/index.html and /api/status. Everything is read-only: the tracker
spreadsheet, the tailored-document files the agents write, and office/state.json
(which the orchestrator edits to say who is on a break and the interview time).
"""
import glob
import json
import os
import sys
import time
from datetime import datetime, date, time as dtime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ROOT)
import openpyxl  # noqa: E402

TRACKER = os.path.join(BASE, "Job_Applications_Tracker.xlsx")
OUTPUT = os.path.join(BASE, "job-agent", "output")
STATE = os.path.join(ROOT, "state.json")
PORT = int(os.environ.get("PORT", "8765"))

PORTALS = ["seek", "indeed", "glassdoor", "jora", "zapid"]
DOC_MARKERS = {
    "seek": ["_seek_"],
    "indeed": ["_indeed_"],
    "glassdoor": ["_gd_", "_glassdoor_"],
    "jora": ["_jora_"],
    "zapid": ["_zp_", "_zapid_"],
}

_cache = {"t": 0, "data": None}
TRANSCRIPTS = os.path.expanduser("~/.claude/projects/" + __import__("re").sub(r"[^A-Za-z0-9]", "-", BASE))
_map = {"t": 0, "files": {}}
PATS = {p: __import__("re").compile(r"\b%s\b" % p, __import__("re").I) for p in PORTALS}


def transcript_files():
    """Map each portal to the transcript file of its agent session (re-detected once a minute).
    A file is an agent's if one portal name clearly dominates the start of its transcript."""
    if time.time() - _map["t"] < 60 and _map["files"]:
        return _map["files"]
    best = {}
    try:
        cands = [f for f in glob.glob(os.path.join(TRANSCRIPTS, "*.jsonl")) if time.time() - os.path.getmtime(f) < 86400]
    except Exception:
        cands = []
    used = set()
    for size in (60000, 400000):
        for f in cands:
            if f in used:
                continue
            try:
                with open(f, errors="replace") as fh:
                    head = fh.read(size)
            except Exception:
                continue
            counts = {p: len(rx.findall(head)) for p, rx in PATS.items()}
            total = sum(counts.values())
            if total < 6:
                continue
            top = max(counts, key=counts.get)
            if top in best:
                continue
            if counts[top] / total >= 0.4:
                best[top] = (counts[top], f)
                used.add(f)
    _map["files"] = {p: v[1] for p, v in best.items()}
    _map["t"] = time.time()
    return _map["files"]


def portal_of(source):
    s = str(source or "").strip().lower()
    for p in PORTALS:
        if s.startswith(p):
            return p
    return "other"


def to_dt(d, t):
    if not isinstance(d, (datetime, date)):
        return None
    day = d.date() if isinstance(d, datetime) else d
    if isinstance(t, dtime):
        return datetime.combine(day, t)
    if isinstance(t, datetime):
        return datetime.combine(day, t.time())
    if isinstance(t, str):
        for fmt in ("%I:%M %p", "%H:%M", "%H:%M:%S"):
            try:
                return datetime.combine(day, datetime.strptime(t.strip(), fmt).time())
            except ValueError:
                pass
    return datetime.combine(day, dtime(0, 0))


def load_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except Exception:
        return {}


def build():
    now = datetime.now()
    today = now.date()
    stats = {p: {"today": 0, "total": 0, "click": 0, "review": 0, "last": None, "last_event": None, "last_ts": None}
             for p in PORTALS}
    other = {"today": 0, "total": 0}
    events = []
    clicks = []
    totals = {"jobs": 0, "applied": 0, "today": 0, "skipped": 0, "review": 0, "click": 0}
    try:
        wb = openpyxl.load_workbook(TRACKER, read_only=True, data_only=True)
        ws = wb["Applications"]
        for r in ws.iter_rows(min_row=2, values_only=True):
            if not r or not r[1]:
                continue
            company, title, source, d, t, status = r[1], r[2], r[6], r[7], r[8], r[9]
            p = portal_of(source)
            when = to_dt(d, t)
            totals["jobs"] += 1
            if status == "Applied":
                totals["applied"] += 1
                if when and when.date() == today:
                    totals["today"] += 1
            elif status == "Skipped":
                totals["skipped"] += 1
            elif status == "Needs Review":
                totals["review"] += 1
            elif status == "Ready - needs user click":
                totals["click"] += 1
                clicks.append({"company": company, "title": title, "portal": p})
            bucket = stats.get(p)
            if bucket is None:
                if status == "Applied":
                    other["total"] += 1
                    if when and when.date() == today:
                        other["today"] += 1
                continue
            if status == "Applied":
                bucket["total"] += 1
                if when and when.date() == today:
                    bucket["today"] += 1
            if status == "Ready - needs user click":
                bucket["click"] += 1
            if status == "Needs Review":
                bucket["review"] += 1
            if when and status in ("Applied", "Ready - needs user click", "Needs Review", "Skipped"):
                ev = {"portal": p, "company": company, "title": title, "status": status, "ts": when.timestamp()}
                events.append(ev)
                if bucket["last_ts"] is None or ev["ts"] > bucket["last_ts"]:
                    bucket["last_ts"] = ev["ts"]
                    bucket["last_event"] = ev
        wb.close()
    except Exception as exc:  # tracker may be mid-write; keep the page alive
        return {"error": str(exc), "now": now.timestamp()}

    # newest tailored document per portal = last time that agent "did real work"
    for p in PORTALS:
        newest = 0
        for pattern in DOC_MARKERS[p]:
            for fn in glob.glob(os.path.join(OUTPUT, "*%s*.pdf" % pattern), recursive=False):
                newest = max(newest, os.path.getmtime(fn))
            # case-insensitive fallback for markers like SEEK
        if p == "seek":
            for fn in glob.glob(os.path.join(OUTPUT, "*SEEK*.pdf")):
                newest = max(newest, os.path.getmtime(fn))
        stats[p]["doc_ts"] = newest or None
        signal = max(x for x in (stats[p]["last_ts"] or 0, newest) if x is not None) if (stats[p]["last_ts"] or newest) else None
        stats[p]["signal_ts"] = signal
        tf = transcript_files().get(p)
        try:
            stats[p]["active_ts"] = os.path.getmtime(tf) if tf else None
        except OSError:
            stats[p]["active_ts"] = None

    events.sort(key=lambda e: e["ts"], reverse=True)
    state = load_state()
    return {
        "now": now.timestamp(),
        "today": today.isoformat(),
        "agents": stats,
        "other": other,
        "totals": totals,
        "events": events[:14],
        "clicks": clicks[:12],
        "state": state,
    }


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            with open(os.path.join(ROOT, "index.html"), "rb") as f:
                return self._send(200, f.read(), "text/html; charset=utf-8")
        if path == "/api/status":
            if time.time() - _cache["t"] > 3 or _cache["data"] is None:
                _cache["data"] = json.dumps(build()).encode()
                _cache["t"] = time.time()
            return self._send(200, _cache["data"], "application/json")
        self._send(404, b"not found", "text/plain")


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print("Office page on http://localhost:%d" % PORT, flush=True)
    srv.serve_forever()
