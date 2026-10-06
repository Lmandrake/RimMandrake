#!/usr/bin/env python3
"""selftest_playtest_runner.py - the launcher's pure logic: journal parse, verdict, timing table."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import playtest_runner as P  # noqa: E402


def _scn(name, status, wall=1.0, ticks=100):
    return {"type": "scenario", "name": name, "status": status, "reason": None,
            "timing": {"wallSec": wall, "ticks": ticks, "frames": 10, "ticksPerSecDuringWaits": 500.0,
                       "phases": {"setup": {"wallSec": 0.1}, "exec": {"wallSec": 0.8}, "observe": {"wallSec": 0.1}}}}


def _end(completed, planned):
    return {"type": "run_end", "completed": completed, "scenariosPlanned": planned,
            "timing": {"wallSec": 5.0, "ticks": 300, "frames": 40, "tickMode": "batch", "frameBudgetMs": 50,
                       "phases": {"setup": {"wallSec": 0.3}, "runner": {"wallSec": 0.2}}}}


def main():
    n = 0
    start = {"type": "run_start"}
    cases = [
        ([start], "INCOMPLETE"),                                                     # killed before any result
        ([start, _scn("fluids", "PASS")], "INCOMPLETE"),                             # killed mid-run
        ([start, _scn("fluids", "PASS"), _scn("inject", "ERROR"), _end(False, 2)], "INCOMPLETE"),
        ([start, _scn("fluids", "PASS"), _end(True, 2)], "INCOMPLETE"),              # a planned scenario missing
        ([start, _scn("fluids", "PASS"), _scn("dig", "PASS"), _end(True, 2)], "PASS"),
        ([start, _scn("fluids", "FAIL"), _scn("dig", "INVALID"), _end(True, 2)], "FAIL"),
        ([start, _scn("fluids", "PASS"), _scn("dig", "INVALID"), _end(True, 2)], "INVALID"),
    ]
    for recs, want in cases:
        got = P.verdict(recs)
        assert got == want, (want, got, [r.get("status", r["type"]) for r in recs])
        n += 1

    text = "\n".join(json.dumps(r) for r in [start, _scn("pit", "PASS")]) + '\n{"type":"scen'
    recs, torn = P.parse_journal(text)
    assert len(recs) == 2 and torn == 1, (len(recs), torn)
    assert P.verdict(recs) == "INCOMPLETE"
    n += 1

    tab = P.timing_table([start, _scn("fluids", "FAIL", 2.5, 1), _scn("pit", "PASS", 12.0, 2400), _end(True, 2)],
                         {"wall": 14.0, "calls": 9})
    for frag in ("fluids", "FAIL", "2.50", "2400", "RUN TOTAL", "setup s", "runner overhead 0.20", "9 bridge calls"):
        assert frag in tab, (frag, tab)
    assert "NO run_end" in P.timing_table([start, _scn("fluids", "PASS")])
    n += 1
    # expected fails: XFAIL alone, FAIL when any unexpected FAIL, INVALID outranks XFAIL
    xf = dict(_scn("sluice", "FAIL"), expectedFailUntil="FLOWWORKS_SLUICE_TWO_DOORS_1")
    xp = dict(_scn("sluice", "PASS"), expectedFailUntil="FLOWWORKS_SLUICE_TWO_DOORS_1")
    for recs, want in [
        ([start, _scn("pump", "PASS"), xf, _end(True, 2)], "XFAIL"),
        ([start, _scn("pump", "FAIL"), xf, _end(True, 2)], "FAIL"),
        ([start, _scn("pump", "INVALID"), xf, _end(True, 2)], "INVALID"),
        ([start, _scn("pump", "PASS"), xp, _end(True, 2)], "PASS"),
    ]:
        got = P.verdict(recs)
        assert got == want, (want, got)
    assert P.mark(xf) == "XFAIL" and P.mark(xp) == "XPASS" and P.mark(_scn("a", "PASS")) == "PASS"
    assert "XFAIL" in P.timing_table([start, xf, _end(True, 1)])
    n += 1

    # two-phase save_reload: PENDING reads INCOMPLETE alone; the resume half settles it
    pend = dict(_scn("save_reload", "PENDING"), runId="fwpt_A",
                evidence={"resumeRecipe": "save_reload_b", "saveName": "JBPT_fwpt_A", "ticksAtSave": 1000})
    first = [start, _scn("pump", "PASS"), pend, _end(True, 2)]
    assert P.verdict(first) == "INCOMPLETE"
    assert P.pending_resume(first) is pend
    assert P.pending_resume([start, _scn("pump", "PASS"), _end(True, 1)]) is None
    assert P.combine(first, None) == "INCOMPLETE"
    assert P.combine(first, [start, _scn("save_reload_b", "PASS"), _end(True, 1)]) == "PASS"
    assert P.combine(first, [start, _scn("save_reload_b", "FAIL"), _end(True, 1)]) == "FAIL"
    assert P.combine(first, [start, _scn("save_reload_b", "PASS")]) == "INCOMPLETE"          # resume half killed
    assert P.combine(first, [start, _scn("other", "PASS"), _end(True, 1)]) == "INCOMPLETE"   # wrong half
    first_x = [start, xf, pend, _end(True, 2)]
    assert P.combine(first_x, [start, _scn("save_reload_b", "PASS"), _end(True, 1)]) == "XFAIL"
    n += 1
    print("selftest_playtest_runner: %d/%d groups passed" % (n, n))


if __name__ == "__main__":
    main()
