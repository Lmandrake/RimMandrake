#!/usr/bin/env python3
"""Rerun offline tests of FlowWorks' version/test_table.json and compare with their recorded runs_today.
    python3 rerun_offline.py --only T_A,T_B [--out reruns.jsonl]
Rows MERGE into --out by test id (run in batches under the 540 s command bound). A rerun matches when its verdict
(rc 0 = PASS) equals the recorded one and its last non-empty line equals the recorded `last` or starts with it (the
recorded one may be cut short), timings and counts of filtered-out cases masked. A test with no command is written
UNRUN (not_rerunnable)."""
import argparse, json, os, re, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TT = os.path.join(REPO, "design/concepts/FlowWorks/version/test_table.json")
mask = lambda s: re.sub(r"\d+\.\d+ ?s\b|\d+(\.\d+)? ?(ms|s)\b|/tmp/\S+|/home/\S+|\d+ filtered out", "<x>", s or "").strip()
def last_line(txt):
    lines = [l for l in (txt or "").splitlines() if l.strip()]
    return lines[-1].strip() if lines else ""
ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl")); ap.add_argument("--only", required=True)
ap.add_argument("--timeout", type=int, default=520)
a = ap.parse_args(); only = [x for x in a.only.split(",") if x]
tests = json.load(open(TT))["tests"]
old = {}
if os.path.exists(a.out):
    for l in open(a.out):
        if l.strip(): r = json.loads(l); old[r["test"]] = r
for k in only:
    v = tests[k]; rec = v.get("runs_today", {}) or {}
    if not v.get("command"):
        old[k] = {"test": k, "command": None, "result": "UNRUN", "recorded_result": rec.get("result") or "UNRUN", "last": "not_rerunnable: no command (" + str(v.get("file")) + ")",
                  "recorded_last": rec.get("why") or "", "last": "not_rerunnable", "match": (rec.get("result") in (None, "UNRUN")), "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        continue
    t0 = time.time()
    try:
        p = subprocess.run(v["command"], shell=True, cwd=REPO, capture_output=True, text=True, timeout=a.timeout)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = -9, (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT"
    got = "PASS" if rc == 0 else "FAIL"; want = rec.get("result")
    ll = last_line(out) or last_line(err); rl = (rec.get("last") or "").strip()
    lm = mask(ll) == mask(rl) or (rl and mask(ll).startswith(mask(rl))) or (rl and mask(rl).startswith(mask(ll)) and ll)
    old[k] = {"test": k, "command": v["command"], "rc": rc, "seconds": round(time.time() - t0, 2), "result": got, "recorded_result": want,
              "recorded_rc": rec.get("rc"), "last": ll[:400], "recorded_last": rl[:400], "result_matches": got == want, "last_matches": bool(lm),
              "match": got == want and bool(lm), "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
with open(a.out, "w") as f:
    for r in old.values(): f.write(json.dumps(r) + "\n")
for k in only:
    r = old[k]; print(("MATCH" if r["match"] else "DIFF "), k, r["result"], "vs", r["recorded_result"], "|", r["last"][:160])
