#!/usr/bin/env python3
"""Offline mockups for the owner's five FlowWorks visual principles (2026-10-05).

Renders BEFORE (what ships today) and AFTER (what the code change draws) for a
3x4-cell dug pit at depths D1..D4, on dirt and on stone, in four states: dry,
water, tar, scorched. Water/tar/oil/slime tiles are animated GIFs so the motion
can be judged; dry/scorched are single-frame GIFs so every tile is one format.

The AFTER algorithm mirrors the C# (RM_WallFaceMath table, RM_LiquidSurface
look rows, RM_PitScorch) so what he approves here is what the game draws.
Real vanilla textures come from resources.assets (extracted with UnityPy into
D:\\Luke\\dev\\_rmscratch\\fwvis\\tex — derived, not committed).

    python3 make_mockups.py            # writes PNG/GIFs beside this file
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = "/mnt/d/Luke/dev/_rmscratch/fwvis/tex"
PX = 46                      # pixels per cell
W, H = 6, 6                  # scene cells
PIT_X0, PIT_X1 = 1, 5        # pit columns [x0, x1)
PIT_R0, PIT_R1 = 1, 4        # pit rows (screen rows, 0 = north) [r0, r1)
FRAMES = 8

# ---- the numbers the C# uses (keep in step with RM_WallFaceMath / RM_LiquidSurface) ----
NORTH = {1: 0.10, 2: 0.18, 3: 0.30, 4: 0.50}      # north face height, cells (vanilla wall face ~0.25)
SIDE = {1: 0.04, 2: 0.07, 3: 0.12, 4: 0.18}       # side face width, cells
FLOOR_TINT = {1: 1.0, 2: 0.78, 3: 0.58, 4: 0.38}  # RM_Channel_* <color> ramp (unchanged)
SINK = 0.3                                         # PIT_DEPTH_DRAW_OFFSET_1 (unchanged)

OLD_NORTH = {d: min(0.92, 0.225 * d) for d in range(1, 5)}
OLD_SIDE = {d: min(0.24, 0.06 * d) for d in range(1, 5)}

# liquid look rows (RM_LiquidSurfaceLook): base RGB, highlight RGB, highlight strength,
# scale (cells per noise tile), speed (cells/s), sharpness, sheen (rainbow 0..1), opacity of body
LOOKS = {
    "water": dict(base=(74, 88, 98), hi=(215, 232, 245), amt=0.45, scale=2.0, speed=0.45, sharp=4.0, sheen=0.0, body=0.88, grid=12, stretch=1.0),
    "tar":   dict(base=(18, 15, 13), hi=(205, 196, 180), amt=0.45, scale=2.2, speed=0.05, sharp=3.0, sheen=0.0, body=1.0, grid=10, stretch=0.4),
    "oil":   dict(base=(30, 23, 15), hi=(230, 210, 170), amt=0.40, scale=2.4, speed=0.10, sharp=2.0, sheen=0.6, body=1.0, grid=8, stretch=0.6),
    "slime": dict(base=(84, 136, 52), hi=(210, 245, 160), amt=0.40, scale=1.6, speed=0.06, sharp=3.0, sheen=0.0, body=0.94, grid=6, stretch=1.0),
}


def load(name, tint=None, scale_cells=8):
    """A vanilla terrain texture tiled over the scene in world space (as the terrain shader does)."""
    im = Image.open(os.path.join(TEX, name + ".png")).convert("RGB")
    size = PX * scale_cells
    im = im.resize((size, size), Image.LANCZOS)
    arr = np.asarray(im).astype(np.float32) / 255.0
    reps = (math.ceil(H * PX / size) + 1, math.ceil(W * PX / size) + 1, 1)
    arr = np.tile(arr, reps)[: H * PX, : W * PX]
    if tint is not None:
        arr = arr * (np.array(tint, np.float32) / 255.0)
    return arr


def noise(n, seed, stretch=1.0, grid=8):
    """Tileable smooth value noise, n x n pixels, values 0..1; stretch > 1 elongates it east-west."""
    rng = np.random.RandomState(seed)
    gy = max(2, int(round(grid * stretch)))
    g = rng.rand(gy, grid).astype(np.float32)
    big = np.tile(g, (3, 3))
    im = Image.fromarray((big * 255).astype(np.uint8)).resize((n * 3, n * 3), Image.BICUBIC)
    a = np.asarray(im).astype(np.float32)[n: 2 * n, n: 2 * n] / 255.0
    return a


NOISE = {}


def surface(look, frame, h_px, w_px, origin_px=(0, 0)):
    """The animated liquid surface: two noise layers drifting against each other, highlights where they
    crest together. Mirrors RM_LiquidSurface's two scrolling overlay layers."""
    L = LOOKS[look]
    n = int(PX * L["scale"])
    key = (look, n)
    if key not in NOISE:
        st = L.get("stretch", 1.0)
        NOISE[key] = (noise(n, 11, st, L.get("grid", 8)), noise(n, 23, st, L.get("grid", 8)))
    a, b = NOISE[key]
    t = frame / FRAMES * 2.0       # seconds into a 2 s loop
    off = int(L["speed"] * t * PX)
    ys, xs = np.mgrid[0:h_px, 0:w_px]
    ys = ys + origin_px[0]
    xs = xs + origin_px[1]
    l1 = a[(ys + off) % n, (xs + off // 2) % n]
    l2 = b[(ys - off // 2) % n, (xs - off) % n]
    crest = np.clip((l1 + l2) / 2.0, 0, 1)
    hi = np.clip((crest - 0.5) * 2.0, 0, 1) ** L["sharp"] * L["amt"] * 3.0
    trough = np.clip((0.5 - crest) * 2.0, 0, 1) * 0.18
    base = np.array(L["base"], np.float32) / 255.0
    col = np.ones((h_px, w_px, 3), np.float32) * base
    col = col * (1 - trough[..., None])
    hic = np.array(L["hi"], np.float32) / 255.0
    if L["sheen"] > 0:
        hue = (l1 * 3.0 + l2 * 2.0) % 1.0
        rb = np.stack([0.5 + 0.5 * np.cos(2 * np.pi * (hue + k)) for k in (0.0, 0.33, 0.66)], -1)
        hic = hic * (1 - L["sheen"]) + rb * L["sheen"]
    col = col + hi[..., None] * hic * 0.6
    return np.clip(col, 0, 1)


def cell_rect(x, r):
    return r * PX, (r + 1) * PX, x * PX, (x + 1) * PX


def draw_scene(material, depth, state, after, frame=0, look=None):
    ground = load("Soil") if material == "dirt" else load("RoughStone", tint=(118, 108, 104))
    gravel = load("Gravel")
    img = ground.copy()
    py0, py1 = PIT_R0 * PX, PIT_R1 * PX
    px0, px1 = PIT_X0 * PX, PIT_X1 * PX
    # pit floor (RM_Channel_* gravel, darker with depth)
    floor = gravel[py0:py1, px0:px1] * FLOOR_TINT[depth]
    if state == "scorched" and after:
        ash = noise(PX, 5)
        ashi = np.kron(np.ones((PIT_R1 - PIT_R0 + 1, PIT_X1 - PIT_X0 + 1)), ash)[: py1 - py0, : px1 - px0]
        char = np.stack([0.11 + 0.10 * ashi, 0.10 + 0.09 * ashi, 0.09 + 0.08 * ashi], -1)
        floor = floor * 0.25 + char * 0.75
    img[py0:py1, px0:px1] = floor
    fill = 0
    if state in ("water", "tar", "oil", "slime"):
        fill = max(1, depth - 1)
    exposed = depth - fill
    # liquid body covers the pit floor (and the foot of the faces, handled by exposed drop)
    if fill > 0:
        lk = state
        if after:
            body = surface(lk, frame, py1 - py0, px1 - px0, (py0, px0))
            a = LOOKS[lk]["body"]
            img[py0:py1, px0:px1] = img[py0:py1, px0:px1] * (1 - a) + body * a
        else:
            ramp = {1: (85, 94, 96), 2: (74, 85, 90), 3: (66, 75, 85)}[min(3, fill)]
            mul = {"water": (255, 255, 255), "tar": (28, 24, 20), "oil": (70, 52, 24), "slime": (96, 150, 64)}[lk]
            c = np.array(ramp, np.float32) / 255.0 * np.array(mul, np.float32) / 255.0
            if lk == "water":
                c = np.array(ramp, np.float32) / 255.0
            img[py0:py1, px0:px1] = c
    # faces
    if exposed > 0:
        if after:
            nh = NORTH[exposed]
            sw = SIDE[exposed]
        else:
            nh = OLD_NORTH[exposed]
            sw = OLD_SIDE[exposed]
        fh = int(round(nh * PX))
        fw = int(round(sw * PX))
        foot_dark = min(0.95, 0.35 + 0.15 * depth)
        if after:
            # north face: the ground's own texture continued down the face, vanilla-wall lit at the rim,
            # ambient-occluded at the foot; strata (dirt) or block joints (stone)
            src = ground[py0 - fh:py0, px0:px1] if fh > 0 else None
            if fh > 0:
                face = ground[py0:py0 + fh, px0:px1].copy()
                v = np.linspace(0, 1, fh)[:, None, None]
                shade = 1.50 - v * (0.30 + 0.25 * (depth / 4.0))
                face = face * shade
                if material == "dirt":
                    strata = 0.86 + 0.14 * np.sin(np.linspace(0, fh / PX * 34, fh))[:, None, None] ** 2
                    face = face * strata
                else:
                    jl = np.ones((fh, px1 - px0, 1), np.float32)
                    for k in range(1, 6):
                        yy = int(fh * k / 5.5)
                        if yy < fh:
                            jl[yy] = 0.62
                    for xx in range(0, px1 - px0, int(PX * 0.6)):
                        jl[:, xx:xx + 1] = np.minimum(jl[:, xx:xx + 1], 0.7)
                    face = face * jl
                if state == "scorched":
                    soot = noise(PX, 9, 0.3)
                    s = np.kron(np.ones((2, PIT_X1 - PIT_X0 + 1)), soot)[:fh, : px1 - px0]
                    climb = (v[..., 0] ** 0.6)
                    face = face * (0.28 + 0.25 * (1 - climb) * (0.6 + 0.4 * s))[..., None]
                img[py0:py0 + fh, px0:px1] = face
                img[py0:py0 + 2, px0:px1] *= 0.25       # crisp rim line, as vanilla's rock atlas outlines its walls
                img[py0 + fh:py0 + fh + 3, px0:px1] *= 0.55   # contact shadow where the face meets the floor
            for side in ("w", "e"):
                xs = slice(px0, px0 + fw) if side == "w" else slice(px1 - fw, px1)
                strip = ground[py0:py1, xs].copy() * (0.55 if side == "w" else 1.25)
                if state == "scorched":
                    strip *= 0.35
                img[py0 + fh:py1, xs] = strip[fh:]
        else:
            rim = np.array((196, 164, 118), np.float32) / 255.0
            earth = np.array((122, 92, 62), np.float32) / 255.0
            dark = earth * (1 - foot_dark)
            v = np.linspace(0, 1, max(1, fh))[:, None, None]
            img[py0:py0 + fh, px0:px1] = rim * (1 - v) + dark * v
            img[py0:py1, px0:px0 + fw] = earth * (1 - min(0.95, 0.35 + 0.15 * (depth + 1)))
            img[py0:py1, px1 - fw:px1] = earth
    # scorched before: vanilla ash filth specks only
    if state == "scorched" and not after:
        rng = random.Random(3)
        for _ in range(140):
            x = rng.uniform(px0, px1 - 3)
            y = rng.uniform(py0, py1 - 3)
            img[int(y):int(y) + 3, int(x):int(x) + 3] = (0.55, 0.55, 0.55)
    if state == "scorched" and after:
        # soot halo on the lip, fading out 0.35 cells
        halo = int(0.35 * PX)
        for k in range(halo):
            f = 1 - 0.55 * (1 - k / halo)
            img[py0 - k - 1, px0 - k:px1 + k] *= f
            img[py1 + k, px0 - k:px1 + k] *= f
            img[py0 - k:py1 + k, px0 - k - 1] *= f
            img[py0 - k:py1 + k, px1 + k] *= f
    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    # a person standing in the middle of the south pit row, sunk by depth
    d = ImageDraw.Draw(out, "RGBA")
    pcx = (PIT_X0 + 1.5) * PX
    prow = PIT_R1 - 1
    sink = SINK * depth
    feet = (prow + 0.5 + 0.45 + sink) * PX
    top = feet - 1.0 * PX
    pawn = Image.new("RGBA", out.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(pawn)
    pd.ellipse([pcx - 0.28 * PX, top + 0.38 * PX, pcx + 0.28 * PX, feet], fill=(150, 60, 50, 255), outline=(20, 15, 10, 255), width=2)
    pd.ellipse([pcx - 0.22 * PX, top, pcx + 0.22 * PX, top + 0.44 * PX], fill=(228, 190, 160, 255), outline=(20, 15, 10, 255), width=2)
    if state in ("water", "oil", "slime", "tar") and after:
        # V wake behind a wading pawn (water-like liquids; tar/slime barely)
        strength = {"water": 1.0, "oil": 0.6, "slime": 0.3, "tar": 0.15}[state]
        ph = frame / FRAMES
        for k in range(3):
            r = (0.25 + 0.35 * ((ph + k / 3) % 1.0)) * PX
            alpha = int(150 * strength * (1 - ((ph + k / 3) % 1.0)))
            cy = (prow + 0.5) * PX - 0.1 * PX
            d.line([pcx - r * 1.6, cy - r * 0.2, pcx - 0.15 * PX, cy + 0.1 * PX], fill=(235, 245, 255, alpha), width=2)
            d.line([pcx + 0.15 * PX, cy + 0.1 * PX, pcx + r * 1.6, cy - r * 0.2], fill=(235, 245, 255, alpha), width=2)
    if after:
        # the near (south) lip hides whatever hangs below the pit's south edge
        lip_y = PIT_R1 * PX
        mask = Image.new("L", out.size, 255)
        md = ImageDraw.Draw(mask)
        md.rectangle([0, lip_y, out.size[0], out.size[1]], fill=int(255 * 0.15))   # 85 % opaque lip
        pawn.putalpha(Image.fromarray(np.minimum(np.asarray(pawn.split()[3]), np.asarray(mask))))
    out = Image.alpha_composite(out.convert("RGBA"), pawn).convert("RGB")
    return out


def label(im, text):
    pad = Image.new("RGB", (im.width, im.height + 26), (34, 26, 20))
    pad.paste(im, (0, 26))
    ImageDraw.Draw(pad).text((6, 6), text, fill=(240, 226, 200))
    return pad


def strip(material, state, after, look_frames=True):
    nframes = FRAMES if state in ("water", "tar", "oil", "slime") else 1
    frames = []
    for f in range(nframes):
        tiles = [label(draw_scene(material, d, state, after, f), f"D{d}") for d in range(1, 5)]
        row = Image.new("RGB", (sum(t.width for t in tiles) + 3 * 6, tiles[0].height), (34, 26, 20))
        x = 0
        for t in tiles:
            row.paste(t, (x, 0))
            x += t.width + 6
        frames.append(row)
    return frames


def save(frames, name):
    p = os.path.join(HERE, name)
    if len(frames) == 1:
        frames[0].save(p.replace(".gif", ".png"))
        return os.path.basename(p.replace(".gif", ".png"))
    frames[0].save(p, save_all=True, append_images=frames[1:], duration=200, loop=0, optimize=True)
    return os.path.basename(p)


def main():
    made = []
    for material in ("dirt", "stone"):
        for state in ("dry", "water", "tar", "scorched"):
            for after in (False, True):
                tag = "after" if after else "before"
                made.append(save(strip(material, state, after), f"{state}_{material}_{tag}.gif"))
    # other liquids, after only, D3 dirt
    for lk in ("oil", "slime"):
        made.append(save(strip("dirt", lk, True), f"{lk}_dirt_after.gif"))
    for m in made:
        print("WROTE", m)


if __name__ == "__main__":
    sys.exit(main())
