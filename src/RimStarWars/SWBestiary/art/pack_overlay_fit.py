#!/usr/bin/env python3
"""pack_overlay_fit.py -- fit the four shared loaded-pack overlays onto every packAnimal body
(PACK_OVERLAYS_BUILD_SHARED_SADDLEBAGS).

    python3 src/RimStarWars/SWBestiary/art/pack_overlay_fit.py sheet --out <dir>   # composites to look at
    python3 src/RimStarWars/SWBestiary/art/pack_overlay_fit.py plan                # what would be written
    python3 src/RimStarWars/SWBestiary/art/pack_overlay_fit.py --apply             # write through the art ledger

Engine (PawnRenderNode_AnimalPack.GraphicFor): the pack is Graphic_Multi at <body path>+"Pack", on the
body's own quad, Cutout shader, white, drawn over the body. So a plain copy of one 512 canvas would sit
at a different place on every animal: the fit reads each body facing's silhouette and places the shared
gear on its back and flanks, in that body's own canvas. Alpha is binarised because Cutout clips anyway.

Waived (item text): juvenile `_j` and `*_Swimming` bodies keep their transparent placeholder.
Kept: existing drawn Pack art (real_pack_exists) is left alone. Ronto's Pack is a byte copy of the body,
the very defect, so it is replaced.

Sources are the artpipe renders packoverlay_<group>_v1_<facing>, read from the artpipe state dir.
"""
import argparse
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
GROUPS = os.path.join(HERE, "pack_overlay_groups.json")
FACINGS = ("east", "south", "north")
PLACEHOLDER_MAX_BYTES = 200
MIN_CANVAS = 512

# per group: gear width as a share of the torso (east), cap on the south/north scale relative to east,
# how far the gear's top rides above the torso top as a share of its height (side, front).
LAYOUT = {
    "quadruped": dict(side=0.84, front_cap=1.15, ride_side=0.08, ride_front=0.10, cut=1.0),
    "biped": dict(side=0.95, front_cap=1.15, ride_side=0.08, ride_front=0.10, cut=1.0),
    "sixlegged": dict(side=0.84, front_cap=1.15, ride_side=0.16, ride_front=0.18, cut=0.45),
    "lowlong": dict(side=0.80, front_cap=1.10, ride_side=0.14, ride_front=0.12, cut=0.0),
}


def art_state():
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils", "artpipe"))
    import state_dir
    return str(state_dir.resolve())


def _parse():
    things, kinds = {}, {}
    for path in glob.glob(os.path.join(ROOT, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for el in root:
            if el.tag not in ("ThingDef", "PawnKindDef"):
                continue
            bucket = things if el.tag == "ThingDef" else kinds
            if el.findtext("defName"):
                bucket[("def", el.findtext("defName"))] = el
            if el.get("Name"):
                bucket[("name", el.get("Name"))] = el
    return things, kinds


def _chain(el, bucket):
    out = []
    while el is not None and len(out) < 20:
        out.append(el)
        parent = el.get("ParentName")
        el = bucket.get(("name", parent)) if parent else None
    return out


def census():
    """[(race, texPath)] for every body/female graphic of every packAnimal race in src/."""
    things, kinds = _parse()

    def is_pack(el):
        for e in _chain(el, things):
            v = e.findtext("race/packAnimal")
            if v is not None:
                return v.strip().lower() == "true"
        return False
    pack = {k[1] for k, v in things.items() if k[0] == "def" and is_pack(v)}
    seen = set()
    for key, el in kinds.items():
        if key[0] != "def":
            continue
        chain = _chain(el, kinds)
        race = next((c.findtext("race") for c in chain if c.findtext("race")), None)
        if race not in pack:
            continue
        for c in chain:
            for li in c.findall("lifeStages/li"):
                for tag in ("bodyGraphicData", "femaleGraphicData"):
                    t = li.findtext(tag + "/texPath")
                    if t:
                        seen.add((race, t.strip()))
    return sorted(seen)


def tex_root(tex):
    for root in sorted(glob.glob(os.path.join(ROOT, "src", "*", "*", "Textures"))):
        if glob.glob(os.path.join(root, tex + "_south.png")) or os.path.isfile(os.path.join(root, tex + ".png")):
            return root
    return None


def waived(tex):
    leaf = tex.rsplit("/", 1)[-1]
    return leaf.endswith("_j") or "_Swimming" in leaf


def body_image(root, tex, facing):
    p = os.path.join(root, tex + "_%s.png" % facing)
    if not os.path.isfile(p):
        p = os.path.join(root, tex + ".png")       # Graphic_Single body
    img = Image.open(p).convert("RGBA")
    if img.width < MIN_CANVAS:                     # the same quad either way; the gear stays crisp
        k = MIN_CANVAS / img.width
        img = img.resize((MIN_CANVAS, int(img.height * k)), Image.BICUBIC)
    return img


def _erode(m):
    return (m & np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))


def _dilate(m):
    return (m | np.roll(m, 1, 0) | np.roll(m, -1, 0) | np.roll(m, 1, 1) | np.roll(m, -1, 1))


def _largest(m):
    seen = np.zeros(m.shape, bool)
    best = None
    for y0, x0 in zip(*np.nonzero(m)):
        if seen[y0, x0]:
            continue
        stack, cells = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            cells.append((y, x))
            for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= ny < m.shape[0] and 0 <= nx < m.shape[1] and m[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        if best is None or len(cells) > len(best):
            best = cells
    return best


def torso(img):
    """Bbox of the trunk in canvas pixels: thin limbs, necks, tails, horns and wing tips are opened away
    on a 128 px mask, then the largest piece left is the trunk."""
    W, H = img.size
    k = W / 128.0
    a = np.array(img.getchannel("A").resize((128, int(H / k)), Image.BILINEAR)) > 128
    ys, xs = np.nonzero(a)
    span = max(xs.max() - xs.min(), ys.max() - ys.min()) + 1
    box = (xs.min(), xs.max() + 1, ys.min(), ys.max() + 1)
    for frac in (0.11, 0.08, 0.05, 0.03):
        r = max(1, int(span * frac))
        m = a.copy()
        for _ in range(r):
            m = _erode(m)
        if not m.any():
            continue
        for _ in range(r):
            m = _dilate(m)
        cells = np.array(_largest(m & a))
        box = (cells[:, 1].min(), cells[:, 1].max() + 1, cells[:, 0].min(), cells[:, 0].max() + 1)
        break
    return tuple(int(v * k) for v in box)


def binarise(img):
    arr = np.array(img)
    arr[..., 3] = np.where(arr[..., 3] >= 128, 255, 0)
    return Image.fromarray(arr, "RGBA")


def gear(over):
    return over.crop(over.getchannel("A").getbbox())


def side_scale(crop, body, group, ov):
    x0, x1, y0, y1 = torso(body)
    L = LAYOUT[group]
    s = (x1 - x0) * ov.get("w", L["side"]) / crop.width
    return min(s, (y1 - y0) * 1.15 / crop.height)


def fit_side(over, body, group, ov):
    crop = gear(over)
    x0, x1, y0, y1 = torso(body)
    L = LAYOUT[group]
    s = side_scale(crop, body, group, ov) * ov.get("s", 1.0)
    tw, th = max(8, int(crop.width * s)), max(8, int(crop.height * s))
    cx = x0 + ov.get("cx", 0.46) * (x1 - x0)
    left, top = int(cx - tw / 2), int(y0 - ov.get("top", L["ride_side"]) * th)
    out = Image.new("RGBA", body.size, (0, 0, 0, 0))
    out.paste(binarise(crop.resize((tw, th), Image.LANCZOS)), (left, top))
    return out


def fit_front(over, body, group, s_side, ov):
    """South/north: bags on the flanks. The bridge strap is cut (`cut` = share of the height, measured
    from the bottom, that loses its middle) so nothing crosses the animal's face."""
    L = LAYOUT[group]
    crop = gear(over)
    x0, x1, y0, y1 = torso(body)
    a = np.array(crop)
    w, h = a.shape[1], a.shape[0]
    if L["cut"]:
        a[int(h * (1 - L["cut"])):, int(w * 0.40):int(w * 0.60), 3] = 0
    crop = Image.fromarray(a, "RGBA")
    s = min((x1 - x0) * ov.get("w", 1.04) / w, s_side * L["front_cap"]) * ov.get("s", 1.0)
    tw, th = max(8, int(w * s)), max(8, int(h * s))
    small = crop.resize((tw, th), Image.LANCZOS)
    top = int(y0 - ov.get("top", L["ride_front"]) * th)
    out = Image.new("RGBA", body.size, (0, 0, 0, 0))
    cx = x0 + ov.get("cx", 0.5) * (x1 - x0)
    if L["cut"] == 1.0:
        half = tw // 2
        reach = (x1 - x0) * ov.get("reach", 0.94) / 2
        alpha = np.array(body.getchannel("A")) > 128

        def local_top(left, right):
            if ov.get("flat"):
                return y0
            cols = alpha[:, max(0, left):right]
            tops = [int(np.argmax(c)) for c in cols.T if c.any()]
            return max(y0, int(np.median(tops))) if tops else y0
        ride = ov.get("top", L["ride_front"]) * th
        lx, rx = int(cx - reach), int(cx + reach - (tw - half))
        out.paste(binarise(small.crop((0, 0, half, th))), (lx, int(local_top(lx, lx + half) - ride)))
        out.paste(binarise(small.crop((half, 0, tw, th))), (rx, int(local_top(rx, rx + tw - half) - ride)))
    else:
        out.paste(binarise(small), (int(cx - tw / 2), top))
    return out


def fitted():
    """texPaths this tool installed, from its own committed list."""
    p = os.path.join(HERE, "pack_overlay_installed.json")
    if not os.path.isfile(p):
        return set()
    with open(p, encoding="utf-8") as fh:
        return set(json.load(fh))


def raw_body(root, tex, facing):
    """The body picture on disk, at its own size; a Graphic_Single body answers every facing."""
    p = os.path.join(root, tex + "_%s.png" % facing)
    return Image.open(p if os.path.isfile(p) else os.path.join(root, tex + ".png")).convert("RGBA")


def is_single(root, tex):
    return not os.path.isfile(os.path.join(root, tex + "_south.png"))


def drawn_pack(root, tex, facing):
    """A drawn Pack there stays. A placeholder or a byte copy of the body is not drawn art."""
    p = os.path.join(root, tex + "Pack_%s.png" % facing)
    if not os.path.isfile(p) or os.path.getsize(p) < PLACEHOLDER_MAX_BYTES:
        return False
    return not np.array_equal(np.array(Image.open(p).convert("RGBA")), np.array(raw_body(root, tex, facing)))


def real_pack_exists(root, tex):
    return all(drawn_pack(root, tex, f) for f in FACINGS + (("west",) if is_single(root, tex) else ()))


def targets(refit=False):
    """Graphics owed. `refit` also takes back what this tool already drew, never another's drawn art."""
    with open(GROUPS, encoding="utf-8") as fh:
        cfg = json.load(fh)
    by_race = {r: g for g, rs in cfg["groups"].items() for r in rs}
    rows = []
    for race, tex in census():
        root = tex_root(tex)
        if root is None or waived(tex):
            continue
        if real_pack_exists(root, tex) and not (refit and tex in fitted()):
            continue
        rows.append((race, tex, by_race[race], root, cfg["overrides"].get(tex, {})))
    return rows


def overlays(state):
    out = {}
    for group in LAYOUT:
        for f in FACINGS:
            n = "packoverlay_%s_v1_%s" % (group, f)
            out[group, f] = Image.open(os.path.join(state, "_artsrc", n, n + ".png")).convert("RGBA")
    return out


def render(row, overs):
    race, tex, group, root, ov = row
    res = {}
    single = is_single(root, tex)
    body = body_image(root, tex, "east")
    s_side = side_scale(gear(overs[group, "east"]), body, group, ov.get("east", {}))
    side = fit_side(overs[group, "east"], body, group, ov.get("east", {}))
    res["east"] = (body, side)
    for f in ("south", "north"):
        b = body_image(root, tex, f)
        # a Graphic_Single body never turns, so its pack is the side view on every facing
        res[f] = (b, side.copy() if single else fit_front(overs[group, f], b, group, s_side, ov.get(f, {})))
    if single:                                     # Graphic_Multi would flip east for west; the body does not
        res["west"] = (body, side.copy())
    return res


def sheet(outdir, overs, per=14, cell=170, only=None):
    os.makedirs(outdir, exist_ok=True)
    rows = [r for r in targets(True) if not only or any(o in r[1] for o in only)]
    n = 0
    for i in range(0, len(rows), per):
        chunk = rows[i:i + per]
        cols = 2
        H = ((len(chunk) + 1) // 2) * cell
        S = Image.new("RGB", (cols * 3 * cell, H), (150, 140, 120))
        for j, row in enumerate(chunk):
            res = render(row, overs)
            for k, f in enumerate(FACINGS):
                body, pack = res[f]
                c = body.copy()
                c.alpha_composite(pack)
                c = c.resize((cell, cell), Image.LANCZOS)
                S.paste(c, ((j % 2) * 3 * cell + k * cell, (j // 2) * cell), c)
        n += 1
        p = os.path.join(outdir, "fit_%02d.png" % n)
        S.save(p)
        print(p, [r[1].rsplit("/", 1)[-1] for r in chunk])


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", nargs="?", default="plan", choices=("plan", "sheet"))
    ap.add_argument("--out")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--export", help="write PNGs here for `art.py install` (a kept slot refuses the script path)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--refit", action="store_true", help="redo graphics this tool already fitted")
    args = ap.parse_args(argv)
    overs = overlays(art_state())
    if args.verb == "sheet" and not args.apply:
        sheet(args.out, overs, only=args.only)
        return 0
    rows = [r for r in targets(args.refit) if not args.only or any(o in r[1] for o in args.only)]
    print("%d graphics, %d facing files" % (len(rows), sum(4 if is_single(r[3], r[1]) else 3 for r in rows)))
    if args.export:
        os.makedirs(args.export, exist_ok=True)
        for row in rows:
            for f, (_b, pack) in render(row, overs).items():
                pack.save(os.path.join(args.export, row[1].rsplit("/", 1)[-1] + "Pack_%s.png" % f), optimize=True)
        return 0
    if not args.apply:
        for r in rows:
            print("  %-22s %-10s %s" % (r[0], r[2], r[1]))
        return 0
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils", "art"))
    from artwrite import TextureWriter
    import io
    tw = TextureWriter(__file__, provenance={"item": "PACK_OVERLAYS_BUILD_SHARED_SADDLEBAGS",
                                             "why": "delegated: art"})
    ours = fitted()
    mixed = set()
    for row in rows:
        for f, (_body, pack) in render(row, overs).items():
            if row[1] not in ours and drawn_pack(row[3], row[1], f):
                mixed.add(row[1])                  # someone's drawn facing beside a missing one: never ours
                continue
            buf = io.BytesIO()
            pack.save(buf, "PNG", optimize=True)
            tw.put(buf.getvalue(), os.path.join(row[3], row[1] + "Pack_%s.png" % f))
    done = sorted(ours | ({r[1] for r in rows} - mixed))
    with open(os.path.join(HERE, "pack_overlay_installed.json"), "w", encoding="utf-8") as fh:
        json.dump(done, fh, indent=0)
        fh.write("\n")
    return 1 if tw.report() else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
