#!/usr/bin/env python3
"""The catching run for RIMMANDRAKE_WIDEN_GSS_NOHOSE_SCAN_FIVE_LEFTOVERS_SLIPPED.
    python3 check_nohose_catches.py
Plants each no-hose fault NH1..NH7 of planted_faults.json in the tree in turn, runs the offline bars' decider T_NO_HOSE
(selftest_gss_no_hose.py), restores the file byte for byte (also on SIGTERM/SIGINT/SIGHUP), then runs the decider on the
clean tree. rc 0 = every planted hose leftover turned the decider's tree row (T1) red AND the clean tree reads green; rc 1 = one survived
or the clean tree read red. On the parent of the fix NH1..NH5 survive (rc 1)."""
import json, os, signal, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
CMD = [sys.executable, os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py")]
saved = {}


def restore(*_):
    for p, d in list(saved.items()):
        open(p, "wb").write(d); del saved[p]


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP): signal.signal(s, lambda sig, fr: (restore(), sys.exit(128 + sig)))
faults = [f for f in json.load(open(os.path.join(HERE, "planted_faults.json"))) if f["id"].startswith("NH")]
missed = []
for f in faults:
    p = os.path.join(REPO, f["file"]); d = open(p, "rb").read(); t = d.decode("utf-8")
    if t.count(f["old"]) != 1: print("NOT APPLIED", f["id"]); missed.append(f["id"]); continue
    saved[p] = d
    try:
        open(p, "w", encoding="utf-8", newline="").write(t.replace(f["old"], f["new"]))
        r = subprocess.run(CMD, cwd=REPO, capture_output=True, text=True, timeout=120)
    finally:
        restore()
    # caught = the decider's own tree row goes red (its mutant loop then reads the planted copy as unclean: rc 2, by design)
    caught = r.returncode != 0 and "FAIL  T1_tree_ships_no_hose" in r.stdout
    print(("CAUGHT  " if caught else "MISSED  ") + f["id"] + "  decider rc %d" % r.returncode)
    if not caught: missed.append(f["id"])
clean = subprocess.run(CMD, cwd=REPO, capture_output=True, text=True, timeout=120).returncode
print("clean tree decider rc %d" % clean)
print("RESULT: %d of %d planted hose leftovers caught%s" % (len(faults) - len(missed), len(faults), "; missed " + ",".join(missed) if missed else ""))
sys.exit(0 if not missed and clean == 0 else 1)
