#!/usr/bin/env python3
"""windows.py - ledger `verify` events (seat RUNNER) that rest on a job run inside a machine-fault window, and whether the
event says so. Join: the attempt id in the event text. Control: attempts of jobs in no window must also be found."""
import collections, json, subprocess, re
from common import records
ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
R, _ = records()
cls = {}
for d in R:
    if d["result"].get("outcome") != "DONE": continue
    m = (d.get("fault_window") or {}).get("mode")
    cls[d["result"]["attempt"]] = "quarantined" if d["_state"] == "quarantined" else "kept, in a window (%s)" % m if m else "kept, no window"
C = collections.Counter(); say = collections.Counter(); jobs = collections.defaultdict(set)
for l in open(ROOT + "/infrastructure/state/ledger/events/RUNNER.jsonl", errors="replace"):
    if '"verify"' not in l: continue
    e = json.loads(l)
    if e.get("event") != "verify": continue
    for a in re.findall(r"J\d{8}T\d{6}Z-[0-9a-f]{6}\.a\d", l):
        if a in cls:
            C[(cls[a], e.get("result"))] += 1; jobs[cls[a]].add(a); say[(cls[a], "names the window" if re.search(r"window|quarantin", l) else "does not")] += 1; break
for k, v in sorted(C.items()): print(v, k)
print({k: len(v) for k, v in jobs.items()}, dict(say))
