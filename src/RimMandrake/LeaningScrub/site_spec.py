"""LeaningScrub saved test site: the data prep_site.py, test_site_saves.py and the preflight read.

Item LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY (called LEANING_SCRUB_LEAN_SITE_1 in validation.py and the walk); kickoff
packet design/RimMandrake/biome_sprint_kickoff_2026-10-15.md §1.3 "New, needing a Scrub site". The Lean applies only on
a map whose BIOME carries RM_LeanExtension; RM_MapComponent_Lean locks ONE heading the first time anything asks for
Downwind and Scribes it (rmLeanHeadingDegrees). So the site is built to LEAN ONE WAY: the heading is locked and read
before the save, and after the reload the SAME heading must come back off the save before anything asks again.
Pattern: Cauldron/site_spec.py; recipe shared in Utils/modcheck/biome_site.py. Dev tooling only, never shipped.

A SCRATCH vanilla quicktest world with a 2-ring patch re-tiled to RM_LeaningScrub: never Ash'karr, never a seed
sweep, never anything a player receives (CLAUDE.md worldgen ban). RM_LeaningScrub on 0 real tiles is expected.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

SITE = "leaningscrub"                     # key in Utils/modcheck/test_site_saves.SITES and its registry
SAVE = "RM_TestSite_leaningscrub_v1"      # a site save is never overwritten: a rebuild bumps _vN here AND in SITES
BIOME = "RM_LeaningScrub"
PROFILE = "danger"                        # ruins and camps are the subject (item text): they stay, dangers go
MAP_SIZE = 250                            # validation.py pads sit 45 cells from the centre, PAD_SIZE 24 (<= 57 out)
COLONISTS = 3
TEMP_BAND = (0.0, 32.0)                   # check_map's outdoor band at save and at every load

# Tile values, from design/Jawa/worldbuilding/biomes/arid_shrubland.md (measured, 665 tiles): temp median 19.7 C,
# elevation median 15 m, flat (312/361 core tiles), no rain planet-wide (rule 1), |lat| median 22.5.
TILE = {"temperature": 19.7, "rainfall": 0.0, "elevation": 15.0, "hilliness": "Flat", "swampiness": 0.0}
LAT_MAX = 45.0                            # scratch world only: any temperate land; the tile temperature is written

# Natives: RM_LeaningScrub's MayRequire-free wildAnimals rows whose race is NOT a predator -- the Lean's scent row
# needs "a wild non-predator" to flee a person standing upwind. selftest_leaningscrub_site.py re-derives this from
# the BiomeDef + race defs and fails on drift.
NATIVES = ("RM_Fuzzrunner", "RM_Thornhold", "RM_Vissler", "RM_Dustflutter", "RM_Shirrel", "RM_Crustweevil",
           "RM_Rollbug", "RM_Tikkit")
MIN_NATIVES = 1

# The Lean, read by jawa/map_comp_read. ORDER MATTERS at the save: Downwind's getter locks the heading, then the
# field is read. At the reload only Applies + the field are read, so a heading the save did not carry reads -1.
LEAN_COMP = "RM_MapComponent_Lean"
LEAN_LOCK_MEMBERS = ("Applies", "Downwind", "headingDegrees")
LEAN_RELOAD_MEMBERS = ("Applies", "headingDegrees")
HEADING_TOL = 0.01

FOOD_PACKS = 60                           # 6 stacks along +x from centre+25 (x 150..155), clear of the dripping pad
COLONY_NAME = "Northstar Scrub"

SERVES = ("the Lean rows: heading locks per map, scent flee upwind within leanScentRange, downwind fire bias",
          "every LeaningScrub chain on a real Scrub map (packet §1.3)")


def site_entry():
    """The SITES row test_site_saves.py carries for this site (single-sourced here; selftest compares them)."""
    return {"save": SAVE, "profile": PROFILE, "size": MAP_SIZE, "temp": TEMP_BAND, "minColonists": COLONISTS,
            "biome": BIOME, "builder": "LeaningScrub/prep_site.py",
            "suites": ["northstar_driver/cli.py run --mod LeaningScrub --plan "
                       "src/RimMandrake/LeaningScrub/northstar_plan.py"]}
