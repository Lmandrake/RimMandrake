#!/usr/bin/env python3
"""Every python file that launches `dotnet run` goes through winbuild's WSL lost-launch retry.

Under load WSL can fail to start a Windows exe at all (rc 1, "UtilAcceptVsock: accept4 failed 110" on stderr); a
selftest that launched dotnet.exe with a bare subprocess call read that as a red test. 25 files did
(SELFTEST_RETRY_FIX_25_STILL_BARE, from NIGHTLY_COP_FIX_RED_MPLZPJ_VKOU). This test:
  1. scans every tracked .py for a `dotnet ..., "run"` launch handed to subprocess directly (class guard), after
     proving on planted samples that the scanner sees both shapes (inline list, list held in a variable);
  2. checks winbuild.run_interop_captured on a stand-in exe: a lost launch goes again, the caller still gets
     stdout/stderr on the result, a real failure is not retried.
Offline, no dotnet needed.
"""
from __future__ import annotations

import os
import re
import stat
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild as WB  # noqa: E402

FAILS = []

DOTNET_RUN = re.compile(r'(?:dotnet|DOTNET)\w*,\s*["\']run["\']')
SUBPROC = re.compile(r'subprocess\.(?:run|Popen|call|check_call|check_output)\(\s*(\w+)?')
ASSIGN = re.compile(r'\s*(\w+)\s*=\s*\[')


def check(ok, what, detail=""):
    print(("PASS " if ok else "FAIL ") + what + ("" if ok else "  -- %s" % (detail,)))
    if not ok:
        FAILS.append(what)


def bare_launches(text):
    """Line numbers (1-based) where a `dotnet run` command reaches subprocess directly."""
    lines = text.split("\n")
    out = []
    for i, line in enumerate(lines):
        if not DOTNET_RUN.search(line):
            continue
        m = SUBPROC.search(line)
        if m and m.start() < DOTNET_RUN.search(line).start():
            out.append(i + 1)
            continue
        # A call may open on the line before (subprocess.run(\n [dotnet, "run", ...]).
        if i and re.search(r'subprocess\.\w+\(\s*$', lines[i - 1]):
            out.append(i + 1)
            continue
        a = ASSIGN.match(line)
        if not a:
            continue
        var = a.group(1)
        for j in range(i + 1, min(i + 25, len(lines))):
            if re.match(r'\s*%s\s*=' % re.escape(var), lines[j]) and not re.match(r'\s*%s\s*\+=' % re.escape(var), lines[j]):
                break
            s = SUBPROC.search(lines[j])
            if s and s.group(1) == var:
                out.append(j + 1)
                break
    return out


def scanner_sees():
    planted = {
        'r = subprocess.run([dotnet, "run", "--project", p], capture_output=True)\n': [1],
        'cmd = [dotnet, "run", "--project", p]\nif x:\n    cmd += ["--"]\nr = subprocess.run(cmd, text=True)\n': [4],
        'r = subprocess.run(\n    [DOTNET_EXE, "run"], cwd=d)\n': [2],
        'cmd = [dotnet, "run"]\nr = run_interop_captured(cmd, capture_output=True)\n': [],
        'r = winbuild.run_interop_captured([dotnet, "run", "-c", "Release"], capture_output=True)\n': [],
        'cmd = [dotnet, "build", p]\nr = subprocess.run(cmd)\n': [],
    }
    for src, want in planted.items():
        got = bare_launches(src)
        check(got == want, "scanner on planted sample %r" % src.split("\n")[0][:50], (got, want))


def tree_clean():
    ls = subprocess.run(["git", "-C", REPO, "ls-files", "*.py"], capture_output=True, text=True, timeout=60)
    files = [f for f in ls.stdout.split("\n") if f]
    check(ls.returncode == 0 and len(files) > 500, "git ls-files sees the tree (%d .py files)" % len(files), ls.stderr)
    launching, bare = 0, []
    for f in files:
        path = os.path.join(REPO, f)
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        if not DOTNET_RUN.search(text) or f.endswith("selftest_dotnet_run_interop_guard.py"):
            continue
        launching += 1
        bare += ["%s:%d" % (f, n) for n in bare_launches(text)]
    check(launching >= 20, "the scan finds the files that launch dotnet run (%d)" % launching, launching)
    check(not bare, "no python file hands a `dotnet run` to subprocess directly (use winbuild.run_interop_captured)",
          bare)


def fake_exe(td, name, body):
    path = os.path.join(td, name)
    with open(path, "w") as f:
        f.write("#!/bin/sh\n" + body)
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
    return path


def captured(td):
    tries = os.path.join(td, "tries")
    count = 'echo x >> "%s"; n=$(wc -l < "%s"); ' % (tries, tries)
    lost = "echo '<3>WSL (1 - ) ERROR: UtilAcceptVsock:273: accept4 failed 110' >&2; "

    def run(body, **kw):
        if os.path.exists(tries):
            os.remove(tries)
        r = WB.run_interop_captured([fake_exe(td, "exe", count + body)], timeout=30, **kw)
        with open(tries) as f:
            return r, len(f.readlines())
    waits = []
    real_time, WB.time = WB.time, types.SimpleNamespace(sleep=waits.append, time=WB.time.time)
    try:
        r, n = run('if [ "$n" -lt 3 ]; then %sexit 1; fi; echo PASS all; echo note >&2; exit 0\n' % lost,
                   capture_output=True, text=True)
        check((r.returncode, n, r.stdout, r.stderr) == (0, 3, "PASS all\n", "note\n"),
              "two lost launches go again; the caller reads the real run's stdout and stderr", (r, n))
        check(waits == [WB.INTEROP_WAIT_S, 2 * WB.INTEROP_WAIT_S], "the waits grow per try", waits)
        r, n = run("echo 'FAIL kernel'; exit 1\n", capture_output=True, text=True)
        check((r.returncode, n, r.stdout) == (1, 1, "FAIL kernel\n"), "a real red run is not retried", (r, n))
        r, n = run(lost + "exit 1\n", capture_output=True, text=True)
        check((r.returncode, n) == (1, WB.INTEROP_TRIES), "a launch never succeeding stops at the bound", (r, n))
        r, n = run('if [ "$n" -lt 2 ]; then %sexit 1; fi; echo ok; exit 0\n' % lost, capture_output=True)
        check((r.returncode, n, r.stdout) == (0, 2, b"ok\n"), "bytes mode works", (r, n))
        r, n = run('if [ "$n" -lt 2 ]; then %sexit 1; fi; exit 0\n' % lost)
        check((r.returncode, n) == (0, 2), "a call that captured nothing still sees the launch failure", (r, n))
    finally:
        WB.time = real_time


def main():
    scanner_sees()
    tree_clean()
    with tempfile.TemporaryDirectory() as td:
        captured(td)
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
