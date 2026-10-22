"""C11 - Prospector's Creek (map R, river-anchored, look Scrapper): the moving-water scenario on a real river.

C11 is review_map_rivers.py's eight R stations (current, ford, weir, worn weir, stakes, silt trap, ferry, sluice box +
panning) re-laid as ONE creek walk with a C11 sign book and labels: its cells are not a fixed rect but the river's own
crossings, picked live by review_map_rivers.river_anchors() (pure, selftested there) with C1's plot passed as the
cell to keep away from. Design §3 C11 ("Low (~60 lines new): ... re-lay them into one plot and add labels/sign books").
A control colonist stands in the moving water beside the ford (added here; the R stations had only the stones' one).
"""
from .common import scenario, staged, deferred

STATION_IDS = ("r_current", "r_ford", "r_weir", "r_breach", "r_stakes", "r_silt", "r_ferry", "r_placer")

SCENARIO = scenario(
    id="C11", n=11, slug="prospectors_creek", name="Prospector's Creek", map="R", size=None, look_style="Scrapper",
    purpose="A working creek: ford stones, a stake levee and silt trap, a weir a flood wears through, a ferry rope "
            "across the deep run, panning and a sluice box - on a real river with real current.",
    start="unpause",
    try_=["START: unpause: the control colonist in the water is carried; the one on the ford stones is not; logs drift",
          "ferry a colonist across the deep run (the rope); the stones carry him dry",
          "watch the weir pool; dev: Incidents > seasonal flood: the worn weir breaches, the stakes hold the bank "
          "(water leaks only through the gap), the silt trap's neighbours richen",
          "panners and the sluice box draw from the shared stock; setting off washes nothing",
          "stand a throwaway colonist in moving water at the map edge: swept off the map; he walks home"],
    look_for="the push follows the river's bend; stones read as stones, not dry ground; the rope drawn above the water",
    broken="nobody carried; the stones carrying; the ferry ignored; a weir that never pools or never breaks; wash drawn "
           "from nothing",
    idle="nothing staged moves by itself except the river: the carried muffalo and logs ARE the demonstration (the "
         "soak reads buildings, not those)",
    setup=dict(),
    anchor="river_stations",
    parts=[],
    pieces=[staged("R station %s on a real crossing" % sid, "rv_station", sid, None) for sid in STATION_IDS]
    + [staged("control colonist in moving water beside the ford", "rv_extra", "control", None, "poked"),
       deferred("a rope suspension bridge over the deep run", "suspension over water is in review "
                "(SUSPENSION_WATERS_BUILD_MAY_BACKTRACK); the ferry rope carries the crossing", "SUSPENSION_WATERS_BUILD_MAY_BACKTRACK",
                None),
       deferred("panners assigned", "work assignment is his (Work tab); the panning spot is placed",
                "RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED", None)],
    exercises={"r_current": "demonstrated", "r_ford": "poked", "r_weir": "demonstrated", "r_breach": "poked",
               "r_stakes": "poked", "r_silt": "demonstrated", "r_ferry": "poked", "r_placer": "poked",
               "land_panning": "poked", "river_ford": "look", "river_works_looks": "look",
               "deep_water_pawn_swims": "poked", "pawn_lowers_on_deeper_cell": "look"},
    goal="live: river_anchors places all eight stations (unplaced ones are reported, never faked)",
)
