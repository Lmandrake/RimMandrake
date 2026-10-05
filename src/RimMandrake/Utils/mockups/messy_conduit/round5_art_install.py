"""round5_art_install.py -- conform + install MessyConduit art round 5 (owner review 2026-10-04 of the per-style map).

    python3 src/RimMandrake/Utils/mockups/messy_conduit/round5_art_install.py conform     # raw -> conf, writes candidates
    python3 src/RimMandrake/Utils/mockups/messy_conduit/round5_art_install.py install [--only substr ...] [--dry]

Raw renders come from round5_art_jobs.py (D:\\Luke\\dev\\_rmscratch\\mc_r5\\raw); conformed candidates land in ...\\conf
under their install path. Install goes ONLY through artledger.install_image (reason script:<this file>).
Report: Transient/mc_art_round5_report.md.

Geometry kept (code offsets unchanged):
  * switch 128: fitted into the old look's switch alpha box, centred.
  * junction 128: X = brick + 4 plugs on the full canvas, brick centre (64,64). T = the SAME X image shifted up by
    TapeAnchorZ*128 = 19 px (CordBuilder.TapeAnchorZ 0.152, the T's junction point sits 0.152 cell north of the decal
    centre, its missing arm is +Z) with everything above the brick's top edge cut away: T and + share one brick size/centre.
  * power strip 64x32: fitted into the old strip's alpha box.
  * lamp mast 256x512: conform_sprite registration onto the old mast, then ONLY the lamp-head box is taken from the new
    render (pole, crossarm, insulators byte-identical, so PoleGeometryTable's insulator tips stay true); Top = rows 0-127.
  * floor lamp 128 (new path Styles/<Look>/StandingLamp.png; vanilla LampStanding is 64 at drawSize 1).
  * clamp 256 (was a 128 upscale of a 64 render): the old clamp's box x2 MINUS its cable stub, jaw tip (left) and vertical
    centre kept, so TapBiteX (-0.40 of width) still lands on the jaws. Drawn at TapSize 1.5 cells either way.
  * reel 256: conform_sprite registration onto the old Modern reel.
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "art"))
sys.path.insert(0, HERE)
TEX = os.path.join(REPO, "src", "RimMandrake", "MessyConduit", "Textures", "RimMandrake", "MessyConduit")
R = "/mnt/d/Luke/dev/_rmscratch/mc_r5"
RAW, IN, CONF = R + "/raw", R + "/in", R + "/conf"
REASON = "script:src/RimMandrake/Utils/mockups/messy_conduit/round5_art_install.py"
CONFORM = os.path.join(REPO, "skills", "generating-rimworld-sprites", "scripts", "conform_sprite.py")
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
FAM = {"Jawa": "Scrapper", "StarWars": "Industrial", "ExtCord": "Modern", "Cybertek": "Futuristic"}
COLOURS = ("Green", "Brown", "Yellow", "Blue")
T_SHIFT = 19
# lamp-head boxes (x0, y0, x1, y1) on the 256x512 mast canvas: right of the pole, below the insulators
HEAD_BOX = {"Scrapper": (150, 90, 256, 212), "Industrial": (146, 136, 256, 228),
            "Modern": (142, 92, 256, 182), "Futuristic": (146, 100, 256, 178)}


def rgba(p):
    return Image.open(p).convert("RGBA")


def bbox(im, floor=32):
    a = np.asarray(im)[..., 3] >= floor
    ys, xs = np.where(a.any(1))[0], np.where(a.any(0))[0]
    return (xs[0], ys[0], xs[-1] + 1, ys[-1] + 1)


def resize(im, w, h):
    return im.convert("RGBa").resize((max(1, w), max(1, h)), Image.LANCZOS).convert("RGBA")


def ensure_alpha(im):
    """A render that came back opaque: key out the background by the corner colour (flood-ish distance key)."""
    a = np.asarray(im).astype(np.float32)
    if (a[..., 3] < 250).mean() > 0.05:
        return im
    corners = np.array([a[2, 2, :3], a[2, -3, :3], a[-3, 2, :3], a[-3, -3, :3]]).mean(0)
    d = np.sqrt(((a[..., :3] - corners) ** 2).sum(2))
    alpha = np.clip((d - 18) / 30, 0, 1) * 255
    a[..., 3] = alpha
    return Image.fromarray(a.astype(np.uint8))


def fit(im, box, canvas, align="centre"):
    """Trim im to its subject, scale (aspect kept) to fit inside box, place on a canvas-sized transparent image."""
    im = ensure_alpha(im)
    sub = im.crop(bbox(im))
    bw, bh = box[2] - box[0], box[3] - box[1]
    k = min(bw / sub.width, bh / sub.height)
    sub = resize(sub, round(sub.width * k), round(sub.height * k))
    x = box[0] if align == "left" else box[0] + (bw - sub.width) // 2
    y = box[1] + (bh - sub.height) // 2
    out = Image.new("RGBA", canvas, (0, 0, 0, 0))
    out.alpha_composite(sub, (x, y))
    return out


def conform(ref, src, dst):
    tmp = src.replace(".png", "_alpha.png")
    ensure_alpha(rgba(src)).save(tmp)
    subprocess.run([sys.executable, CONFORM, "--reference", ref, "--input", tmp, "--out", dst], check=True,
                   capture_output=True)
    return rgba(dst)


def clamp_box(old):
    """Old clamp's box on its own canvas minus the cable stub at its right: columns whose opaque height is under a
    quarter of the tallest column, counted in from the right edge."""
    a = np.asarray(old)[..., 3] >= 32
    h = a.sum(0)
    x0, y0, x1, y1 = bbox(old)
    r = x1 - 1
    while r > x0 and h[r] < 0.25 * h.max():
        r -= 1
    return x0, y0, r + 1, y1


def brick_top(im):
    """First row (from the top) where the opaque width jumps to the brick's: rows above it carry only the north plug."""
    a = np.asarray(im)[..., 3] >= 64
    w = a.sum(1)
    mid = w[w > 0]
    plug = np.median(w[: im.height // 4][w[: im.height // 4] > 0]) if (w[: im.height // 4] > 0).any() else 0
    for y in range(im.height):
        if w[y] > max(plug * 1.6, 0.30 * im.width):
            return y
    return 0


def plan():
    """[(rel under TEX, image, note)]"""
    out = []
    os.makedirs(CONF, exist_ok=True)
    have = lambda n: os.path.isfile(os.path.join(RAW, n + ".png"))
    for L in LOOKS:
        old = os.path.join(TEX, "PowerSwitch.png") if L == "Scrapper" else os.path.join(TEX, "Styles", L, "PowerSwitch.png")
        box = bbox(rgba(os.path.join(IN, "sw_" + L + ".png")))
        base = "PowerSwitch" if L == "Scrapper" else "Styles/%s/PowerSwitch" % L
        if have("sw_" + L):
            out.append((base + ".png", fit(rgba(os.path.join(RAW, "sw_" + L + ".png")), box, (128, 128)), "switch on"))
        if have("swoff_" + L):
            out.append((base + "_Off.png", fit(rgba(os.path.join(RAW, "swoff_" + L + ".png")), box, (128, 128)), "switch off"))
    for F in FAM:
        if not have("jx_" + F):
            continue
        X = fit(rgba(os.path.join(RAW, "jx_" + F + ".png")), (0, 0, 128, 128), (128, 128))
        top = brick_top(X)
        T = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        T.alpha_composite(X.crop((0, top, 128, 128)), (0, top - T_SHIFT))
        xr, tr = ("Junction_Tin.png", "Junction_Tape.png") if F == "Jawa" else ("Styles/%s/Junction_X.png" % F,
                                                                                 "Styles/%s/Junction_T.png" % F)
        out.append((xr, X, "junction + (brick top row %d)" % top))
        out.append((tr, T, "junction T = + shifted up %d, north plug cut" % T_SHIFT))
        if F == "ExtCord":
            import recolor_extcord_pieces as rc
            for C in COLOURS:
                for slot, im in (("Junction_X", X), ("Junction_T", T)):
                    p = os.path.join(CONF, "ext_%s_%s.png" % (slot, C))
                    im.save(p.replace(".png", "_src.png"))
                    v, n = rc.recolor(p.replace(".png", "_src.png"), C)
                    out.append(("Styles/ExtCord/%s/%s.png" % (C, slot), v, "recolour %d px" % n))
    if have("strip"):
        S = fit(rgba(os.path.join(RAW, "strip.png")), bbox(rgba(os.path.join(IN, "strip_old.png"))), (64, 32))
        out.append(("PowerStrip.png", S, "strip"))
        import wire_style_pieces_art as w
        off, n = w.strip_off(S)
        out.append(("Styles/ExtCord/PowerStrip_Off.png", off, "derived LED-off %d px" % n))
    for L in LOOKS:
        if not have("mast_" + L):
            continue
        old_p = os.path.join(IN, "mast_" + L + ".png")
        new = conform(old_p, os.path.join(RAW, "mast_" + L + ".png"), os.path.join(CONF, "mast_%s_reg.png" % L))
        old = rgba(old_p)
        x0, y0, x1, y1 = HEAD_BOX[L]
        m = old.copy()
        m.paste(new.crop((x0, y0, x1, y1)), (x0, y0))
        out.append(("Aerial/Styles/%s/AerialLampMast.png" % L, m, "lamp head box %s" % (HEAD_BOX[L],)))
        out.append(("Aerial/Styles/%s/AerialLampMastTop.png" % L, m.crop((0, 0, 256, 128)), "top = rows 0-127"))
    for L in LOOKS:
        if have("floor_" + L):
            out.append(("Styles/%s/StandingLamp.png" % L, fit(rgba(os.path.join(RAW, "floor_" + L + ".png")),
                                                                (8, 8, 120, 120), (128, 128)), "floor lamp (new path)"))
    for L in LOOKS:
        if not have("clamp_" + L):
            continue
        old = rgba(os.path.join(IN, "clamp_" + L + ".png"))
        k = 256 / old.width
        b = [round(v * k) for v in clamp_box(old)]
        rel = "Aerial/TapClamp.png" if L == "Scrapper" else "Aerial/Styles/%s/TapClamp.png" % L
        out.append((rel, fit(rgba(os.path.join(RAW, "clamp_" + L + ".png")), b, (256, 256), align="left"),
                    "clamp 256, box %s (stub cut)" % b))
    for n, slot in (("reel_stored", "Reel_PumpHookup"), ("reel_laid", "Reel_Deployed")):
        if have(n):
            ref = os.path.join(IN, n + ".png")
            out.append(("Hose/Styles/Modern/%s.png" % slot,
                        conform(ref, os.path.join(RAW, n + ".png"), os.path.join(CONF, n + "_reg.png")), "reel red"))
    for rel, im, _ in out:
        p = os.path.join(CONF, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        im.save(p)
    return out


SHEETS = {
    "switches": ["PowerSwitch", "PowerSwitch_Off"] + ["Styles/%s/PowerSwitch%s" % (L, o) for L in LOOKS[1:] for o in ("", "_Off")],
    "junctions": ["Junction_Tin", "Junction_Tape"] + ["Styles/%s/Junction_%s" % (F, k) for F in ("StarWars", "ExtCord", "Cybertek")
                                                       for k in ("X", "T")] + ["Styles/ExtCord/%s/Junction_X" % C for C in COLOURS],
    "strip_reel_clamp": ["PowerStrip", "Styles/ExtCord/PowerStrip_Off", "Hose/Styles/Modern/Reel_PumpHookup",
                         "Hose/Styles/Modern/Reel_Deployed", "Aerial/TapClamp"] + ["Aerial/Styles/%s/TapClamp" % L for L in LOOKS[1:]],
    "lamps": ["Aerial/Styles/%s/AerialLampMast" % L for L in LOOKS] + ["Styles/%s/StandingLamp" % L for L in LOOKS],
}


def sheets(outdir):
    """Before (git HEAD) | after (conformed candidate), each large on a ground-brown cell plus a true-size inset."""
    import io
    from PIL import ImageDraw
    os.makedirs(outdir, exist_ok=True)
    rel_tex = os.path.relpath(TEX, REPO)
    for name, rels in SHEETS.items():
        C = 260
        sh = Image.new("RGB", (2 * C + 340, len(rels) * (C + 10) + 30), (34, 28, 22))
        d = ImageDraw.Draw(sh)
        d.text((10, 8), "round 5 %s: BEFORE (left) | AFTER (right); small = 64 px thumbnail (in-game scale for a 1-cell piece at 64 px/cell)" % name, fill=(240, 220, 180))
        for i, rel in enumerate(rels):
            y = 30 + i * (C + 10)
            r = subprocess.run(["git", "-C", REPO, "show", "HEAD:%s/%s.png" % (rel_tex, rel)], capture_output=True)
            before = Image.open(io.BytesIO(r.stdout)).convert("RGBA") if r.returncode == 0 else None
            ap = os.path.join(CONF, rel + ".png")
            after = rgba(ap) if os.path.isfile(ap) else None
            for j, im in enumerate((before, after)):
                x = j * (C + 70)
                d.rectangle((x + 4, y, x + C, y + C), fill=(112, 90, 66))
                if im is None:
                    d.text((x + 20, y + C // 2), "none (new path)" if j == 0 else "not made", fill=(255, 200, 200))
                    continue
                k = min((C - 8) / im.width, (C - 8) / im.height)
                big = resize(im, round(im.width * k), round(im.height * k))
                sh.paste(big, (x + 4 + (C - 4 - big.width) // 2, y + (C - big.height) // 2), big)
                f = 64.0 / max(im.size)
                small = resize(im, max(1, round(im.width * f)), max(1, round(im.height * f)))
                d.rectangle((x + C + 2, y, x + C + 66, y + 66), fill=(112, 90, 66))
                sh.paste(small, (x + C + 2, y), small)
            d.text((2 * C + 150, y + 4), "\n".join(rel.split("/")), fill=(240, 220, 180))
        sh.save(os.path.join(outdir, "round5_%s.png" % name))
        print("sheet", os.path.join(outdir, "round5_%s.png" % name))


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
        dest = os.path.join(TEX, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        r = artledger.install_image(dest, im, reason=REASON)
        print(r.get("status"), rel, im.size)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
