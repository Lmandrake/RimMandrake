#!/usr/bin/env python3
"""build.py's deploy step is atomic, held and read back (RIMMANDRAKE_MAKE_COMPANION_DEPLOY_ATOMIC_HELD).

Offline: a temp GAME_ROOT/DEPLOY_DIR, the game-process and bridge-hold probes stubbed. Checks:
  identical bytes copy nothing; a failed replace leaves the old DLL byte-identical and no temp file behind;
  a readback mismatch exits non-zero and never says "deployed"; a running game or a foreign bridge hold refuses
  before any byte is written, and --ignore-bridge-hold passes the hold; the bytes written are the verified bytes;
  --clean waits for the stage lock a peer build holds (x.B4); a tree inside a foreign checkout that TRACKS the
  companion sources reads that checkout's status, and one that tracks none is an export (x.B6).
BUILD_PY=<path> runs it against another copy of build.py placed in THIS directory (build.py finds the repo from
its own path); that is how it was watched failing on the base: 6 of 8 checks FAIL there (2026-11-15), and the
four x.B4/x.B6 checks added 2026-11-19: 3 FAIL on the base build.py (the untracked-export case already passed).
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


def clean_waits_for_stage_lock(B, tmp):
    """x.B4: --clean must not wipe the shared stage while a peer build holds its stage lock."""
    import threading
    import time
    W = getattr(B, "winbuild", None)
    if W is None or not B.STAGED:
        check(False, "clean_waits_for_stage_lock", "build.py is not on the staged route here (needs WSL)")
        return
    saved = (W.BUILD_ROOT, W.LOCK_DIR, W.stage_build, B.ARTIFACT_DIR, B.src_hash_prop)
    try:
        W.BUILD_ROOT, W.LOCK_DIR = os.path.join(tmp, "stage_root"), os.path.join(tmp, "locks")
        B.ARTIFACT_DIR = os.path.join(tmp, "clone_art")          # never the clone's real artifacts
        B.src_hash_prop = lambda: "-p:JawaSrcHash=selftest"
        calls = []
        W.stage_build = lambda *a, **k: (calls.append(k.get("dry_run")), (0, {}))[1]
        rel_art = os.path.relpath(B.ARTIFACT_DIR, B.REPO_ROOT)
        stage_art = os.path.join(W.BUILD_ROOT, "JawaBench", rel_art)
        os.makedirs(stage_art)
        os.makedirs(B.ARTIFACT_DIR)
        if not hasattr(W, "stage_lock"):
            check(False, "clean_waits_for_stage_lock", "winbuild has no stage_lock")
            return
        with W.stage_lock("JawaBench"):                       # a peer build mid-compile
            t = threading.Thread(target=lambda: B.build_staged(True, False), daemon=True)
            t.start()
            time.sleep(0.5)
            survived = os.path.isdir(stage_art)
        t.join(10)
        check(survived and not os.path.isdir(stage_art) and not os.path.isdir(B.ARTIFACT_DIR) and calls,
              "clean_waits_for_stage_lock", (survived, os.path.isdir(stage_art), calls))
    finally:
        W.BUILD_ROOT, W.LOCK_DIR, W.stage_build, B.ARTIFACT_DIR, B.src_hash_prop = saved


def foreign_checkout_status(B, tmp):
    """x.B6: REPO_ROOT inside a foreign git checkout."""
    import subprocess
    saved = (B.REPO_ROOT, B.PROJECT)
    top = os.path.join(tmp, "foreign")
    root = os.path.join(top, "sub")
    proj_dir = os.path.join(root, "src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools")
    os.makedirs(proj_dir)
    open(os.path.join(top, "README"), "w").write("x")
    cs = os.path.join(proj_dir, "A.cs")
    open(cs, "w").write("class A {}")
    g = lambda *a: subprocess.run(["git", "-C", top] + list(a), capture_output=True, text=True)
    g("init", "-q")
    g("-c", "user.name=t", "-c", "user.email=t@t", "add", "README")
    g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x")
    try:
        B.REPO_ROOT, B.PROJECT = root, os.path.join(proj_dir, "JawaBench.BridgeTools.csproj")
        got = B.source_dirty()
        check(got is None, "foreign_checkout_untracked_is_export", got)
        g("-c", "user.name=t", "-c", "user.email=t@t", "add", "sub")
        g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "y")
        got = B.source_dirty()
        check(got == [], "foreign_checkout_tracked_clean_reads_clean", got)
        open(cs, "a").write("// a peer's edit")
        got = B.source_dirty()
        check(bool(got) and any("A.cs" in ln for ln in got), "foreign_checkout_tracked_dirty_reads_dirty", got)
    finally:
        B.REPO_ROOT, B.PROJECT = saved


def game_a_deploy_ignores_game_b(B):
    """A game-b process never maps game a's companion (each game has its own install and BridgeTools), so with game b up
    and game a down, game a's deploy is not refused (RIMMANDRAKE_REPAIR_FLOWWORKS_FORM_REFUSAL_AT_THE_RUN_FOUR: the
    in-game launch's companion repair stops game a only). A game a row, or a row nobody can attribute, still counts."""
    real = load()

    class GI:
        rows = []

        def games(self):
            return self.rows

        def running(self, name=None):
            return any(g["instance"] in (name, None) for g in self.rows)
    gi = GI()
    real._gi, real.GAME = (lambda: gi), "a"
    got = []
    for rows in ([{"instance": "b"}], [{"instance": "a"}, {"instance": "b"}], [{"instance": None}], []):
        gi.rows = rows
        got.append(real.game_running())
    check(got == [False, True, True, False], "game_a_deploy_ignores_game_b",
          "b only / a+b / unattributed / none read %s, want [False, True, True, False]" % got)


def own_take_is_no_hold(B):
    """RIMMANDRAKE_REPAIR_PYRELANDS_FORM_REFUSAL_AT_THE_RUN_EIGHT: the in-game visit's repair holds game a's lock and
    runs this build as its child, under the take it exported (RM_HOST_GUARD_GEN). Its own take is no hold; another live
    process's BENCH hold still is (every detached run is BENCH, so a seat name cannot tell them apart)."""
    import subprocess
    import tempfile as T
    real = load()
    real.GAME = "a"
    rf = os.path.join(os.path.dirname(HERE), "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    import game_lock as GL
    import driver_lock as DL
    path = os.path.join(T.mkdtemp(prefix="selftest_build_lock_"), "DRIVER_LOCK.json")
    keys = ("RIMFLOW_DRIVER_LOCK", "RM_GAME_INSTANCE", "RM_HOST_GUARD_GEN", "RM_DRIVER_PID")
    was = {k: os.environ.get(k) for k in keys}
    os.environ["RIMFLOW_DRIVER_LOCK"] = path
    for k in keys[1:]:
        os.environ.pop(k, None)
    sleeper = subprocess.Popen(["sleep", "60"])
    got = []
    try:
        # the take of a parent run (a process that is not this one or an ancestor), exported to this child
        r = GL.claim("a", "repair", seat="BENCH", identity=dict(DL.my_identity(), pid=sleeper.pid,
                                                                  start=DL._proc_start(sleeper.pid)), path=path)
        os.environ["RM_HOST_GUARD_GEN"] = str(r.get("generation"))
        got.append(real.bridge_holder())
        os.environ.pop("RM_HOST_GUARD_GEN")
        got.append(real.bridge_holder())
    finally:
        sleeper.kill()
        sleeper.wait()
        for k, v in was.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    check(r.get("ok") and got == [None, "BENCH"], "own_take_is_no_hold",
          "under the exported take / without it read %s, want [None, 'BENCH'] (%s)" % (got, r.get("line")))


def gm_tools_by_default(B):
    """A bare build.py includes the GM tools and --no-gm leaves them out; the csproj's own default agrees. (A bare build
    once planned a DLL with 50 tools fewer than the game's copy, to guard a game that nobody plays.)"""
    class Stop(Exception):
        pass
    seen = []
    keep = B.build, B.source_dirty, B.aim

    def spy(clean, gm):
        seen.append(gm)
        raise Stop()
    B.build, B.source_dirty, B.aim = spy, (lambda: []), (lambda *a, **k: None)
    try:
        for argv in ([], ["--gm"], ["--no-gm"]):
            try:
                B.main(argv)
            except Stop:
                pass
            except SystemExit as e:
                seen.append("exit %s" % e.code)
    finally:
        B.build, B.source_dirty, B.aim = keep
    check(seen == [True, True, False], "gm_tools_by_default", seen)
    proj = open(os.path.join(os.path.dirname(os.path.abspath(B.__file__)), "JawaBench.BridgeTools",
                             "JawaBench.BridgeTools.csproj"), encoding="utf-8").read()
    check("""Condition="'$(JawaGmTools)' == ''">true</JawaGmTools>""" in proj, "csproj_gm_tools_by_default")


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
        clean_waits_for_stage_lock(B, tmp)
        foreign_checkout_status(B, tmp)
        game_a_deploy_ignores_game_b(B)
        own_take_is_no_hold(B)
        gm_tools_by_default(B)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("build deploy: %d failure(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
