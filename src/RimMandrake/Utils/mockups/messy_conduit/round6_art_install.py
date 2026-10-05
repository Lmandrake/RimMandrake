"""round6_art_install.py -- conform + install MessyConduit art round 6 (owner review 2026-10-04, station 11).

    python3 src/RimMandrake/Utils/mockups/messy_conduit/round6_art_install.py conform | sheets | install [--only s ...] [--dry]

Raw renders from round6_art_jobs.py (D:\\Luke\\dev\\_rmscratch\\mc_r6\\raw); conformed candidates in ...\\conf.
Install goes ONLY through artledger.install_image. Report: Transient/mc_art_round6_report.md.

Geometry kept (code offsets unchanged):
  * reels 256: conform_sprite registration onto the old Scrapper reel (stored onto stored, laid onto laid).
  * coupling / nozzle / end cap 128: fitted into the old Modern piece's alpha box (= the Scrapper box the hose anchor uses).
  * binding 82x40, mouth 64, strands 256x64: full canvas, as before.
  * strands are procedural: old Modern alpha + its shading (highlights compressed), twill + dirt with periods dividing 256.
"""
import colorsys
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round5_art_install as r5  # noqa: E402  (fit, conform, bbox, resize, ensure_alpha)

REPO, TEX = r5.REPO, r5.TEX
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "art"))
R = "/mnt/d/Luke/dev/_rmscratch/mc_r6"
RAW, IN, CONF = R + "/raw", R + "/in", R + "/conf"
REASON = "script:src/RimMandrake/Utils/mockups/messy_conduit/round6_art_install.py"
H, M = "Hose/", "Hose/Styles/Modern/"
CREAM = np.array([234, 222, 188], np.float32)   # off-white fire-hose jacket
TRACER = np.array([168, 52, 44], np.float32)    # thin printed red tracer line


def old(rel):
    p = os.path.join(TEX, rel)
    r = subprocess.run(["git", "-C", REPO, "show", "HEAD:%s" % os.path.relpath(p, REPO)], capture_output=True)
    import io
    return Image.open(io.BytesIO(r.stdout)).convert("RGBA")


def green_mask(a):
    rgb = a[..., :3].astype(np.float32) / 255
    mx, mn = rgb.max(2), rgb.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    g = rgb[..., 1]
    return (g >= mx - 1e-6) & (sat > 0.25) & (a[..., 3] > 0)


def lum(a):
    return (0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]).astype(np.float32) / 255


def to_cream(a, mask, lo=0.30, hi=0.97, gamma=0.6):
    """Recolour to cream by the pixel's own luminance: outline stays dark, highlights capped (matte canvas, not gloss).
    mask may be bool or a 0..1 weight (soft edge against the dark mouth/inner rim)."""
    out = a.astype(np.float32).copy()
    w = mask.astype(np.float32) if mask is not True else np.ones(a.shape[:2], np.float32)
    L = lum(a)
    v = L[w > 0.5]
    if v.size == 0:
        return a
    p2, p98 = np.percentile(v, 2), np.percentile(v, 98)
    n = np.clip((L - p2) / max(p98 - p2, 1e-3), 0, 1) ** gamma
    shade = np.minimum(lo + (1 - lo) * n, hi)
    col = np.clip(CREAM[None, None, :] * shade[..., None], 0, 255)
    out[..., :3] = out[..., :3] * (1 - w[..., None]) + col * w[..., None]
    return out.astype(np.uint8)


def green_weight(a):
    f = a.astype(np.float32)
    return np.clip((f[..., 1] - np.maximum(f[..., 0], f[..., 2]) - 8) / 30, 0, 1) * (a[..., 3] > 0)


def strand(rel, plump):
    a = np.asarray(old(rel)).copy()
    m = a[..., 3] > 0
    c = to_cream(a, True, gamma=0.75 if plump else 0.45, hi=0.92 if plump else 0.85).astype(np.float32)
    h, w = a.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    twill = 1 + 0.09 * np.sin(2 * np.pi * (x + y) / 4) + 0.03 * np.sin(2 * np.pi * (x - y) / 8)
    rng = np.random.default_rng(6)
    grain = 1 + 0.04 * (rng.random((h, w)) - 0.5)
    dirt = 1 - 0.05 * (np.sin(2 * np.pi * x / 128 + 1.3) * 0.5 + 0.5) * (np.sin(2 * np.pi * x / 64 + y / 9) * 0.5 + 0.5)
    c[..., :3] *= (twill * grain * dirt)[..., None]
    ys = np.where(m.any(1))[0]
    y0, y1 = ys[0], ys[-1]
    ty = int(round(y0 + (y1 - y0) * (0.30 if not plump else 0.36)))
    for yy, k in ((ty, 0.7),):
        row = c[yy, :, :3]
        sh = (row.mean(1, keepdims=True) / CREAM.mean())
        c[yy, :, :3] = row * (1 - k) + TRACER * sh * k
    c[..., 3] = a[..., 3]
    return Image.fromarray(np.clip(c, 0, 255).astype(np.uint8))


def recolour_green(rel):
    a = np.asarray(old(rel)).copy()
    gw = green_weight(a)
    return Image.fromarray(to_cream(a, gw)), int((gw > 0.5).sum())


def plan():
    out = []
    have = lambda n: os.path.isfile(os.path.join(RAW, n + ".png"))
    out.append((M + "Strand_Flat.png", strand(M + "Strand_Flat.png", False), "procedural cream flat"))
    out.append((M + "Strand_Plump.png", strand(M + "Strand_Plump.png", True), "procedural cream plump"))
    im, n = recolour_green(M + "Mouth.png")
    out.append((M + "Mouth.png", im, "green ring -> cream (%d px)" % n))
    for slot in ("Reel_PumpHookup", "Reel_Deployed"):
        im, n = recolour_green(M + slot + ".png")
        if n:
            out.append((M + slot + ".png", im, "green coil/stub -> cream (%d px)" % n))
    for name, slot in (("reel_stored_S", "Reel_PumpHookup"), ("reel_laid_S", "Reel_Deployed")):
        if have(name):
            ref = os.path.join(CONF, "ref_%s.png" % name)
            os.makedirs(CONF, exist_ok=True)
            old(H + slot + ".png").save(ref)
            out.append((H + slot + ".png", r5.conform(ref, os.path.join(RAW, name + ".png"),
                                                      os.path.join(CONF, name + "_reg.png")), "junk reel"))
    for name, slot in (("coup_M", "Coupling_Bare"), ("nozzle_M", "Nozzle_Bare"), ("endcap_M", "EndCap_Bare")):
        if have(name):
            box = r5.bbox(old(M + slot + ".png"))
            out.append((M + slot + ".png", r5.fit(r5.rgba(os.path.join(RAW, name + ".png")), box, (128, 128)),
                        "fit box %s" % (box,)))
    if have("binding_M"):
        b = r5.ensure_alpha(r5.rgba(os.path.join(RAW, "binding_M.png")))
        b = b.crop(r5.bbox(b))
        out.append((M + "Binding.png", r5.resize(b, 82, 40), "binding full canvas"))
    for rel, im, _ in out:
        p = os.path.join(CONF, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        im.save(p)
    return out


SHEETS = {
    "scrapper_reel": [H + "Reel_PumpHookup", H + "Reel_Deployed"],
    "modern_hose": [M + s for s in ("Strand_Flat", "Strand_Plump", "Binding", "Coupling_Bare", "Nozzle_Bare",
                                    "EndCap_Bare", "Mouth", "Reel_PumpHookup", "Reel_Deployed")],
}


def sheets(outdir):
    from PIL import ImageDraw
    os.makedirs(outdir, exist_ok=True)
    for name, rels in SHEETS.items():
        C = 260
        sh = Image.new("RGB", (2 * C + 340, len(rels) * (C + 10) + 30), (34, 28, 22))
        d = ImageDraw.Draw(sh)
        d.text((10, 8), "round 6 %s: BEFORE (left) | AFTER (right); small = 64 px thumbnail" % name, fill=(240, 220, 180))
        for i, rel in enumerate(rels):
            y = 30 + i * (C + 10)
            ap = os.path.join(CONF, rel + ".png")
            for j, im in enumerate((old(rel + ".png"), r5.rgba(ap) if os.path.isfile(ap) else None)):
                x = j * (C + 70)
                d.rectangle((x + 4, y, x + C, y + C), fill=(112, 90, 66))
                if im is None:
                    d.text((x + 20, y + C // 2), "not made", fill=(255, 200, 200))
                    continue
                k = min((C - 8) / im.width, (C - 8) / im.height)
                big = r5.resize(im, round(im.width * k), round(im.height * k))
                sh.paste(big, (x + 4 + (C - 4 - big.width) // 2, y + (C - big.height) // 2), big)
                f = 64.0 / max(im.size)
                small = r5.resize(im, max(1, round(im.width * f)), max(1, round(im.height * f)))
                d.rectangle((x + C + 2, y, x + C + 66, y + 66), fill=(112, 90, 66))
                sh.paste(small, (x + C + 2, y), small)
            d.text((2 * C + 150, y + 4), "\n".join(rel.split("/")), fill=(240, 220, 180))
        p = os.path.join(outdir, "round6_%s.png" % name)
        sh.save(p)
        print("sheet", p)
    # in-context: Modern reel + strand tiled 3x along u + coupling/nozzle, on ground brown
    ctx = Image.new("RGB", (900, 300), (112, 90, 66))
    reel = r5.rgba(os.path.join(CONF, M + "Reel_Deployed.png"))
    s = r5.rgba(os.path.join(CONF, M + "Strand_Flat.png"))
    s = r5.resize(s, 128, 32)
    for i in range(5):
        ctx.paste(s, (180 + i * 128, 120), s)
    p2 = r5.rgba(os.path.join(CONF, M + "Strand_Plump.png"))
    p2 = r5.resize(p2, 128, 32)
    for i in range(5):
        ctx.paste(p2, (180 + i * 128, 200), p2)
    ctx.paste(r5.resize(reel, 200, 200), (0, 40), r5.resize(reel, 200, 200))
    ctx.save(os.path.join(outdir, "round6_modern_context.png"))
    print("sheet", os.path.join(outdir, "round6_modern_context.png"))


def main(argv):
    if argv[0] == "sheets":
        sheets(os.path.join(REPO, "Transient", "mc_style_art"))
        return 0
    if argv[0] == "conform":
        for rel, im, note in plan():
            print("conf", rel, im.size, note)
        return 0
    only = argv[argv.index("--only") + 1:] if "--only" in argv else None
    import artledger
    for rel, im, note in plan():
        if only and not any(o in rel for o in only):
            continue
        if "--dry" in argv:
            print("would install", rel, im.size, note)
            continue
        r = artledger.install_image(os.path.join(TEX, rel), im, reason=REASON)
        print(r.get("status"), rel, im.size, r.get("validator", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
