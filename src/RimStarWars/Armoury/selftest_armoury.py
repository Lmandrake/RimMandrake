#!/usr/bin/env python3
"""selftest_armoury.py -- offline proof for Armoury's melee_ladder_landed and ranged_ladder_landed chains.

Run bare: python3 src/RimStarWars/Armoury/selftest_armoury.py   (exit 0 = clean)

A mock get_defs serves every patched weapon with the patch's own tool powers (donor OuterRim_* defs absent, as
on a list without that mod). Clean must PASS; a power that did not land, one of our absorbed weapons missing, a
non-numeric power and a blind patch parse must each turn the component red.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import runner                                                  # noqa: E402
import validation as V                                         # noqa: E402
from modcheck import Suite                                     # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def make_ext(brk):
    targets = V.melee_targets()

    def ext(game, tool, p):
        if tool != "jawa/get_defs":
            return None
        want = [s.split("/", 1)[1] for s in str(p.get("defs") or "").split(";") if "/" in s]
        rows, missing = [], []
        for n in want:
            if n.startswith("OuterRim_") or ("lost" in brk and n == "guy762_vsword"):
                missing.append(n)
                continue
            tools = [{"label": lb, "power": pw, "cooldownTime": 2.0} for lb, pw in sorted(targets[n].items())]
            if "not_landed" in brk and n == "guy762_vglaive":
                tools[0]["power"] = 9.0
            if "garbage" in brk and n == "RSW_JDSA_Vibroaxe":
                tools[0]["power"] = "n/a"
            rows.append({"defName": n, "fields": {"tools": tools}})
        return {"success": True, "foundCount": len(rows), "notFound": missing, "defs": rows}
    return ext


def run(brk=()):
    suite = Suite("ArmouryMelee")
    suite.chain("melee_ladder_landed")(V.melee_ladder_landed)
    game = MockGame()
    game.ext = make_ext(set(brk))
    saved = V.melee_targets
    if "blind" in brk:
        V.melee_targets = lambda path=None: {}
    try:
        s = FastSession(transport=MockTransport(game), strict=False)
        with s:
            res = runner.run_suite(suite, s, anchor=None, mod=None)
    finally:
        V.melee_targets = saved
    return [(c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"]]


def make_ranged_ext(brk):
    targets = V.ranged_targets()
    own = V.own_declared_defnames()

    def ext(game, tool, p):
        if tool != "jawa/projectile_damage":
            return None
        want = [n for n in str(p.get("defs") or "").split(";") if n]
        val = dict((n, v) for n, v, _g in targets)
        grp = dict((n, g) for n, _v, g in targets)
        rows, missing = [], []
        for n in want:
            donor = grp[n] not in (None, "Core", "Anomaly", "Odyssey") and n not in own
            absent = (grp[n] in ("Outer Rim - Core", "Alpha Mechs") and n not in own)
            if absent or ("lost" in brk and n == "RSW_High_Blue_Blaster_Bolt") \
                    or ("partial" in brk and n == "VFES_Bullet_Catapult"):
                missing.append(n)
                continue
            got = val[n]
            if "not_landed" in brk and n == "Bullet_MiniSlug":
                got = 7
            if "garbage" in brk and n == "RSW_Mid_Red_Blaster_Bolt":
                got = "n/a"
            rows.append({"defName": n, "found": True, "isProjectile": not ("not_proj" in brk and n == "FT_Bullet_ATShell"),
                         "damageAmountBase": got, "damageAmount": got, "donor": donor})
        return {"success": True, "foundCount": len(rows), "notFound": missing, "rows": rows}
    return ext


def run_ranged(brk=(), targets=None):
    suite = Suite("ArmouryRanged")
    suite.chain("ranged_ladder_landed")(V.ranged_ladder_landed)
    game = MockGame()
    game.ext = make_ranged_ext(set(brk))
    saved = V.ranged_targets
    if targets is not None:
        V.ranged_targets = lambda path=None: targets
    try:
        s = FastSession(transport=MockTransport(game), strict=False)
        with s:
            res = runner.run_suite(suite, s, anchor=None, mod=None)
    finally:
        V.ranged_targets = saved
    return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])


def main():
    m = V.melee_targets()
    check("the generated melee patch parses (>= 15 weapons, >= 40 tool powers; 18/49 on 2026-10-03)",
          len(m) >= 15 and sum(len(v) for v in m.values()) >= 40, (len(m), sum(len(v) for v in m.values())))
    check("guy762_vsword carries handle 10 / point 25 / edge 30",
          m.get("guy762_vsword") == {"handle": 10.0, "point": 25.0, "edge": 30.0}, m.get("guy762_vsword"))
    want = [("melee_patch_powers_are_live", "PASS")]
    check("clean: PASS with the donor's defs absent", run() == want, run())
    for brk in ("not_landed", "lost", "garbage", "blind"):
        got = run((brk,))
        check("break %-10s turns the component FAIL" % brk, got == [("melee_patch_powers_are_live", "FAIL")], got)

    # ---- ranged (ARMOURY_PROJECTILE_DAMAGE_TOOL_1)
    r = V.ranged_targets()
    own = V.own_declared_defnames()
    check("the generated ranged patch parses (>= 40 damageAmountBase ops; 43 on 2026-10-03)", len(r) >= 40, len(r))
    check("RSW_High_Blue_Blaster_Bolt is def-guarded at 30 and declared by this mod",
          ("RSW_High_Blue_Blaster_Bolt", 30, None) in r and "RSW_High_Blue_Blaster_Bolt" in own, r[:3])
    # the guard component FAILs exactly when the shipped patch puts an op on our own def under a donor FindMod
    # (the five KotOR bolts did until ARMOURY_KOTOR_BOLT_GUARD_1); a clean patch (same ops, the own-def ops moved out of the FindMod) must PASS both components
    clean = [(n, v, (None if n in own else g)) for n, v, g in r]
    got = run_ranged(targets=clean)
    check("clean (own ops def-guarded): both components PASS",
          got == {"own_ranged_ops_carry_no_donor_guard": "PASS", "ranged_patch_damage_is_live": "PASS"}, got)
    shipped = run_ranged()
    check("shipped patch: guard component FAILs iff an own-def op sits under a donor FindMod",
          shipped.get("own_ranged_ops_carry_no_donor_guard")
          == ("FAIL" if any(n in own and g not in (None, "Core", "Anomaly", "Odyssey") for n, _v, g in r) else "PASS"),
          shipped)
    for brk in ("not_landed", "lost", "garbage", "partial", "not_proj"):
        got = run_ranged((brk,), targets=clean)
        check("ranged break %-10s turns the live component FAIL" % brk,
              got.get("ranged_patch_damage_is_live") == "FAIL" and got.get("own_ranged_ops_carry_no_donor_guard") == "PASS", got)
    got = run_ranged(targets=[])
    check("ranged break blind: guard FAIL, live never PASS",
          got.get("own_ranged_ops_carry_no_donor_guard") == "FAIL"
          and got.get("ranged_patch_damage_is_live") in ("FAIL", "UNMEASURED"), got)

    # durasteel conversion: clean passes; planted defects (a source count the patch lacks; a leftover donor name) fail
    import tempfile, shutil
    check("durasteel convert: clean tree", V.durasteel_convert_static() == [], V.durasteel_convert_static())
    check("outerrim patch: clean", V.durasteel_outerrim_static() == [], V.durasteel_outerrim_static())
    check("plasteel cut: clean", V.plasteel_cut_static() == [], V.plasteel_cut_static())
    tmp = tempfile.mkdtemp()
    try:
        open(os.path.join(tmp, "r.xml"), "w").write("<Defs><RecipeDef><defName>Make_PlasteelGF</defName></RecipeDef></Defs>")
        open(os.path.join(tmp, "empty.xml"), "w").write("<Patch/>")
        got = V.plasteel_cut_static([tmp], os.path.join(tmp, "empty.xml"))
        check("plasteel cut: planted surviving recipe and unnamed donor recipes caught", len(got) == 4, got)
        open(os.path.join(tmp, "p.xml"), "w").write('<Patch><Operation Class="PatchOperationReplace"><xpath>/Defs//OuterRim_Durasteel[text()="30"]</xpath>'
                                                    '<value><RSW_Durasteel>31</RSW_Durasteel></value></Operation></Patch>')
        got = V.durasteel_outerrim_static(os.path.join(tmp, "p.xml"))
        check("outerrim patch: planted wrong count and missing forms caught", any("count 30" in b for b in got) and len(got) >= 3, got)
        open(os.path.join(tmp, "x.xml"), "w").write("<Defs><ThingDef><costList><RSW_Durasteel>777</RSW_Durasteel>"
                                                    "<KOTOR_AlloyDurasteel>5</KOTOR_AlloyDurasteel></costList></ThingDef></Defs>")
        got = V.durasteel_convert_static(defs_dir=tmp)
        check("durasteel convert: planted missing count and leftover name caught",
              any("777" in b for b in got) and any("still names" in b for b in got), got)
    finally:
        shutil.rmtree(tmp)

    # transparisteel fold: clean passes; planted defects caught
    check("transparisteel fold: clean tree", V.transparisteel_fold_static() == [], V.transparisteel_fold_static())
    tmp = tempfile.mkdtemp()
    try:
        d = os.path.join(tmp, "d.xml")
        open(d, "w").write("<Defs><ThingDef><defName>RM_FineSand</defName></ThingDef><ThingDef><defName>RM_Geo</defName><costList><RM_SunGlass>7</RM_SunGlass></costList></ThingDef>"
                           "<RecipeDef><defName>RM_Make_Bottle_Glass</defName><fixedIngredientFilter><thingDefs><li>Steel</li></thingDefs></fixedIngredientFilter></RecipeDef>"
                           "<RecipeDef><defName>RM_Grind</defName><ingredients><li><filter><thingDefs><li>RM_LensGlass</li></thingDefs></filter></li></ingredients></RecipeDef>"
                           "<RecipeDef><defName>RM_MeltSunGlass</defName><products><RM_SunGlass>10</RM_SunGlass></products></RecipeDef></Defs>")
        open(os.path.join(tmp, "empty.xml"), "w").write("<Patch/>")
        got = V.transparisteel_fold_static(stillsand_defs=[d], flowworks_defs=[], patch_path=os.path.join(tmp, "empty.xml"))
        check("transparisteel fold: planted survivors (cost, bottle, lens, old melt) caught with an empty patch",
              any("costList" in b for b in got) and any("bottle" in b for b in got) and any("RM_LensGlass" in b for b in got)
              and any("produces" in b or "old melt" in b for b in got), got)
    finally:
        shutil.rmtree(tmp)

    # doonium / phrik ores and smelts: clean passes; planted defects caught
    check("ores and smelts: clean tree", V.ores_and_smelts_static() == [], V.ores_and_smelts_static())
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "defs"))
        open(os.path.join(tmp, "defs", "RSW_Doonium.xml"), "w").write("<Defs><ThingDef><defName>RSW_MineableDoonium</defName><building><mineableThing>Steel</mineableThing>"
            "<mineableScatterCommonality>2</mineableScatterCommonality></building></ThingDef></Defs>")
        open(os.path.join(tmp, "defs", "RSW_Phrik.xml"), "w").write("<Defs/>")
        open(os.path.join(tmp, "a.xml"), "w").write('<Patch><Operation><xpath>/Defs/GenStepDef[defName="Asteroid"]/genStep/mineableCounts</xpath><value><MineableGold>1~2</MineableGold></value></Operation>'
            '<Operation><xpath>/Defs/GenStepDef/genStep/mineableCounts</xpath></Operation></Patch>')
        open(os.path.join(tmp, "s.xml"), "w").write("<Patch/>")
        got = V.ores_and_smelts_static(defs_dir=os.path.join(tmp, "defs"), ast_patch=os.path.join(tmp, "a.xml"), smelt_patch=os.path.join(tmp, "s.xml"))
        check("ores and smelts: planted wrong yield, scatter route, bad asteroid ops, missing processes caught",
              any("does not yield" in b for b in got) and any("allowlist" in b for b in got) and any("unscoped" in b for b in got)
              and sum("not defined" in b for b in got) >= 4, got)
    finally:
        shutil.rmtree(tmp)

    if FAILS:
        print("\n%d Armoury selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall Armoury melee/ranged-ladder selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
