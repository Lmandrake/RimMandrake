#!/usr/bin/env python3
"""Does an offline test catch one planted fault? The catching run of fixes.jsonl.
    python3 catch_check.py --fault <planted fault id> --test <test_table offline test id>
Plants the fault (planted_faults.json), runs the test's recorded command, restores the file byte for byte (also on SIGTERM,
SIGINT, SIGHUP). rc 0 = CAUGHT (the test went red on the fault), 1 = MISSED (green on the fault), 2 = the anchor is not there
exactly once. It also runs the test unplanted first: a test red on the clean tree cannot catch anything, rc 3."""
import argparse, json, os, signal, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
ap = argparse.ArgumentParser(); ap.add_argument("--fault", required=True); ap.add_argument("--test", required=True)
a = ap.parse_args()
fault = next(f for f in json.load(open(os.path.join(HERE, "planted_faults.json")))["faults"] if f["id"] == a.fault)
cmd = json.load(open(os.path.join(REPO, "design/concepts/Graffiti/version/test_table.json")))["tests"][a.test]["command"]
env = dict(os.environ); env.setdefault("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/graffiti_blind_c2_mut/")
path = os.path.join(REPO, fault["file"]); data = open(path, "rb").read()


def restore(*_):
    open(path, "wb").write(data)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, lambda sig, fr: (restore(), sys.exit(128 + sig)))


def run():
    p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=400, env=env)
    ls = [l for l in (p.stdout or p.stderr).splitlines() if l.strip()]
    return p.returncode, ls[-1].strip() if ls else ""


rc0, last0 = run()
if rc0 != 0:
    print("UNPLANTED RED rc %d: %s" % (rc0, last0)); sys.exit(3)
text = data.decode("utf-8")
if text.count(fault["old"]) != 1:
    print("ANCHOR occurs %d times in %s" % (text.count(fault["old"]), fault["file"])); sys.exit(2)
try:
    open(path, "w", encoding="utf-8", newline="").write(text.replace(fault["old"], fault["new"]))
    rc, last = run()
finally:
    restore()
print("%s %s: %s on the fault (rc %d: %s); green unplanted (%s)" % (a.test, a.fault, "CAUGHT" if rc else "MISSED", rc, last, last0))
sys.exit(0 if rc else 1)
