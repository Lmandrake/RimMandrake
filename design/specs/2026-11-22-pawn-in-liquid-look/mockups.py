#!/usr/bin/env python3
"""Offline mockups for design.md (RIMMANDRAKE_DESIGN_PAWN_IN_LIQUID_LOOK_WATER_SHEET_IS_A_MISTAKE).

Builds a colonist from vanilla pawn textures (body, shirt, head, hair), and draws her standing and lying in water
and in tar under each concept. Nothing here is game code. Usage: mockups.py <texture dir> <his capture dir> <out dir>
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

TEX, CAP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
S = 256                     # work pixels per map cell
PANEL = 2.6                 # panel side, cells
P = int(PANEL * S)
CLOSE, FAR = 150, 56        # shown pixels per cell: close zoom and default zoom
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

LIQ = {
    "water": dict(rgb=(22, 40, 74), seen=0.42, opaque=False, ring=(175, 205, 240), coat=(60, 80, 110)),
    "tar": dict(rgb=(19, 17, 15), seen=0.0, opaque=True, ring=(96, 90, 84), coat=(20, 18, 16)),
}


def tex(name, tint):
    im = Image.open(os.path.join(TEX, name + ".png")).convert("RGBA").resize((int(1.5 * S),) * 2, Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    a[..., :3] *= np.array(tint, np.float32)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def pawn():
    """The colonist's own picture, facing south, on a 2-cell canvas. Returns the image and the canvas rows of her
    feet, waist and head top."""
    c = Image.new("RGBA", (2 * S, 2 * S), (0, 0, 0, 0))
    o = (2 * S - int(1.5 * S)) // 2
    head = int(0.34 * S)
    c.alpha_composite(tex("Naked_Female_south", (1.0, 0.86, 0.76)), (o, o + head // 2))
    c.alpha_composite(tex("ShirtBasic_Female_south", (0.52, 0.76, 0.86)), (o, o + head // 2))
    c.alpha_composite(tex("Female_Average_Normal_south", (1.0, 0.86, 0.76)), (o, o - head // 2))
    c.alpha_composite(tex("Bob_south", (0.36, 0.27, 0.22)), (o, o - head // 2))
    k = 1.5 * S / 128
    feet = int(o + head // 2 + 113 * k)
    waist = int(o + head // 2 + 68 * k)
    return c, feet, waist


def soil(w, h, seed=3):
    src = Image.open(os.path.join(CAP, "station33_water_sheet_misaligned_on_colonist.png")).convert("RGB")
    patch = src.crop((610, 20, 780, 190)).resize((260, 260), Image.LANCZOS)
    tile = Image.new("RGB", (520, 520))
    tile.paste(patch, (0, 0))
    tile.paste(patch.transpose(Image.FLIP_LEFT_RIGHT), (260, 0))
    tile.paste(tile.crop((0, 0, 520, 260)).transpose(Image.FLIP_TOP_BOTTOM), (0, 260))
    out = Image.new("RGB", (w, h))
    for y in range(0, h, 520):
        for x in range(0, w, 520):
            out.paste(tile, (x, y))
    return out.convert("RGBA")


def noise(w, h, scale, seed):
    rnd = np.random.RandomState(seed)
    small = Image.fromarray((rnd.rand(max(2, h // scale), max(2, w // scale)) * 255).astype(np.uint8))
    return np.asarray(small.resize((w, h), Image.BICUBIC)).astype(np.float32) / 255.0


def surface(liq, seed=5):
    """The liquid's surface for one panel's pit."""
    L = LIQ[liq]
    base = np.zeros((P, P, 4), np.float32)
    base[..., :3] = L["rgb"]
    base[..., 3] = 255
    n = noise(P, P, 40, seed)
    if liq == "water":
        base[..., :3] += (n[..., None] - 0.5) * 10
    else:
        streak = np.asarray(Image.fromarray((noise(P, P, 90, seed + 1) * 255).astype(np.uint8))
                            .resize((P, P)).filter(ImageFilter.GaussianBlur(18))).astype(np.float32) / 255.0
        gloss = np.clip(1 - np.abs(streak - 0.5) * 60, 0, 1)
        base[..., :3] += gloss[..., None] * 16 + (n[..., None] - 0.5) * 4
    return Image.fromarray(base.clip(0, 255).astype(np.uint8))


def scene(liq, dry=False):
    """Ground with a 2.1-cell pit of liquid in the middle (or dry ground). Returns the image and the pit box."""
    g = soil(P, P)
    if dry:
        return g, None
    m = int((PANEL - 2.1) / 2 * S)
    box = (m, m, P - m, P - m)
    d = ImageDraw.Draw(g)
    d.rectangle((box[0] - 10, box[1] - 10, box[2] + 10, box[3] + 10), fill=(38, 28, 20, 255))
    g.paste(surface(liq).crop(box), box)
    wall = Image.new("RGBA", (box[2] - box[0], int(0.16 * S)), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wall)
    for y in range(wall.size[1]):
        wd.line((0, y, wall.size[0], y), fill=(120, 96, 74, int(230 * (1 - y / wall.size[1]) ** 0.7)))
    g.alpha_composite(wall, (box[0], box[1]))
    return g, box


def blend_to(img, rgb, k, dark=1.0):
    a = np.asarray(img).astype(np.float32)
    a[..., :3] = (a[..., :3] * (1 - k) + np.array(rgb, np.float32) * k) * dark
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def rows_mask(size, y0, y1=None, ragged=0, seed=1):
    """Alpha mask: 255 on rows y0..y1 (to the bottom when y1 is None). ragged > 0 gives the top edge teeth."""
    w, h = size
    m = np.zeros((h, w), np.uint8)
    edge = np.full(w, y0, np.float32)
    if ragged:
        edge += (noise(w, 1, 14, seed)[0] - 0.5) * 2 * ragged + (noise(w, 1, 5, seed + 3)[0] - 0.5) * ragged
    yy = np.arange(h)[:, None]
    m[(yy >= edge[None, :]) & (yy < (y1 if y1 is not None else h))] = 255
    return Image.fromarray(m)


def cut(img, mask):
    a = img.copy()
    a.putalpha(ImageChops.multiply(img.getchannel("A"), mask))
    return a


def inner_mask(img, depth_px):
    """For a lying body: 255 where the pixel is deeper than depth_px inside the picture's outline (the high middle of
    a rounded body); the rim is the low part that a shallow liquid covers first."""
    a = img.getchannel("A").filter(ImageFilter.GaussianBlur(depth_px))
    return a.point(lambda v: 255 if v > 222 else 0).filter(ImageFilter.GaussianBlur(2))


def ring(size, cx, cy, rx, ry, rgb, alpha, width, half=None, blur=2.5):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    box = (cx - rx, cy - ry, cx + rx, cy + ry)
    if half == "front":
        d.arc(box, 0, 180, fill=rgb + (alpha,), width=width)
    elif half == "back":
        d.arc(box, 180, 360, fill=rgb + (alpha,), width=width)
    else:
        d.ellipse(box, outline=rgb + (alpha,), width=width)
    return im.filter(ImageFilter.GaussianBlur(blur))


def outline_band(img, grow, width, rgb, alpha, blur=3):
    """A band that follows the picture's own outline, `grow` px outside it: the liquid's lip round a body."""
    a = img.getchannel("A")
    big = a.filter(ImageFilter.GaussianBlur(grow)).point(lambda v: 255 if v > 30 else 0)
    small = a.filter(ImageFilter.GaussianBlur(max(1, grow - width))).point(lambda v: 255 if v > 60 else 0)
    band = ImageChops.subtract(big, small).filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", img.size, rgb + (0,))
    out.putalpha(band.point(lambda v: int(v * alpha / 255)))
    return out


def gloss(img, mask, strength=1.0, seed=2):
    """Wet highlights inside mask: a rim of light just inside the picture's upper-left edge, plus a few glints."""
    al = img.getchannel("A")
    inner = al.filter(ImageFilter.GaussianBlur(5)).point(lambda v: 255 if v > 215 else 0)
    rim = ImageChops.subtract(inner, ImageChops.offset(inner, 7, 7)).filter(ImageFilter.GaussianBlur(1.6))
    hi = np.asarray(rim).astype(np.float32) / 255.0 * 0.75
    g = noise(img.size[0], img.size[1], 16, seed)
    hi += np.clip((g - 0.90) * 10, 0, 1) * 0.6
    m = np.asarray(ImageChops.multiply(mask, al)).astype(np.float32) / 255.0
    out = np.zeros((img.size[1], img.size[0], 4), np.uint8)
    out[..., :3] = 255
    out[..., 3] = (np.clip(hi * strength, 0, 1) * m * 255).astype(np.uint8)
    return Image.fromarray(out).filter(ImageFilter.GaussianBlur(1.0))


def coat(img, mask, liq):
    """The picture with the liquid on it inside mask (its own pixels only, so it cannot be out of line)."""
    m = ImageChops.multiply(mask, img.getchannel("A"))
    if liq == "water":
        wet = blend_to(img, LIQ[liq]["coat"], 0.34, dark=0.80)
        sheen = gloss(img, mask, 0.55)
    else:
        lum = np.asarray(img.convert("L")).astype(np.float32)[..., None] / 255.0
        a = np.asarray(img).astype(np.float32)
        a[..., :3] = np.array(LIQ[liq]["coat"], np.float32) + (lum - 0.35).clip(0, 1) * 46
        wet = Image.fromarray(a.clip(0, 255).astype(np.uint8))
        sheen = gloss(img, mask, 0.62)
    out = img.copy()
    out.paste(wet, (0, 0), m)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.alpha_composite(sheen)
    out.alpha_composite(layer)
    return out


def ghost(img, liq, seed=4):
    """The drowned part as seen through a clear liquid: bent by the surface, dimmed, with light lines over it."""
    a = np.asarray(img).copy()
    h, w = a.shape[:2]
    out = np.zeros_like(a)
    for y in range(h):
        out[y] = np.roll(a[y], int(round(7 * math.sin(y / 11.0) + 3 * math.sin(y / 4.3))), axis=0)
    g = Image.fromarray(out)
    grey = Image.merge("RGBA", (*[g.convert("L")] * 3, g.getchannel("A")))
    g = Image.blend(g, grey, 0.35)
    g = blend_to(g, LIQ[liq]["rgb"], 0.50, dark=0.92)
    n1, n2 = noise(w, h, 22, seed), noise(w, h, 22, seed + 9)
    lines = np.clip(1 - np.abs(n1 - n2) * 14, 0, 1) ** 3
    ca = np.zeros((h, w, 4), np.uint8)
    ca[..., :3] = (200, 225, 255)
    ca[..., 3] = (lines * 135 * (np.asarray(g.getchannel("A")) / 255.0)).astype(np.uint8)
    g.alpha_composite(Image.fromarray(ca).filter(ImageFilter.GaussianBlur(1.5)))
    return g


def shadow(img, dx, dy, alpha):
    a = img.getchannel("A").filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * alpha))
    s = Image.new("RGBA", img.size, (0, 0, 0, 0))
    s.putalpha(a)
    return ImageChops.offset(s, dx, dy)


def bubbles(size, cx, cy, n, rgb, seed, spread=60):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = random.Random(seed)
    for _ in range(n):
        x, y, q = cx + r.uniform(-spread, spread), cy + r.uniform(-spread, spread), r.uniform(4, 11)
        d.ellipse((x - q, y - q, x + q, y + q), outline=rgb + (190,), width=3)
    return im.filter(ImageFilter.GaussianBlur(0.8))


def drips(size, cx, feet, liq, seed, trail=True):
    """On dry ground: drops under the body and wet prints behind it, in the liquid's colour."""
    rgb = (48, 44, 40) if liq == "water" else LIQ[liq]["coat"]
    al = 120 if liq == "water" else 235
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = random.Random(seed)
    d.ellipse((cx - 70, feet - 14, cx + 70, feet + 22), fill=rgb + (int(al * 0.55),))
    for _ in range(16):
        x, y, q = cx + r.uniform(-95, 95), feet + r.uniform(-18, 34), r.uniform(3, 9)
        d.ellipse((x - q, y - q * 0.7, x + q, y + q * 0.7), fill=rgb + (al,))
    if trail:
        for i in range(5):
            x = cx - 110 - i * 62
            y = feet + 6 + (14 if i % 2 else -14)
            k = 1 - i * 0.17
            d.ellipse((x - 26, y - 13, x + 26, y + 13), fill=rgb + (int(al * k),))
    return im.filter(ImageFilter.GaussianBlur(1.6))


def place(base, layer, cx, cy):
    base.alpha_composite(layer, (cx - layer.size[0] // 2, cy - layer.size[1] // 2))


def lying(pic):
    return pic.rotate(38, resample=Image.BICUBIC)


def render(concept, liq, state):
    """One panel. concept: cut | coat | surface | under | pick. state: stand | lie_shallow | lie_deep | after."""
    L = LIQ[liq]
    pic, feet, waist = pawn()
    g, box = scene(liq, dry=(state == "after"))
    cx, cy = P // 2, P // 2 + 10
    ox, oy = cx - pic.size[0] // 2, cy - pic.size[1] // 2
    full = Image.new("L", pic.size, 255)
    C = concept
    if state == "after":
        if C in ("coat", "pick"):
            m = rows_mask(pic.size, waist, ragged=16)
            if C == "pick" or True:
                g.alpha_composite(drips(g.size, cx, oy + feet, liq, 7))
            place(g, shadow(pic, 10, 8, 0.25), cx, cy)
            place(g, coat(pic, m, liq), cx, cy)
        elif C == "surface":
            g.alpha_composite(drips(g.size, cx, oy + feet, liq, 7))
            place(g, shadow(pic, 10, 8, 0.25), cx, cy)
            place(g, pic, cx, cy)
        else:
            place(g, shadow(pic, 10, 8, 0.25), cx, cy)
            place(g, pic, cx, cy)
        return g
    if state == "stand":
        above = cut(pic, ImageChops.invert(rows_mask(pic.size, waist)))
        below = cut(pic, rows_mask(pic.size, waist))
        row = np.asarray(pic.getchannel("A"))[waist]
        xs = np.nonzero(row > 40)[0]
        mx, rx = (xs[0] + xs[-1]) // 2 + ox, (xs[-1] - xs[0]) // 2
        wy = oy + waist
        if C == "coat":
            # the liquid on her own picture; the surface itself is untouched
            place(g, coat(pic, rows_mask(pic.size, waist), liq), cx, cy)
            return g
        if not L["opaque"]:
            if C in ("under", "pick"):
                place(g, shadow(below, 16, 22, 0.35), cx, cy)
                place(g, ghost(below, liq), cx, cy + 5)
            elif C == "cut":
                place(g, blend_to(below, L["rgb"], 1 - L["seen"], dark=0.95), cx, cy)
            elif C == "surface":
                place(g, blend_to(below, L["rgb"], 0.80), cx, cy)
        if C in ("cut", "under"):
            g.alpha_composite(ring(g.size, mx, wy, rx + 14, int(rx * 0.40), L["ring"], 200, 7, "back"))
        if C in ("surface", "pick"):
            if liq == "water":
                for k, al in ((1.9, 70), (2.7, 40)):
                    g.alpha_composite(ring(g.size, mx, wy + 6, int(rx * k), int(rx * k * 0.42), L["ring"], al, 5))
                g.alpha_composite(ring(g.size, mx, wy, rx + 18, int(rx * 0.44), (8, 16, 34), 150, 12, "back", 4))
                g.alpha_composite(ring(g.size, mx, wy, rx + 14, int(rx * 0.40), L["ring"], 210, 6, "back"))
            else:
                # tar: a furrow that has not closed behind her, and a rolled lip
                fur = Image.new("RGBA", g.size, (0, 0, 0, 0))
                fd = ImageDraw.Draw(fur)
                fd.polygon([(mx - rx, wy - 8), (mx + rx, wy - 8), (mx + rx * 0.5, box[1] + 30), (mx - rx * 0.5, box[1] + 30)],
                           fill=(7, 6, 5, 235))
                fd.line([(mx - rx, wy - 8), (mx - rx * 0.5, box[1] + 30)], fill=(92, 86, 80, 200), width=5)
                fd.line([(mx + rx, wy - 8), (mx + rx * 0.5, box[1] + 30)], fill=(60, 56, 52, 200), width=5)
                g.alpha_composite(fur.filter(ImageFilter.GaussianBlur(3)))
                g.alpha_composite(ring(g.size, mx, wy, rx + 20, int(rx * 0.46), (6, 5, 4), 230, 14, "back", 3))
                g.alpha_composite(ring(g.size, mx - 3, wy - 3, rx + 20, int(rx * 0.46), L["ring"], 230, 5, "back", 2))
        top = above
        if C == "pick":
            # a thin wet band just above the line: the liquid has climbed the cloth
            top = coat(above, rows_mask(pic.size, waist - 22, ragged=9), liq)
        place(g, top, cx, cy)
        if C in ("cut", "under"):
            g.alpha_composite(ring(g.size, mx, wy, rx + 14, int(rx * 0.40), L["ring"], 230, 7, "front"))
        if C in ("surface", "pick"):
            if liq == "water":
                g.alpha_composite(ring(g.size, mx, wy, rx + 14, int(rx * 0.40), L["ring"], 235, 6, "front"))
            else:
                g.alpha_composite(ring(g.size, mx, wy, rx + 20, int(rx * 0.46), (6, 5, 4), 235, 14, "front", 3))
                g.alpha_composite(ring(g.size, mx - 3, wy - 3, rx + 20, int(rx * 0.46), L["ring"], 235, 5, "front", 2))
        return g
    lp = lying(pic)
    if state == "lie_shallow":
        hi = inner_mask(lp, 17)                     # the part of her that is above a shallow liquid
        lo = ImageChops.invert(hi)
        if C == "coat":
            place(g, coat(lp, lo, liq), cx, cy)
            return g
        if not L["opaque"]:
            under = cut(lp, lo)
            if C in ("under", "pick"):
                place(g, shadow(lp, 8, 10, 0.3), cx, cy)
                place(g, ghost(under, liq), cx, cy + 2)
            else:
                place(g, blend_to(under, L["rgb"], 1 - L["seen"] if C == "cut" else 0.8), cx, cy)
        top = cut(lp, hi)
        if C in ("surface", "pick"):
            if liq == "water":
                lip = outline_band(top, 9, 7, L["ring"], 200)
                wide = outline_band(lp, 30, 6, L["ring"], 70, 5)
                place(g, wide, cx, cy)
            else:
                place(g, outline_band(top, 15, 13, (6, 5, 4), 235), cx, cy)
                lip = ImageChops.offset(outline_band(top, 13, 5, L["ring"], 220, 2), -3, -3)
            place(g, lip, cx, cy)
        elif C in ("cut", "under"):
            place(g, outline_band(top, 7, 5, L["ring"], 190), cx, cy)
        if C == "under" and L["opaque"]:
            # tar draped over her low parts: her own shape, in the tar's colour, lit like the tar
            place(g, coat(cut(lp, lo), full, liq), cx, cy)
        if C == "pick":
            top = coat(top, ImageChops.invert(inner_mask(lp, 27)), liq)
        place(g, top, cx, cy)
        return g
    # lie_deep: 2 m over a lying body
    hx, hy = cx - 62, cy - 78                         # over her head
    if L["opaque"]:
        if C == "coat":
            place(g, coat(lp, full, liq), cx, cy)
        elif C in ("surface", "pick", "under", "cut"):
            g.alpha_composite(ring(g.size, cx, cy, 120, 62, (6, 5, 4), 200, 16, None, 6))
            g.alpha_composite(ring(g.size, cx - 3, cy - 3, 120, 62, L["ring"], 150, 4, None, 2))
            g.alpha_composite(bubbles(g.size, hx, hy, 3 if C != "cut" else 2, (120, 112, 104), 11, 26))
        return g
    if C == "coat":
        place(g, coat(lp, full, liq), cx, cy)
        return g
    if C in ("under", "pick"):
        place(g, shadow(lp, 22, 30, 0.42), cx, cy)
        place(g, ghost(lp, liq), cx, cy)
    elif C == "cut":
        place(g, blend_to(lp, L["rgb"], 0.62, dark=0.95), cx, cy)
    elif C == "surface":
        place(g, blend_to(lp, L["rgb"], 0.85), cx, cy)
    if C in ("surface", "pick"):
        for k, al in ((34, 120), (58, 70), (84, 40)):
            g.alpha_composite(ring(g.size, hx, hy, k, int(k * 0.8), L["ring"], al, 4))
    if C != "coat":
        g.alpha_composite(bubbles(g.size, hx, hy, 5, (190, 215, 245), 12, 30))
    return g


STATES = [("stand", "standing, chest deep"), ("lie_shallow", "lying, 0.2 m of it"), ("lie_deep", "lying under 2 m"),
          ("after", "out on dry ground")]
CONCEPTS = [
    ("cut", "A  CUT AT THE LINE", "Her own picture is cut at the surface. Clear liquid: the lower part shows through it. "
     "Opaque liquid: the lower part is gone. A ring sits where she meets the surface."),
    ("coat", "B  THE TIDE MARK", "The liquid is painted on her own pixels, up to the highest line it reached, and she "
     "keeps it on dry ground until it is washed or wears off."),
    ("surface", "C  THE SURFACE ANSWERS", "She is drawn plain. The liquid moves round her: rings and a lip in water, a "
     "furrow that stays open in tar, and wet prints behind her on dry ground."),
    ("under", "D  THE BODY UNDER THE SURFACE", "The drowned part is drawn as it is seen through the liquid: bent, dim, "
     "with light lines and a shadow on the floor. In tar: her own shape, draped in tar."),
    ("pick", "THE PICK: A + D + C + B together", "Cut at the line, the body seen under a clear surface, the surface "
     "answering, and the tide mark kept afterwards."),
]


def shrink(im, ppc):
    n = int(im.size[0] * ppc / S)
    return im.resize((n, n), Image.LANCZOS)


def text(d, xy, s, size, fill=(235, 235, 235), bold=False):
    d.text(xy, s, font=ImageFont.truetype(FONTB if bold else FONT, size), fill=fill)


def concept_sheet(key, title, blurb):
    cp, fp = int(PANEL * CLOSE), int(PANEL * FAR)
    pad, head = 14, 96
    W = pad + 4 * (cp + pad)
    H = head + 2 * (cp + 34 + fp + 30) + pad
    sh = Image.new("RGB", (W, H), (26, 26, 28))
    d = ImageDraw.Draw(sh)
    text(d, (pad, 10), title, 30, bold=True)
    text(d, (pad, 52), blurb, 16, (200, 200, 200))
    text(d, (pad, 74), "OFFLINE MOCKUP from vanilla pawn textures. Not a game capture. Large: close zoom. Small: default zoom, true size.",
         13, (150, 150, 150))
    y = head
    for liq in ("water", "tar"):
        for i, (st, label) in enumerate(STATES):
            im = render(key, liq, st).convert("RGB")
            x = pad + i * (cp + pad)
            text(d, (x, y), f"{liq}: {label}", 17, bold=True)
            sh.paste(shrink(im, CLOSE), (x, y + 26))
            sh.paste(shrink(im, FAR), (x, y + 34 + cp))
            text(d, (x + fp + 8, y + 34 + cp + 4), "default zoom", 12, (150, 150, 150))
        y += cp + 34 + fp + 30
    sh.save(os.path.join(OUT, f"concept_{key}.png"), compress_level=0)
    return sh


def today_panels():
    a = Image.open(os.path.join(CAP, "station33_water_sheet_misaligned_on_colonist.png")).convert("RGB")
    b = Image.open(os.path.join(CAP, "stations28_33_white_frames_all_six.png")).convert("RGB")
    return a.crop((150, 380, 520, 750)), b.crop((795, 588, 965, 758))


def comparison():
    cols = [("water", "stand", "water, standing"), ("water", "lie_deep", "water, lying under 2 m"),
            ("tar", "stand", "tar, standing"), ("tar", "lie_shallow", "tar, lying in 0.2 m"),
            ("tar", "after", "tar, out on dry ground")]
    cp, fp = int(PANEL * 112), int(PANEL * FAR)
    pad, left, head = 12, 250, 92
    W = left + len(cols) * (cp + pad) + pad
    rowh = cp + pad
    H = head + (len(CONCEPTS) + 1) * rowh + fp + 60
    sh = Image.new("RGB", (W, H), (26, 26, 28))
    d = ImageDraw.Draw(sh)
    text(d, (pad, 8), "A colonist in a FlowWorks liquid: today, four concepts, and the pick", 26, bold=True)
    text(d, (pad, 42), "Rows 2 to 6 are OFFLINE MOCKUPS from vanilla pawn textures. Row 1 is his capture of 2026-11-22.", 14,
         (160, 160, 160))
    for i, (_, _, lab) in enumerate(cols):
        text(d, (left + i * (cp + pad), head - 20), lab, 15, bold=True)
    y = head
    lie, stand = today_panels()
    text(d, (pad, y + 8), "TODAY", 20, bold=True)
    text(d, (pad, y + 38), "A small generic head-and-\ntorso icon in the water's\ncolour, laid over her.\nNo tar capture exists.", 14,
         (200, 200, 200))
    sh.paste(stand.resize((cp, cp), Image.LANCZOS), (left, y))
    sh.paste(lie.resize((cp, cp), Image.LANCZOS), (left + cp + pad, y))
    for i in (2, 3, 4):
        x = left + i * (cp + pad)
        d.rectangle((x, y, x + cp, y + cp), outline=(70, 70, 70))
        text(d, (x + 14, y + cp // 2 - 8), "no capture", 14, (120, 120, 120))
    y += rowh
    pick_row = None
    for key, title, blurb in CONCEPTS:
        text(d, (pad, y + 8), title.split("  ")[0] if key != "pick" else "THE PICK", 20, bold=True)
        words, line, lines = (title.split("  ", 1)[-1] + ". " + blurb).split(), "", []
        for w in words:
            if len(line) + len(w) > 28:
                lines.append(line)
                line = ""
            line += w + " "
        lines.append(line)
        text(d, (pad, y + 38), "\n".join(lines[:13]), 13, (200, 200, 200))
        ims = []
        for i, (liq, st, _) in enumerate(cols):
            im = render(key, liq, st).convert("RGB")
            ims.append(im)
            sh.paste(shrink(im, 112), (left + i * (cp + pad), y))
        if key == "pick":
            pick_row = ims
        y += rowh
    text(d, (pad, y + 8), "THE PICK at default zoom,\ntrue size", 14, (200, 200, 200))
    for i, im in enumerate(pick_row):
        sh.paste(shrink(im, FAR), (left + i * (cp + pad), y + 6))
    sh.save(os.path.join(OUT, "comparison_sheet.png"), compress_level=0)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for key, title, blurb in CONCEPTS:
        concept_sheet(key, title, blurb)
    comparison()
    print("wrote", sorted(os.listdir(OUT)))
