#!/usr/bin/env python3
"""Selftest: v3_cutover.py is retired (V3_CUTOVER_REVERT_RETIRE_NOW_HARMFUL). Its writers would re-assert
FOUNDRY ownership after FOUNDRY's retirement, so apply and revert must refuse with exit 2 and a pointer,
write nothing, and the staged docs patch must be gone. `status` still reads the record.

    python3 src/RimMandrake/rimflow/selftest_v3_cutover.py
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TOOL = os.path.join(HERE, "v3_cutover.py")
STATE = os.path.join(ROOT, "infrastructure", "state", "v3_cutover")
sys.path.insert(0, HERE)
import v3_cutover as vc  # noqa: E402

PASS, FAIL = [], []


def _snapshot():
    return {f: os.path.getmtime(os.path.join(STATE, f)) for f in os.listdir(STATE)} if os.path.isdir(STATE) else {}


def t_writers_refuse_with_pointer_and_write_nothing():
    before = _snapshot()
    for verb in ("apply", "revert", "plan"):
        r = subprocess.run([sys.executable, TOOL, verb, "--why", "x", "--commit"], capture_output=True, text=True,
                           timeout=60)
        assert r.returncode == 2, (verb, r.returncode)
        assert "RETIRED" in r.stderr and "V3_CUTOVER_REVERT_RETIRE_NOW_HARMFUL" in r.stderr, r.stderr
    assert _snapshot() == before, "a refused verb touched infrastructure/state/v3_cutover"


def t_functions_refuse_too():
    with contextlib.redirect_stderr(io.StringIO()):
        assert vc.apply(None, "said", "why", 0, commit=True) == 2
        assert vc.revert(None, None, "why", 0, commit=True) == 2


def t_docs_patch_is_deleted():
    assert not os.path.exists(os.path.join(STATE, "docs.patch")), "the stale FOUNDRY docs patch is back"


def t_status_reads_a_record():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "record.json")
        json.dump({"state": "applied", "applied_at": "2026-10-29T01:32:17Z", "moved": ["A", "B"], "kept": ["C"],
                   "lane_seat_before": "BENCH"}, open(p, "w"))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            assert vc.status(p) == 0
        assert "moved 2, kept 1" in out.getvalue(), out.getvalue()
        with contextlib.redirect_stdout(io.StringIO()):
            assert vc.status(os.path.join(d, "missing.json")) == 1


CASES = [v for k, v in sorted(globals().items()) if k.startswith("t_") and callable(v)]

if __name__ == "__main__":
    for fn in CASES:
        try:
            fn(); PASS.append(fn.__name__); print("ok    " + fn.__name__)
        except Exception as e:  # noqa: BLE001
            FAIL.append(fn.__name__); print("FAIL  %s\n        %s: %s" % (fn.__name__, type(e).__name__, e))
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
