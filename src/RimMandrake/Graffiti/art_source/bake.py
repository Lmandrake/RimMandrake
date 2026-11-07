"""GEN art -> Textures/: crop to the paint, fit the mark's wall-plane canvas (256 px per world cell), weather, colour-bleed the holes.
usage: bake.py [--only name,name] [--dry out_dir]    With --dry writes there instead of the mod."""
import os, shutil, sys
import numpy as np
from PIL import Image, ImageFilter
import manifest as MF
import paintify as P

TEX = os.path.join(MF.REPO, "src/RimMandrake/Graffiti/Textures/Things/Filth/Art")
PPC, TALL = 256, 256


def bleed(rgb, alpha, passes=4):
    """Paint colour out under the transparent pixels, so a mip or a bilinear sample at a soft edge never pulls in black."""
    rgb, a = rgb.copy(), alpha.copy()
    for r in (2, 5, 12, 30):
        w = P.blur(np.clip(a, 0, 1), r) + 1e-4
        col = np.dstack([P.blur(rgb[..., i] / 255 * np.clip(a, 0, 1), r) for i in range(3)]) * 255 / w[..., None]
        hole = alpha < 0.02
        rgb[hole] = np.clip(col, 0, 255)[hole]
    return rgb


def bake(name, m):
    src = Image.open(f"{MF.GEN}/{name}.png").convert("RGBA")
    a = np.asarray(src)[..., 3]
    ys, xs = np.nonzero(a > 16)
    if len(xs) == 0:
        raise ValueError(name + " is empty")
    pad = 4
    box = (max(0, xs.min() - pad), max(0, ys.min() - pad), min(src.width, xs.max() + pad + 1), min(src.height, ys.max() + pad + 1))
    src = src.crop(box)
    W, H = int(PPC * m["width"]), int(TALL * m["height"])
    # Fill the canvas: a mark's proportions are loose, and it has its wall's face and the wall's top to fill (option D).
    aspect_art, aspect_can = src.width / src.height, W / H
    if aspect_art > aspect_can * 1.45:
        w, h = W, int(W / (aspect_can * 1.45))
    elif aspect_art < aspect_can / 1.45:
        h, w = H, int(H * aspect_can / 1.45)
    else:
        w, h = W, H
    pm = np.asarray(src).astype(float)
    al = pm[..., 3:] / 255
    pm = np.dstack((pm[..., :3] * al, pm[..., 3]))
    s = Image.fromarray(np.clip(pm, 0, 255).astype(np.uint8), "RGBA").resize((w, h), Image.LANCZOS)
    s = np.asarray(s).astype(float)
    al = np.maximum(s[..., 3:] / 255, 1e-3)
    s = np.dstack((np.clip(s[..., :3] / al, 0, 255), s[..., 3]))
    can = np.zeros((H, W, 4))
    x0, y0 = (W - w) // 2, (H - h) // 2
    can[y0:y0 + h, x0:x0 + w] = s
    rgb, alpha = can[..., :3], can[..., 3] / 255
    rng = np.random.default_rng(abs(hash_name(name)) % 2 ** 31)
    # Option D: loaded paint. Strengthen what's there before weathering takes some of it.
    alpha = np.clip(alpha, 0, 1) ** 0.42
    if not m["pigmented"] and m["mode"] != "scratch":
        rgb = P.to_pigment(rgb, 0.25)
    if m["pigmented"]:
        # A pale drawing tinted later: keep the variation in its value only, and high.
        l = rgb.mean(2, keepdims=True)
        rgb = np.clip(235 + (l - l[alpha > 0.3].mean() if (alpha > 0.3).any() else 0) * 0.4, 150, 255) * np.ones(3)
    if not m["pigmented"] and m["mode"] != "scratch":
        rgb = bolder(rgb, alpha)
    if m["mode"] == "paste":
        # Option D has no paper: a poster is what its inks left on the wall, the paper gone.
        rgb, alpha = paste_to_paint(rgb, alpha, rng)
    if m["mode"] not in ("paste", "scratch"):
        alpha = break_rim(rgb, alpha, rng)
        # The brush runs out: long level streaks through every fill, so no area of colour stays flat.
        streak = P.fractal((H, W), (W / 2.5, 5), rng, 3)
        load = P.fractal((H, W), (W / 4, H / 2.2), rng, 2)
        alpha = alpha * np.clip(0.76 + 0.7 * streak * (0.55 + 0.75 * load), 0, 1)
    # Weather: patches gone and some fading, varied per mark. A coarse wide patch and a fine horizontal scuff.
    wear = m["wear"]
    if wear > 0:
        patch = P.fractal((H, W), (W / 3.3, H / 2.5), rng, 3)
        alpha = alpha * np.clip((patch - wear * 0.24) / 0.14, 0, 1)
        scuff = P.fractal((H, W), (70, 9), rng, 3)
        alpha = alpha * (1 - 0.22 * wear * (1 - scuff))
    rgb = bleed(rgb, alpha)
    return Image.fromarray(np.dstack((np.clip(rgb, 0, 255), np.clip(alpha, 0, 1) * 255)).astype(np.uint8), "RGBA")


def bolder(rgb, alpha):
    """Loaded paint: the drawing's colours pulled apart, saturation and value, around its own middle. The pigments stay this
    world's; there is just more of them on the wall."""
    grey = rgb.mean(2, keepdims=True)
    painted = alpha > 0.3
    mid = grey[painted].mean() if painted.any() else 128.0
    out = mid + (grey - mid) * 1.3 + (rgb - grey) * 1.35
    return np.clip(out, 0, 255)


def paste_to_paint(rgb, alpha, rng):
    """The paper's ground goes (the palest, most common value of the sheet); what was printed on it stays as a heavy hand's paint."""
    l = rgb.mean(2)
    painted = alpha > 0.3
    if not painted.any():
        return rgb, alpha
    ground = np.quantile(l[painted], 0.62)
    keep = np.clip((ground - l) / 34 + 0.12, 0, 1)
    ragged = P.fractal(alpha.shape, (16, 16), rng, 2)
    return rgb * 0.92, alpha * np.clip(keep * 1.3 + 0.28 * (ragged > 0.72), 0, 1)


def break_rim(rgb, alpha, rng):
    """A dark line following the shape's whole edge is what makes a sticker. Where one exists, a real hand's line skips: knock
    it out in long gaps, and leave the fill's own edge to fray there."""
    solid = (alpha > 0.4).astype(np.uint8) * 255
    inner = np.asarray(Image.fromarray(solid).filter(ImageFilter.MinFilter(25))) > 127
    rim = (alpha > 0.4) & ~inner
    if not rim.any() or not inner.any():
        return alpha
    l = rgb.mean(2)
    fill = np.median(l[inner])
    dark = rim & (l < min(fill * 0.62, 90))
    if dark.sum() < rim.sum() * 0.25:
        return alpha
    gaps = P.fractal(alpha.shape, (46, 46), rng, 2)
    keep = np.clip((gaps - 0.46) / 0.1, 0, 1)
    soft = P.blur(dark.astype(float), 1.2)
    return alpha * (1 - np.clip(soft * 1.4, 0, 1) * (1 - keep))


def hash_name(s):
    h = 2166136261
    for c in s.encode():
        h = (h ^ c) * 16777619 & 0xFFFFFFFF
    return h


def main():
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    dry = sys.argv[sys.argv.index("--dry") + 1] if "--dry" in sys.argv else None
    wiped = set()
    missing = []
    for name, m in MF.M.items():
        if only and name not in only:
            continue
        if not os.path.exists(f"{MF.GEN}/{name}.png"):
            missing.append(name)
            continue
        im = bake(name, m)
        if dry:
            os.makedirs(dry, exist_ok=True)
            im.save(f"{dry}/{name}.png")
            continue
        folder = os.path.join(TEX, m["folder"])
        if folder not in wiped and not only:
            shutil.rmtree(folder, ignore_errors=True)
            wiped.add(folder)
        os.makedirs(folder, exist_ok=True)
        im.save(os.path.join(folder, name + ".png"))
    print("baked", "missing", missing)


if __name__ == "__main__":
    main()
