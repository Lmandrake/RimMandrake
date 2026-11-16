"""The catching run for a fixed test: plant one fault of planted_faults.json, run the test, restore byte for byte.
    python3 catch_check.py <FAULT_ID> <test.py>
Exit 0 = the test went red on the planted fault (caught); 1 = it stayed green (missed); 2 = the anchor is gone.
Restores on SIGTERM, SIGINT and SIGHUP."""
import json, os, signal, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
fid, test = sys.argv[1], sys.argv[2]
f = next(x for x in json.load(open(os.path.join(HERE, "planted_faults.json"))) if x["id"] == fid)
path = os.path.join(REPO, f["file"])
data = open(path, "rb").read()


def restore(*_):
    open(path, "wb").write(data)
    if _:
        sys.exit(130)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, restore)
text = data.decode("utf-8")
if text.count(f["old"]) != 1:
    print("ANCHOR GONE", fid)
    sys.exit(2)
try:
    open(path, "w", encoding="utf-8", newline="").write(text.replace(f["old"], f["new"], 1))
    r = subprocess.run(["python3", test], cwd=REPO, capture_output=True, text=True, timeout=500)
finally:
    restore()
lines = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
print(("CAUGHT " if r.returncode else "MISSED ") + fid + " by " + os.path.basename(test) + ": " + (lines[-1] if lines else "")[:200])
sys.exit(0 if r.returncode else 1)
