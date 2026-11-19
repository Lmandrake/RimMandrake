#!/usr/bin/env python3
"""vv_matrix_clock.py - the clock's one run of the shipped-settings fuzz matrix (RIMMANDRAKE_REVIVE_SHIPPED_FUZZ_WITH_LAWS).

    python3 src/RimMandrake/Utils/vv_matrix_clock.py [--prove] [--dry-run]

Runs vv_shipped_matrix.py at full n (offline: a staged C# build and Windows dotnet.exe, no game), and with --prove (the
timer passes it on Sundays) vv_laws.py prove as well, so a green matrix is known to be able to go red. Writes ONE
reading, <agent storage>/rimmandrake/vv_matrix/last.json, AFTER the runs end and never before (a reading written first
could pass for an answer): {when, matrix_rc, matrix_verdict, prove_rc, prove_line, results}. matrix_verdict is the
matrix's own VERDICT line; a run that printed none reads UNMEASURED with its exit code. Exit: the matrix's exit code,
or the prove's when the matrix passed. Unit: src/RimMandrake/Utils/systemd/rm-vv-matrix.{service,timer}.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)


def reading_path():
    import rmpaths
    return str(rmpaths.rm_path("vv_matrix", "last.json"))


def run(cmd, timeout):
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timed out after %ds" % timeout


def last(pattern, text):
    m = re.findall(pattern, text, re.M)
    return m[-1] if m else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prove", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print the commands, run nothing, write nothing")
    a = ap.parse_args(argv)
    mcmd = [sys.executable, os.path.join(HERE, "vv_shipped_matrix.py")]
    pcmd = [sys.executable, os.path.join(HERE, "vv_laws.py"), "prove"]
    if a.dry_run:
        print("would run:", " ".join(mcmd))
        if a.prove:
            print("would run:", " ".join(pcmd))
        print("would write:", reading_path())
        return 0
    t0 = time.time()
    mrc, mout = run(mcmd, 6 * 3600)
    verdict = last(r"^VERDICT: (\w+)", mout)
    rec = {"when": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "wall_s": None, "matrix_rc": mrc,
           "matrix_verdict": verdict or "UNMEASURED (no VERDICT line; exit %d)" % mrc,
           "matrix_why": [l.strip() for l in mout.splitlines()[-12:] if l.startswith("  ") and "red at" in l],
           "results": last(r"^results: (.+)$", mout), "prove_rc": None, "prove_line": "not run (no --prove)"}
    rc = mrc
    if a.prove:
        prc, pout = run(pcmd, 3 * 3600)
        rec["prove_rc"], rec["prove_line"] = prc, last(r"^laws proven: .+$", pout) or "UNMEASURED (no line; exit %d)" % prc
        if mrc == 0:
            rc = prc
    rec["wall_s"] = round(time.time() - t0, 1)
    p = reading_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    os.replace(p + ".tmp", p)
    print("vv matrix: %s; laws: %s -> %s" % (rec["matrix_verdict"], rec["prove_line"], p))
    return rc


if __name__ == "__main__":
    sys.exit(main())
