#!/usr/bin/env python3
"""Rerun every kind=offline test of Pyrelands' version/test_table.json with its recorded command; compare with runs_today.
    python3 rerun_offline.py [--only T_A,T_B] [--out reruns.jsonl]
Verdict first: PASS = rc 0, except T_SETTINGS_SCREENS (rc 1 by design: the shared suite) which is judged by its own
Pyrelands rows ("N rows for this mod, 0 red"). `last` = last non-empty stdout line (stderr if stdout is empty); a recorded
`last` matches when either is a prefix of the other. Exit 0 = every rerun verdict matches the record."""
import argparse, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = os.path.join(REPO, "design/concepts/Pyrelands/version/test_table.json")


def verdict(tid, rc, out):
    if tid == "T_SETTINGS_SCREENS":
        # the suite prints no per-mod tally (the recorded "14 rows for this mod, 0 red" was the recorder's); count its rows
        mine = [l for l in out.splitlines() if re.match(r"^\S+\s+Pyrelands:", l)]
        return "PASS" if mine and all(l.startswith("ok ") for l in mine) else "FAIL"
    return "PASS" if rc == 0 else "FAIL"


def run(tid, cmd, timeout=500):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=timeout)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = -9, (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT"
    lines = [l for l in out.splitlines() if l.strip()] or [l for l in err.splitlines() if l.strip()]
    return rc, out + "\n" + err, (lines[-1] if lines else ""), round(time.time() - t0, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl"))
    a = ap.parse_args()
    t = json.load(open(TABLE))
    only = set(filter(None, a.only.split(",")))
    rows = []
    for tid, v in t["tests"].items():
        if v.get("kind") != "offline" or (only and tid not in only):
            continue
        rec = v.get("runs_today") or {}
        rc, out, last, secs = run(tid, v["command"])
        res = verdict(tid, rc, out)
        rl = rec.get("last") or ""
        pref = bool(rl) and (last.startswith(rl.strip()) or rl.strip().startswith(last.strip()))
        if tid == "T_SETTINGS_SCREENS":
            mine = [l for l in out.splitlines() if re.match(r"^\S+\s+Pyrelands:", l)]
            last = last + "; %d rows for this mod, %d red" % (len(mine), sum(1 for l in mine if not l.startswith("ok ")))
        rows.append({"id": tid, "command": v["command"], "rc": rc, "seconds": secs, "result": res, "recorded_result": rec.get("result"),
                     "last": last[:300], "recorded_last": rl[:300], "last_prefix_match": pref, "match": res == rec.get("result")})
    rows.append({"id": "RECORD_ART_SHEET", "result": "not_rerunnable", "recorded_result": "recorded",
                 "last": "a record (the owner's sheet approval), no command", "match": None})
    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    tests = [r for r in rows if r["match"] is not None]
    ok = sum(1 for r in tests if r["match"])
    print("RERUNS %d/%d verdicts match; FAIL now: %s" % (ok, len(tests), [r["id"] for r in tests if r["result"] != "PASS"] or "none"))
    sys.exit(0 if ok == len(tests) else 1)


main()
