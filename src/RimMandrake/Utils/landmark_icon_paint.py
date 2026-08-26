"""Repaint a Vanilla-Landmarks-Expanded world icon in Ludeon's own landmark style.

VLE ships its desert landmarks as a single opaque fill at 128x128 -- one colour,
no outline -- which is why they read as flat stamps on the world map.  Ludeon's
own `Cliffs`, `Valley` and `Ruins` do not: they are a TRANSLUCENT wash (max alpha
128-178) over a pure black outline, so the terrain texture reads through and the
outline carries the shape.  Measured 2026-08-25 off the extracted Odyssey bundle.

This paints that treatment onto VLE's existing silhouettes at 256x256 (128 px per
atlas cell, matching Ludeon).  The silhouette is never invented -- it is lifted
from the VLE source and only resampled -- so the atlas stays drop-in compatible.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 4                      # supersample factor; drawn at 512 per cell, area-averaged down
CELL = 128                  # Ludeon's per-cell size (256x256 file, atlasSize (2,2))
OUTLINE_PX = 2.5            # at CELL scale
VLE = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
       "/3656316229/Textures/World/Landmarks")


def _cell_masks(src):
    """Four silhouettes from a VLE 2x2 atlas, resampled to CELL*SS and re-thresholded."""
    im = Image.open(src).convert("RGBA")
    s = im.size[0] // 2
    out = []
    for x, y in ((0, 0), (1, 0), (0, 1), (1, 1)):
        a = im.crop((x * s, y * s, (x + 1) * s, (y + 1) * s)).getchannel("A")
        a = a.resize((CELL * SS, CELL * SS), Image.LANCZOS).filter(ImageFilter.GaussianBlur(SS))
        out.append(np.array(a) > 128)
    return out


def _erode(m, k):
    e = m.copy()
    for _ in range(int(k)):
        e = e & np.roll(e, 1, 0) & np.roll(e, -1, 0) & np.roll(e, 1, 1) & np.roll(e, -1, 1)
    return e


def _noise(shape, rng, scale, amp):
    """Smooth low-frequency value noise, used to warp every field so nothing reads
    as a circle or a straight band -- the two tells that make procedural art look
    procedural at map size."""
    n = max(2, int(shape[0] / scale))
    f = rng.random((n, n)).astype("float32")
    return (np.array(Image.fromarray((f * 255).astype("uint8")).resize(shape, Image.BICUBIC),
                     dtype=float) / 255.0 - 0.5) * 2 * amp


def _salt(mask, rng):
    """Bright playa crust broken into irregular polygonal plates by hairline fissures."""
    N = mask.shape[0]
    gy, gx = np.mgrid[0:N, 0:N].astype(float)
    wy = gy + _noise((N, N), rng, N / 5, N * 0.07)
    wx = gx + _noise((N, N), rng, N / 5, N * 0.07)
    ys, xs = np.nonzero(mask)
    pts = np.stack([ys, xs], 1)[rng.choice(len(ys), 9, replace=False)]
    d = ((wy[..., None] - pts[:, 0]) ** 2 + (wx[..., None] - pts[:, 1]) ** 2)
    lab = d.argmin(2)
    rgb = np.zeros(mask.shape + (3,), float)
    base = np.array((233, 235, 238))
    for i in range(len(pts)):                      # each plate its own faint tone
        rgb[lab == i] = base - rng.uniform(0, 13) * np.array((1.0, 0.95, 0.85))
    edge = np.zeros(mask.shape, bool)
    for ax in (0, 1):
        edge |= lab != np.roll(lab, 1, ax)
    edge = np.array(Image.fromarray((edge * 255).astype("uint8"))
                    .filter(ImageFilter.MaxFilter(2 * int(0.9 * SS) + 1))) > 128
    rgb[edge] = (163, 165, 172)
    return rgb, 174


def _dust(mask, rng):
    """Scoured tan pan: wind-drift crests and a blown-out deflation hollow."""
    N = mask.shape[0]
    gy, gx = np.mgrid[0:N, 0:N].astype(float)
    rgb = np.zeros(mask.shape + (3,), float)
    rgb[:] = (198, 170, 118)
    ang = rng.uniform(-0.6, 0.6)
    v = -gx * np.sin(ang) + gy * np.cos(ang)
    v = v + _noise((N, N), rng, N / 3.2, N * 0.16) + _noise((N, N), rng, N / 9, N * 0.04)
    band = (v / (N * 0.26)) % 1.0
    rgb[band < 0.17] = (221, 199, 154)             # drift crest
    rgb[(band > 0.62) & (band < 0.74)] = (170, 143, 97)
    cy, cx = N * (0.36 + 0.28 * rng.random()), N * (0.36 + 0.28 * rng.random())
    r = np.hypot(gy - cy, gx - cx) + _noise((N, N), rng, N / 4, N * 0.06)
    rgb[r < N * 0.16] = (152, 126, 86)             # deflation hollow, edge warped
    return rgb, 160


PAINTERS = {"VEE_SaltPlains": _salt, "VEE_DustBowl": _dust}


def paint(name, out_path):
    masks = _cell_masks(f"{VLE}/{name}.png")
    sheet = Image.new("RGBA", (CELL * 2, CELL * 2), (0, 0, 0, 0))
    for i, (mask, (x, y)) in enumerate(zip(masks, ((0, 0), (1, 0), (0, 1), (1, 1)))):
        rng = np.random.default_rng(hash((name, i)) % (2 ** 32))
        rgb, body_a = PAINTERS[name](mask, rng)
        inner = _erode(mask, OUTLINE_PX * SS)
        a = np.zeros(mask.shape, float)
        a[mask] = 205.0                                          # outline alpha
        a[inner] = body_a
        rgb[mask & ~inner] = (0, 0, 0)                            # Ludeon's black rim
        rgb[~mask] = 0
        px = np.dstack([rgb, a]).astype("uint8")
        cell = Image.fromarray(px, "RGBA").resize((CELL, CELL), Image.LANCZOS)
        # Clamp the downsample's faint rim away: Ludeon's own icons carry ~0.4%
        # alpha 1-31 pixels, LANCZOS leaves 3%, and that band is invisible but
        # corrupts every coverage measurement taken of the file afterwards.
        ca = np.array(cell)
        ca[..., 3][ca[..., 3] < 26] = 0
        cell = Image.fromarray(ca, "RGBA")
        sheet.paste(cell, (x * CELL, y * CELL))
    sheet.save(out_path)
    return out_path


if __name__ == "__main__":
    import sys
    dest = sys.argv[1]
    for n in PAINTERS:
        print(paint(n, f"{dest}/{n}.png"))
