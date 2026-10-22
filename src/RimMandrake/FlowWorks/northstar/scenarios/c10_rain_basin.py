"""C10 - The Rain Basin (map C, 44x40, east edge): water bodies and weather - where water comes from, where it goes,
and that every litre is accounted.

A limited pond feeding canal A behind a shut sluice, canal B on to the EAST MAP EDGE (the edge sink) behind a second
shut sluice, a spring (a flow source: never runs out) with its own full canal C, a canyon-flood trigger at the head of
a dry winding canal D, open and roofed rain trenches E/F, a small pond drawn down by the build's pulses with a muffalo
in its bed, a pump with a tank and a hose Intake end in the pond, a map-edge setter, and the fenced closed ledger
(GPT #10). C10 sits alone on the east edge (GPT #11); rain lives in the branch save RM_fw_composite_rain.

The closed ledger: far tank (32,5), hose end (34,5) on the reel outlet's row, reel and near tank at x 40. With the far tank
at (33,3) the end was 1.5 cells past the 2.2-cell straight lead-out and the planner refused it ("no room for the straight
lead-out", live 2026-10-21; reproduced offline, SelfTest HoseBandChecks Scenario_C4_C10_hoses_lay_offline). review_map
builds every reel West, one square east of its staged cell (footprint kept).

Idle-stable: both canal sluices shut; the pump is set to POUR from an EMPTY tank (nothing moves until he sets Draw);
the closed ledger's hose end is Capped; nobody is assigned the fill-in (it is a poke).
"""
from .common import scenario, staged, deferred, perimeter, walls, W, MAPCTL, OVERFLOW_ITEM

SIZE = (44, 40)
POND = ("WaterDeep", 1, 28, 12, 8)
CANAL_A = (13, 31, 12, 1, 2)
CANAL_B = (25, 31, 29, 1, 2)        # local x 25..53 = absolute 221..249: off the east edge
LEDGER = perimeter(31, 1, 42, 9, gaps=[(36, 1)])

SETUP = dict(
    terrain=[POND, ("WaterDeep", 26, 20, 2, 2)],
    dig=[CANAL_A, CANAL_B, (7, 20, 14, 1, 2),                                 # canal C from the spring
         (2, 4, 20, 1, 3), (21, 5, 1, 8, 3), (21, 12, 8, 1, 3),               # canal D, dry, winding
         (2, 12, 5, 6, 2), (9, 12, 5, 6, 2),                                  # rain trenches E (open), F (roofed)
         (28, 20, 10, 1, 2), (37, 21, 1, 4, 2)],                              # the small pond's pay-out canal
    fluid=[(14, 31, 11, 1, 2, W), (7, 20, 14, 1, 2, W)],                      # A full beyond its sluice; C full
    roof=[("RoofConstructed", 9, 12, 5, 6)],
    spawn=[("RM_Sluice", 13, 31, "WoodLog"), ("RM_Sluice", 25, 31, "WoodLog")],
    flood_trigger=[(1, 4, False, False, 0)],
    build=[("RM_LiquidPump", 6, 36, None, None), ("RM_UniversalPipe", 7, 36, None, None),
           ("RM_LiquidTank", 8, 36, None, None), ("RM_HoseReel", 14, 37, None, None),
           ("PowerConduit", 5, 37, None, None), ("PowerConduit", 5, 38, None, None), ("Battery", 4, 37, 0, None),
           ("RM_LiquidTank", 32, 5, None, None), ("RM_LiquidTank", 40, 3, None, None), ("RM_HoseReel", 40, 5, None, None)]
    + walls(LEDGER, "WoodLog", "Fence"),
    batteries=[(4, 37)],
    tank=[(8, 36, "Store", "RM_Liquid_FreshWater", 0), (32, 5, "Store", "RM_Liquid_FreshWater", 8000),
          (40, 3, "Store", "RM_Liquid_FreshWater", 0)],
    pump=[(6, 36, "pour")],
    hose=[(14, 37, 10, 33, None), (40, 5, 34, 5, None)],                      # ledger: the far tank sits on the outlet's row,
                                                                             # a straight run (offline: HoseBandChecks C10)
    gizmos=[(14, 37, "Free end:", "Free end: Intake")],
    markers=[("PlaceSource", 7, 20, "RM_Fluid_Water|1"), ("PlaceEdgeSetter", 40, 15, "aaaa")],
    pawns=[("Muffalo", 26, 20, "none", None)],
    keep=True,
)

SCENARIO = scenario(
    id="C10", n=10, slug="rain_basin", name="The Rain Basin", map="C", size=SIZE, look_style="land and water bodies",
    purpose="A dry wash that floods: a limited pond, a limitless spring, a canyon-flood channel, rain trenches, a "
            "fill-in job and a drain off the map edge - every litre accounted.",
    start="open sluice A (the pond's canal), then sluice B; unpause",
    try_=["START: open sluice A, then B; unpause: the pond's shoreline recedes as canal A draws; B runs off the east "
          "edge; the spring's canal C never drops (a source)",
          "set the pump to Draw: the tank fills from the pond through the hose Intake end; then Pour: back into the pond",
          "designate Fill in canal on canal A's far 4 cells: the filled cells' water goes back to the pond",
          "select the canyon trigger at canal D's head > Flood now: the flood runs IN canal D, not over the land",
          "select the edge setter: set the east edge sealed: B stops draining and fills",
          "closed ledger (fenced, south-east): set the reel's Free end to Outflow: the two tanks' sum stays equal to "
          "the litre while litres move",
          "RAIN BRANCH (RM_fw_composite_rain): trench E fills, roofed F stays dry; the drawn-down pond refills around "
          "the muffalo, never over it"],
    look_for="the pond's edge recedes, the spring's never; no water on open ground beside a full canal; the ledger "
             "sum constant",
    broken="the pond full after heavy draw; the spring's readout not saying it is a source; water on open ground "
           "beside a full canal (with the overflow switch off, its shipped default); water poured onto the muffalo; the flood wiping the canal "
           "flat; a sealed edge still draining; any litre unaccounted",
    idle="sluices A and B shut; the pump Pours from an empty tank; the ledger hose is Capped; canal D and the trenches "
         "dry; the edge setter automatic",
    setup=SETUP,
    edge_drain="east",
    parts=[(6, 36, "pump (Pour, empty tank)"), (13, 33, "sluice A"), (25, 33, "sluice B"), (40, 32, "to the east edge"),
           (6, 26, "limited pond"), (7, 22, "spring (source)"), (1, 6, "flood trigger"), (25, 13, "canal D (dry)"),
           (4, 19, "E open"), (11, 19, "F roofed"), (26, 23, "drawn-down pond + muffalo"), (40, 17, "edge setter"),
           (36, 10, "closed ledger"), (19, 33, "fill-in: far 4 cells")],
    pieces=[staged("limited pond 12x8", "terrain", "WaterDeep", (1, 28)),
            staged("canal A behind a shut sluice", "spawn", "RM_Sluice", (13, 31), "poked"),
            staged("canal B to the east map edge behind a shut sluice", "spawn", "RM_Sluice", (25, 31), "poked"),
            staged("spring = flow source, canal C full", "markers", "PlaceSource", (7, 20), "demonstrated"),
            staged("canyon flood trigger at canal D's head", "flood_trigger", None, (1, 4), "poked"),
            staged("rain trench E open", "dig", None, (2, 12), "poked"),
            staged("rain trench F roofed", "roof", "RoofConstructed", (9, 12), "poked"),
            staged("small pond drawn down, muffalo in the bed", "pawns", "Muffalo", (26, 20), "look"),
            staged("pump (Pour) + empty tank + hose Intake end in the pond", "gizmos", None, (14, 37), "poked"),
            staged("map-edge setter", "markers", "PlaceEdgeSetter", (40, 15), "poked"),
            staged("closed ledger: two tanks, one hose, fenced", "hose", None, (40, 5), "poked"),
            deferred("overflow Stage 1+ (D1, D2, D6)", "overflow is built (Stages 1-3) but its master switch ships OFF and this scenario does not turn it on; canal B is sized so "
                     "sealing the edge with the pump pouring overfills it once the switch is on", OVERFLOW_ITEM, (16, 38)),
            deferred("a limitless BODY marker on a natural pond", "the spring is a flow source; a body flagged "
                     "limitless (and its readout) has no staging surface here", "FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS",
                     (19, 38)),
            deferred("rain (global weather)", "lives in the branch save RM_fw_composite_rain, never the main save",
                     "design §2 GPT #11", (22, 38))],
    exercises={"flow_ponds": "poked", "flow_shrinks": "poked", "pond_bed": "look", "pond_occupied": "poked",
               "pond_return": "poked", "flow_rain": "poked", "flow_canyon": "poked", "flow_drains": "poked",
               "dig_fill_in": "poked", "pump_pour": "poked", "hose_into_pond": "poked",
               "reservoir_fill_visibly_drops": "poked", "never_full_reservoir_after_heavy_draw": "poked",
               "empty_reservoir_stops_flow": "poked", "reservoir_shoreline_recedes": "poked",
               "reservoir_recharge_progress_visible": "poked", "limitless_body_marked": "DEFERRED",
               "canal_holds_only_the_channel": "look", "never_liquid_on_open_ground": "look",
               "half_metre_water_reads_as_silt": "look"},
    goal="live: the closed ledger's two tank stocks sum to 8000 L before and after the soak",
    branch={"rain": "RM_fw_composite_rain: weather Rain locked", "days": "RM_fw_composite_days"},
)
