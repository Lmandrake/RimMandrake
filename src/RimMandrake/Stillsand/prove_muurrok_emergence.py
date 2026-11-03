#!/usr/bin/env python3
"""Live proof of STILLSAND_MUURROK_EMERGENCE_1: runs Stillsand validation.py's `site` and `muurrok` chains on the
running game (the site chain retiles the quicktest tile to RM_Stillsand and regenerates the map: a disposable test map,
never a planet anyone receives) and reads two components:

  A1  muurrok.muurrok_emergence_fires is MEASURED (PASS or FAIL, never UNMEASURED) and its note names how the
      forced visit ended: "arrived +N ..." (the 2026-10-07 FAIL was the harness's one census at +2600) or a
      "MOD: ..." line (never arrived / turned back).
  A2  muurrok.muurrok_absent_unforced PASS (no incident forced: no RM_Muurrok, no leviathan visit in 3000 ticks) and
      muurrok.muurrok_emergence_fires PASS (forced: >=1 RM_Muurrok at some 100-tick census within 3000 ticks).

    python3 src/RimMandrake/Stillsand/prove_muurrok_emergence.py --clause A1|A2
    python3 src/RimMandrake/Stillsand/prove_muurrok_emergence.py --selftest     # offline, against the scripted fake

Exit 0 = the clause holds, 1 = it does not, 2 = UNMEASURED (no game, site not built, a tool missing).
One run serves both clauses: the verdicts are cached for 30 minutes beside validation.py's hash
(agent storage scratch/prove_muurrok_emergence.json), so A1 then A2 cost one regeneration.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
for _p in (UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

CHAINS = ("site", "muurrok")
FIRES = "muurrok.muurrok_emergence_fires"
CONTROL = "muurrok.muurrok_absent_unforced"
CACHE_S = 30 * 60


def _load_validation():
    import importlib.util
    spec = importlib.util.spec_from_file_location("stillsand_validation", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    return v


def run_chains(V, session, anchor):
    """{component key: [verdict, detail, notes]} for the CHAINS, in suite order, on `session`."""
    from suite import TestContext
    V._STATE.clear()
    out = {}
    for name, fn in V.suite.chains:
        if name not in CHAINS:
            continue
        t = TestContext(session, anchor=anchor)
        try:
            fn(t)
        except Exception as ex:              # a chain-level crash is a script bug: UNMEASURED, never a verdict
            out[name + ".<CRASH>"] = ["CRASH", "%s: %s" % (type(ex).__name__, ex), []]
            continue
        for c in t.components:
            notes = [e.get("result") for e in (c.evidence or [])
                     if isinstance(e, dict) and str(e.get("call", "")).startswith(("muurrok letters", "control:"))]
            out["%s.%s" % (name, c.name)] = [c.verdict, c.detail, notes]
    return out


def judge(res, clause):
    """(exit code, one line) for `clause` over a run_chains result."""
    if any(k.endswith(".<CRASH>") for k in res):
        return 2, "UNMEASURED: a chain crashed: %s" % {k: v[1] for k, v in res.items() if k.endswith(".<CRASH>")}
    fires, control = res.get(FIRES), res.get(CONTROL)
    if fires is None or control is None:
        return 2, "UNMEASURED: components missing from the run: %s" % sorted(res)
    if clause == "A1":
        if fires[0] not in ("PASS", "FAIL"):
            return 2, "UNMEASURED: %s is %s: %s" % (FIRES, fires[0], fires[1])
        said = "%s %s" % (fires[1] or "", json.dumps(fires[2], default=str))
        ends = (r"arrived \+\d+",) if fires[0] == "PASS" else (r"arrived \+\d+", r"never arrived", r"turned back")
        if not any(re.search(e, said) for e in ends):
            return 1, "A1 cause NOT established: %s %s names no end of the visit (%s): %s" % (
                FIRES, fires[0], " / ".join(ends), said[:600])
        return 0, "A1 cause measured: %s %s -- %s; watch %s" % (FIRES, fires[0], fires[1] or "",
                                                              json.dumps(fires[2], default=str)[:600])
    if fires[0] == "PASS" and control[0] == "PASS":
        return 0, "A2 holds: forced -> RM_Muurrok seen; control -> none (%s PASS, %s PASS)" % (FIRES, CONTROL)
    if "UNMEASURED" in (fires[0], control[0]):
        return 2, "UNMEASURED: fires=%s control=%s: %s | %s" % (fires[0], control[0], fires[1], control[1])
    return 1, "A2 fails: fires=%s (%s) control=%s (%s)" % (fires[0], fires[1], control[0], control[1])


def _cache_path():
    import rmpaths
    return str(rmpaths.rm_path("scratch", "prove_muurrok_emergence.json"))


def _vhash():
    with open(os.path.join(HERE, "validation.py"), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def live_result():
    path = _cache_path()
    try:
        with open(path, encoding="utf-8") as fh:
            c = json.load(fh)
        if c.get("vhash") == _vhash() and time.time() - c.get("at", 0) < CACHE_S:
            print("[prove] reusing the run of %s (%s)" % (time.ctime(c["at"]), path), file=sys.stderr)
            return c["res"]
    except (OSError, ValueError):
        pass
    V = _load_validation()
    import runner
    from rimdrive import Session
    runner.ensure_playing_map()
    with Session(lock=None, focus=False) as s:
        res = run_chains(V, s, runner._default_anchor(s))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"vhash": _vhash(), "at": time.time(), "res": res}, fh, indent=1, default=str)
    return res


def selftest():
    """The judge over the scripted fake: healthy holds both clauses; each break reads as it must."""
    import selftest_stillsand as S
    S.V._STATE.clear()
    bad = []
    cases = [((), 0, 0), (("no_muurrok",), 0, 1), (("muurrok_never_arrives",), 0, 1),
             (("muurrok_arrives_late",), 0, 1), (("muurrok_spawns_unforced",), 0, 1),
             (("muurrok_pawn_unforced_no_visit",), 0, 1)]
    for broken, want1, want2 in cases:
        res = run_chains(S.V, S.Fake(broken), (125, 125))
        got = (judge(res, "A1"), judge(res, "A2"))
        if (got[0][0], got[1][0]) != (want1, want2):
            bad.append("%s: want A1=%d A2=%d, got %s" % (broken or "healthy", want1, want2, got))
        if broken == ("no_muurrok",) and "turned back" not in (res[FIRES][1] or ""):
            bad.append("no_muurrok: the FAIL does not name the end (turned back): %s" % res[FIRES][1])
        if broken == ("muurrok_arrives_late",) and "never arrived" not in (res[FIRES][1] or ""):
            bad.append("arrives_late: the FAIL does not name the end (never arrived): %s" % res[FIRES][1])
        if broken == ("muurrok_never_arrives",) and "never arrived" not in (res[FIRES][1] or ""):
            bad.append("never_arrives: the FAIL does not name the end (never arrived): %s" % res[FIRES][1])
    # can-fail probes of the judge itself: an UNMEASURED or missing component never holds a clause
    probe = {FIRES: ["UNMEASURED", "x", []], CONTROL: ["PASS", "", []]}
    if judge(probe, "A1")[0] != 2 or judge(probe, "A2")[0] != 2 or judge({}, "A2")[0] != 2:
        bad.append("judge: an UNMEASURED/missing component did not read 2")
    # A1 needs the cause line: a measured verdict that names no end of the visit is not a cause (exit 1)
    for v, detail, notes in (("PASS", "", []), ("FAIL", "", []), ("PASS", "", [[["A line of glare"], 1, "", []]]),
                             ("PASS", "never arrived", []), ("FAIL", "", [[[], 0, "something else", []]])):
        if judge({FIRES: [v, detail, notes], CONTROL: ["PASS", "", []]}, "A1")[0] != 1:
            bad.append("judge: A1 %s with no named end (%r, %r) did not read 1" % (v, detail, notes))
    for v, detail in (("PASS", "arrived +1500, last seen +2200"), ("FAIL", "MOD: ... it never arrived"),
                      ("FAIL", "MOD: ... (turned back: no standable entry cell?)")):
        if judge({FIRES: [v, detail, []], CONTROL: ["PASS", "", []]}, "A1")[0] != 0:
            bad.append("judge: A1 %s naming its end (%r) did not read 0" % (v, detail))
    for b in bad:
        print("  BAD:", b)
    print("prove_muurrok_emergence selftest: %d cases, %s" % (len(cases), "FAIL" if bad else "ok"))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--clause", choices=("A1", "A2"))
    g.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        err, sys.stderr = sys.stderr, open(os.devnull, "w")     # the suite's progress lines are for live runs
        try:
            return selftest()
        finally:
            sys.stderr = err
    try:
        res = live_result()
    except Exception as ex:                  # no game, no bridge, no map: unmeasured, never a verdict
        print("UNMEASURED: %s: %s" % (type(ex).__name__, ex))
        return 2
    code, line = judge(res, a.clause)
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
