#!/usr/bin/env python3
"""winbuild.rsync_stage must restage a same-size edit made within 2 s of the previous copy
(WINBUILD_STAGE_REPAIR_STALE_SOURCE). The old --modify-window=2 rsync skipped it, so MSBuild built stale source."""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winbuild

def main():
    with tempfile.TemporaryDirectory() as t:
        src, stage = os.path.join(t, "repo"), os.path.join(t, "stage")
        os.makedirs(os.path.join(src, "m")); os.makedirs(stage)
        f = os.path.join(src, "m", "a.cs")
        open(f, "w").write("int x = 1;")
        r = winbuild.rsync_stage(["m/"], stage, src)
        assert r.returncode == 0
        st = os.path.join(stage, "m", "a.cs")
        assert open(st).read() == "int x = 1;"
        # same-size edit, mtime forced to the same second (and then older, as a cp -p restore would give)
        m = os.stat(st).st_mtime
        open(f, "w").write("int x = 2;")
        os.utime(f, (m, m))
        r = winbuild.rsync_stage(["m/"], stage, src)
        got = open(st).read()
        assert got == "int x = 2;", "stage kept stale source: %r" % got
        assert os.stat(st).st_mtime > m - 0.5 and os.stat(st).st_mtime >= m, "staged mtime not bumped"
        # unchanged file is not touched
        m2 = os.stat(st).st_mtime
        winbuild.rsync_stage(["m/"], stage, src)
        assert os.stat(st).st_mtime == m2
        # prove the old behaviour fails this test
        old = os.path.join(t, "old"); os.makedirs(os.path.join(old, "m"))
        subprocess.run(["rsync", "-rtR", "--modify-window=2", "m/", old + "/"], cwd=src, check=True)
        open(f, "w").write("int x = 3;"); os.utime(f, (m, m))
        subprocess.run(["rsync", "-rtR", "--modify-window=2", "m/", old + "/"], cwd=src, check=True)
        o = open(os.path.join(old, "m", "a.cs")).read()
        assert o != "int x = 3;", "control: old rsync no longer reproduces the bug"
        print("old behaviour kept %r (control)" % o)
    print("PASS selftest_winbuild_stage_content")

main()
