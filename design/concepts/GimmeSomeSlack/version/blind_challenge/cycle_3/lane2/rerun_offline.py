#!/usr/bin/env python3
"""Rerun offline tests of version/test_table.json with their recorded commands and compare with runs_today.
    python3 rerun_offline.py [--out reruns.jsonl] [--only T_A,T_B] [--append]
Runs in batches (each call one foreground command under 540 s); --append keeps earlier rows, a later row for the same
test replaces an earlier one. A rerun MATCHES when its verdict (rc 0 = PASS) equals the recorded one, and its last
non-empty output line equals the recorded `last` or starts with it, or the recorded one is a prefix of it (timings and
check counts masked: the recorded line may be cut short or come from stderr). A test whose table row says `via` another
test with the same command reuses that run. C# builds stage under a private WINBUILD_ROOT."""
import argparse, json, os, re, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TT = os.path.join(REPO, "design/concepts/GimmeSomeSlack/version/test_table.json")
WROOT = "/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c3_rerun/"
mask = lambda s: re.sub(r"\d+(\.\d+)?", "<n>", (s or "").strip())
def last_line(txt):
    lines = [l for l in (txt or "").splitlines() if l.strip()]
    return lines[-1].strip() if lines else ""
ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl"))
ap.add_argument("--only", default=""); ap.add_argument("--append", action="store_true")
a = ap.parse_args(); only = [x for x in a.only.split(",") if x]
tests = json.load(open(TT))["tests"]
old = {}
if a.append and os.path.exists(a.out):
    for l in open(a.out):
        if l.strip(): r = json.loads(l); old[r["test"]] = r
done = {}
env = dict(os.environ, WINBUILD_ROOT=WROOT)
for k in (only or [k for k, v in tests.items() if v.get("kind") == "offline"]):
    v = tests[k]; rec = v.get("runs_today", {}) or {}
    if v["command"] in done:
        p, secs = done[v["command"]]
    else:
        t0 = time.time()
        try:
            p = subprocess.run(v["command"], shell=True, cwd=REPO, capture_output=True, text=True, timeout=530, env=env)
        except subprocess.TimeoutExpired:
            p = subprocess.CompletedProcess(v["command"], 124, "", "TIMEOUT 530 s")
        secs = round(time.time() - t0, 2); done[v["command"]] = (p, secs)
    got = "PASS" if p.returncode == 0 else "FAIL"; want = "PASS" if rec.get("result") == "PASS" else "FAIL"
    ll = last_line(p.stdout) or last_line(p.stderr); rl = (rec.get("last") or "").strip()
    def same(x): return bool(rl) and bool(x) and (mask(x) == mask(rl) or mask(x).startswith(mask(rl)) or mask(rl).startswith(mask(x)))
    lm = same(ll) or same(last_line(p.stderr)) or same(last_line(p.stdout))
    row = {"test": k, "command": v["command"], "rc": p.returncode, "seconds": secs, "result": got,
           "recorded_result": rec.get("result"), "recorded_rc": rec.get("rc"), "last": ll[:300], "recorded_last": rl[:300],
           "result_matches": got == want, "last_matches": lm, "recorded_at": rec.get("at"),
           "rerun_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    row["match"] = row["result_matches"] and row["last_matches"]
    old[k] = row
with open(a.out, "w") as f:
    for r in old.values(): f.write(json.dumps(r) + "\n")
rows = list(old.values())
print("RERUN", sum(r["match"] for r in rows), "of", len(rows), "match;", sum(r["result_matches"] for r in rows), "same verdict ->", a.out)
for r in rows:
    if not r["match"]: print("DIFF", r["test"], r["result"], "vs", r["recorded_result"], "|", r["last"][:150], "| was:", r["recorded_last"][:150])
