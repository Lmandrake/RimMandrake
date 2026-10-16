#!/usr/bin/env python3
"""Build, clean, save and register the Cauldron saved test site (RM_TestSite_cauldron_v1). LIVE ONLY, bridge holder.

BIOME_SPRINT_PROVE_SCRUB_SETS_PACE, BENCH D0 tooling slice (kickoff packet §4 D0 "Cauldron site"). Data: site_spec.py.
Pattern: FlowWorks/northstar/prep_site.py; the scratch-world steps are Pyrelands/northstar_site.py's own functions
(fresh world, candidates, mutator strip, mapgen, home, retire the quicktest colony, food), and the clean / read-back /
save / registry steps are Utils/modcheck/test_site_saves.py's, so every site is cleaned the same way.

    python3    src/RimMandrake/Cauldron/prep_site.py --plan                       # offline: print the recipe
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py build cauldron    # LIVE: build + save + register
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py load cauldron     # LIVE: load + read-back
    then: python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Cauldron \\
              --plan src/RimMandrake/Cauldron/northstar_plan.py

Preconditions (the live round's, not checked here): the game is up on the `biomes_sprint` tier with the composite
deployed (preflight_cauldron.py O-TIER / O-DEPLOY PASS), the bridge held by the running seat.
Nothing is saved unless the clean read-back is clean; a save is never overwritten (bump SAVE in site_spec.py).
"""
import argparse
import importlib.util
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import site_spec as S  # noqa: E402

UTILS = os.path.join(S.ROOT, "src", "RimMandrake", "Utils")
for _p in (UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
PYRE = os.path.join(S.ROOT, "src", "RimMandrake", "Pyrelands")


class SiteError(AssertionError):
    pass


_NS = None


def pyre():
    """Pyrelands/northstar_site.py under its own module name (Cauldron has its own northstar_site.py, which must stay
    the one `import northstar_site` finds). Its directory is APPENDED to sys.path for its `preflight_pyrelands` import."""
    global _NS
    if _NS is None:
        if PYRE not in sys.path:
            sys.path.append(PYRE)
        spec = importlib.util.spec_from_file_location("pyrelands_northstar_site", os.path.join(PYRE, "northstar_site.py"))
        _NS = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_NS)
    return _NS


def _call(s, tool, **p):
    r = s.call(tool, **p)
    if not isinstance(r, dict) or r.get("success") is False:
        raise SiteError("%s failed: %s" % (tool, str(r)[:200]))
    return r


def choose_tile(s, export_dir, colony_tile, max_landmark_checks=50):
    """First clean 2-ring land patch (Pyrelands' site_candidates, Cauldron's LAT_MAX) with no landmark."""
    NS = pyre()
    os.makedirs(export_dir, exist_ok=True)
    tiles_csv = os.path.join(export_dir, "world_tiles_extended.csv")
    nbr_csv = os.path.join(export_dir, "world_neighbors.csv")
    e = _call(s, "jawa/world_tile_export", path=tiles_csv, format="csv", extended=True)
    n = _call(s, "jawa/world_neighbors", path=nbr_csv)
    rows = NS.read_tile_csv(e.get("path") or tiles_csv)
    nbrs = NS.read_neighbor_csv(n.get("path") or nbr_csv)
    checked = 0
    for centre, patch in NS.site_candidates(rows, nbrs, colony_tile, lat_max=S.LAT_MAX):
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
    raise SiteError("no clean 2-ring land patch in |lat|<=%s (checked %d)" % (S.LAT_MAX, checked))


def retile(s, patch):
    """RM_Cauldron + site_spec.TILE on every patch tile, written before anything reads the tile's lazy temperature
    caches (world-editing skill, trap 2); RAW read-back."""
    t = S.TILE
    r = _call(s, "jawa/world_tile_set", tiles=",".join(map(str, patch)), biome=S.BIOME, temperature=t["temperature"],
              rainfall=t["rainfall"], elevation=t["elevation"], hilliness=t["hilliness"],
              swampiness=t["swampiness"], readBack=len(patch))
    back = {x.get("tile"): x for x in r.get("tiles") or []}
    if r.get("written") is not None and r["written"] != len(patch):
        raise SiteError("world_tile_set wrote %s of %d tiles" % (r["written"], len(patch)))
    bad = [p for p in patch if (back.get(p) or {}).get("biome") != S.BIOME
           or abs(float((back.get(p) or {}).get("temperature", 1e9)) - t["temperature"]) > 0.5
           or (back.get(p) or {}).get("hilliness") != t["hilliness"]]
    if bad:
        raise SiteError("re-tile read-back wrong on %d tile(s): %s" % (len(bad), bad[:5]))
    return len(patch)


def census(call):
    """Living natives by def and vents on the current map. A read that cannot complete raises (never 'zero')."""
    out = {"natives": {}, "vents": None}
    for d in S.NATIVES:
        r = call("jawa/list_things", defName=d, includePawns=True, limit=500) or {}
        if r.get("success") is False or not isinstance(r.get("things"), list):
            raise SiteError("list_things %s unreadable: %s" % (d, str(r)[:160]))
        out["natives"][d] = len([t for t in r["things"] if not t.get("dead")])
    r = call("jawa/list_things", defName=S.VENT, limit=500) or {}
    if r.get("success") is not False and isinstance(r.get("things"), list):
        out["vents"] = len(r["things"])
    return out


def site_problems(call):
    """Cauldron-only read-back on top of test_site_saves.check_map: biome and natives."""
    P = []
    mi = call("jawa/map_info") or {}
    if mi.get("mapBiome") != S.BIOME:
        P.append("map biome %s, want %s" % (mi.get("mapBiome"), S.BIOME))
    c = census(call)
    if sum(c["natives"].values()) < S.MIN_NATIVES:
        P.append("natives %s: fewer than %d alive (bloom_spares_natives needs one)" % (c["natives"], S.MIN_NATIVES))
    return P, c


def build_site_save(s, work_dir, saves_dir=None, sleep=time.sleep):
    """The whole recipe (STEPS). `s` is a session with .call(tool, **kw) (FastSession, or a fake in the selftest).
    Raises before saving on any unclean read-back. Returns the receipt; receipt['verified'] after the reload check."""
    import test_site_saves as TS
    NS = pyre()
    if saves_dir is None:
        from game_paths import SAVES as saves_dir
    if S.SAVE + ".rws" in TS.saves_stat(saves_dir):
        raise SiteError("%s.rws exists -- bump SAVE in site_spec.py and SITES (a site save is never overwritten)" % S.SAVE)
    rec = {"site": S.SITE, "save": S.SAVE, "utc": TS._now(), "head": TS._head()}
    rec["world"] = NS.fresh_quicktest_world(s, sleep=sleep)
    rec["colonyTile"] = _call(s, "jawa/map_info").get("tile")
    rec["pick"] = choose_tile(s, os.path.join(work_dir, "cauldron_site"), rec["colonyTile"])
    centre = rec["pick"]["centre"]
    rec["retiled"] = retile(s, rec["pick"]["patch"])
    NS.strip_mutators(s, centre)
    g = NS.generate(s, centre, S.MAP_SIZE)
    rec["mapId"] = g["mapId"]
    rec["colonists"] = NS.home(s, g["mapId"], S.COLONISTS)["colonists"]
    rec["retired"] = NS.retire_offsite_colonies(s, centre)
    nm = _call(s, "jawa/name_colony", factionName=S.COLONY_NAME, settlementName=S.COLONY_NAME)
    rec["named"] = [x.get("tile") for x in nm.get("settlements") or []]
    rec["food"] = NS.stock_food(s, S.MAP_SIZE // 2, S.MAP_SIZE // 2, packs=S.FOOD_PACKS)
    rec["clean"] = TS.clean_map(s.call, S.PROFILE)
    if rec["clean"]["problems"]:
        raise SiteError("clean_map not clean: %s" % rec["clean"]["problems"])
    rec["check"] = TS.check_map(s.call, S.SITE)
    extra, rec["census"] = site_problems(s.call)
    if not rec["check"]["verified"] or extra:
        raise SiteError("read-back after the clean: %s" % (rec["check"]["problems"] + extra))
    rec["backup"] = {"dir": os.path.join(work_dir, "saves_backup_%s" % time.strftime("%Y%m%dT%H%M%S"))}
    rec["backup"]["files"] = TS.backup_saves(saves_dir, rec["backup"]["dir"])
    rec["saved"] = TS.save_site(s.call, S.SAVE, saves_dir, sleep=sleep)
    mi = _call(s, "jawa/map_info")
    entry = {"save": S.SAVE, "tile": mi.get("tile"), "mapId": mi.get("mapId"), "biome": mi.get("mapBiome"),
             "builtUtc": rec["utc"], "head": rec["head"], "profile": S.PROFILE, "census": rec["census"],
             "outdoorAtSave": mi.get("outdoorTempNow"), "bytes": rec["saved"]["bytes"]}
    TS.write_registry(S.SITE, entry)               # load_site reads tile/mapId from the registry
    # The reload is the one reliable entry path (it cures the black generated-map render, Pyrelands §3.4):
    # load the save back from the main menu and read it back clean before the site counts as built.
    rec["reload"] = TS.load_site(s.call, S.SITE, sleep=sleep)
    extra2, c2 = site_problems(s.call)
    rec["reload"]["problems"] = list(rec["reload"].get("problems") or []) + extra2
    rec["verified"] = bool(rec["reload"].get("verified")) and not extra2
    entry["loadVerified"] = rec["verified"]
    entry["censusAfterLoad"] = c2
    TS.write_registry(S.SITE, entry)
    return rec


STEPS = """Cauldron saved-site recipe (%(save)s, profile %(profile)s), bridge holder, game up on biomes_sprint:
 1 main menu if Playing -> start_debug_game_ready ONCE -> poll Playing          (Pyrelands fresh_quicktest_world)
 2 world_tile_export + world_neighbors -> first clean 2-ring land patch, |lat|<=%(lat)s, >= 10 steps from the
   quicktest colony, no landmark                                                 (Pyrelands site_candidates)
 3 world_tile_set patch: %(biome)s, %(tile)s -> RAW read-back
 4 world_mutators_set clear (centre) -> read-back empty -> world_commit          (Pyrelands strip_mutators)
 5 colony_found + world_tile_map_generate %(size)dx%(size)d -> fresh, failedSteps == []   (Pyrelands generate)
 6 set_current_map -> %(cols)d colonists -> abandon the quicktest colony (all colonists on the site)
   -> jawa/name_colony "%(name)s" -> %(food)d MealSurvivalPack east of centre + needs topped
 7 test_site_saves.clean_map(profile=%(profile)s): dangers, triggers, hostiles, fog, fire GONE; wildlife and vents STAY
 8 read-back: check_map(cauldron) [size, fog 0, triggers, danger, hostiles, threats, fires, rain, outdoor %(band)s C,
   >= %(cols)d colonists, map biome %(biome)s] + census: >= %(minn)d living native of %(natives)s; vents recorded
 9 back up Saves/ -> save_game %(save)s -> stat (new file, nothing else touched) -> registry test_site_saves.json
10 load_site(cauldron) from the main menu -> quiet profile + calm sky -> check_map + census again -> registry
   loadVerified. Nothing is saved if 7 or 8 is not clean; nothing is ever overwritten.
Then: northstar_driver run --mod Cauldron --plan src/RimMandrake/Cauldron/northstar_plan.py (its preflight checks
settings at shipped defaults and turns the storyteller off) on the loaded site.
""" % {"save": S.SAVE, "profile": S.PROFILE, "lat": S.LAT_MAX, "biome": S.BIOME, "tile": S.TILE, "size": S.MAP_SIZE,
       "cols": S.COLONISTS, "name": S.COLONY_NAME, "food": S.FOOD_PACKS, "band": S.TEMP_BAND, "minn": S.MIN_NATIVES,
       "natives": ", ".join(S.NATIVES)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", action="store_true", help="print the recipe; touch nothing (the default)")
    ap.parse_args(argv)
    print(STEPS)
    print("Build it with: python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py build cauldron")
    return 0


if __name__ == "__main__":
    sys.exit(main())
