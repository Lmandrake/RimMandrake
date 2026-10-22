"""scenarios_map.py -- the FlowWorks COMPOSITE review map: twelve working systems (C1-C12) for one walk.

Owner by card 2026-10-21 ~21:23 PDT: build all twelve in one go (REVIEW_SCENARIOS_BUILD_ALL_TWELVE_AT_ONCE). Design:
design/RimMandrake/flowworks_composite_review_scenarios_2026-10-21.md. Scenario data: northstar/scenarios/cNN_*.py.

    python3    src/RimMandrake/FlowWorks/northstar/scenarios_map.py --plan          # offline: layout + pieces + defs + key sheet
    python3    src/RimMandrake/FlowWorks/northstar/scenarios_map.py --dry-run       # offline: every bridge call, recorded
    python3    src/RimMandrake/FlowWorks/northstar/scenarios_map.py --mock          # offline: build + verify on a MOCK bridge
    python3    src/RimMandrake/FlowWorks/northstar/scenarios_map.py --stage0 --mock # Stage 0 swim-out harness, MOCK
    # LIVE (Windows python.exe; hold the bridge: rimflow bridge take --for "review scenarios live build"):
    python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --stage0 | tr -d '\\r'
    python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --build --fresh-map [--only C3,C12] | tr -d '\\r'
    python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --soak | tr -d '\\r'          # 2 h unattended re-read
    python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --goto C3 | tr -d '\\r'       # C1..C12, S0, F, Z0
    python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --labels | tr -d '\\r'
    python3 src/RimMandrake/Utils/save_guard.py run --current-slot none -- \\
        python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --save --name RM_fw_scenarios_20261021
    python.exe .../scenarios_map.py --branch raid|rain [--name ...]      # branch saves (load the main save first)
    # map R = a SECOND map in the same game (map C and its colonists stay): founds a mild river tile, builds C1 + C11
    python.exe .../scenarios_map.py --river --build --fresh-map [--soak]  # -> review/scenarios/map_r_placed.json
    python.exe .../scenarios_map.py --river --goto C1|C11|R1..R8          # switches to map R, frames
    python.exe .../scenarios_map.py --river --labels                     # re-pin map R's labels (the save's sign
                                                                         # sidecar holds the CURRENT map's labels only)
    # every map-C --goto/--labels/--save/--soak switches back to map C first (ids from map_r_placed.json)

Rules carried from the design (§2, GPT amendments): one clock (10:00, paused); every plot idle-stable until his first
poke (its Start); the build's verify unpauses two in-game hours with nobody poking (--soak) and a plot that changed on
its own FAILS; raids and global weather only in branch saves; labels AND in-save sign books on every scenario (number,
name, START, what to try, what to look for) and on every DEFERRED piece. Staging reuses review_map.Review unchanged
(build_gallery / stage / late_hoses / gizmo_cycle / sweep / save) -- the scenario setups are written in its station
vocabulary, plot-local.

MOCK means MOCK: --dry-run and --mock never touch a game, take no screenshot, and print MOCK on every verdict line.
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
import argparse
import html
import json
import os
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(FW, "..", "..", ".."))
for p in (HERE, FW, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if p not in sys.path:
        sys.path.insert(0, p)
import scenarios as SC  # noqa: E402
from scenarios import common as C  # noqa: E402
from scenarios import stage0_swim_pit as S0SWIM  # noqa: E402
from scenarios.mock_bridge import MockBridge  # noqa: E402

OUT = os.path.join(HERE, "review", "scenarios")
TAG = "fw_scen"
MAP_SIZE = 250
EDGE_SINK = 10
SAVE_MAIN = "RM_fw_scenarios_20261021"
SAVE_RIVER = "RM_fw_scenarios_rivers_20261021"
BRANCH_SAVE = {"raid": "RM_fw_composite_raid", "rain": "RM_fw_composite_rain"}
GAP = 4
GOLD, CREAM, TEAL, RUST, VIOLET = "#ffd27f", "#f2e6cf", "#8fd3c7", "#ff9a6b", "#c8a2ff"

# Packing plan, map C (design §5.1, GPT #14): plots 40-48 cells, lanes >= 4 cells, C10 alone on the east edge.
PLOTS_C = {"C3": (12, 12), "C12": (62, 12), "C5": (112, 12), "C6": (162, 12),
           "C4": (12, 62), "C2": (62, 62), "C8": (112, 62), "C9": (162, 62),
           "C7": (12, 112), "C10": (196, 112)}
FREE = dict(rect=(110, 112, 40, 24),            # round the quicktest colonists (they stand near 125,125)
            stock=[("Steel", 75, (111 + i, 113)) for i in range(4)]
            + [("ComponentIndustrial", 25, (116, 113)), ("WoodLog", 75, (118, 113)), ("WoodLog", 75, (119, 113)),
               ("BlocksGranite", 75, (121, 113)), ("Chemfuel", 75, (123, 113)), ("RM_BottleEmpty", 20, (125, 113)),
               ("RM_ClimbingGear", 1, (127, 113)), ("RM_BarrelEmpty", 5, (129, 113))])
BOARD = dict(rect=(12, 170, 40, 20))             # S0 status board: labels + one sign book
STAGE0 = dict(rect=(62, 140, 8, 12))             # Stage 0 swim-out site (C3's pit geometry)
# DB: the drawbridge PICTURE row (owner 2026-10-22: "Drawbriges need to be looked at in game"; 443912e4df: each part draws
# its MATERIAL picture first, a look only as fallback). Timber and steel, each lowered and raised, over a dry 2 m ditch,
# plus a closed timber gate and a closed steel gate (the closed Timber/Scrapper gate pictures were never picked).
DBROW = dict(rect=(64, 168, 34, 16), ox=64, oz=168,
             bridges=[(0, "timber", "", "lower"), (8, "timber", "", "raise"), (16, "steel", ";winch", "lower"),
                      (24, "steel", ";winch", "raise")],
             gates=[(2, "WoodLog"), (10, "Steel")])
SPECIAL = {"F": FREE["rect"], "S0": BOARD["rect"], "Z0": STAGE0["rect"], "DB": DBROW["rect"]}
CONDUITS = ("PowerConduit", "RM_UniversalPipe", "RM_PitGuardrail", "RM_PitCover_PlankLattice",
            "RM_PitCover_WovenScrap", "RM_PitCover_ReinforcedFrame")


# ------------------------------------------------------------------------------------------------ placement
def placed_c(only=None):
    """[dict(sc, origin, rect)] for the map-C scenarios, design order C1..C12."""
    out = []
    for sc in SC.ALL:
        if sc["map"] != "C" or (only and sc["id"] not in only):
            continue
        ox, oz = PLOTS_C[sc["id"]]
        out.append(dict(sc=sc, origin=(ox, oz), rect=(ox, oz) + tuple(sc["size"])))
    return out


def synthetic_river(size=MAP_SIZE, z0=150, width=10):
    """A straight E-W river for OFFLINE runs only (dry-run, mock, selftest): moving water z0..z0+width-1, soil
    elsewhere. Map R's real river is read live (review_map_rivers.read_terrain)."""
    t = {}
    for x in range(size):
        for z in range(size):
            if z0 <= z < z0 + width:
                t[(x, z)] = "WaterMovingChestDeep" if z0 + 2 <= z < z0 + width - 2 else "WaterMovingShallow"
            else:
                t[(x, z)] = "Soil"
    return t


def river_bank_anchor(terrain, size, w=48, h=40, wet_x=(4, 21), avoid=(), margin=12):
    """C1's plot: origin (x0, z0) whose w x h cells are all land and whose row z0+h (just north of the plot) is moving
    water for every x in wet_x (the intake, the weir and the pump touch it). None when the river offers no such spot
    (reported, never faked; rotated anchoring is owed)."""
    import review_map_rivers as RV
    W_, H_ = size
    best = None
    for z0 in range(margin, H_ - h - margin):
        zb = z0 + h
        for x0 in range(margin, W_ - w - margin):
            if not all(RV.is_moving(terrain.get((x0 + x, zb))) for x in range(wet_x[0], wet_x[1] + 1)):
                continue
            if any(C_overlap((x0, z0, w, h), r, GAP) for r in avoid):
                continue
            if all(RV.is_land(terrain.get((x0 + i, z0 + j))) for i in range(w) for j in range(h)):
                d = abs(x0 + w // 2 - W_ // 2) + abs(z0 + h // 2 - H_ // 2)
                if best is None or d < best[0]:
                    best = (d, (x0, z0))
        if best:
            break
    return best[1] if best else None


def C_overlap(a, b, pad=0):
    return not (a[0] + a[2] + pad <= b[0] or b[0] + b[2] + pad <= a[0] or a[1] + a[3] + pad <= b[1]
                or b[1] + b[3] + pad <= a[1])


def creek_plan(terrain, size, exclude=()):
    """C11: review_map_rivers' eight stations on real crossings, none inside an excluded rect (C1's plot). Same greedy
    as RV.river_anchors (narrow crossings near the centre first, SPACING apart), plus the exclusion."""
    import review_map_rivers as RV
    w, h = size

    def ok(c):
        return RV.MARGIN <= c[0] < w - RV.MARGIN and RV.MARGIN <= c[1] < h - RV.MARGIN

    def clear(c):
        return not any(r[0] - 8 <= c[0] < r[0] + r[2] + 8 and r[1] - 8 <= c[1] < r[1] + r[3] + 8 for r in exclude)
    cand = [c for c in RV.crossings(terrain, size) if ok(c[0]) and ok(c[3]) and clear(c[0]) and clear(c[3])]
    cx, cz = w // 2, h // 2
    cand.sort(key=lambda c: (c[2] > 12, abs(c[0][0] - cx) + abs(c[0][1] - cz), c[0]))
    pick = []
    for c in cand:
        if all(max(abs(c[0][0] - p[0][0]), abs(c[0][1] - p[0][1])) >= RV.SPACING for p in pick):
            pick.append(c)
        if len(pick) == len(RV.STATIONS):
            break
    placed = [(s, c, RV.station_ops(s, c)) for s, c in zip(RV.STATIONS, pick)]
    return placed, [s["id"] for s in RV.STATIONS[len(pick):]]


def placed_r(terrain, size):
    """-> (c1 placement or None, c11 river plan, c11 unplaced ids, notes)."""
    notes = []
    o = river_bank_anchor(terrain, size)
    c1 = None
    if o is None:
        notes.append("C1: no straight south bank with the river to its north on this map (rotated anchoring owed)")
    else:
        sc = SC.BY_ID["C1"]
        c1 = dict(sc=sc, origin=o, rect=o + tuple(sc["size"]))
    plan, unplaced = creek_plan(terrain, size, exclude=[c1["rect"]] if c1 else [])
    for sid in unplaced:
        notes.append("C11: station %s found no free crossing" % sid)
    return c1, plan, unplaced, notes


# ------------------------------------------------------------------------------------------------ expected state
def expected_depth(u):
    """{(x,z): levels} -- dig rects are INCREMENTS (Deepen() N times), so overlapping rects sum."""
    d = Counter()
    for r in u.get("dig", []):
        for c in C.cells_of(r):
            d[c] += r[4]
    return dict(d)


def expected_fill(u):
    f = {}
    for x, z, w, h, lvl, fluid in u.get("fluid", []):
        for c in C.cells_of((x, z, w, h)):
            f[c] = (lvl, fluid)
    return f


def built_defs(u, optional_ok=()):
    n = Counter(r[0] for k in ("build", "spawn", "hostile") for r in u.get(k, []))
    n.update(r[0] for r in u.get("optional_build", []) if r[5] in optional_ok)
    n.update(SCM_MARKER[r[0]] for r in u.get("markers", []) if r[0] in SCM_MARKER)
    return n


from scenarios.mock_bridge import MARKER_DEF as SCM_MARKER  # noqa: E402


# ------------------------------------------------------------------------------------------------ layout check
def layout_check(placed, facts=None, names=None):
    """Every problem with the map-C plan (and each scenario's data), as strings; [] = fit to build. `facts` and `names`
    come from common.def_facts()/def_index() (slow: the selftest passes them once)."""
    probs = []
    rects = [(p["sc"]["id"],) + p["rect"] for p in placed] + [(k,) + v for k, v in SPECIAL.items()]
    for i, a in enumerate(rects):
        if a[1] < 0 or a[2] < 0 or a[1] + a[3] > MAP_SIZE or a[2] + a[4] + 3 > MAP_SIZE:
            probs.append("%s off the map (or no room for its title label): %s" % (a[0], a[1:]))
        for b in rects[i + 1:]:
            if C_overlap(a[1:], b[1:], GAP):
                probs.append("%s and %s closer than %d cells" % (a[0], b[0], GAP))
    for p in placed:
        probs += scenario_check(p, facts, names)
    return probs


def scenario_check(p, facts=None, names=None):
    sc, (ox, oz) = p["sc"], p["origin"]
    sid = sc["id"]
    u = sc["setup"]
    w, h = sc["size"]
    probs = []
    for k in ("name", "purpose", "start", "look_for", "broken", "idle"):
        if not sc.get(k):
            probs.append("%s: no %s" % (sid, k))
    if len(sc["try_"]) < 2:
        probs.append("%s: fewer than two things to try" % sid)
    if not sc["pieces"]:
        probs.append("%s: no pieces" % sid)
    for t in sc["exercises"].values():
        if t not in C.TAGS:
            probs.append("%s: exercise tag %r" % (sid, t))
    cells = C.setup_cells(u)
    edge = sc.get("edge_drain")
    for (x, z), ws in cells.items():
        gx, gz = ox + x, oz + z
        inside = 0 <= x < w and 0 <= z < h
        if not inside:
            drain_ok = (edge == "west" and x < 0 and 0 <= z < h and all(q == "dig" for q in ws)) or \
                       (edge == "east" and x >= w and 0 <= z < h and all(q in ("dig", "fluid") for q in ws))
            if not drain_ok:
                probs.append("%s: %s at plot cell %s outside its %dx%d plot" % (sid, ws, (x, z), w, h))
        if not (0 <= gx < MAP_SIZE and 0 <= gz < MAP_SIZE):
            probs.append("%s: cell %s off the map" % (sid, (gx, gz)))
        elif min(gx, gz, MAP_SIZE - 1 - gx, MAP_SIZE - 1 - gz) < EDGE_SINK and any(q in ("dig", "fluid", "terrain") for q in ws):
            side = "west" if gx < EDGE_SINK else "east" if gx >= MAP_SIZE - EDGE_SINK else "edge"
            if edge != side:
                probs.append("%s: %s cell (%d,%d) in the %d-cell edge-sink strip (drains off the map)"
                             % (sid, ws, gx, gz, EDGE_SINK))
    # footprints: inside the plot, no two solid things on one cell
    occ = {}
    if facts is not None:
        for k in ("build", "spawn", "hostile", "optional_build"):
            for r in u.get(k, []):
                d, x, z = r[0], r[1], r[2]
                rot = r[3] if k in ("build", "hostile", "optional_build") else None
                f = C.fact(facts, d) or {}
                stuff = r[4] if k in ("build", "hostile", "optional_build") else r[3]
                if stuff and f.get("stuffable") is False:
                    probs.append("%s: %s given stuff %s but takes none" % (sid, d, stuff))
                if f.get("stuffable") and not stuff:
                    probs.append("%s: %s at %s needs a stuff (stuffCategories) and has none" % (sid, d, (x, z)))
                for c in C.footprint(x, z, f.get("size"), rot):
                    if not (0 <= c[0] < w and 0 <= c[1] < h) and not (sc["map"] == "R" and c[1] == h):
                        probs.append("%s: %s at %s spills to %s outside the plot" % (sid, d, (x, z), c))
                    if d in CONDUITS:
                        continue
                    if c in occ and occ[c] != (d, x, z):
                        probs.append("%s: %s at %s overlaps %s at %s (cell %s)" % (sid, d, (x, z), occ[c][0],
                                                                                      occ[c][1:], c))
                    occ[c] = (d, x, z)
    # defs
    if names is not None:
        for d, where in C.referenced_defs(u).items():
            if d in names or d in C.RUNTIME_GENERATED or any(w_.startswith("optional") for w_ in where):
                continue
            probs.append("%s: def %s (%s) not in src/ or the game's Data" % (sid, d, ", ".join(sorted(set(where)))))
        for r in u.get("pens", []):
            if r[0] not in names:
                probs.append("%s: pen pawn kind %s unknown" % (sid, r[0]))
    # pieces
    solid = C.solid_cells(u)
    seen_at = set()
    for pc in sc["pieces"]:
        if pc["status"] == "staged":
            if pc["key"] in ("rv_station", "rv_extra"):
                continue
            if not C.find_ref(u, pc):
                probs.append("%s: piece %r: no %s entry %s at %s" % (sid, pc["name"], pc["key"], pc.get("d"), pc.get("at")))
        elif pc["status"] == "DEFERRED":
            if not (pc.get("why") and pc.get("item")):
                probs.append("%s: DEFERRED piece %r without why/item" % (sid, pc["name"]))
            at = pc.get("at")
            if at is not None:
                if tuple(at) in solid or tuple(at) in seen_at or not (0 <= at[0] < w and 0 <= at[1] < h):
                    probs.append("%s: DEFERRED sign for %r at %s is not a free plot cell" % (sid, pc["name"], at))
                seen_at.add(tuple(at))
        else:
            probs.append("%s: piece %r status %r" % (sid, pc["name"], pc["status"]))
    # wild pawns survive the sweep only inside a keep plot
    if any(r[3] not in ("player",) for r in u.get("pawns", [])) and not u.get("keep"):
        probs.append("%s: a non-colonist pawn but no keep=True (the sweep kills it)" % sid)
    bats = {(r[1], r[2]) for r in u.get("build", []) if r[0] == "Battery"}
    if bats != {tuple(b) for b in u.get("batteries", [])}:
        probs.append("%s: batteries %s vs charged %s" % (sid, sorted(bats), sorted(u.get("batteries", []))))
    return probs


# ------------------------------------------------------------------------------------------------ labels and signs
def _wrap(text, width):
    from modcheck import reviewmap as RM
    return RM._wrap(text, width)


def label_ops(placed, extra_board=True):
    from modcheck import reviewmap as RM
    L = []

    def add(x, z, text, sub="", col=GOLD, size="small"):
        L.append(RM.label_line(x, z, text, sub, col, size, TAG))
    for p in placed:
        sc, (ox, oz) = p["sc"], p["origin"]
        w, h = sc["size"] or (0, 0)
        sub = RM.sign_sub("START: " + sc["start"], sc["look_for"], (sc["try_"][1:2] or [""])[0], "broken if: " + sc["broken"])
        add(ox + w // 2, oz + h + 1, "%s  %s" % (sc["id"], sc["name"].upper()), sub, GOLD, "medium")
        for k, line in enumerate(_wrap("%s: %s" % (sc["id"], sc["purpose"]), 70)[:2]):
            add(ox + w // 2, oz + h + 3 + k, line, "", CREAM, "tiny")
        tries = []
        for i, t in enumerate(sc["try_"], 1):
            tries += _wrap("%s try %d: %s" % (sc["id"], i, t), 64)
        for k, line in enumerate(tries[:4]):
            add(ox + w // 2, oz - 1 - k, line, "", CREAM, "tiny")
        for x, z, text in sc["parts"]:
            add(ox + x, oz + z, text, "", RUST, "tiny")
        dl = [pc for pc in sc["pieces"] if pc["status"] == "DEFERRED" and pc.get("at") is not None]
        for k, pc in enumerate(dl):
            # stacked in one column from the first DEFERRED cell (side by side they overprinted, live 2026-10-21)
            x0, z0 = dl[0]["at"]
            step = -2 if z0 > (sc["size"][1] // 2) else 2
            add(ox + x0, oz + z0 + k * step, "DEFERRED: " + pc["name"], pc["item"], VIOLET, "tiny")
    if extra_board:
        bx, bz, bw, bh = BOARD["rect"]
        add(bx + bw // 2, bz + bh, "S0  FLOWWORKS COMPOSITE SCENARIOS: ONE WALK",
            "every plot is still until YOUR first poke (its START); reload the save to reset; raids and rain live in "
            "branch saves", CREAM, "medium")
        for i, sc in enumerate(SC.ALL):
            n_def = sum(1 for pc in sc["pieces"] if pc["status"] == "DEFERRED")
            where = "map R: --river --goto %s" % sc["id"] if sc["map"] == "R" else "--goto %s" % sc["id"]
            add(bx + bw // 2, bz + bh - 2 - i, "%s %s (%s): %d staged, %d DEFERRED" % (
                sc["id"], sc["name"], where, sum(1 for pc in sc["pieces"] if pc["status"] == "staged"), n_def),
                "", CREAM, "tiny")
        ox, oz = DBROW["ox"], DBROW["oz"]
        add(ox + 16, oz + 15, "DB  DRAWBRIDGE PICTURES", "timber and steel, lowered and raised; two closed gates. Each "
            "part draws its MATERIAL picture; a look shows only where no picture exists", GOLD, "medium")
        for dx, tier, w_, st in DBROW["bridges"]:
            add(ox + dx + 2, oz + 9, "%s %s" % (tier, "raised" if st == "raise" else "lowered"), "", RUST, "tiny")
        for dx, stuff in DBROW["gates"]:
            add(ox + dx, oz + 13, "gate (%s), closed" % ("timber" if stuff == "WoodLog" else "steel"), "", RUST, "tiny")
        fx, fz, fw, fh = FREE["rect"]
        add(fx + fw // 2, fz + fh + 1, "F  FREE AREA", "steel, components, wood, granite, chemfuel, bottles, climbing "
            "gear (south edge)", RUST)
    return "\n".join(L)


def sign_ops(placed, extra_board=True):
    """In-save sign books (vanilla Novels: they survive a plain load): one at each scenario's entrance (its NW corner,
    on the lane), one per DEFERRED piece at its cell, one on the S0 board."""
    from modcheck import reviewmap as RM
    L = []
    for p in placed:
        sc, (ox, oz) = p["sc"], p["origin"]
        h = (sc["size"] or (0, 0))[1]
        defs = [pc for pc in sc["pieces"] if pc["status"] == "DEFERRED"]
        more = "TRY: " + " | ".join("%d) %s" % (i, t) for i, t in enumerate(sc["try_"], 1))
        more += " || STILL UNTIL POKED: " + sc["idle"] + " || " + sc["reset"]
        if defs:
            more += " || DEFERRED: " + "; ".join("%s (%s)" % (pc["name"], pc["item"]) for pc in defs)
        if sc["branch"]:
            more += " || BRANCH SAVES: " + "; ".join(sc["branch"].values())
        L.append(RM.sign_book(ox, oz + h, sc["id"], sc["name"], sc["purpose"] + " START: " + sc["start"],
                              sc["look_for"], (sc["try_"] or [""])[0], "broken if: " + sc["broken"], more=more))
        for k, pc in enumerate(defs, 1):
            if pc.get("at") is None:
                continue
            L.append(RM.sign_book(ox + pc["at"][0], oz + pc["at"][1], "%s.D%d" % (sc["id"], k), "DEFERRED " + pc["name"],
                                  pc["why"], "", "", "", more="Builds under: %s" % pc["item"]))
    if extra_board:
        bx, bz, bw, bh = BOARD["rect"]
        L.append(RM.sign_book(bx, bz + bh - 1, "S0", "Composite scenarios",
                              "Twelve working systems; every plot is still until your first poke. Raids and rain: "
                              "branch saves %s." % ", ".join(BRANCH_SAVE.values()), "", "walk C3 first (the maze)",
                              "", more="; ".join("%s %s" % (s["id"], s["name"]) for s in SC.ALL)))
        L.append(RM.sign_book(DBROW["ox"], DBROW["oz"] + 14, "DB", "Drawbridge pictures",
                              "Timber and steel drawbridges, lowered and raised, and two closed gates.",
                              "each leaf, winch and gate draws its MATERIAL picture (timber/steel); a look is the "
                              "fallback only", "lower/raise one at its winch; open a gate",
                              "which pictures to keep, which to redraw"))
    return L


# ------------------------------------------------------------------------------------------------ build (live or mock)
def review_class():
    import review_map as RVM

    class ScenarioReview(RVM.Review):
        """review_map.Review staging, plus the composite-only keys, one clock (10:00) and the per-plot verify/soak."""

        def calm_at(self, hour=C.CLOCK_HOUR):
            self.calm()                                # weather, Peaceful, sweep, research, god mode (pins noon)
            self.pin_clock(hour)

        def pin_clock(self, hour=C.CLOCK_HOUR):
            """Jump (no simulation) to the next `hour`:00 local. Never calm() here: it sweeps every held pawn."""
            clk, mi = self.B.call("jawa/time_clock"), self.B.call("jawa/map_info")
            lon = mi.get("longitude")
            if isinstance(clk.get("ticksAbs"), int) and isinstance(lon, (int, float)):
                local = (clk["ticksAbs"] + int(round(lon / 360.0 * 60000))) % 60000
                add = (hour * 2500 - local) % 60000
                if add:
                    self.call("jawa/time_set_ticks", ticks=clk["ticksGame"] + add, timeException=True)

        def stations(self, placed):
            return [dict(n=p["sc"]["n"], id=p["sc"]["id"], origin=p["origin"], setup=p["sc"]["setup"],
                         placeholder=False) for p in placed]

        def clear_plots(self, placed):
            B = self.B
            B.call("jawa/review_label", action="clear", tag=TAG)
            for p in placed:
                x, z, w, h = p["rect"]
                # 2026-10-22 night walk (SITE): x-4, not x-2 -- a reel built with no rotation faces WEST (its default; reels turn
                # 4 ways since 73b8805755), so a reel at a plot's west edge needs ~3.5 cells for its lead-out + U-turn; C3's reel
                # park met map limestone at x 8-9 ("no room for the straight lead-out"). Plots stay >= 2 cells apart.
                rects = [(x - 4, z - 6, w + 8, h + 12)]
                soil = None
                if p["sc"]["map"] == "R":
                    # map R: the margin stops at the plot's north edge (row z+h is the RIVER C1's intake, weir and pump touch),
                    # and only the plot itself is repainted Soil (the anchor proved it land; a margin may hold a river bend)
                    rects, soil = [(x - 4, z - 6, w + 8, h + 6)], "Soil:%d,%d,%d,%d" % (x, z, w, h)
                e = p["sc"].get("edge_drain")
                if e == "west":
                    rects.append((0, z, x, h))
                if e == "east":
                    rects.append((x + w, z, MAP_SIZE - x - w, h))
                for rx, rz, rw, rh in rects:
                    rx, rz = max(0, rx), max(0, rz)
                    rr = "%d,%d,%d,%d" % (rx, rz, rw, rh)
                    ex = B.call("jawa/flowworks_excavation_rect", x=rx, z=rz, w=rw, h=rh, onlyNonZero=True,
                                includeTerrain=False)
                    for c in ex.get("rows") or []:
                        if c.get("isExcavated"):
                            B.call("jawa/flowworks_excavation_drive", x=c["x"], z=c["z"], deepenLevels=0, setFill=0,
                                   fillInLevels=int(c.get("d") or 0))
                    for q in B.call("jawa/list_pawns", rect=rr, limit=200).get("pawns") or []:
                        B.call("jawa/set_pawn_faction", pawn=str(q.get("id")), faction="none")
                    B.call("jawa/destroy_batch", rects=rr, categories="All")
                    B.call("jawa/set_terrain_batch", ops=soil or "Soil:" + rr)
                    B.call("jawa/set_fog", action="unfog", rect=rr)
                    B.call("jawa/set_roof_batch", ops="None:" + rr)
                    for area in ("BuildRoof", "Home"):
                        B.call("jawa/paint_area", area=area, ops=rr, value=False)
            B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)

        def extras(self, p, optional_ok):
            """The composite-only keys that need no pawns: optional builds, plants, batteries, markers, proof calls."""
            sc, (ox, oz) = p["sc"], p["origin"]
            u, n = sc["setup"], sc["id"]
            g = lambda x, z: (ox + x, oz + z)  # noqa: E731
            for d, x, z, rot, stuff, need in u.get("optional_build", []):
                if need not in optional_ok:
                    self.notes.append("%s: %s not loaded on this mod list; %s skipped (sign says so)" % (n, need, d))
                    continue
                kw = dict(ops="%s:%d,%d" % ((d,) + g(x, z)) + ("" if rot is None else ",%d" % rot), faction="player",
                          wipeExisting=False)
                if stuff:
                    kw["stuff"] = stuff
                self.call("jawa/build_batch", **kw)
            for d, x, z in u.get("spawn_plants", []):
                self.call("rimworld/spawn_thing", defName=d, stackCount=1, x=g(x, z)[0], z=g(x, z)[1])
            for x, z in u.get("batteries", []):
                th = self.B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,1" % g(x, z), limit=3).get("things") or []
                r = self.call("jawa/battery_set", thing=th[0].get("id"), mode="setPct", value=1.0) if th else {}
                if not (r or {}).get("storedEnergyPctAfter"):
                    self.notes.append("%s: battery at %s NOT charged (%s)" % (n, (x, z), str(r)[:120]))
            for method, x, z, tail in u.get("markers", []):
                self.static(n, C.MAPCTL, method, "%d,%d" % g(x, z) + ("|" + tail if tail else ""))
            for c in u.get("calls", []):
                args = c["fmt"].format(*["%d,%d" % g(*cc) for cc in c["cells"]])
                res = self.static(n, c["typ"], c["method"], args)
                if "ok=False" in res:          # a proof that answers but did not build (live 2026-10-21: drawbridge)
                    self.notes.append("%s %s(%s): %s" % (n, c["method"], args, res[:240]))

        def gizmos(self, p):
            sc, (ox, oz) = p["sc"], p["origin"]
            for x, z, prefix, want in sc["setup"].get("gizmos", []):
                self.gizmo_cycle(sc["id"], (ox + x, oz + z), prefix, want)
            # live 2026-10-21: a ladder's "Ladder up" button now ORDERS a climb job ("Ladder up (ordered)"); the
            # staging route is its DEV instant button, which names the OTHER state once it is reached
            for x, z, op in sc["setup"].get("ladder_dev", []):
                cell, press, done = (ox + x, oz + z), "DEV: ladder %s now" % ("up" if op == "raise" else "down"), \
                    "DEV: ladder %s now" % ("down" if op == "raise" else "up")
                B = self.B
                B.call("rimworld/clear_selection")
                B.call("rimworld/click_cell", x=cell[0], z=cell[1])
                gz = (B.call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
                g = next((q for q in gz if q.get("label") == press), None)
                if g is not None:
                    B.call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id"))
                    gz = (B.call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
                if not any(q.get("label") == done for q in gz):
                    self.notes.append("%s: ladder at %s not %s (gizmos %s)" % (sc["id"], (x, z), op,
                                                                           [q.get("label") for q in gz][:6]))
                B.call("rimworld/clear_selection")

        def pawns(self, p, key="pawns", ops_key="pawn_ops"):
            sc, (ox, oz) = p["sc"], p["origin"]
            u = sc["setup"]
            ids = {}
            rows = u.get(key, [])
            for r in rows:
                kind, x, z, fac = r[0], r[1], r[2], r[3]
                role = r[4] if len(r) > 4 else ("drafted" if key == "pens" else None)
                res = self.call("jawa/spawn_pawn", kindDef=kind, x=ox + x, z=oz + z, faction=fac, count=1)
                pid = (res.get("pawns") or [{}])[0].get("id") if res.get("pawns") else res.get("id") or res.get("pawnId")
                if pid is None:
                    self.notes.append("%s: %s at %s not spawned" % (sc["id"], kind, (x, z)))
                    continue
                ids[(x, z)] = str(pid)
                if role == "drafted" and fac == "player":
                    self.call("jawa/set_draft", pawnId=str(pid), drafted=True)
                elif role == "prisoner":
                    self.call("jawa/pawn_set_guest_status", pawn=str(pid), guestStatus="Prisoner", hostFaction="PlayerColony")
            for x, z, op, arg in u.get(ops_key, []):
                pid = ids.get((x, z))
                if pid is None:
                    self.notes.append("%s: %s %s: no pawn at %s" % (sc["id"], op, arg, (x, z)))
                    continue
                if op == "wear":
                    r = self.call("jawa/pawn_gear", **{"pawn": pid, "action": "wear", "def": arg, "stuff": ""})
                elif op == "need":
                    nd, lv = arg.split("=")
                    r = self.call("jawa/pawn_need", pawn=pid, action="need", need=nd, level=float(lv))
                elif op == "name":
                    r = self.call("jawa/set_pawn_identity", pawn=pid, nick=arg)
                else:
                    r = {"success": False}
                if not r.get("success", True):
                    self.notes.append("%s: %s %s on %s refused" % (sc["id"], op, arg, (x, z)))
            return ids

        def build(self, placed):
            B = self.B
            optional = sorted({r[5] for p in placed for r in p["sc"]["setup"].get("optional_build", [])})
            r = B.call("jawa/get_defs", defs=";".join("ThingDef/" + d for d in optional)) if optional else {}
            missing = " ".join(str(m) for m in (r or {}).get("notFound") or [])
            ok_opt = {d for d in optional if d not in missing}
            S = self.stations(placed)
            self.build_gallery(S)                        # review_map's staging, unchanged (calls late_hoses itself)
            for p in placed:
                self.extras(p, ok_opt)
            for p in placed:
                self.gizmos(p)
            self.call("jawa/flowworks_pulse", count=30, x=0, z=0, w=0, h=0)
            for p in placed:
                if p["sc"]["setup"].get("refill_after_pulse"):
                    ox, oz = p["origin"]
                    for x, z, w, h, f, fl in p["sc"]["setup"].get("fluid", []):
                        for i in range(w):
                            for j in range(h):
                                self.static(p["sc"]["id"], C.FLUID, "ProofFillWithFluid",
                                            "%d,%d,%d,%s" % (ox + x + i, oz + z + j, f, fl))
            for p in placed:
                self.pawns(p)
            return ok_opt

        def keep_rects(self, placed):
            return [p["rect"] for p in placed if p["sc"]["setup"].get("keep") or p["sc"]["setup"].get("pens")]

        def snapshot(self, p):
            """Dug cells (depth, fill), the STAGED defs' counts and the staged pawn kinds' counts. Wild plants that
            spread, hauled loose items and passers-by are not the plot's state (live soak 2026-10-21)."""
            x, z, w, h = p["rect"]
            ex = self.B.call("jawa/flowworks_excavation_rect", x=x, z=z, w=w, h=h, onlyNonZero=True, includeTerrain=False)
            dug = {(c["x"], c["z"]): (c.get("d"), c.get("f")) for c in ex.get("rows") or [] if c.get("isExcavated")}
            th = self.B.call("jawa/list_things", rect="%d,%d,%d,%d" % p["rect"], limit=2000).get("things") or []
            u = p["sc"]["setup"]
            want_defs = set(built_defs(u, ("RM_PipeAdapter_Chemfuel",)))
            defs = Counter(t.get("def") or t.get("defName") for t in th if (t.get("def") or t.get("defName")) in want_defs)
            pw = self.B.call("jawa/list_pawns", rect="%d,%d,%d,%d" % p["rect"], limit=200).get("pawns") or []
            kinds = {r[0] for r in u.get("pawns", [])}
            return dict(dug=dug, defs=defs, pawns=Counter(q.get("kind") or q.get("kindDef") for q in pw
                                                          if (q.get("kind") or q.get("kindDef")) in kinds and
                                                          not (q.get("kind") == "Colonist" and not q.get("drafted", True))))

        def verify_plots(self, placed, optional_ok=()):
            out = {}
            for p in placed:
                sc, (ox, oz) = p["sc"], p["origin"]
                u = sc["setup"]
                snap = self.snapshot(p)
                want_d = {(ox + x, oz + z): d for (x, z), d in expected_depth(u).items()
                          if 0 <= x < sc["size"][0] and 0 <= z < sc["size"][1]}
                bad_d = {c: (snap["dug"].get(c, (0, 0))[0], d) for c, d in want_d.items() if snap["dug"].get(c, (0, 0))[0] != d}
                bad_f = {}
                if not sc.get("fluid_moves"):
                    for (x, z), (lvl, fl) in expected_fill(u).items():
                        c = (ox + x, oz + z)
                        if c in snap["dug"] and snap["dug"][c][1] != lvl:
                            bad_f[c] = (snap["dug"][c][1], lvl)
                need = built_defs(u, optional_ok)
                miss = {d: n - snap["defs"].get(d, 0) for d, n in need.items() if snap["defs"].get(d, 0) < n}
                want_k = Counter(r[0] for r in u.get("pawns", []))
                short = dict(want_k - snap["pawns"])
                ok = not (bad_d or bad_f or miss or short)
                out[sc["id"]] = dict(ok=ok, dug=len(snap["dug"]), want_dug=len(want_d), depth_wrong=len(bad_d),
                                     fill_wrong=len(bad_f), missing=miss, pawns_short=short,
                                     first_bad=[str(x) for x in list(bad_d.items())[:3] + list(bad_f.items())[:3]])
            return out

        def soak(self, placed, ticks=C.SOAK_TICKS):
            """GPT #1: two in-game hours with nobody poking; a plot whose dug cells, buildings or pawn kinds changed
            FAILS. (Item health, filth, plants and tank stocks are not read: see each plot's idle note.)"""
            before = {p["sc"]["id"]: self.snapshot(p) for p in placed}
            self.call("rimworld/step_game_ticks", ticks=ticks, pauseFirst=True, timeoutMs=max(120000, ticks * 40))
            self.call("rimworld/pause_game", pause=True)
            out = {}
            for p in placed:
                a, b = before[p["sc"]["id"]], self.snapshot(p)
                dd = {str(c): (a["dug"].get(c), b["dug"].get(c)) for c in set(a["dug"]) | set(b["dug"])
                      if a["dug"].get(c) != b["dug"].get(c)}
                out[p["sc"]["id"]] = dict(still=not dd and a["defs"] == b["defs"] and a["pawns"] == b["pawns"],
                                          dug_changed=len(dd), first=list(dd.items())[:3],
                                          defs_changed=dict((a["defs"] - b["defs"]) + (b["defs"] - a["defs"])),
                                          pawns_changed=dict((a["pawns"] - b["pawns"]) + (b["pawns"] - a["pawns"])))
            return out

        def place_labels(self, placed):
            self.B.call("jawa/review_label", action="clear", tag=TAG)
            r = self.B.call("jawa/review_label", action="add", ops=label_ops(placed), tag=TAG)
            if not r.get("success"):
                self.notes.append("labels: %s" % json.dumps(r)[:300])
            return r

        def drawbridge_row(self):
            """DB: four drawbridges (timber/steel x lowered/raised) over dry 2 m ditches, two closed gates."""
            ox, oz = DBROW["ox"], DBROW["oz"]
            x, z, w, h = DBROW["rect"]
            rr = "%d,%d,%d,%d" % (x, z, w, h)
            self.call("jawa/destroy_batch", rects=rr, categories="All")
            self.call("jawa/set_terrain_batch", ops="Soil:" + rr)
            self.call("jawa/set_fog", action="unfog", rect=rr)
            self.call("jawa/set_roof_batch", ops="None:" + rr)
            for dx, tier, winch, state in DBROW["bridges"]:
                bx, bz = ox + dx, oz + 6
                for i in range(1, 4):
                    for j in range(-2, 3):
                        self.call("jawa/flowworks_excavation_drive", x=bx + i, z=bz + j, deepenLevels=4, setFill=-1)
                self.static("DB", C.DPROOF, "ProofMakeDrawbridge", "%d,%d;%d,%d;%s;A%s" % (bx, bz, bx + 4, bz, tier, winch))
                if winch:
                    self.static("DB", C.DPROOF, "ProofWinchPower", "%d,%d;on" % (bx + 2, bz))
                if state == "raise":
                    self.static("DB", C.DPROOF, "ProofDevSet", "%d,%d;raise;instant" % (bx + 2, bz))
            for dx, stuff in DBROW["gates"]:
                self.call("jawa/build_batch", ops="RM_DrawbridgeGate:%d,%d" % (ox + dx, oz + 12), faction="player",
                          wipeExisting=False, stuff=stuff)

        def free(self):
            x, z, w, h = FREE["rect"]
            self.call("jawa/destroy_batch", rects="%d,%d,%d,2" % (x, z, w), categories="All")
            for d, n_, c in FREE["stock"]:
                self.call("rimworld/spawn_thing", defName=d, stackCount=n_, x=c[0], z=c[1])

        def goto_(self, placed, which):
            w_ = which.upper()
            if w_ in SPECIAL:
                x, z, ww, hh = SPECIAL[w_]
            else:
                p = next((q for q in placed if q["sc"]["id"] == w_), None)
                if p is None:
                    raise SystemExit("--goto %s: unknown; valid: %s, %s" % (which, ", ".join(q["sc"]["id"] for q in placed),
                                                                           ", ".join(SPECIAL)))
                x, z, ww, hh = p["rect"]
                z, hh = z - 5, hh + 10
            return self.B.call("rimworld/frame_cell_rect", x=x - 2, z=z - 2, width=ww + 4, height=hh + 4, paddingCells=2)

    return ScenarioReview


def run_build(B, placed, log=None, fresh=False, soak=True, only=None):
    """The whole map-C build on bridge B (live or mock). -> result dict."""
    from modcheck import reviewmap as RM
    R = review_class()(B, log)
    t0 = time.time()
    if fresh:
        R.fresh_map()
    R.calm_at()
    R.clear_plots(placed)
    ok_opt = R.build(placed)
    R.free()
    if not only:
        R.drawbridge_row()
    R.call("jawa/map_commit")
    B.ticks(2)
    R.call("rimworld/pause_game", pause=True)
    R.sweep(R.keep_rects(placed))
    ver = R.verify_plots(placed, ok_opt)
    R.place_labels(placed)
    ops = sign_ops(placed)
    sg = RM.place_signs(B, ops)
    if sg.get("count") != len(ops):
        R.notes.append("sign books: %s of %s placed (%s)" % (sg.get("count"), len(ops), str(sg.get("refused"))[:200]))
    soaked = R.soak(placed) if soak else None
    B.call("jawa/clear_ui", all=True)
    return dict(verify=ver, soak=soaked, notes=R.notes, signs=sg.get("count"), sign_ops=len(ops),
                labels=len(label_ops(placed).split("\n")), wall_s=round(time.time() - t0, 1), optional=sorted(ok_opt))


MAP_R_PLACED = os.path.join(OUT, "map_r_placed.json")   # map ids + C1 + the C11 stations of the LAST map-R build


def r_labels(c1, plan):
    """Map R's label ops: C1's plot labels, the C11 headline and the R1-R8 station labels."""
    import review_map_rivers as RV
    from modcheck import reviewmap as RM
    lab = label_ops([c1] if c1 else [], extra_board=False)
    if plan:
        c11 = SC.BY_ID["C11"]
        x, z = plan[0][2]["label"]
        sub = RM.sign_sub("START: " + c11["start"], c11["look_for"], c11["try_"][1], "broken if: " + c11["broken"])
        lab += "\n" + RM.label_line(x, z + 3, "C11  PROSPECTOR'S CREEK (stations R1-R%d)" % len(plan), sub, GOLD, "medium", TAG)
        lab += "\n" + RV.label_ops(plan, RM.label_line)
    return lab


def r_colonist_cells(size, avoid, n=3):
    """n cells for map R's own colonists (map C keeps its own): along z 20, then z 60, away from every avoid rect +4."""
    w, h = size
    out = []
    for z in (20, 60, h - 20):
        for x in range(w // 2 - 30, w // 2 + 30, 2):
            if len(out) < n and not any(C_overlap((x, z, 1, 1), r, 4) for r in avoid):
                out.append((x, z))
    return out


def run_river(B, terrain, size, log=None, soak=False):
    """Map R: C1 on its bank anchor, C11 on the creek plan; labels + signs for both and the R stations; three drafted
    colonists of its own; non-colonists swept outside the plots. -> result dict (incl. 'placed' for MAP_R_PLACED)."""
    import review_map_rivers as RV
    from modcheck import reviewmap as RM
    R = review_class()(B, log)
    c1, plan, unplaced, notes = placed_r(terrain, size)
    R.notes += notes
    placed = [c1] if c1 else []
    if c1:
        R.clear_plots(placed)
        R.build(placed)
    for k, (st, cr, o) in enumerate(plan):
        for t, (x, z) in o["terrain"]:
            R.call("jawa/set_terrain_batch", ops="%s:%d,%d,1,1" % (t, x, z))
        for d, (x, z), rot, stuff in o["build"]:
            kw = dict(ops="%s:%d,%d" % (d, x, z) + ("" if rot is None else ",%d" % rot), faction="player", wipeExisting=False)
            if stuff:
                kw["stuff"] = stuff
            R.call("jawa/build_batch", **kw)
        for d, n_, (x, z) in o["items"]:
            R.call("rimworld/spawn_thing", defName=d, stackCount=n_, x=x, z=z)
        for kind, (x, z), fac, role in o["pawns"]:
            R.call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=fac, count=1)
        if st["id"] == "r_ford":                      # C11's control colonist: in the moving water beside the stones
            (bx, bz), d = cr[0], cr[1]
            p_ = (-d[1], d[0])
            R.call("jawa/spawn_pawn", kindDef="Colonist", x=bx + d[0] + 2 * p_[0], z=bz + d[1] + 2 * p_[1],
                   faction="player", count=1)
    avoid = [c1["rect"]] if c1 else []
    avoid += [(min(cr[0][0], cr[3][0]) - 3, min(cr[0][1], cr[3][1]) - 3, abs(cr[0][0] - cr[3][0]) + 7,
               abs(cr[0][1] - cr[3][1]) + 7) for _, cr, _ in plan]
    for x, z in r_colonist_cells(size, avoid):        # map R's own hands (the walk's pokes need someone here)
        sp = B.call("jawa/spawn_pawn", kindDef="Colonist", x=x, z=z, faction="player", count=1) or {}
        for q in sp.get("pawns") or []:
            if q.get("id"):
                B.call("jawa/set_draft", pawnId=q["id"], drafted=True)
    if c1:
        B.call("jawa/map_commit")
        B.ticks(2)
    B.call("rimworld/pause_game", pause=True)
    ver = R.verify_plots(placed) if placed else {}
    lab = r_labels(c1, plan)
    B.call("jawa/review_label", action="clear", tag=TAG)
    lr = B.call("jawa/review_label", action="add", ops=lab, tag=TAG) or {}
    if lr.get("success") is False:
        R.notes.append("map R labels: %s" % json.dumps(lr)[:200])
    ops = sign_ops(placed, extra_board=False) + (RV.sign_ops(plan) if plan else [])
    if plan:
        c11 = SC.BY_ID["C11"]
        x, z = plan[0][2]["label"]
        defs = [pc for pc in c11["pieces"] if pc["status"] == "DEFERRED"]
        ops.append(RM.sign_book(x, z + 2, "C11", c11["name"], c11["purpose"] + " START: " + c11["start"],
                                c11["look_for"], c11["try_"][0], "broken if: " + c11["broken"],
                                more="TRY: " + " | ".join(c11["try_"]) + " || DEFERRED: "
                                + "; ".join("%s (%s)" % (pc["name"], pc["item"]) for pc in defs)))
    sg = RM.place_signs(B, ops)
    soaked = R.soak(placed) if (soak and placed) else None
    B.call("jawa/clear_ui", all=True)
    rows = [dict(n=k + 1, id=st["id"], crossing=[list(cr[0]), list(cr[1]), cr[2], list(cr[3])], label=list(o["label"]))
            for k, (st, cr, o) in enumerate(plan)]
    return dict(c1=c1["origin"] if c1 else None, c11=len(plan), unplaced=unplaced, verify=ver, notes=R.notes,
                signs=sg.get("count"), sign_ops=len(ops), soak=soaked,
                placed=dict(c1=dict(origin=list(c1["origin"]), rect=list(c1["rect"])) if c1 else None, stations=rows))


def load_map_r(path=MAP_R_PLACED):
    """-> (doc, c1 placement or None, C11 plan as review_map_rivers tuples). SystemExit when map R was never built."""
    import review_map_rivers as RV
    if not os.path.exists(path):
        raise SystemExit("map R was never built here (%s missing): run --river --build --fresh-map first" % path)
    doc = json.load(open(path, encoding="utf-8"))
    c1 = None
    if doc.get("c1"):
        o = tuple(doc["c1"]["origin"])
        c1 = dict(sc=SC.BY_ID["C1"], origin=o, rect=tuple(doc["c1"]["rect"]))
    by = {s["id"]: s for s in RV.STATIONS}
    plan = []
    for r in doc.get("stations") or []:
        b, d, n, e = r["crossing"]
        plan.append((by[r["id"]], (tuple(b), tuple(d), n, tuple(e)), dict(label=tuple(r["label"]))))
    return doc, c1, plan


def use_map(B, which):
    """Make map C or map R current (ids from MAP_R_PLACED). Silent no-op when no map-R build is recorded (a one-map
    game); a refusal is printed, never hidden. -> True when the wanted map is current (read back)."""
    if not os.path.exists(MAP_R_PLACED):
        return which == "C"
    mid = json.load(open(MAP_R_PLACED, encoding="utf-8")).get("map_" + which.lower())
    if not isinstance(mid, int):
        return which == "C"
    r = B.call("jawa/set_current_map", mapId=mid) or {}
    if not r.get("success"):
        print("set_current_map %s (map %s) refused: %s" % (mid, which, str(r)[:200]))
        return False
    return True


def found_map_r(B, max_tries=25):
    """Found map R as a SECOND map in the current game (map C and its colonists stay): a mild river tile whose map has a
    current, moving water on >= 2 edges, AND a straight south bank for C1 plus >= 6 C11 crossings. river_site.py's tile
    filters and readers, minus its colonist vanish / bland reset (those would gut map C). A fast lane is NOT required
    (quicktest worlds rarely have one: 20 of 20 river tiles fast=0, 2026-10-18; C11 needs a current, not a fast lane).
    -> dict(map_c, map_r, tile, size, terrain, problems); map_r None when no tile qualified."""
    import csv
    import tempfile
    import river_site as RS                       # first: it puts Utils/modcheck (bland_world) on sys.path
    import bland_world as BW
    import extensions_rivers as RIV
    import review_map_rivers as RV
    import site_spec as SS
    RS.ALLOW_NO_FAST = True
    out = dict(map_c=(B.call("jawa/map_info") or {}).get("mapId"), map_r=None, tile=None, problems=[])
    path = os.path.join(os.environ.get("TEMP") or tempfile.gettempdir(), "scenarios_map_r_tiles.csv")
    r = B.call("jawa/world_tile_export", path=path) or {}
    if not r.get("success") or not os.path.isfile(path):
        out["problems"].append("world_tile_export failed: %s" % str(r)[:200])
        return out
    with open(path, encoding="utf-8") as f:
        cands = RS.river_candidates(list(csv.DictReader(f)))
    river = []
    for i in range(0, len(cands), 100):
        wg = B.call("jawa/world_tile_get", tiles=",".join(str(t) for t in cands[i:i + 100])) or {}
        river += [g for g in wg.get("tiles") or [] if int(g.get("riverCount") or 0) > 0]
    print("map R: %d mild candidates, %d with a river" % (len(cands), len(river)))
    tries, generated = 0, []
    for row in river:
        if tries >= max_tries:
            break
        t = int(row["tile"])
        if not (B.call("jawa/colony_found", tile=t, faction="Player", name="FlowWorksCreek") or {}).get("success"):
            continue
        tries += 1
        BW.close_naming_dialogs(B)
        g = B.call("jawa/world_tile_map_generate", tile=t, suggestedMapParent="Settlement") or {}
        mid = RS.generated_map_id(g)
        fresh = bool(g.get("success")) and not g.get("wasAlreadyGenerated")
        if fresh:
            generated.append(t)

        def drop(why, t=t, fresh=fresh):
            print("map R: tile %s rejected: %s" % (t, why))
            if fresh:
                B.call("jawa/settlement_remove", mode="map", tile=t, force=True)
        if mid is None:
            drop("map generate refused or gave no mapId: %s" % str(g)[:160])
            continue
        BW.close_naming_dialogs(B)
        if not (B.call("jawa/set_current_map", mapId=mid) or {}).get("success"):
            drop("set_current_map refused")
            continue
        grid = str((B.call("jawa/static_call", type="RimMandrake.FlowWorks.Rivers.RM_RiverWorksProof", method="ProofGrid",
                           args="-") or {}).get("result", ""))
        kv = dict(q.split("=", 1) for q in grid.split() if "=" in q)
        mi = B.call("jawa/map_info") or {}
        size = (int(mi.get("sizeX", 250)), int(mi.get("sizeZ", mi.get("sizeY", 250))))
        tb = B.call("jawa/get_terrain_batch", rects=RIV.edge_rects(size)) or {}
        edges = RIV.moving_edges(SS.parse_ops(tb.get("ops")), size) if tb.get("success") else None
        why = RS.river_reject(kv, edges, False, tile=t, map_tile=mi.get("tile"))
        if not why:
            terrain = RV.read_terrain(B, size)
            c1, plan, unplaced, _ = placed_r(terrain, size)
            if c1 is None:
                why = "no straight south bank for C1"
            elif len(plan) < 6:
                why = "only %d of 8 C11 crossings" % len(plan)
        if why:
            if mi.get("mapId") == mid:
                use_map_id = out["map_c"]
                if isinstance(use_map_id, int):
                    B.call("jawa/set_current_map", mapId=use_map_id)
            drop(why)
            continue
        out.update(map_r=mid, tile=t, size=size, terrain=terrain)
        break
    for m in RS.leftover_maps(RS.loaded_maps(B.call), out["map_r"], generated):
        B.call("jawa/settlement_remove", mode="map", tile=m.get("tile"), force=True)
    if out["map_r"] is None:
        if isinstance(out["map_c"], int):
            B.call("jawa/set_current_map", mapId=out["map_c"])
        out["problems"].append("no river tile qualified among %d tried" % tries)
        return out
    B.call("jawa/set_current_map", mapId=out["map_r"])
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    B.call("jawa/incident_queue_clear")
    d = B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False) or {}
    if d.get("success") is not True:
        out["problems"].append("destroy_bulk nonColonists refused on map R: %s" % str(d)[:160])
    B.call("jawa/set_fog", action="unfog", rect="0,0,%d,%d" % size)
    return out


def river_main(B, a):
    """--river: map R (C1 + C11) in the SAME game as map C. --build [--fresh-map] [--soak] | --labels | --goto ID."""
    import review_map_rivers as RV
    from modcheck import reviewmap as RM
    if a.build:
        if a.fresh_map:
            info = found_map_r(B)
            if info["map_r"] is None:
                print("map R NOT founded: %s" % info["problems"])
                return 2
            size, terrain = info["size"], info["terrain"]
        else:                                           # the current map IS map R (river_site.py made it, a one-map game)
            mi = B.call("jawa/map_info") or {}
            size = (int(mi.get("sizeX") or 0), int(mi.get("sizeZ") or 0))
            terrain = RV.read_terrain(B, size)
            info = dict(map_c=None, map_r=mi.get("mapId"), tile=mi.get("tile"), problems=[])
        res = run_river(B, terrain, size, a.log, soak=a.soak)
        doc = dict(map_c=info["map_c"], map_r=info["map_r"], tile=info["tile"], built=time.strftime("%Y-%m-%dT%H:%M:%S"),
                   **res.pop("placed"))
        with open(MAP_R_PLACED, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=1)
        with open(os.path.join(REPO, "Transient", "fw_scenarios_river_verify.json"), "w", encoding="utf-8") as f:
            json.dump(dict(res, founding=info.get("problems")), f, indent=1, default=str)
        v = res["verify"].get("C1", {})
        moved = [s for s, x in (res["soak"] or {}).items() if not x["still"]]
        print("LIVE map R (tile %s, map %s; map C = %s): C1 at %s %s; C11 %d of 8 stations%s; %d of %d sign books; soak %s; "
              "%d notes -> %s" % (info["tile"], info["map_r"], info["map_c"], res["c1"], "OK" if v.get("ok") else "FAIL %s" % v,
                                  res["c11"], " (unplaced %s)" % res["unplaced"] if res["unplaced"] else "", res["signs"] or 0,
                                  res["sign_ops"], "skipped" if res["soak"] is None else ("still" if not moved else "MOVED %s" % moved),
                                  len(res["notes"]), os.path.relpath(MAP_R_PLACED, REPO)))
        bad = not v.get("ok") or res["c11"] < 8 or (res["signs"] or 0) != res["sign_ops"] or moved
        if a.save:
            name = RM.free_save_name(a.name or SAVE_RIVER, RM.saves_stat())
            r = RM.save_keeper(B, name, signs=r_labels(*load_map_r()[1:]))
            print("save %s: ok=%s" % (name, r["ok"]))
            bad = bad or not r["ok"]
        return 1 if bad else 0
    doc, c1, plan = load_map_r()
    if not use_map(B, "R"):
        return 1
    if a.labels:
        B.call("jawa/review_label", action="clear", tag=TAG)
        r = B.call("jawa/review_label", action="add", ops=r_labels(c1, plan), tag=TAG) or {}
        print("map R labels: %s" % {k: r.get(k) for k in ("success", "added", "count")})
    if a.goto:
        w_ = a.goto.upper()
        if w_ == "C1" and c1:
            x, z, ww, hh = c1["rect"]
            r = B.call("rimworld/frame_cell_rect", x=x - 2, z=z - 2, width=ww + 4, height=hh + 6, paddingCells=2)
        elif w_ == "C11" and plan:
            r = RV.goto(B, plan, "R1")
        elif w_.startswith("R") and w_[1:].isdigit() and 1 <= int(w_[1:]) <= len(plan):
            r = RV.goto(B, plan, w_)
        else:
            raise SystemExit("--river --goto %s: unknown; valid: C1, C11, R1..R%d" % (a.goto, len(plan)))
        print("framed map R %s: %s" % (w_, (r or {}).get("success")))
    return 0


# ------------------------------------------------------------------------------------------------ key sheet
def pieces_summary(sc):
    return Counter(pc["status"] for pc in sc["pieces"])


def keysheet(placed, live=None, save=None, mock=None):
    os.makedirs(OUT, exist_ok=True)
    E = html.escape
    md = ["# FlowWorks composite review scenarios - key sheet", "",
          "Load **%s** (map C) and **%s** (map R: C1, C11). Paused at 10:00, god mode on, clear weather, Peaceful, Mod "
          "Settings at shipped defaults. **Every plot is still until your first poke: its START.** Reload the save to "
          "reset. Raids live in **%s**, rain in **%s** (load the branch, never the main save, for those pokes)."
          % (save or SAVE_MAIN + " (not saved yet)", SAVE_RIVER + " (not saved yet)", BRANCH_SAVE["raid"],
             BRANCH_SAVE["rain"]), "",
          "Each scenario has a gold title label (number, name, START, what to look for), its try lines under the plot, "
          "small rust labels on every part a poke touches, violet **DEFERRED** labels on every piece not built yet, "
          "and in-save sign books (a Novel; mouse over it, press i) at its north-west corner and at each DEFERRED piece "
          "- the books survive a plain load with no agent.", "",
          "Tonight's rulings carried: " + "; ".join(C.RULINGS.values()) + ".", "",
          "| # | scenario | map | plot (x,z,w,h) | look | staged / DEFERRED | goto |", "|---|---|---|---|---|---|---|"]
    rect = {p["sc"]["id"]: p["rect"] for p in placed}
    for sc in SC.ALL:
        n = pieces_summary(sc)
        md.append("| %s | %s | %s | %s | %s | %d / %d | `--goto %s`%s |" % (
            sc["id"], sc["name"], sc["map"], rect.get(sc["id"], "river-anchored (live)"), sc["look_style"],
            n["staged"], n["DEFERRED"], sc["id"], " (map R: framed by `--river --build`; goto on map R owed)" if sc["map"] == "R" else ""))
    md += ["", "Specials: **S0** status board %s, **F** free area %s, **Z0** Stage 0 swim site %s." % (
        BOARD["rect"], FREE["rect"], STAGE0["rect"]), ""]
    if mock:
        md += ["## Offline verification (MOCK - no game)", "", mock, ""]
    if live:
        md += ["## Live build", "", "```", json.dumps(live, indent=1, default=str)[:6000], "```", ""]
    for sc in SC.ALL:
        md += ["## %s - %s (%s, look %s)" % (sc["id"], sc["name"], "map " + sc["map"], sc["look_style"]), "",
               sc["purpose"], "", "**START:** %s" % sc["start"], "", "**Try:**", ""]
        md += ["%d. %s" % (i, t) for i, t in enumerate(sc["try_"], 1)]
        md += ["", "**Look for:** %s" % sc["look_for"], "", "**Broken looks like:** %s" % sc["broken"], "",
               "**Still until poked:** %s" % sc["idle"], ""]
        if sc["branch"]:
            md += ["**Branch saves:** %s" % "; ".join(sc["branch"].values()), ""]
        md += ["| piece | status | tag | note |", "|---|---|---|---|"]
        for pc in sc["pieces"]:
            note = pc.get("note", "") if pc["status"] == "staged" else "%s - builds under `%s`" % (pc["why"], pc["item"])
            md.append("| %s | %s | %s | %s |" % (pc["name"], pc["status"], pc["tag"], note.replace("|", "/")))
        tags = Counter(sc["exercises"].values())
        md += ["", "Exercises (%d ids): %s." % (len(sc["exercises"]), ", ".join("%d %s" % (n, t) for t, n in tags.items())),
               ""]
        if sc["goal"]:
            md += ["Goal read: %s" % sc["goal"], ""]
        if sc["owed_cs"]:
            md += ["Owed C#: %s" % "; ".join(sc["owed_cs"]), ""]
        if sc.get("prove_first"):
            md += ["**Prove first:** `%s` (Stage 0, live owed)." % sc["prove_first"], ""]
    md += ["## Stage 0 - swim out of a flooded sheer pit (C3's bet)", "", S0SWIM.__doc__.strip().split("\n\n")[0], ""]
    text = "\n".join(md) + "\n"
    with open(os.path.join(OUT, "KEYSHEET.md"), "w", encoding="utf-8") as f:
        f.write(text)
    body = []
    for ln in md:
        if ln.startswith("# "):
            body.append("<h1>%s</h1>" % E(ln[2:]))
        elif ln.startswith("## "):
            body.append("<h2>%s</h2>" % E(ln[3:]))
        elif ln.startswith("|---"):
            continue
        elif ln.startswith("| "):
            cells = [E(c.strip()) for c in ln.strip("|").split("|")]
            body.append("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in cells))
        elif ln[:2].rstrip(".").isdigit() or (ln[:3].rstrip(". ").isdigit() and ". " in ln[:4]):
            body.append("<p class=t>%s</p>" % E(ln))
        elif ln.strip():
            body.append("<p>%s</p>" % E(ln).replace("**", ""))
    out, intable = [], False
    for b in body:
        if b.startswith("<tr>") and not intable:
            out.append("<table>")
            intable = True
        if not b.startswith("<tr>") and intable:
            out.append("</table>")
            intable = False
        out.append(b)
    if intable:
        out.append("</table>")
    page = ("<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>Composite Scenarios Key</title><style>:root{--bg:#2b2118;--fg:#f2e6cf;--ac:#ffd27f;--li:#5a4636}"
            "@media (prefers-color-scheme: light){:root:not([data-theme=dark]){--bg:#f6efe3;--fg:#2b2118;--ac:#8a5a10;--li:#c9b79c}}"
            "body{background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif;margin:0 auto;max-width:1100px;"
            "padding:16px}h1,h2{color:var(--ac)}table{border-collapse:collapse;width:100%;margin:8px 0}"
            "td{border:1px solid var(--li);padding:3px 6px;vertical-align:top}p.t{margin:2px 0 2px 16px}</style></head>"
            "<body>" + "\n".join(out) + "</body></html>")
    with open(os.path.join(OUT, "keysheet.html"), "w", encoding="utf-8") as f:
        f.write(page)
    return os.path.join(OUT, "KEYSHEET.md")


# ------------------------------------------------------------------------------------------------ offline runs
def offline_build(mock_defs, placed, soak=True):
    """Build map C on a MockBridge; -> (result, bridge). mock_defs: a def set (refuse unknown) or None (accept all)."""
    B = MockBridge(defs=mock_defs)
    res = run_build(B, placed, soak=soak)
    return res, B


def offline_river(mock_defs):
    B = MockBridge(defs=mock_defs, terrain=synthetic_river())
    return run_river(B, synthetic_river(), (MAP_SIZE, MAP_SIZE)), B


def mock_summary(res, river):
    ok = sum(1 for v in res["verify"].values() if v["ok"])
    lines = ["MOCK map C: %d of %d scenarios verified as staged (dug depths, fills, buildings, pawn kinds); %d labels; "
             "%d of %d sign books; soak %s" % (ok, len(res["verify"]), res["labels"], res["signs"] or 0, res["sign_ops"],
                                               "trivially still (a mock never moves)" if res["soak"] else "skipped")]
    for sid, v in sorted(res["verify"].items(), key=lambda kv: SC.BY_ID[kv[0]]["n"]):
        lines.append("MOCK %-4s %s dug %d/%d%s%s%s" % (sid, "OK  " if v["ok"] else "FAIL", v["dug"], v["want_dug"],
                                                      " missing %s" % v["missing"] if v["missing"] else "",
                                                      " pawns short %s" % v["pawns_short"] if v["pawns_short"] else "",
                                                      " bad %s" % v["first_bad"] if v["first_bad"] else ""))
    if river:
        rv = river["verify"].get("C1", {})
        lines.append("MOCK map R (synthetic river): C1 at %s %s; C11 %d of 8 stations placed%s; %d sign books" % (
            river["c1"], "OK" if rv.get("ok") else "FAIL %s" % rv, river["c11"],
            " (unplaced %s)" % river["unplaced"] if river["unplaced"] else "", river["signs"] or 0))
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for f in ("plan", "dry-run", "mock", "build", "fresh-map", "soak", "labels", "save", "stage0", "river", "no-soak"):
        ap.add_argument("--" + f, action="store_true")
    ap.add_argument("--only", default=None, help="comma list of scenario ids (map C)")
    ap.add_argument("--goto", default=None)
    ap.add_argument("--branch", choices=sorted(BRANCH_SAVE), default=None)
    ap.add_argument("--name", default=None)
    ap.add_argument("--log", default=os.path.join(REPO, "Transient", "fw_scenarios_build_log.md"))
    a = ap.parse_args(argv)
    only = set(a.only.upper().split(",")) if a.only else None
    placed = placed_c(only)
    offline = a.plan or a.dry_run or (a.mock and not a.stage0)
    if offline:
        names, cnt = C.def_index()
        facts = C.def_facts()
        probs = layout_check(placed, facts, names)
        c1, plan, unplaced, notes = placed_r(synthetic_river(), (MAP_SIZE, MAP_SIZE))
        probs += scenario_check(c1, facts, names) if c1 else ["C1: no anchor on the synthetic river"]
        if probs:
            print("LAYOUT/DATA PROBLEMS (%d):\n  %s" % (len(probs), "\n  ".join(probs[:80])))
            return 2
        print("plan ok: %d map-C plots + C1/C11 on map R; defs resolved against %d src + %d game Defs files" % (
            len(placed), cnt["src"], cnt["game"]))
        mock_txt = None
        if a.dry_run or a.mock:
            res, B = offline_build(names | C.RUNTIME_GENERATED if a.mock else None, placed)
            river, BR = offline_river(names | C.RUNTIME_GENERATED if a.mock else None)
            if a.dry_run:
                path = os.path.join(REPO, "Transient", "fw_scenarios_dryrun.txt")
                with open(path, "w", encoding="utf-8") as f:
                    for tool, kw in B.calls + [("--- map R ---", {})] + BR.calls:
                        f.write("%s %s\n" % (tool, json.dumps(kw, default=str)[:400]))
                print("DRY RUN (MOCK, no game): %d bridge calls map C, %d map R -> %s" % (len(B.calls), len(BR.calls), path))
                for k, v in Counter(t for t, _ in B.calls).most_common(8):
                    print("  %5d %s" % (v, k))
            lines = mock_summary(res, river)
            print("\n".join(lines))
            if res["notes"] or river["notes"]:
                print("MOCK notes (%d): %s" % (len(res["notes"]) + len(river["notes"]),
                                              "; ".join((res["notes"] + river["notes"])[:12])))
            mock_txt = "\n".join("- " + ln for ln in lines)
            bad = [s for s, v in res["verify"].items() if not v["ok"]] + ([] if river["verify"].get("C1", {}).get("ok") else ["C1"])
            harm = [n for n in res["notes"] + river["notes"] if "not loaded on this mod list" not in n]
            if a.mock and (bad or harm or river["unplaced"]):
                keysheet(placed, mock=mock_txt)
                return 1
        print("key sheet -> %s" % keysheet(placed, mock=mock_txt))
        if not a.stage0:
            return 0
    if a.stage0:
        if a.mock:
            out = {}
            for label, rule in (("swims out at 2 m", lambda f: f >= 4), ("only at the brim", lambda f: f >= 8),
                                ("never", None)):
                B = MockBridge(swim_rule=rule)
                out[label] = S0SWIM.run(B, STAGE0["rect"][:2])[0]
            print("MOCK Stage 0 harness (simulated pawn, NOT the game): %s" % out)
            print("Stage 0 swim-out: LIVE RUN OWED (needs the bridge)")
            return 0 if out == {"swims out at 2 m": "PASS", "only at the brim": "PASS_AT_BRIM", "never": "FAIL"} else 1
        from modcheck import reviewmap as RM
        B = RM.LiveBridge()
        if a.fresh_map:
            R0 = review_class()(B, None)
            R0.fresh_map()
            R0.calm_at()
        verdict, rows = S0SWIM.run(B, STAGE0["rect"][:2])
        path = os.path.join(REPO, "Transient", "scenarios_stage0_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dict(verdict=verdict, rows=rows), f, indent=1, default=str)
        print("Stage 0 swim-out (LIVE): %s -> %s" % (verdict, path))
        return 0 if verdict in ("PASS", "PASS_AT_BRIM") else 1
    # ---------------------------------------------------------------- live
    from modcheck import reviewmap as RM
    B = RM.LiveBridge()
    if a.river:
        return river_main(B, a)
    if a.build and a.fresh_map and os.path.exists(MAP_R_PLACED):
        os.remove(MAP_R_PLACED)                       # a fresh game: the recorded map ids name nothing any more
    if not a.build and not use_map(B, "C"):
        return 1
    if a.build:
        res = run_build(B, placed, a.log, fresh=a.fresh_map, soak=not a.no_soak, only=only)
        with open(os.path.join(REPO, "Transient", "fw_scenarios_verify.json"), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        bad = [s for s, v in res["verify"].items() if not v["ok"]]
        moved = [s for s, v in (res["soak"] or {}).items() if not v["still"]]
        print("LIVE build: %d/%d scenarios as staged%s; soak: %s; %d notes; %ss" % (
            len(placed) - len(bad), len(placed), " (FAIL %s)" % bad if bad else "",
            "skipped" if res["soak"] is None else ("all still" if not moved else "MOVED %s" % moved), len(res["notes"]),
            res["wall_s"]))
        keysheet(placed, live=res)
        if not a.save:
            return 0 if not (bad or moved) else 1
    R = review_class()(B, None)
    if a.soak and not a.build:
        print(json.dumps(R.soak(placed), default=str)[:3000])
    if a.branch:
        if a.branch == "raid":
            for p in placed:
                if p["sc"]["setup"].get("pens"):
                    R.pawns(p, key="pens", ops_key="pen_ops")
        elif a.branch == "rain":
            R.call("jawa/weather_set", weather="Rain", lockWeather=True)
        name = RM.free_save_name(a.name or BRANCH_SAVE[a.branch], RM.saves_stat())
        r = RM.save_keeper(B, name, signs=label_ops(placed))
        print("branch %s save %s: ok=%s; notes %s" % (a.branch, name, r["ok"], R.notes[:5]))
        return 0 if r["ok"] else 1
    if a.save:
        R.sweep(R.keep_rects(placed))
        R.pin_clock()                                 # the soak ran the clock 2 h: on to the next 10:00 (no sim)
        R.call("rimworld/pause_game", pause=True)
        B.call("jawa/clear_ui", all=True)
        name = RM.free_save_name(a.name or SAVE_MAIN, RM.saves_stat())
        r = RM.save_keeper(B, name, signs=label_ops(placed))
        print("save %s: ok=%s new=%s changed=%s gone=%s signs=%s" % (name, r["ok"], r["new"], r["changed"], r["gone"],
                                                                     r.get("signs")))
        if r["ok"]:
            keysheet(placed, save=name)
        return 0 if r["ok"] else 1
    if a.labels:
        print("labels: %s" % {k: R.place_labels(placed).get(k) for k in ("added", "count")})
    if a.goto:
        R.sweep(R.keep_rects(placed))
        print("framed %s: %s" % (a.goto, R.goto_(placed, a.goto).get("success")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
