#!/usr/bin/env python3
"""Guard: a Conductor goodbye restart is never cancelled by text, and a goodbye that IS cancelled alarms the Conductor
(GOODBYE_CANCEL_FIX_PEER_ATE_THE_NIGHT; 2026-11-01 a peer's message cancelled his goodbye with one journal line, and
the window ran all night).

Runs selftest_seat_restart's G2 (text never cancels) and GC (a cancel alarms) checks against seat_restart.py.

    python3 src/RimMandrake/rimflow/selftest_goodbye_cancel_alarms.py              # the working tree: must pass
    python3 src/RimMandrake/rimflow/selftest_goodbye_cancel_alarms.py --at <sha>   # seat_restart.py at that commit
                                                                                   # (replays the instance; red before 70a1ba5e)
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)


def _seat_restart_at(sha, tmp):
    src = subprocess.run(["git", "show", "%s:src/RimMandrake/rimflow/seat_restart.py" % sha], cwd=ROOT,
                         capture_output=True, check=True, timeout=60, stdin=subprocess.DEVNULL).stdout
    p = os.path.join(tmp, "seat_restart_at.py")
    with open(p, "wb") as f:
        f.write(src)
    spec = importlib.util.spec_from_file_location("seat_restart_at", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv):
    import selftest_seat_restart as T
    tmp = tempfile.mkdtemp(prefix="goodbye_guard_")
    try:
        if "--at" in argv:
            T.SR = _seat_restart_at(argv[argv.index("--at") + 1], tmp)
        T.SR.UNFILED = lambda t: None       # fixtures name no real item
        T.test_g2_bench_restart_holds_on_helpers_input_owner_and_reply()
        T.test_gc_a_cancelled_goodbye_alarms_the_conductor()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(T.TMP, ignore_errors=True)
    print("\n%s: %d failure(s)" % ("FAIL" if T.FAILS else "PASS", len(T.FAILS)))
    return 1 if T.FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
