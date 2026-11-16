#!/usr/bin/env python3
"""Rerun the offline tests of GimmeSomeSlack's version/test_table.json and compare with their recorded runs_today.
    python3 rerun_offline.py [--out reruns.jsonl] [--only T_A,T_B] [--skip T_C] [--append]
A test whose command equals one already rerun in this call reuses that run (the table's `via`).
A rerun MATCHES when its verdict (PASS / FAIL by rc) equals the recorded one and its last non-empty line (stdout, else
stderr) starts with the recorded `last` or the recorded one starts with it (timings masked: the recorded line may be
cut short or come from the other stream)."""
import argparse, json, os, re, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TT = os.path.join(REPO, "design/concepts/GimmeSomeSlack/version/test_table.json")
mask = lambda s: re.sub(r"\d+\.\d+ ?s\b|\d+(\.\d+)? ?(ms|s)\b", "<t>", s or "").strip()


def last_line(txt):
    lines = [l for l in (txt or "").splitlines() if l.strip()]
    return lines[-1].strip() if lines else ""


ap = argparse.ArgumentParser()
ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl")); ap.add_argument("--only", default="")
ap.add_argument("--skip", default=""); ap.add_argument("--append", action="store_true")
a = ap.parse_args(); only = set(filter(None, a.only.split(","))); skip = set(filter(None, a.skip.split(",")))
tests = json.load(open(TT))["tests"]; rows = []; by_cmd = {}
for k, v in tests.items():
    if v.get("kind") != "offline" or (only and k not in only) or k in skip: continue
    rec = v.get("runs_today", {}) or {}
    if v["command"] in by_cmd:
        p, secs = by_cmd[v["command"]]
    else:
        t0 = time.time()
        try:
            p = subprocess.run(v["command"], shell=True, cwd=REPO, capture_output=True, text=True, timeout=530)
        except subprocess.TimeoutExpired:
            p = subprocess.CompletedProcess(v["command"], 124, "", "TIMEOUT after 530 s")
        secs = round(time.time() - t0, 2); by_cmd[v["command"]] = (p, secs)
    got = "PASS" if p.returncode == 0 else "FAIL"; want = "PASS" if rec.get("result") == "PASS" else "FAIL"
    ll = last_line(p.stdout) or last_line(p.stderr)
    rl = (rec.get("last") or "").strip()
    lm = bool(rl) and (mask(ll).startswith(mask(rl)) or mask(rl).startswith(mask(ll)) or mask(rl) in mask(p.stdout + p.stderr))
    row = {"test": k, "command": v["command"], "rc": p.returncode, "seconds": secs, "result": got,
           "recorded_result": rec.get("result"), "recorded_rc": rec.get("rc"), "last": ll[:300], "recorded_last": rl[:300],
           "recorded_at": rec.get("at"), "known_red": v.get("known_red"), "result_matches": got == want, "last_matches": lm}
    row["match"] = row["result_matches"] and row["last_matches"]; rows.append(row)
with open(a.out, "a" if a.append else "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
print("RERUN", sum(r["match"] for r in rows), "of", len(rows), "match;", sum(r["result_matches"] for r in rows), "same verdict ->", a.out)
for r in rows:
    if not r["match"]: print("DIFF", r["test"], r["result"], "vs", r["recorded_result"], "|", r["last"][:150], "| was:", r["recorded_last"][:150])
