"""The harness of the ten acceptance scripts of this folder, copied from src/RimMandrake/rimflow/acceptance/_harness.py
(first home:
design/specs/2026-11-22-coordination-every-agent-must-use/acceptance/_harness.py). A
script names the module its step adds; while the module is absent, every check reads FAIL with that reason."""
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


# ---- added for this folder ------------------------------------------------------------------------------------------
import re  # noqa: E402

SPEND = re.compile(r"\$\s?\d|\bweighted\b|\bbudget|\bcap_usd\b|\bspend|\b\d[\d,.]*\s*[kM]?\s*tokens?\b", re.I)


def no_spend(text):
    """The text tells a launched agent nothing about its spend (CLAUDE.md, No launched agent is told its spend)."""
    return not SPEND.search(str(text))


def need(mod_why):
    """(module, why) of load() -> the module, or the reason as an exception (so each check reads FAIL with it)."""
    mod, why = mod_why
    if mod is None:
        raise RuntimeError(why)
    return mod


def page(rel, *names):
    """The boundary page exists and names each promise."""
    p = os.path.join(REPO, rel)
    if not os.path.isfile(p):
        raise RuntimeError("no page %s" % rel)
    with open(p, encoding="utf-8") as f:
        t = f.read()
    lost = [n for n in names if n not in t]
    if lost:
        raise RuntimeError("%s does not name: %s" % (rel, ", ".join(lost)))
    return "## PROMISES" in t


def listed(rel):
    """A test file exists and src/RimMandrake/Utils/pipeline_tests.json runs it at ./publish."""
    if not os.path.isfile(os.path.join(REPO, rel)):
        raise RuntimeError("no file %s" % rel)
    with open(os.path.join(REPO, "src/RimMandrake/Utils/pipeline_tests.json"), encoding="utf-8") as f:
        return rel in f.read()
