#!/usr/bin/env python3
"""Live proof of SOORRAK_INSTANT_JOB_LOOP_1: runs Stillsand validation.py's `site` and `soorrak` chains on the running
game (the site chain retiles the quicktest tile to RM_Stillsand and regenerates the map: a disposable test map, never a
planet anyone receives; six wild RM_Soorrak are spawned and read every 500 ticks for 3000) and judges the item's
criterion from the chain's evidence. State reads only: no flight is watched or captured.

  A1  Every RM_Soorrak still on the map at the end, within its first 2500 ticks, read a job other than
      Wait_MaintainPosture AND changed cell; and RM_FlightJobStartGuard logged no
      "[RM CreatureBehaviors] instant job loop: ... (RM_Soorrak)" warning. When the loop is back, the FAIL prints that
      warning, which names the instantly-ending JobDef, its giver class and think tree: the fix follows from it.

    python3 src/RimMandrake/Stillsand/prove_soorrak_not_stuck.py --clause A1
    python3 src/RimMandrake/Stillsand/prove_soorrak_not_stuck.py --selftest     # offline, against the scripted fake

Exit 0 = the clause holds, 1 = it does not, 2 = UNMEASURED (no game, every soorrak flew off, a chain crashed).
The run is cached for 30 minutes beside validation.py's hash (agent storage scratch/prove_soorrak_not_stuck.json).
"""
import argparse
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
for _p in (UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

CHAINS = ("site", "soorrak")
STUCK = "soorrak.soorrak_not_stuck"
WINDOW = 2500          # the criterion's ticks
FILLER = "Wait_MaintainPosture"
NOTES = ("soorrak samples", "instant job loop lines", "soorrak path length / jobs seen")
CACHE_S = 30 * 60


def _load_validation():
    import importlib.util
    spec = importlib.util.spec_from_file_location("stillsand_validation", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    return v


def run_chains(V, session, anchor):
    """{component key: [verdict, detail, {note label: data}]} for the CHAINS, on `session`."""
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
            out[name + ".<CRASH>"] = ["CRASH", "%s: %s" % (type(ex).__name__, ex), {}]
            continue
        for c in t.components:
            notes = dict((e.get("call"), e.get("result")) for e in (c.evidence or [])
                         if isinstance(e, dict) and e.get("call") in NOTES)
            out["%s.%s" % (name, c.name)] = [c.verdict, c.detail, notes]
    return out


def judge(res, clause="A1"):
    """(exit code, one line) for A1 over a run_chains result."""
    if any(k.endswith(".<CRASH>") for k in res):
        return 2, "UNMEASURED: a chain crashed: %s" % {k: v[1] for k, v in res.items() if k.endswith(".<CRASH>")}
    comp = res.get(STUCK)
    if comp is None:
        return 2, "UNMEASURED: %s missing from the run: %s" % (STUCK, sorted(res))
    verdict, detail, notes = comp[0], comp[1], comp[2] or {}
    loops = [x for x in (notes.get("instant job loop lines") or []) if x]
    if loops:
        return 1, "A1 fails: the instant job loop is back: %s" % " | ".join(str(x)[:400] for x in loops[:3])
    samples = notes.get("soorrak samples")
    if verdict == "UNMEASURED" or not isinstance(samples, dict) or not samples:
        return 2, "UNMEASURED: %s %s: %s (no soorrak samples to judge)" % (STUCK, verdict, detail)
    stuck = []
    for pid, rows in sorted(samples.items()):
        win = [r for r in rows if isinstance(r, (list, tuple)) and len(r) == 3 and r[0] <= WINDOW]
        cells = [tuple(r[1]) for r in win if r[1]]
        jobs = [r[2] for r in win if r[2]]
        moved = len(set(cells)) > 1
        real_job = any(j != FILLER for j in jobs)
        if not (moved and real_job):
            stuck.append("%s cells=%d distinct=%d jobs=%s" % (pid, len(cells), len(set(cells)), sorted(set(jobs))))
    if stuck:
        return 1, "A1 fails: %d of %d soorrak(s) on the map did not both change cell and read a job other than %s " \
                  "within %d ticks: %s" % (len(stuck), len(samples), FILLER, WINDOW, "; ".join(stuck))
    return 0, "A1 holds: all %d soorrak(s) still on the map changed cell and read a real job within %d ticks; no " \
              "instant job loop line (%s %s)" % (len(samples), WINDOW, STUCK, verdict)


def _cache_path():
    import rmpaths
    return str(rmpaths.rm_path("scratch", "prove_soorrak_not_stuck.json"))


def _vhash():
    h = hashlib.sha256()
    for f in ("validation.py", "prove_soorrak_not_stuck.py"):
        with open(os.path.join(HERE, f), "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:16]


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
    """The judge over the scripted fake (healthy holds, the stuck idle loop fails) and over hand-made evidence."""
    import selftest_stillsand as S
    bad = []
    for broken, want in (((), 0), (("soorrak_stuck",), 1)):
        S.V._STATE.clear()
        res = run_chains(S.V, S.Fake(broken), (125, 125))
        got = judge(res)
        if got[0] != want:
            bad.append("fake %s: want %d, got %s" % (broken or "healthy", want, got))
        if not broken and not (res.get(STUCK) or [0, 0, {}])[2].get("soorrak samples"):
            bad.append("fake healthy: the chain recorded no 'soorrak samples' note")

    def ev(samples, loops=(), verdict="PASS"):
        return {STUCK: [verdict, "", {"soorrak samples": samples, "instant job loop lines": list(loops)}]}

    good = [[0, [10, 10], None], [500, [11, 10], "GotoWander"], [1000, [12, 10], "Wait"]]
    filler = [[k * 500, [10, 10], FILLER if k else None] for k in range(7)]
    late = [[0, [10, 10], None], [500, [10, 10], FILLER], [3000, [14, 10], "GotoWander"]]
    nomove = [[0, [10, 10], None], [500, [10, 10], "Wait"], [1000, [10, 10], "Wait"]]
    onlyfiller_moved = [[0, [10, 10], None], [500, [11, 10], FILLER]]
    loop = "[RM CreatureBehaviors] instant job loop: Soorrak1 (RM_Soorrak) at (10, 0, 10) ended job X ..."
    cases = [(ev({"a": good}), 0), (ev({"a": good, "b": filler}), 1), (ev({"a": late}), 1),
             (ev({"a": nomove}), 1), (ev({"a": onlyfiller_moved}), 1), (ev({"a": good}, [loop]), 1),
             (ev({}), 2), (ev({"a": good}, verdict="UNMEASURED"), 2), ({}, 2),
             ({"soorrak.<CRASH>": ["CRASH", "x", {}]}, 2)]
    for res, want in cases:
        got = judge(res)
        if got[0] != want:
            bad.append("judge(%s): want %d, got %s" % (json.dumps(res)[:200], want, got))
    if "ended job X" not in judge(ev({"a": good}, [loop]))[1]:
        bad.append("judge: a loop FAIL does not print the guard's line")
    for b in bad:
        print("  BAD:", b)
    print("prove_soorrak_not_stuck selftest: %d cases, %s" % (len(cases) + 2, "FAIL" if bad else "ok"))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--clause", choices=("A1",))
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
