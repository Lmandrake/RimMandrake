"""C7 - The Bathhouse and Water Tower (map C, 40x40, look Modern): a desert colony's water, and water finds its level.

A well pump on a small pond fills an extra-tall cargo tank (the tower); a pipe brings it down to three ground tanks of
different sizes that are NOT yet joined (a two-cell gap he closes); a roofed bathhouse with a bath pit kept warm by a
liquid thermostat; a line of three bleed wells (hand-bled ground wells, NOT on the pipe beside them); the bad-water corner (brine -> fuelled still, salt -> sun-pan still) and a
drip filter for poisoned water; a gravity hose from the tower (no pump); four thirsty colonists and a prisoner.
Design §3 C7; GPT #4 (the every-container permutations went to the art wall).
"""
from .common import scenario, staged, deferred, perimeter, walls, OVERFLOW_ITEM

SIZE = (40, 40)
GAP = [(16, 26), (17, 26)]          # the two missing pipe cells between the ground tanks

SETUP = dict(
    terrain=[("WaterDeep", 0, 32, 5, 6)],
    dig=[(29, 31, 2, 3, 2)],                                                 # the bath pit, 1 m
    fluid=[(29, 31, 2, 3, 2, "RM_Fluid_Water")],
    roof=[("RoofConstructed", 27, 29, 10, 8)],
    build=[("RM_LiquidPump", 5, 34, None, None), ("RM_UniversalPipe", 6, 34, None, None),
           ("RM_UniversalPipe", 7, 34, None, None), ("RM_UniversalCargoTankXTall", 8, 33, None, None),
           ("PowerConduit", 5, 33, None, None), ("PowerConduit", 5, 32, None, None), ("Battery", 6, 30, 0, None),
           ("PowerConduit", 5, 31, None, None), ("PowerConduit", 6, 32, None, None)]
    + [("RM_UniversalPipe", 12, z, None, None) for z in range(26, 34)] + [("RM_UniversalPipe", x, 33, None, None) for x in (10, 11)]
    + [("RM_UniversalPipe", x, 26, None, None) for x in (13, 14, 15, 18, 19, 20, 21, 22, 23)]
    + [("RM_LiquidTank", 14, 24, None, None), ("RM_LiquidTankTall", 18, 24, None, None),
       ("RM_UniversalCargoTank", 22, 24, None, None)]
    + walls(perimeter(26, 28, 37, 37, gaps=[(31, 28)]), "Steel") + [("Door", 31, 28, None, "WoodLog"),
                                                                     ("RM_LiquidTap", 32, 32, None, None)]
    # three bleed wells (RM_LiquidTap: ground wells, off the pipe net) beside a pipe, an Empty-mode tank, bottles on a shelf.
    # LIQUID_TAP_RENAME_NOT_A_FAUCET (owner card 2026-10-22): nothing here is a faucet; a pipe-fed faucet is filed work.
    + [("RM_UniversalPipe", x, 18, None, None) for x in range(13, 25)]
    + [("RM_LiquidTap", x, 17, None, None) for x in (14, 17, 20)] + [("RM_LiquidTank", 24, 16, None, None),
                                                                    ("Shelf", 27, 17, 0, "WoodLog")]
    # bad-water corner
    + [("RM_LiquidTank", 2, 8, None, None), ("RM_UniversalPipe", 4, 8, None, None), ("RM_FueledStill", 6, 8, None, None),
       ("RM_UniversalPipe", 8, 8, None, None), ("RM_LiquidTank", 10, 8, None, None),
       ("RM_LiquidTank", 2, 2, None, None), ("RM_UniversalPipe", 4, 2, None, None), ("RM_SunPanStill", 6, 2, None, None),
       ("RM_DripFilter", 15, 3, None, None)]
    # the prisoner's cell (its own small room) and the gravity hose reel by the tower
    + walls(perimeter(30, 4, 36, 10, gaps=[(33, 4)]), "Steel") + [("Door", 33, 4, None, "WoodLog"),
                                                                   ("RM_HoseReel", 10, 36, None, None)],
    beds=[(33, 7, 0)],
    style=[("RM_UniversalCargoTankXTall", 8, 33, "RM_UniversalCargoTankXTall_Modern"),
           ("RM_LiquidTank", 14, 24, "RM_LiquidTank_Modern"), ("RM_LiquidTankTall", 18, 24, "RM_LiquidTankTall_Modern"),
           ("RM_UniversalCargoTank", 22, 24, "RM_UniversalCargoTank_Modern"), ("RM_HoseReel", 10, 36, "RM_HoseReel_Modern")],
    batteries=[(6, 30)],
    pump=[(5, 34, "draw")],
    tank=[(8, 33, "Store", "RM_Liquid_FreshWater", 32000), (14, 24, "Store", "RM_Liquid_FreshWater", 2000),
          (18, 24, "Store", "RM_Liquid_FreshWater", 10000), (22, 24, "Store", "RM_Liquid_FreshWater", 20000),
          (24, 16, "Empty", "RM_Liquid_FreshWater", 8000),
          (2, 8, "Store", "RM_Liquid_Brine", 8000), (2, 2, "Store", "RM_Liquid_SaltWater", 8000)],
    hose=[(10, 36, 26, 38, None)],                                          # to the garden corner; free end Capped
    items=[("RM_Bottle_FreshWater", 6, 27, 18), ("RM_Barrel_ToxicWater", 1, 13, 3)],
    markers=[("PlaceThermostat", 33, 34, "38|4")],
    pawns=[("Colonist", x, 12, "player", "drafted") for x in (14, 16, 18, 20)] + [("Pirate", 33, 6, "hostile", "prisoner")],
    pawn_ops=[(x, 12, "need", "RM_Thirst=0.2") for x in (14, 16, 18, 20)] + [(33, 6, "need", "RM_Thirst=0.3")],
    keep=True,
)

SCENARIO = scenario(
    id="C7", n=7, slug="bathhouse_tower", name="The Bathhouse and Water Tower", map="C", size=SIZE, look_style="Modern",
    purpose="A desert colony's water: a tower tank, gravity down to the ground tanks, a bathhouse, stills for bad water, thirsty "
            "colonists - and communicating vessels in plain sight.",
    start="undraft the four thirsty colonists and unpause",
    try_=["START: undraft the four, unpause: they drink at the tanks and from bottles; the warden carries water to the prisoner",
          "let them build the two missing pipe cells (or place them: Architect > FlowWorks > pipe on the marked gap): "
          "the three ground tanks move to ONE level, in decilitre steps",
          "set the tower reel's Free end to Outflow: the hose flows to the garden with no pump (gravity) and stops when "
          "the tower's level drops below the end",
          "run the stills: the fuelled one works day and night; the sun-pan stops at dusk and under a roof",
          "pour poisoned water into the drip filter: a slow, small clean drip"],
    look_for="pipes end at a tank's CENTRE; tanks on one net hold one level at rest; the bath reads as a bath, not a hole",
    broken="tanks on one net at different levels at rest; a gravity hose flowing uphill; brine drunk as water; the "
           "sun-pan working at night; pipes ending at a tank's edge; the bath pit reading as a hole",
    idle="the four colonists are drafted (drafted pawns do not drink); the ground tanks are not joined; the tower hose's "
         "end is Capped; the well pump draws the pond into the tower (the pond is limited, so it slows; the soak reads "
         "dug cells and buildings)",
    setup=SETUP,
    parts=[(9, 38, "tower (XTall)"), (2, 39, "well pond"), (16, 27, "GAP: 2 pipe cells"), (14, 23, "short"),
           (18, 23, "tall"), (22, 23, "cargo"), (31, 27, "bathhouse"), (30, 35, "bath"), (33, 35, "thermostat 38C"),
           (17, 15, "bleed wells (ground, off the pipe)"), (24, 15, "Empty tank"), (6, 11, "brine > fuelled still"),
           (6, 0, "salt > sun-pan"), (15, 6, "drip filter"), (33, 11, "prisoner"), (26, 39, "garden (hose end)"),
           (17, 10, "thirsty colonists (drafted)")],
    pieces=[staged("well pump, Drawing, powered", "pump", "draw", (5, 34)),
            staged("tower: XTall cargo tank, half full", "tank", "Store", (8, 33)),
            staged("three ground tanks, one per size, NOT joined", "build", "RM_LiquidTankTall", (18, 24), "poked"),
            staged("roofed bathhouse, bath pit filled", "fluid", "RM_Fluid_Water", (29, 31), "look"),
            staged("liquid thermostat keeps the bath warm", "markers", "PlaceThermostat", (33, 34)),
            staged("three bleed wells (ground wells, not on the pipe)", "build", "RM_LiquidTap", (14, 17), "poked"),
            staged("Empty-mode tank + bottles on a shelf", "tank", "Empty", (24, 16), "poked"),
            staged("brine tank > fuelled still > clean tank", "build", "RM_FueledStill", (6, 8), "poked"),
            staged("salt tank > sun-pan still", "build", "RM_SunPanStill", (6, 2), "poked"),
            staged("poisoned barrel + drip filter", "build", "RM_DripFilter", (15, 3), "poked"),
            staged("gravity hose from the tower, end Capped", "hose", None, (10, 36), "poked"),
            staged("four thirsty colonists (drafted)", "pawn_ops", "RM_Thirst=0.2", (14, 12), "poked"),
            staged("prisoner in his own cell", "pawns", "Pirate", (33, 6), "demonstrated"),
            deferred("a blueprint for the two missing pipe cells", "no script surface places a blueprint; the gap is "
                     "labelled and the pipe is his to place", "TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH", (37, 39)),
            deferred("the overflowing bath (D2/D4: leaking under the door)", "overflow Stage 1+ is unbuilt",
                     OVERFLOW_ITEM, (37, 26))],
    exercises={"carry_tanks": "poked", "tank_sizes": "look", "tank_styles": "look", "tank_modes": "poked",
               "carry_drills": "poked", "industry_stages_more": "look", "containers_all": "look", "carry_kits": "look",
               "carry_bottles": "poked", "tank_feeds_hose_without_pump": "poked", "pipe_meets_building_centre": "look",
               "never_tank_bridges_pipe_runs": "look", "still_water_one_surface_height": "poked",
               "reservoir_fill_visibly_drops": "demonstrated", "pipe_and_hose_one_net": "look"},
    goal="live: the three ground tanks read three different stocks before the gap is closed (ProofTank read)",
)
