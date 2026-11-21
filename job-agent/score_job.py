#!/usr/bin/env python3
"""Usage: python3 score_job.py '{"age_days":2,"distance_km":12,"pay":34.76,"christmas":true,"fit":2,"qualifies":true}'
fit: 0 poor, 1 ok, 2 good, 3 excellent (retail/customer service/hospitality/warehouse entry-level = 2-3).
Apply only when apply=true. Work through jobs in descending score."""
import sys, json
d = json.loads(sys.argv[1])
if not d.get("qualifies", True): print(json.dumps({"score": -100, "apply": False, "why": "does not qualify (requirements/visa/etc)"})); sys.exit()
mp = d.get("min_pay", 30)
age = d.get("age_days"); pay = d.get("pay"); dist = d.get("distance_km")
s = 0; why = []
rec = 40 if age is not None and age <= 1 else 30 if age is not None and age <= 3 else 20 if age is not None and age <= 7 else 8 if age is not None and age <= 14 else 0 if age is not None else 10
s += rec; why.append(f"recency {rec}")
if d.get("christmas"): s += 20; why.append("christmas/seasonal +20")
p = (15 if pay and pay >= mp + 5 else 10 if pay and pay >= mp else -50 if pay else 6); s += p; why.append(f"pay {p}")
ds = (15 if dist is not None and dist <= 15 else 10 if dist is not None and dist <= 30 else 5 if dist is not None and dist <= 60 else -50 if dist is not None else 5); s += ds; why.append(f"distance {ds}")
f = {0: -20, 1: 0, 2: 6, 3: 10}.get(int(d.get("fit", 1)), 0); s += f; why.append(f"fit {f}")
print(json.dumps({"score": s, "apply": s >= 45, "why": ", ".join(why)}))
