#!/usr/bin/env python3
"""Census and before/after picture of the wall plug sweep (SelfTest/WallPlugChecks.cs).

    selftest_gimmesomeslack.py --no-export --wallplug-dump BEFORE.jsonl      (on the build before)
    selftest_gimmesomeslack.py --no-export --wallplug-dump AFTER.jsonl
    python3 wall_plug_sweep.py BEFORE.jsonl AFTER.jsonl OUT.png [N]

Prints how each build's cords leave their wall plugs (median, worst, over 3 degrees, by lay) and draws the N worst BEFORE cords of
different lays beside the same cord AFTER: the plug where the art draws it (0.72 scale, its boot at art u -0.102), the cord its
true width, the plug's axis dotted."""
import collections, json, math, os, sys
from PIL import Image, ImageDraw

PX, CORD = 170, 0.075
TEX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "Textures/RimMandrake/GimmeSomeSlack/Styles/ExtCord/Plug.png")


def load(p):
    rows = [json.loads(l) for l in open(p)]
    return {(r["scene"], i): r for r, i in zip(rows, _idx(rows))}


def _idx(rows):
    n = collections.Counter()
    for r in rows:
        n[r["scene"]] += 1
        yield n[r["scene"]]


def census(name, d):
    deg = sorted(r["deg"] for r in d.values())
    bad = [r for r in d.values() if r["deg"] > 3 or r["off"] > 0.02]
    print(f"{name}: {len(deg)} cords, median {deg[len(deg) // 2]:.1f}, worst {deg[-1]:.1f} deg; {len(bad)} over 3 deg or 0.02 cell")
    for k, v in collections.Counter((r["kind"], r["lay"]) for r in bad).most_common(8):
        print("   ", v, *k)


def draw(r):
    S = 2.2
    im = Image.new("RGBA", (int(S * PX), int(S * PX)), (96, 76, 54, 255))
    (tx, tz), (ux, uz) = r["T"], r["U"]
    c = (tx + ux * 0.45, tz + uz * 0.45)
    at = lambda x, z: ((x - c[0] + S / 2) * PX, (S / 2 - (z - c[1])) * PX)
    dr = ImageDraw.Draw(im)
    # the wall, from its face on (the boot stands 0.405 off a north face, 0.295 off a side's)
    back = 0.295 if abs(ux) > 0.5 else 0.405
    if r["kind"] == "wall outlet":
        back = 0.0
    fx, fz = tx - ux * back, tz - uz * back
    px, pz = -uz, ux
    dr.polygon([at(fx + px * 3, fz + pz * 3), at(fx - px * 3, fz - pz * 3), at(fx - px * 3 - ux * 3, fz - pz * 3 - uz * 3), at(fx + px * 3 - ux * 3, fz + pz * 3 - uz * 3)], fill=(40, 34, 28, 255))
    pts = [at(*p) for p in r["pts"]]
    w = int(CORD * PX)
    for col, ww in (((90, 22, 0, 255), w + 4), ((226, 78, 8, 255), w - 2)):
        dr.line(pts, fill=col, width=ww, joint="curve")
    if r["kind"] == "wall plug":
        sz = int(0.72 * PX)
        t = Image.open(TEX).convert("RGBA").resize((sz, sz)).rotate(math.degrees(math.atan2(-uz, -ux)), resample=Image.BICUBIC, expand=True)
        x, y = at(tx - ux * 0.102 * 0.72, tz - uz * 0.102 * 0.72)
        im.alpha_composite(t, (max(0, int(x - t.width / 2)), max(0, int(y - t.height / 2))))
    for k in range(0, 16):
        a, b = 0.02 + k * 0.05, 0.04 + k * 0.05
        dr.line([at(tx + ux * a, tz + uz * a), at(tx + ux * b, tz + uz * b)], fill=(255, 255, 255, 200), width=1)
    dr.text((4, 4), f"{r['scene']}\n{r['kind']}: {r['deg']:.1f} deg, {r['off']:.3f} off", fill=(255, 255, 255, 255))
    return im


def main(a):
    before, after = load(a[0]), load(a[1])
    census("before", before)
    census("after", after)
    n = int(a[3]) if len(a) > 3 else 6
    pick, seen = [], set()
    for k, r in sorted(before.items(), key=lambda x: -x[1]["deg"]):
        tag = (r["kind"], r["lay"], tuple(r["U"]))
        if k in after and tag not in seen and r["deg"] > 3:
            seen.add(tag)
            pick.append(k)
        if len(pick) == n:
            break
    tiles = [(draw(before[k]), draw(after[k])) for k in pick]
    w, h = tiles[0][0].size
    out = Image.new("RGB", (w * n, h * 2 + 6), (255, 255, 255))
    for i, (b, f) in enumerate(tiles):
        out.paste(b.convert("RGB"), (i * w, 0))
        out.paste(f.convert("RGB"), (i * w, h + 6))
    out.save(a[2])
    print("picture:", a[2], "(top row before, bottom row after)")


if __name__ == "__main__":
    main(sys.argv[1:])
