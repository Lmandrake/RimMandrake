#!/usr/bin/env python3
"""selftest_flowworks_selftest_requests.py -- every SelfTest case a chain reads is a case that chain asked for.

validation.py's `_selftest_cases(names)` runs the C# SelfTest with `--only <names>` (SELFTEST_FILTER_BUILD_SERIAL_DLL),
so a chain sees only the cases it named, plus whatever an EARLIER chain in the same process happened to run. Sweep
J20261026T004751Z-6e5292 (SteveDesktop, 2026-10-26) read three rows FAIL "case missing from the SelfTest output"
(flow_map_controls/MapControl_wiring_and_master_switch, flow_map_controls_six/MapControl_six_wiring,
hose_switch_flips/tank_feed_refused_add_puts_back): each chain read one case it never put in its `--only` list, and
it only passed on runs where an earlier full SelfTest had already answered it. This runs every chain that calls
`_selftest_cases` alone, with a fake that answers exactly the names requested (a fresh process under `--only`), and
reds on any component that reads a case it did not request. No game, no bridge, no dotnet.
"""
import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(os.path.dirname(HERE), "Utils"), os.path.join(HERE, "northstar"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import validation as V  # noqa: E402
from modcheck import TestContext  # noqa: E402 - modcheck re-exports the top-level `suite` module's classes

FAILS = []
MISSING = "case missing from the SelfTest output"


def check(what, ok):
    print("%s  %s" % ("ok  " if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


class _T(TestContext):
    def __init__(self):
        super(_T, self).__init__(session=None)


def _only_requested(names=None):
    """A fresh `--only` process: every requested case passes, nothing else is in the output."""
    if names is None:
        raise V.ExpectationFailed("UNMEASURED: this selftest asks every chain to name its cases")
    return {n: "ok" for n in names}


def _inner(fn):
    """The function a chain was registered with (Suite.chain wraps it as chain_fn(t, _fn=fn, _name=name))."""
    d = getattr(fn, "__defaults__", None) or ()
    return d[0] if d and callable(d[0]) else fn


class _R(object):
    def __init__(self, rc, out="", err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


def crash_retry():
    """The sweep's rc=5 row: a `dotnet run --no-build` that crashed in the CLI is rebuilt and asked once more, and a
    run that still fails names its exception line, not only the stack frames after it."""
    import subprocess
    calls = []
    stack = "Unhandled exception: System.IO.IOException: the file is in use\n" + "   at Frame.Of.The.Cli()\n" * 20

    def fake(cmd, **kw):
        calls.append(list(cmd))
        return _R(5, "", stack) if len(calls) == 1 else _R(0, "ok    PumpPorts_hose_at_a_side_port\n")

    real_run, memo, state = subprocess.run, dict(V._SELFTEST_CASES), dict(V._SELFTEST_STATE)
    subprocess.run = fake
    try:
        V._SELFTEST_CASES.clear()
        V._SELFTEST_STATE.update(built=True, full=False)
        try:
            got = V._selftest_cases(["PumpPorts_hose_at_a_side_port"])
        except Exception as ex:                         # noqa: BLE001 - the old code raised UNMEASURED here
            got = {"raised": str(ex)}
        check("a CLI crash under --no-build is rebuilt once and its cases read (got %s)" % sorted(got),
              got.get("PumpPorts_hose_at_a_side_port") == "ok" and len(calls) == 2)
        check("the retry drops --no-build", len(calls) == 2 and "--no-build" in calls[0] and "--no-build" not in calls[1])
        calls.clear()
        V._SELFTEST_CASES.clear()
        subprocess.run = lambda cmd, **kw: (calls.append(cmd), _R(5, "", stack))[1]
        try:
            V._selftest_cases(["PumpPorts_hose_at_a_side_port"])
            why = ""
        except Exception as ex:                         # noqa: BLE001
            why = str(ex)
        check("a run that still crashes says what crashed (%s)" % why[:90], "IOException" in why and "UNMEASURED" in why)
    finally:
        subprocess.run = real_run
        V._SELFTEST_CASES.clear()
        V._SELFTEST_CASES.update(memo)
        V._SELFTEST_STATE.clear()
        V._SELFTEST_STATE.update(state)


def main():
    real = V._selftest_cases
    V._selftest_cases = _only_requested
    ran = 0
    try:
        for name, fn in V.suite.chains:
            try:
                src = inspect.getsource(_inner(fn))
            except (OSError, TypeError):
                continue
            if "_selftest_cases(" not in src:
                continue
            ran += 1
            t = _T()
            try:
                fn(t)
            except Exception as ex:                       # noqa: BLE001 - a chain that cannot run alone is a finding
                check("%s runs alone on its requested cases (raised %s: %s)" % (name, type(ex).__name__, ex), False)
                continue
            missing = [c.name for c in t.components if MISSING in (c.detail or "")]
            check("%s reads only the SelfTest cases it requested%s"
                  % (name, "" if not missing else " (unrequested: %s)" % ", ".join(missing)), not missing)
    finally:
        V._selftest_cases = real
    check("the scan saw the SelfTest chains (%d)" % ran, ran >= 10)
    crash_retry()
    # the three rows the sweep read red, by name
    for chain in ("flow_map_controls", "flow_map_controls_six", "hose_switch_flips"):
        check("%s is among the chains scanned" % chain, any(n == chain for n, _ in V.suite.chains))
    print("\n%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
