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
suite.toggles = ["tracksEnabled"]

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
