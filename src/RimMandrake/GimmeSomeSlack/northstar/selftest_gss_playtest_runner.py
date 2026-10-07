#!/usr/bin/env python3
"""selftest_gss_playtest_runner.py - the GSS launcher's pure logic: recipe expansion agrees with the C# catalogue,
and the shared verdict rule reads a GSS journal (PENDING save_reload, red-error FAIL) the way it reads FlowWorks'."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gss_playtest_runner as G  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CS = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools", "JawaBenchGssPlaytest.cs")


def main():
    n = 0
    assert G.expand("quick") == ["cords", "hose_bend", "ui"]
    assert G.expand("full")[-1] == "save_reload" and "save_reload_b" not in G.expand("full")
    assert G.expand("cords, soak") == ["cords", "soak"]
    try:
        G.expand("cord")
        raise AssertionError("typo accepted")
    except ValueError:
        pass
    n += 4
    # the C# catalogue and recipes match this file's (a drift would make the launcher refuse a valid scene or accept a bad one)
    src = open(CS, encoding="utf-8").read()
    known = re.search(r"GssKnown = \{([^}]*)\}", src).group(1)
    full = re.search(r"GssFull = \{([^}]*)\}", src).group(1)
    assert tuple(re.findall(r'"([a-z_]+)"', known)) == G.SCENES, known
    assert tuple(re.findall(r'"([a-z_]+)"', full)) == G.RECIPES["full"], full
    n += 2
    for tool in G.TOOLS.values():
        assert '"%s"' % tool in src, tool
    n += 1
    P = G.P
    end = {"type": "run_end", "completed": True, "scenariosPlanned": 2}
    pend = {"type": "scenario", "name": "save_reload", "status": "PENDING", "evidence": {"resumeRecipe": "save_reload_b"}, "runId": "r1"}
    ok = {"type": "scenario", "name": "cords", "status": "PASS", "expectedFailUntil": None}
    red = {"type": "scenario", "name": "ui", "status": "FAIL", "expectedFailUntil": None}
    assert P.verdict([{"type": "run_start"}, ok, pend, end]) == "INCOMPLETE"
    assert P.pending_resume([ok, pend])["runId"] == "r1"
    assert P.verdict([{"type": "run_start"}, ok, red, end]) == "FAIL"
    b = [{"type": "run_start"}, {"type": "scenario", "name": "save_reload_b", "status": "PASS", "expectedFailUntil": None},
         {"type": "run_end", "completed": True, "scenariosPlanned": 1}]
    assert P.combine([{"type": "run_start"}, ok, pend, end], b) == "PASS"
    n += 4
    print("%d/%d passed" % (n, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
