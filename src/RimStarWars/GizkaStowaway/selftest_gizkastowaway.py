#!/usr/bin/env python3
"""selftest_gizkastowaway.py -- GIZKASTOWAWAY_COVERAGE_GAPS_1 (offline half): the behaviour_rules chain of validation.py is green on
the shipped source and goes red on each planted break (source text mutated in memory). The chain runs through its OWN Suite.
python3 src/RimStarWars/GizkaStowaway/selftest_gizkastowaway.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))
for p in (HERE, UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)
import validation as V                                         # noqa: E402
import runner                                                  # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def mutated(fn, old, new):
    s = dict(V.load_srcs())
    assert old in s[fn], "planted break target not in %s: %r" % (fn, old)    # a break that matches nothing proves nothing
    s[fn] = s[fn].replace(old, new, 1)
    return s


def main():
    srcs, props = V.load_srcs(), V.behaviour_props()
    for name, fn, args in (("sliders", V.slider_findings, (srcs,)), ("triggers", V.trigger_findings, (srcs,)),
                           ("fecundity", V.fecundity_findings, (srcs, props)), ("infestation", V.infestation_findings, (srcs,)),
                           ("cull", V.cull_findings, (srcs,))):
        check("shipped source: %s clean" % name, fn(*args) == [], fn(*args))
    check("sanity probe: props are (4 d, 8x, 12 C, 0.35) and 5 source files read", props == (4.0, 8.0, 12.0, 0.35) and len(srcs) == 6, (props, len(srcs)))
    check("interval mirror: empty 4 d, half full 18 d, capped 32 d, 2x rate halves", [V.replicate_interval_days(4, 8, p, 22, r) for p, r in ((0, 1), (11, 1), (22, 1), (22, 2))] == [4.0, 18.0, 32.0, 16.0])
    check("interval mirror: cap 0 means full, rate 0 means 1x", V.replicate_interval_days(4, 8, 3, 0, 1) == 32.0 and V.replicate_interval_days(4, 8, 0, 22, 0.0) == 4.0)
    check("discovery chance: 0.35 x1 = .35, x3 clamps to 1, x0 = 0", [V.discovery_chance(0.35, f) for f in (1, 3, 0)] == [0.35, 1.0, 0.0] or V.discovery_chance(0.35, 3) == 1.0)
    check("stage mirror at cap 22: 0,1,3,7,16 -> 0,1,2,3,4", [V.stage_for(srcs, n, 22) for n in (0, 1, 3, 7, 16)] == [0, 1, 2, 3, 4])
    check("Plague reachable at every cap 4..80 (was [4, 5] before the clamp)", V.plague_unreachable_caps(srcs) == [], V.plague_unreachable_caps(srcs))
    check("no stage skipped at any cap 4..80", V.skipped_stage_caps(srcs) == [], V.skipped_stage_caps(srcs))
    check("stage mirror at cap 4: counts 0..4 -> 0,1,2,3,4; cap 5 -> 0,1,1,2,3,4", [V.stage_for(srcs, n, 4) for n in range(5)] == [0, 1, 2, 3, 4]
          and [V.stage_for(srcs, n, 5) for n in range(6)] == [0, 1, 1, 2, 3, 4], ([V.stage_for(srcs, n, 4) for n in range(5)], [V.stage_for(srcs, n, 5) for n in range(6)]))
    check("method_body: expression member and missing method", V.method_body("x public bool A => b && c; y", r"public bool A") is not None
          and V.method_body("nothing", r"zzz") is None)

    M, F, I, P, S = V.MGR, V.FEC, V.INF, V.PAT, "RSW_GizkaSettings.cs"

    def brk(tag, fn, old, new, finder, must, extra=()):
        got = finder(mutated(fn, old, new), *extra)
        check("break %-46s -> %s" % (tag, must[:30]), any(must in g for g in got), got)

    for name, setting, const in V.TRIGGERS:
        brk("%s ignores %s" % (name[7:], setting), M, "Ready(RSW_GizkaSettings.%s)" % setting, "Ready(true)", V.trigger_findings, setting)
    brk("master switch dropped from Ready", M, "!RSW_GizkaSettings.stowawayEventsEnabled || ", "", V.trigger_findings, "Ready()")
    brk("donor-absent guard dropped", M, "if (RSW_GizkaPopulation.Kind == null) return false;", "", V.trigger_findings, "Ready()")
    brk("cooldown 1 day", M, "DiscoveryCooldownTicks = 900000", "DiscoveryCooldownTicks = 60000", V.trigger_findings, "cooldown")
    brk("trade as common as gravship", M, "ChanceTrade = 0.05f", "ChanceTrade = 0.5f", V.trigger_findings, "not gravship > salvage")
    brk("salvage rolls the trade chance", M, "Roll(ChanceSalvage)", "Roll(ChanceTrade)", V.trigger_findings, "does not roll")
    brk("Roll ignores the frequency slider", M, "baseChance * f", "baseChance", V.trigger_findings, "Roll is no longer")
    brk("discovery spawns a wild gizka", M, "Faction.OfPlayer, newborn: false", "null, newborn: false", V.trigger_findings, "ONE tame")
    brk("a Discover delivered twice", M, "            Discover(map, salvage.Position,", "            Discover(map, salvage.Position, \"a\", \"b\");\n            Discover(map, salvage.Position,", V.trigger_findings, "exactly one gizka")
    brk("a hook stops reaching Notify_TradeCompleted", P, "Instance?.Notify_TradeCompleted(", "Instance?.Nothing(", V.trigger_findings, "no Harmony hook")

    fb = lambda tag, fn, old, new, must: brk(tag, fn, old, new, V.fecundity_findings, must, (props,))
    fb("comfort gate dropped", F, "if (!IsComfortable(pawn)) return;", "", "comfort gate must return")
    fb("fuse burns before the comfort gate", F, "if (!IsComfortable(pawn)) return;\n\n            ticksUntilReplicate -= delta;", "ticksUntilReplicate -= delta;\n            if (!IsComfortable(pawn)) return;", "order")
    fb("cold threshold ignored", F, "temp < Props.minBreedingTemperature) return false", "false) return false", "IsComfortable")
    fb("hunger threshold ignored", F, "food.CurLevelPercentage < Props.minFoodLevel) return false", "false) return false", "IsComfortable")
    fb("cap check dropped from TryReplicate", F, "CountOnMap(pawn.Map) >= cap) return;", "CountOnMap(pawn.Map) >= 9999) return;", "population cap")
    fb("offspring join no faction", F, "pawn.Faction, newborn: true", "null, newborn: true", "inherit")
    fb("breedingRate no longer divides", F, "stretch / rate", "stretch", "ResetInterval")
    fb("interval floor gone", F, "Mathf.Max(2500,", "Mathf.Max(0,", "ResetInterval")
    fb("no stretch toward the cap", F, "Mathf.Lerp(1f, Mathf.Max(1f, Props.intervalStretchAtCap), fill)", "1f", "ResetInterval")
    fb("juveniles breed", F, "CurLifeStageIndex", "Xx", "order")
    for tag, props2, must in (("stretch 1x (no flattening)", (4.0, 1.0, 12.0, 0.35), "strictly increasing"), ("freezing threshold 0", (4.0, 8.0, 0.0, 0.35), "comfort gate numbers"),
                              ("hunger threshold 1.5", (4.0, 8.0, 12.0, 1.5), "comfort gate numbers")):
        got = V.fecundity_findings(srcs, props2)
        check("break hediff %-32s -> %s" % (tag, must[:26]), any(must in g for g in got), got)

    ib = lambda tag, fn, old, new, must: brk(tag, fn, old, new, V.infestation_findings, must)
    ib("chewing ignores its toggle", I, "RSW_GizkaSettings.chewingEnabled && stage", "stage", "chewing is not gated")
    ib("chewing at any stage", I, "stage >= GizkaStage.Infestation)", "stage >= GizkaStage.Cute)", "chewing is not gated")
    ib("announce on the way down", I, "if (stage > lastStage) AnnounceStage", "if (stage != lastStage) AnnounceStage", "steps DOWN")
    ib("plague band at 95 percent", I, "cap * 0.72f", "cap * 0.95f", "stage bands")
    ib("plague cap clamp lost", I, "Mathf.Min(cap, Mathf.Max(6,", "(Mathf.Max(6,", "Plague is unreachable")
    ib("infestation clamp lost", I, "Mathf.Min(plague - 1, Mathf.Max(4,", "(Mathf.Max(4,", "stage is skipped")
    ib("band floor lost", I, "Mathf.Max(3, Mathf.RoundToInt(cap * 0.14f))", "Mathf.RoundToInt(cap * 0.14f)", "StageFor")
    ib("outdoor gizka chew", I, "r.UsesOutdoorTemperature) continue", "false) continue", "outdoors")
    ib("unpowered buildings chew", I, "!power.PowerOn) continue", "false) continue", "DoChewing")
    ib("chewing ignores the room's gizka count", I, "ChewMtbTicksPerGizka / here", "ChewMtbTicksPerGizka", "DoChewing")
    ib("every chewable building chewed", I, "return;   // at most one chewed building per check", "", "DoChewing")
    ib("cadence gate lost", I, "TicksGame % CheckIntervalTicks != 0", "TicksGame < 0", "cadence")
    ib("count includes bought gizka", POP_ := V.POP, "IsStowawayGizka(pawns[i])) n++", "pawns[i] != null) n++", "not stowaway lineage")
    ib("stowaway test ignores the hediff", V.POP, "GetFirstHediffOfDef(Fecundity) != null", "true", "IsStowawayGizka")

    cb = lambda tag, fn, old, new, must: brk(tag, fn, old, new, V.cull_findings, must)
    cb("cull guilt ignores its toggle", P, "|| !RSW_GizkaSettings.cullGuiltEnabled) return;", ") return;", "gated on the master")
    cb("every gizka death is guilt", P, "if (!RSW_GizkaPopulation.IsStowawayGizka(victim)) return;", "", "IsStowawayGizka")
    cb("witness radius 40", P, "WitnessRadius = 12f", "WitnessRadius = 40f", "radius")
    cb("no line of sight needed", P, "!GenSight.LineOfSight(c.Position, victim.Position, victim.Map)", "false", "LineOfSight")

    sb = lambda tag, old, new, must: brk(tag, S, old, new, V.slider_findings, must)
    sb("frequency slider floor 0.5", "discoveryFrequency = list.Slider(discoveryFrequency, 0f, 3f)", "discoveryFrequency = list.Slider(discoveryFrequency, 0.5f, 3f)", "cannot be slid to 0")
    sb("cap default 100 outside 4..80", "public static int populationCap = 22;", "public static int populationCap = 100;", "does not contain")

    def chain(srcs_patch=None):
        saved = V.load_srcs
        if srcs_patch:
            V.load_srcs = lambda: srcs_patch
        try:
            own = V.Suite("GizkaStowaway")
            own.toggles = list(V.suite.toggles)
            own.chains = [(n, f) for n, f in V.suite.chains if n == "behaviour_rules"]
            with FastSession(transport=MockTransport(MockGame()), strict=False) as s:
                res = runner.run_suite(own, s, anchor=None, mod=None)
        finally:
            V.load_srcs = saved
        return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])
    got = chain()
    check("clean chain: five behaviour bars PASS", sorted(got.values()) == ["PASS"] * 5, got)
    got = chain(mutated(F, "if (!IsComfortable(pawn)) return;", ""))
    check("a comfort-gate break reddens only the replication bar", [k for k, v in got.items() if v == "FAIL"] == ["replication_stalls_cold_and_hungry_and_stops_at_the_cap"], got)

    if FAILS:
        print("\n%d GizkaStowaway selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall GizkaStowaway selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
