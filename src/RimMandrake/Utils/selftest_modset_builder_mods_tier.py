#!/usr/bin/env python3
"""selftest_modset_builder_mods_tier.py -- a tier named by its mods (LIGHTSPEED_REWIRE_ROUND_AS_TESTQ_CLIENT).

Relentless sends every live-proof clause with no live-tier line to SteveDesktop as a testq job of profile
tier:mods__<tokens> (relentless_live_round.mods_tier writes the name); the worker resolves that name here, at the job's
source_sha. What must hold, offline, on a fake installed map:
  - the name round-trips: relentless_live_round.mods_tier(pids) -> modset_builder.tier_def(name, installed) wants the
    bridge, Gimme Some Slack and exactly those pids; `mods__base` wants the base alone;
  - resolve_tier closes it over dependencies and all five DLC, and refuses nothing on a clean map;
  - a token no installed mod spells stays as written, so resolve_tier reports it missing (never a quieter list); a
    token two installed packageIds spell raises; a malformed or overlong name is no tier;
  - the two sides agree on prefix, base name, always-loaded mods and the length cap; the marker the round greps for
    at a build's sha is the name modset_builder defines;
  - testq.tier_problem and tier_load accept a mods__ name; --tier accepts one.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "testq"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
import modset_builder as MB           # noqa: E402
import relentless_live_round as LR    # noqa: E402

FAILS = []


def ok(cond, msg):
    print(("ok    " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def rec(pid, deps=()):
    return {"packageId": pid, "name": pid, "deps": list(deps), "after": [], "before": [], "dir": "/x/" + pid}


def installed():
    m = {p: rec(p) for p in ("ludeon.rimworld",) + MB.DLC_IDS + (MB.HARMONY, MB.BRIDGE)}
    m["mandrake.rm.gimmesomeslack"] = rec("mandrake.rm.gimmesomeslack", [MB.HARMONY])
    m["mandrake.rm.flowworks"] = rec("mandrake.rm.flowworks", [MB.HARMONY, "mandrake.rm.gimmesomeslack"])
    m["mandrake.rm.dep_one"] = rec("mandrake.rm.dep_one")
    m["mandrake.rut.graffiti"] = rec("mandrake.rut.graffiti", ["mandrake.rm.dep_one"])
    m["7f.alienworlds"] = rec("7f.alienworlds")
    return m


def t_round_trip():
    inst = installed()
    pids = ["mandrake.rut.graffiti", "mandrake.rm.flowworks", "7f.alienworlds", "brrainz.rimbridgeserver"]
    name, why = LR.mods_tier(pids)
    ok(name == "mods__7f_alienworlds__mandrake_rm_flowworks__mandrake_rut_graffiti" and why is None,
       "mods_tier sorts, drops the always-loaded, dots become _: %s %s" % (name, why))
    ok(LR.mods_tier(list(reversed(pids)))[0] == name, "the name does not depend on order (one train per mod set)")
    t = MB.tier_def(name, inst)
    ok(t and set(t["want"]) == set(MB.MODS_TIER_ALWAYS) | set(pids) and t["dlc"],
       "tier_def decodes it back: %s" % (t or {}).get("want"))
    ordered, missing, refusals = MB.resolve_tier(name, inst)
    ok(not missing and not refusals and all(d in ordered for d in MB.DLC_IDS) and "mandrake.rm.dep_one" in ordered
       and MB.HARMONY in ordered, "resolve_tier: closure, all five DLC, no refusal: %s %s %s" % (ordered, missing, refusals))
    base, _ = LR.mods_tier(["brrainz.rimbridgeserver", "Mandrake.RM.GimmeSomeSlack"])
    ok(base == MB.MODS_TIER_BASE == "mods__base" and set(MB.tier_def(base, inst)["want"]) == set(MB.MODS_TIER_ALWAYS),
       "only the always-loaded mods: mods__base, the base alone: %s" % base)


def t_refusals():
    inst = installed()
    ordered, missing, _r = MB.resolve_tier("mods__mandrake_rm_flowworks__mandrake_rm_nosuchmod", inst)
    ok("mandrake_rm_nosuchmod" in missing, "an unspelled token is reported missing, not dropped: %s" % missing)
    inst["a.b_c"], inst["a_b.c"] = rec("a.b_c"), rec("a_b.c")
    try:
        MB.tier_def("mods__a_b_c", inst)
        ok(False, "an ambiguous token raises")
    except ValueError as e:
        ok("2 installed" in str(e), "an ambiguous token raises: %s" % e)
    for bad in ("mods__", "mods__a___b", "mods__A_b", "mods___x", "mods__" + "x" * 200, "nope", "mods_x"):
        ok(MB.tier_def(bad) is None, "no tier: %r" % bad[:40])
    ok(LR.mods_tier(["bad pid"])[0] is None and LR.mods_tier(["a__b.c"])[0] is None,
       "a packageId with no clean token is refused by name")
    ok(LR.mods_tier(["mandrake.rm.m%03d" % i for i in range(20)])[0] is None, "an overlong name is refused")
    ok(MB.tier_def("gimmesomeslack") is MB.TIERS["gimmesomeslack"], "a TIERS key is still its own record")


def t_sides_agree():
    ok(LR.MODS_TIER == MB.MODS_TIER_PREFIX and LR.MODS_TIER_BASE == MB.MODS_TIER_BASE
       and tuple(LR.MODS_TIER_ALWAYS) == tuple(MB.MODS_TIER_ALWAYS) and LR.MODS_TIER_MAX == MB.MODS_TIER_MAX,
       "relentless_live_round and modset_builder agree on the mods__ form")
    ok(hasattr(MB, LR.MODS_TIER_MARK), "the marker the round reads at a build's sha (%s) is modset_builder's" % LR.MODS_TIER_MARK)
    import testq
    import tier_load
    ok(testq.tier_problem("mods__mandrake_rm_flowworks") is None and testq.tier_problem("mods__A") is not None,
       "testq accepts a mods__ tier at submit and refuses a malformed one")
    ok("tier_def(tier) is None" in open(tier_load.__file__, encoding="utf-8").read(),
       "tier_load measures a mods__ tier instead of calling it unknown")
    ok(MB.tier_arg("mods__base") == "mods__base", "--tier takes a mods__ name")


if __name__ == "__main__":
    t_round_trip()
    t_refusals()
    t_sides_agree()
    print("selftest_modset_builder_mods_tier: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
