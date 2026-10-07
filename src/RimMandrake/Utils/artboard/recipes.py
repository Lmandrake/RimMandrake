"""Board recipes for the live half: what to stage where, and what each crop must show.

A recipe is board-LOCAL (cells relative to an origin chosen at run time) and is turned into
  * stage ops for jawa/artboard_stage   (plan() -> ops lines, absolute cells)
  * the board JSON artboard.run reads    (board_json() once the capture returns its mapping)
so the grid key the owner walks in game IS the recipe.

Recipe JSON:
  name, note, ground (TerrainDef laid under the whole board), ppc, pad (ring, cells), margin (cells of plain
  ground around the capture), defaults (expect block merged under every subject), subjects:
  [{id, cell:[x,z], size:[w,h], overhang, expect, differs_from, question, label,
    stage:[{kind, dx, dz, w, h, ...tool keys...}]}]        dx/dz are relative to the subject's cell.

    python3 -m artboard.recipes write      regenerate the committed recipe JSON files (deterministic)
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RECIPE_DIR = os.path.join(HERE, "recipes")

FLUIDS = {"water": "RM_Fluid_Water", "tar": "RM_Fluid_Tar"}
FLUID_COLOUR = {"water": ["blue", "cyan", "grey"], "tar": ["black", "brown", "grey"]}
STAGE_KEYS = ("def", "depth", "fill", "fluid", "rot", "stuff", "growth", "faction")


def legal_states():
    """Every legal excavated (D, F): D 1..4, F 0..D -> 14 states."""
    return [(d, f) for d in range(1, 5) for f in range(0, d + 1)]


def flowworks_pit_states():
    """FlowWorks contact board: all 14 legal (D,F) states x {water, tar} as 3x3 plots, an undug plot, vanilla
    shallow/deep water references, and the lip-occlusion case (a pawn standing below the lip of a D2 and a D3
    pit, and one standing ON the near lip of a D3 pit)."""
    pitch, plot = 5, 3
    subs = []
    rows = {"water": 14, "tar": 8}
    for fl, z in rows.items():
        for i, (d, f) in enumerate(legal_states()):
            sid = "D%dF%d_%s" % (d, f, fl)
            diff = ["undug"]
            if f >= 1:
                diff.append("D%dF%d_%s" % (d, f - 1, fl))
                if fl == "tar":
                    diff.append("D%dF%d_water" % (d, f))
            elif d >= 2:
                diff.append("D%dF0_%s" % (d - 1, fl))
            exp = {"organic": False}
            if f > 0:
                exp["colour"] = FLUID_COLOUR[fl]
            op = {"kind": "pit", "dx": 0, "dz": 0, "w": plot, "h": plot, "depth": d, "fill": f}
            if f > 0:
                op["fluid"] = FLUIDS[fl]
            subs.append({
                "id": sid, "label": "D%d F%d %s" % (d, f, fl if f else "dry"),
                "cell": [i * pitch, z], "size": [plot, plot], "expect": exp, "differs_from": diff,
                "question": ("Is this a %dx%d excavation %d levels deep holding %s?" % (plot, plot, d,
                             "nothing (dry)" if f == 0 else "%d level%s of %s" % (f, "s" if f > 1 else "", fl))),
                "stage": [op]})
    refs = [
        {"id": "undug", "label": "undug soil", "expect": {"may_be_empty": True, "organic": False},
         "question": "Is this plain undug ground with no hole, lip or liquid?",
         "stage": [{"kind": "terrain", "dx": 0, "dz": 0, "w": plot, "h": plot, "def": "Soil"}]},
        {"id": "vanilla_shallow", "label": "vanilla shallow water", "differs_from": ["undug"],
         "expect": {"organic": False, "colour": ["blue", "cyan", "grey"]},
         "question": "Is this vanilla shallow water (reference for the water fills)?",
         "stage": [{"kind": "terrain", "dx": 0, "dz": 0, "w": plot, "h": plot, "def": "WaterShallow"}]},
        {"id": "vanilla_deep", "label": "vanilla deep water", "differs_from": ["vanilla_shallow"],
         "expect": {"organic": False, "colour": ["blue", "cyan", "grey"]},
         "question": "Is this vanilla deep water (reference for the deepest water fill)?",
         "stage": [{"kind": "terrain", "dx": 0, "dz": 0, "w": plot, "h": plot, "def": "WaterDeep"}]},
        {"id": "pawn_below_lip_D2", "label": "pawn in D2 pit", "differs_from": ["D2F0_water"],
         "overhang": 0.4, "expect": {"may_overflow": True, "organic": False},
         "question": "A person stands in the middle of this dry D2 pit: is the person drawn, with the near "
                     "(bottom) lip hiding the lower body rather than the person floating on top?",
         "stage": [{"kind": "pit", "dx": 0, "dz": 0, "w": plot, "h": plot, "depth": 2, "fill": 0},
                   {"kind": "pawn", "dx": 1, "dz": 1, "def": "Colonist", "rot": "south", "faction": "none"}]},
        {"id": "pawn_below_lip_D3", "label": "pawn in D3 pit", "differs_from": ["D3F0_water", "pawn_below_lip_D2"],
         "overhang": 0.4, "expect": {"may_overflow": True, "organic": False},
         "question": "A person stands in the middle of this dry D3 pit: is more of the body hidden by the near lip "
                     "than in the D2 pit, but the head still visible?",
         "stage": [{"kind": "pit", "dx": 0, "dz": 0, "w": plot, "h": plot, "depth": 3, "fill": 0},
                   {"kind": "pawn", "dx": 1, "dz": 1, "def": "Colonist", "rot": "south", "faction": "none"}]},
        {"id": "pawn_on_lip_D3", "label": "pawn on D3 lip", "size": [plot, plot + 2],
         "differs_from": ["pawn_below_lip_D3"], "overhang": 0.4, "expect": {"may_overflow": True, "organic": False},
         "question": "A person stands on the undug ground just below (south of) a dry D3 pit: is the whole body "
                     "drawn, standing in front of the pit's near lip and not clipped by it?",
         "stage": [{"kind": "pit", "dx": 0, "dz": 1, "w": plot, "h": plot, "depth": 3, "fill": 0},
                   {"kind": "pawn", "dx": 1, "dz": 0, "def": "Colonist", "rot": "south", "faction": "none"}]},
    ]
    for i, r in enumerate(refs):
        r.setdefault("size", [plot, plot])
        r["cell"] = [i * pitch, 0]
        subs.append(r)
    return {
        "name": "flowworks_pit_states",
        "note": "Every legal excavated (D,F) x {water, tar}, undug + vanilla water references, and the lip-occlusion "
                "case. Plots 3x3 at pitch 5 (rows 6 apart; the lip case is 3x5 so its pit stays centred) so each centre cell has same-state neighbours and its "
                "edges show the lip. F0 water and F0 tar are both dry and are expected to look the same.",
        "ground": "Soil", "ppc": 48, "pad": 1.0, "margin": 1, "overhang": 0.25,
        "subjects": subs,
    }


GSS_LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
GSS_OP_KEYS = ("end", "flow", "look", "cut", "n")


def gss_states():
    """Gimme Some Slack looks board (design/RimMandrake/gss_looks_prereview.md): cords in every state a player meets
    (powered run to a lamp, the same unpowered, a run ending in a wall, a T junction feeding two devices, a cut run
    with a live frayed end), hose reels in all four looks stored, hoses laid ahead of / behind the outlet (the
    behind case is the G2 tight-bend shape), flat vs flowing (plump), the three free ends, and overhead spans up,
    cut (fallen halves) and to a wall bracket. Things are vanilla/GSS defs spawned by jawa/artboard_stage; the GSS
    states (charge, lay, flow, end, look, link, cut, ticks) are gss_* ops applied after by jawa/gss_stage."""
    subs = []

    def cords(sid, label, col, row, stage, question, diff, colour=None):
        exp = {"organic": False, "may_overflow": True}
        if colour:
            exp["colour"] = colour
        subs.append({"id": sid, "label": label, "cell": [col * 9, row], "size": [7, 5], "overhang": 0.3,
                     "expect": exp, "differs_from": diff, "question": question, "stage": stage})

    run = [{"kind": "thing", "dx": x, "dz": 2, "def": "PowerConduit"} for x in range(0, 6)]
    bat = [{"kind": "thing", "dx": 0, "dz": 3, "def": "Battery", "rot": "north"}]
    lamp = [{"kind": "thing", "dx": 5, "dz": 0, "def": "StandingLamp"}]
    cords("cord_powered", "cord to lamp, powered", 0, 0, run + bat + lamp + [{"kind": "gss_charge", "dx": 0, "dz": 3}, {"kind": "gss_ticks", "n": 30}],
          "A conduit run with a battery feeding a standing lamp: do loose cords run from the conduit to the lamp and battery, lying on the ground, with lit (powered) ends?",
          ["cord_unpowered"])
    cords("cord_unpowered", "cord to lamp, no power", 1, 0, run + lamp,
          "The same run with no power source: are the cords drawn the same shape but with dead (unlit) ends and dark strips?",
          ["cord_powered"])
    cords("cord_wall_end", "run into a wall", 2, 0, run[:4] + [{"kind": "thing", "dx": 4, "dz": 2, "def": "Wall"},
                                                              {"kind": "thing", "dx": 4, "dz": 3, "def": "Wall"}] + bat + [{"kind": "gss_charge", "dx": 0, "dz": 3}],
          "A powered run that ends against a wall: does the cord disappear INTO the wall face with a stub, never drawn on top of the wall?",
          ["cord_powered"])
    tee = [{"kind": "thing", "dx": x, "dz": 2, "def": "PowerConduit"} for x in range(0, 6)] + \
          [{"kind": "thing", "dx": 3, "dz": z, "def": "PowerConduit"} for z in (3, 4)]
    cords("cord_tee", "T junction, two devices", 0, 7, tee + bat + [{"kind": "thing", "dx": 5, "dz": 0, "def": "StandingLamp"},
                                                             {"kind": "thing", "dx": 1, "dz": 0, "def": "StandingLamp"},
                                                             {"kind": "gss_charge", "dx": 0, "dz": 3}],
          "A T-shaped powered run feeding two lamps: is there a junction where the branches meet and one cord to each lamp?",
          ["cord_powered"])
    cords("cord_cut_live", "cut run, live end", 1, 7, run[:2] + run[3:] + bat + lamp + [{"kind": "gss_charge", "dx": 0, "dz": 3}],
          "A powered run with one conduit missing in the middle: does the live side end in a frayed/sparking tip and the far side read dead?",
          ["cord_powered"])
    # hoses: reel 2x2 at the subject's cell; its outlet faces west (-x), so 'ahead' targets are to the west
    def hose(sid, label, col, row, ops, question, diff, w=12, h=6, colour=None):
        exp = {"organic": False, "may_overflow": True}
        if colour:
            exp["colour"] = colour
        subs.append({"id": sid, "label": label, "cell": [col * 14, row], "size": [w, h], "overhang": 0.6,
                     "expect": exp, "differs_from": diff, "question": question, "stage": ops})

    def reel(dx=9, dz=2):
        return {"kind": "thing", "dx": dx, "dz": dz, "def": "RM_HoseReel"}
    for i, look in enumerate(GSS_LOOKS):
        subs.append({"id": "reel_stored_" + look, "label": "reel stored, " + look, "cell": [i * 5, 14], "size": [3, 3], "overhang": 0.5,
                     "expect": {"organic": False}, "differs_from": ["reel_stored_" + o for o in GSS_LOOKS if o != look],
                     "question": "A hose reel in the %s look with its hose wound on the drum: does it read as that look, hose stored, nothing spilling?" % look,
                     "stage": [{"kind": "thing", "dx": 0, "dz": 0, "def": "RM_HoseReel"}, {"kind": "gss_hose", "dx": 0, "dz": 0, "look": look}]})
    hose("hose_ahead_flat", "hose laid ahead, flat", 0, 19, [reel(), {"kind": "gss_hose", "dx": 9, "dz": 2, "tdx": 1, "tdz": 3, "flow": 0}],
         "A hose laid out of the reel's outlet to the left: does it leave THROUGH the outlet coupling, lie flat and limp, and bend smoothly?",
         ["hose_ahead_flowing"])
    hose("hose_ahead_flowing", "hose laid ahead, flowing", 1, 19, [reel(), {"kind": "gss_hose", "dx": 9, "dz": 2, "tdx": 1, "tdz": 3, "flow": 1}, {"kind": "gss_ticks", "n": 120}],
         "The same hose with liquid moving: is it plumper and rounder than the flat one, same route?",
         ["hose_ahead_flat"])
    hose("hose_behind_uturn", "hose laid BEHIND the outlet", 2, 19, [reel(dx=2), {"kind": "gss_hose", "dx": 2, "dz": 2, "tdx": 11, "tdz": 3, "flow": 0}],
         "A hose whose target is behind the reel (to the right): does it leave the outlet, then turn back in a smooth wide curve - no kink or hairpin right after the coupling? (fuzz gap G2, live MX_H FAILs)",
         ["hose_ahead_flat"])
    for i, (end, word) in enumerate((("open", "open end"), ("nozzle", "nozzle"), ("cap", "end cap"))):
        hose("hose_end_" + end, "free end: " + word, i, 27, [reel(), {"kind": "gss_hose", "dx": 9, "dz": 2, "tdx": 2, "tdz": 2, "end": end}],
             "Does the hose's free end (left) show a %s?" % word, ["hose_end_" + o for o in ("open", "nozzle", "cap") if o != end])
    # overhead lines
    def span(sid, label, col, ops, question, diff):
        subs.append({"id": sid, "label": label, "cell": [col * 14, 35], "size": [12, 4], "overhang": 1.0,
                     "expect": {"organic": False, "may_overflow": True}, "differs_from": diff, "question": question, "stage": ops})
    masts = [{"kind": "thing", "dx": 1, "dz": 1, "def": "RM_AerialMast"}, {"kind": "thing", "dx": 10, "dz": 1, "def": "RM_AerialMast"}]
    span("span_up", "span up", 0, masts + [{"kind": "gss_link", "dx": 1, "dz": 1, "dx2": 10, "dz2": 1}],
         "Two masts joined by an overhead wire: does the wire hang in a gentle sag from insulator to insulator, with a ground shadow?", ["span_cut"])
    span("span_cut", "span cut", 1, masts + [{"kind": "gss_link", "dx": 1, "dz": 1, "dx2": 10, "dz2": 1, "cut": 1}],
         "The same wire cut in the middle: do both halves hang down from their masts to the ground, no wire across the gap?", ["span_up"])
    span("span_bracket", "mast to wall bracket", 2,
         [{"kind": "thing", "dx": 1, "dz": 1, "def": "RM_AerialMast"}, {"kind": "thing", "dx": 10, "dz": 2, "def": "Wall"},
          {"kind": "thing", "dx": 10, "dz": 1, "def": "RM_AerialWallBracket", "rot": "north"},
          {"kind": "gss_link", "dx": 1, "dz": 1, "dx2": 10, "dz2": 1}],
         "A wire from a mast to a bracket on a wall: does the wire land on the bracket's drawn insulator, not the cell centre?", ["span_up"])
    return {
        "name": "gss_states",
        "note": "Gimme Some Slack looks board: cords, hose reels/hoses and overhead spans in the states a player meets. "
                "Pre-review policy (owner 2026-10-06): staging faults fixed silently, art faults with a known fix regenerated, "
                "only judgement calls reach him (artboard/autofix.py triage).",
        "ground": "Soil", "ppc": 48, "pad": 1.0, "margin": 1, "overhang": 0.3,
        "subjects": subs,
    }


RECIPES = {"flowworks_pit_states": flowworks_pit_states, "gss_states": gss_states}


def load(path_or_name):
    if path_or_name in RECIPES:
        return RECIPES[path_or_name]()
    with open(path_or_name) as fh:
        return json.load(fh)


def _crop_bounds(recipe):
    """World-local (x0, z0, x1, z1) covering every subject's crop (cells + overhang + pad)."""
    pad = float(recipe.get("pad", 0.5))
    x0 = z0 = math.inf
    x1 = z1 = -math.inf
    for s in recipe["subjects"]:
        ov = float(s.get("overhang", recipe.get("overhang", 0.15)))
        w, h = s.get("size", [1, 1])
        x, z = s["cell"]
        x0, z0 = min(x0, x - pad - ov), min(z0, z - pad - ov)
        x1, z1 = max(x1, x + w + pad + ov), max(z1, z + h + pad + ov)
    return x0, z0, x1, z1


def plan(recipe, origin):
    """Absolute staging plan: {clear_rect:[x,z,w,h], capture_rect:[x,z,w,h], ops:[line], by_id:{id:[op ids]}}.
    The capture rect covers every crop plus `margin` cells; the clear rect equals it, so the plate is plain ground."""
    ox, oz = origin
    m = int(recipe.get("margin", 1))
    bx0, bz0, bx1, bz1 = _crop_bounds(recipe)
    x0, z0 = ox + int(math.floor(bx0)) - m, oz + int(math.floor(bz0)) - m
    x1, z1 = ox + int(math.ceil(bx1)) + m, oz + int(math.ceil(bz1)) + m
    rect = [x0, z0, x1 - x0, z1 - z0]
    ops, gss_ops, by_id = [], [], {}
    for s in recipe["subjects"]:
        sx, sz = s["cell"]
        for k, op in enumerate(s.get("stage", [])):
            oid = "%s#%d" % (s["id"], k)
            gss = op["kind"].startswith("gss_")
            kv = [("id", oid), ("kind", op["kind"])]
            if op["kind"] != "gss_ticks":
                kv += [("x", ox + sx + op.get("dx", 0)), ("z", oz + sz + op.get("dz", 0))]
            if op["kind"] in ("pit", "terrain"):
                kv += [("w", op.get("w", 1)), ("h", op.get("h", 1))]
            if gss:
                # second cells are subject-relative too: tdx/tdz (hose target), dx2/dz2 (span partner)
                if "tdx" in op:
                    kv += [("tx", ox + sx + op["tdx"]), ("tz", oz + sz + op["tdz"])]
                if "dx2" in op:
                    kv += [("x2", ox + sx + op["dx2"]), ("z2", oz + sz + op["dz2"])]
                kv += [(k2, op[k2]) for k2 in GSS_OP_KEYS if k2 in op]
            else:
                kv += [(k2, op[k2]) for k2 in STAGE_KEYS if k2 in op]
            for _, v in kv:
                if "|" in str(v) or "\n" in str(v):
                    raise ValueError("op value may not contain | or newline: %r" % (v,))
            (gss_ops if gss else ops).append("|".join("%s=%s" % (k2, v) for k2, v in kv))
            by_id.setdefault(s["id"], []).append(oid)
    return {"clear_rect": rect, "capture_rect": rect, "ops": ops, "gss_ops": gss_ops, "by_id": by_id}


def parse_op(line):
    """Inverse of the op line format (what the C# side parses) - for the selftest."""
    return dict(p.split("=", 1) for p in line.split("|"))


def board_json(recipe, origin, capture, image, plate=None, drop=()):
    """The board artboard.run reads, in ABSOLUTE cells with the capture's own exact mapping."""
    ox, oz = origin
    drop = set(drop)
    subs = []
    for s in recipe["subjects"]:
        if s["id"] in drop:
            continue
        b = {k: v for k, v in s.items() if k != "stage"}
        b["cell"] = [ox + s["cell"][0], oz + s["cell"][1]]
        b["differs_from"] = [d for d in s.get("differs_from", []) if d not in drop]
        subs.append(b)
    board = {"image": image, "camera": {"ppc": capture["ppc"], "origin_px": list(capture["origin_px"])},
             "pad": recipe.get("pad", 0.5), "overhang": recipe.get("overhang", 0.15),
             "defaults": recipe.get("defaults", {}), "subjects": subs,
             "_recipe": recipe.get("name"), "_origin": [ox, oz]}
    if plate:
        board["plate"] = plate
    return board


def write_all():
    os.makedirs(RECIPE_DIR, exist_ok=True)
    out = []
    for name, fn in RECIPES.items():
        p = os.path.join(RECIPE_DIR, name + ".json")
        with open(p, "w") as fh:
            json.dump(fn(), fh, indent=1)
            fh.write("\n")
        out.append(p)
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["write"]:
        for p in write_all():
            print("wrote", p)
    else:
        print(__doc__)
