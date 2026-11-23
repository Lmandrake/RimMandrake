#!/usr/bin/env python3
"""Rerun the offline and record tests of Pyrelands' test_table.json with their recorded commands; compare with runs_today.
    python3 rerun_offline.py [--tests T_A,T_B | --deciders | --rest] [--out reruns.jsonl] [--append]
--deciders: the tests that decide an offline bar (proves_at 2 or 4-5); --rest: every other offline/record test.
A row: test, result (PASS rc 0 | FAIL rc non-zero | TIMEOUT | NOT_RUN), rc, recorded_result, last, recorded_last, match
(verdicts equal, and the recorded last line a prefix of ours or ours of it, whitespace-normalised). Each run gets a private
WINBUILD_ROOT so a C# selftest never shares a staging folder. Exit 0 when every rerun matches, 1 otherwise."""
import argparse, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = os.path.join(REPO, "design/concepts/Pyrelands/version/test_table.json")


def norm(s):
    return re.sub(r"\d+(\.\d+)?s\b", "<t>", " ".join((s or "").split()))  # timings masked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests")
    ap.add_argument("--deciders", action="store_true")
    ap.add_argument("--rest", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl"))
    ap.add_argument("--append", action="store_true")
    ap.add_argument("--timeout", type=int, default=480)
    a = ap.parse_args()
    t = json.load(open(TABLE))
    tests = t["tests"]
    deciders = []
    for b in t["bars"]:
        if str(b.get("proves_at")) in ("2", "4-5"):
            deciders += [d for d in b["decides"] if d not in deciders]
    if a.tests:
        names = a.tests.split(",")
    elif a.deciders:
        names = deciders
    else:
        names = [k for k, v in tests.items() if v.get("kind") in ("offline", "record") and (not a.rest or k not in deciders)]
    rows = []
    for n in names:
        v = tests[n]
        rt = v.get("runs_today") or {}
        rec_res, rec_last = rt.get("result") or ("PASS" if rt.get("rc") == 0 else "FAIL"), rt.get("last") or ""
        cmd = v.get("command")
        if not cmd:
            rows.append({"test": n, "command": None, "result": "NOT_RUN", "rc": None, "recorded_result": rec_res, "last": "no command in the table",
                         "recorded_last": rec_last, "match": False})
            continue
        env = dict(os.environ, WINBUILD_ROOT="/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c6_rerun/" + n)
        os.makedirs(env["WINBUILD_ROOT"], exist_ok=True)
        t0 = time.time()
        try:
            r = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=a.timeout, env=env)
            rc, out = r.returncode, (r.stdout + "\n" + r.stderr)
            res = "PASS" if rc == 0 else "FAIL"
        except subprocess.TimeoutExpired:
            rc, out, res = None, "", "TIMEOUT"
        lines = [l for l in r.stdout.splitlines() if l.strip()] if res != "TIMEOUT" else []
        last = lines[-1] if lines else ([l for l in out.splitlines() if l.strip()] or [""])[-1]
        a1, b1 = norm(last), norm(rec_last)
        same_line = bool(b1) and (a1.startswith(b1[:60]) or b1.startswith(a1[:60]) or b1 in norm(out))
        row = {"test": n, "command": cmd, "result": res, "rc": rc, "seconds": round(time.time() - t0, 1), "recorded_result": rec_res,
               "last": last[:300], "recorded_last": rec_last[:300], "match": res == rec_res and (same_line or not b1),
               "decides_offline_bar": n in deciders}
        rows.append(row)
        print(n, res, "match" if row["match"] else "MISMATCH", last[:120], flush=True)
    with open(a.out, "a" if a.append else "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    sys.exit(0 if all(r["match"] for r in rows) else 1)


main()
