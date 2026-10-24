#!/usr/bin/env python3
"""Top-down sprinkler heads, one per pipe look, cut from that look's pump hub (SPRINKLER_HEAD_REDRAW_SEEN_FROM_ABOVE).

Owner 2026-10-24: "I think the sprinkler should be shown as viewed from above though to avoid the constant pipe fitting
problems. Like the pump is viewed."

A head seen from above is a round, centred, four-fold symmetric part, so the same drawing sits on any pipe cell (straight,
elbow, end, tee, cross) with no side-view clamp to line up: drawOffset (0,0,0), RM_PipeSeatMath still moves it onto an
elbow's arc. Each look's head is that look's pump (RM_LiquidPump textures, the owner's "like the pump") reduced to its round
hub: the hub disc with its four bolts, its fan grille replaced by a sprinkler's face -- a recessed plate, a ring of six
large spray nozzles (light rims, wet blue-dark bores) and the pump's own centre boss as the rotor cap. The plate is the
hub's median colour, except where a naive judge found the head lost its look (2026-10-24 r1, r2): the Scrapper pump hub
is plain grey, so its whole disc is toned to its own pipe's copper (luminance kept); Industrial's plate is lifted a value
step and its nozzles ringed in brass (gunmetal on gunmetal read as a drain cover); Modern's plate is darkened so the blue
plate and the blue rim separate.

    python3 top_heads.py <out_dir>     # <out_dir>/<Look>/RM_SprinklerHead.png (256 px canvas, drawSize 1) + preview.png
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
TEX = HERE.parent.parent / "Textures"
PUMP = {"Scrapper": "Things/Building/FlowWorks/Machinery/RM_LiquidPump",
        "Industrial": "RimMandrake/FlowWorks/Pump/Industrial/RM_LiquidPump",
        "Modern": "RimMandrake/FlowWorks/Pump/Modern/RM_LiquidPump",
        "Futuristic": "RimMandrake/FlowWorks/Pump/Futuristic/RM_LiquidPump"}
LOOKS = tuple(PUMP)
CANVAS = 256
HUB_R = 100          # px of the 512 px pump: the round hub with its four bolts
GRILLE_R = 58        # px of the 512 px pump: the fan grille, replaced
BOSS_R = 21          # px of the 512 px pump: the centre cap, kept as the rotor
NOZZLES, NOZZLE_RING, NOZZLE_R = 5, 36, 12.5
TONE_TO_PIPE = {"Scrapper": "RimMandrake/FlowWorks/Pipe/Scrapper/UniversalPipe_Atlas"}
PLATE_LIFT = {"Industrial": 1.45, "Modern": 0.72}
NOZZLE_RIM = {"Industrial": (205, 168, 78)}     # brass
DIAMETER = 0.42      # cell: over three bore widths (bore 0.136), so the disc hides the joint under it on any cell


def _disc(n, r, cx=None, cy=None):
    cx = n / 2 if cx is None else cx
    cy = n / 2 if cy is None else cy
    y, x = np.mgrid[0:n, 0:n] + 0.5
    return np.hypot(x - cx, y - cy) <= r


def head(look, scale=4):
    """-> RGBA CANVAS x CANVAS: the look's top-down head, centred."""
    pump = Image.open(TEX / (PUMP[look] + ".png")).convert("RGBA")
    assert pump.size == (512, 512), (look, pump.size)
    if look in TONE_TO_PIPE:
        pp = np.asarray(Image.open(TEX / (TONE_TO_PIPE[look] + ".png")).convert("RGBA"), np.float32).reshape(-1, 4)
        tone = np.median(pp[pp[:, 3] > 200][:, :3], axis=0)
        pa = np.asarray(pump, np.float32).copy()
        lum = pa[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)
        ref = np.median(lum[pa[..., 3] > 200])
        pa[..., :3] = np.clip(lum[..., None] / max(ref, 1.0) * tone, 0, 255)
        pump = Image.fromarray(pa.astype(np.uint8), "RGBA")
    n = 2 * HUB_R + 8
    c0 = 256 - n // 2
    hub = np.asarray(pump.crop((c0, c0, c0 + n, c0 + n)), np.float32).copy()
    y, x = np.mgrid[0:n, 0:n] + 0.5
    rr = np.hypot(x - n / 2, y - n / 2)
    ring = (rr > GRILLE_R + 4) & (rr < HUB_R - 6)
    plate = np.median(hub[ring][:, :3], axis=0)
    plate = np.clip(plate * PLATE_LIFT.get(look, 1.0), 0, 255)
    # the recessed sprinkler face: the hub's median, darker toward the north-west rim (lit from the south-east, as the pump)
    ang = np.arctan2(y - n / 2, x - n / 2)
    shade = 0.78 + 0.14 * np.cos(ang - math.pi / 4) * np.clip(rr / GRILLE_R, 0, 1)
    face = rr <= GRILLE_R
    hub[face, :3] = plate * shade[face, None]
    hub[face, 3] = 255
    lip = (rr > GRILLE_R - 2.5) & (rr <= GRILLE_R + 1.5)
    hub[lip, :3] = plate * 0.45
    boss_src = np.asarray(pump.crop((256 - BOSS_R - 2, 256 - BOSS_R - 2, 256 + BOSS_R + 2, 256 + BOSS_R + 2)), np.float32)
    im = Image.fromarray(np.clip(hub, 0, 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(im)
    for k in range(NOZZLES):
        a = 2 * math.pi * k / NOZZLES - math.pi / 2
        nx, ny = n / 2 + NOZZLE_RING * math.cos(a), n / 2 + NOZZLE_RING * math.sin(a)
        rim = NOZZLE_RIM.get(look) or tuple(int(v) for v in np.clip(plate * 1.35 + 45, 0, 255))
        rim = tuple(rim) + (255,)
        d.ellipse((nx - NOZZLE_R - 2, ny - NOZZLE_R - 2, nx + NOZZLE_R + 2, ny + NOZZLE_R + 2), fill=rim)
        d.ellipse((nx - NOZZLE_R, ny - NOZZLE_R, nx + NOZZLE_R, ny + NOZZLE_R), fill=(18, 34, 52, 255))
        d.ellipse((nx - 5, ny - 5.5, nx + 1.5, ny + 0.5), fill=(120, 175, 215, 255))   # a wet glint
    a = np.asarray(im, np.float32).copy()
    b = boss_src.shape[0]
    bm = _disc(b, BOSS_R + 0.5)
    s = n // 2 - b // 2
    a[s:s + b, s:s + b][bm] = boss_src[bm]
    # the hub's own outline, then a dark rim so the disc reads against any pipe and ground
    outside = rr > HUB_R
    a[outside, 3] = 0
    edge = (rr > HUB_R - 3) & (rr <= HUB_R)
    a[edge, :3] *= 0.35
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    px = round(DIAMETER * CANVAS)
    im = im.resize((px * scale, px * scale), Image.LANCZOS).resize((px, px), Image.LANCZOS)
    out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    sh = Image.new("L", (px, px), 0)
    ImageDraw.Draw(sh).ellipse((0, 0, px - 1, px - 1), fill=90)
    o = (CANVAS - px) // 2
    shadow.paste(Image.new("RGBA", (px, px), (0, 0, 0, 255)), (o, o), sh)   # concentric: an offset shadow breaks the centring
    out.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(3)))
    out.alpha_composite(im, (o, o))
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    out = Path(argv[0] if argv else ".")
    tiles = []
    for look in LOOKS:
        im = head(look)
        (out / look).mkdir(parents=True, exist_ok=True)
        im.save(out / look / "RM_SprinklerHead.png")
        tiles.append(im)
    pv = Image.new("RGBA", (CANVAS * len(tiles), CANVAS), (70, 70, 70, 255))
    for i, t in enumerate(tiles):
        pv.alpha_composite(t, (i * CANVAS, 0))
    pv.save(out / "preview.png")
    print(out / "preview.png")


if __name__ == "__main__":
    main()
