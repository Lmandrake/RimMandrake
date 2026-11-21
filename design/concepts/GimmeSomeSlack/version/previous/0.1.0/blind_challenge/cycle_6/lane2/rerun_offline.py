#!/usr/bin/env python3
"""Rerun the offline tests of GimmeSomeSlack's version/test_table.json and compare with each one's recorded runs_today.
    python3 rerun_offline.py [--out reruns.jsonl] [--only T_A,T_B] [--skip T_C,...] [--append]
Verdicts are compared first; the last line matches when the recorded `last` (timings masked) is a prefix of the rerun's
last stdout or stderr line, or the reverse (the recorded one may be cut short). --append adds rows so long tests can run
in separate foreground calls; a later row for the same test replaces an earlier one when read."""
import argparse, json, os, re, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TT = os.path.join(REPO, "design/concepts/GimmeSomeSlack/version/test_table.json")
mask = lambda s: re.sub(r"\d+\.\d+s|\d+(\.\d+)? ?(ms|s)\b|\d+(\.\d+)? s\b", "<t>", s or "").strip()
def last_line(txt):
    lines = [l for l in (txt or "").splitlines() if l.strip()]
    return lines[-1] if lines else ""
def last_match(got_lines, rec):
    r = mask(rec)
    return any(mask(g).startswith(r) or (r.startswith(mask(g)) and g) for g in got_lines if g is not None) if r else True
ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl"))
ap.add_argument("--only", default=""); ap.add_argument("--skip", default=""); ap.add_argument("--append", action="store_true")
a = ap.parse_args(); only = set(filter(None, a.only.split(","))); skip = set(filter(None, a.skip.split(",")))
tests = json.load(open(TT))["tests"]; rows = []
for k, v in tests.items():
    if v.get("kind") != "offline" or (only and k not in only) or k in skip: continue
    rec = v.get("runs_today") or {}; t0 = time.time()
    try:
        p = subprocess.run(v["command"], shell=True, cwd=REPO, capture_output=True, text=True, timeout=520)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = -9, (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT 520 s"
    got = "PASS" if rc == 0 else "FAIL"; want = "PASS" if rec.get("result") == "PASS" else "FAIL"
    lo, le = last_line(out), last_line(err)
    row = {"test": k, "command": v["command"], "rc": rc, "seconds": round(time.time() - t0, 2), "result": got,
           "recorded_result": rec.get("result"), "recorded_rc": rec.get("rc"), "last": (lo or le)[:300], "last_stderr": le[:200],
           "recorded_last": (rec.get("last") or "")[:300], "result_matches": got == want,
           "last_matches": last_match([lo, le], rec.get("last") or "")}
    row["match"] = row["result_matches"] and row["last_matches"]; rows.append(row)
    print(("SAME " if row["match"] else "DIFF ") + k, got, "vs", rec.get("result"), "|", row["last"][:120], flush=True)
with open(a.out, "a" if a.append else "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
print("RERUN", sum(r["match"] for r in rows), "of", len(rows), "match;", sum(r["result_matches"] for r in rows), "same result ->", a.out)
