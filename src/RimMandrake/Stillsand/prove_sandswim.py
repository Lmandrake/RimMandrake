#!/usr/bin/env python3
"""Live proof of STILLSAND_SAND_SWIM_REMAINDER_1 §7: the sand-swim kit on a Stillsand quicktest map, each clause a state
read through validation.py's sandswim chain (never a screenshot hunt).

  A1  submerged and surfaced: a vekka is RM_SandSubmerged on Sand and not on Gravel; struck, it surfaces, and
      re-submerges after its window (sandswim.vekka_submerges_on_sand, sandswim.vekka_surfaces_when_struck)
  A2  the take: a kill on sand lays the RM_Filth_DisturbedSand funnel and sends the 'Taken under' letter
      (sandswim.vekka_take_leaves_funnel)
  A3  mech immunity: a submerged vekka ordered six times onto a Mech_Militor leaves it unhurt
      (sandswim.vekka_spares_a_mech)
  A4  a catch: painted RM_DeepSand is a water body whose catch list holds RM_DuneCrawler, and one Fish job there
      lands a Stillsand catch (sandswim.stillsand_catch)
  A5  the wake trough: a submerged vekka's 20-cell swim raises its own count in RM_TrackGridDiag.WakeTroughReport
      (sandswim.vekka_wake_trough_record)

    python3 src/RimMandrake/Stillsand/prove_sandswim.py --clause A1|A2|A3|A4|A5
    python3 src/RimMandrake/Stillsand/prove_sandswim.py --selftest        # offline, against selftest_stillsand's fake

Exit 0 = the clause holds, 1 = it does not, 2 = UNMEASURED (no game, a tool missing, an arm that could not be read).
The clauses share one run of the site, sandswim and log chains, cached 30 min beside validation.py's hash
(agent storage scratch/prove_sandswim.json). A run a surprise ended (a wild hostile's arrival, a mental break: the
safe_advance latch) says nothing about the mod, so it is run again, up to RUNS times, and never cached.
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

CHAINS = ("site", "sandswim", "log")
CLAUSES = {
    "A1": ("sandswim.vekka_submerges_on_sand", "sandswim.vekka_surfaces_when_struck"),
    "A2": ("sandswim.vekka_take_leaves_funnel",),
    "A3": ("sandswim.vekka_spares_a_mech",),
    "A4": ("sandswim.stillsand_catch",),
    "A5": ("sandswim.vekka_wake_trough_record",),
}
CACHE_S = 30 * 60
RUNS = 3


def _load_validation():
    import importlib.util
    spec = importlib.util.spec_from_file_location("stillsand_validation", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    return v


def run_chains(V, session, anchor):
    """{chain.component: [verdict, detail]} for CHAINS."""
    from suite import TestContext
    V._STATE.clear()
    out = {}
    for name, fn in V.suite.chains:
        if name not in CHAINS:
            continue
        t = TestContext(session, anchor=anchor)
        try:
            fn(t)
        except Exception as ex:
            out[name + ".<CRASH>"] = ["CRASH", "%s: %s" % (type(ex).__name__, ex)]
            continue
        for c in t.components:
            out["%s.%s" % (name, c.name)] = [c.verdict, c.detail]
    return out


def judge(res, clause):
    keys = CLAUSES[clause]
    crash = dict((k, v[1]) for k, v in res.items() if k.endswith(".<CRASH>") and k.split(".")[0] in ("site", "sandswim"))
    if crash:
        return 2, "UNMEASURED: a chain crashed: %s" % crash
    miss = [k for k in keys if k not in res]
    if miss:
        return 2, "UNMEASURED: components missing from the run: %s" % miss
    red = dict((k, res[k]) for k in keys if res[k][0] in ("FAIL", "CRASH"))
    if red:
        return 1, "%s fails: %s" % (clause, red)
    if any(res[k][0] != "PASS" for k in keys):
        return 2, "UNMEASURED: %s" % dict((k, res[k]) for k in keys if res[k][0] != "PASS")
    return 0, "%s holds: %s PASS" % (clause, ", ".join(k.split(".")[1] for k in keys))


def surprised(res):
    """True when a clause's component read UNMEASURED because a surprise ended the chain."""
    return any(res.get(k, ("", ""))[0] == "UNMEASURED" and "surprise" in str(res.get(k, ("", ""))[1])
               for keys in CLAUSES.values() for k in keys)


def run_past_surprises(run, runs=RUNS):
    """run() until a run no surprise ended, at most `runs` times -> the last result."""
    res = {}
    for _ in range(runs):
        res = run()
        if not surprised(res):
            break
    return res


def _vhash():
    h = hashlib.sha256()
    for f in ("validation.py", "prove_sandswim.py"):
        with open(os.path.join(HERE, f), "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:16]


def live_result():
    import rmpaths
    path = str(rmpaths.rm_path("scratch", "prove_sandswim.json"))
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
        res = run_past_surprises(lambda: run_chains(V, s, runner._default_anchor(s)))
    if surprised(res):
        return res
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"vhash": _vhash(), "at": time.time(), "res": res}, fh, indent=1, default=str)
    return res


def selftest():
    """Every clause reads 0 on the healthy fake, 1 when its own arm is broken, 2 on a missing or crashed run."""
    import selftest_stillsand as S
    bad = []

    def run(broken=()):
        S.V._STATE.clear()
        return run_chains(S.V, S.Fake(broken), (125, 125))

    healthy = run()
    for c in sorted(CLAUSES):
        got = judge(healthy, c)
        if got[0] != 0:
            bad.append("healthy %s: %s" % (c, got[1]))
    breaks = {"A1": ("no_surface", "submerge_on_rock"), "A2": ("no_funnel",), "A3": ("mech_hurt",),
              "A4": ("no_catch", "wrong_fish", "zone_refused"), "A5": ("no_trough",)}
    for c, bs in sorted(breaks.items()):
        for b in bs:
            res = run([b])
            if judge(res, c)[0] != 1:
                bad.append("break %s: %s did not read 1: %s" % (b, c, judge(res, c)[1]))
            for other in CLAUSES:
                if other != c and other not in [k for k, v in breaks.items() if b in v] and judge(res, other)[0] == 1:
                    bad.append("break %s also turned %s red" % (b, other))
    res = run(["no_submerge"])
    if judge(res, "A5")[0] != 2 or judge(res, "A3")[0] != 2:
        bad.append("a vekka that never submerges must leave A3/A5 UNMEASURED, not red or green")
    if judge({}, "A4")[0] != 2 or judge({"sandswim.<CRASH>": ["CRASH", "x"]}, "A1")[0] != 2:
        bad.append("a missing or crashed run did not read 2")
    if judge(run(["wander_once"]), "A1")[0] != 0:
        bad.append("a vekka wandering off its half once must void that attempt, not the clause")
    if judge(run(["wander_always"]), "A1")[0] != 2:
        bad.append("a vekka that never holds its half must leave A1 UNMEASURED")
    hit = {"sandswim.vekka_spares_a_mech": ["UNMEASURED", "a surprise ended this chain earlier: surprise: x"]}
    clean = {"sandswim.vekka_spares_a_mech": ["PASS", ""]}
    runs = [hit, clean]
    if run_past_surprises(lambda: runs.pop(0)) is not clean or runs:
        bad.append("a surprise-ended run was not run again")
    if not surprised(run_past_surprises(lambda: hit)):
        bad.append("run_past_surprises hid a surprise that never cleared")
    for b in bad:
        print("  BAD:", b)
    print("prove_sandswim selftest: %d clauses, %s" % (len(CLAUSES), "FAIL" if bad else "ok"))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--clause", choices=sorted(CLAUSES))
    g.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        err, sys.stderr = sys.stderr, open(os.devnull, "w")
        try:
            return selftest()
        finally:
            sys.stderr = err
    try:
        res = live_result()
    except Exception as ex:
        print("UNMEASURED: %s: %s" % (type(ex).__name__, ex))
        return 2
    code, line = judge(res, a.clause)
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
