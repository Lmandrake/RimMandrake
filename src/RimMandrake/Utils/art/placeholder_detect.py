#!/usr/bin/env python3
"""placeholder_detect.py — which census rows are drawn with PLACEHOLDER art (owner, 2026-10-05).

The Grey Sea sheet showed flat ellipses, cubes and vanilla cactus photos, and every gate counted them as "art of ours".
A row's live art is PLACEHOLDER when either holds:

  (a) FLAT   the texture is script-drawn: <= FLAT_MAX_COLOURS distinct colours (5-bit quantised, opaque pixels),
             >= FLAT_MIN_SMOOTH of neighbouring opaque pixels equal within 6/765, and >= FLAT_MIN_PIXELS opaque pixels.
  (b) BORROWED  the texPath depicts something else: a non-plant row (creature / fish / catch item) on a Things/Plant/*
             path, or an RM_/RSW_/RUT_ def whose texPath tail does not contain its own subject name AND the same
             texture is shared by 2+ distinct subjects, or sits under a vanilla-plant / vanilla-item folder.

    python3 src/RimMandrake/Utils/art/placeholder_detect.py sweep [--census PATH] [--out JSON]
    python3 src/RimMandrake/Utils/art/placeholder_detect.py file <png>...     GEOMETRIC verdict per file (exit 1 if any)
    python3 src/RimMandrake/Utils/art/placeholder_detect.py selftest

Library: classify_row(row, kind, shared) -> {"verdict": PLACEHOLDER|REAL|NONE|UNMEASURED, "reasons": [...]}.
A row with several body resources is PLACEHOLDER only when EVERY body resource is. UNMEASURED = the file could not
be found and the texPath rule did not fire; that is never read as REAL by sweep totals (printed separately).
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SRC = REPO / "src"
CENSUS = REPO / "Transient/biome_ffar/census.json"

# thresholds, calibrated 2026-10-05: Grey Sea script-drawn shapes read 1-3 colours / flat 0.91-1.00;
# 400 random real artpipe renders read min 12 colours, 1st percentile 74, flat <= 0.87, median 607 colours.
FLAT_MAX_COLOURS = 8
FLAT_MIN_SMOOTH = 0.85
FLAT_MIN_PIXELS = 300

VANILLA_FOLDERS = ("Things/Plant/", "Things/Item/ToxicMeat", "Things/Item/Resource/", "Things/Item/Special/")
OWN_TREE = re.compile(r"(^|/)(RM|RSW|RUT)_")
OWN_PREFIX = re.compile(r"^(RM|RSW|RUT)_")


def pixel_metrics(path):
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(path).convert("RGBA")).astype(int)
    m = a[..., 3] > 200
    n = int(m.sum())
    if n == 0:
        return {"n": 0, "ncol": 0, "smooth": 1.0}
    q = a[..., :3][m] >> 3
    ncol = len(np.unique(q[:, 0] * 1024 + q[:, 1] * 32 + q[:, 2]))
    g = a[..., :3].sum(-1)
    h = np.abs(g[:, 1:] - g[:, :-1])[m[:, 1:] & m[:, :-1]]
    v = np.abs(g[1:] - g[:-1])[m[1:] & m[:-1]]
    d = np.concatenate([h, v])
    smooth = float((d <= 6).mean()) if len(d) else 1.0
    return {"n": n, "ncol": int(ncol), "smooth": round(smooth, 3)}


def is_flat(m) -> bool:
    return m["n"] >= FLAT_MIN_PIXELS and m["ncol"] <= FLAT_MAX_COLOURS and m["smooth"] >= FLAT_MIN_SMOOTH


# ---- GEOMETRIC placeholder (owner, 2026-10-07 22:33 PDT: "make sure that at no time can geometric placeholder art
# ever remain a viable Variant or selection"). Stricter than FLAT: few hard colours AND one dominant colour AND a
# silhouette that IS a circle/ellipse/rectangle (optionally with a uniform outline). Calibrated 2026-10-07 over every
# PNG under src/**/Textures (8,434 files): the 21 FeverWood/Webwork circles read dom 0.859 / 2 colours / ellipse-IoU
# 1.00; solid-square stand-ins read dom 1.0 / rect-fill 1.0; the 50 other hits were all visibly flat shapes; low-colour
# real sprites (AloeVera 17-69 colours dom<=0.30, JadePlant 29-54, ScorchedStars 24-27 smooth<=0.895) never trip.
GEO_MAX_COLOURS = 8          # 5-bit-quantised distinct colours over opaque pixels
GEO_MIN_DOMINANT = 0.55      # share of opaque pixels in the single most common colour
GEO_MIN_SMOOTH = 0.90        # neighbouring opaque pixels equal within 6/765
GEO_MIN_ELLIPSE_IOU = 0.95   # silhouette vs its moment-matched ellipse
GEO_MIN_RECT_FILL = 0.95     # silhouette area / bounding box area


def _rgba(src):
    import io
    import numpy as np
    from PIL import Image
    if isinstance(src, (bytes, bytearray)):
        src = io.BytesIO(src)
    return np.asarray(Image.open(src).convert("RGBA")).astype(int)


def geometry_metrics(src) -> dict:
    """src: path, bytes or file object. Returns n, ncol, dominant, smooth, ellipse_iou, rect_fill."""
    import numpy as np
    a = _rgba(src)
    m = a[..., 3] > 128
    n = int(m.sum())
    if n == 0:
        return {"n": 0, "ncol": 0, "dominant": 1.0, "smooth": 1.0, "ellipse_iou": 0.0, "rect_fill": 0.0}
    q = a[..., :3][m] >> 3
    _, cnt = np.unique(q[:, 0] * 1024 + q[:, 1] * 32 + q[:, 2], return_counts=True)
    g = a[..., :3].sum(-1)
    d = np.concatenate([np.abs(g[:, 1:] - g[:, :-1])[m[:, 1:] & m[:, :-1]], np.abs(g[1:] - g[:-1])[m[1:] & m[:-1]]])
    ys, xs = np.nonzero(m)
    cy, cx = ys.mean(), xs.mean()
    ell_iou = 0.0
    if n >= 3:
        ev, evec = np.linalg.eigh(np.cov(np.vstack([ys - cy, xs - cx])))
        hh, ww = m.shape
        yy, xx = np.mgrid[:hh, :ww]
        dd = np.stack([yy - cy, xx - cx], -1) @ evec
        ell = (dd[..., 0] ** 2 / (4 * ev[0] + 1e-9) + dd[..., 1] ** 2 / (4 * ev[1] + 1e-9)) <= 1
        ell_iou = float((ell & m).sum() / max(1, (ell | m).sum()))
    box = (ys.max() - ys.min() + 1) * (xs.max() - xs.min() + 1)
    return {"n": n, "ncol": int(len(cnt)), "dominant": round(float(cnt.max() / n), 3),
            "smooth": round(float((d <= 6).mean()) if len(d) else 1.0, 3),
            "ellipse_iou": round(ell_iou, 3), "rect_fill": round(float(n / box), 3)}


def _quick_reject(a) -> bool:
    """Cheap pre-pass: True when the picture certainly is NOT a geometric placeholder (too few opaque pixels, too many
    colours or no dominant colour) — skips the silhouette fit for almost every real sprite."""
    import numpy as np
    m = a[..., 3] > 128
    n = int(m.sum())
    if n == 0:
        return True
    q = a[..., :3][m] >> 3
    _, cnt = np.unique(q[:, 0] * 1024 + q[:, 1] * 32 + q[:, 2], return_counts=True)
    return len(cnt) > GEO_MAX_COLOURS or cnt.max() / n < GEO_MIN_DOMINANT


def placeholder_reason(src):
    """None for real art; otherwise a one-line reason naming the shape. src: path, bytes or file object.
    Unreadable input raises (callers must treat that as UNMEASURED, never as real)."""
    import io
    from PIL import Image
    if isinstance(src, (bytes, bytearray)):
        src = io.BytesIO(src)
    im = Image.open(src).convert("RGBA")
    import numpy as np
    if int((np.asarray(im.getchannel("A")) > 128).sum()) < FLAT_MIN_PIXELS:   # judged at full size
        return None
    if max(im.size) > 256:      # NEAREST keeps the exact colours; the silhouette fit is scale-free
        im = im.resize((max(1, im.width * 256 // max(im.size)), max(1, im.height * 256 // max(im.size))), Image.NEAREST)
    if _quick_reject(np.asarray(im).astype(int)):
        return None
    b = io.BytesIO()
    im.save(b, "PNG")
    g = geometry_metrics(b.getvalue())
    if g["ncol"] > GEO_MAX_COLOURS or g["dominant"] < GEO_MIN_DOMINANT or g["smooth"] < GEO_MIN_SMOOTH:
        return None
    if g["ellipse_iou"] >= GEO_MIN_ELLIPSE_IOU:
        shape = "circle/ellipse"
    elif g["rect_fill"] >= GEO_MIN_RECT_FILL:
        shape = "rectangle"
    else:
        return None
    return (f"geometric placeholder: flat {shape}, {g['ncol']} colours, dominant {g['dominant']:.0%}, "
            f"ellipse-IoU {g['ellipse_iou']}, rect-fill {g['rect_fill']}")


def is_placeholder(src) -> bool:
    return placeholder_reason(src) is not None


def find_png(mod: str | None, res: str):
    """The picture the game draws for res: prefer _south, then bare, then any non-mask facing."""
    roots = [SRC / mod / "Textures"] if mod else []
    for r in roots + [p for p in SRC.glob("*/*/Textures")]:
        base = r / res
        if base.is_dir():  # Graphic_Random / Graphic_Collection: the folder is the texPath
            pngs = sorted(q for q in base.glob("*.png") if not q.stem.endswith("m"))
            if pngs:
                return pngs[0]
        for suf in ("_south", "", "_east", "_north", "_a", "A", "_0"):
            p = Path(str(base) + suf + ".png")
            if p.is_file():
                return p
    return None


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def subject_stem(defname: str) -> str:
    s = re.sub(r"^[A-Z]{2,4}_", "", defname)
    s = re.sub(r"(Catch|Fish|Item|Juv|Plant)$", "", s)
    s = re.sub(r"^Plant_", "", s)
    return norm(s)


def borrowed_reason(defname: str, kind: str, res: str, shared: dict):
    """(b). shared: res -> set of distinct subject stems drawing it across the census."""
    low = res
    if kind in ("fauna", "fish") and low.startswith("Things/Plant/"):
        return f"{kind} row on plant texPath {res}"
    if not OWN_PREFIX.match(defname):
        return None
    stem = subject_stem(defname)
    tail = norm(res.rsplit("/", 1)[-1])
    if stem and (stem in norm(res) or (len(tail) >= 4 and tail in stem)):
        return None
    if OWN_TREE.search(res) or not res.startswith("Things/"):
        return None  # our own folder (a deliberate family) or a donor mod's own tree: not a vanilla picture of something else
    if len(shared.get(res, ())) >= 2:
        return f"{defname} shares {res} with {len(shared[res]) - 1} other subject(s)"
    if any(res.startswith(v) for v in VANILLA_FOLDERS):
        return f"{defname} draws vanilla {res}"
    return None


def classify_row(row: dict, shared: dict) -> dict:
    kind = row.get("kind")
    dn = (row.get("defNames") or [row.get("key")])[0]
    bodies = [x for x in row["art"]["resources"] if x.get("role") == "body"] or row["art"]["resources"]
    if not bodies:
        return {"verdict": "NONE", "reasons": ["no body texPath"], "def": dn}
    per, reasons = [], []
    for x in bodies:
        res = x["res"]
        mod = ((x.get("live") or {}).get("mod"))
        why = []
        b = borrowed_reason(dn, kind, res, shared)
        if b:
            why.append("BORROWED: " + b)
        p = find_png(mod, res)
        met = pixel_metrics(p) if p else None
        if met and is_flat(met):
            why.append(f"FLAT: {met['ncol']} colours, smooth {met['smooth']}")
        elif p and is_placeholder(p):
            why.append("GEOMETRIC: " + placeholder_reason(p))
        per.append("PLACEHOLDER" if why else ("REAL" if met else "UNMEASURED"))
        reasons += [f"{res}: {w}" for w in why] or ([f"{res}: {met}"] if met else [f"{res}: file not found"])
    if all(v == "PLACEHOLDER" for v in per):
        v = "PLACEHOLDER"
    elif "REAL" in per:
        v = "REAL"
    else:
        v = "UNMEASURED"
    return {"verdict": v, "reasons": reasons, "def": dn}


def shared_map(census: dict) -> dict:
    sh = defaultdict(set)
    for b in census["biomes"].values():
        for r in b["rows"]:
            for x in r["art"]["resources"]:
                if x.get("role") == "body":
                    dn = (r.get("defNames") or [r["key"]])[0]
                    sh[x["res"]].add(subject_stem(dn))
    return sh


def sweep(census_path=CENSUS):
    census = json.load(open(census_path))
    sh = shared_map(census)
    out = {}
    for bd in census["biome_order"]:
        for r in census["biomes"][bd]["rows"]:
            c = classify_row(r, sh)
            c.update(kind=r.get("kind"), label=r.get("label"), biome=bd)
            out.setdefault(bd, []).append(c)
    return out


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    if cmd == "file":
        bad = 0
        for p in argv[1:]:
            r = placeholder_reason(p)
            bad += bool(r)
            print(("PLACEHOLDER " if r else "real        ") + str(p) + (f"  [{r}]" if r else ""))
        return 1 if bad else 0
    if cmd == "calibrate":
        import numpy as np
        res = sweep()
        pl, rl = [], []
        for rows in res.values():
            for x in rows:
                for rs in x["reasons"]:
                    pass
        census = json.load(open(CENSUS))
        for bd in census["biome_order"]:
            for r in census["biomes"][bd]["rows"]:
                for x in r["art"]["resources"]:
                    f = find_png((x.get("live") or {}).get("mod"), x["res"])
                    if f:
                        m = pixel_metrics(f)
                        (pl if is_flat(m) else rl).append(m)
        import glob
        art = [pixel_metrics(f) for f in glob.glob("/mnt/d/Luke/dev/_artpipe/_artsrc/*/*.png")[::6]]
        for name, ms in (("FLAT (live census)", pl), ("live census not flat", rl), ("artpipe real renders", art)):
            for k in ("ncol", "smooth"):
                v = np.array([m[k] for m in ms if m["n"] >= FLAT_MIN_PIXELS], float)
                if len(v):
                    print(f"{name:22} n={len(v):4} {k:6} min {v.min():8.3f} p5 {np.percentile(v,5):8.3f} median {np.median(v):8.3f} p95 {np.percentile(v,95):8.3f} max {v.max():8.3f}")
        return 0
    if cmd == "selftest":
        import selftest_placeholder_detect as T
        return T.run()
    if cmd == "sweep":
        cp = CENSUS
        outp = None
        if "--census" in argv:
            cp = Path(argv[argv.index("--census") + 1])
        if "--out" in argv:
            outp = Path(argv[argv.index("--out") + 1])
        res = sweep(cp)
        print(f"{'biome':26} rows  PLACEHOLDER  REAL  UNMEAS  NONE")
        for bd, rows in sorted(res.items(), key=lambda kv: -sum(r['verdict'] == 'PLACEHOLDER' for r in kv[1])):
            cnt = lambda v: sum(r["verdict"] == v for r in rows)
            print(f"{bd:26} {len(rows):4} {cnt('PLACEHOLDER'):8} {cnt('REAL'):9} {cnt('UNMEASURED'):6} {cnt('NONE'):6}")
        if outp:
            outp.write_text(json.dumps(res, indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
