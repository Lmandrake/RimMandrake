"""validation.py -- first script for RimMandrake: Watchers (mandrake.rm.watchers), standalone (owner
ruling 2026-09-30: its own mod, not folded into a biome mod; so no Biomes.compose.json entry).

WATCHER_CREATURES_MOD_1: the kit core (extension, injected comp, hidden hediff, sign, watch job,
medium lock, geophone hook, death action + remains, alarm ripple, settings) and the first member,
the piinnok (design
design/RimMandrake/watcher_creatures_kit_design_2026-10-02.md §2-§9; owner card rulings 2026-10-03).
Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Watchers

Offline: `python3 src/RimMandrake/Watchers/validation.py` runs static_checks() only.
The optional non-body cues (gas, heat, fire, steam, shade, buried, light; owner ruling 2026-10-08)
are per-member data under RM_WatcherExtension.cues, each behind its own toggle.
Owner rulings 2026-10-08 (DEATH card): no flushing; a hidden watcher cannot be targeted, a visible one
is an ordinary target; almost no damage kills one, and area damage (fire, explosions, acid) reaches a
hidden one because the hidden hediff never despawns it; death leaves small sad remains; a bounded
alarm ripple spreads to about 5 neighbours (its own toggle).
Not proven here (no bridge run yet; each live component says what it needs): the hide/sign cycle,
the facing, the geophone, area death while hidden, the remains, the ripple, save/load repair. Every
one is provable by a STATE read (hediff on the pawn, sign Thing on the cell, pawn.Rotation,
CurJobDef, Dead, things on the cell), never by screenshot.
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
suite.toggles = ["watchersEnabled", "hideAndFlinch", "turnToFace", "stayOnMedium", "geophone", "alarmRipple",
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
OWN_DEFS = ["JobDef/RM_WatcherWatch", "JobDef/RM_WatcherRelocate", "HediffDef/RM_WatcherHidden", "ThinkTreeDef/RM_Watchers",
            "ThingDef/RM_WatcherSign_SandDimple", "ThingDef/RM_Piinnok", "PawnKindDef/RM_Piinnok", "ThingDef/RM_WatcherRemains_Piinnok"]


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
            ("hunt_order_dropped_when_it_hides", None,
             "needs a watching piinnok given a Hunt designation and a hunter: while visible the hunter may shoot it; a colonist "
             "stepping inside 6 sends it under and the Hunt designation is gone the same step (the hunt job fails)"),
            ("aoe_kills_hidden", None,
             "needs three hidden piinnok (RM_WatcherHidden on each): a frag grenade / GenExplosion Bomb on one, a Fire started on "
             "another's cell, an acid spray (Proj_Acid) on the third: each Dead, no RM_WatcherSign naming it left on the map"),
            ("hidden_not_targetable", None,
             "needs a hidden piinnok and a drafted colonist: no attack order can target it (FloatMenu/Verb.CanHitTargetFrom); "
             "a visible one is targeted and killed by one hit"),
            ("death_leaves_remains", None,
             "needs a piinnok killed (visible or hidden): no Corpse of RM_Piinnok, one RM_WatcherRemains_Piinnok on or by its cell, "
             "no RM_WatcherSign whose owner is it, no RM_WatcherHidden visible on anything"),
            ("alarm_ripple_bounded", "alarmRipple",
             "needs 8 watching piinnok within 6 cells of each other and a colonist stepped beside one: that one hides, then at most "
             "5 others hide over the next ~3 s with no colonist inside their flinch radius, and nothing more after 10 s; with "
             "alarmRipple off only the approached one hides"),
            ("save_load_repairs_signs", None,
             "needs a hidden piinnok saved and reloaded: exactly one sign naming it after load; a sign whose owner was killed "
             "or is no longer in its watch job is gone within 250 ticks"),
            ("lifecycle_full", None,
             "the piinnok full lifecycle on one map: spawn on RM_DeepSand, watch, hide + sign, emerge, interrupted job (drafted "
             "tame / forced job), hunger emerge, injury, AOE death while hidden, save/load, medium loss (off deep sand -> "
             "RM_WatcherRelocate), settings off (watchersEnabled false -> no hide, no sign)")):
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

    # Owner ruling 2026-10-08: watchers cannot be flushed. No flush machinery may come back.
    for dp, _dns, fns in os.walk(HERE):
        if "SelfTest" in dp or "Assemblies" in dp:
            continue
        for fn in fns:
            if fn.endswith((".cs", ".xml")) and re.search(r"Flush|boltTicks|Bolting", open(os.path.join(dp, fn), encoding="utf-8").read()):
                bad.append("flush machinery survives in %s (watchers cannot be flushed, 2026-10-08)" % fn)

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
        rd = ext.findtext("remainsDef")
        if not rd or ("ThingDef", rd) not in d:
            bad.append("%s has no remainsDef of this mod (every member owes a death asset, 2026-10-08)" % race)
        bhs = float(td.findtext("race/baseHealthScale") or "1")
        if not 150 * bhs <= float(ext.findtext("maxLethalDamage") or "5"):
            bad.append("%s dies at %g damage, above its maxLethalDamage (almost no damage destroys a watcher)" % (race, 150 * bhs))
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
