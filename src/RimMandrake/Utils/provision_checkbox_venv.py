#!/usr/bin/env python3
"""Make (or confirm) the checkbox venv: the system python3 plus opencv-python-headless, so `python3 -c 'import cv2,
numpy'` runs in a walled checker box (RELENTLESS_FIX_CHECKBOX_TEST_SERIAL_LANE; relentless_box.json path_prepend).

Idempotent: a venv that already imports cv2 with the SYSTEM numpy is left alone (exit 0, "ALREADY"). A missing or
broken one is (re)made with --system-site-packages over /usr/bin/python3 and opencv-python-headless installed under a
constraint pinning numpy to the system's version (a wheel that pulled a second numpy would shadow the one every other
tool here uses). uv when it is on PATH, else `python3 -m venv` + pip (SteveDesktop has no uv).

  provision_checkbox_venv.py              make or confirm the venv at relentless_box.json path_prepend[0] (minus /bin)
  provision_checkbox_venv.py --venv DIR   another folder
  provision_checkbox_venv.py --check      read only: exit 0 provisioned, 1 not
Last line: ALREADY|PROVISIONED|MISSING venv=<dir> cv2=<v> numpy=<v>, or FAILED <reason> (exit 1).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BOX_JSON = os.path.join(HERE, "..", "rimflow", "relentless_box.json")
SYSTEM_PY = "/usr/bin/python3"
PROBE = "import cv2, numpy, sys; print(cv2.__version__, numpy.__version__, numpy.__file__)"


def default_venv(box_json=BOX_JSON):
    """-> the venv folder relentless_box.json path_prepend[0] names (its bin/ stripped), ~ expanded."""
    with open(box_json, encoding="utf-8") as f:
        pre = json.load(f).get("path_prepend") or []
    if not pre:
        raise SystemExit("FAILED relentless_box.json has no path_prepend")
    d = os.path.expanduser(str(pre[0])).rstrip("/")
    return d[:-4] if d.endswith("/bin") else d


def _run(argv, timeout=480):
    p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    return p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()


def system_numpy(run=_run, py=SYSTEM_PY):
    code, out = run([py, "-c", "import numpy; print(numpy.__version__)"])
    if code or not out:
        raise SystemExit("FAILED the system python3 (%s) has no numpy: %s" % (py, out[-200:]))
    return out.splitlines()[-1].strip()


def probe(venv, run=_run):
    """-> (cv2, numpy, numpy_file) from the venv's python, or None when it is missing or cannot import them."""
    py = os.path.join(venv, "bin", "python3")
    if not os.path.exists(py):
        return None
    code, out = run([py, "-c", PROBE], timeout=120)
    parts = out.splitlines()[-1].split() if out else []
    return tuple(parts) if code == 0 and len(parts) == 3 else None


def healthy(got, want_numpy):
    """A probe passes only with the system's numpy (a venv-local second numpy is a broken venv)."""
    return bool(got) and got[1] == want_numpy


def make(venv, want_numpy, run=_run, which=shutil.which, py=SYSTEM_PY):
    """(Re)make the venv and install opencv-python-headless with numpy pinned. -> list of the commands run."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", prefix="checkbox_c_", delete=False) as f:
        f.write("numpy==%s\n" % want_numpy)
        cons = f.name
    vpy = os.path.join(venv, "bin", "python3")
    if which("uv"):
        steps = [["uv", "venv", "--clear", "--system-site-packages", "-p", py, venv],
                 ["uv", "pip", "install", "--python", vpy, "-c", cons, "opencv-python-headless"]]
    else:
        steps = [[py, "-m", "venv", "--clear", "--system-site-packages", venv],
                 [vpy, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "-c", cons,
                  "opencv-python-headless"]]
    try:
        os.makedirs(os.path.dirname(venv) or ".", exist_ok=True)
        for argv in steps:
            code, out = run(argv)
            if code:
                raise SystemExit("FAILED %s exit=%d: %s" % (" ".join(argv[:3]), code, out[-400:]))
    finally:
        os.unlink(cons)
    return steps


def main(argv=None, run=_run, which=shutil.which):
    try:
        return _main(argv, run, which)
    except SystemExit as e:     # a FAILED reason raised as a string: print it, exit 1
        if isinstance(e.code, str):
            print(e.code)
            return 1
        raise


def _main(argv, run, which):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--venv", help="venv folder (default: relentless_box.json path_prepend[0] without /bin)")
    ap.add_argument("--check", action="store_true", help="read only: exit 0 provisioned, 1 not")
    a = ap.parse_args(argv)
    venv = os.path.abspath(os.path.expanduser(a.venv)) if a.venv else default_venv()
    want = system_numpy(run)
    got = probe(venv, run)
    if healthy(got, want):
        print("ALREADY venv=%s cv2=%s numpy=%s" % (venv, got[0], got[1]))
        return 0
    if a.check:
        print("MISSING venv=%s cv2=%s numpy=%s (system numpy %s)" % (venv, got and got[0], got and got[1], want))
        return 1
    make(venv, want, run, which)
    got = probe(venv, run)
    if not healthy(got, want):
        print("FAILED venv=%s made but the probe reads %r (system numpy %s)" % (venv, got, want))
        return 1
    print("PROVISIONED venv=%s cv2=%s numpy=%s" % (venv, got[0], got[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
