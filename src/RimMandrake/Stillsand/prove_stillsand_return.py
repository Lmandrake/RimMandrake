#!/usr/bin/env python3
"""Live proof of STILLSAND_RETURN_REMAINDER_1 (the Return's remainder) on a Stillsand quicktest map, every DLC, each
clause a state read through validation.py's water chain plus the log chain's log_clean (never a screenshot hunt).

  A1  UTINNI TIER (the Utinni layer + Ideology): a colony whose primary ideo holds RUT_Ritual_TheReturn accrues 6 L of
      Sun-Debt from one canteen egg's drink hook, the Return opens when a dune gale (RM_DuneGale) ends (opening serial
      up, the ritual holds an obligation), and a good outcome at a RUT_DebtStone lowers the debt and blooms hourbloom
      in the ring (water.return_sun_debt_gale_opens_good_outcome_pays); the outcome's own Player.log line is
      "[RM_WaterLedgerProof] Return outcome 1 at RUT_DebtStone: ..."
  A2  RM TIER (no Utinni layer): no ledger def loads, so the settings window draws no debt row and nothing counts
      (water.rm_tier_has_no_ledger), and a poured canteen egg still blooms hourbloom (water.pour_blooms_on_sand)
  A3  either tier: a pour leaves a drawn darker stain on every live wet cell, none with the drawReturnLine toggle
      off, and a dune gale wipes the cells and the stain (water.wet_line_drawn_then_gale_wipes)

A1 reads UNMEASURED (2) on the RM tier and A2 on the Utinni tier: each holds on its own tier.

    python3 src/RimMandrake/Stillsand/prove_stillsand_return.py --clause A1|A2|A3
    python3 src/RimMandrake/Stillsand/prove_stillsand_return.py --selftest      # offline, against selftest_stillsand's fake

Exit 0 = the clause holds, 1 = it does not, 2 = UNMEASURED (no game, a tool missing, the wrong tier).
The clauses share one run of the site, water and log chains, cached 30 min beside validation.py's hash
(agent storage scratch/prove_stillsand_return.json).
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

CHAINS = ("site", "water", "log")
CLAUSES = {
    "A1": ("water.return_sun_debt_gale_opens_good_outcome_pays", "log.log_clean"),
    "A2": ("water.rm_tier_has_no_ledger", "water.pour_blooms_on_sand", "log.log_clean"),
    "A3": ("water.wet_line_drawn_then_gale_wipes", "log.log_clean"),
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
    crash = dict((k, v[1]) for k, v in res.items() if k.endswith(".<CRASH>") and k.split(".")[0] in ("site", "water"))
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
    for f in ("validation.py", "prove_stillsand_return.py"):
        with open(os.path.join(HERE, f), "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:16]


def live_result():
    import rmpaths
    path = str(rmpaths.rm_path("scratch", "prove_stillsand_return.json"))
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
    """Every clause reads 0 on its own healthy tier, 2 on the other tier, 1 when its own arm is broken, 2 on a
    missing or crashed run."""
    import selftest_stillsand as S
    bad = []

    def run(broken=()):
        S.V._STATE.clear()
        return run_chains(S.V, S.Fake(broken), (125, 125))

    tiers = {"utinni": run(), "rm": run(["rm_tier"])}
    want = {("A1", "utinni"): 0, ("A1", "rm"): 2, ("A2", "utinni"): 2, ("A2", "rm"): 0,
            ("A3", "utinni"): 0, ("A3", "rm"): 0}
    for (c, tier), code in sorted(want.items()):
        got = judge(tiers[tier], c)
        if got[0] != code:
            bad.append("%s tier %s: want %d, got %s" % (tier, c, code, got))
    breaks = {"A1": ([], ("gale_no_opening", "egg_drink_free", "return_no_pay", "return_no_ring", "log_error")),
              "A2": (["rm_tier"], ("rm_ledger_live", "no_bloom", "log_error")),
              "A3": ([], ("line_not_drawn", "line_ignores_toggle", "gale_keeps_wet", "log_error"))}
    for c, (base, bs) in sorted(breaks.items()):
        for b in bs:
            res = run(base + [b])
            if judge(res, c)[0] != 1:
                bad.append("break %s: %s did not read 1: %s" % (b, c, judge(res, c)[1]))
            for other in CLAUSES:
                if b == "log_error":      # every clause carries log.log_clean: a log error turns all of them red
                    continue
                hit = [k for k, (bb, v) in breaks.items() if b in v and bb == base]
                if other != c and other not in hit and judge(res, other)[0] == 1:
                    bad.append("break %s also turned %s red" % (b, other))
    if judge({}, "A2")[0] != 2 or judge({"water.<CRASH>": ["CRASH", "x"]}, "A1")[0] != 2:
        bad.append("a missing or crashed run did not read 2")
    for b in bad:
        print("  BAD:", b)
    print("prove_stillsand_return selftest: %d clauses, %s" % (len(CLAUSES), "FAIL" if bad else "ok"))
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
