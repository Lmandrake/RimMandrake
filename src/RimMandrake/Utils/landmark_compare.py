"""Before/after contact sheet for the landmark repaints, over real world-map terrain.

Two sizes always, because they answer different questions: 128 px says whether the
craft is there, 64 px -- the size the globe actually draws -- says whether it reads.
An icon that only works at 128 is not finished.
"""
import csv, os, sys
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import landmark_icon_sheet as L                                     # noqa: E402
import landmark_art as A                                            # noqa: E402

REPO = L.REPO
NEW = os.path.join(REPO, "src/RimMandrake/AshkarrLandmarkArt/Textures/World/Landmarks/Ashkarr")
BG = os.path.join(REPO, "world/_landmark_terrain.png")


def sheet(out_png, names=None, big=170, cols=3):
    defs, idx = L.landmark_defs(), L.texture_index()
    counts = Counter(r["landmark"] for r in csv.DictReader(
        open(os.path.join(REPO, "world/ASHKARR_WORLDMAP_landmarks.csv"))))
    names = names or [n for n, _ in counts.most_common() if n in A.SPECS]
    names += [n for n in A.SPECS if n not in names]
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except OSError:
        f = fb = ImageFont.load_default()
    unit_w, unit_h = big * 2 + 74 + 30, big + 34
    W, H = cols * unit_w + 16, ((len(names) + cols - 1) // cols) * unit_h + 44
    bg = Image.open(BG).convert("RGB").resize((W, H)) if os.path.exists(BG) else None
    im = Image.new("RGBA", (W, H), (176, 164, 138, 255))
    if bg:
        im.paste(bg.convert("RGBA"))
    d = ImageDraw.Draw(im)
    d.text((10, 10), "Ash'karr landmark repaints — left: shipping icon · centre: repaint "
                     "· right: repaint at 64 px, true map size", font=fb, fill=(15, 15, 15))
    for i, n in enumerate(names):
        c, r = i % cols, i // cols
        x, y = 8 + c * unit_w, 34 + r * unit_h
        dd = defs.get(n)
        old = idx.get((dd["icon"] if dd else "").lower())
        for j, p in enumerate((old, f"{NEW}/{n}.png")):
            if p and os.path.exists(p):
                s0 = Image.open(p).convert("RGBA")
                cw = s0.size[0] // ((dd or {}).get("atlas") or (2, 2))[0]
                im.alpha_composite(s0.crop((0, 0, cw, cw)).resize((big, big), Image.LANCZOS),
                                   (x + j * (big + 6), y))
        s1 = Image.open(f"{NEW}/{n}.png").convert("RGBA")
        cw = s1.size[0] // ((dd or {}).get("atlas") or (2, 2))[0]
        for k in range(2):
            box = (k % 2) * cw, (k // 2) * cw, (k % 2 + 1) * cw, (k // 2 + 1) * cw
            im.alpha_composite(s1.crop(box).resize((64, 64), Image.LANCZOS),
                               (x + 2 * big + 14, y + k * 68))
        d.text((x, y + big + 2), f"{n}  ({counts.get(n, 0)} tiles) — {A.SPECS[n]['treat']}",
               font=f, fill=(15, 15, 15))
    im.convert("RGB").save(out_png)
    return out_png, names


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "TRANSIENT_landmark_compare.png"
    only = sys.argv[2:] or None
    p, names = sheet(out, only)
    print(p, len(names), "icons")
