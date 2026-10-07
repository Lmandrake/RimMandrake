"""validation.py -- modcheck suite for RimMandrake Abyss (mandrake.rm.abyss).

First script for this mod (debug_process.md). Covers ABYSS_ETCHCAP_BUILD_1 and ABYSS_GHARREK_BUILD_1.
Two layers: `static_check()` is offline (parses the shipped XML, runs with plain
`python3 validation.py`); the chain is a live def-resolution read, NEVER RUN YET.
Mod Settings: the Abyss's only control is the worldgen-rarity slider; the etchcap carries no
toggle (it is a def, and gating a def needs C# plus a DLL rebuild -- owed, see the item).
"""
import os
import re
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
        # Graphic_Random reads a FOLDER of PNGs; anything else reads one file (etchcap was a
        # Graphic_Random pointed at a single PNG and rendered nothing: ABYSS_SHEET_DONOR_PORT_1 #3)
        if d.findtext("graphicData/graphicClass") == "Graphic_Random":
            folder = os.path.join(HERE, "Textures", tp or "")
            found = os.path.isdir(folder) and any(f.endswith(".png") for f in os.listdir(folder))
        else:
            found = os.path.isfile(os.path.join(HERE, "Textures", (tp or "") + ".png"))
        if tp != "RM_Abyss/" + ext or not found:
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
    # map signs: den + salvage cache defs with art, the GenStep wired through RM_Abyss extraGenSteps
    for dn in ("RM_DurrgakDen", "RM_DurrgakSalvageCache"):
        d = next((x for x in root.iter("ThingDef") if x.findtext("defName") == dn), None)
        if d is None:
            bad.append("missing def %s" % dn)
            continue
        if not os.path.isfile(os.path.join(HERE, "Textures", (d.findtext("graphicData/texPath") or "") + ".png")):
            bad.append("%s texture missing" % dn)
        if "durrgak" in (d.findtext("description") or "").lower():
            bad.append("%s description must never say who made it" % dn)
    gs = next((g for g in _defs("MapGeneration/RM_DurrgakSigns_GenStep.xml").iter("GenStepDef")
               if g.findtext("defName") == "RM_DurrgakSigns"), None)
    if gs is None or gs.find("genStep").get("Class") != "RimMandrake.Abyss.RM_GenStep_DurrgakSigns":
        bad.append("GenStepDef RM_DurrgakSigns missing or wrong class")
    elif {gs.findtext("genStep/denDef"), gs.findtext("genStep/cacheDef"), gs.findtext("genStep/cairnDef")} != {
            "RM_DurrgakDen", "RM_DurrgakSalvageCache", "RM_DurrgakCairn"}:
        bad.append("RM_DurrgakSigns not pointed at den/cache/cairn")
    if "RM_DurrgakSigns" not in [li.text for li in biome.findall(".//extraGenSteps/li")]:
        bad.append("RM_Abyss extraGenSteps lacks RM_DurrgakSigns")
    if 'Compile Include="RM_GenStep_DurrgakSigns.cs"' not in proj:
        bad.append("RM_GenStep_DurrgakSigns.cs not compiled")
    if "durrgakMapSignsEnabled" not in open(os.path.join(HERE, "Source", "RM_AbyssMod.cs")).read():
        bad.append("Mod Settings toggle durrgakMapSignsEnabled missing")
    return bad


def freed_beasts_check():
    """Offline (ABYSS_DONOR_BEASTS_FREED_1): summ + summing + drokattak defs, own art, zero donor names, rosters, comps, toggles."""
    bad = []
    summ = _defs("ThingDefs_Races/RM_Summ.xml")
    drok = _defs("ThingDefs_Races/RM_Drokattak.xml")
    kinds = {k.findtext("defName"): k for r in (summ, drok) for k in r.iter("PawnKindDef")}
    things = {t.findtext("defName"): t for r in (summ, drok) for t in r.iter("ThingDef")}
    for k in ("RM_Summ", "RM_Summing", "RM_Drokattak"):
        if k not in kinds:
            bad.append("missing PawnKindDef %s" % k)
    for t in ("RM_Summ", "RM_Drokattak"):
        if t not in things:
            bad.append("missing ThingDef %s" % t)
    if bad:
        return bad
    if kinds["RM_Summing"].findtext("race") != "RM_Summ":
        bad.append("RM_Summing must be a kind on the RM_Summ race")
    if int(kinds["RM_Summing"].findtext("maxGenerationAge") or 999) > 3:
        bad.append("RM_Summing must generate young only")
    n_stages = len(things["RM_Summ"].findall("race/lifeStageAges/li"))
    for k in ("RM_Summ", "RM_Summing"):
        if len(kinds[k].findall("lifeStages/li")) != n_stages:
            bad.append("%s lifeStages count != race lifeStageAges (%d)" % (k, n_stages))
    for k in kinds.values():
        for tex in {l.findtext("bodyGraphicData/texPath") for l in k.findall("lifeStages/li")}:
            for f in ("south", "east", "north"):
                if not os.path.isfile(os.path.join(HERE, "Textures", "%s_%s.png" % (tex, f))):
                    bad.append("missing facing %s_%s.png" % (tex, f))
    raw = open(os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_Summ.xml")).read() + open(
        os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_Drokattak.xml")).read()
    code = re.sub(r"<!--.*?-->", "", raw, flags=re.S)  # headers name the donors they replace; defs must not
    for donor in ("AA_", "GR_", "MayRequire", "Behemoth", "Nighthrumbo"):
        if donor in code:
            bad.append("donor trace %r in the freed-beast defs" % donor)
    body = code.lower()
    if "dragon" in body:
        bad.append("the word dragon reached a def (ruling 9)")
    if things["RM_Summ"].find("comps/li[@Class='RimMandrake.Abyss.CompProperties_RM_SummHide']") is None:
        bad.append("summ lacks RM_SummHide comp")
    if things["RM_Drokattak"].find("comps/li[@Class='RimMandrake.Abyss.CompProperties_RM_QuillHackle']") is None:
        bad.append("drokattak lacks RM_QuillHackle comp")
    biome = _defs("BiomeDefs/RM_Abyss.xml")
    for k in ("RM_Summ", "RM_Drokattak"):
        if biome.find(".//wildAnimals/%s" % k) is None:
            bad.append("RM_Abyss <wildAnimals> lacks %s" % k)
    proj = open(os.path.join(HERE, "Source", "RM_Abyss.csproj")).read()
    for cs in ("RM_CompSummHide.cs", "RM_CompQuillHackle.cs"):
        if 'Compile Include="%s"' % cs not in proj:
            bad.append("%s not compiled" % cs)
    mod = open(os.path.join(HERE, "Source", "RM_AbyssMod.cs")).read()
    for tog in ("summRegenerates", "summUVSensitive", "drokattakHackleEnabled"):
        if tog not in mod:
            bad.append("Mod Settings toggle %s missing" % tog)
    if '"RM_Summ"' not in open(os.path.join(HERE, "Source", "RM_MapComponentDark.cs")).read():
        bad.append("storm call no longer looks up RM_Summ")
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


def predators_check():
    """Offline (ABYSS_INVENTED_CREATURES_TO_RM_1): cindermare + skarnix defs, wound chain, art, roster rows, comp, toggles."""
    bad = []
    cin = _defs("ThingDefs_Races/RM_Cindermare.xml")
    ska = _defs("ThingDefs_Races/RM_Skarnix.xml")

    def find(root, tag, name):
        return next((d for d in root.iter(tag) if d.findtext("defName") == name), None)
    things = {"RM_Cindermare": find(cin, "ThingDef", "RM_Cindermare"), "RM_Skarnix": find(ska, "ThingDef", "RM_Skarnix")}
    kinds = {"RM_Cindermare": find(cin, "PawnKindDef", "RM_Cindermare"), "RM_Skarnix": find(ska, "PawnKindDef", "RM_Skarnix")}
    dmg = find(cin, "DamageDef", "RM_ColdDrainDamage")
    hed = find(cin, "HediffDef", "RM_ColdDrain")
    if None in list(things.values()) + list(kinds.values()) + [dmg, hed]:
        return ["missing def among cindermare/skarnix thing, kind, damage, hediff"]
    for name in things:
        if kinds[name].findtext("race") != name:
            bad.append("%s PawnKind race mismatch" % name)
        if float(things[name].findtext("statBases/Wildness")) < 1.0:
            bad.append("%s must be untameable (Wildness 1.0)" % name)
        tex = kinds[name].findtext(".//bodyGraphicData/texPath")
        if not os.path.isfile(os.path.join(HERE, "Textures", tex + ".png")):
            bad.append("texture missing: " + tex)
    if dmg.findtext("hediff") != "RM_ColdDrain":
        bad.append("cold-drain damage does not apply RM_ColdDrain")
    if "RM_ColdDrainDamage" not in ET.tostring(things["RM_Cindermare"], encoding="unicode"):
        bad.append("cindermare grip does not deal RM_ColdDrainDamage")
    comp = things["RM_Skarnix"].find("comps/li[@Class='RimMandrake.Abyss.CompProperties_LightAversion']")
    if comp is None:
        bad.append("skarnix lacks CompProperties_LightAversion")
    biome = _defs("BiomeDefs/RM_Abyss.xml")
    for name in things:
        wa = biome.find(".//wildAnimals/" + name)
        if wa is None or not float(wa.text) > 0:
            bad.append("RM_Abyss <wildAnimals> lacks <%s>" % name)
    src = os.path.join(HERE, "Source")
    proj = open(os.path.join(src, "RM_Abyss.csproj")).read()
    if 'Compile Include="RM_CompLightAversion.cs"' not in proj or not os.path.isfile(os.path.join(src, "RM_CompLightAversion.cs")):
        bad.append("RM_CompLightAversion.cs not compiled or missing")
    mod = open(os.path.join(src, "RM_AbyssMod.cs")).read()
    for needle in ("lightAversionEnabled", "fleeRadiusMultiplier"):
        if mod.count(needle) < 3:
            bad.append("Mod Settings lacks " + needle)
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


def light_check():
    """Offline (ABYSS_LAMP_CROPS_BUILD_1 + ABYSS_FOLD_LAMP_BUILD_1): wickwood, fold-lamp, research gate, lane, settings, art."""
    bad = []
    wick = next((d for d in _defs("ThingDefs_Plants/RM_Wickwood.xml").iter("ThingDef") if d.findtext("defName") == "RM_Wickwood"), None)
    if wick is None:
        return ["RM_Wickwood missing"]
    if wick.get("ParentName") != "TreeBase":
        bad.append("wickwood must be a TreeBase tree (minifiable -> extract and replant)")
    gl = wick.find("comps/li[@Class='CompProperties_Glower']")
    if gl is None or not float(gl.findtext("overlightRadius") or 0) > 0:
        bad.append("wickwood has no overlightRadius (crops need GroundGlowAt 1.0; plain glow caps at 0.5)")
    if float(wick.findtext("plant/growMinGlow") or 1) != 0:
        bad.append("wickwood must grow in the dark (growMinGlow 0)")
    wp = _defs("BiomeDefs/RM_Abyss.xml").find(".//wildPlants/RM_Wickwood")
    if wp is None or not float(wp.text) > 0:
        bad.append("RM_Abyss <wildPlants> lacks RM_Wickwood")
    root = _defs("ThingDefs_Buildings/RM_FoldLamp.xml")
    lamp = next((d for d in root.iter("ThingDef") if d.findtext("defName") == "RM_FoldLamp"), None)
    rp = {d.findtext("defName"): d for d in root.iter("ResearchProjectDef")}
    eth = next((d for d in root.iter("ThingDef") if d.findtext("defName") == "RM_TheDarkItself"), None)
    if lamp is None or eth is None or "RM_HeatFolding" not in rp or "RM_DarkFoldsFromWarmth" not in rp:
        return bad + ["fold-lamp defs missing"]
    for c in ("CompProperties_Refuelable", "CompProperties_Glower", "CompProperties_HeatPusher"):
        if lamp.find("comps/li[@Class='%s']" % c) is None:
            bad.append("fold-lamp lacks " + c)
    if lamp.findtext("rotatable") != "true" or lamp.findtext("graphicData/graphicClass") != "Graphic_Multi":
        bad.append("fold-lamp must be rotatable Graphic_Multi (the throat points the facing)")
    if [li.text for li in lamp.findall("researchPrerequisites/li")] != ["RM_HeatFolding"]:
        bad.append("fold-lamp not gated by RM_HeatFolding")
    if [li.text for li in rp["RM_HeatFolding"].findall("prerequisites/li")] != ["RM_DarkFoldsFromWarmth"]:
        bad.append("heat-folding not gated by the observation")
    if rp["RM_DarkFoldsFromWarmth"].findtext("requiredResearchBuilding") != "RM_TheDarkItself" or eth.findtext("category") != "Ethereal":
        bad.append("observation must require the unbuildable Ethereal RM_TheDarkItself (never a bench)")
    tp = lamp.findtext("graphicData/texPath")
    for f in ("south", "east", "north"):
        if not os.path.isfile(os.path.join(HERE, "Textures", "%s_%s.png" % (tp, f))):
            bad.append("fold-lamp art missing: " + f)
    src = os.path.join(HERE, "Source")
    cs = open(os.path.join(src, "RM_AbyssLight.cs")).read()
    for needle in ("FinishProject", "RM_DarkFoldsFromWarmth", "c.Filled(map)", "Rot4", "overlightRadius = 0f",
                   "cachedPlantCommonalities", "foldLaneEnabled", "foldDiscoveryByWatching", "lampCropsEnabled", "GenSight.LineOfSight"):
        if needle not in cs:
            bad.append("light source lacks " + needle)
    dark = open(os.path.join(src, "RM_MapComponentDark.cs")).read()
    if "RM_MapComponent_FoldLanes.ClearanceAt" not in dark or "RM_HeatFoldingDiscovery.Check" not in dark:
        bad.append("the Dark does not read the lane / run the discovery")
    mod = open(os.path.join(src, "RM_AbyssMod.cs")).read()
    for needle in ("lampCropsEnabled", "foldLaneEnabled", "foldDiscoveryByWatching"):
        if mod.count(needle) < 3:
            bad.append("Mod Settings lacks " + needle)
    if 'Compile Include="RM_AbyssLight.cs"' not in open(os.path.join(src, "RM_Abyss.csproj")).read():
        bad.append("RM_AbyssLight.cs not in csproj")
    return bad


def soundscape_check():
    """Offline (ABYSS_SOUNDSCAPE_BUILD_1): four sound defs each with the Dark low-pass mapping, silent Dark bed, component, settings."""
    bad = []
    sd = {d.findtext("defName"): d for d in _defs("SoundDefs/RM_AbyssSoundscape.xml").iter("SoundDef")}
    for n in ("RM_AbyssGustImpact", "RM_AbyssGillRustle", "RM_AbyssGrainTick", "RM_AbyssLampClatter"):
        d = sd.get(n)
        if d is None:
            bad.append("sound missing: " + n)
            continue
        if d.find(".//inParam[@Class='RimMandrake.Abyss.SoundParamSource_RM_DarkMuffle']") is None \
                or d.find(".//filters/li[@Class='SoundFilterLowPass']") is None:
            bad.append(n + " lacks the Dark low-pass mapping")
    dark = next((d for d in _defs("WeatherDefs/RM_Weathers_Abyss.xml").iter("WeatherDef") if d.findtext("defName") == "RM_AbyssDark"), None)
    if dark is not None and dark.find("ambientSounds") is not None:
        bad.append("RM_AbyssDark still has an ambient bed (ruling: silence by default)")
    src = os.path.join(HERE, "Source")
    cs = open(os.path.join(src, "RM_AbyssSoundscape.cs")).read()
    for needle in ("GustCount", "RM_AbyssGustImpact", "RM_AbyssGillRustle", "RM_AbyssGrainTick", "RM_AbyssLampClatter",
                   "GrainMultiplier", "SoundParamSource", "darkMuffleEnabled", "gustSoundscapeEnabled"):
        if needle not in cs:
            bad.append("soundscape source lacks " + needle)
    if "LampClatter" not in open(os.path.join(src, "RM_CompKrizzak.cs")).read():
        bad.append("krizzak feed does not clatter")
    if "Ambient_Wind_Fog" not in open(os.path.join(src, "RM_AbyssLight.cs")).read():
        bad.append("soundscape-off does not restore the wind bed")
    mod = open(os.path.join(src, "RM_AbyssMod.cs")).read()
    for needle in ("gustSoundscapeEnabled", "darkMuffleEnabled"):
        if mod.count(needle) < 3:
            bad.append("Mod Settings lacks " + needle)
    if 'Compile Include="RM_AbyssSoundscape.cs"' not in open(os.path.join(src, "RM_Abyss.csproj")).read():
        bad.append("RM_AbyssSoundscape.cs not in csproj")
    hook = os.path.join(src, "RM_AbyssSoundHook.cs")
    if not os.path.exists(hook):
        bad.append("ABYSS_DARK_MUFFLE_ALL_SOUNDS_1: RM_AbyssSoundHook.cs missing")
    else:
        h = open(hook).read()
        for needle in ("typeof(Sample), nameof(Sample.Update)", "AudioLowPassFilter", "RM_Abyss", "darkMuffleAllSounds"):
            if needle not in h:
                bad.append("sound hook lacks " + needle)
    if 'Compile Include="RM_AbyssSoundHook.cs"' not in open(os.path.join(src, "RM_Abyss.csproj")).read():
        bad.append("RM_AbyssSoundHook.cs not in csproj")
    if "brrainz.harmony" not in open(os.path.join(HERE, "About", "About.xml")).read():
        bad.append("About.xml lacks the harmony dependency")
    if mod.count("darkMuffleAllSounds") < 3:
        bad.append("Mod Settings lacks darkMuffleAllSounds")
    return bad


def cryptid_check():
    """Offline (ABYSS_FREE_CRYPTID_1): the name lives in exactly one def of this mod; no pawn/faction of the cryptid;
    every grammar consumer includes the pack; the Utinni patch only adds, with no rename and no ancients wording."""
    bad = []
    name = "Nhaleth"
    hits = []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in files:
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    if isinstance(el.tag, str) and name in ET.tostring(el, encoding="unicode"):
                        hits.append(el.findtext("defName"))
    if hits != ["RM_AbyssCryptid"]:
        bad.append("the name must live only in RulePackDef RM_AbyssCryptid, found in %r" % hits)
    if not any("RM_Durrgak" in (d.findtext("defName") or "") for d in _defs("ThingDefs_Races/RM_Durrgak.xml")):
        bad.append("sanity probe: could not read the durrgak defs")
    root = _defs("MapGeneration/RM_AbyssCryptid.xml")
    for d in root:
        if d.tag in ("PawnKindDef", "FactionDef") or (d.tag == "ThingDef" and d.find("race") is not None):
            bad.append("ban 7: the cryptid may not have a %s (%s)" % (d.tag, d.findtext("defName")))
        if name.lower() in (d.findtext("defName") or "").lower():
            bad.append("defName names the cryptid: " + d.findtext("defName"))
    for tag in ("InteractionDef", "TaleDef"):
        for d in root.iter(tag):
            if "RM_AbyssCryptid" not in [li.text for li in d.iter("li")]:
                bad.append("%s %s does not include RM_AbyssCryptid" % (tag, d.findtext("defName")))
    biome = ET.tostring(_defs("BiomeDefs/RM_Abyss.xml"), encoding="unicode")
    if "RM_AbyssRumorSites" not in biome:
        bad.append("rumor-sites genstep not in RM_Abyss extraGenSteps")
    src = os.path.join(HERE, "Source")
    mod = open(os.path.join(src, "RM_AbyssMod.cs")).read()
    if mod.count("cryptidSignsEnabled") < 3:
        bad.append("Mod Settings lacks cryptidSignsEnabled (field, Scribe, control)")
    if "PhantomClearanceAt" not in open(os.path.join(src, "RM_MapComponentDark.cs")).read():
        bad.append("the Dark has no clear-pocket-around-nothing hook")
    if 'Compile Include="RM_AbyssCryptid.cs"' not in open(os.path.join(src, "RM_Abyss.csproj")).read():
        bad.append("RM_AbyssCryptid.cs not in csproj")
    ut = os.path.join(HERE, "..", "..", "RimUtinni", "UtinniPatches", "Patches", "Abyss_CryptidSithWhisper.xml")
    if not os.path.isfile(ut):
        bad.append("Utinni Sith whisper patch missing")
    else:
        txt = open(ut).read()
        body = re.sub(r"<!--.*?-->", "", txt, flags=re.S)
        if "Sith" not in body or re.search(r"rakat|ancient|terraform|forsaken|PatchOperationReplace", body, re.I):
            bad.append("Utinni patch must only ADD a Sith whisper (no rename, no Rakata/ancients/Forsaken wording)")
    return bad


def _const(src, name):
    m = re.search(r"const float %s\s*=\s*([0-9.]+)f" % name, src)
    return float(m.group(1)) if m else None


def brood_check():
    """Offline (ABYSS_LIGHTFALL_BROOD_WRECK_1): every def the lair names resolves, the wreck's stock and its
    salvage bills agree, the ship takes four parts and refuses three (refused ones smelt), the greed arithmetic
    keeps a modest haul safe and the whole haul plus the egg always past the line, no 'dragon' anywhere a player
    reads, the great bone can only be placed on substructure, both patches wire it, settings and csproj complete."""
    bad = []
    lair = _defs("BroodLair/RM_BroodLair.xml")
    wreckx = _defs("BroodLair/RM_RescueShipWreck.xml")
    defs = {}
    for root in (lair, wreckx, _defs("ThingDefs_Races/RM_Summ.xml")):
        for d in root:
            if isinstance(d.tag, str) and d.findtext("defName"):
                defs[(d.tag, d.findtext("defName"))] = d
    things = {k[1]: v for k, v in defs.items() if k[0] == "ThingDef"}
    if len(things) < 10:
        return ["sanity probe: read only %d ThingDefs from the brood files" % len(things)]

    # 1. the genstep's fields resolve
    gs = lair.find(".//GenStepDef[defName='RM_BroodLair']/genStep")
    if gs is None:
        bad.append("GenStepDef RM_BroodLair missing")
    else:
        for f in ("motherDef", "eggDef", "greatBoneDef", "boneDef", "wreckDef"):
            if gs.findtext(f) not in things:
                bad.append("genstep %s -> %r does not resolve" % (f, gs.findtext(f)))
    # 2. wreck stock == recipe products, every recipe used at the wreck
    wreck = things.get("RM_RescueShipWreck")
    stock = [c.tag for c in wreck.find(".//stock")] if wreck is not None and wreck.find(".//stock") is not None else []
    recipes = [d for d in wreckx.iter("RecipeDef") if d.get("Abstract") != "True"]
    products = []
    base = wreckx.find(".//RecipeDef[@Name='RM_WreckSalvageBase']")
    if base is None or "RM_RescueShipWreck" not in [li.text for li in base.iter("li")]:
        bad.append("salvage recipes are not used at RM_RescueShipWreck")
    for r in recipes:
        if r.get("ParentName") != "RM_WreckSalvageBase":
            bad.append("recipe %s does not inherit the salvage worker" % r.findtext("defName"))
        products += [c.tag for c in r.find("products")]
    if sorted(stock) != sorted(products) or len(stock) != 7:
        bad.append("wreck stock %r != salvage products %r" % (sorted(stock), sorted(products)))
    # 3. four accepted, three refused; refused parts smelt; accepted parts are consumed when fitted
    acc = [p for p in stock if things.get(p) is not None and things[p].get("ParentName") == "RM_ShipPartAcceptedBase"]
    ref = [p for p in stock if things.get(p) is not None and things[p].get("ParentName") == "RM_ShipPartRefusedBase"]
    if (len(acc), len(ref)) != (4, 3):
        bad.append("expected 4 accepted / 3 refused parts, got %d / %d" % (len(acc), len(ref)))
    for p in ref:
        if things[p].find("smeltProducts") is None:
            bad.append("refused part %s has no smeltProducts (it must stay loot)" % p)
    abase = wreckx.find(".//ThingDef[@Name='RM_ShipPartAcceptedBase']")
    rbase = wreckx.find(".//ThingDef[@Name='RM_ShipPartRefusedBase']")
    if abase is None or abase.find(".//li[@Class='CompProperties_UseEffectDestroySelf']") is None \
            or (abase.findtext(".//accepted") or "").strip() != "true":
        bad.append("accepted parts must be fitted (accepted=true) and consumed")
    if rbase is None or (rbase.findtext(".//accepted") or "").strip() != "false" \
            or rbase.find(".//li[@Class='CompProperties_UseEffectDestroySelf']") is not None:
        bad.append("refused parts must say accepted=false and never be consumed")
    # 4. greed arithmetic against the C# constants
    src = os.path.join(HERE, "Source")
    logic = open(os.path.join(src, "RM_BroodWakeLogic.cs")).read()
    tmin, tmax, egg = _const(logic, "ThresholdMin"), _const(logic, "ThresholdMax"), _const(logic, "EggWeight")
    greeds = sorted(float(things[p].findtext(".//greed") or 0) for p in stock if p in things)
    if None in (tmin, tmax, egg) or not greeds:
        bad.append("could not read the wake constants or greeds")
    else:
        if sum(greeds) + egg <= tmax:
            bad.append("whole haul + egg (%.2f) does not pass the highest line %.2f: greed never wakes her" % (sum(greeds) + egg, tmax))
        if sum(greeds[-3:]) >= tmin:
            bad.append("a modest haul (the 3 greediest parts, %.2f) can pass the lowest line %.2f" % (sum(greeds[-3:]), tmin))
        if _const(logic, "RumbleFraction") is None or not (_const(logic, "StirFraction") < _const(logic, "RumbleFraction") < 1.0):
            bad.append("signs out of order: stir < rumble < wake")
    # 5. no fantasy-dragon tells in any player-facing text
    for root in (lair, wreckx):
        for el in root.iter():
            if el.tag in ("label", "description", "labelPlural", "jobString", "useLabel") and el.text \
                    and re.search(r"dragon|fire.?breath|hoard", el.text, re.I):
                bad.append("fantasy-dragon wording in %s: %r" % (el.tag, el.text[:60]))
            if el.tag == "defName" and el.text and "dragon" in el.text.lower():
                bad.append("defName names a dragon: " + el.text)
    for fn in ("RM_BroodLair.cs", "RM_BroodEgg.cs", "RM_ShipWreck.cs", "RM_BroodWakeLogic.cs"):
        code = re.sub(r"//[^\n]*", "", open(os.path.join(src, fn)).read())   # comments may quote the ban itself
        for lit in re.findall(r'"([^"\n]*)"', code):
            if re.search(r"dragon|hoard", lit, re.I):
                bad.append("fantasy-dragon wording in a %s string: %r" % (fn, lit[:60]))
    # 6. the bond: great bone only on substructure, and the egg looks for that def
    gb = things.get("RM_SummGreatBone")
    if gb is None or "PlaceWorker_OnSubstructure" not in [li.text for li in gb.iter("li")] or gb.findtext("minifiedDef") != "MinifiedThing":
        bad.append("great bone must be minifiable and placeable only on substructure")
    eggc = things.get("RM_SummEgg")
    if eggc is None or eggc.findtext(".//greatBoneDef") != "RM_SummGreatBone" or eggc.findtext(".//hatchKind") != "RM_Summing":
        bad.append("egg must hatch RM_Summing and look for RM_SummGreatBone")
    if things.get("RM_SummBone") is None or things["RM_SummBone"].find("stuffProps") is None:
        bad.append("summ bone is not stuff")
    # 7. she is a summ, five life stages like the race; the awake hediff blocks almost all damage
    ak = defs.get(("PawnKindDef", "RM_SummAllRender"))
    race = things.get("RM_Summ")
    if ak is None or ak.findtext("race") != "RM_Summ" or race is None \
            or len(ak.find("lifeStages")) != len(race.find("race/lifeStageAges")):
        bad.append("RM_SummAllRender must be an RM_Summ kind with one graphic per race life stage")
    aw = defs.get(("HediffDef", "RM_BroodMotherAwake"))
    if aw is None or not float(aw.findtext(".//IncomingDamageFactor") or 1) <= 0.1:
        bad.append("woken brood-mother is not essentially unkillable (IncomingDamageFactor > 0.1)")
    if race is None or race.find(".//li[@Class='RimMandrake.Abyss.CompProperties_RM_SummBane']") is None:
        bad.append("RM_Summ lacks the bane comp")
    # 8. textures of our own resolve
    for d in things.values():
        tp = d.findtext("graphicData/texPath") or ""
        if tp.startswith("RM_Abyss/"):
            ok = os.path.isfile(os.path.join(HERE, "Textures", tp + ".png")) or \
                 os.path.isfile(os.path.join(HERE, "Textures", tp + "_south.png"))
            if not ok:
                bad.append("texture missing for %s: %s" % (d.findtext("defName"), tp))
    # 9. wiring: map-gen patch, Utinni landmark patch, settings, csproj
    mg = os.path.join(HERE, "Patches", "RM_BroodLair_MapGen.xml")
    if not os.path.isfile(mg) or "<li>RM_BroodLair</li>" not in open(mg).read() or "MapCommonBase" not in open(mg).read():
        bad.append("RM_BroodLair genstep is not added to MapCommonBase")
    ut = os.path.join(HERE, "..", "..", "RimUtinni", "UtinniPatches", "Patches", "RUT_Lightfall_BroodLair.xml")
    if not os.path.isfile(ut) or 'RUT_Lightfall' not in open(ut).read() or "RimMandrake.Abyss.RM_BroodLairExtension" not in open(ut).read():
        bad.append("Utinni patch does not mark RUT_Lightfall with RM_BroodLairExtension")
    if "class RM_BroodLairExtension" not in open(os.path.join(src, "RM_BroodLair.cs")).read():
        bad.append("RM_BroodLairExtension class missing")
    mod = open(os.path.join(src, "RM_AbyssMod.cs")).read()
    for f in ("broodLairEnabled", "wreckEnabled", "eggStormsEnabled", "baneEnabled", "beastHunger", "broodSleepDepth"):
        # field, Scribe and an on-screen control, each matched by shape (a bare count passes on a comment)
        field = re.search(r"public static (bool|float) %s\b" % f, mod)
        scribe = "Scribe_Values.Look(ref %s," % f in mod
        control = re.search(r"CheckboxLabeled\([^;]*ref %s\b" % f, mod) or ("%s = list.Slider(%s," % (f, f)) in mod
        if not (field and scribe and control):
            bad.append("Mod Settings lacks %s (field=%s scribe=%s control=%s)" % (f, bool(field), scribe, bool(control)))
    proj = open(os.path.join(src, "RM_Abyss.csproj")).read()
    for fn in ("RM_BroodWakeLogic.cs", "RM_BroodLair.cs", "RM_BroodEgg.cs", "RM_ShipWreck.cs"):
        if 'Compile Include="%s"' % fn not in proj:
            bad.append("%s not in csproj" % fn)
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
            for d in ("ThingDef/RM_Durrgak", "PawnKindDef/RM_Durrgak", "ThingDef/RM_DurrgakCairn", "ThoughtDef/RM_SawDurrgakRing",
                      "ThingDef/RM_DurrgakDen", "ThingDef/RM_DurrgakSalvageCache", "GenStepDef/RM_DurrgakSigns"):
                r = t.bridge_call("jawa/get_defs", defs=d)
                if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                    raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
        # the real map-sign placement run on the current map (RM_GenStep_DurrgakSigns.ProofSigns). Not proven
        # here: a freshly GENERATED Abyss map carrying them (extraGenSteps) -- generate an Abyss quicktest.
        with t.component("durrgak_signs_placed", beyond_toggle=True):
            r = t.bridge_call("jawa/static_call", type="RimMandrake.Abyss.RM_GenStep_DurrgakSigns",
                              method="ProofSigns", args="current")
            res = str((r or {}).get("result", ""))
            if t._guard() and not res.startswith("den=1"):
                raise ExpectationFailed("no den placed: %r" % (r,))
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
        # Flight by STATE READ (jawa/pawn_flight report), never a screenshot: a spawned krizzak can ever fly.
        with t.component("krizzak_can_fly", beyond_toggle=True):
            s = t.bridge_call("jawa/spawn_pawn", kindDef="RM_Krizzak", x=15, z=15, faction="none", count=1)
            pid = (((s or {}).get("pawns") or [{}])[0]).get("id")
            r = t.bridge_call("jawa/pawn_flight", action="report", pawn=pid) if pid else None
            rows = (r or {}).get("pawns") or []
            if t._guard() and (not rows or rows[0].get("canEverFly") is not True):
                raise ExpectationFailed("RM_Krizzak canEverFly not True: spawn=%r flight=%r" % (s, rows[:1]))

    @suite.chain("freed_beasts")
    def freed_beasts(t):
        """Live: summ/summing/drokattak loaded; a spawned summing is young (generation age gate). The storm call's
        spawn of RM_Summ, the daylight burn and the hackle need a joint session or a storm on the Abyss."""
        with t.component("freed_beasts_defs_loaded", beyond_toggle=True):
            for d in ("ThingDef/RM_Summ", "PawnKindDef/RM_Summ", "PawnKindDef/RM_Summing", "ThingDef/RM_Drokattak",
                      "PawnKindDef/RM_Drokattak", "HediffDef/RM_SummSunburn", "LifeStageDef/RM_SummElder"):
                r = t.bridge_call("jawa/get_defs", defs=d)
                if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                    raise ExpectationFailed("def did not load: %s -> %r" % (d, r))

    @suite.chain("predators_defs_resolve")
    def predators_defs_resolve(t):
        """Live: cindermare/skarnix defs and the cold-drain wound chain loaded."""
        with t.component("predators_defs_loaded", beyond_toggle=True):
            for d in ("ThingDef/RM_Cindermare", "PawnKindDef/RM_Cindermare", "ThingDef/RM_Skarnix", "PawnKindDef/RM_Skarnix",
                      "DamageDef/RM_ColdDrainDamage", "HediffDef/RM_ColdDrain"):
                r = t.bridge_call("jawa/get_defs", defs=d)
                if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                    raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
    @suite.chain("lamp_crops_fold_lamp")
    def lamp_crops_fold_lamp(t):
        """Live: wickwood/fold-lamp/research defs load; state reads of the wickwood setting, and (with a lit fold-lamp on the
        current map) the lane clearance near/far/behind. Expected: overlight=4.5 wildInAbyss=True; near=1.00 far>0 behind=0.00."""
        with t.component("light_defs_loaded", beyond_toggle=True):
            for d in ("ThingDef/RM_Wickwood", "ThingDef/RM_FoldLamp", "ThingDef/RM_TheDarkItself",
                      "ResearchProjectDef/RM_HeatFolding", "ResearchProjectDef/RM_DarkFoldsFromWarmth"):
                r = t.bridge_call("jawa/get_defs", defs=d)
                if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                    raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
        with t.component("wickwood_state", beyond_toggle=True):
            r = t.bridge_call("jawa/static_call", type="RimMandrake.Abyss.RM_AbyssLightProof", method="ProofWickwood")
            if t._guard() and "overlight=4.5" not in str(r):
                raise ExpectationFailed("wickwood overlight not in force: %r" % (r,))

    @suite.chain("gust_soundscape")
    def gust_soundscape(t):
        """Live: the four sound defs load. On an Abyss map, ProofGust forces a gust; a second read a few seconds later should
        show impacts+1. Whether it SOUNDS right is judged with the owner present."""
        with t.component("sound_defs_loaded", beyond_toggle=True):
            for d in ("SoundDef/RM_AbyssGustImpact", "SoundDef/RM_AbyssGillRustle", "SoundDef/RM_AbyssGrainTick", "SoundDef/RM_AbyssLampClatter"):
                r = t.bridge_call("jawa/get_defs", defs=d)
                if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                    raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
    @suite.chain("cryptid")
    def cryptid(t):
        """ABYSS_FREE_CRYPTID_1, live. The name resolves from the one pack (campaign build: a whisper may name the Sith);
        an unwatched item on a ring is swapped and a watched one is not; a clear pocket opens over nothing. Run with no
        colonist near the map centre for the unwatched read; the art tale and the dream are a joint look with the owner."""
        def _c(method):
            r = t.bridge_call("jawa/static_call", type="RimMandrake.Abyss.RM_MapComponent_AbyssCryptid", method=method, args="current")
            return str((r or {}).get("result", ""))
        with t.component("cryptid_defs_loaded", beyond_toggle=True):
            for d in ("RulePackDef/RM_AbyssCryptid", "InteractionDef/RM_AbyssWhisper", "TaleDef/RM_WhisperedInTheDark",
                      "ThoughtDef/RM_DreamtNoLight", "GenStepDef/RM_AbyssRumorSites"):
                r = t.bridge_call("jawa/get_defs", defs=d)
                if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                    raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
        with t.component("name_from_one_pack", beyond_toggle=True):
            txt = _c("ProofName")
            if t._guard() and "NAME the Nhaleth" not in txt:
                raise ExpectationFailed("the cryptid name did not resolve from RM_AbyssCryptid: %r" % txt)
        with t.component("exchange_never_watched", beyond_toggle=True):
            txt = _c("ProofExchange")
            if t._guard() and not (("watched=False swapped=1" in txt) or ("watched=True swapped=0" in txt)):
                raise ExpectationFailed("exchange broke the watched rule or did nothing: %r" % txt)
        with t.component("clear_pocket_around_nothing", beyond_toggle=True):
            txt = _c("ProofPhantom")
            if t._guard() and (not txt.startswith("PHANTOM") or "clearance=1.00" not in txt):
                raise ExpectationFailed("no clear pocket opened: %r" % txt)
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
    fb = freed_beasts_check()
    print("FREED BEASTS static: %s" % ("PASS" if not fb else "FAIL " + "; ".join(fb)))
    print("KRIZZAK static: %s" % ("PASS" if not k else "FAIL " + "; ".join(k)))
    r = dark_check()
    print("DARK static: %s" % ("PASS" if not r else "FAIL " + "; ".join(r)))
    v = cover_check()
    print("SHIP COVER static: %s" % ("PASS" if not v else "FAIL " + "; ".join(v)))
    pr = predators_check()
    print("PREDATORS static: %s" % ("PASS" if not pr else "FAIL " + "; ".join(pr)))
    lc = light_check()
    print("LAMP CROPS + FOLD LAMP static: %s" % ("PASS" if not lc else "FAIL " + "; ".join(lc)))
    ss = soundscape_check()
    print("SOUNDSCAPE static: %s" % ("PASS" if not ss else "FAIL " + "; ".join(ss)))
    cy = cryptid_check()
    print("CRYPTID static: %s" % ("PASS" if not cy else "FAIL " + "; ".join(cy)))
    bl = brood_check()
    print("BROOD LAIR static: %s" % ("PASS" if not bl else "FAIL " + "; ".join(bl)))
    sys.exit(1 if (f or g or d or e or k or r or v or pr or lc or ss or cy or bl) else 0)
