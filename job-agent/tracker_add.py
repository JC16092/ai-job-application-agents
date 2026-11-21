#!/usr/bin/env python3
"""Usage: python3 job-agent/tracker_add.py '{"company":..., "title":..., "url":..., ...}'
Adds a row to ../Job_Applications_Tracker.xlsx under a file lock. Fuzzy-dedupes on company+title and on job link.
Results: added | duplicate | same_company_already_applied (skip the job in both non-added cases).
Fields: company,title,location,pay,type,source,status,resume,cover,notes,url ; date/time default to now when status=Applied."""
import sys, json, os, fcntl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dedupe import same_company, same_title, norm_url
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Job_Applications_Tracker.xlsx")
d = json.loads(sys.argv[1])
_lock = open(os.path.join(os.path.dirname(P), "job-agent", ".tracker.lock"), "w")
fcntl.flock(_lock, fcntl.LOCK_EX)
wb = load_workbook(P); ws = wb["Applications"]
if not ws["P1"].value:
    ws["P1"] = "Job Link"; ws["P1"].font = Font(bold=True, color="FFFFFF"); ws["P1"].fill = PatternFill("solid", fgColor="1F3A5F")
    ws["P1"].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); ws.column_dimensions["P"].width = 50
BLOCKING = ("applied", "applying", "ready", "prepared")
new_status = d.get("status", "Applied"); url_id = norm_url(d.get("url"))
row = None
for r in range(2, 5000):
    b, c = ws[f"B{r}"].value, ws[f"C{r}"].value
    if not b:
        if row is None: row = r
        continue
    st = str(ws[f"J{r}"].value or "").lower()
    if url_id and norm_url(ws[f"P{r}"].value) == url_id:
        print(json.dumps({"result": "duplicate", "reason": "same job link", "row": r, "existing": f"{b} | {c} | {ws[f'J{r}'].value}"})); sys.exit(0)
    if same_company(b, d["company"]):
        if same_title(c, d["title"]):
            print(json.dumps({"result": "duplicate", "row": r, "existing": f"{b} | {c} | {ws[f'J{r}'].value}"})); sys.exit(0)
        if st.startswith(BLOCKING) and new_status in ("Applied", "Applying") and not d.get("allow_same_company"):
            print(json.dumps({"result": "same_company_already_applied", "row": r, "existing": f"{b} | {c} | {ws[f'J{r}'].value}"})); sys.exit(0)
now = datetime.fromisoformat(os.environ["TRACKER_NOW"]) if os.environ.get("TRACKER_NOW") else datetime.now()
vals = {"B": d["company"], "C": d["title"], "D": d.get("location"), "E": d.get("pay"), "F": d.get("type"), "G": d.get("source"),
        "J": new_status, "K": d.get("resume"), "L": d.get("cover"), "O": d.get("notes"), "P": d.get("url")}
if new_status == "Applied":
    vals["H"] = now.date(); vals["I"] = now.time().replace(microsecond=0, second=0)
for k, v in vals.items():
    if v is not None: ws[f"{k}{row}"] = v
wb.save(P)
print(json.dumps({"result": "added", "row": row}))
