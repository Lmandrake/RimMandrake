#!/usr/bin/env python3
"""Rerun kind=offline tests of FlowWorks' version/test_table.json and compare with runs_today.
    python3 rerun_offline.py [--ids A,B] [--first ID] [--budget SECONDS] [--per SECONDS] [--build] [--out reruns.jsonl]
Appends one row per test to --out (a test already in the file is skipped, so calls can be chained under the 540 s
foreground limit). C# SelfTest commands (selftest_flowworks_stock.py) run with --no-build: the source is unchanged, so
one build (--build, or any earlier run) serves every glob; the full suite is never run in one command.
Row: id, command, result PASS|FAIL|TIMEOUT|UNRUN, rc, last, recorded_result, recorded_last, match, seconds.
match compares verdicts first, then accepts the recorded last line as a prefix of (or contained in) any of the last lines."""
import argparse, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = os.path.join(REPO, "design/concepts/FlowWorks/version/test_table.json")
STOCK = "selftest_flowworks_stock.py"


def recorded(rt):
    if not rt or not rt.get("ran"):
        return "UNRUN", ""
    rc = rt.get("rc")
    if rt.get("fail"):
        return "FAIL", rt.get("tail", "")
    return ("PASS" if rc == 0 else "FAIL"), rt.get("tail", "") or ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default=None)
    ap.add_argument("--budget", type=float, default=480)
    ap.add_argument("--per", type=float, default=300)
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl"))
    a = ap.parse_args()
    tests = json.load(open(TABLE))["tests"]
    ids = a.ids.split(",") if a.ids else [k for k, v in tests.items() if v.get("kind") == "offline"]
    done = set()
    if os.path.exists(a.out):
        done = {json.loads(l)["id"] for l in open(a.out) if l.strip()}
    env = dict(os.environ)
    env.setdefault("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/fw_blind_rerun/")
    t_start = time.time()
    built = not a.build
    for tid in ids:
        if tid in done:
            continue
        if time.time() - t_start > a.budget:
            print("BUDGET reached; next", tid)
            break
        v = tests[tid]
        cmd = v.get("command") or ""
        rres, rlast = recorded(v.get("runs_today"))
        if not cmd:
            row = dict(id=tid, command=None, result="UNRUN", rc=None, last="no command recorded", recorded_result=rres, recorded_last=rlast,
                       match=rres == "UNRUN", seconds=0)
        else:
            run = cmd
            if STOCK in cmd and "--no-build" not in cmd:
                run = cmd if not built else cmd.replace(STOCK, STOCK + " --no-build", 1)
                built = True
            t0 = time.time()
            try:
                p = subprocess.run(run, shell=True, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                   timeout=a.per, env=env)
                rc, out = p.returncode, (p.stdout + "\n" + p.stderr)
                res = "PASS" if rc == 0 else "FAIL"
            except subprocess.TimeoutExpired:
                rc, out, res = None, "", "TIMEOUT"
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            stdout_lines = [l.strip() for l in (p.stdout if rc is not None else "").splitlines() if l.strip()]
            last = stdout_lines[-1] if stdout_lines else (lines[-1] if lines else "")
            tail = lines[-12:]
            text_ok = (not rlast) or any(l.startswith(rlast[:120]) or rlast[:120] in l for l in tail) or rlast[:60] in out
            row = dict(id=tid, command=run, result=res, rc=rc, last=last[:400], recorded_result=rres, recorded_last=rlast[:400],
                       match=(res == rres) and text_ok, verdict_match=res == rres, seconds=round(time.time() - t0, 1))
        with open(a.out, "a") as f:
            f.write(json.dumps(row) + "\n")
        print(tid, row["result"], "rec", row["recorded_result"], "match" if row["match"] else "MISMATCH", row.get("seconds"))
    rows = [json.loads(l) for l in open(a.out) if l.strip()]
    print("RERUNS", len(rows), "of", len(ids), "matching", sum(r["match"] for r in rows), "verdict-matching", sum(r.get("verdict_match", r["match"]) for r in rows))


main()
