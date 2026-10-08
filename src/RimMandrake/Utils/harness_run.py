"""Run a heavy child (the judge's `claude -p`) inside rm-harness.slice, not the caller's seat.

SEAT_MEMORY_CLONES_DRIVES_1 (design/RimMandrake/memory_clones_drives_2026-10-08.md §7). Reuses
run_selftests.py's mechanism verbatim: probe_harness() (fail-closed placement + numeric memory.max),
_scope_argv() (per-child scope, MemoryMax, no swap) and its wrapper, which refuses to run the child
unless /proc/self/cgroup shows rm-harness.slice. If systemd-run --user is unavailable the child runs
in the caller, exactly as before, and a note goes to stderr once.
"""
import subprocess
import sys

import run_selftests as _rs

CAP = 3 * (1 << 30)  # one `claude -p` judge call
_state = {"probed": False}


def _contained() -> bool:
    if not _state["probed"]:
        _state["probed"] = True
        harness, why = _rs.probe_harness()
        _rs._HARNESS = harness
        if not harness:
            print("harness_run: NOT CONTAINED (%s) - running in the caller" % why, file=sys.stderr)
    return bool(_rs._HARNESS)


def run(cmd, timeout, cwd=None, cap=CAP):
    """subprocess.run(cmd, capture_output, text, timeout, cwd) -> CompletedProcess, contained when possible.
    Raises FileNotFoundError / TimeoutExpired like subprocess.run."""
    if not _contained():
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    argv = _rs._scope_argv(cap, timeout, list(cmd))
    r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    err, rep = _rs._split_marker(r.stderr)
    if not rep:
        raise FileNotFoundError("contained run gave no wrapper report (rc %d): %s" % (r.returncode, err.strip()[-300:]))
    if not rep.get("ok"):
        raise RuntimeError("refused: child landed outside rm-harness.slice: %s" % rep.get("placement"))
    if rep.get("oom_kill"):
        err += "\nKILLED by memory cap (oom_kill=%s, cap %d bytes)" % (rep["oom_kill"], cap)
    return subprocess.CompletedProcess(r.args, r.returncode, r.stdout, err)
