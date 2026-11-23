"""Procedural mockups of the redesigned jetties and suspension bridges (offline options for the owner's pick; nothing here is
installed in the mod). RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD; design:
design/specs/2026-11-22-jetty-bridge-art/design.md.

What the drawing proves, and what the draw code must copy:
- ONE deck: the deck is drawn as one continuous strip from root to tip (or anchor to anchor). Plate seams, rivet lines and
  rail posts sit at positions that never fall on a cell boundary, the girders and rails run unbroken, and only the ROOT and
  TIP ends carry end detail. In game the strip is cut into root / mid / tip pieces (or a solo piece for a 1-square jetty),
  which join exactly because each is a slice of the same strip.
- Height reads the way RimWorld draws tall things: a post of height h is drawn rising h cells NORTH (up the screen) from
  its foot, and its shadow and every cable's shadow fall south-east by the height above ground. A taut cable from a post top
  to the deck tip therefore shows as a diagonal with a shadow that meets it at the tip.
- North/south is drawn from the same geometry, never by rotating a finished picture, so posts still rise north and
  shadows still fall south-east.
Rendered at SS x the target scale, then reduced (anti-aliasing)."""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import backdrop

SS = 2                     # supersampling
SUN = (0.42, 0.30)         # shadow offset per cell of height (east, south), in cells
DIRS = {"E": (1, 0), "W": (-1, 0), "N": (0, -1), "S": (0, 1)}

# ---------------------------------------------------------------- looks (looks.md: Scrapper / Industrial / Modern / Futuristic)
LOOKS = {
    "Scrapper": dict(base=(118, 108, 96), dark=(58, 52, 46), light=(170, 160, 146), rust=0.42, wear=0.5,
                     panels=[(96, 104, 72), (134, 76, 54), (142, 142, 136), (112, 94, 72), (84, 94, 98), (150, 120, 70)],
                     accent=(168, 104, 52), cable=(70, 60, 50), cable_hi=(160, 134, 100), rail=(120, 100, 80), glow=None,
                     concrete=(140, 134, 124)),
    "Industrial": dict(base=(82, 88, 94), dark=(40, 44, 49), light=(146, 152, 158), rust=0.07, wear=0.3,
                       panels=[(82, 88, 94), (92, 97, 101), (150, 140, 118), (88, 92, 66)],
                       accent=(214, 168, 30), cable=(52, 55, 60), cable_hi=(170, 176, 182), rail=(70, 76, 82), glow=None,
                       concrete=(148, 146, 140)),
    "Modern": dict(base=(164, 168, 166), dark=(92, 96, 98), light=(214, 216, 214), rust=0.015, wear=0.25,
                   panels=[(164, 168, 166), (84, 112, 88), (150, 152, 150)],
                   accent=(214, 182, 52), cable=(176, 180, 184), cable_hi=(236, 238, 240), rail=(214, 182, 52), glow=None,
                   concrete=(182, 178, 170)),
    "Futuristic": dict(base=(226, 229, 232), dark=(46, 50, 56), light=(250, 251, 252), rust=0.0, wear=0.05,
                       panels=[(226, 229, 232), (210, 214, 218)],
                       accent=(80, 222, 255), cable=(54, 58, 64), cable_hi=(160, 170, 182), rail=(200, 206, 212),
                       glow=(80, 222, 255), concrete=(220, 222, 224)),
}


# ---------------------------------------------------------------- small helpers
def rng(seed):
    return np.random.default_rng(seed)


def vnoise(h, w, cell, seed, octaves=3):
    """Value noise in [-1, 1], h x w."""
    out = np.zeros((h, w))
    amp, tot = 1.0, 0.0
    r = rng(seed)
    for o in range(octaves):
        c = max(2, int(cell / (2 ** o)))
        g = r.random((h // c + 2, w // c + 2))
        im = Image.fromarray((g * 255).astype(np.uint8)).resize(((w // c + 2) * c, (h // c + 2) * c), Image.BICUBIC)
        out += amp * (np.asarray(im)[:h, :w] / 127.5 - 1)
        tot += amp
        amp *= 0.5
    return out / tot


def fill(h, w, col, var, seed, cell=24):
    n = vnoise(h, w, cell, seed)
    a = np.zeros((h, w, 3))
    for k in range(3):
        a[..., k] = col[k] * (1 + var * n)
    return a


def blend(a, col, mask):
    m = np.clip(mask, 0, 1)[..., None]
    return a * (1 - m) + np.array(col)[None, None, :] * m


def shade(a, f, mask=None):
    if mask is None:
        return a * f
    m = np.clip(mask, 0, 1)[..., None]
    return a * (1 - m) + a * f * m


def to_img(rgb, alpha):
    a = np.dstack([np.clip(rgb, 0, 255), np.clip(alpha, 0, 255)]).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def off_grid_positions(length_cells, P, seed, spacing=(0.42, 0.75), guard=0.1):
    """Transverse seam positions along a deck, in px: irregular, never within `guard` cells of a cell boundary (the rule
    that keeps the cell grid out of the picture)."""
    r = random.Random(seed)
    out, x = [], r.uniform(*spacing)
    while x < length_cells - 0.15:
        frac = x - math.floor(x)
        if guard < frac < 1 - guard:
            out.append(int(x * P))
        x += r.uniform(*spacing)
    return out


# ---------------------------------------------------------------- deck surfaces (local frame: x root -> tip, y across)
def surface(kind, L, W, look, seed, spec):
    """RGB array W x L of the deck's walking surface, before edges and ends."""
    lk = LOOKS[look]
    P = W
    base = spec.get("deck_col") or lk["base"]
    if kind == "diamond":
        a = fill(W, L, base, 0.10, seed)
        step = max(6, P // 9)
        yy, xx = np.mgrid[0:W, 0:L]
        cx = (xx % step) - step / 2
        cy = (yy % step) - step / 2
        flip = ((xx // step + yy // step) % 2) * 2 - 1
        bar = np.abs(cx * flip - cy) < step * 0.12
        bar &= (np.abs(cx) < step * 0.34) & (np.abs(cy) < step * 0.34)
        a = shade(a, 1.28, bar)
        sh = np.roll(bar, (1, 1), (0, 1)) & ~bar
        a = shade(a, 0.72, sh)
    elif kind in ("grating", "galvgrating"):
        hole = np.array((26, 22, 18)) if kind == "grating" else np.array((30, 26, 22))
        a = np.ones((W, L, 3)) * hole
        bars = max(4, P // 14)
        yy, xx = np.mgrid[0:W, 0:L]
        bearing = (yy % bars) < max(2, bars * 0.36)
        cross = (xx % (bars * 4)) < max(2, bars * 0.3)
        metal = fill(W, L, base, 0.12, seed)
        m = bearing | cross
        a[m] = metal[m]
        a = shade(a, 1.25, (yy % bars) == 0)
    elif kind == "plate":
        a = fill(W, L, base, 0.12, seed)
        rib = max(10, P // 6)
        xx = np.arange(L)[None, :].repeat(W, 0)
        a = shade(a, 1.15, (xx % rib) < 2)
        a = shade(a, 0.80, (xx % rib) == 2)
    elif kind == "concrete":
        col = spec.get("concrete_col") or lk["concrete"]
        a = fill(W, L, col, 0.07, seed, cell=40)
        r = rng(seed + 1)
        spk = r.random((W, L))
        a = shade(a, 0.78, spk > 0.985)
        a = shade(a, 1.12, spk < 0.012)
        stain = vnoise(W, L, P // 2, seed + 7) > 0.35
        a = shade(a, 0.86, stain * 0.7)
    elif kind == "concrete_panels":
        a = surface("concrete", L, W, look, seed, spec)
    elif kind == "corrugated":
        a = np.zeros((W, L, 3))
        cols = lk["panels"] if look != "Scrapper" else [(128, 62, 46), (64, 86, 112), (126, 122, 104), (96, 104, 72)]
        xs = [0] + off_grid_positions(L / P, P, seed, (0.55, 1.0)) + [L]
        r = random.Random(seed)
        for x0, x1 in zip(xs, xs[1:]):
            a[:, x0:x1] = fill(W, x1 - x0, r.choice(cols), 0.12, seed + x0)
        yy = np.arange(W)[:, None].repeat(L, 1)
        wave = np.sin(yy / max(3, P / 12) * math.pi)
        a = a * (1 + 0.16 * wave[..., None])
    elif kind == "patchwork":
        a = fill(W, L, lk["base"], 0.1, seed)
        r = random.Random(seed)
        for _ in range(int(L / P * 7)):
            pw, ph = int(r.uniform(0.22, 0.6) * P), int(r.uniform(0.25, 0.7) * W)
            x0, y0 = r.randrange(0, max(1, L - pw)), r.randrange(0, max(1, W - ph))
            col = r.choice(lk["panels"])
            a[y0:y0 + ph, x0:x0 + pw] = fill(ph, pw, col, 0.12, r.randrange(9999))
            a[y0:y0 + ph, x0:x0 + 2] *= 0.6
            a[y0:y0 + 2, x0:x0 + pw] *= 1.18
            for k in range(x0 + 6, x0 + pw - 4, max(8, P // 10)):
                for yy in (y0 + 5, y0 + ph - 6):
                    a[max(0, yy - 1):yy + 2, k - 1:k + 2] = (60, 54, 48)
    elif kind == "hull":
        a = fill(W, L, spec.get("deck_col") or (70, 88, 72), 0.12, seed)
        xs = off_grid_positions(L / P, P, seed, (0.5, 0.8))
        for x in xs:
            a[:, x:x + 3] *= 0.55
            a[:, x + 3:x + 5] *= 1.2
            for yy in range(6, W - 4, max(8, P // 11)):
                a[yy - 1:yy + 2, x - 6:x - 3] = (48, 44, 40)
        chip = vnoise(W, L, P // 5, seed + 3) > 0.3
        a = blend(a, (128, 112, 96), chip * 0.8)
    elif kind == "antislip":
        a = fill(W, L, base, 0.06, seed, cell=60)
        r = rng(seed + 5)
        g = r.random((W, L))
        a = shade(a, 0.82, g > 0.8)
        a = shade(a, 1.1, g < 0.08)
        yy = np.arange(W)[:, None].repeat(L, 1)
        path = np.exp(-((yy - W / 2) / (W * 0.18)) ** 2)
        a = shade(a, 1.08, path * 0.8)          # the worn walking line down the middle
    elif kind == "composite":
        a = fill(W, L, base, 0.025, seed, cell=80)
    elif kind == "glass":
        a = np.ones((W, L, 3)) * np.array((60, 84, 92))
        yy, xx = np.mgrid[0:W, 0:L]
        a = shade(a, 1.5, ((xx + yy) % (P // 2)) < P // 14)
    else:
        raise ValueError(kind)
    return a


def edges_and_ends(a, L, W, look, spec, seed, ends):
    """Girders down both sides, transverse seams (off the cell grid), the root and tip ends. Returns (rgb, alpha)."""
    lk = LOOKS[look]
    P = W
    dw = spec.get("deck_w", 0.8)
    top, bot = int((1 - dw) / 2 * W), int((1 + dw) / 2 * W)
    alpha = np.zeros((W, L))
    alpha[top:bot] = 255
    if spec.get("deck") in ("grating", "galvgrating"):
        holes = a.sum(2) < 100
        alpha[holes & (alpha > 0)] = 215          # the pit shows through the grating
    if spec.get("deck") == "glass":
        alpha[top:bot] = 140
    # seams across the deck, never on a cell boundary
    if spec.get("seams", True) and spec.get("deck") not in ("grating", "galvgrating", "glass", "corrugated", "patchwork"):
        for x in off_grid_positions(L / P, P, seed + 11, spec.get("seam_spacing", (0.45, 0.8))):
            a[top:bot, x:x + 2] *= 0.62
            a[top:bot, x + 2:x + 3] *= 1.15
            if spec.get("rivets"):
                for yy in range(top + 6, bot - 4, max(8, P // 10)):
                    a[yy - 1:yy + 2, x - 5:x - 2] = lk["dark"]
                    a[yy - 1, x - 5:x - 2] = lk["light"]
    if look == "Futuristic" and spec.get("deck") == "composite":
        for x in off_grid_positions(L / P, P, seed + 3, (0.9, 1.3)):
            a[top:bot, x:x + 1] *= 0.86
    # girders / edge members
    g = spec.get("girder", "ibeam")
    gw = int(spec.get("girder_w", 0.08) * P)
    gcol = spec.get("girder_col") or lk["dark"]
    for side in (0, 1):
        y0 = top - gw // 2 if side == 0 else bot - gw + gw // 2
        y0 = max(0, y0)
        y1 = min(W, y0 + gw)
        if g == "none" or gw <= 0:
            continue
        alpha[y0:y1] = 255
        if g == "truss":
            gcol = spec.get("girder_col") or tuple(int(v * 0.85) for v in lk["light"])
            a[y0:y1] = fill(y1 - y0, L, gcol, 0.08, seed + side)
            a[y0:y1] *= 0.5                     # the gap between the truss chords reads dark
            a[y0:y0 + 3] = np.array(gcol) * 1.25
            a[y1 - 3:y1] = np.array(gcol) * 0.95
            step = int(0.33 * P)
            for x in range(0, L, step):
                for t in range(step):
                    yy = y0 + int((t / step if (x // step) % 2 == 0 else 1 - t / step) * (y1 - y0 - 1))
                    if x + t < L:
                        a[max(y0, yy - 1):min(y1, yy + 2), x + t] = np.array(gcol) * 1.15
            alpha[y0 + 3:y1 - 3] = np.where(a[y0 + 3:y1 - 3].sum(2) > 3 * 0.6 * np.mean(gcol), 255, 120)
        else:
            a[y0:y1] = fill(y1 - y0, L, gcol, 0.08, seed + side, cell=30)
            if g in ("ibeam", "box", "angle"):
                a[y0:y0 + 2] = np.array(lk["light"]) * 0.9 if g != "angle" else np.array(gcol) * 1.5
                a[y1 - 2:y1] = np.array(gcol) * 0.6
                if g == "box":
                    a[y0 + 3:y1 - 3] *= 1.08
            if g == "trim":                       # futuristic: a slim graphite trim with a light strip
                if lk["glow"]:
                    mid = (y0 + y1) // 2
                    a[mid - 1:mid + 2] = lk["glow"]
            if spec.get("bolts", True) and g in ("ibeam", "box", "angle"):
                for x in range(int(0.12 * P), L, max(10, int(P * spec.get("bolt_pitch", 0.16)))):
                    yy = (y0 + y1) // 2
                    a[yy - 2:yy + 2, x - 2:x + 2] = np.array(gcol) * 0.5
                    a[yy - 2, x - 2:x + 1] = lk["light"]
        if spec.get("hazard_edge"):
            yy0, yy1 = (top + gw // 2 + 8, top + gw // 2 + 16) if side == 0 else (bot - gw // 2 - 16, bot - gw // 2 - 8)
            for x in range(L):
                a[yy0:yy1, x] = lk["accent"] if ((x // 10) % 2 == 0) else (30, 30, 30)
        if lk["glow"] and spec.get("glow_edge"):
            yy = top + 3 if side == 0 else bot - 5
            a[yy:yy + 3] = spec.get("glow_col") or lk["glow"]
    # ends
    for end, x0 in (("root", 0), ("tip", L)):
        kind = ends.get(end)
        if not kind:
            continue
        w = int((0.10 if kind in ("bumper", "hazard") else 0.06) * P)
        xs = slice(0, w) if end == "root" else slice(L - w, L)
        if kind == "joint":       # the expansion joint into the anchor: a steel angle with pins
            a[top:bot, xs] = np.array(lk["dark"]) * 1.1
            for yy in range(top + 8, bot - 6, max(10, P // 7)):
                a[yy - 2:yy + 2, (xs.start + xs.stop) // 2 - 2:(xs.start + xs.stop) // 2 + 2] = lk["light"]
        elif kind == "beam":
            a[top:bot, xs] = np.array(spec.get("girder_col") or lk["dark"]) * 1.15
            a[top:bot, xs.start:xs.start + 2] = lk["light"]
        elif kind in ("hazard", "bumper"):
            for yy in range(top, bot):
                for x in range(xs.start, xs.stop):
                    a[yy, x] = lk["accent"] if (((x + yy) // 9) % 2 == 0) else (28, 28, 28)
            if kind == "bumper":
                a[top:bot, xs.start:xs.start + 3] = (30, 30, 30)
        elif kind == "light":
            a[top:bot, xs] = lk["dark"]
            g_ = spec.get("glow_col") or lk["glow"] or (255, 255, 255)
            m = (xs.start + xs.stop) // 2
            a[top + 4:bot - 4, m - 1:m + 2] = g_
        alpha[top:bot, xs] = 255
        if end == "tip" and spec.get("lugs", True):
            for yy in (top + 4, bot - 10):
                a[yy:yy + 6, L - w - 8:L - w - 2] = np.array(lk["light"]) * 0.95
    return a, alpha


def wear(a, alpha, look, seed, spec):
    lk = LOOKS[look]
    W, L = a.shape[:2]
    if lk["rust"] > 0:
        n = vnoise(W, L, W // 3, seed + 21)
        streak = vnoise(W, L, W // 10, seed + 22)
        m = np.clip((n - (1 - 2 * lk["rust"])) * 3, 0, 1) * (0.6 + 0.4 * streak)
        a = blend(a, (124, 66, 34), m * 0.75)
    grime = vnoise(W, L, W // 2, seed + 30)
    a = shade(a, 1 - 0.18 * lk["wear"], np.clip(grime, 0, 1))
    if look == "Modern" and spec.get("touchup", True):
        r = random.Random(seed)
        for _ in range(int(L / W * 2)):
            pw, ph = int(r.uniform(0.15, 0.35) * W), int(r.uniform(0.1, 0.25) * W)
            x0, y0 = r.randrange(0, max(1, L - pw)), r.randrange(int(W * 0.15), int(W * 0.7))
            col = r.choice([(150, 154, 152), (128, 130, 126), (176, 178, 172)])
            yy, xx = np.mgrid[0:ph, 0:pw]
            m = np.clip(np.minimum(np.minimum(xx, pw - 1 - xx), np.minimum(yy, ph - 1 - yy)) / 6.0, 0, 1)
            m = (m * (0.5 + 0.5 * (vnoise(ph, pw, 8, x0 + y0) > -0.2)))[..., None] * 0.35    # soft-edged, uneven
            a[y0:y0 + ph, x0:x0 + pw] = a[y0:y0 + ph, x0:x0 + pw] * (1 - m) + np.array(col) * m
    return a


def railings(img_rgb, alpha, L, W, look, spec, seed):
    """Rails along both edges, one continuous line each; posts on an irregular pitch so none sits on a cell boundary."""
    lk = LOOKS[look]
    r = spec.get("rail")
    if not r:
        return img_rgb, alpha
    P = W
    dw = spec.get("deck_w", 0.8)
    top, bot = int((1 - dw) / 2 * W), int((1 + dw) / 2 * W)
    col = spec.get("rail_col") or lk["rail"]
    th = {"tube": 4, "heavy": 7, "rope": 3, "cable": 2, "glass": 3}.get(r, 4)
    for yy in (top + 2, bot - 2 - th):
        if r == "glass":
            img_rgb[yy - 3:yy + th + 3] = img_rgb[yy - 3:yy + th + 3] * 0.6 + np.array((170, 210, 225)) * 0.4
        img_rgb[yy:yy + th] = col
        img_rgb[yy:yy + 1] = np.minimum(np.array(col) * 1.35, 255)
        if r == "heavy":
            img_rgb[yy + th + 4:yy + th + 7] = np.array(col) * 0.9
        posts = [int(P * 0.12)] + [x + int(P * 0.08) for x in off_grid_positions(L / P, P, seed + 40, (0.36, 0.5), 0.12)]
        for x in posts:
            ps = th + 4
            img_rgb[yy - 2:yy + ps - 2, x:x + ps] = np.array(col) * 0.75
            img_rgb[yy - 2, x:x + ps] = np.minimum(np.array(col) * 1.4, 255)
    return img_rgb, alpha


def deck_image(n, look, spec, seed, ends, P):
    L, W = n * P, P
    a = surface(spec["deck"], L, W, look, seed, spec)
    a, alpha = edges_and_ends(a, L, W, look, spec, seed, ends)
    a = wear(a, alpha, look, seed, spec)
    a, alpha = railings(a, alpha, L, W, look, spec, seed)
    return to_img(a, alpha)


def orient(img, d):
    if d == "E":
        return img
    if d == "W":
        return img.rotate(180, expand=True)
    if d == "N":
        return img.rotate(90, expand=True)
    return img.rotate(-90, expand=True)


# ---------------------------------------------------------------- anchors (one cell, local frame: the deck leaves at +x)
def anchor_image(look, spec, seed, P):
    lk = LOOKS[look]
    kind = spec.get("anchor", "steelblock")
    a = np.zeros((P, P, 3))
    alpha = np.zeros((P, P))
    m = int(0.06 * P)
    if kind == "concrete":
        a[:] = surface("concrete", P, P, look, seed + 50, spec)
        a[m:P - m, m:P - m] *= 1.04
        a[m:m + 3, m:P - m] *= 1.2
        a[P - m - 3:P - m, m:P - m] *= 0.75
        alpha[:] = 255
        for (x, y) in ((0.2, 0.2), (0.2, 0.8), (0.55, 0.2), (0.55, 0.8)):
            cx, cy = int(x * P), int(y * P)
            a[cy - 5:cy + 5, cx - 5:cx + 5] = lk["dark"]
            a[cy - 2:cy + 2, cx - 2:cx + 2] = lk["light"]
        a[:, P - int(0.1 * P):] = np.array(spec.get("girder_col") or lk["dark"]) * 1.05      # steel bearing plate at the deck side
    elif kind == "scrap":
        a[:] = surface("patchwork", P, P, look, seed + 50, spec)
        alpha[m:P - m, m:P - m] = 255
    elif kind == "composite":
        a[:] = fill(P, P, lk["base"], 0.02, seed)
        alpha[m:P - m, m:P - m] = 255
        a[m:P - m, m:m + 4] = lk["dark"]
        if lk["glow"]:
            a[int(0.3 * P):int(0.7 * P), int(0.2 * P):int(0.2 * P) + 3] = spec.get("glow_col") or lk["glow"]
    else:
        a[:] = fill(P, P, spec.get("anchor_col") or lk["base"], 0.1, seed + 50)
        alpha[m:P - m, m:P - m] = 255
        a[m:m + 3, m:P - m] *= 1.25
        a[P - m - 3:P - m, m:P - m] *= 0.7
        for x in range(m + 8, P - m - 4, max(10, P // 8)):
            for y in (m + 7, P - m - 9):
                a[y - 2:y + 2, x - 2:x + 2] = lk["dark"]
    a = wear(a, alpha, look, seed + 60, {"touchup": False})
    return to_img(a, alpha)


# ---------------------------------------------------------------- the scene
class Scene(object):
    """One structure over the real pit, drawn at P = ppc * SS px per cell."""

    def __init__(self, cols, rows, pit_at, ns, ppc):
        self.P = ppc * SS
        self.ppc = ppc
        self.img = backdrop.scene(cols, rows, pit_at, ns, self.P)
        self.shadow = Image.new("L", self.img.size, 0)
        self.sd = ImageDraw.Draw(self.shadow)
        self.over = []          # (z, callable) drawn after the deck, sorted

    def px(self, c, r):
        return (c * self.P, r * self.P)

    def scr(self, p, h):
        """Screen point of world point p (px) at height h (cells): drawn h cells north."""
        return (p[0], p[1] - h * self.P)

    def shd(self, p, h):
        return (p[0] + SUN[0] * h * self.P, p[1] + SUN[1] * h * self.P)

    def paste(self, im, xy):
        self.img.alpha_composite(im, (int(xy[0]), int(xy[1])))

    def deck_shadow(self, box, h=0.35):
        x0, y0, x1, y1 = box
        dx, dy = SUN[0] * h * self.P, SUN[1] * h * self.P
        self.sd.rectangle([x0 + dx, y0 + dy, x1 + dx, y1 + dy], fill=150)

    def cable_shadow(self, p0, h0, p1, h1, w):
        self.sd.line([self.shd(p0, h0), self.shd(p1, h1)], fill=170, width=max(2, int(w)))

    def post_shadow(self, base, h, w):
        self.sd.line([self.shd(base, 0), self.shd(base, h)], fill=170, width=max(2, int(w)))

    def finish(self):
        sh = self.shadow.filter(ImageFilter.GaussianBlur(self.P * 0.03))
        dark = Image.new("RGBA", self.img.size, (10, 8, 6, 0))
        dark.putalpha(sh.point(lambda v: int(v * 0.55)))
        base = self.img.copy()
        base.alpha_composite(dark)
        self.img = base
        return self

    def result(self):
        return self.img.resize((self.img.width // SS, self.img.height // SS), Image.LANCZOS)


def draw_post(sc, d, base, h, w, look, kind, spec):
    """A post rising h cells north from base: a billboard, lit on its west face."""
    lk = LOOKS[look]
    x, y = base
    top = sc.scr(base, h)[1]
    col = {"concrete": lk["concrete"], "pipe": lk["cable_hi"], "composite": lk["dark"] if look == "Futuristic" else lk["base"]}.get(
        kind, spec.get("post_col") or lk["base"])
    if look == "Scrapper" and kind == "pipe":
        col = (110, 96, 80)
    x0, x1 = x - w / 2, x + w / 2
    n = 8
    for i in range(n):
        f = 1.25 - 0.55 * i / (n - 1)
        c = tuple(int(min(255, v * f)) for v in col)
        d.rectangle([x0 + (x1 - x0) * i / n, top, x0 + (x1 - x0) * (i + 1) / n, y], fill=c)
    if kind == "concrete":
        for k in range(1, 4):
            yy = y - (y - top) * k / 4
            d.line([x0, yy, x1, yy], fill=tuple(int(v * 0.8) for v in col), width=2)
    cap = tuple(int(min(255, v * 1.35)) for v in (lk["light"] if kind != "concrete" else lk["dark"]))
    d.rectangle([x0 - w * 0.15, top - w * 0.25, x1 + w * 0.15, top + w * 0.2], fill=cap)
    if lk["glow"] and spec.get("glow_nodes", True):
        g = spec.get("glow_col") or lk["glow"]
        d.ellipse([x - w * 0.22, top + w * 0.35, x + w * 0.22, top + w * 0.8], fill=g)
    if look == "Industrial" and spec.get("post_hazard", True):
        for k in range(4):
            yy = y - w * 0.4 * (k + 1)
            d.line([x0, yy, x1, yy - w * 0.25], fill=lk["accent"] if k % 2 == 0 else (25, 25, 25), width=max(2, int(w * 0.22)))


def draw_beam(sc, draw, t0, t1, pw, look, spec):
    lk = LOOKS[look]
    draw.line([t0, t1], fill=spec.get("post_col") or lk["dark"], width=int(pw * 0.8))
    draw.line([(t0[0], t0[1] - pw * 0.3), (t1[0], t1[1] - pw * 0.3)], fill=lk["light"], width=max(1, int(pw * 0.15)))


def draw_leg(sc, draw, f, at, pw, look, spec):
    lk = LOOKS[look]
    draw.line([f, at], fill=spec.get("post_col") or lk["dark"], width=int(pw * 0.7))
    draw.line([(f[0] - pw * 0.2, f[1]), (at[0] - pw * 0.2, at[1])], fill=lk["light"], width=max(1, int(pw * 0.15)))


def draw_cable(sc, d, p0, h0, p1, h1, w, look, spec, style=None):
    lk = LOOKS[look]
    style = style or spec.get("cable_style", "wire")
    a, b = sc.scr(p0, h0), sc.scr(p1, h1)
    col = spec.get("cable_col") or lk["cable"]
    hi = spec.get("cable_hi") or lk["cable_hi"]
    if style == "chain":
        L = math.dist(a, b)
        k = max(2, int(L / (w * 1.6)))
        for i in range(k):
            t = (i + 0.5) / k
            cx, cy = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            r = w * 0.75
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=max(2, int(w * 0.35)))
        return
    d.line([a, b], fill=col, width=max(2, int(w)))
    ox, oy = -0.25 * w, -0.25 * w
    d.line([(a[0] + ox, a[1] + oy), (b[0] + ox, b[1] + oy)], fill=hi, width=max(1, int(w * 0.38)))
    L = math.dist(a, b)
    step = max(4, w * 0.9)
    if style in ("wire", "rope"):
        sc_ = (0.55 if style == "wire" else 0.45)
        tcol = tuple(int(v * sc_) for v in col) if style == "wire" else tuple(int(v * 0.7) for v in hi)
        k = int(L / step)
        ux, uy = (b[0] - a[0]) / max(L, 1), (b[1] - a[1]) / max(L, 1)
        nx, ny = -uy, ux
        for i in range(k):
            t = i * step
            cx, cy = a[0] + ux * t, a[1] + uy * t
            d.line([(cx - nx * w * 0.45, cy - ny * w * 0.45), (cx + nx * w * 0.45 + ux * w * 0.4, cy + ny * w * 0.45 + uy * w * 0.4)],
                   fill=tcol, width=1)
    if lk["glow"] and spec.get("glow_nodes", True):
        g = spec.get("glow_col") or lk["glow"]
        for t in (0.33, 0.66):
            cx, cy = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            d.ellipse([cx - w * 0.5, cy - w * 0.5, cx + w * 0.5, cy + w * 0.5], fill=g)


def structure(sc, look, spec, seed, anchors, deck_cells, d, n, ends, human_at=None):
    """Draw anchors, deck, posts and cables. anchors: [(col, row, dir the deck leaves it)]; deck_cells: top-left cell of the
    deck's bounding box; d: deck direction from the first anchor; n: deck length in cells."""
    P = sc.P
    lk = LOOKS[look]
    dx, dy = DIRS[d]
    deck = orient(HOOKS["deck"](n, look, spec, seed, ends, P), d)
    bx, by = sc.px(*deck_cells)
    # the deck's own drop shadow goes UNDER the deck (on the pit and ledge), never over it
    under = Image.new("L", sc.img.size, 0)
    hdx, hdy = SUN[0] * 0.12 * P, SUN[1] * 0.12 * P
    ImageDraw.Draw(under).rectangle([bx + hdx, by + hdy, bx + deck.width + hdx, by + deck.height + hdy], fill=150)
    under = under.filter(ImageFilter.GaussianBlur(P * 0.03))
    ul = Image.new("RGBA", sc.img.size, (10, 8, 6, 0))
    ul.putalpha(under.point(lambda v: int(v * 0.55)))
    sc.img.alpha_composite(ul)
    for (c, r, ad) in anchors:
        sc.paste(orient(anchor_image(look, spec, seed + c * 7 + r, P), ad), sc.px(c, r))
    sc.paste(deck, (bx, by))
    # posts and cables
    sw = spec.get("deck_w", 0.8) / 2 * P
    posts = spec.get("posts", "twin")
    H = spec.get("post_h", 1.2)
    pw = spec.get("post_w", 0.09) * P
    cw = spec.get("cable_w", 0.05) * P
    draw = ImageDraw.Draw(sc.img)
    overs = []
    tops = []
    for (c, r, ad) in anchors:
        ax, ay = DIRS[ad]
        cx, cy = (c + 0.5) * P, (r + 0.5) * P
        edge = (cx + ax * 0.5 * P, cy + ay * 0.5 * P)
        nx, ny = -ay, ax
        inset = spec.get("post_inset", 0.16)
        foot = (edge[0] - ax * inset * P, edge[1] - ay * inset * P)
        side_off = sw + spec.get("post_out", 0.09) * P
        if posts in ("twin", "portal"):
            feet = [(foot[0] + nx * side_off * s, foot[1] + ny * side_off * s) for s in (-1, 1)]
            tops.append([(f, H, s) for f, s in zip(feet, (-1, 1))])
        elif posts == "aframe":
            apex = (foot[0] - ax * 0.05 * P, foot[1] - ay * 0.05 * P)
            feet = [(foot[0] + nx * side_off * s, foot[1] + ny * side_off * s) for s in (-1, 1)]
            tops.append([(apex, H, s) for s in (-1, 1)])
            overs.append(("aframe", feet, apex))
        elif posts == "pylon":
            tops.append([(foot, H, s) for s in (-1, 1)])
            feet = [foot]
        for f in feet:
            sc.post_shadow(f, H, pw)
        if posts != "aframe":
            overs.append(("posts", feet, None))
        if spec.get("backstay", True):
            back = (cx - ax * 0.42 * P, cy - ay * 0.42 * P)
            for (tp, h, s) in tops[-1]:
                bb = (back[0] + nx * side_off * s * 0.9, back[1] + ny * side_off * s * 0.9)
                overs.append(("cable", (tp, h, bb, 0.04), 0.8))
    # cables to the far end (jetty) or the main cable (bridge)
    if spec.get("bridge"):
        ax0 = 1 if d in ("E", "W") else 0          # the across-deck screen axis
        t0 = sorted(tops[0], key=lambda e: e[0][ax0])
        t1 = sorted(tops[1], key=lambda e: e[0][ax0])
        hmin = spec.get("sag_low", 0.22)
        for i in range(2):
            (pa, ha, s), (pb, hb, _) = t0[i], t1[i]
            # side point under the cable at parameter t along the deck edge
            pts = []
            K = 24
            for k in range(K + 1):
                t = k / K
                p = (pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t)
                h = ha - (ha - hmin) * 4 * t * (1 - t)
                pts.append((p, h))
            for (p, h), (q, g) in zip(pts, pts[1:]):
                overs.append(("cable", (p, h, q, g), 1.0))
            hk = spec.get("hanger_pitch", 0.5)
            m = int(n / hk)
            for k in range(1, m + 1):
                t = min(0.97, max(0.03, (k * hk + spec.get("post_inset", 0.16)) / (n + 2 * spec.get("post_inset", 0.16))))
                p = (pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t)
                h = ha - (ha - hmin) * 4 * t * (1 - t)
                # the hanger meets the deck edge (inside the post line)
                ax_, ay_ = DIRS[anchors[0][2]]
                nx_, ny_ = -ay_, ax_
                q = (p[0] - nx_ * spec.get("post_out", 0.09) * P * s, p[1] - ny_ * spec.get("post_out", 0.09) * P * s)
                overs.append(("cable", (p, h, q, 0.06), spec.get("hanger_w", 0.45)))
    else:
        ax, ay = DIRS[anchors[0][2]]
        nx, ny = -ay, ax
        cx, cy = (anchors[0][0] + 0.5) * P, (anchors[0][1] + 0.5) * P
        root = (cx + ax * 0.5 * P, cy + ay * 0.5 * P)
        targets = [n - 0.1] if spec.get("fan", 1) == 1 or n == 1 else [n * 0.5, n - 0.1]
        for (tp, h, s) in tops[0]:
            for L_ in targets:
                q = (root[0] + ax * L_ * P + nx * sw * 0.92 * s, root[1] + ay * L_ * P + ny * sw * 0.92 * s)
                if spec.get("doubled"):
                    for o in (-0.35, 0.35):
                        oq = (q[0] - ax * o * cw, q[1] - ay * o * cw)
                        ot = (tp[0] - ax * o * cw, tp[1] - ay * o * cw)
                        overs.append(("cable", (ot, h, oq, spec.get("cable_end_h", 0.12)), 0.75))
                else:
                    overs.append(("cable", (tp, h, q, spec.get("cable_end_h", 0.12)), 1.0))
    # pawn for scale (cables draw above pawns: the design's altitude rule)
    if human_at is not None:
        hum, m, off = HUMAN(sc.P)
        hx, hy = (human_at[0] + 0.5) * P, (human_at[1] + 0.5) * P
        sc.sd.ellipse([hx - 0.22 * P, hy + 0.2 * P, hx + 0.22 * P, hy + 0.36 * P], fill=120)
    sc.finish()
    draw = ImageDraw.Draw(sc.img)
    if human_at is not None:
        sc.img.alpha_composite(hum, (int(hx - m / 2), int(hy - m / 2 - off)))
    # shadows of the cables first, then posts north-to-south, then cables, then the post caps again
    shadow_layer = Image.new("L", sc.img.size, 0)
    sd = ImageDraw.Draw(shadow_layer)
    for kind, a, b in overs:
        if kind == "cable":
            p, h, q, g = a
            sd.line([sc.shd(p, h), sc.shd(q, g)], fill=190, width=max(2, int(cw * b)))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(P * 0.02))
    dark = Image.new("RGBA", sc.img.size, (10, 8, 6, 0))
    dark.putalpha(shadow_layer.point(lambda v: int(v * 0.62)))
    sc.img.alpha_composite(dark)
    draw = ImageDraw.Draw(sc.img)
    for kind, a, b in overs:
        if kind == "posts":
            for f in sorted(a, key=lambda f: f[1]):
                HOOKS["post"](sc, draw, f, H, pw, look, spec.get("post_kind", "steel"), spec)
            if posts == "portal" and len(a) == 2:      # the crossbeam joining the two post heads
                t0, t1 = sc.scr(a[0], H), sc.scr(a[1], H)
                HOOKS["beam"](sc, draw, t0, t1, pw, look, spec)
        if kind == "aframe":
            feet, apex = a, b
            for f in feet:
                at = sc.scr(apex, H)
                HOOKS["leg"](sc, draw, f, at, pw, look, spec)
            at = sc.scr(apex, H)
            draw.ellipse([at[0] - pw * 0.5, at[1] - pw * 0.5, at[0] + pw * 0.5, at[1] + pw * 0.5], fill=lk["light"])
    for kind, a, b in overs:
        if kind == "cable":
            p, h, q, g = a
            HOOKS["cable"](sc, draw, p, h, q, g, cw * b, look, spec)
    if spec.get("cable_style") == "rope" or look == "Scrapper":
        for tl in tops:          # lashing wraps where the cables meet the post tops
            for (tp, h, s) in tl:
                t = sc.scr(tp, h)
                draw.ellipse([t[0] - cw, t[1] - cw, t[0] + cw, t[1] + cw], fill=(150, 120, 80))
    return sc


# the draw functions structure() calls; gen_render.py swaps in the generated pieces
HOOKS = dict(deck=deck_image, post=draw_post, cable=draw_cable, beam=draw_beam, leg=draw_leg)

_HUM = {}


def HUMAN(P):
    if P not in _HUM:
        import sys
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, os.path.normpath(os.path.join(here, "../../../Utils/art")))
        import scale_panel
        _HUM[P] = scale_panel.human_sprite(P)
    return _HUM[P]


# ---------------------------------------------------------------- layouts
def jetty(look, spec, seed, d, n, ppc, human=False):
    """A jetty n cells long leaving a ledge toward d, over the 4x3 (or 3x4) real pit."""
    if d in ("E", "W"):
        sc = Scene(6, 5, (1, 1), False, ppc)
        if d == "E":
            anc, cell = (0, 2, "E"), (1, 2)
        else:
            anc, cell = (5, 2, "W"), (5 - n, 2)
        tip = (anc[0] + DIRS[d][0] * n, 2)
    else:
        sc = Scene(5, 8, (1, 2), True, ppc)
        if d == "N":
            anc, cell = (2, 6, "N"), (2, 6 - n)
        else:
            anc, cell = (2, 1, "S"), (2, 2)
        tip = (2, anc[1] + DIRS[d][1] * n)
    ends = dict(root="joint", tip=spec.get("tip", "beam"))
    structure(sc, look, spec, seed, [anc], cell, d, n, ends, human_at=tip if human else None)
    return sc.result()


def bridge(look, spec, seed, ns, ppc, human=False):
    """A suspension bridge anchor - 4 deck - anchor over the real pit."""
    spec = dict(spec, bridge=True)
    if not ns:
        sc = Scene(8, 5, (2, 1), False, ppc)
        anchors = [(1, 2, "E"), (6, 2, "W")]
        cell, d = (2, 2), "E"
        mid = (4, 2)
    else:
        sc = Scene(5, 8, (1, 2), True, ppc)
        anchors = [(2, 6, "N"), (2, 1, "S")]
        cell, d = (2, 2), "N"
        mid = (2, 4)
    structure(sc, look, spec, seed, anchors, cell, d, 4, dict(root="joint", tip="joint"), human_at=mid if human else None)
    return sc.result()
