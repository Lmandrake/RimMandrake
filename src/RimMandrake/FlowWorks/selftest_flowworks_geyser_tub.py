#!/usr/bin/env python3
"""RIMMANDRAKE_SINK_GEYSER_INTO_PIT_BUBBLING_HOT_TUB -- a geyser in a pit sinks, bubbles and is a hot pool (offline, no game).

Spec: design/specs/geyser_in_pit_hot_tub_2026-11-12.md section 4.1 O2, with the owner's card answers of 2026-11-12
("Water plus harmless liquids" bathe, each with a cost; a generator caps a dry sunk geyser; vanilla's hot-spring memory).
Reads the shipped defs and the comment-blanked C# and checks:
  1-4  the hediffs, job and joy giver carry Standalone Hot Spring's numbers as our own;
  5    every setting is declared, scribed with its declared default, drawn, and the screen is registered;
  6    no dependency on Standalone Hot Spring (no defName, class or packageId of it under FlowWorks; About.xml unchanged);
  7    the spawn, sprayer and puff patches exist, gated by geyserSinksEnabled; the print shift reaches PrintPlane;
  8    the heat push is never skipped (no PushHeat patch, the sprayer prefix cannot skip the tick);
  9    FluidDef.bathGroup defaults to None; exactly water, tar, oil, blood and the four slimes bathe; the pool gate calls
       RM_GeyserTubMath.PoolSafe with Bathable(fluid);
  10   RM_HotLiquid is not called from the geyser code;
  11   the under-liquid law has a geyser row (GeyserMetres 0.4);
  12   the map component's tick never scans the map (no listerThings / AllThings in it);
  13   each non-water bath has its cost (tar: filth + memory; oil: filth; blood: filth + memory; slime: slip), and every
       def a cost names exists;
  14   the bather never lies down (FlowWorks drowning reads a lying pawn by its lying height);
  15   the generator waiver holds only on a dry sunk geyser and only on the geyser's own squares;
  16   RIMMANDRAKE_RESTRICT_HEAT_TO_GEYSER_BENEATH_PIT_WATER_ONLY: the soak cells and the no-freeze squares are the
       heated water only (HeatedCells: the vent covered, the vent's own liquid, joined to the vent by
       RM_GeyserTubMath.PoolRegion), never a radius alone.
Named MUTANTS of the real text must each turn a check red (can-fail).
NOT proven here: anything in game (spec 4.2 L1-L8: drawing, puffs, plume, the job, hediffs, generator, save/load).
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
DEFS = os.path.join(HERE, "Defs")
SELF = os.path.abspath(__file__)

FILES = {
    "math": os.path.join(SRC, "Superdeep", "RM_GeyserTubMath.cs"),
    "pit": os.path.join(SRC, "Superdeep", "RM_GeyserPit.cs"),
    "settings": os.path.join(SRC, "Superdeep", "RM_GeyserPitSettings.cs"),
    "job": os.path.join(SRC, "Superdeep", "JobDriver_RM_SoakInGeyserPool.cs"),
    "submerge": os.path.join(SRC, "Superdeep", "RM_SubmergeDraw.cs"),
    "fluiddef": os.path.join(SRC, "FluidDef.cs"),
    "mod": os.path.join(SRC, "RimMandrakeFlowWorksMod.cs"),
    "pool_xml": os.path.join(DEFS, "Pits", "GeyserPool", "RM_GeyserPool.xml"),
    "fluids_xml": os.path.join(DEFS, "Canals", "FluidDefs", "FlowWorks_Fluids.xml"),
    "pitfluids_xml": os.path.join(DEFS, "Canals", "FluidDefs", "FlowWorks_PitFluids.xml"),
    "about": os.path.join(HERE, "About", "About.xml"),
}
CS = {"math", "pit", "settings", "job", "submerge", "fluiddef", "mod"}
BATHERS = {"RM_Fluid_Water": "Water", "RM_Fluid_Tar": "Tar", "RM_Fluid_Oil": "Oil", "RM_Fluid_Blood": "Blood",
           "RM_Fluid_SlimeRed": "Slime", "RM_Fluid_SlimeGreen": "Slime", "RM_Fluid_SlimeWhite": "Slime",
           "RM_Fluid_SlimeYellow": "Slime"}
VANILLA_DEFS = {"Filth_Blood"}


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def body_of(src, sig):
    i = src.find(sig)
    if i < 0:
        return ""
    j = src.find("{", i)
    d = 0
    for k in range(j, len(src)):
        d += {"{": 1, "}": -1}.get(src[k], 0)
        if d == 0:
            return src[j:k + 1]
    return ""


def defs_of(xml_text, tag):
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return {}
    return {d.findtext("defName"): d for d in root if d.tag == tag and d.findtext("defName")}


def num(e, path):
    try:
        return float(e.findtext(path))
    except (TypeError, ValueError, AttributeError):
        return None


def stage_ok(h, comfy):
    st = h.find("stages/li")
    if st is None:
        return False
    ok = num(st, "naturalHealingFactor") == 1.25
    ok &= any(li.findtext("capacity") == "BloodFiltration" and num(li, "offset") == 0.08 for li in st.findall("capMods/li"))
    if comfy:
        ok &= num(st, "statOffsets/ComfyTemperatureMin") == -50 and num(st, "statOffsets/ComfyTemperatureMax") == 50
    return ok


def repo_defnames():
    names = set()
    for dp, _dn, fn in os.walk(DEFS):
        for f in fn:
            if f.endswith(".xml"):
                with open(os.path.join(dp, f), encoding="utf-8", errors="replace") as fh:
                    names.update(re.findall(r"<defName>([^<]+)</defName>", fh.read()))
    return names


def checks(t, flowworks_texts, defnames):
    fails = []

    def check(n, ok, why):
        if not ok:
            fails.append("%s: %s" % (n, why))

    hed = defs_of(t["pool_xml"], "HediffDef")
    soak, after = hed.get("RM_HotPoolSoak"), hed.get("RM_HotPoolAfterglow")
    check(1, soak is not None and stage_ok(soak, True), "RM_HotPoolSoak: comfy -50/+50, BloodFiltration +0.08, healing 1.25")
    check(2, after is not None and stage_ok(after, False) and num(after, "maxSeverity") == 0.5
          and any(li.get("Class") == "HediffCompProperties_SeverityPerDay" and num(li, "severityPerDay") == -0.4
                  for li in after.findall("comps/li")), "RM_HotPoolAfterglow: 0.5 falling 0.4/day, same healing")
    job = defs_of(t["pool_xml"], "JobDef").get("RM_SoakInGeyserPool")
    check(3, job is not None and job.findtext("joyKind") == "Meditative" and num(job, "joyDuration") == 4000
          and num(job, "joyMaxParticipants") == 6, "JobDef RM_SoakInGeyserPool: Meditative, 4000, 6")
    joy = defs_of(t["pool_xml"], "JoyGiverDef").get("RM_SoakInGeyserPool")
    check(4, joy is not None and num(joy, "baseChance") == 5 and joy.findtext("joyKind") == "Meditative"
          and (joy.findtext("giverClass") or "").startswith("RimMandrake.FlowWorks."), "JoyGiverDef: baseChance 5, ours")

    s = t["settings"]
    decl = dict(re.findall(r"public static (?:bool|float|int) (\w+) = ([^;]+);", s))
    scribed = dict(re.findall(r'Scribe_Values\.Look\(ref (\w+), "\1", ([^)]+)\);', s))
    want = {"geyserSinksEnabled", "geyserPlumeEnabled", "geyserPlumeDensity", "geyserPoolEnabled", "geyserPoolReach",
            "geyserPoolHealing", "geyserPoolAfterglowEnabled", "geyserPoolMoodEnabled", "geyserPoolMoodFactor",
            "geyserPoolHidesClothes", "geyserBathTarEnabled", "geyserBathOilEnabled", "geyserBathBloodEnabled",
            "geyserBathSlimeEnabled", "geyserBathFilthEnabled", "geyserBathMoodCostEnabled", "geyserBathSlipEnabled",
            "geyserGeneratorOnSunkEnabled"}
    draw = body_of(s, "public static void DoSettingsSection(")
    bad = [k for k in want if k not in decl or scribed.get(k, "").strip() != decl[k].strip() or ("ref " + k) not in draw
           and k not in draw]
    check(5, not bad and "RM_GeyserPitSettings.ExposeData();" in t["mod"]
          and 'Block(list, "Geysers in pits", RM_GeyserPitSettings.DoSettingsSection);' in t["mod"]
          and "RM_SettingsReset.Snapshot(typeof(RM_GeyserPitSettings))" in s and all(decl[k] == "true" for k in want if k.endswith("Enabled")),
          "settings declared/scribed/drawn/registered, switches shipped on: %s" % bad)

    hits = [p for p, txt in flowworks_texts.items() if re.search(r"StandaloneHotSpring|balistafreak|BathStandaloneHotSpring", txt)]
    check(6, not hits and "balistafreak" not in t["about"], "no Standalone Hot Spring names: %s" % hits)

    pit = t["pit"]
    sub = t["submerge"]
    check(7, "[HarmonyPatch(typeof(Building_SteamGeyser), nameof(Building_SteamGeyser.SpawnSetup))]" in pit
          and "[HarmonyPatch(typeof(IntermittentSteamSprayer), nameof(IntermittentSteamSprayer.SteamSprayerTick))]" in pit
          and "[HarmonyPatch(typeof(FleckMaker), nameof(FleckMaker.ThrowAirPuffUp))]" in pit
          and "RM_GeyserPit.On ? RM_GeyserPit.ParentOf(__instance)" in pit
          and "if (!On || g == null" in body_of(pit, "public static float PrintShiftZ(")
          and "ctxShiftZ = t is Building_SteamGeyser geyser ? RM_GeyserPit.PrintShiftZ(geyser)" in sub
          and "RM_SubmergeDraw.Shift(ref center);" in body_of(sub, "private static bool Prefix(MapDrawLayer layer, ref Vector3 center"),
          "spawn/sprayer/puff patches gated by geyserSinksEnabled; the print shift reaches PrintPlane")
    pre = body_of(pit, "private static void Prefix(IntermittentSteamSprayer __instance)")
    check(8, "PushHeat" not in pit and pre != "" and "return false" not in pre,
          "the heat push stays: no PushHeat patch, the sprayer prefix cannot skip the tick")

    fd = t["fluiddef"]
    groups = {}
    for key in ("fluids_xml", "pitfluids_xml"):
        for n, d in defs_of(t[key], "RimMandrake.FlowWorks.FluidDef").items():
            groups[n] = d.findtext("bathGroup") or "None"
    pool = body_of(pit, "public static bool PoolOpen(")
    check(9, "public RM_GeyserTubMath.BathGroup bathGroup = RM_GeyserTubMath.BathGroup.None;" in fd
          and {n: g for n, g in groups.items() if g != "None"} == BATHERS and len(groups) >= 16
          and "RM_GeyserTubMath.PoolSafe(s.fluid != null, Bathable(s.fluid), s.covered, s.capped)" in pool,
          "bath groups: exactly water, tar, oil, blood, four slimes (got %s)" % {n: g for n, g in groups.items() if g != "None"})

    check(10, not any("RM_HotLiquid" in t[k] for k in ("pit", "job", "math", "settings")), "the geyser code never calls RM_HotLiquid")
    check(11, "if (t is Building_SteamGeyser && RM_GeyserPit.On)" in sub and "return RM_GeyserTubMath.GeyserMetres;" in sub
          and re.search(r"public const float GeyserMetres = 0\.4f;", t["math"]) is not None, "the under-liquid law's geyser row, 0.4 m")
    tick = body_of(pit, "public override void MapComponentTick(")
    check(12, tick != "" and not re.search(r"listerThings|AllThings|AllPawns", tick), "no map scan in the tick")

    costs = {}
    for key in ("fluids_xml", "pitfluids_xml"):
        for n, d in defs_of(t[key], "RimMandrake.FlowWorks.FluidDef").items():
            c = d.find("bathCost")
            if c is not None:
                costs[n] = (c.findtext("filth"), int(c.findtext("filthCount") or 0), c.findtext("thought"),
                            int(c.findtext("slipStunTicks") or 0))
    th = defs_of(t["pool_xml"], "ThoughtDef")
    named = {v for c in costs.values() for v in (c[0], c[2]) if v}
    missing = [n for n in named if n not in defnames and n not in VANILLA_DEFS and n not in th]
    ok13 = (costs.get("RM_Fluid_Tar", (None, 0, None, 0))[:3] == ("RM_Filth_Tar", 3, "RM_BathedInTar")
            and costs.get("RM_Fluid_Oil", (None, 0))[1] > 0
            and costs.get("RM_Fluid_Blood", (None, 0, None))[:3] == ("Filth_Blood", 3, "RM_BathedInBlood")
            and all(costs.get(n, (0, 0, 0, 0))[3] > 0 for n, g in BATHERS.items() if g == "Slime")
            and "RM_Fluid_Water" not in costs and not missing
            and all(num(th[n], "stages/li/baseMoodEffect") is not None and num(th[n], "stages/li/baseMoodEffect") < 0
                    for n in ("RM_BathedInTar", "RM_BathedInBlood") if n in th) and len(th) >= 2)
    check(13, ok13, "bath costs per liquid (missing defs: %s)" % missing)
    check(14, "LayingOnGroundFaceUp" not in t["job"] and "posture" not in t["job"], "the bather sits up, never lies down")
    gen = body_of(pit, "private static void Postfix(BuildableDef entDef, IntVec3 c, Map map, Rot4 rot, ThingDef stuffDef, ref bool __result)")
    check(15, "typeof(PlaceWorker_OnSteamGeyser)" in gen and "s.seat <= 0 || s.levelMetres > 0f" in gen
          and "!vent.Contains(q) && (!q.InBounds(map) || (need != null && !q.GetAffordances(map).Contains(need)))" in gen,
          "the generator waiver: dry sunk geysers only, and the geyser's own squares only")
    heat = body_of(pit, "public static List<IntVec3> HeatedCells(")
    soakc = body_of(pit, "public static IEnumerable<IntVec3> SoakCells(")
    warm = body_of(pit, "public bool Warmed(IntVec3 c)")
    check(16, heat != "" and "!s.covered" in heat and "RM_GeyserTubMath.PoolRegion(w, h, water, vent.ToArray())" in heat
          and "FluidOn(map, eng, c) == s.fluid" in heat and "foreach (IntVec3 c in HeatedCells(g, s))" in soakc
          and "InReach" not in soakc and "RM_GeyserPit.HeatedCells(g, RM_GeyserPit.Read(g))" in warm and "set.Contains(c)" in warm
          and "InReach" not in warm,
          "heat only through the water over the vent: soak cells and no-freeze read HeatedCells, never a radius alone")
    return fails


MUTANTS = [
    ("soak healing 1.0", "pool_xml", "<naturalHealingFactor>1.25</naturalHealingFactor>", "<naturalHealingFactor>1.0</naturalHealingFactor>"),
    ("afterglow never fades", "pool_xml", "<severityPerDay>-0.4</severityPerDay>", "<severityPerDay>0</severityPerDay>"),
    ("five bathers", "pool_xml", "<joyMaxParticipants>6</joyMaxParticipants>", "<joyMaxParticipants>5</joyMaxParticipants>"),
    ("joy giver chance 1", "pool_xml", "<baseChance>5</baseChance>", "<baseChance>1</baseChance>"),
    ("a setting not scribed", "settings", 'Scribe_Values.Look(ref geyserBathSlipEnabled, "geyserBathSlipEnabled", true);', ""),
    ("the screen not registered", "mod", 'Block(list, "Geysers in pits", RM_GeyserPitSettings.DoSettingsSection);', ""),
    ("sprayer patch ungated", "pit", "RM_GeyserPit.On ? RM_GeyserPit.ParentOf(__instance)", "true ? RM_GeyserPit.ParentOf(__instance)"),
    ("print shift dropped", "submerge", "RM_SubmergeDraw.Shift(ref center);", ""),
    ("sprayer prefix skips the tick", "pit", "RM_GeyserPit.spraying = RM_GeyserPit.On", "return false; RM_GeyserPit.spraying = RM_GeyserPit.On"),
    ("bathGroup defaults to Water", "fluiddef", "bathGroup = RM_GeyserTubMath.BathGroup.None;", "bathGroup = RM_GeyserTubMath.BathGroup.Water;"),
    ("acid made bathable", "pitfluids_xml", "<defName>RM_Fluid_AcidWater</defName>", "<defName>RM_Fluid_AcidWater</defName><bathGroup>Tar</bathGroup>"),
    ("pool gate ignores bathable", "pit", "Bathable(s.fluid), s.covered", "true, s.covered"),
    ("hot liquid called", "pit", "public static bool Spraying(", "static void X() { RM_HotLiquid.Foo(); } public static bool Spraying("),
    ("geyser row gone", "submerge", "return RM_GeyserTubMath.GeyserMetres;", "return RM_UnderLiquid.MinThingMetres;"),
    ("tick scans the map", "pit", "bool remesh = Find.TickManager.TicksGame % 250 == 0;",
     "bool remesh = Find.TickManager.TicksGame % 250 == 0; map.listerThings.AllThings.Clear();"),
    ("tar bath free", "fluids_xml", "<thought>RM_BathedInTar</thought>", ""),
    ("slime does not slip", "fluids_xml", "<slipStunTicks>120</slipStunTicks>", "<slipStunTicks>0</slipStunTicks>"),
    ("bather lies down", "job", "pawn.pather.StopDead();", "pawn.pather.StopDead(); pawn.jobs.posture = PawnPosture.LayingOnGroundFaceUp;"),
    ("generator allowed wet", "pit", "s.seat <= 0 || s.levelMetres > 0f", "s.seat <= 0"),
    ("generator waiver on the whole footprint", "pit", "!vent.Contains(q) && (", "false && ("),
    ("soak cells by radius alone", "pit", "foreach (IntVec3 c in HeatedCells(g, s))",
     "foreach (IntVec3 c in g.OccupiedRect().ExpandedBy(3)) if (RM_GeyserTubMath.InReach(c.x, c.z, 2.5f))"),
    ("no-freeze by radius alone", "pit", "if (set.Contains(c))", "if (RM_GeyserTubMath.InReach(dx, dz, 2.5f))"),
    ("any water near the vent is the pool", "pit", "bool[] reached = RM_GeyserTubMath.PoolRegion(w, h, water, vent.ToArray());",
     "bool[] reached = water;"),
    ("a dry vent heats", "pit", "s.seat <= 0 || !s.covered || s.capped", "s.seat <= 0 || s.capped"),
    ("a mod name leaks", "job", "public bool soaking;", "public bool soaking; // StandaloneHotSpring\n string n = \"StandaloneHotSpring\";"),
]


def main():
    raw = {}
    for k, p in FILES.items():
        if not os.path.isfile(p):
            print("FAIL missing %s" % p)
            print("FAILED 1")
            return 1
        with open(p, encoding="utf-8") as f:
            raw[k] = f.read()
    t = {k: strip_comments(v) if k in CS else v for k, v in raw.items()}
    fw = {}
    for dp, _dn, fn in os.walk(HERE):
        if os.sep + "obj" in dp or os.sep + "bin" in dp:
            continue
        for f in fn:
            p = os.path.join(dp, f)
            if os.path.abspath(p) != SELF and f.endswith((".cs", ".xml", ".py")):
                with open(p, encoding="utf-8", errors="replace") as fh:
                    fw[p] = fh.read()
    defnames = repo_defnames()
    fails = checks(t, fw, defnames)
    for name, key, a, b in MUTANTS:
        if a not in raw[key]:
            fails.append("CAN-IT-FAIL: mutant '%s' no longer applies (source moved: update the mutant)" % name)
            continue
        m = dict(raw)
        m[key] = raw[key].replace(a, b, 1)
        mt = {k: strip_comments(v) if k in CS else v for k, v in m.items()}
        mfw = dict(fw)
        mfw[FILES[key]] = mt[key] if key == "job" else mfw.get(FILES[key], "")
        if not checks(mt, mfw, defnames):
            fails.append("CAN-IT-FAIL: mutant '%s' passed every check" % name)
    for f in fails:
        print("FAIL", f)
    print("PASS selftest_flowworks_geyser_tub (16 checks, %d mutants red)" % len(MUTANTS) if not fails else "FAILED %d" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
