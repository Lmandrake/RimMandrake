#!/usr/bin/env python3
"""visits.py - the jobs the visit feed sent (requested_by BENCH.visit): what each measured, and whether its job id is in any
visit folder (design/concepts/*/version/in_game). Control: the same search finds the ids of older jobs in those folders."""
import collections, glob, os, re, subprocess
from common import records, ts
ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
pat = re.compile(r"J2026\d{4}T\d{6}Z-[0-9a-f]{6}"); ids = collections.Counter(); steve = 0; rows = 0
for f in glob.glob(ROOT + "/design/concepts/*/version/in_game/**/*", recursive=True):
    if os.path.isfile(f) and f.endswith((".md", ".jsonl", ".json", ".log", ".txt", ".csv")):
        t = open(f, errors="replace").read(); ids.update(set(pat.findall(t)))
        if os.path.basename(f) == "rows.jsonl": rows += t.count("\n"); steve += len(re.findall(r'"game":\s*"(stevedesktop|Steve\w+)', t))
R, _ = records(); V = [d for d in R if d["job"]["requested_by"] == "BENCH.visit"]
c = lambda d: d["result"].get("counts") or {}
print("visit jobs", len(V), collections.Counter(d["result"]["outcome"] for d in V), "with a PASS or FAIL row", sum(bool(c(d).get("PASS") or c(d).get("FAIL")) for d in V))
print("PASS rows", sum(c(d).get("PASS", 0) for d in V), "FAIL", sum(c(d).get("FAIL", 0) for d in V), "UNMEASURED", sum(c(d).get("UNMEASURED", 0) for d in V), "NOT_RUN", sum(c(d).get("NOT_RUN", 0) for d in V))
print("visit jobs named in a visit folder", sum(d["job"]["id"] in ids for d in V), "| all job ids in visit folders (control)", len(ids), "| rows in rows.jsonl", rows, "of them with game stevedesktop", steve)
n = collections.Counter((d["job"]["mod"], tuple(d["job"]["selector"]["chains"])) for d in V)
print("chain sets sent more than once:", {k[0] + ":" + ",".join(k[1])[:60]: v for k, v in n.items() if v > 1})
