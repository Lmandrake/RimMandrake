"""validation.py -- modcheck suite for RimMandrake Abyss (mandrake.rm.abyss).

First script for this mod (debug_process.md). Covers ABYSS_ETCHCAP_BUILD_1 and ABYSS_GHARREK_BUILD_1.
Two layers: `static_check()` is offline (parses the shipped XML, runs with plain
`python3 validation.py`); the chain is a live def-resolution read, NEVER RUN YET.
Mod Settings: the Abyss's only control is the worldgen-rarity slider; the etchcap carries no
toggle (it is a def, and gating a def needs C# plus a DLL rebuild -- owed, see the item).
"""
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))


def _defs(rel):
    return ET.parse(os.path.join(HERE, "Defs", rel)).getroot()


def static_check():
    """Returns a list of failure strings; empty means every etchcap link resolves on disk."""
    bad = []
    plant = next((d for d in _defs("ThingDefs_Plants/RM_Etchcap.xml").iter("ThingDef")
                  if d.findtext("defName") == "RM_Etchcap"), None)
    cap = next((d for d in _defs("ThingDefs_Items/RM_EtchcapCap.xml").iter("ThingDef")
                if d.findtext("defName") == "RM_EtchcapCap"), None)
    ter = next((d for d in _defs("TerrainDefs/RM_EtchHollow.xml").iter("TerrainDef")
                if d.findtext("defName") == "RM_EtchHollow"), None)
    if plant is None or cap is None or ter is None:
        return ["missing def: plant=%s cap=%s terrain=%s" % (plant is not None, cap is not None, ter is not None)]
    p = plant.find("plant")
    if p.findtext("harvestedThingDef") != cap.findtext("defName"):
        bad.append("plant does not harvest RM_EtchcapCap")
    # growth restriction: plant minimum above any ordinary ground, met only by the hollow
    fmin = float(p.findtext("fertilityMin"))
    if not (fmin >= 0.8 and float(ter.findtext("fertility")) >= fmin):
        bad.append("fertility gate broken: plant fertilityMin %s vs hollow %s" % (fmin, ter.findtext("fertility")))
    if float(p.findtext("growMinGlow")) != 0:
        bad.append("etchcap must not need light (growMinGlow != 0)")
    if cap.find("ingestible/foodType") is None or cap.find("ingredient") is None:
        bad.append("cap is not a food ingredient")
    # wiring in the biome, shorthand form
    biome = _defs("BiomeDefs/RM_Abyss.xml")
    wp = biome.find(".//wildPlants/RM_Etchcap")
    if wp is None or not float(wp.text) > 0:
        bad.append("RM_Abyss <wildPlants> lacks <RM_Etchcap>commonality</RM_Etchcap>")
    # textures resolve
    for d, ext in ((plant, "Things/Plant/Etchcap"), (cap, "Things/Item/EtchcapCap")):
        tp = d.findtext("graphicData/texPath")
        if tp != "RM_Abyss/" + ext or not os.path.isfile(os.path.join(HERE, "Textures", tp + ".png")):
            bad.append("texture missing for %s: %s" % (d.findtext("defName"), tp))
    if not os.path.isfile(os.path.join(HERE, "Textures", ter.findtext("texturePath") + ".png")):
        bad.append("terrain texture missing")
    return bad


def gharrek_check():
    """Offline: gharrek defs, art, gill-ash, comp wiring, roster row, csproj. Returns failures."""
    bad = []
    root = _defs("ThingDefs_Races/RM_Gharrek.xml")
    thing = next((d for d in root.iter("ThingDef") if d.findtext("defName") == "RM_Gharrek"), None)
    kind = next((d for d in root.iter("PawnKindDef") if d.findtext("defName") == "RM_Gharrek"), None)
    hed = next((d for d in root.iter("HediffDef") if d.findtext("defName") == "RM_GharrekDormant"), None)
    ash = next((d for d in _defs("ThingDefs_Items/RM_GillAsh.xml").iter("ThingDef")
                if d.findtext("defName") == "RM_GillAsh"), None)
    if None in (thing, kind, hed, ash):
        return ["missing def: thing=%s kind=%s hediff=%s ash=%s" % (thing is not None, kind is not None, hed is not None, ash is not None)]
    if kind.findtext("race") != "RM_Gharrek":
        bad.append("PawnKind race != RM_Gharrek")
    if thing.find("statBases/MaxFlightTime") is not None:
        bad.append("gharrek must not fly (spec: crawler)")
    comp = thing.find("comps/li[@Class='RimMandrake.Abyss.CompProperties_Gharrek']")
    if comp is None or comp.findtext("dormantHediff") != "RM_GharrekDormant":
        bad.append("gust comp missing or not pointed at RM_GharrekDormant")
    sh = thing.find("comps/li[@Class='CompProperties_Shearable']")
    if sh is None or sh.findtext("woolDef") != "RM_GillAsh":
        bad.append("gill-ash shearable comp missing")
    if hed.find("stages/li/capMods/li/setMax") is None:
        bad.append("dormant hediff does not cap movement")
    # roster: shorthand element form, ~0.6, and one home only
    biome = _defs("BiomeDefs/RM_Abyss.xml")
    wa = biome.find(".//wildAnimals/RM_Gharrek")
    if wa is None or abs(float(wa.text) - 0.6) > 1e-6:
        bad.append("RM_Abyss <wildAnimals> lacks <RM_Gharrek>0.6</RM_Gharrek>")
    if not float(biome.findtext(".//animalDensity")) > 0:
        bad.append("RM_Abyss animalDensity is 0: roster is dead content")
    # art: 3 facings of the pawn, one single for the item
    for tex in {l.findtext("bodyGraphicData/texPath") for l in kind.iter("li") if l.find("bodyGraphicData") is not None}:
        for f in ("south", "east", "north"):
            if not os.path.isfile(os.path.join(HERE, "Textures", "%s_%s.png" % (tex, f))):
                bad.append("missing facing %s_%s.png" % (tex, f))
    if not os.path.isfile(os.path.join(HERE, "Textures", ash.findtext("graphicData/texPath") + ".png")):
        bad.append("gill-ash texture missing")
    # C# sources are compiled (EnableDefaultCompileItems false => unlisted file compiles into nothing)
    proj = open(os.path.join(HERE, "Source", "RM_Abyss.csproj")).read()
    for cs in ("RM_GustController.cs", "RM_CompGharrek.cs"):
        if 'Compile Include="%s"' % cs not in proj:
            bad.append("%s not in csproj" % cs)
        elif not os.path.isfile(os.path.join(HERE, "Source", cs)):
            bad.append("%s missing on disk" % cs)
    return bad


def durrgak_check():
    """Offline: durrgak defs, cairn, memory, art, comps, roster row, toggle, csproj. Returns failures."""
    bad = []
    root = _defs("ThingDefs_Races/RM_Durrgak.xml")
    thing = next((d for d in root.iter("ThingDef") if d.findtext("defName") == "RM_Durrgak"), None)
    kind = next((d for d in root.iter("PawnKindDef") if d.findtext("defName") == "RM_Durrgak"), None)
    cairn = next((d for d in root.iter("ThingDef") if d.findtext("defName") == "RM_DurrgakCairn"), None)
    mem = next((d for d in root.iter("ThoughtDef") if d.findtext("defName") == "RM_SawDurrgakRing"), None)
    if None in (thing, kind, cairn, mem):
        return ["missing def: thing=%s kind=%s cairn=%s memory=%s" % (thing is not None, kind is not None, cairn is not None, mem is not None)]
    if kind.findtext("race") != "RM_Durrgak":
        bad.append("PawnKind race != RM_Durrgak")
    if thing.find("statBases/MaxFlightTime") is not None:
        bad.append("durrgak must not fly")
    if thing.findtext("race/trainability") != "Advanced":
        bad.append("durrgak must be Advanced-trainable (vanilla Haul requires it) so tamed it tidies")
    comp = thing.find("comps/li[@Class='RimMandrake.Abyss.CompProperties_Durrgak']")
    if comp is None or comp.findtext("cairnDef") != "RM_DurrgakCairn":
        bad.append("durrgak comp missing or not pointed at RM_DurrgakCairn")
    cc = cairn.find("comps/li[@Class='RimMandrake.Abyss.CompProperties_DurrgakCairn']")
    if cc is None or cc.findtext("memory") != "RM_SawDurrgakRing":
        bad.append("cairn comp missing or not pointed at RM_SawDurrgakRing")
    if cairn.findtext("tickerType") != "Rare":
        bad.append("cairn needs tickerType Rare for CompTickRare")
    if "who" in (cairn.findtext("description") or "").lower().split() or "durrgak" in (cairn.findtext("description") or "").lower():
        bad.append("cairn description must never say who made it")
    biome = _defs("BiomeDefs/RM_Abyss.xml")
    wa = biome.find(".//wildAnimals/RM_Durrgak")
    if wa is None or not float(wa.text) > 0:
        bad.append("RM_Abyss <wildAnimals> lacks <RM_Durrgak>commonality</RM_Durrgak>")
    for tex in {l.findtext("bodyGraphicData/texPath") for l in kind.iter("li") if l.find("bodyGraphicData") is not None}:
        for f in ("south", "east", "north"):
            if not os.path.isfile(os.path.join(HERE, "Textures", "%s_%s.png" % (tex, f))):
                bad.append("missing facing %s_%s.png" % (tex, f))
    if not os.path.isfile(os.path.join(HERE, "Textures", cairn.findtext("graphicData/texPath") + ".png")):
        bad.append("cairn texture missing")
    proj = open(os.path.join(HERE, "Source", "RM_Abyss.csproj")).read()
    if 'Compile Include="RM_CompDurrgak.cs"' not in proj or not os.path.isfile(os.path.join(HERE, "Source", "RM_CompDurrgak.cs")):
        bad.append("RM_CompDurrgak.cs not compiled or missing")
    if "durrgakRingsEnabled" not in open(os.path.join(HERE, "Source", "RM_AbyssMod.cs")).read():
        bad.append("Mod Settings toggle durrgakRingsEnabled missing")
    return bad


def krizzak_check():
    """Offline: krizzak flight state (MaxFlightTime>0 + flags), flip-book frames, comp, toggle, roster row, csproj."""
    bad = []
    root = _defs("ThingDefs_Races/RM_Krizzak.xml")
    thing = next((d for d in root.iter("ThingDef") if d.findtext("defName") == "RM_Krizzak"), None)
    kind = next((d for d in root.iter("PawnKindDef") if d.findtext("defName") == "RM_Krizzak"), None)
    if thing is None or kind is None:
        return ["missing def: thing=%s kind=%s" % (thing is not None, kind is not None)]
    if kind.findtext("race") != "RM_Krizzak":
        bad.append("PawnKind race != RM_Krizzak")
    # flight is a STAT (Pawn_FlightTracker.CanEverFly = MaxFlightTime > 0), never a bool or a render node
    try:
        mft = float(thing.findtext("statBases/MaxFlightTime"))
    except (TypeError, ValueError):
        mft = 0.0
    if not mft > 0:
        bad.append("MaxFlightTime must be > 0 (CanEverFly reads the stat)")
    if thing.find("statBases/FlightCooldown") is None:
        bad.append("FlightCooldown missing")
    if not float(thing.findtext("race/flightSpeedFactor") or 0) > 0:
        bad.append("race flightSpeedFactor missing")
    if "Spastic" in open(os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_Krizzak.xml")).read().replace("NEVER a Spastic", ""):
        bad.append("Spastic wing render node is forbidden")
    # flip-book: <prefix><N>_<dir> for N=1..count, dirs south/east/north
    prefix = kind.findtext("flyingAnimationFramePathPrefix")
    count = int(kind.findtext("flyingAnimationFrameCount") or 0)
    if not prefix or count < 1:
        bad.append("flip-book prefix/count missing")
    else:
        for n in range(1, count + 1):
            for f in ("south", "east", "north"):
                if not os.path.isfile(os.path.join(HERE, "Textures", "%s%d_%s.png" % (prefix, n, f))):
                    bad.append("missing flight frame %s%d_%s.png" % (prefix, n, f))
    for tex in {l.findtext("bodyGraphicData/texPath") for l in kind.iter("li") if l.find("bodyGraphicData") is not None}:
        for f in ("south", "east", "north"):
            if not os.path.isfile(os.path.join(HERE, "Textures", "%s_%s.png" % (tex, f))):
                bad.append("missing facing %s_%s.png" % (tex, f))
    if thing.find("comps/li[@Class='RimMandrake.Abyss.CompProperties_Krizzak']") is None:
        bad.append("krizzak comp missing")
    biome = _defs("BiomeDefs/RM_Abyss.xml")
    wa = biome.find(".//wildAnimals/RM_Krizzak")
    if wa is None or not float(wa.text) > 0:
        bad.append("RM_Abyss <wildAnimals> lacks <RM_Krizzak>commonality</RM_Krizzak>")
    src = os.path.join(HERE, "Source")
    if 'Compile Include="RM_CompKrizzak.cs"' not in open(os.path.join(src, "RM_Abyss.csproj")).read() or not os.path.isfile(os.path.join(src, "RM_CompKrizzak.cs")):
        bad.append("RM_CompKrizzak.cs not compiled or missing")
    if "krizzakLightEatingEnabled" not in open(os.path.join(src, "RM_AbyssMod.cs")).read():
        bad.append("Mod Settings toggle krizzakLightEatingEnabled missing")
    return bad


def etchfall_check():
    """Offline: tholin, both chemfuel recipes (tholin + gill-ash), erosion comp, slider, csproj."""
    bad = []
    items = _defs("ThingDefs_Items/RM_Tholin.xml")
    tho = next((d for d in items.iter("ThingDef") if d.findtext("defName") == "RM_Tholin"), None)
    if tho is None:
        return ["RM_Tholin def missing"]
    if not os.path.isfile(os.path.join(HERE, "Textures", tho.findtext("graphicData/texPath") + ".png")):
        bad.append("tholin texture missing")
    rec = {r.findtext("defName"): r for r in _defs("RecipeDefs/RM_Recipes_Chemfuel.xml").iter("RecipeDef")}
    for name, ing in (("RM_Make_ChemfuelFromTholin", "RM_Tholin"), ("RM_Make_ChemfuelFromGillAsh", "RM_GillAsh")):
        r = rec.get(name)
        if r is None:
            bad.append("recipe missing: " + name)
            continue
        if r.findtext("ingredients/li/filter/thingDefs/li") != ing or r.find("products/Chemfuel") is None:
            bad.append("%s does not turn %s into Chemfuel" % (name, ing))
        if r.findtext("recipeUsers/li") != "BiofuelRefinery":
            bad.append(name + " has no recipeUsers BiofuelRefinery")
    ter = _defs("TerrainDefs/RM_EtchHollow.xml").find(".//TerrainDef/defName")
    src = os.path.join(HERE, "Source")
    cs = open(os.path.join(src, "RM_MapComponentEtchfall.cs")).read() if os.path.isfile(os.path.join(src, "RM_MapComponentEtchfall.cs")) else ""
    for needle in ("RM_EtchHollow", "RM_Tholin", "c.Roofed(map)", "isNaturalRock", "ThingDefOf.Steel", "etchfallStrength"):
        if needle not in cs:
            bad.append("etchfall source lacks " + needle)
    if ter is None or ter.text != "RM_EtchHollow":
        bad.append("RM_EtchHollow terrain def missing")
    if 'Compile Include="RM_MapComponentEtchfall.cs"' not in open(os.path.join(src, "RM_Abyss.csproj")).read():
        bad.append("RM_MapComponentEtchfall.cs not in csproj")
    if "etchfallStrength" not in open(os.path.join(src, "RM_AbyssMod.cs")).read():
        bad.append("Mod Settings slider etchfallStrength missing")
    return bad


def dark_check():
    """Offline: the three weathers, murk hediff, biome wiring (no donor weather), Dark component, settings, grain hook, csproj."""
    bad = []
    w = {d.findtext("defName"): d for d in _defs("WeatherDefs/RM_Weathers_Abyss.xml").iter("WeatherDef")}
    for n in ("RM_AbyssDark", "RM_AbyssUnveiling", "RM_AbyssWitchfire"):
        if n not in w:
            bad.append("weather missing: " + n)
    if not any(d.findtext("defName") == "RM_Murk" for d in _defs("HediffDefs/RM_Hediffs_Dark.xml").iter("HediffDef")):
        bad.append("RM_Murk hediff missing")
    biome = _defs("BiomeDefs/RM_Abyss.xml")
    bw = biome.find(".//baseWeatherCommonalities")
    if bw is None:
        return bad + ["biome has no baseWeatherCommonalities"]
    c = {e.tag: float(e.text) for e in bw}
    if c.get("Clear") != 0:
        bad.append("Clear weather commonality must stay 0 (hard ban 4)")
    if any(t.startswith("AB_") for t in c):
        bad.append("donor AB_ weather still in the biome")
    if not (c.get("RM_AbyssDark", 0) > 0 and 0 < c.get("RM_AbyssUnveiling", 0) <= 2 and c.get("RM_AbyssUnveiling", 0) < c.get("RM_AbyssDark", 0) / 20):
        bad.append("Dark must dominate and the Unveiling be rare (<5%% of the Dark): %r" % c)
    if c.get("RM_AbyssWitchfire", 0) <= 0:
        bad.append("Witchfire not in biome")
    if w.get("RM_AbyssUnveiling") is not None and w["RM_AbyssUnveiling"].findtext("repeatable") != "false":
        bad.append("Unveiling must not be repeatable")
    src = os.path.join(HERE, "Source")
    cs = open(os.path.join(src, "RM_MapComponentDark.cs")).read() if os.path.isfile(os.path.join(src, "RM_MapComponentDark.cs")) else ""
    for needle in ("GetTemperature(map)", "Roofed(map)", "RM_Murk", "CompGlower", "RM_Summ", "WeatherEvent_LightningFlash",
                   "darkStrength", "unveilingEnabled", "stormCallEnabled", "RM_DurrgakCairn", "GrainMultiplier"):
        if needle not in cs:
            bad.append("Dark source lacks " + needle)
    if "IsGrainfall" in cs and "return map?.Biome" in open(os.path.join(src, "RM_MapComponentEtchfall.cs")).read():
        bad.append("IsGrainfall is still the biome stand-in")
    mod = open(os.path.join(src, "RM_AbyssMod.cs")).read()
    for needle in ("darkEnabled", "darkStrength", "unveilingEnabled", "stormCallEnabled"):
        if needle not in mod:
            bad.append("Mod Settings lacks " + needle)
    if 'Compile Include="RM_MapComponentDark.cs"' not in open(os.path.join(src, "RM_Abyss.csproj")).read():
        bad.append("RM_MapComponentDark.cs not in csproj")
    if not os.path.isfile(os.path.join(HERE, "Assemblies", "RimMandrake.Abyss.dll")):
        bad.append("DLL not built")
    return bad


def cover_check():
    """Offline: ship cover component, probe extension on the biome, settings, csproj."""
    bad = []
    src = os.path.join(HERE, "Source")
    f = os.path.join(src, "RM_MapComponentShipCover.cs")
    cs = open(f).read() if os.path.isfile(f) else ""
    for needle in ("GravEngine", "IsCovered", "MaxCoveredTicks", "RM_AbyssProbeExtension", "Faction.OfMechanoids",
                   "ReportTicks", "Collapse(", "shipCoverEnabled", "probesEnabled", "pather.Moving"):
        if needle not in cs:
            bad.append("cover source lacks " + needle)
    mod = open(os.path.join(src, "RM_AbyssMod.cs")).read()
    for needle in ("shipCoverEnabled", "probesEnabled"):
        if mod.count(needle) < 3:
            bad.append("Mod Settings lacks " + needle)
    if 'Compile Include="RM_MapComponentShipCover.cs"' not in open(os.path.join(src, "RM_Abyss.csproj")).read():
        bad.append("RM_MapComponentShipCover.cs not in csproj")
    biome = _defs("BiomeDefs/RM_Abyss.xml")
    if biome.find(".//modExtensions/li[@Class='RimMandrake.Abyss.RM_AbyssProbeExtension']") is None:
        bad.append("biome lacks RM_AbyssProbeExtension")
    return bad


try:
    from modcheck import Suite, ExpectationFailed
    suite = Suite("Abyss")
    suite.toggles = []

    @suite.chain("etchcap_defs_resolve")
    def etchcap_defs_resolve(t):
        """Live: the three defs loaded (a def with an unresolvable field is silently discarded)."""
        with t.component("etchcap_defs_loaded", beyond_toggle=True):
            for d in ("ThingDef/RM_Etchcap", "ThingDef/RM_EtchcapCap", "TerrainDef/RM_EtchHollow"):
                r = t.bridge_call("jawa/get_defs", defs=d)
                if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                    raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
            t.screenshot()

    @suite.chain("gharrek_defs_resolve")
    def gharrek_defs_resolve(t):
        """Live: the gharrek defs loaded and the biome rosters it."""
        with t.component("gharrek_defs_loaded", beyond_toggle=True):
            for d in ("ThingDef/RM_Gharrek", "PawnKindDef/RM_Gharrek", "ThingDef/RM_GillAsh", "HediffDef/RM_GharrekDormant"):
                r = t.bridge_call("jawa/get_defs", defs=d)
                if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                    raise ExpectationFailed("def did not load: %s -> %r" % (d, r))

    @suite.chain("durrgak_defs_resolve")
    def durrgak_defs_resolve(t):
        """Live: the durrgak defs loaded."""
        with t.component("durrgak_defs_loaded", beyond_toggle=True):
            for d in ("ThingDef/RM_Durrgak", "PawnKindDef/RM_Durrgak", "ThingDef/RM_DurrgakCairn", "ThoughtDef/RM_SawDurrgakRing"):
                r = t.bridge_call("jawa/get_defs", defs=d)
                if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                    raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
    @suite.chain("etchfall_defs_resolve")
    def etchfall_defs_resolve(t):
        """Live: tholin and both chemfuel recipes loaded."""
        with t.component("etchfall_defs_loaded", beyond_toggle=True):
            for d in ("ThingDef/RM_Tholin", "RecipeDef/RM_Make_ChemfuelFromTholin", "RecipeDef/RM_Make_ChemfuelFromGillAsh"):
                r = t.bridge_call("jawa/get_defs", defs=d)
                if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                    raise ExpectationFailed("def did not load: %s -> %r" % (d, r))

    @suite.chain("dark_defs_resolve")
    def dark_defs_resolve(t):
        """Live: the three weathers and the murk hediff loaded. The Dark's effect on a pawn needs a joint session (a state read of RM_Murk severity in a cold vs a heated room)."""
        with t.component("dark_defs_loaded", beyond_toggle=True):
            for d in ("WeatherDef/RM_AbyssDark", "WeatherDef/RM_AbyssUnveiling", "WeatherDef/RM_AbyssWitchfire", "HediffDef/RM_Murk"):
                r = t.bridge_call("jawa/get_defs", defs=d)
                if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                    raise ExpectationFailed("def did not load: %s -> %r" % (d, r))

    @suite.chain("krizzak_defs_resolve")
    def krizzak_defs_resolve(t):
        """Live: the krizzak defs loaded. Flight itself is proved by a Pawn_FlightTracker state read with the owner present, never a visual hunt."""
        with t.component("krizzak_defs_loaded", beyond_toggle=True):
            for d in ("ThingDef/RM_Krizzak", "PawnKindDef/RM_Krizzak"):
                r = t.bridge_call("jawa/get_defs", defs=d)
                if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                    raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
except ImportError:
    suite = None

if __name__ == "__main__":
    f = static_check()
    print("ETCHCAP static: %s" % ("PASS" if not f else "FAIL " + "; ".join(f)))
    g = gharrek_check()
    print("GHARREK static: %s" % ("PASS" if not g else "FAIL " + "; ".join(g)))
    d = durrgak_check()
    print("DURRGAK static: %s" % ("PASS" if not d else "FAIL " + "; ".join(d)))
    e = etchfall_check()
    print("ETCHFALL static: %s" % ("PASS" if not e else "FAIL " + "; ".join(e)))
    k = krizzak_check()
    print("KRIZZAK static: %s" % ("PASS" if not k else "FAIL " + "; ".join(k)))
    r = dark_check()
    print("DARK static: %s" % ("PASS" if not r else "FAIL " + "; ".join(r)))
    v = cover_check()
    print("SHIP COVER static: %s" % ("PASS" if not v else "FAIL " + "; ".join(v)))
    sys.exit(1 if (f or g or d or e or k or r or v) else 0)
