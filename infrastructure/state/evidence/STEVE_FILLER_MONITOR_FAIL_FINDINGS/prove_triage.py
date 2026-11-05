#!/usr/bin/env python3
"""Proof for STEVE_FILLER_MONITOR_FAIL_FINDINGS: every FAIL-row finding this host carries is triaged on the ledger.

The set is every finding event whose `from` is STEVE_FILLER_MONITOR_FAIL_FINDINGS/run-N@..., by name. Each passes only
if (a) its LATEST finding event (by tsn) has a type other than UNTRIAGED, so a re-open to UNTRIAGED goes red, and
(b) a TRACKED finding names, in its reason, an item that a spawn/file event on the ledger created from a finding of
this host, so TRACKED-into-nothing goes red. Sanity floor: at least MIN findings (runs 1-4 hold 14), so a blind
instrument cannot pass on an empty set. Exit 0 = all hold, 1 = not.
Usage: prove_triage.py [ledger_events_dir]   (default infrastructure/state/ledger/events)
"""
import glob, json, os, sys

HOST, MIN = "STEVE_FILLER_MONITOR_FAIL_FINDINGS/run-", 14
d = sys.argv[1] if len(sys.argv) > 1 else "infrastructure/state/ledger/events"
files = glob.glob(os.path.join(d, "*.jsonl"))
if not files:
    print("UNMEASURED: no ledger shards under", d); sys.exit(1)
L = [json.loads(l) for f in files for l in open(f) if l.strip()]
F = [e for e in L if e.get("event") == "finding" and str(e.get("from", "")).startswith(HOST)]
names = sorted({e.get("name") for e in F})
created = {}                                   # item id -> finding it came from
for e in L:
    if e.get("event") in ("spawn", "file"):
        iid = e.get("name") if e.get("event") == "spawn" else e.get("id")
        if iid and e.get("from"):
            created[iid] = e.get("from")
bad = []
if len(names) < MIN:
    bad.append(("<set>", "only %d findings hosted here, expected >= %d" % (len(names), MIN)))
for n in names:
    last = sorted((e for e in F if e.get("name") == n), key=lambda e: e.get("tsn", 0))[-1]
    t = last.get("type")
    if t in (None, "UNTRIAGED"):
        bad.append((n, "latest type %s" % t)); continue
    if t == "TRACKED":
        why = last.get("why", "")
        hit = [i for i in created if i in why and created[i] in names]
        if not hit:
            bad.append((n, "TRACKED but names no item the ledger created from this host: %r" % why[:120])); continue
        print("ok", n, "TRACKED ->", hit[0])
    else:
        print("ok", n, t)
print("findings:", len(names), "untriaged:", bad)
sys.exit(0 if not bad else 1)
