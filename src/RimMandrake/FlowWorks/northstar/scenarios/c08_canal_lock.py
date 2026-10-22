"""C8 - The Canal Lock (map C, 44x24, look Futuristic): the level-solving scenario.

Two machine-dug 3 m canals at different water levels joined by a lock chamber with a sluice at each end, each sluice on
a timer; a swimmer in the chamber rides it up; three meters. Design §3 C8 after GPT #3 (3 m reaches, 2-3 m of water,
Mode A closed / Mode B through-flow, a chamber ladder, timer windows on the map's one clock).

Timer windows are set AFTER the build's two-hour soak (10:00-12:00) so the soak sees a still lock: S1 13:00-14:30,
S2 15:30-17:00. The level holder and the sink (Mode B) are NOT staged: the Place* surfaces build them switched on, and a
switched-off holder needs a toggle surface (owed C#).
"""
from .common import scenario, staged, deferred, W, DEEP_DIG_ITEM

SIZE = (44, 24)
UPPER = (2, 10, 16, 3, 6)
NECK1 = (18, 11, 1, 1, 6)
CHAMBER = (19, 10, 6, 3, 6)
NECK2 = (25, 11, 1, 1, 6)
LOWER = (26, 10, 16, 3, 6)
SHALLOWS = (26, 17, 12, 1, 2)       # a separate spur at 0.5 m: the silt look (not joined to anything)

SETUP = dict(
    dig=[UPPER, NECK1, CHAMBER, NECK2, LOWER, SHALLOWS],
    fluid=[(2, 10, 16, 3, 6, W), (18, 11, 1, 1, 6, W),                        # upper brim-full to S1
           (19, 10, 6, 3, 4, W), (25, 11, 1, 1, 4, W), (26, 10, 16, 3, 4, W),  # chamber and lower at 2 m
           (26, 17, 12, 1, 1, W)],
    spawn=[("RM_Sluice", 18, 11, "Steel"), ("RM_Sluice", 25, 11, "Steel"), ("RM_Ladder", 22, 12, None)],
    ladder_dev=[(22, 12, "lower")],
    markers=[("PlaceTimer", 18, 14, "hours|13|14.5|false|3"), ("PlaceTimer", 25, 14, "hours|15.5|17|false|3"),
             ("PlaceMeter", 10, 12, ""), ("PlaceMeter", 21, 10, ""), ("PlaceMeter", 33, 12, "")],
    pawns=[("Colonist", 20, 13, "player", "drafted")],
)

SCENARIO = scenario(
    id="C8", n=8, slug="canal_lock", name="The Canal Lock", map="C", size=SIZE, look_style="Futuristic",
    purpose="Two canals at different water levels, a lock chamber between two timed sluices, and a swimmer riding the "
            "lock up: one still surface per body, levels equalising only through open gates.",
    start="order the swimmer down the chamber ladder into the water, then unpause and wait for 13:00",
    try_=["START: order the swimmer (on the bank) into the chamber; unpause: at 13:00 the S1 timer opens S1; the chamber rises to the upper level and the swimmer rises "
          "with it; at 14:30 S1 shuts; at 15:30 S2 opens and the chamber falls to the lower level",
          "read the three meters as it happens: net in/out per day, levels held",
          "Mode A (closed): open both sluices by hand: the run settles to ONE surface",
          "Mode B (through-flow): DEFERRED (no switched-off holder/sink can be staged yet)",
          "the separate spur north of the lower canal: 0.5 m reads as silt-coloured shallows, not blue water"],
    look_for="gate state legible without selecting; one surface per body; the swimmer rises and falls with the chamber",
    broken="two levels on one side of an open gate; a gate drawn open while shut (or turning unlike a door); the "
           "swimmer standing on the floor; the timer firing at the wrong hours; meters disagreeing with what is drawn",
    idle="both sluices shut; timers first fire at 13:00 (after the 10:00-12:00 soak); the swimmer waits drafted on the BANK (two hours "
         "of swimming would tire him: swim exhaustion); a closed system",
    setup=SETUP,
    parts=[(18, 9, "S1"), (25, 9, "S2"), (9, 14, "upper 3 m water"), (21, 14, "chamber 2 m"), (33, 14, "lower 2 m"),
           (20, 15, "swimmer (bank)"), (22, 15, "chamber ladder"), (18, 16, "T1 13:00-14:30"), (25, 16, "T2 15:30-17:00"),
           (10, 9, "M1"), (21, 8, "M2"), (33, 9, "M3"), (31, 19, "0.5 m spur")],
    pieces=[staged("upper canal, 3 m machine-dug, brim-full", "fluid", W, (2, 10)),
            staged("lock chamber, 2 m water", "dig", None, (19, 10)),
            staged("lower canal, 2 m water", "dig", None, (26, 10)),
            staged("sluice S1", "spawn", "RM_Sluice", (18, 11), "poked"),
            staged("sluice S2", "spawn", "RM_Sluice", (25, 11), "poked"),
            staged("timer on S1", "markers", "PlaceTimer", (18, 14), "demonstrated"),
            staged("timer on S2", "markers", "PlaceTimer", (25, 14), "demonstrated"),
            staged("three meters", "markers", "PlaceMeter", (21, 10)),
            staged("swimmer on the chamber bank, drafted", "pawns", "Colonist", (20, 13), "poked"),
            staged("chamber ladder (the swimmer's exit)", "ladder_dev", "lower", (22, 12), "poked"),
            staged("0.5 m silt spur", "fluid", W, (26, 17), "look"),
            deferred("Mode B: level holder + sink switched off", "Place* builds them ON; an OFF-staged holder/sink "
                     "needs a toggle proof surface (owed C#)", "FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS", (41, 21)),
            deferred("a boat", "FlowWorks has none: the swimmer is the boat", "design §3 C8", (41, 18)),
            deferred("machine-dug 3 m reaches", "past the 2 m colonist cap; staged by the dig tool", DEEP_DIG_ITEM,
                     (41, 2))],
    exercises={"hold_gates": "poked", "look_sink": "look", "look_canal": "look", "flow_spreads": "poked",
               "still_water_one_surface_height": "poked", "sluice_gate_state_legible": "look",
               "depth_and_fill_jointly_legible": "look", "fill_tier_legible": "look",
               "canal_partial_fill_distinct": "look", "deep_water_pawn_swims": "demonstrated",
               "pawn_rises_on_shallower_cell": "demonstrated", "half_metre_water_reads_as_silt": "look"},
    goal="live: the timers read back 13-14.5 and 15.5-17 (static read); upper fill 6, chamber and lower fill 4",
    owed_cs=["a Place* 'off' flag (or a toggle proof) so a level holder and a sink can be staged switched OFF "
             "(C8 Mode B, idle-stable)"],
)
