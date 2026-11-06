#!/usr/bin/env python3
# selftest-timeout: 120
"""RELENTLESS_FIX_CHECKBOX_TEST_SERIAL_LANE: (a) selftest_relentless_checkbox.py runs in run_selftests' dotnet serial
lane; (b) provision_checkbox_venv.py makes the checkbox venv idempotently on any host (uv, or python3 -m venv + pip).
Offline: the installer runs against a fake command runner over a temp folder; no network, no real venv is touched."""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import provision_checkbox_venv as P  # noqa: E402
import run_selftests as rs  # noqa: E402

fails = 0


def check(label, ok, detail=""):
    global fails
    print("%s %s%s" % ("ok  " if ok else "FAIL", label, "" if ok else "  -- %r" % (detail,)))
    fails += 0 if ok else 1


# (a) the serial lane
name = "selftest_relentless_checkbox.py"
check("(a) %s is in DOTNET_LANE" % name, name in rs.DOTNET_LANE)
check("(a) _lane_of puts it in the dotnet lane", rs._lane_of(Path(name)) == "dotnet", rs._lane_of(Path(name)))
check("(a) the test it names exists", os.path.isfile(os.path.join(HERE, "..", "rimflow", name)))
src = open(os.path.join(HERE, "run_selftests.py"), encoding="utf-8").read()
check("(a) the pool admits no test whose lane is busy (the gate the lane relies on)",
      "if _lane_of(t) not in busy - {None}" in src)


class Fake:
    """A command runner: the system numpy is SYS; the venv's python imports cv2 when state['cv2'], with numpy state['np']."""

    def __init__(self, venv, sys_np="2.3.5", cv2=False, np=None, exists=False, fail=None):
        self.venv, self.sys_np, self.calls, self.fail = venv, sys_np, [], fail
        self.state = {"cv2": cv2, "np": np or sys_np}
        if exists:
            self._touch()

    def _touch(self):
        os.makedirs(os.path.join(self.venv, "bin"), exist_ok=True)
        open(os.path.join(self.venv, "bin", "python3"), "w").close()

    def __call__(self, argv, timeout=480):
        self.calls.append(list(argv))
        if argv[0] == P.SYSTEM_PY and argv[1] == "-c":
            return 0, self.sys_np
        if argv[1:3] == ["-c", P.PROBE]:
            if not self.state["cv2"]:
                return 1, "ModuleNotFoundError: No module named 'cv2'"
            return 0, "5.0.0 %s /usr/lib/python3/dist-packages/numpy/__init__.py" % self.state["np"]
        if self.fail and self.fail in argv:
            return 2, "boom"
        if "venv" in argv:
            self._touch()
            self.state.update(cv2=False, np=self.sys_np)
            return 0, ""
        if "install" in argv:
            cons = argv[argv.index("-c") + 1]
            self.pins = open(cons).read()
            self.state["cv2"] = True
            return 0, ""
        return 99, "unexpected %r" % argv


def run(fake, *args, uv=True):
    out = io.StringIO()
    with redirect_stdout(out):
        try:
            code = P.main(["--venv", fake.venv] + list(args), run=fake, which=lambda n: "/x/uv" if uv and n == "uv" else None)
        except SystemExit as e:
            code = e.code
    return code, out.getvalue().strip()


def makes(fake):
    return [c for c in fake.calls if "venv" in c or "install" in c]


tmp = tempfile.mkdtemp(prefix="cbprov_selftest_")
try:
    v = os.path.join(tmp, "a", "checkbox")
    f = Fake(v)
    code, out = run(f, "--check")
    check("(b) --check on a missing venv: exit 1, MISSING, nothing made", code == 1 and out.startswith("MISSING")
          and not makes(f) and not os.path.exists(v), (code, out))
    code, out = run(f)
    check("(b) a missing venv is made: exit 0, PROVISIONED", code == 0 and out.startswith("PROVISIONED"), (code, out))
    m = makes(f)
    check("(b) with uv: uv venv --clear --system-site-packages over /usr/bin/python3, then uv pip install",
          len(m) == 2 and m[0][:5] == ["uv", "venv", "--clear", "--system-site-packages", "-p"] and m[0][5] == P.SYSTEM_PY
          and m[1][:3] == ["uv", "pip", "install"] and m[1][-1] == "opencv-python-headless", m)
    check("(b) numpy is pinned to the system's version", getattr(f, "pins", "") == "numpy==2.3.5\n", getattr(f, "pins", None))
    n = len(f.calls)
    code, out = run(f)
    check("(b) a second run changes nothing: ALREADY, no venv or install command", code == 0 and out.startswith("ALREADY")
          and not [c for c in f.calls[n:] if "venv" in c or "install" in c], (code, out, f.calls[n:]))

    v2 = os.path.join(tmp, "b", "checkbox")
    f2 = Fake(v2)
    code, out = run(f2, uv=False)
    m = makes(f2)
    check("(b) without uv: python3 -m venv --clear --system-site-packages, then the venv's pip",
          code == 0 and len(m) == 2 and m[0][:5] == [P.SYSTEM_PY, "-m", "venv", "--clear", "--system-site-packages"]
          and m[1][0] == os.path.join(v2, "bin", "python3") and m[1][1:4] == ["-m", "pip", "install"], (code, m))

    f3 = Fake(os.path.join(tmp, "c"), exists=True, cv2=False)
    code, out = run(f3)
    check("(b) a broken venv (python3 there, no cv2) is rebuilt", code == 0 and out.startswith("PROVISIONED")
          and len(makes(f3)) == 2, (code, out))

    f4 = Fake(os.path.join(tmp, "d"), exists=True, cv2=True, np="2.5.2")
    code, out = run(f4)
    check("(b) a venv with a numpy other than the system's is rebuilt", code == 0 and out.startswith("PROVISIONED")
          and len(makes(f4)) == 2, (code, out))

    f5 = Fake(os.path.join(tmp, "e"), fail="opencv-python-headless")
    code, out = run(f5)
    check("(b) a failed install exits 1 with FAILED", code == 1 and "FAILED" in out, (code, out))
finally:
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)

box = json.load(open(P.BOX_JSON, encoding="utf-8"))
check("(b) relentless_box.json venv_fix runs the installer", "provision_checkbox_venv.py" in box.get("venv_fix", ""),
      box.get("venv_fix"))
check("(b) the installer's default venv is the box's path_prepend folder",
      os.path.join(P.default_venv(), "bin") == os.path.expanduser(box["path_prepend"][0]), P.default_venv())

print("RESULT %s (%d failed)" % ("PASS" if not fails else "FAIL", fails))
sys.exit(1 if fails else 0)
