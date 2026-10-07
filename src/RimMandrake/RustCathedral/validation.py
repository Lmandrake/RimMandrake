"""validation.py -- modcheck suite for RimMandrake: the Rust Cathedral (mandrake.rm.rustcathedral).

First north-star script (RUST_CATHEDRAL_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/RustCathedral.md
(`## must be true`, agent-owned, not hashed). Process: design/RimMandrake/debug_process.md section 2.

The mod: a mechanoid-garrisoned plateau biome (RM_RustCathedral) that absorbed two former kits, the Hum
(attitude value voiced as hum layers, living bolts, bolt-shed curiosities, coolant-eel fishing consequences, the
deep-drill response) and the Walls (deck plate, dead smartsteel, sacred wall, live pattern metal), plus the
cathedral roaches. Fold-aware: when folded into mandrake.rm.biomes the mod is active under the composed name
'RimMandrake: Baroque Biomes'; every read here is by def name / Harmony id / settings type, never by mod name.

CHAINS
  defs_resolve        every def under Defs/ (parsed from the XML) resolves live; a control reads notFound; the one
                      namespaced def class (the attitude def) is read separately and says UNMEASURED if the tool
                      cannot take its type name.
  settings_roundtrip  every `public static` scalar of the THREE settings classes (own / Hum / Walls), found by regex.
  biome_wiring        animalDensity > 0, roster rows, fishTypes and forceRockTypes land, wildPlants stays EMPTY
                      (ruled zero, never a gap), the wall scatter steps are on MapCommonBase.
  hum_attitude        the attitude def targets this biome and carries the five-band thresholds.
  harmony_gates       the Walls deep-scan gate and the Hum watched-bolt / fishing / infestation hooks are installed.
  roach_gate          the roach think tree carries the cleaning toggle node ahead of the eat-cleanable node.
  map_mechanics       bolt dance and freeze, curiosity pricing, eel fishing consequence, drill response, wall tiers
                      at mapgen: UNMEASURED, each says what it needs (a generated RM_RustCathedral map, game time).

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
BIOME = "RM_RustCathedral"
CONTROL_ABSENT = "ThingDef/RM_RustCathedralNoSuchDef_ZZ"
OWN_SETTINGS = "RimMandrake.RustCathedral.RM_RustCathedralSettings"
HUM_SETTINGS = "RimMandrake.RustCathedral.Hum.RustCathedralHumSettings"
WALLS_SETTINGS = "RimMandrake.RustCathedral.Walls.RustCathedralWallsSettings"
SETTINGS_SOURCES = (
    (OWN_SETTINGS, os.path.join("Source", "RustCathedral", "RM_RustCathedralMod.cs"), "RM_RustCathedralSettings"),
    (HUM_SETTINGS, os.path.join("Source", "Hum", "RustCathedralHumSettings.cs"), "RustCathedralHumSettings"),
    (WALLS_SETTINGS, os.path.join("Source", "Walls", "RustCathedralWallsSettings.cs"), "RustCathedralWallsSettings"),
)
# a real field line: `public static T name = value;` -- not `const`, not the `=>` computed properties
_FIELD = re.compile(r"public\s+static\s+(bool|int|float|string)\s+(\w+)\s*=(?!>)\s*([^;]+);")
# (typeName, methodName, expected harmony owner, what it gates)
HARMONY = (
    ("CompDeepScanner", "ChooseLumpThingDef", "mandrake.rut.rustcathedralwalls", "live pattern metal only from the cathedral's deep scans"),
    ("Pawn", "Kill", "mandrake.rut.rustcathedralhum", "killing a living bolt irritates the hum"),
    ("CompSpawner", "TryDoSpawn", "mandrake.rut.rustcathedralhum", "bolt shed curiosity gated by its toggle"),
    ("WaterBodyTracker", "Notify_Fished", "mandrake.rut.rustcathedralhum", "coolant eel catch consequences"),
    ("IncidentWorker_DeepDrillInfestation", "CanFireNowSub", "mandrake.rut.rustcathedralhum", "vanilla infestation replaced by the cathedral response"),
    ("Bill", "PawnAllowedToStartAnew", "mandrake.rut.rustcathedralhum", "only a hum reader writes a hum primer"),
    ("Corpse", "ButcherProducts", "mandrake.rut.rustcathedralhum", "butchering a living coolant eel counts as a catch"),
)


def _read(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as fh:
        return fh.read()


def _nocomment(src):
    return re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", src, flags=re.S))


def settings_fields():
    """{(typeName, field): (cs type, default text)} read from the three C# settings classes."""
    out = {}
    for typ, rel, cls in SETTINGS_SOURCES:
        src = _nocomment(_read(rel))
        body = src.split("class " + cls, 1)[1]
        body = body.split("ExposeData", 1)[0] if cls == "RM_RustCathedralSettings" else body
        for m in _FIELD.finditer(body):
            out[(typ, m.group(2))] = (m.group(1), m.group(3).strip())
    return out


def shipped_defs():
    """[(DefTypeTag, defName)] for every non-abstract top-level def under Defs/, from the XML."""
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
PLAIN = [(t, n) for t, n in SHIPPED if "." not in t]
NAMESPACED = [(t, n) for t, n in SHIPPED if "." in t]


def _biome():
    return ET.parse(os.path.join(HERE, "Defs", "BiomeDefs", "RM_RustCathedral_Biome.xml")).getroot().find("BiomeDef")


def static_checks():
    bad = []
    if len(SHIPPED) < 20:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if len(fields) < 14:
        return ["settings probe found %d scalar fields, floor 14 (sanity probe failed)" % len(fields)]
    own_src = _read(os.path.join("Source", "RustCathedral", "RM_RustCathedralMod.cs"))
    for (typ, name), _v in sorted(fields.items()):
        if typ == OWN_SETTINGS:
            if '"%s"' % name not in own_src:
                bad.append("own settings field %s is not Scribed" % name)
        else:
            prefix = "hum_" if typ == HUM_SETTINGS else "walls_"
            if '"%s%s"' % (prefix, name) not in own_src:
                bad.append("absorbed field %s.%s is not Scribed by RM_RustCathedralSettings (it would never persist)" % (typ.rsplit(".", 1)[1], name))
    for sub in ("RustCathedral", "Hum", "Walls"):
        d = os.path.join(HERE, "Source", sub)
        projs = [f for f in os.listdir(d) if f.endswith(".csproj")]
        proj = _read(os.path.join("Source", sub, projs[0]))
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
                bad.append("%s/%s is not in the csproj (compiles into nothing)" % (sub, fn))
    b = _biome()
    if b is None or b.findtext("defName") != BIOME:
        bad.append("BiomeDef %s not parsed" % BIOME)
    else:
        if not float(b.findtext("animalDensity") or 0) > 0:
            bad.append("animalDensity is 0: the roster is dead content")
        # floor 2: roach + living bolt; GR_Mecharat was cut by the owner on the 2026-10-05 sheet
        if len(list(b.find("wildAnimals"))) < 2:
            bad.append("wildAnimals roster has fewer than 2 rows")
        if b.find("wildPlants") is not None and len(list(b.find("wildPlants"))):
            bad.append("wildPlants is no longer empty: ruled zero (frozen sheet ban 7), a deliberate edit must update this check")
    for need in ("BiomeDef", "ThingDef", "PawnKindDef", "GenStepDef", "ThinkTreeDef", "HediffDef", "IncidentDef", "TerrainDef", "SoundDef"):
        if need not in set(t for t, _n in SHIPPED):
            bad.append("no %s parsed" % need)
    for cls in ("RM_BiomeWorker_RustCathedral", "GenStep_ScatterCathedralWallTiers", "GenStep_ScatterSacredWalls",
                "RM_ThinkNode_ConditionalRoachCleaningEnabled"):
        found = any(("class %s" % cls) in _read(os.path.join("Source", d, f))
                    for d in ("RustCathedral", "Hum", "Walls") for f in os.listdir(os.path.join(HERE, "Source", d)) if f.endswith(".cs"))
        if not found:
            bad.append("class %s not found in Source/" % cls)
    walls_src = _read(os.path.join("Source", "Walls", "HarmonyPatch_GateLivePatternMetal.cs"))
    if "ChooseLumpThingDef" not in walls_src:
        bad.append("the deep-scan gate no longer patches CompDeepScanner.ChooseLumpThingDef")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "RustCathedral.md")):
        bad.append("walk missing")
    bad.extend(borehulk_problems()[0])
    bad.extend(basefinish_problems()[0])
    bad.extend(hullbolts_problems())
    return bad


# ---- the borehulk (RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1), L0 half of its criteria -------------------------------
BOREHULK_DEFS = (("ThingDef", "RM_Borehulk"), ("PawnKindDef", "RM_Borehulk"), ("ThinkTreeDef", "RM_ThinkTree_Borehulk"),
                 ("GenStepDef", "RM_BorehulkPlacement"), ("SoundDef", "RM_BorehulkGrind"))
# a think-tree node class carrying any of these is a fight branch; the borehulk must have none
_FIGHT_WORDS = ("Fight", "Attack", "Melee", "Manhunter", "Hunt", "Berserk", "Retaliat", "AIDefend", "AIGoto")
VANILLA_DATA = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
SRC_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def _xml_files(root):
    for dp, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", "Textures", "Assemblies", "obj", "bin")]
        for fn in files:
            if fn.endswith(".xml"):
                yield os.path.join(dp, fn)


def _vanilla_mech_armour(data_root):
    """{defName: (sharp, blunt)} for every non-abstract vanilla mechanoid race, ParentName chains resolved across
    every Races_Mechanoid*.xml of every installed expansion. None when the install is unreachable (the Mac)."""
    files = [os.path.join(data_root, d, "Defs", "ThingDefs_Races", f)
             for d in (os.listdir(data_root) if os.path.isdir(data_root) else ())
             if os.path.isdir(os.path.join(data_root, d, "Defs", "ThingDefs_Races"))
             for f in os.listdir(os.path.join(data_root, d, "Defs", "ThingDefs_Races")) if f.startswith("Races_Mechanoid")]
    if not files:
        return None
    by_name, races = {}, []
    for f in files:
        for el in ET.parse(f).getroot():
            if el.tag != "ThingDef":
                continue
            if el.get("Name"):
                by_name[el.get("Name")] = el
            if el.findtext("defName") and el.get("Abstract", "").lower() != "true" and el.find("race") is not None:
                races.append(el)

    def stat(el, key):
        seen = 0
        while el is not None and seen < 20:
            v = el.findtext("statBases/" + key)
            if v is not None:
                return float(v)
            el, seen = by_name.get(el.get("ParentName")), seen + 1
        return 0.0
    return {el.findtext("defName"): (stat(el, "ArmorRating_Sharp"), stat(el, "ArmorRating_Blunt")) for el in races}


def borehulk_problems(mod_root=None, src_root=None, vanilla_data=None):
    """(problems, unmeasured). Static reads of the five defs, the ruled numbers, the roster ban, the fight-free think
    tree, the gated GenStep and the armour floor against vanilla. Arguments exist so the selftest can plant breaks in a
    temp copy; every default reads the shipped files."""
    mod_root = mod_root or HERE
    src_root = src_root or SRC_ROOT
    vanilla_data = VANILLA_DATA if vanilla_data is None else vanilla_data
    bad, unmeasured = [], []
    defs = {}
    for f in _xml_files(os.path.join(mod_root, "Defs")):
        for el in ET.parse(f).getroot():
            if isinstance(el.tag, str) and el.findtext("defName"):
                defs[(el.tag, el.findtext("defName").strip())] = el
    for key in BOREHULK_DEFS:
        if key not in defs:
            bad.append("borehulk: %s/%s not defined under Defs/" % key)
    thing = defs.get(("ThingDef", "RM_Borehulk"))
    if thing is not None:
        race = thing.find("race")
        size = float(race.findtext("baseBodySize") or 0) if race is not None else 0
        if size < 5:
            bad.append("borehulk: baseBodySize %s < 5 (item: about 6)" % size)
        if race is None or race.findtext("manhunterOnDamageChance", "").strip() not in ("0", "0.0"):
            bad.append("borehulk: manhunterOnDamageChance is not 0 (it must never retaliate)")
        if race is None or race.findtext("thinkTreeMain") != "RM_ThinkTree_Borehulk":
            bad.append("borehulk: thinkTreeMain is not RM_ThinkTree_Borehulk")
        if race is None or race.findtext("intelligence") != "Animal":
            bad.append("borehulk: intelligence is not Animal (item: dim)")
        comps = [li.get("Class", "") for li in thing.findall("comps/li")]
        if not any(c.endswith("RM_CompProperties_BorehulkDrill") for c in comps):
            bad.append("borehulk: RM_CompProperties_BorehulkDrill is not on the ThingDef")
        sharp = float(thing.findtext("statBases/ArmorRating_Sharp") or 0)
        blunt = float(thing.findtext("statBases/ArmorRating_Blunt") or 0)
        vanilla = _vanilla_mech_armour(vanilla_data)
        if vanilla is None:
            unmeasured.append("borehulk armour vs vanilla mechanoids: no Races_Mechanoid*.xml under %s" % vanilla_data)
        elif len(vanilla) < 10:
            unmeasured.append("borehulk armour: only %d vanilla mechanoid races parsed (sanity floor 10)" % len(vanilla))
        else:
            ms = max(vanilla.items(), key=lambda kv: kv[1][0])
            mb = max(vanilla.items(), key=lambda kv: kv[1][1])
            if sharp <= ms[1][0]:
                bad.append("borehulk: ArmorRating_Sharp %.2f does not exceed vanilla %s %.2f" % (sharp, ms[0], ms[1][0]))
            if blunt <= mb[1][1]:
                bad.append("borehulk: ArmorRating_Blunt %.2f does not exceed vanilla %s %.2f" % (blunt, mb[0], mb[1][1]))
    tree = defs.get(("ThinkTreeDef", "RM_ThinkTree_Borehulk"))
    if tree is not None:
        classes = [n.get("Class", "") for n in tree.iter() if n.get("Class")]
        subtrees = [n.findtext("treeDef") or "" for n in tree.iter() if n.get("Class") == "ThinkNode_Subtree"]
        fights = [c for c in classes + subtrees if any(w in c for w in _FIGHT_WORDS)]
        if fights:
            bad.append("borehulk: think tree carries a fight branch %s (it must never attack)" % fights)
        for need in ("RM_JobGiver_BorehulkBackAway", "RM_ThinkNode_ConditionalAttitudeBand"):
            if not any(c.endswith(need) for c in classes):
                bad.append("borehulk: think tree lost %s" % need)
    step = defs.get(("GenStepDef", "RM_BorehulkPlacement"))
    if step is not None and step.findtext("genStep/pawnKind") != "RM_Borehulk":
        bad.append("borehulk: RM_BorehulkPlacement does not place RM_Borehulk")
    patched = False
    for f in _xml_files(os.path.join(mod_root, "Patches")):
        for op in ET.parse(f).getroot():
            if "MapCommonBase" in (op.findtext("xpath") or "") and any(
                    (li.text or "").strip() == "RM_BorehulkPlacement" for li in op.iter("li")):
                patched = True
    if not patched:
        bad.append("borehulk: RM_BorehulkPlacement is not added to MapCommonBase by any patch (it never runs)")
    gen = os.path.join(mod_root, "Source", "RustCathedral", "RM_GenStep_BorehulkPlacement.cs")
    gsrc = _nocomment(open(gen, encoding="utf-8").read()) if os.path.isfile(gen) else ""
    gate = re.search(r'map\.Biome\.defName\s*!=\s*(CathedralBiomeDefName|"RM_RustCathedral")', gsrc)
    if not gate or (gate.group(1) == "CathedralBiomeDefName" and
                    not re.search(r'CathedralBiomeDefName\s*=\s*"RM_RustCathedral"', gsrc)):
        bad.append("borehulk: the GenStep no longer self-gates on RM_RustCathedral (it would place on every biome)")
    if "borehulkEnabled" not in gsrc:
        bad.append("borehulk: the GenStep ignores the borehulkEnabled toggle")
    # roster ban: a wildAnimals row is an ELEMENT NAMED for the kind, never an <li>; probe with a kind that IS rostered
    hits, probe = [], 0
    for f in _xml_files(src_root):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for el in root.iter():
            if el.tag == "RM_CathedralRoach":
                probe += 1
            elif el.tag == "RM_Borehulk":
                hits.append(os.path.relpath(f, src_root))
    if probe == 0:
        unmeasured.append("borehulk roster ban: the probe RM_CathedralRoach roster row was not found under %s" % src_root)
    elif hits:
        bad.append("borehulk: rostered as a wild animal in %s (it must never respawn)" % sorted(set(hits)))
    return bad, unmeasured


# ---- the base finish (RUSTCATHEDRAL_BASE_FINISH_BUILD_1), L0 half of its criteria -------------------------------
BASEFINISH_DEFS = (("IncidentDef", "RM_LineCycle"), ("SoundDef", "RM_LineCycleRoll"), ("JobDef", "RM_Job_LineCycleStill"),
                   ("ThoughtDef", "RM_FeltTheGroundTurn"), ("TraitDef", "RM_HumReader"), ("ThingDef", "RM_HumPrimer"),
                   ("ThingDef", "RM_CoolantEel"), ("PawnKindDef", "RM_CoolantEel"), ("GenStepDef", "RM_CathedralStrays"),
                   ("GenStepDef", "RM_CoolantEelSpawn"), ("RecipeDef", "RM_WriteHumPrimer"),
                   ("ThinkTreeDef", "RM_ThinkTree_CoolantEel"))
UTINNI_PATCHES = os.path.join(SRC_ROOT, "RimUtinni", "UtinniPatches", "Patches")
BESTIARY_NAME = "RimMandrake: SW \u2014 Bestiary"


def _cs_all(mod_root):
    out = {}
    for sub in ("RustCathedral", "Hum", "Walls"):
        d = os.path.join(mod_root, "Source", sub)
        for fn in (sorted(os.listdir(d)) if os.path.isdir(d) else ()):
            if fn.endswith(".cs"):
                with open(os.path.join(d, fn), encoding="utf-8") as fh:
                    out[sub + "/" + fn] = _nocomment(fh.read())
    return out


def _class_body(srcs, cls):
    """Source text of `class cls` up to the next top-level class declaration, or ''."""
    for s in srcs.values():
        m = re.search(r"\bclass\s+%s\b" % re.escape(cls), s)
        if m:
            rest = s[m.end():]
            nxt = re.search(r"\n\t?(public|internal)\s+(static\s+)?class\s", rest)
            return rest[:nxt.start()] if nxt else rest
    return ""


def basefinish_problems(mod_root=None, utinni_patches=None):
    """(problems, unmeasured). Static reads of the base-finish build: the twelve defs, the line-cycle's gates, the
    trait with no stat, the primer and its trait-gated recipe, the canal-locked eel and its placement, the sun kind,
    the strays' gate, the readout comp on the bolts, and the campaign mynock patch's guard. Arguments exist so the
    selftest can plant breaks in a temp copy."""
    mod_root = mod_root or HERE
    utinni_patches = utinni_patches or UTINNI_PATCHES
    bad, unmeasured = [], []
    defs = {}
    for f in _xml_files(os.path.join(mod_root, "Defs")):
        for el in ET.parse(f).getroot():
            if isinstance(el.tag, str) and el.findtext("defName"):
                defs[(el.tag, el.findtext("defName").strip())] = el
    for key in BASEFINISH_DEFS:
        if key not in defs:
            bad.append("basefinish: %s/%s not defined under Defs/" % key)
    inc = defs.get(("IncidentDef", "RM_LineCycle"))
    if inc is not None:
        if inc.findtext("category") != "Misc":
            bad.append("basefinish: RM_LineCycle category is not Misc (it must never be a threat)")
        if float(inc.findtext("baseChance") or 1) != 0:
            bad.append("basefinish: RM_LineCycle baseChance is not 0 (the storyteller would fire it besides the MTB roll)")
        if not (inc.findtext("workerClass") or "").endswith("RM_IncidentWorker_LineCycle"):
            bad.append("basefinish: RM_LineCycle does not use RM_IncidentWorker_LineCycle")
    trait = defs.get(("TraitDef", "RM_HumReader"))
    if trait is not None:
        if (trait.findtext("commonality") or "").strip() not in ("0", "0.0"):
            bad.append("basefinish: RM_HumReader commonality is not 0 (it would roll at pawn generation)")
        if trait.find(".//statOffsets") is not None or trait.find(".//statFactors") is not None:
            bad.append("basefinish: RM_HumReader carries a stat (the item: no stat buff anywhere)")
    primer = defs.get(("ThingDef", "RM_HumPrimer"))
    if primer is not None and not any((li.get("Class") or "").endswith("BookOutcomeProperties_HumPrimer")
                                      for li in primer.iter("li")):
        bad.append("basefinish: RM_HumPrimer has no BookOutcomeProperties_HumPrimer doer (reading it teaches nothing)")
    rec = defs.get(("RecipeDef", "RM_WriteHumPrimer"))
    if rec is not None:
        ext = [li for li in rec.findall("modExtensions/li") if (li.get("Class") or "").endswith("RM_RecipeRequiresTraitExtension")]
        if not ext or ext[0].findtext("trait") != "RM_HumReader":
            bad.append("basefinish: RM_WriteHumPrimer is not gated on RM_HumReader")
        if rec.find("products/RM_HumPrimer") is None:
            bad.append("basefinish: RM_WriteHumPrimer does not make RM_HumPrimer")
    eel = defs.get(("ThingDef", "RM_CoolantEel"))
    if eel is not None:
        race = eel.find("race")
        get = (lambda k: race.findtext(k) if race is not None else None)
        if get("trainability") != "None":
            bad.append("basefinish: RM_CoolantEel trainability is not None (it must never be tamed)")
        if (eel.findtext("statBases/Wildness") or "").strip() not in ("1", "1.0"):
            bad.append("basefinish: RM_CoolantEel Wildness is not 1")
        if get("specificMeatDef") != "RM_CoolantEelCatch":
            bad.append("basefinish: butchering RM_CoolantEel does not yield RM_CoolantEelCatch")
        if get("thinkTreeMain") != "RM_ThinkTree_CoolantEel":
            bad.append("basefinish: RM_CoolantEel does not run RM_ThinkTree_CoolantEel")
        if not any((li.get("Class") or "").endswith("CompProperties_WaterLocked") for li in eel.findall("comps/li")):
            bad.append("basefinish: RM_CoolantEel lost the RM_CompWaterLocked backstop")
        if eel.find("tools") is not None:
            bad.append("basefinish: RM_CoolantEel has tools (it never hunts or fights)")
    tree = defs.get(("ThinkTreeDef", "RM_ThinkTree_CoolantEel"))
    if tree is not None:
        classes = [n.get("Class", "") for n in tree.iter() if n.get("Class")]
        if not any(c.endswith("RM_JobGiver_WaterWander") for c in classes):
            bad.append("basefinish: the eel's think tree lost RM_JobGiver_WaterWander")
        fights = [c for c in classes if any(w in c for w in _FIGHT_WORDS)]
        if fights:
            bad.append("basefinish: the eel's think tree carries a fight branch %s" % fights)
    biome = defs.get(("BiomeDef", BIOME))
    if biome is not None:
        wild = biome.find("wildAnimals")
        if wild is not None and wild.find("RM_CoolantEel") is not None:
            bad.append("basefinish: RM_CoolantEel is in wildAnimals (the vanilla spawner would strand it on the plate)")
        sun = [li for li in biome.findall("modExtensions/li") if (li.get("Class") or "").endswith("RM_SunHeatExtension")]
        if not sun or sun[0].findtext("heatKind") != "overhead":
            bad.append("basefinish: %s does not declare RM_SunHeatExtension heatKind overhead" % BIOME)
    bolt = defs.get(("ThingDef", "RM_LivingBolt"))
    if bolt is not None and not any((li.get("Class") or "").endswith("CompProperties_HumReadout") for li in bolt.findall("comps/li")):
        bad.append("basefinish: the living bolt lost the hum readout comp (a hum reader sees nothing)")
    patched = set()
    for f in _xml_files(os.path.join(mod_root, "Patches")):
        for op in ET.parse(f).getroot():
            if "MapCommonBase" in (op.findtext("xpath") or ""):
                patched.update((li.text or "").strip() for li in op.iter("li"))
    for step in ("RM_CoolantEelSpawn", "RM_CathedralStrays"):
        if step not in patched:
            bad.append("basefinish: %s is not added to MapCommonBase by any patch (it never runs)" % step)
    srcs = _cs_all(mod_root)
    gates = {
        "RM_GenStep_CoolantEels": ("coolantEelsEnabled", "CathedralBiomeDefName"),
        "RM_GenStep_CathedralStrays": ("straysEnabled", "CathedralBiomeDefName"),
        "RM_IncidentWorker_LineCycle": ("lineCycleEnabled", "TargetBiomeDefName"),
        "RM_GameComponent_HumExposure": ("humReadingEnabled", "CathedralBiomeDefName"),
    }
    for cls, (toggle, gate) in gates.items():
        body = _class_body(srcs, cls)
        if not body:
            bad.append("basefinish: class %s not found in Source/" % cls)
            continue
        if toggle not in body:
            bad.append("basefinish: %s ignores its toggle %s" % (cls, toggle))
        if not re.search(r"defName\s*!=\s*(RM_HumReading\.)?%s" % gate, body):
            bad.append("basefinish: %s no longer self-gates to %s" % (cls, BIOME))
    stops = _class_body(srcs, "RM_MapComponent_LineCycle")
    if stops and ("IsColonist" not in stops or "IsMechanoid" not in stops):
        bad.append("basefinish: the line-cycle no longer exempts colonists and hostile mechanoids")
    allsrc = "\n".join(srcs.values())
    for needle, why in (("nameof(Bill.PawnAllowedToStartAnew)", "the primer's trait gate"),
                        ("nameof(Corpse.ButcherProducts)", "the butchered-eel catch"),
                        ("SetLineCycleDrop", "the hum's one-band drop")):
        if needle not in allsrc:
            bad.append("basefinish: %s is gone (%s)" % (needle, why))
    mp = os.path.join(utinni_patches, "WildAnimals_RustCathedral.xml")
    if not os.path.isdir(utinni_patches):
        unmeasured.append("basefinish mynocks: %s not found" % utinni_patches)
    elif not os.path.isfile(mp):
        bad.append("basefinish: WildAnimals_RustCathedral.xml is missing (no mynocks on the campaign tier)")
    else:
        ops = list(ET.parse(mp).getroot())
        ok = False
        for op in ops:
            if op.get("MayRequire"):
                bad.append("basefinish: the mynock patch guards an <Operation> with MayRequire, which the engine ignores")
            if (op.get("Class") == "PatchOperationFindMod"
                    and any((li.text or "").strip() == BESTIARY_NAME for li in op.findall("mods/li"))
                    and any(n.tag == "RSW_Mynock" for n in op.iter())
                    and any('defName="%s"' % BIOME in (x.text or "") for x in op.iter("xpath"))):
                ok = True
        if not ok:
            bad.append("basefinish: the mynock patch no longer adds RSW_Mynock to %s under a FindMod on the bestiary" % BIOME)
        warscar = os.path.join(utinni_patches, "WildAnimals_Warscar.xml")
        if os.path.isfile(warscar) and "WildAnimals_RustCathedral.xml" not in open(warscar, encoding="utf-8").read():
            bad.append("basefinish: WildAnimals_Warscar.xml lost its multi-homing note for the mynock")
    return bad, unmeasured


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


# ---- hull bolts (RUSTCATHEDRAL_HULL_BOLTS_BUILD_1), L0 half of its criteria ---------------------------------------
HULLBOLT_DEFS = (("ThingDef", "RM_HullBolt"), ("PawnKindDef", "RM_HullBolt"), ("ThinkTreeDef", "RM_ThinkTree_HullBolt"),
                 ("JobDef", "RM_HullBoltTell"), ("JobDef", "RM_PryHullBolt"), ("ThoughtDef", "RM_HullBoltsSeen"),
                 ("LetterDef", "RM_HullBoltsDilemma"))
WITNESS_TAG = "RimMandrake.RustCathedral.Hum.RM_CathedralWitnessDef"
HULLBOLT_TOGGLES = ("hullBoltsEnabled", "hullBoltBoardMin", "hullBoltBoardMax", "hullBoltNoneChance", "hullBoltEdgePull",
                    "hullBoltWitnessEnabled", "hullBoltWeightScale", "hullBoltIrritationCap", "hullBoltRealiseDays",
                    "hullBoltRevealDays", "hullBoltPetMemoryEnabled")
# the sheet's ban 1: free-tier player text never names the Cathedral as a listener or explains the mind
_BANNED_WORDS = ("cathedral", "spy", "spies", "listen", "ears", "hears", "watching you")


def hullbolts_problems(mod_root=None):
    """Static reads of the hull bolts: defs present, the resistances the item names, no fight branch, the dance on the
    hull, every witnessed Sell act names its things, the hooks that board/hear/tell exist, every setting is saved and
    read, and no player-facing string names the listener."""
    mod_root = mod_root or HERE
    bad = []
    defs = {}
    witness = []
    for f in _xml_files(os.path.join(mod_root, "Defs")):
        for el in ET.parse(f).getroot():
            if not isinstance(el.tag, str) or not el.findtext("defName"):
                continue
            defs[(el.tag, el.findtext("defName").strip())] = el
            if el.tag == WITNESS_TAG:
                witness.append(el)
    for key in HULLBOLT_DEFS:
        if key not in defs:
            bad.append("hullbolts: %s/%s not defined under Defs/" % key)
    hb = defs.get(("ThingDef", "RM_HullBolt"))
    if hb is not None:
        mult = {li.findtext("damageDef"): float(li.findtext("multiplier") or 1) for li in hb.findall("damageMultipliers/li")}
        for dd in ("Flame", "Burn", "Frostbite", "EMP", "ToxGas"):
            if mult.get(dd, 1.0) > 0.1:
                bad.append("hullbolts: RM_HullBolt damage factor for %s is not <= 0.1" % dd)
        if (hb.findtext("statBases/VacuumResistance") or "").strip() not in ("1", "1.0"):
            bad.append("hullbolts: RM_HullBolt VacuumResistance is not 1 (it would not survive space)")
        if hb.findtext("race/thinkTreeMain") != "RM_ThinkTree_HullBolt":
            bad.append("hullbolts: RM_HullBolt does not run RM_ThinkTree_HullBolt")
        if not any((li.get("Class") or "").endswith("CompProperties_HullBound") for li in hb.findall("comps/li")):
            bad.append("hullbolts: RM_HullBolt lost CompProperties_HullBound (nothing keeps it on the hull)")
        if any((li.get("Class") or "") == "CompProperties_Spawner" for li in hb.findall("comps/li")):
            bad.append("hullbolts: RM_HullBolt sheds curiosities (it would litter the ship)")
    tree = defs.get(("ThinkTreeDef", "RM_ThinkTree_HullBolt"))
    if tree is not None:
        classes = [n.get("Class", "") for n in tree.iter() if n.get("Class")]
        if not any(c.endswith("RM_JobGiver_HullDance") for c in classes):
            bad.append("hullbolts: the hull bolt's think tree lost RM_JobGiver_HullDance")
        if any("Wander" in c for c in classes):
            bad.append("hullbolts: the hull bolt's think tree wanders (it would leave the hull)")
        fights = [c for c in classes if any(w in c for w in _FIGHT_WORDS)]
        if fights:
            bad.append("hullbolts: the hull bolt's think tree carries a fight branch %s" % fights)
    if not witness:
        bad.append("hullbolts: no RM_CathedralWitnessDef (nothing is ever heard)")
    kinds = set()
    for w in witness:
        kind = (w.findtext("kind") or "").strip()
        kinds.add(kind)
        if kind == "Sell" and not w.findall("things/li"):
            bad.append("hullbolts: witness %s is a Sell with no <things> (it would hear every sale)" % w.findtext("defName"))
    for k in ("Sell", "Butcher", "DestroyHullBolt", "PryHullBolt"):
        if k not in kinds:
            bad.append("hullbolts: no witness def of kind %s" % k)
    th = defs.get(("ThoughtDef", "RM_HullBoltsSeen"))
    if th is not None and float(th.findtext("stages/li/baseMoodEffect") or 0) <= 0:
        bad.append("hullbolts: RM_HullBoltsSeen is not a positive memory")
    srcs = _cs_all(mod_root)
    allsrc = "\n".join(srcs.values())
    for needle, why in (("nameof(GravshipUtility.GenerateGravship)", "boarding at liftoff"),
                        ("nameof(Tradeable.ResolveTrade)", "hearing a sale"),
                        ("RM_WitnessKind.Butcher", "hearing a bolt broken down"),
                        ("RM_WitnessKind.DestroyHullBolt", "hearing a hull bolt destroyed"),
                        ("RM_HullBolts.ShipEdgeAnchor", "the plateau bolts drifting to the ship's edge"),
                        ("AddIrritation(m, applied)", "the ledger applied on landing"),
                        ("ArrivedUneasy", "the hum reader's arrival line")):
        if needle not in allsrc:
            bad.append("hullbolts: %s is gone (%s)" % (needle, why))
    if not re.search(r"void Witness\([^)]*\)\s*\{[^}]*hullBoltWitnessEnabled", allsrc):
        bad.append("hullbolts: RM_HullBolts.Witness ignores hullBoltWitnessEnabled")
    for cls, toggle in (("RM_HullBolts", "HullBoltsActive"),
                        ("RM_GameComponent_HullBoltWitness", "hullBoltPetMemoryEnabled"),
                        ("RM_GameComponent_HullBoltWitness", "hullBoltIrritationCap"),
                        ("RM_GameComponent_HullBoltWitness", "hullBoltRevealDays"),
                        ("RM_CompHullBound", "hullBoltRealiseDays")):
        body = _class_body(srcs, cls)
        if not body:
            bad.append("hullbolts: class %s not found in Source/" % cls)
        elif toggle not in body:
            bad.append("hullbolts: %s ignores %s" % (cls, toggle))
    modsrc = srcs.get("RustCathedral/RM_RustCathedralMod.cs", "")
    setsrc = srcs.get("Hum/RustCathedralHumSettings.cs", "")
    for t in HULLBOLT_TOGGLES:
        if '"hum_%s"' % t not in modsrc:
            bad.append("hullbolts: setting %s is not saved by the mod's settings" % t)
        if "ref %s" % t not in setsrc.split("DoWindowContents")[-1] and "%s = " % t not in setsrc.split("DoWindowContents")[-1]:
            bad.append("hullbolts: setting %s has no control on the settings screen" % t)
    proj = os.path.join(mod_root, "Source", "Hum", "RimMandrake.RustCathedral.Hum.csproj")
    if os.path.isfile(proj) and 'Include="RM_HullBolts.cs"' not in open(proj, encoding="utf-8").read():
        bad.append("hullbolts: RM_HullBolts.cs is not in the Hum csproj (it compiles into nothing)")
    texts = []
    for key in (("ThingDef", "RM_HullBolt"), ("ThoughtDef", "RM_HullBoltsSeen")):
        el = defs.get(key)
        if el is not None:
            texts += [(t.text or "") for t in el.iter() if t.tag in ("description", "label")]
    raw = ""
    hp = os.path.join(mod_root, "Source", "Hum", "RM_HullBolts.cs")
    if os.path.isfile(hp):
        raw = _nocomment(open(hp, encoding="utf-8").read())
    texts += [m for m in re.findall(r'"((?:[^"\\]|\\.)*)"', raw) if " " in m]
    for t in texts:
        low = t.lower()
        for w in _BANNED_WORDS:
            if re.search(r"\b%s\b" % re.escape(w), low):
                bad.append("hullbolts: player text names the listener (%r in %r)" % (w, t[:60]))
    return bad


def _build_suite():
    suite = Suite("RustCathedral")
    suite.toggles = sorted(n for (_t, n), (ty, _v) in settings_fields().items() if ty == "bool")

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _unmeasured(t, why):
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _raw(t, typ, action, field, value=None):
        if value is not None:
            r = t.session.call("jawa/mod_settings_field", typeName=typ, action=action, field=field, value=str(value))
        else:
            r = t.session.call("jawa/mod_settings_field", typeName=typ, action=action, field=field)
        return r if isinstance(r, dict) else {}

    def _same(ty, a, b):
        if ty == "bool":
            return str(a).lower() == str(b).lower()
        if ty == "string":
            return str(a) == str(b)
        try:
            return abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))
        except (TypeError, ValueError):
            return False

    def _flat(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield str(k)
                for x in _flat(v):
                    yield x
        elif isinstance(o, (list, tuple)):
            for v in o:
                for x in _flat(v):
                    yield x
        elif o is not None:
            yield str(o)

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
            names = ["%s/%s" % p for p in PLAIN]
            missing, ok = [], 0
            for i in range(0, len(names), 40):
                r = t.bridge_call("jawa/get_defs", defs=";".join(names[i:i + 40]), fields="defName", limit=60)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed: %r" % r)
                missing.extend(r.get("notFound") or [])
                ok += int(r.get("foundCount", 0))
            if _live(t) and (missing or ok != len(names)):
                raise ExpectationFailed("%d of %d defs resolved; notFound=%r" % (ok, len(names), missing[:8]))
        with t.component("namespaced_attitude_def_resolves", beyond_toggle=True):
            for ty, nm in NAMESPACED:
                short = ty.rsplit(".", 1)[1]
                # LIVE 2026-10-03: a custom def type resolves only by its FULL namespaced name (the short one is notFound
                # though the def is loaded: get_def "RimMandrake.RustCathedral.Hum.RM_BiomeAttitudeDef" finds it).
                r = t.bridge_call("jawa/get_defs", defs="%s/%s" % (ty, nm), fields="defName", limit=2)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is False:
                    _unmeasured(t, "get_defs cannot take the custom def type %s: %s" % (short, str(r)[:140]))
                    return
                if int(r.get("foundCount", 0)) != 1:
                    raise ExpectationFailed("%s/%s did not resolve: %r" % (short, nm, r))

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        fields = settings_fields()
        with t.component("settings_probe_finds_fields_in_all_three_classes", beyond_toggle=True):
            if len(fields) < 14 or len(set(k[0] for k in fields)) != 3:
                raise ExpectationFailed("settings probe found %d fields in %d classes (blind regex)" % (len(fields), len(set(k[0] for k in fields))))
        for (typ, field), (ty, _dv) in sorted(fields.items()):
            with t.component("%s_%s_round_trips" % (typ.rsplit(".", 1)[1].replace("RustCathedral", "")[:8] or "own", field),
                             toggle=(field if ty == "bool" else None), beyond_toggle=(ty != "bool")):
                if not _live(t):
                    continue
                old = _raw(t, typ, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s.%s: get returned no value" % (typ, field))
                if ty == "bool":
                    new = "False" if str(old).lower() == "true" else "True"
                elif ty == "string":
                    new = "zz_probe"
                elif ty == "int":
                    new = str(int(float(old)) + 1)       # an Int32 field refuses "25.0" (LIVE 2026-10-03)
                else:
                    new = str(float(old) + 1.0)
                try:
                    if not _raw(t, typ, "set", field, new).get("success"):
                        raise ExpectationFailed("%s.%s: set failed" % (typ, field))
                    back = _raw(t, typ, "get", field).get("value")
                    if not _same(ty, back, new):
                        raise ExpectationFailed("%s.%s: wrote %s, read %r" % (typ, field, new, back))
                finally:
                    _raw(t, typ, "set", field, old)
                back = _raw(t, typ, "get", field).get("value")
                if not _same(ty, back, old):
                    raise ExpectationFailed("%s.%s did not restore to %r (read %r)" % (typ, field, old, back))

    @suite.chain("biome_wiring")
    def biome_wiring(t):
        b = _biome()
        want_animals = [c.tag for c in b.find("wildAnimals")]
        want_fish = [c.tag for ft in b.find("fishTypes") for c in ft]
        want_rock = [li.text.strip() for li in b.find("forceRockTypes")]
        with t.component("animal_density_positive_and_deep_read_succeeds", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="BiomeDef/" + BIOME, fields="animalDensity,plantDensity,maxFishPopulation,workerClass", deep=True, limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows:
                    raise ExpectationFailed("could not read %s: %r" % (BIOME, r))
                f = rows[0].get("fields") or {}
                try:
                    ad = float(f.get("animalDensity"))
                except (TypeError, ValueError):
                    _unmeasured(t, "get_defs did not return a numeric animalDensity: %r" % (f,))
                    return
                if not ad > 0:
                    raise ExpectationFailed("animalDensity %s: the whole roster would never spawn" % ad)
        with t.component("roster_fish_and_rock_rows_present", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="BiomeDef/" + BIOME, fields="wildAnimals,fishTypes,forceRockTypes,wildPlants", deep=True, limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows:
                    raise ExpectationFailed("could not read %s: %r" % (BIOME, r))
                f = rows[0].get("fields") or {}
                blob = "|".join(_flat({k: f.get(k) for k in ("wildAnimals", "fishTypes", "forceRockTypes")}))
                if not f or all(f.get(k) in (None, "") for k in ("wildAnimals", "fishTypes", "forceRockTypes")):
                    _unmeasured(t, "get_defs did not serialise the roster fields: %r" % (list(f)[:6],))
                    return
                # LIVE 2026-10-03: get_defs renders a BiomeAnimalRecord without the animal's name (3 shipped animals read
                # "missing"); the animals come from jawa/biome_probe, fish and rock rows still from the blob.
                pr = t.bridge_call("jawa/biome_probe", biomes=BIOME, animals=True, limit=100)
                brows = (((pr or {}).get("biomes") or [{}])[0].get("animals") or []) if isinstance(pr, dict) else []
                names = set(a.get("defName") for a in brows)
                if not names:
                    _unmeasured(t, "biome_probe returned no roster for %s: %s" % (BIOME, str(pr)[:140]))
                    return
                missing = [n for n in want_animals if n not in names] + [n for n in want_fish + want_rock if n not in blob]
                if missing:
                    raise ExpectationFailed("biome lacks rows the XML ships: %s" % missing)
        with t.component("wild_plants_stay_empty_ruled_zero", beyond_toggle=True):
            r = t.bridge_call("jawa/biome_probe", biomes=BIOME)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    _unmeasured(t, "biome_probe could not be asked: %s" % str(r)[:140])
                    return
                rows = r.get("biomes") or []
                row = next((x for x in rows if x.get("defName") == BIOME or x.get("biome") == BIOME), rows[0] if len(rows) == 1 else None)
                if row is None or "plants" not in row:
                    _unmeasured(t, "biome_probe returned no plants list for %s: %s" % (BIOME, str(r)[:140]))
                    return
                if row.get("plants"):
                    raise ExpectationFailed("%s now lists wild plants %r: ruled zero (frozen sheet ban 7)" % (BIOME, row.get("plants")))
        with t.component("wall_scatter_steps_on_map_common_base", beyond_toggle=True):
            steps = [n for ty, n in SHIPPED if ty == "GenStepDef"]
            r = t.bridge_call("jawa/get_defs", defs="MapGeneratorDef/MapCommonBase", fields="genSteps", deep=True, limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows or "genSteps" not in (rows[0].get("fields") or {}):
                    _unmeasured(t, "get_defs did not serialise MapCommonBase.genSteps (the patch is a plain PatchOperationAdd): %s" % str(r)[:140])
                    return
                blob = "|".join(_flat(rows[0]["fields"]["genSteps"]))
                miss = [s for s in steps if s not in blob]
                if miss:
                    raise ExpectationFailed("MapCommonBase.genSteps lacks %s: the wall patch did not apply" % miss)

    @suite.chain("hum_attitude")
    def hum_attitude(t):
        with t.component("attitude_def_targets_this_biome", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="RimMandrake.RustCathedral.Hum.RM_BiomeAttitudeDef/RM_RustCathedralAttitude", fields="targetBiome,bandThresholds", deep=True, limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows:
                    _unmeasured(t, "get_defs cannot read the custom attitude def: %s" % str(r)[:140])
                    return
                f = rows[0].get("fields") or {}
                if BIOME not in "|".join(_flat(f.get("targetBiome"))):
                    raise ExpectationFailed("attitude def targetBiome is %r, not %s" % (f.get("targetBiome"), BIOME))
                bands = [x for x in _flat(f.get("bandThresholds")) if re.fullmatch(r"-?\d+(\.\d+)?", x)]
                if len(bands) != 4:
                    raise ExpectationFailed("attitude def should carry four band thresholds (five bands), read %r" % bands)

    @suite.chain("harmony_gates")
    def harmony_gates(t):
        for typ, meth, owner, why in HARMONY:
            with t.component("%s_%s_patched_by_%s" % (typ, meth, owner.rsplit(".", 1)[1]), beyond_toggle=True):
                r = t.bridge_call("jawa/harmony_patches", typeName=typ, methodName=meth)
                if _live(t):
                    if not isinstance(r, dict) or r.get("success") is not True or r.get("harmonyError"):
                        _unmeasured(t, "harmony_patches could not be asked: %s" % str(r)[:160])
                        return
                    owners = []
                    for m in (r.get("methods") or []):
                        for kind in ("prefixes", "postfixes", "transpilers", "finalizers"):
                            owners.extend(p.get("owner") for p in (m.get(kind) or []))
                    if owner not in owners:
                        raise ExpectationFailed("%s.%s carries no patch from %s (%s); owners: %s"
                                                % (typ, meth, owner, why, sorted(set(o for o in owners if o))[:8]))

    @suite.chain("roach_gate")
    def roach_gate(t):
        with t.component("think_tree_carries_cleaning_toggle_node", toggle="roachCleaningEnabled"):
            r = t.bridge_call("jawa/get_defs", defs="ThinkTreeDef/RM_ThinkTree_CathedralRoach", fields="thinkRoot", deep=True, limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows or "thinkRoot" not in (rows[0].get("fields") or {}):
                    _unmeasured(t, "get_defs did not serialise the think tree: %s" % str(r)[:140])
                    return
                blob = "|".join(_flat(rows[0]["fields"]["thinkRoot"]))
                if "depth limit reached" in blob and "RM_ThinkNode_ConditionalRoachCleaningEnabled" not in blob:
                    # LIVE 2026-10-03: get_defs stops at ~3 nodes deep, the toggle node sits below that; not a verdict.
                    _unmeasured(t, "get_defs cannot read the think tree past its depth limit; the toggle node is below it")
                    return
                if "RM_ThinkNode_ConditionalRoachCleaningEnabled" not in blob:
                    raise ExpectationFailed("the roach tree no longer carries the cleaning toggle node (the toggle gates nothing)")

    def _hum(t, method, args):
        kw = dict(type="RimMandrake.RustCathedral.Hum.RM_RustCathedralHumProof", method=method)
        if args is not None:
            kw["args"] = args
        r = t.bridge_call("jawa/static_call", **kw)
        return str((r or {}).get("result", "")) if isinstance(r, dict) else ""

    @suite.chain("map_mechanics")
    def map_mechanics(t):
        for name, toggle, why in (
            ("bolts_dance_and_freeze_with_the_hum", "boltDanceEnabled",
             "the bolt dance and the freeze at the worst band read the attitude value per tick on a living bolt; needs a generated "
             "RM_RustCathedral map (or a spawned bolt plus an attitude read tool) and game time"),
            ("eel_fishing_consequence", "fishingPricingEnabled",
             "a catch consequence needs a fishing job on a river of a generated Cathedral map"),
            ("deep_drill_response_replaces_infestation", "drillResponseEnabled",
             "the response incident fires from a deep drill on the Cathedral; fire_incident dry-run reports success=False with "
             "canFireNow=False, so no honest read exists"),
            ("wall_tiers_laid_at_mapgen", "wallTiersEnabled",
             "deck plate, dead smartsteel and sacred wall scatter exist only on a map GENERATED as RM_RustCathedral; the bridge cannot generate one"),
            ("hum_commentary_and_goodwill_drain", "goodwillDrainEnabled",
             "the timed drain (-1 standing per 4 hours at the worst band) needs hours of game time; one drain step is proved in calm_bands_reachable"),
        ):
            with t.component(name, toggle=toggle):
                if _live(t):
                    _unmeasured(t, why)
        with t.component("watched_pricing_and_kill_irritation", toggle="boltWatchedPricingEnabled"):
            text = _hum(t, "ProofWatched", "true")
            if _live(t):
                if not text.startswith("WATCHED"):
                    _unmeasured(t, "ProofWatched gave no answer: %r" % text[:160]); return
                if not ("pickup +3.0" in text and "again +0.0" in text and "kill +15.0" in text):
                    raise ExpectationFailed("pickup +3 once, kill +15 expected (RM_WatchedBolts): %s" % text)
            off = _hum(t, "ProofWatched", "false")
            if _live(t) and not ("pickup +0.0" in off and "kill +0.0" in off):
                raise ExpectationFailed("boltWatchedPricingEnabled off still raised irritation: %s" % off)
        with t.component("hum_value_ladder_and_hysteresis", beyond_toggle=True):
            text = _hum(t, "ProofLadder", None)
            if _live(t):
                if not text.startswith("LADDER"):
                    _unmeasured(t, "ProofLadder gave no answer: %r" % text[:160]); return
                g = float(text.split("standing ")[1].split(" |")[0])
                w = float(text.split("weight ")[1].split(" |")[0])
                th, margin, layers = [10.0, 30.0, 55.0, 80.0], 6.0, 3
                floor = max(0.0, min(100.0, -g * w))
                expect, prev = [], 0
                for c in (0, 10, 30, 55, 80, 77, 73, 52, 48):
                    comp = max(floor, float(c))
                    raw = sum(1 for x in th if comp >= x)
                    if raw < prev and prev - 1 < len(th) and comp >= th[prev - 1] - margin:
                        raw = prev
                    prev = raw
                    expect.append("%d:%d/%d" % (c, raw, 0 if raw >= len(th) else min(raw + 1, layers)))
                got = text.split("up ")[1].split(" |")[0].split(",") + text.split("down ")[1].split(",")
                if got != expect:
                    raise ExpectationFailed("band/layer ladder %s != the def's thresholds/hysteresis %s (%s)" % (got, expect, text))
        with t.component("calm_bands_reachable", beyond_toggle=True):
            # LIVE question, not a tautology: the composite subtracts the attitude component's own standing x
            # weight (RUSTCATHEDRAL_GOODWILL_FLOOR_1 -- it used to read the permanentEnemy Mechanoid faction's
            # goodwill, which cannot move). A standing low enough to floor the composite at >= 10 makes bands
            # 0-1 unreachable, and the worst-band drain must actually move the value the composite reads.
            text = _hum(t, "ProofLadder", None)
            if _live(t):
                if not text.startswith("LADDER"):
                    _unmeasured(t, "ProofLadder gave no answer: %r" % text[:160]); return
                g = float(text.split("standing ")[1].split(" |")[0])
                w = float(text.split("weight ")[1].split(" |")[0])
                if -g * w >= 10.0:
                    raise ExpectationFailed("standing %d x weight %.2f puts the composite floor at %.0f: the calm bands (0-1) "
                                            "are unreachable (RUSTCATHEDRAL_GOODWILL_FLOOR_1)" % (g, w, -g * w))
            drain = _hum(t, "ProofDrain", None)
            if _live(t):
                if not drain.startswith("DRAIN"):
                    _unmeasured(t, "ProofDrain gave no answer: %r" % drain[:160]); return
                a, b = (int(x) for x in drain.split("standing ")[1].split(" |")[0].split(" -> "))
                d = int(drain.split("expected ")[1])
                if b - a != max(d, -100 - a):
                    raise ExpectationFailed("one worst-band drain step moved standing %d -> %d, expected %+d: the drain does "
                                            "not move the value the composite reads (RUSTCATHEDRAL_GOODWILL_FLOOR_1)" % (a, b, d))
        with t.component("roach_eats_filth", toggle="roachCleaningEnabled"):
            if _live(t):
                _unmeasured(t, "a roach seeking filth needs a spawned roach, filth and a ticked map; the think-tree wiring is read in roach_gate")

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    for u in basefinish_problems()[1]:
        print("  UNMEASURED " + u)
    for u in borehulk_problems()[1]:
        print("  UNMEASURED " + u)
    sys.exit(1 if problems else 0)
