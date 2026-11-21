"""Shared fuzzy matching for company / job titles (used by tracker_add.py and the audit)."""
import re, difflib
STOP = {"pty","ltd","limited","group","australia","australian","aus","anz","the","and","co","company","corp","corporation","inc","retail","recruitment","recruit","consult","consulting","services","service","solutions","jobs","careers","hr","staffing","personnel","workforce","people","talent","hire","labour","labor","staff","partners","group","management","hospitality","kitchen"}
def norm_company(s):
    s = (s or "").lower()
    s = re.sub(r"\(.*?\)", " ", s)              # drop bracketed text
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    toks = [t for t in s.split() if t not in STOP]
    return " ".join(toks) or re.sub(r"[^a-z0-9]", "", (s or ""))
def same_company(a, b):
    na, nb = norm_company(a), norm_company(b)
    if not na or not nb: return False
    if na == nb or na.replace(" ", "") == nb.replace(" ", ""): return True
    ta, tb = set(na.split()), set(nb.split())
    if ta and tb and (ta <= tb or tb <= ta) and min(len(na), len(nb)) >= 4: return True
    return difflib.SequenceMatcher(None, na, nb).ratio() >= 0.86
def norm_title(s):
    s = re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower())
    return " ".join(t for t in s.split() if t not in {"the","a","an","and","or","for","at","in","of","vic","melbourne","casual","part","time","full"})
def same_title(a, b):
    na, nb = norm_title(a), norm_title(b)
    if not na or not nb: return False
    if na == nb: return True
    return difflib.SequenceMatcher(None, na, nb).ratio() >= 0.8

def norm_url(u):
    """Reduce a job link to a stable id so the same ad is recognised across tracking params."""
    u = (u or "").strip().lower()
    if not u: return ""
    for pat in (r"jk=([a-f0-9]{8,})", r"/job/(\d{6,})", r"/jobs/view/(\d{6,})", r"jobid=(\d{6,})", r"jobListingId=(\d{6,})", r"/(\d{7,})(?:[/?#]|$)", r"vjk=([a-f0-9]{8,})"):
        m = re.search(pat, u, re.I)
        if m: return m.group(1)
    return re.sub(r"[?#].*$", "", u).rstrip("/")
