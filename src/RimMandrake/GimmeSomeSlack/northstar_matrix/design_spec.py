#!/usr/bin/env python3
"""The phase-2 design's screenshot matrix (design/RimMandrake/messy_conduit_phase2_design_2026-10-02.md section 4)
in its own scene-spec JSON format (section 4.3, spec_version 1), with expect.intrinsic filled by oracle.py.

    python3 design_spec.py                  # counts + the design's pair-coverage claims re-proved per group
    python3 design_spec.py --out scenes.json

Groups (section 4.2): floor 64 (T16 x S4, F/P/V/Z by the design's formulas), density 16 ({1,10,100,1000} x S4),
aerial 18, hose 9 (L9), controls 2 = 109. Refuses to write if any group's pair coverage has a gap.

Mapping of the design's T levels onto scenes.py topologies, and where they could not be met as written:
  T4  "lattice/mesh (5x5 grid)"   -> lattice5. A spacing-2 5x5 grid is ONE dense field to the reducer (every hole
                                     has 8 conduit neighbours), so it reads as a tangle either way; `mesh` (spacing 3,
                                     9 junctions) is in the pairwise matrix instead.
  T7  "gap, live side"            -> gap (P decides whether the source side is live)
  T8  "gap, both dead"            -> gap with the feeder ALSO broken: nothing past the first break is fed
  T14 "under an impassable building (device stub)" -> under_building, which has NO device stub: every powered building
                                     checked (Battery, WoodFiredGenerator, SolarGenerator, ElectricSmelter, Heater) is
                                     PassThroughOnly, so the C# adapter never buries conduit under it. NEEDED: a powered
                                     building with passability Impassable, or drop the device-stub expectation.
  S0  tidy: "slack 0, 1 cord, tangles off"   -> tangles OFF changes the graph (oracle tangle_min = huge)
  S3  "lattice tangle (tangle threshold 6)"  -> oracle tangle_min = 6. NEEDED SETTING: GimmeSomeSlackSettings has no
                                     tangleMin field today (CordGraph.TangleMin is a constant), so `set:tangleMin=6`
                                     will answer "no settings field" until 1b adds it.
"""
import argparse
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE in sys.path:
    sys.path.remove(HERE)
sys.path.insert(0, HERE)   # front always: Utils/scenes (a package) must not shadow this directory's scenes.py
_m = sys.modules.get("scenes")
if _m is not None and os.path.dirname(os.path.abspath(getattr(_m, "__file__", "") or "")) != HERE:
    del sys.modules["scenes"]
import matrix as MX  # noqa: E402
import oracle as O  # noqa: E402
import scenes as S  # noqa: E402

T_LEVELS = ["line", "tee", "cross4", "ring", "lattice5", "star", "spur_blob", "gap", "gap_dead", "multinet",
            "device_attached", "doorway", "wall_entry", "rock_entry", "under_building", "canal"]
S_LEVELS = ["tidy", "ropey", "ratsnest", "lattice_tangle"]
F_LEVELS = ["StarWarsJawa", "StarWars", "ExtensionCord", "Cybertek"]
P_LEVELS = ["live", "dead"]
V_LEVELS = ["normal", "overlay", "selected"]
Z_LEVELS = ["close", "far"]
STAGE = {
    "tidy": {"settings": {"slack": "0", "cordsPerConnection": "1", "tangles": "False"}, "tangle_min": 10 ** 9, "cmax": 1},
    "ropey": {"settings": {"slack": "1", "cordsPerConnection": "3", "tangles": "True"}, "tangle_min": None, "cmax": 3},
    "ratsnest": {"settings": {"slack": "1.8", "sprawlCap": "40", "cordsPerConnection": "3", "tangles": "True"},
                 "tangle_min": None, "cmax": 3},
    "lattice_tangle": {"settings": {"slack": "1", "cordsPerConnection": "3", "tangles": "True", "tangleMin": "6"},
                       "tangle_min": 6, "cmax": 3, "needs": "tangleMin setting (not in GimmeSomeSlackSettings today)"},
}
ZOOM_ROOT = {"close": 11, "far": 30}
BOARD_PITCH = [40, 30]
DENSITY_SIDE = {1: 1, 10: 4, 100: 12, 1000: 34}


# ----------------------------------------------------------------------------- rows (section 4.2 formulas)
def floor_rows():
    out = []
    for t in range(16):
        for s in range(4):
            out.append({"T": T_LEVELS[t], "S": S_LEVELS[s], "F": F_LEVELS[(t + s) % 4], "P": P_LEVELS[(s + t // 4) % 2],
                        "V": V_LEVELS[(t + s + t // 4) % 3], "Z": Z_LEVELS[(s // 2 + t) % 2]})
    return out


def aerial_rows():
    out = []
    for i in range(18):
        P, N, R = i // 9, (i % 9) // 3, i % 3
        out.append({"P": P_LEVELS[P], "N": [2, 3, 5][N], "R": [6, 12, 19][R], "St": ["up", "cut", "fallen"][(N + R + P) % 3],
                    "G": ["open", "room", "water"][(N + 2 * R) % 3]})
    return out


def hose_rows():
    out = []
    for x in range(3):
        for y in range(3):
            out.append({"St": ["Flat", "Plump", "Filling50"][x], "Ro": ["straight", "corner", "water"][y],
                        "Le": [6, 14, 24][(x + y) % 3], "Fl": ["water", "tar", "chemfuel"][(x + 2 * y) % 3]})
    return out


GROUP_AXES = {
    "floor": [("T", T_LEVELS), ("S", S_LEVELS), ("F", F_LEVELS), ("P", P_LEVELS), ("V", V_LEVELS), ("Z", Z_LEVELS)],
    "aerial": [("P", P_LEVELS), ("N", [2, 3, 5]), ("R", [6, 12, 19]), ("St", ["up", "cut", "fallen"]),
               ("G", ["open", "room", "water"])],
    "hose": [("St", ["Flat", "Plump", "Filling50"]), ("Ro", ["straight", "corner", "water"]), ("Le", [6, 14, 24]),
             ("Fl", ["water", "tar", "chemfuel"])],
}


# ----------------------------------------------------------------------------- scene -> section 4.3 build ops
def _gc(sc, p):
    return [p[0], sc["h"] - 1 - p[1]]


def build_ops(sc, pct=None):
    ops = [{"op": "terrain", "def": "Soil", "rect": [0, 0, sc["w"], sc["h"]]}]
    if sc["water"]:
        ops.append({"op": "terrain", "def": "WaterDeep", "cells": [_gc(sc, p) for p in sc["water"]]})
    if sc["rock"]:
        ops.append({"op": "build", "def": "Granite", "cells": [_gc(sc, p) for p in sc["rock"]]})
    if sc["walls"]:
        ops.append({"op": "build", "def": "Wall", "stuff": "Steel", "cells": [_gc(sc, p) for p in sc["walls"]]})
    if sc["doors"]:
        ops.append({"op": "build", "def": "Door", "stuff": "Steel", "cells": [_gc(sc, p) for p in sc["doors"]]})
    wset = {tuple(p) for p in sc["water"]}
    dry = [_gc(sc, p) for p in sc["conduit"] if tuple(p) not in wset]
    wet = [_gc(sc, p) for p in sc["conduit"] if tuple(p) in wset]
    if dry:
        ops.append({"op": "build", "def": "PowerConduit", "cells": dry})
    if wet:
        ops.append({"op": "build", "def": "WaterproofConduit", "cells": wet})
    devs = sorted(sc["devices"], key=lambda d: (not S.DEVICE_DEFS[d["role"]]["transmitter"], d["id"]))
    for d in devs:
        r = S.DEVICE_DEFS[d["role"]]
        op = {"op": "build", "def": r["def"], "cells": [_gc(sc, S.game_position(d))], "id": d["id"]}
        if d["role"] in ("battery", "bench"):
            op["rot"] = 0
        ops.append(op)
        if d["role"] == "battery":
            ops.append({"op": "battery", "at": _gc(sc, S.game_position(d)),
                        "pct": 1.0 if d.get("charged") else 0.0})
    if sc["trees"]:
        ops.append({"op": "plant", "def": "Plant_TreeOak", "cells": [_gc(sc, p) for p in sc["trees"]], "growth": 1.0})
    return ops


def intrinsic(sc, stage, view, with_aerial=False):
    st = STAGE[stage]
    e = O.expect(sc, "ropey", with_aerial, tangle_min=st["tangle_min"])
    stubs = sum(v for k, v in e["node_types"].items() if k.startswith("stub_"))
    out = {"junctions": e["node_types"].get("junction", 0), "terminals": len(e["terminals"]),
           "terminals_live": sum(1 for t in e["terminals"] if t[2]), "stubs": stubs, "tangles": e["tangles"],
           "cord_edges": e["cord_edges"], "cords_min": e["cord_edges"],
           "cords_max": st["cmax"] * e["cord_edges"] + O.TANGLE_STRAND_ALLOWANCE * e["tangles"],
           "nets": O.nets(sc, with_aerial), "cross_net_edges": 0, "unwalkable_vertices": 0,
           "wall_terminals": len(e["wall_terminals"]), "node_types": e["node_types_live"]}
    if view == "selected":
        out["highlight_cords_eq_net_cords"] = True
    return out


def _plot(sc):
    return [0, 0, sc["w"], sc["h"]]


def floor_scene(r, k):
    t = r["T"]
    sc = S.compose("gap" if t == "gap_dead" else t, 5, "live_gap" if t == "gap_dead" else "none", name="F%02d" % k)
    for d in sc["devices"]:
        if d["id"] == "src":
            d["charged"] = r["P"] == "live"
    return sc


def floor_spec(r, k):
    sc = floor_scene(r, k)
    st = STAGE[r["S"]]
    settings = dict(st["settings"], style="CordStyle." + r["F"])
    sid = "F%02d_T%d_S%d" % (k, T_LEVELS.index(r["T"]), S_LEVELS.index(r["S"]))
    sel = None
    if r["V"] == "selected":
        sel = _gc(sc, sc["conduit"][len(sc["conduit"]) // 2])
    spec = {"id": sid, "group": "floor", "factors": r, "plot": _plot(sc), "zoom_root": ZOOM_ROOT[r["Z"]],
            "settings": settings, "build": build_ops(sc), "view": {"overlay": "power" if r["V"] == "overlay" else "none",
                                                                  "select_at": sel},
            "expect": {"intrinsic": intrinsic(sc, r["S"], r["V"]), "parity": "core"},
            "shows": ["cords_loopy_slack", "tangle_stages_distinct"]}
    notes = []
    if st.get("needs"):
        notes.append("NEEDED: " + st["needs"])
    if r["T"] == "under_building":
        notes.append("design asks for a DEVICE stub; no impassable powered building found (all PassThroughOnly)")
    if r["V"] == "selected":
        notes.append("selection highlight is phase 1b (UNBUILT)")
    if r["F"] != "StarWarsJawa":
        notes.append("art pending: only the Jawa family has real art")
    spec["notes"] = notes
    t = r["T"]
    if t in ("gap", "gap_dead"):
        spec["shows"].append("break_live_vs_dead")
    if t in ("wall_entry", "rock_entry", "under_building", "canal"):
        spec["shows"].append("cord_enters_wall_or_rock")
    if t in ("tee", "cross4", "star", "mesh", "ring"):
        spec["shows"].append("junction_reads_as_join")
    return spec, sc


def density_spec(n, stage, k):
    sc = S.field_scene(n, seed=1, name="D%02d" % k)
    side = DENSITY_SIDE[n]
    sc = _resize_field(sc, n, side, 0)        # seeded by n only: the 4 stages tangle the SAME field
    return {"id": "D%02d_n%d_S%d" % (k, n, S_LEVELS.index(stage)), "group": "density",
            "factors": {"n": n, "S": stage, "F": "StarWarsJawa", "P": "live", "V": "normal", "Z": "far" if n >= 1000 else "close"},
            "plot": _plot(sc), "zoom_root": ZOOM_ROOT["far" if n >= 1000 else "close"],
            "settings": dict(STAGE[stage]["settings"], style="CordStyle.StarWarsJawa"), "build": build_ops(sc),
            "view": {"overlay": "none", "select_at": None},
            "expect": {"intrinsic": intrinsic(sc, stage, "normal"), "parity": "core", "perf": ["rebuildMs", "laidPoints"]},
            "shows": ["tangle_stages_distinct"], "notes": []}, sc


def _resize_field(sc, n, side, k):
    """field_scene sized to the design's plot side (1, 4, 12, 34)."""
    import random
    rng = random.Random(1000 * n + k)
    X0, Y0 = 3, 3
    ey = Y0 + side // 2
    cells = [(2, ey)]
    while len(cells) < n:
        if rng.random() < 0.6:
            bx, by = X0 + rng.randrange(side), Y0 + rng.randrange(side)
            add = [(bx + a, by + b) for a in range(3) for b in range(3)]
        else:
            bx, by = X0 + rng.randrange(side), Y0 + rng.randrange(side)
            L = rng.randint(3, 8)
            add = [(bx + i, by) for i in range(L)] if rng.random() < 0.5 else [(bx, by + i) for i in range(L)]
        for p in add:
            if X0 <= p[0] < X0 + side and Y0 <= p[1] < Y0 + side and p not in cells and len(cells) < n:
                cells.append(p)
        if side * side + 1 <= len(cells):
            break
    sc = dict(sc, w=X0 + side + 4, h=Y0 + side + 4, conduit=[list(p) for p in sorted(cells)])
    sc["devices"] = [dict(sc["devices"][0], x=1, y=ey - 1)]
    sc["params"] = {"density_target": n, "side": side, "actual": len(cells)}
    return sc


def aerial_scene(r, k):
    N, R = r["N"], r["R"]
    a = 4
    poles = [5 + i * R for i in range(N)]
    xp = poles[-1]
    W, H = xp + 8, 9
    sc = {"format": "mc_scene/1", "name": "A%02d" % k, "topology": "aerial", "w": W, "h": H,
          "conduit": [[3, a], [4, a], [xp + 1, a], [xp + 2, a]], "walls": [], "doors": [], "rock": [], "water": [],
          "trees": [], "devices": [
              {"id": "src", "role": "battery", "x": 2, "y": a - 1, "w": 1, "h": 2, "hookup": None,
               "charged": r["P"] == "live"},
              {"id": "h_air", "role": "consumer", "x": xp + 3, "y": a, "w": 1, "h": 1, "hookup": [xp + 2, a]}],
          "aerial": {"poles": [[x, a] for x in poles], "spans": [[i, i + 1] for i in range(N - 1)], "cut": [], "killed": []},
          "hose": None, "break_cell": None, "intended_dense": False, "notes": []}
    mid = (N - 1) // 2
    if r["St"] == "cut":
        sc["aerial"]["cut"] = [mid]
    elif r["St"] == "fallen":
        sc["aerial"]["killed"] = [N - 1 if N == 2 else mid + 1 if N > 3 else 1]
    if r["G"] == "room":
        x0, x1 = poles[0] + 2, poles[1] - 2
        if x1 - x0 >= 2:
            sc["walls"] = [[x, y] for x in range(x0, x1 + 1) for y in (1, 7)] + \
                          [[x, y] for x in (x0, x1) for y in range(2, 7)]
    elif r["G"] == "water":
        sc["water"] = [[x, y] for x in range(poles[0] + 2, poles[1] - 1) for y in range(0, H)]
    S._canon(sc)
    return sc


def aerial_spec(r, k):
    sc = aerial_scene(r, k)
    a = sc["aerial"]
    killed = set(a["killed"])
    fallen = [s for s in range(len(a["spans"])) if set(a["spans"][s]) & killed]
    live, dl = O.liveness(sc, with_aerial=True)
    exp = intrinsic(sc, "ropey", "normal", with_aerial=True)
    exp.update({"spans_up": len(a["spans"]) - len(a["cut"]) - len(fallen), "spans_cut": len(a["cut"]),
                "spans_fallen": len(fallen), "net_repairs": 0, "far_consumer_live": dl.get("h_air"),
                "pole_live": [dl.get("pole%d" % i) for i in range(len(a["poles"]))],
                # design 2.6: a cut span hangs as two downed wires; a fallen span lies on the floor from the
                # surviving anchor with a free terminal end (live -> whip/sparks, dead -> limp)
                "downed_ends": [{"pole": p, "live": dl.get("pole%d" % p)} for s in a["cut"] for p in a["spans"][s]],
                "fallen_ends": [{"pole": p, "live": dl.get("pole%d" % p)} for s in fallen for p in a["spans"][s]
                                if p not in killed]})
    ops = build_ops(sc)
    ops.append({"op": "anchor", "def": "RM_AerialMast", "cells": [_gc(sc, p) for p in a["poles"]], "unbuilt": True})
    ops.append({"op": "link", "pairs": [[_gc(sc, a["poles"][i]), _gc(sc, a["poles"][j])] for i, j in a["spans"]],
                "unbuilt": True})
    for s in a["cut"]:
        i, j = a["spans"][s]
        mx = [(a["poles"][i][0] + a["poles"][j][0]) // 2, a["poles"][i][1]]
        ops.append({"op": "explode", "at": _gc(sc, mx), "radius": 2.9, "unbuilt": True})
    for p in sorted(killed):
        ops.append({"op": "kill", "at": _gc(sc, a["poles"][p]), "unbuilt": True})
    return {"id": "A%02d_N%d_R%d_%s" % (k, r["N"], r["R"], r["St"]), "group": "aerial", "factors": r,
            "plot": _plot(sc), "zoom_root": ZOOM_ROOT["close"] if r["R"] < 19 else ZOOM_ROOT["far"],
            "settings": dict(STAGE["ropey"]["settings"], style="CordStyle.StarWarsJawa"), "build": ops,
            "view": {"overlay": "none", "select_at": None},
            "expect": {"intrinsic": exp, "parity": "core"},
            "shows": ["aerial_span_reads_overhead"] + (["aerial_fallen_span_on_ground"] if fallen else []),
            "notes": ["RM_AerialMast/CompAerialAnchor UNBUILT: anchor/link/explode/kill ops have nothing to call yet; "
                      "the floor part (battery, stubs, heater) is built and checked today"]}, sc


def hose_max_length(L):
    """PROVISIONAL (GIMMESOMESLACK_HOSE_BEND_TRACE_1): the nozzle faces west and every scene's end lies east, so the laid hose
    is the straight lead-out + a full-radius U-turn + the run; offline that needs about L+10 cells (L6 16, L14 23, L24 33). The old
    ceil(L*1.3) left L6/L14 refused ('route too long') once lead-out landed, and before it read as the 0.19-cell U-turn."""
    return int(math.ceil(L * 1.3)) + 14


def hose_spec(r, k):
    L = r["Le"]
    W, H = L + 8, 9 if r["Ro"] != "corner" else L // 2 + 9
    a = [2, 4]
    if r["Ro"] == "corner":
        b = [2 + L // 2, 4 + L - L // 2]
        walls = [[x, 5] for x in range(1, 2 + L // 2)]
    else:
        b = [2 + L, 4]
        walls = []
    water = [[x, y] for x in range(2 + L // 2 - 1, 2 + L // 2 + 1) for y in range(0, H)] if r["Ro"] == "water" else []
    # GIMMESOMESLACK_HOSE_BEND_TRACE_1 (live 2026-10-09): the nozzle faces WEST and its straight lead-out + U-turn ran past
    # the plot's west edge onto unprepared map ground (another plot's margin, marsh, rock), so H01/H02/H04/H05/H07 failed
    # "no room for the straight lead-out" on one fresh map and passed on another. A soil margin of M cells west of the scene.
    M = 6
    plot = [0, 0, W + M, H]

    def gc(p):
        return [p[0] + M, H - 1 - p[1]]
    ops = [{"op": "terrain", "def": "Soil", "rect": plot}]
    if water:
        ops.append({"op": "terrain", "def": "WaterShallow", "cells": [gc(p) for p in water]})
    if walls:
        ops.append({"op": "build", "def": "Wall", "stuff": "Steel", "cells": [gc(p) for p in walls]})
    # RM_HoseReel is 2x2: Position gc(a) is its SW game cell, so the footprint is design (a.x..a.x+1, a.y-1..a.y)
    foot = {(a[0] + i, a[1] - j) for i in (0, 1) for j in (0, 1)}
    assert not foot & {tuple(p) for p in walls + water}, "hose reel footprint overlaps a wall/water cell"
    assert tuple(b) not in foot, "hose free end inside the reel footprint"
    ops.append({"op": "debug_hose", "a": gc(a), "b": gc(b), "maxLength": hose_max_length(L),
                "fluid": {"water": "RM_Liquid_FreshWater", "tar": None, "chemfuel": None}[r["Fl"]], "fluid_key": r["Fl"],
                "force_state": "Filling" if r["St"] == "Filling50" else r["St"]})
    # HoseMath: VisibleWidth = FlatVisible 0.38 + PlumpExtra 0.085 * plumpAmount(1) * eased; Filling50 is read half way
    # through the transition (validation_hose.py H6: blend in (0.2, 0.8)), so its width lies strictly between the two.
    state = "Filling" if r["St"] == "Filling50" else r["St"]
    width = {"Flat": [0.375, 0.385], "Plump": [0.46, 0.47], "Filling": [0.381, 0.464]}[state]
    dist = math.hypot(b[0] - a[0], b[1] - a[1])
    return {"id": "H%02d_%s_%s_L%d" % (k, r["St"], r["Ro"], L), "group": "hose", "factors": r, "plot": plot,
            "zoom_root": ZOOM_ROOT["close"], "settings": {}, "build": ops, "view": {"overlay": "none", "select_at": None},
            "expect": {"intrinsic": {"state": state, "visible_width": width, "width_over_wire_ge": 4.0,
                                     "blend": {"Flat": [0, 0], "Plump": [1, 1], "Filling": [0.2, 0.8]}[state],
                                     "min_bend_radius_ge": 1.2, "couplings_min": 2,   # the two end fittings; joiners only at bends (owner review 2026-10-04 B17)
                                     "self_intersections": 0, "unwalkable_points": 0}, "parity": None},
            "shows": ["hose_thicker_than_wire"] + (["hose_flat_vs_plump"] if r["St"] in ("Flat", "Plump") else []),
            "notes": ["hose kit built; placed and read by run_live.py through HoseProbe (validation_hose.py call shapes)",
                      "tar/chemfuel LiquidDef names not authored yet: fluid None, fluid_key carries the intent; HoseProbe has no fluid input"]}


def control_specs():
    empty = {"id": "C00_empty", "group": "controls", "factors": {"kind": "empty"}, "plot": [0, 0, 12, 10],
             "zoom_root": ZOOM_ROOT["close"], "settings": {}, "build": [{"op": "terrain", "def": "Soil", "rect": [0, 0, 12, 10]}],
             "view": {"overlay": "none", "select_at": None},
             "expect": {"intrinsic": {"cord_edges": 0, "junctions": 0, "terminals": 0, "nets": 0,
                                      "image_wires": "none (the wire check must report no wires)"}, "parity": "core"},
             "shows": [], "notes": ["proves the image wire check can fail"]}
    sc = S.compose("line", 5, name="C01")
    off = {"id": "C01_line_master_off", "group": "controls", "factors": {"kind": "master_off"}, "plot": _plot(sc),
           "zoom_root": ZOOM_ROOT["close"], "settings": {"enabled": "False"}, "build": build_ops(sc),
           "view": {"overlay": "none", "select_at": None},
           "expect": {"intrinsic": {"layer_visible": False, "cords_drawn": 0, "vanilla_conduit_art": True}, "parity": None},
           "shows": [], "notes": ["the planted negative for the mask check: ON-census mask over this OFF frame must fail"]}
    return [empty, off]


def build_spec():
    groups = {"floor": floor_rows(), "aerial": aerial_rows(), "hose": hose_rows()}
    proofs = {}
    for g, rows in groups.items():
        n, missing = MX.prove(rows, GROUP_AXES[g])
        proofs[g] = {"rows": len(rows), "pairs": n, "missing": missing}
    scenes, oversize = [], []
    for k, r in enumerate(groups["floor"]):
        spec, sc = floor_spec(r, k)
        scenes.append(spec)
        if sc["w"] > BOARD_PITCH[0] or sc["h"] > BOARD_PITCH[1]:
            oversize.append((spec["id"], sc["w"], sc["h"]))
    k = 0
    for n in (1, 10, 100, 1000):
        for st in S_LEVELS:
            spec, sc = density_spec(n, st, k)
            scenes.append(spec)
            k += 1
    for k, r in enumerate(groups["aerial"]):
        scenes.append(aerial_spec(r, k)[0])
    for k, r in enumerate(groups["hose"]):
        scenes.append(hose_spec(r, k))
    scenes += control_specs()
    body = json.dumps(scenes, sort_keys=True, default=list)
    return {"spec_version": 1, "generator": "src/RimMandrake/GimmeSomeSlack/northstar_matrix/design_spec.py",
            "spec_hash": hashlib.sha256(body.encode()).hexdigest(), "board_pitch": BOARD_PITCH,
            "counts": {g: sum(1 for s in scenes if s["group"] == g) for g in ("floor", "density", "aerial", "hose", "controls")},
            "pair_proofs": proofs, "oversize_for_board": oversize, "scenes": scenes}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    spec = build_spec()
    gaps = {g: p["missing"] for g, p in spec["pair_proofs"].items() if p["missing"]}
    print("scenes: %d %s" % (len(spec["scenes"]), spec["counts"]))
    for g, p in spec["pair_proofs"].items():
        print("  %-7s %d rows, %d pairs required, %d missing" % (g, p["rows"], p["pairs"], len(p["missing"])))
    print("  oversize for the %dx%d board: %s" % (spec["board_pitch"][0], spec["board_pitch"][1], spec["oversize_for_board"]))
    print("  spec_hash %s" % spec["spec_hash"][:16])
    if gaps:
        print("REFUSED: pair coverage gap %s" % gaps)
        return 1
    if a.out:
        with open(a.out, "w") as f:
            json.dump(spec, f, indent=1, default=list)
        print("wrote %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
