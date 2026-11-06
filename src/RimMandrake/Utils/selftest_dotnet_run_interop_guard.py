#!/usr/bin/env python3
"""Every python file that launches `dotnet run` goes through winbuild's WSL lost-launch retry.

Under load WSL can fail to start a Windows exe at all (rc 1, "UtilAcceptVsock: accept4 failed 110" on stderr); a
selftest that launched dotnet.exe with a bare subprocess call read that as a red test. 25 files did
(SELFTEST_RETRY_FIX_25_STILL_BARE, from NIGHTLY_COP_FIX_RED_MPLZPJ_VKOU). This test:
  1. scans every tracked .py for a `dotnet ..., "run"` launch handed to subprocess directly (class guard), after
     proving on planted samples that the scanner sees both shapes (inline list, list held in a variable);
  2. scans every tracked selftest_*.py, by AST, for a built exe (`[winbuild.dotnet_exe(), dll]`, `[exe, ...]`, a
     command list held in a variable, `list(cmd)`, `cmd + [...]`) handed to subprocess directly: 79+ such lines were
     still bare after (1) (INTEROP_RETRY_FIX_EIGHTY_SCRIPTS_LEFT), and two went red on the 2026-11-03 nightly;
  3. checks winbuild.run_interop_captured on a stand-in exe: a lost launch goes again, the caller still gets
     stdout/stderr on the result, a real failure is not retried.
Offline, no dotnet needed.
"""
from __future__ import annotations

import ast
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


EXE_NAME = re.compile(r'dotnet|(^|_)exe($|_)', re.I)
SUBPROC_FNS = {"run", "Popen", "call", "check_call", "check_output"}


def _exeish(n):
    """A node naming a Windows exe: winbuild.dotnet_exe(), or a name like dotnet / DOTNET_EXE / exe / cs_exe."""
    if isinstance(n, ast.Call):
        f = n.func
        return (isinstance(f, ast.Attribute) and f.attr == "dotnet_exe") or (isinstance(f, ast.Name) and f.id == "dotnet_exe")
    ident = n.id if isinstance(n, ast.Name) else n.attr if isinstance(n, ast.Attribute) else ""
    return bool(ident) and ident != "executable" and "python" not in ident.lower() and bool(EXE_NAME.search(ident))


def _cmdish(n, names):
    if isinstance(n, ast.List):
        return bool(n.elts) and _exeish(n.elts[0])
    if isinstance(n, ast.Name):
        return n.id in names
    if isinstance(n, ast.BinOp):
        return _cmdish(n.left, names)
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "list" and n.args:
        return _cmdish(n.args[0], names)
    return False


def bare_exe_launches(text):
    """Line numbers where a command whose first element is a Windows exe reaches subprocess directly."""
    tree = ast.parse(text)
    names = set()
    for _ in range(3):          # cmd = [exe]; args = list(cmd); full = args + [...]
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and _cmdish(node.value, names):
                names.update(t.id for t in node.targets if isinstance(t, ast.Name))
    return sorted(node.lineno for node in ast.walk(tree)
                  if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                  and node.func.attr in SUBPROC_FNS and isinstance(node.func.value, ast.Name)
                  and node.func.value.id == "subprocess" and node.args and _cmdish(node.args[0], names))


def exe_scanner_sees():
    planted = {
        'r = subprocess.run([winbuild.dotnet_exe(), dll], capture_output=True)\n': [1],
        'args = [winbuild.dotnet_exe(), dll]\nargs += ["-x"]\nsys.exit(subprocess.run(args, cwd=d).returncode)\n': [3],
        'exe_args = [WB.dotnet_exe(), dll]\nargs = list(exe_args)\nr = subprocess.run(args)\n': [3],
        'r = subprocess.run(exe_args + ["--map"], cwd=d)\nexe_args = [dotnet, dll]\n': [1],
        'r = subprocess.call(\n    [DOTNET_EXE, dll], cwd=d)\n': [1],
        'p = subprocess.run([exe, "--version"], text=True)\n': [1],
        'r = winbuild.run_interop([winbuild.dotnet_exe(), dll], cwd=d, timeout=None)\n': [],
        'r = subprocess.run([sys.executable, "-c", "x"])\n': [],
        'r = subprocess.run([python_exe, "x.py"])\n': [],
        'r = subprocess.run(["git", "status"])\n': [],
    }
    for src, want in planted.items():
        got = bare_exe_launches(src)
        check(got == want, "exe scanner on planted sample %r" % src.split("\n")[0][:50], (got, want))


def selftests_exe_clean(files):
    tests = [f for f in files if os.path.basename(f).startswith("selftest_") and not f.endswith("_guard.py")]
    check(len(tests) > 300, "the exe scan sees the selftests (%d)" % len(tests), len(tests))
    launching, bare = 0, []
    for f in tests:
        try:
            with open(os.path.join(REPO, f), encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            if "winbuild" not in text and "dotnet" not in text:
                continue
            launching += 1
            bare += ["%s:%d" % (f, n) for n in bare_exe_launches(text)]
        except (OSError, SyntaxError, ValueError):
            continue
    check(launching >= 80, "the exe scan finds the selftests that build or launch a Windows exe (%d)" % launching, launching)
    check(not bare, "no selftest hands a built exe to subprocess directly (use winbuild.run_interop or "
                    "run_interop_captured)", bare)


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
    return files


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
    exe_scanner_sees()
    selftests_exe_clean(tree_clean())
    with tempfile.TemporaryDirectory() as td:
        captured(td)
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
