#!/usr/bin/env python3
"""Plant one fault of planted_faults.json, run a command, restore the file byte for byte, exit with the command's rc.
    python3 plant_one.py <fault id> -- <command ...>
Restores on SIGTERM, SIGINT and SIGHUP; prints the command's last line and `restored <file>`."""
import json, os, signal, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))


def main():
    fid, cmd = sys.argv[1], sys.argv[sys.argv.index("--") + 1:]
    f = {x["id"]: x for x in json.load(open(os.path.join(HERE, "planted_faults.json")))["faults"]}[fid]
    p = os.path.join(REPO, f["file"])
    orig = open(p, "rb").read()
    t = orig.decode("utf-8")
    if t.count(f["old"]) != 1:
        print("PLANT REFUSED: old text found %d times" % t.count(f["old"]))
        sys.exit(2)

    def restore(*_):
        open(p, "wb").write(orig)
        if _:
            sys.exit(3)
    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(s, restore)
    open(p, "wb").write(t.replace(f["old"], f["new"]).encode("utf-8"))
    try:
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=500)
    finally:
        restore()
    assert open(p, "rb").read() == orig
    lines = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
    for l in [x for x in lines if "FAIL" in x and "mutant" not in x][:4]:
        print(l[:300])
    print(lines[-1] if lines else "")
    print("restored", f["file"])
    sys.exit(r.returncode)


main()
