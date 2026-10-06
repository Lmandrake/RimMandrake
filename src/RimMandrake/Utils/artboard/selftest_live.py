"""Selftest for the live half's pure logic: recipes, the staging plan, the op-line format the C# tool parses,
refusal bookkeeping, and the capture mapping convention end to end on a synthetic frame painted with the
SAME formula jawa/artboard_capture returns (u = (X - x0)*ppc, v = (z0 + h - Z)*ppc).

    cd src/RimMandrake/Utils && python3 -m artboard.selftest_live      (or: python3 artboard/selftest_live.py)
"""
import json
import os
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from artboard import live, recipes, run as runmod  # noqa: E402
else:
    from . import live, recipes, run as runmod

GROUND = (110, 80, 55)


def fake_capture(rect, ppc):
    """Exactly what JawaBenchArtboardTools.ArtboardRenderNow returns for the mapping."""
    x, z, w, h = rect
    return {"success": True, "ppc": ppc, "origin_px": [-x * ppc, (z + h) * ppc], "frame": [w * ppc, h * ppc],
            "foggedCells": 0, "roofedCells": 0, "skyGlow": 1.0, "cameraRestored": True}


def paint(recipe, origin, rect, ppc, skip=()):
    x0, z0, w, h = rect
    img = np.zeros((h * ppc, w * ppc, 3), np.uint8)
    img[:] = GROUND
    plate = img.copy()

    def fill(X, Z, W, H, col):
        l, r = int((X - x0) * ppc), int((X + W - x0) * ppc)
        t, b = int((z0 + h - (Z + H)) * ppc), int((z0 + h - Z) * ppc)
        img[t:b, l:r] = col
    for i, s in enumerate(recipe["subjects"]):
        if s["id"] in skip or s["id"] == "undug":
            continue
        X, Z = origin[0] + s["cell"][0], origin[1] + s["cell"][1]
        for op in s["stage"]:
            ox, oz = X + op.get("dx", 0), Z + op.get("dz", 0)
            if op["kind"] in ("pit", "terrain"):
                if op.get("def") == "Soil":
                    continue
                f = op.get("fill", 0)
                fl = op.get("fluid", "")
                d = op.get("depth", 1)
                if op.get("def") == "WaterShallow":
                    col = (40, 100, 200)
                elif op.get("def") == "WaterDeep":
                    col = (20, 50, 140)
                elif f == 0:
                    col = (230 - 25 * d,) * 3
                elif "Water" in fl:
                    col = (20, 20 + 40 * f, 110 + 25 * d)
                else:
                    col = (5 + 9 * f + 2 * d,) * 3
                fill(ox, oz, op["w"], op["h"], col)
            elif op["kind"] == "pawn":
                l, t = int((ox + 0.2 - x0) * ppc), int((z0 + h - (oz + 0.95)) * ppc)
                im = Image.fromarray(img)
                ImageDraw.Draw(im).ellipse([l, t, l + int(0.6 * ppc), t + int(0.85 * ppc)], fill=(230, 120, 40))
                img[:] = np.asarray(im)
    return img, plate


def main():
    fails = []
    n = 0

    def expect(name, ok, got=None):
        nonlocal n
        n += 1
        if not ok:
            fails.append(name)
            print("FAIL %s: %s" % (name, got))

    r = recipes.flowworks_pit_states()
    pits = [s for s in r["subjects"] if any(op["kind"] == "pit" for op in s["stage"]) and "pawn" not in s["id"]]
    states = {(op["depth"], op["fill"]) for s in pits for op in s["stage"]}
    expect("14 legal (D,F) states", len(recipes.legal_states()) == 14 and states == set(recipes.legal_states()), states)
    expect("every state x {water, tar} = 28 pit subjects", len(pits) == 28, len(pits))
    expect("references + lip cases present", {"undug", "vanilla_shallow", "vanilla_deep", "pawn_below_lip_D2",
                                               "pawn_below_lip_D3", "pawn_on_lip_D3"} <= {s["id"] for s in r["subjects"]})
    ids = [s["id"] for s in r["subjects"]]
    expect("subject ids unique", len(ids) == len(set(ids)))
    expect("differs_from names only real ids", all(d in ids for s in r["subjects"] for d in s.get("differs_from", [])))
    committed = os.path.join(recipes.RECIPE_DIR, "flowworks_pit_states.json")
    expect("committed recipe JSON == generator (run: python3 -m artboard.recipes write)",
           os.path.exists(committed) and json.load(open(committed)) == json.loads(json.dumps(r)))

    # no two subjects' crops overlap their cores (pitch >= size + pad)
    pad = r["pad"]
    boxes = []
    for s in r["subjects"]:
        ov = s.get("overhang", r["overhang"])
        w, h = s["size"]
        boxes.append((s["id"], s["cell"][0] - ov, s["cell"][1] - ov, s["cell"][0] + w + ov, s["cell"][1] + h + ov))
    clash = [(a[0], b[0]) for i, a in enumerate(boxes) for b in boxes[i + 1:]
             if a[1] < b[3] + pad and b[1] < a[3] + pad and a[2] < b[4] + pad and b[2] < a[4] + pad]
    expect("no core lies inside a neighbour's ring", not clash, clash[:3])

    origin = (40, 30)
    pl = recipes.plan(r, origin)
    x, z, w, h = pl["capture_rect"]
    expect("capture rect fits one frame at the recipe ppc", w * r["ppc"] <= 8192 and h * r["ppc"] <= 8192, (w, h))
    parsed = [recipes.parse_op(o) for o in pl["ops"]]
    expect("op lines round-trip with id/kind/x/z", all({"id", "kind", "x", "z"} <= set(p) for p in parsed))
    pit_d4 = [p for p in parsed if p["kind"] == "pit" and p["depth"] == "4" and p["fill"] == "4"]
    expect("D4F4 ops carry the fluid", len(pit_d4) == 2 and {p.get("fluid") for p in pit_d4} ==
           {"RM_Fluid_Water", "RM_Fluid_Tar"}, pit_d4)
    expect("dry pits carry no fluid", all("fluid" not in p for p in parsed if p.get("fill") == "0"))
    xs = [int(p["x"]) for p in parsed]
    zs = [int(p["z"]) for p in parsed]
    expect("every op inside the clear rect", min(xs) >= x and min(zs) >= z and max(xs) < x + w and max(zs) < z + h)
    lip = [p for p in parsed if p["id"].startswith("pawn_on_lip_D3")]
    expect("lip pawn stands one cell south of its pit", int(lip[1]["z"]) == int(lip[0]["z"]) - 1, lip)
    try:
        recipes.plan({"subjects": [{"id": "a|b", "cell": [0, 0], "stage": [{"kind": "terrain", "def": "x|y"}]}]}, (0, 0))
        expect("a '|' in an op value is refused", False)
    except ValueError:
        expect("a '|' in an op value is refused", True)

    # refusal bookkeeping
    st = {"ops": [{"id": "D1F0_water#0", "ok": True}, {"id": "pawn_on_lip_D3#0", "ok": True},
                  {"id": "pawn_on_lip_D3#1", "ok": False, "error": "cell (1,0,1) is not standable"}]}
    rf = live.subject_status(st, pl["by_id"])
    expect("refused op -> its subject listed", "pawn_on_lip_D3" in rf and "D1F0_water" not in rf, rf)
    expect("missing result counts as refused", "D2F2_tar" in rf, list(rf)[:4])
    expect("capture warnings name fog and dusk",
           len(live.capture_warnings({"foggedCells": 3, "skyGlow": 0.5})) == 2)

    expect("WSL drive path -> Windows path for the game", live.WIN or
           live.to_win("/mnt/d/Luke/dev/_rmscratch/a/b.png") == "D:\\Luke\\dev\\_rmscratch\\a\\b.png")
    try:
        live.WIN or live.to_win("/home/x/out")
        expect("an ext4 output path is refused (the game cannot write it)", live.WIN)
    except ValueError:
        expect("an ext4 output path is refused (the game cannot write it)", True)

    # end to end on a synthetic frame painted with the C# mapping
    with tempfile.TemporaryDirectory() as tmp:
        ppc = 16
        img, plate = paint(r, origin, pl["capture_rect"], ppc)
        Image.fromarray(img).save(os.path.join(tmp, "board.png"))
        Image.fromarray(plate).save(os.path.join(tmp, "plate.png"))
        cap = fake_capture(pl["capture_rect"], ppc)
        drop = {"vanilla_deep"}
        b = recipes.board_json(r, origin, cap, "board.png", "plate.png", drop=drop)
        expect("dropped subject removed and unreferenced", all(s["id"] not in drop for s in b["subjects"]) and
               all("vanilla_deep" not in s.get("differs_from", []) for s in b["subjects"]))
        json.dump(b, open(os.path.join(tmp, "b.json"), "w"))
        rep = runmod.run(os.path.join(tmp, "b.json"), os.path.join(tmp, "o"))
        flagged = {row["id"]: [f["check"] for f in row["findings"]] for row in rep["rows"] if row["findings"]}
        expect("synthetic board from the C# mapping: every crop lands, zero findings", not flagged, flagged)
        expect("all subjects but the dropped one segmented", rep["subjects"] == len(r["subjects"]) - 1, rep["subjects"])

        # and the mapping is not trivially forgiving: shift the origin by 1 cell -> findings appear
        cap2 = dict(cap, origin_px=[cap["origin_px"][0] + ppc, cap["origin_px"][1]])
        b2 = recipes.board_json(r, origin, cap2, "board.png", "plate.png")
        json.dump(b2, open(os.path.join(tmp, "b2.json"), "w"))
        rep2 = runmod.run(os.path.join(tmp, "b2.json"), os.path.join(tmp, "o2"))
        expect("a one-cell mapping error is caught", rep2["flagged"] >= 10, rep2["by_check"].keys())

    print("%d/%d passed" % (n - len(fails), n))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
