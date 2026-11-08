"""Offline prototype of WallPlane.PaintedIcon (pass 18): each writer copies the faith's sign by hand, a clumsy hand worse,
sprayed through card (mist past the edge) and running when the hand is poor. Rows here are top-down (PIL); the C# is bottom-up."""
import sys, numpy as np
from PIL import Image

def perlin_like(shape, scale, seed):
    rng = np.random.default_rng(seed)
    h, w = shape
    gh, gw = max(2, int(h / scale) + 2), max(2, int(w / scale) + 2)
    g = rng.random((gh, gw))
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((int(gw * scale), int(gh * scale)), Image.BICUBIC)
    return np.asarray(im)[:h, :w] / 255.0

def blur(a, r):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    from PIL import ImageFilter
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r))) / 255.0

def painted(src, hand, wobble, drips):
    a = np.asarray(src.convert("RGBA")).astype(float) / 255
    size = a.shape[0]
    seed = hand * 7919 + 13
    drift = size * min(0.09, max(0.012, 0.035 * wobble))
    dx = (perlin_like((size, size), size / 2.2, seed) - 0.5) * 2 * drift
    dy = (perlin_like((size, size), size / 2.2, seed + 1) - 0.5) * 2 * drift
    ys, xs = np.mgrid[0:size, 0:size]
    sx = np.clip(np.round(xs + dx), 0, size - 1).astype(int)
    sy = np.clip(np.round(ys + dy), 0, size - 1).astype(int)
    px = a[sy, sx]
    lum = px[..., :3].mean(2)
    # One can through card: the sign's light is the paint, its shade the paint thinner, its black outline the card left standing (bare wall).
    tone = np.where(lum > 0.55, 1.0, 0.72)
    al = np.where(px[..., 3] > 0.43, 1.0, np.where(px[..., 3] > 0.16, 0.47, 0.0)) * np.clip((lum - 0.22) / 0.12, 0, 1)
    # card edge: the cut wobbles a little at fine scale too
    streak = perlin_like((size, size), size / 1.5, seed + 2)
    patch = perlin_like((size, size), size / 5, seed + 3)
    grit = perlin_like((size, size), max(2, size / 40), seed + 4)
    keep = np.clip((streak + patch * 0.8 - 0.62) / 0.28, 0, 1) * np.clip((grit + 0.35) / 0.6, 0, 1)
    al = al * (0.55 + 0.45 * keep)
    # spray mist past the card's edge: soft, speckled, thin
    speck = perlin_like((size, size), max(1.5, size / 90), seed + 5)
    mist = blur((al > 0.5).astype(float), size * 0.025) * 0.42 * np.clip((speck - 0.35) / 0.3, 0, 1)
    al = np.maximum(al, mist * (1.25 - 0.25 * min(wobble, 1)))
    tone = np.where(al > mist + 1e-3, tone, 0.8)
    # runs: from a bottom edge, straight down, a bead where each stopped
    if drips > 0:
        rng = np.random.default_rng(seed + 6)
        solid = al > 0.6
        bottom = solid & ~np.vstack([solid[1:], np.zeros((1, size), bool)])
        cand = np.argwhere(bottom)
        n = int(2 + 5 * drips)
        for _ in range(n if len(cand) else 0):
            y, x = cand[rng.integers(len(cand))]
            ln = int(size * (0.06 + 0.22 * drips * rng.random()))
            wdt = max(2, size // 48)
            for k in range(ln):
                yy = y + 1 + k
                if yy >= size: break
                al[yy, x:x + wdt] = np.maximum(al[yy, x:x + wdt], 0.9 - 0.35 * k / ln)
                tone[yy, x:x + wdt] = 1.0
            yb = min(size - 2, y + ln)
            al[yb:yb + 2, max(0, x - 1):x + wdt + 1] = 0.9
            tone[yb:yb + 2, max(0, x - 1):x + wdt + 1] = 1.0
    out = np.dstack([tone, tone, tone, al])
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "RGBA")

if __name__ == "__main__":
    names = sys.argv[1].split(",")
    out = sys.argv[2]
    col = np.array([0.20, 0.55, 0.55])
    wall = (88, 78, 70)
    rows = []
    for n in names:
        src = Image.open(f"/mnt/d/ClaudeWork/rimmandrake/scratch/ideoicons_vanilla/{n}.png").convert("RGBA").resize((128, 128), Image.LANCZOS)
        cells = []
        for (hand, wob, dr) in [(-1, 0, 0), (0, 1, 0), (1, 1, 0), (2, 0.6, 0), (3, 2, 0.5), (4, 3, 1)]:
            im = src if hand < 0 else painted(src, hand, wob, dr)
            a = np.asarray(im).astype(float) / 255
            tint = a[..., :3].mean(2, keepdims=True) * col if hand >= 0 else a[..., :3] * col * 1.6
            bg = np.ones((128, 128, 3)) * np.array(wall) / 255
            c = bg * (1 - a[..., 3:]) + np.clip(tint, 0, 1) * a[..., 3:]
            cells.append((c * 255).astype(np.uint8))
        rows.append(np.hstack(cells))
    big = Image.fromarray(np.vstack(rows))
    big.save(out)
    big.resize((big.width // 2, big.height // 2), Image.LANCZOS).save(out.replace(".png", "_half.png"))
