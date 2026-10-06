"""review_map.py -- the FlowWorks human review MAP: a walkable quicktest map, not a browser sheet (owner, 2026-10-05).

    python.exe src/RimMandrake/FlowWorks/review_map.py --build --fresh-map [--only visuals|gallery] | tr -d '\\r'
    python.exe src/RimMandrake/FlowWorks/review_map.py --goto N | tr -d '\\r'   # N = station; V = visuals block;
                                                       # S0 = status board; M = art board; F = free area
    python.exe src/RimMandrake/FlowWorks/review_map.py --labels | tr -d '\\r'   # re-pin labels after a load
    python.exe src/RimMandrake/FlowWorks/review_map.py --clear | tr -d '\\r'
    python.exe src/RimMandrake/FlowWorks/review_map.py --save [--name RM_fw_review_YYYYMMDD] | tr -d '\\r'
    python3    src/RimMandrake/FlowWorks/review_map.py --plan            # offline: layout check + key sheet only

Owner, 2026-10-05 (typed): *"We should wire up a review MAP for me rather than a review sheet, in the style of Give
Me Some Slack review maps."* and, same day: *"stop making that review sheet in the browser for the pits. I need to see
it in the game."* So the VISUALS block (pits D1..D4 x dirt/stone x dry/water/tar/scorched, plus oil and slime; data:
review_map_stations_visuals.json, built by review_map_visuals.station_ops) is built and verified FIRST; the feature
gallery follows.

Copies the GimmeSomeSlack pattern (src/RimMandrake/GimmeSomeSlack/human_review.py): one quicktest map on the flowworks
tier; calm world (weather Clear locked, clock pinned noon, incident queue cleared, Peaceful, non-colonists swept,
research finished, god mode ON, game PAUSED, screenshot mode OFF); labelled stations by jawa/review_label (labels are
process memory: --labels re-pins them after a load); a FREE AREA round the quicktest colonists with material stacks;
idempotent --build (clears its rects first, filling dug cells back in); --save writes the keeper with the before/after
Saves stat (modcheck/reviewmap.save_keeper).

STATUS IS DATA, NEVER TYPED: every gallery station is one FEATURE of the FlowWorks feature sheet (human_review.py
FEATURES, 8 sections) and its status (Works in game / Built, not yet seen / Partly built / Not built) comes from that
sheet's own feature_status() over its capability table, read at build/plan time. A NOT BUILT feature gets a placeholder
pad that says so. Setups (what is built in each station) are code: SETUPS below. Mod Settings stay at shipped defaults.
"""
import argparse
import html
import importlib.util
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)
from modcheck import reviewmap as RM  # noqa: E402
import review_map_visuals as VIS  # noqa: E402

OUT = os.path.join(HERE, "northstar", "review", "map")       # under northstar/: not in the mod hash, DEPLOY_HOLD'd
TAG = "fw_review"
MAP_SIZE = 250
SW, SH = 16, 14                     # a gallery station's footprint
PITCH_X, PITCH_Z = 22, 21           # 6 / 7 cells between stations: labels sit in the gap, liquids never join
GX0, GZ0 = 52, 4                    # gallery grid origin (columns x 52..244)
NCOL = 9
VIS_BASE = (10, 6)                  # visuals block: 4 columns x 9 rows of 6x5 plots, pitch 8 x 7 -> x 10..41, z 6..68
VIS_RECT = (VIS_BASE[0] - 2, VIS_BASE[1] - 2, 4 * (VIS.PLOT_W + VIS.GAP) + 2, 9 * (VIS.PLOT_H + VIS.GAP) + 4)
FREE = dict(rect=(96, 108, 52, 26),   # round the quicktest colonists (they stand near 125,125)
            stock=[("Steel", 75, (98 + i, 109)) for i in range(6)] + [("ComponentIndustrial", 25, (105, 109)),
                   ("ComponentIndustrial", 25, (106, 109)), ("WoodLog", 75, (108, 109)), ("WoodLog", 75, (109, 109)),
                   ("WoodLog", 75, (110, 109)), ("BlocksGranite", 75, (112, 109)), ("BlocksGranite", 75, (113, 109)),
                   ("Chemfuel", 75, (115, 109)), ("Chemfuel", 75, (116, 109)), ("RM_Bottle_FreshWater", 10, (118, 109)),
                   ("RM_Bottle_Tar", 10, (119, 109)), ("RM_BottleEmpty", 20, (120, 109)), ("RM_BucketEmpty", 10, (121, 109)),
                   ("RM_BarrelEmpty", 5, (122, 109))],
            pond=("WaterDeep", 138, 110, 6, 5))
BOARD = dict(rect=(8, 108, 36, 22))         # S0 status board (labels only), west of the free area
ART = dict(rect=(8, 86, 36, 14))            # M  art board (labels only)
STATUS_WORD = {"works": "WORKS IN GAME", "built": "BUILT, NOT YET SEEN", "partly": "PARTLY BUILT", "not": "NOT BUILT YET"}
GOLD, CREAM, TEAL, RUST = "#ffd27f", "#f2e6cf", "#8fd3c7", "#ff9a6b"


# ------------------------------------------------------------------------------------------------ the data layer
def feature_sheet():
    """The FlowWorks feature sheet module (human_review.py), loaded under its own name (GSS has a human_review too)."""
    sp = importlib.util.spec_from_file_location("fw_feature_sheet", os.path.join(HERE, "human_review.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def derive(m=None, rows=None):
    """-> (m, {feature_id: status}, capd). Statuses from the sheet's own derivation: probes + newest live result."""
    m = m or feature_sheet()
    if rows is None:
        _, rows = m.latest_result()
    capd = {c["id"]: dict(c, d=m.derive_status(c, rows)) for c in m.CAPS}
    st = {f["id"]: m.feature_status(f, capd)[0] for f in m.FEATURES}
    return m, st, capd


def sentence(title, say):
    """The feature's designer sentence plus its plain line, as two sentences."""
    t = title.strip()
    if say:
        t = (t if t.endswith((".", "!", "?")) else t + ".") + " " + say.strip()
    return t


def missing_parts(m, f, capd):
    return [m.PLAIN.get(c, capd[c]["label"]) for c in f["caps"] + f.get("minor", [])
            if capd[c]["d"]["status"] in ("NOT BUILT", "PARTIAL")]


# ------------------------------------------------------------------------------------------------ station setups
# Local cells (x 0..15, z 0..13, north up). Vocabulary:
#   terrain [(Def, x, z, w, h)]        painted first (ponds are sources: deep liquid terrain)
#   dig     [(x, z, w, h, D)]          flowworks_excavation_drive deepenLevels=D
#   fluid   [(x, z, w, h, F, FluidDef)] RM_FluidIdentityProof.ProofFillWithFluid (named fluid, no-mix enforced)
#   build   [(Def, x, z, rot, stuff)]  jawa/build_batch, player
#   spawn   [(Def, x, z, stuff)]       jawa/spawn_batch (ladders, spikes, covers, doors: as the extension suite does)
#   items   [(Def, n, x, z)]           rimworld/spawn_thing
#   pawns   [(kind, x, z, faction, role)]  role: "drafted" (stands still), "prisoner", None
#   beds    [(x, z, rot)]              a wooden bed made a PRISONER bed
#   roof    [(RoofDef, x, z, w, h)]    designate [(DesignationDef, x, z, w, h)]    marks [(x, z, text)]
# A station whose feature is NOT BUILT gets only a concrete placeholder pad + its label (build() adds it).
W, T = "RM_Fluid_Water", "RM_Fluid_Tar"


def _pit(x, z, w=3, h=3):
    return (x, z, w, h, 4)


SETUPS = {
    # ---- 1 digging
    "dig_canal": dict(short="Dig a canal, dig deeper", notice="four depths side by side, D1 to D4; the right one is a pit",
                      dig=[(1, 2, 2, 8, 1), (5, 2, 2, 8, 2), (9, 2, 2, 8, 3), (13, 2, 2, 8, 4)],
                      designate=[("RM_DigCanal", 1, 11, 6, 1)],
                      marks=[(2, 1, "D1"), (6, 1, "D2"), (10, 1, "D3"), (14, 1, "D4")],
                      try_=["unpause: a colonist digs the marked strip (top left)",
                            "Architect > Orders > Dig canal on a dug strip: it goes one level deeper; a D4 strip refuses"]),
    "dig_fill_in": dict(short="Fill a canal back in", notice="a water canal with a fill-in order on its east end",
                        terrain=[("WaterDeep", 0, 5, 3, 4)], dig=[(3, 6, 12, 2, 2)], fluid=[(3, 6, 12, 2, 1, W)],
                        designate=[("RM_FillInCanal", 11, 6, 3, 2)],
                        try_=["unpause: a colonist fills the marked cells and their water moves back along the canal, "
                              "not deleted"]),
    "dig_slows": dict(short="Trenches slow people down", notice="dry lanes D1, D2, D3, a pit row D4, and a flooded D2 lane",
                      dig=[(1, 1, 14, 1, 1), (1, 3, 14, 1, 2), (1, 5, 14, 1, 3), (1, 7, 14, 1, 4), (1, 10, 14, 1, 2)],
                      fluid=[(1, 10, 14, 1, 2, W)],
                      marks=[(0, 1, "D1"), (0, 3, "D2"), (0, 5, "D3"), (0, 7, "pit"), (0, 10, "wet")],
                      try_=["hover a lane: the walk cost climbs with depth; the wet lane is slower than the dry D2",
                            "order a colonist across: he goes round the pit row"]),
    "dig_finds": dict(short="Digging turns up minerals", notice="a dig order 14 cells long, waiting for a colonist",
                      designate=[("RM_DigCanal", 1, 6, 14, 1)],
                      try_=["unpause: about 1 in 70 dug tiles leaves a lump on the bank, with a letter the first time"]),
    # ---- 2 flow
    "flow_drains": dict(short="A canal off the map edge drains", notice="the lower canal runs off the map edge and stays "
                        "empty; the upper one ends inside the map and holds its water",
                        terrain=[("WaterDeep", 9, 4, 3, 6)], dig=[(-GX0, 5, GX0 + 9, 1, 2), (1, 9, 8, 1, 2)],
                        west_edge=True, try_=["unpause: the lower canal keeps pouring away off the edge"]),
    "flow_spreads": dict(short="Liquid spreads along the canal", notice="one pond, a canal branching three ways, all filled",
                         terrain=[("WaterDeep", 0, 5, 3, 4)], dig=[(3, 6, 12, 1, 2), (8, 7, 1, 6, 2), (8, 1, 1, 5, 2)],
                         try_=["dig a new cell onto any end: next pulse it fills", "unpause: it moves in pulses, not every tick"]),
    "flow_identity": dict(short="Tar crawls, water runs", notice="same canal, same pulses: the water canal (top) is full, "
                          "the tar canal (bottom) has crawled a few cells",
                          terrain=[("WaterDeep", 0, 9, 3, 4), ("RM_TarDeep", 0, 1, 3, 4)],
                          dig=[(3, 10, 12, 1, 2), (3, 2, 12, 1, 2)],
                          try_=["unpause and watch the tar front creep"]),
    "flow_no_mix": dict(short="Liquids never mix", notice="water from the west, tar from the east: the fronts meet and stop",
                        terrain=[("WaterDeep", 0, 5, 3, 4), ("RM_TarDeep", 13, 5, 3, 4)], dig=[(3, 6, 10, 1, 2)],
                        try_=["fill in a water cell: the tar moves in"]),
    "flow_ponds": dict(short="A small pond runs dry", notice="a 2x2 pond feeding a long canal: it fills about 20 cells, "
                       "then stops (5 canal cells per pond cell)",
                       terrain=[("WaterDeep", 0, 5, 2, 2)], dig=[(2, 5, 14, 1, 2), (15, 6, 1, 3, 2), (1, 9, 15, 1, 2)],
                       try_=["the far end stays dry: the pond has paid out", "a lake touching the map edge never runs out"]),
    "flow_shrinks": dict(short="A pond shrinks as it pays out", notice="a 4x4 pond feeding a long canal: its edge cells "
                         "turn to shallow then mud as it is drawn down",
                         terrain=[("WaterDeep", 0, 4, 4, 4)], dig=[(4, 5, 12, 1, 2), (15, 6, 1, 6, 2), (6, 11, 9, 1, 2)],
                         try_=["unpause through rain: it slowly refills"]),
    "flow_rain": dict(short="Rain fills open trenches", notice="two dry trenches; the right one is roofed",
                      dig=[(1, 3, 5, 6, 2), (9, 3, 5, 6, 2)], roof=[("RoofConstructed", 9, 3, 5, 6)],
                      try_=["dev: Change weather > Rain, unpause: the open trench fills, the roofed one stays dry"]),
    "flow_canyon": dict(short="Canyon floods run through canals", notice="a dry canal waiting for a canyon flood",
                        dig=[(1, 6, 14, 1, 2)], try_=["dev: start a canyon flood upstream: it runs down the canal"]),
    "flow_slime": dict(short="Slime is nearly uncrossable", notice=""),
    # ---- 3 fire
    "fire_lights": dict(short="Fire lights tar", notice="a tar pond and its canal; the mark is where to drop a fire",
                        terrain=[("RM_TarDeep", 0, 5, 3, 4)], dig=[(3, 6, 12, 1, 2)], marks=[(14, 8, "light here")],
                        try_=["dev: Spawn fire (or an explosion) at the mark: the flame runs back along the canal",
                              "nothing lights? 'Liquid ignition' ships OFF in Mod Settings > FlowWorks"]),
    "fire_lasts": dict(short="A burning canal burns for days", notice="a long tar canal back to its pond",
                       terrain=[("RM_TarDeep", 0, 5, 4, 4)], dig=[(4, 6, 12, 1, 2), (15, 7, 1, 5, 2)],
                       marks=[(15, 12, "light here")],
                       try_=["light the far end, unpause: about one canal level a day, and it spreads back into the pond"]),
    "fire_out": dict(short="Foam or rain puts it out", notice="a tar canal with a firefoam popper beside it",
                     terrain=[("RM_TarDeep", 0, 5, 3, 4)], dig=[(3, 6, 12, 1, 2)],
                     build=[("FirefoamPopper", 9, 8, None, None)], marks=[(13, 8, "light here")],
                     try_=["light it, then trigger the popper: foamed cells stop burning while the foam lies there"]),
    # ---- 4 catching
    "pit_holds": dict(short="Nothing climbs out of a pit", notice="a muffalo in a 3x3 pit",
                      dig=[_pit(6, 5)], pawns=[("Muffalo", 7, 6, "none", None)], keep=True,
                      try_=["unpause: it walks the floor and never climbs out; its info line says trapped"]),
    "pit_width": dict(short="A pit only holds what fits", notice="a muffalo in a 1-wide slot (too narrow) and a hare in "
                      "a 1x1 pit",
                      dig=[(3, 4, 1, 5, 4), (11, 6, 1, 1, 4)], pawns=[("Muffalo", 3, 6, "none", None),
                                                                     ("Hare", 11, 6, "none", None)], keep=True,
                      try_=["unpause: the muffalo walks out, the hare stays"]),
    "pit_fall": dict(short="Falling in hurts", notice="a pit and one of your colonists beside it",
                     dig=[_pit(6, 5)], pawns=[("Colonist", 4, 6, "player", "drafted")],
                     try_=["order him into the pit: he is hurt by the fall, and (shipped default) climbs back out"]),
    "pit_shooting": dict(short="Shots only from the pit's edge", notice="a boar in a pit; your colonist stands 6 cells off",
                         dig=[_pit(9, 5)], pawns=[("WildBoar", 10, 6, "none", None), ("Colonist", 3, 6, "player", "drafted")],
                         keep=True, try_=["order an attack on the boar: he walks to the lip before he can shoot"]),
    "pit_ways_in": dict(short="Jump in on purpose", notice="a pit and a colonist beside it",
                        dig=[_pit(6, 5)], pawns=[("Colonist", 4, 6, "player", "drafted")],
                        try_=["select him: 'Jump into pit' drops him in, and he is stuck there too"]),
    "pit_cover": dict(short="A cover hides the hole", notice="left: a covered pit; right: the same pit uncovered",
                      dig=[_pit(2, 5), _pit(10, 5)],
                      spawn=[("RM_PitCover_PlankLattice", 2 + i, 5 + j, None) for i in range(3) for j in range(3)],
                      try_=["zoom in close on the left one: only a faint seam shows"]),
    "pit_cover_drop": dict(short="Step on a cover, fall through", notice="three covered pits: plank lattice, woven scrap, "
                           "reinforced frame",
                           dig=[_pit(1, 5), _pit(6, 5), _pit(11, 5)],
                           spawn=[(d, ox + i, 5 + j, None) for d, ox in (("RM_PitCover_PlankLattice", 1),
                                  ("RM_PitCover_WovenScrap", 6), ("RM_PitCover_ReinforcedFrame", 11))
                                  for i in range(3) for j in range(3)],
                           marks=[(2, 4, "plank"), (7, 4, "scrap"), (12, 4, "frame")],
                           try_=["order a colonist across each: the weaker covers give way"]),
    "pit_spikes": dict(short="Spikes at the bottom", notice="a pit floored with spikes",
                       dig=[_pit(6, 5)], spawn=[("RM_Spikes", 6 + i, 5 + j, None) for i in range(3) for j in range(3)],
                       try_=["walking up to the spikes is harmless; only a fall in triggers them"]),
    "pit_flood": dict(short="Flood an occupied pit", notice="a boar in a pit, a water canal behind a shut sluice",
                      terrain=[("WaterDeep", 0, 5, 3, 3)], dig=[(3, 6, 5, 1, 2), (8, 6, 1, 1, 2), _pit(9, 5)],
                      spawn=[("RM_Sluice", 8, 6, "WoodLog")], pawns=[("WildBoar", 10, 6, "none", None)], keep=True,
                      try_=["open the sluice (select it): water pours into the pit"]),
    # ---- 5 holding
    "hold_ladder": dict(short="A ladder in and out", notice="a pit with a ladder on its west wall and a colonist in it",
                        dig=[_pit(6, 5)], spawn=[("RM_Ladder", 6, 6, None)],
                        pawns=[("Colonist", 7, 6, "player", "drafted")],
                        try_=["select the ladder: raise it and he is stranded; lower it and he climbs out"]),
    "hold_prison": dict(short="A pit prison, run from the lip", notice="a 3x4 pit with a prisoner bed and a prisoner",
                        dig=[(6, 5, 3, 4, 4)], beds=[(7, 7, 0)], pawns=[("Pirate", 6, 5, "hostile", "prisoner")], keep=True,
                        try_=["wardens feed and talk to him from the lip; nobody climbs down"]),
    "hold_exposure": dict(short="Sun and cold wear him down", notice="an open pit with a prisoner, noon sun on it",
                          dig=[_pit(6, 5)], beds=[(7, 6, 0)], pawns=[("Pirate", 6, 5, "hostile", "prisoner")], keep=True,
                          try_=["inspect a pit cell: hotter than the ground by day, colder by night"]),
    "hold_gates": dict(short="Sluice and grate doors", notice="a pit with a sluice (wood) and a security grate (steel) "
                       "in its wall; a hare and a prisoner inside",
                       terrain=[("WaterDeep", 0, 5, 3, 4)], dig=[(3, 6, 4, 1, 2), (7, 6, 1, 1, 2), (7, 8, 1, 1, 2),
                                                               (3, 8, 4, 1, 2), (8, 5, 4, 5, 4)],
                       spawn=[("RM_Sluice", 7, 6, "WoodLog"), ("RM_SecurityGrateDoor", 7, 8, "Steel")],
                       pawns=[("Hare", 10, 6, "none", None), ("Pirate", 10, 8, "hostile", "prisoner")], keep=True,
                       try_=["open either door: liquid flows through, nobody inside can open it"]),
    # ---- 6 looks
    "look_sink": dict(short="People sink as the ground deepens", notice="one colonist standing at each depth D1..D4",
                      dig=[(1, 5, 3, 3, 1), (5, 5, 3, 3, 2), (9, 5, 3, 3, 3), (13, 5, 3, 3, 4)],
                      pawns=[("Colonist", 2, 6, "player", "drafted"), ("Colonist", 6, 6, "player", "drafted"),
                             ("Colonist", 10, 6, "player", "drafted"), ("Colonist", 14, 6, "player", "drafted")],
                      marks=[(2, 4, "D1"), (6, 4, "D2"), (10, 4, "D3"), (14, 4, "D4")],
                      try_=["undraft one and order it out: it rises step by step"]),
    "look_canal": dict(short="A canal looks dug and shows how full", notice="D2 cells: empty, trace, half, brim; and a "
                       "brimming pit",
                       dig=[(1, 5, 2, 3, 2), (4, 5, 2, 3, 2), (7, 5, 2, 3, 2), (10, 5, 2, 3, 2), (13, 5, 3, 3, 4)],
                       fluid=[(4, 5, 2, 3, 1, W), (7, 5, 2, 3, 1, W), (10, 5, 2, 3, 2, W), (13, 5, 3, 3, 4, W)],
                       marks=[(1, 4, "empty"), (4, 4, "low"), (7, 4, "half"), (10, 4, "brim"), (14, 4, "pit")]),
    "look_pit": dict(short="A pit reads as one dark hole", notice="two 4x4 pits: empty (left) and occupied (right)",
                     dig=[(1, 5, 4, 4, 4), (10, 5, 4, 4, 4)], pawns=[("Muffalo", 11, 6, "none", None)], keep=True),
    "look_parts": dict(short="Spikes, ladder, gates: own drawings", notice="a ladder, spikes, a sluice and a grate on dug "
                       "ground, side by side",
                       dig=[(2, 6, 1, 1, 4), (5, 6, 1, 1, 4), (8, 6, 1, 1, 2), (11, 6, 1, 1, 2)],
                       spawn=[("RM_Ladder", 2, 6, None), ("RM_Spikes", 5, 6, None), ("RM_Sluice", 8, 6, "WoodLog"),
                              ("RM_SecurityGrateDoor", 11, 6, "Steel")],
                       marks=[(2, 4, "ladder"), (5, 4, "spikes"), (8, 4, "sluice"), (11, 4, "grate")]),
    "look_liquids": dict(short="Tar and slime look thick", notice="a tar pond and canal (left), a slime pond (right)",
                         terrain=[("RM_TarDeep", 0, 5, 3, 4), ("RM_SlimeGreenDeep", 10, 5, 4, 4)], dig=[(3, 6, 6, 1, 2)]),
    "look_fire": dict(short="Burning liquid looks alight", notice="a tar canal to light, and a scorched-dry pit beside it",
                      terrain=[("RM_TarDeep", 0, 5, 3, 3)], dig=[(3, 6, 6, 1, 2), (11, 5, 3, 3, 3)],
                      scorch=[(11, 5, 3, 3)], marks=[(8, 8, "light here")]),
    # ---- 7 carry
    "carry_bottles": dict(short="Bottles, buckets, barrels", notice="empty, full and dirty bottles, a bucket and a barrel "
                          "by a pond and a tank",
                          terrain=[("WaterDeep", 0, 5, 3, 4)], build=[("RM_LiquidTank", 10, 6, None, None)],
                          items=[("RM_BottleEmpty", 5, 4, 6), ("RM_Bottle_FreshWater", 5, 5, 6), ("RM_BottleDirty", 3, 6, 6),
                                 ("RM_BucketEmpty", 2, 7, 6), ("RM_BarrelEmpty", 1, 8, 6), ("RM_Bottle_Tar", 2, 4, 8)],
                          try_=["unpause: colonists fill bottles at the shore or the tank and wash dirty ones"]),
    "carry_tanks": dict(short="Tanks, pumps, hoses", notice="a pump on the pond shore piped to a tank, powered by a battery",
                        terrain=[("WaterDeep", 0, 5, 3, 4)],
                        build=[("RM_LiquidPump", 3, 6, None, None), ("RM_LiquidTank", 8, 6, None, None),
                               ("RM_UniversalCargoTank", 12, 6, None, None), ("Battery", 4, 9, 0, None),
                               ("PowerConduit", 3, 7, None, None), ("PowerConduit", 3, 8, None, None),
                               ("PowerConduit", 3, 9, None, None)],
                        try_=["unpause: the pump draws the pond down into the tank"]),
    "carry_drills": dict(short="Drills, taps and stills", notice="a liquid drill, a tap, a fuelled still, a sun-pan still "
                         "and a drip filter",
                         build=[("RM_LiquidDrill", 1, 6, None, None), ("RM_LiquidTap", 5, 6, None, None),
                                ("RM_FueledStill", 7, 6, None, None), ("RM_SunPanStill", 10, 6, None, None),
                                ("RM_DripFilter", 13, 6, None, None)],
                         marks=[(1, 4, "drill"), (5, 4, "tap"), (7, 4, "still"), (10, 4, "sun pan"), (13, 4, "filter")]),
    "carry_industry": dict(short="Ruined liquid works", notice="a wrecked desalination plant, a kludged tar refinery, a "
                           "repaired pumping station",
                           build=[("RM_DesalPlant_Wrecked", 1, 6, None, None), ("RM_TarRefinery_Kludged", 6, 6, None, None),
                                  ("RM_PumpingStation_Repaired", 11, 6, None, None)],
                           try_=["select the wreck: repair it in stages; none are on the build menu in the campaign"]),
    # ---- 8 land
    "land_liquids": dict(short="Many liquids as ground", notice="brine, boiling water, propane, acid, tar, red slime",
                         terrain=[("RM_WaterBrineDeep", 0, 7, 4, 4), ("RM_WaterBoilingDeep", 6, 7, 4, 4),
                                  ("RM_PropaneDeep", 12, 7, 4, 4), ("RM_AcidDeep", 0, 1, 4, 4), ("RM_TarDeep", 6, 1, 4, 4),
                                  ("RM_SlimeRedDeep", 12, 1, 4, 4)],
                         marks=[(2, 11, "brine"), (8, 11, "boiling"), (14, 11, "propane"), (2, 5, "acid"),
                                (8, 5, "tar"), (14, 5, "red slime")]),
    "land_shores": dict(short="Liquid shores on new maps", notice="shores come only on newly generated maps; here a "
                        "boiling pool for the steam", terrain=[("RM_WaterBoilingShallow", 3, 4, 10, 6)]),
    "land_swale": dict(short="A swale turns sand to soil", notice="a swale on sand beside a water canal",
                       terrain=[("Sand", 0, 0, 16, 14), ("WaterDeep", 0, 6, 3, 3)], dig=[(3, 7, 12, 1, 2)],
                       build=[("RM_Swale", 8, 9, None, None)],
                       try_=["unpause for days: the sand beside the swale slowly turns to soil"]),
    "land_panning": dict(short="Panning and the sluice box", notice=""),
    "land_settings": dict(short="Every mechanic has a switch", notice="nothing to see here: open Options > Mod Settings > "
                          "FlowWorks", try_=["switch everything off: the mod still digs dry canals"]),
}

# The river works (owner list: weir, stake-line/levee, silt trap, fish catch, ferry rope, ford, drift/breach). Stake-line
# and levee are one build (the stakeLineLevee setting), so 7 stations. Status = feature_status over the listed caps.
RIVER = [("WaterMovingShallow", 0, 3, 16, 2), ("WaterMovingChestDeep", 0, 5, 16, 4), ("WaterMovingShallow", 0, 9, 16, 2)]
RIVERS = [
    dict(id="river_ford", caps=["L09"], short="Ford stones", notice="a shallow river with a line of ford stones across",
         terrain=[("WaterMovingShallow", 0, 3, 16, 8), ("RM_FordStones", 7, 3, 1, 8)],
         try_=["on a real river the current carries people; on ford stones it does not"]),
    dict(id="river_weir", caps=["L10"], short="A weir", notice="a weir on the bank edge, its slack pool upstream",
         terrain=RIVER, build=[("RM_BankWeir", 7, 11, None, None)], try_=["select the weir: its pool and catch"]),
    dict(id="river_stakes", caps=["L11"], short="Stake-line levee", notice="a line of bank stakes with one gap",
         terrain=RIVER, build=[("RM_BankStake", x, 11, None, None) for x in range(1, 15) if x != 8],
         try_=["a seasonal flood does not spread past the stakes, only through the gap"]),
    dict(id="river_silt", caps=["L11"], short="Silt trap", notice="a silt trap on the bank",
         terrain=RIVER, build=[("RM_SiltTrap", 7, 11, None, None)], try_=["over time the ground beside it richens"]),
    dict(id="river_fish", caps=["L10", "L13"], short="Fish catch", notice="a weir that catches fish and drift",
         terrain=RIVER, build=[("RM_BankWeir", 4, 11, None, None)], try_=["unpause: fish and drift gather at the weir"]),
    dict(id="river_ferry", caps=["L13"], short="Ferry rope", notice="ferry posts on both banks, the rope strung between",
         terrain=RIVER, build=[("RM_FerryPost", 7, 2, None, None), ("RM_FerryPost", 7, 11, None, None)],
         try_=["undrafted colonists cross on the rope instead of being swept"]),
    dict(id="river_breach", caps=["L12", "L13"], short="Drift and breach", notice="an untended weir: in a flood it breaches "
         "and washes its catch away", terrain=RIVER, build=[("RM_BankWeir", 7, 11, None, None)],
         try_=["dev: start a flood: the weir breaches"]),
]
for _r in RIVERS:
    SETUPS[_r["id"]] = _r

# Gallery order: rows top to bottom; each row = one or two sections. flow_drains first in its row (it needs the
# map's west edge). land_rivers is shown as the RIVERS stations.
ROWS = [
    ("dig+fire", ["dig", "fire"]),
    ("flow", ["flow"]),
    ("catch", ["catch"]),
    ("hold+carry", ["hold", "carry"]),
    ("look", ["look"]),
    ("land", ["land"]),
    ("rivers", ["rivers"]),
]
FIRST = {"flow_drains"}
RESERVED = [FREE["rect"]]


def feature_order(m):
    by = {}
    for f in m.FEATURES:
        if f["id"] == "land_rivers":
            continue
        by.setdefault(f["s"], []).append(f["id"])
    by["flow"] = [i for i in by["flow"] if i in FIRST] + [i for i in by["flow"] if i not in FIRST]
    by["rivers"] = [r["id"] for r in RIVERS]
    return by


def _overlap(a, b, pad=0):
    return not (a[0] + a[2] + pad <= b[0] or b[0] + b[2] + pad <= a[0] or a[1] + a[3] + pad <= b[1] or b[1] + b[3] + pad <= a[1])


def station_list(m=None, st=None, capd=None):
    """[station dict] in number order. Station = feature (or river work) + setup + derived status + origin."""
    if st is None:
        m, st, capd = derive(m)
    feats = {f["id"]: f for f in m.FEATURES}
    by = feature_order(m)
    sec_name = dict(m.SECTIONS)
    sec_name["rivers"] = "8 · Rivers: the bank works"
    S = []
    n = 0
    j = 0
    for rname, secs in ROWS:
        ids = [(s, i) for s in secs for i in by.get(s, [])]
        i = 0
        while ids:
            x, z = GX0 + PITCH_X * i, GZ0 + PITCH_Z * (len(ROWS) + 3 - j)
            rect = (x, z, SW, SH)
            if i >= NCOL:
                j += 1
                i = 0
                continue
            if any(_overlap(rect, r, 2) for r in RESERVED + [VIS_RECT]):
                i += 1
                continue
            sec, fid = ids.pop(0)
            n += 1
            setup = SETUPS.get(fid, {})
            if fid in feats:
                f = feats[fid]
                status = st[fid]
                title = f["title"]
                say = f.get("say", "")
                missing = missing_parts(m, f, capd)
            else:                                   # a river work: its own caps through the same derivation
                fake = dict(caps=setup["caps"])
                status = m.feature_status(fake, capd)[0]
                title = setup["short"]
                say = ""
                missing = [m.PLAIN.get(c, capd[c]["label"]) for c in setup["caps"]
                           if capd[c]["d"]["status"] in ("NOT BUILT", "PARTIAL")]
            S.append(dict(n=n, id=fid, section=sec, section_name=sec_name.get(sec, sec), row=rname, origin=(x, z),
                          size=(SW, SH), status=status, title=title, say=say, missing=missing,
                          short=setup.get("short", fid), notice=setup.get("notice", ""), try_=setup.get("try_", []),
                          setup=setup, placeholder=(status == "not")))
            i += 1
        j += 1
    return S


# ------------------------------------------------------------------------------------------------ visuals block
def visuals_doc():
    p = os.path.join(HERE, "review_map_stations_visuals.json")
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf-8"))


def visuals_status(st, state):
    return st.get({"dry": "look_pit", "scorched": "look_fire"}.get(state, "look_liquids"), "partly")


def vis_label(v):
    s = v["setup"]
    return "D%d %s %s" % (s["pit"]["depth"], s["ground_kind"], v["id"].split("_")[1])


# ------------------------------------------------------------------------------------------------ layout check
def layout_check(S, doc=None):
    """No overlaps (pitch >= footprint + margin), everything on the map, every station labelled with a status and a
    what-to-notice line, setups inside their footprint (except a declared map-edge canal)."""
    probs = []
    if PITCH_X < SW + 4 or PITCH_Z < SH + 4:
        probs.append("pitch %dx%d < station %dx%d + 4" % (PITCH_X, PITCH_Z, SW, SH))
    rects = [("%d" % s["n"],) + tuple(s["origin"]) + tuple(s["size"]) for s in S]
    rects += [("F",) + tuple(FREE["rect"]), ("S0",) + tuple(BOARD["rect"]), ("M",) + tuple(ART["rect"]),
              ("V",) + tuple(VIS_RECT)]
    for i in range(len(rects)):
        a = rects[i]
        if a[1] < 0 or a[2] < 0 or a[1] + a[3] > MAP_SIZE or a[2] + a[4] > MAP_SIZE - 3:
            probs.append("%s off the map (or no room for its label): %s" % (a[0], a[1:]))
        for b in rects[i + 1:]:
            if _overlap(a[1:], b[1:], 4):
                probs.append("%s and %s closer than 4 cells" % (a[0], b[0]))
    if [s["n"] for s in S] != list(range(1, len(S) + 1)):
        probs.append("station numbers not 1..N")
    for s in S:
        if s["status"] not in STATUS_WORD:
            probs.append("station %d: status %r" % (s["n"], s["status"]))
        if not s["placeholder"] and not s["notice"]:
            probs.append("station %d (%s): no what-to-notice line" % (s["n"], s["id"]))
        if not s["setup"]:
            probs.append("station %d (%s): no setup" % (s["n"], s["id"]))
        u = s["setup"]
        cells = []
        for k in ("terrain", "dig", "fluid", "roof", "designate"):
            for r in u.get(k, []):
                rr = r[1:5] if isinstance(r[0], str) else r[:4]
                cells += [(rr[0], rr[1]), (rr[0] + rr[2] - 1, rr[1] + rr[3] - 1)]
        for k in ("build", "spawn"):
            cells += [(r[1], r[2]) for r in u.get(k, [])]
        cells += [(r[2], r[3]) for r in u.get("items", [])] + [(r[1], r[2]) for r in u.get("pawns", [])]
        cells += [(r[0], r[1]) for r in u.get("beds", [])] + [(r[0], r[1]) for r in u.get("marks", [])]
        for c in cells:
            if not (0 <= c[1] < SH and (0 <= c[0] < SW or (u.get("west_edge") and c[0] < SW))):
                probs.append("station %d (%s): cell %s outside its %dx%d footprint" % (s["n"], s["id"], c, SW, SH))
            if s["origin"][0] + c[0] < 0:
                probs.append("station %d: cell %s off the map" % (s["n"], c))
        if u.get("west_edge") and s["origin"][0] + min(r[0] for r in u["dig"]) != 0:
            probs.append("station %d: the drain canal does not reach the map edge" % s["n"])
    for k, s in enumerate(S):
        for t in S[k + 1:]:
            if s["setup"].get("west_edge") and t["origin"][1] == s["origin"][1] and t["origin"][0] < s["origin"][0]:
                probs.append("station %d sits on station %d's drain canal" % (t["n"], s["n"]))
    if doc:
        for v in doc["stations"]:
            ox, oz = VIS.origin_of(v, *VIS_BASE)
            if not (VIS_RECT[0] <= ox and ox + VIS.PLOT_W <= VIS_RECT[0] + VIS_RECT[2] and VIS_RECT[1] <= oz
                    and oz + VIS.PLOT_H <= VIS_RECT[1] + VIS_RECT[3]):
                probs.append("visuals %s outside the V block" % v["id"])
            if not v.get("what_to_notice"):
                probs.append("visuals %s: no what-to-notice line" % v["id"])
    return probs


# ------------------------------------------------------------------------------------------------ labels
def wrap(text, width):
    out, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return out + ([cur] if cur else [])


def label_ops(S, st, doc, m=None):
    L = []

    def add(x, z, text, sub="", col=GOLD, size="medium"):
        L.append(RM.label_line(x, z, text, sub, col, size, TAG))
    m = m or feature_sheet()
    col = {k: m.F_COLOR[k] for k in m.F_ORDER}
    vx, vz, vw, vh = VIS_RECT
    add(vx + vw // 2, vz + vh + 1, "V  FLOWWORKS PITS: WHAT THEY LOOK LIKE",
        "columns: depth D1 to D4   |   rows: dry, water, tar, scorched (soil then granite), top row oil + slime   |   "
        "--goto V", CREAM)
    if doc:
        for v in doc["stations"]:
            ox, oz = VIS.origin_of(v, *VIS_BASE)
            stt = visuals_status(st, v["id"].split("_")[1])
            add(ox + 3, oz + 5, vis_label(v), "", col[stt], "tiny")
    else:
        add(vx + vw // 2, vz + vh // 2, "VISUALS PENDING", "review_map_stations_visuals.json not found", RUST)
    rows_seen = {}
    for s in S:
        rows_seen.setdefault(s["row"], s)
    for rname, first in rows_seen.items():
        secs = sorted({s["section_name"] for s in S if s["row"] == rname}, key=lambda t: t)
        nums = [s["n"] for s in S if s["row"] == rname]
        add(GX0 - 7, first["origin"][1] + SH + 3, "   +   ".join(x.upper() for x in secs),
            "stations %d-%d" % (min(nums), max(nums)), TEAL, "small")
    for s in S:
        x, z = s["origin"]
        # title + status above the station; the what-to-notice line below it (tiny): one line each never runs into the
        # neighbouring station's label (live look 2026-10-05: a 170-char sub line overran three stations)
        add(x + SW // 2, z + SH + 1, "%d  %s" % (s["n"], s["short"]), STATUS_WORD[s["status"]], col[s["status"]], "small")
        low = ("NOT BUILT yet: " + (s["say"] or s["title"])) if s["placeholder"] else s["notice"]
        if low:
            for k, part in enumerate(wrap(low, 46)[:3]):
                add(x + SW // 2, z - 1 - k, part, "", CREAM, "tiny")
        for dx, dz, text in s["setup"].get("marks", []):
            add(x + dx, z + dz, text, "", RUST, "tiny")
    fx, fz, fw, fh = FREE["rect"]
    add(fx + fw // 2, fz + fh + 1, "F  FREE AREA", "steel, components, wood, granite, chemfuel, bottles (south edge); a pond "
        "(east). Architect > Orders: Dig canal / Fill in canal; Structure: ladder, spikes, covers, doors", RUST)
    bx, bz, bw, bh = BOARD["rect"]
    tot = {k: sum(1 for s in S if s["status"] == k) for k in STATUS_WORD}
    add(bx + bw // 2, bz + bh, "S0  FLOWWORKS: WHAT EXISTS, WHAT WORKS", "%d stations: %s" % (
        len(S), "   ".join("%d %s" % (tot[k], STATUS_WORD[k].lower()) for k in STATUS_WORD)), CREAM)
    secs = []
    for s in S:
        if s["section_name"] not in secs:
            secs.append(s["section_name"])
    for i, name in enumerate(secs):
        ss = [s for s in S if s["section_name"] == name]
        add(bx + bw // 2, bz + bh - 2 - 2 * i, name, "   ".join("%d %s" % (sum(1 for s in ss if s["status"] == k),
                                                                  STATUS_WORD[k].lower()) for k in STATUS_WORD
                                                 if any(s["status"] == k for s in ss)), CREAM, "small")
    ax, az, aw, ah = ART["rect"]
    art = [s for s in S if s["section"] == "look" and s["missing"]]
    add(ax + aw // 2, az + ah, "M  STILL DRAWN WITH BORROWED OR MISSING ART", "from the feature sheet's own status", RUST)
    for i, s in enumerate(art[:6]):
        add(ax + aw // 2, az + ah - 2 - 2 * i, "%d %s" % (s["n"], s["short"]), "; ".join(s["missing"])[:160], CREAM, "small")
    return "\n".join(L)


# ------------------------------------------------------------------------------------------------ live build
class Review(object):
    def __init__(self, B, log=None):
        self.B, self.log = B, log
        self.notes, self.verify, self.pawn_ids = [], {}, {}

    def say(self, msg):
        ln = "%s %s" % (time.strftime("%H:%M:%S"), msg)
        print(ln, flush=True)
        if self.log:
            with open(self.log, "a", encoding="utf-8") as f:
                f.write("- " + ln + "\n")

    def call(self, tool, **kw):
        r = self.B.call(tool, **kw)
        if not isinstance(r, dict) or r.get("success") is False:
            self.notes.append("%s %s refused: %s" % (tool, json.dumps(kw)[:120], json.dumps(r)[:200]))
        return r if isinstance(r, dict) else {}

    def fresh_map(self):
        B = self.B
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        for _ in range(480):
            if B.call("rimworld/get_ui_state").get("programState") == "Playing" and B.call("jawa/map_info").get("success"):
                return True
            time.sleep(0.5)
        raise SystemExit("no fresh map")

    def calm(self):
        B = self.B
        mi = B.call("jawa/map_info")
        if mi.get("sizeX") != MAP_SIZE:
            raise SystemExit("expected a %dx%d quicktest map, got %s" % (MAP_SIZE, MAP_SIZE, mi.get("sizeX")))
        self.call("jawa/weather_set", weather="Clear", lockWeather=True)
        clk = B.call("jawa/time_clock")
        lon = mi.get("longitude")
        if isinstance(clk.get("ticksAbs"), int) and isinstance(lon, (int, float)):
            local = (clk["ticksAbs"] + int(round(lon / 360.0 * 60000))) % 60000
            add = (12 * 2500 - local) % 60000
            if add:
                self.call("jawa/time_set_ticks", ticks=clk["ticksGame"] + add)
        self.call("jawa/incident_queue_clear")
        self.peaceful = B.call("jawa/storyteller_swap", difficultyDef="Peaceful").get("success")
        self.sweep()
        self.call("jawa/research_bulk", mode="finish_all")
        self.call("rimworld/set_god_mode", enabled=True)
        self.call("jawa/screenshot_mode", enabled=False)

    def sweep(self, keep=()):
        r = RM.sweep_pawns(self.B, keep)
        if r.get("removed"):
            self.notes.append("swept %s non-colonist pawn(s) (kept %s held on purpose)" % (r["removed"], r.get("kept")))
        return r

    def rects(self, S, doc, only):
        out = []
        if only in (None, "visuals"):
            out.append(VIS_RECT)
        if only in (None, "gallery"):
            out += [(s["origin"][0] - 2, s["origin"][1] - 1, SW + 4, SH + 3) for s in S]
            for s in S:
                if s["setup"].get("west_edge"):
                    out.append((0, s["origin"][1], s["origin"][0], SH))
        return out

    def clear(self, S, doc, only=None):
        """Wipe our rects: labels, every non-pawn thing, dug cells filled back in, Soil, unfogged, unroofed; the pawns
        a previous build stood there are handed to no faction and swept."""
        B = self.B
        B.call("jawa/review_label", action="clear", tag=TAG)
        rects = self.rects(S, doc, only)
        for rx, rz, rw, rh in rects:
            rr = "%d,%d,%d,%d" % (rx, rz, rw, rh)
            ex = B.call("jawa/flowworks_excavation_rect", x=rx, z=rz, w=rw, h=rh, onlyNonZero=True, includeTerrain=False)
            for c in ex.get("rows") or []:
                if c.get("isExcavated"):
                    B.call("jawa/flowworks_excavation_drive", x=c["x"], z=c["z"], deepenLevels=0, setFill=0,
                           fillInLevels=int(c.get("d") or 0))
            for p in B.call("jawa/list_pawns", rect=rr, limit=200).get("pawns") or []:
                if p.get("isPlayer") or p.get("faction"):
                    B.call("jawa/set_pawn_faction", pawn=str(p.get("id")), faction="none")
            B.call("jawa/destroy_batch", rects=rr, categories="All")
            B.call("jawa/set_terrain_batch", ops="Soil:" + rr)
            B.call("jawa/set_fog", action="unfog", rect=rr)
            B.call("jawa/set_roof_batch", ops="None:" + rr)
        B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)

    def no_home(self, S, doc, only):
        for rx, rz, rw, rh in self.rects(S, doc, only):
            for area in ("BuildRoof", "Home"):
                self.B.call("jawa/paint_area", area=area, ops="%d,%d,%d,%d" % (rx, rz, rw, rh), value=False)

    # ---- visuals
    def build_visuals(self, doc):
        n = 0
        for v in doc["stations"]:
            for tool, kw in VIS.station_ops(v, *VIS_BASE):
                r = self.call(tool, **kw)
                if tool == "jawa/static_call" and str(r.get("result", "")).startswith(("REFUSED", "FAIL")):
                    self.notes.append("%s %s: %s" % (v["id"], kw.get("method"), str(r.get("result"))[:120]))
                if tool == "jawa/spawn_pawn":
                    pid = (r.get("pawns") or [{}])[0].get("id") if r.get("pawns") else r.get("id") or r.get("pawnId")
                    if pid is not None:
                        self.pawn_ids[v["id"]] = pid
                        self.call("jawa/set_draft", pawnId=str(pid), drafted=True)
            n += 1
        self.say("visuals: %d stations placed" % n)

    def verify_visuals(self, doc):
        """State reads only: every pit cell's D and F (excavation_rect), scorch strength at the pit's centre, one
        colonist in the plot."""
        B = self.B
        ok = 0
        for v in doc["stations"]:
            s = v["setup"]
            ox, oz = VIS.origin_of(v, *VIS_BASE)
            p = s["pit"]
            px, pz = ox + p["dx"], oz + p["dz"]
            ex = B.call("jawa/flowworks_excavation_rect", x=px, z=pz, w=p["w"], h=p["h"])
            rows = ex.get("rows") or []
            ds = sorted({c.get("d") for c in rows})
            fs = sorted({c.get("f") for c in rows})
            sc = str(B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_PitScorchProof", method="ProofScorchAt",
                            args="%d,%d" % (px + 1, pz + 1)).get("result", ""))
            strength = float(sc.split("strength=")[1].split()[0]) if "strength=" in sc else None
            pw = [q for q in B.call("jawa/list_pawns", rect="%d,%d,%d,%d" % (ox, oz, VIS.PLOT_W, VIS.PLOT_H), limit=20)
                  .get("pawns") or [] if q.get("isPlayer")]
            want_f = s["fill_level"]
            good = (len(rows) == p["w"] * p["h"] and ds == [p["depth"]] and fs == [want_f]
                    and ((strength or 0) > 0) == bool(s["scorched"]) and len(pw) >= 1)
            self.verify[v["id"]] = dict(ok=good, cells=len(rows), d=ds, f=fs, want=(p["depth"], want_f),
                                        scorch=strength, pawns=len(pw))
            ok += good
        self.say("visuals verified: %d of %d stations as built" % (ok, len(doc["stations"])))
        return ok

    # ---- gallery
    def build_gallery(self, S):
        B = self.B
        for s in S:
            ox, oz = s["origin"]
            u = s["setup"]
            g = lambda x, z: (ox + x, oz + z)  # noqa: E731
            if s["placeholder"]:
                self.call("jawa/set_terrain_batch", ops="Concrete:%d,%d,6,4" % g(5, 5))
                continue
            terr = ["%s:%d,%d,%d,%d" % ((d,) + g(x, z) + (w, h)) for d, x, z, w, h in u.get("terrain", [])]
            if terr:
                self.call("jawa/set_terrain_batch", ops=";".join(terr))
            for x, z, w, h, d in u.get("dig", []):
                for i in range(w):
                    for j in range(h):
                        self.call("jawa/flowworks_excavation_drive", x=ox + x + i, z=oz + z + j, deepenLevels=d,
                                  setFill=-1)
            for x, z, w, h, f, fluid in u.get("fluid", []):
                for i in range(w):
                    for j in range(h):
                        r = self.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_FluidIdentityProof",
                                      method="ProofFillWithFluid", args="%d,%d,%d,%s" % (ox + x + i, oz + z + j, f, fluid))
                        if str(r.get("result", "")).startswith("REFUSED"):
                            self.notes.append("station %d fill: %s" % (s["n"], str(r.get("result"))[:100]))
            for x, z, w, h in u.get("scorch", []):
                self.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_PitScorchProof", method="ProofScorch",
                          args="%d,%d,%d,%d" % (g(x, z) + g(x + w - 1, z + h - 1)))
            for d, x, z, rot, stuff in u.get("build", []):
                kw = dict(ops="%s:%d,%d" % ((d,) + g(x, z)) + ("" if rot is None else ",%d" % rot), faction="player",
                          wipeExisting=False)
                if stuff:
                    kw["stuff"] = stuff
                r = self.call("jawa/build_batch", **kw)
                if r.get("survived") == 0:
                    self.notes.append("station %d: %s not built %s" % (s["n"], d, (r.get("failed") or [])[:1]))
            for d, x, z, stuff in u.get("spawn", []):
                kw = dict(ops="%s:%d,%d" % ((d,) + g(x, z)))
                if stuff:
                    kw["stuff"] = stuff
                self.call("jawa/spawn_batch", **kw)
            for x, z, rot in u.get("beds", []):
                r = self.call("jawa/build_batch", ops="Bed:%d,%d,%d" % (g(x, z) + (rot,)), stuff="WoodLog", faction="player")
                lt = B.call("jawa/list_things", defName="Bed", rect="%d,%d,1,1" % g(x, z), limit=5).get("things") or []
                if lt:
                    self.call("jawa/set_bed_owner_type", thing=str(lt[0].get("id") or lt[0].get("thingId")),
                              ownerType="Prisoner", medical="false")
            for d, n_, x, z in u.get("items", []):
                self.call("rimworld/spawn_thing", defName=d, stackCount=n_, x=ox + x, z=oz + z)
            for d, x, z, w, h in u.get("roof", []):
                self.call("jawa/set_roof_batch", ops="%s:%d,%d,%d,%d" % ((d,) + g(x, z) + (w, h)))
            for d, x, z, w, h in u.get("designate", []):
                self.call("jawa/designate_batch", action="add", designation=d, rect="%d,%d,%d,%d" % (g(x, z) + (w, h)))
        self.say("gallery: %d stations placed" % len(S))

    def gallery_pawns(self, S):
        for s in S:
            if s["placeholder"]:
                continue
            for kind, x, z, fac, role in s["setup"].get("pawns", []):
                gx, gz = s["origin"][0] + x, s["origin"][1] + z
                r = self.call("jawa/spawn_pawn", kindDef=kind, x=gx, z=gz, faction=fac, count=1)
                pid = (r.get("pawns") or [{}])[0].get("id") if r.get("pawns") else r.get("id") or r.get("pawnId")
                if pid is None:
                    continue
                if role == "drafted":
                    self.call("jawa/set_draft", pawnId=str(pid), drafted=True)
                elif role == "prisoner":
                    self.call("jawa/pawn_set_guest_status", pawn=str(pid), guestStatus="Prisoner",
                              hostFaction="PlayerColony")

    def keep_rects(self, S):
        return [(s["origin"][0] - 1, s["origin"][1] - 1, SW + 2, SH + 2) for s in S if s["setup"].get("keep")]

    def verify_gallery(self, S):
        """Per station: dug cells and their depths as specified, buildings present (list_things in the footprint)."""
        B = self.B
        ok = 0
        for s in S:
            ox, oz = s["origin"]
            u = s["setup"]
            want = {}
            for x, z, w, h, d in ([] if s["placeholder"] else u.get("dig", [])):
                for i in range(w):
                    for j in range(h):
                        if 0 <= ox + x + i:
                            want[(ox + x + i, oz + z + j)] = d
            ex = B.call("jawa/flowworks_excavation_rect", x=ox, z=oz, w=SW, h=SH, onlyNonZero=True, includeTerrain=False)
            got = {(c["x"], c["z"]): c.get("d") for c in ex.get("rows") or [] if c.get("isExcavated")}
            dig_ok = all(got.get(c) == d for c, d in want.items() if ox <= c[0] < ox + SW)
            things = B.call("jawa/list_things", rect="%d,%d,%d,%d" % (ox, oz, SW, SH), limit=300).get("things") or []
            defs = {t.get("def") or t.get("defName") for t in things}
            need = {d for d, *_ in u.get("build", []) + u.get("spawn", [])} if not s["placeholder"] else set()
            miss = sorted(d for d in need if d not in defs)
            pw = B.call("jawa/list_pawns", rect="%d,%d,%d,%d" % (ox, oz, SW, SH), limit=50).get("pawns") or []
            npaw = len(u.get("pawns", [])) if not s["placeholder"] else 0
            good = dig_ok and not miss and len(pw) >= npaw
            self.verify[s["n"]] = dict(ok=good, dug=len(got), want_dug=len(want), missing=miss, pawns=len(pw), want_pawns=npaw)
            ok += good
        self.say("gallery verified: %d of %d stations as built" % (ok, len(S)))
        return ok

    def free_area(self):
        x, z, w, h = FREE["rect"]
        self.call("jawa/destroy_batch", rects="%d,%d,%d,1" % (x, z, w), categories="All")
        for d, n_, c in FREE["stock"]:
            self.call("rimworld/spawn_thing", defName=d, stackCount=n_, x=c[0], z=c[1])
        t, px, pz, pw, ph = FREE["pond"]
        self.call("jawa/set_terrain_batch", ops="%s:%d,%d,%d,%d" % (t, px, pz, pw, ph))

    def labels(self, S, st, doc):
        self.B.call("jawa/review_label", action="clear", tag=TAG)
        r = self.B.call("jawa/review_label", action="add", ops=label_ops(S, st, doc), tag=TAG)
        if not r.get("success"):
            self.notes.append("labels: %s" % json.dumps(r)[:300])
        return r

    def goto(self, S, which):
        w = which.upper()
        if w == "V":
            x, z, ww, h = VIS_RECT
        elif w == "F":
            x, z, ww, h = FREE["rect"]
        elif w == "S0":
            x, z, ww, h = BOARD["rect"]
        elif w == "M":
            x, z, ww, h = ART["rect"]
        else:
            s = next(s for s in S if str(s["n"]) == which)
            x, z, ww, h = s["origin"][0] - 2, s["origin"][1] - 2, SW + 4, SH + 5
        return self.B.call("rimworld/frame_cell_rect", x=x, z=z, width=ww, height=h, paddingCells=2)


# ------------------------------------------------------------------------------------------------ key sheet
def keysheet(S, st, doc, m, live=None, save=None):
    os.makedirs(OUT, exist_ok=True)
    E = html.escape
    tot = {k: sum(1 for s in S if s["status"] == k) for k in STATUS_WORD}
    md = ["# FlowWorks review map - key sheet", "",
          "Load the save in RimWorld (Load game > %s). The game is paused, god mode is on, clear weather, noon, "
          "Peaceful. Mod Settings are the shipped defaults." % (save or "RM_fw_review_20261005"), "",
          "Each station is labelled in the world with its number, a short name, its status and what to look at. "
          "Status colours: green = works in game, blue = built, not yet seen, gold = partly built, rust = not built.", "",
          "%d stations: %s." % (len(S), ", ".join("%d %s" % (tot[k], STATUS_WORD[k].lower()) for k in STATUS_WORD)), "",
          "## V - pits: what they look like (south-west block)", "",
          "Columns: depth 1 to 4, left to right. Rows from the bottom: dry in soil, dry in granite, water in soil, water "
          "in granite, tar in soil, tar in granite, scorched in soil, scorched in granite; the top row is oil and green "
          "slime at depth 3. A colonist stands in the near row of every pit so you can see how far the near bank hides "
          "him.", ""]
    if doc:
        for state in ("dry", "water", "tar", "scorched", "oil", "slime"):
            v = next((v for v in doc["stations"] if v["id"].split("_")[1] == state), None)
            if v:
                md += ["- **%s:** %s" % (state, v["what_to_notice"])]
        md += [""]
    else:
        md += ["Visuals pending.", ""]
    secs = []
    for s in S:
        if s["section_name"] not in secs:
            secs.append(s["section_name"])
    for name in secs:
        md += ["## " + name, ""]
        for s in [s for s in S if s["section_name"] == name]:
            md += ["### %d. %s - %s" % (s["n"], s["short"], STATUS_WORD[s["status"]].lower()), "", sentence(s["title"], s["say"]), ""]
            if s["placeholder"]:
                md += ["Not built yet: the station is an empty concrete pad with its label.", ""]
                continue
            if s["notice"]:
                md += ["**Look at:** " + s["notice"], ""]
            if s["try_"]:
                md += ["**Try:**", ""] + ["- " + x for x in s["try_"]] + [""]
            if s["missing"]:
                md += ["**Not built yet in this feature:** " + "; ".join(s["missing"]), ""]
    md += ["## F - free area", "", "Round your colonists, in the middle of the map: steel, components, wood, granite "
           "blocks, chemfuel, bottles, buckets and barrels along the south edge, a pond on the east side. Dig, fill, "
           "build ladders, spikes, covers and doors here yourself.", "",
           "## S0 and M", "", "S0 (west of the free area) is the status board: each section's counts. M (below it) lists "
           "the look features still drawn with borrowed or missing art.", ""]
    if live:
        md += ["<details><summary>For the agent: this build</summary>", "", "```", json.dumps(live, indent=1, default=str),
               "```", "", "</details>", ""]
    with open(os.path.join(OUT, "KEYSHEET.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    col = {k: m.F_COLOR[k] for k in m.F_ORDER}
    cards = []
    for name in secs:
        cs = []
        for s in [s for s in S if s["section_name"] == name]:
            body = "<p class='what'>%s</p>" % E(sentence(s["title"], s["say"]))
            if s["placeholder"]:
                body += "<p>Not built yet: an empty concrete pad with its label.</p>"
            else:
                if s["notice"]:
                    body += "<p><b>Look at:</b> %s</p>" % E(s["notice"])
                if s["try_"]:
                    body += "<p><b>Try:</b></p><ul>%s</ul>" % "".join("<li>%s</li>" % E(x) for x in s["try_"])
                if s["missing"]:
                    body += "<p class='miss'><b>Not built yet here:</b> %s</p>" % E("; ".join(s["missing"]))
            cs.append("<section class='st'><div class='num'>%d</div><div><h3>%s</h3><span class='badge' "
                      "style='background:%s'>%s</span>%s</div></section>" % (s["n"], E(s["short"]), col[s["status"]],
                                                                             E(STATUS_WORD[s["status"]].capitalize()), body))
        cards.append("<h2>%s</h2><div class='grid'>%s</div>" % (E(name), "".join(cs)))
    vis = ""
    if doc:
        vis = "<ul>%s</ul>" % "".join("<li><b>%s:</b> %s</li>" % (E(state), E(v["what_to_notice"])) for state in
                                       ("dry", "water", "tar", "scorched", "oil", "slime") for v in
                                       [next((v for v in doc["stations"] if v["id"].split("_")[1] == state), None)] if v)
    legend = " ".join("<span class='badge' style='background:%s'>%s</span>" % (col[k], E(STATUS_WORD[k].capitalize()))
                      for k in STATUS_WORD)
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FlowWorks Review Map</title><style>
:root{--bg:#2a1d14;--panel:#3a291c;--ink:#f2e6cf;--muted:#c9b79a;--gold:#ffd27f;--teal:#8fd3c7;--rust:#ff9a6b;--line:#5a4230}
body{margin:0;background:var(--bg);color:var(--ink);font:18px/1.5 Georgia,serif;padding:20px 16px;overflow-x:hidden}
h1{color:var(--gold);margin:0 0 6px;font-size:28px}h2{color:var(--teal);border-bottom:1px solid var(--line);padding-bottom:4px;margin-top:30px}
.sub{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(320px,100%%),1fr));gap:12px}
.st{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px;display:flex;gap:12px}
.num{font-size:30px;color:var(--gold);min-width:42px;text-align:center;font-weight:bold}
h3{margin:0 0 4px;color:var(--gold);font-size:20px}.what{color:var(--muted);margin:6px 0}.miss{color:var(--rust)}
.badge{display:inline-block;color:#1c130c;border-radius:10px;padding:1px 10px;font-size:16px;font-weight:bold;margin:2px 0}
.box{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px}ul{margin:4px 0;padding-left:20px}
</style></head><body>
<h1>FlowWorks &mdash; review map</h1>
<p class="sub">Load <b>%s</b> in RimWorld. Paused, god mode on, clear weather, noon, Peaceful, Mod Settings at shipped defaults. Every station is labelled in the world with its number, name, status and what to look at.</p>
<div class="box">%s<br>%d stations: %s.</div>
<h2>V &mdash; pits: what they look like</h2><div class="box">South-west corner of the map. Columns: depth 1 to 4. Rows from the bottom: dry (soil, then granite), water, tar, scorched; top row oil and green slime. A colonist stands in each pit's near row.%s</div>
%s
<h2>F &mdash; free area</h2><div class="box">Round your colonists in the middle of the map: materials, bottles and a pond. Dig, fill and build here yourself.</div>
<h2>S0 and M</h2><div class="box">S0, west of the free area, is the status board. M, below it, lists the look features still drawn with borrowed or missing art.</div>
</body></html>""" % (E(save or "RM_fw_review_20261005"), legend, len(S),
                      E(", ".join("%d %s" % (tot[k], STATUS_WORD[k].lower()) for k in STATUS_WORD)), vis, "\n".join(cards))
    with open(os.path.join(OUT, "keysheet.html"), "w", encoding="utf-8") as f:
        f.write(page)


# ------------------------------------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--only", choices=("visuals", "gallery"), default=None)
    ap.add_argument("--goto", default=None)
    ap.add_argument("--labels", action="store_true")
    ap.add_argument("--clear", action="store_true")
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--name", default="RM_fw_review_%s" % time.strftime("%Y%m%d"))
    ap.add_argument("--log", default=os.path.join(REPO, "Transient", "fw_review_map_build_log.md"))
    a = ap.parse_args(argv)
    m, st, capd = derive()
    S = station_list(m, st, capd)
    doc = visuals_doc()
    probs = layout_check(S, doc)
    if probs:
        print("LAYOUT PROBLEMS:\n  " + "\n  ".join(probs))
        return 2
    if a.plan:
        keysheet(S, st, doc, m)
        print("layout ok: %d gallery stations + %s visuals + S0/M/F; key sheet -> %s" % (
            len(S), len(doc["stations"]) if doc else "pending", OUT))
        return 0
    R = Review(RM.LiveBridge(), a.log if a.build else None)
    if a.clear:
        R.clear(S, doc, a.only)
        print("cleared")
        return 0
    if a.build:
        t0 = time.time()
        if a.fresh_map:
            R.say("fresh quicktest map")
            R.fresh_map()
        R.calm()
        R.say("calm world (peaceful=%s)" % R.peaceful)
        R.clear(S, doc, a.only)
        R.say("cleared")
        R.no_home(S, doc, a.only)
        if a.only in (None, "visuals") and doc:
            R.build_visuals(doc)
        if a.only in (None, "gallery"):
            R.build_gallery(S)
            R.call("jawa/flowworks_pulse", count=30, x=0, z=0, w=0, h=0)
            R.gallery_pawns(S)
        R.free_area()
        R.call("jawa/map_commit")
        R.B.ticks(2)
        R.call("rimworld/pause_game", pause=True)
        R.sweep(R.keep_rects(S))
        vis_ok = R.verify_visuals(doc) if a.only in (None, "visuals") and doc else None
        gal_ok = R.verify_gallery(S) if a.only in (None, "gallery") else None
        R.labels(S, st, doc)
        R.B.call("jawa/clear_ui", all=True)          # the debug log auto-opens on a fresh map
        R.goto(S, "V")
        live = dict(visuals_ok=vis_ok, gallery_ok=gal_ok, verify=R.verify, notes=R.notes, wall_s=round(time.time() - t0, 1))
        with open(os.path.join(REPO, "Transient", "fw_review_map_verify.json"), "w", encoding="utf-8") as f:
            json.dump(live, f, indent=1, default=str)
        keysheet(S, st, doc, m, live)
        R.say("DONE in %ss; visuals %s, gallery %s; %d notes (Transient/fw_review_map_verify.json)" % (
            live["wall_s"], vis_ok, gal_ok, len(R.notes)))
        return 0
    if a.save:
        R.sweep(R.keep_rects(S))
        R.call("rimworld/pause_game", pause=True)
        R.B.call("jawa/clear_ui", all=True)
        name = RM.free_save_name(a.name, RM.saves_stat())
        r = RM.save_keeper(R.B, name)
        print("save %s: ok=%s new=%s changed=%s gone=%s" % (name, r["ok"], r["new"], r["changed"], r["gone"]))
        if r["ok"]:
            keysheet(S, st, doc, m, save=name)
            print("key sheet -> %s" % OUT)
        return 0 if r["ok"] else 1
    if a.labels:
        r = R.labels(S, st, doc)
        print("labels: %s" % {k: r.get(k) for k in ("added", "refused", "count")})
    if a.goto:
        R.sweep(R.keep_rects(S))
        print("framed %s: %s" % (a.goto, R.goto(S, a.goto).get("success")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
