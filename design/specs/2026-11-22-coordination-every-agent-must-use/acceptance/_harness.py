"""Shared by the acceptance scripts of plan.md steps 3 to 5. Steps 1 and 2 moved, green, to
src/RimMandrake/rimflow/acceptance/, which has its own copy of this file. Each script names the module that its step must
add; while the module is absent, every check reads FAIL with that reason, and the script exits 1."""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
RIMFLOW = os.path.join(REPO, "src", "RimMandrake", "rimflow")
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
for p in (RIMFLOW, UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
RESULTS = []


def load(name):
    """-> (module, None) or (None, why). A module that is absent is the step not built yet."""
    try:
        return importlib.import_module(name), None
    except Exception as e:  # noqa: BLE001 - any import failure is the reason every check fails
        return None, "%s cannot be imported (%s: %s)" % (name, type(e).__name__, e)


def check(name, fn):
    """fn() -> truthy to pass. An exception is a FAIL with its text, never a crash of the script."""
    try:
        ok, why = bool(fn()), ""
    except Exception as e:  # noqa: BLE001
        ok, why = False, "%s: %s" % (type(e).__name__, e)
    RESULTS.append(ok)
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else ("  -- " + why if why else "")))


def done(expected):
    n = sum(RESULTS)
    print("%s %d/%d (expected when built: PASS %d/%d)" % ("PASS" if n == len(RESULTS) == expected else "FAIL", n,
                                                           len(RESULTS), expected, expected))
    sys.exit(0 if n == len(RESULTS) == expected else 1)
