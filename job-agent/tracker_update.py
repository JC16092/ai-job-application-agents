#!/usr/bin/env python3
"""Usage: python3 tracker_update.py '{"company":..., "title":..., "status":"Applied", "notes":"..."}'
Finds the row (company+title) and updates status/date/time/notes under the same file lock."""
import sys, json, os, fcntl
from datetime import datetime
from openpyxl import load_workbook
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Job_Applications_Tracker.xlsx")
d = json.loads(sys.argv[1])
_lock = open(os.path.join(os.path.dirname(P), "job-agent", ".tracker.lock"), "w")
fcntl.flock(_lock, fcntl.LOCK_EX)
wb = load_workbook(P); ws = wb["Applications"]
norm = lambda s: (s or "").strip().lower()
for r in range(2, ws.max_row + 1):
    if norm(ws[f"B{r}"].value) == norm(d["company"]) and norm(ws[f"C{r}"].value) == norm(d["title"]):
        ws[f"J{r}"] = d.get("status", "Applied")
        if d.get("status", "Applied") == "Applied":
            now = datetime.fromisoformat(os.environ["TRACKER_NOW"]) if os.environ.get("TRACKER_NOW") else datetime.now(); ws[f"H{r}"] = now.date(); ws[f"I{r}"] = now.time().replace(second=0, microsecond=0)
        if d.get("notes"): ws[f"O{r}"] = d["notes"]
        wb.save(P); print(json.dumps({"result": "updated", "row": r})); sys.exit(0)
print(json.dumps({"result": "not_found"}))
