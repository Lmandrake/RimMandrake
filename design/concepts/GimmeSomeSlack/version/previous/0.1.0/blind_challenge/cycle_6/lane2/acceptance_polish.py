#!/usr/bin/env python3
"""Acceptance tests of the Polish faults blind cycle 6 filed (each fails on c991553a4f, the commit judged).
    python3 acceptance_polish.py flexible_pipes   rc 0 when planting P15 (CLAIM loses "flexible pipes") turns T_NO_HOSE red
    python3 acceptance_polish.py about            rc 0 when planting P05 (About says the hoses ship here) turns T_NO_HOSE red
    python3 acceptance_polish.py hose_preset      rc 0 when planting P09 (GSS lays its cords with LayParams.Hose) turns T_NO_HOSE red
    python3 acceptance_polish.py fallen_wall      rc 0 when lane 1's K_FALLEN_WIRE_LIES_ON_GROUND row is PASS
    python3 acceptance_polish.py restring_nan     rc 0 when lane 1's K_RESTRING_IS_A_JOB row is PASS
A plant is made in the tree and restored byte for byte (also on SIGTERM, SIGINT, SIGHUP); the run ends with the tree clean."""
import json, os, signal, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
FAULTS = {f["id"]: f for f in json.load(open(os.path.join(HERE, "planted_faults.json")))}
DECIDER = "python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py"
PLANT = {"flexible_pipes": "P15_DECIDER_FORGETS_FLEXIBLE_PIPES", "about": "P05_ABOUT_SAYS_HOSES_SHIP_HERE",
         "hose_preset": "P09_CORDS_LAID_WITH_HOSE_PRESET"}
ROW = {"fallen_wall": "K_FALLEN_WIRE_LIES_ON_GROUND", "restring_nan": "K_RESTRING_IS_A_JOB"}
saved = {}


def restore(*sig):
    for p, b in saved.items():
        open(p, "wb").write(b)
    saved.clear()
    if sig:
        sys.exit(130)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, restore)


def main(which):
    if which in PLANT:
        f = FAULTS[PLANT[which]]
        p = os.path.join(REPO, f["file"]); orig = open(p, "rb").read(); t = orig.decode("utf-8")
        if t.count(f["old"]) != 1:
            print("UNMEASURED: %s old text found %d times" % (f["id"], t.count(f["old"]))); return 2
        saved[p] = orig
        try:
            open(p, "wb").write(t.replace(f["old"], f["new"]).encode("utf-8"))
            r = subprocess.run(DECIDER, shell=True, cwd=REPO, capture_output=True, text=True, timeout=300)
        finally:
            restore()
        caught = r.returncode != 0
        print("%s  %s planted: T_NO_HOSE rc %d (%s)" % ("PASS" if caught else "FAIL", f["id"], r.returncode, "caught" if caught else "stays green"))
        return 0 if caught else 1
    if which in ROW:
        out = "/tmp/gss_c6_accept_lane1.jsonl"
        subprocess.run([sys.executable, os.path.join(HERE, "..", "lane1", "run_lane1.py"), "--out", out], cwd=REPO, capture_output=True, timeout=500)
        rows = {json.loads(l)["id"]: json.loads(l) for l in open(out)}
        v = rows.get(ROW[which], {}).get("verdict")
        print("%s  %s %s: %s" % ("PASS" if v == "PASS" else "FAIL", ROW[which], v, rows.get(ROW[which], {}).get("detail", "")[:200]))
        return 0 if v == "PASS" else 1
    print("usage: acceptance_polish.py " + "|".join(list(PLANT) + list(ROW))); return 2


sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
