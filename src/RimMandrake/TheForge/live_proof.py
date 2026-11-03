#!/usr/bin/env python3
"""Live proofs of FORGE_SKY_PASTURES_1, one clause per call: exit 0 when it holds, 1 when it does not.

    python3 src/RimMandrake/TheForge/live_proof.py A1|A2

A1 runs ONLY validation.py's sky_pastures chain through the northstar driver (TheForge plan, a Forge map with lava, so
the vapour-column field has cells) and reads one bar, sky_pastures.sky_live_flock_reaches_columns: a wild flock of
fleet fliers and bulloos set down 18-30 cells from a column, outside every leash, stands >=70% in a column or its
leash after 5000 stepped ticks, and the pasture wander gave jobs. Never a flight: the flock is walkers' wander only.
A2 is read-only: the running game's defs carry the stage-5 wiring and Player.log names none of its classes in an error.
The Windows-side driver runs under python.exe; this wrapper keeps each live-proof line a literal command.
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
NORTHSTAR = os.path.join(UTILS, "northstar_driver", "cli.py")
PLAN = os.path.join(HERE, "northstar_plan.py")
SCRATCH = "/mnt/d/ClaudeWork/rimmandrake/scratch"
BAR = "sky_pastures.sky_live_flock_reaches_columns"
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
    if len(argv) != 2 or argv[1] not in ("A1", "A2"):
        print(__doc__)
        return 2
    if argv[1] == "A2":
        rc = run([sys.executable, os.path.join(UTILS, "live_def_check.py"),
                  "--has", "ThinkTreeDef/RM_ThinkTree_ForgeSkyPasture=RM_JobGiver_SkyPastureWander",
                  "--has", "ThingDef/RM_Bulloo=CompProperties_VaporDrifter",
                  "--has", "ThingDef/RM_Dhokkur=RM_DhokkurColumnsExtension"])
        if rc == 0:
            rc = run([sys.executable, os.path.join(UTILS, "live_log_check.py"), "--absent", "RM_JobGiver_SkyPastureWander",
                      "--absent", "RM_DhokkurColumnsExtension", "--absent", "RM_ThinkTree_ForgeSkyPasture"])
        print("A2 %s (exit %d)" % ("PASS" if rc == 0 else "FAIL", rc))
        return 0 if rc == 0 else 1
    os.makedirs(SCRATCH, exist_ok=True)
    # a name of this run alone: a stale or concurrent run's file can never pass for this one
    out = os.path.join(SCRATCH, "sky_A1_%d_%d.json" % (os.getpid(), time.time_ns()))
    rc = run(["python.exe", win(NORTHSTAR), "run", "--mod", "TheForge", "--plan", win(PLAN), "--chains", "sky_pastures",
              "--out", win(SCRATCH) + "\\" + os.path.basename(out)])
    if not os.path.exists(out):
        print("A1 FAIL: the driver wrote no %s (exit %d)" % (out, rc))
        return 1
    # The driver's exit code is not the verdict: running one chain leaves every other chain NOT_RUN, which the driver
    # may report as nonzero. The clause is this one bar, read from this run's own --out file.
    r = bar_status(out, BAR)
    print("A1 %s: %s -> %r (driver exit %d)" % ("PASS" if r and r[0] == "PASS" else "FAIL", BAR, r, rc))
    return 0 if r and r[0] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
