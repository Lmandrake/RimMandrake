#!/usr/bin/env python3
"""selftest_enact_missing_snapshot.py — build_plan / ruling_status refuse a decisions doc with no readable snapshot BY NAME
(ValueError "snapshot missing: <path>" / "not a decisions doc"), never a raw FileNotFoundError / IsADirectoryError, and an
empty snapshot never maps to the repo root (ENACT_MISSING_SNAPSHOT_HARDEN_NAMED_REFUSAL)."""
from __future__ import annotations

# selftest temp containment (wave 7, DIRTY_CODE_REVIEW_STANDING_LOOP_1): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit — this
# test used to leave its temp dirs behind in the seat TMPDIR on every run.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_enact_missing_snapshot_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
FAILS = []


def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAILS.append(m)


def main():
    root = Path(tempfile.mkdtemp())
    for d in ("ledger/events", "store", "src"):
        (root / d).mkdir(parents=True)
    os.environ.update(ART_LEDGER_DIR=str(root / "ledger"), ARTSTORE=str(root / "store"), ART_SRC_ROOT=str(root / "src"),
                      RIMFLOW_SEAT="TEST")
    import enact as E
    for label, snap, want in (("empty", "", "names no snapshot"), ("none", None, "names no snapshot"),
                              ("missing", str(root / "nope.json"), "snapshot missing")):
        p = root / f"{label}.decisions.json"
        p.write_text(json.dumps({"schema": 2, "decisions": {}, "snapshot": snap}))
        for fn in (E.build_plan, E.ruling_status):
            try:
                fn(p)
                got = "returned"
            except ValueError as e:
                got = str(e)
            except Exception as e:      # noqa: BLE001
                got = f"RAW {type(e).__name__}"
            check(want in got, f"{fn.__name__} with snapshot={snap!r}: named refusal ({got[:90]})")
    sys.exit(1 if FAILS else 0)


main()
