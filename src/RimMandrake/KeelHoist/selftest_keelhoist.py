#!/usr/bin/env python3
"""selftest_keelhoist.py -- KEELHOIST_COVERAGE_GAPS_1 (offline half): the static gate/formula bars of validation.py stay green on the
shipped source and go red on each planted break (source text mutated in memory, never the shipped files). Runs the new chain
through its OWN Suite so no legacy chain takes a real desktop screenshot. python3 src/RimMandrake/KeelHoist/selftest_keelhoist.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
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
    assert old in s[fn], "planted break target not in %s: %r" % (fn, old)   # a break that matches nothing proves nothing
    s[fn] = s[fn].replace(old, new, 1)
    return s


def main():
    srcs = V.load_srcs()
    hed = V._xml("Defs", "HediffDefs", "RM_HoistRestraint.xml").find("HediffDef")
    check("shipped source: settings clean", V.settings_findings(srcs) == [], V.settings_findings(srcs))
    check("shipped source: gates clean", V.gate_findings(srcs) == [], V.gate_findings(srcs))
    check("shipped source: formulas clean", V.formula_findings(srcs, hed) == [], V.formula_findings(srcs, hed))
    fm = V.cycle_formula(srcs)
    check("sanity probe: formula parsed as (625, 60, 50) and 19 gates declared", fm == (625, 60, 50) and len(V.GATES) == 19, fm)
    check("cycle ticks: 0 kg 625, 50 kg 1250, 0.25x 156, 4x 2500", [V.cycle_ticks(fm, 0, 1.0), V.cycle_ticks(fm, 50, 1.0),
          V.cycle_ticks(fm, 0, 0.25), V.cycle_ticks(fm, 0, 4.0)] == [625, 1250, 156, 2500])
    check("method_body reads an expression-bodied member", "KeelHoistSettings.pitSales" in (V.method_body(srcs["RM_HoistFrame.cs"], r"public bool KeepersBuying") or ""))
    check("method_body returns None for a missing method", V.method_body(srcs["RM_KeelHoist.cs"], r"NoSuchMethodHere\(") is None)

    K, P, M, H = "RM_KeelHoist.cs", "KeelHoistPatches.cs", "KeelHoistMod.cs", "RM_HoistFrame.cs"
    KN = "RM_HoistKernel.cs"   # the Verse-free kernel the gates and formulas now live in

    def gate_break(tag, fn, old, new, must):
        got = V.gate_findings(mutated(fn, old, new))
        check("break gate: %-44s -> %s" % (tag, must), any(must in g for g in got), got)

    gate_break("tetherLock ignored", KN, "return accepted && tetherLock &&", "return accepted && true &&", "tetherLock")
    gate_break("tetherLock not passed in", P, "TetherBlocksLaunch(__result.Accepted, KeelHoistSettings.tetherLock,", "TetherBlocksLaunch(__result.Accepted, true,", "tetherLock")
    gate_break("tether lock stops refusing", P, 'new AcceptanceReport("Reel in the keel hoist first.")', "AcceptanceReport.WasAccepted", "tether lock")
    gate_break("masterEnabled dropped from IsEnterable", K, "EnterRefusal(KeelHoistSettings.masterEnabled,", "EnterRefusal(true,", "masterEnabled")
    gate_break("masterEnabled guard lost in the kernel", KN, 'if (!masterEnabled) return "off";', "", "masterEnabled")
    gate_break("requireGravEngine ignored", "PlaceWorker_NeedsGravEngine.cs", "!KeelHoistSettings.requireGravEngine", "false", "requireGravEngine")
    gate_break("cableRange unread", K, "float range = KeelHoistSettings.cableRange;", "float range = 14f;", "cableRange")
    gate_break("restraintHours unread", K, "KeelHoistSettings.restraintHours", "24f", "restraintHours")
    gate_break("cycleTimeMultiplier unread", K, "KeelHoistSettings.cycleTimeMultiplier", "1f", "cycleTimeMultiplier")
    gate_break("openLineMeter unread", P, "OpenLineStepsNow(KeelHoistSettings.openLineMeter,", "OpenLineStepsNow(true,", "openLineMeter")
    gate_break("openLineMeter dropped from the kernel step", KN, "return openLineMeter && ticksGame", "return ticksGame", "openLineMeter")
    gate_break("downedStrangers guard lost in TryCapture", K, "CaptureFor(KeelHoistSettings.downedStrangersAndBeasts, p.Dead,", "CaptureFor(true, p.Dead,", "downedStrangersAndBeasts")
    gate_break("downedStrangers guard lost in the kernel", KN, "if (!downedStrangersAndBeasts || dead || playerFaction)", "if (dead || playerFaction)", "downedStrangersAndBeasts")
    gate_break("pitSales unread", H, "KeelHoistSettings.pitSales,", "true,", "pitSales")
    gate_break("pitSales dropped from the kernel", KN, "return hasBuyer && pitSales &&", "return hasBuyer &&", "pitSales")
    gate_break("genstep ignores masterEnabled", H, "if (!KeelHoistSettings.masterEnabled)", "if (false)", "masterEnabled")

    def formula_break(tag, fn, old, new, must):
        got = V.formula_findings(mutated(fn, old, new), hed)
        check("break formula: %-40s -> %s" % (tag, must[:34]), any(must in g for g in got), got)

    formula_break("base cycle 600", KN, "BaseCycleTicks = 625;", "BaseCycleTicks = 600;", "BaseCycleTicks")
    formula_break("mass divisor 100", KN, "mass / 50f", "mass / 100f", "ruled 50")
    formula_break("multiplier dropped", KN, "BaseCycleTicks * cycleTimeMultiplier", "BaseCycleTicks", "no longer has the parsed shape")
    formula_break("stack mass ignores stackCount", K, "t.GetStatValue(StatDefOf.Mass) * t.stackCount", "t.GetStatValue(StatDefOf.Mass)", "stackCount")
    formula_break("Open Line rises 2/h", KN, "OpenLineRisePerHour = 1f", "OpenLineRisePerHour = 2f", "Open Line meter arithmetic")
    formula_break("Open Line falls 0.25/h", KN, "OpenLineFallPerHour = 0.5f", "OpenLineFallPerHour = 0.25f", "Open Line meter arithmetic")
    formula_break("Open Line never stepped hourly", KN, "ticksGame % TicksPerHour == OpenLineMinute", "ticksGame % 5 == OpenLineMinute", "once per hour")
    formula_break("restraint ignores hours", KN, "Math.Round(restraintHours * TicksPerHour)", "60000", "restraintHours")
    formula_break("owned animals restrained", K, "p.Faction == null", "true", "unowned")
    s2 = dict(srcs)
    s2[M] = s2[M].replace("restraintHours = 24f;", "restraintHours = 12f;", 1)
    check("break formula: restraintHours default 12 vs hediff 60000", any("disagrees" in g for g in V.formula_findings(s2, hed)))
    import xml.etree.ElementTree as ET
    h2 = ET.fromstring(ET.tostring(hed))
    h2.find(".//capMods/li/setMax").text = "1"
    check("break formula: restraint no longer caps Moving at 0", any("Moving" in g for g in V.formula_findings(srcs, h2)))

    def settings_break(tag, old, new, must):
        got = V.settings_findings(mutated(M, old, new))
        check("break settings: %-36s -> %s" % (tag, must), any(must in g for g in got), got)

    settings_break("Scribe default drifts", 'Scribe_Values.Look(ref cableRange, "cableRange", 14f)', 'Scribe_Values.Look(ref cableRange, "cableRange", 20f)', "Scribe default")
    settings_break("setting never saved", 'Scribe_Values.Look(ref chuteHours, "chuteHours", 6f);', "", "not saved")
    settings_break("default outside slider", "cableRange = 14f;", "cableRange = 50f;", "outside its slider")
    settings_break("no checkbox", 'list.CheckboxLabeled("Open Line meter", ref openLineMeter,', 'list.Label("Open Line meter",', "no checkbox")

    # the chain through its own Suite: green on shipped source, red on a planted break, live stubs UNMEASURED
    def chain(srcs_patch=None):
        saved = V.load_srcs
        if srcs_patch:
            V.load_srcs = lambda: srcs_patch
        try:
            own = V.Suite("KeelHoist")
            own.toggles = list(V.suite.toggles)
            own.chains = [(n, f) for n, f in V.suite.chains if n == "static_gates_and_formulas"]
            with FastSession(transport=MockTransport(MockGame()), strict=False) as s:
                res = runner.run_suite(own, s, anchor=None, mod=None)
        finally:
            V.load_srcs = saved
        return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])
    got = chain()
    check("clean chain: three static bars PASS", [got[k] for k in got if not k.startswith(("hoist_", "tether_", "beast_"))] == ["PASS"] * 3, got)
    check("live stubs are never a PASS", all(got[k] != "PASS" for k in ("hoist_cycle_moves_cargo_down_and_up", "tether_lock_refuses_a_real_launch", "beast_arrives_restrained_live")), got)
    got = chain(mutated(KN, "return accepted && tetherLock &&", "return accepted && true &&"))
    check("a tether-lock break reddens every_gate_reads_its_toggle_where_it_must", got["every_gate_reads_its_toggle_where_it_must"] == "FAIL", got)

    if FAILS:
        print("\n%d KeelHoist selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall KeelHoist selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
