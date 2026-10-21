"""Cauldron saved test site: the data prep_site.py, test_site_saves.py and the preflight read.

BIOME_SPRINT_PROVE_SCRUB_SETS_PACE (kickoff packet design/RimMandrake/biome_sprint_kickoff_2026-10-15.md §1 M1, §1.1:
`bloom.bloom_spares_natives` needs "a real RM_Cauldron site with a native and a non-native herbivore"). Pattern:
FlowWorks/northstar/site_spec.py (data) + prep_site.py (recipe); Pyrelands/northstar_site.py supplies the scratch-world
steps. Dev tooling only: deploy_custom_mods.py never ships *.py.

The site is a SCRATCH vanilla quicktest world with a 2-ring patch re-tiled to RM_Cauldron: never Ash'karr, never a
seed sweep, never anything a player receives (CLAUDE.md worldgen ban). RM_Cauldron on 0 tiles of the real planet is the
expected state; this patch exists only on the discarded test world.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

SITE = "cauldron"                         # key in Utils/modcheck/test_site_saves.SITES and its registry
SAVE = "RM_TestSite_cauldron_v2"          # a site save is never overwritten: a rebuild bumps _vN here AND in SITES
BIOME = "RM_Cauldron"
PROFILE = "danger"                        # the biome IS the subject: its wildlife and vents stay, dangers go
MAP_SIZE = 250                            # validation.py pads sit up to 85 cells from the centre (PADS, PAD_SIZE 24)
COLONISTS = 3
TEMP_BAND = (0.0, 30.0)                   # check_map's outdoor band at save and at every load

# Tile values, from design/Jawa/worldbuilding/biomes/cauldron.md §0 (measured on Ash'karr, 546 PoisonForest tiles):
# canon +14 C at theta 90, realised median +13.0 C; rain median 0 mm (water arrives as condensation, never rain);
# elevation median 58 m; flat is the commonest hilliness (311 of 546); no water or river tiles.
TILE = {"temperature": 13.0, "rainfall": 0.0, "elevation": 58.0, "hilliness": "Flat", "swampiness": 0.0}
LAT_MAX = 45.0                            # scratch world only: any temperate land; the tile temperature is written

# Natives (validation.NATIVES): the biome's own MayRequire-free wildAnimals rows. The saved map must hold at least
# MIN_NATIVES of them alive after the clean, or bloom_spares_natives has no native to spare.
NATIVES = ("RM_Suush", "RM_Vexxiss", "RM_Zisska", "RM_Eskith")
MIN_NATIVES = 1
VENT = "RM_CauldronVent"                  # recorded, not required: the suite builds its own vent pad (PADS["vent"])

# Food: the colony must not starve between site loads and long chains. 60 packs = 6 stacks along +x from centre+25
# (x 150..155 at z 125), clear of validation.py's yield pad (centre (170,125), 24 cells -> x 158..182).
FOOD_PACKS = 60

COLONY_NAME = "Northstar Cauldron"

# What this site serves (packet §1.1 rows that need a real RM_Cauldron map, not a calm quicktest):
SERVES = ("bloom.bloom_spares_natives", "the M1 run of every Cauldron chain on its registered site")
# NOT this site's job (suite-side fixes, packet §1.1): suush control out of blast reach (validation.py PADS),
# the test vexxiss penned in the pond (water chain), the yield harvest rerun (CAULDRON_YIELD_LIVE_RERUN_1).


def site_entry():
    """The SITES row test_site_saves.py carries for this site (single-sourced here; selftest compares them)."""
    return {"save": SAVE, "profile": PROFILE, "size": MAP_SIZE, "temp": TEMP_BAND, "minColonists": COLONISTS,
            "biome": BIOME, "builder": "Cauldron/prep_site.py",
            "suites": ["northstar_driver/cli.py run --mod Cauldron --plan src/RimMandrake/Cauldron/northstar_plan.py"]}
