#!/usr/bin/env python3
"""DRAWBRIDGE_LOOKS_FIX_HIS_PICKS_OUTRANK (owner card 2026-10-22): DRAFT (not installed) shut gate pictures that match the
INSTALLED open gates exactly: the installed open frame is kept pixel-for-pixel and drawn OVER a planked door taken from the
2026-10-21 closed render of the same look (door cropped between its posts, scaled into the open frame's opening).
East: the installed open post with the door's edge slab behind it (the Steel/Industrial closed-east convention).
Outputs draft/<name>_{south,east}.png and ../phone/gate_shut_phone.png (+ .md)."""
import glob, sys
from pathlib import Path
from PIL import Image, ImageDraw
H = Path(__file__).resolve().parent
sys.path.insert(0, str(H.parent / "phone"))
import make_phone as M  # noqa: E402
ROOT = M.ROOT
T = ROOT / "src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Drawbridge"
A = "/mnt/d/ClaudeWork/rimmandrake/artpipe/_artsrc/"
# (name, open south/east stem, 10-21 closed render stem, door crop box in that render, opening box in the open frame)
GATES = [("Timber", "RM_DrawbridgeGate_Timber_Open", "RM_DrawbridgeGate_Timber_Closed", (56, 134, 200, 328), (56, 140, 199, 330)),
         ("Scrapper", "RM_DrawbridgeGate_Open_Scrapper", "RM_DrawbridgeGate_Closed_Scrapper", (77, 151, 189, 333), (55, 122, 199, 338))]
(H / "draft").mkdir(exist_ok=True)
out = {}
for name, open_stem, closed_stem, door_box, hole in GATES:
    src = Image.open(glob.glob(A + closed_stem + "_south/*.png")[0]).convert("RGBA")
    door = src.crop(door_box)
    fr_s = Image.open(T / (open_stem + "_south.png")).convert("RGBA")
    d = door.resize((hole[2] - hole[0], hole[3] - hole[1]), Image.LANCZOS)
    s = Image.new("RGBA", fr_s.size, (0, 0, 0, 0))
    s.alpha_composite(d, (hole[0], hole[1]))
    s.alpha_composite(fr_s)            # the installed frame on top, unchanged
    fr_e = Image.open(T / (open_stem + "_east.png")).convert("RGBA")
    bb = fr_e.split()[3].point(lambda v: 255 if v > 40 else 0).getbbox()
    slab_w = max(10, (bb[2] - bb[0]) // 3)
    strip = door.crop((0, 0, max(6, door.width // 6), door.height)).resize((slab_w, hole[3] - hole[1]), Image.LANCZOS)
    shade = Image.new("RGBA", strip.size, (0, 0, 0, 70)); shade.putalpha(strip.split()[3].point(lambda v: v * 70 // 255))
    strip.alpha_composite(shade)
    e = Image.new("RGBA", fr_e.size, (0, 0, 0, 0))
    e.alpha_composite(strip, (bb[2] - slab_w // 2, hole[1]))
    e.alpha_composite(fr_e)
    for face, im in (("south", s), ("east", e)):
        p = H / "draft" / f"RM_DrawbridgeGate_{name}_Shut_{face}.png"
        im.save(p); out[(name, face)] = (im, p)

PPC = 256.0
items = [("A", "Timber", "south"), ("B", "Timber", "east"), ("C", "Scrapper", "south"), ("D", "Scrapper", "east")]
tiles = []
for L, name, face in items:
    stem = dict((g[0], g[1]) for g in GATES)[name]
    tiles.append(M.caption_tile(Image.open(T / f"{stem}_{face}.png").convert("RGBA"), "·", f"{name} OPEN {face} (installed)", 256, 384))
    tiles.append(M.caption_tile(out[(name, face)][0], L, f"{name} SHUT {face} draft {out[(name, face)][0].width}x{out[(name, face)][0].height}", 256, 384))
grid = M.stack([M.row(tiles[0:4], gap=8), M.row(tiles[4:8], gap=8)], gap=12)
sc_items = []
for L, name, face in items:
    stem = dict((g[0], g[1]) for g in GATES)[name]
    sc_items.append((M.resize_ppc(Image.open(T / f"{stem}_{face}.png").convert("RGBA"), PPC, 64), f"{name[:4]} open"))
    sc_items.append((M.resize_ppc(out[(name, face)][0], PPC, 64), L))
sc = M.scene(sc_items, 64, "TRUE SCALE at 64 px/cell (normal play): human, then each draft beside its installed OPEN gate (1 x 1.5 cells)",
             h_cells=2.4, pad_cells=0.3)
W = max(grid.width, sc.width)
img = M.stack([M.title("Drawbridge gate: SHUT drafts (A-D), NOT installed",
                       "Frame = the installed open gate, pixel for pixel; door = planks from the 10-21 closed render. (·) = installed open.", W),
               grid, sc])
po = M.OUT / "gate_shut_phone.png"
img.convert("RGB").save(po, optimize=True)
with open(M.OUT / "gate_shut_phone.md", "w") as f:
    f.write("# gate_shut_phone.png — letter key\n\nItem `DRAWBRIDGE_LOOKS_FIX_HIS_PICKS_OUTRANK`. DRAFTS, NOT installed. Each shut picture keeps the "
            "installed OPEN gate's frame pixel for pixel and puts a planked door behind it (planks cropped from the 2026-10-21 closed "
            "render of that look; that render itself was never picked: its frame does not match the installed open gate). "
            "No Scrapper closed gate had been picked, so C/D are drafted too.\n\n| letter | gate | facing | draft file | slot it would fill |\n|---|---|---|---|---|\n")
    slot = {"Timber": "Things/Building/FlowWorks/Drawbridge/RM_DrawbridgeGate_Timber_Closed", "Scrapper": "Things/Building/FlowWorks/Drawbridge/RM_DrawbridgeGate_Closed_Scrapper"}
    for L, name, face in items:
        f.write(f"| {L} | {name} | {face} | `Transient/pile_2026-10-22/gate_shut/draft/RM_DrawbridgeGate_{name}_Shut_{face}.png` | `{slot[name]}_{face}` |\n")
    f.write("\nTop rows: installed open (·) then the shut draft, full res. Bottom strip: true scale at 64 px/cell beside a vanilla human, "
            "each draft beside its open gate.\nCard shape: per letter accept / redo (note what to change).\n")
print(po)
