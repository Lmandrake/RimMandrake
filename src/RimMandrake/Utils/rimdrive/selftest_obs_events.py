"""Selftest for the RETIRED rimdrive.obs_events shim (design 08 P5, 2026-10-21): every old entry point
still exists, does nothing, writes nothing and never raises; Session.call no longer routes through it.
Run: python3 selftest_obs_events.py"""
# selftest temp containment (wave 7, DIRTY_CODE_REVIEW_STANDING_LOOP_1): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit — this
# test used to leave its temp dirs behind in the seat TMPDIR on every run.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_obs_events_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
from rimdrive import obs_events as O  # noqa: E402
from rimdrive import session as S  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


tmp = tempfile.mkdtemp(prefix="obs_shim_")
rid = O.new_run_id("t")
check("new_run_id still returns a unique id", isinstance(rid, str) and rid.endswith("-%d" % os.getpid()))
check("install is a no-op", O.install(rid, tmp) is None and O.current() is None)
h = O.call_start("x")
O.call_end(h, "ok", True)
O.end_exception(h, TimeoutError("timed out"))
O.uninstall()
check("no file written", os.listdir(tmp) == [])
check("classify_result kept", O.classify_result({"success": False}) == ("reply_fail", False))
check("classify_exception kept", O.classify_exception(TimeoutError("x")) == ("timeout", True))
src = open(S.__file__, encoding="utf-8").read()
check("Session no longer calls obs_events", "obs_events" not in src)

if FAILS:
    print("\nFAILED: %s" % FAILS)
    sys.exit(1)
print("\nOK: selftest_obs_events")
