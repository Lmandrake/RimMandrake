#!/usr/bin/env python3
"""Rerun Pyrelands' offline and record tests from version/test_table.json with their recorded commands; compare with runs_today.
    python3 rerun_offline.py [--only T_A,T_B] [--out reruns.jsonl] [--append]
One row per test: test, result, recorded_result, last, recorded_last, match (verdicts first; a recorded last line may be a
prefix of, or cut from, the rerun's). Exit 0 = every rerun matched its recorded result."""
import argparse, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = os.path.join(REPO, "design/concepts/Pyrelands/version/test_table.json")
ap = argparse.ArgumentParser()
ap.add_argument("--only", default="")
ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl"))
ap.add_argument("--append", action="store_true")
ap.add_argument("--timeout", type=int, default=500)
a = ap.parse_args()
tests = json.load(open(TABLE))["tests"]
only = [x for x in a.only.split(",") if x]
todo = [k for k, v in tests.items() if v.get("kind") in ("offline", "record") and (not only or k in only)]
rows, bad = [], 0
for k in todo:
    v = tests[k]
    rt = v.get("runs_today") or {}
    t0 = time.time()
    try:
        p = subprocess.run(v["command"], shell=True, cwd=REPO, capture_output=True, text=True, timeout=a.timeout)
        rc, out = p.returncode, (p.stdout.strip().splitlines() or p.stderr.strip().splitlines() or [""])
        last = out[-1]
    except subprocess.TimeoutExpired:
        rc, last = -9, "TIMEOUT after %ss" % a.timeout
    result = "PASS" if rc == 0 else "FAIL"
    rec_last = rt.get("last") or ""
    same_line = rec_last.strip() == last.strip() or last.strip().startswith(rec_last.strip()[:60]) or rec_last.strip() in last
    match = result == rt.get("result")
    row = {"test": k, "command": v["command"], "rc": rc, "result": result, "recorded_result": rt.get("result"), "last": last[:400],
           "recorded_last": rec_last[:400], "last_line_same": same_line, "match": match, "seconds": round(time.time() - t0, 2),
           "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rows.append(row)
    bad += not match
    print(("MATCH " if match else "MISMATCH ") + k, result, last[:160], flush=True)
with open(a.out, "a" if a.append else "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print("RERUN %d of %d matched -> %s" % (len(rows) - bad, len(rows), a.out))
sys.exit(1 if bad else 0)
