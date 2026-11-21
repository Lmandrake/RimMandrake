"""Offline checks for pit_relief_live.py (RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN): every FakeBridge fault (a
planted defect: the pre-rebuild layer, the 2-argument MapMeshDirty, an old deploy, a blind instrument, a refused dig) lands on
its expected row, the clean model passes, and the pure verdict can go red. No bridge."""
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_pit_relief_live_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import contextlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pit_relief_live as P  # noqa: E402

fails = []


def check(name, cond):
    print("%-4s  %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


def run(faults):
    out = os.path.join(tempfile.gettempdir(), "pr_%s.json" % (faults or "clean"))
    with contextlib.redirect_stdout(io.StringIO()):
        rc = P.main(["--mock", out] + (["--mock-faults", faults] if faults else []))
    rows = {r["id"]: (r["status"], r["class"]) for r in json.load(open(out))["rows"]}
    return rc, rows


SQ, EDGE = P.ROW_IDS
want = {
    "": (0, {SQ: ("PASS", "MOD"), EDGE: ("PASS", "MOD")}),
    "no_redraw": (1, {SQ: ("FAIL", "MOD"), EDGE: ("FAIL", "MOD")}),
    "two_arg": (1, {SQ: ("PASS", "MOD"), EDGE: ("FAIL", "MOD")}),
    "old_deploy": (2, {SQ: ("UNMEASURED", "HARNESS"), EDGE: ("UNMEASURED", "HARNESS")}),
    "no_dig": (2, {SQ: ("UNMEASURED", "SITE"), EDGE: ("UNMEASURED", "SITE")}),
    "blind": (2, {SQ: ("UNMEASURED", "HARNESS"), EDGE: ("UNMEASURED", "HARNESS")}),
}
for f, (rc_want, rows_want) in want.items():
    rc, rows = run(f)
    check("mock %-10s rc %d rows %s" % (f or "clean", rc, rows), rc == rc_want and rows == rows_want)

b = {"fresh": "a", "stale": "False", "dirty": "False"}
check("verdict: stale and not dirty is FAIL", P.mesh_verdict(b, {"built": "a", "fresh": "b", "stale": "True", "dirty": "False"})[0] == "FAIL")
check("verdict: stale but dirty is PASS", P.mesh_verdict(b, {"built": "a", "fresh": "b", "stale": "True", "dirty": "True"})[0] == "PASS")
check("verdict: art unchanged is SITE, never PASS", P.mesh_verdict(b, {"built": "a", "fresh": "a", "stale": "False", "dirty": "False"})[:2] == ("UNMEASURED", "SITE"))
check("verdict: a missing read is HARNESS", P.mesh_verdict(b, None)[:2] == ("UNMEASURED", "HARNESS"))
print("%s: %d checks failed" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
