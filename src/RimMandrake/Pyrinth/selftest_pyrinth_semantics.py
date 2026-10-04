#!/usr/bin/env python3
"""selftest_pyrinth_semantics.py -- PYRINTH_COVERAGE_GAPS_1: the furniture/blade/effecter/patch bars of validation.py go red on the
XML break each exists to catch (planted on the parsed elements in memory, never the shipped files) and stay green on the
shipped pack. Run bare: python3 src/RimMandrake/Pyrinth/selftest_pyrinth_semantics.py"""
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


def comp(el, named, cls):
    return V._comp(V.effective_comps(el, named), cls)[0]


def main():
    byname, named, patches = V.load_pack()
    check("shipped pack: no semantic finding", V.semantic_findings(byname, named, patches) == [], V.semantic_findings(byname, named, patches))
    check("sanity probe: 4 glowing defs, 3 flame defs, blade and heater parsed", all(n in byname for n in V.GLOW_DEFS) and "DV_MeleeWeapon_PyrinthBlade" in byname)
    check("sanity probe: wall lamp's own Inherit=False comps are the effective ones (one glower, radius 9)",
          V._num(comp(byname["DV_PyrinthWallLamp"], named, "CompProperties_Glower"), "glowRadius") == 9.0)

    def run_break(tag, fn, must):
        b, n, pa = V.load_pack()
        fn(b, n, pa)
        got = V.semantic_findings(b, n, pa)
        check("break %-34s reddens (%s)" % (tag, must), any(must in g for g in got), got)

    def setc(el, n, cls, tag, val):
        comp(el, n, cls).find(tag).text = val

    run_break("lamp glowRadius 0", lambda b, n, p: setc(b["DV_PyrinthLamp"], n, "CompProperties_Glower", "glowRadius", "0"), "Glower")
    run_break("wall lamp brighter than lamp", lambda b, n, p: setc(b["DV_PyrinthWallLamp"], n, "CompProperties_Glower", "glowRadius", "11"), "dimmer")
    run_break("heater weaker than pylon", lambda b, n, p: setc(b["DV_PyrinthHeater"], n, "CompProperties_HeatPusher", "heatPerSecond", "1"), "heat ladder")
    run_break("pylon heat not powered-class", lambda b, n, p: setc(b["DV_PyrinthBrazier"], n, "CompProperties_HeatPusher", "compClass", "CompHeatPusher"), "CompHeatPusherPowered")
    run_break("heater heatPerSecond 0", lambda b, n, p: setc(b["DV_PyrinthHeater"], n, "CompProperties_HeatPusher", "heatPerSecond", "0"), "HeatPusher")

    def focus_artistic(b, n, p):
        comp(b["DV_PyrinthLamp"], n, "CompProperties_MeditationFocus").find("focusTypes/li").text = "Artistic"
    run_break("lamp focus not Flame", focus_artistic, "Flame")

    def drop_lamp_from_list(b, n, p):
        defs = comp(b["DV_PyrinthBrazier"], n, "CompProperties_MeditationFocus").find("offsets/li[@Class='FocusStrengthOffset_BuildingDefsLit']/defs")
        for li in list(defs):
            if li.text == "DV_PyrinthLamp":
                defs.remove(li)
    run_break("pylon forgets the torch", drop_lamp_from_list, "nearby-flame list omits")

    def no_focus_stat(b, n, p):
        sb = n["DV_PyrinthTorchBase"].find("statBases")
        sb.remove(sb.find("MeditationFocusStrength"))
    run_break("torch base loses the focus stat", no_focus_stat, "MeditationFocusStrength statBase")

    def lit_zero(b, n, p):
        comp(b["DV_PyrinthBrazier"], n, "CompProperties_MeditationFocus").find("offsets/li[@Class='FocusStrengthOffset_Lit']/offset").text = "0"
    run_break("pylon lit offset 0", lit_zero, "lit-flame offset")

    run_break("spark effecter names a missing mote", lambda b, n, p: b["DV_PyrinthSparkingEffect"].find("children/li/moteDef").__setattr__("text", "DV_Mote_Nope"), "mote")
    run_break("spark mote wrong class", lambda b, n, p: b["DV_Mote_PyrinthSpark"].find("thingClass").__setattr__("text", "Mote"), "mote")
    run_break("spark never fires", lambda b, n, p: b["DV_PyrinthSparkingEffect"].find("children/li/chancePerTick").__setattr__("text", "0"), "chancePerTick")
    run_break("small spark not rarer", lambda b, n, p: b["DV_PyrinthSparkingEffectSmall"].find("children/li/chancePerTick").__setattr__("text", "0.5"), "rarer")
    run_break("lamp effecter missing", lambda b, n, p: b["DV_PyrinthLamp"].find("comps/li[@Class='CompProperties_Effecter']/effecterDef").__setattr__("text", "DV_NoEffecter"), "effecter")
    run_break("blade point stops searing", lambda b, n, p: b["DV_MeleeWeapon_PyrinthBlade"].findall("tools/li")[1].find("extraMeleeDamages/li/amount").__setattr__("text", "0"), "blade")

    def edge_not_burning(b, n, p):
        t = b["DV_MeleeWeapon_PyrinthBlade"].findall("tools/li")[2]
        t.remove(t.find("extraMeleeDamages"))
    run_break("blade edge loses flame", edge_not_burning, "blade")
    run_break("blade tool power 0", lambda b, n, p: b["DV_MeleeWeapon_PyrinthBlade"].find("tools/li/power").__setattr__("text", "0"), "blade")
    run_break("heater filth missing", lambda b, n, p: setc(b["DV_PyrinthHeater"], n, "CompProperties_Explosive", "preExplosionSpawnThingDef", "DV_Nope"), "explosive")

    def bad_cost(b, n, p):
        import xml.etree.ElementTree as ET
        ET.SubElement(b["DV_PyrinthHeater"].find("costList"), "DV_Nope").text = "1"
    run_break("heater costs an undefined item", bad_cost, "costs ")

    def mo_target(b, n, p):
        for fn, root in p:
            for xp in root.iter("xpath"):
                if "DV_PyrinthHeater" in (xp.text or ""):
                    xp.text = xp.text.replace("DV_PyrinthHeater", "DV_NoHeater")
    run_break("MO patch targets a missing def", mo_target, "xpath")

    def roy_value(b, n, p):
        for fn, root in p:
            for li in root.iter("li"):
                if li.text == "DV_PyrinthBrazier":
                    li.text = "DV_NoBrazier"
    run_break("Royalty patch adds an undefined def", roy_value, "patch adds")

    def roy_unguarded(b, n, p):
        for fn, root in p:
            for li in root.iter("li"):
                if li.text == "DV_PyrinthBrazier" and "MayRequire" in li.attrib:
                    del li.attrib["MayRequire"]
    run_break("Royalty patch loses its MayRequire", roy_unguarded, "MayRequire")

    # the chain: clean passes (offline), a planted break reddens only through the chain, stubs stay UNMEASURED
    def chain(mutate=None):
        saved = V.semantic_findings
        if mutate:
            V.semantic_findings = lambda b, n, p: mutate(saved(b, n, p))
        try:
            game = MockGame()
            s = FastSession(transport=MockTransport(game), strict=False)
            with s:
                res = runner.run_suite(V.suite, s, anchor=None, mod=None)
        finally:
            V.semantic_findings = saved
        return dict((c["name"], c["verdict"]) for ch in res["chains"] if ch["name"] == "furniture_and_weapon" for c in ch["components"])
    got = chain()
    check("clean chain: the 6 static bars PASS", sum(1 for v in got.values() if v == "PASS") == 6, got)
    got = chain(lambda f: f + ["DV_X: something brand new and unclaimed"])
    check("an unclaimed finding reddens no_finding_escapes_the_five_bars_above", got["no_finding_escapes_the_five_bars_above"] == "FAIL", got)
    got = chain(lambda f: f + ["DV_PyrinthLamp: no Glower with glowRadius > 0 (0 glowers)"])
    check("a Glower finding reddens the torch bar", got["torch_family_glows_heats_and_carries_the_ladder"] == "FAIL", got)

    if FAILS:
        print("\n%d Pyrinth semantic selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall Pyrinth semantic selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
