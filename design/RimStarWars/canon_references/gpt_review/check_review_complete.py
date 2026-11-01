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
need(all(r["disposition"] in ("APPLIED", "MET", "REJECTED", "OWNER") for r in rows), "each disposition is valid")
# Judged one by one: no shared or short reason, no default in the tool, and MET points at text really in the entry.
whys = [r["why"] for r in rows]
need(len(set(whys)) == len(whys) and min(map(len, whys)) >= 30, f"every row has its own reason ({len(set(whys))} distinct of {len(whys)})")
tool = open(os.path.join(HERE, "triage_mustshow.py"), encoding="utf-8").read()
need("DEFAULT" not in tool and "no decision for" in tool, "triage tool has no default: an undecided bullet stops it")
entry = lambda s: open(os.path.join(LIB, s, "description.md"), encoding="utf-8").read()
must = lambda s: (re.search(r"^## Must show\n(.*?)(?=^## )", entry(s), re.M | re.S) or [None, ""])[1]
gone = [f"{r['entry']}#{r['n']}" for r in rows if r["disposition"] == "MET" and (not r.get("met_quote") or r["met_quote"] not in entry(r["entry"]))]
need(not gone, f"each MET row quotes text really in its entry; missing: {gone}")
gone = [r["entry"] for r in rows if r["disposition"] == "APPLIED" and r["applied_text"] not in must(r["entry"])]
need(not gone, f"each applied edit is inside its entry's Must show; missing: {gone}")
state = {(r["entry"], r["n"]): r["disposition"] for r in rows}
want_state = {("teemuss", 0): "APPLIED", ("uvak", 2): "APPLIED", ("worrt", 1): "APPLIED", ("coloclawfish", 3): "MET", ("kinrath", 1): "MET"}
need(all(state.get(k) == v for k, v in want_state.items()), "sanity probe: the five rows a blind checker named are not rejected")
flagged = [r for r in rows if r["disposition"] == "OWNER"]
events = []
evdir = os.path.join(ROOT, "infrastructure/state/ledger/events")
for f in os.listdir(evdir):
    if f.endswith(".jsonl"):
        for ln in open(os.path.join(evdir, f), errors="ignore"):
            if tri["owner_item"] in ln: events.append(json.loads(ln))
need(any(e.get("event") == "file" for e in events) and flagged, f"{len(flagged)} ruling conflicts flagged to the owner in {tri['owner_item']}")
filed = " ".join(e.get("spec", "") + " " + e.get("text", "") for e in events)
miss = [r["entry"] for r in flagged if r["entry"] not in filed]
need(not miss, f"each conflict is named in the decision item; missing: {miss}")
notes = [e for e in events if str(e.get("why", "")).startswith("delegated:")]
told = " ".join(json.dumps(e, ensure_ascii=False) for e in notes)
miss = sorted({r["entry"] for r in rows if r["disposition"] == "APPLIED" and r["entry"] not in told})
need(not miss, f"every applied edit has a delegated: ledger event on the decision item; missing: {miss}")
ruled_told = " ".join(json.dumps(e, ensure_ascii=False) for e in notes if "ruled" in str(e.get("text", "")))
miss = sorted({r["entry"] for r in rows if r["disposition"] == "APPLIED" and r["ruled_entry"] and r["entry"] not in ruled_told})
need(not miss, f"every edit on a ruled entry is flagged to the owner as such; missing: {miss}")
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
