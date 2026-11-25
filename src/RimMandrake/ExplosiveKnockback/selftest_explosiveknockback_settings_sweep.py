#!/usr/bin/env python3
"""Offline settings sweep for Explosive Knockback (bars settings_scale_and_switch / inv_settings, T_SETTINGS_SWEEP_OFFLINE).

Owner 2026-11-13: "can't we actually simulate that settings check offline?" Two halves:
1. The kernel lane (Source/SelfTest/KnockbackSweep.cs, `--sweep`): sc_settings_sweep's lane as kernel inputs, run once at
   default and once per kernel-side setting; each change alters only its own outcomes, the way the scene expects; two
   coupling mutants must go red; the default run repeats identically.
2. Static, here: the mod's Kernel() maps each kernel-side setting to its own KbSettings field (the sweep mirrors that
   mapping); the sweep's defaults equal RM_KnockbackMod.cs's; the saved Scribe fields equal the kernel sweep list plus the
   game-side list below plus enabled (sc_settings_off) and shieldsAbsorbThrow (sc_shield); no per-explosion, per-tick or
   body-size field is saved or declared.
Game-side settings stay in the live scene (sc_settings_sweep's wiring lines, or the scene named).

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_settings_sweep.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_explosiveknockback_kernel as kernel  # noqa: E402  (stages and runs Source/SelfTest)

MOD = os.path.join(HERE, "Source", "RM_KnockbackMod.cs")
SCENES = os.path.join(HERE, "..", "..", "..", "design", "concepts", "ExplosiveKnockback", "scenes.json")
# game-side: the kernel never reads these; each is proven where named
GAME_SIDE = {
    "throwDowned": "sc_settings_sweep", "throwAnimals": "sc_settings_sweep", "throwMechanoids": "sc_settings_sweep",
    "throwItems": "sc_settings_sweep", "throwCorpses": "sc_settings_sweep", "landingStunMin": "sc_settings_sweep",
    "landingStunMax": "sc_settings_sweep", "doorsTakeDamage": "sc_settings_sweep", "debugDrawVectors": "sc_settings_sweep",
    "flyingGoods": "sc_settings_sweep", "vanillaCratesClosed": "sc_settings_sweep", "gasChain": "sc_settings_sweep",
    "goodsFlightSpeed": "sc_storeroom_mortar", "goodsArcHeight": "sc_storeroom_mortar", "goodsSpinDegPerTick": "sc_storeroom_mortar",
    "goodsRebound": "sc_storeroom_mortar", "thrownGoodsBlastDamagePercent": "sc_storeroom_mortar",
    "goodsWallImpactPerCell": "sc_storeroom_mortar", "gasBurstRadius": "T_GAS_CLUMP_ORDER", "gasBurstGoodsCells": "T_GAS_CLUMP_ORDER",
    "gasPawnCooldownTicks": "T_GAS_CLUMP_ORDER",
    "closedContainerGuard": "sc_settings_sweep", "fireAtHalf": "sc_settings_sweep",
    # the blast show (0.2.0): what each switch does to a blast is the show kernel's (T_BLAST_SHOW_OFFLINE, S_SWITCH); that
    # the throws stay the same with the show off is sc_settings_sweep's showOff lane
    "showFireAndFlash": "sc_settings_sweep", "showScreenShake": "sc_settings_sweep", "showAirRipple": "sc_settings_sweep",
    "showCraterScars": "sc_settings_sweep", "showShakeStrength": "sc_settings_sweep", "showMarksLast": "sc_settings_sweep",
}
# the sheet's switches (settings_scale_and_switch, sheet.md "closed guard off, container goods thrown loose ... fire at half off,
# fire throws nothing"): each is a saved setting, default on, reset to on, and READ by the code path it switches (blind cycle 2,
# steward's decision 6). file -> the code that must read it.
SWITCH_READS = {
    # the throw decision is the Verse-free plan since 2026-11-17 (RM_KnockbackPlan.cs, run by the SelfTest): a switch the plan
    # reads is read there as q.<name>, and RM_KnockbackMod.Rules() must carry the setting into it (checked in switches())
    "closedContainerGuard": [("RM_KnockbackPlan.cs", r"public static string HeldReason\(KbFacts f, KbRules q\)(.*?)\n        \}"),
                             ("RM_MapComponent_Knockback.cs", r"InClosedContainer\(Thing t, Map map\)(.*?)\n        \}")],
    "fireAtHalf": [("RM_Patch_DamageWorker_ExplosionKnockback.cs", r"public static KbConfig ConfigOf\((.*?)\n        \}")],
    # goods in the air off: goods unthrown, never the old hop (sheet; the walk row yields to the bar, steward's decision 8)
    "flyingGoods": [("RM_KnockbackPlan.cs", r"public static bool GoodWillBeThrown\((.*?)\n        \}"),
                    ("RM_KnockbackPlan.cs", r"public static KbPlan Decide\((.*?)\n        \}\n\n")],
}
# a switch the plan reads reaches it only through the game-side caller: each caller must hand the plan the live Rules()
# (the old reads stood in these very bodies, so this is the hop the move added)
PLAN_CALLERS = {
    "closedContainerGuard": [(r"private static string HeldReason\(Thing t, Map map\)(.*?)\n        \}",
                              "KbPlanner.HeldReason(f, RimMandrakeExplosiveKnockbackSettings.Rules())")],
    "flyingGoods": [(r"public static bool ItemWillBeThrown\((.*?)\n        \}",
                     "KbPlanner.GoodWillBeThrown(f, blast, RimMandrakeExplosiveKnockbackSettings.Rules(),"),
                    (r"private bool Execute\(KnockbackRequest r\)(.*?)\n        \}\n\n",
                     "KbPlanner.Decide(f, BlastOf(r), RimMandrakeExplosiveKnockbackSettings.Rules(),")],
}


def switches(mod, src):
    """Each sheet switch: declared true, saved with default true, reset to true, and read inside the code path it switches."""
    faults = []
    for name, reads in SWITCH_READS.items():
        if not re.search(r"public static bool %s = true;" % name, mod):
            faults.append("switch %s is not a bool setting defaulting to true" % name)
        if not re.search(r'Scribe_Values\.Look\(ref %s, "%s", true\);' % (name, name), mod):
            faults.append("switch %s is not saved with default true" % name)
        if not re.search(r"RimMandrakeExplosiveKnockbackSettings\.%s = true;" % name, mod):
            faults.append("switch %s is not reset to true" % name)
        if not re.search(r"ref %s\b" % name, mod.split("DoWindowContents", 1)[-1]):
            faults.append("switch %s has no checkbox on the settings page" % name)
        for f, body_re in reads:
            m = re.search(body_re, src.get(f, ""), re.S)
            in_plan = f == "RM_KnockbackPlan.cs"
            carried = not in_plan or re.search(r"\b%s = %s\b" % (name, name), mod.split("public static KbRules Rules()", 1)[-1].split("\n        }", 1)[0])
            if not m or not carried or not re.search((r"\bq\.%s\b" if in_plan else r"RimMandrakeExplosiveKnockbackSettings\.%s\b") % name, m.group(1)):
                faults.append("switch %s is not read by %s (%s)" % (name, f, body_re.split("\\(")[0]))
        for body_re, call in PLAN_CALLERS.get(name, []):
            m = re.search(body_re, src.get("RM_MapComponent_Knockback.cs", ""), re.S)
            if not m or call not in m.group(1):
                faults.append("switch %s does not reach the plan: RM_MapComponent_Knockback.cs (%s) does not call %s"
                              % (name, body_re.split("\\(")[0], call.split("(")[0]))
    # flying goods off: goods unthrown, never the instant move (the skip moved from Execute into the plan's Decide)
    dec = re.search(r"public static KbPlan Decide\((.*?)\n        \}\n\n", src.get("RM_KnockbackPlan.cs", ""), re.S)
    if not dec or not re.search(r"if \(!pawn && !q\.flyingGoods\)\s*\{\s*return Skip\(p, \"flying_off\"\);", dec.group(1)):
        faults.append("flyingGoods off still falls through to the instant move (no flying_off skip)")
    return faults
SWEPT_ELSEWHERE = {"enabled": "sc_settings_off", "shieldsAbsorbThrow": "sc_shield"}
BANNED = re.compile(r"maxThrowsPerExplosion|maxItemThrowsPerMapTick|immuneBodySize|Throws\w*Per|BodySize", re.I)  # throw caps, body size
# Kernel(): mod setting -> KbSettings field, as KnockbackSweep.Kernel mirrors it
MAPPING = {"globalMultiplier": "strength", "creatureMassLimit": "creatureMassLimit", "lightMassLimit": "lightMassLimit",
           "impactEnabled": "impactDamageEnabled", "impactPerCell": "impactDamagePerCell", "sandbagsStop": "sandbagsStopThrow",
           "intoPits": "throwIntoPits"}


def static(mod, swept, defaults):
    faults = []
    k = re.search(r"public static KbSettings Kernel\(int ownCap = 0\)\s*\{(.*?)\n        \}", mod, re.S)
    if not k:
        return ["Kernel(int ownCap) not found in RM_KnockbackMod.cs"]
    got = dict(re.findall(r"^\s*(\w+)\s*=\s*(.+?),\s*$", k.group(1), re.M))
    if got.get("maxCells", "").replace(" ", "") != "RM_KnockbackMath.CapFor(ownCap,maxThrowCells,ownCapScale)":
        faults.append("Kernel() maxCells is %r, the sweep mirrors CapFor(ownCap, maxThrowCells, ownCapScale)" % got.get("maxCells"))
    for field, setting in MAPPING.items():
        if got.get(field, "").strip() != setting:
            faults.append("Kernel() sets %s from %r; the sweep mirrors %s" % (field, got.get(field), setting))
    extra = set(got) - set(MAPPING) - {"maxCells"}
    if extra:
        faults.append("Kernel() sets fields the sweep does not mirror: %s" % sorted(extra))
    declared = dict(re.findall(r"public static (?:bool|float|int) (\w+) = ([^;]+);", mod))
    for name, val in defaults.items():
        want = declared.get(name, "?").rstrip("f").lower()
        if want.replace(".0", "") != val.lower().replace(".0", ""):
            faults.append("default of %s: sweep %s, mod %s" % (name, val, declared.get(name)))
    saved = re.findall(r"Scribe_Values\.Look\(ref (\w+),", mod)
    listed = set(swept) | set(GAME_SIDE) | set(SWEPT_ELSEWHERE)
    for f in sorted(set(saved) - listed):
        faults.append("saved setting %s is in no sweep list (kernel, game side or elsewhere)" % f)
    for f in sorted(listed - set(saved)):
        faults.append("sweep lists %s, which is not a saved setting" % f)
    for f in sorted(set(saved) | set(declared)):
        if BANNED.search(f):
            faults.append("a per-explosion, per-tick or body-size setting exists: %s" % f)
    return faults


def main():
    rc, out = kernel.main(["--sweep"])
    if out == "UNMEASURED":
        print("UNMEASURED: no Windows dotnet.exe / D: staging root on this machine")
        return 1
    lines = out.replace("\r", "").splitlines()
    for l in lines:
        if l.startswith("FAIL") or "error" in l:
            print(l)
    sw = next((l for l in lines if l.startswith("SWEPT ")), None)
    df = next((l for l in lines if l.startswith("DEFAULTS ")), None)
    if not sw or not df:
        print("FAIL the kernel sweep printed no SWEPT/DEFAULTS lines (build failed?)")
        return 1
    swept = sw.split()[1].split(",")
    defaults = dict(kv.split("=", 1) for kv in df.split()[1:])
    mod = open(MOD, encoding="utf-8").read()
    src = {f: open(os.path.join(HERE, "Source", f), encoding="utf-8").read()
           for f in ("RM_MapComponent_Knockback.cs", "RM_Patch_DamageWorker_ExplosionKnockback.cs", "RM_KnockbackPlan.cs")}
    faults = static(mod, swept, defaults) + switches(mod, src)
    for f in faults:
        print("FAIL", f)
    # planted static faults
    planted = {
        "a coupled Kernel() field": mod.replace("lightMassLimit = lightMassLimit,", "lightMassLimit = creatureMassLimit,", 1),
        "a saved setting in no list": mod.replace('Scribe_Values.Look(ref enabled, "enabled", true);',
                                                  'Scribe_Values.Look(ref enabled, "enabled", true); Scribe_Values.Look(ref zzNew, "zzNew", 1f);', 1),
        "a per-explosion cap back": mod.replace("public static bool enabled = true;", "public static bool enabled = true; public static int maxThrowsPerExplosion = 8;", 1),
        "a changed default": mod.replace("public static float strength = 1f;", "public static float strength = 1.5f;", 1),
    }
    missed = [k for k, m in planted.items() if m == mod or not static(m, swept, defaults)]
    # planted switch faults: each must be seen by switches()
    cg_src = dict(src)
    cg_src["RM_KnockbackPlan.cs"] = re.sub(r"\bq\.closedContainerGuard\b", "true", src["RM_KnockbackPlan.cs"])
    cg_src["RM_MapComponent_Knockback.cs"] = re.sub(r"RimMandrakeExplosiveKnockbackSettings\.closedContainerGuard\b", "true", src["RM_MapComponent_Knockback.cs"])
    comp_k = src["RM_MapComponent_Knockback.cs"]
    fh_src = dict(src)
    fh_src["RM_Patch_DamageWorker_ExplosionKnockback.cs"] = re.sub(r"RimMandrakeExplosiveKnockbackSettings\.fireAtHalf\b", "true",
                                                                   src["RM_Patch_DamageWorker_ExplosionKnockback.cs"])
    sw_planted = {
        "closed guard read nowhere": (mod, cg_src),
        "fire at half read nowhere": (mod, fh_src),
        "fire at half defaults off": (mod.replace("public static bool fireAtHalf = true;", "public static bool fireAtHalf = false;", 1), src),
        "closed guard not carried into the plan": (mod.replace("closedContainerGuard = closedContainerGuard,", "", 1), src),
        "goods in the air read nowhere": (mod, dict(src, **{"RM_KnockbackPlan.cs": re.sub(r"\bq\.flyingGoods\b", "true", src["RM_KnockbackPlan.cs"])})),
        "the guard's caller hands the plan default rules": (mod, dict(src, **{"RM_MapComponent_Knockback.cs": comp_k.replace(
            "KbPlanner.HeldReason(f, RimMandrakeExplosiveKnockbackSettings.Rules())", "KbPlanner.HeldReason(f, new KbRules())", 1)})),
        "goods-in-the-air caller hands the plan default rules": (mod, dict(src, **{"RM_MapComponent_Knockback.cs": comp_k.replace(
            "KbPlanner.GoodWillBeThrown(f, blast, RimMandrakeExplosiveKnockbackSettings.Rules(),", "KbPlanner.GoodWillBeThrown(f, blast, new KbRules(),", 1)})),
        "Execute hands the plan default rules": (mod, dict(src, **{"RM_MapComponent_Knockback.cs": comp_k.replace(
            "KbPlanner.Decide(f, BlastOf(r), RimMandrakeExplosiveKnockbackSettings.Rules(), s, new RM_MapKbWorld(map, t))",
            "KbPlanner.Decide(f, BlastOf(r), new KbRules(), s, new RM_MapKbWorld(map, t))", 1)})),
        "goods in the air off falls through": (mod, dict(src, **{"RM_KnockbackPlan.cs": src["RM_KnockbackPlan.cs"].replace(
            'return Skip(p, "flying_off");', 'p.reason = "flying_off";', 1)})),
        "closed guard not saved": (re.sub(r'Scribe_Values\.Look\(ref closedContainerGuard, "closedContainerGuard", true\);', "", mod), src),
    }
    sw_missed = [k for k, (m, sr) in sw_planted.items() if (m == mod and sr == src) or not switches(m, sr)]
    for k in sw_missed:
        print("FAIL planted switch fault NOT CAUGHT:", k)

    for k in missed:
        print("FAIL planted static fault NOT CAUGHT:", k)
    # the scene's own action list, for the record: saved settings it never names (test text, a journal question)
    scene = next(s for s in json.load(open(SCENES))["scenes"] if s["id"] == "sc_settings_sweep")
    words = json.dumps(scene["action"])
    unnamed = [f for f in re.findall(r"Scribe_Values\.Look\(ref (\w+),", mod) if f not in words and f not in SWEPT_ELSEWHERE]
    if unnamed:
        print("NOTE sc_settings_sweep's action names %d saved settings fewer than the class saves: %s" % (len(unnamed), ",".join(unnamed)))
    kline = next((l for l in lines if l.startswith("explosive knockback settings sweep")), "no summary line")
    ok = rc == 0 and not faults and not missed and not sw_missed
    print("%s | static: %d faults, %d/%d planted caught, %d/%d switch faults caught | %s" % (kline, len(faults), len(planted) - len(missed), len(planted),
                                                                                          len(sw_planted) - len(sw_missed), len(sw_planted), "PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
