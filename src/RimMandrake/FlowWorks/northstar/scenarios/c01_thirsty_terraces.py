"""C1 - The Thirsty Terraces (map R, 48x40, all four looks in the sprinkler rows): grow a crop on dry ground above a
real river.

Map R: the plot is ANCHORED live on a straight south bank (river to the north: plot row z 39 is the bank, z 40 is
moving water) found by scenarios_map.river_bank_anchor() on the river site map (northstar/river_site.py); painted river
has no current, so this never goes on map C. Offline (--dry-run/--mock/selftest) the same finder runs on a synthetic
river.

Two separate nets (GPT #6): the CANAL feed (river -> intake channel behind sluice S0 -> terrace 1 -> S1 -> terrace 2 ->
S2 -> terrace 3) and the SPRINKLER circuit (bank pump -> pipe -> pole span over the dry ditch -> tall tank (Fill) ->
trunk -> four rows of heads, one per look). A labelled witness sprinkler.

Design deviation, stated: the design stages terrace 2 "part-filled with its front half way, held by S1 shut"; a canal
levels itself, so a half front cannot hold through the two-hour soak. Terrace 2 is staged DRY behind S1; opening S1 is
the Start that shows the front.
"""
from .common import scenario, staged, deferred, LOOKS, W, LPROOF, OVERFLOW_ITEM, GIRTH_NOTE

SIZE = (48, 40)
ROWS = [(30, "Scrapper"), (24, "Industrial"), (18, "Modern"), (12, "Futuristic")]

SETUP = dict(
    terrain=[("Sand", 2, 17, 26, 3)],                                         # terrace 3's sand strip
    dig=[(5, 34, 1, 6, 2),                                                    # intake: bank (z 39) down to terrace 1
         (2, 33, 25, 1, 2),                                                   # terrace 1 canal
         (27, 33, 1, 1, 2), (27, 28, 1, 5, 3), (2, 27, 26, 1, 3),             # S1, the drop, terrace 2
         (28, 27, 1, 1, 3), (28, 21, 1, 6, 2), (2, 21, 27, 1, 2),             # S2, the drop, terrace 3
         (34, 0, 2, 39, 2)],                                                  # the dry ditch the pole span crosses
    fluid=[(5, 34, 1, 5, 2, W), (2, 33, 25, 1, 2, W)],                        # intake and terrace 1 full; T2/T3 dry
    spawn=[("RM_Sluice", 5, 39, "WoodLog"), ("RM_Sluice", 27, 33, "WoodLog"), ("RM_Sluice", 28, 27, "WoodLog")],
    build=[("RM_BankWeir", 10, 39, 0, None),
           # C1_CORD_REWIRE_BATTERY_GOES_SKINNY_DIPPING: the battery sits inland and its conduit runs SOUTH from the bank pump,
           # so the GSS cord's slack bulges sideways over land, not north over the river (a run along the bank row did)
           ("RM_LiquidPump", 20, 39, None, None), ("PowerConduit", 19, 39, None, None), ("PowerConduit", 19, 38, None, None),
           ("PowerConduit", 19, 37, None, None), ("Battery", 19, 35, 0, None)]
    + [("RM_UniversalPipe", x, 38, None, None) for x in range(20, 32)]
    + [("RM_PipePole", 32, 38, None, None), ("RM_PipePole", 37, 38, None, None)]
    + [("RM_UniversalPipe", x, 38, None, None) for x in range(38, 44)]
    + [("RM_LiquidTankTall", 44, 37, None, None)]
    + [("RM_UniversalPipe", 46, z, None, None) for z in range(12, 38)]   # from the top sprinkler row (z 12) down: z 10-11 was a tail past its T into nothing
    + [("RM_UniversalPipe", x, z, None, None) for z, _ in ROWS for x in range(38, 46)]
    + [("RM_SprinklerHead", x, z, None, None) for z, _ in ROWS for x in (39, 41, 43)]
    + [("RM_Swale", 14, 19, None, None),
       ("RM_HoseReel", 2, 8, None, None), ("RM_HoseReel", 20, 14, None, None)],
    style=[("RM_BankWeir", 10, 39, "RM_BankWeir_Scrapper"), ("RM_HoseReel", 2, 8, "RM_HoseReel_Industrial")]
    + [("RM_UniversalPipe", x, z, "RM_UniversalPipe_" + lk) for z, lk in ROWS for x in range(38, 46)]
    + [("RM_SprinklerHead", x, z, "RM_SprinklerHead_" + lk) for z, lk in ROWS for x in (39, 41, 43)],
    spawn_plants=[("Plant_Rice", x, z) for x in range(2, 27) for z in (29, 30, 31)],
    batteries=[(19, 35)],
    pump=[(20, 39, "draw")],
    tank=[(44, 37, "Fill", "RM_Liquid_FreshWater", 12800)],
    hose=[(2, 8, 31, 8, None), (20, 14, 20, 1, None)],
    hose_flow=[(2, 8, "Plump"), (20, 14, "Plump")],
    calls=[dict(typ=LPROOF, method="ProofLinkPoles", fmt="{0};{1}", cells=[(32, 38), (37, 38)])],
    markers=[("PlaceMeter", 14, 33, "")],
)

SCENARIO = scenario(
    id="C1", n=1, slug="thirsty_terraces", name="The Thirsty Terraces", map="R", size=SIZE, look_style="all four",
    purpose="Grow a crop on dry ground three steps above a river: caught, lifted, carried over a ditch, stored, let down "
            "terrace by terrace, and sprayed. The field greens only if every link works.",
    start="open sluice S1 (terrace 1's tail)",
    try_=["START: open S1: terrace 2's front runs along it",
          "unpause an in-game hour: every sprinkler in all four rows sprays (the spray mote centred on its pipe); "
          "sprayed cells stay wet till the next spray - read the inspect pane and the crop's yield, NOT a ground tint "
          "(ruling 36: no irrigation line)",
          "open S2: the front runs along terrace 3; after days (branch save _days) the sand by the swale turns to soil",
          "switch the bank pump to Pour, OR (separately) cut its power: the sprinklers stop on the next hour; the "
          "remote hose goes flat",
          "select the meter on terrace 1: squares, levels held, net in/out per day; shut S1 and watch it turn",
          "deconstruct one pipe pole: the overhead span is gone and the pipe can no longer cross the ditch",
          "watch the labelled WITNESS sprinkler: the canal feed and the sprinkler circuit are separate nets"],
    look_for="sprinklers centred on their pipe; the pipe rises onto the tall tank's flange; the span sags over the ditch, "
             "not on its floor; the four looks working side by side; each reel's hose leaves the way the reel faces",
    broken="a sprinkler off its pipe's centre; spraying with no pump on the net; a pipe drawn through the tank or slipping under its skid; the "
           "overhead pipe on the ditch floor or without sag; terrace 3 wet with S2 shut; a hose crossing that is not "
           "clean over/under",
    idle="S0 shut (terrace 1 full), S1 and S2 shut (terraces 2 and 3 dry); the pump fills the tall tank in Fill mode "
         "and the heads spray on the hour (that IS the scenario; the soak reads dug cells and buildings)",
    setup=SETUP,
    anchor="south_bank",
    parts=[(10, 37, "weir"), (5, 37, "S0 intake"), (27, 35, "S1"), (28, 25, "S2"), (14, 35, "meter"),
           (21, 37, "bank pump (Draw)"), (34, 36, "pole span over the ditch"), (44, 35, "tall tank (Fill)"),
           (37, 31, "Scrapper"), (37, 25, "Industrial"), (37, 19, "Modern"), (37, 13, "Futuristic"),
           (43, 31, "WITNESS"), (14, 16, "swale on sand"), (2, 10, "remote field hose"), (21, 2, "crossing hose"),
           (12, 30, "crop")],
    pieces=[staged("weir on the bank (Scrapper)", "build", "RM_BankWeir", (10, 39), "look"),
            staged("intake channel behind S0", "spawn", "RM_Sluice", (5, 39)),
            staged("terrace 1 canal, full", "fluid", W, (2, 33)),
            staged("S1 at terrace 1's tail, shut", "spawn", "RM_Sluice", (27, 33), "poked"),
            staged("terrace 2 canal, dry", "dig", None, (2, 27), "poked"),
            staged("S2, shut; terrace 3 dry", "spawn", "RM_Sluice", (28, 27), "poked"),
            staged("crop rows between the terraces", "spawn_plants", "Plant_Rice", (2, 29), "look"),
            staged("bank pump Drawing, powered", "pump", "draw", (20, 39), "poked"),
            staged("pipe poles + overhead span over the dry ditch", "calls", "ProofLinkPoles", (32, 38), "poked"),
            staged("tall tank, Fill, about 40 %", "tank", "Fill", (44, 37)),
            staged("four sprinkler rows, one per look", "style", None, (39, 30), "look"),
            staged("flow meter on terrace 1", "markers", "PlaceMeter", (14, 33), "poked"),
            staged("sand + swale strip on terrace 3", "build", "RM_Swale", (14, 19), "poked"),
            staged("remote field hose (Industrial), Plump", "hose", None, (2, 8), "look"),
            staged("a second hose crossing it at right angles", "hose", None, (20, 14), "look"),
            deferred("overflow onto the field (D2/D3)", "overflow is built (Stages 1-3) but its master switch ships OFF and this scenario does not turn it on (C13 The Spill Yard does); terrace 1's brim is one notch from "
                     "spilling, so leaving S1 shut with the pump on will spill once the switch is on", OVERFLOW_ITEM, (31, 2)),
            deferred("joint fittings art (coupler, flange, saddle)", GIRTH_NOTE, "PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID", (31, 5)),
            deferred("terrace 2's front frozen half way", "a canal levels itself: no frozen half front survives the "
                     "soak; staged dry, opening S1 shows the front", "design §3 C1 (deviation)", (31, 11))],
    exercises={"flow_spreads": "poked", "look_canal": "look", "land_swale": "poked", "land_deepsand": "look",
               "pipe_styles": "look", "hose_grid": "look", "r_weir": "look",
               "canal_fill_spreads_along_itself": "poked", "canal_fill_front_watchable": "poked",
               "canal_reads_as_dug_channel": "look", "depth_and_fill_jointly_legible": "look",
               "pipe_and_hose_one_net": "look", "pipe_meets_building_centre": "look",
               "never_tank_bridges_pipe_runs": "look", "hose_far_end_pump_reaches_reel_tank": "poked",
               "hose_drawn_under_overhead_span": "look", "sluice_gate_state_legible": "look"},
    goal="live: ProofLinkPoles reads strung=True; the tall tank's stock rises over the soak (the pump is on the net)",
    branch={"days": "RM_fw_composite_rivers_days: sand to soil by the swale"},
)
