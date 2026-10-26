#!/usr/bin/env python3
"""selftest_mock_dll_identity.py -- a clean --mock run never reads its own DLL as stale.

Sweep J20261026T004751Z-6e5292 (SteveDesktop, 2026-10-26) read O-LIVE-NEG FAIL: four MockBridge fault runs (one was
ladder_raise_ignored) aborted "stale DLL" with the mock reporting sha 04377e2b137a / f17767d260f4 against a repo
2099946a42ad, neither of them a committed build. The mock's jawa/type_probe and the L2 preflight each hashed the repo
DLL on their own (and the mock ignored FW_REPO_DLL), so one read that disagreed with the other turned a clean mock run
into an ABORT. This feeds both sides a file read that returns a different hash on every read and checks that they
agree, that FW_REPO_DLL is honoured by the mock, and that the deliberate dll_stale fault still reads stale.
No game, no bridge.
"""
import itertools
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(os.path.dirname(os.path.dirname(HERE)), "Utils"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import validation_v2 as V  # noqa: E402

FAILS = []


def check(what, ok):
    print("%s  %s" % ("ok  " if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def _preflight_want():
    """What phase_L compares the loaded assembly against (the pre-fix line, if the shared helper is absent)."""
    f = getattr(V, "_repo_dll_sha", None)
    if f is not None:
        return f()
    return V._sha256(os.environ.get("FW_REPO_DLL") or os.path.join(V.MOD, "Assemblies", "RimMandrakeFlowWorks.dll"))


def main():
    real = V._sha256
    counter = itertools.count()
    reads = []

    def flaky(p):                       # every read of the file answers differently (a racing / torn read)
        reads.append(p)
        return "%064x" % next(counter)

    tmp = tempfile.NamedTemporaryFile(prefix="fw_dll_", suffix=".dll", delete=False)
    tmp.write(b"MZ not really a dll")
    tmp.close()
    old_env = os.environ.get("FW_REPO_DLL")
    try:
        V._sha256 = flaky
        getattr(V, "_REPO_DLL_SHA", {}).clear()
        m = V.MockBridge()
        got = m.t_jawa_type_probe("RimMandrake.FlowWorks.RM_MapComponent_Excavation")["assemblyFileSha256"]
        want = _preflight_want()
        check("a clean mock's type_probe sha equals the preflight's repo sha under flaky reads (%s vs %s)"
              % (got[-6:], want[-6:]), got == want)

        os.environ["FW_REPO_DLL"] = tmp.name
        getattr(V, "_REPO_DLL_SHA", {}).clear()
        reads[:] = []
        m.t_jawa_type_probe("x")
        check("the mock hashes FW_REPO_DLL when it is set (read %s)" % [os.path.basename(r) for r in reads[:2]],
              bool(reads) and all(r == tmp.name for r in reads))

        V._sha256 = real
        getattr(V, "_REPO_DLL_SHA", {}).clear()
        stale = V.MockBridge(faults=("dll_stale",)).t_jawa_type_probe("x")["assemblyFileSha256"]
        check("the dll_stale fault still reads stale", stale != _preflight_want())
    finally:
        V._sha256 = real
        getattr(V, "_REPO_DLL_SHA", {}).clear()
        if old_env is None:
            os.environ.pop("FW_REPO_DLL", None)
        else:
            os.environ["FW_REPO_DLL"] = old_env
        os.unlink(tmp.name)
    print("\n%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
