#!/usr/bin/env python3
"""selftest_scene_library_no_litter.py — a run of selftest_scene_library.py leaves no git repo in its TMPDIR
(LIVE_RESTORE_RM_SCRATCH_REAP).

The failure (Archmagi, 2026-11-27): `_tree` in selftest_scene_library.py made each fixture repo with a bare
tempfile.mkdtemp() and never removed it. scene_library_mutants.py runs the selftest about 45 times, so each mutant pass
left about 135 repos (s/good.py, s/old2.py ...) in one tmp.XXXXXXXXXX folder under ~/.seat-tmp/BENCH. A day later the
scratch reap archived and deleted 1,093 of them in one run, at 4 to 680 s each: the 8:00 PM PST run took 2 h 58 min,
and the 2 h promises on last_run.json broke.

Proves: the selftest, run once as a child with a fresh TMPDIR, exits 0 and leaves no `.git` under that TMPDIR."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN_S = 600     # hang guard only: the selftest takes about 1 s; 10 s at load 25


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="selftest_scene_litter_") as td:
        env = dict(os.environ, TMPDIR=td, TMP=td, TEMP=td)
        p = subprocess.run([sys.executable, str(HERE / "selftest_scene_library.py")], env=env, capture_output=True,
                           text=True, timeout=RUN_S)
        left = sorted(str(Path(dp).relative_to(td)) for dp, dns, _ in os.walk(td) if ".git" in dns)
        ok = p.returncode == 0 and not left
        print(("PASS" if p.returncode == 0 else "FAIL") + " the scene library selftest passes in a fresh TMPDIR (rc %s%s)"
              % (p.returncode, "" if p.returncode == 0 else ", " + (p.stdout + p.stderr)[-300:]))
        print(("PASS" if not left else "FAIL") + " a run leaves no fixture repo in its TMPDIR (%d left: %s)" % (len(left), left[:5]))
    print("ALL PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
