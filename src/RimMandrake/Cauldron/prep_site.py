#!/usr/bin/env python3
"""Build, clean, save and register the Cauldron saved test site (RM_TestSite_cauldron_v1). LIVE ONLY, bridge holder.

BIOME_SPRINT_PROVE_SCRUB_SETS_PACE, BENCH D0 tooling slice (kickoff packet §4 D0 "Cauldron site"). Data: site_spec.py.
Recipe: Utils/modcheck/biome_site.py (shared with Contagion and LeaningScrub); Cauldron's own read-back is the probe
below (records the vent count). The >=1 living native guard is site_spec.MIN_NATIVES, enforced by the shared recipe.

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
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
_MODCHECK = os.path.join(HERE, "..", "Utils", "modcheck")
if _MODCHECK not in sys.path:
    sys.path.insert(0, _MODCHECK)
import biome_site as B  # noqa: E402

S = B.load_spec(os.path.join(HERE, "site_spec.py"), "cauldron_site_spec")
SiteError = B.SiteError


def probe(call, phase, saved=None):
    """Cauldron's own read-back: the vent count, recorded and never required (the suite builds its own vent pad).
    A read that cannot complete records None. -> (problems, {"vents": n|None})."""
    r = call("jawa/list_things", defName=S.VENT, limit=500) or {}
    n = len(r["things"]) if r.get("success") is not False and isinstance(r.get("things"), list) else None
    return [], {"vents": n}


def site_problems(call, phase="save", saved=None):
    return B.site_problems(call, S, probe, phase, saved)


def build_site_save(s, work_dir, saves_dir=None, sleep=time.sleep):
    return B.build_site_save(s, S, work_dir, saves_dir=saves_dir, sleep=sleep, probe=probe)


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
