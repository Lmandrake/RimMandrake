#!/usr/bin/env python3
"""check_config_errors.py: an `ours-fixed` line is history in an old log and a regression in a later one."""
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "check_config_errors.py")
DAY = 86400


def run(log, baseline):
    return subprocess.run([sys.executable, TOOL, "--log", log, "--baseline", baseline],
                          capture_output=True, text=True, encoding="utf-8").returncode


def main():
    with tempfile.TemporaryDirectory() as d:
        log = os.path.join(d, "Player.log")
        baseline = os.path.join(d, "baseline.json")
        with open(log, "w", encoding="utf-8") as fh:
            fh.write("Config error in RR_Thing: researchViewX and/or researchViewY not set\n")
        today = time.strftime("%Y-%m-%d")
        with open(baseline, "w", encoding="utf-8") as fh:
            json.dump({"entries": [{"pattern": "Config error in RR_Thing", "kind": "configerror",
                                    "class": "ours-fixed", "expectCount": 0, "fixedOn": today, "note": ""}]}, fh)
        now = time.time()
        os.utime(log, (now - 5 * DAY, now - 5 * DAY))
        got = [run(log, baseline)]
        os.utime(log, (now + 5 * DAY, now + 5 * DAY))
        got.append(run(log, baseline))
    assert got == [0, 1], "old log clean, later log regression; got %s" % got
    print("ok")


if __name__ == "__main__":
    main()
