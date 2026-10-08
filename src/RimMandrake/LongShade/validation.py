"""validation.py -- modcheck suite for RimMandrake: Long Shade (mandrake.rm.longshade).

First north-star script (LONG_SHADE_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/LongShade.md.
A dayside desert biome (RM_LongShade) with 22 native creatures, 5 native plants, the vorrel cycle plant, two map
generation steps (Crawler Road, Sun Graves), the Shipfall Commons think tree and a Harmony rim gate for the dewfringe.
Fold-aware: when folded into mandrake.rm.biomes the mod is active under the composed name 'RimMandrake: Baroque Biomes';
every read here is by def name / Harmony id, never by mod name.

CHAINS
  defs_resolve       every def under Defs/ (parsed from the XML) resolves live; a control name reads notFound.
  settings_roundtrip every `public static` bool the C# declares (RM_LongShadeSettings): default / write / restore.
  biome_wiring       RM_LongShade's animalDensity and plantDensity are > 0 (animalDensity 0 would make the whole roster dead
                     content) and both gen steps resolve.
  dewfringe_gate     the Harmony postfix on WildPlantSpawner.CalculatePlantsWhichCanGrowAt is attached by this mod.
  dewfringe_gate     also: the gate's C# reads both toggles and removes the plant by ShadeAt.
  map_mechanics      Crawler Road, Sun Graves, Shipfall Commons, mirrak ambush, vorrel cycle: each has an asserting wiring component
                     (toggle gate in the C#, def graph, live resolve) plus an UNMEASURED behaviour component naming its missing tool.
  roster_wiring      every shipped creature race / plant is in the biome roster; every PawnKindDef resolves live.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import contextlib
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.LongShade.RM_LongShadeSettings"
HARMONY_ID = "mandrake.rm.longshade"
BIOME = "RM_LongShade"
CONTROL_ABSENT = "ThingDef/RM_LongShadeNoSuchDef_ZZ"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")


def shipped_defs():
    """[(DefType, defName)] for every non-abstract top-level def under Defs/, from the XML (never a hand list)."""
    out = []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    nm = el.find("defName") if isinstance(el.tag, str) else None
                    if nm is not None and nm.text and el.get("Abstract", "").lower() != "true":
                        out.append((el.tag, nm.text.strip()))
    return sorted(set(out))


SHIPPED = shipped_defs()


def settings_fields():
    """{name: type} for every scalar `public static` field of RM_LongShadeSettings, read from the C#."""
    src = open(os.path.join(HERE, "Source", "RM_LongShadeMod.cs"), encoding="utf-8").read()
    body = src.split("class RM_LongShadeSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def static_checks():
    bad = []
    if len(SHIPPED) < 10:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if not fields:
        return ["settings probe found no scalar field (sanity probe failed)"]
    src = open(os.path.join(HERE, "Source", "RM_LongShadeMod.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    proj = open(os.path.join(HERE, "Source", "RM_LongShade.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    kinds = set(ty for ty, _n in SHIPPED)
    for need in ("BiomeDef", "GenStepDef", "ThingDef", "PawnKindDef", "HediffDef", "RecipeDef"):
        if need not in kinds:
            bad.append("no %s parsed" % need)
    if (("BiomeDef", BIOME)) not in SHIPPED:
        bad.append("BiomeDef %s missing" % BIOME)
    biome = ET.parse(os.path.join(HERE, "Defs", "BiomeDefs", "RM_LongShade.xml")).getroot()
    if not float(biome.findtext(".//animalDensity") or 0) > 0:
        bad.append("animalDensity is 0: the roster is dead content")
    gs = ET.parse(os.path.join(HERE, "Defs", "MapGeneration", "RM_LongShade_GenSteps.xml")).getroot()
    mapgen = open(os.path.join(HERE, "Source", "RM_LongShadeMapgen.cs"), encoding="utf-8").read()
    for g in gs.iter("genStep"):
        cls = g.get("Class", "").split(".")[-1]
        if "class %s" % cls not in mapgen:
            bad.append("gen step class %s not found in RM_LongShadeMapgen.cs" % cls)
    if "WildPlantSpawner" not in open(os.path.join(HERE, "Source", "RM_Patch_DewfringeWildSpawnGate.cs"), encoding="utf-8").read():
        bad.append("dewfringe gate no longer patches WildPlantSpawner")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "LongShade.md")):
        bad.append("walk missing")
    for fn in (crawler_road_problems, sun_graves_problems, shipfall_problems, mirrak_problems, vorrel_problems,
               dewfringe_problems, roster_problems, midden_problems):
        bad.extend(fn())
    return bad


def _cs(name):
    return open(os.path.join(HERE, "Source", name), encoding="utf-8").read()


def _xml(*rel):
    return ET.parse(os.path.join(HERE, "Defs", *rel)).getroot()


def _def(root, tag, name):
    for el in root.iter(tag):
        if el.findtext("defName") == name:
            return el
    return None


def _shipped_names(ty):
    return set(n for t, n in SHIPPED if t == ty)


def crawler_road_defs():
    gs = _def(_xml("MapGeneration", "RM_LongShade_GenSteps.xml"), "GenStepDef", "RM_GenStep_CrawlerRoad")
    step = gs.find("genStep")
    rows = []
    wl = step.findtext("wreckList")
    if wl:  # SALVAGE_WRECKAGE_EVERYWHERE_1 step 7: the road's casualties list (element-name rows)
        lst = _def(_xml("RM_WreckListDefs", "RM_CrawlerRoadWreckList.xml"), "RimMandrake.Wreckage.RM_WreckListDef", wl.strip())
        rows = [r.tag for r in lst.find("wrecks")] if lst is not None and lst.find("wrecks") is not None else ["<missing list %s>" % wl]
    return [e.text.strip() for e in step.iter("li")] + rows + [step.findtext("terminusMarker").strip()]


def crawler_road_problems():
    bad, mapgen = [], _cs("RM_LongShadeMapgen.cs")
    gen = mapgen.split("class RM_GenStep_CrawlerRoad", 1)[1].split("class RM_CrawlerRoadLogic", 1)[0]
    if "crawlerRoadEnabled" not in gen or "modEnabled" not in gen or "return;" not in gen.split("Lay(", 1)[0]:
        bad.append("Crawler Road Generate() no longer returns early on modEnabled/crawlerRoadEnabled (off arm lays a road)")
    if "RM_CrawlerRoadLogic.Lay(" not in gen:
        bad.append("Crawler Road Generate() never calls Lay (the step does nothing when on)")
    biome = _def(_xml("BiomeDefs", "RM_LongShade.xml"), "BiomeDef", BIOME)
    if "RM_GenStep_CrawlerRoad" not in [e.text for e in biome.find("extraGenSteps")]:
        bad.append("RM_LongShade.extraGenSteps does not name RM_GenStep_CrawlerRoad (step never runs)")
    for n in crawler_road_defs():
        if n not in _shipped_names("ThingDef"):
            bad.append("crawler road def %s is not a shipped ThingDef" % n)
    # Every road wreck is shade: the shade grid's caster scan reads staticSunShadowHeight.
    links = [n for n in crawler_road_defs() if n != "RM_CrawlerRoadTerminus"]
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs", "ThingDefs_Buildings")):
        for fn in files:
            for el in ET.parse(os.path.join(dp, fn)).getroot().iter("ThingDef"):
                if el.findtext("defName") in links and not el.findtext("staticSunShadowHeight"):
                    bad.append("crawler road wreck %s casts no shade (no staticSunShadowHeight)" % el.findtext("defName"))
    if "step.wreckList.PickWreck()" not in mapgen:
        bad.append("Crawler Road never reads its wreckList (SALVAGE_WRECKAGE_EVERYWHERE_1 step 7)")
    return bad


def sun_graves_problems():
    bad, mapgen = [], _cs("RM_LongShadeMapgen.cs")
    gen = mapgen.split("class RM_GenStep_SunGraves", 1)[1].split("class RM_SunGravesLogic", 1)[0]
    if "sunGravesEnabled" not in gen or "modEnabled" not in gen or "return;" not in gen.split("Lay(", 1)[0]:
        bad.append("Sun Graves Generate() no longer returns early on modEnabled/sunGravesEnabled (off arm lays graves)")
    if "RM_SunGravesLogic.Lay(" not in gen:
        bad.append("Sun Graves Generate() never calls Lay (the step does nothing when on)")
    biome = _def(_xml("BiomeDefs", "RM_LongShade.xml"), "BiomeDef", BIOME)
    if "RM_GenStep_SunGraves" not in [e.text for e in biome.find("extraGenSteps")]:
        bad.append("RM_LongShade.extraGenSteps does not name RM_GenStep_SunGraves (step never runs)")
    step = _def(_xml("MapGeneration", "RM_LongShade_GenSteps.xml"), "GenStepDef", "RM_GenStep_SunGraves").find("genStep")
    if not step.find("load") is not None or len(list(step.find("load"))) < 1:
        bad.append("Sun Graves carries no load (a grave with nothing in it)")
    if not step.findall("travellerKinds/li"):
        bad.append("Sun Graves names no travellerKinds")
    return bad


def shipfall_problems():
    bad, src = [], _cs("RM_ShipfallCommons.cs")
    if "shipfallCommonsEnabled" not in src.split("class RM_JobGiver_ShipfallCommons", 1)[1].split("TryGiveJob", 1)[1][:400]:
        bad.append("RM_JobGiver_ShipfallCommons.TryGiveJob no longer gates on shipfallCommonsEnabled (off arm still gathers)")
    if "shipfallCommonsEnabled" not in src.split("bool Active", 1)[1].split(";", 1)[0]:
        bad.append("RM_MapComponent_ShipfallCommons.Active no longer gates on shipfallCommonsEnabled")
    tt = _def(_xml("ThinkTreeDefs", "RM_LongShade_ShipfallCommons.xml"), "ThinkTreeDef", "RM_ThinkTree_ShipfallCommons")
    if tt is None or tt.findtext("insertTag") != "Animal_PreWander":
        bad.append("think tree does not insert into Animal_PreWander (wildlife never consults it)")
    elif "RimMandrake.LongShade.RM_JobGiver_ShipfallCommons" not in ET.tostring(tt, encoding="unicode"):
        bad.append("think tree does not hold RM_JobGiver_ShipfallCommons")
    biome = _def(_xml("BiomeDefs", "RM_LongShade.xml"), "BiomeDef", BIOME)
    ext = [e for e in biome.iter("li") if e.get("Class") == "RimMandrake.LongShade.RM_ShipfallCommonsExtension"]
    if len(ext) != 1:
        bad.append("RM_LongShade carries %d RM_ShipfallCommonsExtension (want 1)" % len(ext))
        return bad
    hours = [float(s.findtext("afterHours")) for s in ext[0].findall("stages/li")]
    if len(hours) < 2 or hours != sorted(hours) or len(set(hours)) != len(hours):
        bad.append("shipfall rungs are not strictly ascending by afterHours: %r" % hours)
    if not float(ext[0].findtext("dispersalDistance") or 0) > 0:
        bad.append("dispersalDistance is not > 0 (animals would never scatter)")
    return bad


def midden_problems():
    """LONGSHADE_MIDDENS_DESIGN_1: heap def, vrekka builder wiring, toggle gates, vanilla-only yields."""
    bad, src = [], _cs("RM_LongShadeMiddens.cs")
    root = _xml("ThingDefs_Buildings", "RM_LongShade_Middens.xml")
    heap = _def(root, "ThingDef", "RM_LongShadeMidden")
    if heap is None:
        return ["RM_LongShadeMidden ThingDef missing"]
    comp = [e for e in heap.iter("li") if e.get("Class") == "RimMandrake.LongShade.CompProperties_RM_MiddenHeap"]
    if len(comp) != 1:
        return ["RM_LongShadeMidden carries %d CompProperties_RM_MiddenHeap (want 1)" % len(comp)]
    c = comp[0]
    builders = [e.text for e in c.findall("builderRaces/li")]
    if "RM_Vrekka" not in builders:
        bad.append("midden builderRaces does not name RM_Vrekka (ruled: the vrekka builds the heaps)")
    if "RM_Vrekka" not in _shipped_names("ThingDef"):
        bad.append("RM_Vrekka is not a shipped ThingDef")
    ylds = [y.findtext("thing") for y in c.findall("yields/li")]
    if len(ylds) < 3:
        bad.append("midden yields table has %d rows" % len(ylds))
    own = set(n for _t, n in SHIPPED)
    for y in ylds:
        if y in own or y.startswith(("RM_", "RSW_", "RUT_")):
            bad.append("midden yields %s, not a vanilla item (ruled: vanilla items only)" % y)
    if not float(c.findtext("tendGain") or 0) > 0 or not int(c.findtext("maxLayers") or 0) > 0:
        bad.append("midden tendGain/maxLayers not > 0 (heaps never regrow)")
    for d in ("RM_VrekkaTendMidden", "RM_SearchMidden"):
        if _def(root, "JobDef", d) is None:
            bad.append("JobDef %s missing" % d)
    if _def(root, "WorkGiverDef", "RM_SearchMidden") is None:
        bad.append("WorkGiverDef RM_SearchMidden missing (colonists can never search)")
    tt = _def(root, "ThinkTreeDef", "RM_VrekkaMiddenInsert")
    if tt is None or tt.findtext("insertTag") != "Animal_PreMain" or \
            "RimMandrake.LongShade.JobGiver_RM_VrekkaMidden" not in ET.tostring(tt, encoding="unicode"):
        bad.append("vrekka midden think-tree insert missing or not at Animal_PreMain")
    giver = src.split("class JobGiver_RM_VrekkaMidden", 1)[1].split("class JobDriver_RM_VrekkaTendMidden", 1)[0]
    if "if (RM_LongShadeSettings.middenVrekkaBuildEnabled) TryBuildHeap(" not in giver:
        bad.append("heap building no longer gated on middenVrekkaBuildEnabled")
    if "!RM_LongShadeSettings.middenRegrowthEnabled) return null;" not in giver:
        bad.append("tending (the regrowth) no longer gated on middenRegrowthEnabled")
    if "RM_LongShadeSettings.modEnabled" not in giver or "IsBuilder(pawn.def)" not in giver:
        bad.append("vrekka giver lost its modEnabled / builder-race gate")
    heapcls = src.split("class RM_CompMiddenHeap", 1)[1].split("class RM_LongShadeMiddenDefOf", 1)[0]
    kernel = open(os.path.join(HERE, "Source", "Kernel", "RM_LongShadeKernel.cs"), encoding="utf-8").read()
    tend_body = heapcls.split("void Tend()", 1)[1].split("void Search", 1)[0]
    if "RM_LongShadeKernel.Tend(" not in tend_body or "layers++" not in kernel.split("public static void Tend(", 1)[1].split("public static int SearchRolls", 1)[0]:
        bad.append("Tend() no longer adds layers (regrowth broken): the heap must call RM_LongShadeKernel.Tend, which does layers++")
    if "TicksGame" in heapcls.split("CompTick", 1)[-1] and "CompTick" in heapcls:
        bad.append("heap has a CompTick: regrowth must come only from vrekka tending (ruled)")
    return bad


def mirrak_problems():
    bad = []
    root = _xml("ThingDefs_Races", "RM_LongShade_Mirrak.xml")
    race = _def(root, "ThingDef", "RM_Mirrak")
    if race is None or _def(root, "PawnKindDef", "RM_Mirrak") is None:
        return ["RM_Mirrak ThingDef or PawnKindDef missing"]
    cls = [e.get("Class", "") for e in race.iter("li")]
    if "RimMandrake.CreatureBehaviors.RM_FalseShadeExtension" not in cls:
        bad.append("mirrak lost RM_FalseShadeExtension (its cells no longer read as shade)")
    if "RimMandrake.CreatureBehaviors.CompProperties_FalseShadeAmbusher" not in cls:
        bad.append("mirrak lost CompProperties_FalseShadeAmbusher (it never strikes)")
    amb = [e for e in race.iter("li") if e.get("Class", "").endswith("CompProperties_FalseShadeAmbusher")]
    if amb and not float(amb[0].findtext("strikeRangeCells") or 0) > 0:
        bad.append("mirrak strikeRangeCells is not > 0")
    if "RM_Mirrak" not in [e.tag for e in _def(_xml("BiomeDefs", "RM_LongShade.xml"), "BiomeDef", BIOME).find("wildAnimals")]:
        bad.append("mirrak is not in the biome roster")
    return bad


def vorrel_problems():
    """The cycle as a graph: plant -> fruit (-> brood hediff) -> recipe -> seed dish (-> euphoria hediff) -> thought."""
    bad = []
    plant = _def(_xml("ThingDefs_Plants", "RM_Vorrel.xml"), "ThingDef", "RM_Vorrel")
    items = _xml("ThingDefs_Items", "RM_Vorrel_Items.xml")
    recipe = _def(_xml("RecipeDefs", "RM_Vorrel_Recipes.xml"), "RecipeDef", "RM_Cook_VorrelSeedDish")
    thought = _def(_xml("ThoughtDefs", "RM_Vorrel_Thoughts.xml"), "ThoughtDef", "RM_VorrelEuphoriaThought")
    if plant is None or recipe is None or thought is None:
        return ["vorrel plant, recipe or thought def missing"]
    if plant.findtext("plant/harvestedThingDef") != "RM_VorrelFruit":
        bad.append("RM_Vorrel does not harvest RM_VorrelFruit")
    for item, hediff in (("RM_VorrelFruit", "RM_VorrelBrood"), ("RM_VorrelSeedDish", "RM_VorrelEuphoria")):
        d = _def(items, "ThingDef", item)
        if d is None or hediff not in [e.text for e in d.iter("hediffDef")]:
            bad.append("%s no longer gives %s when eaten" % (item, hediff))
    if "RM_VorrelFruit" not in [e.text for e in recipe.findall("ingredients/li/filter/thingDefs/li")]:
        bad.append("the recipe's ingredient is not RM_VorrelFruit")
    if recipe.find("products/RM_VorrelSeedDish") is None:
        bad.append("the recipe does not produce RM_VorrelSeedDish")
    if thought.findtext("hediff") != "RM_VorrelEuphoria":
        bad.append("the thought no longer reads RM_VorrelEuphoria")
    hed = _def(_xml("HediffDefs", "RM_Vorrel_Hediffs.xml"), "HediffDef", "RM_VorrelEuphoria")
    n_h, n_t = len(hed.findall("stages/li")), len(thought.findall("stages/li"))
    if n_t < n_h - 1:
        bad.append("thought has %d stages for a hediff of %d (a stage can index past the thought)" % (n_t, n_h))
    return bad


def dewfringe_problems():
    src = _cs("RM_Patch_DewfringeWildSpawnGate.cs")
    bad = []
    if "dewfringeShadeLineGateEnabled" not in src or "modEnabled" not in src:
        bad.append("dewfringe gate no longer reads its toggles")
    if "ShadeAt" not in src or "RemoveAt" not in src:
        bad.append("dewfringe gate no longer tests ShadeAt and removing the plant from the candidates")
    if _def(_xml("ThingDefs_Plants", "RM_Dewfringe.xml"), "ThingDef", "RM_Dewfringe") is None:
        bad.append("RM_Dewfringe ThingDef missing")
    return bad


# Defs LongShade still ships but whose roster row moved to another biome at the 2026-10-04 sheet
# (commits dfc35ba68 Ommok, 0e98ccfdf Vosska, d2a4879b5 Ulgga, b5df5f05d TruffleMole, 1b0aba6b1 UltrissPad).
# Each must be in that biome's roster instead: (def, biome mod folder, biome file, roster element).
MOVED_ROWS = (
    ("RM_Ommok", "Miasma", "RM_Miasma.xml", "wildAnimals"),
    ("RM_Vosska", "Stillsand", "RM_Stillsand_Biome.xml", "wildAnimals"),
    ("RM_Ulgga", "Stillsand", "RM_Stillsand_Biome.xml", "wildAnimals"),
    ("RM_TruffleMole", "LeaningScrub", "RM_LeaningScrub_Biome.xml", "wildAnimals"),
    ("RM_UltrissPad", "Stillsand", "RM_Stillsand_Biome.xml", "wildPlants"),
)


def _moved_row_home(name):
    for nm, mod, fn, elem in MOVED_ROWS:
        if nm != name:
            continue
        path = os.path.join(HERE, "..", mod, "Defs", "BiomeDefs", fn)
        if not os.path.isfile(path):
            return False
        for el in ET.parse(path).getroot().iter(elem):
            if any(e.tag == nm for e in el):
                return True
        return False
    return None


def roster_problems():
    """Every shipped creature race and plant is named in the biome's roster (a def nobody can spawn is dead content)."""
    biome = _def(_xml("BiomeDefs", "RM_LongShade.xml"), "BiomeDef", BIOME)
    animals = set(e.tag for e in biome.find("wildAnimals"))
    plants = set(e.tag for e in biome.find("wildPlants"))
    bad = []
    for sub, tag, key, have in (("ThingDefs_Races", "race", "creature", animals), ("ThingDefs_Plants", "plant", "plant", plants)):
        found = 0
        for fn in sorted(os.listdir(os.path.join(HERE, "Defs", sub))):
            for el in _xml(sub, fn):
                nm = el.findtext("defName") if isinstance(el.tag, str) else None
                if el.tag == "ThingDef" and el.find(tag) is not None and nm and el.get("Abstract", "").lower() != "true":
                    found += 1
                    home = _moved_row_home(nm) if nm not in have else True
                    if home is False:
                        bad.append("%s %s moved to another biome but is not in that roster" % (key, nm))
                    elif nm not in have and home is None:
                        bad.append("%s %s is not in the biome roster" % (key, nm))
        if found < 4:
            bad.append("only %d %ss parsed (sanity probe failed)" % (found, key))
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


def _build_suite():
    suite = Suite("LongShade")
    suite.toggles = sorted(settings_fields())

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _unmeasured(t, why):
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _raw(t, action, field, value=None):
        if value is not None:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field, value=str(value))
        else:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field)
        return r if isinstance(r, dict) else {}

    def _same(ty, a, b):
        if ty == "bool":
            return str(a).lower() == str(b).lower()
        return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present: %r" % r)
        with t.component("every_shipped_def_resolves", beyond_toggle=True):
            names = ["%s/%s" % p for p in SHIPPED]
            missing, ok = [], 0
            for i in range(0, len(names), 40):      # batches: a long defs string risks the 30 s reply timeout
                chunk = names[i:i + 40]
                r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields="defName", limit=60)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed: %r" % r)
                missing.extend(r.get("notFound") or [])
                ok += int(r.get("foundCount", 0))
            if _live(t) and (missing or ok != len(names)):
                raise ExpectationFailed("%d of %d defs resolved; notFound=%r" % (ok, len(names), missing[:8]))

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with t.component("settings_probe_finds_fields", beyond_toggle=True):
            if len(settings_fields()) < 1:
                raise ExpectationFailed("settings probe found no field (blind regex)")
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                if ty == "bool":
                    new = "False" if str(old).lower() == "true" else "True"
                elif ty == "int":
                    new = str(int(float(old)) + 1)       # an Int32 field refuses "25.0" (LIVE 2026-10-03)
                else:
                    new = str(float(old) + 1.0)
                try:
                    if not _raw(t, "set", field, new).get("success"):
                        raise ExpectationFailed("%s: set failed" % field)
                    back = _raw(t, "get", field).get("value")
                    if not _same(ty, back, new):
                        raise ExpectationFailed("%s: wrote %s, read %r" % (field, new, back))
                finally:
                    _raw(t, "set", field, old)
                back = _raw(t, "get", field).get("value")
                if not _same(ty, back, old):
                    raise ExpectationFailed("%s did not restore to %r (read %r)" % (field, old, back))

    @suite.chain("biome_wiring")
    def biome_wiring(t):
        with t.component("animal_and_plant_density_positive", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="BiomeDef/" + BIOME, fields="animalDensity,plantDensity", limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows:
                    raise ExpectationFailed("could not read %s: %r" % (BIOME, r))
                f = rows[0].get("fields") or {}
                try:
                    ad, pd = float(f.get("animalDensity")), float(f.get("plantDensity"))
                except (TypeError, ValueError):
                    _unmeasured(t, "get_defs did not return numeric densities: %r" % (f,))
                    return
                if not ad > 0:
                    raise ExpectationFailed("animalDensity %s: the roster would never spawn" % ad)
                if not pd > 0:
                    raise ExpectationFailed("plantDensity %s: the flora would never spawn" % pd)
        with t.component("gen_steps_resolve", beyond_toggle=True):
            names = ["GenStepDef/%s" % n for ty, n in SHIPPED if ty == "GenStepDef"]
            r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields="defName", limit=10)
            if _live(t) and (not isinstance(r, dict) or r.get("notFound") or int(r.get("foundCount", 0)) != len(names)):
                raise ExpectationFailed("gen steps did not resolve: %r" % r)

    @suite.chain("dewfringe_gate")
    def dewfringe_gate(t):
        with t.component("rim_gate_postfix_attached", toggle="dewfringeShadeLineGateEnabled"):
            r = t.bridge_call("jawa/harmony_patches", typeName="WildPlantSpawner", methodName="CalculatePlantsWhichCanGrowAt")
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is not True or r.get("harmonyError"):
                    _unmeasured(t, "harmony_patches could not be asked: %s" % str(r)[:160])
                    return
                owners = []
                for m in (r.get("methods") or []):
                    owners.extend(p.get("owner") for p in (m.get("postfixes") or []))
                if HARMONY_ID not in owners:
                    raise ExpectationFailed("WildPlantSpawner.CalculatePlantsWhichCanGrowAt carries no postfix from %s (owners: %s)"
                                            % (HARMONY_ID, sorted(set(o for o in owners if o))[:8]))
        with t.component("rim_gate_logic_wired", toggle="dewfringeShadeLineGateEnabled"):
            _fail_on(dewfringe_problems())
        with t.component("rim_only_growth_on_a_long_shade_map", toggle="modEnabled"):
            if _live(t):
                _unmeasured(t, "wild dewfringe appearing only on shade-boundary cells needs a generated RM_LongShade map "
                               "with shade patches (CreatureBehaviors shade grid)")

    def _resolve_live(t, names, what):
        """Live: every 'DefType/Name' resolves (reads foundCount/notFound, never a substring)."""
        r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields="defName", limit=60)
        if _live(t):
            if not isinstance(r, dict) or r.get("success") is False:
                raise ExpectationFailed("%s: get_defs failed: %r" % (what, r))
            if r.get("notFound") or int(r.get("foundCount", 0)) != len(names):
                raise ExpectationFailed("%s did not resolve: notFound=%r" % (what, r.get("notFound")))

    def _fail_on(problems):
        if problems:
            raise ExpectationFailed("; ".join(problems))

    @suite.chain("map_mechanics")
    def map_mechanics(t):
        with t.component("crawler_road_wiring_and_gate", toggle="crawlerRoadEnabled"):
            _fail_on(crawler_road_problems())
            _resolve_live(t, ["ThingDef/%s" % n for n in crawler_road_defs()], "crawler road link/terminus defs")
        with t.component("crawler_road_laid_at_mapgen", toggle="crawlerRoadEnabled"):
            if _live(t):
                _unmeasured(t, "a line of wrecks across the widest shade gap exists only on a map GENERATED as RM_LongShade with the "
                               "toggle on, and none with it off; jawa/run_genstep runs a gen step on the CURRENT map but no tool "
                               "generates an RM_LongShade map to run it on")
        with t.component("sun_graves_wiring_and_gate", toggle="sunGravesEnabled"):
            _fail_on(sun_graves_problems())
            _resolve_live(t, ["PawnKindDef/Drifter", "PawnKindDef/Dromedary", "ThingDef/Silver", "ThingDef/ComponentIndustrial",
                              "ThingDef/MedicineHerbal", "ThingDef/Pemmican", "ThingDef/Novel"], "sun-grave kinds, load and readable")
        with t.component("sun_graves_laid_at_mapgen", toggle="sunGravesEnabled"):
            if _live(t):
                _unmeasured(t, "sun-grave corpses with their load exist only on a generated RM_LongShade map; no tool generates one "
                               "(same missing instrument as crawler_road_laid_at_mapgen)")
        with t.component("shipfall_commons_wiring_and_gate", toggle="shipfallCommonsEnabled"):
            _fail_on(shipfall_problems())
            _resolve_live(t, ["ThinkTreeDef/RM_ThinkTree_ShipfallCommons", "BiomeDef/" + BIOME], "think tree and biome")
        with t.component("shipfall_commons_draws_wildlife", toggle="shipfallCommonsEnabled"):
            if _live(t):
                _unmeasured(t, "wildlife gathering round a landed gravship in rungs, and scattering when a pilot takes the console, needs a "
                               "landed gravship on an RM_LongShade map (jawa/gravship_land) and game hours of ticks (jawa/time_set_ticks); "
                               "no tool reads a map component's admitted-animal state")
        with t.component("mirrak_ambush_wiring", beyond_toggle=True):
            _fail_on(mirrak_problems())
            _resolve_live(t, ["ThingDef/RM_Mirrak", "PawnKindDef/RM_Mirrak", "ThingDef/RM_Filth_DragMark"], "mirrak defs and seize filth")
        with t.component("mirrak_false_shade_ambush", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "the mirrak ambush is a CreatureBehaviors mechanism (falseShadeAmbushEnabled there); no tool reads the "
                               "false-shade state or a comp's strike; jawa/shadegrid_read needs a live shade patch, a mirrak and a passing pawn")
        with t.component("vorrel_cycle_chain_wired", beyond_toggle=True):
            _fail_on(vorrel_problems())
            _resolve_live(t, ["ThingDef/RM_Vorrel", "ThingDef/RM_VorrelFruit", "ThingDef/RM_VorrelSeedDish", "RecipeDef/RM_Cook_VorrelSeedDish",
                              "HediffDef/RM_VorrelBrood", "HediffDef/RM_VorrelEuphoria", "ThoughtDef/RM_VorrelEuphoriaThought"], "vorrel cycle defs")
        with t.component("vorrel_cycle", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "the vorrel's seasonal growth, eating the fruit/dish and the thought firing need game days "
                               "(jawa/time_set_ticks) and nothing drives a meal of the dish on a pawn")

    @suite.chain("roster_wiring")
    def roster_wiring(t):
        with t.component("every_creature_and_plant_is_in_the_biome_roster", beyond_toggle=True):
            _fail_on(roster_problems())
        with t.component("every_pawnkind_resolves", beyond_toggle=True):
            kinds = ["PawnKindDef/%s" % n for ty, n in SHIPPED if ty == "PawnKindDef"]
            for i in range(0, len(kinds), 40):
                _resolve_live(t, kinds[i:i + 40], "pawn kinds")

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
