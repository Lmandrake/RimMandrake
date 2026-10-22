"""C7 - The Bathhouse and Water Tower (map C, 40x40, look Modern): a desert colony's water, and water finds its level.

A well pump on a small pond fills an extra-tall cargo tank (the tower); three ground tanks of different sizes stand
apart (a size look: tanks in Store mode never level with each other -- storage fill stays pump-only, GSS ruling 3);
two dug ponds at different levels joined by one hose net (two reels on a pipe, a hose into each pond): the low pond's
hose end is Capped, and opening it lets water find its level (PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL A4); a roofed bathhouse with a bath pit kept warm by a
liquid thermostat; a line of three bleed wells (hand-bled ground wells, NOT on the pipe beside them); the bad-water corner (brine -> fuelled still, salt -> sun-pan still) and a
drip filter for poisoned water; a gravity hose from the tower (no pump); four thirsty colonists and a prisoner.
Design §3 C7; GPT #4 (the every-container permutations went to the art wall).
"""
from .common import scenario, staged, deferred, perimeter, walls, OVERFLOW_ITEM

SIZE = (40, 40)
# Water finds its level (owner card 2026-10-21, item PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL): two dug ponds, 2 m deep,
# HIGH full (4 notches) and LOW at 1 notch, each with a hose free end on its lip; the two reels are joined by a pipe (x=11,
# between them), no pump. The LOW end is Capped (idle-stable); setting it to Outflow is the poke that starts the levelling.
# Reels stand 6 squares east of the lips: a hose needs ~4.4 squares of straight lead-out (live 2026-10-22: 4 squares was
# refused "no room for the straight lead-out from the nozzle").
POND_HIGH, POND_LOW = (1, 22, 4, 4), (1, 14, 4, 4)
REEL_HIGH, REEL_LOW = (11, 22), (11, 15)
END_HIGH, END_LOW = (5, 22), (5, 15)
LPROOF = "RimMandrake.FlowWorks.Machinery.RM_LineProofs"

SETUP = dict(
    terrain=[("WaterDeep", 0, 32, 5, 6)],
    dig=[(29, 31, 2, 3, 2), POND_HIGH + (4,), POND_LOW + (4,)],              # the bath pit, 1 m; the two ponds, 2 m
    fluid=[(29, 31, 2, 3, 2, "RM_Fluid_Water"), POND_HIGH + (4, "RM_Fluid_Water"), POND_LOW + (1, "RM_Fluid_Water")],
    roof=[("RoofConstructed", 27, 29, 10, 8)],
    build=[("RM_LiquidPump", 5, 34, None, None), ("RM_UniversalPipe", 6, 34, None, None),
           ("RM_UniversalPipe", 7, 34, None, None), ("RM_UniversalCargoTankXTall", 8, 33, None, None),
           ("PowerConduit", 5, 33, None, None), ("PowerConduit", 5, 32, None, None), ("Battery", 6, 30, 0, None),
           ("PowerConduit", 5, 31, None, None), ("PowerConduit", 6, 32, None, None)]
    + [("RM_LiquidTank", 14, 24, None, None), ("RM_LiquidTankTall", 18, 24, None, None),
       ("RM_UniversalCargoTank", 22, 24, None, None)]
    + [("RM_HoseReel", REEL_HIGH[0], REEL_HIGH[1], None, None), ("RM_HoseReel", REEL_LOW[0], REEL_LOW[1], None, None)]
    + [("RM_UniversalPipe", 11, z, None, None) for z in range(REEL_LOW[1] + 1, REEL_HIGH[1])]
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
           ("RM_UniversalCargoTank", 22, 24, "RM_UniversalCargoTank_Modern"), ("RM_HoseReel", 10, 36, "RM_HoseReel_Modern"),
           ("RM_HoseReel", REEL_HIGH[0], REEL_HIGH[1], "RM_HoseReel_Modern"), ("RM_HoseReel", REEL_LOW[0], REEL_LOW[1], "RM_HoseReel_Modern")],
    batteries=[(6, 30)],
    pump=[(5, 34, "draw")],
    tank=[(8, 33, "Store", "RM_Liquid_FreshWater", 32000), (14, 24, "Store", "RM_Liquid_FreshWater", 2000),
          (18, 24, "Store", "RM_Liquid_FreshWater", 10000), (22, 24, "Store", "RM_Liquid_FreshWater", 20000),
          (24, 16, "Empty", "RM_Liquid_FreshWater", 8000),
          (2, 8, "Store", "RM_Liquid_Brine", 8000), (2, 2, "Store", "RM_Liquid_SaltWater", 8000)],
    hose=[(10, 36, 26, 38, None),                                           # to the garden corner; free end Capped
          REEL_HIGH + END_HIGH + (None,), REEL_LOW + END_LOW + (None,)],     # the ponds' hoses (the 5th field is the end LOOK)
    # free-end ROLES (RM_LineProofs.ProofHoseRole; a hose's role is not a lay field): HIGH open, LOW Capped until his poke.
    # Live 2026-10-22: with both open, 10,000 dL moved per 250-tick cycle, the reels reading "Levelling: flowing".
    calls=[dict(typ=LPROOF, method="ProofHoseRole", fmt="{0};Outflow", cells=[REEL_HIGH]),
           dict(typ=LPROOF, method="ProofHoseRole", fmt="{0};Capped", cells=[REEL_LOW])],
    items=[("RM_Bottle_FreshWater", 6, 27, 18), ("RM_Barrel_ToxicWater", 1, 13, 3)],
    markers=[("PlaceThermostat", 33, 34, "38|4")],
    pawns=[("Colonist", x, 12, "player", "drafted") for x in (14, 16, 18, 20)] + [("Pirate", 33, 6, "hostile", "prisoner")],
    pawn_ops=[(x, 12, "need", "RM_Thirst=0.2") for x in (14, 16, 18, 20)] + [(33, 6, "need", "RM_Thirst=0.3")],
    keep=True,
)

SCENARIO = scenario(
    id="C7", n=7, slug="bathhouse_tower", name="The Bathhouse and Water Tower", map="C", size=SIZE, look_style="Modern",
    purpose="A desert colony's water: a tower tank, a bathhouse, stills for bad water, thirsty colonists - and water finding "
            "its level between two ponds joined by a hose, no pump.",
    start="undraft the four thirsty colonists and unpause",
    try_=["START: undraft the four, unpause: they drink at the tanks and from bottles; the warden carries water to the prisoner",
          "set the LOW pond's hose reel Free end to Outflow: water runs from the full pond to the low one through the hose, "
          "no pump, in decilitre steps, until both stand at one level (the reel reads 'Levelling: flowing', then 'level'). "
          "The three ground tanks do NOT level with each other: storage fill stays pump-only (GSS ruling 3)",
          "set the tower reel's Free end to Outflow: the hose flows to the garden with no pump (gravity) and stops when "
          "the tower's level drops below the end",
          "run the stills: the fuelled one works day and night; the sun-pan stops at dusk and under a roof",
          "pour poisoned water into the drip filter: a slow, small clean drip"],
    look_for="a pipe rises onto a tank's flange (never under its skid); two ponds joined by an open hose end at one level; "
             "the bath reads as a bath, not a hole",
    broken="two ponds joined by open hose ends still at different levels after an hour; a gravity hose flowing uphill; brine drunk as water; the "
           "sun-pan working at night; a pipe slipping under a tank's skid; the bath pit reading as a hole",
    idle="the four colonists are drafted (drafted pawns do not drink); the LOW pond's hose end is Capped; the tower hose's "
         "end is Capped; the well pump draws the pond into the tower (the pond is limited, so it slows; the soak reads "
         "dug cells and buildings)",
    setup=SETUP,
    parts=[(9, 38, "tower (XTall)"), (2, 39, "well pond"), (1, 27, "HIGH pond (full)"), (1, 19, "LOW pond: cap open = levels"),
           (12, 20, "one hose net, no pump"), (14, 23, "short"),
           (18, 23, "tall"), (22, 23, "cargo"), (31, 27, "bathhouse"), (30, 35, "bath"), (33, 35, "thermostat 38C"),
           (17, 15, "bleed wells (ground, off the pipe)"), (24, 15, "Empty tank"), (6, 11, "brine > fuelled still"),
           (6, 0, "salt > sun-pan"), (15, 6, "drip filter"), (33, 11, "prisoner"), (26, 39, "garden (hose end)"),
           (17, 10, "thirsty colonists (drafted)")],
    pieces=[staged("well pump, Drawing, powered", "pump", "draw", (5, 34)),
            staged("tower: XTall cargo tank, half full", "tank", "Store", (8, 33)),
            staged("three ground tanks, one per size (a size look; Store tanks never level)", "build", "RM_LiquidTankTall",
                   (18, 24), "look"),
            staged("two ponds at different levels, one hose net, LOW end Capped", "hose", None, REEL_LOW, "poked"),
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
            deferred("the overflowing bath (D2/D4: leaking under the door)", "overflow is built (Stages 1-3) but its master switch ships OFF and this scenario does not turn it on (C13 The Spill Yard does)",
                     OVERFLOW_ITEM, (37, 26))],
    exercises={"carry_tanks": "poked", "tank_sizes": "look", "tank_styles": "look", "tank_modes": "poked",
               "carry_drills": "poked", "industry_stages_more": "look", "containers_all": "look", "carry_kits": "look",
               "carry_bottles": "poked", "tank_feeds_hose_without_pump": "poked", "pipe_meets_building_centre": "look",
               "never_tank_bridges_pipe_runs": "look", "still_water_one_surface_height": "poked",
               "reservoir_fill_visibly_drops": "demonstrated", "pipe_and_hose_one_net": "look"},
    goal="live: the two ponds read different water before the LOW end is opened (ProofPitWater read)",
)
