"""validation.py -- modcheck suite for RimMandrake: Creature Behaviors (mandrake.rm.creaturebehaviors).

FIRST CHAIN: the footprint grid (FOOTPRINT_TRACK_GRID_1). CreatureBehaviors is a shared engine of ~50
mechanics; this file starts with the track grid and is meant to grow one chain per mechanic. No walk doc
exists for this mod yet (design/validation_walks/RimMandrake/CreatureBehaviors.md is owed).

WHAT IS READ. The grid is read as STATE, never pixels: `RM_TrackGridDiag` (Source/RM_TrackGridDiag.cs)
is a static class of session counters (printsWritten, invisiblePrintsWritten, lastPrintCell,
lastPrintInvisible, lastPoolCount ...) that `jawa/mod_settings_field action=list` reads by type name,
so no new bridge tool is needed. Every assertion is on a BEFORE/AFTER delta taken inside the chain, so a
previous session's counters never satisfy a check. The section-layer draw is not judged here (appearance).

THE SURFACE. Only a terrain or filth carrying RM_TrackSurfaceExtension takes prints. Today the only
wired consumer is the Stillsand (Stillsand/Patches/RM_TrackSurface_Stillsand.xml: Sand and RM_DeepSand,
biome-filtered to RM_Stillsand). The Warscar's settled film (RM_Filth_SettledFilm) is not built yet
(WARSCAR_SETTLING_WEATHER_1). So the walking arms need the CURRENT MAP to be an RM_Stillsand map
(`jawa/map_info` mapBiome); on any other map they record UNMEASURED with that reason, never PASS or
FAIL. The Stillsand suite's `site` chain builds such a map; run this suite on it, or after it.

EVERY CHECK CAN FAIL. The print arm has a gravel control (same walk, no surface: zero prints) and the
toggle arm turns tracksEnabled off and expects zero; so a harness that moves nothing reads UNMEASURED
(the walk did not happen: stepsSeen did not move), never PASS.

NOT DRIVEN HERE: eviction order and the cap, save/load byte identity, the downwind sweep order (all
proven offline by Utils/selftest_track_grid.py on the real RM_TrackPool.cs); the print sprites and
opacity (appearance); the erasers (each biome brings its own, none wired yet).
"""
import contextlib
import re
import sys
import time

from modcheck import Suite, ExpectationFailed

suite = Suite("CreatureBehaviors")
suite.toggles = ["tracksEnabled", "verminBreedingEnabled", "gnawBehaviorEnabled", "eatCleanableBehaviorEnabled",
                 "seekShadeBehaviorEnabled", "seekMarkedTerrainBehaviorEnabled", "sunScaldEnabled", "senseWebEnabled",
                 "chewAnchorsBehaviorEnabled", "frontCreepEnabled", "aquaticAmbushEnabled", "parentalEnrageEnabled",
                 "drumLureEnabled"]

SETTINGS = "RimMandrake.CreatureBehaviors.RM_CreatureBehaviorsSettings"
DIAG = "RimMandrake.CreatureBehaviors.RM_TrackGridDiag"
HARMONY_ID = "mandrake.rm.creaturebehaviors.trackgrid"
SURFACE_BIOME = "RM_Stillsand"
INVISIBILITY_HEDIFF = "PsychicInvisibility"    # Royalty; HediffComp_Invisibility (RimSage search_defs)
WALK = 12                                       # cells walked per arm
MISSING_TOOL = re.compile(r"(unknown|no such) tool|not (found|registered)|Method not found", re.I)


class _Unmeasured(Exception):
    pass


def _live(t):
    return t.session is not None and not t.upstream_failed


def _unmeasured(t, why):
    t._why = why
    t._record("UNMEASURED", why)
    t.upstream_failed = True
    raise _Unmeasured(why)


@contextlib.contextmanager
def _comp(t, name, **kw):
    """t.component() that keeps an UNMEASURED reason, reads a missing bridge tool as UNMEASURED, and
    does not let one red arm poison the next (the arms are independent)."""
    before = t.upstream_failed
    t._why = None
    with t.component(name, **kw) as tt:
        yield tt
    c = t.components[-1]
    why = getattr(t, "_why", None)
    if why and not before:
        c.detail = "UNMEASURED: %s" % why
        t.upstream_failed = False
    elif c.verdict == "FAIL" and not before:
        if MISSING_TOOL.search(str(c.detail)):
            c.verdict = "UNMEASURED"
            c.detail = "UNMEASURED: a bridge tool this check needs is unavailable (%s)" % str(c.detail)[:200]
        t.upstream_failed = False
    t._why = None
    if t.session is not None:
        print("[creaturebehaviors] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict),
              str(c.detail or "")[:300], file=sys.stderr, flush=True)


def _diag(t):
    """The grid's counters as {name: str}. UNMEASURED if the type cannot be read."""
    r = t.bridge_call("jawa/mod_settings_field", typeName=DIAG, action="list")
    if not _live(t):
        return {}
    if not isinstance(r, dict) or not r.get("success"):
        _unmeasured(t, "could not read %s: %s" % (DIAG, str(r)[:200]))
    return {f.get("name"): f.get("value") for f in r.get("fields") or []}


def _int(d, k):
    try:
        return int(d.get(k))
    except (TypeError, ValueError):
        raise ExpectationFailed("diag field %s unreadable: %r" % (k, d.get(k)))


def _need_surface_map(t):
    mi = t.bridge_call("jawa/map_info")
    if not _live(t):
        return
    biome = (mi or {}).get("mapBiome") or ((mi or {}).get("tileInfo") or {}).get("biome")
    if biome != SURFACE_BIOME:
        _unmeasured(t, "current map is %r; the only wired track surface is %s sand (no Warscar film yet)"
                    % (biome, SURFACE_BIOME))
    if mi.get("sizeX") and mi.get("sizeZ"):
        t.anchor = (int(mi["sizeX"]) // 2, int(mi["sizeZ"]) // 2)


def _lay(t, terrain, dz):
    x, z = t.anchor
    t.bridge_call("jawa/set_roof_batch", ops="%d,%d,%d,%d" % (x - 2, z + dz - 2, WALK + 6, 5), roofDef="None")
    t.bridge_call("jawa/set_terrain_batch", ops="%s:%d,%d,%d,%d" % (terrain, x - 2, z + dz - 2, WALK + 6, 5),
                  layer="top")


def _walk(t, dz, hediff=None):
    """Spawn a colonist at the strip's west end, optionally make it invisible, walk it east. Returns
    the diag before and after, and the cells the walker covered on the x axis (from its position)."""
    x, z = t.anchor
    t.anchor = (x, z + dz)
    pid = t.spawn_pawn("Colonist")
    t.anchor = (x, z)
    if _live(t) and not pid:
        _unmeasured(t, "could not spawn a walker")
    if hediff:
        r = t.bridge_call("jawa/pawn_health", pawn=pid, action="add", hediff=hediff, severity=1.0)
        if _live(t) and not (r or {}).get("success"):
            _unmeasured(t, "pawn_health add %s failed: %s" % (hediff, str(r)[:160]))
    before = _diag(t)
    t.walk_over(pid, [(x + WALK, z + dz)], wait_ticks=900)
    after = _diag(t)
    moved = 0
    if _live(t):
        px, _ = t._pawn_pos(pid)
        moved = (int(px) - x) if px is not None else 0
    return before, after, moved


def _delta(before, after, k):
    return _int(after, k) - _int(before, k)


@suite.chain("track_grid")
def track_grid(t):
    with _comp(t, "writer_patched", beyond_toggle=True):
        r = t.bridge_call("jawa/harmony_patches", typeName="Pawn_FilthTracker", methodName="Notify_EnteredNewCell")
        if _live(t):
            if not r or r.get("success") is False:
                _unmeasured(t, "harmony_patches could not read Pawn_FilthTracker.Notify_EnteredNewCell: %s"
                            % str(r)[:200])
            if HARMONY_ID not in repr(r):
                raise ExpectationFailed("no postfix owned by %s on Pawn_FilthTracker.Notify_EnteredNewCell: %s"
                                        % (HARMONY_ID, str(r)[:300]))
        _diag(t)   # the diag type must be loaded and readable

    with _comp(t, "walker_lays_prints", beyond_toggle=True):
        _need_surface_map(t)
        t.clear_area(size=WALK + 12)
        _lay(t, "Sand", 0)
        _lay(t, "Gravel", 6)
        b, a, moved = _walk(t, 0)
        if _live(t):
            if _delta(b, a, "stepsSeen") < WALK // 2:
                _unmeasured(t, "the walker did not walk (stepsSeen +%d)" % _delta(b, a, "stepsSeen"))
            n = _delta(b, a, "printsWritten")
            if n < WALK // 2:
                raise ExpectationFailed("a %d-cell walk on %s sand laid %d prints" % (WALK, SURFACE_BIOME, n))
            if _int(a, "lastPoolCount") < 1:
                raise ExpectationFailed("prints written but the grid holds none")
        b, a, moved = _walk(t, 6)    # control: gravel takes no prints
        if _live(t):
            if _delta(b, a, "stepsSeen") < WALK // 2:
                _unmeasured(t, "the control walker did not walk")
            if _delta(b, a, "printsWritten") != 0:
                raise ExpectationFailed("gravel took %d prints (control)" % _delta(b, a, "printsWritten"))

    with _comp(t, "invisible_walker_recorded_flagged", beyond_toggle=True):
        _need_surface_map(t)
        t.clear_area(size=WALK + 12)
        _lay(t, "Sand", 0)
        b, a, moved = _walk(t, 0, hediff=INVISIBILITY_HEDIFF)
        if _live(t):
            if _delta(b, a, "stepsSeen") < WALK // 2:
                _unmeasured(t, "the invisible walker did not walk")
            n = _delta(b, a, "invisiblePrintsWritten")
            if n < WALK // 2:
                raise ExpectationFailed("an invisible walker laid %d flagged prints over %d cells" % (n, WALK))
            if str(a.get("lastPrintInvisible")).lower() != "true":
                raise ExpectationFailed("last print not flagged invisible: %r" % a.get("lastPrintInvisible"))
            if _int(a, "lastPoolInvisible") < 1:
                raise ExpectationFailed("the grid holds no flagged record after an invisible walk")

    with _comp(t, "toggle_off_no_prints", toggle="tracksEnabled"):
        _need_surface_map(t)
        t.clear_area(size=WALK + 12)
        _lay(t, "Sand", 0)
        t.set_setting(SETTINGS, {"tracksEnabled": False})
        try:
            b, a, moved = _walk(t, 0)
        finally:
            t.set_setting(SETTINGS, {"tracksEnabled": True})
        if _live(t):
            # stepsSeen counts only while tracks are on, so it cannot prove the walk here: read the position.
            if moved < WALK // 2:
                _unmeasured(t, "the walker did not walk (moved %d cells)" % moved)
            if _delta(b, a, "printsWritten") != 0:
                raise ExpectationFailed("tracksEnabled=false still laid %d prints" % _delta(b, a, "printsWritten"))

    # The Stillsand's eraser (Stillsand RM_DuneTrackEraser.cs, a postfix on SandGrid.SetDepth): a print on a
    # sand cell is gone once that cell's sand moves by 0.3. Needs an RM_Stillsand map (the biome filter).
    with _comp(t, "stillsand_moving_sand_erases_print", beyond_toggle=True):
        _need_surface_map(t)
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Stillsand.RM_DuneTrackEraser",
                          method="ProofErase", args="current|0.3")
        res = str((r or {}).get("result", ""))
        if _live(t):
            if res.startswith("REFUSED") or not res:
                _unmeasured(t, "eraser proof could not run: %r" % (r,))
            if res != "printed=True erased=True":
                raise ExpectationFailed("moving sand did not bury the print: %r" % res)

# ---- CREATUREBEHAVIORS_COVERAGE_GAPS_1: one component per mechanic toggle -------------------------------------
# Each component asserts, per mechanic: (1) the C# classes that DO the job are loaded in the running game
# (`jawa/type_probe` resolved, and an absent-type control reads resolved=False), (2) the defs that carry it
# resolve (`jawa/get_defs` success + foundCount, never a substring), (3) the toggle's off arm: the Mod Settings
# field flips to False, reads back False, and is restored to True in a finally. What this does NOT prove is the
# behaviour in motion (a vermin breeding, a pawn gnawing): that needs a spawned carrier race on a real map, and
# the carriers live in other mods (Greentide/Miasma/Webwork/LanternDeeps) that this suite's list does not load, so
# the walk marks the in-motion lines UNCOVERED with that reason. Gate field names are the real statics of
# RM_CreatureBehaviorsSettings (Source/RM_CreatureBehaviorsMod.cs).
NS = "RimMandrake.CreatureBehaviors."
ABSENT_TYPE = NS + "NoSuchType_Probe"

# field -> (types that do the job, "DefType/DefName" carriers this mod itself ships)
MECHANICS = [
    ("verminBreedingEnabled", ["RM_CompVerminBreeder", "RM_MapComponent_VerminPopulation", "RM_Alert_VerminPopulationBase"], []),
    ("gnawBehaviorEnabled", ["RM_JobDriver_Gnaw", "RM_JobGiver_GnawTargets", "RM_GnawTargetExtension"],
     ["JobDef/RM_Gnaw", "ThinkTreeDef/RM_ThinkTree_VerminBehaviors"]),
    ("eatCleanableBehaviorEnabled", ["RM_JobDriver_EatCleanable", "RM_ThinkNode_EatCleanable", "RM_EatCleanableExtension"],
     ["JobDef/RM_EatCleanable"]),
    ("seekShadeBehaviorEnabled", ["RM_JobGiver_SeekShade"], ["ThinkTreeDef/RM_ThinkTree_VerminBehaviors"]),
    ("seekMarkedTerrainBehaviorEnabled", ["RM_JobGiver_SeekMarkedTerrain"], ["ThinkTreeDef/RM_ThinkTree_VerminBehaviors"]),
    ("sunScaldEnabled", ["RM_Hediff_SunScald"], []),
    ("senseWebEnabled", ["RM_MapComponent_SenseWeb", "RM_CompSenseWebNode"], []),
    ("chewAnchorsBehaviorEnabled", ["RM_JobGiver_ChewAnchors", "RM_ChewAnchorsConsumerExtension", "RM_ChewableExtension"],
     ["ThinkTreeDef/RM_ChewAnchors_Consume"]),
    ("frontCreepEnabled", ["RM_MapComponent_FrontCreep", "RM_FrontCreepExtension"], []),
    ("aquaticAmbushEnabled", ["RM_CompAquaticAmbusher", "RM_JobDriver_LungeAttack"],
     ["JobDef/RM_LungeAttack", "HediffDef/RM_AquaticAmbushInvisibility", "HediffDef/RM_LungeSpeedBurst"]),
    ("parentalEnrageEnabled", ["RM_CompParentalEnrage"], ["MentalStateDef/RM_ParentalEnrage"]),
    ("drumLureEnabled", ["RM_CompDrumLure"], ["HediffDef/RM_DrumLureSubmersion", "HediffDef/RM_DrumLureLured"]),
]


def _setting(t, action, field, value=None):
    if value is None:
        r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field)
    else:
        r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field, value=str(value))
    return r if isinstance(r, dict) else {}


@suite.chain("mechanic_toggles")
def mechanic_toggles(t):
    with _comp(t, "control_absent_type_reads_absent", beyond_toggle=True):
        r = t.bridge_call("jawa/type_probe", typeName=ABSENT_TYPE)
        if _live(t) and (not isinstance(r, dict) or r.get("resolved") is not False):
            raise ExpectationFailed("sanity probe: an absent type did not read resolved=False: %r" % (r,))

    for field, types, defs in MECHANICS:
        with _comp(t, field.replace("Enabled", "").replace("Behavior", "") + "_wired_and_gated", toggle=field):
            bad = []
            for ty in types:
                r = t.bridge_call("jawa/type_probe", typeName=NS + ty)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("type_probe(%s) failed outright: %r" % (ty, r))
                if r.get("resolved") is not True:
                    bad.append("%s did not resolve" % ty)
            if defs:
                r = t.bridge_call("jawa/get_defs", defs=";".join(defs), fields="defName", limit=len(defs) + 2)
                if _live(t):
                    if not isinstance(r, dict) or r.get("success") is False:
                        raise ExpectationFailed("get_defs failed: %r" % (r,))
                    if r.get("notFound") or int(r.get("foundCount", 0)) != len(defs):
                        bad.append("%s of %d carrier defs resolved; notFound=%r"
                                   % (r.get("foundCount"), len(defs), r.get("notFound")))
            if bad:
                raise ExpectationFailed("; ".join(bad))
            if not _live(t):
                continue
            old = _setting(t, "get", field).get("value")
            if old is None:
                raise ExpectationFailed("%s: get returned no value (field name wrong?)" % field)
            try:
                if not _setting(t, "set", field, "False").get("success"):
                    raise ExpectationFailed("%s: set False failed" % field)
                off = _setting(t, "get", field).get("value")
                if str(off).lower() != "false":
                    raise ExpectationFailed("%s: wrote False, read %r (the off arm does not take)" % (field, off))
            finally:
                _setting(t, "set", field, old)
            back = _setting(t, "get", field).get("value")
            if str(back).lower() != str(old).lower():
                raise ExpectationFailed("%s did not restore to %r (read %r)" % (field, old, back))

# ---------------------------------------------------------------- every Mod Settings field (2026-10-06)
# The settings class is the list: every `public static bool|int|float x = v;` in RM_CreatureBehaviorsMod.cs.
# A default written as a constant (`RM_TrackPool.DefaultCapacity`) is resolved from that class's `const` line.
import glob as _glob  # noqa: E402
import os as _os  # noqa: E402

_SRC_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "Source")
SETTING_FIELDS = {}                      # name -> (type, python default)
SETTINGS_PARSE_ERRORS = []


def _const(ref):
    cls, _, name = ref.rpartition(".")
    for path in _glob.glob(_os.path.join(_SRC_DIR, "**", cls + ".cs"), recursive=True):
        m = re.search(r"const\s+\w+\s+%s\s*=\s*([^;]+);" % re.escape(name), open(path, encoding="utf-8").read())
        if m:
            return m.group(1).strip()
    raise ValueError("cannot resolve %s" % ref)


try:
    _txt = open(_os.path.join(_SRC_DIR, "RM_CreatureBehaviorsMod.cs"), encoding="utf-8").read()
    for _m in re.finditer(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);", _txt):
        _typ, _nm, _raw = _m.group(1), _m.group(2), _m.group(3).strip()
        if not re.match(r"^-?[\d.]+[fF]?$|^(true|false)$", _raw):
            _raw = _const(_raw)
        SETTING_FIELDS[_nm] = (_typ, (_raw == "true") if _typ == "bool" else
                               (int(_raw) if _typ == "int" else float(_raw.rstrip("fF"))))
except Exception as _ex:
    SETTINGS_PARSE_ERRORS.append(str(_ex))
BOOL_TOGGLES = sorted(n for n, (ty, _) in SETTING_FIELDS.items() if ty == "bool")
suite.toggles = sorted(set(suite.toggles) | set(BOOL_TOGGLES))


def _same_setting(name, live):
    typ, default = SETTING_FIELDS[name]
    if typ == "bool":
        return str(live).lower() == str(default).lower()
    try:
        return abs(float(live) - float(default)) < 1e-4
    except (TypeError, ValueError):
        return False


@suite.chain("settings")
def settings(t):
    """Every RM_CreatureBehaviorsSettings field answers by name at its shipped default (parsed from the C#), and
    every bool round-trips off/on and restores. The mechanic each switch gates is mechanic_toggles' and the
    per-mechanic chains' business; this chain only proves the screen and the fields are honest."""
    with _comp(t, "all_fields_at_shipped_defaults", beyond_toggle=True):
        if SETTINGS_PARSE_ERRORS or len(SETTING_FIELDS) < 80 or len(BOOL_TOGGLES) < 30:
            raise ExpectationFailed("settings source parse: %d fields / %d bools; errors %r"
                                    % (len(SETTING_FIELDS), len(BOOL_TOGGLES), SETTINGS_PARSE_ERRORS))
        wrong = {}
        for name in sorted(SETTING_FIELDS):
            r = _setting(t, "get", name)
            if _live(t) and not _same_setting(name, r.get("value")):
                wrong[name] = r.get("value")
        if _live(t) and wrong:
            raise ExpectationFailed("not at the shipped default (or unreachable by name): %r" % wrong)

    for name in BOOL_TOGGLES:
        with _comp(t, "toggle_roundtrip_%s" % name, toggle=name):
            flipped = not SETTING_FIELDS[name][1]
            try:
                _setting(t, "set", name, flipped)
                got = _setting(t, "get", name).get("value")
                if _live(t) and str(got).lower() != str(flipped).lower():
                    raise ExpectationFailed("%s did not take %r (reads %r)" % (name, flipped, got))
            finally:
                if t.session is not None:
                    t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=name,
                                   value=str(SETTING_FIELDS[name][1]))


# Every def this mod ships is loaded and its label is what its XML says (NORTHSTAR_PARTIAL_GAPS_FILL_1;
# the shared engine's own defs). The Defs/ parse is the list, so a def added later is covered with no edit here.
from modcheck import shipped_defs  # noqa: E402
shipped_defs.add_chain(suite, __file__, sanity=('RM_PincerCrush', 'RM_Mirage'), min_count=35)
