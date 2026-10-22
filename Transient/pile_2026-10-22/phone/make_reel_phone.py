#!/usr/bin/env python3
"""Phone collection for REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED (16 north/south reel drafts, A-P)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_phone as M  # noqa: E402
ROOT = M.ROOT
A = Path("/mnt/d/ClaudeWork/rimmandrake/artpipe/_artsrc")
B = ROOT / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose"
LOOKS = {"Scrapper": "", "Industrial": "Styles/Industrial/", "Modern": "Styles/Modern/", "Futuristic": "Styles/Futuristic/"}
ST = {"stored": "PumpHookup", "laid": "Deployed"}
letters = iter("ABCDEFGHIJKLMNOP")
key, rows, scale_items = [], [], []
NATIVE_PPC = 256 / 2.15
for look, sub in LOOKS.items():
    tiles = []
    for st, tex in ST.items():
        west = Image.open(B / f"{sub}Reel_{tex}.png").convert("RGBA")
        tiles.append(M.caption_tile(west, "·", f"{look} {st} WEST (today)", 256, 256))
        for face in ("north", "south"):
            fam = f"reelns_{look.lower()}_{st}_{face}_v1"
            p = A / fam / f"{fam}.png"
            im = Image.open(p).convert("RGBA")
            L = next(letters)
            key.append((L, look, st, face, fam, f"RimMandrake/FlowWorks/Hose/{sub}Reel_{tex}_{face}"))
            tiles.append(M.caption_tile(im, L, f"{st} {face.upper()} {im.width}px", 256, 256))
            if st == "stored":
                scale_items.append((M.resize_ppc(im, NATIVE_PPC, 64), f"{L}"))
        if st == "stored":
            scale_items.insert(len(scale_items) - 2, (M.resize_ppc(west, NATIVE_PPC, 64), f"{look[:4]} W"))
    rows.append(M.row(tiles, gap=8))
grid = M.stack(rows, gap=16)
sc = M.scene(scale_items, 64, "TRUE SCALE at 64 px/cell (normal play): human, then each look's stored reel W / N / S (2x2 reel, drawn 2.15 cells)",
             h_cells=3.2, pad_cells=0.2)
W = max(grid.width, sc.width)
img = M.stack([M.title("Hose reel: north + south drafts (A-P)",
                       "Each row: today's WEST picture (·), then the new NORTH and SOUTH, stored (full drum) then laid (empty drum).", W),
               grid, sc])
out = M.OUT / "reel_ns_phone.png"
img.convert("RGB").save(out, optimize=True)
with open(M.OUT / "reel_ns_phone.md", "w") as f:
    f.write("# reel_ns_phone.png — letter key\n\nItem `REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED`. 16 artpipe drafts drawn from each "
            "look's installed west picture; registered in the art ledger (kind artpipe, facing north/south), NOT installed. "
            "Installing them also owes a small C# change: Graphic_HoseReel/HoseReelRect.ArtPose today turns the west picture "
            "for north/south (stand-in).\n\n| letter | look | state | facing | artpipe job | slot (texPath) |\n|---|---|---|---|---|---|\n")
    for L, look, st, face, fam, tp in key:
        f.write(f"| {L} | {look} | {st} | {face} | `{fam}` (`D:\\ClaudeWork\\rimmandrake\\artpipe\\_artsrc\\{fam}\\{fam}.png`) | `{tp}` |\n")
    f.write("\n`·` tiles are today's installed west pictures, for comparison. Bottom strip: stored reels at true scale beside "
            "a vanilla human.\nCard shape: per look 'accept all 4 / redo <letters>'.\n")
print(out)
