#!/usr/bin/env python3
"""winbuild.rsync_stage must restage a same-size edit made within 2 s of the previous copy
(WINBUILD_STAGE_REPAIR_STALE_SOURCE). The old --modify-window=2 rsync skipped it, so MSBuild built stale source.

The mtime clauses are made falsifiable (WINBUILD_SELFTEST_FIX_VACUOUS_MTIME_CHECK): the source carries an mtime 1000 s
old, so a stage that copied it with -t and no os.utime (mutant M1) reads old, and a control runs M1 to show it. A
stubbed stage_build must route its copy through rsync_stage and run no rsync of its own (mutant M2)."""
import inspect, os, subprocess, sys, tempfile, time, types
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winbuild

OLD = 1000          # seconds; far outside any clock slack


def bumped(path, since):
    """The staged mtime counts as bumped only if it is no older than the moment the restage began."""
    return os.stat(path).st_mtime >= since - 1


def m1_stage(rels, stage, cwd, excl=()):
    """Mutant M1: content-checked rsync that keeps -t and never touches the mtime."""
    return subprocess.run(["rsync", "-rtR", "-c", "-i", *excl, *rels, stage + "/"], cwd=cwd,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=120)


def restage_check(stage_fn, t, tag):
    """Copy, then a same-size edit whose mtime is OLD s in the past. -> (content restaged, mtime bumped, unchanged kept)."""
    src, stage = os.path.join(t, tag, "repo"), os.path.join(t, tag, "stage")
    os.makedirs(os.path.join(src, "m")); os.makedirs(stage)
    f = os.path.join(src, "m", "a.cs")
    open(f, "w").write("int x = 1;")
    assert stage_fn(["m/"], stage, src).returncode == 0
    st = os.path.join(stage, "m", "a.cs")
    assert open(st).read() == "int x = 1;"
    old = time.time() - OLD
    open(f, "w").write("int x = 2;")
    os.utime(f, (old, old))
    os.utime(st, (old, old))        # the stage's copy is as old as the clone's: only a bump makes it newer than obj
    since = time.time()
    r = stage_fn(["m/"], stage, src)
    assert r.returncode == 0
    content = open(st).read() == "int x = 2;"
    mtime = bumped(st, since)
    m2 = os.stat(st).st_mtime
    stage_fn(["m/"], stage, src)
    return content, mtime, os.stat(st).st_mtime == m2


def stage_build_calls(stage_fn, t):
    """Run a stubbed stage_build with winbuild.rsync_stage = stage_fn. -> (rsync_stage calls, raw rsync subprocesses)."""
    calls, raw, inside = [], [], []
    real_run = winbuild.subprocess.run

    def run(cmd, *a, **kw):
        if not inside and cmd and os.path.basename(str(cmd[0])) == "rsync":
            raw.append(cmd)                 # an rsync stage_build ran itself, not through rsync_stage
            return types.SimpleNamespace(returncode=0, stdout="", stderr="")
        return real_run(cmd, *a, **kw)

    def spy(rels, stage, cwd, excl=()):
        calls.append(rels)
        inside.append(1)
        try:
            return stage_fn(rels, stage, cwd, excl)
        finally:
            inside.pop()
    stubs = {"BUILD_ROOT": os.path.join(t, "build"), "LOCK_DIR": os.path.join(t, "locks"),
             "needed_dirs": lambda csproj, seen=None: {os.path.dirname(csproj)}, "win": lambda p: p,
             "_ce_snapshot": lambda scope=None: None, "source_sha": lambda paths: ("0" * 40, False),
             "built_outputs": lambda tree, since: [], "_copy_back": lambda outs, stage, record, staged_in=None: None,
             "rsync_stage": spy, "run_dotnet": lambda csproj_win, cwd, config, extra: 0}
    saved = {k: getattr(winbuild, k) for k in stubs}
    for k, v in stubs.items():
        setattr(winbuild, k, v)
    winbuild.subprocess.run = run
    try:
        winbuild.stage_build(os.path.join(winbuild.ROOT, "src", "RimMandrake", "M", "Source", "M.csproj"))
    finally:
        winbuild.subprocess.run = real_run
        for k, v in saved.items():
            setattr(winbuild, k, v)
    return calls, raw


def main():
    with tempfile.TemporaryDirectory() as t:
        content, mtime, kept = restage_check(winbuild.rsync_stage, t, "real")
        assert content, "stage kept stale source"
        assert mtime, "staged mtime not bumped past the clone's old mtime"
        assert kept, "an unchanged file's staged mtime was touched"
        r = winbuild.rsync_stage([], t, t)
        assert isinstance(r, subprocess.CompletedProcess), "rsync_stage returned %r" % type(r)
        # control M1: -t kept, os.utime dropped -> content right, mtime old; the mtime check must see it
        c1, m1, _ = restage_check(m1_stage, t, "m1")
        assert c1 and not m1, "control: M1 (-t, no utime) is not caught by the mtime check (content %s, bumped %s)" % (c1, m1)
        print("control M1 caught: content restaged, mtime left %d s old" % OLD)
        # the old --modify-window=2 rsync skips the same-size edit
        src = os.path.join(t, "real", "repo"); f = os.path.join(src, "m", "a.cs")
        old = os.path.join(t, "old"); os.makedirs(os.path.join(old, "m"))
        m = os.stat(f).st_mtime
        subprocess.run(["rsync", "-rtR", "--modify-window=2", "m/", old + "/"], cwd=src, check=True)
        open(f, "w").write("int x = 3;"); os.utime(f, (m, m))
        subprocess.run(["rsync", "-rtR", "--modify-window=2", "m/", old + "/"], cwd=src, check=True)
        o = open(os.path.join(old, "m", "a.cs")).read()
        assert o != "int x = 3;", "control: old rsync no longer reproduces the bug"
        print("old behaviour kept %r (control)" % o)
        # stage_build routes its copy through rsync_stage and runs no rsync itself
        calls, raw = stage_build_calls(winbuild.rsync_stage, os.path.join(t, "sb"))
        assert calls and not raw, "stage_build: %d rsync_stage calls, %d raw rsync runs" % (len(calls), len(raw))
        # control M2: _stage_build_locked back on the old raw rsync must be seen
        src_fn = inspect.getsource(winbuild._stage_build_locked)
        call = "rsync_stage(rels, stage, ROOT, excl)"
        assert src_fn.count(call) == 1, "stage_build's copy no longer reads %r: update this control" % call
        ns = dict(winbuild.__dict__)
        exec(src_fn.replace(call, 'subprocess.run(["rsync", "-rtR", "--modify-window=2", *excl, *rels, stage + "/"], '
                            'cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)'), ns)
        real = winbuild._stage_build_locked
        # rebound to the live module globals, so the stubs stage_build_calls installs reach the mutant too
        winbuild._stage_build_locked = types.FunctionType(ns["_stage_build_locked"].__code__, winbuild.__dict__)
        try:
            calls2, raw2 = stage_build_calls(winbuild.rsync_stage, os.path.join(t, "sb2"))
        finally:
            winbuild._stage_build_locked = real
        assert raw2 and not calls2, "control: M2 (old rsync in stage_build) is not caught (%d calls, %d raw)" % (
            len(calls2), len(raw2))
        print("control M2 caught: raw rsync seen, rsync_stage not called")
    print("PASS selftest_winbuild_stage_content")

main()
