"""C4 - The Wet Quarry (map C, 40x40, look Industrial): dug below the water table, kept workable by pumping up and away.

A stepped quarry (D1 > D2 > D3 benches, soil walls west, rock walls east), a machine-dug sump (3 m) with groundwater
bleeding in from a bleed well and LOW/HIGH marks on its wall, a pump on the D3 bench with a hose up the ramp to a drain canal
that runs off the map's west edge (the only edge drain on this map besides C10's), three flow meters, a workbench just
above HIGH as the stake, a miner in climbing gear, a rail ladder on the sump wall, a wrecked pumping station on the rim.
Design §3 C4; GPT #7 (no level holder; LOW/HIGH marks; three meters; a workbench; the dig order as a ~70-cell job).

Digs here are INCREMENTS (flowworks_excavation_drive calls Deepen() N times), so the nested benches sum: D1 ring,
+1 = D2, +1 = D3, sump +3 = 6 levels (3 m).
"""
from .common import scenario, staged, deferred, DEEP_DIG_ITEM, W

SIZE = (40, 40)
SUMP = (14, 14, 4, 4, 3)
DRAIN = (-12, 36, 16, 1, 1)         # west to the map edge: plot x 12 (absolute) - 12 = 0

SETUP = dict(
    terrain=[("Granite_Rough", 20, 0, 20, 36)],                              # rock east, soil west: wall faces differ
    dig=[(4, 4, 32, 30, 1), (7, 7, 26, 24, 1), (10, 10, 20, 18, 1), SUMP, DRAIN],
    fluid=[(14, 14, 4, 4, 3, W)],                                            # 1.5 m standing water: LOW
    build=[("RM_PitRamp", 20, 33, 0, "WoodLog"),                            # D1 bench up to the rim (north)
           ("RM_LiquidTap", 17, 17, None, None),                            # groundwater bleeding in
           ("RM_LiquidPump", 13, 16, None, None), ("RM_HoseReel", 11, 16, None, None),
           ("PowerConduit", 13, 15, None, None), ("PowerConduit", 13, 14, None, None), ("Battery", 12, 12, 0, None),
           ("PowerConduit", 13, 13, None, None), ("PowerConduit", 12, 14, None, None),
           ("HandTailoringBench", 22, 12, 0, "WoodLog"),                    # the stake: on the D3 bench just above HIGH
           ("RM_PumpingStation_Wrecked", 36, 37, None, None)],
    spawn=[("RM_Ladder", 14, 16, None)],
    style=[("RM_HoseReel", 11, 16, "RM_HoseReel_Industrial")],
    batteries=[(12, 12)],
    pump=[(13, 16, "draw")],
    ladder_dev=[(14, 16, "lower")],
    hose=[(11, 16, 3, 36, None)],                                            # up the benches to the drain canal's head
    gizmos=[(11, 16, "Free end:", "Free end: Outflow")],
    markers=[("PlaceMeter", 16, 14, ""), ("PlaceMeter", 1, 36, ""), ("PlaceMeter", 10, 20, "")],
    pawns=[("Colonist", 12, 18, "player", "drafted")],
    pawn_ops=[(12, 18, "wear", "RM_ClimbingGear")],
    designate=[("RM_DigCanal", 15, 15, 1, 1)],                              # past the 2 m colonist cap: waits for a machine
)

SCENARIO = scenario(
    id="C4", n=4, slug="wet_quarry", name="The Wet Quarry", map="C", size=SIZE, look_style="Industrial",
    purpose="A quarry dug below the water table: the deeper it goes the more it floods; a pump rig keeps it workable. "
            "The dig ladder, rock vs soil, ways in and out, and pumping water up and away.",
    start="mark the drain-canal extension (Architect > Orders > Dig canal along the labelled strip) and unpause",
    try_=["START: designate the labelled 70-cell strip, unpause: a colonist digs it; about 1 in 70 dug tiles leaves a "
          "lump (a letter the first time); soil digs faster than rock and rock drops chunks",
          "the sump floor (3 m) carries a 'Dig canal' order: an undrafted colonist will not take it (2 m colonist cap, "
          "owner 2026-10-21; right-click says it needs machine labour) and the order stays for a machine",
          "stop the pump (the deliberate flood): the sump rises half a metre at a time from LOW toward HIGH and the "
          "workbench; the miner wades, then swims; restart it and the level falls",
          "raise the rail ladder from below, lower it from above (only from above); the geared miner climbs a sheer "
          "wall anyway",
          "walk a colonist down the ramp and the benches: lower with each step, never trapped"],
    look_for="dug ground never reads as a gravel path; dirt and rock walls drawn differently; the sump has visible "
             "depth; 0.5 m water reads as silt",
    broken="a dug tile reading as gravel path; dirt and stone walls alike; the sump a flat blue square; the miner "
           "standing ON water at 2 m; the ladder lowered from below",
    idle="the pump draws the sump through the hose to the drain canal, which runs off the map edge, against the bleed well's "
         "groundwater: the sump stays near LOW (the soak MEASURES whether this balance holds; the build fails if not); "
         "the miner is drafted; no dig is designated until he does it",
    setup=SETUP,
    edge_drain="west",
    fluid_moves=True,
    parts=[(13, 13, "LOW 1.5 m"), (13, 18, "HIGH 3 m (brim)"), (17, 18, "bleed well (groundwater)"), (12, 17, "pump (Draw)"),
           (10, 18, "reel: hose up and away"), (20, 35, "ramp"), (22, 14, "workbench (the stake)"),
           (12, 19, "miner (gear)"), (14, 19, "rail ladder"), (2, 37, "drain canal > west edge"),
           (16, 13, "meter sump"), (1, 35, "meter drain"), (10, 21, "meter bench"), (6, 2, "soil walls"),
           (30, 2, "rock walls"), (6, 38, "DIG STRIP: designate here (70 cells)"), (37, 39, "wrecked pumping station")],
    pieces=[staged("stepped benches D1 > D2 > D3", "dig", None, (8, 8)),
            staged("rock east / soil west", "terrain", "Granite_Rough", (20, 0), "look"),
            staged("machine-dug sump, 3 m, water at LOW", "fluid", W, (14, 14)),
            staged("groundwater bleed well into the sump", "build", "RM_LiquidTap", (17, 17)),
            staged("pump Drawing on the sump rim", "pump", "draw", (13, 16), "poked"),
            staged("hose up and away, free end Outflow", "gizmos", None, (11, 16), "poked"),
            staged("drain canal off the west edge", "dig", None, (-12, 36)),
            staged("three flow meters", "markers", "PlaceMeter", (16, 14)),
            staged("workbench just above HIGH", "build", "HandTailoringBench", (22, 12), "look"),
            staged("miner in climbing gear, drafted", "pawn_ops", "RM_ClimbingGear", (12, 18), "poked"),
            staged("rail ladder on the sump's west wall, lowered", "ladder_dev", "lower", (14, 16), "poked"),
            staged("ramp from the D1 bench to the rim", "build", "RM_PitRamp", (20, 33), "poked"),
            staged("wrecked pumping station on the rim", "build", "RM_PumpingStation_Wrecked", (36, 37), "look"),
            staged("a colonist refusing a dig past 2 m (the sump floor's order waits for a machine)", "designate",
                   "RM_DigCanal", (15, 15), "poked"),
            deferred("machine digging past 2 m (the sump)", "machine labour digs to 20 m (built 2026-10-21, "
                     "design/RimMandrake/machine_dig_2026-10-21.md); a colony Tunneler under a mechanitor is not staged "
                     "here yet, and the ridable digging rig is not built", DEEP_DIG_ITEM, (1, 3)),
            deferred("deepstone stratum finds", "unbuilt", "PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS", (37, 1))],
    exercises={"dig_canal": "poked", "dig_finds": "poked", "pit_ramp": "poked", "pit_pocket": "poked",
               "look_walls": "look", "look_pit": "look", "flow_drains": "demonstrated", "carry_industry": "look",
               "industry_stages_more": "look", "canal_reads_as_dug_channel": "look", "never_gravel_path": "look",
               "pit_depth_ladder_legible": "look", "pit_walls_have_visible_depth": "look",
               "pawn_lowers_on_deeper_cell": "poked", "pawn_rises_on_shallower_cell": "poked",
               "pawn_height_ladder_legible": "look", "half_metre_water_reads_as_silt": "poked",
               "geared_pawn_climbs_out": "poked", "climbing_gear_reads_as_kit": "look",
               "wall_ladder_rides_on_rails": "poked", "empty_reservoir_stops_flow": "poked"},
    goal="live: the sump's fill after the two-hour soak within one level of LOW (the pump and bleed well balance)",
)
