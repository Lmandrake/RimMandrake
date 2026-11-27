#!/usr/bin/env python3
"""Rerun offline tests of FlowWorks' test_table.json with their recorded commands; compare with runs_today.

    python3 rerun_offline.py TEST_ID... [--out reruns.jsonl] [--append]

One row per test: test, result, recorded_result, last, recorded_last, match, rc, seconds, command, at.
match: the verdicts agree, and the recorded last line is a prefix of the new last line or the other way round, or both lines
carry the same counts (a recorded line may be cut short or come from stderr; FORMAT_NOTES trap d).
Each command runs with WINBUILD_ROOT set to this run's private folder (FORMAT_NOTES trap c). A test with no command is a row
with result UNRUN and the table's reason. Exit 0 = every rerun PASS; 1 = a rerun not PASS."""
import argparse, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = os.path.join(REPO, "design/concepts/FlowWorks/version/test_table.json")
WROOT = os.environ.get("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/flowworks_blind_c5_rerun")


def last_line(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return lines[-1] if lines else ""


def nums(s):
    return re.findall(r"\d+", s or "")


def cases_ran(s):
    m = re.search(r"(\d+) case\(s\)", s or "")
    return m.group(1) if m else None


def same(rl, last, text=""):
    """The recorded last line agrees with the new one: a prefix either way, found in the output, the same numbers, or (a
    selftest_flowworks_stock.py summary) the same count of cases run: its "N filtered out" grows as the suite grows."""
    if not rl:
        return True
    if last.startswith(rl[:60]) or rl.startswith(last[:60]) or rl in text or nums(rl) == nums(last):
        return True
    return cases_ran(rl) is not None and cases_ran(rl) == cases_ran(last)


def run(tid, t):
    rt = t.get("runs_today") or {}
    cmd = t.get("command")
    base = {"test": tid, "recorded_result": rt.get("result", "UNRUN" if not rt.get("ran") else None), "recorded_last": rt.get("last"),
            "command": cmd}
    if not cmd:
        return dict(base, result="UNRUN", last=t.get("runs_today", {}).get("why", "no command"), match=base["recorded_result"] == "UNRUN", rc=None, seconds=0)
    env = dict(os.environ, WINBUILD_ROOT=WROOT)
    t0 = time.time()
    try:
        p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
                           timeout=1500)  # a hang guard: the slowest decider recorded 264 s
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return dict(base, result="UNMEASURED", last="timed out at 1500 s (hang guard)", match=False, rc=None, seconds=1500)
    sec = round(time.time() - t0, 2)
    last = last_line(out) or last_line(err)
    if rt.get("last") and rt["last"] not in last and last_line(err) and rt["last"] in last_line(err):
        last = last_line(err)
    result = "PASS" if rc == 0 else "FAIL"
    rl = rt.get("last") or ""
    match = result == base["recorded_result"] and same(rl, last, out + err)
    return dict(base, result=result, last=last[:400], match=bool(match), rc=rc, seconds=sec,
                at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), tail=(out + err)[-1200:] if rc else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tests", nargs="+")
    ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl"))
    ap.add_argument("--append", action="store_true")
    ap.add_argument("--rematch", action="store_true", help="recompute match on the rows already in --out; run nothing")
    a = ap.parse_args()
    if a.rematch:
        rows = [json.loads(l) for l in open(a.out)]
        for r in rows:
            if r.get("rc") is not None:
                r["match"] = r["result"] == r["recorded_result"] and same(r.get("recorded_last"), r.get("last") or "")
        with open(a.out, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print("\n".join("%s %s match=%s" % (r["test"], r["result"], r["match"]) for r in rows))
        sys.exit(0)
    tab = json.load(open(TABLE))
    tests = {x["id"]: x for x in tab["tests"]} if isinstance(tab["tests"], list) else tab["tests"]
    rows = []
    for tid in a.tests:
        r = run(tid, tests[tid])
        rows.append(r)
        print(json.dumps({k: r[k] for k in ("test", "result", "recorded_result", "match", "rc", "seconds", "last")}), flush=True)
    with open(a.out, "a" if a.append else "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    sys.exit(0 if all(r["result"] == "PASS" for r in rows) else 1)


main()
