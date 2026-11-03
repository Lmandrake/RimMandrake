#!/usr/bin/env python3
"""Live proofs of ExplosiveGrowth items, one clause per call: exit 0 when it holds, 1 when it does not, 2 when nothing
was measured (relentless_live.py reads any exit but 0/1 as UNMEASURED).

    python3 src/RimMandrake/ExplosiveGrowth/live_proof.py A1|T1|T2

A1 is EGROWTH_SAVELOAD_PROVE_DICT_SCRIBE_SHARE; T1/T2 are EGROWTH_TINDER_HAY_PROVE_COMES_UP_EMPTY (chain top_tinder).

Exit 2 (UNMEASURED), never 1: the driver wrote no out file (it never launched: a WSL interop 'UtilAcceptVsock' error
cost T2 a FAIL at 0d984538 while the same chain's T2 bar read PASS in the T1 run 25 s earlier), the out file is not
JSON, the bar is absent, or the bar's own status is not PASS/FAIL (UNMEASURED, REFUSED, NOT_RUN). Only a bar that reads
FAIL is a FAIL; only a bar that reads PASS is a PASS.

A1 runs ONLY validation.py's scribe_round_trip chain through the northstar driver on the loaded quicktest map and reads
one bar, scribe_round_trip.scribe_dicts_survive_save_load. The Windows-side driver runs under python.exe; this wrapper
exists so the live-proof line is a literal command a gate can read (no shell expansion).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
NORTHSTAR = os.path.join(REPO, "src", "RimMandrake", "Utils", "northstar_driver", "cli.py")
PLAN = os.path.join(HERE, "northstar_plan.py")
SCRATCH = "/mnt/d/ClaudeWork/rimmandrake/scratch"
BARS = {"A1": ("scribe_round_trip", "scribe_round_trip.scribe_dicts_survive_save_load"),
        # EGROWTH_TINDER_HAY_PROVE_COMES_UP_EMPTY: the Tinder top on its real donor (RM_FE_Plant_ScorchFruit)
        "T1": ("top_tinder", "top_tinder.tinder_leaves_fuel"),
        "T2": ("top_tinder", "top_tinder.tinder_off_falls_back_to_churn")}
TIMEOUT = 520
UNMEASURED = 2


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
    try:
        with open(out_path) as f:
            bars = json.load(f).get("bars", [])
    except (OSError, ValueError, AttributeError):
        return None
    hits = [b for b in bars if b.get("id") == bar_id]
    if len(hits) != 1:
        return None
    return hits[0].get("status"), hits[0].get("detail", "")


def main(argv):
    if len(argv) != 2 or argv[1] not in BARS:
        print(__doc__)
        return 2
    clause = argv[1]
    chain, bar = BARS[clause]
    os.makedirs(SCRATCH, exist_ok=True)
    # a name of this run alone: a stale or concurrent run's file can never pass for this one
    out = os.path.join(SCRATCH, "egrowth_%s_%d_%d.json" % (clause, os.getpid(), time.time_ns()))
    rc = run(["python.exe", win(NORTHSTAR), "run", "--mod", "ExplosiveGrowth", "--plan", win(PLAN), "--chains", chain,
              "--out", win(SCRATCH) + "\\" + os.path.basename(out)])
    if not os.path.exists(out):
        print("%s UNMEASURED: the driver wrote no %s (exit %d)" % (clause, out, rc))
        return UNMEASURED
    r = bar_status(out, bar)
    if not r or r[0] not in ("PASS", "FAIL"):
        print("%s UNMEASURED: %s -> %r (out %s)" % (clause, bar, r, out))
        return UNMEASURED
    print("%s %s: %s -> %r (out %s)" % (clause, r[0], bar, r, out))
    return 0 if r[0] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
