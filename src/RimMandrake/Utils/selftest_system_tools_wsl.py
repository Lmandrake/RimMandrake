#!/usr/bin/env python3
"""selftest_system_tools_wsl.py -- system_screenshot.py and system_click.py work when called from WSL.

    python3 src/RimMandrake/Utils/selftest_system_tools_wsl.py

Failure that happened (RIMMANDRAKE_RENEW_STEVEN_LOGIN_ARCHMAGI_DIES_THURSDAY_AFTERNOON, 2026-11-26): a
brief said `python3 src/RimMandrake/Utils/system_screenshot.py <out.bmp>`. Under WSL's python3 the tool
printed "nothing to do" and exited 0 with no picture: a could-not-look reported as success.
Now, under WSL, each tool re-runs itself through Windows python.exe; with no Windows Python it exits 2.
Checks: the argv that the re-run builds (offline, both tools), and one real capture when python.exe exists.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS = []


def check(cond, what, detail=""):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  -- %s" % (detail,)))
    if not cond:
        FAILS.append(what)


def main():
    try:
        import win_reexec as W
    except ImportError as e:
        check(False, "win_reexec imports", e)
        W = None
    if W is not None:
        offline(W)
    live()
    return finish()


def offline(W):
    # argv shape: the script and each path argument become Windows paths; a number stays a number.
    argv = W.windows_argv("/home/x/system_screenshot.py", ["/tmp/out.bmp"], path_args=(0,),
                          to_win=lambda p: "WIN:" + p, py="python.exe")
    check(argv == ["python.exe", "WIN:/home/x/system_screenshot.py", "WIN:/tmp/out.bmp"],
          "screenshot argv translates the script and the out path", argv)
    argv = W.windows_argv("/home/x/system_click.py", ["10", "20"], path_args=(),
                          to_win=lambda p: "WIN:" + p, py="python.exe")
    check(argv == ["python.exe", "WIN:/home/x/system_click.py", "10", "20"],
          "click argv keeps the coordinates", argv)
    # relative out path becomes absolute before translation (python.exe's cwd differs)
    argv = W.windows_argv("/s.py", ["rel.bmp"], path_args=(0,), to_win=lambda p: p, py="py")
    check(argv[2] == os.path.abspath("rel.bmp"), "relative out path is made absolute", argv)
    # no Windows Python: exit 2 by name, never 0
    rc = W.reexec_or_exit("/s.py", [], path_args=(), py_finder=lambda: None, runner=None, stream=open(os.devnull, "w"))
    check(rc == 2, "no python.exe -> exit 2 (could not look), not 0", rc)


def live():
    # live: one real capture, when this machine has a Windows Python
    if sys.platform.startswith("linux") and shutil.which("python.exe"):
        d = tempfile.gettempdir()
        out = os.path.join(d, "selftest_system_tools_wsl_%d.bmp" % os.getpid())
        r = subprocess.run([sys.executable, os.path.join(HERE, "system_screenshot.py"), out],
                           capture_output=True, text=True, timeout=120)  # hang guard: a capture takes ~2 s
        ok = r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 1000
        check(ok, "python3 system_screenshot.py <out> under WSL writes a picture", (r.returncode, r.stdout, r.stderr))
        if os.path.exists(out):
            os.unlink(out)
    else:
        print("SKIP live capture: no Windows python.exe on PATH (UNMEASURED here)")


def finish():
    print("selftest_system_tools_wsl: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
