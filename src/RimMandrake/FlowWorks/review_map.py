"""review_map.py -- the FlowWorks human review MAP: a walkable quicktest map, not a browser sheet (owner, 2026-10-05).

    python.exe src/RimMandrake/FlowWorks/review_map.py --build --fresh-map [--only visuals|gallery] | tr -d '\\r'
    python.exe src/RimMandrake/FlowWorks/review_map.py --goto N | tr -d '\\r'   # N = station; V = visuals block;
                                                       # S0 = status board; M = art board; F = free area
    python.exe src/RimMandrake/FlowWorks/review_map.py --labels | tr -d '\\r'   # re-pin labels after a load
    python.exe src/RimMandrake/FlowWorks/review_map.py --clear | tr -d '\\r'
    python.exe src/RimMandrake/FlowWorks/review_map.py --save [--name RM_fw_review_YYYYMMDD] | tr -d '\\r'
    python3    src/RimMandrake/FlowWorks/review_map.py --plan            # offline: layout check, key sheet, COVERAGE.md
    python.exe src/RimMandrake/FlowWorks/northstar/river_site.py | tr -d '\\r'            # then, for map R:
    python.exe src/RimMandrake/FlowWorks/review_map.py --rivers --build --save | tr -d '\\r'   # river works on a real river
    python.exe src/RimMandrake/FlowWorks/review_map.py --rivers --goto R3 | tr -d '\\r'       # (or --rivers --labels)

Round 2 (2026-10-15, owner: "a nice, orderly station-by-station demonstration of the mechanics to test, the art to
examine"): every card carries how to poke it and what to look for (the suspected weak spot); EXTRA stations cover what
the feature sheet predates (tank sizes and looks, pond bed hollow, relative climb, ramps, raised ladder, hoses, pipes,
spills, every liquid ground and container); time-varying things are staged frozen through the proof surfaces the
player's own buttons write (tank mode/stock, pump mode, ladder up/down, hose lay); river MECHANICS moved to map R
(review_map_rivers.py: painted river has no current). review_map_coverage.py derives the inventory and writes
northstar/review/map/COVERAGE.md; --plan fails while any item has no station or stated reason.

Owner, 2026-10-05 (typed): *"We should wire up a review MAP for me rather than a review sheet, in the style of Give
Me Some Slack review maps."* and, same day: *"stop making that review sheet in the browser for the pits. I need to see
it in the game."* So the VISUALS block (pits D1..D4 x dirt/stone x dry/water/tar/scorched, plus oil and slime; data:
review_map_stations_visuals.json, built by review_map_visuals.station_ops) is built and verified FIRST; the feature
gallery follows.

Copies the GimmeSomeSlack pattern (src/RimMandrake/GimmeSomeSlack/human_review.py): one quicktest map on the flowworks
tier; calm world (weather Clear locked, clock pinned noon, incident queue cleared, Peaceful, non-colonists swept,
research finished, god mode ON, game PAUSED, screenshot mode OFF); a SIGN BOOK in the save at every built station (a
vanilla Novel: mouse-over shows the DO line, its info card the whole sign; readable on a plain load, sign_ops); labelled
stations by jawa/review_label, each title carrying the same sign (the labels come back with the save through the
companion's sidecar once it is awake, and --labels re-pins them); a FREE AREA round the quicktest colonists with material stacks;
idempotent --build (clears its rects first, filling dug cells back in); --save writes the keeper with the before/after
Saves stat (modcheck/reviewmap.save_keeper).

STATUS IS DATA, NEVER TYPED: a gallery station is one FEATURE of the FlowWorks feature sheet (human_review.py
FEATURES, 8 sections) or an EXTRA (SETUPS entry with its own section); its status (Works in game / Built, not yet seen /
Partly built / Not built) comes from that sheet's own feature_status() over its capability table, or for an extra from
its caps or disk probes through the sheet's derive_status (extra_status), read at build/plan time. A NOT BUILT feature gets a placeholder
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
import review_map_rivers as RV  # noqa: E402
import review_map_coverage as COV  # noqa: E402

OUT = os.path.join(HERE, "northstar", "review", "map")       # under northstar/: not in the mod hash, DEPLOY_HOLD'd
TAG = "fw_review"
MAP_SIZE = 250
SW, SH = 16, 14                     # a gallery station's footprint
PITCH_X, PITCH_Z = 22, 20           # 6 cells between stations both ways: labels sit in the gap, liquids never join
GX0, TOP_Z = 52, 228                # gallery grid: columns x 52..244, rows from z 228 down by PITCH_Z
NCOL = 9
VIS_BASE = (10, 6)                  # visuals block: 4 columns x 10 rows of 6x5 plots, pitch 8 x 7 -> x 10..41, z 6..75
VIS_RECT = (VIS_BASE[0] - 2, VIS_BASE[1] - 2, 4 * (VIS.PLOT_W + VIS.GAP) + 2, 10 * (VIS.PLOT_H + VIS.GAP) + 4)
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


def _nav_cache_path():
    return r"D:\Luke\dev\_rmscratch\fw_review_nav_cache.pickle" if os.name == "nt" else \
        "/mnt/d/Luke/dev/_rmscratch/fw_review_nav_cache.pickle"


def _nav_key():
    import hashlib
    h = hashlib.sha1()
    for f in ("review_map.py", "human_review.py", "review_map_stations_visuals.json"):
        with open(os.path.join(HERE, f), "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()


def _nav_cache_write(S, st):
    """A program reads it, so it lives outside the repo (D:\\Luke\\dev\\_rmscratch, where python.exe can reach it)."""
    import pickle
    try:
        with open(_nav_cache_path(), "wb") as f:
            pickle.dump(dict(key=_nav_key(), S=S, st=st), f)
    except OSError:
        pass


def _nav_cache_read():
    import pickle
    try:
        with open(_nav_cache_path(), "rb") as f:
            d = pickle.load(f)
    except (OSError, EOFError, pickle.UnpicklingError):
        return None
    return (d["S"], d["st"]) if d.get("key") == _nav_key() else None


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
#   stuffed [(Def, x, z, n, Stuff)]    jawa/spawn_batch, stack n, stuff or None (containers per material; filth)
#   tank    [(x, z, Mode, LiquidDef, units)]  contents by RM_NorthstarProofs.ProofTank, then the "Job:" button to Mode
#   pump    [(x, z, "pour"|"draw")]    the pump's own Draw/Pour button
#   ladder  [(x, z, "raise"|"lower")]  the ladder's own Ladder up/down button
#   hose    [(rx, rz, x, z, end)]      HoseProbe "lay:" (instant staging verb) then "end:" nozzle|cap (end None = leave it)
#   style   [(Def, x, z, StyleDef)]    jawa/set_thing_props style= on the thing at that cell (Choose style's write)
#   hostile [(Def, x, z, rot, stuff)]  jawa/build_batch, faction hostile (another faction's tank for a hose to couple to)
#   hose_order [(rx, rz, x, z)]        HoseProbe "order:rx,rz=deploy:x,z": the player's Deploy order, left for a colonist
#   hose_trail [(rx, rz, [(x, z)..])]  HoseProbe "settrail:rx,rz=dropped;...": a carried end dropped part way
#   hose_flow  [(rx, rz, state)]       late pass (late_hoses): Plump = the reel's debug flow on and fully filled; Filling =
#                                      flow on half a transition before the map is frozen (caught mid-swell)
#   hose_reelin [(rx, rz)]             late pass: laid, then reeled back in (the stored drum keeps the reel's look)
#   build_after [(Def, x, z, rot, stuff)]  late pass, after every hose is down: built, then 60 ticks for the hose to answer
# The hose stations hose_reels_laid .. hose_their_tank came from the Gimme Some Slack walk (owner 2026-10-15, touring it:
# "But wait! GimmeSomeSlack shouldn't even have hoses in it anymore! It should just have the cables! We moved the hoses
# into FlowWorks! Get rid of those hoses..."): its hose cards, shrunk to this 16x14 footprint, so nothing reviewed is lost.
# An EXTRA station (not a feature-sheet FEATURE) carries its section `s`, `after` (the station it sits beside) and
# either `caps` or disk `probes`; extra_status() derives its status from them.
# A station whose feature is NOT BUILT gets only a concrete placeholder pad + its label (build() adds it).
W, T = "RM_Fluid_Water", "RM_Fluid_Tar"


def _perimeter(x0, z0, x1, z1, gaps=()):
    return [(x, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1) if (x in (x0, x1) or z in (z0, z1)) and (x, z) not in gaps]


# the Gimme Some Slack walk's hose maze (its stations 21/22 until 2026-10-15): an outer 13x11 ring with two gaps on the east
# side (south-east short way, north-east long way) round an inner chamber whose door faces west; the reel sits inside it
MAZE = _perimeter(0, 0, 12, 10, gaps=[(12, 1), (12, 2), (12, 8), (12, 9)]) + _perimeter(4, 3, 8, 7, gaps=[(4, 5)]) + \
    [(x, 5) for x in range(9, 12)]
HOSE_TRANSITION_TICKS = 30          # HoseSettings.transitionTicks default (GimmeSomeSlack/northstar_matrix/placer.py, same value)
TANK = "RimMandrake.FlowWorks.RM_NorthstarProofs"
BIOME_MC = "RimMandrake.FloodedCanyon.MapControls.RM_BiomeMapControls"   # Baroque Biomes' flood trigger / soak zone
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")


def _pit(x, z, w=3, h=3):
    return (x, z, w, h, 4)


def _pool(deep, x, z):
    """A 4x4 liquid square: its shallow twin underneath, the deep 3x3 on top, so a one-cell shallow rim shows on the
    south and east edges (both grounds of every liquid side by side)."""
    return [(deep.replace("Deep", "Shallow"), x, z, 4, 4), (deep, x, z + 1, 3, 3)]


# Every station card answers three things (northstar_human_review.md): `notice` = what is staged here (one clause, also
# the in-world sub-line), `try_` = how to poke it, `look` = what to look for, naming the SUSPECTED WEAK SPOT. That last
# line is what finds bugs: layout_check refuses a built station without it.
SETUPS = {
    # ---- 1 digging
    "dig_canal": dict(short="Dig a canal, dig deeper", notice="four depths side by side, D1 to D4; the right one is a pit",
                      dig=[(1, 2, 2, 8, 1), (5, 2, 2, 8, 2), (9, 2, 2, 8, 3), (13, 2, 2, 8, 4)],
                      designate=[("RM_DigCanal", 1, 11, 6, 1)],
                      marks=[(2, 1, "D1"), (6, 1, "D2"), (10, 1, "D3"), (14, 1, "D4")],
                      try_=["unpause: a colonist digs the marked strip (top left)",
                            "Architect > Orders > Dig canal on a dug strip: it goes one level deeper; a D4 strip refuses"],
                      look="weak spot: a D4 strip that still takes a dig order; dug ground that reads as a gravel path"),
    "dig_fill_in": dict(short="Fill a canal back in", notice="a water canal with a fill-in order on its east end",
                        terrain=[("WaterDeep", 0, 5, 3, 4)], dig=[(3, 6, 12, 2, 2)], fluid=[(3, 6, 12, 2, 1, W)],
                        designate=[("RM_FillInCanal", 11, 6, 3, 2)],
                        try_=["unpause: a colonist fills the marked cells and their water moves back along the canal, "
                              "not deleted"],
                        look="weak spot: water that vanishes instead of moving back; a filled cell still drawn as canal"),
    "dig_slows": dict(short="Trenches slow people down", notice="dry lanes D1, D2, D3, a pit row D4, and a flooded D2 lane",
                      dig=[(1, 1, 14, 1, 1), (1, 3, 14, 1, 2), (1, 5, 14, 1, 3), (1, 7, 14, 1, 4), (1, 10, 14, 1, 2)],
                      fluid=[(1, 10, 14, 1, 2, W)],
                      marks=[(0, 1, "D1"), (0, 3, "D2"), (0, 5, "D3"), (0, 7, "pit"), (0, 10, "wet")],
                      try_=["hover a lane: the walk cost climbs with depth; the wet lane is slower than the dry D2",
                            "order a colonist across: he goes round the pit row"],
                      look="weak spot: the pit row crossed anyway; the wet lane no slower than the dry D2"),
    "dig_finds": dict(short="Digging turns up minerals", notice="a dig order 14 cells long, waiting for a colonist",
                      designate=[("RM_DigCanal", 1, 6, 14, 1)],
                      try_=["unpause: about 1 in 70 dug tiles leaves a lump on the bank, with a letter the first time"],
                      look="weak spot: a lump dropped into the canal; a second letter for the same mineral"),
    # ---- 2 flow
    "flow_drains": dict(short="A canal off the map edge drains", notice="the lower canal runs off the map edge and stays "
                        "empty; the upper one ends inside the map and holds its water",
                        terrain=[("WaterDeep", 9, 4, 3, 6)], dig=[(-GX0, 5, GX0 + 9, 1, 2), (1, 9, 8, 1, 2)],
                        west_edge=True, try_=["unpause: the lower canal keeps pouring away off the edge"],
                        look="weak spot: the upper canal draining too; water standing in the lower one"),
    "flow_spreads": dict(short="Liquid spreads along the canal", notice="one pond, a canal branching three ways, all filled",
                         terrain=[("WaterDeep", 0, 5, 3, 4)], dig=[(3, 6, 12, 1, 2), (8, 7, 1, 6, 2), (8, 1, 1, 5, 2)],
                         try_=["dig a new cell onto any end: next pulse it fills", "unpause: it moves in pulses, not every tick"],
                         look="weak spot: liquid outside the dug cells; one branch left dry"),
    "flow_identity": dict(short="Tar crawls, water runs", notice="same canal, same pulses: the water canal (top) is full, "
                          "the tar canal (bottom) has crawled a few cells",
                          terrain=[("WaterDeep", 0, 9, 3, 4), ("RM_TarDeep", 0, 1, 3, 4)],
                          dig=[(3, 10, 12, 1, 2), (3, 2, 12, 1, 2)],
                          try_=["unpause and watch the tar front creep"],
                          look="weak spot: the tar canal drawn as water; both fronts the same length"),
    "flow_no_mix": dict(short="Liquids never mix", notice="water from the west, tar from the east: the fronts meet and stop",
                        terrain=[("WaterDeep", 0, 5, 3, 4), ("RM_TarDeep", 13, 5, 3, 4)], dig=[(3, 6, 10, 1, 2)],
                        try_=["fill in a water cell: the tar moves in"],
                        look="weak spot: a cell between the fronts drawn as a blend; one liquid overwriting the other"),
    "flow_ponds": dict(short="A small pond runs dry", notice="a 2x2 deep pond feeding a long 2-deep canal: it fills about "
                       "8 cells, then stops (a deep pond square holds 4 levels, two canal cells)",
                       terrain=[("WaterDeep", 0, 5, 2, 2)], dig=[(2, 5, 14, 1, 2), (15, 6, 1, 3, 2), (1, 9, 15, 1, 2)],
                       try_=["the far end stays dry: the pond has paid out", "a lake touching the map edge never runs out"],
                       look="weak spot: water at the far end (the pond never runs out)"),
    "flow_shrinks": dict(short="A pond shrinks as it pays out", notice="a 4x4 pond feeding a long canal: its edge cells "
                         "turn to shallow then mud as it is drawn down",
                         terrain=[("WaterDeep", 0, 4, 4, 4)], dig=[(4, 5, 12, 1, 2), (15, 6, 1, 6, 2), (6, 11, 9, 1, 2)],
                         try_=["unpause through rain: it slowly refills"],
                         look="weak spot: a pond that shrinks from the middle, or not at all"),
    "pond_bed": dict(short="A drained pond leaves a hollow", notice="a 2x2 pond fed out into a long canal: its bed is "
                     "left as lakebed, a hollow, not flat ground",
                     s="flow", after="flow_shrinks",
                     probes=["set:pondBedHollowEnabled", "set:dugBedLeavesPondEnabled", "xml:defName>RM_Lakebed_Deep<",
                             "xml:defName>RM_Lakebed_Shallow<"],
                     terrain=[("WaterDeep", 0, 6, 2, 2)], dig=[(2, 6, 14, 1, 2), (15, 7, 1, 5, 2), (2, 12, 14, 1, 2)],
                     try_=["hover the bed: lakebed terrain, and a hollow you climb down into",
                           "order a colonist into the bed and back out: a hollow never traps"],
                     look="weak spot: water still in the pond (the build's pulses ran short, say so); a bed drawn as "
                          "flat soil; a colonist stuck in it"),
    "pond_occupied": dict(short="Refill waits for whoever stands in it", notice="the same drained pond with a muffalo "
                          "standing in its bed", s="flow", after="pond_bed",
                          probes=["set:refillWaitsForOccupants", "set:refillEnabled"],
                          terrain=[("WaterDeep", 0, 6, 2, 2)], dig=[(2, 6, 14, 1, 2), (15, 7, 1, 5, 2), (2, 12, 14, 1, 2)],
                          pawns=[("Muffalo", 0, 6, "none", None)], keep=True,
                          try_=["dev: Change weather > Rain, unpause: the bed refills around the muffalo, never over it"],
                          look="weak spot: water poured onto the muffalo; a refill that never starts after it walks off"),
    "pond_return": dict(short="Filling in sends water home", notice="a pond feeding a water canal, with a fill-in order "
                        "on the canal's far end", s="flow", after="pond_occupied",
                        probes=["set:pondReturnLegEnabled"],
                        terrain=[("WaterDeep", 0, 5, 3, 3)], dig=[(3, 6, 12, 1, 2)],
                        designate=[("RM_FillInCanal", 10, 6, 5, 1)],
                        try_=["unpause: a colonist fills the far end and that water runs back into the pond"],
                        look="weak spot: water deleted at the filled cells; the pond's edge never rising"),
    "flow_rain": dict(short="Rain fills open trenches", notice="two dry trenches; the right one is roofed",
                      dig=[(1, 3, 5, 6, 2), (9, 3, 5, 6, 2)], roof=[("RoofConstructed", 9, 3, 5, 6)],
                      try_=["dev: Change weather > Rain, unpause: the open trench fills, the roofed one stays dry"],
                      look="weak spot: the roofed trench filling; rain filling undug ground"),
    # FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS: a flood trigger (Baroque Biomes map control, button only so the paused map
    # never floods by itself) at the canal's west end aims the canyon flood into it; this map is not a canyon biome, and
    # the trigger lifts that gate for its own flood (the forced map-wide flood ran 393 cells elsewhere, 2026-10-16).
    "flow_canyon": dict(short="Canyon floods run through canals", notice="a dry canal waiting for a canyon flood; the small "
                        "marker at its west end is a flood trigger",
                        dig=[(1, 6, 14, 1, 2)], flood_trigger=[(0, 6, False, False, 0)],
                        try_=["dev: select the flood trigger at the canal's west end, press Flood now: the water enters "
                              "there and runs down the whole canal, and nowhere else",
                              "dev: Flood after warning plays the signs and chimes first"],
                        look="weak spot: the flood wiping the canal flat instead of running in it; water outside the "
                             "canal; the flood vanishing on the next tick (this is not a canyon biome)"),
    "flow_slime": dict(short="Slime is nearly uncrossable", notice="a canal three wide, brim-full of green slime; one "
                       "colonist waits on the south bank, another stands stuck in the middle of it; a natural slime pool, undug, top right",
                       terrain=[("RM_SlimeGreenShallow", 11, 10, 5, 3)], dig=[(0, 5, 16, 3, 2)], fluid=[(0, 5, 16, 3, 2, "RM_Fluid_SlimeGreen")],
                       pawns=[("Colonist", 8, 2, "player", "drafted"), ("Colonist", 4, 6, "player", "drafted")],
                       marks=[(8, 1, "cross"), (8, 11, "to here"), (4, 9, "stuck"), (13, 13, "natural")],
                       try_=["unpause, order the bank colonist to the far mark: he walks round the canal's end rather "
                             "than wade three cells of slime",
                             "order him onto a slime cell instead: he wades in and keeps stopping, 'Slipped in the green "
                             "slime' over his head each time",
                             "undraft the stuck one: every slip on the climb out says 'Slid back into the green slime' and "
                             "he starts the climb again; getting out takes many seconds",
                             "order the bank colonist into the natural pool (owner 2026-10-16: \"Natural slime should also be "
                             "slippery.\"): he slips there too, but never slides back (no climb out of undug ground)",
                             "Mod Settings > Slime is so slippery it is nearly impossible to cross OFF: both just wade"],
                       look="weak spot: a colonist who stops with no text over him; one who walks across at tar speed; "
                            "a climb out that never ends"),
    # ---- 3 fire
    "fire_lights": dict(short="Fire lights tar", notice="a tar pond and its canal; the mark is where to drop a fire",
                        terrain=[("RM_TarDeep", 0, 5, 3, 4)], dig=[(3, 6, 12, 1, 2)], marks=[(14, 8, "light here")],
                        try_=["dev: Spawn fire (or an explosion) at the mark: the flame runs back along the canal",
                              "nothing lights? Mod Settings > FlowWorks: burning liquid and liquid ignition both ship ON"],
                        look="weak spot: a flame that lights and dies at once; fire jumping onto dry ground"),
    "fire_lasts": dict(short="A burning canal burns for days", notice="a long tar canal back to its pond",
                       terrain=[("RM_TarDeep", 0, 5, 4, 4)], dig=[(4, 6, 12, 1, 2), (15, 7, 1, 5, 2)],
                       marks=[(15, 12, "light here")],
                       try_=["light the far end, unpause: about one canal level a day, and it spreads back into the pond"],
                       look="weak spot: the whole canal burnt out within an hour; the pond never catching"),
    "fire_out": dict(short="Foam or rain puts it out", notice="a tar canal with a firefoam popper beside it",
                     terrain=[("RM_TarDeep", 0, 5, 3, 4)], dig=[(3, 6, 12, 1, 2)],
                     build=[("FirefoamPopper", 9, 8, None, None)], marks=[(13, 8, "light here")],
                     try_=["light it, then trigger the popper: foamed cells stop burning while the foam lies there"],
                     look="weak spot: foamed cells relighting while the foam still lies there"),
    # CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL (owner by card, 2026-10-15): both fuel channels frozen UNLIT; the owner lights them.
    "fire_chemfuel": dict(short="Chemfuel goes up like gasoline", notice="a short chemfuel moat, unlit, with wood lying "
                          "two cells off both banks",
                          s="fire", after="fire_out",
                          probes=["set:chemfuelInfernoEnabled", "xml:defName>RM_LiquidFlame_Inferno<", "cs:ApplyInfernoEffects"],
                          dig=[(3, 7, 10, 1, 2)], fluid=[(3, 7, 10, 1, 2, "RM_Fluid_Chemfuel")],
                          items=[("WoodLog", 25, 6, 5), ("WoodLog", 25, 10, 9)], marks=[(13, 7, "light here")],
                          try_=["dev: Spawn fire on the mark (the cell just past the moat's east end), unpause: the whole "
                                "moat is alight within a couple of seconds, tall flames, the wood catches, and the chemfuel "
                                "is burnt away inside a minute",
                                "Mod Settings > FlowWorks > Burning liquid: intensity, spread speed and burn-down dials"],
                          look="weak spot: flames no bigger than tar's; the wood two cells off the bank never catching; "
                               "chemfuel still burning after a minute; a lot of smoke"),
    "fire_astrofuel": dict(short="Astrofuel detonates", notice="a short astrofuel channel, unlit, a muffalo standing "
                           "beside it and wood two cells off",
                           s="fire", after="fire_chemfuel",
                           probes=["set:astrofuelDetonationEnabled", "set:astrofuelBlastScale", "cs:StartDetonation",
                                   "cs:RunDetonation"],
                           dig=[(3, 7, 10, 1, 2)], fluid=[(3, 7, 10, 1, 2, "RM_Fluid_Astrofuel")],
                           items=[("WoodLog", 25, 8, 4)], pawns=[("Muffalo", 8, 9, "none", None)], keep=True,
                           marks=[(13, 7, "light here")],
                           try_=["dev: Spawn fire on the mark, unpause: a ripple of explosions runs the channel's length "
                                 "in about a second, the muffalo is staggered and thrown back, and the channel is empty "
                                 "and scorched",
                                 "with RimUtinni's Empire Pursuit loaded: a 'seen from orbit' message, and an Imperial "
                                 "squad drops onto the blast two hours later"],
                           look="weak spot: one flash instead of a ripple; astrofuel left in a cell; the game hitching; "
                                "the muffalo neither staggered nor thrown"),
    "fire_corrosion": dict(short="Acid eats what lies in it", notice="an acid canal with steel and wood lying in it",
                           s="fire", after="fire_out", caps=["E10"],
                           terrain=[("RM_AcidDeep", 0, 5, 3, 4)], dig=[(3, 6, 12, 1, 2)],
                           items=[("Steel", 30, 7, 6), ("WoodLog", 30, 11, 6)],
                           try_=["unpause: what lies in the acid loses health (Liquid corrosion ships ON)",
                                 "Mod Settings > FlowWorks > Liquid corrosion OFF: the damage stops"],
                           look="weak spot: damage while the switch is OFF; a stack gone in seconds"),
    # ---- 4 catching
    "pit_holds": dict(short="Nothing climbs out of a pit", notice="a muffalo in a 3x3 pit",
                      dig=[_pit(6, 5)], pawns=[("Muffalo", 7, 6, "none", None)], keep=True,
                      try_=["unpause: it walks the floor and never climbs out; its info line says trapped"],
                      look="weak spot: the muffalo on the lip an hour later; no 'trapped' on its info line"),
    "pit_width": dict(short="A pit only holds what fits", notice="a muffalo in a 1-wide slot (too narrow) and a hare in "
                      "a 1x1 pit",
                      dig=[(3, 4, 1, 5, 4), (11, 6, 1, 1, 4)], pawns=[("Muffalo", 3, 6, "none", None),
                                                                     ("Hare", 11, 6, "none", None)], keep=True,
                      try_=["unpause: the muffalo walks out, the hare stays"],
                      look="weak spot: the muffalo held in the slot; the hare walking out"),
    "pit_climb": dict(short="Climbing depends on size", notice="three 2-deep pens: a chicken, a husky, a muffalo",
                      s="catch", after="pit_width",
                      probes=["set:pitRelativeClimbEnabled", "cs:class RM_PocketGrid", "cs:ClimbLimit"],
                      dig=[(1, 5, 3, 3, 2), (6, 5, 3, 3, 2), (11, 5, 3, 3, 2)],
                      pawns=[("Chicken", 2, 6, "none", None), ("Husky", 7, 6, "none", None),
                             ("Muffalo", 12, 6, "none", None)], keep=True,
                      marks=[(2, 4, "chicken"), (7, 4, "husky"), (12, 4, "muffalo")],
                      try_=["unpause: the chicken stays, the husky climbs out slowly, the muffalo steps out",
                            "Mod Settings > Pits trap by relative height OFF: only D4 holds, and all three walk out"],
                      look="weak spot: all three held or all three out; 'trapped' on any but the chicken"),
    "pit_fall": dict(short="Falling in hurts", notice="a pit and one of your colonists beside it",
                     dig=[_pit(6, 5)], pawns=[("Colonist", 4, 6, "player", "drafted")],
                     try_=["order him into the pit: he will not walk in (colonists never path into an open pit); 'Jump "
                           "into pit', or a blast or skip that puts him in, hurts him and holds him until a lowered ladder "
                           "lets him climb out"],
                     look="weak spot: a colonist who walks in on an ordinary move order; a fall with no injury"),
    "pit_shooting": dict(short="Shots only from the pit's edge", notice="a boar in a pit; your colonist stands 6 cells off",
                         dig=[_pit(9, 5)], pawns=[("WildBoar", 10, 6, "none", None), ("Colonist", 3, 6, "player", "drafted")],
                         keep=True, try_=["order an attack on the boar: he walks to the lip before he can shoot"],
                         look="weak spot: a shot fired from 6 cells away"),
    "pit_ways_in": dict(short="Jump in on purpose", notice="a pit and a colonist beside it",
                        dig=[_pit(6, 5)], pawns=[("Colonist", 4, 6, "player", "drafted")],
                        try_=["select him: 'Jump into pit' drops him in, and he is stuck there too"],
                        look="weak spot: no 'Jump into pit' button; the jumper unhurt and free"),
    "pit_ramp": dict(short="A ramp is a way out", notice="two 3-deep pits with a chicken in each; the left one has a "
                     "ramp up its north wall", s="catch", after="pit_ways_in",
                     probes=["xml:defName>RM_PitRamp<", "set:pitRampsEnabled", "set:pitRampMaxSpan"],
                     dig=[(1, 5, 4, 3, 3), (10, 5, 4, 3, 3)], build=[("RM_PitRamp", 2, 7, 0, "WoodLog")],
                     pawns=[("Chicken", 3, 5, "none", None), ("Chicken", 12, 5, "none", None)], keep=True,
                     try_=["unpause: the left chicken walks up the ramp and out; the right one is held",
                           "Architect > Structure > pit ramp: the ghost marks the square it climbs to"],
                     look="weak spot: placeholder art, judge the shape not the paint; a ramp facing the wrong way; the "
                          "right chicken escaping"),
    "pit_pocket": dict(short="A staircase never traps", notice="a staircase dug D1 to D4 with a chicken at the bottom",
                       s="catch", after="pit_ramp", probes=["cs:class RM_PocketGridMath", "cs:IsHeldAt"],
                       dig=[(1, 6, 3, 3, 1), (4, 6, 3, 3, 2), (7, 6, 3, 3, 3), (10, 6, 3, 3, 4)],
                       pawns=[("Chicken", 11, 7, "none", None)], keep=True,
                       marks=[(2, 5, "D1"), (5, 5, "D2"), (8, 5, "D3"), (11, 5, "D4")],
                       try_=["unpause: it climbs out one step at a time"],
                       look="weak spot: the chicken read as trapped at the bottom (a slope must never trap)"),
    "pit_cover": dict(short="A cover hides the hole", notice="left: a covered pit; right: the same pit uncovered",
                      dig=[_pit(2, 5), _pit(10, 5)],
                      spawn=[("RM_PitCover_PlankLattice", 2 + i, 5 + j, None) for i in range(3) for j in range(3)],
                      try_=["zoom in close on the left one: only a faint seam shows"],
                      look="weak spot: a hole outline showing through the cover at play zoom"),
    "pit_cover_drop": dict(short="Step on a cover, fall through", notice="three covered pits: plank lattice, woven scrap, "
                           "reinforced frame",
                           dig=[_pit(1, 5), _pit(6, 5), _pit(11, 5)],
                           spawn=[(d, ox + i, 5 + j, None) for d, ox in (("RM_PitCover_PlankLattice", 1),
                                  ("RM_PitCover_WovenScrap", 6), ("RM_PitCover_ReinforcedFrame", 11))
                                  for i in range(3) for j in range(3)],
                           marks=[(2, 4, "plank"), (7, 4, "scrap"), (12, 4, "frame")],
                           try_=["order a colonist across each: the weaker covers give way"],
                           look="weak spot: the reinforced frame giving way under one colonist; all three alike"),
    "pit_spikes": dict(short="Spikes at the bottom", notice="a pit floored with spikes",
                       dig=[_pit(6, 5)], spawn=[("RM_Spikes", 6 + i, 5 + j, None) for i in range(3) for j in range(3)],
                       try_=["walking up to the spikes is harmless; only a fall in triggers them"],
                       look="weak spot: spikes hurting someone who only walks beside them; a fatal stab"),
    "pit_flood": dict(short="Flood an occupied pit", notice="a boar in a pit, a water canal behind a shut sluice",
                      terrain=[("WaterDeep", 0, 5, 3, 3)], dig=[(3, 6, 5, 1, 2), (8, 6, 1, 1, 2), _pit(9, 5)],
                      spawn=[("RM_Sluice", 8, 6, "WoodLog")], pawns=[("WildBoar", 10, 6, "none", None)], keep=True,
                      try_=["open the sluice (select it): water pours into the pit"],
                      look="weak spot: water stopping at the open sluice; a boar that never starts drowning"),
    # ---- 5 holding
    # PIT_LADDER_REDRAW_HUNG_ON_THE_WALL: a ladder hangs on ONE wall (it turns to the only wall its square has, on spawn),
    # so each station stages a slid-down and a slid-up ladder on DIFFERENT walls: west down + south up here, north up +
    # east down next door. The south-wall one sits behind the near lip (the art must read so).
    "hold_ladder": dict(short="A ladder in and out", notice="a 5x5 pit: a ladder SLID DOWN on its west wall, another SLID UP "
                        "on its south wall, a colonist in it and steel on its floor",
                        dig=[_pit(5, 4, 5, 5)], spawn=[("RM_Ladder", 5, 6, None), ("RM_Ladder", 7, 4, None)],
                        items=[("Steel", 20, 7, 6)], ladder=[(7, 4, "raise")],
                        pawns=[("Colonist", 6, 5, "player", "drafted")],
                        try_=["undraft him: he climbs out by the west ladder; undrafted haulers then fetch the steel",
                              "select the west ladder: Ladder up and nobody climbs it either way",
                              "the south ladder lies on the rim beyond the near lip; the west one hangs down its wall"],
                        look="weak spot: a ladder lying loose in the pit instead of hung on its wall; slid up and "
                             "slid down drawn alike"),
    "hold_ladder_raised": dict(short="A raised ladder strands him", notice="the same pit: its only ladder SLID UP on the "
                               "north wall; a ladder slid down on the east wall of a sealed 1x1 shaft beside it",
                               s="hold", after="hold_ladder", caps=["H01", "J08"],
                               dig=[_pit(5, 4, 5, 5), (12, 6, 1, 1, 4)],
                               spawn=[("RM_Ladder", 7, 8, None)], build=[("RM_Ladder", 12, 6, 1, None)],
                               items=[("Steel", 20, 7, 6)],
                               ladder=[(7, 8, "raise")], pawns=[("Colonist", 6, 5, "player", "drafted")],
                               try_=["undraft him: he stays put, and nobody goes down for the steel",
                                     "select the north ladder: Ladder down and he climbs out",
                                     "the shaft's ladder was built turned east: every side of a 1x1 shaft is a wall, "
                                     "so the placed turn stands"],
                               look="weak spot: raised and lowered drawn the same (compare the station to the left); "
                                    "anyone using a raised ladder"),
    "hold_prison": dict(short="A pit prison, run from the lip", notice="a 3x4 pit with a prisoner bed and a prisoner",
                        dig=[(6, 5, 3, 4, 4)], beds=[(7, 7, 0)], pawns=[("Pirate", 6, 5, "hostile", "prisoner")], keep=True,
                        try_=["wardens feed and talk to him from the lip; nobody climbs down"],
                        look="weak spot: a warden climbing down; the room not labelled a prison"),
    "hold_exposure": dict(short="Sun and cold wear him down", notice="an open pit with a prisoner, noon sun on it",
                          dig=[_pit(6, 5)], beds=[(7, 6, 0)], pawns=[("Pirate", 6, 5, "hostile", "prisoner")], keep=True,
                          try_=["inspect a pit cell: hotter than the ground by day, colder by night"],
                          look="weak spot: the pit cell's temperature the same as the ground's"),
    "hold_gates": dict(short="Sluice and grate doors", notice="a pit with a sluice (wood) and a security grate (steel) "
                       "in its wall; a hare and a prisoner inside",
                       terrain=[("WaterDeep", 0, 5, 3, 4)], dig=[(3, 6, 4, 1, 2), (7, 6, 1, 1, 2), (7, 8, 1, 1, 2),
                                                               (3, 8, 4, 1, 2), (8, 5, 4, 5, 4)],
                       spawn=[("RM_Sluice", 7, 6, "WoodLog"), ("RM_SecurityGrateDoor", 7, 8, "Steel")],
                       pawns=[("Hare", 10, 6, "none", None), ("Pirate", 10, 8, "hostile", "prisoner")], keep=True,
                       try_=["open either door: liquid flows through, nobody inside can open it"],
                       look="weak spot: water stopped by an open door; the prisoner opening it from inside"),
    # ---- 6 looks
    "look_sink": dict(short="People sink as the ground deepens", notice="one colonist standing at each depth D1..D4",
                      dig=[(1, 5, 3, 3, 1), (5, 5, 3, 3, 2), (9, 5, 3, 3, 3), (13, 5, 3, 3, 4)],
                      pawns=[("Colonist", 2, 6, "player", "drafted"), ("Colonist", 6, 6, "player", "drafted"),
                             ("Colonist", 10, 6, "player", "drafted"), ("Colonist", 14, 6, "player", "drafted")],
                      marks=[(2, 4, "D1"), (6, 4, "D2"), (10, 4, "D3"), (14, 4, "D4")],
                      try_=["undraft one and order it out: it rises step by step"],
                      look="weak spot: the D4 head showing over the wall; a snap instead of a step on the way out"),
    # D3, not D2: RM_ExcavationDepth.FillTier is fill/depth (<=0.34 trace, <=0.67 half, else brim), so D2 cannot show a
    # trace (F1/D2 = 0.5 is half). F1/F2/F3 at D3 are trace/half/brim.
    "look_canal": dict(short="A canal looks dug and shows how full", notice="D3 cells: empty, trace, half, brim; and a "
                       "brimming pit",
                       dig=[(1, 5, 2, 3, 3), (4, 5, 2, 3, 3), (7, 5, 2, 3, 3), (10, 5, 2, 3, 3), (13, 5, 3, 3, 4)],
                       fluid=[(4, 5, 2, 3, 1, W), (7, 5, 2, 3, 2, W), (10, 5, 2, 3, 3, W), (13, 5, 3, 3, 4, W)],
                       marks=[(1, 4, "empty"), (4, 4, "trace"), (7, 4, "half"), (10, 4, "brim"), (14, 4, "pit")],
                       try_=["hover each: the fill reads empty, trace, half, brim"],
                       look="weak spot: trace and half drawn the same"),
    "canal_fluids_more": dict(short="Four more canal liquids", notice="D3 canals brimming with poison, yellow slime, "
                              "boiling water and icy water", s="look", after="look_canal",
                              probes=["xml:defName>RM_Fluid_Poison<", "xml:defName>RM_Fluid_SlimeYellow<",
                                      "xml:defName>RM_Fluid_BoilingWater<", "xml:defName>RM_Fluid_IcyWater<"],
                              dig=[(1, 5, 2, 4, 3), (5, 5, 2, 4, 3), (9, 5, 2, 4, 3), (13, 5, 2, 4, 3)],
                              fluid=[(1, 5, 2, 4, 3, "RM_Fluid_Poison"), (5, 5, 2, 4, 3, "RM_Fluid_SlimeYellow"),
                                     (9, 5, 2, 4, 3, "RM_Fluid_BoilingWater"), (13, 5, 2, 4, 3, "RM_Fluid_IcyWater")],
                              marks=[(1, 4, "poison"), (5, 4, "yellow"), (9, 4, "boiling"), (13, 4, "icy")],
                              try_=["hover each: the canal names its liquid"],
                              look="weak spot: boiling and icy water drawn like plain water; the V block holds the other "
                                   "seven canal liquids"),
    "look_pit": dict(short="A pit reads as one dark hole", notice="two 4x4 pits: empty (left) and occupied (right)",
                     dig=[(1, 5, 4, 4, 4), (10, 5, 4, 4, 4)], pawns=[("Muffalo", 11, 6, "none", None)], keep=True,
                     try_=["zoom out to play zoom, then in close"],
                     look="weak spot: a pit drawn as a grid of tiles; the muffalo drawn over the wall"),
    "look_walls": dict(short="Walls show what they are cut in", notice="four 3-deep pits cut in soil, sand, gravel and "
                       "granite", s="look", after="look_pit",
                       probes=["set:excavationWallMaterialEnabled", "tex:RM_WallFace_North", "tex:RM_WallFace_Side"],
                       terrain=[("Soil", 0, 4, 4, 5), ("Sand", 4, 4, 4, 5), ("Gravel", 8, 4, 4, 5),
                                ("Granite_Rough", 12, 4, 4, 5)],
                       dig=[(0, 5, 3, 3, 3), (4, 5, 3, 3, 3), (8, 5, 3, 3, 3), (12, 5, 3, 3, 3)],
                       marks=[(1, 4, "soil"), (5, 4, "sand"), (9, 4, "gravel"), (13, 4, "granite")],
                       try_=["zoom in: each wall face takes its ground's colour",
                             "Mod Settings > wall material OFF: all four turn the same"],
                       look="weak spot: all four walls one colour; a seam where the wall meets the floor"),
    "look_parts": dict(short="Spikes, ladder, gates: own drawings", notice="a ladder, spikes, a sluice and a grate on dug "
                       "ground, side by side",
                       dig=[(2, 6, 1, 1, 4), (5, 6, 1, 1, 4), (8, 6, 1, 1, 2), (11, 6, 1, 1, 2)],
                       spawn=[("RM_Ladder", 2, 6, None), ("RM_Spikes", 5, 6, None), ("RM_Sluice", 8, 6, "WoodLog"),
                              ("RM_SecurityGrateDoor", 11, 6, "Steel")],
                       marks=[(2, 4, "ladder"), (5, 4, "spikes"), (8, 4, "sluice"), (11, 4, "grate")],
                       try_=["open the sluice and the grate: open and shut read differently without selecting"],
                       look="weak spot: any of the four drawn with a vanilla stand-in"),
    "look_liquids": dict(short="Tar and slime look thick", notice="a tar pond and canal (left); green, white and yellow "
                         "slime pools (right)",
                         terrain=[("RM_TarDeep", 0, 5, 3, 4), ("RM_SlimeGreenShallow", 10, 8, 3, 1),
                                  ("RM_SlimeGreenDeep", 10, 9, 3, 3), ("RM_SlimeWhiteShallow", 13, 8, 3, 1),
                                  ("RM_SlimeWhiteDeep", 13, 9, 3, 3), ("RM_SlimeYellowShallow", 10, 3, 3, 1),
                                  ("RM_SlimeYellowDeep", 10, 4, 3, 3)],
                         dig=[(3, 6, 6, 1, 2)], marks=[(11, 13, "green"), (14, 13, "white"), (11, 3, "yellow")],
                         try_=["order a colonist through the tar: he leaves a wake and is drawn sunk into it"],
                         look="weak spot: slime that looks like tinted water; no bubbles or surface motion"),
    "look_fire": dict(short="Burning liquid looks alight", notice="a tar canal to light, and a scorched-dry pit beside it",
                      terrain=[("RM_TarDeep", 0, 5, 3, 3)], dig=[(3, 6, 6, 1, 2), (11, 5, 3, 3, 3)],
                      scorch=[(11, 5, 3, 3)], marks=[(8, 8, "light here")],
                      try_=["dev: Spawn fire at the mark"],
                      look="weak spot: the scorched pit looking like plain dirt; the flame drawn as a vanilla fire"),
    # ---- 7 carry
    "carry_bottles": dict(short="Bottles, buckets, barrels", notice="empty, full and dirty bottles, a bucket and a barrel "
                          "by a pond and a tank",
                          terrain=[("WaterDeep", 0, 5, 3, 4)], build=[("RM_LiquidTank", 10, 6, None, None)],
                          items=[("RM_BottleEmpty", 5, 4, 6), ("RM_Bottle_FreshWater", 5, 5, 6), ("RM_BottleDirty", 3, 6, 6),
                                 ("RM_BucketEmpty", 2, 7, 6), ("RM_BarrelEmpty", 1, 8, 6), ("RM_Bottle_Tar", 2, 4, 8)],
                          try_=["unpause: colonists fill bottles at the shore or the tank and wash dirty ones"],
                          look="weak spot: dirty bottles never washed; tar bottled as water"),
    "containers_all": dict(short="Every liquid, every container", notice="bottles (top), buckets, barrels (bottom) of "
                           "nine liquids; left to right fresh, salt, boiling, icy, toxic, acid, tar, brine, propane",
                           s="carry", after="carry_bottles", probes=["xml:defName>RM_Barrel_Propane<"],
                           items=[("RM_%s_%s" % (c, lq), 5 if c == "Bottle" else 3 if c == "Bucket" else 1, 3 + i, z)
                                  for c, z in (("Bottle", 10), ("Bucket", 6), ("Barrel", 2))
                                  for i, lq in enumerate(("FreshWater", "SaltWater", "BoilingWater", "IcyWater",
                                                          "ToxicWater", "AcidWater", "Tar", "Brine", "Propane"))]
                           + [("RM_BucketDirty", 2, 14, 6), ("RM_BarrelDirty", 1, 14, 2)],
                           marks=[(1, 10, "bottles"), (1, 6, "buckets"), (1, 2, "barrels"), (14, 4, "dirty")],
                           try_=["hover each stack: its liquid; unpause a while: the boiling water cools"],
                           look="weak spot: two liquids whose containers read the same; the dirty ones not looking dirty"),
    "carry_containers": dict(short="Containers in every material", notice="empty bottles, buckets and barrels in each "
                             "material, by a crafting spot", s="carry", after="containers_all",
                             probes=["xml:defName>RM_Make_Bottle_Glass<", "xml:defName>RM_Make_Barrel_Plasteel<",
                                     "xml:defName>RM_Make_Bucket_Leather<"],
                             build=[("CraftingSpot", 13, 11, None, None)],
                             stuffed=[("RM_BottleEmpty", 5, 2, 10, "Leather_Plain"), ("RM_BottleEmpty", 5, 4, 10, "BlocksGranite"),
                                      ("RM_BottleEmpty", 5, 6, 10, "Steel"), ("RM_BucketEmpty", 8, 2, 10, "WoodLog"),
                                      ("RM_BucketEmpty", 8, 4, 10, "Steel"), ("RM_BucketEmpty", 8, 6, 10, "Leather_Plain"),
                                      ("RM_BarrelEmpty", 11, 2, 8, "WoodLog"), ("RM_BarrelEmpty", 11, 4, 8, "Steel"),
                                      ("RM_BarrelEmpty", 11, 6, 8, "Plasteel")],
                             marks=[(5, 8, "bottles"), (8, 8, "buckets"), (11, 8, "barrels")],
                             try_=["select the crafting spot: Bills lists the bottle, bucket and barrel recipes"],
                             look="weak spot: every material drawn the same; a material named but not in the label"),
    # LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS (owner 2026-10-16, sheet approved; by card: material on the TRIM only): each
    # look a 4-cell column group (empty, fresh water, toxic water, tar), bottles top, buckets, barrels bottom; all steel, so
    # every cap/handle/hoop is the same steel trim and only the look and the window differ.
    "containers_styles": dict(short="Containers in the four looks", notice="bottles (top), buckets, barrels (bottom) in "
                              "scrapper, industrial, modern and futuristic; each look: empty, fresh water, toxic water, tar",
                              s="carry", after="carry_containers", probes=["xml:defName>RM_Barrel_Futuristic<",
                                                                         "xml:defName>RM_Bottle_Scrapper<"],
                              stuffed=[("RM_%s%s" % (c, lq), 4 * i + k, z, n_, "Steel")
                                       for i, _lk in enumerate(("Scrapper", "Industrial", "Modern", "Futuristic"))
                                       for c, z, n_ in (("Bottle", 11, 3), ("Bucket", 7, 2), ("Barrel", 3, 1))
                                       for k, lq in enumerate(("Empty", "_FreshWater", "_ToxicWater", "_Tar"))],
                              style=[("RM_%s%s" % (c, lq), 4 * i + k, z, "RM_%s_%s" % (c, lk))
                                     for i, lk in enumerate(("Scrapper", "Industrial", "Modern", "Futuristic"))
                                     for c, z in (("Bottle", 11), ("Bucket", 7), ("Barrel", 3))
                                     for k, lq in enumerate(("Empty", "_FreshWater", "_ToxicWater", "_Tar"))],
                              marks=[(0, 13, "scrapper"), (4, 13, "industrial"), (8, 13, "modern"), (12, 13, "futuristic")],
                              try_=["select a crafting spot or smithy: a container bill has a Style button (four looks)",
                                    "hover a stack: the look shows in its info card; the cap/handle/hoops are steel"],
                              look="weak spot: the window not taking the liquid colour; the body tinted; two looks in one stack"),
    "carry_tanks": dict(short="Tanks, pumps, hoses", notice="a pump on the pond shore piped to a tank, powered by a battery",
                        terrain=[("WaterDeep", 0, 5, 3, 4)],
                        build=[("RM_LiquidPump", 3, 6, None, None), ("RM_LiquidTank", 8, 6, None, None),
                               ("RM_UniversalCargoTank", 12, 6, None, None), ("Battery", 4, 9, 0, None),
                               ("PowerConduit", 3, 7, None, None), ("PowerConduit", 3, 8, None, None),
                               ("PowerConduit", 3, 9, None, None)],
                        charge=[(4, 9)],    # GSS_CORD_SILENCE_PHANTOM_SPARK: a battery is built empty; fill it
                        try_=["unpause: the pump draws the pond down into the tank"],
                        look="weak spot: the pond not going down; the tank's fill bar never moving"),
    "pump_pour": dict(short="A pump set to Pour", notice="the same pump and tank, the pump set to Pour and the tank full",
                      s="carry", after="carry_tanks", caps=["K08"],
                      terrain=[("WaterDeep", 0, 5, 3, 4)],
                      build=[("RM_LiquidPump", 3, 6, None, None), ("RM_LiquidTank", 8, 6, None, None),
                             ("Battery", 4, 9, 0, None), ("PowerConduit", 3, 7, None, None),
                             ("PowerConduit", 3, 8, None, None), ("PowerConduit", 3, 9, None, None)],
                      tank=[(8, 6, "Store", "RM_Liquid_FreshWater", 80)], pump=[(3, 6, "pour")], charge=[(4, 9)],
                      try_=["unpause: the tank empties back into the pond", "the pump's button flips Draw and Pour"],
                      look="weak spot: pouring with no power; water poured onto dry ground"),
    "tank_sizes": dict(short="Four tank sizes", notice="a short, a tall, a cargo and an extra-tall tank, each half full",
                       s="carry", after="pump_pour",
                       probes=["xml:defName>RM_LiquidTankTall<", "xml:defName>RM_UniversalCargoTankXTall<",
                               "tex:RM_LiquidTankTall", "tex:RM_UniversalCargoTankXTall"],
                       build=[("RM_LiquidTank", 1, 5, None, None), ("RM_LiquidTankTall", 5, 5, None, None),
                              ("RM_UniversalCargoTank", 9, 5, None, None), ("RM_UniversalCargoTankXTall", 13, 5, None, None)],
                       tank=[(1, 5, "Store", "RM_Liquid_FreshWater", 40), (5, 5, "Store", "RM_Liquid_FreshWater", 80),
                             (9, 5, "Store", "RM_Liquid_FreshWater", 80), (13, 5, "Store", "RM_Liquid_FreshWater", 160)],
                       try_=["select each: 80, 160, 160 and 320 units, every fill bar at half"],
                       look="weak spot: both tall tanks are placeholder art (a drum stacked twice); a tall top cut off or "
                            "hidden behind the label"),
    "tank_styles": dict(short="Tank looks: short and tall", notice="the short tank (bottom) and the tall tank (top) in "
                        "each of the four looks", s="carry", after="tank_sizes",
                        probes=["xml:defName>RM_LiquidTank_Futuristic<", "xml:defName>RM_LiquidTankTall_Futuristic<"],
                        build=[(d, x, z, None, None) for d, z in (("RM_LiquidTank", 2), ("RM_LiquidTankTall", 8))
                               for x in (1, 5, 9, 13)],
                        style=[(d, x, z, "%s_%s" % (d, lk)) for d, z in (("RM_LiquidTank", 2), ("RM_LiquidTankTall", 8))
                               for x, lk in zip((1, 5, 9, 13), LOOKS)],
                        marks=[(1, 0, "scrapper"), (5, 0, "industrial"), (9, 0, "modern"), (13, 0, "futuristic")],
                        try_=["select a tank: Choose style (this tank)", "drag-select a row: Choose style, every selected tank"],
                        look="weak spot: no Choose style button on a built tank; a look whose tall tank does not match its "
                             "short one; a tall tank's top left in the old look after a switch"),
    "tank_styles_cargo": dict(short="Tank looks: cargo tanks", notice="the cargo tank (bottom) and the extra-tall cargo "
                              "tank (top) in each of the four looks", s="carry", after="tank_styles",
                              probes=["xml:defName>RM_UniversalCargoTank_Futuristic<",
                                      "xml:defName>RM_UniversalCargoTankXTall_Futuristic<"],
                              build=[(d, x, z, None, None) for d, z in (("RM_UniversalCargoTank", 2),
                                                                        ("RM_UniversalCargoTankXTall", 8))
                                     for x in (1, 5, 9, 13)],
                              style=[(d, x, z, "%s_%s" % (d, lk)) for d, z in (("RM_UniversalCargoTank", 2),
                                                                               ("RM_UniversalCargoTankXTall", 8))
                                     for x, lk in zip((1, 5, 9, 13), LOOKS)],
                              marks=[(1, 0, "scrapper"), (5, 0, "industrial"), (9, 0, "modern"), (13, 0, "futuristic")],
                              try_=["select a tank: Choose style (this tank)",
                                    "drag-select a row: Choose style, every selected tank"],
                              look="weak spot: the extra-tall tank's top running into the label above the station"),
    "tank_modes": dict(short="Tank modes", notice="four tanks set Store, Fill, Empty and Dump, with empty bottles by them",
                       s="carry", after="tank_styles_cargo", probes=["cs:RMFlow_TankMode_", "cs:class Building_LiquidTank"],
                       build=[("RM_LiquidTank", 1, 6, None, None), ("RM_LiquidTank", 5, 6, None, None),
                              ("RM_LiquidTank", 9, 6, None, None), ("RM_LiquidTank", 13, 6, None, None)],
                       tank=[(1, 6, "Store", "RM_Liquid_FreshWater", 40), (5, 6, "Fill", "RM_Liquid_FreshWater", 40),
                             (9, 6, "Empty", "RM_Liquid_FreshWater", 40), (13, 6, "Dump", "RM_Liquid_FreshWater", 40)],
                       items=[("RM_BottleEmpty", 10, 7, 3), ("RM_Bottle_FreshWater", 10, 9, 3)],
                       marks=[(1, 4, "store"), (5, 4, "fill"), (9, 4, "empty"), (13, 4, "dump")],
                       try_=["unpause: colonists fill bottles from Empty and pour into Fill only",
                             "the Tank mode button cycles the four"],
                       look="weak spot: the Dump tank losing water with nothing connected; a Store tank being emptied"),
    "hose_reel": dict(short="A hose laid to a tank", notice="a hose reel with its hose laid out to a tank, nozzle on",
                      s="carry", after="tank_modes", caps=["K09"],
                      build=[("RM_HoseReel", 2, 6, None, None), ("RM_LiquidTank", 13, 6, None, None)],
                      hose=[(2, 6, 11, 6, "nozzle")],
                      try_=["select the reel: Retract, Move hose end, Fitting, Free end role",
                            "dev mode adds: lay instantly, reel in instantly, flow through hose"],
                      look="weak spot: the hose drawn through the tank; bends sharper than it can take; a nozzle with "
                           "no art"),
    "hose_styles": dict(short="Four hose reel looks", notice="four hose reels: scrapper, industrial, modern, futuristic",
                        s="carry", after="hose_reel", probes=["xml:defName>RM_HoseReel_Futuristic<"],
                        build=[("RM_HoseReel", 1, 6, None, None), ("RM_HoseReel", 5, 6, None, None),
                               ("RM_HoseReel", 9, 6, None, None), ("RM_HoseReel", 13, 6, None, None)],
                        style=[("RM_HoseReel", 1, 6, "RM_HoseReel_Scrapper"), ("RM_HoseReel", 5, 6, "RM_HoseReel_Industrial"),
                               ("RM_HoseReel", 9, 6, "RM_HoseReel_Modern"), ("RM_HoseReel", 13, 6, "RM_HoseReel_Futuristic")],
                        marks=[(1, 4, "scrapper"), (5, 4, "industrial"), (9, 4, "modern"), (13, 4, "futuristic")],
                        try_=["select one: Choose style"],
                        look="weak spot: the scrapper look has no art folder of its own; two looks that read the same"),
    # ---- the hose gallery that left the Gimme Some Slack walk (owner 2026-10-15). Reels are 2x2, Position = SW cell.
    "hose_reels_laid": dict(short="Reels per look: laid, reeled in", notice="per look (top to bottom: scrapper, industrial, "
                            "modern, futuristic) a reel with its hose laid out and full, and beside it a reel whose hose was "
                            "laid and then reeled back in",
                            s="carry", after="hose_styles", caps=["K09"],
                            build=[("RM_HoseReel", x, z, None, None) for z in (10, 7, 4, 1) for x in (0, 11)],
                            style=[("RM_HoseReel", x, z, "RM_HoseReel_" + lk) for z, lk in zip((10, 7, 4, 1), LOOKS)
                                   for x in (0, 11)],
                            hose=[(x, z, fx, z, None) for z in (10, 7, 4, 1) for x, fx in ((0, 8), (11, 15))],
                            hose_flow=[(0, z, "Plump") for z in (10, 7, 4, 1)], hose_reelin=[(11, z) for z in (10, 7, 4, 1)],
                            try_=["select a reel: Deploy hose / Retract hose (dev mode: the instant DEV ones); lay a reeled-in "
                                  "one again: the same look", "build a reel from the menu in a look; copy a reel: the copy "
                                  "keeps its look"],
                            look="weak spot: a reeled-in drum not full again, or back in another look; a laid hose strand, "
                                 "wrap, coupling or end not in its reel's look (non-scrapper wraps have no cloth tint); the "
                                 "design's coil overlay is NOT BUILT (the reel swaps two whole images)"),
    "hose_states": dict(short="Hose states: flat, filling, plump", notice="three hoses side by side (top to bottom): flat "
                        "(nothing flowing), filling (flow on, frozen half-way), plump (flow on, full)",
                        s="carry", after="hose_reels_laid", caps=["K09"],
                        build=[("RM_HoseReel", 0, z, None, None) for z in (10, 6, 2)],
                        hose=[(0, z, 15, z, None) for z in (10, 6, 2)],
                        hose_flow=[(0, 6, "Filling"), (0, 2, "Plump")],
                        marks=[(3, 12, "flat"), (3, 8, "filling"), (3, 4, "plump")],
                        try_=["UNPAUSE: the filling hose finishes plumping in about half a second",
                              "dev mode: the reel's 'DEV: flow through hose' gizmo fakes flow (no tank feeds these reels)"],
                        look="weak spot: a joiner drawn along a straight hose; filling jumping straight to plump; plump no "
                             "wider than flat; the free end not the hose's own width"),
    "hose_grid": dict(short="Hoses crossing in a grid", notice="four hoses, two each way, crossing in a 2 x 2 grid: one "
                      "is one line with two ends, hoses never branch (ruled by card), there is no crossing piece",
                      s="carry", after="hose_states", caps=["K09"],
                      build=[("RM_HoseReel", 0, 3, None, None), ("RM_HoseReel", 0, 10, None, None),
                             ("RM_HoseReel", 5, 0, None, None), ("RM_HoseReel", 11, 0, None, None)],
                      hose=[(0, 3, 15, 3, None), (0, 10, 15, 10, None), (5, 0, 5, 13, None), (11, 0, 11, 13, None)],
                      hose_flow=[(0, 3, "Plump"), (0, 10, "Plump"), (5, 0, "Plump"), (11, 0, "Plump")],
                      try_=["lay a fifth hose across the grid", "NOT designed: no crossing piece, no T or + fitting"],
                      look="weak spot: a crossing that is not cleanly over/under in a fixed order (newest on top); where "
                           "S-curve slack runs alongside another hose the two may overlap for a stretch"),
    "hose_maze": dict(short="A hose out of a maze", notice="a hose laid from a reel deep in a small walled maze to a free "
                      "end outside; two ways out: the short one (south-east gap) and a longer one (north-east gap)",
                      s="carry", after="hose_grid", caps=["K09"],
                      build=[("Wall", x, z, None, "Steel") for x, z in MAZE] + [("RM_HoseReel", 6, 5, None, None)],
                      hose=[(6, 5, 15, 2, None)], hose_flow=[(6, 5, "Plump")],
                      try_=["reel it in and lay it again to the same free end: does it pick the same route?"],
                      look="weak spot: not the SHORT route (out the inner chamber's west door, down, out the south-east "
                           "gap); a bend clipping a wall corner in a one-cell corridor; the hose jumping a wall"),
    "hose_maze_walled": dict(short="Maze, short way walled after", notice="the same maze; after the hose was laid, a wall "
                             "was built across the short (south-east) gap and the hose given 60 ticks to answer",
                             s="carry", after="hose_maze", caps=["K09"],
                             build=[("Wall", x, z, None, "Steel") for x, z in MAZE] + [("RM_HoseReel", 6, 5, None, None)],
                             hose=[(6, 5, 15, 2, None)], hose_flow=[(6, 5, "Plump")],
                             build_after=[("Wall", 12, 1, None, "Steel"), ("Wall", 12, 2, None, "Steel")],
                             marks=[(13, 0, "walled")],
                             try_=["deconstruct the blocking wall (the two marked cells): does it go back to the short way?",
                                   "add walls to lengthen the way round past the hose's 40 cells: it must reel in"],
                             look="weak spot: the hose passing THROUGH the new wall; neither a clean re-route north-east "
                                  "(about 25 of its 40 cells) nor a reel-in with a message and an alert saying how many "
                                  "cells the way round needs"),
    "hose_relay": dict(short="Relay reels: going farther", notice="three reels in a row: the first reel's hose is laid onto "
                       "the second reel, whose hose is laid onto the third; flow into the first (shrunk to fit: on the "
                       "walk they stood 28 apart, beyond one 40-cell hose)",
                       s="carry", after="hose_maze_walled", caps=["K09"],
                       build=[("RM_HoseReel", 0, 6, None, None), ("RM_HoseReel", 7, 6, None, None),
                              ("RM_HoseReel", 14, 6, None, None)],
                       hose=[(0, 6, 6, 6, None), (7, 6, 13, 6, None)], hose_flow=[(0, 6, "Plump")],
                       try_=["reel in the first hose: the second drains (nothing feeds it)",
                             "lay the third reel's hose back onto the first: refused, a chain may not loop back",
                             "select the middle reel: 'Relay: fed by the hose from the reel at ...'"],
                       look="weak spot: a hose that does not end in a brass coupling on the NEXT reel (two loose hoses, "
                            "not a chain); the second hose not plump though fed; a loop back accepted"),
    "hose_deploy_by_hand": dict(short="Deploy by hand, then wind in", notice="a reel with a Deploy order 15 cells out and "
                                "one idle colonist beside it: UNPAUSE and he walks the hose out; then press Retract",
                                s="carry", after="hose_relay", caps=["K09"],
                                build=[("RM_HoseReel", 0, 6, None, None)], hose_order=[(0, 6, 15, 7)],
                                pawns=[("Colonist", 3, 9, "player", None)],
                                try_=["UNPAUSE: he picks up the end and walks it out; then press Retract on the reel",
                                      "draft him mid-walk: the end drops where he stands"],
                                look="weak spot: the hose longer than his walk (jumping to the target); Retract making the "
                                     "hose vanish at once instead of winding back along its route; not ending Stored"),
    "hose_dropped": dict(short="A carry dropped halfway", notice="a reel whose hose end was dropped 11 cells out (an "
                         "interrupted carry): the hose is drawn only as far as it was walked",
                         s="carry", after="hose_deploy_by_hand", caps=["K09"],
                         build=[("RM_HoseReel", 0, 6, None, None)], hose_trail=[(0, 6, [(x, 6) for x in range(0, 12)])],
                         try_=["select the reel: Move hose end to a cell beside it, then unpause: an idle colonist walks "
                               "it there"],
                         look="weak spot: anyone shown carrying it before a colonist picks it up; the open end not lying "
                              "at the hose's end; Move hose end / Retract not offered"),
    "hose_into_pond": dict(short="A hose laid into a pond", notice="a reel beside a pond, its hose end laid into the water",
                           s="carry", after="hose_dropped", caps=["K09"], terrain=[("WaterShallow", 9, 0, 7, 14)],
                           build=[("RM_HoseReel", 0, 6, None, None)], hose=[(0, 6, 13, 6, None)],
                           hose_flow=[(0, 6, "Plump")],
                           try_=["select the reel: inspect"],
                           look="weak spot: the end on the bank, not IN the water; the end drawing water by itself (owner "
                                "ruling 2026-10-11 #3: it draws nothing; filling a tank takes a pump; the reel reads 'Not "
                                "connected')"),
    "hose_their_tank": dict(short="A hose on THEIR tank", notice="a hose coupled to another faction's liquid tank",
                            s="carry", after="hose_into_pond", caps=["K09"],
                            build=[("RM_HoseReel", 0, 6, None, None)], hostile=[("RM_LiquidTank", 13, 6, None, None)],
                            hose=[(0, 6, 12, 6, None)],
                            try_=["select the reel and the tank"],
                            look="weak spot: the brass coupling not on THEIR tank; their faction is only a state read "
                                 "(HoseProbe census): nobody's inspect names it"),
    "pipe_styles": dict(short="Four pipe looks", notice="four rigid pipe runs, one per look", s="carry", after="hose_styles",
                        probes=["xml:defName>RM_UniversalPipe_Futuristic<", "tex:Pipe/Scrapper"],
                        build=[("RM_UniversalPipe", x, z, None, None) for z in (2, 5, 8, 11) for x in range(2, 14)]
                        + [("RM_UniversalPipe", 8, z, None, None) for z in (3, 9)],
                        style=[("RM_UniversalPipe", x, z, "RM_UniversalPipe_" + lk) for z, lk in
                               ((2, "Scrapper"), (5, "Industrial"), (8, "Modern"), (11, "Futuristic"))
                               for x in range(2, 14)]
                        + [("RM_UniversalPipe", 8, 3, "RM_UniversalPipe_Scrapper"),
                           ("RM_UniversalPipe", 8, 9, "RM_UniversalPipe_Modern")],
                        marks=[(0, 2, "scrapper"), (0, 5, "industrial"), (0, 8, "modern"), (0, 11, "futuristic")],
                        try_=["select a pipe: Choose style, for one pipe or its whole run"],
                        look="weak spot: the tees (middle of the bottom run and the third run up) breaking the joins; a run that changes "
                             "look half way"),
    "pipe_adapter": dict(short="Pipe-net adapters", notice="the chemfuel and propane adapters next to a tank", s="carry",
                         after="pipe_styles", caps=["K10"], needs_def="RM_PipeAdapter_Chemfuel",
                         build=[("RM_LiquidTank", 1, 6, None, None), ("RM_PipeAdapter_Chemfuel", 6, 6, None, None),
                                ("RM_PipeAdapter_Propane", 10, 6, None, None)],
                         try_=["select an adapter: its mode button cycles Send, Take and Shut"],
                         look="weak spot: the adapters exist only with Vanilla Chemfuel Expanded loaded; without it "
                              "(the release test list) this pad is empty and the build notes say so"),
    # walk 2026-10-15: on Soil (filthAcceptanceMask Unnatural) BOTH filths are refused, the Natural spill and the
    # Terrain-sourced tar alike, so the pad is concrete (mask Any). The soil refusal of the spill is a MOD finding.
    "liquid_spill": dict(short="Spilled liquid", notice="spilled liquid (left) and tracked tar (right) on a concrete pad",
                         terrain=[("Concrete", 1, 4, 13, 5)],
                         s="carry", after="pipe_adapter",
                         probes=["xml:defName>RM_Filth_LiquidSpill<", "xml:defName>RM_Filth_Tar<", "tex:RM_FilthTar"],
                         stuffed=[("RM_Filth_LiquidSpill", x, z, 1, None) for x in (2, 3, 4) for z in (5, 6, 7)]
                         + [("RM_Filth_Tar", x, z, 1, None) for x in (10, 11, 12) for z in (5, 6, 7)],
                         try_=["unpause: colonists clean both"],
                         look="weak spot: the spill drawn as a vanilla water puddle; tar filth with no art"),
    "carry_drills": dict(short="Drills, taps and stills", notice="a liquid drill, a tap, a fuelled still, a sun-pan still "
                         "and a drip filter",
                         build=[("RM_LiquidDrill", 1, 6, None, None), ("RM_LiquidTap", 5, 6, None, None),
                                ("RM_FueledStill", 7, 6, None, None), ("RM_SunPanStill", 10, 6, None, None),
                                ("RM_DripFilter", 13, 6, None, None)],
                         marks=[(1, 4, "drill"), (5, 4, "tap"), (7, 4, "still"), (10, 4, "sun pan"), (13, 4, "filter")],
                         try_=["select the drill: it says what liquid lies under it, if any"],
                         look="weak spot: a drill with nothing under it and no message saying so"),
    "carry_industry": dict(short="Ruined liquid works", notice="four wrecked plants: desalination, detox works, tar "
                           "refinery, pumping station",
                           build=[("RM_DesalPlant_Wrecked", 1, 6, None, None), ("RM_DetoxWorks_Wrecked", 5, 6, None, None),
                                  ("RM_TarRefinery_Wrecked", 9, 6, None, None),
                                  ("RM_PumpingStation_Wrecked", 13, 6, None, None)],
                           try_=["select a wreck: repair it in stages; none are on the build menu in the campaign"],
                           look="weak spot: a wreck that offers no repair"),
    "industry_stages": dict(short="Wrecked, kludged, repaired", notice="one desalination plant at each stage", s="carry",
                            after="carry_industry",
                            probes=["xml:defName>RM_DesalPlant_Kludged<", "xml:defName>RM_DesalPlant_Repaired<",
                                    "tex:RM_DesalPlant_Kludged"],
                            build=[("RM_DesalPlant_Wrecked", 2, 6, None, None), ("RM_DesalPlant_Kludged", 7, 6, None, None),
                                   ("RM_DesalPlant_Repaired", 12, 6, None, None)],
                            marks=[(2, 4, "wrecked"), (7, 4, "kludged"), (12, 4, "repaired")],
                            try_=["select each: what it makes and what it needs"],
                            look="weak spot: the three stages hard to tell apart"),
    "industry_stages_more": dict(short="The other plants, mended", notice="detox works, tar refinery and pumping "
                                 "station, kludged (bottom) and repaired (top)", s="carry", after="industry_stages",
                                 probes=["xml:defName>RM_DetoxWorks_Repaired<", "xml:defName>RM_TarRefinery_Kludged<",
                                         "xml:defName>RM_PumpingStation_Kludged<"],
                                 build=[("RM_DetoxWorks_Kludged", 2, 3, None, None), ("RM_TarRefinery_Kludged", 7, 3, None, None),
                                        ("RM_PumpingStation_Kludged", 12, 3, None, None),
                                        ("RM_DetoxWorks_Repaired", 2, 9, None, None), ("RM_TarRefinery_Repaired", 7, 9, None, None),
                                        ("RM_PumpingStation_Repaired", 12, 9, None, None)],
                                 marks=[(2, 12, "detox"), (7, 12, "tar refinery"), (12, 12, "pumping")],
                                 try_=["select each: what it needs and what it makes"],
                                 look="weak spot: a kludged and a repaired plant drawn alike"),
    "carry_kits": dict(short="Liquid kits", notice="a reaction vat between two tanks; the bath bills, scalding floods "
                       "and tar stains have nothing to show until a biome wires them in",
                       build=[("RM_LiquidTank", 2, 6, None, None), ("RM_ReactionVat", 7, 6, None, None),
                              ("RM_LiquidTank", 11, 6, None, None)],
                       tank=[(2, 6, "Store", "RM_Liquid_Tar", 40), (11, 6, "Store", "RM_Liquid_AcidWater", 40)],
                       marks=[(2, 4, "tar tank"), (7, 4, "vat"), (11, 4, "acid tank")],
                       try_=["unpause: with tar and acid water in the tanks the vat vents a gas cloud"],
                       look="weak spot: no gas although both tanks hold their liquids"),
    # ---- 8 land
    "land_liquids": dict(short="Many liquids as ground", notice="brine, boiling water, propane, acid, tar, red slime",
                         terrain=[*_pool("RM_WaterBrineDeep", 0, 7), *_pool("RM_WaterBoilingDeep", 6, 7),
                                  *_pool("RM_PropaneDeep", 12, 7), *_pool("RM_AcidDeep", 0, 1), *_pool("RM_TarDeep", 6, 1),
                                  *_pool("RM_SlimeRedDeep", 12, 1)],
                         marks=[(2, 11, "brine"), (8, 11, "boiling"), (14, 11, "propane"), (2, 5, "acid"),
                                (8, 5, "tar"), (14, 5, "red slime")],
                         try_=["hover each: the ground names its liquid"],
                         look="weak spot: two liquids that look the same"),
    "land_liquids_2": dict(short="Six more liquids", notice="frigid, brackish, mineral, poisoned water, ammonia, coolant",
                           s="land", after="land_liquids", probes=["xml:defName>RM_WaterFrigidDeep<",
                                                                   "xml:defName>RM_CoolantDeep<"],
                           terrain=[*_pool("RM_WaterFrigidDeep", 0, 7), *_pool("RM_WaterBrackishDeep", 6, 7),
                                    *_pool("RM_WaterMineralDeep", 12, 7), *_pool("RM_WaterPoisonedDeep", 0, 1),
                                    *_pool("RM_AmmoniaDeep", 6, 1), *_pool("RM_CoolantDeep", 12, 1)],
                           marks=[(2, 11, "frigid"), (8, 11, "brackish"), (14, 11, "mineral"), (2, 5, "poisoned"),
                                  (8, 5, "ammonia"), (14, 5, "coolant")],
                           try_=["hover each: the ground names its liquid"],
                           look="weak spot: the four waters reading as plain water"),
    "land_liquids_3": dict(short="Six odd grounds", notice="fuel sap, ichor, ooze, reaction liquor, churnmud, tar glass",
                           s="land", after="land_liquids_2", probes=["xml:defName>RM_IchorDeep<", "xml:defName>RM_TarGlass<"],
                           terrain=[*_pool("RM_FuelSapDeep", 0, 7), *_pool("RM_IchorDeep", 6, 7), *_pool("RM_OozeDeep", 12, 7),
                                    *_pool("RM_ReactionLiquorDeep", 0, 1), ("RM_Churnmud", 6, 1, 4, 4),
                                    ("RM_TarGlass", 12, 1, 4, 4)],
                           marks=[(2, 11, "fuel sap"), (8, 11, "ichor"), (14, 11, "ooze"), (2, 5, "liquor"),
                                  (8, 5, "churnmud"), (14, 5, "tar glass")],
                           try_=["hover each; walk a colonist across the churnmud and the tar glass"],
                           look="weak spot: tar glass that walks like liquid; churnmud that looks like plain mud"),
    "many_waters": dict(short="Coloured waters and slimes", notice="five coloured waters (top), five coloured slimes "
                        "(middle), a bottle of each water (bottom)", s="land", after="land_liquids_3",
                        probes=["xml:defName>RM_Water_Rust<", "xml:defName>RM_Slime_Chalk<"],
                        terrain=[("RM_Water_" + c, 3 * i, 8, 3, 3) for i, c in enumerate(
                            ("Rust", "Verdigris", "Amber", "Violet", "Chalk"))]
                        + [("RM_Slime_" + c, 3 * i, 3, 3, 3) for i, c in enumerate(
                            ("Rust", "Verdigris", "Amber", "Violet", "Chalk"))],
                        marks=[(1, 12, "rust"), (4, 12, "verdigris"), (7, 12, "amber"), (10, 12, "violet"),
                               (13, 12, "chalk")],
                        items=[("RM_WaterBottle_" + c, 5, 1 + 3 * i, 1) for i, c in enumerate(
                            ("Rust", "Verdigris", "Amber", "Violet", "Chalk"))],
                        try_=["hover each; the bottles along the bottom are each water bottled",
                              "coloured steam rises only off a RIVER of these waters (not here)"],
                        look="weak spot: two colours that read the same; a slime that looks like its water"),
    "land_deepsand": dict(short="Deep sand", notice="a patch of deep sand with a colonist on it", s="land",
                          after="many_waters", caps=["L04"],
                          terrain=[("RM_DeepSand", 2, 3, 12, 8)], pawns=[("Colonist", 8, 7, "player", "drafted")],
                          try_=["undraft him: idle colonists never go swimming in sand for fun", "hover: the walk cost"],
                          look="weak spot: deep sand that reads as ordinary sand"),
    "land_shores": dict(short="Liquid shores on new maps", notice="shores come only on newly generated maps; here a "
                        "boiling pool for the steam", terrain=[("RM_WaterBoilingShallow", 3, 4, 10, 6)],
                        try_=["unpause: steam rises; hover the air over it: hotter"],
                        look="weak spot: no steam; the air over boiling water no warmer"),
    "land_swale": dict(short="A swale turns sand to soil", notice="a swale on sand beside a water canal",
                       terrain=[("Sand", 0, 0, 16, 14), ("WaterDeep", 0, 6, 3, 3)], dig=[(3, 7, 12, 1, 2)],
                       build=[("RM_Swale", 8, 9, None, None)],
                       try_=["unpause for days: the sand beside the swale slowly turns to soil"],
                       look="weak spot: soil turning far from the swale; nothing changing after days"),
    "land_panning": dict(short="Panning and the sluice box", notice="a sluice box across the bank edge and a panning "
                         "spot beside the shallow margin (painted river: see map R for the real one)",
                         terrain=[("WaterMovingShallow", 0, 3, 16, 2), ("WaterMovingChestDeep", 0, 5, 16, 4),
                                  ("WaterMovingShallow", 0, 9, 16, 2)],  # = RIVER below
                         build=[("RM_SluiceBox", 4, 11, None, None), ("RM_PanningSpot", 11, 11, None, None)],
                         marks=[(4, 13, "sluice"), (11, 13, "pan here")],
                         try_=["unpause a day: the sluice washes a little ore onto its bank end",
                               "a miner pans at the spot: mostly nothing, sometimes a few units"],
                         look="weak spot: ore on the water end; compare with map R, where the river is real"),
    "land_settings": dict(short="Every mechanic has a switch", notice="nothing to see here: open Options > Mod Settings > "
                          "FlowWorks", try_=["switch everything off: the mod still digs dry canals",
                                             "a master switch off greys its dependents and keeps their values"],
                          look="weak spot: a switch that changes nothing; all off and the dig order gone"),
}

# The river works on the MAIN map are LOOKS only: painted river terrain has no current (only map generation writes
# the flow map), so nothing here pools, catches, breaches or carries. The mechanics are map R (review_map_rivers.py).
RIVER = [("WaterMovingShallow", 0, 3, 16, 2), ("WaterMovingChestDeep", 0, 5, 16, 4), ("WaterMovingShallow", 0, 9, 16, 2)]
RIVERS = [
    dict(id="river_ford", caps=["L09"], short="Ford stones (look)", notice="a shallow river with a line of ford stones "
         "across; painted, so no current",
         terrain=[("WaterMovingShallow", 0, 3, 16, 8), ("RM_FordStones", 7, 3, 1, 8)],
         try_=["judge the stones; the crossing itself is on map R"],
         look="weak spot: stones that read as dry ground; a seam at the stones' edge"),
    dict(id="river_works_looks", caps=["L10", "L11", "L13"], short="Bank works (look)",
         notice="a weir, a stake line, a silt trap and ferry posts on a painted river: no current here",
         terrain=RIVER, build=[("RM_BankWeir", 2, 11, None, None), ("RM_SiltTrap", 5, 11, None, None)]
         + [("RM_BankStake", x, 11, None, None) for x in (7, 8, 10, 11)]
         + [("RM_FerryPost", 14, 2, None, None), ("RM_FerryPost", 14, 11, None, None)],
         marks=[(2, 13, "weir"), (5, 13, "silt"), (9, 13, "stakes"), (14, 13, "ferry")],
         try_=["judge the drawings; every one of them WORKS only on map R"],
         look="weak spot: a rope drawn across land or not at all; a weir whose wet end sits on the bank"),
]
for _r in RIVERS:
    _r["s"] = "rivers"
    SETUPS[_r["id"]] = _r

# Gallery order: rows top to bottom; a row is one or more sections. flow_drains first in its row (it needs the map's
# west edge). land_rivers is shown as the RIVERS stations here plus the whole of map R.
ROWS = [
    ("flow+dig", ["flow", "dig"]),
    ("fire+catch", ["fire", "catch"]),
    ("hold+look", ["hold", "look"]),
    ("carry+land+rivers", ["carry", "land", "rivers"]),
]
FIRST = {"flow_drains"}
RESERVED = [FREE["rect"]]


def extras():
    """Stations that are not a feature-sheet FEATURE: a setup carrying its own section `s` (river looks included)."""
    return {k: v for k, v in SETUPS.items() if v.get("s")}


def feature_order(m):
    by = {}
    for f in m.FEATURES:
        if f["id"] == "land_rivers":
            continue
        by.setdefault(f["s"], []).append(f["id"])
    by["flow"] = [i for i in by["flow"] if i in FIRST] + [i for i in by["flow"] if i not in FIRST]
    by["rivers"] = []
    for k, v in extras().items():               # an extra sits right after its `after` (neighbours differ in one thing)
        lst = by.setdefault(v["s"], [])
        a = v.get("after")
        lst.insert(lst.index(a) + 1 if a in lst else len(lst), k)
    return by


def _overlap(a, b, pad=0):
    return not (a[0] + a[2] + pad <= b[0] or b[0] + b[2] + pad <= a[0] or a[1] + a[3] + pad <= b[1] or b[1] + b[3] + pad <= a[1])


def extra_status(m, setup, capd, rows):
    """An extra station's status, DERIVED like a feature's: from its caps through feature_status, or (a mechanism the
    feature sheet predates) from its disk probes through the sheet's own derive_status -> never typed."""
    if setup.get("caps"):
        st = m.feature_status(dict(caps=setup["caps"]), capd)[0]
        miss = [m.PLAIN.get(c, capd[c]["label"]) for c in setup["caps"] if capd[c]["d"]["status"] in ("NOT BUILT", "PARTIAL")]
        return st, miss
    d = m.derive_status(dict(probes=setup.get("probes", []), rows=[]), rows)
    st = {"PROVEN-LIVE": m.F_WORKS, "BUILT-UNPROVEN": m.F_BUILT, "PARTIAL": m.F_PARTLY}.get(d["status"], m.F_NOT)
    miss = [p for p, ok in d["probes"] if not ok]       # probe specs are code; the owner reads a plain count
    return st, (["%d of its %d parts not found on disk yet" % (len(miss), len(d["probes"]))] if miss else [])


def station_list(m=None, st=None, capd=None, rows=None):
    """[station dict] in number order. Station = feature (or extra) + setup + derived status + origin."""
    if st is None:
        m, st, capd = derive(m)
    if rows is None:
        rows = m.latest_result()[1]
    feats = {f["id"]: f for f in m.FEATURES}
    by = feature_order(m)
    sec_name = dict(m.SECTIONS)
    sec_name["rivers"] = "9 · Rivers: the bank works as they look (they work on map R)"
    S = []
    n = 0
    j = 0
    for rname, secs in ROWS:
        ids = [(s, i) for s in secs for i in by.get(s, [])]
        i = 0
        while ids:
            x, z = GX0 + PITCH_X * i, TOP_Z - PITCH_Z * j
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
            else:
                status, missing = extra_status(m, setup, capd, rows)
                title = setup["short"]
                say = ""
            S.append(dict(n=n, id=fid, section=sec, section_name=sec_name.get(sec, sec), row=rname, origin=(x, z),
                          size=(SW, SH), status=status, title=title, say=say, missing=missing,
                          short=setup.get("short", fid), notice=setup.get("notice", ""), try_=setup.get("try_", []),
                          look=setup.get("look", ""), setup=setup, placeholder=(status == "not")))
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
        if not s["placeholder"] and not (s["try_"] and s["look"]):
            probs.append("station %d (%s): no how-to-poke or what-to-look-for line" % (s["n"], s["id"]))
        if not s["setup"]:
            probs.append("station %d (%s): no setup" % (s["n"], s["id"]))
        u = s["setup"]
        # the build's sweep removes every non-colonist outside a keep rect: such a pawn without keep=True is killed
        if any(p[3] != "player" for p in u.get("pawns", [])) and not u.get("keep"):
            probs.append("station %d (%s): a non-colonist pawn but no keep=True (the sweep kills it)" % (s["n"], s["id"]))
        cells = []
        for k in ("terrain", "dig", "fluid", "roof", "designate"):
            for r in u.get(k, []):
                rr = r[1:5] if isinstance(r[0], str) else r[:4]
                cells += [(rr[0], rr[1]), (rr[0] + rr[2] - 1, rr[1] + rr[3] - 1)]
        for k in ("build", "spawn", "stuffed", "style", "hostile", "build_after"):
            cells += [(r[1], r[2]) for r in u.get(k, [])]
        for k in ("hose_flow", "hose_reelin"):
            cells += [(r[0], r[1]) for r in u.get(k, [])]
        cells += [c for r in u.get("hose_order", []) for c in ((r[0], r[1]), (r[2], r[3]))]
        cells += [c for r in u.get("hose_trail", []) for c in [(r[0], r[1])] + list(r[2])]
        for k in ("tank", "pump", "ladder", "flood_trigger", "charge"):
            cells += [(r[0], r[1]) for r in u.get(k, [])]
        # GSS_CORD_SILENCE_PHANTOM_SPARK (owner 2026-10-16): a battery is built at 0 Wd, so a station whose only power is
        # a battery is unpowered unless the battery is charged or a generator stands beside it
        bats = {(r[1], r[2]) for r in u.get("build", []) if r[0] == "Battery"}
        gens = [r for r in u.get("build", []) if "Generator" in r[0]]
        charged = {(r[0], r[1]) for r in u.get("charge", [])}
        if bats and not gens and not bats <= charged:
            probs.append("station %d (%s): battery at %s starts empty and no generator powers it (add charge=)"
                         % (s["n"], s["id"], sorted(bats - charged)))
        for c in charged - bats:
            probs.append("station %d (%s): charge at %s names no battery built there" % (s["n"], s["id"], c))
        dug = {(x, z) for r in u.get("dig", []) for x in range(r[0], r[0] + r[2]) for z in range(r[1], r[1] + r[3])}
        for r in u.get("flood_trigger", []):
            if not any((r[0] + dx, r[1] + dz) in dug for dx, dz in ((0, 0), (0, 1), (1, 0), (0, -1), (-1, 0))):
                probs.append("station %d (%s): flood trigger at %s has no dug cell at or beside it (aimed at nothing)"
                             % (s["n"], s["id"], (r[0], r[1])))
        cells += [c for r in u.get("hose", []) for c in ((r[0], r[1]), (r[2], r[3]))]
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
        "columns: depth D1 to D4   |   rows: dry, water, tar, scorched (soil then granite), top two rows more liquids   |   "
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
        # REVIEW SIGNS (owner 2026-10-15: "text signs ... to tell me what to DO at each station"): the first poke and
        # the weak spot under the status word; zoomed out only the status word draws (modcheck/reviewmap)
        sign = STATUS_WORD[s["status"]] if s["placeholder"] else RM.weak_spot_sign(
            STATUS_WORD[s["status"]], "", (s["try_"] or [""])[0], s["look"])
        add(x + SW // 2, z + SH + 1, "%d  %s" % (s["n"], s["short"]), sign, col[s["status"]], "small")
        low = ("NOT BUILT yet: " + (s["say"] or s["title"])) if s["placeholder"] else s["notice"]
        if low:
            # owner walk 2026-10-16: seen from the next row up, these lines floated with no number ("two stations with
            # no numbers and nothing built"); the number card is north of the body, this line south of it. So every
            # line carries its station's number.
            for k, part in enumerate(wrap(low, 46)[:3]):
                add(x + SW // 2, z - 1 - k, "%d: %s" % (s["n"], part), "", CREAM, "tiny")
        for dx, dz, text in s["setup"].get("marks", []):
            add(x + dx, z + dz, text, "", RUST, "tiny")
    fx, fz, fw, fh = FREE["rect"]
    add(fx + fw // 2, fz + fh + 1, "F  FREE AREA", "steel, components, wood, granite, chemfuel, bottles (south edge); a pond "
        "(east). Orders: Dig canal / Fill in canal; Structure: ladder, ramp, spikes, covers, doors; Pipe networks: tanks, "
        "pipe, hose reel", RUST)
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


def vis_sign_ops(doc):
    """One sign book per VISUALS plot (keys V1..Vn, walking order), on the gap row just north of the plot's west corner,
    where its tiny label already sits. The standard (biome_review_save_standard.md §7) wants a book at every station."""
    L = []
    for i, v in enumerate((doc or {}).get("stations", []), 1):
        ox, oz = VIS.origin_of(v, *VIS_BASE)
        s = v["setup"]
        name = "Pit D%d %s %s" % (s["pit"]["depth"], VIS.GROUNDS[s["ground_kind"]]["words"], v["id"].split("_")[1])
        L.append(RM.sign_book(ox, oz + VIS.PLOT_H, "V%d" % i, name[:24], v["title"], v["what_to_notice"],
                              "zoom in and compare this pit with its row neighbours",
                              "does this pit read right for its depth, ground and fill?",
                              more="Key sheet: visuals block V (%s)." % v["id"]))
    return L


def sign_ops(S, doc=None):
    """The signs that live IN the save (BENCH 2026-10-15: they must survive a plain load with no agent): one vanilla
    Novel a built station on the gap cell north of its NW corner (modcheck/reviewmap.sign_book; jawa/review_sign).
    Mouse over it for the DO line, press i for the whole sign. NOT BUILT placeholders get none. With `doc`, the
    visuals block's plots get theirs too (vis_sign_ops)."""
    L = vis_sign_ops(doc)
    for s in S:
        if s["placeholder"]:
            continue
        x, z = s["origin"]
        L.append(RM.sign_book(x, z + SH, s["n"], s["short"], "%s. %s" % (STATUS_WORD[s["status"]], s["notice"]),
                              "", (s["try_"] or [""])[0], RM.weak_decide(s["look"]),
                              more="Key sheet: station %d." % s["n"]))
    return L


# ------------------------------------------------------------------------------------------------ live build
def visual_verdict(p, want_f, scorched, rows, strength, n_player_pawns):
    """One visuals station: True / False, or None when the scorch read was blind (ProofScorchAt refused or gave no
    "strength=", e.g. static_call refused in campaign) -- a missing reading is never "not scorched"."""
    ds = sorted({c.get("d") for c in rows})
    fs = sorted({c.get("f") for c in rows})
    built = len(rows) == p["w"] * p["h"] and ds == [p["depth"]] and fs == [want_f] and n_player_pawns >= 1
    if strength is None:
        return False if not built else None
    return built and (strength > 0) == bool(scorched)


def gallery_verdict(placeholder, dig_ok, missing, want_kinds, got_kinds):
    """One gallery station: True / False, or None for a placeholder (NOT BUILT): nothing was read, so it is not
    "verified as built". Pawns are matched by KIND (multiset), not by a head count of whatever stands there."""
    if placeholder:
        return None
    from collections import Counter
    short = Counter(want_kinds) - Counter(got_kinds)
    return bool(dig_ok and not missing and not short)


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
                # timeException=True: noon pin for a review shot; nothing simulated (safe-advance gate)
                self.call("jawa/time_set_ticks", ticks=clk["ticksGame"] + add, timeException=True)
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
                # a reel's hose leaves through its WEST outlet: the straight lead-out needs open, unfogged ground in the
                # gap west of the station (2026-10-16: natural rock there refused two of station 63's three lays)
                if any(s["setup"].get(k) for k in ("hose", "hose_order", "hose_trail")):
                    out.append((s["origin"][0] - (PITCH_X - SW), s["origin"][1] - 1, PITCH_X - SW, SH + 3))
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
        blind = 0
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
            good = visual_verdict(p, want_f, s["scorched"], rows, strength, len(pw))
            self.verify[v["id"]] = dict(ok=good, cells=len(rows), d=ds, f=fs, want=(p["depth"], want_f),
                                        scorch=strength if strength is not None else "UNMEASURED: %s" % sc[:120],
                                        pawns=len(pw))
            ok += good is True
            blind += good is None
        self.say("visuals verified: %d of %d stations as built%s" % (
            ok, len(doc["stations"]), "; %d UNMEASURED (no scorch reading)" % blind if blind else ""))
        return ok

    # ---- gallery
    def build_gallery(self, S):
        B = self.B
        for s in S:
            ox, oz = s["origin"]
            u = s["setup"]
            g = lambda x, z: (ox + x, oz + z)  # noqa: E731
            if u.get("needs_def") and not (B.call("jawa/get_defs", defs="ThingDef/" + u["needs_def"]) or {}).get("foundCount"):
                s["absent"] = True          # a def another mod brings, not loaded on this tier: say so, read nothing
                self.notes.append("station %d (%s): %s is not loaded on this mod list; empty pad" % (
                    s["n"], s["id"], u["needs_def"]))
            if s["placeholder"] or s.get("absent"):
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
            for d, x, z, rot, stuff in u.get("hostile", []):
                kw = dict(ops="%s:%d,%d" % ((d,) + g(x, z)) + ("" if rot is None else ",%d" % rot), faction="hostile",
                          wipeExisting=False)
                if stuff:
                    kw["stuff"] = stuff
                if self.call("jawa/build_batch", **kw).get("survived") == 0:
                    self.notes.append("station %d: their %s not built" % (s["n"], d))
            for d, x, z, stuff in u.get("spawn", []):
                # walk 2026-10-15: spawn_batch takes no faction, so a spawned ladder/cover/sluice was unowned ("Claim"
                # button, no Ladder button: st.36 could not be raised). Build it as the player's first, as a player has it;
                # spawn_batch stays the fallback for what build_batch refuses (e.g. a cell build_batch will not accept).
                kw = dict(ops="%s:%d,%d" % ((d,) + g(x, z)), faction="player", wipeExisting=False)
                if stuff:
                    kw["stuff"] = stuff
                if (self.call("jawa/build_batch", **kw) or {}).get("survived"):
                    continue
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
            for d, x, z, n_, stuff in u.get("stuffed", []):
                kw = dict(ops="%s:%d,%d,%d" % ((d,) + g(x, z) + (n_,)))   # the third op field is the stack size
                if stuff:
                    kw["stuff"] = stuff
                self.call("jawa/spawn_batch", **kw)
            self.stage(s, u, g)
        self.late_hoses(S)
        self.say("gallery: %d stations placed" % len(S))

    def static(self, n, typ, method, args):
        """A staging proof call; a REFUSED/FAIL answer lands in the notes (the station is then not as its card says)."""
        r = self.call("jawa/static_call", type=typ, method=method, args=args)
        res = str(r.get("result", ""))
        if not res or res.startswith(("REFUSED", "FAIL", "UNMEASURED")):
            self.notes.append("station %s %s(%s): %s" % (n, method, args, res[:120] or json.dumps(r)[:120]))
        return res

    def hose_probe(self, cmd, wait_s=20.0):
        """HoseProbe's request/serial channel (validation_hose.H.hp): answered on the next frame, paused or not."""
        hp = "RimMandrake.FlowWorks.Hose.HoseProbe"
        before = self.B.call("jawa/mod_settings_field", typeName=hp, action="get", field="serial").get("value")
        self.B.call("jawa/mod_settings_field", typeName=hp, action="set", field="request", value=cmd)
        t0 = time.time()
        while time.time() - t0 < wait_s:
            if self.B.call("jawa/mod_settings_field", typeName=hp, action="get", field="serial").get("value") != before:
                return str(self.B.call("jawa/mod_settings_field", typeName=hp, action="get", field="result").get("value"))
            time.sleep(0.25)
        self.notes.append("hose probe %s: timed out (no frame serviced it)" % cmd)
        return ""

    def hose_cmd(self, n, cmd):
        res = self.hose_probe(cmd)
        try:
            ok = json.loads(res).get("success") is not False
        except (ValueError, AttributeError):
            ok = False
        if not ok:
            self.notes.append("station %d hose %s: %s" % (n, cmd, res[:120]))
        return ok

    def late_hoses(self, S):
        """After every station is placed (the hose stations from the GSS walk, 2026-10-15): flow the Plump hoses, the
        Filling ones half a transition later (frozen mid-swell), reel in the reelin ones, then build the build_after walls
        and give the hoses 60 ticks to answer. The ticks run the whole map, so this is one pass, not one per station."""
        todo = [s for s in S if not (s["placeholder"] or s.get("absent"))
                and any(s["setup"].get(k) for k in ("hose_flow", "hose_reelin", "build_after"))]
        if not todo:
            return
        B = self.B

        def g(s, x, z):
            return (s["origin"][0] + x, s["origin"][1] + z)
        B.ticks(2)
        for s in todo:
            for rx, rz, state in s["setup"].get("hose_flow", []):
                if state == "Plump":
                    self.hose_cmd(s["n"], "flow:%d,%d=on" % g(s, rx, rz))
        B.ticks(HOSE_TRANSITION_TICKS - HOSE_TRANSITION_TICKS // 2 + 5)
        for s in todo:
            for rx, rz, state in s["setup"].get("hose_flow", []):
                if state == "Filling":
                    self.hose_cmd(s["n"], "flow:%d,%d=on" % g(s, rx, rz))
        B.ticks(HOSE_TRANSITION_TICKS // 2)
        for s in todo:
            for rx, rz in s["setup"].get("hose_reelin", []):
                self.hose_cmd(s["n"], "reelin:%d,%d" % g(s, rx, rz))
        B.ticks(2)
        walls = 0
        for s in todo:
            for d, x, z, rot, stuff in s["setup"].get("build_after", []):
                kw = dict(ops="%s:%d,%d" % ((d,) + g(s, x, z)) + ("" if rot is None else ",%d" % rot), faction="player",
                          wipeExisting=False)
                if stuff:
                    kw["stuff"] = stuff
                if self.call("jawa/build_batch", **kw).get("survived") == 0:
                    self.notes.append("station %d: build_after %s not built" % (s["n"], d))
                walls += 1
        if walls:
            B.ticks(60)

    def gizmo_cycle(self, n, cell, prefix, want, max_clicks=4):
        """Press the thing's own button until its label reads `want` (liquid_checks.gizmo_cycle's route: select by
        click, list the gizmos, execute by id). The button's own action runs, side effects included -- a raw field
        write would skip them (ProofLadder sets `raised` without SetRaised's path/mesh refresh)."""
        B = self.B
        B.call("rimworld/clear_selection")
        B.call("rimworld/click_cell", x=cell[0], z=cell[1])
        try:
            for _ in range(max_clicks + 1):
                gz = (B.call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
                g = next((q for q in gz if str(q.get("label") or "").startswith(prefix)), None)   # str or tuple
                if g is None:
                    self.notes.append("station %s: no %r button at %s (saw %s)" % (
                        n, prefix, cell, [q.get("label") for q in gz][:8]))
                    return False
                if g.get("label") == want:
                    return True
                r = B.call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id"))
                if not isinstance(r, dict) or r.get("success") is False:
                    self.notes.append("station %s: %r button refused: %s" % (n, prefix, json.dumps(r)[:120]))
                    return False
            self.notes.append("station %s: %r never read %r" % (n, prefix, want))
            return False
        finally:
            B.call("rimworld/clear_selection")

    def stage(self, s, u, g):
        """Frozen mid-states. Contents through the proof surface (ProofTank: stock only, in Store), every mode and
        state through the player's own button (gizmo_cycle), so the save holds what a player's click leaves."""
        n = s["n"]
        for x, z, mode, liquid, units in u.get("tank", []):
            self.static(n, TANK, "ProofTank", "%d,%d;Store;%s;%d" % (g(x, z) + (liquid, units)))
            if mode != "Store":
                self.gizmo_cycle(n, g(x, z), "Job:", "Job: " + mode)
        for x, z, on_clock, spill, cap in u.get("flood_trigger", []):
            self.static(n, BIOME_MC, "PlaceFloodTrigger", "%d,%d|%s|%s|%d" % (g(x, z) + (on_clock, spill, cap)))
        for x, z in u.get("charge", []):   # fill the battery (a built battery holds 0 Wd); GSS's stage op owns the call
            r = self.B.call("jawa/gss_stage", ops="kind=gss_charge|x=%d|z=%d" % g(x, z))
            if not isinstance(r, dict) or r.get("success") is not True:
                self.notes.append("station %s: battery at %s not charged: %s" % (n, (x, z), json.dumps(r)[:160]))
        for x, z, mode in u.get("pump", []):
            self.gizmo_cycle(n, g(x, z), ("Pouring", "Drawing"),
                             "Pouring into the channel" if mode == "pour" else "Drawing into the tank")
        for x, z, op in u.get("ladder", []):
            self.gizmo_cycle(n, g(x, z), "Ladder", "Ladder up" if op == "raise" else "Ladder down")
        if any(u.get(k) for k in ("hose", "hose_order", "hose_trail")):
            self.B.ticks(1)     # the hose layer's whole-map CordWorld is cached per TICK: paused, it still sees the pre-clear map
        for rx, rz, x, z, end in u.get("hose", []):
            (ax, az), (bx, bz) = g(rx, rz), g(x, z)
            for cmd in ["lay:%d,%d,%d,%d" % (ax, az, bx, bz)] + (["end:%d,%d=%s" % (ax, az, end)] if end else []):
                res = self.hose_probe(cmd)
                try:
                    ok = json.loads(res).get("success") is not False
                except (ValueError, AttributeError):
                    ok = False
                if not ok:
                    self.notes.append("station %d hose %s: %s" % (n, cmd, res[:120]))
        for rx, rz, x, z in u.get("hose_order", []):
            self.hose_cmd(n, "order:%d,%d=deploy:%d,%d" % (g(rx, rz) + g(x, z)))
        for rx, rz, cells in u.get("hose_trail", []):
            self.hose_cmd(n, "settrail:%d,%d=dropped;%s" % (g(rx, rz) + (";".join("%d,%d" % g(*c) for c in cells),)))
        for d, x, z, style in u.get("style", []):
            th = self.B.call("jawa/list_things", defName=d, rect="%d,%d,1,1" % g(x, z), limit=3).get("things") or []
            if not th:
                self.notes.append("station %d style: no %s at %s" % (n, d, g(x, z)))
                continue
            r = self.call("jawa/set_thing_props", thing=str(th[0].get("id") or th[0].get("thingId")), style=style)
            if "style" not in (r.get("changed") or []):
                self.notes.append("station %d style %s not written: %s" % (n, style, json.dumps(r)[:120]))

    def gallery_pawns(self, S):
        for s in S:
            if s["placeholder"] or s.get("absent"):
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
        """Per station: dug cells and their depths as specified, buildings present (list_things in the footprint), the
        pawn kinds asked for. A placeholder records verified=None (nothing read), never "as built"."""
        B = self.B
        ok = unread = 0
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
            want_kinds = [r[0] for r in u.get("pawns", [])] if not s["placeholder"] else []
            got_kinds = [q.get("kind") or q.get("kindDef") for q in pw]
            good = gallery_verdict(s["placeholder"] or s.get("absent", False), dig_ok, miss, want_kinds, got_kinds)
            self.verify[s["n"]] = dict(ok=good, dug=len(got), want_dug=len(want), missing=miss, pawns=sorted(map(str, got_kinds)),
                                       want_pawns=sorted(want_kinds))
            ok += good is True
            unread += good is None
        self.say("gallery verified: %d of %d stations as built (%d placeholders or absent-def stations not read)" % (
            ok, len(S) - unread, unread))
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
            s = next((s for s in S if str(s["n"]) == which), None)
            if s is None:
                raise SystemExit("--goto %s: unknown station; valid: V, F, S0, M, %s" % (
                    which, ", ".join(str(s["n"]) for s in S)))
            x, z, ww, h = s["origin"][0] - 2, s["origin"][1] - 2, SW + 4, SH + 5
        return self.B.call("rimworld/frame_cell_rect", x=x, z=z, width=ww, height=h, paddingCells=2)


# ------------------------------------------------------------------------------------------------ key sheet
VIS_STATES = ("dry", "water", "tar", "scorched") + VIS.EXTRAS   # every state the V block holds, extras included
NO_SAVE = "(no keeper saved yet: build, then --save)"
RIVER_SAVE_HINT = "RM_fw_review_rivers_<date>"


def fill_tier(fill, depth):
    """Mirror of RM_ExcavationDepth.FillTier: 0 none, 1 trace, 2 half, 3 brim."""
    if fill <= 0 or depth <= 0:
        return 0
    r = fill / depth
    return 1 if r <= 0.34 else 2 if r <= 0.67 else 3


def build_exit(vis_ok, n_vis, gal_ok, n_gal):
    """-> (rc, text). rc 0 only when every verify that ran read every station as built; a verify that ran short
    (failed or UNMEASURED stations) is rc 1, so --build cannot read as success on an exit code alone."""
    parts, bad = [], False
    for name, got, want in (("visuals", vis_ok, n_vis), ("gallery", gal_ok, n_gal)):
        if got is None:
            parts.append("%s not run" % name)
            continue
        parts.append("%s %d/%d" % (name, got, want))
        bad = bad or got < want
    return (1 if bad else 0), ", ".join(parts)


def keysheet(S, st, doc, m, live=None, save=None):
    os.makedirs(OUT, exist_ok=True)
    E = html.escape
    tot = {k: sum(1 for s in S if s["status"] == k) for k in STATUS_WORD}
    md = ["# FlowWorks review map - key sheet", "",
          "Load the save in RimWorld (Load game > %s). The game is paused, god mode is on, clear weather, noon, "
          "Peaceful. Mod Settings are the shipped defaults." % (save or NO_SAVE), "",
          "Each station is labelled in the world with its number, a short name, its status and what to look at. "
          "Status colours: green = works in game, blue = built, not yet seen, gold = partly built, rust = not built.", "",
          "%d stations: %s." % (len(S), ", ".join("%d %s" % (tot[k], STATUS_WORD[k].lower()) for k in STATUS_WORD)), "",
          "## V - pits: what they look like (south-west block)", "",
          "Columns: depth 1 to 4, left to right. Rows from the bottom: dry in soil, dry in granite, water in soil, water "
          "in granite, tar in soil, tar in granite, scorched in soil, scorched in granite; the top two rows are seven more "
          "liquids in soil at depth 3. A colonist stands in the near row of every pit so you can see how far the near bank hides "
          "him.", ""]
    if doc:
        for state in VIS_STATES:
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
                md += ["**Poke it:**", ""] + ["- " + x for x in s["try_"]] + [""]
            if s["look"]:
                md += ["**Look for:** " + s["look"], ""]
            if s["missing"]:
                md += ["**Not built yet in this feature:** " + "; ".join(s["missing"]), ""]
    md += ["## R - map R: the river works on a real river", "",
           "River works only work on a real river: painted river ground has no current. So the second save (%s) holds "
           "a river map with these stations, each placed where the river suits it; ask and the agent frames any one." % (
               RIVER_SAVE_HINT), ""]
    for k, rs in enumerate(RV.STATIONS):
        md += ["### R%d. %s" % (k + 1, rs["short"]), "", "**Look at:** " + rs["notice"], "", "**Poke it:**", ""]
        md += ["- " + x for x in rs["try_"]] + ["", "**Look for:** " + rs["look"], ""]
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
                    body += "<p><b>Poke it:</b></p><ul>%s</ul>" % "".join("<li>%s</li>" % E(x) for x in s["try_"])
                if s["look"]:
                    body += "<p class='look'><b>Look for:</b> %s</p>" % E(s["look"])
                if s["missing"]:
                    body += "<p class='miss'><b>Not built yet here:</b> %s</p>" % E("; ".join(s["missing"]))
            cs.append("<section class='st'><div class='num'>%d</div><div><h3>%s</h3><span class='badge' "
                      "style='background:%s'>%s</span>%s</div></section>" % (s["n"], E(s["short"]), col[s["status"]],
                                                                             E(STATUS_WORD[s["status"]].capitalize()), body))
        cards.append("<h2>%s</h2><div class='grid'>%s</div>" % (E(name), "".join(cs)))
    vis = ""
    if doc:
        vis = "<ul>%s</ul>" % "".join("<li><b>%s:</b> %s</li>" % (E(state), E(v["what_to_notice"])) for state in
                                       VIS_STATES for v in
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
.look{color:var(--teal)}.box{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px}ul{margin:4px 0;padding-left:20px}
</style></head><body>
<h1>FlowWorks &mdash; review map</h1>
<p class="sub">Load <b>%s</b> in RimWorld. Paused, god mode on, clear weather, noon, Peaceful, Mod Settings at shipped defaults. Every station is labelled in the world with its number, name, status and what to look at.</p>
<div class="box">%s<br>%d stations: %s.</div>
<h2>V &mdash; pits: what they look like</h2><div class="box">South-west corner of the map. Columns: depth 1 to 4. Rows from the bottom: dry (soil, then granite), water, tar, scorched; top two rows: seven more liquids at depth 3. A colonist stands in each pit's near row.%s</div>
%s
<h2>R &mdash; map R: the river works on a real river</h2><div class="box">River works only work on a real river: painted river ground has no current. The second save holds a river map with these stations, each placed where the river suits it.</div><div class='grid'>%s</div>
<h2>F &mdash; free area</h2><div class="box">Round your colonists in the middle of the map: materials, bottles and a pond. Dig, fill and build here yourself.</div>
<h2>S0 and M</h2><div class="box">S0, west of the free area, is the status board. M, below it, lists the look features still drawn with borrowed or missing art.</div>
</body></html>""" % (E(save or NO_SAVE), legend, len(S),
                      E(", ".join("%d %s" % (tot[k], STATUS_WORD[k].lower()) for k in STATUS_WORD)), vis, "\n".join(cards),
                      "".join("<section class='st'><div class='num'>R%d</div><div><h3>%s</h3><p><b>Look at:</b> %s</p>"
                              "<p><b>Poke it:</b></p><ul>%s</ul><p class='look'><b>Look for:</b> %s</p></div></section>" % (
                                  k + 1, E(rs["short"]), E(rs["notice"]), "".join("<li>%s</li>" % E(x) for x in rs["try_"]),
                                  E(rs["look"])) for k, rs in enumerate(RV.STATIONS)))
    with open(os.path.join(OUT, "keysheet.html"), "w", encoding="utf-8") as f:
        f.write(page)


# ------------------------------------------------------------------------------------------------ map R
RIVERS_PLACED = os.path.join(OUT, "rivers_placed.json")


def rivers_main(R, a):
    """--rivers: build / label / frame / save map R on the CURRENT map (river_site.py makes the river map current).
    --build is NOT idempotent: it expects the fresh map river_site.py just founded (the ford stones repaint the river,
    so a second plan on the same map lands elsewhere); rebuild map R by running river_site.py again first."""
    if a.build:
        t0 = time.time()
        R.calm()
        R.say("map R: calm world (peaceful=%s)" % R.peaceful)
        placed, verify = RV.build(R, RM.label_line)
        RV.save_placed(RIVERS_PLACED, placed)
        R.B.call("jawa/clear_ui", all=True)
        if placed:
            RV.goto(R.B, placed, "R1")
        live = dict(rivers_ok=sum(1 for v in verify.values() if v["ok"]), placed=len(placed), verify=verify,
                    failed=[k for k, v in verify.items() if v["ok"] is False], notes=R.notes,
                    wall_s=round(time.time() - t0, 1))
        with open(os.path.join(REPO, "Transient", "fw_review_map_rivers_verify.json"), "w", encoding="utf-8") as f:
            json.dump(live, f, indent=1, default=str)
        R.say("map R DONE in %ss: %d/%d placed, %d read as built, failed %s; %d notes" % (
            live["wall_s"], len(placed), len(RV.STATIONS), live["rivers_ok"], live["failed"], len(R.notes)))
        rc = 0 if len(placed) == len(RV.STATIONS) and not live["failed"] else 1
        if not a.save:
            return rc
    else:
        rc = 0
    if a.save:
        R.call("rimworld/pause_game", pause=True)
        R.B.call("jawa/clear_ui", all=True)
        name = RM.free_save_name(a.name or "RM_fw_review_rivers_%s" % time.strftime("%Y%m%d"), RM.saves_stat())
        r = RM.save_keeper(R.B, name, signs=RV.label_ops(RV.load_placed(RIVERS_PLACED), RM.label_line))
        print("save %s: ok=%s new=%s changed=%s gone=%s signs=%s" % (name, r["ok"], r["new"], r["changed"], r["gone"],
                                                                     r.get("signs")))
        return rc if r["ok"] else 1
    placed = RV.load_placed(RIVERS_PLACED)
    if a.labels:
        print("labels: %s" % {k: v for k, v in RV.labels(R.B, placed, RM.label_line).items() if k in ("added", "refused")})
    if a.goto:
        print("framed %s: %s" % (a.goto, RV.goto(R.B, placed, a.goto).get("success")))
    return 0


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
    ap.add_argument("--rivers", action="store_true", help="act on map R (the river site map, made current by "
                    "northstar/river_site.py) instead of the main review map")
    ap.add_argument("--name", default=None)
    ap.add_argument("--log", default=os.path.join(REPO, "Transient", "fw_review_map_build_log.md"))
    a = ap.parse_args(argv)
    # walk 2026-10-15: under Windows python.exe the feature sheet's derivation reads the repo through \\wsl.localhost
    # and takes ~5 minutes, so a --goto took 5 minutes. --plan/--build (re)write a cache of the station list keyed on
    # this file's and the sheet's bytes; a plain --goto/--labels on Windows reads it, and falls back to deriving.
    nav_only = (a.goto or a.labels) and not (a.plan or a.build or a.save or a.clear or a.rivers)
    cached = _nav_cache_read() if nav_only and os.name == "nt" else None
    if cached:
        m, capd = None, None
        S, st = cached
    else:
        m, st, capd = derive()
        S = station_list(m, st, capd)
        _nav_cache_write(S, st)
    doc = visuals_doc()
    probs = layout_check(S, doc)
    if probs:
        print("LAYOUT PROBLEMS:\n  " + "\n  ".join(probs))
        return 2
    if a.plan:
        keysheet(S, st, doc, m)
        cov = COV.write(S)
        print("layout ok: %d gallery stations + %s visuals + %d river stations (map R) + S0/M/F; key sheet -> %s" % (
            len(S), len(doc["stations"]) if doc else "pending", len(RV.STATIONS), OUT))
        print("coverage: %d inventory items in %d features; %d features with no station, each with its reason; "
              "%d uncovered -> %s" % (cov["items"], cov["features"], cov["matrix"], cov["uncovered"], cov["path"]))
        return 1 if cov["uncovered"] else 0
    R = Review(RM.LiveBridge(), a.log if (a.build or a.rivers) else None)
    if a.rivers:
        return rivers_main(R, a)
    if a.clear:
        R.clear(S, doc, a.only)
        print("cleared")
        return 0
    live, rc = None, 0
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
        sg = RM.place_signs(R.B, sign_ops(S, doc if a.only in (None, "visuals") else None))
        if sg.get("count") != len(sign_ops(S, doc if a.only in (None, "visuals") else None)):
            R.notes.append("sign books: %s" % json.dumps({k: sg.get(k) for k in ("count", "refused", "message")})[:300])
        R.B.call("jawa/clear_ui", all=True)          # the debug log auto-opens on a fresh map
        R.goto(S, "V")
        live = dict(visuals_ok=vis_ok, gallery_ok=gal_ok, verify=R.verify, notes=R.notes, wall_s=round(time.time() - t0, 1))
        with open(os.path.join(REPO, "Transient", "fw_review_map_verify.json"), "w", encoding="utf-8") as f:
            json.dump(live, f, indent=1, default=str)
        keysheet(S, st, doc, m, live)
        rc, vtxt = build_exit(vis_ok, len(doc["stations"]) if doc else 0, gal_ok,
                              sum(1 for s in S if not (s["placeholder"] or s.get("absent"))))
        R.say("DONE in %ss; %s; %d notes (Transient/fw_review_map_verify.json)" % (live["wall_s"], vtxt, len(R.notes)))
        if not a.save:          # --build --save used to return here and skip the save silently
            return rc
    if a.save:
        R.sweep(R.keep_rects(S))
        R.call("rimworld/pause_game", pause=True)
        R.B.call("jawa/clear_ui", all=True)
        name = RM.free_save_name(a.name or "RM_fw_review_%s" % time.strftime("%Y%m%d"), RM.saves_stat())
        r = RM.save_keeper(R.B, name, signs=label_ops(S, st, doc, m))
        print("save %s: ok=%s new=%s changed=%s gone=%s signs=%s" % (name, r["ok"], r["new"], r["changed"], r["gone"],
                                                                     r.get("signs")))
        if r["ok"]:
            keysheet(S, st, doc, m, live, save=name)     # keep the agent block --build just wrote
            print("key sheet -> %s" % OUT)
        return rc if r["ok"] else 1
    if a.labels:
        r = R.labels(S, st, doc)
        print("labels: %s" % {k: r.get(k) for k in ("added", "refused", "count")})
    if a.goto:
        R.sweep(R.keep_rects(S))
        print("framed %s: %s" % (a.goto, R.goto(S, a.goto).get("success")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
