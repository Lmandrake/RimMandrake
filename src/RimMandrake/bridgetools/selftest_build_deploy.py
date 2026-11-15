#!/usr/bin/env python3
"""build.py's deploy step is atomic, held and read back (RIMMANDRAKE_MAKE_COMPANION_DEPLOY_ATOMIC_HELD).

Offline: a temp GAME_ROOT/DEPLOY_DIR, the game-process and bridge-hold probes stubbed. Checks:
  identical bytes copy nothing; a failed replace leaves the old DLL byte-identical and no temp file behind;
  a readback mismatch exits non-zero and never says "deployed"; a running game or a foreign bridge hold refuses
  before any byte is written, and --ignore-bridge-hold passes the hold; the bytes written are the verified bytes.
BUILD_PY=<path> runs it against another copy of build.py placed in THIS directory (build.py finds the repo from
its own path); that is how it was watched failing on the base: 6 of 8 checks FAIL there.
"""
import contextlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def check(ok, name, why=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else "  " + str(why)))
    if not ok:
        fails.append(name)


def load():
    path = os.environ.get("BUILD_PY") or os.path.join(HERE, "build.py")
    sys.path.insert(0, HERE)
    spec = importlib.util.spec_from_file_location("build_under_test", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run(B, dll, apply_it=True, **kw):
    """-> (exit code or None, stdout)."""
    out = io.StringIO()
    code = None
    with contextlib.redirect_stdout(out):
        try:
            B.plan_deploy(dll, apply_it, **kw)
        except SystemExit as e:
            code = e.code if e.code is not None else 0
            out.write("\nEXIT %s" % e.code)
    return code, out.getvalue()


def main():
    B = load()
    tmp = tempfile.mkdtemp(prefix="selftest_build_deploy_")
    try:
        B.GAME_ROOT = os.path.join(tmp, "game")
        B.DEPLOY_DIR = os.path.join(B.GAME_ROOT, "Mods", "JawaBench")
        os.makedirs(B.DEPLOY_DIR)
        target = os.path.join(B.DEPLOY_DIR, B.DLL_NAME)
        dll = os.path.join(tmp, "built.dll")
        new, old = b"MZ new build bytes " * 50, b"MZ old deployed bytes " * 50
        B.tool_surface = lambda data: set()                 # surfaces are build.py's other guard, not this test's
        B.build_stamp = lambda data: None
        game = {"up": False}
        hold = {"holder": None}
        B.game_running = lambda: game["up"]                 # absent on the base: the base never asks
        B.bridge_holder = lambda: hold["holder"]

        def reset():
            open(dll, "wb").write(new)
            open(target, "wb").write(old)

        # 1. identical bytes: nothing copied
        open(dll, "wb").write(new)
        open(target, "wb").write(new)
        before = os.stat(target).st_mtime_ns
        os.utime(target, ns=(before - 10 ** 9, before - 10 ** 9))
        stamp = os.stat(target).st_mtime_ns
        code, out = run(B, dll)
        check(code is None and os.stat(target).st_mtime_ns == stamp and "identical" in out.lower(),
              "identical_bytes_copy_nothing", out[-300:])

        # 2. a failing replace leaves the old DLL and no temp file
        reset()
        real_replace, real_copy2 = os.replace, shutil.copy2

        def boom(*a, **k):
            e = OSError(22, "a file with a user-mapped section open")
            e.winerror = 1224
            raise e
        os.replace = boom
        shutil.copy2 = boom
        try:
            code, out = run(B, dll)
        finally:
            os.replace, shutil.copy2 = real_replace, real_copy2
        left = sorted(os.listdir(B.DEPLOY_DIR))
        check(code not in (None, 0) and open(target, "rb").read() == old and left == [B.DLL_NAME],
              "failed_replace_keeps_old_dll_and_no_temp", (code, left, out[-200:]))

        # 3. readback mismatch exits non-zero, never "deployed"
        reset()

        def corrupting(src, dst, *a, **k):
            real_replace(src, dst)
            open(dst, "ab").write(b"!")
        os.replace = corrupting
        shutil.copy2 = lambda s, d, *a, **k: (real_copy2(s, d), open(d, "ab").write(b"!"))
        try:
            code, out = run(B, dll)
        finally:
            os.replace, shutil.copy2 = real_replace, real_copy2
        check(code not in (None, 0) and "\ndeployed" not in out, "readback_mismatch_exits_nonzero", (code, out[-200:]))

        # 4. a running game refuses before any write
        reset()
        game["up"] = True
        code, out = run(B, dll)
        game["up"] = False
        check(code not in (None, 0) and open(target, "rb").read() == old and "RUNNING" in out + str(code),
              "running_game_refuses_before_write", (code, out[-200:]))

        # 5. a foreign bridge hold refuses; the flag passes it
        reset()
        hold["holder"] = "OWNER"
        code, out = run(B, dll)
        check(code not in (None, 0) and open(target, "rb").read() == old, "foreign_bridge_hold_refuses", (code, out[-200:]))
        try:
            code, out = run(B, dll, ignore_hold=True)
        except TypeError as e:
            code, out = "TypeError", str(e)
        check(code is None and open(target, "rb").read() == new and "deployed" in out, "ignore_bridge_hold_deploys", (code, out[-200:]))
        hold["holder"] = None

        # 6. the bytes written are the verified bytes, not a re-read of the path (x.B3)
        reset()
        code, out = run(B, dll)
        check(code is None and open(target, "rb").read() == new, "deploys_the_built_bytes", (code, out[-200:]))

        # 7. a stale sibling in the deploy dir is named in the plan (x.B9)
        open(os.path.join(B.DEPLOY_DIR, "JawaBench.Old.dll"), "wb").write(b"MZ stale")
        code, out = run(B, dll, apply_it=False)
        check("JawaBench.Old.dll" in out, "plan_names_stale_siblings", out[-200:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("build deploy: %d failure(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
