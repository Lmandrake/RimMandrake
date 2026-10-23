"""validation.py -- modcheck suite for RimMandrake: Webwork (mandrake.rm.webwork).

First north-star script (WEBWORK_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/Webwork.md
(`## must be true`, agent-owned, not hashed). Process: design/RimMandrake/debug_process.md section 2.

The mod: RM_Webwork jungle biome, 16 invented plants, 5 invented animals, the owner species RM_Ollathrix (mouth-loom
spit, loom-bound hediff, sun-scald), and the nest + egg economy (a guaranteed nest on every Webwork map, a mineable egg
clutch that the nest wall re-seeds while an ollathrix lives, an inert contraband egg item). Fold-aware: when folded into
mandrake.rm.biomes the mod is active under the composed name 'RimMandrake: Baroque Biomes'; reads here are by def name
and settings type, never by mod name.

CHAINS
  defs_resolve        every def under Defs/ resolves live (parsed from the XML); a control reads notFound.
  settings_roundtrip  every `public static` scalar of RM_WebworkSettings (found by regex): default / write / restore.
  biome_wiring        animalDensity and plantDensity > 0; the 6 roster rows and the nest scatter step on MapCommonBase.
  nest_egg_state      the nest wall carries the relay comp, the clutch mines to the egg, the egg is inert contraband
                      with NO hatcher comp (ban 1), the ollathrix is dormant-capable with the turret comp.
  scald_binding       the sun-scald hediff resolves to the CreatureBehaviors class (hard dependency).
  web_terrain_weather WEBWORK_TERRAIN_WEATHER_PASS_1: the web laid at mapgen (cables, local webs, silk carpet only near
                      spider sites) and webfall (in the biome's weather table, forceable), each toggle's off arm.
  map_mechanics       nest placement at mapgen, the 20-30 day re-lay, emergent spawn on destroy, the web
                      harvest (Deconstruct -> thrixweave + emergent spawn), sun-scald in sun,
                      loom spit: UNMEASURED, each says what it needs.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
MOCK:   `python3 validation.py --mock` -> runs the web_terrain_weather chain against a fake session that answers like a
        game where the mod works, so the chain's plumbing and parsing are exercised offline.
        It also runs map_mechanics (fog timeout), urraveth_remains, traction_lance, siege and thrixweave_and_front against
        mocks with planted defects; each defect must turn ITS row FAIL (or UNMEASURED when it blinds the instrument).
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
BIOME = "RM_Webwork"
SETTINGS = "RimMandrake.Webwork.RM_WebworkSettings"
SETTINGS_SRC = os.path.join("Source", "RM_WebworkMod.cs")
CONTROL_ABSENT = "ThingDef/RM_WebworkNoSuchDef_ZZ"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float|string)\s+(\w+)\s*=(?!>)\s*([^;]+);")


def _read(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as fh:
        return fh.read()


def shipped_defs():
    """[(DefType, defName)] for every non-abstract top-level def under Defs/, from the XML."""
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
    """{name: type} for every scalar `public static` field of RM_WebworkSettings, read from the C#."""
    src = re.sub(r"//[^\n]*", "", _read(SETTINGS_SRC))
    body = src.split("class RM_WebworkSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(body))


def _biome():
    return ET.parse(os.path.join(HERE, "Defs", "BiomeDefs", "RM_Webwork_Biome.xml")).getroot().find("BiomeDef")


def _base_port_findings():
    bad = []
    txt = lambda rel: re.sub(r"<!--.*?-->", "", _read(rel), flags=re.S)
    st = txt(os.path.join("Defs", "ThingDefs_Buildings", "RM_WebworkStructures.xml"))
    for n in ("Anchor", "Web", "Gutter"):
        m = re.search(r"<defName>RM_Webwork_%s</defName>(.*?)</ThingDef>" % n, st, flags=re.S)
        if not m:
            bad.append("RM_Webwork_%s not defined" % n)
        else:
            if "<Hyperweave>" not in m.group(1) or "RM_CompProperties_SenseWebNode" not in m.group(1):
                bad.append("RM_Webwork_%s needs a thrixweave killedLeavings and a sense-web comp" % n)
            if "RM_CompProperties_EmergentSpawnOnDestroy" not in m.group(1):
                bad.append("RM_Webwork_%s carries no emergent-spawn comp (a cut has no teeth)" % n)
            if n != "Gutter" and not ("RimMandrake.Webwork.RM_CompProperties_HarvestYield" in m.group(1)
                                      and "<yield>Hyperweave</yield>" in m.group(1)
                                      and "<alwaysDeconstructible>true</alwaysDeconstructible>" in m.group(1)
                                      and "<claimable>false</claimable>" in m.group(1)):
                bad.append("RM_Webwork_%s is not a colonist-harvestable node (alwaysDeconstructible, claimable false, "
                           "RM_CompProperties_HarvestYield of Hyperweave)" % n)
            if not os.path.isfile(os.path.join(HERE, "Textures", "Things", "Building", "Natural", "RM_Webwork_%s.png" % n)):
                bad.append("RM_Webwork_%s has no texture" % n)
    if "RM_Webwork_Slick" not in txt(os.path.join("Defs", "HediffDefs", "RM_WebworkSlick.xml")):
        bad.append("RM_Webwork_Slick hediff missing")
    ren = txt(os.path.join("Patches", "RM_Thrixweave_Rename.xml"))
    if "<label>thrixweave</label>" not in ren:
        bad.append("Hyperweave is not renamed thrixweave")
    oll = txt(os.path.join("Defs", "ThingDefs_Races", "RM_Ollathrix.xml"))
    if not re.search(r"<butcherProducts>\s*<Hyperweave>\d+</Hyperweave>", oll):
        bad.append("RM_Ollathrix has no thrixweave butcher yield")
    # the retired campaign names must be gone repo-wide, with a probe that the search can see anything
    root = os.path.normpath(os.path.join(HERE, "..", ".."))
    gone = re.compile(r"RUT_Webwork_(Anchor|Web|Gutter|Slick)\b")
    probe, hits = 0, []
    for dp, _d, files in os.walk(root):
        if "__pycache__" in dp or os.sep + "Textures" in dp or os.sep + "Assemblies" in dp:
            continue
        for fn in files:
            if fn.endswith((".xml", ".cs", ".py")):
                try:
                    body = open(os.path.join(dp, fn), encoding="utf-8").read()
                except (OSError, UnicodeDecodeError):
                    continue
                if "RM_Webwork_NestWall" in body:
                    probe += 1
                if gone.search(body) and fn != "validation.py":
                    hits.append(os.path.relpath(os.path.join(dp, fn), root))
    if probe == 0:
        bad.append("sanity probe: RM_Webwork_NestWall found in no source file (the walk cannot see)")
    if hits:
        bad.append("retired RUT_Webwork_Anchor/Web/Gutter/Slick still named in: %s" % sorted(hits)[:6])
    return bad


def _traction_lance_findings():
    """WEBWORK_TRACTION_LANCE_BUILD_1, offline half: one pull, two buildings, two doors, fabric tether."""
    bad = []
    rm = os.path.normpath(os.path.join(HERE, ".."))
    pull_cls = "RimMandrake.CreatureBehaviors.RM_CompProperties_TetherPull"
    lance = _read(os.path.join("Defs", "ThingDefs_Buildings", "RM_TractionLance.xml"))
    cap_p = os.path.join(rm, "TheSump", "Defs", "ThingDefs_Buildings", "RM_CapstanTurret.xml")
    cap = open(cap_p, encoding="utf-8").read() if os.path.isfile(cap_p) else ""
    if pull_cls not in lance:
        bad.append("RM_TractionLance does not carry the shared RM_CompTetherPull")
    if pull_cls not in cap:
        bad.append("RM_CapstanTurret does not carry the shared RM_CompTetherPull")
    for f in ("Cloth", "DevilstrandCloth", "Hyperweave"):
        if "<stuff>%s</stuff>" % f not in lance:
            bad.append("RM_TractionLance has no tether factor for %s" % f)
    if "<li>Fabric</li>" not in lance or "RM_Research_TractionLance" not in lance:
        bad.append("RM_TractionLance is not fabric-stuffed or not gated on RM_Research_TractionLance")
    # One pull implementation: the forced-move call (Notify_Teleported in a reel) lives only in RM_CompTetherPull.
    # Sanity probe: the search must find the shared class itself, or it is blind.
    pull_sites, saw_shared = [], False
    for mod in ("CreatureBehaviors", "TheSump", "Webwork"):
        src = os.path.join(rm, mod, "Source")
        for dp, _d, files in os.walk(src):
            for fn in files:
                if not fn.endswith(".cs"):
                    continue
                txt = open(os.path.join(dp, fn), encoding="utf-8").read()
                if "Notify_Teleported(" in txt and ("ReelStep" in txt or "TryRope" in txt):
                    if fn == "RM_CompTetherPull.cs":
                        saw_shared = True
                    else:
                        pull_sites.append(fn)
    if not saw_shared:
        bad.append("sanity probe: the pull search did not find RM_CompTetherPull.cs (the check is blind)")
    if pull_sites:
        bad.append("a second pull implementation exists: %s" % sorted(pull_sites))
    junction = _read(os.path.join("Defs", "ThingDefs_Items", "RM_GutterJunction.xml"))
    if "RM_CompProperties_AnalyzableGrantResearch" not in junction or "RM_Research_TractionLance" not in junction:
        bad.append("RM_GutterJunction does not grant RM_Research_TractionLance")
    structures = _read(os.path.join("Defs", "ThingDefs_Buildings", "RM_WebworkStructures.xml"))
    if "<specimen>RM_GutterJunction</specimen>" not in structures or "<alwaysDeconstructible>true</alwaysDeconstructible>" not in structures:
        bad.append("RM_Webwork_Gutter cannot be cut out into an RM_GutterJunction")
    dj_p = os.path.join(rm, "TheSump", "Defs", "ThingDefs_Items", "RUT_PreservedDrawJoint.xml")
    if os.path.isfile(dj_p) and "RM_Research_TractionLance" not in open(dj_p, encoding="utf-8").read():
        bad.append("the Sump draw-joint does not grant RM_Research_TractionLance")
    return bad


WEB_DEFS = {"ThingDef": ("RM_Webwork_Cable", "RM_Webwork_Strand"), "TerrainDef": ("RM_Webwork_SilkCarpet",),
            "WeatherDef": ("RM_Webfall",), "GenStepDef": ("RM_WebworkWebScatter",)}


def _web_terrain_weather_findings():
    """WEBWORK_TERRAIN_WEATHER_PASS_1, offline half (parsed from the XML and C#)."""
    bad = []
    have = set(SHIPPED)
    for ty, names in WEB_DEFS.items():
        for n in names:
            if (ty, n) not in have:
                bad.append("%s/%s not defined" % (ty, n))
    if bad:
        return bad
    root = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_WebworkWebNetwork.xml")).getroot()
    things = dict((d.findtext("defName"), d) for d in root.findall("ThingDef"))
    cable, strand = things["RM_Webwork_Cable"], things["RM_Webwork_Strand"]
    for n, d in (("RM_Webwork_Cable", cable), ("RM_Webwork_Strand", strand)):
        if d.findtext("passability") != "Standable" or not int(d.findtext("pathCost") or 0) > 0:
            bad.append("%s must be Standable with a pathCost > 0 (slow, never impassable: a line must not cut the map)" % n)
        if (d.findtext("building/isEdifice") or "").lower() != "false" or float(d.findtext("fillPercent") or 1) != 0:
            bad.append("%s must be a non-edifice with fillPercent 0, or it blocks the trees (the jungle must stay a jungle)" % n)
        comps = "|".join(li.get("Class", "") for li in d.findall("comps/li"))
        if "RM_CompProperties_SenseWebNode" not in comps:
            bad.append("%s is not part of the sense-web" % n)
        tex = d.findtext("graphicData/texPath") or ""
        if not os.path.isfile(os.path.join(HERE, "Textures", tex + ".png")):
            bad.append("%s stand-in texPath %s has no PNG in this mod" % (n, tex))
    if not int(cable.findtext("pathCost")) > int(strand.findtext("pathCost")):
        bad.append("the cable (main structure) must cost more to cross than a local web")
    ccomps = "|".join(li.get("Class", "") for li in cable.findall("comps/li"))
    if "RM_CompProperties_HarvestYield" not in ccomps or cable.find("modExtensions/li[@Class='RimMandrake.CreatureBehaviors.RM_ChewableExtension']") is None:
        bad.append("RM_Webwork_Cable must be cuttable for thrixweave and chewable by beetles")
    if "RM_CompProperties_AdhesiveSlick" not in "|".join(li.get("Class", "") for li in strand.findall("comps/li")) \
            or strand.findtext("tickerType") != "Normal":
        bad.append("RM_Webwork_Strand must carry the adhesive (and tick Normal, which RM_CompAdhesiveSlick needs)")
    terr = ET.parse(os.path.join(HERE, "Defs", "TerrainDefs", "RM_WebworkSilkCarpet.xml")).getroot().find("TerrainDef")
    if (terr.findtext("natural") or "").lower() != "true" or not float(terr.findtext("fertility") or 0) > 0:
        bad.append("RM_Webwork_SilkCarpet must be natural with fertility > 0 (a site sits under the canopy, not in a clearing)")
    b = _biome()
    if any(li.findtext("terrain") == "RM_Webwork_SilkCarpet" for li in b.findall("terrainsByFertility/li")):
        bad.append("silk carpet is painted biome-wide (terrainsByFertility); it belongs only at spider sites")
    wc = b.find("baseWeatherCommonalities")
    if wc is None or wc.find("RM_Webfall") is None:
        bad.append("RM_Webwork's weather table has no RM_Webfall row")
    wf = ET.parse(os.path.join(HERE, "Defs", "WeatherDefs", "RM_Webfall.xml")).getroot().find("WeatherDef")
    if (wf.findtext("canOccurAsRandomForcedEvent") or "").lower() != "false":
        bad.append("RM_Webfall must not occur as a random forced event (mechanics promised only inside our biome)")
    if wf.find("maxGlow") is not None and float(wf.findtext("maxGlow")) < 1:
        bad.append("RM_Webfall lowers the sky glow: that would open the light-moat, which only overcast may do")
    if any(float(wf.findtext(f) or 0) > 0 for f in ("rainRate", "snowRate", "sandRate")):
        bad.append("RM_Webfall builds up rain/snow/sand")
    if "RimMandrake.Webwork.RM_WeatherOverlay_Webfall" not in [li.text for li in wf.findall("overlayClasses/li")]:
        bad.append("RM_Webfall does not use the webfall overlay")
    gs = ET.parse(os.path.join(HERE, "Defs", "MapGeneration", "RM_WebworkWebScatter.xml")).getroot().find("GenStepDef")
    if not int(gs.findtext("order")) > 325:
        bad.append("RM_WebworkWebScatter must run after the nest (324) and the urraveth skeleton (325)")
    if "<li>RM_WebworkWebScatter</li>" not in _read(os.path.join("Patches", "RM_WebworkWebScatter_MapGenPatch.xml")):
        bad.append("RM_WebworkWebScatter is not added to MapCommonBase")
    gen = _read(os.path.join("Source", "RM_GenStep_WebworkWeb.cs"))
    if "WebworkBiomeDefName" not in gen.split("public override void Generate", 1)[1].split("PlaceWeb", 1)[0]:
        bad.append("RM_GenStep_WebworkWeb.Generate does not gate on the Webwork biome before laying anything")
    for want in ("RM_Webwork_Cable", "RM_Webwork_Strand", "RM_Webwork_SilkCarpet"):
        if '"%s"' % want not in gen:
            bad.append("RM_GenStep_WebworkWeb never names %s" % want)
    if '"RM_Webwork_Cable"' not in _read(os.path.join("Source", "RM_WebworkStartupGate.cs")):
        bad.append("webHarvestEnabled does not reach RM_Webwork_Cable (startup gate harvest list)")
    return bad


def _siege_findings():
    """WEB_SIEGE_DESIGN_SPIDERS_BRING_SHADE, offline half (parsed from the XML and C#)."""
    bad = []
    have = set(SHIPPED)
    want = [("IncidentDef", "RM_WebworkSiege"), ("ThingDef", "RM_Webwork_SiegeWeb"), ("ThingDef", "RM_Webwork_SiegeDoorWrap"),
            ("ThingDef", "RM_Webwork_SiegeCocoon"), ("JobDef", "RM_WebSiegeSpin"), ("JobDef", "RM_WebSiegeCocoon"),
            ("JobDef", "RM_WebSiegeWrapDoor"), ("DutyDef", "RM_WebSiegeSpinDuty"), ("DutyDef", "RM_WebSiegePressDuty"),
            ("HediffDef", "RM_Webwork_SilkSuffocation")]
    for ty, n in want:
        if (ty, n) not in have:
            bad.append("%s/%s not defined" % (ty, n))
    if bad:
        return bad
    inc = ET.parse(os.path.join(HERE, "Defs", "IncidentDefs", "RM_WebworkSiege.xml")).getroot().find("IncidentDef")
    if inc.findtext("category") != "ThreatBig" or inc.findtext("workerClass") != "RimMandrake.Webwork.RM_IncidentWorker_WebworkSiege":
        bad.append("RM_WebworkSiege must be ThreatBig with RM_IncidentWorker_WebworkSiege")
    if (inc.findtext("canOccurOnAllPlanetLayers") or "").lower() == "true":
        bad.append("RM_WebworkSiege must stay on the surface layer")
    root = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_WebworkSiege.xml")).getroot()
    things = dict((d.findtext("defName"), d) for d in root.findall("ThingDef"))
    web = things["RM_Webwork_SiegeWeb"]
    if (web.findtext("building/isEdifice") or "").lower() != "false" or float(web.findtext("fillPercent") or 1) != 0 \
            or web.findtext("passability") != "Standable":
        bad.append("RM_Webwork_SiegeWeb must be a Standable non-edifice with fillPercent 0 (trees and items stay)")
    if not float(web.findtext("statBases/Flammability") or 0) >= 1:
        bad.append("RM_Webwork_SiegeWeb must burn well (fire is the canon answer)")
    if web.find("killedLeavings") is not None:
        bad.append("RM_Webwork_SiegeWeb has killedLeavings: force-broken siege silk would bypass the per-siege thrixweave cap")
    comps = "|".join(li.get("Class", "") for li in web.findall("comps/li"))
    if "RM_CompProperties_SiegeSilk" not in comps or web.findtext("tickerType") != "Normal":
        bad.append("RM_Webwork_SiegeWeb must carry RM_CompProperties_SiegeSilk (capped yield + slick) and tick Normal")
    if "EmergentSpawn" in comps or "AdhesiveSlick" in comps:
        bad.append("RM_Webwork_SiegeWeb must not carry the emergent spawn or RM_CompAdhesiveSlick (it would stick the spiders)")
    if (web.findtext("building/alwaysDeconstructible") or "").lower() != "true":
        bad.append("RM_Webwork_SiegeWeb must be cuttable with vanilla Deconstruct")
    wrap, coc = things["RM_Webwork_SiegeDoorWrap"], things["RM_Webwork_SiegeCocoon"]
    if wrap.findtext("thingClass") != "RimMandrake.Webwork.RM_Building_SiegeDoorWrap" or (wrap.findtext("building/isEdifice") or "").lower() != "false":
        bad.append("RM_Webwork_SiegeDoorWrap must be a non-edifice RM_Building_SiegeDoorWrap (an edifice would wipe the door)")
    if coc.findtext("thingClass") != "RimMandrake.Webwork.RM_Building_SiegeCocoon" or (coc.findtext("building/isEdifice") or "").lower() != "false" \
            or coc.findtext("tickerType") != "Normal":
        bad.append("RM_Webwork_SiegeCocoon must be a ticking non-edifice RM_Building_SiegeCocoon")
    for n, d in things.items():
        tex = d.findtext("graphicData/texPath") or ""
        if not os.path.isfile(os.path.join(HERE, "Textures", tex + ".png")):
            bad.append("%s texPath %s has no PNG in this mod" % (n, tex))
    hed = ET.parse(os.path.join(HERE, "Defs", "HediffDefs", "RM_WebworkSiege_Hediffs.xml")).getroot().find("HediffDef")
    if hed.findtext("lethalSeverity") != "1":
        bad.append("RM_Webwork_SilkSuffocation must be lethal at severity 1 (the cocoon adds it at 1)")
    src = _read(os.path.join("Source", "RM_WebworkSiege.cs"))
    for cls in ("RM_IncidentWorker_WebworkSiege", "RM_LordJob_WebworkSiege", "RM_JobDriver_SpinSiegeWeb", "RM_Building_SiegeCocoon",
                "RM_Building_SiegeDoorWrap", "RM_WebworkSiegeDoorPatch", "RM_MapComponent_WebworkSiege", "RM_CompSiegeSilk"):
        if "class %s" % cls not in src:
            bad.append("class %s not found in RM_WebworkSiege.cs" % cls)
    if "RM_WebworkSiegeKernel.Eligibility" not in src or "MeasureShade" not in src:
        bad.append("the worker does not gate on the kernel's shaded-neighbour eligibility")
    about = _read(os.path.join("About", "About.xml"))
    if "<packageId>brrainz.harmony</packageId>" not in about:
        bad.append("Webwork patches with Harmony but does not declare brrainz.harmony")
    proj = _read(os.path.join("Source", "RM_Webwork.csproj"))
    if 'Include="Kernel\\RM_WebworkSiegeKernel.cs"' not in proj:
        bad.append("Kernel/RM_WebworkSiegeKernel.cs is not in the csproj")
    st = _read(os.path.join("Source", "SelfTest", "RimMandrakeWebwork.SelfTest.csproj"))
    if "RM_WebworkSiegeKernel.cs" not in st:
        bad.append("the siege kernel is not compiled into the fuzz selftest")
    return bad


def static_checks():
    bad = []
    # WEBWORK_HEAT_SHADE_BUILD_1: the biome declares an overhead sun-heat kind (state read lives in the live chain)
    biome_txt = _read(os.path.join(HERE, "Defs", "BiomeDefs", "RM_Webwork_Biome.xml"))
    if 'Class="RimMandrake.CreatureBehaviors.RM_SunHeatExtension"' not in biome_txt or "<heatKind>overhead</heatKind>" not in biome_txt:
        bad.append("RM_Webwork lacks an overhead RM_SunHeatExtension")
    if len(SHIPPED) < 30:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if len(fields) < 5:
        return ["settings probe found %d scalar fields, floor 5 (sanity probe failed)" % len(fields)]
    src = _read(SETTINGS_SRC)
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    # a setting no code reads gates nothing (the "screen that lies" trap)
    code = "".join(_read(os.path.join("Source", f)) for f in os.listdir(os.path.join(HERE, "Source"))
                   if f.endswith(".cs") and f != "RM_WebworkMod.cs")
    for n in fields:
        if "RM_WebworkSettings.%s" % n not in code:
            bad.append("settings field %s is read by no other source file (it gates nothing)" % n)
    proj = _read(os.path.join("Source", "RM_Webwork.csproj"))
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    kinds = set(t for t, _n in SHIPPED)
    for need in ("BiomeDef", "ThingDef", "PawnKindDef", "HediffDef", "GenStepDef", "SoundDef", "DamageDef", "TerrainDef", "WeatherDef"):
        if need not in kinds:
            bad.append("no %s parsed" % need)
    b = _biome()
    if b is None or b.findtext("defName") != BIOME:
        bad.append("BiomeDef %s not parsed" % BIOME)
    else:
        if not float(b.findtext("animalDensity") or 0) > 0:
            bad.append("animalDensity is 0: the roster is dead content")
        if len(list(b.find("wildAnimals"))) < 6:
            bad.append("wildAnimals has fewer than 6 rows")
        if len(list(b.find("wildPlants"))) < 16:
            bad.append("wildPlants has fewer than 16 rows")
    # WEBWORK_BASE_PORT_BUILD_1: structures, front extension, thrixweave rename, butcher yield (parsed from the XML)
    bad.extend(_base_port_findings())
    bad.extend(_traction_lance_findings())
    bad.extend(_web_terrain_weather_findings())
    bad.extend(_siege_findings())
    for cls in ("RM_GenStep_WebworkNest", "RM_CompEggClutchRelay", "RM_CompEmergentSpawnOnDestroy", "RM_BiomeWorker_Webwork",
                "RM_GenStep_WebworkWeb", "RM_WeatherOverlay_Webfall"):
        if not any(("class %s" % cls) in _read(os.path.join("Source", f)) for f in os.listdir(os.path.join(HERE, "Source")) if f.endswith(".cs")):
            bad.append("class %s not found in Source/" % cls)
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "Webwork.md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


def _build_suite():
    suite = Suite("Webwork")
    suite.toggles = sorted(n for n, ty in settings_fields().items() if ty == "bool")

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

    def _deep(t, spec, fields):
        """One deep get_defs row's `fields` dict, or None after recording UNMEASURED (tool could not answer)."""
        r = t.bridge_call("jawa/get_defs", defs=spec, fields=fields, deep=True, limit=2)
        if not _live(t):
            return None
        rows = (r or {}).get("defs") or []
        if not isinstance(r, dict) or r.get("success") is False or int(r.get("foundCount", 0)) != 1 or not rows:
            raise ExpectationFailed("%s did not resolve: %s" % (spec, str(r)[:200]))
        f = rows[0].get("fields") or {}
        if not f:
            _unmeasured(t, "get_defs returned no fields for %s (%s)" % (spec, fields))
            return None
        return f

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

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with t.component("settings_probe_finds_fields", beyond_toggle=True):
            if len(settings_fields()) < 1:
                raise ExpectationFailed("settings probe found no field (blind regex)")
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=(field if ty == "bool" else None), beyond_toggle=(ty != "bool")):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else (str(int(float(old)) + 1) if ty == "int" else str(float(old) + 1.0))
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
        b = _biome()
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
        with t.component("roster_rows_present", beyond_toggle=True):
            want = [c.tag for c in b.find("wildAnimals")]
            # LIVE 2026-10-03: get_defs renders a BiomeAnimalRecord without the animal's name (the live roster was complete and the
            # check still read 6 rows missing); jawa/biome_probe lists the resolved roster by defName.
            r = t.bridge_call("jawa/biome_probe", biomes=BIOME, animals=True, limit=100)
            if _live(t):
                brows = (((r or {}).get("biomes") or [{}])[0].get("animals") or []) if isinstance(r, dict) else []
                names = set(a.get("defName") for a in brows)
                if not names:
                    _unmeasured(t, "biome_probe returned no roster for %s: %s" % (BIOME, str(r)[:140]))
                    return
                missing = [n for n in want if n not in names]
                if missing:
                    raise ExpectationFailed("biome lacks roster rows the XML ships: %s (live roster: %s)" % (missing, sorted(names)))
        with t.component("nest_scatter_step_on_map_common_base", toggle="nestEnabled"):
            r = t.bridge_call("jawa/get_defs", defs="MapGeneratorDef/MapCommonBase", fields="genSteps", deep=True, limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows or "genSteps" not in (rows[0].get("fields") or {}):
                    _unmeasured(t, "get_defs did not serialise MapCommonBase.genSteps: %s" % str(r)[:140])
                    return
                if "RM_WebworkNestScatter" not in "|".join(_flat(rows[0]["fields"]["genSteps"])):
                    raise ExpectationFailed("MapCommonBase.genSteps lacks RM_WebworkNestScatter: the nest patch did not apply")

    @suite.chain("nest_egg_state")
    def nest_egg_state(t):
        with t.component("nest_wall_carries_the_relay_comp", beyond_toggle=True):
            f = _deep(t, "ThingDef/RM_Webwork_NestWall", "comps")
            if f is not None:
                blob = "|".join(_flat(f.get("comps")))
                if "EggClutchRelay" not in blob:
                    if "comps" not in f or not blob:
                        _unmeasured(t, "get_defs did not serialise comps")
                        return
                    raise ExpectationFailed("the nest wall no longer carries RM_CompProperties_EggClutchRelay: %s" % blob[:200])
        with t.component("clutch_mines_to_the_egg", beyond_toggle=True):
            f = _deep(t, "ThingDef/RM_Webwork_EggClutch", "building")
            if f is not None:
                blob = "|".join(_flat(f.get("building")))
                if not blob:
                    _unmeasured(t, "get_defs did not serialise the building block")
                    return
                if "RM_OllathrixEgg" not in blob:
                    raise ExpectationFailed("the egg clutch no longer mines to RM_OllathrixEgg: %s" % blob[:200])
        with t.component("egg_is_inert_contraband_with_no_hatcher", beyond_toggle=True):
            f = _deep(t, "ThingDef/RM_OllathrixEgg", "tradeability,tradeTags,comps")
            if f is not None:
                # LIVE 2026-10-03: a substring over the whole comps dump matched CompRottable's own field name `disableIfHatcher`;
                # only a comp CLASS named Hatcher is a hatcher.
                classes = [str(c.get("compClass")) for c in (f.get("comps") or []) if isinstance(c, dict)]
                if any("Hatcher" in c for c in classes):
                    raise ExpectationFailed("the egg carries a hatcher comp: ban 1 (inert cargo, it must never hatch)")
                if "RM_Contraband" not in "|".join(_flat(f.get("tradeTags"))):
                    raise ExpectationFailed("the egg lost its RM_Contraband trade tag: %r" % (f.get("tradeTags"),))
                # LIVE 2026-10-03: reads 'All' (Buyable|Sellable) on the campaign list, where the RUT patch replaces the
                # def's explicit Sellable; both let the player sell it, which is the property under test.
                if "|".join(_flat(f.get("tradeability"))) not in ("Sellable", "All"):
                    raise ExpectationFailed("the egg tradeability is %r, not Sellable or All" % (f.get("tradeability"),))
        with t.component("ollathrix_is_dormant_capable_with_a_turret_gun", beyond_toggle=True):
            f = _deep(t, "ThingDef/RM_Ollathrix", "comps")
            if f is not None:
                blob = "|".join(_flat(f.get("comps")))
                if not blob:
                    _unmeasured(t, "get_defs did not serialise comps")
                    return
                for need in ("CanBeDormant", "TurretGun"):
                    if need not in blob:
                        raise ExpectationFailed("RM_Ollathrix lacks a %s comp (ambush burst / loom spit): %s" % (need, blob[:200]))

    @suite.chain("thrixweave_and_front")
    def thrixweave_and_front(t):
        """WEBWORK_BASE_PORT_BUILD_1: state reads. Free tier only (the campaign layer repaints the label to shokkweave)."""
        with t.component("hyperweave_reads_thrixweave", beyond_toggle=True):
            f = _deep(t, "ThingDef/Hyperweave", "label")
            if f is not None and "thrixweave" not in "|".join(_flat(f.get("label"))).lower():
                raise ExpectationFailed("Hyperweave label reads %r, expected thrixweave (free tier)" % (f.get("label"),))
        with t.component("trader_strip_applied", toggle="thrixweaveTraderStripEnabled"):
            f = _deep(t, "ThingDef/Hyperweave", "tradeability")
            if f is not None and "Sellable" not in "|".join(_flat(f.get("tradeability"))):
                raise ExpectationFailed("Hyperweave tradeability reads %r with the strip on, expected Sellable" % (f.get("tradeability"),))
        with t.component("rare_trader_resale_line", toggle="thrixweaveResaleEnabled"):
            # WEBWORK_RESELL (Q8, 2026-10-22): Orbital_Exotic carries the resale generator (state read, no trade driven)
            # SHALLOW read on purpose: deep=True renders each generator as a dict of its public fields with no class name
            # (DeepSerializeValue), and the resale generator declares none, so its name is invisible there. Shallow
            # list items are the generators' TYPE names.
            r = t.bridge_call("jawa/get_defs", defs="TraderKindDef/Orbital_Exotic", fields="stockGenerators", deep=False, limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or [] if isinstance(r, dict) else []
                gens = [str(g) for g in ((rows[0].get("fields") or {}).get("stockGenerators") or [])] if rows else []
                if not any(g.startswith("StockGenerator_") for g in gens):
                    _unmeasured(t, "Orbital_Exotic's stockGenerators came back without generator type names, so the "
                                   "resale line is invisible: %s" % str(r)[:200])
                elif "StockGenerator_ThrixweaveResale" not in gens:
                    raise ExpectationFailed("Orbital_Exotic carries no StockGenerator_ThrixweaveResale: %r" % (gens,))
        with t.component("structures_resolve", beyond_toggle=True):
            for n in ("Anchor", "Web", "Gutter"):
                f = _deep(t, "ThingDef/RM_Webwork_" + n, "killedLeavings")
                if f is not None and "Hyperweave" not in "|".join(_flat(f.get("killedLeavings"))):
                    raise ExpectationFailed("RM_Webwork_%s yields no Hyperweave on kill: %r" % (n, f.get("killedLeavings")))

    @suite.chain("scald_binding")
    def scald_binding(t):
        with t.component("sun_scald_hediff_class_is_the_creature_behaviors_one", beyond_toggle=True):
            f = _deep(t, "HediffDef/RM_Webwork_SunScald", "hediffClass")
            if f is not None:
                if "RM_Hediff_SunScald" not in "|".join(_flat(f.get("hediffClass"))):
                    raise ExpectationFailed("RM_Webwork_SunScald hediffClass is %r, not RM_Hediff_SunScald (mandrake.rm.creaturebehaviors)" % (f.get("hediffClass"),))

    def _wp(t, method, args):
        # jawa/static_call splits args on '|' into PARAMETERS; every RM_WebworkProof method takes ONE string, so the proof
        # args travel ';'-joined (live 2026-10-21: '|' answered "No public static ProofWebNetwork with 3 params")
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Webwork.RM_WebworkProof", method=method, args=args.replace("|", ";"))
        text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
        if _live(t) and (not text or text.startswith("REFUSED")):
            # a proof that could not stage (or gave nothing) measured nothing: every arm reads UNMEASURED, never FAIL
            _unmeasured(t, "%s(%s) gave no measurement: %r" % (method, args, text[:160]))
        return text

    def _num(text, key):
        import re as _re
        m = _re.search(key + r" ([\d.\-]+)", text)
        return float(m.group(1)) if m else None

    @suite.chain("map_mechanics")
    def map_mechanics(t):
        """WEBWORK_COVERAGE_GAPS_1. Runs on the CURRENT map through RM_WebworkProof (static_call); each proof sets
        its settings for the call and restores them. Not proven here: the GenStep firing inside real mapgen
        (static: it is in the biome's genSteps, biome_wiring), sun-scald, loom spit."""
        with t.component("nest_placed_by_the_genstep", toggle="nestEnabled"):
            text = _wp(t, "ProofNest", "true")
            if _live(t):
                if not text.startswith("NEST"):
                    _unmeasured(t, "ProofNest gave no answer: %r" % text[:160]); return
                if "biomeGateRefuses False" in text:
                    raise ExpectationFailed("the nest GenStep placed a nest on a non-Webwork map: %s" % text)
                walls = text.split("walls ")[1].split(" |")[0].split("->")
                if not (_num(text, "placed") or 0) >= 1 or int(walls[1]) != int(walls[0]) + 1:
                    raise ExpectationFailed("the nest placement did not lay one wall and >= 1 clutch: %s" % text)
            off = _wp(t, "ProofNest", "false")
            if _live(t) and not ("placed -1" in off and off.split("walls ")[1].split(" |")[0].split("->")[0] == off.split("walls ")[1].split(" |")[0].split("->")[1]):
                raise ExpectationFailed("nestEnabled off still placed a nest: %s" % off)
        with t.component("clutch_relays_every_20_to_30_days", toggle="eggRelayIntervalMultiplier", beyond_toggle=True):
            text = _wp(t, "ProofRelay", "true|1")
            if _live(t):
                if not text.startswith("RELAY"):
                    _unmeasured(t, "ProofRelay gave no answer: %r" % text[:160]); return
                d = _num(text, "intervalDays")
                if d is None or not (20.0 <= d <= 30.0):
                    raise ExpectationFailed("relay interval at multiplier 1 is not 20-30 days: %s" % text)
                if not text.endswith("0->1") and not text.endswith("0->2"):
                    raise ExpectationFailed("a due nest with a living mother and no clutch did not re-lay 1-2: %s" % text)
            half = _wp(t, "ProofRelay", "true|0.5")
            if _live(t):
                d = _num(half, "intervalDays")
                if d is None or not (10.0 <= d <= 15.0):
                    raise ExpectationFailed("eggRelayIntervalMultiplier 0.5 did not halve the interval: %s" % half)
        with t.component("dying_nest_without_mother_relays_nothing", beyond_toggle=True):
            text = _wp(t, "ProofRelay", "false|1")
            if _live(t) and not ("mother False" in text and text.endswith("0->0")):
                raise ExpectationFailed("a nest with no living ollathrix re-laid: %s" % text)
        with t.component("emergent_spawn_on_destroy", toggle="emergentSpawnEnabled"):
            text = _wp(t, "ProofEmergent", "true|1|1|Vanish")
            if _live(t):
                if not text.startswith("EMERGENT"):
                    _unmeasured(t, "ProofEmergent gave no answer: %r" % text[:160]); return
                if "spawned 1" not in text or "manhunter True" not in text:
                    raise ExpectationFailed("a sure harvest (chance 1) did not spawn one manhunter ollathrix: %s" % text)
            for args, why in (("false|1|1|Vanish", "emergentSpawnEnabled off"), ("true|1|1|KillFinalize", "a combat kill (not a harvest)")):
                text = _wp(t, "ProofEmergent", args)
                if _live(t) and "spawned 0" not in text:
                    raise ExpectationFailed("%s still spawned: %s" % (why, text))
        with t.component("emergent_spawn_chance_scales", toggle="emergentSpawnChanceMultiplier", beyond_toggle=True):
            text = _wp(t, "ProofEmergent", "true|0.5|2|Vanish")
            if _live(t) and "spawned 1" not in text:
                raise ExpectationFailed("chance 0.5 x multiplier 2 (= 1) did not spawn: %s" % text)
            text = _wp(t, "ProofEmergent", "true|1|0|Vanish")
            if _live(t) and "spawned 0" not in text:
                raise ExpectationFailed("multiplier 0 still spawned: %s" % text)
        with t.component("creep_web_harvest", toggle="webHarvestEnabled"):
            # SHOKKWEAVE_SOLE_SOURCE_1: designator + WorkGiver accept the node, a Deconstruct drops the silk, and a
            # sure chance (multiplier 34 on base 0.03) spawns the emergent ollathrix. The ticked colonist walk is
            # ProofHarvestDesignate/ProofHarvestRead (bridge item), not this chain.
            text = _wp(t, "ProofHarvest", "true;RM_Webwork_Anchor;34")
            if _live(t):
                if not text.startswith("HARVEST"):
                    _unmeasured(t, "ProofHarvest gave no answer: %r" % text[:160]); return
                if "designatable False" in text and re.search(r"after (\d+) ticks", text) and int(re.search(r"after (\d+) ticks", text).group(1)) >= 250:
                    # Real Fog of War never let the designator see the node within the 250-tick wait: a SITE/HARNESS
                    # miss, not the mod refusing to be cut. Scoring it FAIL read a fog timeout as a mod result.
                    _unmeasured(t, "HARNESS/SITE: the Deconstruct designator never saw the node within the fog-of-war wait: %s" % text[:200]); return
                if not ("designatable True" in text and "workgiver True" in text and "yield 3" in text
                        and "weaveNear 0->3" in text and "spawned 1" in text):
                    raise ExpectationFailed("cutting an anchor line did not designate/yield 3/spawn: %s" % text)
            text = _wp(t, "ProofHarvest", "true;RM_Webwork_Web;0")
            if _live(t) and "designatable False" in text and re.search(r"after (\d+) ticks", text):
                _unmeasured(t, "HARNESS/SITE: the sheet-web arm hit the fog-of-war wait: %s" % text[:200]); return
            if _live(t) and not ("yield 2" in text and "spawned 0" in text):
                raise ExpectationFailed("cutting a sheet web did not yield 2 (or spawned at multiplier 0): %s" % text)
            off = _wp(t, "ProofHarvest", "false;RM_Webwork_Anchor;0")
            if _live(t) and not ("designatable False" in off and "yield 0" in off):
                raise ExpectationFailed("webHarvestEnabled off still lets a colonist cut web for silk: %s" % off)
        with t.component("webwork_competes_for_tiles", toggle="generateOnWorldgen"):
            if _live(t):
                _unmeasured(t, "worldgen-affecting and inert on the frozen world (CLAUDE.md: no worldgen feature); no map can exercise it")
        for name, why in (
            ("sun_scald_in_open_sun", "RM_Hediff_SunScald lives in mandrake.rm.creaturebehaviors: its proof belongs there (an ollathrix in lit sun, ticks)"),
            ("loom_spit_fires", "the ranged spit needs an awake ollathrix and a hostile target"),
        ):
            with t.component(name, beyond_toggle=True):
                if _live(t):
                    _unmeasured(t, why)

    def _field(text, key):
        """The token after `key ` in a proof line (the next ' | ' ends it)."""
        if (key + " ") not in text:
            return None
        return text.split(key + " ", 1)[1].split(" |", 1)[0].strip()

    def _arrow(text, key):
        v = _field(text, key)
        try:
            a, b = v.split("->")
            return int(a), int(b)
        except (AttributeError, ValueError):
            return None

    @suite.chain("web_terrain_weather")
    def web_terrain_weather(t):
        """WEBWORK_TERRAIN_WEATHER_PASS_1. Runs RM_GenStep_WebworkWeb's placement and the webfall gate on the CURRENT map
        through RM_WebworkProof (static_call); each proof sets its settings for the call and restores them."""
        with t.component("web_network_laid", toggle="webNetworkEnabled"):
            text = _wp(t, "ProofWebNetwork", "true|true|1")
            if _live(t):
                if not text.startswith("WEB"):
                    _unmeasured(t, "ProofWebNetwork gave no answer: %r" % text[:160]); return
                if _field(text, "biomeGateRefuses") == "False":
                    raise ExpectationFailed("the web GenStep laid web on a non-Webwork map: %s" % text)
                k, st = _arrow(text, "cables"), _arrow(text, "strands")
                if _field(text, "placed") != "True" or not k or k[1] <= k[0] or not st or st[1] <= st[0]:
                    raise ExpectationFailed("the placement laid no cables or no local webs: %s" % text)
                if not int(_field(text, "sites") or 0) >= 1 or not int(_field(text, "carpet") or 0) > 0:
                    raise ExpectationFailed("no spider site or no silk carpet: %s" % text)
                if _field(text, "carpetOutsideSites") != "0":
                    raise ExpectationFailed("silk carpet laid away from every spider site: %s" % text)
                if _field(text, "cableBlocksPlants") != "False":
                    raise ExpectationFailed("a cable blocks trees (the jungle would be cut into stripes): %s" % text)
                if _field(text, "strandSticky") != "True":
                    raise ExpectationFailed("the local web carries no adhesive: %s" % text)
            off = _wp(t, "ProofWebNetwork", "false|true|1")
            if _live(t):
                k = _arrow(off, "cables")
                if _field(off, "placed") != "False" or (k and k[0] != k[1]):
                    raise ExpectationFailed("webNetworkEnabled off still laid web: %s" % off)
        with t.component("silk_carpet_toggle", toggle="siteCarpetEnabled"):
            text = _wp(t, "ProofWebNetwork", "true|false|1")
            if _live(t) and not (_field(text, "placed") == "True" and _field(text, "carpet") == "0"):
                raise ExpectationFailed("siteCarpetEnabled off still laid carpet (or laid nothing): %s" % text)
        with t.component("local_web_density_zero_lays_none", toggle="localWebDensityMultiplier", beyond_toggle=True):
            text = _wp(t, "ProofWebNetwork", "true|true|0")
            if _live(t):
                st = _arrow(text, "strands")
                if not st or st[0] != st[1]:
                    raise ExpectationFailed("density 0 still laid local webs: %s" % text)
        with t.component("webfall_in_biome_and_occurs", toggle="webfallEnabled"):
            text = _wp(t, "ProofWebfall", "true|6")
            if _live(t):
                if not text.startswith("WEBFALL"):
                    _unmeasured(t, "ProofWebfall gave no answer: %r" % text[:160]); return
                if _field(text, "def") != "True" or _field(text, "inBiome") != "6":
                    raise ExpectationFailed("webfall is not in RM_Webwork's weather table at 6: %s" % text)
                if _field(text, "forcedNow") != "RM_Webfall":
                    raise ExpectationFailed("webfall could not be made the current weather: %s" % text)
                if _field(text, "forcedEvent") != "False" or _field(text, "glowCap") != "1":
                    raise ExpectationFailed("webfall can be forced onto other biomes or dims the sun: %s" % text)
                if _field(text, "overlayMat") != "True":
                    raise ExpectationFailed("the webfall overlay has no material (nothing would drift): %s" % text)
            off = _wp(t, "ProofWebfall", "false|6")
            if _live(t) and not (_field(off, "inBiome") == "0" and _field(off, "forcedNow") == "none"):
                raise ExpectationFailed("webfallEnabled off still leaves webfall in the table: %s" % off)
        with t.component("webfall_commonality_scales", toggle="webfallCommonality", beyond_toggle=True):
            text = _wp(t, "ProofWebfall", "true|12")
            if _live(t) and _field(text, "inBiome") != "12":
                raise ExpectationFailed("webfallCommonality 12 did not reach the table: %s" % text)
        with t.component("generated_webwork_map", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "the bridge cannot generate an RM_Webwork map (our biome sits on 0 tiles until the one end-paint, "
                               "CLAUDE.md); the placement is proven through PlaceWeb on the current map above")

    def _up(t, method, args):
        # RM_UrravethProof (WEBWORK_DEAD_GIANT_BUILD_1): one-string proofs, so args travel ';'-joined like _wp's
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Webwork.RM_UrravethProof", method=method, args=args.replace("|", ";"))
        return str((r or {}).get("result", "")) if isinstance(r, dict) else ""

    @suite.chain("urraveth_remains")
    def urraveth_remains(t):
        """WEBWORK_DEAD_GIANT_BUILD_1 criteria A2, on the CURRENT map through RM_UrravethProof (static_call). Order matters:
        site (chance 0, then 1), read one limb pile, read all, open the skull, then the load gauntlet (idle, clear, leave;
        leave collapses the rib, so it runs last). The planet half of criterion 1 needs no check: the GenStep is a map
        GenStep and the proof never touches Find.WorldGrid (static: RM_UrravethRemains_MapGenPatch.xml)."""
        with t.component("site_chance_zero_places_none", toggle="urravethSiteChance", beyond_toggle=True):
            text = _up(t, "ProofSite", "0")
            if _live(t):
                if not text.startswith("SITE"):
                    _unmeasured(t, "ProofSite gave no answer: %r" % text[:160]); return
                p = _arrow(text, "pieces")
                if _field(text, "rolled") != "False" or not p or p[0] != p[1]:
                    raise ExpectationFailed("site chance 0 still placed remains: %s" % text)
        with t.component("site_places_every_piece_wrapped", toggle="urravethEnabled"):
            text = _up(t, "ProofSite", "1")
            if _live(t):
                if not text.startswith("SITE"):
                    _unmeasured(t, "ProofSite gave no answer: %r" % text[:160]); return
                if _field(text, "rolled") == "True" and _field(text, "placed") in ("0", "-1"):
                    _unmeasured(t, "no open 15x9 ground on this map (SITE skipped, not a mod defect): %s" % text); return
                p, rows = _arrow(text, "pieces"), int(_field(text, "layoutRows") or 0)
                if _field(text, "rolled") != "True" or not p or p[1] - p[0] != rows or rows < 1:
                    raise ExpectationFailed("site chance 1 did not lay one piece per layout row: %s" % text)
                if int(_field(text, "pieceDefs") or 0) < 5 or _field(text, "allWrapped") != "True":
                    raise ExpectationFailed("a piece def is missing or a piece spawned unwrapped: %s" % text)
        with t.component("reading_one_piece_cuts_its_wrapping", toggle="urravethThrixweavePerPiece", beyond_toggle=True):
            text = _up(t, "ProofRead", "RM_Urraveth_LimbPile")
            if _live(t):
                if not text.startswith("READ"):
                    _unmeasured(t, "ProofRead gave no answer: %r" % text[:160]); return
                if _field(text, "wrapped(RM_Urraveth_LimbPile)") != "False" or "pinned" not in (_field(text, "chapters") or ""):
                    raise ExpectationFailed("reading a limb pile did not unwrap it or record 'pinned': %s" % text)
                if int(_field(text, "thrixweaveNear") or 0) < int(_field(text, "perPieceSetting") or 1):
                    raise ExpectationFailed("no thrixweave stack of the configured size beside the read piece: %s" % text)
        with t.component("all_read_then_skull_opens_complete", beyond_toggle=True):
            _up(t, "ProofRead", "all")
            text = _up(t, "ProofRead", "final")
            if _live(t):
                if not text.startswith("READ"):
                    _unmeasured(t, "ProofRead final gave no answer: %r" % text[:160]); return
                if _field(text, "chapters") != "[pinned,bound,cut,eaten]" or _field(text, "complete") != "True":
                    raise ExpectationFailed("the reading is not complete with the four chapters in order: %s" % text)
                if not int(_field(text, "outlineCells") or 0) > 0:
                    raise ExpectationFailed("the urraveth outline was not drawn: %s" % text)
        with t.component("unloaded_bones_never_creak", beyond_toggle=True):
            text = _up(t, "ProofLoad", "0|idle")
            if _live(t) and not (text.startswith("IDLE") and _field(text, "everCreaking") == "False"):
                raise ExpectationFailed("an unloaded rib creaked over 60,000 ticks (or no answer): %s" % text)
        with t.component("load_creaks_and_clearing_saves_it", toggle="urravethWarningHours", beyond_toggle=True):
            text = _up(t, "ProofLoad", "4|clear")
            if _live(t):
                if "CLEAR" not in text:
                    _unmeasured(t, "ProofLoad clear gave no CLEAR answer (mode not reached?): %r" % text[:200]); return
                if _field(text, "creaking") != "True" or _field(text, "ticksLeft") != _field(text, "window"):
                    raise ExpectationFailed("four colonists on a rib did not start a full warning window: %s" % text)
                if _field(text, "CLEAR creaking") != "False" or _field(text, "ribSpawned") != "True" or _field(text, "anyPawnHurt") != "False":
                    raise ExpectationFailed("taking the load off did not end the creak harmlessly: %s" % text)
        with t.component("load_left_collapses_with_rubble_and_spreads", toggle="urravethCollapseDamageMultiplier", beyond_toggle=True):
            text = _up(t, "ProofLoad", "4|leave")
            if _live(t):
                if "LEAVE" not in text:
                    _unmeasured(t, "ProofLoad leave gave no LEAVE answer: %r" % text[:200]); return
                if _field(text, "LEAVE ribGone") != "True" or not int(_field(text, "rubbleCells") or 0) > 0 or _field(text, "pawnDamaged") != "True":
                    raise ExpectationFailed("a rib left loaded past its window did not collapse into rubble and hurt someone: %s" % text)
                nb = _field(text, "neighbour") or ""
                if not nb.startswith("none") and not nb.endswith("creaking True"):
                    raise ExpectationFailed("the piece the rib held up did not start creaking: %s" % text)

    def _lp(t, method, args):
        # RM_TractionLanceProof lives in mandrake.rm.creaturebehaviors (the shared pull); ProofPull takes TWO params, so its
        # args stay '|'-joined (static_call's parameter separator)
        r = t.bridge_call("jawa/static_call", type="RimMandrake.CreatureBehaviors.RM_TractionLanceProof", method=method, args=args)
        return str((r or {}).get("result", "")) if isinstance(r, dict) else ""

    def _kv(text):
        return dict(tok.split("=", 1) for tok in text.split() if "=" in tok)

    @suite.chain("traction_lance")
    def traction_lance(t):
        """WEBWORK_TRACTION_LANCE_BUILD_1 criteria A3 (the parts a proof exists for). RM_TractionLance is this mod's def;
        the pull is CreatureBehaviors' RM_CompTetherPull. Not covered here: per-toggle off effects, and the junction cut
        registering a touch in RM_MapComponent_SenseWeb."""
        def pull(t, stuff, mode):
            text = _lp(t, "ProofPull", "%s|%s" % (stuff, mode))
            if _live(t) and not text.startswith("LANCE"):
                _unmeasured(t, "ProofPull %s/%s gave no answer: %r" % (stuff, mode, text[:160]))
                return None
            return _kv(text) if _live(t) else None
        with t.component("manned_lance_pulls_a_raider", beyond_toggle=True):
            kv = pull(t, "Hyperweave", "raider")
            if kv is not None:
                if kv.get("roped") != "True" or int(kv.get("cellsMoved", "0")) < 1 or float(kv.get("endDist", "99")) >= float(kv.get("startDist", "0")):
                    raise ExpectationFailed("a manned thrixweave lance did not reel a raider toward it: %r" % kv)
        with t.component("unmanned_lance_does_nothing", beyond_toggle=True):
            kv = pull(t, "Hyperweave", "unmanned")
            if kv is not None and (kv.get("roped") != "False" or kv.get("cellsMoved") not in ("0", None)):
                raise ExpectationFailed("an unmanned lance roped or moved its target: %r" % kv)
        with t.component("wall_stops_the_pull", beyond_toggle=True):
            kv = pull(t, "Hyperweave", "wall")
            if kv is not None and kv.get("outcome") != "wall":
                raise ExpectationFailed("a raider behind a steel wall was not stopped with reason 'wall': %r" % kv)
        with t.component("downed_colonist_pulled_in", beyond_toggle=True):
            kv = pull(t, "Hyperweave", "downed")
            if kv is not None and (kv.get("roped") != "True" or int(kv.get("cellsMoved", "0")) < 1):
                raise ExpectationFailed("friendly pull on did not drag a downed colonist in: %r" % kv)
        with t.component("over_mass_target_snaps_a_cloth_tether", beyond_toggle=True):
            kv = pull(t, "Cloth", "heavy")
            if kv is not None and (kv.get("outcome") != "mass" or int(kv.get("snaps", "0")) < 1):
                raise ExpectationFailed("a thrumbo on a cloth tether did not snap it for mass: %r" % kv)
        with t.component("cloth_weaker_than_thrixweave", beyond_toggle=True):
            text = _lp(t, "ProofStuffTable", "")
            if _live(t):
                rows = {}
                for part in text[len("STUFF "):].split(" | ") if text.startswith("STUFF") else []:
                    name, rest = part.split(":", 1)
                    rows[name.strip()] = {k: float(v) for k, v in _kv(rest).items()}
                if "Cloth" not in rows or "Hyperweave" not in rows:
                    _unmeasured(t, "ProofStuffTable gave no Cloth/Hyperweave rows: %r" % text[:200]); return
                c, h = rows["Cloth"], rows["Hyperweave"]
                if not (c["snap"] > h["snap"] and c["range"] < h["range"]):
                    raise ExpectationFailed("cloth is not snappier and shorter than thrixweave: %r" % rows)
        with t.component("friendly_pull_off_leaves_a_downed_colonist", beyond_toggle=True):
            # target chosen the production way (FindTarget); foundOn is the control that proves the proof can see
            kv = pull(t, "Hyperweave", "friendlyoff")
            if kv is not None:
                if kv.get("foundOn") != "True":
                    _unmeasured(t, "control failed: FindTarget did not pick the downed colonist even with friendly pull ON "
                                "(a visible hostile in range outranks it?): %r" % kv); return
                if kv.get("foundOff") != "False" or kv.get("roped") != "False" or kv.get("cellsMoved") != "0":
                    raise ExpectationFailed("friendly pull OFF still picked or dragged a downed colonist: %r" % kv)
        with t.component("ollathrix_pulled_from_shade_into_sun", beyond_toggle=True):
            # the lance needs thrixweave for it: body size 2.6 is over the cloth (1.2) and devilstrand (2.0) caps
            kv = pull(t, "Hyperweave", "ollathrix")
            if kv is not None:
                if kv.get("roped") != "True" or int(kv.get("cellsMoved", "0")) < 1:
                    raise ExpectationFailed("a thrixweave lance did not reel a wild ollathrix: %r" % kv)
                if kv.get("startExposed") != "False":
                    raise ExpectationFailed("the roofed (canopy stand-in) start cell did not read shaded to the scald predicate: %r" % kv)
                if kv.get("sunAtEnd") != "True" or float(kv.get("endShade", "-1")) >= float(kv.get("threshold", "0.5")):
                    _unmeasured(t, "the lance's end cell is not in open sun (night, roof or cast shade): %r" % kv); return
                if kv.get("endExposed") != "True":
                    raise ExpectationFailed("an ollathrix reeled onto a sunlit cell does not read exposed to sun-scald: %r" % kv)

        def door(t, which, item):
            text = _lp(t, "ProofResearchDoor", which)
            if not _live(t):
                return
            if not text.startswith("DOOR"):
                _unmeasured(t, "ProofResearchDoor %s gave no answer: %r" % (which, text[:200])); return
            kv = _kv(text)
            if kv.get("before") != "False" or kv.get("buildableBefore") != "False":
                _unmeasured(t, "could not reset RM_Research_TractionLance to unfinished: %r" % kv); return
            if kv.get("after") != "True" or kv.get("buildable") != "True":
                raise ExpectationFailed("studying %s did not finish RM_Research_TractionLance / make the lance buildable: %r" % (item, kv))
        with t.component("gutter_junction_study_teaches_the_lance", beyond_toggle=True):
            door(t, "junction", "RM_GutterJunction")
        with t.component("sump_drawjoint_study_teaches_the_lance", beyond_toggle=True):
            door(t, "drawjoint", "RUT_PreservedDrawJoint (needs mandrake.rm.thesump loaded)")

    def _sp(t, method, args):
        # RM_WebworkSiegeProof (WEB_SIEGE_DESIGN_SPIDERS_BRING_SHADE): one-string proofs, so args travel ';'-joined like _wp's
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Webwork.RM_WebworkSiegeProof", method=method, args=args.replace("|", ";"))
        return str((r or {}).get("result", "")) if isinstance(r, dict) else ""

    @suite.chain("siege")
    def siege(t):
        """WEB_SIEGE_DESIGN_SPIDERS_BRING_SHADE (design/RimMandrake/webwork_spider_siege_2026-10-22.md section 8), on the CURRENT
        map through RM_WebworkSiegeProof. Order matters: the eligibility gate, then a forced fire (test hook on) whose siege the
        spin and break rows use; break runs last because it kills half the siege. Test pawns and doors are made by the proof."""
        with t.component("setting_off_refuses", toggle="siegeEnabled"):
            off, on = _sp(t, "ProofEligibility", "true|false"), _sp(t, "ProofEligibility", "true|true")
            if _live(t):
                if not (off.startswith("ELIG") and on.startswith("ELIG")):
                    _unmeasured(t, "ProofEligibility gave no answer: %r / %r" % (off[:120], on[:120])); return
                if _field(off, "reason") != "Disabled" or _field(off, "canFire") != "False":
                    raise ExpectationFailed("siegeEnabled off still lets the siege fire: %s" % off)
                if _field(on, "reason") != "Eligible" or _field(on, "canFire") != "True":
                    raise ExpectationFailed("control (on, test hook on) does not let the siege fire: %s" % on)
        with t.component("unshaded_or_unbordered_map_refuses", beyond_toggle=True):
            text = _sp(t, "ProofEligibility", "false|true")
            if _live(t):
                if not text.startswith("ELIG"):
                    _unmeasured(t, "ProofEligibility gave no answer: %r" % text[:160]); return
                if _field(text, "reason") == "Eligible":
                    _unmeasured(t, "this map really is a shaded Webwork neighbour, so the refusal arm cannot be read here: %s" % text); return
                if _field(text, "reason") not in ("NotNeighbour", "ShadeUnmeasurable", "NotShaded", "WebworkMapItself") or _field(text, "canFire") != "False":
                    raise ExpectationFailed("hook off on an ineligible map did not refuse with a named reason: %s" % text)
        with t.component("fires_and_spawns_awake_ollathrix", toggle="siegeTestIgnoreMapChecks"):
            text = _sp(t, "ProofFire", "800")
            if _live(t):
                if not text.startswith("FIRE"):
                    _unmeasured(t, "ProofFire gave no answer: %r" % text[:160]); return
                lords = _arrow(text, "lords")
                if _field(text, "ok") != "True" or not int(_field(text, "spiders") or 0) > 0 or not lords or lords[1] != lords[0] + 1:
                    raise ExpectationFailed("a forced fire did not arrive as one siege lord with spiders: %s" % text)
                if _field(text, "allOllathrix") != "True" or _field(text, "insects") != "True" or _field(text, "dormant") != "0":
                    raise ExpectationFailed("the siege is not awake RM_Ollathrix of the insect faction: %s" % text)
        with t.component("spider_spins_a_web_on_an_unexposed_cell", toggle="siegeSpinSpeed", beyond_toggle=True):
            text = _sp(t, "ProofSpin", "2500")
            if _live(t):
                if not text.startswith("SPIN"):
                    _unmeasured(t, "ProofSpin gave no answer: %r" % text[:160]); return
                if text.startswith("SPIN noCell") or text.startswith("SPIN noSpider") or text.startswith("SPIN noSiege"):
                    _unmeasured(t, "no spider with an unexposed reachable cell near it (sun on a map the grid does not shade?): %s" % text); return
                sp = _arrow(text, "spun")
                if _field(text, "web") != "True" or _field(text, "tagged") != "True" or not sp or sp[1] != sp[0] + 1:
                    raise ExpectationFailed("the spider's spin job did not leave one tagged siege web: %s" % text)
                if _field(text, "exposed") != "False":
                    raise ExpectationFailed("the spider chose a cell the sun-scald predicate reads exposed: %s" % text)
        with t.component("siege_web_slicks_others_not_ollathrix", beyond_toggle=True):
            text = _sp(t, "ProofSlick", "-")   # "" = ZERO params to static_call: never reached (GPT deep review 2026-10-22 #8)
            if _live(t):
                if not text.startswith("SLICK") or _field(text, "after") is None:
                    _unmeasured(t, "ProofSlick gave no answer: %r" % text[:160]); return
                if not float(_field(text, "after")) > float(_field(text, "before") or 0):
                    raise ExpectationFailed("a colonist standing on siege silk gained no RM_Webwork_Slick: %s" % text)
                if float(_field(text, "ollathrixAfter") or 0) > 0:
                    raise ExpectationFailed("an ollathrix stuck in its own silk: %s" % text)
        with t.component("cut_yield_is_capped_per_siege", toggle="siegeSilkYieldCap", beyond_toggle=True):
            text = _sp(t, "ProofCut", "30")
            if _live(t):
                if not text.startswith("CUT cap"):
                    _unmeasured(t, "ProofCut gave no answer: %r" % text[:160]); return
                cap, per, cuts = int(_field(text, "cap")), int(_field(text, "perCut")), int(_field(text, "cuts"))
                want = min(max(cap, 0), cuts * per)
                if int(_field(text, "total")) != want or int(_field(text, "ledger")) != want:
                    raise ExpectationFailed("cutting %d webs did not yield exactly min(cap, cuts x perCut) = %d: %s" % (cuts, want, text))
                if _field(text, "forceBroken") != "0":
                    raise ExpectationFailed("siege silk broken by force yielded thrixweave: %s" % text)
        with t.component("wrapped_door_shut_until_cut", toggle="siegeWrapDoors"):
            text = _sp(t, "ProofDoor", "-")   # "" = ZERO params to static_call: never reached (GPT deep review 2026-10-22 #8)
            if _live(t):
                if not text.startswith("DOOR wrapSpawned"):
                    _unmeasured(t, "ProofDoor gave no answer: %r" % text[:160]); return
                if _field(text, "wrapSpawned") != "True" or _field(text, "wrappedOpens") != "False" or _field(text, "afterCutOpens") != "True":
                    raise ExpectationFailed("a wrapped door opened, or stayed shut after the wrap was cut: %s" % text)
                if _field(text, "controlOpens") != "True" or _field(text, "controlAfter") != "True":
                    raise ExpectationFailed("the unwrapped control door did not open (the patch leaks): %s" % text)
        with t.component("cocoon_cut_open_frees_the_colonist", toggle="siegeCocoonDowned"):
            text = _sp(t, "ProofCocoon", "rescue")
            if _live(t):
                if not text.startswith("COCOON made"):
                    _unmeasured(t, "ProofCocoon gave no answer: %r" % text[:160]); return
                if _field(text, "made") != "True" or _field(text, "inside") != "True" or _field(text, "spawned") != "False":
                    raise ExpectationFailed("the downed colonist was not taken into a cocoon: %s" % text)
                if _field(text, "RESCUE out") != "True" or _field(text, "alive") != "True" or _field(text, "cocoonGone") != "True":
                    raise ExpectationFailed("Open did not free the colonist alive: %s" % text)
        with t.component("cocoon_kills_after_the_deadline", toggle="siegeCocoonDeathHours", beyond_toggle=True):
            text = _sp(t, "ProofCocoon", "deadline")
            if _live(t):
                if "DEADLINE" not in text:
                    _unmeasured(t, "ProofCocoon deadline gave no DEADLINE answer: %r" % text[:200]); return
                if _field(text, "DEADLINE deadBefore") != "False" or _field(text, "deadAfter") != "True" or _field(text, "cause") != "True":
                    raise ExpectationFailed("the cocoon did not kill exactly at its deadline with silk suffocation: %s" % text)
        with t.component("half_lost_breaks_the_siege", toggle="siegeMaxDays", beyond_toggle=True):
            text = _sp(t, "ProofBreak", "-")   # "" = ZERO params to static_call: never reached (GPT deep review 2026-10-22 #8)
            if _live(t):
                if not text.startswith("BREAK killed"):
                    _unmeasured(t, "ProofBreak gave no answer: %r" % text[:160]); return
                if _field(text, "toil") != "LordToil_ExitMap" or _field(text, "letter") != "True":
                    raise ExpectationFailed("losing half the spiders did not break the siege with its letter: %s" % text)

    return suite


suite = _build_suite() if Suite is not None else None


class _MockSession:
    """--mock: answers like a game where the web and webfall work, so web_terrain_weather's plumbing runs offline."""

    def __init__(self):
        self.calls = []
        self.cables = self.strands = 0

    def sweep(self):
        return None

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "jawa/static_call":
            m, a = kw.get("method"), re.split(r"[|;]", kw.get("args") or "")
            if m == "ProofWebNetwork":
                net, carpet, dens = a[0] == "true", a[1] == "true", float(a[2])
                k0, s0 = self.cables, self.strands
                if net:
                    self.cables += 400
                    self.strands += int(250 * dens)
                return {"success": True, "result": "WEB biomeGateRefuses True | placed %s | sites %d | cables %d->%d | strands %d->%d | "
                        "carpet %d | carpetOutsideSites 0 | cableBlocksPlants False | cablePath 30 | strandPath 14 | strandSticky True"
                        % (net, 4 if net else 0, k0, self.cables, s0, self.strands, 300 if (net and carpet) else 0)}
            if m == "ProofWebfall":
                on, c = a[0] == "true", float(a[1])
                inb = c if on else 0
                return {"success": True, "result": "WEBFALL def True | overlayMat True | inBiome %s | share 0.08 | forcedEvent False | "
                        "glowCap 1 | forcedNow %s | installedArt none" % (("%g" % inb), "RM_Webfall" if inb > 0 else "none")}
            return {"success": True, "result": "OK"}
        return {"success": True}


class _MockHarvestSession(_MockSession):
    """--mock: map_mechanics against a game whose Real Fog of War never lets the Deconstruct designator see the node.
    Every earlier proof answers as a working mod; ProofHarvest answers the 250-tick timeout verdict."""

    def call(self, tool, **kw):
        if tool == "jawa/static_call":
            m, a = kw.get("method"), (kw.get("args") or "").replace(";", "|")
            self.calls.append((tool, kw))
            if m == "ProofNest":
                return {"success": True, "result": "NEST biomeGateRefuses True | placed 1 | walls 0->1 | x" if a == "true"
                        else "NEST placed -1 | walls 0->0 | x"}
            if m == "ProofRelay":
                return {"success": True, "result": {"true|1": "RELAY intervalDays 25 | 0->1", "true|0.5": "RELAY intervalDays 12.5 | 0->1",
                                                    "false|1": "RELAY mother False | 0->0"}.get(a, "RELAY")}
            if m == "ProofEmergent":
                return {"success": True, "result": "EMERGENT spawned %d manhunter True" % (1 if a in ("true|1|1|Vanish", "true|0.5|2|Vanish") else 0)}
            if m == "ProofHarvest":
                return {"success": True, "result": "HARVEST designatable False (after 250 ticks) | workgiver False | yield 0 | weaveNear 0->0 | spawned 0"}
        return super(_MockHarvestSession, self).call(tool, **kw)


def mock_harvest_fog_timeout():
    """A fog-of-war wait that timed out is UNMEASURED (site/harness), never a mod FAIL on creep_web_harvest."""
    from runner import run_suite
    chains = list(suite.chains)
    try:
        suite.chains[:] = [c for c in chains if c[0] == "map_mechanics"]
        res = run_suite(suite, _MockHarvestSession(), anchor=(50, 50))
    finally:
        suite.chains[:] = chains
    comps = [c for ch in res.get("chains", []) for c in (ch.get("components") or [])]
    c = [x for x in comps if x.get("name") == "creep_web_harvest"]
    ok = bool(c) and str(c[0].get("verdict", "")).upper() == "UNMEASURED" and "fog-of-war" in str(c[0].get("detail", "")) \
        and not [x for x in comps if str(x.get("verdict", "")).upper() == "FAIL"]
    print("MOCK harvest fog timeout: %s (%s)" % ("PASS" if ok else "FAIL", [(x.get("name"), x.get("verdict")) for x in comps][:8]))
    return ok


class _MockUrravethSession(_MockSession):
    """--mock: urraveth_remains against a working mod. broken="pipe" answers ProofLoad as the pre-2026-10-22 DLL did (it split
    only on '|', so 'N;clear' fell through to the default mode, leave); broken="order" records the chapters out of order."""

    def __init__(self, broken=None):
        _MockSession.__init__(self)
        self.broken, self.pieces = broken, 0

    def call(self, tool, **kw):
        if tool == "jawa/static_call" and kw.get("type") == "RimMandrake.Webwork.RM_UrravethProof":
            self.calls.append((tool, kw))
            m, a = kw.get("method"), kw.get("args") or ""
            if m == "ProofSite":
                b = self.pieces
                if a == "1":
                    self.pieces += 7
                return {"success": True, "result": "SITE rolled %s | placed %d | pieces %d->%d | layoutRows 7 | pieceDefs 5 | allWrapped True | "
                        "RM_Urraveth_Skull=1" % (a == "1", 7 if a == "1" else 0, b, self.pieces)}
            if m == "ProofRead":
                ch = {"RM_Urraveth_LimbPile": "[pinned]", "all": "[pinned,bound,cut,eaten]",
                      "final": "[bound,pinned,cut,eaten]" if self.broken == "order" else "[pinned,bound,cut,eaten]"}[a]
                return {"success": True, "result": "READ x | wrapped(%s) False | chapters %s | complete %s | outlineCells %d | thrixweaveNear 8 | "
                        "perPieceSetting 8" % ("RM_Urraveth_LimbPile" if a != "final" else "RM_Urraveth_Skull", ch, a == "final", 40 if a == "final" else 0)}
            if m == "ProofLoad":
                mode = a.split("|")[-1] if self.broken == "pipe" else re.split(r"[|;]", a)[-1]
                mode = mode if mode in ("clear", "idle") else "leave"
                if mode == "idle":
                    return {"success": True, "result": "IDLE load 0.00 | everCreaking False | spawned True"}
                head = "LOAD pawns 4 | load 4.00 | capacity 3.00 | creaking True | ticksLeft 15000 | window 15000"
                if mode == "clear":
                    return {"success": True, "result": head + " | CLEAR creaking False | ribSpawned True | anyPawnHurt False"}
                return {"success": True, "result": head + " | LEAVE ribGone True | rubbleCells 6 | pawnDamaged True | neighbour RM_Urraveth_Pelvis creaking True"}
        return super(_MockUrravethSession, self).call(tool, **kw)


def mock_urraveth():
    """urraveth_remains: all 7 PASS on a working mod; the old '|'-only split reads UNMEASURED (never PASS) on the idle/clear rows;
    chapters out of order read FAIL."""
    from runner import run_suite
    chains = list(suite.chains)
    out = {}
    try:
        for broken in (None, "pipe", "order"):
            suite.chains[:] = [c for c in chains if c[0] == "urraveth_remains"]
            res = run_suite(suite, _MockUrravethSession(broken), anchor=(50, 50))
            out[broken] = {c.get("name"): str(c.get("verdict", "")).upper()
                           for ch in res.get("chains", []) for c in (ch.get("components") or [])}
    finally:
        suite.chains[:] = chains
    good = out[None]
    ok = len(good) == 7 and set(good.values()) == {"PASS"}
    ok = ok and out["pipe"].get("load_creaks_and_clearing_saves_it") == "UNMEASURED" \
        and out["pipe"].get("unloaded_bones_never_creak") == "FAIL"
    ok = ok and out["order"].get("all_read_then_skull_opens_complete") == "FAIL"
    print("MOCK urraveth: %s (good=%s pipe=%s order=%s)" % ("PASS" if ok else "FAIL", good,
          {k: v for k, v in out["pipe"].items() if v != "PASS"}, {k: v for k, v in out["order"].items() if v != "PASS"}))
    return ok


class _MockLanceSession(_MockSession):
    """--mock: traction_lance against a working pull. broken= "wall" pulls straight through the wall (outcome arrived);
    "friendly" ignores the friendly-pull setting (FindTarget picks the downed colonist with it OFF, and drags it);
    "ollathrix" has no pull for an ollathrix (snaps for mass, as with a body-size cap under 2.6); "door:junction" /
    "door:drawjoint" has no grant on that specimen (its study finishes nothing; one at a time, as a FAIL stops the chain); "night" is a working lance whose end cell is not sunlit (must read UNMEASURED)."""

    def __init__(self, broken=None):
        _MockSession.__init__(self)
        self.broken = broken

    def call(self, tool, **kw):
        if tool == "jawa/static_call" and kw.get("type") == "RimMandrake.CreatureBehaviors.RM_TractionLanceProof":
            self.calls.append((tool, kw))
            if kw.get("method") == "ProofStuffTable":
                return {"success": True, "result": "STUFF Cloth: range=8.4 snap=0.090 maxMass=1.2 | DevilstrandCloth: range=12.0 snap=0.060 "
                        "maxMass=2.0 | Hyperweave: range=15.6 snap=0.030 maxMass=3.0"}
            if kw.get("method") == "ProofResearchDoor":
                door = kw.get("args") or ""
                item = "RM_GutterJunction" if door == "junction" else "RUT_PreservedDrawJoint"
                done = self.broken != "door:" + door
                return {"success": True, "result": "DOOR door=%s item=%s grantComp=True studies=%d before=False buildableBefore=False "
                        "after=%s buildable=%s" % (door, item, 1 if door == "junction" else 2, done, done)}
            stuff, mode = (kw.get("args") or "|").split("|")
            extra = ""
            if mode == "friendlyoff":
                if self.broken == "friendly":
                    extra = " foundOn=True foundOff=True"
                else:
                    extra = " foundOn=True foundOff=False"
            if mode == "ollathrix":
                extra = " startExposed=True" if self.broken == "ollathrix" else " startExposed=False"
                if self.broken == "night":
                    extra += " endExposed=False sunAtEnd=False endShade=0.00 threshold=0.50"
                elif self.broken == "ollathrix":
                    extra += " endExposed=False sunAtEnd=False endShade=-1.00 threshold=0.50"
                else:
                    extra += " endExposed=True sunAtEnd=True endShade=0.00 threshold=0.50"
            moved, end, outcome, snaps, roped = 8, 1.0, "arrived", 0, True
            if mode == "ollathrix" and self.broken == "ollathrix":
                moved, end, outcome, snaps, roped = 0, 9.0, "mass", 1, False
            elif mode == "friendlyoff" and self.broken != "friendly":
                moved, end, outcome, roped = 0, 9.0, "none", False
            elif mode == "unmanned":
                moved, end, outcome, roped = 0, 9.0, "none", False
            elif mode == "wall" and self.broken != "wall":
                moved, end, outcome = 3, 6.0, "wall"
            elif mode == "heavy":
                moved, end, outcome, snaps = 0, 9.0, "mass", 1
            return {"success": True, "result": "LANCE stuff=%s mode=%s canWork=%s roped=%s startDist=9.0 endDist=%.1f cellsMoved=%d steps=8 "
                    "outcome=%s snaps=%d range=15.6 snapChance=0.030 maxMass=3.0 rigging=1.00 mass=80.0 bodySize=2.60%s"
                    % (stuff, mode, roped, roped, end, moved, outcome, snaps, extra)}
        return super(_MockLanceSession, self).call(tool, **kw)


def mock_lance():
    from runner import run_suite
    chains = list(suite.chains)
    out = {}
    try:
        for broken in (None, "wall", "friendly", "ollathrix", "door:junction", "door:drawjoint", "night"):
            suite.chains[:] = [c for c in chains if c[0] == "traction_lance"]
            res = run_suite(suite, _MockLanceSession(broken), anchor=(50, 50))
            out[broken] = {c.get("name"): str(c.get("verdict", "")).upper()
                           for ch in res.get("chains", []) for c in (ch.get("components") or [])}
    finally:
        suite.chains[:] = chains
    red = {"wall": out["wall"].get("wall_stops_the_pull"),
           "friendly": out["friendly"].get("friendly_pull_off_leaves_a_downed_colonist"),
           "ollathrix": out["ollathrix"].get("ollathrix_pulled_from_shade_into_sun"),
           "door_junction": out["door:junction"].get("gutter_junction_study_teaches_the_lance"),
           "door_drawjoint": out["door:drawjoint"].get("sump_drawjoint_study_teaches_the_lance")}
    night = out["night"].get("ollathrix_pulled_from_shade_into_sun")
    ok = (len(out[None]) == 10 and set(out[None].values()) == {"PASS"} and set(red.values()) == {"FAIL"}
          and night not in ("PASS", "FAIL", None))
    print("MOCK lance: %s (good=%s red=%s night=%s)" % ("PASS" if ok else "FAIL", out[None], red, night))
    return ok


class _MockSiegeSession(_MockSession):
    """--mock: the siege chain against a working mod. broken="cap" yields past the cap; "door" leaves a wrapped door
    openable; "nocell" has no unexposed cell near the spider (must read UNMEASURED, never FAIL)."""

    def __init__(self, broken=None):
        _MockSession.__init__(self)
        self.broken, self.lords = broken, 0

    def call(self, tool, **kw):
        if tool == "jawa/static_call" and kw.get("type") == "RimMandrake.Webwork.RM_WebworkSiegeProof":
            self.calls.append((tool, kw))
            m, a = kw.get("method"), re.split(r"[|;]", kw.get("args") or "")
            r = None
            if m == "ProofEligibility":
                hook, on = a[0] == "true", a[1] != "false"
                reason = "Disabled" if not on else ("Eligible" if hook else "ShadeUnmeasurable")
                r = "ELIG reason %s | measurable False | sampled 0 | shaded 0 | canFire %s | why x" % (reason, reason == "Eligible")
            elif m == "ProofFire":
                self.lords += 1
                r = "FIRE ok True | spiders 5 | allOllathrix True | insects True | dormant 0 | lords %d->%d | siegeId 1" % (self.lords - 1, self.lords)
            elif m == "ProofSpin":
                r = "SPIN noCell | spun 0" if self.broken == "nocell" else "SPIN cell (40,40) | exposed False | ticks 640 | web True | tagged True | spun 0->1"
            elif m == "ProofSlick":
                r = "SLICK before 0.000 | after 0.102 | ollathrixAfter 0.000"
            elif m == "ProofCut":
                total = 60 if self.broken == "cap" else 40
                r = "CUT cap 40 | perCut 2 | cuts 30 | total %d | ledger %d | forceBroken 0" % (total, total)
            elif m == "ProofDoor":
                r = "DOOR wrapSpawned True | wrappedOpens %s | controlOpens True | afterCutOpens True | controlAfter True" % (self.broken == "door")
            elif m == "ProofCocoon":
                head = "COCOON made True | inside True | spawned False"
                r = head + (" | DEADLINE deadBefore False | deadAfter True | cause True" if a[0] == "deadline"
                            else " | RESCUE out True | alive True | cocoonGone True")
            elif m == "ProofBreak":
                r = "BREAK killed 3 of 5 | toil LordToil_ExitMap | letter True"
            return {"success": True, "result": r or "?"}
        return super(_MockSiegeSession, self).call(tool, **kw)


def mock_siege():
    """siege: all 10 PASS on a working mod except the refusal arm (PASS); broken cap / door read FAIL; no spin cell reads UNMEASURED."""
    from runner import run_suite
    chains = list(suite.chains)
    out = {}
    try:
        for broken in (None, "cap", "door", "nocell"):
            suite.chains[:] = [c for c in chains if c[0] == "siege"]
            res = run_suite(suite, _MockSiegeSession(broken), anchor=(50, 50))
            out[broken] = {c.get("name"): str(c.get("verdict", "")).upper()
                           for ch in res.get("chains", []) for c in (ch.get("components") or [])}
    finally:
        suite.chains[:] = chains
    good = out[None]
    ok = len(good) == 10 and set(good.values()) == {"PASS"}
    ok = ok and out["cap"].get("cut_yield_is_capped_per_siege") == "FAIL"
    ok = ok and out["door"].get("wrapped_door_shut_until_cut") == "FAIL"
    ok = ok and out["nocell"].get("spider_spins_a_web_on_an_unexposed_cell") == "UNMEASURED"
    print("MOCK siege: %s (good=%s cap=%s door=%s nocell=%s)" % ("PASS" if ok else "FAIL", good,
          {k: v for k, v in out["cap"].items() if v != "PASS"}, {k: v for k, v in out["door"].items() if v != "PASS"},
          {k: v for k, v in out["nocell"].items() if v != "PASS"}))
    return ok


class _MockThrixSession(_MockSession):
    """--mock: thrixweave_and_front against a working mod. broken="noresale" drops StockGenerator_ThrixweaveResale from
    Orbital_Exotic (must FAIL rare_trader_resale_line); "blind" returns rows with no fields (must read UNMEASURED)."""

    def __init__(self, broken=None):
        _MockSession.__init__(self)
        self.broken = broken

    def call(self, tool, **kw):
        if tool != "jawa/get_defs":
            return super(_MockThrixSession, self).call(tool, **kw)
        self.calls.append((tool, kw))
        spec, field = kw.get("defs"), kw.get("fields")
        if field == "stockGenerators" and kw.get("deep") is not False:
            gens = [{"countRange": "1~2"}] * 3      # the real deep shape: field dicts, no class name -> must not be used
        else:                                         # the real shallow shape: each generator's TYPE name
            gens = ["StockGenerator_Tag", "StockGenerator_Category"] + ([] if self.broken == "noresale" else
                                                                       ["StockGenerator_ThrixweaveResale"])
        if self.broken == "blind" and field == "stockGenerators":
            gens = []
        val = {"label": "thrixweave", "tradeability": "Sellable", "stockGenerators": gens,
               "killedLeavings": [{"thingDef": "Hyperweave", "count": 3}]}.get(field)
        return {"success": True, "foundCount": 1, "notFound": [],
                "defs": [{"defName": spec.split("/", 1)[1], "fields": {} if self.broken == "blind" else {field: val}}]}


def mock_thrix():
    """thrixweave_and_front: 4 PASS on a working mod; a missing resale generator FAILs its row; empty fields read UNMEASURED."""
    from runner import run_suite
    chains = list(suite.chains)
    out = {}
    try:
        for broken in (None, "noresale", "blind"):
            suite.chains[:] = [c for c in chains if c[0] == "thrixweave_and_front"]
            res = run_suite(suite, _MockThrixSession(broken), anchor=(50, 50))
            out[broken] = {c.get("name"): str(c.get("verdict", "")).upper()
                           for ch in res.get("chains", []) for c in (ch.get("components") or [])}
    finally:
        suite.chains[:] = chains
    ok = len(out[None]) == 4 and set(out[None].values()) == {"PASS"}
    ok = ok and out["noresale"].get("rare_trader_resale_line") == "FAIL" and out["noresale"].get("trader_strip_applied") == "PASS"
    ok = ok and out["blind"].get("hyperweave_reads_thrixweave") == "UNMEASURED" and "PASS" not in out["blind"].values()
    print("MOCK thrixweave: %s (good=%s noresale=%s blind=%s)" % ("PASS" if ok else "FAIL", out[None], out["noresale"], out["blind"]))
    return ok


def mock_run():
    from runner import run_suite  # modcheck package dir is on sys.path via _UTILS/modcheck
    harvest_ok = all([mock_harvest_fog_timeout(), mock_urraveth(), mock_lance(), mock_siege(), mock_thrix()])  # run every mock
    fake = _MockSession()
    suite.chains[:] = [c for c in suite.chains if c[0] == "web_terrain_weather"]
    res = run_suite(suite, fake, anchor=(50, 50))
    comps = [c for ch in res.get("chains", []) for c in (ch.get("components") or [])]
    v = lambda c: str(c.get("verdict", "")).upper()
    bad = [c for c in comps if v(c) not in ("PASS", "UNMEASURED") or (v(c) == "UNMEASURED" and c.get("name") != "generated_webwork_map")]
    calls = sum(1 for tl, kw in fake.calls if tl == "jawa/static_call")
    ok = len(comps) == 6 and not bad and calls == 7
    ok = harvest_ok and ok
    print("MOCK: %s (%d components, %d proof calls, problems=%s)" % ("PASS" if ok else "FAIL", len(comps), calls,
                                                                    [(c.get("name"), c.get("verdict"), c.get("detail")) for c in bad][:4]))
    return 0 if ok else 1

if __name__ == "__main__":
    if "--mock" in sys.argv:
        sys.path.insert(0, os.path.join(HERE, "..", "Utils", "modcheck"))
        sys.exit(mock_run())
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
