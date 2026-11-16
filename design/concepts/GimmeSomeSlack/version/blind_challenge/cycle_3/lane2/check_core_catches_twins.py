#!/usr/bin/env python3
"""Does T_CORE (a decider of cords_never_repeat) catch a broken twin pass?
    python3 check_core_catches_twins.py [--only C_TWIN_APART_ZERO,C_TWIN_PICKS_CLOSER]
Plants each fault (lane2/planted_faults.json) in the tree, runs T_CORE's recorded command (selftest_gimmesomeslack.py, no
--geometry) under a private WINBUILD_ROOT, and restores byte for byte (also on SIGTERM, SIGINT, SIGHUP). A fault is caught
when T_CORE prints a FAIL line naming the twin leads. Exit 0 = every fault caught; 1 = one missed; 2 = instrument broke
(the tree was dirty, or the clean T_CORE run already fails on twin leads)."""
import argparse, json, os, signal, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
CMD = ["python3", "src/RimMandrake/Utils/selftest_gimmesomeslack.py"]
ENV = dict(os.environ, WINBUILD_ROOT="/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c3_mut/")
saved = {}
def restore(*_):
    for p, d in saved.items(): open(p, "wb").write(d)
    saved.clear()
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP): signal.signal(s, lambda *a: (restore(), sys.exit(130)))
def twin_fails():
    p = subprocess.run(CMD, cwd=REPO, capture_output=True, text=True, timeout=500, env=ENV)
    return [l.strip() for l in p.stdout.splitlines() if l.startswith("FAIL") and "twin lead" in l], p.returncode
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", default="C_TWIN_APART_ZERO,C_TWIN_PICKS_CLOSER"); ap.add_argument("--no-clean-run", action="store_true")
    a = ap.parse_args()
    if subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/GimmeSomeSlack"], cwd=REPO).returncode: print("UNMEASURED: tree dirty"); return 2
    faults = {f["id"]: f for f in json.load(open(os.path.join(HERE, "planted_faults.json")))["faults"]}
    missed = []
    for fid in a.only.split(","):
        f = faults[fid]; path = os.path.join(REPO, f["file"]); data = open(path, "rb").read(); saved[path] = data
        try:
            t = data.decode("utf-8")
            if t.count(f["old"]) != 1: print("UNMEASURED: %s old text not unique" % fid); return 2
            open(path, "wb").write(t.replace(f["old"], f["new"]).encode("utf-8"))
            fails, rc = twin_fails()
        finally:
            restore()
        print("%s  %s  rc %s  %s" % ("CAUGHT" if fails else "MISSED", fid, rc, fails[:1]))
        if not fails: missed.append(fid)
    clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/GimmeSomeSlack"], cwd=REPO).returncode == 0
    print("RESULT: T_CORE caught %d of %d twin-pass faults%s; tree clean %s" % (len(a.only.split(",")) - len(missed), len(a.only.split(",")), (", missed " + ",".join(missed)) if missed else "", clean))
    return 2 if not clean else (1 if missed else 0)
if __name__ == "__main__":
    sys.exit(main())
