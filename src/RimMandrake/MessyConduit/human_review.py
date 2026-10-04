"""human_review.py -- the Northstar "for the human" review map for Messy Conduit (owner, 2026-10-04).

    python.exe src/RimMandrake/MessyConduit/human_review.py --build [--fresh-map] [--style StarWarsJawa] | tr -d '\\r'
    python.exe src/RimMandrake/MessyConduit/human_review.py --goto 7 | tr -d '\\r'     # frame station 7 (0 = whole gallery, F = free area)
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
TAG = "mc_review"
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
    st(9, "B", B_X[2], ROW_B, 30, 11, "WALL BRACKET", "an overhead wire from a mast to a bracket bolted ON a shed wall; floor cord from the bracket to a lamp",
       ["the bracket is drawn on the wall face, like a vanilla wall torch (it stands in the cell beside the wall, facing it)",
        "the wire lands on the bracket's insulator", "a floor cord continues from the bracket to the lamp"],
       ["build another: Architect > Power > scrap wall bracket, point it AT a wall (vanilla wall-attachment placement)",
        "deconstruct the wall behind the bracket", "unlink and re-link the span from the mast's gizmo"],
       devs=[("Battery", (1, 4), 0, 1.0), ("StandingLamp", (21, 5), None, None)],
       walls=line(12, 16, 3) + [(12, z) for z in range(0, 3)] + [(16, z) for z in range(0, 3)] + line(13, 15, 0),
       conduit=line(15, 20, 4),
       masts=[("RM_AerialMast", (2, 4)), ("RM_AerialWallBracket", (14, 4))], links=[(0, 1)])   # bracket faces SOUTH, at the wall
    st(10, "B", B_X[3], ROW_B, 30, 11, "CUT + FALLEN SPAN", "the station-7 chain with the SECOND span cut (as if blown by an explosion)",
       ["the cut wire still hangs from each mast TOP down to the ground, then lies on the ground, in the span's own cable",
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
    for d in S:
        if d["hose"] and not d["hoses"]:
            d["hoses"] = [d["hose"]]
    return S


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
    rx, rz, rw, rh = REGION
    rects = [(s["n"], s["origin"][0], s["origin"][1], s["size"][0], s["size"][1]) for s in S]
    fx, fz, fw, fh = FREE["rect"]
    rects.append(("F", fx, fz, fw, fh))
    for n, x, z, w, h in rects:
        if x < rx or z < rz or x + w > rx + rw or z + h > rz + rh:
            probs.append("station %s outside REGION" % n)
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            a, b = rects[i], rects[j]
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
         9: "wire from a mast to a bracket on a shed wall", 10: "station 7 with the second span CUT",
         11: "clamp drains THEIR grid into our lamp", 12: "laid, nothing flowing", 13: "flow on, frozen half-filled",
         14: "flow on, fully filled", 15: "26 cells, bends round a wall stub", 16: "two hoses crossing: one cleanly over",
         17: "two hoses side by side", 18: "four hoses crossing in a 2 x 2 grid"}   # in-world sub line: one short clause


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
    for s in S:
        x, z = s["origin"]
        w, h = s["size"]
        sub = SHORT[s["n"]]
        if s["n"] == 4:   # the pile pieces follow the look: strips only in Modern, junction boxes elsewhere
            sub += " with power strips" if style == "ExtensionCord" else " with junction boxes"
        add(x + w // 2, z + h, "%d  %s" % (s["n"], s["title"]), sub)
    fx, fz, fw, fh = FREE["rect"]
    add(fx + fw // 2, fz + fh + 1, "F  FREE BUILD AREA", "steel, components, wood below; charged power pad at the west end - build anything", RUST)
    add(179, 29, "plug in here", "end of the powered conduit (just left)", RUST, "small")
    return "\n".join(L)


# ------------------------------------------------------------------------------------------------ live build
class Review(object):
    def __init__(self, B, log):
        self.B, self.log = B, log
        self.notes = []

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
        rr = "%d,%d,%d,%d" % REGION
        pw = B.call("jawa/list_pawns", rect=rr, limit=50)
        self.pawns_in_region = [p.get("label") or p.get("id") for p in pw.get("pawns") or []]

    def clear(self):
        B = self.B
        rr = "%d,%d,%d,%d" % REGION
        B.call("jawa/review_label", action="clear", tag=TAG)
        B.call("jawa/destroy_batch", rects=rr, categories="All")
        B.call("jawa/set_terrain_batch", ops="Soil:" + rr)
        B.call("jawa/set_fog", action="unfog", rect=rr)
        B.call("jawa/set_roof_batch", ops="None:" + rr)

    def build(self, S, style):
        B = self.B
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
            for h in s["hostile"]:
                put(h[0], g(s, h[1]), rot=h[2] if len(h) > 2 else None, faction="hostile")
                if h[0] == "Battery":
                    bats.append((g(s, h[1]), h[3]))
            for m in s["masts"]:
                # the bracket's rotation points AT its wall (vanilla Placeworker_AttachedToWall); station 9's wall is south
                put(m[0], g(s, m[1]), rot=2 if m[0] == "RM_AerialWallBracket" else None)
            for d, c, rot, ch in s["devs"]:
                put(d, g(s, c), rot=rot)
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
        order = ["Granite", "Wall", "PowerConduit"] + list(transmitters)
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
        for item, n, c in FREE["stock"]:
            self.call("rimworld/spawn_thing", defName=item, stackCount=n, x=c[0], z=c[1])
        self.call("jawa/map_commit")
        B.ticks(1)
        # overhead lines: link by id, then cut
        c0 = B.ap("census")
        apos = {(a["x"], a["z"]): a["id"] for a in c0.get("anchors") or []}
        for s in S:
            ids = [apos.get(g(s, m[1])) for m in s["masts"]]
            for a, b in s["links"]:
                if ids[a] is None or ids[b] is None:
                    self.notes.append("station %d: anchor missing for link %d-%d" % (s["n"], a, b))
                    continue
                v = B.ap("link:%d,%d" % (ids[a], ids[b])).get("verdict")
                if v not in ("Ok", "Linked", "Success", None):
                    self.notes.append("station %d link %d-%d verdict %s" % (s["n"], a, b, v))
            s["_ids"] = ids
        B.ticks(2)
        for s in S:
            for a, b in s["cuts"]:
                d = B.ap("cut:%d,%d" % (s["_ids"][a], s["_ids"][b])).get("done")
                if not d:
                    self.notes.append("station %d cut %d-%d not done" % (s["n"], a, b))
        B.ticks(30)
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
        hc = B.hp("census")
        self.hose_states = {}
        for s, h in hs:
            reel = list(g(s, h["reel"]))
            x = next((x for x in hc.get("hoses") or [] if x.get("reel") == reel), {})
            self.hose_states["%d@%d,%d" % (s["n"], reel[0], reel[1])] = {k: x.get(k) for k in ("state", "blend", "couplings", "pathLen")}
        B.probe("poll")
        self.call("rimworld/pause_game", pause=True)

    def labels(self, S, style):
        r = self.B.call("jawa/review_label", action="clear", tag=TAG)
        r = self.B.call("jawa/review_label", action="add", ops=label_ops(S, style), tag=TAG)
        if not r.get("success"):
            self.notes.append("labels: %s" % json.dumps(r)[:300])
        return r

    def goto(self, S, which):
        if which in ("0", "all"):
            x, z, w, h = REGION
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
          "Jump the camera: `human_review.py --goto N` (N = station, 0 = whole gallery, F = free area).", "",
          "## Everywhere", "",
          "- Mod Settings > RimMandrake: Messy Conduit: master switch OFF restores vanilla conduit art instantly, ON brings the cords back.",
          "- Looks (Mod Settings name = `--style` value): Scrapper = StarWarsJawa, Industrial = StarWars, Modern = ExtensionCord, "
          "Futuristic = Cybertek. Each look owns its floor cords, its junction pieces, its power poles and its overhead lines. "
          "Modern also has a colour mode: in 'one colour everywhere' every plug, junction box and wall stub takes that colour.",
          "- Unpause (space) to see motion: sway, live-end sparks, hose filling. Pause again to study a frame.",
          "- Power overlay (bottom-right toggle) still shows vanilla connector lines.", ""]
    for row, name in (("A", "Row A - floor cords"), ("B", "Row B - overhead lines"), ("C", "Row C - flexible hoses"),
                      ("D", "Row D - hose crossings and parallel runs (hoses never branch: no T or + pieces, by ruling)")):
        md += ["## " + name, ""]
        for s in [s for s in S if s["row"] == row]:
            md += ["### %d. %s" % (s["n"], s["title"]), "", s["what"], "", "**Notice**", ""] + ["- " + x for x in s["notice"]] + \
                  ["", "**Try**", ""] + ["- " + x for x in s["interact"]] + [""]
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
<p class="sub">Cable look now: <b>%s</b> (Scrapper = StarWarsJawa, Industrial = StarWars, Modern = ExtensionCord, Futuristic = Cybertek). Game paused, god mode on, clear weather, noon, Peaceful. Jump: <code>human_review.py --goto N</code> (0 = whole gallery, F = free area). Flip every station's look: Mod Settings &rsaquo; RimMandrake: Messy Conduit &rsaquo; Style, or <code>--style StarWars | ExtensionCord | Cybertek | StarWarsJawa</code>.</p>
<div class="box"><b>Everywhere:</b> master switch OFF = vanilla conduit art, ON = cords back, no restart. Unpause (space) for motion: sway, sparks, hoses filling. Power overlay still shows the vanilla connector lines.</div>
<h2>Row A &mdash; floor cords</h2><div class="grid">%s</div>
<h2>Row B &mdash; overhead lines</h2><div class="grid">%s</div>
<h2>Row C &mdash; flexible hoses</h2><div class="grid">%s</div>
<h2>Row D &mdash; hose crossings and parallel runs</h2><p class="sub">Hoses never branch (ruled by card): one hose is one line with two ends. Shown as the system does it today; there is no crossing piece.</p><div class="grid">%s</div>
<h2>F &mdash; free build area</h2><div class="box">Open soil east of the hoses. West end: charged power pad (2 solar, 3 full batteries) with a conduit stub labelled <i>plug in here</i>. South edge: steel, components, wood. God mode builds instantly; research is finished. New masts here auto-link (shipped default); gallery masts are over 20 cells away. <span class="go">--goto F</span></div>
</body></html>""" % (E(LOOK.get(style, style)), "".join(c for c, s in zip(cards, S) if s["row"] == "A"),
                     "".join(c for c, s in zip(cards, S) if s["row"] == "B"), "".join(c for c, s in zip(cards, S) if s["row"] == "C"),
                     "".join(c for c, s in zip(cards, S) if s["row"] == "D"))
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
        r = R.goto(S, a.goto)
        print("framed %s: %s" % (a.goto, r.get("success")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
