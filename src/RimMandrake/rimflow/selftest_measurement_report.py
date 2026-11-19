#!/usr/bin/env python3
"""selftest_measurement_report.py - RIMMANDRAKE_PRINT_MEASUREMENT_REPORT_BESIDE_EVERY_GREEN_CHECK: the measurement report
is built from a fixed set of check readings, refuses one missing parity, family, exclusions, worst case or source
commit, keeps "could not look" (UNMEASURED) apart from a missing field, never gates on a margin, and reads Gimme Some
Slack's live-end sweep output (a captured copy, so this runs in a second, not the sweep's three minutes) into the very
numbers the sweep printed."""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measurement_report as MR  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


GOOD = {"check": "whip", "verdict": "PASS",
        "parity": {"agreement": 0.98, "disagreements": [{"what": "tail 0.95 at seed 7", "explained": "float order"}]},
        "family": {"generator": "straight cords, tails 0.7 and 0.95, 30 seeds x 20 s", "cases": 60},
        "exclusions": ["bent cords", "tails other than 0.7 and 0.95"],
        "worst": {"value": 0.265, "limit": 0.20, "reads": "at least"},
        "regressions": [{"name": "the old sideways whip folds a 0.7 tail under the bar", "result": "PASS"}],
        "source": {"commit": "0123456789abcdef0123456789abcdef01234567", "settings": {"LIVE_BEND_R": 0.2},
                   "instrument": "sha256:abc"}}

# the sweep's own lines, captured 2026-11-18 on 8c12040bd3 (selftest_gss_live_end_sweep.py, 8/8 PASS)
SWEEP = """PASS whip: the bend wave never bends a straight cord under 0.20 (tail 0.7: 0.265, tail 0.95: 0.470; 30 seeds x 20 s)
PASS whip can fail: the old sideways whip folds a straight 0.7 tail to 0.095, under the bar's 0.10 (0.95: 0.105)
PASS shot: a fitting under 0.85 behind the end lies still, from 0.85 the whole pigtail whips on a bare cord (still up to 0.80, whipping from 0.85, other outcomes [])
PASS poses: 13248 fitting poses 0.3-2.5 cells round the end (the lay alone, no fitting body): every one a bare cord holding the three bars ({'join': 12950, 'kept': 298}); tightest bend 0.206; unlaid []
PASS poses: the tied loop is used on none of them (0)
PASS poses, the fitting a box, plate or strip: 2004 of 13248 unlaid, every one with the fitting's middle within 0.749 cell of the end's run (limit 0.75; the grid's nearest is 0.835)
PASS poses, the fitting a machine's plug: 2272 of 13248 unlaid, 2188 with the machine's footprint ON the end's run, the rest within 0.219 cell of it (limit 0.22)
PASS can fail: a hooked cord (0.05 corners) is refused (P) and laid again (join 0.66, tightest bend 0.498)
8/8 live end sweep checks pass
"""
SRC = {"commit": "8c12040bd387", "settings": {"BOX_CROWD": 0.75, "MIN_BEND_R": 0.1}, "instrument": "sha256:test"}


def refused(fn, *a):
    try:
        fn(*a)
    except MR.Refused as e:
        return str(e)
    return None


def main():
    rep = MR.build(GOOD)
    check("build: a complete reading becomes a report", rep["check"] == "whip" and rep["worst"]["headroom"] == 0.065,
          rep)
    for field in MR.REQUIRED:
        bad = copy.deepcopy(GOOD)
        bad.pop(field)
        why = refused(MR.build, bad)
        check("build: a reading with no %s is refused, naming it" % field, why is not None and field in why, why)
    bad = copy.deepcopy(GOOD)
    bad["source"].pop("commit")
    why = refused(MR.build, bad)
    check("build: a source with no commit is refused", why is not None and "commit" in why, why)
    for sub in ("generator", "cases"):
        bad = copy.deepcopy(GOOD)
        bad["family"].pop(sub)
        check("build: a family with no %s is refused" % sub, refused(MR.build, bad) is not None)
    for sub in ("value", "limit", "reads"):
        bad = copy.deepcopy(GOOD)
        bad["worst"].pop(sub)
        check("build: a worst case with no %s is refused" % sub, refused(MR.build, bad) is not None)
    bad = copy.deepcopy(GOOD)
    bad["exclusions"] = []
    check("build: an empty exclusions list with no reason is refused (silence is not 'none')",
          refused(MR.build, bad) is not None)
    bad["exclusions_none_why"] = "the family is the whole input space"
    check("build: an empty exclusions list with its reason is kept", refused(MR.build, bad) is None)
    unm = copy.deepcopy(GOOD)
    unm["parity"] = {"state": "UNMEASURED", "why": "no instrument compares the copy with the game"}
    r = MR.build(unm)
    check("build: parity UNMEASURED with its cause is a complete answer, printed as such",
          "UNMEASURED" in MR.render([r]) and "no instrument compares" in MR.render([r]), MR.render([r]))
    bad = copy.deepcopy(GOOD)
    bad["parity"] = {"state": "UNMEASURED"}
    check("build: UNMEASURED parity with no cause is refused", refused(MR.build, bad) is not None)
    bad = copy.deepcopy(GOOD)
    bad["parity"] = {"agreement": 0.9, "disagreements": [{"what": "x"}]}
    r = MR.build(bad)
    check("build: a disagreement with no explanation is kept and named unexplained",
          "unexplained" in MR.render([r]), MR.render([r]))
    near = copy.deepcopy(GOOD)
    near["worst"] = {"value": 0.749, "limit": 0.75, "reads": "at most"}
    r = MR.build(near)
    check("report, not a gate: a worst case a hair from its limit keeps its verdict and says the headroom",
          r["verdict"] == "PASS" and abs(r["worst"]["headroom"] - 0.001) < 1e-9 and "0.001" in MR.render([r]), r)
    over = copy.deepcopy(GOOD)
    over["worst"] = {"value": 0.19, "limit": 0.20, "reads": "at least"}
    r = MR.build(over)
    check("report: a worst case past its limit says so (negative headroom), it does not rewrite the verdict",
          r["worst"]["headroom"] < 0 and r["verdict"] == "PASS" and "PAST ITS LIMIT" in MR.render([r]), r)
    # Gimme Some Slack's live-end sweep, from its own printed lines
    reps, unread = MR.gss_live_end_readings(SWEEP, SRC)
    reps = [MR.build(x) for x in reps]
    by = {x["check"]: x for x in reps}
    check("gss: every check line the sweep printed is read (none left unread)", unread == [], unread)
    check("gss: the whip's worst is the sweep's own 0.265 against its 0.20",
          by.get("whip", {}).get("worst", {}).get("value") == 0.265 and by["whip"]["worst"]["limit"] == 0.20,
          by.get("whip"))
    box = by.get("poses, box/plate/strip", {})
    check("gss: the box case reads 0.749 against 0.75 over 13248 poses, 2004 unlaid",
          box.get("worst", {}).get("value") == 0.749 and box["worst"]["limit"] == 0.75
          and box["family"]["cases"] == 13248 and "2004" in str(box.get("observed")), box)
    shot = by.get("shot", {})
    check("gss: the shot reads its boundary from its own line (whipping from 0.85, against 0.85), its case count "
          "UNMEASURED with a cause, never a made-up number",
          shot.get("worst", {}).get("value") == 0.85 and shot["worst"]["limit"] == 0.85
          and shot["family"]["cases"].get("state") == "UNMEASURED", shot)
    check("gss: the lay-alone limit is the sweep's own 1.5 x MIN_BEND_R",
          by.get("poses, lay alone", {}).get("worst", {}).get("limit") == 0.15, by.get("poses, lay alone"))
    mach = by.get("poses, machine plug", {})
    check("gss: the machine case reads 0.219 against 0.22", mach.get("worst", {}).get("value") == 0.219
          and mach["worst"]["limit"] == 0.22, mach)
    check("gss: parity is UNMEASURED with its cause on every check (no instrument compares the Python copy with "
          "CordLiveEnd.cs)", all(x["parity"].get("state") == "UNMEASURED" and x["parity"].get("why") for x in reps), reps)
    check("gss: the instrument-can-fail lines are the regressions, PASS",
          any(g["result"] == "PASS" and "sideways" in g["name"] for g in by["whip"]["regressions"]), by["whip"])
    reps2, unread2 = MR.gss_live_end_readings(SWEEP.replace("tightest bend 0.206", "tightest bend ?"), SRC)
    check("gss: a line the reader cannot parse is named unread, never dropped or zeroed", unread2 != [], unread2)
    reps3, _ = MR.gss_live_end_readings(SWEEP.replace("PASS poses, the fitting a box", "FAIL poses, the fitting a box"),
                                        SRC)
    check("gss: a FAIL line is reported FAIL", any(x["verdict"] == "FAIL" for x in reps3), reps3)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
