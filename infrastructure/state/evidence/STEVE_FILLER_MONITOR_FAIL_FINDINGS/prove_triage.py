#!/usr/bin/env python3
"""Proof for STEVE_FILLER_MONITOR_FAIL_FINDINGS: run-1's four FAIL-row findings are triaged on the ledger.

Each finding passes only if (a) its LATEST finding event (by tsn) has a type other than UNTRIAGED, so a later
re-open to UNTRIAGED goes red, and (b) a TRACKED finding names, in its reason, an item that a spawn/file event on
the ledger created from that finding, so TRACKED-into-nothing goes red. Exit 0 = all four hold, 1 = not.
Usage: prove_triage.py [ledger_events_dir]   (default infrastructure/state/ledger/events)
"""
import glob, json, os, sys

N = ["FLOWWORKS_H6_PLUMP_WITHIN_TRANSITION_FAILS_D73263", "FLOWWORKS_M2_GAP_WALLED_REROUTES_FAILS_D73263",
     "FLOWWORKS_CR2_TRAIL_FOLLOWS_WALK_FAILS_D73263", "FLOWWORKS_SL3_HOSES_AND_REEL_STYLES_SURVIVE_FAILS_D73263"]
d = sys.argv[1] if len(sys.argv) > 1 else "infrastructure/state/ledger/events"
files = glob.glob(os.path.join(d, "*.jsonl"))
if not files:
    print("UNMEASURED: no ledger shards under", d); sys.exit(1)
L = [json.loads(l) for f in files for l in open(f) if l.strip()]
created = {}                                   # item id -> finding it came from
for e in L:
    if e.get("event") in ("spawn", "file"):
        iid = e.get("name") if e.get("event") == "spawn" else e.get("id")
        if iid:
            created[iid] = e.get("from") or created.get(iid)
bad = []
for n in N:
    fs = sorted((e for e in L if e.get("event") == "finding" and e.get("name") == n), key=lambda e: e.get("tsn", 0))
    if not fs:
        bad.append((n, "no finding event at all")); continue
    last = fs[-1]
    t = last.get("type")
    if t in (None, "UNTRIAGED"):
        bad.append((n, "latest type %s" % t)); continue
    if t == "TRACKED":
        why = last.get("why", "")
        hit = [i for i in created if i in why and created[i] == n]
        if not hit:
            bad.append((n, "TRACKED but names no item the ledger created from it: %r" % why[:120])); continue
        print("ok", n, "TRACKED ->", hit[0])
    else:
        print("ok", n, t)
print("untriaged:", bad)
sys.exit(0 if not bad else 1)
