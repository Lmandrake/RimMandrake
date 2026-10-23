#!/usr/bin/env python3
"""northstar_site.py -- obtain a Pyrelands trial site WITHOUT painting Ash'karr (trial plan §3.4-§3.7).

The site is a SCRATCH vanilla quicktest world, one fresh world per fixture (GPT #6). On it a
2-ring patch (~19 tiles) is re-tiled to RM_Pyrelands, the centre's mutators are stripped, a
250x250 map is generated, homed, isolated, saved as an NS_Pyrelands_site_* fixture and RELOADED
(the one reliable entry path; it cures the black generated-map render). Nothing here touches the
campaign save, chooses or sweeps a seed, or produces anything a player receives: the scratch world
is test scaffolding and is discarded (CLAUDE.md worldgen ban -- no alternative planets). The world's
seedString is RECORDED for reproduction only, never tuned.

Bridge holder only, under Windows python.exe from the repo root (WSL cannot reach the bridge):
  python.exe src/RimMandrake/Pyrelands/northstar_site.py --plan            # offline: print the steps
  python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint <def fp>
  python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 2 --temp 30   # the 30 C control site
  python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint <fp> --reload-only --tile <id>
  python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint <fp> --tag anima0   # rebuild, same defs
Then run preflight_pyrelands.py --gate B --tile <tile> on the reloaded fixture.

Every write is followed by an independent read; a read that cannot be completed raises
Unmeasured, never "zero". Tool params/result keys are read off each JawaBench [Tool]'s own
signature and ResultDescription; shapes are UNPROVEN live until the first run.
Item: PYRELANDS_GREEN_MINIMAL_1 (parent PYRELANDS_NORTHSTAR_TRIAL_1).
"""
import argparse
import collections
import csv
import json
import os
import shutil
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import preflight_pyrelands as P                       # noqa: E402  (also puts Utils on sys.path)
from preflight_pyrelands import Unmeasured, _call     # noqa: E402
import bridge_concurrency_guard as _GUARD             # noqa: E402  (MAP_DROP_DIAGNOSE_MENU_MIDRUN_GHOST)

BIOME = P.BIOME


def _QS():
    """The shared quiet isolated test-site profile (Utils/modcheck/quiet_site.py)."""
    d = os.path.join(os.path.join(P.ROOT, "src", "RimMandrake", "Utils"), "modcheck")
    if d not in sys.path:
        sys.path.append(d)
    import quiet_site
    return quiet_site

RINGS = 2
MIN_COLONY_DISTANCE = 10          # plan §3.4 step 2
OK_HILLS = ("Flat", "SmallHills")
ELEVATION = 257.0                 # the_pyrelands.md §0
HILLINESS = "Flat"
TARGET_TEMP = 50.0                # plan §3.5; control site 30
CONTROL_TEMP = 30.0
QUICKTEST_TIMEOUT_MS = 280000
POLL_S = 1.0
# Mechanics that start fires / move herds: OFF while the gen census runs (plan §2.3a, §3.7).
ISOLATION_OFF = ("burnLineEnabled", "fireHawkSpreadEnabled", "fireClockEnabled",
                 "furnaceWorldMigrationEnabled", "burrowOnFireEnabled",
                 "furnaceThermalEnabled")
TICKS_PER_DAY = 60000
TICKS_PER_HOUR = 2500
TICKS_PER_QUADRUM = 15 * TICKS_PER_DAY
COLONIST_KIND = "Colonist"
PLAYER_FACTION = "PlayerColony"   # plan §3.4 step 6

# Food for the colony (PYRE_SITE_FOOD_REPAIR_COLONY_STARVES). Pass 7 (2026-10-13): colonists started unfed with no food
# on a 56 C map and all six died of malnutrition inside the long waits. MealSurvivalPack is non-perishable (Core:
# Nutrition 0.9, no rot clock), stack limit 10; a colonist eats ~1.6 nutrition a day (~2 packs). jawa/spawn_batch's
# count is the thing's stackCount (capability-matrix.md). The cache sits east of the map centre, outside every
# validation.py test pad's clear_area (centre pad clears x 105..145; the burrow pad starts at x 170).
FOOD_DEF = "MealSurvivalPack"
FOOD_STACK = 10
FOOD_PACKS_PER_COLONIST_DAY = 2
FOOD_COLONISTS = 6                # the live fixtures held 6 player pawns
FOOD_RUN_TICKS = 8 * TICKS_PER_DAY  # the longest declared chain: embergrass_regrow waits 7 days; burn_line 2 days
FOOD_CACHE_DX = 25                # first stack at (centre x + 25, centre z)


def food_packs_needed(ticks=FOOD_RUN_TICKS, colonists=FOOD_COLONISTS):
    """Packs that feed `colonists` for `ticks` of game time, plus one spare day. Pure."""
    days = (ticks + TICKS_PER_DAY - 1) // TICKS_PER_DAY + 1
    return colonists * FOOD_PACKS_PER_COLONIST_DAY * days


def food_ops(packs, cx, cz):
    """jawa/spawn_batch `ops` string ('Def:x,z,count' split on ';') for `packs` packs in FOOD_STACK stacks along +x."""
    ops, left, i = [], packs, 0
    while left > 0:
        n = min(FOOD_STACK, left)
        ops.append("%s:%d,%d,%d" % (FOOD_DEF, cx + FOOD_CACHE_DX + i, cz, n))
        left -= n
        i += 1
    return ";".join(ops)


class SiteError(AssertionError):
    pass


# ------------------------------------------------------------------ step 1: a fresh quicktest world

def _ui_state(s):
    try:
        return s.call("rimworld/get_ui_state") or {}
    except Exception:
        return {}


def _wait_state(s, want, budget_s, sleep=time.sleep):
    t0 = time.time()
    while True:
        st = _ui_state(s).get("programState")
        if st == want:
            return st
        if time.time() - t0 > budget_s:
            raise SiteError("programState %r, wanted %r after %ds" % (st, want, budget_s))
        sleep(POLL_S)


def fresh_quicktest_world(s, budget_s=420, sleep=time.sleep):
    """Main menu if needed, then start_debug_game_ready ONCE. A timed-out socket is never
    retried: reconnect (FastSession does it) and poll the postcondition (plan §3.4 step 1)."""
    if _ui_state(s).get("programState") == "Playing":
        try:
            _GUARD.refuse_if_foreign_activity("rimworld/go_to_main_menu")
        except _GUARD.ConcurrentBridgeClient as ex:
            raise SiteError(str(ex))
        try:
            s.call("rimworld/go_to_main_menu")
        except Exception:
            pass
        _wait_state(s, "Entry", 180, sleep)
    try:
        s.call("rimworld/start_debug_game_ready", timeoutMs=QUICKTEST_TIMEOUT_MS,
               readiness="mapData", pauseIfNeeded=True)
    except Exception as ex:                      # timeout / reconnect: poll, never resend
        print("  start_debug_game_ready raised %s -- polling, not resending" % type(ex).__name__)
    _wait_state(s, "Playing", budget_s, sleep)
    gi = s.call("rimworld/get_game_info") or {}
    if gi.get("ticksGame") is None:
        raise SiteError("Playing but get_game_info has no ticksGame -- zombie load")
    wi = _call(s, "jawa/world_info_get").get("info") or {}
    return {"seedString": wi.get("seedString"), "planetCoverage": wi.get("planetCoverage")}


# ------------------------------------------------------------------ step 2/11: choose the tile (raw fields)

def _flag(v, path, tile):
    """The live jawa/world_tile_export writes waterCovered as 1/0 (MEASURED 2026-10-21, Transient/test_site_saves/
    leaningscrub_site); comparing to "true" read every ocean tile as land, so Scrub/Cauldron sites were built on
    re-tiled sea (SCRUB_WILDLIFE_PROVE_NOBODY_CAME). Any other spelling is refused, never guessed."""
    s = str(v if v is not None else "").strip().lower()
    if s in ("1", "true"):
        return True
    if s in ("0", "false"):
        return False
    raise Unmeasured("tile export %s: waterCovered %r on tile %s is neither 1/0 nor true/false" % (path, v, tile))


def read_tile_csv(path):
    rows = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[int(r["tile"])] = {
                "lat": float(r["lat"]), "long": float(r["long"]), "biome": r["biome"],
                "hilliness": r["hilliness"],
                "waterCovered": _flag(r.get("waterCovered"), path, r["tile"]),
                "riverCount": int(float(r.get("riverCount") or 0)),
                "roadCount": int(float(r.get("roadCount") or 0)),
                "mutatorCount": int(float(r.get("mutatorCount") or 0)),
            }
    if not rows or "waterCovered" not in open(path, encoding="utf-8").readline():
        raise Unmeasured("tile export %s is not the EXTENDED csv (no waterCovered column)" % path)
    return rows


def read_neighbor_csv(path):
    """tile -> [neighbour ids]. Accepts 'tile,n0..n5' or 'tile,neighbors' ('a;b;c'). A pentagon's
    sixth slot is written as -1 (GetTileNeighbors pads to 6) and is dropped, never a tile."""
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        head = next(rd)
        for r in rd:
            if not r or not r[0].strip().isdigit():
                continue
            vals = []
            for cell in r[1:]:
                for v in cell.replace(";", " ").replace("|", " ").split():
                    if v.isdigit():
                        vals.append(int(v))
            out[int(r[0])] = vals
    if not out:
        raise Unmeasured("neighbour csv %s parsed empty (header %s)" % (path, head))
    return out


def ring(nbrs, centre, rings):
    """Tiles within `rings` steps of centre, centre first, BFS order."""
    seen, frontier = [centre], [centre]
    for _ in range(rings):
        nxt = []
        for t in frontier:
            for n in nbrs.get(t, ()):
                if n not in seen:
                    seen.append(n)
                    nxt.append(n)
        frontier = nxt
    return seen


def distances_from(nbrs, src, cap):
    d = {src: 0}
    q = collections.deque([src])
    while q:
        t = q.popleft()
        if d[t] >= cap:
            continue
        for n in nbrs.get(t, ()):
            if n not in d:
                d[n] = d[t] + 1
                q.append(n)
    return d


def _land_ok(r):
    return (r is not None and not r["waterCovered"] and r["riverCount"] == 0
            and r["roadCount"] == 0 and r["hilliness"] in OK_HILLS and r["biome"] not in ("(null)", ""))


def site_candidates(rows, nbrs, colony_tile, lat_max=P.LAT_MAX, rings=RINGS,
                    min_dist=MIN_COLONY_DISTANCE):
    """Yield (centre, patch tiles) in a fixed order (|lat|, tile id). Pure -- no bridge.
    Every tile of the 2-ring patch is land, unwatered, roadless, riverless, flat/small hills;
    the centre is >= min_dist steps from the quicktest colony and inside the hot band."""
    near = distances_from(nbrs, colony_tile, min_dist - 1) if colony_tile is not None else {}
    for t in sorted(rows, key=lambda i: (abs(rows[i]["lat"]), i)):
        r = rows[t]
        if abs(r["lat"]) > lat_max or t in near or not _land_ok(r):
            continue
        patch = ring(nbrs, t, rings)
        if len(patch) < 13:                      # 1 + 6 + 12 (fewer only at a pentagon)
            continue
        if all(_land_ok(rows.get(p)) for p in patch):
            yield t, patch


def choose_tile(s, export_dir, colony_tile, max_landmark_checks=50):
    """Export raw tile fields + neighbour order to disk, pick the first clean candidate,
    then confirm no landmark in its patch with a live read."""
    os.makedirs(export_dir, exist_ok=True)
    tiles_csv = os.path.join(export_dir, "world_tiles_extended.csv")
    nbr_csv = os.path.join(export_dir, "world_neighbors.csv")
    e = _call(s, "jawa/world_tile_export", path=tiles_csv, format="csv", extended=True)
    n = _call(s, "jawa/world_neighbors", path=nbr_csv)
    rows = read_tile_csv(e.get("path") or tiles_csv)
    nbrs = read_neighbor_csv(n.get("path") or nbr_csv)
    checked = 0
    for centre, patch in site_candidates(rows, nbrs, colony_tile):
        checked += 1
        if checked > max_landmark_checks:
            break
        mu = _call(s, "jawa/world_mutators_get", tiles=",".join(map(str, patch)), limit=100)
        trows = mu.get("tiles")
        if not isinstance(trows, list) or len(trows) != len(patch):
            raise Unmeasured("world_mutators_get returned %s rows for %d tiles" % (
                None if trows is None else len(trows), len(patch)))
        if any(r.get("landmark") for r in trows):
            continue
        return {"centre": centre, "patch": patch, "lat": rows[centre]["lat"],
                "long": rows[centre]["long"], "was": dict(rows[centre]),
                "candidatesChecked": checked}
    raise SiteError("no clean 2-ring land patch in |lat|<=%s (checked %d)" % (P.LAT_MAX, checked))


# ------------------------------------------------------------------ step 3/4: re-tile, strip mutators

def retile(s, patch, temp):
    """Biome, temperature, rainfall 0, elevation, flat -- written BEFORE anything reads the
    tile's lazy Min/MaxTemperature caches (world-editing skill, trap 2). Read back RAW."""
    r = _call(s, "jawa/world_tile_set", tiles=",".join(map(str, patch)), biome=BIOME,
              temperature=temp, rainfall=0.0, elevation=ELEVATION, hilliness=HILLINESS,
              swampiness=0.0, readBack=len(patch))
    back = {t.get("tile"): t for t in r.get("tiles") or []}
    if r.get("written") is not None and r["written"] != len(patch):
        raise SiteError("world_tile_set wrote %s of %d tiles" % (r["written"], len(patch)))
    bad = [t for t in patch if (back.get(t) or {}).get("biome") != BIOME
           or abs(float((back.get(t) or {}).get("temperature", 1e9)) - temp) > 0.5
           or (back.get(t) or {}).get("hilliness") != HILLINESS]
    if bad:
        raise SiteError("re-tile read-back wrong on %d tile(s): %s" % (len(bad), bad[:5]))
    return len(patch)


def strip_mutators(s, centre):
    _call(s, "jawa/world_mutators_set", action="clear", tiles=str(centre))
    mu = _call(s, "jawa/world_mutators_get", tiles=str(centre))
    left = ((mu.get("tiles") or [{}])[0]).get("mutators")
    if left is None:
        raise Unmeasured("world_mutators_get gave no mutators[] for %s" % centre)
    if left:
        raise SiteError("mutators survived clear on %s: %s" % (centre, left))
    c = _call(s, "jawa/world_commit")
    failed = [st for st in c.get("steps") or [] if str(st.get("status", st.get("result", ""))).lower() == "failed"]
    if failed:
        raise SiteError("world_commit step(s) failed: %s" % failed)


# ------------------------------------------------------------------ step 5/6: generate, home

def generate(s, centre, size=P.MAP_SIZE):
    # The engine culls a generated map that is not a player home (MEASURED live 2026-10-01: after save + reload
    # only the quicktest colony map survived), so the site gets a PLAYER settlement first; the map is then
    # built by the generate call below (colony_found itself never generates one).
    f = _call(s, "jawa/colony_found", tile=centre, faction="Player")
    if f.get("success") is False:
        raise SiteError("colony_found refused at %s: %s" % (centre, str(f)[:200]))
    r = _call(s, "jawa/world_tile_map_generate", tile=centre, sizeX=size, sizeZ=size)
    if r.get("wasAlreadyGenerated"):
        raise SiteError("tile %s already had a map -- not a fresh fixture" % centre)
    ms = r.get("mapSize") or {}
    if (ms.get("x"), ms.get("z")) != (size, size):
        raise SiteError("mapSize %s != %dx%d" % (ms, size, size))
    fin = r.get("mapFinalize")
    if not isinstance(fin, dict) or "failedSteps" not in fin:
        raise Unmeasured("world_tile_map_generate gave no mapFinalize.failedSteps")
    if fin["failedSteps"]:
        raise SiteError("mapgen finalize steps failed: %s" % fin["failedSteps"])
    if r.get("mapId") is None:
        raise Unmeasured("world_tile_map_generate returned no mapId")
    return r


def home(s, map_id, n=3):
    r = _call(s, "jawa/set_current_map", mapId=map_id)
    mi = _call(s, "jawa/map_info")
    if mi.get("mapId") != map_id:
        raise SiteError("set_current_map %s but map_info reads %s" % (map_id, mi.get("mapId")))
    cx, cz = mi.get("sizeX", P.MAP_SIZE) // 2, mi.get("sizeZ", P.MAP_SIZE) // 2
    sp = _call(s, "jawa/spawn_pawn", kindDef=COLONIST_KIND, x=cx, z=cz, faction=PLAYER_FACTION, count=n)
    ids = [p.get("id") for p in sp.get("pawns") or [] if p.get("id")]
    if len(ids) != n:
        raise SiteError("spawned %d of %d colonists: %s" % (len(ids), n, str(sp)[:160]))
    return {"previousMapId": r.get("previousMapId"), "colonists": ids, "mapInfo": mi}


def _colonists(s, current_only):
    r = _call(s, "rimworld/list_colonists", currentMapOnly=bool(current_only))
    rows = r.get("colonists", r) if isinstance(r, dict) else r
    if not isinstance(rows, list):
        raise Unmeasured("rimworld/list_colonists gave no colonists[]: %s" % str(r)[:200])
    return rows


def retire_offsite_colonies(s, centre):
    """Abandon every OTHER settlement of the site's own faction -- the quicktest colony the world was born with -- and
    read back that every colonist now stands on the site map.

    MEASURED pass 8 (2026-10-13, PYRE_SITE_VITALS_REPAIR_HALF_THE_COLONY / TESTENV_TOXIC_HARDEN_SITE_POISONS_ITS_GUESTS):
    the fixture kept the quicktest colony's map (map 0) with its own 3 colonists and their animals. The suite's
    vitals and top-up read the CURRENT map (the site, 3 colonists) and never saw map 0, where Hernan, brogg and thozzik
    died of ToxicBuildup and Stout and Vargas starved while the suite read "3 colonists, damage []". Nobody tests
    anything on map 0: it is removed with vanilla's Abandon (no confirmation dialogs), not watched."""
    site = [o for o in _call(s, "jawa/world_objects_get", tiles=str(centre), limit=50).get("objects") or []
            if o.get("isSettlement")]
    if len(site) != 1 or not site[0].get("faction"):
        raise SiteError("no single faction settlement on the site tile %s: %s" % (centre, site))
    fac = site[0]["faction"]
    others = [o for o in _call(s, "jawa/world_objects_get", faction=fac, limit=500).get("objects") or []
              if o.get("isSettlement") and o.get("tile") != centre]
    gone = []
    for o in others:
        r = _call(s, "jawa/settlement_remove", mode="settlement", settlementId=o["id"])
        if r.get("success") is False or not r.get("destroyed", True):
            raise SiteError("abandon of off-site settlement %s (tile %s) failed: %s" % (o["id"], o.get("tile"), str(r)[:200]))
        gone.append({"id": o["id"], "tile": o.get("tile"), "label": o.get("label"), "hadMap": r.get("hasMap")})
    try:
        s.call("jawa/window_list_close", action="close", closeAll=True, typeName="Dialog_MessageBox")
    except Exception:
        pass                                       # housekeeping: nothing open to close
    left = [o for o in _call(s, "jawa/world_objects_get", faction=fac, limit=500).get("objects") or []
            if o.get("isSettlement") and o.get("tile") != centre]
    if left:
        raise SiteError("off-site settlements survive the abandon: %s" % left)
    every, here = _colonists(s, False), _colonists(s, True)
    if len(every) != len(here):
        raise SiteError("%d colonists in the game but %d on the site map after retiring %s" % (len(every), len(here), gone))
    return {"retired": gone, "faction": fac, "colonists": len(here)}


def stock_food(s, cx, cz, packs=None):
    """Put the colony's food cache on the map and top every colonist's Food need to full, each read back.
    Returns {packs, stacks, colonists}. A cache that reads back short is a SiteError, never a silent starve."""
    packs = food_packs_needed() if packs is None else packs
    _call(s, "jawa/spawn_batch", ops=food_ops(packs, cx, cz))
    rect = "%d,%d,%d,%d" % (cx + FOOD_CACHE_DX, cz, (packs + FOOD_STACK - 1) // FOOD_STACK, 1)
    got = _call(s, "jawa/list_things", defName=FOOD_DEF, rect=rect, limit=500)
    if got.get("isCompleteList") is False:
        raise Unmeasured("food read-back truncated")
    have = sum(int(t.get("stackCount") or 0) for t in got.get("things") or [])
    if have < packs:
        raise SiteError("food cache reads %d of %d %s in %s" % (have, packs, FOOD_DEF, rect))
    pids = top_up_needs(s)
    return {"packs": have, "stacks": len(got.get("things") or []), "colonists": pids}


def top_up_needs(s):
    """Food and Rest to 1.0 on every living player pawn (jawa/pawn_need, the tool the suites already use)."""
    r = _call(s, "jawa/list_pawns", faction="player", limit=100)
    pids = [p["id"] for p in r.get("pawns") or [] if p.get("id") and not p.get("dead")]
    for pid in pids:
        for need in ("Food", "Rest"):
            _call(s, "jawa/pawn_need", pawn=pid, action="need", need=need, level=1.0)
    return pids


def name_colony(s, centre):
    """Name the player faction and EVERY player settlement (jawa/name_colony == the naming dialogs' OK).

    MEASURED live 2026-10-11 (ratchet pilot): an unnamed colony makes Faction.FactionTick raise
    Dialog_NamePlayerFactionAndSettlement at every TicksGame % 1000 == 200. The dialog force-pauses the clock
    (the suite's "clock stalled at 425200 / 455200 / 458200 / 468200") and hops Find.CurrentMap to the quicktest
    colony (tile 52347, RM_TheRot), so the site recipe's own reload check crashed before its settle step, gate B
    then found unsettled cell temperatures and a queued incident, and the suite's reads after a wait landed on
    the wrong map. Naming is a scribed fact, so a fixture saved after this never raises the dialog again."""
    r = _call(s, "jawa/name_colony", factionName="Northstar Pyrelands", settlementName="Northstar Pyrelands")
    rows = r.get("settlements")
    if not isinstance(rows, list):
        raise Unmeasured("jawa/name_colony gave no settlements[]: %s" % str(r)[:200])
    if centre is not None and not any(x.get("tile") == centre and x.get("namedByPlayer") for x in rows):
        raise SiteError("name_colony did not name the site settlement on tile %s: %s" % (centre, rows))
    try:
        s.call("jawa/window_list_close", action="close", typeName="Dialog_NamePlayer", closeAll=True)
    except Exception:
        pass                                       # housekeeping: nothing open to close
    return [x.get("tile") for x in rows]


# ------------------------------------------------------------------ §3.5-3.7 environment

def isolate(s, settings_off=ISOLATION_OFF):
    """Fire/migration mechanics OFF (read back), storyteller quiet, queue empty, Clear locked,
    fog off (rect unfog, never unfogAll), normal speed pin off. Returns what was changed."""
    changed = {}
    for f in settings_off:
        before = _call(s, "jawa/mod_settings_field", typeName=P.SETTINGS, action="get", field=f).get("value")
        _call(s, "jawa/mod_settings_field", typeName=P.SETTINGS, action="set", field=f, value="false")
        after = _call(s, "jawa/mod_settings_field", typeName=P.SETTINGS, action="get", field=f).get("value")
        if P._norm_val(after) is not False:
            raise SiteError("%s did not read back false (%r)" % (f, after))
        changed[f] = before
    st = _call(s, "jawa/storyteller_swap", storytellerDef=P.QUIET_STORYTELLER)
    _call(s, "jawa/incident_queue_clear")
    _call(s, "jawa/weather_set", weather="Clear", lockWeather=True)
    wg = _call(s, "jawa/weather_get")
    cur = wg.get("weather")
    if isinstance(cur, dict):                      # live shape: {"weather": {"current": "Clear", ...}}
        cur = cur.get("current")
    if (cur or wg.get("current")) != "Clear":
        raise SiteError("weather read-back is not Clear (%r)" % (wg,))
    return {"settingsBefore": changed, "storyteller": st.get("before")}


def restore_isolation(s, changed):
    """Always called in a finally: every toggle back to the SHIPPED default, read back."""
    bad = {}
    for f in changed:
        want = P.DEFAULTS[f]
        _call(s, "jawa/mod_settings_field", typeName=P.SETTINGS, action="set", field=f,
              value=str(want).lower() if isinstance(want, bool) else str(want))
        got = _call(s, "jawa/mod_settings_field", typeName=P.SETTINGS, action="get", field=f).get("value")
        if P._norm_val(got) != P._norm_val(want):
            bad[f] = got
    if bad:
        raise SiteError("settings did not restore: %s" % bad)


def fog_off(s, size):
    r = _call(s, "jawa/set_fog", action="unfog", rect="0,0,%d,%d" % size)
    if "foggedCellsNow" not in r:
        raise Unmeasured("set_fog gave no foggedCellsNow")
    if r["foggedCellsNow"]:
        raise SiteError("fog remains on %s cell(s) after unfog" % r["foggedCellsNow"])


def midsummer_noon_ticks(clk, lat, lon, date_at):
    """Smallest forward ticksGame whose date at (lat, lon) is mid-Summer at local 12:00.
    `date_at(ticksAbs) -> season string`. time_set_ticks simulates nothing (plan §3.5)."""
    tg, ta = int(clk["ticksGame"]), int(clk["ticksAbs"])
    off = ta - tg
    tz_ticks = int(round(lon / 15.0)) * TICKS_PER_HOUR      # GenDate.TimeZoneAt
    for q in range(0, 9):
        mid = (ta // TICKS_PER_QUADRUM + q) * TICKS_PER_QUADRUM + 7 * TICKS_PER_DAY
        local_noon = mid - ((mid + tz_ticks) % TICKS_PER_DAY) + 12 * TICKS_PER_HOUR
        if local_noon <= ta:
            continue
        if "summer" in str(date_at(local_noon)).lower():
            return local_noon - off
    raise SiteError("no Summer quadrum found in the next two years at lat %s" % lat)


def set_midsummer_noon(s, lat, lon):
    clk = _call(s, "jawa/time_clock")
    if clk.get("ticksAbs") is None:
        raise Unmeasured("time_clock has no ticksAbs")

    def date_at(ticks_abs):
        return _call(s, "jawa/time_date_at", latitude=lat, longitude=lon, ticksAbs=ticks_abs).get("season")
    target = midsummer_noon_ticks(clk, lat, lon, date_at)
    # timeException=True: mid-summer noon set BEFORE mapgen; the colony is not on the map under test (safe-advance gate)
    _call(s, "jawa/time_set_ticks", ticks=target, timeException=True)
    after = _call(s, "jawa/time_clock")
    if int(after.get("ticksGame", -1)) != target:
        raise SiteError("time_set_ticks read-back %s != %s" % (after.get("ticksGame"), target))
    return target


# ------------------------------------------------------------------ step 9: save + reload the fixture

def _stat_saves(saves_dir):
    out = {}
    for f in os.listdir(saves_dir):
        if f.endswith(".rws"):
            st = os.stat(os.path.join(saves_dir, f))
            out[f] = (st.st_size, int(st.st_mtime))
    return out


def save_fixture(s, name, saves_dir, backup_dir, sleep=time.sleep, wait_s=120):
    """Back up Saves/ first, save, then STAT: a new <name>.rws appeared and no existing file
    changed (CLAUDE.md: save_game has written the CURRENT slot instead of saveName)."""
    before = _stat_saves(saves_dir)
    if name + ".rws" in before:
        raise SiteError("%s.rws already exists -- fixtures are never overwritten" % name)
    os.makedirs(backup_dir, exist_ok=True)
    for f in before:
        dst = os.path.join(backup_dir, f)
        if os.path.exists(dst):     # TESTENV_SITE_BACKUP_REPAIR_READONLY_REUSE: reused index => read-only copy of the last backup
            os.chmod(dst, 0o666)
            os.remove(dst)
        shutil.copy2(os.path.join(saves_dir, f), dst)
    _call(s, "rimworld/save_game", saveName=name)
    t0 = time.time()
    while name + ".rws" not in _stat_saves(saves_dir):
        if time.time() - t0 > wait_s:
            raise SiteError("no %s.rws appeared in %s" % (name, saves_dir))
        sleep(POLL_S)
    after = _stat_saves(saves_dir)
    touched = [f for f in before if after.get(f) != before[f]]
    if touched:
        raise SiteError("save touched existing file(s) %s -- backups in %s" % (touched, backup_dir))
    return os.path.join(saves_dir, name + ".rws")


def find_site_map(s, tile, max_id=8):
    """mapId of the loaded map on `tile` (jawa/set_current_map takes the map id; there is no map listing tool)."""
    for mid in range(max_id + 1):
        try:
            _call(s, "jawa/set_current_map", mapId=mid)
            if _call(s, "jawa/map_info").get("tile") == tile:
                return mid
        except Unmeasured:
            continue
    raise SiteError("no loaded map sits on tile %s (map ids 0..%d tried)" % (tile, max_id))


SETTLE_TICKS = 1500


def settle_site(s, tile, map_id, sleep=time.sleep):
    """After a load: name the colony FIRST (before any tick can raise the naming dialog), make the site current,
    clear the storyteller queue, run SETTLE_TICKS so cell temperatures converge on the outdoor temperature
    (MEASURED: 41.6 vs 50.4 C at tick 0 of a load; 59.0 vs 55.7 C on the 2026-10-11 pilot fixture, which never
    settled), then clear the queue again and re-assert the site. Returns the final map_info."""
    name_colony(s, tile)
    if map_id is None:
        map_id = find_site_map(s, tile)
    _call(s, "jawa/set_current_map", mapId=map_id)
    retire_offsite_colonies(s, tile)               # a fixture saved before the retire step still holds the quicktest colony
    _call(s, "jawa/incident_queue_clear")          # a reload re-arms the storyteller's queue
    # the shared quiet isolated profile (isolated suite; the receipt rides on the returned map_info). A load resets
    # DebugSettings.enableStoryteller, so it is applied after EVERY load, before the settle ticks.
    quiet = _QS().site_profile_receipt(s, "pyrelands_settle_%s" % tile)
    s.call("rimworld/step_game_ticks", ticks=SETTLE_TICKS, pauseFirst=True, timeoutMs=120000)
    _call(s, "jawa/incident_queue_clear")          # anything queued during the settle
    _call(s, "jawa/set_current_map", mapId=map_id)
    mi = _call(s, "jawa/map_info")
    if mi.get("tile") != tile or mi.get("mapBiome") != BIOME:
        raise SiteError("settled current map is tile %s biome %s, want %s %s" % (
            mi.get("tile"), mi.get("mapBiome"), tile, BIOME))
    mi["quietSite"] = quiet
    return mi


def reload_fixture(s, name, tile, budget_s=420, sleep=time.sleep, map_id=None):
    """`rimworld/load_game` (load_game_ready is a PRE-condition check, traps.md); assert on
    programState, never on the call's own success. Then settle_site."""
    # Load from the MAIN MENU, once: loading over a live game runs Game.Dispose() right after queueing the
    # async load, and a map still being torn down then NREs during the new load (GlowGrid.GlowPool.Take,
    # "Error while loading a map" -- MEASURED live 2026-10-01, twice).
    if _ui_state(s).get("programState") == "Playing":
        try:
            _GUARD.refuse_if_foreign_activity("rimworld/go_to_main_menu")
        except _GUARD.ConcurrentBridgeClient as ex:
            raise SiteError(str(ex))
        try:
            s.call("rimworld/go_to_main_menu")
        except Exception:
            pass
        _wait_state(s, "Entry", 180, sleep)
    try:
        s.call("rimworld/load_game", saveName=name)
    except Exception as ex:
        print("  load_game raised %s -- polling, not resending" % type(ex).__name__)
    _wait_state(s, "Playing", budget_s, sleep)
    # programState is still "Playing" on the OLD map while the load begins (MEASURED live 2026-10-01:
    # map_info answered "No current map"), so poll until a map answers; WHICH map is current does not matter,
    # settle_site makes the site current itself.
    t0 = time.time()
    while True:
        try:
            if _call(s, "jawa/map_info").get("tile") is not None:
                break
        except Unmeasured:
            pass
        if time.time() - t0 > budget_s:
            raise SiteError("no current map answered within %ds of load_game %s" % (budget_s, name))
        sleep(POLL_S)
    return settle_site(s, tile, map_id, sleep=sleep)


# ------------------------------------------------------------------ the whole recipe

def fixture_name(k, fingerprint, temp, tag=None):
    """NS_Pyrelands_site_<k>[_t<temp>]_<fp12>[_<tag>]. `tag` names a rebuild whose Pyrelands defs did not change:
    the def fingerprint covers only Pyrelands' own defs, so a fix in ANOTHER mod (2026-10-12: the anima-tree block in
    MandrakePatches) leaves the fingerprint, and therefore the name, of the stale fixture -- and save_fixture refuses
    to overwrite it. A tag is letters, digits and '-' only."""
    tt = "" if temp == TARGET_TEMP else "_t%d" % int(temp)
    if tag is not None and (not tag or not all(c.isalnum() or c == "-" for c in tag)):
        raise SiteError("fixture tag %r: use letters, digits and '-' only" % (tag,))
    return "NS_Pyrelands_site_%d%s_%s%s" % (k, tt, (fingerprint or "nofp")[:12], "_" + tag if tag else "")


def build_site(s, k, fingerprint, saves_dir, work_dir, temp=TARGET_TEMP, census=None,
               sleep=time.sleep, fresh_world=True, tag=None):
    """Plan §3.4 steps 1-9 for ONE site in its own fresh quicktest world. `census(s, record)`
    is called at tick 0, before any tick, with fire mechanics isolated (bars 1, 2, 4)."""
    rec = {"site": k, "temp": temp, "fingerprint": fingerprint, "tag": tag,
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    fixture_name(k, fingerprint, temp, tag)        # a bad tag refuses before any world is touched
    if fresh_world:
        rec["world"] = fresh_quicktest_world(s, sleep=sleep)
    rec["colonyTile"] = _call(s, "jawa/map_info").get("tile")
    rec["pick"] = choose_tile(s, os.path.join(work_dir, "site_%d" % k), rec["colonyTile"])
    centre = rec["pick"]["centre"]
    rec["retiled"] = retile(s, rec["pick"]["patch"], temp)
    strip_mutators(s, centre)
    # isolate() runs INSIDE the try: when one read-back refuses midway, the toggles it already turned off are still
    # put back by the finally (restore_isolation sets every listed field to its shipped default, read back).
    iso = {"settingsBefore": dict.fromkeys(ISOLATION_OFF)}
    try:
        iso = isolate(s)                           # before mapgen: no burn line at gen
        rec["isolation"] = iso
        # The season is set BEFORE the site map exists (PYRE_SITE_CLOCK_REPAIR_ASH_EXPIRES_FIRST, owner: warping time
        # on a populated map is "an EXTREMELY risky proposition"). time_set_ticks simulates nothing, so with no colony
        # on the site the jump costs nothing, and the map is generated AT mid-Summer noon: its loose ash is minutes
        # old at the first sample instead of 6-10 days past its lifetime.
        rec["ticksGameNoon"] = set_midsummer_noon(s, rec["pick"]["lat"], rec["pick"]["long"])
        g = generate(s, centre)
        rec["mapId"] = g["mapId"]
        rec["generate"] = {k2: g.get(k2) for k2 in ("pawnCount", "thingCount", "mapIndex", "mapParentDef")}
        h = home(s, g["mapId"])
        rec["colonists"] = h["colonists"]
        rec["retired"] = retire_offsite_colonies(s, centre)   # before food/top-up: every colonist is on the site
        # the fixture is SAVED without mapgen hives/turrets/dormant structures or an unsent monolith letter (map-only
        # controls: the static storyteller switch is not saved, settle_site applies the full profile after each load)
        rec["quietMap"] = _QS().site_profile_receipt(s, "pyrelands_site_build_%d" % k, controls=_QS().MAP_ONLY)
        rec["food"] = stock_food(s, P.MAP_SIZE // 2, P.MAP_SIZE // 2)
        rec["named"] = name_colony(s, centre)       # before any tick: the fixture is saved named
        rec["tickAtGen"] = _call(s, "jawa/time_clock").get("ticksGame")
        fog_off(s, (P.MAP_SIZE, P.MAP_SIZE))
        if census is not None:
            rec["census"] = census(s, rec)
        name = fixture_name(k, fingerprint, temp, tag)
        rec["save"] = save_fixture(s, name, saves_dir, os.path.join(work_dir, "saves_backup_%d" % k), sleep=sleep)
        rec["saveName"] = name
    finally:
        restore_isolation(s, iso["settingsBefore"])
    # GPT deep review 2026-10-22 #7: ONE reload (the comprehension used to call reload_fixture once per key: 5 loads)
    ri = reload_fixture(s, rec["saveName"], centre, sleep=sleep, map_id=rec["mapId"])
    rec["reload"] = {k2: ri.get(k2) for k2 in ("mapId", "tile", "mapBiome", "outdoorTempNow", "season")}
    return rec


STEPS = """Pyrelands site recipe (plan 3.4), per fixture, each in its own fresh quicktest world:
 1 main menu if Playing -> rimworld/start_debug_game_ready ONCE (mapData) -> poll programState
 2 world_tile_export extended csv + world_neighbors csv -> first (|lat|, id) centre whose 2-ring
   patch is all land/no river/no road/flat-or-small-hills, >= 10 steps from the colony, |lat|<=25;
   world_mutators_get: no landmark in the patch
 3 world_tile_set patch: RM_Pyrelands, temp 50 (control 30), rainfall 0, elev 257, Flat -> RAW read-back
 4 world_mutators_set clear (centre) -> read-back empty -> world_commit
 - isolate: 7 fire/migration toggles OFF (read back), storyteller Tutor, queue cleared, Clear locked
 5 world_tile_map_generate 250x250 -> fresh, mapSize, failedSteps == []
 6 set_current_map -> 3 colonists (PlayerColony) -> abandon every other settlement of that faction (the quicktest
   colony; read back: all colonists on the site map) -> jawa/name_colony (every player settlement named, so the
   force-pausing, map-hopping naming dialog is never raised) -> fog unfog rect (never unfogAll)
 - stock_food: 8 days of MealSurvivalPack east of the centre (read back) + Food/Rest need topped on every colonist
 8 census hook at tick 0 (bars 1, 2, 4)
 - time_set_ticks -> local noon, mid-Summer for the tile's lat/long (simulates nothing) -- BEFORE mapgen, so the
   map is born at the season and no multi-day jump ever runs on a populated map
 9 back up Saves/ -> save_game NS_Pyrelands_site_<k>_<fp> -> stat (new file, nothing else touched)
 - finally: toggles restored to shipped defaults (read back)
   rimworld/load_game -> programState Playing -> settle: name_colony, site current, queue cleared,
   1500 ticks (cell temperatures converge), queue cleared, site current
 then: preflight_pyrelands.py --gate B --tile <centre>  (the northstar plan re-runs gate B and refuses on it)
 --reload-only: reload + settle an EXISTING fixture (no new world), e.g. after a crash in the reload step
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", action="store_true", help="print the recipe; touch nothing")
    ap.add_argument("--site", type=int, help="fixture index k (1-based)")
    ap.add_argument("--temp", type=float, default=TARGET_TEMP)
    ap.add_argument("--fingerprint", help="def fingerprint from gate A evidence")
    ap.add_argument("--work", default=os.path.join(P.ROOT, "Transient", "modcheck", "pyrelands", "sites"))
    ap.add_argument("--out", help="fixture record JSON (default <work>/site_<k>.json)")
    ap.add_argument("--reload-only", action="store_true",
                    help="load + settle the existing fixture NS_Pyrelands_site_<k>_<fp12>; needs --tile")
    ap.add_argument("--tile", type=int, help="--reload-only: the site's centre tile")
    ap.add_argument("--map-id", type=int, help="--reload-only: the site's map id (found by tile when omitted)")
    ap.add_argument("--tag", help="fixture name suffix for a rebuild whose Pyrelands def fingerprint is unchanged "
                                  "(e.g. 'anima0' after the MandrakePatches anima block); --reload-only needs it too")
    a = ap.parse_args(argv)
    if a.plan or a.site is None:
        print(STEPS)
        return 0
    from northstar_driver.session import FastSession
    from game_paths import SAVES
    s = FastSession(strict=False)
    if a.reload_only:
        if a.tile is None:
            ap.error("--reload-only needs --tile")
        name = fixture_name(a.site, a.fingerprint, a.temp, a.tag)
        with s:
            mi = reload_fixture(s, name, a.tile, map_id=a.map_id)
        print("reloaded %s: map %s tile %s %s outdoor %s -- now run gate B" % (
            name, mi.get("mapId"), mi.get("tile"), mi.get("mapBiome"), mi.get("outdoorTempNow")))
        return 0
    with s:
        rec = build_site(s, a.site, a.fingerprint, SAVES, a.work, temp=a.temp, tag=a.tag)
    out = a.out or os.path.join(a.work, "site_%d%s.json" % (a.site, "_" + a.tag if a.tag else ""))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, sort_keys=True, default=str)
    print("site %d: tile %s map %s saved %s -> %s" % (a.site, rec["pick"]["centre"], rec.get("mapId"),
                                                      rec.get("saveName"), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
