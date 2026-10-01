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

BIOME = P.BIOME
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
                 "furnaceThermalEnabled", "fulguriteEnabled")
TICKS_PER_DAY = 60000
TICKS_PER_HOUR = 2500
TICKS_PER_QUADRUM = 15 * TICKS_PER_DAY
COLONIST_KIND = "Colonist"
PLAYER_FACTION = "PlayerColony"   # plan §3.4 step 6


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

def read_tile_csv(path):
    rows = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[int(r["tile"])] = {
                "lat": float(r["lat"]), "long": float(r["long"]), "biome": r["biome"],
                "hilliness": r["hilliness"],
                "waterCovered": str(r.get("waterCovered", "")).lower() == "true",
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
    _call(s, "jawa/time_set_ticks", ticks=target)
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
        shutil.copy2(os.path.join(saves_dir, f), os.path.join(backup_dir, f))
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


def reload_fixture(s, name, tile, budget_s=420, sleep=time.sleep, map_id=None):
    """`rimworld/load_game` (load_game_ready is a PRE-condition check, traps.md); assert on
    programState, never on the call's own success."""
    try:
        s.call("rimworld/load_game", saveName=name)
    except Exception as ex:
        print("  load_game raised %s -- polling, not resending" % type(ex).__name__)
    _wait_state(s, "Playing", budget_s, sleep)
    # programState is still "Playing" on the OLD map while the load begins (MEASURED live 2026-10-01:
    # map_info answered "No current map"), so poll the map itself until it answers.
    t0, mi = time.time(), None
    while True:
        try:
            mi = _call(s, "jawa/map_info")
            if mi.get("tile") == tile or time.time() - t0 > budget_s:
                break
        except Unmeasured:
            if time.time() - t0 > budget_s:
                raise
        sleep(POLL_S)
    if mi.get("tile") != tile and map_id is not None:
        # the save's current map is the quicktest colony; the site is the second map
        _call(s, "jawa/set_current_map", mapId=map_id)
        mi = _call(s, "jawa/map_info")
    if mi.get("tile") == tile:
        _call(s, "jawa/incident_queue_clear")      # a reload re-arms the storyteller's queue
    if mi.get("tile") != tile or mi.get("mapBiome") != BIOME:
        raise SiteError("reloaded current map is tile %s biome %s, want %s %s" % (
            mi.get("tile"), mi.get("mapBiome"), tile, BIOME))
    return mi


# ------------------------------------------------------------------ the whole recipe

def fixture_name(k, fingerprint, temp):
    tag = "" if temp == TARGET_TEMP else "_t%d" % int(temp)
    return "NS_Pyrelands_site_%d%s_%s" % (k, tag, (fingerprint or "nofp")[:12])


def build_site(s, k, fingerprint, saves_dir, work_dir, temp=TARGET_TEMP, census=None,
               sleep=time.sleep, fresh_world=True):
    """Plan §3.4 steps 1-9 for ONE site in its own fresh quicktest world. `census(s, record)`
    is called at tick 0, before any tick, with fire mechanics isolated (bars 1, 2, 4)."""
    rec = {"site": k, "temp": temp, "fingerprint": fingerprint, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if fresh_world:
        rec["world"] = fresh_quicktest_world(s, sleep=sleep)
    rec["colonyTile"] = _call(s, "jawa/map_info").get("tile")
    rec["pick"] = choose_tile(s, os.path.join(work_dir, "site_%d" % k), rec["colonyTile"])
    centre = rec["pick"]["centre"]
    rec["retiled"] = retile(s, rec["pick"]["patch"], temp)
    strip_mutators(s, centre)
    iso = isolate(s)                               # before mapgen: no burn line at gen
    rec["isolation"] = iso
    try:
        g = generate(s, centre)
        rec["mapId"] = g["mapId"]
        rec["generate"] = {k2: g.get(k2) for k2 in ("pawnCount", "thingCount", "mapIndex", "mapParentDef")}
        h = home(s, g["mapId"])
        rec["colonists"] = h["colonists"]
        rec["tickAtGen"] = _call(s, "jawa/time_clock").get("ticksGame")
        fog_off(s, (P.MAP_SIZE, P.MAP_SIZE))
        if census is not None:
            rec["census"] = census(s, rec)
        rec["ticksGameNoon"] = set_midsummer_noon(s, rec["pick"]["lat"], rec["pick"]["long"])
        name = fixture_name(k, fingerprint, temp)
        rec["save"] = save_fixture(s, name, saves_dir, os.path.join(work_dir, "saves_backup_%d" % k), sleep=sleep)
        rec["saveName"] = name
    finally:
        restore_isolation(s, iso["settingsBefore"])
    rec["reload"] = {k2: reload_fixture(s, rec["saveName"], centre, sleep=sleep, map_id=rec["mapId"]).get(k2)
                     for k2 in ("mapId", "tile", "mapBiome", "outdoorTempNow", "season")}
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
 6 set_current_map -> 3 colonists (PlayerColony) -> fog unfog rect (never unfogAll)
 8 census hook at tick 0 (bars 1, 2, 4)
 - time_set_ticks -> local noon, mid-Summer for the tile's lat/long (simulates nothing)
 9 back up Saves/ -> save_game NS_Pyrelands_site_<k>_<fp> -> stat (new file, nothing else touched)
 - finally: toggles restored to shipped defaults (read back)
   rimworld/load_game -> programState Playing -> current map is the site
 then: preflight_pyrelands.py --gate B --tile <centre>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", action="store_true", help="print the recipe; touch nothing")
    ap.add_argument("--site", type=int, help="fixture index k (1-based)")
    ap.add_argument("--temp", type=float, default=TARGET_TEMP)
    ap.add_argument("--fingerprint", help="def fingerprint from gate A evidence")
    ap.add_argument("--work", default=os.path.join(P.ROOT, "Transient", "modcheck", "pyrelands", "sites"))
    ap.add_argument("--out", help="fixture record JSON (default <work>/site_<k>.json)")
    a = ap.parse_args(argv)
    if a.plan or a.site is None:
        print(STEPS)
        return 0
    from northstar_driver.session import FastSession
    from game_paths import SAVES
    s = FastSession(strict=False)
    with s:
        rec = build_site(s, a.site, a.fingerprint, SAVES, a.work, temp=a.temp)
    out = a.out or os.path.join(a.work, "site_%d.json" % a.site)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, sort_keys=True, default=str)
    print("site %d: tile %s map %s saved %s -> %s" % (a.site, rec["pick"]["centre"], rec.get("mapId"),
                                                      rec.get("saveName"), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
