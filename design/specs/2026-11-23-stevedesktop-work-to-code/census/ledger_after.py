#!/usr/bin/env python3
"""ledger_after.py - for each job a person or agent or the visit feed asked for: is its job id in any ledger event written
after it finished, and by whom (a seat, or only the RUNNER program)? A note a seat wrote without the id is not seen."""
import collections, glob, json, re, subprocess
from common import records, ts
ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
pat = re.compile(r"J2026\d{4}T\d{6}Z-[0-9a-f]{6}"); E = collections.defaultdict(list)
for f in glob.glob(ROOT + "/infrastructure/state/ledger/events/*.jsonl"):
    for l in open(f, errors="replace"):
        ids = set(pat.findall(l))
        if ids:
            e = json.loads(l)
            for i in ids: E[i].append((e.get("seat"), ts(e["ts"])))
R, _ = records(); C = collections.Counter(); GONE = ts("2026-11-19T02:19:39Z")     # b28e0d6975 deleted the retired relentless_game.py
for d in R:
    j = d["job"]
    if "filler" in str(j["requested_by"]): continue
    kind = "proofs" if j["selector"].get("proofs") else "visit" if j["requested_by"] == "BENCH.visit" else "modcheck"
    h = {s for s, t in E[j["id"]] if t >= d["_fin"]}
    who = "a seat" if h - {"RUNNER"} else "RUNNER program only" if h else "NONE"
    C[(d["_state"], "after 11-18" if d["_fin"] > GONE else "to 11-18", kind, who)] += 1
for k, v in sorted(C.items()): print(v, k)
for s in ("done", "quarantined"):
    t = collections.Counter()
    for k, v in C.items():
        if k[0] == s: t[k[3]] += v
    print(s, dict(t))
