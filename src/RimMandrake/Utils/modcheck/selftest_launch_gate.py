"""Selftest for launch_gate (negative controls included). Run: python3 selftest_launch_gate.py"""
# selftest temp containment (wave 7, DIRTY_CODE_REVIEW_STANDING_LOOP_1): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit — this
# test used to leave its temp dirs behind in the seat TMPDIR on every run.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_launch_gate_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import launch_gate as G   # noqa: E402

BAD = ("Bridge token: abc\n"
       'Exception loading def from file Stats.xml: System.ArgumentException: Could not find type named '
       'RimMandrake.Stillsand.RM_StatPart_SunPowered from node <li Class="RimMandrake.Stillsand.RM_StatPart_SunPowered" />\n'
       "Could not find a type named RimMandrake.TheForge.CompProperties_KeelBrace\n")
CLEAN = "Bridge token: abc\nCould not find type named SomeDonor.Thing from node\nall fine\n"
res = []


def check(n, c):
    res.append(c)
    print("%s %s" % ("ok  " if c else "FAIL", n))


r = G.scan(BAD)
check("fake log with missing RimMandrake types FAILS", not r["ok"] and len(r["missing_types"]) == 2)
check("both spellings ('type named' / 'a type named') found", "RimMandrake.TheForge.CompProperties_KeelBrace" in r["missing_types"])
check("clean log passes (donor-mod missing type is not ours)", G.scan(CLEAN)["ok"])
check("sanity probe: log without Bridge token is UNMEASURED, not clean", not G.scan("nothing here\n")["ok"] and not G.scan("")["probe"])
p = os.path.join(tempfile.mkdtemp(), "Player.log")
open(p, "w").write(BAD)
check("file path route fails on bad log", not G.check_player_log(p)["ok"])
open(p, "w").write(CLEAN)
check("file path route passes on clean log", G.check_player_log(p)["ok"])
check("missing file is UNMEASURED not clean", not G.check_player_log(p + ".nope")["ok"])
print("%d/%d" % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)
