#!/usr/bin/env python3
"""Selftest for winbuild.stage_build's locks (review night): two builds of ONE stage never overlap from the rsync to the
end of the build (one would rsync --delete under the other's compile), and two builds of DIFFERENT stages never copy
back at the same time (a shared dependency's dll and .srchash would land as a mismatched pair). No dotnet; the steps are
stubbed and timed, except main_atmos_fresh_stage, whose rsync is real because what it staged is the point."""
import importlib.util
import os
import re
import sys
import tempfile
import threading
import time
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winbuild as WB  # noqa: E402

FAILS = []


def check(ok, msg, detail=""):
    print(("ok    " if ok else "FAIL  ") + msg + ("" if ok else "  %s" % (detail,)))
    if not ok:
        FAILS.append(msg)


def overlaps(spans):
    spans = sorted(spans)
    return any(b[0] < a[1] for a, b in zip(spans, spans[1:]))


def main():
    with tempfile.TemporaryDirectory() as td:
        build_spans, copy_spans, errs = [], [], []
        mu = threading.Lock()
        saved = {k: getattr(WB, k, None) for k in ("BUILD_ROOT", "LOCK_DIR", "needed_dirs", "win", "_ce_snapshot",
                                                   "rsync_stage", "source_sha", "run_dotnet", "built_outputs",
                                                   "_copy_back")}
        WB.BUILD_ROOT, WB.LOCK_DIR = os.path.join(td, "build"), os.path.join(td, "locks")
        WB.needed_dirs = lambda csproj, seen=None: {os.path.dirname(csproj)}
        WB.win = lambda p: p
        WB._ce_snapshot = lambda scope=None: None
        WB.source_sha = lambda paths: ("0" * 40, False)
        WB.built_outputs = lambda tree, since: [os.path.join(tree, "Assemblies", "X.dll")]
        starts = {}

        rsync_spans = []

        def rsync(rels, stage, cwd, excl=()):
            starts[threading.get_ident()] = t0 = time.time()
            time.sleep(0.15)
            with mu:
                rsync_spans.append((t0, time.time()))
            return types.SimpleNamespace(returncode=0, stdout="")

        def dotnet(csproj_win, cwd, config, extra):
            time.sleep(0.05)
            with mu:
                build_spans.append((os.path.basename(os.path.dirname(cwd)), starts[threading.get_ident()], time.time()))
            return 0

        def copy_back(outs, stage, record, staged_in=None):
            t0 = time.time()
            time.sleep(0.4)
            with mu:
                copy_spans.append((t0, time.time()))
        WB.rsync_stage, WB.run_dotnet, WB._copy_back = rsync, dotnet, copy_back
        proj = lambda m: os.path.join(WB.ROOT, "src", "RimMandrake", m, "Source", "%s.csproj" % m)  # noqa: E731

        def go(m):
            if m == "ModB":
                time.sleep(0.3)       # its rsync lands inside ModA's first copy-back unless the lock orders them
            try:
                rc, _ = WB.stage_build(proj(m))
                if rc:
                    errs.append((m, rc))
            except Exception as e:  # noqa: BLE001
                errs.append((m, repr(e)))
        try:
            ts = [threading.Thread(target=go, args=(m,)) for m in ("ModA", "ModA", "ModB")]
            for t in ts:
                t.start()
            for t in ts:
                t.join(30)
        finally:
            for k, v in saved.items():
                if v is not None:
                    setattr(WB, k, v)
        check(not errs, "three stubbed builds ran", errs)
        check(len(copy_spans) == 3 and not overlaps(copy_spans), "copy-backs never overlap across stages", copy_spans)
        mixed = [(a, b) for a in rsync_spans for b in copy_spans if a[0] < b[1] and b[0] < a[1]]
        check(len(rsync_spans) == 3 and not mixed, "no stage rsync reads while another build copies back (r3)", mixed)
    print("\n%s" % ("FAILED %d" % len(FAILS) if FAILS else "all passed"))
    return FAILS


def main_clones_independent():
    """The pair lock belongs to one clone (NIGHTLY_COP_FIX_RED_HMGHDI_RQAA): another tree's copy-back or long rsync never
    queues this clone's build, and within a clone staging readers share while a copy-back excludes them."""
    import fcntl
    with tempfile.TemporaryDirectory() as td:
        saved = WB.LOCK_DIR, WB.ROOT
        WB.LOCK_DIR = os.path.join(td, "locks")
        try:
            WB.ROOT = os.path.join(td, "cloneA")
            a = WB._clone_pairs_lock()
            WB.ROOT = os.path.join(td, "cloneB")
            b = WB._clone_pairs_lock()
            check(a != b, "two clones hold different pair locks", (a, b))
            os.makedirs(WB.LOCK_DIR)
            path = os.path.join(WB.LOCK_DIR, a + ".lock")

            def free(mode):
                with open(path, "w") as f:
                    try:
                        fcntl.flock(f, mode | fcntl.LOCK_NB)
                    except BlockingIOError:
                        return False
                    fcntl.flock(f, fcntl.LOCK_UN)
                    return True
            WB.ROOT = os.path.join(td, "cloneA")
            with WB._flock(a, shared=True):
                check(free(fcntl.LOCK_SH), "a staging reader lets another staging reader in")
                check(not free(fcntl.LOCK_EX), "a staging reader excludes a copy-back")
            with WB._flock(a):
                check(not free(fcntl.LOCK_SH), "a copy-back excludes a staging reader")
        finally:
            WB.LOCK_DIR, WB.ROOT = saved


def main_clones_never_queue():
    """Two real processes through the real stage_build, each its own clone: B gets on with its work while A sits inside
    the step that used to hold a machine-wide lock. main_clones_independent only reads the helper's return value and
    would stay green if stage_build stopped using it (blind check, NIGHTLY_COP_FIX_RED_HMGHDI_RQAA). The same harness
    with ONE clone must queue: that control proves the harness can see a queue at all."""
    with tempfile.TemporaryDirectory() as raw:
        td = os.path.realpath(raw)

        def seen(name):
            return os.path.exists(os.path.join(td, "ev", name))

        def mark(name):
            open(os.path.join(td, "ev", name), "w").close()

        def await_mark(name, seconds):
            end = time.time() + seconds
            while time.time() < end:
                if seen(name):
                    return True
                time.sleep(0.01)
            return seen(name)

        def build(tag, clone, hold=None, until=None, seconds=0):
            pid = os.fork()
            if pid:
                return pid
            rc = 1
            try:
                os.dup2(os.open(os.devnull, os.O_WRONLY), 1)

                def step(name):
                    mark("%s.%s" % (tag, name))
                    if name == hold and await_mark(until, seconds):
                        mark("%s.%s.saw" % (tag, name))
                WB.ROOT = os.path.join(td, clone)
                WB.BUILD_ROOT, WB.LOCK_DIR = os.path.join(td, "build"), os.path.join(td, "locks")
                WB.needed_dirs = lambda csproj, seen=None: {os.path.dirname(csproj)}
                WB.win = lambda p: p
                WB._ce_snapshot = lambda scope=None: None
                WB.source_sha = lambda paths: ("0" * 40, False)
                WB.built_outputs = lambda tree, since: []
                WB.run_dotnet = lambda csproj_win, cwd, config, extra: 0
                WB.rsync_stage = lambda rels, stage, cwd, excl=(): (step("rsync"),
                                                                    types.SimpleNamespace(returncode=0, stdout=""))[1]
                WB._copy_back = lambda outs, stage, record, staged_in=None: step("copy")
                # a stage per build: the per-stage lock is another lock, on purpose shared by clones of one stage path
                proj = os.path.join(WB.ROOT, "src", "RimMandrake", "Mod" + tag, "Source", "Mod%s.csproj" % tag)
                rc = WB.stage_build(proj)[0]
            finally:
                os._exit(rc)

        def run(name, clone_b, a_hold, b_step, seconds):
            """-> did A, still inside a_hold, see B reach b_step?"""
            for sub in ("ev", "locks"):
                os.makedirs(os.path.join(td, sub), exist_ok=True)
            for f in os.listdir(os.path.join(td, "ev")):
                os.unlink(os.path.join(td, "ev", f))
            a = build("A", "cloneA", a_hold, "B." + b_step, seconds)
            entered = await_mark("A." + a_hold, 30)
            b = build("B", clone_b)
            rcs = [os.waitpid(p, 0)[1] for p in (a, b)]
            check(entered and rcs == [0, 0], "%s: both builds ran" % name, (entered, rcs))
            return seen("A.%s.saw" % a_hold)
        # generous: a green run leaves the moment B arrives, only a real queue costs the whole wait
        check(run("rsync past copy-back", "cloneB", "copy", "rsync", 15),
              "clone B's rsync starts while clone A is inside copy-back")
        check(run("copy-back past rsync", "cloneB", "rsync", "copy", 15),
              "clone B's copy-back runs while clone A is inside its long rsync (the measured 100 s queue)")
        check(run("copy-back past copy-back", "cloneB", "copy", "copy", 15),
              "clone B's copy-back runs while clone A is inside copy-back")
        check(not run("control: one clone", "cloneA", "copy", "rsync", 1.5),
              "control: within ONE clone the same harness shows the rsync queued behind the copy-back")
        check(run("control: one clone, readers", "cloneA", "rsync", "rsync", 15),
              "control: within ONE clone two staging rsyncs share")


def main_atmos_fresh_stage():
    """The atmos kernel's real stage call and a real rsync onto an EMPTY root, dotnet stubbed: every file its C# selftest
    finds by walking up is there. A reused stage keeps a file its stage list dropped (--delete prunes only inside the
    listed dirs), so the kernel test alone goes green on any root that ever held it (blind check,
    NIGHTLY_COP_FIX_RED_HMGHDI_RQAA, reverted extra_dirs: green reused, red empty)."""
    here = os.path.join(WB.ROOT, "src", "RimMandrake", "AtmosphericBase")
    # the reads come from the C# source, so a new FindUp is covered the day it is written
    wanted = set()
    src = os.path.join(here, "Source", "SelfTest")
    for n in sorted(os.listdir(src)):
        if n.endswith(".cs"):
            with open(os.path.join(src, n), encoding="utf-8") as f:
                for args in re.findall(r"FindUp\(\s*(?:System\.IO\.)?Path\.Combine\(([^)]*)\)", f.read()):
                    parts = re.findall(r'"([^"]+)"', args)
                    if parts and parts[0] == "src":
                        wanted.add(os.path.join(*parts))
    must = os.path.join("src", "RimUtinni", "UtinniPatches", "Defs", "AtmosphericBase", "RUT_NineSignatures.xml")
    check(must in wanted, "the source scan sees the Nine signature read (the instrument can see)", sorted(wanted))
    spec = importlib.util.spec_from_file_location("atmos_kernel_for_stage",
                                                  os.path.join(here, "selftest_atmosphericbase_kernel.py"))
    kernel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kernel)
    with tempfile.TemporaryDirectory() as td:
        names = ("BUILD_ROOT", "LOCK_DIR", "win", "_ce_snapshot", "run_dotnet", "built_outputs", "source_sha")
        saved = {k: getattr(WB, k) for k in names}
        real_run = kernel.subprocess.run

        def run(cmd, *a, **k):      # the wiring test and `dotnet run`, both this interpreter by DOTNET below; rsync is real
            if cmd[0] == sys.executable:
                return types.SimpleNamespace(returncode=0, stdout="", stderr="")
            return real_run(cmd, *a, **k)
        WB.BUILD_ROOT, WB.LOCK_DIR = os.path.join(td, "build"), os.path.join(td, "locks")
        os.makedirs(WB.BUILD_ROOT)
        WB.win = lambda p: p
        WB._ce_snapshot = lambda scope=None: None
        WB.run_dotnet = lambda csproj_win, cwd, config, extra: 0
        WB.built_outputs = lambda tree, since: []
        WB.source_sha = lambda paths: ("0" * 40, False)
        kernel.DOTNET = (sys.executable,)
        kernel.subprocess.run = run
        try:
            rc = kernel.main()
        finally:
            kernel.subprocess.run = real_run
            for k, v in saved.items():
                setattr(WB, k, v)
        check(rc == 0, "the atmos kernel's stage call ran", rc)
        stages = os.listdir(os.path.join(td, "build"))
        check(len(stages) == 1, "one stage on the empty root", stages)
        stage = os.path.join(td, "build", stages[0])
        missing = [w for w in sorted(wanted) if not os.path.isfile(os.path.join(stage, w))]
        check(not missing, "a fresh stage holds every file the atmos C# selftest reads", missing)


def main_winstage_narrow():
    """A narrow stage (whole_src=False) stages the project plus extra_dirs, never the 3 GB src tree: that tree cost the
    atmospheric kernel test its 240 s (NIGHTLY_COP_FIX_RED_HMGHDI_RQAA)."""
    import selftest_winstage as WS
    got = {}
    saved = WB.stage_build, WB.staged_win

    def fake(p, stage_name=None, extra_dirs=()):
        got["extra"] = list(extra_dirs)
        return 0, {"stage": "x"}
    WB.stage_build, WB.staged_win = fake, lambda rec, p: "x"
    try:
        csproj = os.path.join(WB.ROOT, "src", "RimMandrake", "ModA", "Source", "ModA.csproj")
        WS.windows_project_path(csproj, whole_src=False, extra_dirs=["/one/mod"])
        check(got["extra"] == ["/one/mod"], "whole_src=False stages only the extra_dirs", got)
        WS.windows_project_path(csproj)
        check(got["extra"] == [os.path.join(WB.ROOT, "src")], "the default still stages the whole tree", got)
    finally:
        WB.stage_build, WB.staged_win = saved


def main_same_stage():
    """Two builds of one stage: rsync..build spans must not overlap."""
    with tempfile.TemporaryDirectory() as td:
        spans, mu = [], threading.Lock()
        saved = {k: getattr(WB, k, None) for k in ("BUILD_ROOT", "LOCK_DIR", "needed_dirs", "win", "_ce_snapshot",
                                                   "rsync_stage", "source_sha", "run_dotnet", "built_outputs",
                                                   "_copy_back")}
        WB.BUILD_ROOT, WB.LOCK_DIR = os.path.join(td, "build"), os.path.join(td, "locks")
        WB.needed_dirs = lambda csproj, seen=None: {os.path.dirname(csproj)}
        WB.win = lambda p: p
        WB._ce_snapshot = lambda scope=None: None
        WB.source_sha = lambda paths: ("0" * 40, False)
        WB.built_outputs = lambda tree, since: []
        WB._copy_back = lambda outs, stage, record, staged_in=None: None
        starts = {}

        def rsync(rels, stage, cwd, excl=()):
            starts[threading.get_ident()] = time.time()
            time.sleep(0.15)
            return types.SimpleNamespace(returncode=0, stdout="")

        def dotnet(csproj_win, cwd, config, extra):
            time.sleep(0.15)
            with mu:
                spans.append((starts[threading.get_ident()], time.time()))
            return 0
        WB.rsync_stage, WB.run_dotnet = rsync, dotnet
        p = os.path.join(WB.ROOT, "src", "RimMandrake", "ModA", "Source", "ModA.csproj")
        try:
            ts = [threading.Thread(target=WB.stage_build, args=(p,)) for _ in range(2)]
            for t in ts:
                t.start()
            for t in ts:
                t.join(30)
        finally:
            for k, v in saved.items():
                if v is not None:
                    setattr(WB, k, v)
        check(len(spans) == 2 and not overlaps(spans), "two builds of one stage never overlap rsync..build", spans)


def main_no_revert():
    """review night r2: a dll+stamp pair the build did not change (staged in as an input, byte-identical) is never
    written back: a peer build may have replaced it in the clone meanwhile. A changed pair is copied."""
    import hashlib
    h = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
    with tempfile.TemporaryDirectory() as td:
        stage, clone = os.path.join(td, "stage"), os.path.join(td, "clone")
        sa, ca = os.path.join(stage, "Assemblies"), os.path.join(clone, "Assemblies")
        os.makedirs(sa)
        os.makedirs(ca)
        files = {"B.dll": b"old B", "B.dll.srchash": b"# dll: oldB", "A.dll": b"new A", "A.dll.srchash": b"# dll: newA"}
        for n, b in files.items():
            with open(os.path.join(sa, n), "wb") as f:
                f.write(b)
        # staged in: both B files as they are now, A's previous build (since rebuilt)
        staged_in = {os.path.join(sa, "B.dll"): h(b"old B"), os.path.join(sa, "B.dll.srchash"): h(b"# dll: oldB"),
                     os.path.join(sa, "A.dll"): h(b"old A")}
        for n, b in (("B.dll", b"NEWER B"), ("B.dll.srchash", b"# dll: newerB")):
            with open(os.path.join(ca, n), "wb") as f:
                f.write(b)
        saved = WB.ROOT
        WB.ROOT = clone
        rec = {"outputs": []}
        try:
            WB._copy_back([os.path.join(sa, n) for n in files], stage, rec, staged_in)
            err = None
        except Exception as e:  # noqa: BLE001
            err = repr(e)
        finally:
            WB.ROOT = saved
        rd = lambda n: open(os.path.join(ca, n), "rb").read() if os.path.exists(os.path.join(ca, n)) else None  # noqa: E731
        check(err is None and rd("B.dll") == b"NEWER B" and rd("B.dll.srchash") == b"# dll: newerB",
              "an unchanged staged-in pair does not revert a peer's newer copy in the clone", (err, rd("B.dll")))
        check(err is None and rd("A.dll") == b"new A" and rd("A.dll.srchash") == b"# dll: newA",
              "a pair the build changed is copied back", (err, rd("A.dll")))


def main_inplace():
    """review night r4: a clone on a Windows drive builds in place (no stage), so two in-place builds share obj/, bin/
    and Assemblies/ in that tree; they must not overlap."""
    with tempfile.TemporaryDirectory() as td:
        spans, mu = [], threading.Lock()
        saved = {k: getattr(WB, k, None) for k in ("LOCK_DIR", "on_windows_drive", "find_csproj", "win", "_ce_snapshot",
                                                   "run_dotnet", "pulse_report", "evidence_report")}
        WB.LOCK_DIR = os.path.join(td, "locks")
        WB.on_windows_drive = lambda p: True
        WB.find_csproj = lambda t: os.path.join(WB.ROOT, "src", "RimMandrake", t, "Source", "%s.csproj" % t)
        WB.win = lambda p: p
        WB._ce_snapshot = lambda scope=None: None
        WB.pulse_report = lambda *a, **k: None
        WB.evidence_report = lambda *a, **k: None

        def dotnet(csproj_win, cwd, config, extra):
            t0 = time.time()
            time.sleep(0.2)
            with mu:
                spans.append((t0, time.time()))
            return 0
        WB.run_dotnet = dotnet
        try:
            ts = [threading.Thread(target=WB.main, args=([m],)) for m in ("ModA", "ModB")]
            for t in ts:
                t.start()
            for t in ts:
                t.join(30)
        finally:
            for k, v in saved.items():
                if v is not None:
                    setattr(WB, k, v)
        check(len(spans) == 2 and not overlaps(spans), "two in-place builds in one clone never overlap (r4)", spans)


if __name__ == "__main__":
    main_inplace()
    main_same_stage()
    main_no_revert()
    main_clones_independent()
    main_clones_never_queue()
    main_atmos_fresh_stage()
    main_winstage_narrow()
    main()
    sys.exit(1 if FAILS else 0)
