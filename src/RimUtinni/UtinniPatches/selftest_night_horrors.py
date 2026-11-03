#!/usr/bin/env python3
"""HORRORS_RAIDING_FACTION_1: offline proof of the Assailant horrors as a nightside RAIDING faction.

Owner ruled 2026-09-09 that the reach is nightside/cold ("a threat you walk toward, not one that finds you"). What this
file can prove without the game, each as one numbered check:
  1. FactionDef RUT_Horrors cannot hold ground: hidden, not humanlike, never made at world start, no settlement weight,
     permanent enemy, and a raidCommonalityFromPointsCurve that is zero everywhere (vanilla RaidEnemy weighs factions by
     it, so a zero curve keeps every generic raid off it, exactly as vanilla keeps it off Insect).
  2. Every pawnGroupMaker option and every crysalis pawnKind names a PawnKindDef that exists in src/, with a race.
  3. RUT_HorrorRaid's worker, the lair GenStep and the crysalis comp are classes in RUT_NightHorrors.cs, compiled by the
     csproj, and every Horror act is gated: CanFireNowSub, TryExecuteWorker and Generate all ask MapInReach, and
     MapInReach is the WeatherSuite nightside band, nothing else.
  4. The lair GenStep is registered on Base_Player and Encounter, and nowhere else.
  5. Every texPath in the two def files resolves: ours to a PNG under this mod's Textures (all three facings for a pawn
     graphic), vanilla ones to a texPath vanilla's own defs use.
  6. Both settings exist, are scribed and are drawn.
  7. The committed DLL's .srchash covers RUT_NightHorrors.cs and dll_source_stamp.py check (committed blobs) reads MATCH
     for the UtinniPatches DLL: meaningful only on a committed tree, which is where the blind checker runs it.
  8. The canonical world save holds no Horrors faction at all (so no settlement of one); positive control: it does hold
     Insect and Mechanoid, so the reader can see factions.
  9. The sinkhole is the dungeon door into the cave network: RUT_HorrorSinkhole is a MapPortal whose pocketMapGenerator
     RUT_HorrorTunnels is an underground Core cave map (biome Underground, UndergroundCave mutator, every genStep resolves,
     PlaceCaveExit before the nests, Fog), colder than every crysalis's thaw line; its nest GenStep holds hives,
     crysalises and larders and no further sinkhole, and is gated on the pocket map's SOURCE map being in reach; the
     first lair on a surface map always tries for a door; the live probe RUT_HorrorSinkholeProbe.Descend exists.
 10. No load-time Config error the 2026-11-03 live A1 read (Player.log lines 250/257/258): no PawnKindDef of ours sets
     weaponMoney without weaponTags, and no ThingDef of ours with useHitPoints false is flammable (Flammability > 0).
Exit 0 = all pass. Offline, no game."""
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

MOD = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(MOD, "..", "..", ".."))
DEFS = os.path.join(MOD, "Defs", "Misc", "RUT_NightHorrors.xml")
RACES = os.path.join(MOD, "Defs", "ThingDefs_Races", "RUT_NightHorrors_Races.xml")
VISCERAL = os.path.join(MOD, "Defs", "ThingDefs_Races", "RM_Visceral.xml")
CS = os.path.join(MOD, "Source", "RUT_NightHorrors.cs")
CSPROJ = os.path.join(MOD, "Source", "RimMandrake.Utinni.UtinniPatches.csproj")
SETTINGS = os.path.join(MOD, "Source", "UtinniPatchesSettings.cs")
REGISTER = os.path.join(MOD, "Patches", "RUT_NightHorrorLairs_Register.xml")
TEX = os.path.join(MOD, "Textures")
SAVE = os.path.join(REPO, "world", "ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws")
VANILLA_DATA = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"

fails = []


def check(n, ok, what):
    print(("PASS" if ok else "FAIL") + " %d %s" % (n, what))
    if not ok:
        fails.append(n)


def text(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


defs = ET.parse(DEFS).getroot()
races = ET.parse(RACES).getroot()
cs = text(CS)

# 1 faction shape
fd = [f for f in defs.iter("FactionDef") if f.findtext("defName") == "RUT_Horrors"]
check(1, len(fd) == 1, "one FactionDef RUT_Horrors")
f = fd[0] if fd else ET.Element("x")
curve = [li.text for li in f.findall("raidCommonalityFromPointsCurve/points/li")]
zero = bool(curve) and all(float(c.strip("() ").split(",")[1]) == 0 for c in curve)
shape = {
    "hidden": f.findtext("hidden") == "true",
    "humanlikeFaction=false": f.findtext("humanlikeFaction") == "false",
    "permanentEnemy": f.findtext("permanentEnemy") == "true",
    "requiredCountAtGameStart=0": f.findtext("requiredCountAtGameStart") == "0",
    "no settlementGenerationWeight>0": float(f.findtext("settlementGenerationWeight") or 0) == 0,
    "canMakeRandomly not true": f.findtext("canMakeRandomly") != "true",
    "zero raid curve": zero,
}
check(1, all(shape.values()), "faction cannot hold ground or be picked by RaidEnemy: %s" % {k: v for k, v in shape.items() if not v})

# 2 kinds resolve
kinds = {}
for p in (RACES, VISCERAL):
    for k in ET.parse(p).getroot().iter("PawnKindDef"):
        kinds[k.findtext("defName")] = k.findtext("race")
race_names = {t.findtext("defName") for p in (RACES, VISCERAL) for t in ET.parse(p).getroot().iter("ThingDef")}
opts = [o.tag for g in f.findall("pawnGroupMakers/li") for o in (g.find("options") if g.find("options") is not None else [])]
cry = [c.findtext("comps/li/pawnKind") for c in defs.iter("ThingDef") if c.find("comps/li/pawnKind") is not None]
missing = [k for k in opts + cry if k not in kinds or kinds[k] not in race_names]
check(2, bool(opts) and bool(cry) and not missing, "%d group options + %d crysalis kinds resolve to kinds with races (missing %s)" % (len(opts), len(cry), missing))

# 3 classes exist, compiled, gated
classes = set(re.findall(r"public class (\w+)", cs))
named = [x.split(".")[-1] for x in re.findall(r'(?:Class="|<workerClass>)(RimMandrake\.Utinni\.UtinniPatches\.\w+)', text(DEFS))]
check(3, bool(named) and all(n in classes for n in named), "def-named classes in RUT_NightHorrors.cs: %s" % sorted(set(named)))
check(3, '<Compile Include="RUT_NightHorrors.cs" />' in text(CSPROJ), "csproj compiles RUT_NightHorrors.cs")


def body(sig):
    i = cs.find(sig)
    if i < 0:
        return ""
    j = cs.find("{", i)
    depth, k = 0, j
    while k < len(cs):
        depth += cs[k] == "{"
        depth -= cs[k] == "}"
        if depth == 0:
            return cs[j:k + 1]
        k += 1
    return ""


gates = {
    "CanFireNowSub": "MapInReach(" in body("protected override bool CanFireNowSub"),
    "TryExecuteWorker": "MapInReach(" in body("protected override bool TryExecuteWorker"),
    "GenStep.Generate": "if (!InReach(map)) return;" in body("public override void Generate"),
    "lair InReach=MapInReach": "RUT_HorrorFaction.MapInReach(map," in body("protected virtual bool InReach"),
    "tunnel InReach=source map in reach": "map?.Parent is PocketMapParent pocket && RUT_HorrorFaction.MapInReach(pocket.sourceMap,"
                                          in body("protected override bool InReach"),
    "MapInReach=nightside band": "WeatherGeometryUtility.MapInNightsideBand(map)" in body("public static bool MapInReach"),
    "InReach=enabled&&nightside": "return enabled && nightside;" in body("public static bool InReach"),
}
check(3, all(gates.values()), "every Horror act asks the nightside reach: %s" % {k: v for k, v in gates.items() if not v})

# 4 registration
reg = ET.parse(REGISTER).getroot()
targets = sorted(re.findall(r'defName="(\w+)"', "".join(o.findtext("xpath") for o in reg.iter("Operation"))))
adds = [li.text for li in reg.iter("li")]
check(4, targets == ["Base_Player", "Encounter"] and adds == ["RUT_NightHorrorLairs"] * 2, "GenStep on %s, adds %s" % (targets, adds))

# 5 textures
vanilla_tex = set()
if os.path.isdir(VANILLA_DATA):
    for r, _, fs in os.walk(VANILLA_DATA):
        if os.sep + "Defs" in r:
            for fn in fs:
                if fn.endswith(".xml"):
                    vanilla_tex.update(re.findall(r"<(?:texPath|factionIconPath|settlementTexturePath)>([^<]+)<", text(os.path.join(r, fn))))
bad = []
paths = []
for root_ in (defs, races):
    for e in root_.iter():
        if e.tag in ("texPath", "factionIconPath", "settlementTexturePath"):
            paths.append((e.tag, e.text.strip(), root_ is races))
for tag, p, pawn in paths:
    if p.startswith("RimUtinni/"):
        need = [p + "_%s.png" % s for s in ("north", "east", "south")] if pawn else [p + ".png"]
        if not all(os.path.isfile(os.path.join(TEX, *n.split("/"))) for n in need):
            bad.append(p)
    elif p not in vanilla_tex:
        bad.append(p)
check(5, bool(vanilla_tex) and len(paths) > 20 and not bad, "%d texture paths resolve (bad %s)" % (len(paths), bad))

# 6 settings
st = text(SETTINGS)
sets = all(("public static bool %s = true;" % s) in st and ('Scribe_Values.Look(ref %s, "%s", true);' % (s, s)) in st and ("ref %s," % s) in st
           for s in ("nightHorrorRaidsEnabled", "nightHorrorLairsEnabled"))
check(6, sets, "both Mod Settings declared, scribed and drawn")

# 7 DLL stamp
r = subprocess.run([sys.executable, os.path.join(REPO, "src", "RimMandrake", "Utils", "dll_source_stamp.py"), "check"],
                   cwd=REPO, capture_output=True, text=True, timeout=300)
stamp = os.path.join(MOD, "Assemblies", "RimMandrake.Utinni.UtinniPatches.dll.srchash")
covered = os.path.isfile(stamp) and "RUT_NightHorrors.cs" in text(stamp)
ours = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.endswith("/RimMandrake.Utinni.UtinniPatches.dll")]
check(7, covered and ours == ["MATCH src/RimUtinni/UtinniPatches/Assemblies/RimMandrake.Utinni.UtinniPatches.dll"],
      "UtinniPatches .srchash lists RUT_NightHorrors.cs and dll_source_stamp (committed blobs) reads %s" % ours)

# 8 canonical save
with open(SAVE, "rb") as fh:
    b = fh.read()
i, j = b.find(b"<factionManager>"), b.find(b"</factionManager>")
fdefs = [li.findtext("def") for li in ET.fromstring(b[i:j + len(b"</factionManager>")]).find("allFactions")] if i >= 0 < j else []
check(8, {"Insect", "Mechanoid"} <= set(fdefs) and not {"RUT_Horrors", "Horrors"} & set(fdefs),
      "canonical save: %d factions read (control Insect+Mechanoid present), no Horrors faction, so 0 Horror settlements" % len(fdefs))

# 9 the sinkhole door into the tunnels
core_defs = {}
core = os.path.join(VANILLA_DATA, "Core", "Defs")
if os.path.isdir(core):
    for r_, _, fs in os.walk(core):
        for fn in fs:
            if fn.endswith(".xml"):
                try:
                    for d in ET.parse(os.path.join(r_, fn)).getroot():
                        if d.findtext("defName"):
                            core_defs.setdefault(d.tag, set()).add(d.findtext("defName"))
                except ET.ParseError:
                    pass
ours = {}
for d in defs:
    if d.findtext("defName"):
        ours.setdefault(d.tag, {})[d.findtext("defName")] = d
hole = ours.get("ThingDef", {}).get("RUT_HorrorSinkhole", ET.Element("x"))
gen = ours.get("MapGeneratorDef", {}).get(hole.findtext("portal/pocketMapGenerator") or "", ET.Element("x"))
nests = ours.get("GenStepDef", {}).get("RUT_HorrorTunnelNests", ET.Element("x"))
steps = [li.text for li in gen.findall("genSteps/li")]
gsdefs = core_defs.get("GenStepDef", set()) | set(ours.get("GenStepDef", {}))
thaw = [float(c.findtext("comps/li/thawTemperature") or 0) for c in defs.iter("ThingDef") if c.find("comps/li/pawnKind") is not None]
ng = nests.find("genStep") if nests.find("genStep") is not None else ET.Element("x")
door = {
    "sinkhole thingClass MapPortal": hole.findtext("thingClass") == "MapPortal",
    "generator RUT_HorrorTunnels": hole.findtext("portal/pocketMapGenerator") == "RUT_HorrorTunnels" and gen.findtext("defName") == "RUT_HorrorTunnels",
    "exitDef CaveExit in Core": hole.findtext("portal/exitDef") == "CaveExit" and "CaveExit" in core_defs.get("ThingDef", set()),
    "portal ITab": "ITab_ContentsMapPortal" in [li.text for li in hole.findall("inspectorTabs/li")],
    "isUnderground": gen.findtext("isUnderground") == "true",
    "biome Underground in Core": gen.findtext("pocketMapProperties/biome") == "Underground" and "Underground" in core_defs.get("BiomeDef", set()),
    "UndergroundCave mutator": [li.text for li in gen.findall("pocketMapProperties/tileMutators/li")] == ["UndergroundCave"]
                              and "UndergroundCave" in core_defs.get("TileMutatorDef", set()),
    "every genStep resolves": bool(steps) and all(x in gsdefs for x in steps),
    "PlaceCaveExit, nests, Fog": all(x in steps for x in ("PlaceCaveExit", "RUT_HorrorTunnelNests", "Fog")),
    "nests after the exit (order > 400)": float(nests.findtext("order") or 0) > 400,
    "colder than every thaw line": bool(thaw) and float(gen.findtext("pocketMapProperties/temperature") or 99) < min(thaw),
    "nest class": ng.get("Class") == "RimMandrake.Utinni.UtinniPatches.RUT_GenStep_HorrorTunnelNests"
                  and "public class RUT_GenStep_HorrorTunnelNests : RUT_GenStep_NightHorrorLairs" in cs,
    "nests hold hive, crysalises, larder, no sinkhole": bool(ng.findtext("hive")) and bool(ng.findtext("larder"))
                  and len(ng.findall("crysalises/li")) > 0 and ng.find("sinkhole") is None,
    "first lair tries for a door": "(!doorPlaced || Rand.Chance(0.5f))" in body("private bool BuildLair") and "doorPlaced = false;" in body("public override void Generate"),
    "probe Descend": "public static string Descend(string arg)" in cs and "portal.GetOtherMap()" in body("public static string Descend"),
}
check(9, len(core_defs.get("GenStepDef", ())) > 20 and all(door.values()),
      "sinkhole is a working door to RUT_HorrorTunnels (%d genSteps): %s" % (len(steps), {k: v for k, v in door.items() if not v}))

# 10 load-time Config errors the engine logs (seen live 2026-11-03)
allk = [k for p in (RACES, VISCERAL) for k in ET.parse(p).getroot().iter("PawnKindDef")]
money = [k.findtext("defName") for k in allk if k.find("weaponMoney") is not None and k.find("weaponTags") is None]
check(10, bool(allk) and not money, "%d pawnkinds, none with weaponMoney but no weaponTags (offenders %s)" % (len(allk), money))
abstract = {d.get("Name"): d for d in defs.iter("ThingDef") if d.get("Name")}


def flam(d):
    while d is not None:
        v = d.findtext("statBases/Flammability")
        if v is not None:
            return float(v)
        d = abstract.get(d.get("ParentName"))
    return None


nohp = [d for d in defs.iter("ThingDef") if d.findtext("useHitPoints") == "false"]
burn = [d.findtext("defName") for d in nohp if flam(d) != 0]
check(10, bool(nohp) and not burn, "%d hit-point-less things, none flammable (offenders %s)" % (len(nohp), burn))

print("RESULT", "PASS" if not fails else "FAIL %s" % sorted(set(fails)))
sys.exit(1 if fails else 0)
