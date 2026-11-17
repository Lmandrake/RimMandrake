#!/usr/bin/env python3
"""Rerun every offline test of Graffiti's version/test_table.json and compare with its recorded runs_today.
    python3 rerun_offline.py [--out reruns.jsonl] [--only T_A,T_B] [--append]
Verdicts first: a rerun's result class (PASS / FAIL) against the recorded one; then its last non-empty line (stdout, else
stderr) against the recorded `last`, timings masked, a recorded prefix accepted either way. Builds go to a private
WINBUILD_ROOT (default /mnt/d/ClaudeWork/rimmandrake/scratch/graffiti_blind_c2_rerun). Each test is capped at 500 s."""
import argparse, json, os, re, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TT = os.path.join(REPO, "design/concepts/Graffiti/version/test_table.json")
mask = lambda s: re.sub(r"\d+(\.\d+)? ?(ms|s)\b", "<t>", s or "").strip()
def last_line(txt):
    lines = [l for l in (txt or "").splitlines() if l.strip()]
    return lines[-1].strip() if lines else ""
ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl")); ap.add_argument("--only", default="")
ap.add_argument("--append", action="store_true")
a = ap.parse_args(); only = set(filter(None, a.only.split(",")))
env = dict(os.environ); env.setdefault("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/graffiti_blind_c2_rerun")
tests = json.load(open(TT))["tests"]; rows = []
for k, v in tests.items():
    if v.get("kind") != "offline" or (only and k not in only): continue
    rec = v.get("runs_today") or {}; t0 = time.time()
    try:
        p = subprocess.run(v["command"], shell=True, cwd=REPO, capture_output=True, text=True, timeout=500, env=env)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = -9, (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT 500 s"
    got = "PASS" if rc == 0 else "FAIL"; want = "PASS" if rec.get("result") == "PASS" else "FAIL"
    ll = last_line(out) or last_line(err); rl = (rec.get("last") or "").strip()
    m1, m2 = mask(ll), mask(rl)
    row = {"test": k, "command": v["command"], "rc": rc, "seconds": round(time.time() - t0, 2), "result": got,
           "recorded_result": rec.get("result"), "recorded_rc": rec.get("rc"), "last": ll[:400], "recorded_last": rl[:400],
           "recorded_at": rec.get("at"), "result_matches": got == want,
           "last_matches": bool(m1 == m2 or (m2 and m1.startswith(m2)) or (m1 and m2.startswith(m1)))}
    row["match"] = row["result_matches"] and row["last_matches"]; rows.append(row)
    print(k, got, "rc", rc, round(time.time() - t0, 1), "s", flush=True)
with open(a.out, "a" if a.append else "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
print("RERUN", sum(r["match"] for r in rows), "of", len(rows), "match;", sum(r["result_matches"] for r in rows), "same result ->", a.out)
for r in rows:
    if not r["match"]: print("DIFF", r["test"], r["result"], "vs", r["recorded_result"], "|", r["last"][:200], "| was:", r["recorded_last"][:200])
