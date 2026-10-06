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


RECIPES = {"flowworks_pit_states": flowworks_pit_states}


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
    ops, by_id = [], {}
    for s in recipe["subjects"]:
        sx, sz = s["cell"]
        for k, op in enumerate(s.get("stage", [])):
            oid = "%s#%d" % (s["id"], k)
            kv = [("id", oid), ("kind", op["kind"]), ("x", ox + sx + op.get("dx", 0)), ("z", oz + sz + op.get("dz", 0))]
            if op["kind"] in ("pit", "terrain"):
                kv += [("w", op.get("w", 1)), ("h", op.get("h", 1))]
            kv += [(k2, op[k2]) for k2 in STAGE_KEYS if k2 in op]
            for _, v in kv:
                if "|" in str(v) or "\n" in str(v):
                    raise ValueError("op value may not contain | or newline: %r" % (v,))
            ops.append("|".join("%s=%s" % (k2, v) for k2, v in kv))
            by_id.setdefault(s["id"], []).append(oid)
    return {"clear_rect": rect, "capture_rect": rect, "ops": ops, "by_id": by_id}


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
