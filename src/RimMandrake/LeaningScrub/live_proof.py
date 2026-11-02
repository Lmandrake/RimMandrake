#!/usr/bin/env python3
"""Live proofs of LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY, one clause per call: exit 0 when it holds, 1 when it does not.

    python3 src/RimMandrake/LeaningScrub/live_proof.py A1|A2|A3|A4

Read-only on the running game beyond what each clause names: A1 loads the saved site RM_TestSite_leaningscrub
(test_site_saves.py load leaningscrub); A2-A4 run ONLY validation.py's lean chain on that loaded map through the
northstar driver and read one bar. The Windows-side tools run under python.exe; this wrapper exists so the live-proof
line is a literal command a gate can read (no shell expansion).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SITE_SAVES = os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck", "test_site_saves.py")
NORTHSTAR = os.path.join(REPO, "src", "RimMandrake", "Utils", "northstar_driver", "cli.py")
PLAN = os.path.join(HERE, "northstar_plan.py")
SCRATCH = "/mnt/d/ClaudeWork/rimmandrake/scratch"
BARS = {"A2": "lean.lean_heading_from_sun", "A3": "lean.lean_scent_upwind_flees", "A4": "lean.lean_fire_downwind"}
TIMEOUT = 520


def win(path):
    out = subprocess.run(["wslpath", "-w", path], capture_output=True, text=True, timeout=20).stdout.strip()
    if not out:
        raise SystemExit("wslpath gave nothing for %s" % path)
    return out


def run(argv):
    print("$ " + " ".join(argv), flush=True)
    return subprocess.run(argv, stdin=subprocess.DEVNULL, timeout=TIMEOUT).returncode


def bar_status(out_path, bar_id):
    """-> (status, detail) of one bar in a northstar --out file, or None if the bar is absent."""
    with open(out_path) as f:
        bars = json.load(f).get("bars", [])
    for b in bars:
        if b.get("id") == bar_id:
            return b.get("status"), b.get("detail", "")
    return None


def main(argv):
    if len(argv) != 2 or argv[1] not in ("A1",) + tuple(BARS):
        print(__doc__)
        return 2
    clause = argv[1]
    if clause == "A1":
        rc = run(["python.exe", win(SITE_SAVES), "load", "leaningscrub"])
        print("A1 %s (test_site_saves load exit %d)" % ("PASS" if rc == 0 else "FAIL", rc))
        return 0 if rc == 0 else 1
    os.makedirs(SCRATCH, exist_ok=True)
    # a name of this run alone: a stale or concurrent run's file can never pass for this one
    out = os.path.join(SCRATCH, "lean_%s_%d_%d.json" % (clause, os.getpid(), time.time_ns()))
    rc = run(["python.exe", win(NORTHSTAR), "run", "--mod", "LeaningScrub", "--plan", win(PLAN), "--chains", "lean",
              "--out", win(SCRATCH) + "\\" + os.path.basename(out)])
    if not os.path.exists(out):
        print("%s FAIL: the driver wrote no %s (exit %d)" % (clause, out, rc))
        return 1
    r = bar_status(out, BARS[clause])
    print("%s %s: %s -> %r" % (clause, "PASS" if r and r[0] == "PASS" else "FAIL", BARS[clause], r))
    return 0 if r and r[0] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
