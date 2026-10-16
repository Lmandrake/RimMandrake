"""Contagion saved test site: the data prep_site.py, test_site_saves.py and the preflight read.

BIOME_SPRINT_PROVE_SCRUB_SETS_PACE, kickoff packet design/RimMandrake/biome_sprint_kickoff_2026-10-15.md §1.2: the
suite's on-Contagion rows (sky state reads of RM_MapComponent_ContagionSky, Bloom/Burn tells, Sunbeam, coalescence,
genome, the Unfinished) want a real RM_Contagion map; the off-Contagion arm (repulsor_clear.site_ready_baseline and
downstream, site.retile_to_contagion) keeps running on the calm site. Pattern: Cauldron/site_spec.py; recipe shared in
Utils/modcheck/biome_site.py. Dev tooling only: deploy_custom_mods.py never ships *.py.

A SCRATCH vanilla quicktest world with a 2-ring patch re-tiled to RM_Contagion: never Ash'karr, never a seed sweep,
never anything a player receives (CLAUDE.md worldgen ban). RM_Contagion on 0 tiles of the real planet is expected.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

SITE = "contagion"                        # key in Utils/modcheck/test_site_saves.SITES and its registry
SAVE = "RM_TestSite_contagion_v1"         # a site save is never overwritten: a rebuild bumps _vN here AND in SITES
BIOME = "RM_Contagion"
PROFILE = "danger"                        # the biome IS the subject: its wildlife and ocular flora stay, dangers go
MAP_SIZE = 250                            # validation.py pads sit 45 cells from the centre, PAD_SIZE 30 (<= 60 out)
COLONISTS = 3
TEMP_BAND = (0.0, 38.0)                   # check_map's outdoor band; the tile mean is 25 C, so a hot afternoon passes

# Tile values, from design/Jawa/worldbuilding/biomes/the_contagion.md §0 (measured, 179 painted tiles):
# temp p10/median/p90 25/32/45 C, elevation median 1,387 m, rain median 60 mm. Chosen for a TEST site, not realism:
# 25 C (the p10, not the 32 C median) so colonists do not take heatstroke across long chains; Flat, not the peaks the
# biome lives on, because the suite's seven 30-cell pads need open ground (a pad clears things, not natural rock).
TILE = {"temperature": 25.0, "rainfall": 60.0, "elevation": 1387.0, "hilliness": "Flat", "swampiness": 0.0}
LAT_MAX = 45.0                            # scratch world only: any temperate land; the tile temperature is written

# Natives: RM_Contagion's own MayRequire-free wildAnimals rows (selftest_contagion_site.py re-derives them from the
# BiomeDef and fails on drift). The saved map must hold at least MIN_NATIVES alive after the clean.
NATIVES = ("RM_Gawpsack", "RM_Scorchpod", "RM_BloodyMess", "RM_ContagionIkee", "RM_Peeper", "RM_Ogleknot",
           "RM_Eyestinger", "RM_Fleshsop", "RM_Blisterfloat", "RM_Bloodlurk", "RM_Sparkleech", "RM_Doublemaw",
           "RM_Meltgut", "RM_Scaldhide", "RM_Gnashling", "RM_Skinflap", "RM_Sloshbelly", "RM_Crispling",
           "RM_Danglemaw", "RM_Gorekite", "RM_SparkleechGrub", "RM_OcularJelly", "RM_InfectedAerofleet")
MIN_NATIVES = 1

# The sky: a site must not be saved (or load) mid-Burn. Read by jawa/map_comp_read on this component.
SKY_COMP = "RM_MapComponent_ContagionSky"
SKY_MEMBERS = ("BurnActive", "NextBurnTick", "TellsBegun")

FOOD_PACKS = 60
FOOD_AT = (125, 145)                      # stacks at x 150..155, z 145: the coal pad (170,125) spans z 110..140 and
                                          # x 155..185, the genome pad (125,170) z 155..185 -- the centre row would
                                          # put the last stack on the coal pad's edge
COLONY_NAME = "Northstar Contagion"

SERVES = ("the on-Contagion chains: sky state (Bloom/Burn tells), burn_forced/burn_natural, uv, coalescence, genome,"
          " spawner, Sunbeam and limb rows (packet §1.2)",)
# NOT this site's job: the off-Contagion arm (the retile control) stays on the calm site; northstar_site.py's
# preflight still REFUSES an RM_Contagion map ("the retile has no control") until the arms are split (harness work).


def site_entry():
    """The SITES row test_site_saves.py carries for this site (single-sourced here; selftest compares them)."""
    return {"save": SAVE, "profile": PROFILE, "size": MAP_SIZE, "temp": TEMP_BAND, "minColonists": COLONISTS,
            "biome": BIOME, "builder": "Contagion/prep_site.py",
            "suites": ["northstar_driver/cli.py run --mod Contagion --plan src/RimMandrake/Contagion/northstar_plan.py"
                       " (on-Contagion arm only; needs the arm split first)"]}
