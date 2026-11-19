#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_SHARE_PROBE_RESULT_TYPE_NINE_FILES_ROLL_OWN.

src/RimMandrake/rimflow/probe_result.py gives every read of the outside world one result type with four answers:
value(x), empty(), could_not_look(cause), failed(cause). The last two cannot be used as a truth value, a list or a
number: doing so raises at once. src/RimMandrake/Utils/could_not_look_lint.py is red on `<call> or []` and on an
`except` that returns an empty value in a pipeline file, unless the line is on its counted allowlist.
Exit 0 here = every check passes (expected: 6)."""
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
LINT = os.path.join(REPO, "src", "RimMandrake", "Utils", "could_not_look_lint.py")
FAILS = []


def check(name, ok, got=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, "" if ok else got))
    FAILS.append(name) if not ok else None


def raises(fn):
    try:
        fn()
    except Exception:       # noqa: BLE001
        return True
    return False


try:
    import probe_result as P
except ImportError as e:
    P = None
    check("probe_result imports", False, e)
if P:
    blind = P.could_not_look("systemctl show failed (rc 1)")
    check("could-not-look as a truth value raises", raises(lambda: bool(blind)))
    check("could-not-look as a list raises (`x or []`, list(x), len(x))",
          raises(lambda: blind or []) and raises(lambda: list(blind)) and raises(lambda: len(blind)))
    check("failed raises the same way and keeps its cause", raises(lambda: bool(P.failed("boom"))) and "boom" in str(P.failed("boom")))
    check("a value and an empty answer are used normally", list(P.value([1, 2])) == [1, 2] and list(P.empty()) == []
          and not P.empty() and bool(P.value([1])))


def lint(text):
    if not os.path.isfile(LINT):
        return 127, "no %s" % LINT
    d = tempfile.mkdtemp(prefix="cnl_lint_")
    p = os.path.join(d, "fixture.py")
    with open(p, "w") as f:
        f.write(text)
    r = subprocess.run([sys.executable, LINT, "--files", p], capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout + r.stderr


rc, out = lint("def f(cg):\n    return (_procs(cg) or [])\n")
check("the lint is red on `<call> or []`", rc == 1 and "fixture.py:2" in out, (rc, out[-200:]))
rc, out = lint("def f(cg):\n    r = _procs(cg)\n    if r is None:\n        raise RuntimeError('could not look')\n    return r\n")
check("the lint is green on a read that says could-not-look", rc == 0, (rc, out[-200:]))
print("FAILED %d" % len(FAILS) if FAILS else "PASS probe_result_type_accept (6 checks)")
sys.exit(1 if FAILS else 0)
