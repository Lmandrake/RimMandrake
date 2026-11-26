"""win_reexec.py -- run a Windows-only tool (system_screenshot.py, system_click.py) from WSL.

Under WSL's python3, ctypes.windll does not exist. The tool calls reexec_or_exit(), which re-runs the
same script through Windows python.exe, with each path argument translated by `wslpath -w`, and
returns that run's exit code. With no Windows python.exe on PATH it returns 2 (could not look) and
says so: never 0, because an exit 0 with no picture once read as success (selftest_system_tools_wsl.py).
"""
import os
import shutil
import subprocess
import sys


def _wslpath_w(p):
    # hang guard: wslpath answers in milliseconds; 60 s is far above any real run
    return subprocess.run(["wslpath", "-w", p], capture_output=True, text=True, check=True, timeout=60).stdout.strip()


def windows_argv(script, args, path_args, to_win=_wslpath_w, py="python.exe"):
    out = [py, to_win(os.path.abspath(script))]
    for i, a in enumerate(args):
        out.append(to_win(os.path.abspath(a)) if i in path_args else a)
    return out


def reexec_or_exit(script, args, path_args, py_finder=lambda: shutil.which("python.exe"),
                   runner=subprocess.call, stream=sys.stderr):
    name = os.path.basename(script)
    if any(a in ("-h", "--help") for a in args):
        print(f"{name} is Windows-only; from WSL it re-runs itself through Windows python.exe.", file=stream)
        return 0
    py = py_finder()
    if not py:
        print(f"{name}: COULD NOT LOOK: Windows-only (ctypes.windll) and no Windows python.exe on PATH; "
              f"run it with a Windows Python.", file=stream)
        return 2
    return runner(windows_argv(script, args, path_args, py=py))
