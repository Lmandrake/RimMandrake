#!/usr/bin/env python3
"""Rerun every kind=offline test of GimmeSomeSlack's version/test_table.json and compare with its recorded runs_today.
    python3 rerun_offline.py [--out reruns.jsonl] [--only T_A,T_B] [--append]
A rerun MATCHES when its verdict (PASS / FAIL; known red counts as FAIL) equals the recorded one and the recorded `last`
line, timings masked, equals the rerun's last line or is a prefix of it (the recorded line may be cut short or taken from
stderr, so stderr's last line is accepted too). A test whose command another row already ran (via) reuses that run."""
import argparse, json, os, re, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TT = os.path.join(REPO, "design/concepts/GimmeSomeSlack/version/test_table.json")
mask = lambda s: re.sub(r"\d+\.\d+s|\d+(\.\d+)? ?(ms|s)\b", "<t>", s or "").strip()
def last_line(txt):
    lines = [l for l in (txt or "").splitlines() if l.strip()]
    return lines[-1] if lines else ""
ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl")); ap.add_argument("--only", default="")
ap.add_argument("--append", action="store_true"); ap.add_argument("--timeout", type=int, default=530)
a = ap.parse_args(); only = set(filter(None, a.only.split(",")))
tests = json.load(open(TT))["tests"]; rows = []; ran = {}
for k, v in tests.items():
    if v.get("kind") != "offline" or (only and k not in only): continue
    rec = v.get("runs_today", {}); t0 = time.time(); cmd = v["command"]
    if cmd in ran: p, secs = ran[cmd]
    else:
        try: p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=a.timeout)
        except subprocess.TimeoutExpired as e: p = subprocess.CompletedProcess(cmd, 124, e.stdout or "", "TIMEOUT")
        secs = round(time.time() - t0, 2); ran[cmd] = (p, secs)
    got = "PASS" if p.returncode == 0 else "FAIL"; want = "PASS" if rec.get("result") == "PASS" else "FAIL"
    lo, le = last_line(p.stdout if isinstance(p.stdout, str) else ""), last_line(p.stderr if isinstance(p.stderr, str) else "")
    rl = mask(rec.get("last"))
    lm = any(rl and (mask(x) == rl or mask(x).startswith(rl) or rl.startswith(mask(x)) and len(mask(x)) > 10) for x in (lo, le))
    row = {"test": k, "command": cmd, "rc": p.returncode, "seconds": secs, "result": got, "recorded_result": rec.get("result"),
           "recorded_rc": rec.get("rc"), "last": (lo or le)[:300], "recorded_last": (rec.get("last") or "")[:300],
           "result_matches": got == want, "last_matches": lm, "known_red": v.get("known_red"), "partial": v.get("partial")}
    row["match"] = row["result_matches"] and row["last_matches"]; rows.append(row)
    print(("OK  " if row["match"] else "DIFF"), k, got, "rc", p.returncode, secs, "s |", row["last"][:120], flush=True)
with open(a.out, "a" if a.append else "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
print("RERUN", sum(r["match"] for r in rows), "of", len(rows), "match;", sum(r["result_matches"] for r in rows), "same verdict ->", a.out)
