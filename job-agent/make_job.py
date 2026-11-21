#!/usr/bin/env python3
"""Usage: python3 job-agent/make_job.py '{"slug":"seek-acme-cashier","company":"Acme","role":"Cashier","place":"Suburb VIC","keywords":["customer service","pos"]}'
Builds job-agent/output/jobs/<slug>.json from VERIFIED facts in profile.json only, then run build_docs.js on it. Prints the json path.
Nothing is invented: bullets = experience[].verified_duties, skills = skills_verified + keyword_skills lines you wrote and approved."""
import json, sys, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "profile.json")))
d = json.loads(sys.argv[1])

if "FILL_ME" in json.dumps({k: v for k, v in P.items() if not k.startswith("_")}):
    sys.exit("profile.json still contains FILL_ME placeholders. Finish the profile first (prompts/1_FILL_MY_PROFILE.md).")

today = datetime.date.today()
date = f"{today.day} {today.strftime('%B %Y')}"
role, comp = d["role"], d["company"]
kws = [k.lower() for k in d.get("keywords", [])]

# skills: keyword matches first (only lines the user wrote and approved), then the verified list
matched = []
for ks in P.get("keyword_skills", []):
    line = ks.get("line", "")
    if line.upper().startswith("EXAMPLE"):
        continue
    if any(any(k in m.lower() or m.lower() in k for m in ks.get("match", [])) for k in kws) and line not in matched:
        matched.append(line)
skills = (matched + [s for s in P.get("skills_verified", []) if s not in matched])[:6]

experience = [{"title": e["title"], "dates": e["dates"], "org": e["org"],
               "bullets": [b[0].upper() + b[1:] for b in e["verified_duties"]][:5]} for e in P["experience"]]

resume = {
    "work_rights_line": "Work rights: " + P["work_rights"]["statement"],
    "profile": P["career_summary"] + " " + P["availability"]["statement"],
    "skills": skills,
    "experience": experience,
    "certificates": P.get("certificates", []),
    "languages": P.get("languages"),
    "systems": P.get("systems"),
}
if P.get("checks_held"):
    resume["extra_line"] = {"label": "Checks", "text": "; ".join(P["checks_held"])}

paras = [
    f"I am writing to apply for the {role} role at {comp}. I am reliable, hardworking and keen to contribute to your team. {P['availability']['statement']}",
    P["cover_experience_paragraph"],
]
if matched:
    paras.insert(1, f"I noticed the role calls for {', '.join(k for k in d.get('keywords', [])[:3])}. These are strengths from my previous work.")
cover = {
    "recipient": ["Hiring Manager", comp, d.get("place", P["location"])],
    "subject": f"Application for {role}",
    "paragraphs": paras,
    "bullets": P.get("cover_strength_bullets", []),
    "closing": f"I have attached my resume and would welcome the chance to speak with you. You can contact me on {P['phone']} or at {P['email']}.",
}
job = {"slug": d["slug"], "date": date, "resume": resume, "cover": cover}
os.makedirs(os.path.join(HERE, "output", "jobs"), exist_ok=True)
path = os.path.join(HERE, "output", "jobs", f"{d['slug']}.json")
json.dump(job, open(path, "w"), indent=1)
print(path)
