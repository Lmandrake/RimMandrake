#!/usr/bin/env python3
"""The catching run: plant one fault of planted_faults.json, run one test of test_table.json, restore byte for byte.
    python3 catch.py <fault_id> <TEST_ID>
Exit 0 = the test went red on the fault (caught), 1 = it stayed green (missed), 2 = the fault's anchor is not there.
Restores on SIGTERM, SIGINT and SIGHUP."""
import json, os, signal, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
fid, tid = sys.argv[1], sys.argv[2]
fault = next(f for f in json.load(open(os.path.join(HERE, "planted_faults.json")))["faults"] if f["id"] == fid)
cmd = json.load(open(os.path.join(REPO, "design/concepts/Pyrelands/version/test_table.json")))["tests"][tid]["command"]
path = os.path.join(REPO, fault["file"])
orig = open(path, "rb").read()


def restore(*a):
    open(path, "wb").write(orig)
    if a:
        sys.exit(130)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, restore)
text = orig.decode("utf-8")
if text.count(fault["old"]) != 1:
    print("ANCHOR %s occurs %d times in %s" % (fid, text.count(fault["old"]), fault["file"]))
    sys.exit(2)
try:
    open(path, "wb").write(text.replace(fault["old"], fault["new"]).encode("utf-8"))
    p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=500)
finally:
    restore()
last = (p.stdout.strip().splitlines() or p.stderr.strip().splitlines() or [""])[-1]
print(("CAUGHT %s by %s (rc %d): " if p.returncode else "MISSED %s by %s (rc %d): ") % (fid, tid, p.returncode) + last[:200])
sys.exit(0 if p.returncode else 1)
