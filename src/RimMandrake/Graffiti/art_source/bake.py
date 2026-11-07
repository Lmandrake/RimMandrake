"""GEN art -> Textures/: crop to the paint, fit the mark's wall-plane canvas (256 px per world cell), weather, colour-bleed the holes.
usage: bake.py [--only name,name] [--dry out_dir]    With --dry writes there instead of the mod."""
import os, shutil, sys
import numpy as np
from PIL import Image, ImageFilter
import manifest as MF
import paintify as P

TEX = os.path.join(MF.REPO, "src/RimMandrake/Graffiti/Textures/Things/Filth/Art")
PPC, TALL = 256, 192


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
    # Fill the canvas: a mark's proportions are loose, and every pixel of height counts on a face 25 px tall at play zoom.
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
    # Reads at 25 px: strengthen what's there before weathering takes some of it.
    alpha = np.clip(alpha, 0, 1) ** 0.72
    if not m["pigmented"] and m["mode"] != "scratch":
        rgb = P.to_pigment(rgb, 0.25)
    if m["pigmented"]:
        # A pale drawing tinted later: keep the variation in its value only, and high.
        l = rgb.mean(2, keepdims=True)
        rgb = np.clip(235 + (l - l[alpha > 0.3].mean() if (alpha > 0.3).any() else 0) * 0.4, 150, 255) * np.ones(3)
    # Weather: patches gone and some fading, varied per mark. A coarse wide patch and a fine horizontal scuff.
    wear = m["wear"]
    if wear > 0:
        patch = P.fractal((H, W), (W / 3.3, H / 2.5), rng, 3)
        alpha = alpha * np.clip((patch - wear * 0.34) / 0.14, 0, 1)
        scuff = P.fractal((H, W), (70, 9), rng, 3)
        alpha = alpha * (1 - 0.28 * wear * (1 - scuff))
    rgb = bleed(rgb, alpha)
    return Image.fromarray(np.dstack((np.clip(rgb, 0, 255), np.clip(alpha, 0, 1) * 255)).astype(np.uint8), "RGBA")


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
