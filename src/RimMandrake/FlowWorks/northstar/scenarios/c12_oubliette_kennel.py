"""C12 - The Oubliette and the Kennel (map C, 40x36, look Modern): pits hold, or do not.

A prison dug into the ground (wardens work from the lip), a covered cell a colonist will step onto, one animal yard
ringed by a 2 m trench (who leaves and how is the test), a thrumbo beside a 1x1 pit it cannot fit, and three ways in
and out of a pit: a portable ladder that fits, climbing gear in a deeper one, a jump-pack colonist at a lip.
Design §3 C12; GPT #4 (the kennel is ONE ringed yard, not a row of pens). No flyer here (never without the owner).
"""
from .common import scenario, staged, deferred, perimeter, DEEP_DIG_ITEM

SIZE = (40, 36)
OUB = (3, 22, 3, 4, 8)              # machine-dug 4 m, 3x4
COVERED = (10, 22, 3, 3, 4)         # 2 m: colonist depth
LADDER_PIT = (3, 4, 3, 3, 6)        # 3 m: the portable ladder's reach (portableLadderMaxLevels 6)
GEAR_PIT = (10, 4, 3, 3, 10)        # 5 m
JUMP_PIT = (17, 4, 3, 3, 6)
SHAFT = (35, 26, 1, 1, 8)           # the 1x1 the thrumbo cannot fit
RING = [(x, z) for x, z in perimeter(18, 18, 31, 31) + perimeter(19, 19, 30, 30)]
GUARD = [c for c in perimeter(2, 21, 6, 26) if c[0] != 6]   # the east lip carries the sluice and the grate

SETUP = dict(
    dig=[OUB, COVERED, LADDER_PIT, GEAR_PIT, JUMP_PIT, SHAFT,
         (6, 23, 1, 1, 4), (6, 25, 1, 1, 4),                      # the two door cells in the oubliette's east wall
         (7, 23, 6, 1, 2), (7, 25, 6, 1, 2)]                      # dry drain canals behind them
    + [(x, z, 1, 1, 4) for x, z in RING],                         # the kennel's 2 m trench ring, 2 wide
    beds=[(4, 23, 0)],
    spawn=[("RM_Ladder", 4, 25, None),                           # rail ladder on the oubliette's north wall
           ("RM_Sluice", 6, 23, "WoodLog"), ("RM_SecurityGrateDoor", 6, 25, "Steel"),
           ("RM_LadderPortable", 3, 5, None)]                    # portable ladder leaning on the west wall (3 m: fits)
    + [("RM_PitGuardrail", x, z, "Steel") for x, z in GUARD]
    + [("RM_PitCover_PlankLattice", 10 + i, 22 + j, None) for i in range(3) for j in range(3)],
    ladder_dev=[(4, 25, "raise")],
    pawns=[("Pirate", 4, 22, "hostile", "prisoner"),
           ("Colonist", 9, 21, "player", "drafted"),              # will be ordered onto the cover
           ("Chicken", 23, 23, "none", None), ("Husky", 25, 25, "none", None), ("Muffalo", 27, 27, "none", None),
           ("Colonist", 16, 24, "player", "drafted"),             # the handler at the ring
           ("Thrumbo", 35, 23, "none", None),
           ("Colonist", 5, 4, "player", "drafted"),               # in the ladder pit
           ("Colonist", 11, 5, "player", "drafted"),              # in the 5 m pit, climbing gear on
           ("Colonist", 16, 5, "player", "drafted")],             # at the third pit's lip, jump pack on
    pawn_ops=[(4, 22, "need", "Food=0.3"), (4, 22, "need", "RM_Thirst=0.25"),
              (11, 5, "wear", "RM_ClimbingGear"), (16, 5, "wear", "Apparel_PackJump")],
    keep=True,
)

SCENARIO = scenario(
    id="C12", n=12, slug="oubliette_kennel", name="The Oubliette and the Kennel", map="C", size=SIZE,
    look_style="Modern",
    purpose="What a pit holds, what climbs out, how wardens work from the lip, and every way in and out of a pit.",
    start="unpause: wardens go to the prisoner from the lip; the kennel beasts start testing the ring",
    try_=["START: unpause: wardens feed and water the prisoner from the lip; nobody climbs down",
          "oubliette: lower the rail ladder from ABOVE (only from above); raise it from below with the prisoner on it: "
          "stranded",
          "kennel: just watch: the chicken stays in the ring, the husky climbs out slowly, the muffalo steps across; "
          "the thrumbo walks round the 1x1 shaft",
          "order the colonist beside the concealed pit onto it: falls through, hurt",
          "jump the jump-pack colonist into the third pit: lands unhurt; undraft the geared one: climbs out of 5 m; "
          "undraft the ladder-pit one: climbs the portable ladder",
          "inspect a pit cell at noon and at midnight (dev advance; branch save _days): its temperature differs from the "
          "ground's (vanilla temperature only, no extra sun)"],
    look_for="a pit reads as a dark hole at its size; occupants drawn below the floor; raised vs lowered ladder "
             "legible; the guardrail keeps people off the lip",
    broken="a warden climbing down; the room not a prison; all three kennel beasts held, or all out; the thrumbo in "
           "the 1x1; the concealed pit visible at play zoom; a ladder lowered from below; the guardrail letting someone walk off",
    idle="every colonist drafted; the prisoner is in a sealed 4 m pit; the beasts are wild and roam INSIDE the ring "
         "(climbing out is the test, so the soak reads their KIND per plot, not their cell)",
    setup=SETUP,
    parts=[(4, 27, "oubliette 4 m (machine-dug)"), (4, 21, "prisoner"), (6, 22, "sluice"), (6, 26, "grate"),
           (11, 26, "concealed pit"), (24, 33, "kennel ring 2 m"), (16, 26, "handler"), (35, 28, "1x1 shaft"),
           (35, 21, "thrumbo"), (4, 8, "portable ladder 3 m"), (11, 8, "gear, 5 m"), (18, 8, "jump pack")],
    pieces=[staged("oubliette 3x4, 4 m, prisoner bed", "beds", None, (4, 23)),
            staged("prisoner, hungry-ish and thirsty", "pawn_ops", "RM_Thirst=0.25", (4, 22)),
            staged("rail ladder on the north wall, RAISED", "ladder_dev", "raise", (4, 25), "poked"),
            staged("guardrail round the lip", "spawn", "RM_PitGuardrail", (2, 21), "look"),
            staged("sluice (wood) in the east wall", "spawn", "RM_Sluice", (6, 23), "poked"),
            staged("security grate (steel) in the east wall", "spawn", "RM_SecurityGrateDoor", (6, 25), "poked"),
            staged("dry drain canals behind the doors", "dig", None, (7, 23), "look"),
            staged("concealed pit 3x3 (planks)", "spawn", "RM_PitCover_PlankLattice", (10, 22), "poked",
                   "plank lattice, not the design's reinforced frame: the frame should HOLD one colonist "
                   "(review_map pit_cover_drop), and this poke wants a fall"),
            staged("kennel ring, 2 m trench, 2 wide", "dig", None, (18, 18)),
            staged("chicken, husky, muffalo in the yard", "pawns", "Husky", (25, 25)),
            staged("drafted handler at the ring", "pawns", "Colonist", (16, 24)),
            staged("thrumbo beside a 1x1 sheer shaft", "pawns", "Thrumbo", (35, 23)),
            staged("portable ladder in a 3 m pit", "spawn", "RM_LadderPortable", (3, 5), "poked"),
            staged("climbing gear colonist in a 5 m pit", "pawn_ops", "RM_ClimbingGear", (11, 5), "poked"),
            staged("jump-pack colonist at a lip", "pawn_ops", "Apparel_PackJump", (16, 5), "poked"),
            deferred("flyers and floaters (pit travel)", "never live-tested without the owner (ruling 2026-09-19): "
                     "added only when he is at the keyboard", "FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT", (33, 2)),
            deferred("machine-digging the 3-5 m pits", "past the 2 m colonist cap; the pits are staged, a machine "
                     "dig order is not built", DEEP_DIG_ITEM, (36, 2))],
    exercises={"pit_holds": "demonstrated", "pit_width": "demonstrated", "pit_climb": "demonstrated",
               "pit_fall": "poked", "pit_ways_in": "poked", "hold_ladder": "poked", "hold_ladder_raised": "poked",
               "hold_prison": "demonstrated", "hold_exposure": "poked", "hold_gates": "poked", "look_pit": "look",
               "pit_cover": "poked", "pit_reads_as_hole": "look", "pit_not_vanilla_trap": "look",
               "never_reads_as_building": "look", "pit_reads_at_size": "look", "pit_occupied_distinguishable": "look",
               "pit_trapped_reads_as_trapped": "look", "pit_occupant_below_floor": "look",
               "ladder_state_legible": "look", "wall_ladder_rides_on_rails": "poked",
               "portable_ladder_leans_on_its_wall": "look", "climbing_gear_reads_as_kit": "look",
               "geared_pawn_climbs_out": "poked", "jump_into_pit_lands_unhurt": "poked",
               "pit_walls_have_visible_depth": "look"},
    goal="live: ProofLadder read on the oubliette ladder says raised; the prisoner's room reads as a prison",
    branch={"days": "RM_fw_composite_days: midnight for the pit-temperature read"},
)
