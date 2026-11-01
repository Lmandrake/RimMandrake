#!/usr/bin/env python3
"""Proof of CANON_FAUNA_FLORA_GPT_REVIEW_1 against its filing criteria; offline, exit 0 only if all hold.
usage: check_review_complete.py"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(LIB, "..", "..", ".."))
bad = []
def need(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok: bad.append(msg)
slugs = open(os.path.join(HERE, "REVIEWED_SLUGS.txt")).read().split()
need(len(slugs) == 119, f"{len(slugs)} reviewed slugs, spec says 119")
small = [n for n in range(1, 13) if os.path.getsize(os.path.join(HERE, f"batch_{n:02d}.md")) < 2000]
need(not small, f"12 GPT batches on disk, none a stub {small}")
log = open(os.path.join(HERE, "VERIFICATION_LOG.md"), encoding="utf-8").read()
need(len(re.findall(r"^## Batch \d\d$", log, re.M)) == 12, "verification log holds all 12 batches")
logged = {m.group(1) for m in re.finditer(r"^\| ([a-z_]+) \|", log, re.M)}
LOG_ALIAS = {"faascalefish": "faa"}  # the log used the short name
miss = [s for s in slugs if LOG_ALIAS.get(s, s) not in logged]
need(not miss, f"every reviewed entry has verification rows; missing: {miss}")
src = open(os.path.join(HERE, "MUSTSHOW_PROPOSALS.md"), encoding="utf-8").read()
want = {(e.split("\n")[0].strip(), i) for e in re.split(r"^### ", src, flags=re.M)[1:] for i, _ in enumerate(re.findall(r"^- .*$", e, re.M))}
tri = json.load(open(os.path.join(HERE, "MUSTSHOW_TRIAGE.json"), encoding="utf-8"))
rows = tri["rows"]
need({(r["entry"], r["n"]) for r in rows} == want, f"every one of {len(want)} proposals has a disposition")
need(all(r["disposition"] in ("APPLIED", "MET", "REJECTED", "OWNER") and r["why"] for r in rows), "each disposition is valid and reasoned")
gone = []
for r in rows:
    if r["disposition"] == "APPLIED":
        t = open(os.path.join(LIB, r["entry"], "description.md"), encoding="utf-8").read()
        m = re.search(r"^## Must show\n(.*?)(?=^## )", t, re.M | re.S)
        if not m or r["applied_text"] not in m.group(1): gone.append(r["entry"])
need(not gone, f"each applied edit is inside its entry's Must show; missing: {gone}")
flagged = [r for r in rows if r["disposition"] == "OWNER"]
ledger = "".join(open(os.path.join(ROOT, "infrastructure/state/ledger/events", f), errors="ignore").read() for f in os.listdir(os.path.join(ROOT, "infrastructure/state/ledger/events")) if f.endswith(".jsonl"))
need(tri["owner_item"] in ledger and flagged, f"{len(flagged)} ruling conflicts flagged to the owner in {tri['owner_item']}")
c = json.load(open(os.path.join(HERE, "census_no_entry.json")))
need(c["races"] > 500 and len(c["matched"]) > 100, f"census saw {c['races']} races, joined {len(c['matched'])} to entries (instrument can see)")
for known in ("RSW_Tauntaun", "RSW_Bantha", "RSW_Wampa"):
    need(known in c["matched"], f"sanity probe: {known} joins to an entry")
md = open(os.path.join(HERE, "CENSUS_NO_ENTRY.md"), encoding="utf-8").read()
miss = [r["defName"] for r in c["canon_named_no_entry"] if r["defName"] not in md]
need(not miss and "UNJUDGED" not in md, "every canon-named race is in CENSUS_NO_ENTRY.md, judged")
r = subprocess.run([sys.executable, os.path.join(HERE, "census_no_entry.py")], capture_output=True, text=True)
c2 = json.load(open(os.path.join(HERE, "census_no_entry.json")))
need(r.returncode == 0 and c2 == c, "census regenerates identically from src/ and the cached wiki answers")
print("PROVEN" if not bad else f"{len(bad)} FAILED")
sys.exit(1 if bad else 0)
