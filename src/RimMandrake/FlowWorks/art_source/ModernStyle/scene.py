#!/usr/bin/env python3
"""Offline in-context mock of a Modern water line (NOT an in-game capture): pipe network from a linked atlas,
joins, faucet, sprinkler, pump, tank, hose strand, reel, on game-dirt ground.
Usage: scene.py OUT.png [--over DIR] [--px N]   DIR holds candidate files named like the live ones
(UniversalPipe_Atlas.png, Coupler.png, Flange.png, Saddle.png, RM_PipeFaucet.png, RM_SprinklerHead.png,
RM_LiquidPump.png, PipeSpan.png, RM_Barrel.png, RM_Bucket.png); missing ones fall back to live art."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw
REPO = Path(__file__).resolve().parents[5]
FW = REPO / "src/RimMandrake/FlowWorks/Textures"
LIVE = {
 "UniversalPipe_Atlas.png": FW / "RimMandrake/FlowWorks/Pipe/Modern/UniversalPipe_Atlas.png",
 "Coupler.png": FW / "RimMandrake/FlowWorks/Joins/Modern/Coupler.png",
 "Flange.png": FW / "RimMandrake/FlowWorks/Joins/Modern/Flange.png",
 "Saddle.png": FW / "RimMandrake/FlowWorks/Joins/Modern/Saddle.png",
 "RM_PipeFaucet.png": FW / "RimMandrake/FlowWorks/Faucet/Modern/RM_PipeFaucet.png",
 "RM_SprinklerHead.png": FW / "RimMandrake/FlowWorks/Sprinkler/Modern/RM_SprinklerHead.png",
 "RM_LiquidPump.png": FW / "RimMandrake/FlowWorks/Pump/Modern/RM_LiquidPump.png",
 "RM_LiquidTank.png": FW / "RimMandrake/FlowWorks/Tank/Modern/RM_LiquidTank.png",
 "RM_LiquidTankTall.png": FW / "RimMandrake/FlowWorks/Tank/Modern/RM_LiquidTankTall.png",
 "Strand_Plump.png": FW / "RimMandrake/FlowWorks/Hose/Styles/Modern/Strand_Plump.png",
 "Reel_PumpHookup.png": FW / "RimMandrake/FlowWorks/Hose/Styles/Modern/Reel_PumpHookup.png",
 "PipeSpan.png": FW / "RimMandrake/FlowWorks/PipePole/Modern/PipeSpan.png",
 "RM_Barrel.png": FW / "Things/Item/Resource/FlowWorks/Modern/RM_Barrel.png",
 "RM_Bucket.png": FW / "Things/Item/Resource/FlowWorks/Modern/RM_Bucket.png",
}
T, P, C = 176, 22, 132
# pipe cells (x, y) on a 12 x 7 grid, y down
PIPE = {(x, 3) for x in range(2, 11)} | {(6, y) for y in range(1, 3)} | {(9, y) for y in range(4, 6)}  # coupler (machine-tank edge) not shown

def get(name, over):
    p = Path(over) / name if over else None
    return Image.open(p if p and p.exists() else LIVE[name]).convert("RGBA")

def tile(atlas, i):
    col, row_b = i % 4, i // 4; r = 3 - row_b
    return atlas.crop((col * T + P, r * T + P, col * T + P + C, r * T + P + C))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--over"); ap.add_argument("--px", type=int, default=64)
    a = ap.parse_args(); px = a.px
    W, H = 12, 7
    im = Image.new("RGBA", (W * px, H * px), (112, 86, 62, 255))
    d = ImageDraw.Draw(im)
    for x in range(W):                       # faint dirt mottling
        for y in range(H):
            if (x * 7 + y * 3) % 5 == 0:
                d.rectangle((x * px, y * px, x * px + px - 1, y * px + px - 1), fill=(106, 81, 58, 255))
    atlas = get("UniversalPipe_Atlas.png", a.over)
    def put(img, cx, cy, w, h):              # centre (cx,cy) in cells, size in cells
        t = img.resize((int(w * px), int(h * px)), Image.LANCZOS)
        im.alpha_composite(t, (int(cx * px - t.width / 2), int(cy * px - t.height / 2)))
    for (x, y) in PIPE:
        i = ((x, y - 1) in PIPE) * 1 + ((x + 1, y) in PIPE) * 2 + ((x, y + 1) in PIPE) * 4 + (((x - 1, y) in PIPE) or (x, y) == (2, 3)) * 8 + ((x, y) == (10, 3)) * 2  # (2,3) runs into the tank (pipeLinksIntoMachines)
        im.alpha_composite(tile(atlas, i).resize((px, px), Image.LANCZOS), (x * px, y * px))
    put(get("RM_LiquidTankTall.png", a.over), 1.3, 2.75, 2, 3)          # tank 2x2 (+north); nudged so its DRAWN edge meets the flange (TANK_FLANGE_FIX: flange on the drawn outline)
    put(get("Flange.png", a.over).transpose(Image.FLIP_LEFT_RIGHT), 2.25, 3.5, 0.5, 0.5)   # FlangeSize 0.5, face on the cell edge   # pipe meets the tank to its west
    put(get("Saddle.png", a.over), 8.5, 3.5, 1, 1)   # SaddleLength/Width 1.0                                   # hose on a straight pipe cell
    put(get("RM_PipeFaucet.png", a.over), 6.5, 1.5, 1, 1)                            # on the north pipe end cell
    put(get("RM_LiquidPump.png", a.over), 11.5, 3.5, 1, 1)
    put(get("RM_SprinklerHead.png", a.over), 9.5, 5.5, 1, 1)
    put(get("RM_Barrel.png", a.over), 3.5, 5.5, 1, 1)
    put(get("RM_Bucket.png", a.over), 4.5, 5.5, 1, 1)
    sp = get("PipeSpan.png", a.over); put(sp, 9.0, 0.5, 3, 0.136)
    st = get("Strand_Plump.png", a.over).rotate(90, expand=True); put(st, 11.5, 5.5, 0.195, 3); put(st, 8.5, 5.25, 0.195, 3.1)
    put(get("Reel_PumpHookup.png", a.over), 11.0, 1.5, 2.15, 2.15)
    im.convert("RGB").save(a.out); print(a.out, im.size)

if __name__ == "__main__":
    main()
