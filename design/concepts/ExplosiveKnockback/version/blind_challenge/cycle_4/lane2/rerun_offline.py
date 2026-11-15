#!/usr/bin/env python3
"""Rerun every offline test of version/test_table.json and compare with its recorded runs_today.
    python3 rerun_offline.py [--out reruns.jsonl] [--only T_A,T_B]
A rerun MATCHES when its result class (PASS / FAIL) equals the recorded one (KNOWN RED counts as FAIL) and its
last non-empty stdout line equals the recorded `last` (timings masked) or starts with its first 120 characters. Cycle 4 copy of the cycle-1 tool (via cycles 2 and 3)."""
import argparse, json, os, re, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TT = os.path.join(REPO, "design/concepts/ExplosiveKnockback/version/test_table.json")
mask = lambda s: re.sub(r"\d+\.\d+s|\d+(\.\d+)? ?(ms|s)\b", "<t>", s or "").strip()
def last_line(txt):
    lines = [l for l in (txt or "").splitlines() if l.strip()]
    return lines[-1] if lines else ""
ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl")); ap.add_argument("--only", default="")
a = ap.parse_args(); only = set(filter(None, a.only.split(",")))
tests = json.load(open(TT))["tests"]; rows = []
for k, v in tests.items():
    if v.get("kind") != "offline" or (only and k not in only): continue
    rec = v.get("runs_today", {}); t0 = time.time()
    p = subprocess.run(v["command"], shell=True, cwd=REPO, capture_output=True, text=True, timeout=1800)
    got = "PASS" if p.returncode == 0 else "FAIL"; want = "PASS" if rec.get("result") == "PASS" else "FAIL"
    ll = last_line(p.stdout) or last_line(p.stderr)
    row = {"test": k, "command": v["command"], "rc": p.returncode, "seconds": round(time.time() - t0, 2), "result": got,
           "recorded_result": rec.get("result"), "recorded_rc": rec.get("rc"), "last": ll[:300], "recorded_last": (rec.get("last") or "")[:300],
           "result_matches": got == want,
           # a recorded last line may be truncated or taken from stderr: accept a recorded prefix (FORMAT_NOTES trap d)
           "last_matches": mask(ll) == mask(rec.get("last")) or (bool(mask(rec.get("last"))) and mask(ll).startswith(mask(rec.get("last"))[:120]))}
    row["match"] = row["result_matches"] and row["last_matches"]; rows.append(row)
with open(a.out, "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
print("RERUN", sum(r["match"] for r in rows), "of", len(rows), "match;", sum(r["result_matches"] for r in rows), "same result ->", a.out)
for r in rows:
    if not r["match"]: print("DIFF", r["test"], r["result"], "vs", r["recorded_result"], "|", r["last"][:150], "| was:", r["recorded_last"][:150])
