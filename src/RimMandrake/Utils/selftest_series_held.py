#!/usr/bin/env python3
"""selftest_series_held.py — series_held.py: held, broken, a hole, a torn line, an UNMEASURED point, a missing file."""
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "series_held.py"
FAILS = []
NOW = 1_800_000_000.0


def at(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def write(path, rows, extra=""):
    with open(path, "w", encoding="utf-8") as f:
        for t, m, v in rows:
            f.write(json.dumps({"at": at(t), "family": "disk", "points": {"disk.tmp_used_pct": {"m": m, "v": v}}}) + "\n")
        f.write(extra)


def run(path, *extra):
    p = subprocess.run([sys.executable, str(TOOL), "--key", "disk.tmp_used_pct", "--below", "80", "--hours", "48",
                        "--series", str(path), "--now", str(NOW), *extra], capture_output=True, text=True, timeout=60)
    return p.returncode, p.stdout.strip()


def check(name, got, want_code, want_word):
    code, out = got
    if code != want_code or not out.startswith(want_word) or "\n" in out:
        FAILS.append("%s: exit %s %r (wanted %s %s)" % (name, code, out, want_code, want_word))


with tempfile.TemporaryDirectory() as td:
    f = Path(td) / "disk.jsonl"
    every15 = [NOW - 48 * 3600 + i * 900 for i in range(193)]          # 48 h at 15 min, both edges covered
    write(f, [(t, "MEASURED", 30.0) for t in every15], extra="{torn\n")
    check("held", run(f), 0, "HELD")
    write(f, [(t, "MEASURED", 85.0 if i == 100 else 30.0) for i, t in enumerate(every15)])
    check("breach", run(f), 1, "BROKEN")
    write(f, [(t, "MEASURED", 30.0) for t in every15 if not NOW - 30 * 3600 < t < NOW - 26 * 3600])
    check("hole", run(f), 2, "UNMEASURED")
    write(f, [(t, "UNMEASURED" if NOW - 30 * 3600 < t < NOW - 26 * 3600 else "MEASURED", 30.0) for t in every15])
    check("unmeasured points are a hole", run(f), 2, "UNMEASURED")
    write(f, [(t, "MEASURED", 30.0) for t in every15 if t < NOW - 3 * 3600])
    check("stale tail is a hole", run(f), 2, "UNMEASURED")
    write(f, [(t - 80 * 3600, "MEASURED", 99.0) for t in every15[:5]] + [(t, "MEASURED", 30.0) for t in every15])
    check("breach before the window is ignored", run(f), 0, "HELD")
    write(f, [(t, "MEASURED", 80.0 if i == 7 else 30.0) for i, t in enumerate(every15)])
    check("on the line is broken", run(f), 1, "BROKEN")
    check("hole limit widens", run(f, "--max-gap-min", "600"), 1, "BROKEN")
    check("missing file", run(Path(td) / "nope.jsonl"), 2, "UNMEASURED")

if FAILS:
    print("FAIL selftest_series_held:\n  " + "\n  ".join(FAILS))
    sys.exit(1)
print("PASS selftest_series_held (9 cases)")
