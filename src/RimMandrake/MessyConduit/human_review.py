"""human_review.py -- the Northstar "for the human" review map for Messy Conduit (owner, 2026-10-04).

    python.exe src/RimMandrake/MessyConduit/human_review.py --build [--fresh-map] [--style StarWarsJawa] | tr -d '\\r'
    python.exe src/RimMandrake/MessyConduit/human_review.py --goto 7 | tr -d '\\r'     # frame station 7 (0 = south gallery 1-18, N0 = north gallery 19-29, F = free area)
    python.exe src/RimMandrake/MessyConduit/human_review.py --style Cybertek | tr -d '\\r'   # switch every station's cable look
    python.exe src/RimMandrake/MessyConduit/human_review.py --labels | tr -d '\\r'     # re-pin the labels (after a load/restart)
    python.exe src/RimMandrake/MessyConduit/human_review.py --clear | tr -d '\\r'      # wipe the review region and its labels
    python3    src/RimMandrake/MessyConduit/human_review.py --plan                        # offline: layout check + key sheet only

Owner, 2026-10-04 (typed): *"a 'for the human' review configuration that is prepared for me to quickly look at a well
presented tilemap to assess what things look like, act like, etc. It should be set up for me to easily interact with,
explore, and see the various key combinations"*. Layout chosen by card: GALLERY PLUS FREE AREA.

What it builds (one quicktest map, the messyconduit tier, ~1-2 min):
  * calm world: weather Clear locked, clock pinned to noon, incident queue cleared, difficulty Peaceful, every
    non-colonist destroyed, research finished (masts need Electricity), god mode ON, game PAUSED, screenshot mode
    OFF (he needs the UI), the review region unfogged + unroofed + Soil.
  * a GALLERY of numbered stations in three labelled rows (cords / overhead lines / hoses), each a self-contained
    little grid with its own battery, labelled in world by jawa/review_label (the dev-only JawaBench labeller).
  * round 2 (owner notes 2026-10-04): a NORTH GALLERY (REGION2, above the colonists, out to the NE map corner) with
    stations 19-29 appended after 18 so his station numbers never move: power showpieces (row E), hose mazes (row F,
    judged by validation_hose.py through the hose hooks) and challenge configurations (row G). Some stations carry their
    own terrain (river), roof (mountain, roofed room), fog (mountain: re-hidden after the region is unfogged) and
    blueprints (half-built work for the save-load check).
  * a FREE AREA beside it: open soil, a charged power pad (2 solar + 3 batteries + a conduit stub to plug into),
    and stacks of steel, components and wood.
  * the key sheet: Transient/mc_human_review/KEYSHEET.md + keysheet.html (what each station is, what to notice,
    how to poke it).

Cable STYLE is one global Mod Setting (MessyConduitSettings.style), so four styles cannot stand side by side without a
change to the shipped mod; every station shows the current style and `--style X` (or Mod Settings) flips them all at once.

Idempotent: --build always clears the region first. Labels are process memory (never in a save): --labels re-pins them.
Reuses run_live.LiveBridge (the probe protocol) and placer._ops (the op-string shape).
"""
import argparse
import html
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NS = os.path.join(HERE, "northstar_matrix")
for p in (HERE, NS):
    if p not in sys.path:
        sys.path.insert(0, p)
import placer as PL  # noqa: E402  (numpy-free)

OUT = os.path.join(REPO, "Transient", "mc_human_review")
STYLES = ("StarWarsJawa", "StarWars", "ExtensionCord", "Cybertek")
# the Mod Settings names (owner review 2026-10-04 B19: labels only, the enum names / saved keys are unchanged)
LOOK = {"StarWarsJawa": "Scrapper", "StarWars": "Industrial", "ExtensionCord": "Modern", "Cybertek": "Futuristic"}
REGION = (8, 6, 228, 106)              # x, z, w, h: everything the review owns (quicktest colonists stand near 125,125)
REGION2 = (8, 140, 242, 110)           # round 2 stations 19+: north of the colonists, out to the map's NE corner (250x250)
REGIONS = {1: REGION, 2: REGION2}
MAP_SIZE = 250
SPAN_RANGE = 20                        # AerialSettings.maxSpan default
TAG = "mc_review"
ROWS = (("A", "Row A - floor cords", ""),
        ("B", "Row B - overhead lines", ""),
        ("C", "Row C - flexible hoses", ""),
        ("D", "Row D - hose crossings and parallel runs",
         "Hoses never branch (ruled by card): one hose is one line with two ends. Shown as the system does it today; there is no crossing piece."),
        ("E", "Row E - power showpieces (north gallery)",
         "Round 2 (owner notes 2026-10-04): a pole with many kinds of devices, a crowded electric room under an overhead line, cords through a fogged mountain."),
        ("F", "Row F - hose mazes (north gallery)",
         "Two routes out of a small maze, then the short one walled off after laying. validation_hose.py owns the pass/fail; this map shows it."),
        ("G", "Row G - challenge configurations (north gallery)",
         "Built to make visible bugs show: map edge, water, roof edge, longest/odd spans, a full pole, neighbouring nets, half-built work and save-load."))
GOLD, CREAM, TEAL, RUST = "#ffd27f", "#f2e6cf", "#8fd3c7", "#ff9a6b"

# ------------------------------------------------------------------------------------------------ the gallery
# Local coords (dx, dz) from the station origin, north up. Battery is 1x2 (rot 0: cells z, z+1); WoodFiredGenerator 2x2.
ROW_A, ROW_B, ROW_C, ROW_D = 86, 60, 40, 8   # origin z of each row
A_X = [20 + 24 * i for i in range(6)]
B_X = [20 + 40 * i for i in range(5)]
C_X = [20, 48, 76, 104]
D_X = [20, 50, 82]


def line(x0, x1, z):
    return [(x, z) for x in range(x0, x1 + 1)]


def station_list():
    S = []

    def st(n, row, x, z, w, h, title, what, notice, interact, **k):
        d = dict(n=n, row=row, origin=(x, z), size=(w, h), title=title, what=what, notice=notice, interact=interact,
                 conduit=[], walls=[], rock=[], devs=[], hostile=[], masts=[], links=[], cuts=[], hose=None, hoses=[])
        d.update(k)
        S.append(d)
        return d

    # ---- row A: floor cords
    base = dict(conduit=line(2, 9, 3), devs=[("Battery", (1, 3), 0, 1.0), ("Heater", (10, 3), None, None),
                                             ("StandingLamp", (5, 6), None, None)])
    st(1, "A", A_X[0], ROW_A, 12, 9, "POWERED LINE", "battery (full) -> conduit -> heater, plus a lamp plugged in from 3 cells away",
       ["no conduit graphic at all: only a loose, too-long cord lying between the nodes",
        "the plug cord from the lamp curls over to the run; the plug head sits at the lamp",
        "the cord ends in a plug at the heater and at the battery"],
       ["select the battery: the whole net's cords highlight", "open the power overlay (bottom-right): vanilla connector lines still draw",
        "unpause: the cord sways a little in the wind"], **base)
    st(2, "A", A_X[1], ROW_A, 12, 9, "UNPOWERED LINE", "the same build, battery EMPTY",
       ["the cord looks identical to station 1: power state changes nothing on an intact cord",
        "the lamp and heater are off (compare with 1)"],
       ["god mode: right-click the battery > dev: set charge, or drag a cord from station 1's grid over"],
       conduit=line(2, 9, 3), devs=[("Battery", (1, 3), 0, 0.0), ("Heater", (10, 3), None, None), ("StandingLamp", (5, 6), None, None)])
    st(3, "A", A_X[2], ROW_A, 12, 9, "CUT LINE", "powered line with ONE conduit cell missing in the middle (cell 6)",
       ["two cut ends: the battery side end is LIVE (sparks when unpaused), the far end is DEAD and lies limp",
        "no cord bridges the gap", "the far lamp and heater are off; the near lamp is on"],
       ["unpause at 1x: watch the live end spark", "build one conduit into the gap (god mode = instant): the cord rejoins",
        "deconstruct another conduit cell: a new pair of ends appears"],
       conduit=[c for c in line(2, 9, 3) if c != (6, 3)],
       devs=[("Battery", (1, 3), 0, 1.0), ("Heater", (10, 3), None, None), ("StandingLamp", (4, 6), None, None),
             ("StandingLamp", (8, 6), None, None)])
    st(4, "A", A_X[3], ROW_A, 12, 9, "TANGLED PILE", "a 3x3 block of conduit (9+ cells = a tangle) feeding three lamps and a heater",
       ["the block becomes one TANGLE: a mass of cables plugged into each other",
        "Scrapper / Industrial / Futuristic: the cables run into MANY + and T junction boxes, every box has cables in it, no power strips",
        "Modern: power strips, every strip with cables PLUGGED IN (a plug in each used socket), LEDs lit while the net is live",
        "every lamp's cord runs out of the pile"],
       ["--style ExtensionCord (Modern) vs StarWars (Industrial): strips vs junction boxes",
        "Modern: empty the battery (or cut the feed at cell 3): the strip LEDs go dark", "add conduit cells to the block: the pile grows"],
       conduit=line(2, 3, 3) + [(x, z) for x in range(4, 7) for z in range(2, 5)] + line(7, 9, 3),
       devs=[("Battery", (1, 3), 0, 1.0), ("Heater", (10, 3), None, None), ("StandingLamp", (3, 6), None, None),
             ("StandingLamp", (8, 6), None, None), ("StandingLamp", (8, 0), None, None)])
    st(5, "A", A_X[4], ROW_A, 13, 9, "DEVICES + PLUGS", "battery, an in-line power switch, a wood generator (unfuelled), lamps, heater",
       ["each device gets its own plug; the switch sits in-line with NO dark outline round its tile",
        "the generator hooks to the run on two cells",
        "a lamp 3 cells off the run still gets a cord"],
       ["flick the switch off (select it > toggle): everything past it goes dead", "refuel the generator: nothing changes visually"],
       conduit=line(2, 4, 3) + line(6, 10, 3),
       devs=[("Battery", (1, 3), 0, 1.0), ("PowerSwitch", (5, 3), None, None), ("WoodFiredGenerator", (7, 4), None, None),
             ("Heater", (11, 3), None, None), ("StandingLamp", (3, 6), None, None), ("StandingLamp", (10, 0), None, None)])
    st(6, "A", A_X[5], ROW_A, 14, 9, "WALL + ROCK ENTRIES", "a run passing under a steel wall and through a granite block; a branch ending inside the wall",
       ["where the cord meets the wall it goes into a STUB (a hole/grommet), and comes out the other side",
        "the rock tunnel has rock holes on both faces, drawn foreshortened (angled like the rock face), not straight down",
        "the branch ending in the wall is a wall terminal"],
       ["deconstruct a wall cell: the cord re-plans across the gap", "mine the granite: the tunnel opens"],
       conduit=line(1, 11, 3) + [(2, 4), (2, 5), (3, 5), (4, 5)], walls=[(4, z) for z in range(0, 8)],
       rock=[(x, z) for x in range(7, 10) for z in range(1, 6)],
       devs=[("Battery", (0, 3), 0, 1.0), ("Heater", (12, 3), None, None)])

    # ---- row B: overhead lines (masts are 4 cells tall; span range 20)
    st(7, "B", B_X[0], ROW_B, 30, 11, "MAST SPAN CHAIN", "battery -> scrap power mast -> mast -> mast -> lamp, two 12-cell overhead spans",
       ["the wires sag between masts and cast a ground shadow", "the far lamp is lit through the air",
        "the overhead cable is the look's own: thick dark scrap cable (Scrapper), thick BLACK cable (Industrial), thin black power line (Modern), sleek steel (Futuristic)",
        "the poles change with the look too: weathered wood (Scrapper), riveted steel with black insulators (Industrial), grey concrete with a transformer can (Modern), faceted steel with blade insulators (Futuristic)",
        "masts are 4 cells tall and 2 wide; the wire leaves from the insulator tips on the crossarm"],
       ["select a mast: Link wire / Unlink wire / Re-string gizmos", "build a new mast within 20 cells: it auto-links to the nearest",
        "unpause: spans sway"],
       devs=[("Battery", (1, 4), 0, 1.0), ("StandingLamp", (27, 6), None, None)],
       masts=[("RM_AerialMast", (2, 4)), ("RM_AerialMast", (14, 4)), ("RM_AerialMast", (26, 4))], links=[(0, 1), (1, 2)])
    st(8, "B", B_X[1], ROW_B, 30, 11, "LAMP MASTS", "a power mast feeding two scrap lamp masts over the air",
       ["each lamp mast is a light AND an anchor: it lights the ground under it", "the wire runs mast to lamp mast to lamp mast"],
       ["unlink the second span: that lamp mast goes dark", "build one more lamp mast within range"],
       devs=[("Battery", (1, 4), 0, 1.0)],
       masts=[("RM_AerialMast", (2, 4)), ("RM_AerialLampMast", (14, 4)), ("RM_AerialLampMast", (26, 4))], links=[(0, 1), (1, 2)])
    st(9, "B", B_X[2], ROW_B, 30, 11, "WALL BRACKET", "an overhead wire from a mast to a bracket bolted ON a shed wall, feeding a lamp INSIDE the shed",
       ["the bracket is drawn on the wall face, like a vanilla wall torch (it stands in the cell beside the wall, facing it); the look's own art per facing",
        "three spare brackets show the other facings: on the shed's west, east and south walls (outside, unlinked)",
        "the wire ENDS on the bracket's insulator; nothing lies on the ground outside",
        "the power goes through the wall into the shed (a conduit under the wall) and lights the lamp inside"],
       ["build another: Architect > Power > scrap wall bracket, point it AT a wall (vanilla wall-attachment placement)",
        "deconstruct the wall behind the bracket", "unlink and re-link the span from the mast's gizmo"],
       devs=[("Battery", (1, 4), 0, 1.0), ("StandingLamp", (14, 1), None, None)],
       walls=line(12, 16, 3) + [(12, z) for z in range(0, 3)] + [(16, z) for z in range(0, 3)] + line(13, 15, 0),
       conduit=[(14, 3), (14, 2)],    # round 2 (B21 join rule): bracket -> under its wall -> the lamp inside; no floor cord outside
       masts=[("RM_AerialMast", (2, 4)), ("RM_AerialWallBracket", (14, 4), 2), ("RM_AerialWallBracket", (11, 1), 1),
              ("RM_AerialWallBracket", (17, 1), 3), ("RM_AerialWallBracket", (13, -1), 0)],
       links=[(0, 1)])   # (def, cell, rot): rot points AT the wall; the linked one faces SOUTH, three unlinked show E / W / N
    st(10, "B", B_X[3], ROW_B, 30, 11, "CUT + FALLEN SPAN", "the station-7 chain with the SECOND span cut (as if blown by an explosion)",
       ["each cut half is ONE wire in the span's own cable: from the mast's insulator down to the break, where both halves meet on the ground",
        "the live downed end sparks; the far lamp is dark",
        "the first span still hangs and still carries power"],
       ["select the middle mast > Re-string cut wires: the span goes back up and the lamp relights",
        "god mode: drop an explosion under a span (dev tools) to cut another"],
       devs=[("Battery", (1, 4), 0, 1.0), ("StandingLamp", (27, 6), None, None)],
       masts=[("RM_AerialMast", (2, 4)), ("RM_AerialMast", (14, 4)), ("RM_AerialMast", (26, 4))], links=[(0, 1), (1, 2)], cuts=[(1, 2)])
    st(11, "B", B_X[4], ROW_B, 14, 11, "POWER TAP", "a power-tap clamp biting ANOTHER faction's grid (left, hostile battery), drained one-way into our lamp (right)",
       ["the crocodile clamp sits on their conduit; one of our cords is taped to it",
        "the two grids never merge (their net and ours stay separate)", "our lamp is lit with no power source of our own"],
       ["unpause and watch their battery drain", "Mod Settings > Messy Conduit > taps off: our lamp goes dark"],
       hostile=[("Battery", (2, 4), 0, 1.0), ("PowerConduit", (3, 4)), ("PowerConduit", (4, 4))],
       conduit=[(7, 4), (8, 4)], devs=[("RM_PowerTapClamp", (5, 4), None, None), ("StandingLamp", (10, 5), None, None)])

    # ---- row C: flexible hoses (a reel; the hose is laid as data from the reel to a free end)
    hose_i = ["select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos",
              "dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)"]
    st(12, "C", C_X[0], ROW_C, 18, 6, "HOSE: FLAT", "a laid hose with nothing flowing through it",
       ["the hose lies flat and thin", "a straight hose has NO joiner along it; the free end is a plain open end the hose's own width"], hose_i,
       hose=dict(reel=(0, 2), far=(16, 2), state="Flat"))
    st(13, "C", C_X[1], ROW_C, 18, 6, "HOSE: FILLING", "the same hose, flow ON, frozen half-way through filling",
       ["half-plump: the swell is mid-transition", "UNPAUSE and it finishes plumping in ~half a second"], hose_i,
       hose=dict(reel=(0, 2), far=(16, 2), state="Filling"))
    st(14, "C", C_X[2], ROW_C, 18, 6, "HOSE: PLUMP", "flow ON, fully filled",
       ["full round hose, visibly wider than the flat one", "still no joiner on the straight"], hose_i,
       hose=dict(reel=(0, 2), far=(16, 2), state="Plump"))
    st(15, "C", C_X[3], ROW_C, 28, 6, "HOSE: LONG + BEND", "a 26-cell plump hose routed round a wall stub",
       ["the hose bends smoothly round the obstacle (never kinks tighter than the minimum bend)",
        "joiners only at the bends: two brass couplings screwed face to face, joining two lengths", "it never crosses the wall"], hose_i,
       walls=[(13, z) for z in range(1, 5)], hose=dict(reel=(0, 2), far=(26, 2), state="Plump"))
    # ---- row D: hose crossings and parallel runs (owner review 2026-10-04 B18/B20; ruled by card: hoses do NOT branch,
    # one hose = one line with two ends, a "grid" is hoses crossing or lying side by side). What it does TODAY, shown as is.
    cross_i = hose_i + ["NOT designed: there is no crossing piece and no T or + hose fitting (hoses never branch, by ruling)"]
    st(16, "D", D_X[0], ROW_D, 20, 20, "HOSE CROSSING", "two plump hoses laid straight across each other at right angles",
       ["one hose passes cleanly OVER the other, the same way every frame (the newer reel's hose is on top)",
        "no joiner and no end fitting at the crossing", "the hoses do not route round each other: a hose is not an obstacle to another"],
       cross_i, hoses=[dict(reel=(0, 10), far=(19, 10), state="Plump"), dict(reel=(10, 0), far=(10, 19), state="Plump")])
    st(17, "D", D_X[1], ROW_D, 22, 10, "PARALLEL RUNS", "two hoses laid side by side, two cells apart, one flat and one plump",
       ["each keeps its own lane; where their S-curves meet, one draws over the other cleanly",
        "flat vs plump side by side: width and shine"],
       cross_i, hoses=[dict(reel=(0, 3), far=(21, 3), state="Flat"), dict(reel=(0, 5), far=(21, 5), state="Plump")])
    st(18, "D", D_X[2], ROW_D, 22, 22, "HOSE GRID", "four hoses, two each way, crossing in a 2 x 2 grid",
       ["four crossings: every one is over/under, with a fixed order (newest on top)",
        "FINDING to judge: where the S-curve slack of two hoses runs along each other they may overlap for a stretch"],
       cross_i, hoses=[dict(reel=(0, 6), far=(21, 6), state="Plump"), dict(reel=(0, 15), far=(21, 15), state="Plump"),
                       dict(reel=(6, 0), far=(6, 21), state="Plump"), dict(reel=(15, 0), far=(15, 21), state="Plump")])
    stations_round2(st, hose_i)
    for d in S:
        if d["hose"] and not d["hoses"]:
            d["hoses"] = [d["hose"]]
    return S


def rect_cells(x, z, w, h):
    return [(i, j) for i in range(x, x + w) for j in range(z, z + h)]


def perimeter(x0, z0, x1, z1, gaps=()):
    c = [(x, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1) if x in (x0, x1) or z in (z0, z1)]
    return [p for p in c if p not in set(gaps)]


def stations_round2(st, hose_i):
    """Round 2 stations (owner notes 2026-10-04, design/RimMandrake/messyconduit_review_round2_owner_notes_2026-10-04.md).
    Numbered AFTER 18 so the owner's station numbers never move. They live in REGION2, north of the quicktest colonists.
    Extra per-station keys: terrain [(TerrainDef, rect)] painted before building; roof [(RoofDef, rect)] laid after the
    region is unroofed; fog {refog: [rect], unfog: [rect]} applied last (the region is unfogged by clear()); blueprints
    [(def, cell, rot)] placed as real blueprints; wconduit [cell] = WaterproofConduit; links may carry a third element,
    the verdict the link is EXPECTED to get (Roofed / OutOfRange / FullA): a refusal shown on purpose; hook = the name of a
    hose hook run after the hoses are laid."""
    R2 = dict(region=2)
    # ---- row E: power showpieces
    s19 = [("Battery", (16, 10), 0, 1.0), ("Battery", (17, 10), 0, 1.0),            # adjacent to the pole
           ("StandingLamp", (18, 15), None, None), ("Heater", (22, 15), None, None), ("SunLamp", (20, 10), None, None),
           ("Turret_MiniTurret", (23, 12), None, None),
           ("ElectricStove", (35, 13), None, None), ("HiTechResearchBench", (4, 16), None, None),   # at distance, by conduit
           ("FlatscreenTelevision", (9, 9), 0, None), ("Cooler", (26, 21), 3, None),
           ("WallLamp", (29, 23), 0, None), ("WallLamp", (29, 17), 0, None)]
    st(19, "E", 12, 144, 40, 26, "POLE CLUSTER", "one power pole with a wide mix of devices: some right beside it (lamp, heater, sun "
       "lamp, mini-turret, two batteries), some reached by conduit runs (stove, hi-tech research bench, TV), a walk-in freezer "
       "with an in-wall cooler and wall lamps inside and out, and a lamp mast fed over the air",
       ["each device right beside the pole gets its own hookup from the pole's insulators; with more hookups than insulators, "
        "see whether they share a terminal or pile onto one (owner question: which terminal does each go to?)",
        "big devices (5x2 bench, 3x1 stove, 2x1 TV): the cord should meet the building, not stop short of its edge or end in mid-air",
        "the in-wall cooler: the cord reaches it through the wall face, not across the room",
        "wall lamps (one inside the freezer, one outside on its south wall): their cords run to the wall, never through the room's "
        "middle", "the turret's cord does not cross the turret's own base art",
        "the lamp mast on the far NW gets its power through the air: one span, lit"],
       ["toggle each device off (select > flick): its cord stays, the device goes dark",
        "deconstruct the pole: every adjacent hookup falls; the conduit-fed devices keep their cords",
        "build another lamp right beside the pole: does it pick a free terminal?"],
       conduit=line(6, 19, 13) + line(21, 32, 13) + [(20, z) for z in range(14, 22)] + line(21, 25, 21),
       walls=perimeter(26, 18, 32, 24, gaps=[(26, 21)]), devs=s19,
       masts=[("RM_AerialMast", (20, 13)), ("RM_AerialLampMast", (6, 22))], links=[(0, 1)], **R2)
    room = perimeter(4, 2, 30, 18, gaps=[(17, 2), (30, 13)])
    s20 = [("Battery", (1, 7), 0, 1.0), ("Battery", (6, 7), 0, 1.0), ("Battery", (27, 11), 0, 1.0),
           ("ElectricStove", (8, 15), None, None), ("ElectricStove", (12, 15), None, None),
           ("HiTechResearchBench", (24, 15), None, None), ("FlatscreenTelevision", (7, 5), 0, None),
           ("StandingLamp", (6, 12), None, None), ("StandingLamp", (27, 6), None, None), ("StandingLamp", (19, 4), None, None),
           ("Heater", (25, 8), None, None), ("SunLamp", (14, 13), None, None), ("Turret_MiniTurret", (24, 4), None, None),
           ("Cooler", (30, 13), 1, None), ("WallLamp", (18, 17), 0, None), ("WallLamp", (5, 14), 3, None),
           ("StandingLamp", (33, 13), None, None)]
    st(20, "E", 62, 144, 35, 22, "ELECTRIC ROOM", "a walled workshop crammed with powered devices joined by messy conduit (with a "
       "tangle), and three power poles carrying a line OVER it: west pole outside, middle pole inside the room, east pole outside",
       ["the showpiece: does the room read as lived-in and messy without turning into noise?",
        "the overhead line passes over the walls and the devices; its ground shadow falls across the floor and furniture",
        "floor cords never cross on top of a device's art; the tangle sits in the open between the stoves and the TV",
        "the middle pole stands inside the (unroofed) room and joins both the overhead line and the floor run",
        "the east pole lights the lamp outside the room through the air"],
       ["unlink the east span: only the outside lamp goes dark", "roof the room (Architect > Structure > Build roof, god mode): "
        "the middle pole is now under a roof - its spans should be cut (roof cut) and drop",
        "switch looks (--style): the whole room changes at once"],
       conduit=[(x, 10) for x in range(5, 30) if x != 17] + [(10, z) for z in range(11, 15)] + [(22, z) for z in range(5, 10)] +
       rect_cells(13, 7, 3, 3) + [(29, 11), (29, 12), (29, 13)],
       walls=room, devs=s20, masts=[("RM_AerialMast", (1, 10)), ("RM_AerialMast", (17, 10)), ("RM_AerialMast", (33, 10))],
       links=[(0, 1), (1, 2)], **R2)
    tunnel = [(4, 5, 3, 1), (6, 5, 1, 16), (6, 20, 12, 1), (18, 14, 7, 8), (25, 16, 19, 1)]   # x, z, w, h (station-local)
    open_ = set(c for r in tunnel for c in rect_cells(*r))
    st(21, "E", 108, 144, 48, 32, "MOUNTAIN TUNNEL", "a cord run through a winding one-cell tunnel and a small cavern inside a big "
       "block of granite under OVERHEAD MOUNTAIN, fog of war ON over the rock; a pole in the cavern tries to link to one outside",
       ["the cords stay INSIDE the tunnel: their curls must not draw over the fogged rock or poke out of the fog",
        "the cords are drawn under the mountain-roof shading like everything else (no bright cord in a dark tunnel)",
        "where the tunnel turns, the cord turns with it (no shortcut through rock)",
        "the cavern pole is under the mountain roof: its link to the pole outside is REFUSED (anchors need open sky), "
        "so no wire runs through the rock", "the lamp in the cavern and the one past the east exit are lit"],
       ["mine a cell of the tunnel wall: the fog lifts there; do the cords move?", "toggle the roof overlay (bottom-right)",
        "select the cavern pole > Link wire to the outside pole: the refusal message should say 'roofed'"],
       rock=[c for c in rect_cells(4, 0, 40, 26) if c not in open_],
       conduit=line(2, 6, 5) + [(6, z) for z in range(6, 21)] + line(7, 21, 20) + [(21, z) for z in range(16, 20)] +
       line(22, 44, 16),
       devs=[("Battery", (1, 5), 0, 1.0), ("StandingLamp", (19, 15), None, None), ("Heater", (23, 19), None, None),
             ("StandingLamp", (46, 16), None, None)],
       masts=[("RM_AerialMast", (21, 29)), ("RM_AerialMast", (23, 17))], links=[(0, 1, "Roofed")],
       roof=[("RoofRockThick", (4, 0, 40, 26))], fog=dict(refog=[(4, 0, 40, 26)], unfog=tunnel), **R2)
    # ---- row F: hose mazes (the paths are judged by validation_hose.py; this file only lays them out and calls the hooks)
    maze = perimeter(0, 0, 12, 10, gaps=[(12, 1), (12, 2), (12, 8), (12, 9)]) + perimeter(4, 3, 8, 7, gaps=[(4, 5)]) + \
        line(9, 11, 5)
    maze_i = hose_i + ["reel it in and lay it again to the same free end: does it pick the same route?"]
    st(22, "F", 166, 144, 18, 11, "HOSE MAZE: TWO ROUTES", "a hose laid from a reel deep inside a small walled maze to a free end "
       "outside; two ways out: the short one (south-east gap) and a longer one (north-east gap)",
       ["the hose finds the SHORT route out through the inner chamber's west door, down and out the south-east gap",
        "it never clips a wall corner, and its bends stay smooth in the one-cell corridors",
        "it stays inside the corridors (it never jumps a wall)"],
       maze_i, walls=maze, hose=dict(reel=(6, 5), far=(16, 2), state="Plump"), hook="hose_maze_hook", **R2)
    st(23, "F", 194, 144, 18, 11, "HOSE MAZE: SHORT WAY WALLED", "station 22's maze; after the hose is laid, a wall is built across the "
       "short (south-east) gap - does the hose re-route the long way, refuse, or pass through the new wall?",
       ["what the hose does when its route is blocked AFTER laying: re-routes north-east, stays and clips the wall, or drops",
        "if it re-routes, the new path is as clean as station 22's"],
       maze_i + ["deconstruct the blocking wall (cells 12,1 and 12,2): does the hose go back to the short way?"],
       walls=maze, hose=dict(reel=(6, 5), far=(16, 2), state="Plump"), hook="hose_block_wall_hook",
       block=[(12, 1), (12, 2)], **R2)
    # ---- row G: challenge configurations (bugs a human eye catches)
    st(24, "G", 222, 226, 28, 24, "MAP EDGE", "poles and cords at the map's north-east corner: a pole IN the corner cell, poles on the "
       "top and right edge cells, and floor runs lying along both edges",
       ["the cords' loose curls must not draw off the map (nothing hanging past the edge, nothing cut off with a hard line)",
        "the corner pole's wires and shadow stay on the map", "no red errors (open the debug log: none mentioning MessyConduit)"],
       ["pan the camera to the edge: is anything drawn in the black past the map?", "deconstruct the corner pole: both its spans drop"],
       conduit=line(2, 12, 23) + [(2, z) for z in range(13, 23)] + [(27, z) for z in range(0, 8)] + [(26, 2)],
       devs=[("Battery", (3, 20), 0, 1.0), ("StandingLamp", (12, 21), None, None), ("Battery", (25, 2), 0, 1.0),
             ("StandingLamp", (25, 6), None, None)],
       masts=[("RM_AerialMast", (2, 12)), ("RM_AerialMast", (14, 23)), ("RM_AerialMast", (27, 23)), ("RM_AerialMast", (27, 8))],
       links=[(0, 1), (1, 2), (2, 3)], label_below=True, **R2)
    st(25, "G", 12, 192, 30, 22, "RIVER CROSSING", "a river (chest-deep moving water, shallow banks): an overhead span from bank to bank, "
       "and a floor run fording the shallow end in waterproof conduit",
       ["the overhead wire's shadow falls on the water like on the ground (or not at all), never as a dark stripe on the river bed",
        "the floor cord on the water: does it float, sink or draw on top as if on soil? (waterproof conduit has its own look?)",
        "the cords' curls do not wander into the deep water", "both far devices are lit"],
       ["unpause: the river flows; does the cord on the water move with it (it should not)?",
        "deconstruct one waterproof conduit cell in the river: the cut ends lie in water - do they still spark?"],
       terrain=[("WaterMovingShallow", (11, 0, 8, 22)), ("WaterMovingChestDeep", (13, 8, 4, 14))],
       conduit=line(2, 10, 4) + line(19, 26, 4) + line(3, 5, 12), wconduit=line(11, 18, 4),
       devs=[("Battery", (1, 4), 0, 1.0), ("Heater", (27, 4), None, None), ("Battery", (2, 12), 0, 1.0),
             ("StandingLamp", (27, 12), None, None)],
       masts=[("RM_AerialMast", (6, 12)), ("RM_AerialMast", (23, 12))], links=[(0, 1)], **R2)
    st(26, "G", 54, 192, 34, 20, "ROOF BOUNDARY", "a roofed steel room: an overhead span passes OVER its roof, a floor run goes in "
       "under the wall, and a pole standing INSIDE under the roof tries to link out",
       ["wires over a roof are allowed: the span is drawn over the roof, its shadow on the roof",
        "the pole under the roof is refused (anchors need open sky): no wire through the roof",
        "the floor cord inside the room: drawn under the roof shading, no seam where it passes the roof edge",
        "the lamp and heater inside are lit"],
       ["roof overlay on (bottom-right) to see the roof edge", "build a roof over the east pole (god mode): its span drops (roof cut)",
        "remove the room's roof: link the inside pole from its gizmo"],
       walls=perimeter(9, 4, 19, 14), roof=[("RoofConstructed", (9, 4, 11, 11))],
       conduit=[(3, 10), (3, 11)] + line(4, 15, 11),
       devs=[("Battery", (1, 9), 0, 1.0), ("StandingLamp", (15, 12), None, None), ("Heater", (12, 6), None, None),
             ("StandingLamp", (25, 9), None, None)],
       masts=[("RM_AerialMast", (3, 9)), ("RM_AerialMast", (22, 9)), ("RM_AerialMast", (14, 7))],
       links=[(0, 1), (0, 2, "Roofed")], **R2)
    st(27, "G", 96, 192, 44, 34, "LONG SPAN + DIAGONALS", "four chains: a span of EXACTLY the longest length (20), one cell too long "
       "(21, refused), a 45-degree diagonal chain, an odd-angle span, and a very short span (3 cells)",
       ["the 20-cell span: the deepest sag; it must not touch or dip below the ground, and its shadow stays a smooth curve",
        "the 21-cell pair stays unlinked and its lamp dark (refused: too far)",
        "diagonals: the wire leaves from the insulator tips on the correct side of the crossarm, not from the pole's middle",
        "the odd-angle span: no kink or zig-zag where it changes direction",
        "the 3-cell span: nearly no sag, but the wire still meets both insulators (not a straight line through the poles)"],
       ["select a mast > Link wire to the 21-cell partner: the message says too far",
        "Mod Settings: raise the longest span to 25: then link it"],
       devs=[("Battery", (0, 2), 0, 1.0), ("StandingLamp", (23, 2), None, None), ("Battery", (0, 8), 0, 1.0),
             ("StandingLamp", (24, 8), None, None), ("Battery", (0, 14), 0, 1.0), ("StandingLamp", (29, 14), None, None),
             ("Battery", (30, 22), 0, 1.0), ("StandingLamp", (40, 6), None, None), ("Battery", (32, 29), 0, 1.0)],
       masts=[("RM_AerialMast", (1, 2)), ("RM_AerialMast", (21, 2)), ("RM_AerialMast", (1, 8)), ("RM_AerialMast", (22, 8)),
              ("RM_AerialMast", (1, 14)), ("RM_AerialMast", (14, 27)), ("RM_AerialMast", (27, 14)),
              ("RM_AerialMast", (31, 22)), ("RM_AerialMast", (41, 8)), ("RM_AerialMast", (33, 30)), ("RM_AerialLampMast", (36, 31))],
       links=[(0, 1), (2, 3, "OutOfRange"), (4, 5), (5, 6), (7, 8), (9, 10)], **R2)
    st(28, "G", 156, 192, 32, 32, "CONVERGING HUB", "a hub pole with four spans (its maximum) arriving from N, E, S and W, a FIFTH pole "
       "trying to link (refused: full), and three lamps plus a heater right beside the hub",
       ["four wires meet on one crossarm: each lands on an insulator tip, none crossing through the pole art",
        "with more wires than insulators, do two share a tip cleanly or overlap in a blob?",
        "the fifth (NE) pole stays unlinked, its lamp dark", "the hub's local hookups: which terminal does each lamp take?"],
       ["unlink one spoke, then link the NE pole: it takes the freed slot", "deconstruct the hub: four spans drop at once"],
       devs=[("Battery", (13, 16), 0, 1.0), ("StandingLamp", (16, 19), None, None), ("StandingLamp", (19, 16), None, None),
             ("StandingLamp", (16, 13), None, None), ("Heater", (19, 19), None, None),
             ("StandingLamp", (18, 30), None, None), ("StandingLamp", (30, 18), None, None), ("StandingLamp", (18, 2), None, None),
             ("StandingLamp", (2, 18), None, None), ("StandingLamp", (27, 29), None, None)],
       masts=[("RM_AerialMast", (16, 16)), ("RM_AerialMast", (16, 30)), ("RM_AerialMast", (30, 16)), ("RM_AerialMast", (16, 2)),
              ("RM_AerialMast", (2, 16)), ("RM_AerialMast", (27, 27))],
       links=[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5, "FullA")], **R2)
    st(29, "G", 196, 192, 26, 24, "NETS SIDE BY SIDE + HALF-BUILT", "three separate powered nets two cells apart; two nets end to end "
       "with a one-cell gap that is a conduit BLUEPRINT; a half-built run (conduit, then blueprints, a pole blueprint, a lamp blueprint)",
       ["side by side: each net's cords stay with its own net (no cord jumping across to the neighbour's run)",
        "Modern look, 'a different colour per power net': three nets = three colours; after the gap is built, the two merged nets "
        "should become ONE colour", "blueprints draw no cords (a cord never runs to a ghost)",
        "SAVE then LOAD the game here: every cord comes back the same (same curls, same colours), blueprints still cord-free"],
       ["god mode: build the gap blueprint (or unpause and let colonists build): nets merge, the dark lamp lights",
        "save, load, compare (this is the save-load station)", "--style ExtensionCord for the colour checks"],
       conduit=line(2, 20, 2) + line(2, 20, 4) + line(2, 20, 6) + line(2, 10, 12) + line(12, 20, 12) + line(2, 8, 18),
       devs=[("Battery", (1, 2), 0, 1.0), ("Battery", (1, 4), 0, 1.0), ("Battery", (1, 6), 0, 1.0),
             ("StandingLamp", (21, 2), None, None), ("StandingLamp", (21, 4), None, None), ("StandingLamp", (21, 6), None, None),
             ("Battery", (1, 12), 0, 1.0), ("StandingLamp", (21, 12), None, None),
             ("Battery", (1, 18), 0, 1.0), ("StandingLamp", (4, 20), None, None)],
       blueprints=[("PowerConduit", (11, 12), None)] + [("PowerConduit", (x, 18), None) for x in range(9, 19)] +
       [("RM_AerialMast", (20, 20), None), ("StandingLamp", (21, 18), None)], **R2)


FREE = dict(rect=(160, 10, 70, 30), pad_conduit=line(161, 176, 31),
            batteries=[(168, 32), (170, 32), (172, 32)], solar=[(162, 33), (175, 33)],
            stock=[("Steel", 75, (162 + i, 13)) for i in range(10)] + [("ComponentIndustrial", 25, (174, 13)),
                   ("ComponentIndustrial", 25, (175, 13)), ("WoodLog", 75, (177, 13)), ("WoodLog", 75, (178, 13)),
                   ("WoodLog", 75, (179, 13)), ("WoodLog", 75, (180, 13))])


def g(st, c):
    return (st["origin"][0] + c[0], st["origin"][1] + c[1])


def rect_of(st, pad=1):
    x, z = st["origin"]
    w, h = st["size"]
    return (x - pad, z - pad, w + 2 * pad, h + 2 * pad)


def layout_check(S):
    """Every station inside REGION, no two stations closer than the cord lateral reach allows (2R+2 cells, R=5 from
    CordLayer.cs; overhead masts of different stations > 20 cells apart unless linked on purpose), the free area clear."""
    probs = []
    rects = [(s["n"], s["origin"][0], s["origin"][1], s["size"][0], s["size"][1], s.get("region", 1)) for s in S]
    fx, fz, fw, fh = FREE["rect"]
    rects.append(("F", fx, fz, fw, fh, 1))
    for n, x, z, w, h, reg in rects:
        rx, rz, rw, rh = REGIONS[reg]
        if x < rx or z < rz or x + w > rx + rw or z + h > rz + rh:
            probs.append("station %s outside REGION%s" % (n, "" if reg == 1 else reg))
    r1, r2 = REGION, REGION2                # the two regions must not overlap (clear() wipes each)
    if not (r1[1] + r1[3] <= r2[1] or r2[1] + r2[3] <= r1[1]):
        probs.append("REGION and REGION2 overlap")
    nums = [s["n"] for s in S]
    if nums != list(range(1, len(S) + 1)):
        probs.append("station numbers not 1..N in order: %s" % nums)
    for s in S:                             # every cell a station uses stays inside its own footprint and on the map
        w, h = s["size"]
        cells = list(s["conduit"]) + list(s["walls"]) + list(s["rock"]) + list(s.get("wconduit", [])) + \
            [d[1] for d in s["devs"]] + [m[1] for m in s["masts"]] + [b[1] for b in s.get("blueprints", [])] + list(s.get("block", []))
        for hz in s["hoses"]:
            cells += [hz["reel"], hz["far"]]
        for c in cells:
            if s["n"] >= 19 and not (0 <= c[0] < w and 0 <= c[1] < h):   # 1-18 predate the rule (st.9's N bracket)
                probs.append("station %d cell %s outside its %dx%d footprint" % (s["n"], c, w, h))
            gx, gz = g(s, c)
            if not (0 <= gx < MAP_SIZE and 0 <= gz < MAP_SIZE):
                probs.append("station %d cell %s off the map" % (s["n"], (gx, gz)))
        for a, b, *exp in s["links"]:      # a link meant to succeed must be in range; an OutOfRange one must not be
            (ax, az), (bx, bz) = s["masts"][a][1], s["masts"][b][1]
            ok = (ax - bx) ** 2 + (az - bz) ** 2 <= SPAN_RANGE ** 2
            if ok != (exp[:1] != ["OutOfRange"]):
                probs.append("station %d link %d-%d: in range=%s but expected %s" % (s["n"], a, b, ok, exp or "Ok"))
    masts = [(s["n"], g(s, m[1])) for s in S for m in s["masts"]] + \
        [(s["n"], g(s, b[1])) for s in S for b in s.get("blueprints", []) if b[0].startswith("RM_Aerial")]
    for i in range(len(masts)):              # round-2 stations: no mast within span range of another station's mast
        for j in range(i + 1, len(masts)):
            (na, pa), (nb, pb) = masts[i], masts[j]
            if na != nb and max(na, nb) >= 19 and (pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2 <= SPAN_RANGE ** 2:
                probs.append("masts of stations %d and %d within span range (%s, %s)" % (na, nb, pa, pb))
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            a, b = rects[i], rects[j]
            if a[5] != b[5]:
                continue
            dx = max(b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]))
            dz = max(b[2] - (a[2] + a[4]), a[2] - (b[2] + b[4]))
            if max(dx, dz) < 8:
                probs.append("stations %s and %s only %d cells apart" % (a[0], b[0], max(dx, dz)))
    for s in S:                          # gallery masts vs the free area: a mast he builds there auto-links (range 20)
        for m in s["masts"]:
            x, z = g(s, m[1])
            dx = max(fx - x, 0, x - (fx + fw - 1))
            dz = max(fz - z, 0, z - (fz + fh - 1))
            if (dx * dx + dz * dz) ** 0.5 <= 20:
                probs.append("mast of station %s within auto-link range (20) of the free area" % s["n"])
    return probs


# ------------------------------------------------------------------------------------------------ labels
SHORT = {1: "full battery, cord to heater + a plugged lamp", 2: "same build, battery EMPTY",
         3: "one conduit cell missing: live end / dead end", 4: "9+ conduit cells = a tangle",
         5: "switch, generator, lamps: one plug each", 6: "cord stubs into a wall and through rock",
         7: "battery > mast > mast > mast > lamp, overhead", 8: "a power mast feeding two lamp masts",
         9: "wire from a mast to a bracket on a shed wall, lamp inside", 10: "station 7 with the second span CUT",
         11: "clamp drains THEIR grid into our lamp", 12: "laid, nothing flowing", 13: "flow on, frozen half-filled",
         14: "flow on, fully filled", 15: "26 cells, bends round a wall stub", 16: "two hoses crossing: one cleanly over",
         17: "two hoses side by side", 18: "four hoses crossing in a 2 x 2 grid",
         19: "one pole, many kinds of device, near and far", 20: "crowded electric room, a line overhead",
         21: "cords through a fogged mountain tunnel", 22: "hose out of a maze: two routes",
         23: "maze, short way walled after laying", 24: "poles and cords on the map's corner",
         25: "span over a river, cord fording it", 26: "span over a roof, pole under one",
         27: "longest span, too long, diagonals, tiny", 28: "four spans into one pole, a fifth refused",
         29: "neighbour nets, a blueprint gap: save + load"}   # in-world sub line: one short clause


def label_ops(S, style):
    L = []
    rx, rz, rw, rh = REGION

    def add(x, z, text, sub="", col=GOLD, size="medium"):
        L.append("%d|%d|%s|%s|%s|%s|%s" % (x, z, text.replace("|", "/"), sub.replace("|", "/"), col, size, TAG))
    add(86, 104, "MESSY CONDUIT - HUMAN REVIEW", "cable look now: %s   |   game paused, god mode on   |   key sheet: Transient\\mc_human_review\\keysheet.html" % LOOK.get(style, style),
        CREAM)
    add(20 + 6, ROW_A + 12, "ROW A - FLOOR CORDS", "stations 1-6", TEAL, "small")
    add(20 + 6, ROW_B + 14, "ROW B - OVERHEAD LINES", "stations 7-11", TEAL, "small")
    add(20 + 6, ROW_C + 8, "ROW C - FLEXIBLE HOSES", "stations 12-15", TEAL, "small")
    add(20 + 6, ROW_D + 23, "ROW D - HOSE CROSSINGS", "stations 16-18: crossings and parallel runs", TEAL, "small")
    add(120, 182, "MESSY CONDUIT - NORTH GALLERY (round 2)", "stations 19-29   |   --goto N frames one   |   --goto N0 the whole north gallery", CREAM)
    add(32, 174, "ROW E - POWER SHOWPIECES", "stations 19-21", TEAL, "small")
    add(188, 160, "ROW F - HOSE MAZES", "stations 22-23", TEAL, "small")
    add(30, 218, "ROW G - CHALLENGE CONFIGURATIONS", "stations 24-29: edge, river, roof, spans, hub, nets + save-load", TEAL, "small")
    for s in S:
        x, z = s["origin"]
        w, h = s["size"]
        sub = SHORT[s["n"]]
        if s["n"] == 4:   # the pile pieces follow the look: strips only in Modern, junction boxes elsewhere
            sub += " with power strips" if style == "ExtensionCord" else " with junction boxes"
        add(x + w // 2, z - 2 if s.get("label_below") else z + h, "%d  %s" % (s["n"], s["title"]), sub)
    fx, fz, fw, fh = FREE["rect"]
    add(fx + fw // 2, fz + fh + 1, "F  FREE BUILD AREA", "steel, components, wood below; charged power pad at the west end - build anything", RUST)
    add(179, 29, "plug in here", "end of the powered conduit (just left)", RUST, "small")
    return "\n".join(L)


STUFFED = {"Turret_MiniTurret": "Steel", "HiTechResearchBench": "Steel"}   # MadeFromStuff (Metallic), RimSage 2026-10-04


# ------------------------------------------------------------------------------------------------ hose hooks (st.22/23)
# SLOT for validation_hose.py (HOSE workstream, owner notes round 2: "make the hose solve a complex path ... then 'build' a
# wall to block the obvious solution so we can see if it changes to go the other way... or what happens"). This file
# only lays the maze and the hose; the judging belongs to validation_hose.py. If it defines review_maze(R, station) or
# review_block_wall(R, station), the hook hands over to it; otherwise the default below runs and records a census.
def _hose_census(R, s):
    reel = list(g(s, s["hose"]["reel"]))
    hc = R.B.hp("census")
    x = next((x for x in hc.get("hoses") or [] if x.get("reel") == reel), {})
    return {k: x.get(k) for k in ("state", "pathLen", "couplings", "layOk", "reason") if k in x}


def _delegate(name, R, s):
    try:
        import validation_hose as VH                 # noqa: E402  (same folder; may not define the hook yet)
    except Exception as e:                           # pragma: no cover - live only
        R.notes.append("validation_hose import failed: %s" % e)
        return False
    fn = getattr(VH, name, None)
    if fn is None:
        return False
    R.hook_results[s["n"]] = fn(R, s)
    return True


def hose_maze_hook(R, s):
    """Station 22: the hose is already laid reel -> far through the maze. TODO(validation_hose.py): define
    review_maze(R, station) to assert the SHORT route (out the inner west door, down, out the south-east gap)."""
    if not _delegate("review_maze", R, s):
        R.hook_results[s["n"]] = {"route": _hose_census(R, s), "judged": "TODO validation_hose.review_maze"}


def hose_block_wall_hook(R, s):
    """Station 23: after laying, wall off the short (south-east) gap and see what the hose does. TODO(validation_hose.py):
    define review_block_wall(R, station) to judge it (re-route north-east / refuse / clip). Default: build the wall, step
    60 ticks, census before and after."""
    if _delegate("review_block_wall", R, s):
        return
    before = _hose_census(R, s)
    R.call("jawa/build_batch", ops=PL._ops("Wall", [g(s, c) for c in s["block"]]), stuff="Steel", faction="player", wipeExisting=False)
    R.B.ticks(60)
    R.hook_results[s["n"]] = {"before": before, "after_wall": _hose_census(R, s), "judged": "TODO validation_hose.review_block_wall"}


HOOKS = {"hose_maze_hook": hose_maze_hook, "hose_block_wall_hook": hose_block_wall_hook}


# ------------------------------------------------------------------------------------------------ live build
class Review(object):
    def __init__(self, B, log):
        self.B, self.log = B, log
        self.notes = []
        self.hook_results, self.refusals, self.S = {}, {}, []

    def say(self, msg):
        line_ = "%s %s" % (time.strftime("%H:%M:%S"), msg)
        print(line_, flush=True)
        if self.log:
            with open(self.log, "a", encoding="utf-8") as f:
                f.write("- " + line_ + "\n")

    def call(self, tool, **kw):
        r = self.B.call(tool, **kw)
        if r.get("success") is False:
            self.notes.append("%s refused: %s" % (tool, json.dumps(r)[:240]))
        return r

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
        if mi.get("sizeX") != 250:
            raise SystemExit("expected a 250x250 quicktest map, got %s" % mi.get("sizeX"))
        self.call("jawa/weather_set", weather="Clear", lockWeather=True)
        clk = B.call("jawa/time_clock")
        lon = mi.get("longitude")
        if isinstance(clk.get("ticksAbs"), int) and isinstance(lon, (int, float)):
            local = (clk["ticksAbs"] + int(round(lon / 360.0 * 60000))) % 60000
            add = (12 * 2500 - local) % 60000
            if add:
                self.call("jawa/time_set_ticks", ticks=clk["ticksGame"] + add)
        self.call("jawa/incident_queue_clear")
        st = B.call("jawa/storyteller_swap", difficultyDef="Peaceful")
        self.peaceful = st.get("success")
        self.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        self.call("jawa/research_bulk", mode="finish_all")
        self.call("rimworld/set_god_mode", enabled=True)
        self.call("jawa/screenshot_mode", enabled=False)
        self.pawns_in_region = []
        for reg in (REGION, REGION2):
            pw = B.call("jawa/list_pawns", rect="%d,%d,%d,%d" % reg, limit=50)
            self.pawns_in_region += [p.get("label") or p.get("id") for p in pw.get("pawns") or []]

    def clear(self):
        B = self.B
        B.call("jawa/review_label", action="clear", tag=TAG)
        for reg in (REGION, REGION2):
            rr = "%d,%d,%d,%d" % reg
            B.call("jawa/destroy_batch", rects=rr, categories="All")
            B.call("jawa/set_terrain_batch", ops="Soil:" + rr)
            B.call("jawa/set_fog", action="unfog", rect=rr)
            B.call("jawa/set_roof_batch", ops="None:" + rr)

    def no_roofs(self):
        """The shed of station 9 is an enclosed room: vanilla adds it to the Build-roof area and colonists roof it (the
        frozen Mote_TempRoof then hides the bracket). Keep the region out of Home and Build roof, and unroofed."""
        for reg in (REGION, REGION2):
            rr = "%d,%d,%d,%d" % reg
            for area in ("BuildRoof", "Home"):
                r = self.B.call("jawa/paint_area", area=area, ops=rr, value=False)
                if not r.get("success", True):
                    self.notes.append("paint_area %s: %s" % (area, json.dumps(r)[:200]))
            self.B.call("jawa/set_roof_batch", ops="None:" + rr)
        self.station_roofs()

    def station_roofs(self):
        """Round 2: the stations that are ABOUT a roof (21 mountain, 26 roofed room) get theirs back after every unroofing."""
        ops = ["%s:%d,%d,%d,%d" % ((rd,) + g(s, r[:2]) + tuple(r[2:])) for s in self.S for rd, r in s.get("roof", [])]
        if ops:
            r = self.call("jawa/set_roof_batch", ops=";".join(ops))
            self.roofs = r.get("success")

    def station_fog(self):
        """Round 2 per-station fog: clear() unfogs the whole region (and never uses unfogAll, which has wedged the game);
        a station with `fog` is re-hidden over its refog rects, then its unfog rects (the tunnel) are revealed again."""
        for s in self.S:
            f = s.get("fog")
            if not f:
                continue
            for act in ("refog", "unfog"):
                for r in f.get(act, []):
                    x, z = g(s, r[:2])
                    self.call("jawa/set_fog", action=act, rect="%d,%d,%d,%d" % (x, z, r[2], r[3]))

    def build(self, S, style):
        B = self.B
        self.S = S
        terr = ["%s:%d,%d,%d,%d" % ((td,) + g(s, r[:2]) + tuple(r[2:])) for s in S for td, r in s.get("terrain", [])]
        if terr:                                       # round 2 (st.25 river): paint before anything is built on it
            self.call("jawa/set_terrain_batch", ops=";".join(terr))
        B.probe("defaults")
        B.probe("set:style=%s" % style)
        B.ap("defaults")
        B.ap("set:autoLink=False")                    # no gallery mast may link across stations; restored below
        B.hp("defaults")
        per = {}
        def put(d, cell, stuff=None, rot=None, faction="player"):
            per.setdefault((d, stuff, rot, faction), []).append(cell)
        bats = []
        for s in S:
            for c in s["rock"]:
                put("Granite", g(s, c), faction=None)
            for c in s["walls"]:
                put("Wall", g(s, c), stuff="Steel")
            for c in s["conduit"]:
                put("PowerConduit", g(s, c))
            for c in s.get("wconduit", []):
                put("WaterproofConduit", g(s, c))
            for h in s["hostile"]:
                put(h[0], g(s, h[1]), rot=h[2] if len(h) > 2 else None, faction="hostile")
                if h[0] == "Battery":
                    bats.append((g(s, h[1]), h[3]))
            for m in s["masts"]:
                # the bracket's rotation points AT its wall (vanilla Placeworker_AttachedToWall); station 9's wall is south
                put(m[0], g(s, m[1]), rot=m[2] if len(m) > 2 else None)
            for d, c, rot, ch in s["devs"]:
                put(d, g(s, c), stuff=STUFFED.get(d), rot=rot)
                if d == "Battery":
                    bats.append((g(s, c), ch))
            for h in s["hoses"]:
                put("RM_HoseReel", g(s, h["reel"]))
        for c in FREE["pad_conduit"]:
            put("PowerConduit", c)
        for c in FREE["batteries"]:
            put("Battery", c, rot=0)
            bats.append((c, 1.0))
        for c in FREE["solar"]:
            put("SolarGenerator", c)
        transmitters = ("Battery", "WoodFiredGenerator", "PowerSwitch", "SolarGenerator", "RM_AerialMast", "RM_AerialLampMast",
                        "RM_AerialWallBracket", "RM_HoseReel")
        order = ["Granite", "Wall", "PowerConduit", "WaterproofConduit"] + list(transmitters)
        keys = sorted(per, key=lambda k: (order.index(k[0]) if k[0] in order else 99, k[0], str(k[3])))
        self.builds = {}
        for k in keys:
            d, stuff, rot, fac = k
            kw = {"ops": PL._ops(d, per[k], rot), "wipeExisting": False}
            if fac:
                kw["faction"] = fac
            if stuff:
                kw["stuff"] = stuff
            r = self.call("jawa/build_batch", **kw)
            self.builds["%s/%s" % (d, fac)] = "%s/%d" % (r.get("survived"), len(per[k]))
            if r.get("survived") != len(per[k]):
                self.notes.append("build %s: %s of %d survived %s" % (d, r.get("survived"), len(per[k]), (r.get("failed") or [])[:3]))
        self.say("built: %s" % self.builds)
        rr = "%d,%d,%d,%d" % REGION
        lt = B.call("jawa/list_things", defName="Battery", rect=rr, limit=500)
        bypos = {(t.get("x"), t.get("z")): t.get("id") or t.get("thingId") for t in lt.get("things") or []}
        for cell, pct in bats:
            tid = bypos.get(tuple(cell))
            if tid is None:
                self.notes.append("battery at %s not found" % (cell,))
                continue
            self.call("jawa/battery_set", thing=tid, mode="setPct", value=pct)
        for s in S:                                    # round 2 (st.29): real blueprints, left unbuilt for the owner
            for d, c, rot in s.get("blueprints", []):
                kw = {"def": d}
                x, z = g(s, c)
                kw.update(x=x, z=z, faction="Player", ignoreValidity=True)
                if rot is not None:
                    kw["rot"] = str(rot)
                self.call("jawa/blueprint_place", **kw)
        for item, n, c in FREE["stock"]:
            self.call("rimworld/spawn_thing", defName=item, stackCount=n, x=c[0], z=c[1])
        self.call("jawa/map_commit")
        self.no_roofs()
        B.ticks(1)
        # overhead lines: link by id, then cut
        self.refusals = {}
        c0 = B.ap("census")
        apos = {(a["x"], a["z"]): a["id"] for a in c0.get("anchors") or []}
        for s in S:
            ids = [apos.get(g(s, m[1])) for m in s["masts"]]
            for a, b, *exp in s["links"]:
                if ids[a] is None or ids[b] is None:
                    self.notes.append("station %d: anchor missing for link %d-%d" % (s["n"], a, b))
                    continue
                v = B.ap("link:%d,%d" % (ids[a], ids[b])).get("verdict")
                if exp:                                # a refusal shown on purpose (round 2: Roofed / OutOfRange / FullA)
                    self.refusals["%d:%d-%d" % (s["n"], a, b)] = "%s (expected %s)" % (v, exp[0])
                    if v != exp[0]:
                        self.notes.append("station %d link %d-%d verdict %s, expected %s" % (s["n"], a, b, v, exp[0]))
                elif v not in ("Ok", "Linked", "Success", None):
                    self.notes.append("station %d link %d-%d verdict %s" % (s["n"], a, b, v))
            s["_ids"] = ids
        B.ticks(2)
        for s in S:
            for a, b in s["cuts"]:
                d = B.ap("cut:%d,%d" % (s["_ids"][a], s["_ids"][b])).get("done")
                if not d:
                    self.notes.append("station %d cut %d-%d not done" % (s["n"], a, b))
        B.ticks(30)
        # T4 (round 2): vanilla PowerNet.PowerNetTick switches waiting consumers on ONE at a time, every 200/n ticks
        # (min 30), so a map paused right after the build left the second lamp mast of station 8 dark with the NeedsPower
        # bolt although its net was live. Let every net finish switching on before the map is frozen.
        B.ticks(600)
        self.no_roofs()            # round 2: colonists had roofed the station-9 shed in those ticks (frozen roof mote)
        B.ap("poll")
        B.ap("set:autoLink=True")                     # the free area behaves as shipped
        # hoses: lay all, flow the plump ones, then the filling one half a transition later
        hs = [(s, h) for s in S for h in s["hoses"]]
        for s, h in hs:
            r, f = g(s, h["reel"]), g(s, h["far"])
            lay = B.hp("lay:%d,%d,%d,%d" % (r + f))
            if not lay.get("success", True) or lay.get("layOk") is False:
                self.notes.append("station %d hose lay: %s" % (s["n"], json.dumps(lay)[:200]))
        B.ticks(2)
        for s, h in hs:
            if h["state"] == "Plump":
                B.hp("flow:%d,%d=on" % g(s, h["reel"]))
        B.ticks(PL.TRANSITION_TICKS - PL.TRANSITION_TICKS // 2 + 5)
        for s, h in hs:
            if h["state"] == "Filling":
                B.hp("flow:%d,%d=on" % g(s, h["reel"]))
        B.ticks(PL.TRANSITION_TICKS // 2)
        for s in S:                                    # round 2 (st.22/23): the maze hooks, after the hoses are down
            if s.get("hook"):
                HOOKS[s["hook"]](self, s)
        hc = B.hp("census")
        self.hose_states = {}
        for s, h in hs:
            reel = list(g(s, h["reel"]))
            x = next((x for x in hc.get("hoses") or [] if x.get("reel") == reel), {})
            self.hose_states["%d@%d,%d" % (s["n"], reel[0], reel[1])] = {k: x.get(k) for k in ("state", "blend", "couplings", "pathLen")}
        B.probe("poll")
        self.station_fog()
        self.call("rimworld/pause_game", pause=True)

    def labels(self, S, style):
        r = self.B.call("jawa/review_label", action="clear", tag=TAG)
        r = self.B.call("jawa/review_label", action="add", ops=label_ops(S, style), tag=TAG)
        if not r.get("success"):
            self.notes.append("labels: %s" % json.dumps(r)[:300])
        return r

    def goto(self, S, which, sub=None):
        if sub and which not in ("0", "all") and which.upper() not in ("F", "N0"):
            s = next(s for s in S if str(s["n"]) == which)
            dx, dz, w, h = sub
            r = self.B.call("rimworld/frame_cell_rect", x=s["origin"][0] + dx, z=s["origin"][1] + dz, width=w, height=h, paddingCells=0)
            self.B.call("rimworld/set_camera_zoom", rootSize=max(4.0, max(h, w * 9.0 / 16.0) / 2.0 + 0.5))
            return r
        if which in ("0", "all"):
            x, z, w, h = REGION
        elif which.upper() == "N0":                     # round 2: the north gallery (stations 19-29)
            x, z, w, h = REGION2
        elif which.upper() == "F":
            x, z, w, h = FREE["rect"]
        else:
            s = next(s for s in S if str(s["n"]) == which)
            x, z, w, h = rect_of(s, 2)
        return self.B.call("rimworld/frame_cell_rect", x=x, z=z, width=w, height=h, paddingCells=2)


# ------------------------------------------------------------------------------------------------ key sheet
def keysheet(S, style, live=None):
    os.makedirs(OUT, exist_ok=True)
    md = ["# Messy Conduit - human review key sheet", "",
          "Built by `src/RimMandrake/MessyConduit/human_review.py`. Game paused, god mode on, weather clear, noon, Peaceful.",
          "Cable look now: **%s** (one global setting: flip it with Mod Settings > RimMandrake: Messy Conduit > Style, "
          "or `human_review.py --style <X>`; every station changes at once)." % LOOK.get(style, style), "",
          "Jump the camera: `human_review.py --goto N` (N = station, 0 = south gallery 1-18, N0 = north gallery 19-29, F = free area).", "",
          "Station numbers never move: round-2 stations are appended as 19-29 in a north gallery (above the colonists).", "",
          "## Everywhere", "",
          "- Mod Settings > RimMandrake: Messy Conduit: master switch OFF restores vanilla conduit art instantly, ON brings the cords back.",
          "- Looks (Mod Settings name = `--style` value): Scrapper = StarWarsJawa, Industrial = StarWars, Modern = ExtensionCord, "
          "Futuristic = Cybertek. Each look owns its floor cords, its junction pieces, its power poles and its overhead lines. "
          "Modern also has a colour mode: in 'one colour everywhere' every plug, junction box and wall stub takes that colour.",
          "- Unpause (space) to see motion: sway, live-end sparks, hose filling. Pause again to study a frame.",
          "- Power overlay (bottom-right toggle) still shows vanilla connector lines.", ""]
    for row, name, blurb in ROWS:
        md += ["## " + name, ""] + ([blurb, ""] if blurb else [])
        for s in [s for s in S if s["row"] == row]:
            md += ["### %d. %s" % (s["n"], s["title"]), "", s["what"], "", "**Notice**", ""] + ["- " + x for x in s["notice"]] + \
                  ["", "**Try**", ""] + ["- " + x for x in s["interact"]] + [""]
    md += ["## Expected refusals (shown on purpose)", "",
           "- 21: the cavern pole's link to the outside pole is refused (Roofed).",
           "- 26: the pole inside the roofed room is refused (Roofed).",
           "- 27: the 21-cell pair is refused (OutOfRange).", "- 28: the fifth pole is refused (FullA: the hub's 4 slots are used).", ""]
    md += ["## F. Free build area", "", "Open soil east of the hoses. West end: a charged power pad (2 solar generators, 3 full "
           "batteries) with a conduit stub labelled *plug in here*. South edge: steel, components and wood. God mode builds "
           "instantly; research is finished. Masts built here auto-link (shipped default); gallery masts are more than 20 cells "
           "away, so nothing you build links into the gallery.", ""]
    if live:
        md += ["## This build", "", "```", json.dumps(live, indent=1, sort_keys=True), "```", ""]
    with open(os.path.join(OUT, "KEYSHEET.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    E = html.escape
    cards = []
    for s in S:
        cards.append('<section class="st row%s"><div class="num">%d</div><div><h3>%s</h3><p class="what">%s</p>'
                     '<h4>Notice</h4><ul>%s</ul><h4>Try</h4><ul>%s</ul><p class="go">--goto %d</p></div></section>' % (
                         s["row"], s["n"], E(s["title"]), E(s["what"]), "".join("<li>%s</li>" % E(x) for x in s["notice"]),
                         "".join("<li>%s</li>" % E(x) for x in s["interact"]), s["n"]))
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Messy Conduit Review</title><style>
:root{--bg:#2a1d14;--panel:#3a291c;--ink:#f2e6cf;--muted:#c9b79a;--gold:#ffd27f;--teal:#8fd3c7;--rust:#ff9a6b;--line:#5a4230}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 Georgia,serif;padding:20px 16px}
h1{color:var(--gold);margin:0 0 4px;font-size:26px}h2{color:var(--teal);border-bottom:1px solid var(--line);padding-bottom:4px;margin-top:28px}
.sub{color:var(--muted);margin:0 0 14px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
.st{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px;display:flex;gap:12px}
.num{font-size:30px;color:var(--gold);min-width:40px;text-align:center;font-weight:bold}
h3{margin:0;color:var(--gold);font-size:16px}h4{margin:8px 0 2px;color:var(--teal);font-size:13px;text-transform:uppercase;letter-spacing:.05em}
ul{margin:0;padding-left:18px}.what{margin:4px 0;color:var(--muted)}.go{margin:8px 0 0;font-family:monospace;color:var(--rust);font-size:12px}
code{color:var(--rust)}.box{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px}
</style></head><body>
<h1>Messy Conduit &mdash; human review</h1>
<p class="sub">Cable look now: <b>%s</b> (Scrapper = StarWarsJawa, Industrial = StarWars, Modern = ExtensionCord, Futuristic = Cybertek). Game paused, god mode on, clear weather, noon, Peaceful. Jump: <code>human_review.py --goto N</code> (0 = south gallery 1-18, N0 = north gallery 19-29, F = free area). Flip every station's look: Mod Settings &rsaquo; RimMandrake: Messy Conduit &rsaquo; Style, or <code>--style StarWars | ExtensionCord | Cybertek | StarWarsJawa</code>.</p>
<div class="box"><b>Everywhere:</b> master switch OFF = vanilla conduit art, ON = cords back, no restart. Unpause (space) for motion: sway, sparks, hoses filling. Power overlay still shows the vanilla connector lines.</div>
%s
<h2>F &mdash; free build area</h2><div class="box">Open soil east of the hoses. West end: charged power pad (2 solar, 3 full batteries) with a conduit stub labelled <i>plug in here</i>. South edge: steel, components, wood. God mode builds instantly; research is finished. New masts here auto-link (shipped default); gallery masts are over 20 cells away. <span class="go">--goto F</span></div>
</body></html>""" % (E(LOOK.get(style, style)), "\n".join(
        '<h2>%s</h2>%s<div class="grid">%s</div>' % (E(name.replace(" - ", " \u2014 ", 1)), '<p class="sub">%s</p>' % E(blurb) if blurb else "",
                                                     "".join(c for c, s in zip(cards, S) if s["row"] == row))
        for row, name, blurb in ROWS))
    with open(os.path.join(OUT, "keysheet.html"), "w", encoding="utf-8") as f:
        f.write(page)


# ------------------------------------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", action="store_true", help="offline: layout check + key sheet, no bridge")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--fresh-map", action="store_true", help="with --build: start a new quicktest map first")
    ap.add_argument("--style", choices=STYLES, default=None)
    ap.add_argument("--goto", default=None)
    ap.add_argument("--sub", default=None, help="with --goto N: frame only dx,dz,w,h (station-local cells), a close look")
    ap.add_argument("--shot", default=None, help="with --goto N --sub: the game's own render of that rect (no window focus "
                                                 "needed) copied to D:\\Luke\\dev\\_rmscratch\\<shot>.png")
    ap.add_argument("--labels", action="store_true")
    ap.add_argument("--clear", action="store_true")
    ap.add_argument("--log", default=os.path.join("Transient", "mc_human_review_build_log_20261004.md"))
    a = ap.parse_args(argv)
    S = station_list()
    probs = layout_check(S)
    if probs:
        print("LAYOUT PROBLEMS:\n  " + "\n  ".join(probs))
        return 2
    if a.plan:
        keysheet(S, a.style or "StarWarsJawa")
        print("layout ok: %d stations + free area; key sheet -> %s" % (len(S), OUT))
        return 0
    import run_live as RL  # noqa: E402  (python.exe: numpy-free path)
    R = Review(RL.LiveBridge(), a.log if a.build else None)
    if a.clear:
        R.clear()
        print("cleared region %s and its labels" % (REGION,))
        return 0
    style = a.style
    if a.build:
        t0 = time.time()
        if a.fresh_map:
            R.say("fresh quicktest map")
            R.fresh_map()
        R.calm()
        R.say("calm world set (peaceful=%s, pawns in region %s)" % (R.peaceful, R.pawns_in_region))
        R.clear()
        R.say("region cleared")
        style = style or "StarWarsJawa"
        R.build(S, style)
        R.say("stations built; hose states %s" % R.hose_states)
        lab = R.labels(S, style)
        R.say("labels: added %s, refused %s" % (lab.get("added"), lab.get("refused")))
        R.goto(S, "0")
        live = {"style": style, "builds": R.builds, "hose_states": R.hose_states, "peaceful": R.peaceful,
                "expected_refusals": R.refusals, "hose_hooks": R.hook_results, "station_roofs": getattr(R, "roofs", None),
                "pawns_in_region": R.pawns_in_region, "notes": R.notes, "wall_s": round(time.time() - t0, 1)}
        keysheet(S, style, live)
        R.say("DONE in %ss; notes: %s" % (live["wall_s"], R.notes or "none"))
        return 0
    if style:
        r = R.B.probe("set:style=%s" % style)
        R.labels(S, style)
        keysheet(S, style)
        print("style -> %s (%s)" % (style, r.get("value")))
    if a.labels:
        cur = (R.B.call("jawa/mod_settings_field", typeName="RimMandrake.MessyConduit.MessyConduitSettings", action="get",
                        field="style").get("value") or "StarWarsJawa")
        r = R.labels(S, str(cur).replace("CordStyle.", ""))
        print("labels: %s" % {k: r.get(k) for k in ("added", "refused", "count", "installed")})
    if a.goto is not None:
        sub = [int(v) for v in a.sub.split(",")] if a.sub else None
        r = R.goto(S, a.goto, sub)
        st = next((s for s in S if str(s["n"]) == a.goto), None)
        print("framed %s%s: %s (origin %s)" % (a.goto, " sub %s" % sub if sub else "", r.get("success"), st["origin"] if st else "-"))
        if a.shot and st and sub:
            import shutil
            x, z = st["origin"][0] + sub[0], st["origin"][1] + sub[1]
            R.B.call("jawa/clear_ui", all=True)
            time.sleep(1.5)
            res = R.B.call("rimworld/screenshot_cell_rect", x=x, z=z, width=sub[2], height=sub[3], paddingCells=1, fileName=a.shot,
                           rootSize=max(4.0, max(sub[3], sub[2] * 9.0 / 16.0) / 2.0 + 1.0))
            src = res.get("filePath") or res.get("path") or res.get("savedPath")
            for _ in range(20):
                if src and os.path.exists(src):
                    break
                time.sleep(0.5)
            dst = os.path.join("D:\\Luke\\dev\\_rmscratch", a.shot + ".png") if os.name == "nt" else None
            if src and dst and os.path.exists(src):
                shutil.copyfile(src, dst)
            print("shot %s -> %s" % (a.shot, dst if dst and os.path.exists(dst) else "FAILED %s" % json.dumps(res)[:200]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
