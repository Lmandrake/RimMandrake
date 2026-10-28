#!/usr/bin/env python3
"""Selftest for winbuild.stage_build's locks (review night): two builds of ONE stage never overlap from the rsync to the
end of the build (one would rsync --delete under the other's compile), and two builds of DIFFERENT stages never copy
back at the same time (a shared dependency's dll and .srchash would land as a mismatched pair). No dotnet, no rsync:
the steps are stubbed and timed."""
import os
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

        def rsync(rels, stage, cwd, excl=()):
            starts[threading.get_ident()] = time.time()
            time.sleep(0.15)
            return types.SimpleNamespace(returncode=0, stdout="")

        def dotnet(csproj_win, cwd, config, extra):
            time.sleep(0.15)
            with mu:
                build_spans.append((os.path.basename(os.path.dirname(cwd)), starts[threading.get_ident()], time.time()))
            return 0

        def copy_back(outs, stage, record, staged_in=None):
            t0 = time.time()
            time.sleep(0.15)
            with mu:
                copy_spans.append((t0, time.time()))
        WB.rsync_stage, WB.run_dotnet, WB._copy_back = rsync, dotnet, copy_back
        proj = lambda m: os.path.join(WB.ROOT, "src", "RimMandrake", m, "Source", "%s.csproj" % m)  # noqa: E731

        def go(m):
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
    print("\n%s" % ("FAILED %d" % len(FAILS) if FAILS else "all passed"))
    return FAILS


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


if __name__ == "__main__":
    main_same_stage()
    main_no_revert()
    main()
    sys.exit(1 if FAILS else 0)
