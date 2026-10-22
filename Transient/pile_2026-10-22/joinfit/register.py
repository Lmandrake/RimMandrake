#!/usr/bin/env python3
"""PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID ("Draw fittings", owner card 2026-10-22): register the conformed fittings
(cand/<Look>_<Piece>[_v2].png from conform.py) as kind=artpipe variants bound to Joins/<Look>/<Piece>, build the pipe
composites shown as read-only reference, and write the texture manifest the gated sheet is built from. NOT installed;
joinFittings stays off. Re-runnable: ids deterministic, store content-addressed.
    python3 register.py  -> textures_manifest.json
"""
import json, sys
from pathlib import Path
from PIL import Image
REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/artpipe"))
import artledger as L  # noqa: E402
import state_dir  # noqa: E402

HERE = Path(__file__).resolve().parent
ART = state_dir.resolve() / "_artsrc"
ITEM = "PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID"
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
ATLAS = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Pipe/{look}/UniversalPipe_Atlas.png"
PPC = 256
PIECES = {
    "Flange": ([0.5, 0.5], "pipe flange where a pipe meets a tank or machine",
               "RM_LiquidJoins/LiquidJoinRule.FlangeSize: a 0.5 x 0.5 cell quad, its face (canvas right edge) on the shared cell edge; collar 0.13 cell (joints study D4)"),
    "Coupler": ([0.5, 0.5], "union coupler where a pump or reel shares an edge with a tank",
                "SectionLayer_RM_LiquidJoins: a 0.5 x 0.5 cell quad centred on the shared edge; collar 0.12 cell (joints study D4)"),
    "Saddle": ([1, 1], "hose saddle on the pipe cell a hose end couples onto",
               "RM_LiquidJoins.DrawHosePortFitting: a 1 x 1 cell quad (SaddleLength x SaddleWidth) across the pipe cell; clamp 0.24 cell (joints study D4/D8)"),
}
w = L.Writer()
rows = []


def add(png, fam, res, prompt):
    d = ART / fam
    d.mkdir(parents=True, exist_ok=True)
    b = png.read_bytes()
    sha = L.store_put_bytes(b)
    (d / f"{fam}.png").write_bytes(b)
    ph, wd, ht = L.dhash(b)
    w.add({"type": "variant", "id": L.det_id("variant", "benchdraw", sha, fam), "sha": sha, "ph": ph, "w": wd, "h": ht,
           "kind": "artpipe", "loc": f"_artsrc/{fam}/{fam}.png", "date": L.now(), "job": fam, "res": res,
           "facing": "single", "mask": False, "item": ITEM, "prompt": prompt})


def pipe_tile(look):
    a = Image.open(str(ATLAS).format(look=look)).convert("RGBA")
    t = 176
    return a.crop((2 * t, 1 * t, 3 * t, 2 * t)).resize((PPC, PPC), Image.LANCZOS)   # tile 6: straight east-west


def composite(look, piece, cand):
    """The fitting on its pipe as RM_LiquidJoins draws it: Flange at the east end of a 2-cell run (a tank edge there);
    Saddle on the middle of a 3-cell run. Coupler has no pipe: shown alone between two grey tank-edge blocks."""
    c = Image.open(cand).convert("RGBA")
    if piece == "Flange":
        im = Image.new("RGBA", (2 * PPC + PPC // 2, PPC), (0, 0, 0, 0))
        for i in range(2):
            im.alpha_composite(pipe_tile(look), (i * PPC, 0))
        im.paste((96, 100, 104, 255), (2 * PPC, PPC // 8, im.width, PPC - PPC // 8))       # a tank's wall, east
        im.alpha_composite(c, (2 * PPC - c.width, PPC // 2 - c.height // 2))
        return im, [2.5, 1]
    if piece == "Saddle":
        im = Image.new("RGBA", (3 * PPC, PPC), (0, 0, 0, 0))
        for i in range(3):
            im.alpha_composite(pipe_tile(look), (i * PPC, 0))
        im.alpha_composite(c, (PPC, 0))
        return im, [3, 1]
    im = Image.new("RGBA", (PPC, PPC // 2), (0, 0, 0, 0))
    im.paste((96, 100, 104, 255), (0, 0, PPC // 2 - 2, PPC // 2))
    im.paste((120, 112, 100, 255), (PPC // 2 + 2, 0, PPC, PPC // 2))
    im.alpha_composite(c, (PPC // 2 - c.width // 2, 0))
    return im, [1, 0.5]


(HERE / "comp").mkdir(exist_ok=True)
for piece, (ds, labf, src) in PIECES.items():
    for look in LOOKS:
        res = f"RimMandrake/FlowWorks/Joins/{look}/{piece}"
        refs, made = [], False
        for ver in ("v1", "v2"):
            png = HERE / "cand" / (f"{look}_{piece}.png" if ver == "v1" else f"{look}_{piece}_v2.png")
            if not png.exists():
                continue
            fam = f"joinfit_{piece.lower()}_{look.lower()}_{ver}"
            add(png, fam, res, f"{piece} in the {look} look: artpipe master joinfitraw_{piece.lower()}_{look.lower()}_{ver} "
                               f"(1024, prompt carries the look's pipe-atlas colours), cropped to its collar and scaled to the "
                               f"study size by Transient/pile_2026-10-22/joinfit/conform.py")
            comp, cds = composite(look, piece, png)
            cp = HERE / "comp" / f"{look}_{piece}_{ver}.png"
            comp.save(cp)
            refs.append({"path": str(cp.relative_to(REPO)),
                         "size": {"drawSize": cds, "footprint": [max(1, round(cds[0])), 1],
                                  "source": f"composite ({ver}): the {piece.lower()} on the {look} pipe atlas, as RM_LiquidJoins places it"}})
            made = True
        if made:
            rows.append({"key": f"JoinFit_{piece}_{look}", "label": f"{labf}, {look.lower()} look", "part": piece.lower(),
                         "look": look, "variant": "A", "section": "joint fittings", "resources": [res],
                         "render_match": f"joinfit_{piece.lower()}_{look.lower()}_", "reference_textures": refs,
                         "size": {"drawSize": ds, "footprint": [1, 1], "source": src}})
w.flush()
lead = ("<p>Owner, by card 2026-10-22 (<i>Joints: fittings art and pipe meets tank</i> &rarr; <b>Draw fittings + pipe riser</b>): "
        "the 12 joint fitting pictures, one Flange, Coupler and Saddle per look, in that look's own pipe colours. Sizes from the "
        "joints study (D4): flange collar about 0.13 cell, union coupler 0.12, hose saddle 0.24, against a pipe of 0.10. "
        "Pick a column per row, or note what to change. The REFERENCE picture beside each row shows the piece on its pipe as the "
        "game places it. Nothing is installed and <code>joinFittings</code> stays off until you have picked. "
        "Item PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID; study Transient/pile_2026-10-22/joints_study.md.</p>")
(HERE / "textures_manifest.json").write_text(json.dumps({"rows": rows, "lead_html": lead}, indent=1))
print(len(rows), "rows")
