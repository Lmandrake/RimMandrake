#!/usr/bin/env python3
"""Rerun the offline tests of ExplosiveKnockback 0.2.0 with their recorded commands (version/test_table.json) and compare.
    python3 rerun_offline.py [--only T_A,T_B] [--skip T_C] [--out reruns.jsonl]
One row per test: test, result, recorded_result, last, recorded_last, match (verdict equal, and the last line equal or a
prefix either way), rc, seconds, command. A test sharing a command with one already run reuses that run.
Exit 0 = every row matches; 1 = a mismatch."""
import argparse, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = os.path.join(REPO, "design/concepts/ExplosiveKnockback/version/test_table.json")


def last_line(text):
    ls = [l.strip() for l in text.splitlines() if l.strip()]
    return ls[-1] if ls else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--skip", default="")
    ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl"))
    a = ap.parse_args()
    tests = json.load(open(TABLE))["tests"]
    only = [t for t in a.only.split(",") if t]
    skip = set(t for t in a.skip.split(",") if t)
    ids = only or sorted(k for k, v in tests.items() if v.get("kind") == "offline" and "python3" in str(v.get("command", "")))
    cache, rows = {}, []
    for t in ids:
        if t in skip:
            continue
        v = tests[t]
        cmd = v["command"]
        rec = v.get("runs_today") or {}
        if cmd not in cache:
            t0 = time.time()
            try:
                # hang guard: the slowest recorded offline test took 315 s (T_SITUATION_MAP_OFFLINE)
                p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=3300)
                rc, out = p.returncode, p.stdout + "\n" + p.stderr
            except subprocess.TimeoutExpired:
                rc, out = 124, "TIMEOUT after 3300 s"
            cache[cmd] = (rc, last_line(p.stdout) or last_line(out) if rc != 124 else out, round(time.time() - t0, 2), out)
        rc, last, secs, out = cache[cmd]
        res = "PASS" if rc == 0 else "FAIL"
        rlast = rec.get("last", "")
        norm = lambda x: re.sub(r"\d+\.\d+s\b", "<t>s", x)   # a run's own timing is not a verdict
        lmatch = norm(last) == norm(rlast) or last.startswith(rlast) or rlast.startswith(last) or rlast in out
        row = {"test": t, "result": res, "recorded_result": rec.get("result"), "last": last, "recorded_last": rlast,
               "match": res == rec.get("result") and lmatch, "verdict_match": res == rec.get("result"), "rc": rc, "seconds": secs, "command": cmd}
        rows.append(row)
        print("%-32s %s rec %s match %s  %s" % (t, res, rec.get("result"), row["match"], last[:100]), flush=True)
    mode = "a" if os.path.exists(a.out) and only else "w"
    with open(a.out, mode) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    bad = [r["test"] for r in rows if not r["match"]]
    print("RERUNS %d, matching %d, mismatched %s" % (len(rows), len(rows) - len(bad), bad or "none"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
