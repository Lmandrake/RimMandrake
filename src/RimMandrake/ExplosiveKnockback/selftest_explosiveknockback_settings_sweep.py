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
# selftest-timeout: 300
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
}
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
    faults = static(mod, swept, defaults)
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
    for k in missed:
        print("FAIL planted static fault NOT CAUGHT:", k)
    # the scene's own action list, for the record: saved settings it never names (test text, a journal question)
    scene = next(s for s in json.load(open(SCENES))["scenes"] if s["id"] == "sc_settings_sweep")
    words = json.dumps(scene["action"])
    unnamed = [f for f in re.findall(r"Scribe_Values\.Look\(ref (\w+),", mod) if f not in words and f not in SWEPT_ELSEWHERE]
    if unnamed:
        print("NOTE sc_settings_sweep's action names %d saved settings fewer than the class saves: %s" % (len(unnamed), ",".join(unnamed)))
    kline = next((l for l in lines if l.startswith("explosive knockback settings sweep")), "no summary line")
    ok = rc == 0 and not faults and not missed
    print("%s | static: %d faults, %d/%d planted caught | %s" % (kline, len(faults), len(planted) - len(missed), len(planted), "PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
