#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_BUILD_STANDING_SCAN_OF_QUIET_FILES_ON_SONNET: the standing scan runs on this machine and has
read real quiet files. It reads the timer, the scan's last reading and its outcome book, and checks git for each ended file.
Exit 0: the timer is active, the reading is under 2 h old, and at least one file that a sonnet run picked has ended, and
every ended file was quiet when picked and ended clean, flagged or noted with a reason. Exit 1: not so. Exit 3: could not look."""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
BAD = []


def main():
    try:
        import quiet_scan as QS
    except ImportError as e:
        print("FAIL quiet_scan.py is not here: %s" % e)
        return 1
    r = subprocess.run(["systemctl", "--user", "is-active", "rm-quiet-scan.timer"], capture_output=True, text=True, timeout=30)
    if (r.stdout or "").strip() != "active":
        BAD.append("rm-quiet-scan.timer reads %s" % ((r.stdout or r.stderr).strip() or "nothing"))
    d = QS.sdir(create=False)
    try:
        rd = json.load(open(os.path.join(d, "reading.json"), encoding="utf-8"))
        age = time.time() - rd["at"]
        print("reading: %s, %d s old (%s)" % (rd["decision"], age, rd.get("why")))
        if age > 7200:
            BAD.append("the reading is %d s old" % age)
    except FileNotFoundError:
        BAD.append("no reading")
    picks = {(p["run"], p["path"]): p for p in QS.picks()}
    ends = QS.ends()
    real = [e for e in ends if e.get("outcome") in ("clean", "flagged") or
            (e.get("outcome") == "noted" and (e.get("reason") or "").strip() and not e.get("by_program"))]
    if not real:
        BAD.append("no picked file has ended by a run's own word (%d ended by the program)" % len(ends))
    for e in ends:
        p = picks.get((e["run"], e["path"]))
        if p is None:
            BAD.append("%s ended and was never picked by %s" % (e["path"], e["run"]))
        elif not p.get("last_commit"):
            BAD.append("%s: its last commit is unknown" % e["path"])
        elif p["at"] - p["last_commit"] < 7 * 86400:
            BAD.append("%s was picked %.1f days after its last commit" % (e["path"], (p["at"] - p["last_commit"]) / 86400))
    for b in BAD:
        print("FAIL " + b)
    print("ended %d, by a run's own word %d" % (len(ends), len(real)))
    return 1 if BAD else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print("could not look: %s: %s" % (type(e).__name__, e))
        sys.exit(3)
