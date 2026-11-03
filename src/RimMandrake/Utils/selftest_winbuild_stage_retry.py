#!/usr/bin/env python3
"""winbuild staging survives a transient rsync exit (NIGHTLY_COP_FIX_RED_CZZSPJ_OFFZ): a 9p readdir ENOMEM on a drvfs stage
made rsync exit 23 and turned two selftests red on the nightly of 2026-11-03, though each passes alone. ENOMEM and a
vanished source file go again; any other exit, and a fault that never clears, still fails. No dotnet: rsync and the build
steps are stubbed, except that the capture of rsync's stderr runs a real subprocess."""
import os
import stat
import subprocess
import sys
import tempfile
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winbuild as WB  # noqa: E402

FAILS = []
ENOMEM = ('rsync: [generator] readdir("/mnt/d/stage/x"): Cannot allocate memory (12)\n'
          "rsync error: some files/attrs were not transferred (see previous errors) (code 23) at main.c(1356)\n")
DENIED = 'rsync: [generator] opendir("/mnt/d/stage/x"): Permission denied (13)\n' + ENOMEM.split("\n")[1] + "\n"


def check(ok, msg, detail=""):
    print(("ok    " if ok else "FAIL  ") + msg + ("" if ok else "  %s" % (detail,)))
    if not ok:
        FAILS.append(msg)


def stage_with(results, td):
    """Run stage_build with rsync answering `results` in turn (the last repeats). -> (rc, record, rsync calls, dotnet calls)."""
    calls, built = [], []

    def rsync(rels, stage, cwd, excl=()):
        rc, err = results[min(len(calls), len(results) - 1)]
        calls.append(rc)
        return types.SimpleNamespace(returncode=rc, stdout="", stderr=err)

    def dotnet(csproj_win, cwd, config, extra):
        built.append(cwd)
        return 0
    stubs = {"BUILD_ROOT": os.path.join(td, "build"), "LOCK_DIR": os.path.join(td, "locks"), "RSYNC_ENOMEM_WAIT_S": 0,
             "needed_dirs": lambda csproj, seen=None: {os.path.dirname(csproj)}, "win": lambda p: p,
             "_ce_snapshot": lambda scope=None: None, "source_sha": lambda paths: ("0" * 40, False),
             "built_outputs": lambda tree, since: [], "_copy_back": lambda outs, stage, record, staged_in=None: None,
             "rsync_stage": rsync, "run_dotnet": dotnet}
    saved = {k: getattr(WB, k) for k in stubs}
    real_sleep, WB.time.sleep = WB.time.sleep, lambda s: None
    for k, v in stubs.items():
        setattr(WB, k, v)
    try:
        rc, record = WB.stage_build(os.path.join(WB.ROOT, "src", "RimMandrake", "M", "Source", "M.csproj"))
    finally:
        WB.time.sleep = real_sleep
        for k, v in saved.items():
            setattr(WB, k, v)
    return rc, record, calls, built


def real_stderr_capture(td):
    """rsync_stage itself must keep stderr: a stub cannot show that, and without it ENOMEM is never recognised."""
    bindir = os.path.join(td, "bin")
    os.makedirs(bindir)
    fake = os.path.join(bindir, "rsync")
    with open(fake, "w") as f:
        f.write('#!/bin/sh\nprintf \'%s\' "$RM_FAKE_RSYNC_ERR" >&2\nexit 23\n')
    os.chmod(fake, os.stat(fake).st_mode | stat.S_IXUSR)
    code = ("import os, sys; sys.path.insert(0, %r); import winbuild as WB\n"
            "r = WB.rsync_stage(['m/'], %r, %r); print(r.returncode, repr(WB.rsync_retry_wait(r, 0)))"
            % (os.path.dirname(os.path.abspath(__file__)), os.path.join(td, "stage"), td))
    env = dict(os.environ, PATH=bindir + os.pathsep + os.environ["PATH"], RM_FAKE_RSYNC_ERR=ENOMEM)
    p = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=60)
    check(p.returncode == 0 and p.stdout.strip() == "23 %d" % WB.RSYNC_ENOMEM_WAIT_S,
          "a real rsync_stage keeps stderr, so its ENOMEM is recognised", p.stdout + p.stderr)
    check("Cannot allocate memory" in p.stderr, "rsync's complaint still reaches the caller's stderr", p.stderr)


def fake_exe(td, name, body):
    """A stand-in for a Windows exe: a real process, so run_interop's real stderr capture runs."""
    path = os.path.join(td, name)
    with open(path, "w") as f:
        f.write("#!/bin/sh\n" + body)
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
    return path


def interop(td):
    """run_interop (NIGHTLY_COP_FIX_RED_BXSKPY_FGXD): WSL's launch timeout goes again; anything else is the exe's answer."""
    tries = os.path.join(td, "tries")
    count = 'echo x >> "%s"; n=$(wc -l < "%s"); ' % (tries, tries)

    def run(body):
        if os.path.exists(tries):
            os.remove(tries)
        rc = WB.run_interop([fake_exe(td, "exe", count + body)], timeout=30)
        with open(tries) as f:
            return rc, len(f.readlines())
    waits = []
    # winbuild's own sleeps only: time.sleep itself is shared with subprocess, whose wait loop polls through it under load
    real_time, WB.time = WB.time, types.SimpleNamespace(sleep=waits.append, time=WB.time.time)
    try:
        lost = "echo '<3>WSL (1 - ) ERROR: UtilAcceptVsock:273: accept4 failed 110' >&2; "
        # This exe closes stderr and lingers, so subprocess's wait poll always runs, loaded machine or not: a stub on the
        # shared time.sleep goes red here every time instead of only under load.
        linger = "exec 2>&-; sleep 0.3; "
        got = run('if [ "$n" -lt 2 ]; then %sexit 1; fi; %sexit 0\n' % (lost, linger))
        check(got == (0, 2) and waits == [WB.INTEROP_WAIT_S], "one lost launch goes again and the exe's 0 is the answer", (got, waits))
        got = run('if [ "$n" -lt 4 ]; then %sexit 1; fi; exit 0\n' % lost)
        check(got == (0, 4), "a launch succeeding on the last try still passes (3 lost in a row was measured)", got)
        got = run(lost + "exit 1\n")
        check(got == (1, WB.INTEROP_TRIES), "a launch never succeeding fails after the bound, not forever", got)
        got = run('if [ "$n" -lt 2 ]; then %sexit 1; fi; exit 7\n' % lost)
        check(got == (7, 2), "the exe's own failure after a lost launch keeps its own exit code", got)
        got = run("echo 'error CS1002: ; expected' >&2; exit 1\n")
        check(got == (1, 1), "a compile failure is not retried", got)
        got = run("echo 'error CS1002: ; expected'; exit 1\n")
        check(got == (1, 1), "a compile failure on stdout is not retried", got)
        got = run(lost + "exit 0\n")
        check(got == (0, 1), "a zero exit is never run again, whatever stderr said", got)
    finally:
        WB.time = real_time
    code = ("import sys; sys.path.insert(0, %r); import winbuild as WB\nsys.exit(WB.run_interop([%r], timeout=30))"
            % (os.path.dirname(os.path.abspath(__file__)), fake_exe(td, "talker", "echo to-stdout; echo to-stderr >&2; exit 3\n")))
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
    check(p.returncode == 3 and p.stdout.strip() == "to-stdout" and p.stderr.strip() == "to-stderr",
          "the exe's stdout and stderr both still reach the caller", (p.returncode, p.stdout, p.stderr))
    built = []

    def interop_stub(cmd, cwd=None, timeout=900):
        built.append((cmd, cwd, timeout))
        return 5
    saved, WB.run_interop = WB.run_interop, interop_stub
    saved_exe, WB.dotnet_exe = WB.dotnet_exe, lambda: "dotnet.exe"
    try:
        rc = WB.run_dotnet("x.csproj", td, "Release", [])
    finally:
        WB.run_interop, WB.dotnet_exe = saved, saved_exe
    check(rc == 5 and len(built) == 1 and built[0][0][:3] == ["dotnet.exe", "build", "x.csproj"],
          "run_dotnet builds through run_interop", (rc, built))


def wastes_fuzz_launch(td):
    """The fuzz's own DLL launch goes through run_interop too: a lost launch at that step reads as a red test otherwise."""
    import selftest_wastes_fuzz as WF
    launched = []

    def interop_stub(cmd, cwd=None, timeout=900):
        launched.append(cmd)
        return 6
    stubs = {"stage_build": lambda csproj, **kw: (0, {}), "staged_win": lambda rec, path: "S",
             "dotnet_exe": lambda: fake_exe(td, "dotnet", "exit 0\n"), "run_interop": interop_stub}
    saved = {k: getattr(WB, k) for k in stubs}
    for k, v in stubs.items():
        setattr(WB, k, v)
    try:
        rc = WF.main(["--fuzz-seed", "9"])
    finally:
        for k, v in saved.items():
            setattr(WB, k, v)
    check(rc == 6 and len(launched) == 1 and launched[0][-2:] == ["--fuzz-seed", "9"],
          "the Wastes fuzz runs its DLL through run_interop and answers with its code", (rc, launched))


def main():
    with tempfile.TemporaryDirectory() as td:
        interop(td)
        wastes_fuzz_launch(td)
        rc, rec, calls, built = stage_with([(23, ENOMEM), (0, "")], td)
        check(rc == 0 and calls == [23, 0] and len(built) == 1 and rec.get("staged") is True,
              "one ENOMEM: staged again and the build ran", (rc, calls, built))
        rc, rec, calls, built = stage_with([(23, ENOMEM)] * 3 + [(0, "")], td)
        check(rc == 0 and calls == [23, 23, 23, 0] and len(built) == 1, "ENOMEM clearing on the last try still builds", (rc, calls))
        rc, rec, calls, built = stage_with([(23, ENOMEM)], td)
        check(rc == 23 and len(calls) == 4 and not built and rec.get("staged") is False,
              "ENOMEM that never clears gives up after 4 tries, unbuilt", (rc, calls, built))
        rc, rec, calls, built = stage_with([(23, DENIED)], td)
        check(rc == 23 and calls == [23] and not built, "another exit 23 (permission) is not retried", (rc, calls))
        rc, rec, calls, built = stage_with([(23, None)], td)
        check(rc == 23 and calls == [23] and not built, "exit 23 with no stderr at all is not retried", (rc, calls))
        rc, rec, calls, built = stage_with([(24, "vanished\n"), (0, "")], td)
        check(rc == 0 and calls == [24, 0] and len(built) == 1, "exit 24 (vanished source) still goes again", (rc, calls))
        rc, rec, calls, built = stage_with([(12, ENOMEM)], td)
        check(rc == 12 and calls == [12] and not built, "another exit code is final even with the same words", (rc, calls))
        check([WB.rsync_retry_wait(types.SimpleNamespace(returncode=23, stderr=ENOMEM), a) for a in range(3)]
              == [WB.RSYNC_ENOMEM_WAIT_S * n for n in (1, 2, 3)], "the ENOMEM wait grows with the attempt")
        real_stderr_capture(td)
    print("\n%s" % ("FAILED %d" % len(FAILS) if FAILS else "all passed"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
