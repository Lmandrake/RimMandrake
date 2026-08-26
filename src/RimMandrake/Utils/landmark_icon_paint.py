"""Repaint a Vanilla-Landmarks-Expanded world icon in Ludeon's own landmark style.

VLE ships its desert landmarks as a single opaque fill at 128x128 -- one colour,
no outline -- which is why they read as flat stamps on the world map.  Ludeon's
own `Cliffs`, `Valley` and `Ruins` do not: they are a TRANSLUCENT wash (max alpha
128-178) over a pure black outline, so the terrain texture reads through and the
outline carries the shape.  Measured 2026-08-25 off the extracted Odyssey bundle.

This paints that treatment onto VLE's existing silhouettes at 1024x1024 -- 512 px
per atlas cell, four times Ludeon's own density.  The silhouette is never invented; it
is lifted from the VLE source and only resampled, so the atlas stays drop-in.

Each painter returns (rgb, alpha) with alpha PER PIXEL, which Ludeon's icons do
not use.  It is what lets a dust storm thin out where the dust is thin.
"""
import numpy as np
from PIL import Image, ImageFilter

SS = 2                      # supersample factor
CELL = 512                  # per-cell size; the file is 2x2 of these
OUTLINE_PX = 3.0            # at CELL scale
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
    """Smooth low-frequency value noise.  Every field gets warped by this; without it
    a procedural spiral reads as a logo and a procedural hollow reads as a circle."""
    n = max(3, int(shape[0] / scale))
    f = rng.random((n, n)).astype("float32")
    im = Image.fromarray((f * 255).astype("uint8")).resize(shape, Image.BICUBIC)
    # Blur after the upscale.  A 3x3 grid stretched bicubic keeps AXIS-ALIGNED edges,
    # and thresholding that field paints straight-sided rectangles -- which is exactly
    # how the first brine patch shipped as a vertical grey bar.
    im = im.filter(ImageFilter.GaussianBlur(max(1, shape[0] / (n * 3))))
    g = np.asarray(im, dtype="float32") / 255.0
    return (g - 0.5) * 2 * amp


def _salt(mask, rng):
    """A real playa crust: polygonal plates whose FISSURES ARE RAISED WHITE RIDGES,
    because that is where the brine wicks up and the crystals grow.  Getting that
    inversion right -- bright seams, duller plates -- is what separates salt from
    cracked mud, which is what darker seams read as."""
    N = mask.shape[0]
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    wy = gy + _noise((N, N), rng, N / 5.5, N * 0.06)
    wx = gx + _noise((N, N), rng, N / 5.5, N * 0.06)
    ys, xs = np.nonzero(mask)
    pts = np.stack([ys, xs], 1)[rng.choice(len(ys), 11, replace=False)].astype("float32")
    d = ((wy[..., None] - pts[:, 0]) ** 2 + (wx[..., None] - pts[:, 1]) ** 2)
    lab = d.argmin(2)
    near = np.sort(d, 2)[..., :2]
    seam = np.sqrt(near[..., 1]) - np.sqrt(near[..., 0])          # 0 on a plate boundary

    rgb = np.zeros(mask.shape + (3,), "float32")
    for i in range(len(pts)):                                     # bright, faintly varied plates
        rgb[lab == i] = np.array((236, 236, 231)) - rng.uniform(0, 11) * np.array((1.0, .96, .86))
    dip = _noise((N, N), rng, N / 3.0, 1.0) + 0.5 * _noise((N, N), rng, N / 8.0, 1.0)
    rgb[dip > 0.52] = (214, 222, 226)                             # damp brine low spots

    ridge_w = N * 0.009
    ridge = seam < ridge_w * (1.0 + 0.9 * _noise((N, N), rng, N / 7, 1.0))
    crest = seam < ridge_w * 0.40
    rgb[ridge] = (243, 243, 239)                                  # crystal ruff along the seam
    rgb[crest] = (254, 254, 252)                                  # its lit crest

    # Crystal growth is a CLUSTERED field hugging the seams, not scattered dots.
    # Uniform round specks read as measles at any size -- measured on the 2026-08-25
    # first pass, which had to be thrown away for exactly that.
    bloom = (_noise((N, N), rng, N / 26, 1.0) > 0.30) & (seam < ridge_w * 4.5)
    bloom |= (_noise((N, N), rng, N / 40, 1.0) > 0.52) & (seam < ridge_w * 9)
    rgb[bloom] = (249, 249, 245)
    glint = (rng.random(mask.shape) < 0.004) & bloom
    glint = np.array(Image.fromarray((glint * 255).astype("uint8"))
                     .filter(ImageFilter.MaxFilter(2 * int(0.004 * N) + 1))) > 128
    rgb[glint] = (255, 255, 255)

    # Salt has to read BRIGHTER than the ground it sits on, so its wash runs
    # denser than Ludeon's brown-on-brown Cliffs (alpha 128).  At 170 the
    # terrain bled through and the pan read grey at 64 px.
    a = np.full(mask.shape, 196.0, "float32")
    a[bloom] = 214.0
    a[ridge] = 228.0
    a[crest] = 236.0
    a[glint] = 246.0
    return rgb, a


def _dust(mask, rng):
    """A dust storm caught turning: loose spiral arms about an off-centre eye, broken
    up by turbulence so the curl reads as weather rather than as a logo.  Dense and
    near-opaque in the arms, thin enough between them that the ground shows through --
    the per-pixel alpha is doing most of the work here."""
    N = mask.shape[0]
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    cy = N * (0.32 + 0.36 * rng.random())
    cx = N * (0.32 + 0.36 * rng.random())
    dy, dx = gy - cy, gx - cx
    # floor r well above zero: a tight log singularity at the eye winds the arms into
    # a rosette, which is the tell that killed the first attempt
    r = np.maximum(np.hypot(dy, dx) + _noise((N, N), rng, N / 3.5, N * 0.10), N * 0.10)
    th = np.arctan2(dy, dx)

    arms = 2 if rng.random() < 0.5 else 3
    twist = (1.15 + 0.55 * rng.random()) * (1 if rng.random() < 0.5 else -1)
    phase = arms * (th + twist * np.log(r))
    phase += 1.3 * _noise((N, N), rng, N / 5.5, 1.0)              # turbulence, large
    phase += 0.7 * _noise((N, N), rng, N / 13, 1.0)               # turbulence, fine
    band = 0.5 + 0.5 * np.sin(phase)
    band = band * (0.62 + 0.38 * np.clip(r / (N * 0.42), 0, 1))
    band += 0.09 * _noise((N, N), rng, N / 30, 1.0)               # grain

    rgb = np.zeros(mask.shape + (3,), "float32")
    base = np.array((190, 166, 120), "float32")
    lit = np.array((233, 215, 177), "float32")
    dark = np.array((146, 120, 82), "float32")
    t = np.clip(band, 0, 1)[..., None]
    rgb[:] = np.where(t > 0.5, dark + (lit - dark) * ((t - 0.5) * 2),
                      base + (dark - base) * (1 - t * 2))

    wisp = (rng.random(mask.shape) < 0.003) & (band > 0.74)       # blown grit in the arms
    rgb[wisp] = (246, 232, 199)

    a = 92.0 + 122.0 * np.clip(band, 0, 1)
    a[wisp] = 234.0
    return rgb, a.astype("float32")


PAINTERS = {"VEE_SaltPlains": _salt, "VEE_DustBowl": _dust}


def paint(name, out_path):
    masks = _cell_masks(f"{VLE}/{name}.png")
    sheet = Image.new("RGBA", (CELL * 2, CELL * 2), (0, 0, 0, 0))
    for i, (mask, (x, y)) in enumerate(zip(masks, ((0, 0), (1, 0), (0, 1), (1, 1)))):
        rng = np.random.default_rng(abs(hash((name, i))) % (2 ** 32))
        rgb, a = PAINTERS[name](mask, rng)
        inner = _erode(mask, OUTLINE_PX * SS)
        a = np.where(inner, a, 205.0)                             # outline alpha
        rgb[mask & ~inner] = (0, 0, 0)                            # Ludeon's black rim
        a[~mask] = 0
        rgb[~mask] = 0
        cell = Image.fromarray(np.dstack([rgb, a]).clip(0, 255).astype("uint8"), "RGBA")
        cell = cell.resize((CELL, CELL), Image.LANCZOS)
        # Clamp the downsample's faint rim away: Ludeon's own icons carry ~0.4% of
        # alpha 1-31 pixels, LANCZOS leaves 3%, and that band is invisible on screen
        # but corrupts every coverage measurement taken of the file afterwards.
        ca = np.array(cell)
        ca[..., 3][ca[..., 3] < 26] = 0
        sheet.paste(Image.fromarray(ca, "RGBA"), (x * CELL, y * CELL))
    sheet.save(out_path)
    return out_path


if __name__ == "__main__":
    import sys
    dest = sys.argv[1]
    for n in PAINTERS:
        print(paint(n, f"{dest}/{n}.png"))
