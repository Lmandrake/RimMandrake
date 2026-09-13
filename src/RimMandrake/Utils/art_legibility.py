#!/usr/bin/env python3
"""art_legibility.py — numeric downscale-legibility gate for sprite art.

art_zoom_sim.py is the EYE (a contact sheet a human judges); this is the
INSTRUMENT: it renders a sprite exactly the way the sim does — trim to the
drawn subject, BOX-downscale (~GPU mipmap, conservative) to an on-screen
tier height, composited over the Ash'karr desert brown — and then MEASURES
the three properties the frostmite pilot (2026-09-12) proved carry
legibility, instead of asking a human to squint:

  keyline   does a dark rim still trace the silhouette at this size?
            boundary-ring luminance vs interior luminance, and boundary
            contrast against the terrain behind it.
  structure does the interior keep a few bold shapes, or collapse to
            grey mud? mean luminance-gradient energy + luminance spread
            inside the silhouette AFTER the downscale.
  ground    does the body separate from a mid-tone ground? interior-vs-
            background luminance distance, plus the fraction of the body
            within camouflage distance of the terrain.
  coverage  do thin limbs survive at all? alpha area retained at the tier
            relative to the area the native silhouette predicts.

Composite score is 0-100 per tier. Weights are fixed; THRESHOLDS ARE NOT
GUESSED — they come from `calibrate` runs over known-shipping art (Alpha
Animals' loose 256² creatures) and live in a JSON the gate reads, so the
pass line is a measured property of art that ships, never an opinion.

Modes:
  score      score files/dirs at --tiers (default 96,32,18: the requested
             1:1 zoom-in plus two zoom-outs — owner, 2026-09-13)
  calibrate  score a corpus, print distribution + suggested thresholds JSON
  gate       score one file against a thresholds JSON; exit 1 on fail with
             reasons on stdout (the artpiped hook)
  resexp     the resolution experiment: for hi-res sources, build stored
             copies at --stored sizes (LANCZOS, the mod-shipping downscale),
             render each to the zoom-out tiers (BOX, the GPU path), and
             report score deltas + pixel RMSE between renders — measuring
             whether stored resolution above native buys ANY legibility at
             play zooms.

    python3 src/RimMandrake/Utils/art_legibility.py score path/a.png
    python3 src/RimMandrake/Utils/art_legibility.py calibrate --glob \
        "/mnt/c/.../Animal/*/*east.png" --out infrastructure/artpipe/legibility_thresholds.json
    python3 src/RimMandrake/Utils/art_legibility.py gate cand.png \
        --thresholds infrastructure/artpipe/legibility_thresholds.json
    python3 src/RimMandrake/Utils/art_legibility.py resexp big.png --stored 128,256,512
"""
import argparse
import glob as globmod
import json
import os
import sys

import numpy as np
from PIL import Image

# Same viewing model as art_zoom_sim.py — one instrument family, one truth.
BG = (150, 120, 85)                # Ash'karr desert brown
BG_LUM = 0.299 * BG[0] + 0.587 * BG[1] + 0.114 * BG[2]   # ~124.6
DEFAULT_TIERS = (96, 32, 18)       # 1:1-ish zoom-in + two zoom-outs (owner ruling)
ALPHA_SOLID = 127

# Fixed metric weights. Thresholds are calibrated, weights are definitional:
# keyline and structure are the two halves the pilot moved (30.8 -> 49.3);
# ground and coverage are the supporting cast.
W = {"keyline": 0.35, "structure": 0.30, "ground": 0.20, "coverage": 0.15}


def _lum(rgb):
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def trim(im):
    bb = im.split()[-1].getbbox()
    return im.crop(bb) if bb else im


def render_tier(im, target_px):
    """BOX-downscale the trimmed sprite to target height and composite over
    the terrain brown — byte-for-byte the sim's viewing condition."""
    w, h = im.size
    s = target_px / max(w, h)
    small = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.BOX)
    comp = Image.new("RGBA", small.size, BG + (255,))
    comp.alpha_composite(small)
    return np.asarray(comp.convert("RGB"), dtype=np.float32), \
        np.asarray(small.split()[-1], dtype=np.float32)


def _erode(mask):
    """4-neighbour erosion, pure numpy."""
    e = mask.copy()
    e[1:, :] &= mask[:-1, :]
    e[:-1, :] &= mask[1:, :]
    e[:, 1:] &= mask[:, :-1]
    e[:, :-1] &= mask[:, 1:]
    return e


def tier_metrics(im, target_px):
    """The four raw metrics at one tier, each normalized to 0..1."""
    rgb, alpha = render_tier(im, target_px)
    lum = _lum(rgb)
    mask = alpha > ALPHA_SOLID
    n = int(mask.sum())
    if n < 4:
        return {"keyline": 0.0, "structure": 0.0, "ground": 0.0,
                "coverage": 0.0, "solid_px": n}

    inner = _erode(mask)
    boundary = mask & ~inner
    interior = _erode(inner) if inner.sum() > 8 else inner

    # keyline: the boundary ring should be DARKER than the interior (a drawn
    # rim), and distinct from the terrain behind it. Both in 0..1.
    int_lum = float(lum[interior].mean()) if interior.any() else float(lum[mask].mean())
    bnd_lum = float(lum[boundary].mean()) if boundary.any() else int_lum
    rim_dark = max(0.0, (int_lum - bnd_lum) / 96.0)            # ~96 lum drop = full marks
    rim_vs_bg = abs(bnd_lum - BG_LUM) / 128.0
    keyline = min(1.0, 0.6 * min(1.0, rim_dark) + 0.4 * min(1.0, rim_vs_bg))

    # structure: gradient energy + luminance spread INSIDE the silhouette
    # after downscale — grey mud has neither.
    if interior.any() and interior.sum() > 8:
        gy, gx = np.gradient(lum)
        grad = np.hypot(gx, gy)
        g = float(grad[interior].mean()) / 48.0                # ~48 = busy vanilla art
        spread = float(lum[interior].std()) / 56.0
        structure = min(1.0, 0.5 * min(1.0, g) + 0.5 * min(1.0, spread))
    else:
        structure = 0.0

    # ground: body value must separate from a mid-tone ground.
    sep = abs(float(lum[mask].mean()) - BG_LUM) / 72.0
    camo = float((np.abs(lum[mask] - BG_LUM) < 14).mean())     # fraction that vanishes
    ground = min(1.0, max(0.0, 0.7 * min(1.0, sep) + 0.3 * (1.0 - camo)))

    # coverage: alpha area retained vs what the native silhouette predicts.
    w0, h0 = im.size
    native_alpha = np.asarray(im.split()[-1], dtype=np.float32) > ALPHA_SOLID
    scale = (max(1, round(max(w0, h0) * (target_px / max(w0, h0)))) / max(w0, h0)) ** 2
    expected = float(native_alpha.sum()) * scale
    coverage = min(1.0, n / expected) if expected > 0 else 0.0

    return {"keyline": round(keyline, 4), "structure": round(structure, 4),
            "ground": round(ground, 4), "coverage": round(coverage, 4),
            "solid_px": n}


def score_file(path, tiers):
    im = trim(Image.open(path).convert("RGBA"))
    out = {"path": path, "src": list(im.size), "tiers": {}}
    for t in tiers:
        m = tier_metrics(im, t)
        m["score"] = round(100.0 * sum(W[k] * m[k] for k in W), 1)
        out["tiers"][str(t)] = m
    return out


def _collect(paths, pattern):
    files = []
    for p in paths or []:
        if os.path.isdir(p):
            files += sorted(globmod.glob(os.path.join(p, "**", "*.png"), recursive=True))
        else:
            files.append(p)
    if pattern:
        files += sorted(globmod.glob(pattern))
    return [f for f in files if f.lower().endswith(".png")]


def cmd_score(args):
    tiers = [int(t) for t in args.tiers.split(",")]
    results = [score_file(f, tiers) for f in _collect(args.paths, args.glob)]
    for r in results:
        line = "  ".join(f"{t}px={r['tiers'][str(t)]['score']:5.1f}" for t in tiers)
        print(f"{line}   {os.path.basename(r['path'])} ({r['src'][0]}x{r['src'][1]})")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(results, fh, indent=1)
        print(f"written: {args.json}")
    return 0


def cmd_calibrate(args):
    tiers = [int(t) for t in args.tiers.split(",")]
    files = _collect(args.paths, args.glob)
    if len(files) < args.min_corpus:
        print(f"REFUSING to calibrate on {len(files)} files (< {args.min_corpus}): "
              f"a threshold from a tiny corpus is a guess wearing a number.")
        return 1
    per_tier = {t: [] for t in tiers}
    for f in files:
        try:
            r = score_file(f, tiers)
        except Exception as e:                      # corrupt/atlas pngs exist
            print(f"  skip {f}: {e}")
            continue
        for t in tiers:
            per_tier[t].append(r["tiers"][str(t)]["score"])
    th = {"corpus_n": len(files), "gate_pct": args.pct, "tiers": {}}
    for t in tiers:
        a = np.array(per_tier[t])
        # The gate line is a chosen percentile of SHIPPING art minus a small
        # margin. p10 admits the shipping corpus's own muddy tail (measured:
        # the pilot's known-bad frostmite passes a p10 line); p25 is where the
        # known-bad/known-good pilot pair separates. Calibrate, then CHECK the
        # line against known cases before trusting it.
        th["tiers"][str(t)] = {
            "p10": round(float(np.percentile(a, 10)), 1),
            "p25": round(float(np.percentile(a, 25)), 1),
            "p50": round(float(np.percentile(a, 50)), 1),
            "mean": round(float(a.mean()), 1),
            "min": round(float(a.min()), 1),
            "gate": round(float(np.percentile(a, args.pct)) - args.margin, 1),
        }
        print(f"{t:>3}px  n={len(a)}  min={a.min():5.1f}  p10={np.percentile(a,10):5.1f}  "
              f"p25={np.percentile(a,25):5.1f}  p50={np.percentile(a,50):5.1f}  "
              f"mean={a.mean():5.1f}  -> gate {th['tiers'][str(t)]['gate']}")
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(th, fh, indent=1)
        print(f"thresholds written: {args.out}")
    return 0


def cmd_gate(args):
    with open(args.thresholds) as fh:
        th = json.load(fh)
    tiers = [int(t) for t in th["tiers"]]
    r = score_file(args.path, tiers)
    fails = []
    for t in tiers:
        m = r["tiers"][str(t)]
        line = th["tiers"][str(t)]["gate"]
        if m["score"] < line:
            worst = min(W, key=lambda k: m[k] * W[k] / max(W[k], 1e-9))
            weakest = min(W, key=lambda k: m[k])
            fails.append(f"{t}px: score {m['score']} < gate {line} "
                         f"(weakest metric: {weakest}={m[weakest]})")
    if fails:
        print("LEGIBILITY FAIL " + "; ".join(fails))
        return 1
    print("LEGIBILITY PASS " + "  ".join(
        f"{t}px={r['tiers'][str(t)]['score']}" for t in tiers))
    return 0


def cmd_resexp(args):
    """Does stored resolution above native buy legibility at play zooms?
    For each hi-res source: store it at each --stored size (LANCZOS, how a
    mod would ship it), render every stored copy to each zoom-out tier (BOX,
    how the GPU shows it), then compare scores and pixels."""
    tiers = [int(t) for t in args.tiers.split(",")]
    stored_sizes = [int(s) for s in args.stored.split(",")]
    files = _collect(args.paths, args.glob)
    rows = []
    for f in files:
        im = trim(Image.open(f).convert("RGBA"))
        if max(im.size) < max(stored_sizes):
            print(f"  skip {os.path.basename(f)}: source {max(im.size)}px < "
                  f"largest stored size {max(stored_sizes)}")
            continue
        row = {"path": f, "src_px": max(im.size), "stored": {}}
        renders = {}
        for s in stored_sizes:
            sc = s / max(im.size)
            stored = im.resize((max(1, round(im.width * sc)),
                                max(1, round(im.height * sc))), Image.LANCZOS)
            entry = {}
            for t in tiers:
                m = tier_metrics(stored, t)
                m["score"] = round(100.0 * sum(W[k] * m[k] for k in W), 1)
                entry[str(t)] = m["score"]
                renders[(s, t)] = render_tier(stored, t)[0]
            row["stored"][str(s)] = entry
        # pixel RMSE between the largest and each smaller stored copy, per tier
        big = max(stored_sizes)
        row["rmse_vs_largest"] = {}
        for s in stored_sizes:
            if s == big:
                continue
            for t in tiers:
                a, b = renders[(s, t)], renders[(big, t)]
                if a.shape != b.shape:
                    continue
                row["rmse_vs_largest"][f"{s}@{t}"] = round(
                    float(np.sqrt(((a - b) ** 2).mean())), 2)
        rows.append(row)
        scores = "  ".join(
            f"[{s}px] " + " ".join(f"{t}:{row['stored'][str(s)][str(t)]:.0f}"
                                   for t in tiers)
            for s in stored_sizes)
        print(f"{os.path.basename(f)} src={row['src_px']}  {scores}  "
              f"rmse={row['rmse_vs_largest']}")
    if not rows:
        print("no usable hi-res sources — nothing proven either way (UNMEASURED).")
        return 1
    # Aggregate verdict material
    for t in tiers:
        for s in stored_sizes:
            a = np.array([r["stored"][str(s)][str(t)] for r in rows])
            print(f"AGG stored={s:>4}px tier={t:>3}px  mean={a.mean():5.1f}  "
                  f"p50={np.percentile(a,50):5.1f}")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(rows, fh, indent=1)
        print(f"written: {args.json}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("paths", nargs="*")
        p.add_argument("--glob")
        p.add_argument("--tiers", default=",".join(map(str, DEFAULT_TIERS)))
        p.add_argument("--json")

    p = sub.add_parser("score"); common(p); p.set_defaults(fn=cmd_score)
    p = sub.add_parser("calibrate"); common(p)
    p.add_argument("--out"); p.add_argument("--margin", type=float, default=3.0)
    p.add_argument("--pct", type=float, default=25.0,
                   help="corpus percentile the gate sits at (minus margin)")
    p.add_argument("--min-corpus", type=int, default=40)
    p.set_defaults(fn=cmd_calibrate)
    p = sub.add_parser("gate")
    p.add_argument("path"); p.add_argument("--thresholds", required=True)
    p.set_defaults(fn=cmd_gate)
    p = sub.add_parser("resexp"); common(p)
    p.add_argument("--stored", default="128,256,512")
    p.set_defaults(fn=cmd_resexp)

    args = ap.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
