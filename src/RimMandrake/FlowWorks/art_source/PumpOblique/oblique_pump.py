"""LIQUID_PUMP_REDRAW_PLAN_VIEW_HUB: turn the plan-view pump medallions into the oblique camera the tanks use.

Deterministic. Input: plan/<Look>.png (the installed 2026-10-23 plan-view art, 512 px = 1 cell).
  1. The four side-port arms (neck + flange; |perp| <= ARM_HALF, radial >= ARM_R) are cut out and put back unmoved,
     so every port stays where the port code expects it (edge centres) - the arms lie on the ground under the body.
     The N and S necks are run on with their own cross-section to meet the foreshortened body; the south one leaves
     through the wall face under a collar ring.
  2. The body (everything else) is foreshortened to the top face: squashed vertically by SQUASH and lifted WALL/2.
  3. A south wall WALL px tall under the top face's lower silhouette: a clean plate in the face's median material
     colour at WALL_LIT x its brightness, shaded by which way each facet looks (light from the north-west), with a lit
     rim lip, a seam band, plate joints, a rivet row and a dark ground line. (Stretching the rim, and mirroring the
     face's band, were both judged REJECT: streaks / ghost rings.)
  4. A soft contact shadow grounds it (down-right of the wall foot); interior anti-alias pinholes are closed.
Gate: check_oblique.py (--dir for candidates).
Run: python3 oblique_pump.py [outdir]   (writes <outdir>/<Look>.png; default ./out; install with art.py install)
"""
import os
import sys
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
N, C = 512, 256.0
ARM_HALF, ARM_R = 86, 146      # port strip half-width and inner radius, px (body plate ends at radial ~144)
SQUASH = 0.62                  # top-face foreshortening (the building camera's ellipse)
WALL = 80                      # south wall height, px (0.156 cell)
RIVET_STEP = 46                # px between skirt rivets
WALL_LIT = 0.72                # wall brightness at its top, x the top face's mean (lit from the north-west, wall faces south)


def premul(a):
    p = a.copy()
    p[..., :3] *= p[..., 3:4] / 255.0
    return p


def unpremul(p):
    a = p.copy()
    al = np.maximum(a[..., 3:4], 1e-6)
    a[..., :3] = np.where(a[..., 3:4] > 0, a[..., :3] * 255.0 / al, 0)
    return a


def over(dst, src):
    """Straight-alpha src OVER straight-alpha dst (float arrays, 0..255)."""
    sa, da = src[..., 3:4] / 255.0, dst[..., 3:4] / 255.0
    oa = sa + da * (1 - sa)
    rgb = (src[..., :3] * sa + dst[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6)
    return np.concatenate([np.where(oa > 0, rgb, 0), oa * 255.0], axis=-1)


def port_mask():
    yy, xx = np.mgrid[0:N, 0:N]
    dx, dy = xx - C + 0.5, yy - C + 0.5
    return ((np.abs(dy) <= ARM_HALF) & (np.abs(dx) >= ARM_R)) | ((np.abs(dx) <= ARM_HALF) & (np.abs(dy) >= ARM_R))


def oblique(src):
    a = np.array(src.convert("RGBA")).astype(np.float64)
    pm = port_mask()
    arms = a.copy(); arms[~pm] = 0
    body = a.copy(); body[pm] = 0

    # 2. top face: squash about the centre, lift by WALL/2 so the whole body (face + wall) stays centred on the cell
    nh = int(round(N * SQUASH))
    face_small = np.array(Image.fromarray(np.clip(premul(body), 0, 255).astype(np.uint8), "RGBA")
                          .resize((N, nh), Image.LANCZOS)).astype(np.float64)
    face = np.zeros_like(a)
    top = int(round(C - WALL / 2.0 - nh / 2.0))
    face[top:top + nh] = face_small
    face = unpremul(face)

    # 3. south wall
    wall = np.zeros_like(a)
    solid = face[..., 3] > 128
    cols = np.where(solid.any(0))[0]
    yb = np.full(N, -1)
    for x in cols:
        yb[x] = np.where(solid[:, x])[0][-1]
    # the wall's material is the face's own lower band, mirrored down (real rivets and plate grain, not a stretched edge),
    # each column rescaled to one lit brightness (WALL_LIT x the top face's) so no column extrudes as a black box
    lit = face[..., 3] > 200
    lum_face = face[..., :3].mean(-1)[lit].mean()
    tex = np.zeros((WALL, N, 3))
    for x in cols:
        for i in range(WALL):
            y = yb[x] - 3 - i
            tex[i, x] = face[y, x, :3] if y >= 0 and face[y, x, 3] > 128 else face[yb[x], x, :3]
    col_l = np.maximum(tex.mean(-1).mean(0), 1.0)                      # per-column mean brightness
    rel = np.ones((WALL, N))                                            # a clean plate: mirrored grain read as ghost rings
    for xs_ in range(int(C) % RIVET_STEP + RIVET_STEP // 2, N, RIVET_STEP):  # plate joints between the rivets
        if 0 < xs_ < N - 1:
            rel[:, xs_] = 0.78
            rel[:, xs_ + 1] = 1.08
    px = face[..., :3][lit]
    hue = np.median(px / np.maximum(px.mean(-1, keepdims=True), 1.0), axis=0)   # ONE material colour for the casing
    hue = np.tile(hue, (N, 1))
    cover = face[..., 3].max(0)                               # column coverage: anti-aliases the wall's outer columns
    ybf = yb.astype(np.float64)
    slope = np.gradient(np.where(yb >= 0, ybf, np.nan))
    slope = np.nan_to_num(slope)
    for x in cols:
        nx = -slope[x] / np.hypot(slope[x], 1.0)          # outward normal's x of the lower silhouette: <0 faces west
        facing = np.clip(1.0 - 0.30 * nx, 0.75, 1.25)
        for i in range(1, WALL + 1):
            y = yb[x] + i
            if y >= N:
                break
            t = i / float(WALL)
            level = lum_face * WALL_LIT * (1.0 - 0.28 * t) * facing * rel[i - 1, x]
            if i <= 3:
                level = lum_face * 1.05 * facing                        # rim lip catching the light
            elif abs(t - 0.55) < 0.025:
                level *= 0.75                                           # a seam band round the casing
            elif i > WALL - 3:
                level = lum_face * 0.30                                 # dark ground line: it stands on the ground
            wall[y, x, :3] = np.clip(hue[x] * level, 0, 255)
            wall[y, x, 3] = cover[x]
    # a row of rivets round the casing, a third of the way down: reads as a bolted metal skirt
    yy, xx = np.mgrid[-6:7, -6:7]
    d = np.hypot(yy, xx)
    for x0 in range(int(C) % RIVET_STEP, N, RIVET_STEP):
        full = [x for x in range(x0 - 8, x0 + 9) if 0 <= x < N and yb[x] >= 0 and cover[x] > 250]
        if len(full) < 17:
            continue
        y0 = yb[x0] + int(WALL * 0.33)
        for (dy, dx), r in np.ndenumerate(d):
            y, x = y0 + dy - 6, x0 + dx - 6
            if r <= 3.6:
                light = 1.25 - 0.12 * (dy - 6) - 0.08 * (dx - 6)       # lit from the north-west
                wall[y, x, :3] = np.clip(hue[x] * lum_face * 0.85 * light, 0, 255)
            elif r <= 5.0 and dy >= 6:
                wall[y, x, :3] *= 0.6                                   # its shadow on the skirt

    # anti-alias the wall's stepped outline (integer silhouette rows): soften its alpha by a pixel
    wa = Image.fromarray(np.clip(wall[..., 3], 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.9))
    lower = np.zeros((N, N), bool)                                     # only the foot and sides: the top joins the face
    for x in cols:
        lower[yb[x] + WALL // 2:, x] = True
    lower[:, :] |= (cover < 250)[None, :] & (np.arange(N)[:, None] > 0)
    wall[..., 3] = np.where(lower, np.minimum(wall[..., 3], np.array(wa).astype(np.float64)), wall[..., 3])
    wall[..., 3] = np.where(wall[..., 3] > 250, 255, wall[..., 3])

    # 4. contact shadow from the wall foot, down-right, soft
    foot = np.zeros((N, N))
    for x in cols:
        y0 = yb[x] + WALL - 4
        foot[max(0, y0):min(N, y0 + 12), x] = 1.0
    sh = Image.fromarray((foot * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))
    sh = np.roll(np.array(sh).astype(np.float64), (5, 6), axis=(0, 1))
    shadow = np.zeros_like(a)
    shadow[..., 3] = sh * 0.50

    # the N and S necks: foreshortening pulled the body away from them, so each neck is run on with its own straight
    # cross-section - the north one under the face to the centre, the south one up over the wall to half its height
    # (it leaves through the wall face, collared)
    xs = np.abs(np.arange(N) - C + 0.5) <= ARM_HALF
    south, north = np.zeros_like(arms), np.zeros_like(arms)
    south[int(C):, xs] = arms[int(C):, xs]
    north[:int(C), xs] = arms[:int(C), xs]
    rest = arms - south - north

    def neck_row(arm, rows):
        al = arm[..., 3] > 128
        spans = [(int(al[r].sum()), r) for r in rows if al[r].any()]
        return min(spans)[1]

    s_on = np.where((south[..., 3] > 128).any(1))[0]
    n_on = np.where((north[..., 3] > 128).any(1))[0]
    nrow = neck_row(south, range(s_on[0] + 2, s_on[0] + 30))
    yjoin = int(np.median([yb[x] for x in cols if abs(x - C) < 20])) + int(WALL * 0.6)
    ncols = np.where(south[nrow, :, 3] > 128)[0]
    for y in range(yjoin, nrow):
        south[y] = np.where(south[y][:, 3:4] > south[nrow][:, 3:4], south[y], south[nrow])
    # a collar where it leaves the wall: a ring 8 px proud of the neck each side, lit on top, shadowed below
    ring_c = south[nrow, ncols, :3].mean(0)
    for j, y in enumerate(range(yjoin - 2, yjoin + 10)):
        lit = 1.15 if j < 3 else (0.6 if j > 9 else 0.9)
        for x in range(ncols[0] - 8, ncols[-1] + 9):
            r = abs(x - (ncols[0] + ncols[-1]) / 2.0) / ((ncols[-1] - ncols[0]) / 2.0 + 8)
            south[y, x, :3] = np.clip(ring_c * lit * (1.1 - 0.35 * r * r), 0, 255)
            south[y, x, 3] = 255
    nrow = neck_row(north, range(n_on[-1] - 30, n_on[-1] - 1))
    for y in range(nrow + 1, int(C)):
        north[y] = np.where(north[y][:, 3:4] > north[nrow][:, 3:4], north[y], north[nrow])
    rest = over(rest, north)

    out = rest
    out = over(out, shadow)
    out = over(out, wall)
    out = over(out, face)
    out = over(out, south)
    al = out[..., 3]
    # seams where two layers' anti-aliased edges meet would show the ground through the casing: close interior pinholes
    for _ in range(2):
        ok = al > 250
        inner = (al < 250) & np.roll(ok, 4, 0) & np.roll(ok, -4, 0) & np.roll(ok, 4, 1) & np.roll(ok, -4, 1)
        al[inner] = 255
    al[al < 24] = 0
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out")
    os.makedirs(outdir, exist_ok=True)
    for look in LOOKS:
        im = oblique(Image.open(os.path.join(HERE, "plan", look + ".png")))
        p = os.path.join(outdir, look + ".png")
        im.save(p)
        print("wrote", p)


if __name__ == "__main__":
    main()
