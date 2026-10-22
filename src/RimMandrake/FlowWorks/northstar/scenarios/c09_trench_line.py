"""C9 - The Trench Line (map C, 44x32, earthworks): dug ground as terrain - cover, movement cost, shooting from holes,
and what raiders do about trenches.

A zig-zag trench of waist (1 m) and chest (1.5 m) bays with three drafted colonists in the chest bays, one bay flooded
to 0.5 m (the wet foxhole), a tar ditch in front, a 4-wide titan gap at the south end, a stone rampart behind the north
end, and a raider pen 30 cells east behind a shut security grate. Hostiles live ONLY in the raid branch save
(RM_fw_composite_raid, design §2 / GPT #5): the main save holds the empty pen.
"""
from .common import scenario, staged, deferred, perimeter, walls, hline, TAR, W

SIZE = (44, 32)
BAYS = [((10 if k % 2 == 0 else 13), 2 + 4 * k, 3, 4, (2 if k % 2 == 0 else 3)) for k in range(7)]   # zig-zag
PEN = perimeter(36, 20, 42, 28, gaps=[(36, 24)])

SETUP = dict(
    dig=BAYS + [(28, 2, 2, 28, 1), (16, 0, 4, 6, 3)],                        # tar ditch; the titan gap (4 wide)
    fluid=[(28, 2, 2, 28, 1, TAR), (13, 22, 3, 4, 1, W)],                     # tar unlit; the wet chest bay at 0.5 m
    build=walls(hline(4, 16, 31), "BlocksGranite") + walls(PEN, "Steel"),
    spawn=[("RM_SecurityGrateDoor", 36, 24, "Steel")],
    pawns=[("Colonist", 14, 7, "player", "drafted"), ("Colonist", 14, 15, "player", "drafted"),
           ("Colonist", 14, 23, "player", "drafted")],
    pens=[("Pirate", 38, 22, "hostile"), ("Pirate", 40, 22, "hostile"), ("Pirate", 38, 25, "hostile"),
          ("Pirate", 40, 25, "hostile"), ("Pirate", 39, 27, "hostile"), ("Mech_CentipedeBlaster", 39, 21, "hostile")],
    pen_ops=[(38, 22, "wear", "RM_ClimbingGear")],
)

SCENARIO = scenario(
    id="C9", n=9, slug="trench_line", name="The Trench Line", map="C", size=SIZE, look_style="earthworks",
    purpose="A dry trench line facing an open field, the way a desert colony fights: cover, movement cost, shooting "
            "from holes, and what raiders do about trenches.",
    start="(raid branch save RM_fw_composite_raid) open the pen's grate and unpause",
    try_=["main save: hover a lane: walk cost climbs with depth; the wet bay is slower than a dry chest bay",
          "RAID BRANCH: hover a raider's shot at a colonist: the hit chance lists a 'trench wall' cover line, bigger "
          "for the chest-deep man",
          "RAID BRANCH START: open the pen grate, unpause: raiders cross the tar ditch (slow), hit the trench line, set "
          "a ladder or fill a cell to cross, and never shelter in a sheer pocket; the geared raider goes over the north "
          "rampart",
          "RAID BRANCH: light the tar ditch as they cross",
          "the large mechanoid must not step across the 4-wide titan gap"],
    look_for="a cover line on the hit chance, larger for chest than waist; raiders never trapped in a pocket",
    broken="no cover line, or the same for waist and chest; a raider stuck in a pocket; raiders walking over a trench "
           "as if flat; the large pawn stepping across the 4-wide gap; the wet bay no slower",
    idle="main save: no hostiles; colonists drafted in the bays; the tar unlit. Raid branch: the pen's shut grate is "
         "proven by the build's two-hour soak with the raiders inside",
    setup=SETUP,
    parts=[(39, 30, "raider pen (raid branch)"), (36, 26, "grate"), (29, 31, "tar ditch (unlit)"),
           (11, 0, "waist 1 m"), (14, 4, "chest 1.5 m"), (14, 26, "wet bay 0.5 m"), (18, 7, "titan gap 4 wide"),
           (10, 30, "stone rampart")],
    pieces=[staged("zig-zag trench, waist and chest bays", "dig", None, (10, 2)),
            staged("three colonists in the chest bays, drafted", "pawns", "Colonist", (14, 7)),
            staged("wet foxhole bay at 0.5 m", "fluid", W, (13, 22), "look"),
            staged("tar ditch, 2 wide, unlit", "fluid", TAR, (28, 2), "poked"),
            staged("4-wide titan gap", "dig", None, (16, 0), "poked"),
            staged("stone rampart behind the north end", "build", "Wall", (4, 31), "poked"),
            staged("raider pen behind a shut security grate", "spawn", "RM_SecurityGrateDoor", (36, 24), "poked"),
            staged("six raiders incl. one with climbing gear (raid branch)", "pens", "Pirate", (38, 22), "poked"),
            staged("a large mechanoid (raid branch)", "pens", "Mech_CentipedeBlaster", (39, 21), "poked",
                   "a vanilla centipede stands in for titan size"),
            deferred("wet foxhole: cold feet, shaky aim", "unbuilt; the wet bay is placed so it shows once built",
                     "WET_FOXHOLE_BUILD_COLD_FEET_SHAKY_AIM", (24, 30)),
            deferred("defenders holding fire until drafted", "no bridge surface sets fire-at-will off: owed", "owed C#",
                     (24, 27)),
            deferred("raider ladder / fill-in rows proven live", "raid_trench_proof A2-A7 L2 rows must pass first, else "
                     "he sees known failures (design §5.3)", "RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP", (24, 24))],
    exercises={"dig_slows": "poked", "pit_shooting": "poked", "look_sink": "look", "flow_identity": "look",
               "trench_wall_cover_shown": "poked", "raiders_never_shelter_in_a_cage": "poked",
               "canal_dry_reads_as_obstacle": "poked", "filled_excavation_reads_as_obstacle": "poked",
               "pawn_lowers_on_deeper_cell": "look", "never_snared_standing": "poked",
               "geared_pawn_scales_built_wall": "poked"},
    goal="live (raid branch): ProofTrenchCover on a chest-bay colonist vs a penned raider returns trench > 0",
    branch={"raid": "RM_fw_composite_raid: the six raiders and the mechanoid in the pen, grate shut"},
    owed_cs=["a fire-at-will/hold-fire bridge surface so raid-branch defenders hold fire until drafted (C2, C9)"],
)
