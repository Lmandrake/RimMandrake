"""validation.py -- first script for RimMandrake: Watchers (mandrake.rm.watchers), standalone (owner
ruling 2026-09-30: its own mod, not folded into a biome mod; so no Biomes.compose.json entry).

WATCHER_CREATURES_MOD_1: the kit core (extension, injected comp, hidden hediff, sign, watch job,
medium lock, geophone hook, flush order, settings) and the first member, the piinnok (design
design/RimMandrake/watcher_creatures_kit_design_2026-10-02.md §2-§9; owner card rulings 2026-10-03).
Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Watchers

Offline: `python3 src/RimMandrake/Watchers/validation.py` runs static_checks() only.
The optional non-body cues (gas, heat, fire, steam, shade, buried, light; owner ruling 2026-10-08)
are per-member data under RM_WatcherExtension.cues, each behind its own toggle.
Not proven here (no bridge run yet; each live component says what it needs): the hide/sign cycle,
the facing, the geophone, the flush and bolt. Every one is provable by a STATE read (hediff on the
pawn, sign Thing on the cell, pawn.Rotation, CurJobDef), never by screenshot.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, ".."))
NS = "RimMandrake.Watchers."
suite = Suite("Watchers")
suite.toggles = ["watchersEnabled", "hideAndFlinch", "turnToFace", "stayOnMedium", "geophone", "flushMarksHunt",
                 "flinchRadiusScale", "emergeDelayScale", "maxActivePerMap",
                 "cueGas", "cueHeat", "cueFire", "cueSteam", "cueShade", "cueBuried", "cueLight"]
# The optional non-body cues (owner ruling 2026-10-08, "Full set"): kind -> (toggle, what a live proof needs).
# No shipped member carries a cue yet (members are admitted at each biome's sitting), so each proof needs a
# test race given that cue; the state read is the same as flinch_hides_with_sign (hediff + sign, no body near).
CUES = {
    "gas": ("cueGas", "tox gas spawned on its cell (GenExplosion/gasGrid.AddGas ToxGas) with no pawn within flinch"),
    "heat": ("cueHeat", "its cell's temperature pushed above cues.heat.aboveC (a heater or GenTemperature.PushHeat)"),
    "fire": ("cueFire", "a Fire started within cues.fire.radius; it comes back up after the fire is out and the delay passes"),
    "steam": ("cueSteam", "an RM_SteamDevil spawned within cues.steam.radius (needs mandrake.rm.terminalbiomes)"),
    "shade": ("cueShade", "unroofed at noon: stays hidden; roofed or at night: comes up (with and without the CreatureBehaviors shade grid)"),
    "buried": ("cueBuried", "a murrek carrying RM_MurrekBuried within cues.buried.radius (needs mandrake.rm.bluedesert)"),
    "light": ("cueLight", "a standing lamp lit beside it (GroundGlowAt >= cues.light.minGlow): it hides; lamp off: it comes up"),
}

MEMBERS = {"RM_Piinnok": "RM_DeepSand"}   # race -> its ONE medium (Q9 / Q1 ruling)
NEEDLES = ("mandrake.rm.watchers", "RimMandrake.Watchers", "RM_Watcher", "RM_Piinnok", "[Watchers]")
OWN_DEFS = ["JobDef/RM_WatcherWatch", "JobDef/RM_WatcherRelocate", "JobDef/RM_WatcherFlush",
            "DesignationDef/RM_WatcherFlushMark", "HediffDef/RM_WatcherHidden", "ThinkTreeDef/RM_Watchers",
            "WorkGiverDef/RM_WatcherFlush", "ThingDef/RM_WatcherSign_SandDimple", "ThingDef/RM_Piinnok",
            "PawnKindDef/RM_Piinnok"]


@suite.chain("load")
def load(t):
    with t.component("no_errors_naming_this_mod", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, errorsOnly=True)
        if t._guard():
            if not isinstance(r, dict) or r.get("success") is False:
                raise ExpectationFailed("UNMEASURED: drain_log did not answer")
            msgs = [m.get("text", "") for m in (r.get("messages") or [])]
            hits = [m[:160] for m in msgs if any(n in m for n in NEEDLES)]
            if hits:
                raise ExpectationFailed("errors name this mod: %r" % hits[:4])


@suite.chain("defs")
def defs(t):
    with t.component("own_defs_resolve", beyond_toggle=True):
        if t._guard():
            # A ThingDef whose modExtension Class cannot resolve is discarded whole, so presence is the check.
            r = t.bridge_call("jawa/get_defs", defs=";".join(OWN_DEFS), fields="defName")
            if not isinstance(r, dict) or not r.get("success"):
                raise ExpectationFailed("UNMEASURED: get_defs failed: %r" % (r,))
            if r.get("notFound"):
                raise ExpectationFailed("defs missing: %r" % r.get("notFound"))


@suite.chain("behaviour")
def behaviour(t):
    for comp, tog, why in (
            ("watches_and_faces", "turnToFace",
             "needs a piinnok spawned on RM_DeepSand and a colonist walked round it at 8-14 cells: CurJobDef "
             "RM_WatcherWatch, and pawn.Rotation changes with the colonist's quadrant"),
            ("flinch_hides_with_sign", "hideAndFlinch",
             "needs a colonist moved within 6: RM_WatcherHidden on the pawn AND one RM_WatcherSign_SandDimple on "
             "its cell whose owner is it; both gone after the colonist leaves and the hide delay passes"),
            ("never_hides_off_medium", "stayOnMedium",
             "needs a piinnok spawned on plain Sand: no RM_WatcherWatch job ever; with stayOnMedium on it walks "
             "(RM_WatcherRelocate) onto RM_DeepSand"),
            ("geophone_sinks_field", "geophone",
             "needs a submerged sand swimmer of body size >= 2.5 moved within 14 of a watching piinnok: it hides "
             "with no pawn inside 6 (needs mandrake.rm.biomes for the swimmer and RM_SandSwimUtility)"),
            ("flush_bolts_and_marks_hunt", "flushMarksHunt",
             "needs a hidden piinnok, its sign given RM_WatcherFlushMark, a hunter: hunter runs RM_WatcherFlush, "
             "piinnok CurJobDef Flee, hediff and sign gone, Hunt designation on it"),
            ("hunt_order_sinks_peeker", None,
             "needs a watching piinnok given a Hunt designation: it hides and the designation is removed")):
        with t.component(comp, toggle=tog, beyond_toggle=tog is None):
            if t._guard():
                raise ExpectationFailed("UNMEASURED: " + why)
    for kind, (tog, why) in CUES.items():
        with t.component("cue_%s_hides_and_holds" % kind, toggle=tog):
            if t._guard():
                raise ExpectationFailed("UNMEASURED: needs a watcher carrying cues.%s and %s; and with %s off it ignores it" % (kind, why, tog))


def _xml(*parts):
    return ET.parse(os.path.join(HERE, *parts)).getroot()


def _src(*parts):
    return open(os.path.join(HERE, "Source", *parts), encoding="utf-8").read()


def _all_defs():
    """{(DefType, defName): element} over every Defs/*.xml of this mod."""
    out = {}
    for dp, _dns, fns in os.walk(os.path.join(HERE, "Defs")):
        for fn in fns:
            if fn.endswith(".xml"):
                for e in ET.parse(os.path.join(dp, fn)).getroot():
                    dn = e.findtext("defName")
                    if dn:
                        out[(e.tag, dn)] = e
    return out


def _grep_src_defs(defname, tag):
    """True when some XML under src/RimMandrake (outside this mod) defines <tag> with this defName."""
    pat = re.compile(r"<defName>%s</defName>" % re.escape(defname))
    for dp, dns, fns in os.walk(SRC):
        dns[:] = [d for d in dns if d not in (".git", "obj", "bin", "__pycache__", "Watchers")]
        for fn in fns:
            if fn.endswith(".xml"):
                txt = open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read()
                if pat.search(txt):
                    for e in ET.fromstring(txt.encode("utf-8")).iter(tag):
                        if e.findtext("defName") == defname:
                            return True
    return False


def static_checks():
    """Offline, no game. Returns failure strings; empty means pass."""
    bad = []
    about = _xml("About", "About.xml")
    if about.findtext("packageId") != "mandrake.rm.watchers":
        bad.append("packageId is %s, want mandrake.rm.watchers" % about.findtext("packageId"))
    compose = open(os.path.join(SRC, "Biomes.compose.json"), encoding="utf-8").read()
    if '"source": "Watchers"' in compose:
        bad.append("Watchers is in Biomes.compose.json, but it was ruled standalone (2026-09-30)")

    d = _all_defs()
    for ref in OWN_DEFS:
        tag, dn = ref.split("/")
        if (tag, dn) not in d:
            bad.append("%s not defined in this mod" % ref)

    # Every Class / driverClass / giverClass / thingClass of ours names a class the source defines.
    classes = set()
    for f in os.listdir(os.path.join(HERE, "Source")):
        if f.endswith(".cs"):
            classes |= set(re.findall(r"\bclass (\w+)", _src(f)))
    named = set()
    for dp, _dns, fns in os.walk(HERE):
        for fn in fns:
            if fn.endswith(".xml"):
                txt = open(os.path.join(dp, fn), encoding="utf-8").read()
                named |= set(re.findall(r"RimMandrake\.Watchers\.(\w+)", txt))
    for c in sorted(named - classes):
        bad.append("XML names RimMandrake.Watchers.%s, which no source file defines" % c)

    # DefOf fields match defs of the right type.
    defof = _src("RM_WatchersDefOf.cs")
    for typ, name in re.findall(r"public static (\w+) (\w+);", defof):
        if (typ, name) not in d:
            bad.append("DefOf %s %s has no matching def (it would be null at startup)" % (typ, name))

    hidden = d.get(("HediffDef", "RM_WatcherHidden"))
    if hidden is not None:
        inv = [li for li in hidden.findall("comps/li") if li.get("Class") == "HediffCompProperties_Invisibility"]
        if len(inv) != 1 or inv[0].findtext("visibleToPlayer") != "false":
            bad.append("RM_WatcherHidden must carry one HediffCompProperties_Invisibility with visibleToPlayer false")

    # Signs: Ethereal RM_WatcherSign (never blocks, wipes plants, gets hauled or cleaned).
    base = [e for e in ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Misc", "RM_WatcherSigns.xml")).getroot()
            if e.get("Name") == "RM_WatcherSignBase"]
    if not base or base[0].findtext("thingClass") != NS + "RM_WatcherSign" or base[0].findtext("category") != "Ethereal":
        bad.append("RM_WatcherSignBase must be an Ethereal RimMandrake.Watchers.RM_WatcherSign")

    tt = d.get(("ThinkTreeDef", "RM_Watchers"))
    if tt is not None:
        nodes = [li.get("Class") for li in tt.findall("thinkRoot/subNodes/li")]
        if tt.findtext("insertTag") != "Animal_PreWander" or nodes != [NS + "RM_JobGiver_Watch", NS + "RM_JobGiver_WanderInMedium"]:
            bad.append("RM_Watchers think tree must insert at Animal_PreWander: watch, then wander-in-medium")

    patch = open(os.path.join(HERE, "Patches", "RM_Watchers_OrdersDesignator.xml"), encoding="utf-8").read()
    if 'DesignationCategoryDef[defName="Orders"]/specialDesignatorClasses' not in patch or NS + "RM_Designator_Flush" not in patch:
        bad.append("Flush designator is not patched into Orders")

    # Members.
    for race, medium in MEMBERS.items():
        td, pk = d.get(("ThingDef", race)), d.get(("PawnKindDef", race))
        if td is None or pk is None:
            continue
        ext = [li for li in td.findall("modExtensions/li") if li.get("Class") == NS + "RM_WatcherExtension"]
        if len(ext) != 1:
            bad.append("%s carries %d RM_WatcherExtension (want 1)" % (race, len(ext)))
            continue
        ext = ext[0]
        med = ext.findall("mediumTerrains/li")
        if [li.text for li in med] != [medium]:
            bad.append("%s medium is %s, ruled ONE medium %s" % (race, [li.text for li in med], medium))
        if ext.findtext("hiddenHediff") is None or ("HediffDef", ext.findtext("hiddenHediff")) not in d:
            bad.append("%s hiddenHediff does not name a hediff of this mod" % race)
        if ("ThingDef", ext.findtext("signDef") or "") not in d:
            bad.append("%s signDef does not name a sign of this mod" % race)
        fl, wr = float(ext.findtext("flinchRadius") or "6"), float(ext.findtext("watchRadius") or "14")
        if not 0 < fl <= wr:
            bad.append("%s needs 0 < flinchRadius <= watchRadius" % race)
        # Design §5 trap: a swimming sprite outranks the stationary peek on IsWater deep sand.
        stages = pk.findall("lifeStages/li")
        if not stages or any(s.find("stationaryGraphicData") is None for s in stages):
            bad.append("%s: every life stage needs stationaryGraphicData (the peek pose, Q2 two pictures)" % race)
        if any(s.find("swimmingGraphicData") is not None for s in stages):
            bad.append("%s has swimmingGraphicData: it would hide the peek pose on deep sand (design §5)" % race)
        if td.findtext("race/waterSeeker") != "true" or td.findtext("race/waterCellCost") is None:
            bad.append("%s needs race waterSeeker true + waterCellCost (vanilla wander refuses avoidWander deep sand otherwise)" % race)
        if not _grep_src_defs(medium, "TerrainDef"):
            bad.append("%s medium %s is defined nowhere under src/RimMandrake" % (race, medium))
        for li in td.findall("butcherProducts/*"):
            if not _grep_src_defs(li.tag, "ThingDef"):
                bad.append("%s butchers to %s, defined nowhere under src/RimMandrake" % (race, li.tag))
            if li.get("MayRequire") != "mandrake.rm.biomes":
                bad.append("%s butcher product %s lacks MayRequire mandrake.rm.biomes (standalone mod)" % (race, li.tag))
        for li in td.findall("modExtensions/li"):
            if li.get("Class", "").startswith("RimMandrake.CreatureBehaviors.") and li.get("MayRequire") != "mandrake.rm.biomes":
                bad.append("%s CreatureBehaviors extension lacks MayRequire mandrake.rm.biomes (else the def is discarded alone)" % race)
        # One home: at most one of our BiomeDefs lists it.
        homes = set()
        for dp, dns, fns in os.walk(SRC):
            dns[:] = [x for x in dns if x not in (".git", "obj", "bin", "__pycache__")]
            for fn in fns:
                if fn.endswith(".xml"):
                    txt = open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read()
                    if "<%s" % race in txt and ("BiomeDef" in txt or "wildAnimals" in txt):
                        homes.add(os.path.relpath(os.path.join(dp, fn), SRC))
        if len(homes) > 1:
            bad.append("%s wired into more than one biome file %s (animals belong to ONE biome)" % (race, sorted(homes)))

    # The geophone binds CreatureBehaviors by reflection: the signature must still match.
    cb = os.path.join(SRC, "CreatureBehaviors", "Source", "RM_CompSandSwim.cs")
    if not re.search(r"public static class RM_SandSwimUtility", open(cb, encoding="utf-8").read()) or not re.search(
            r"public static int SubmergedSwimmersNear\(Map map, IntVec3 cell, float radius, float minBodySize, List<Pawn> results = null\)",
            open(cb, encoding="utf-8").read()):
        bad.append("CreatureBehaviors RM_SandSwimUtility.SubmergedSwimmersNear signature changed: the geophone reflection binds nothing")
    # The shade cue binds CreatureBehaviors' shade grid by reflection: ShadeAt(IntVec3) -> float and SunHeatActive.
    sg = open(os.path.join(SRC, "CreatureBehaviors", "Source", "RM_MapComponent_ShadeGrid.cs"), encoding="utf-8").read()
    if not re.search(r"public float ShadeAt\(IntVec3 cell\)", sg) or not re.search(r"public bool SunHeatActive\b", sg) \
            or "namespace RimMandrake.CreatureBehaviors" not in sg:
        bad.append("CreatureBehaviors RM_MapComponent_ShadeGrid.ShadeAt/SunHeatActive changed: the shade cue binds nothing")
    if '"RimMandrake.CreatureBehaviors.RM_MapComponent_ShadeGrid"' not in _src("RM_WatcherCues.cs"):
        bad.append("shade-grid reflection target string missing from RM_WatcherCues.cs")
    # Each cue kind has its toggle read where the cue is read.
    cues_src = _src("RM_WatcherCues.cs")
    for kind, (tog, _why) in CUES.items():
        if "c.%s != null && RM_WatchersSettings.%s" % (kind, tog) not in cues_src:
            bad.append("cue %s is not gated by its toggle %s" % (kind, tog))
    util = _src("RM_WatcherUtility.cs")
    if '"RimMandrake.CreatureBehaviors.RM_SandSwimUtility"' not in util:
        bad.append("geophone reflection target string missing from RM_WatcherUtility.cs")

    src_dir = os.path.join(HERE, "Source")
    proj = open(os.path.join(src_dir, "RM_Watchers.csproj"), encoding="utf-8").read()
    for f in os.listdir(src_dir):
        if f.endswith(".cs") and ('Compile Include="%s"' % f) not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % f)
    mod = _src("RM_WatchersMod.cs")
    for f in suite.toggles:
        if not re.search(r'Scribe_Values\.Look\(ref %s, "%s"' % (f, f), mod):
            bad.append("toggle %s is not Scribed" % f)
    if "maxOneColumn = true" not in mod or "BeginScrollView" not in mod:
        bad.append("settings screen does not scroll with maxOneColumn (Webwork cfdba9344)")
    keyed = open(os.path.join(HERE, "Languages", "English", "Keyed", "RM_Watchers.xml"), encoding="utf-8").read()
    used = set()
    for f in os.listdir(src_dir):
        if f.endswith(".cs"):
            used |= set(re.findall(r'"(RM_Watchers_[A-Za-z_]+)"', _src(f)))
    for k in sorted(used):
        if "<%s>" % k not in keyed:
            bad.append("keyed string %s missing" % k)
    asm = os.path.join(HERE, "Assemblies", "RimMandrake.Watchers.dll")
    if not os.path.isfile(asm) or not os.path.isfile(asm + ".srchash"):
        bad.append("no DLL + .srchash at %s" % asm)
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
