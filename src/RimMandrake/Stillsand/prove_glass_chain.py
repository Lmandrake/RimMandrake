#!/usr/bin/env python3
"""Live proof of STILLSAND_GLASS_CHAIN_REMAINDER_1 spec 4 (the parent STILLSAND_GLASS_LENS_CHAIN_1's criteria) on a
Stillsand quicktest map, each clause a state read through validation.py's glass chain (never a screenshot hunt).

  A1  clearing a drift drops glass sand: a colonist clears three 0.5-deep drift cells and RM_GlassSand appears,
      no more than 0.5 x 6 per cell (glass.drift_clear_drops_glass_sand)
  A2  the sun furnace and the lens bench each complete one bill cycle in full sun (10 sun glass, 1 precision lens),
      and both are refused by their sun gate in the RM_DuneGale weather and under a roof
      (glass.furnace_and_bench_cycle_in_sun_stop_in_gale_and_roof)
  A3  the solar oven (no fuel or power comp) cooks one simple meal in sun, and is refused by its sun gate in shade
      (a roofed oven) (glass.oven_cooks_in_sun_not_shade)

    python3 src/RimMandrake/Stillsand/prove_glass_chain.py --clause A1|A2|A3
    python3 src/RimMandrake/Stillsand/prove_glass_chain.py --selftest      # offline, against selftest_stillsand's fake

Exit 0 = the clause holds, 1 = it does not, 2 = UNMEASURED (no game, a tool missing, an arm that could not be read).
The clauses share one run of the site, glass and log chains, cached 30 min beside validation.py's hash
(agent storage scratch/prove_glass_chain.json).
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

CHAINS = ("site", "glass", "log")
CLAUSES = {
    "A1": ("glass.drift_clear_drops_glass_sand",),
    "A2": ("glass.furnace_and_bench_cycle_in_sun_stop_in_gale_and_roof",),
    "A3": ("glass.oven_cooks_in_sun_not_shade",),
}
CACHE_S = 30 * 60


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
    crash = dict((k, v[1]) for k, v in res.items() if k.endswith(".<CRASH>") and k.split(".")[0] in ("site", "glass"))
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


def _vhash():
    h = hashlib.sha256()
    for f in ("validation.py", "prove_glass_chain.py"):
        with open(os.path.join(HERE, f), "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:16]


def live_result():
    import rmpaths
    path = str(rmpaths.rm_path("scratch", "prove_glass_chain.json"))
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
    breaks = {"A1": ("drift_no_yield",), "A2": ("gale_ignored", "lens_double", "no_workgiver"),
              "A3": ("oven_in_shade", "oven_fuel", "no_workgiver")}
    for c, bs in sorted(breaks.items()):
        for b in bs:
            res = run([b])
            if judge(res, c)[0] != 1:
                bad.append("break %s: %s did not read 1: %s" % (b, c, judge(res, c)[1]))
            for other in CLAUSES:
                if other != c and other not in [k for k, v in breaks.items() if b in v] and judge(res, other)[0] == 1:
                    bad.append("break %s also turned %s red" % (b, other))
    if judge({}, "A2")[0] != 2 or judge({"glass.<CRASH>": ["CRASH", "x"]}, "A1")[0] != 2:
        bad.append("a missing or crashed run did not read 2")
    for b in bad:
        print("  BAD:", b)
    print("prove_glass_chain selftest: %d clauses, %s" % (len(CLAUSES), "FAIL" if bad else "ok"))
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
