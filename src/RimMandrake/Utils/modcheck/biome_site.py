#!/usr/bin/env python3
"""Shared saved-site recipe for a biome suite: scratch quicktest world -> 2-ring patch re-tiled to the biome -> map ->
clean -> read back -> save -> registry -> reload -> read back. LIVE ONLY, bridge holder. Dev tooling, never deployed.

BIOME_SPRINT_PROVE_SCRUB_SETS_PACE (kickoff packet design/RimMandrake/biome_sprint_kickoff_2026-10-15.md §4 D0). The
recipe is Cauldron's (src/RimMandrake/Cauldron/prep_site.py, commit e1e5a6ff3a) with the biome's data passed in as a
`spec` module (a <Biome>/site_spec.py) and its own extra read-back as a `probe(call, phase, saved)` function, so
Cauldron, Contagion and LeaningScrub run the same steps instead of a copy each.

`spec` must carry: SITE SAVE BIOME PROFILE MAP_SIZE COLONISTS TEMP_BAND TILE LAT_MAX NATIVES MIN_NATIVES FOOD_PACKS
COLONY_NAME (optional FOOD_AT). `probe(call, phase, saved)` -> (problems, info): phase "save" runs on the cleaned map before the save,
phase "reload" after the reload with `saved` = the save-phase info. A problem at "save" stops the build BEFORE anything
is written; a problem at "reload" leaves the site registered but loadVerified False.

The worlds are SCRATCH vanilla quicktests: never Ash'karr, never a seed sweep, never anything a player receives
(CLAUDE.md worldgen ban). A biome of ours on 0 tiles of the real planet is the expected state.
"""
import importlib.util
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
ROOT = os.path.abspath(os.path.join(_UTILS, "..", "..", ".."))
PYRE = os.path.join(ROOT, "src", "RimMandrake", "Pyrelands")
for _p in (_UTILS, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)


class SiteError(AssertionError):
    pass


_NS = None


def pyre():
    """Pyrelands/northstar_site.py under its own module name (each biome has its own northstar_site.py, which must stay
    the one `import northstar_site` finds). Its directory is APPENDED to sys.path for its `preflight_pyrelands` import."""
    global _NS
    if _NS is None:
        if PYRE not in sys.path:
            sys.path.append(PYRE)
        spec = importlib.util.spec_from_file_location("pyrelands_northstar_site", os.path.join(PYRE, "northstar_site.py"))
        _NS = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_NS)
    return _NS


def load_spec(path, name):
    """A biome's site_spec.py by file path under a unique module name: three biomes each own a `site_spec.py`, and a
    plain `import site_spec` in one process returns whichever was imported first."""
    sp = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


def _call(s, tool, **p):
    r = s.call(tool, **p)
    if not isinstance(r, dict) or r.get("success") is False:
        raise SiteError("%s failed: %s" % (tool, str(r)[:200]))
    return r


def comp_read(call, comp, members):
    """jawa/map_comp_read -> {member: text}. Raises when the read cannot complete or a member is missing (never a
    silent default). Members are read IN ORDER (a property getter with a side effect, like the Lean's Downwind, runs
    before the fields after it)."""
    r = call("jawa/map_comp_read", comp=comp, members=",".join(members)) or {}
    if r.get("success") is False or not isinstance(r.get("values"), dict):
        raise SiteError("map_comp_read %s unreadable: %s" % (comp, str(r)[:200]))
    if r.get("missing"):
        raise SiteError("map_comp_read %s: members missing %s" % (comp, r["missing"]))
    return r["values"]


def as_bool(v):
    return str(v).strip().lower() == "true"


def as_float(v):
    try:
        return float(str(v).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None


def choose_tile(s, spec, export_dir, colony_tile, max_landmark_checks=50):
    """First clean 2-ring land patch (Pyrelands' site_candidates, the spec's LAT_MAX) with no landmark."""
    NS = pyre()
    os.makedirs(export_dir, exist_ok=True)
    tiles_csv = os.path.join(export_dir, "world_tiles_extended.csv")
    nbr_csv = os.path.join(export_dir, "world_neighbors.csv")
    e = _call(s, "jawa/world_tile_export", path=tiles_csv, format="csv", extended=True)
    n = _call(s, "jawa/world_neighbors", path=nbr_csv)
    rows = NS.read_tile_csv(e.get("path") or tiles_csv)
    nbrs = NS.read_neighbor_csv(n.get("path") or nbr_csv)
    checked = 0
    for centre, patch in NS.site_candidates(rows, nbrs, colony_tile, lat_max=spec.LAT_MAX):
        checked += 1
        if checked > max_landmark_checks:
            break
        mu = _call(s, "jawa/world_mutators_get", tiles=",".join(map(str, patch)), limit=100)
        trows = mu.get("tiles")
        if not isinstance(trows, list) or len(trows) != len(patch):
            raise SiteError("world_mutators_get returned %s rows for %d tiles" % (
                None if trows is None else len(trows), len(patch)))
        if any(r.get("landmark") for r in trows):
            continue
        return {"centre": centre, "patch": patch, "lat": rows[centre]["lat"], "long": rows[centre]["long"],
                "was": dict(rows[centre]), "candidatesChecked": checked}
    raise SiteError("no clean 2-ring land patch in |lat|<=%s (checked %d)" % (spec.LAT_MAX, checked))


def retile(s, spec, patch):
    """spec.BIOME + spec.TILE on every patch tile, written before anything reads the tile's lazy temperature caches
    (world-editing skill, trap 2); RAW read-back."""
    t = spec.TILE
    r = _call(s, "jawa/world_tile_set", tiles=",".join(map(str, patch)), biome=spec.BIOME, temperature=t["temperature"],
              rainfall=t["rainfall"], elevation=t["elevation"], hilliness=t["hilliness"],
              swampiness=t["swampiness"], readBack=len(patch))
    back = {x.get("tile"): x for x in r.get("tiles") or []}
    if r.get("written") is not None and r["written"] != len(patch):
        raise SiteError("world_tile_set wrote %s of %d tiles" % (r["written"], len(patch)))
    bad = [p for p in patch if (back.get(p) or {}).get("biome") != spec.BIOME
           or abs(float((back.get(p) or {}).get("temperature", 1e9)) - t["temperature"]) > 0.5
           or (back.get(p) or {}).get("hilliness") != t["hilliness"]]
    if bad:
        raise SiteError("re-tile read-back wrong on %d tile(s): %s" % (len(bad), bad[:5]))
    return len(patch)


def census(call, spec):
    """Living natives by def on the current map. A read that cannot complete raises (never 'zero')."""
    out = {}
    for d in spec.NATIVES:
        r = call("jawa/list_things", defName=d, includePawns=True, limit=500) or {}
        if r.get("success") is False or not isinstance(r.get("things"), list):
            raise SiteError("list_things %s unreadable: %s" % (d, str(r)[:160]))
        out[d] = len([t for t in r["things"] if not t.get("dead")])
    return out


def site_problems(call, spec, probe=None, phase="save", saved=None):
    """Biome read-back on top of test_site_saves.check_map: map biome, >= MIN_NATIVES living natives, then the biome's
    own probe. -> (problems, {"natives": {...}, "probe": info})."""
    P = []
    mi = call("jawa/map_info") or {}
    if mi.get("mapBiome") != spec.BIOME:
        P.append("map biome %s, want %s" % (mi.get("mapBiome"), spec.BIOME))
    info = {"natives": census(call, spec), "probe": None}
    if sum(info["natives"].values()) < spec.MIN_NATIVES:
        P.append("natives %s: fewer than %d alive" % (info["natives"], spec.MIN_NATIVES))
    if probe is not None:
        try:
            p2, info["probe"] = probe(call, phase, saved)
        except SiteError as ex:
            p2 = ["probe: %s" % ex]
        P.extend(p2)
    return P, info


def clear_colonist_ground(s, radius=2):
    """Remove the plants within `radius` of every colonist, so no colonist is SAVED standing in a stand that hurts it.
    LIVE 2026-10-16 (SPRINT_SITES_DIAGNOSE_VENOMVINE_SCRATCHES, SITE): RM_TestSite_leaningscrub_v1 saved colonist Yume
    on an RM_DrippingVenomvine cell (colonists spawn on random standable cells around the centre, and a venomvine stand
    is standable); the contact venom scratched Yume ~15 ticks into every load and every 2500 ticks after, and 13 rows
    went UNMEASURED. -> the rects cleared. Raises when the colonists cannot be read. HIDES: nothing reads the cleared
    cells back; a plant that regrows there before the save is not caught (a save follows within seconds)."""
    import helpers as H
    r = s.call("jawa/list_pawns", limit=500) or {}
    if r.get("success") is False or not isinstance(r.get("pawns"), list):
        raise SiteError("list_pawns unreadable before clearing colonist ground: %s" % str(r)[:200])
    rows = [p for p in r["pawns"] if H.is_colonist(p) and not p.get("dead")]
    return H.clear_bystander_ground(s, rows, radius)


def build_site_save(s, spec, work_dir, saves_dir=None, sleep=time.sleep, probe=None):
    """The whole recipe (steps()). `s` has .call(tool, **kw) (FastSession, or a fake in a selftest). Raises before
    saving on any unclean read-back. Returns the receipt; receipt['verified'] after the reload check."""
    import test_site_saves as TS
    NS = pyre()
    if saves_dir is None:
        from game_paths import SAVES as saves_dir
    if spec.SAVE + ".rws" in TS.saves_stat(saves_dir):
        raise SiteError("%s.rws exists -- bump SAVE in site_spec.py and SITES (a site save is never overwritten)" % spec.SAVE)
    rec = {"site": spec.SITE, "save": spec.SAVE, "utc": TS._now(), "head": TS._head()}
    rec["world"] = NS.fresh_quicktest_world(s, sleep=sleep)
    rec["colonyTile"] = _call(s, "jawa/map_info").get("tile")
    rec["pick"] = choose_tile(s, spec, os.path.join(work_dir, "%s_site" % spec.SITE), rec["colonyTile"])
    centre = rec["pick"]["centre"]
    rec["retiled"] = retile(s, spec, rec["pick"]["patch"])
    NS.strip_mutators(s, centre)
    g = NS.generate(s, centre, spec.MAP_SIZE)
    rec["mapId"] = g["mapId"]
    rec["colonists"] = NS.home(s, g["mapId"], spec.COLONISTS)["colonists"]
    rec["retired"] = NS.retire_offsite_colonies(s, centre)
    nm = _call(s, "jawa/name_colony", factionName=spec.COLONY_NAME, settlementName=spec.COLONY_NAME)
    rec["named"] = [x.get("tile") for x in nm.get("settlements") or []]
    fx, fz = getattr(spec, "FOOD_AT", (spec.MAP_SIZE // 2, spec.MAP_SIZE // 2))   # stacks go at x fx+25.. on row fz
    rec["food"] = NS.stock_food(s, fx, fz, packs=spec.FOOD_PACKS)
    rec["clean"] = TS.clean_map(s.call, spec.PROFILE)
    if rec["clean"]["problems"]:
        raise SiteError("clean_map not clean: %s" % rec["clean"]["problems"])
    rec["colonistGround"] = clear_colonist_ground(s)
    rec["check"] = TS.check_map(s.call, spec.SITE)
    extra, rec["census"] = site_problems(s.call, spec, probe, "save")
    if not rec["check"]["verified"] or extra:
        raise SiteError("read-back after the clean: %s" % (rec["check"]["problems"] + extra))
    rec["backup"] = {"dir": os.path.join(work_dir, "saves_backup_%s" % time.strftime("%Y%m%dT%H%M%S"))}
    rec["backup"]["files"] = TS.backup_saves(saves_dir, rec["backup"]["dir"])
    rec["saved"] = TS.save_site(s.call, spec.SAVE, saves_dir, sleep=sleep)
    mi = _call(s, "jawa/map_info")
    entry = {"save": spec.SAVE, "tile": mi.get("tile"), "mapId": mi.get("mapId"), "biome": mi.get("mapBiome"),
             "builtUtc": rec["utc"], "head": rec["head"], "profile": spec.PROFILE, "census": rec["census"],
             "outdoorAtSave": mi.get("outdoorTempNow"), "bytes": rec["saved"]["bytes"]}
    TS.write_registry(spec.SITE, entry)            # load_site reads tile/mapId from the registry
    # The reload is the one reliable entry path (it cures the black generated-map render, Pyrelands §3.4):
    # load the save back from the main menu and read it back clean before the site counts as built.
    rec["reload"] = TS.load_site(s.call, spec.SITE, sleep=sleep)
    extra2, c2 = site_problems(s.call, spec, probe, "reload", rec["census"].get("probe"))
    rec["reload"]["problems"] = list(rec["reload"].get("problems") or []) + extra2
    rec["verified"] = bool(rec["reload"].get("verified")) and not extra2
    entry["loadVerified"] = rec["verified"]
    entry["censusAfterLoad"] = c2
    TS.write_registry(spec.SITE, entry)
    return rec


def steps(spec, probe_lines=""):
    """The recipe as text (prep_site.py --plan)."""
    return """%(biome)s saved-site recipe (%(save)s, profile %(profile)s), bridge holder, game up on biomes_sprint:
 1 main menu if Playing -> start_debug_game_ready ONCE -> poll Playing          (Pyrelands fresh_quicktest_world)
 2 world_tile_export + world_neighbors -> first clean 2-ring land patch, |lat|<=%(lat)s, >= 10 steps from the
   quicktest colony, no landmark                                                 (Pyrelands site_candidates)
 3 world_tile_set patch: %(biome)s, %(tile)s -> RAW read-back
 4 world_mutators_set clear (centre) -> read-back empty -> world_commit          (Pyrelands strip_mutators)
 5 colony_found + world_tile_map_generate %(size)dx%(size)d -> fresh, failedSteps == []   (Pyrelands generate)
 6 set_current_map -> %(cols)d colonists -> abandon the quicktest colony (all colonists on the site)
   -> jawa/name_colony "%(name)s" -> %(food)d MealSurvivalPack east of %(foodat)s + needs topped
 7 test_site_saves.clean_map(profile=%(profile)s) -> plants within 2 cells of every colonist removed
   (clear_colonist_ground: no colonist is saved standing in a venomvine stand)
 8 read-back: check_map(%(site)s) [size, fog 0, triggers, danger, hostiles, threats, fires, rain, outdoor %(band)s C,
   >= %(cols)d colonists, map biome %(biome)s] + census: >= %(minn)d living native of %(natives)s
%(probe)s 9 back up Saves/ -> save_game %(save)s -> stat (new file, nothing else touched) -> registry test_site_saves.json
10 load_site(%(site)s) from the main menu -> quiet profile + calm sky -> check_map + census + probe again -> registry
   loadVerified. Nothing is saved if 7 or 8 is not clean; nothing is ever overwritten.
""" % {"save": spec.SAVE, "profile": spec.PROFILE, "lat": spec.LAT_MAX, "biome": spec.BIOME, "tile": spec.TILE,
       "size": spec.MAP_SIZE, "cols": spec.COLONISTS, "name": spec.COLONY_NAME, "food": spec.FOOD_PACKS,
       "band": spec.TEMP_BAND, "minn": spec.MIN_NATIVES, "natives": ", ".join(spec.NATIVES), "site": spec.SITE,
       "probe": probe_lines,
       "foodat": getattr(spec, "FOOD_AT", "centre")}
