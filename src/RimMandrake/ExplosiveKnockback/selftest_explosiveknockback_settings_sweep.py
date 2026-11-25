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
3. The show half (T_SETTINGS_SWEEP_SHOW, bar blast_show_switches_off_clean): RM_KnockbackShowPlan run by its own generator
   (Source/SelfTestShow `--sweep-dump`) over the declared range of blasts, at default, once per show switch off, all off
   and the shake slider at 0 and 2, each through RM_KnockbackShow.Switches() as read from source: each switch off gives its
   own part the unmodded look and leaves every other part as at default; all off is the unmodded look with nothing of
   vanilla's stopped or replayed; every design part without a switch of its own fails by name (smoke and the two soots
   are unbuilt in 0.2.0); the throw reads no show setting, carries no show field and reads none of the show's writes.
   Planted switch-map and throw faults must be caught. The drawn look stays in sc_settings_sweep_show_switches.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_settings_sweep.py [--half offline|show]
The last line holds the show half's counts and both halves' verdicts; the exit code is both halves' unless --half.
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


def offline_half():
    """T_SETTINGS_SWEEP_OFFLINE: -> (ok, its summary line), the line printed as it always was."""
    rc, out = kernel.main(["--sweep"])
    if out == "UNMEASURED":
        print("UNMEASURED: no Windows dotnet.exe / D: staging root on this machine")
        return False, "offline UNMEASURED"
    lines = out.replace("\r", "").splitlines()
    for l in lines:
        if l.startswith("FAIL") or "error" in l:
            print(l)
    sw = next((l for l in lines if l.startswith("SWEPT ")), None)
    df = next((l for l in lines if l.startswith("DEFAULTS ")), None)
    if not sw or not df:
        print("FAIL the kernel sweep printed no SWEPT/DEFAULTS lines (build failed?)")
        return False, "offline FAIL: the kernel sweep printed no SWEPT/DEFAULTS lines"
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
    summary = "%s | static: %d faults, %d/%d planted caught, %d/%d switch faults caught | %s" % (
        kline, len(faults), len(planted) - len(missed), len(planted), len(sw_planted) - len(sw_missed), len(sw_planted), "PASS" if ok else "FAIL")
    print(summary)
    return ok, summary


# ---------------------------------------------------------------------------------------------------------------------
# T_SETTINGS_SWEEP_SHOW (bar blast_show_switches_off_clean, design/specs/2026-11-24-knockback-blast-show/design.md §5):
# "Each part of the blast show has its own on/off switch in Mod Settings, all on by default. With every switch off, a
# blast looks as it does in the unmodded game, and the throws are the same with the show on or off."
# Decided on the SHIPPED code: RM_KnockbackShowPlan.Plan is run by its own generator (Source/SelfTestShow, --sweep-dump)
# once per scenario over the declared range of blasts (SweepDump's comment there); each scenario's switches are what
# RM_KnockbackShow.Switches() hands the plan for those Mod Settings (Switches() and the defaults are read from source).
# The throw half is static: the throw code reads no show setting and carries no show field (the plan's three writes to
# a vanilla Explosion are read by no throw file, and by no vanilla damage code: decomp rw16 Explosion/DamageWorker).
import fcntl  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import selftest_explosiveknockback_blast_show as blast_show  # noqa: E402  (PARTS: the design's parts and switch names)

SRC = os.path.join(HERE, "Source")
SHOW_STAGE = os.environ.get("WINBUILD_ROOT", blast_show.rm_str("build")) + "/ExplosiveKnockbackShowSweep"
SETTINGS = "RimMandrakeExplosiveKnockbackSettings"
# design §4's ranked parts (keys and switch names are blast_show.PARTS') -> the KbShowSwitches field Switches() sets for it
PART_FIELD = {"fire_and_flash": "fireAndFlash", "screen_shake": "screenShake", "air_ripple": "airRipple",
              "crater_scar": "craterScars", "smoke": "smoke", "soot_on_things": "sootOnThings", "soot_on_pawns": "sootOnPawns"}
# what each part shows, from KbShowPlan's fields (their comments in RM_KnockbackShowPlan.cs). Each vanilla flag is the
# part's vanilla look KEPT: doVisualEffects stops vanilla's flash, cell flecks, shake and splash at once (§3.15), so a
# part's vanilla look is kept when nothing stops it or when the plan replays it.
OWN = {"fire_and_flash": ["flashScale", "fireballLobes", "fireballScale", "sparks", "debris", "debrisIsStone"],
       "screen_shake": ["shakeMag", "shakeHoldTicks"],
       "air_ripple": ["rippleDiameter", "rippleSeconds", "rippleAlpha"],
       "crater_scar": ["scarKind", "scarSize", "scarSizeClass"],
       "smoke": ["smokePuffs", "smokeSeconds"],
       "soot_on_things": ["sootReach"], "soot_on_pawns": ["sootReach"]}
VANILLA = {"fire_and_flash": [("vanilla flash and cell flecks", lambda r: r["suppressVanillaVisuals"] == "0"),
                              ("vanilla water splash", lambda r: r["suppressVanillaVisuals"] == "0" or r["replayWaterSplash"] == "1")],
           "screen_shake": [("vanilla shake", lambda r: (r["suppressVanillaVisuals"] == "0" and r["zeroVanillaShake"] == "0")
                             or r["replayVanillaShake"] == "1")],
           "crater_scar": [("vanilla blast mark", lambda r: r["suppressVanillaBlastMark"] == "0")]}
HANDOVER = ("suppressVanillaVisuals", "zeroVanillaShake", "suppressVanillaBlastMark", "replayVanillaShake", "replayWaterSplash")
NOT_PARTS = {"power": "the blast's measure, shared with the throw (S_ONE_MEASURE)",
             "show": "a harmful blast on the map; draws nothing by itself (every part's own field gates its drawing)"}
# the Explosion fields the show's prefix may write; the throw must read none of them
EXPLOSION_WRITES = ("doVisualEffects", "screenShakeFactor", "preExplosionSpawnSingleThingDef")
TEST_SOURCE = re.compile(r"^RM_Knockback(Proof\w*|Scenes|Verdicts)\.cs$|^RM_PatchApplierProbe\.cs$")
SHOW_FILES = ("RM_KnockbackShow.cs", "RM_KnockbackShowPlan.cs")
THROW_API = re.compile(r"\b(KbPlanner|KbSettings|KbRules|KbPlan|RM_MapComponent_Knockback|RM_ThingFlyer_Knockback|PawnFlyer\w*|"
                       r"%s\.(Kernel|Rules)\()" % SETTINGS)


def look(part, r):
    """-> the part's look on one row: its own fields, then each vanilla look kept or not."""
    return tuple(r[f] for f in OWN[part]) + tuple(fn(r) for _, fn in VANILLA.get(part, []))


def unmodded(part):
    """The unmodded game's look of a part: nothing of ours, every vanilla look kept (bar: "as in the unmodded game")."""
    return tuple("0" for _ in OWN[part]) + tuple(True for _ in VANILLA.get(part, []))


def nocomment(code):
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    return re.sub(r"//[^\n]*", "", code)


def body(code, head_re):
    m = re.search(head_re + r"(.*?)\n        \}", code, re.S)
    return m.group(1) if m else None


def read_switches(show_src):
    """RM_KnockbackShow.Switches() -> {KbShowSwitches field: ("setting", name) | ("literal", text)}, or None."""
    b = body(show_src, r"public static KbShowSwitches Switches\(\)")
    if b is None:
        return None
    out = {}
    for f, e in re.findall(r"^\s*(\w+)\s*=\s*([^,\n]+),", nocomment(b), re.M):
        e = e.strip()
        m = re.fullmatch(SETTINGS + r"\.(\w+)", e)
        out[f] = ("setting", m.group(1)) if m else ("literal", e)
    return out


def setting_defaults(mod):
    """Every declared setting -> (type, default literal) from RM_KnockbackMod.cs."""
    return {n: (t, v.strip()) for t, n, v in re.findall(r"public static (bool|float|int) (\w+)\s*=\s*([^;]+);", mod)}


def value_of(t, lit):
    if t == "bool":
        return "1" if lit == "true" else "0"
    return lit.rstrip("f")


def scenario_arg(name, mapping, settings):
    """-> "name:field=value,..." for SweepDump, every KbShowSwitches field as Switches() would hand it."""
    kv = []
    for f, (how, what) in mapping.items():
        if how == "setting":
            kv.append("%s=%s" % (f, settings[what]))
        elif what in ("true", "false"):
            kv.append("%s=%s" % (f, "1" if what == "true" else "0"))
        else:
            kv.append("%s=%s" % (f, what.rstrip("f")))
    return "%s:%s" % (name, ",".join(kv))


def show_static(mod, src):
    """The throw is the same with the show on or off, read from source -> list of faults (empty: clean)."""
    faults = []
    show_names = sorted(n for n in setting_defaults(mod) if n.startswith("show"))
    if not show_names:
        faults.append("no show setting is declared in RM_KnockbackMod.cs (the blast show's switches are missing)")
    ms = re.search(r"public struct KbShowSwitches\s*\{(.*?)\n    \}", src.get("RM_KnockbackShowPlan.cs", ""), re.S)
    sw_fields = [n for decl in re.findall(r"public (?:bool|float|int) ([^;=]+);", nocomment(ms.group(1)))
                 for n in re.findall(r"\w+", decl)] if ms else []
    if not sw_fields:
        faults.append("cannot read the struct KbShowSwitches' fields in RM_KnockbackShowPlan.cs")
    vocab = re.compile(r"\b(%s|KbShow\w*|RM_KnockbackShow\w*)\b" % "|".join(show_names or ["showNONE"]))
    # Kernel() and Rules(): the only settings the throw reads, and the classes they fill
    for head in (r"public static KbSettings Kernel\(int ownCap = 0\)", r"public static KbRules Rules\(\)"):
        b = body(mod, head)
        if b is None:
            faults.append("cannot find %s in RM_KnockbackMod.cs to read" % head.split("public static ")[1])
        elif vocab.search(nocomment(b)):
            faults.append("%s carries a show setting: %s" % (head.split(" ")[3], vocab.search(nocomment(b)).group(0)))
    for f, cls in (("RM_KnockbackMath.cs", "KbSettings"), ("RM_KnockbackPlan.cs", "KbRules")):
        m = re.search(r"public sealed class %s\b(.*?)\n    \}" % cls, src.get(f, ""), re.S)
        if not m:
            faults.append("cannot find class %s in %s to read" % (cls, f))
            continue
        bad = [x for x in re.findall(r"public \w+ (\w+)", nocomment(m.group(1)))
               if x.lower().startswith("show") or x in sw_fields]
        if bad:
            faults.append("%s (%s) carries a show field: %s" % (cls, f, ",".join(bad)))
    dec = body(src.get("RM_KnockbackPlan.cs", ""), r"public static KbPlan Decide\(")
    if dec is None:
        faults.append("cannot find KbPlanner.Decide in RM_KnockbackPlan.cs to read")
    elif vocab.search(nocomment(dec)) or re.search(r"\b(%s)\b" % "|".join(EXPLOSION_WRITES), nocomment(dec)):
        faults.append("KbPlanner.Decide reads the show")
    # every throw file: no show setting, no show type, none of the three Explosion fields the show writes
    for f, code in src.items():
        if f in SHOW_FILES or f == "RM_KnockbackMod.cs" or TEST_SOURCE.match(f):
            continue
        c = nocomment(code)
        hit = vocab.search(c) or re.search(r"\b(%s)\b" % "|".join(EXPLOSION_WRITES), c)
        if hit:
            faults.append("throw file %s reads the show: %s" % (f, hit.group(0)))
    # the mod file names a show setting only where a setting lives: declared, saved, drawn, reset
    rest = nocomment(mod)
    for cut in (r"public override void ExposeData\(\)", r"public static void Reset\(\)"):
        b = body(rest, cut)
        if b is not None:
            rest = rest.replace(b, "")
    w0 = rest.find("public void DoWindowContents")
    w1 = rest.find("public static void ResetFields", w0)
    if w0 >= 0 and w1 > w0:
        rest = rest[:w0] + rest[w1:]
    rest = re.sub(r"public static (bool|float|int) show\w+\s*=[^;]+;", "", rest)
    if vocab.search(rest):
        faults.append("RM_KnockbackMod.cs reads a show setting outside its declaration, saving, drawing and reset: %s"
                      % vocab.search(rest).group(0))
    # the show side: reads settings only in Switches() (and the scar's lifetime in LayScar), writes only the three
    # Explosion fields, and calls no throw code
    sh = nocomment(src.get("RM_KnockbackShow.cs", ""))
    sw = body(sh, r"public static KbShowSwitches Switches\(\)") or ""
    reads = [n for n in re.findall(SETTINGS + r"\.(\w+)", sh.replace(sw, ""))]
    if [n for n in reads if n != "showMarksLast"]:
        faults.append("RM_KnockbackShow.cs reads settings outside Switches(): %s" % ",".join(sorted(set(reads) - {"showMarksLast"})))
    for f in SHOW_FILES:
        c = nocomment(src.get(f, ""))
        if THROW_API.search(c):
            faults.append("%s calls throw code: %s" % (f, THROW_API.search(c).group(0)))
    writes = set(re.findall(r"\b(?:__instance|e)\.(\w+)\s*=(?!=)", sh))
    if writes - set(EXPLOSION_WRITES):
        faults.append("the show writes Explosion fields beyond its three: %s" % ",".join(sorted(writes - set(EXPLOSION_WRITES))))
    return faults


def show_kernel(args):
    """Build Source/SelfTestShow on its own stage and run --sweep-dump -> (dump lines, error text)."""
    dotnet = next((d for d in blast_show.DOTNET if os.path.isfile(d)), None)
    if dotnet is None or not os.path.isdir(os.path.dirname(SHOW_STAGE)):
        return None, "UNMEASURED: no Windows dotnet.exe or D: staging root on this machine"
    from winbuild import run_interop_captured  # WSL lost-launch retry
    dump = os.path.join(SHOW_STAGE, "sweep_dump.tsv")
    with open(os.path.join("/tmp", "explosiveknockback_showsweep.lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        for d in ("obj", "bin"):    # a retained output can look newer than a fresh source: build clean
            shutil.rmtree(os.path.join(SHOW_STAGE, "SelfTestShow", d), ignore_errors=True)
        os.makedirs(os.path.join(SHOW_STAGE, "SelfTestShow"), exist_ok=True)
        if os.path.exists(dump):
            os.remove(dump)
        for f in blast_show.SHIPPED:   # shutil.copy, never copy2: a fresh mtime makes dotnet rebuild
            shutil.copy(os.path.join(SRC, f), os.path.join(SHOW_STAGE, f))
        for f in ("Program.cs", "RimMandrakeExplosiveKnockback.ShowSelfTest.csproj"):
            shutil.copy(os.path.join(SRC, "SelfTestShow", f), os.path.join(SHOW_STAGE, "SelfTestShow", f))
        r = run_interop_captured([dotnet, "run", "--project", blast_show.win(os.path.join(SHOW_STAGE, "SelfTestShow",
                                  "RimMandrakeExplosiveKnockback.ShowSelfTest.csproj")), "-c", "Release", "--",
                                  "--sweep-dump", blast_show.win(dump)] + args,
                                 capture_output=True, text=True, stdin=subprocess.DEVNULL)
        out = (r.stdout or "") + (r.stderr or "")
        if r.returncode != 0 or not os.path.isfile(dump):
            return None, "exit %d: %s" % (r.returncode, " / ".join(out.strip().splitlines()[-6:]))
        return open(dump, encoding="utf-8").read().replace("\r", "").splitlines(), None


def show_half():
    """T_SETTINGS_SWEEP_SHOW -> (ok, summary line)."""
    rows_out = []

    def check(ok, ident, what, worst, limit, cases):
        rows_out.append(ok)
        print("%s %s %s: worst %s, limit %s, %s cases" % ("PASS" if ok else "FAIL", ident, what, worst, limit, cases))

    mod = open(MOD, encoding="utf-8").read()
    src = {f: open(os.path.join(SRC, f), encoding="utf-8").read() for f in sorted(os.listdir(SRC)) if f.endswith(".cs")}
    defaults = setting_defaults(mod)
    mapping = read_switches(src.get("RM_KnockbackShow.cs", ""))
    if not mapping:
        print("FAIL S_SWITCHES cannot read RM_KnockbackShow.Switches()")
        return False, "explosive knockback settings sweep show: FAIL (Switches() unreadable)"
    # C6: every part of the design's set has its own switch: a real setting (declared on, saved, drawn, reset) that
    # Switches() hands its part. A part with none fails by name; smoke and soot are unbuilt (no switch is faked here).
    built, unbuilt = [], []
    for part, (switch, _, _) in blast_show.PARTS.items():
        field = PART_FIELD.get(part)
        ok, why = blast_show.setting_ok(src, switch)
        handed = mapping.get(field)
        if ok and handed == ("setting", switch):
            built.append(part)
            continue
        unbuilt.append(part)
        miss = (["switch %s not %s" % (switch, ", ".join(why))] if not ok else []) + \
               (["Switches() hands the plan %s = %s, not the setting" % (field, handed[1] if handed else "nothing")]
                if handed != ("setting", switch) else [])
        print("FAIL S_PART_SWITCH %s has no switch of its own (%s)%s" % (part, "; ".join(miss),
              "; the part is unbuilt in 0.2.0 (its draw is a later batch), so the sweep cannot read it" if handed and handed[0] == "literal" else ""))
    print("%s S_PARTS_SWITCHED %d/%d of design §4's parts have their own switch: worst %d unswitched, limit 0, %d parts"
          % ("PASS" if not unbuilt else "FAIL", len(built), len(blast_show.PARTS), len(unbuilt), len(blast_show.PARTS)))
    rows_out.append(not unbuilt)
    # the scenarios: the player's settings, through Switches(), into the plan
    base = {n: value_of(t, v) for n, (t, v) in defaults.items()}
    show_bools = [n for n, (t, _) in defaults.items() if n.startswith("show") and t == "bool" and ("setting", n) in mapping.values()]
    unknown = [what for how, what in mapping.values() if how == "setting" and what not in base]
    if unknown:
        print("FAIL S_SWITCHES Switches() reads settings the mod does not declare: %s" % ",".join(unknown))
        rows_out.append(False)
    field_of = {what: f for f, (how, what) in mapping.items() if how == "setting"}
    part_of_field = {v: k for k, v in PART_FIELD.items()}
    scen = {"default": dict(base), "all_off": dict(base, **{n: "0" for n in show_bools})}
    for n in show_bools:
        scen["off_" + n] = dict(base, **{n: "0"})
    shake_slider = next((what for f, (how, what) in mapping.items() if f == "shakeStrength" and how == "setting"), None)
    if shake_slider:
        scen["slider0"] = dict(base, **{shake_slider: "0"})
        scen["slider2"] = dict(base, **{shake_slider: "2"})
    args = [scenario_arg(k, mapping, v) for k, v in scen.items()]
    # planted map faults (in memory, run in the same dump): each must go red below
    pl = {}
    if "showFireAndFlash" in show_bools and "airRipple" in mapping:
        crossed = dict(mapping, airRipple=("setting", "showFireAndFlash"))
        args.append(scenario_arg("plant_crossed", crossed, scen["off_showFireAndFlash"]))
        pl["plant_crossed"] = ("off_showFireAndFlash", "air ripple wired to the fire switch")
    if "showCraterScars" in show_bools and "craterScars" in mapping:
        dead = dict(mapping, craterScars=("literal", "true"))
        args.append(scenario_arg("plant_dead", dead, scen["off_showCraterScars"]))
        pl["plant_dead"] = ("off_showCraterScars", "crater switch read nowhere (always on)")
    lines, err = show_kernel(args)
    if lines is None:
        print("FAIL S_SHOW_KERNEL the show kernel builds and dumps the sweep: %s" % err)
        return False, "explosive knockback settings sweep show: FAIL (%s)" % ("UNMEASURED" if err.startswith("UNMEASURED") else "no dump")
    fields = lines[0].split(" ", 1)[1].split(",")
    data, sets, bad = {}, {}, [l for l in lines if l.startswith("BADFIELD")]
    nsw = len(lines[1].split(" ", 1)[1].split(","))
    for l in lines[2:]:
        if l.startswith("SCENARIO "):
            sets[l.split()[1]] = int(l.split("set=")[1])
        elif "\t" in l:
            c = l.split("\t")
            data.setdefault(c[0], {})[c[1]] = dict(zip(fields, c[2:]))
    end = lines[-1] if lines and lines[-1].startswith("END rows=") else "no END"
    total = sum(len(v) for v in data.values())
    check(not bad and all(v == nsw for v in sets.values()) and end == "END rows=%d" % total and len(data) == len(args),
          "S_DUMP", "every scenario hands the plan all %d switch fields and every row came back" % nsw,
          "%d bad fields, %d scenarios short" % (len(bad), sum(1 for v in sets.values() if v != nsw)), "0", total)
    owned = set(f for fs in OWN.values() for f in fs) | set(HANDOVER) | set(NOT_PARTS)
    loose = [f for f in fields if f not in owned]
    check(not loose, "S_FIELDS", "every field of the plan belongs to a part (or is the measure)", ",".join(loose) or "none", "none", len(fields))
    D = data.get("default", {})
    keys = sorted(D)

    def judge(name, off_part, slider=None):
        """-> (own-part failures, other-part failures, own part differs from default count, first failure)"""
        S = data.get(name, {})
        own_bad = other_bad = live = 0
        first = "-"
        for k in keys:
            r, d = S.get(k), D[k]
            if r is None:
                own_bad += 1
                continue
            for part in OWN:
                if part == off_part:
                    if slider is None and look(part, r) != unmodded(part):
                        own_bad += 1
                        first = first if first != "-" else "%s %s %s" % (k, part, look(part, r))
                    if slider == "0" and r["shakeMag"] != "0":
                        own_bad += 1
                        first = first if first != "-" else "%s shakeMag %s" % (k, r["shakeMag"])
                    live += look(part, r) != look(part, d)
                elif look(part, r) != look(part, d):
                    other_bad += 1
                    first = first if first != "-" else "%s %s %s vs default %s" % (k, part, look(part, r), look(part, d))
        return own_bad, other_bad, live, first

    for n in show_bools:
        part = part_of_field.get(field_of.get(n))
        own_bad, other_bad, live, first = judge("off_" + n, part)
        check(own_bad == 0, "S_OFF_OWN[%s]" % n, "%s off gives its part (%s) the unmodded look" % (n, part), own_bad, 0, len(keys))
        check(other_bad == 0, "S_OFF_ONLY[%s]" % n, "%s off leaves every other part as at default" % n, other_bad, 0,
              len(keys) * (len(OWN) - 1))
        check(live >= 1, "S_LIVE[%s]" % n, "%s off changes its part in some blast (the switch is live)" % n, live, ">= 1", len(keys))
        if own_bad or other_bad:
            print("  first: %s" % first)
    if shake_slider:
        for v in ("0", "2"):
            own_bad, other_bad, live, first = judge("slider" + v, "screen_shake", slider=v)
            check(own_bad == 0 and other_bad == 0 and live >= 1, "S_SLIDER[%s=%s]" % (shake_slider, v),
                  "the shake strength changes only the shake (0 = none)", "%d own, %d other" % (own_bad, other_bad), "0", len(keys))
    # all off: every part unmodded, and the plan touches nothing of vanilla's
    A = data.get("all_off", {})
    worst, first = 0, "-"
    for k in keys:
        r = A.get(k)
        bads = [p for p in OWN if r is None or look(p, r) != unmodded(p)] + [h for h in HANDOVER if r is not None and r[h] != "0"]
        if bads:
            worst += 1
            first = first if first != "-" else "%s %s" % (k, ",".join(bads))
    check(worst == 0, "S_ALL_OFF", "every switch off: every part as in the unmodded game, nothing of vanilla's stopped or replayed",
          worst, 0, len(keys))
    if worst:
        print("  first: %s" % first)
    # the planted map faults must be caught
    caught = 0
    for name, (as_scen, what) in pl.items():
        part = part_of_field[{"plant_crossed": "fireAndFlash", "plant_dead": "craterScars"}[name]]
        own_bad, other_bad, live, _ = judge(name, part)
        hit = own_bad > 0 or other_bad > 0 or live == 0
        caught += hit
        if not hit:
            print("FAIL S_PLANT planted switch-map fault NOT CAUGHT: %s" % what)
    rows_out.append(caught == len(pl))
    # the throw: the same with the show on or off (static, on the shipped source)
    sf = show_static(mod, src)
    for f in sf:
        print("FAIL S_THROW", f)
    check(not sf, "S_THROW", "the throw reads no show setting, carries no show field, reads none of the show's writes",
          len(sf), 0, len([f for f in src if not TEST_SOURCE.match(f)]))
    st_pl = {
        "Kernel() carries a show switch": (mod.replace("intoPits = throwIntoPits,", "intoPits = throwIntoPits && showFireAndFlash,", 1), src),
        "Decide reads a show setting": (mod, dict(src, **{"RM_KnockbackPlan.cs": re.sub(
            r"(public static KbPlan Decide\([^{]*\{)", r"\1 bool zz = %s.showAirRipple;" % SETTINGS, src["RM_KnockbackPlan.cs"], count=1)})),
        "the throw reads doVisualEffects": (mod, dict(src, **{"RM_Patch_DamageWorker_ExplosionKnockback.cs":
            src["RM_Patch_DamageWorker_ExplosionKnockback.cs"] + "\n// x\nnamespace X { static class W { static bool V(Verse.Explosion e) => e.doVisualEffects; } }\n"})),
        "KbRules gains a show field": (mod, dict(src, **{"RM_KnockbackPlan.cs": re.sub(
            r"(public sealed class KbRules\s*\{)", r"\1 public bool showScreenShake;", src["RM_KnockbackPlan.cs"], count=1)})),
        "the show calls the throw plan": (mod, dict(src, **{"RM_KnockbackShow.cs": src["RM_KnockbackShow.cs"] + "\n// KbPlanner\nclass Q { object q = KbPlanner.Decide; }\n"})),
    }
    st_missed = [k for k, (m, s2) in st_pl.items() if (m == mod and s2 == src) or not show_static(m, s2)]
    for k in st_missed:
        print("FAIL S_PLANT planted throw fault NOT CAUGHT:", k)
    rows_out.append(not st_missed)
    fails = sum(1 for x in rows_out if not x)
    ok = fails == 0
    summary = ("explosive knockback settings sweep show: %s (%d scenarios x %d blasts = %d rows; %d/%d checks failing; parts with "
               "their own switch %d/%d, unbuilt: %s; %d/%d planted map faults caught, %d/%d planted throw faults caught)"
               % ("PASS" if ok else "FAIL", len(scen), len(keys), total, fails, len(rows_out), len(built), len(blast_show.PARTS),
                  ",".join(unbuilt) or "none", caught, len(pl), len(st_pl) - len(st_missed), len(st_pl)))
    return ok, summary


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    half = argv[argv.index("--half") + 1] if "--half" in argv else "both"
    results = []
    if half in ("both", "offline"):
        ok, line_ = offline_half()
        results.append(("offline", ok, line_))
    if half in ("both", "show"):
        ok, line_ = show_half()
        results.append(("show", ok, line_))
    if not results:
        print("FAIL --half takes offline, show or both, not %r" % half)
        return 2
    show_line = next((l for h, _, l in results if h == "show"), "explosive knockback settings sweep show: not run (--half offline)")
    verdicts = ", ".join("%s %s" % (h, "PASS" if ok else "FAIL") for h, ok, _ in results)
    print("%s | halves: %s" % (show_line if half != "offline" else results[0][2], verdicts))
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())
