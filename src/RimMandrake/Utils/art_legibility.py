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


def outline_coverage(im, target_px):
    """What fraction of the silhouette's outer ring is a LEGIBLE DARK OUTLINE
    at this render size? A ring pixel counts as outline when it is genuinely
    dark — near-black in absolute terms AND clearly darker than both the
    body and the terrain behind it (downscale blending lightens a surviving
    black line; pure `lum < 60` would call every 18px outline dead).
    Returns (coverage 0..1, boolean dark-ring map, mask) — the map is what
    the diagnostic overlay renders, so a human can SEE what was counted."""
    rgb, alpha = render_tier(im, target_px)
    lum = _lum(rgb)
    mask = alpha > ALPHA_SOLID
    if int(mask.sum()) < 4:
        return 0.0, np.zeros_like(mask), mask
    inner = _erode(mask)
    ring = (mask & ~_erode(inner)) if inner.sum() > 8 else (mask & ~inner)   # ~2px ring
    interior = _erode(inner) if inner.sum() > 8 else inner
    int_lum = float(lum[interior].mean()) if interior.any() else float(lum[mask].mean())
    dark = ring & (lum < 110) & (lum < int_lum - 20) & (lum < BG_LUM - 20)
    # coverage along the PERIMETER: a boundary position is covered if the
    # 2px ring holds a dark pixel there; approximate by dark-ring area over
    # single-boundary area, capped at 1.
    boundary = mask & ~inner
    nb = max(1, int(boundary.sum()))
    return min(1.0, float(dark.sum()) / nb), dark, mask


def tier_metrics(im, target_px, ref_outline_cov=None):
    """The four raw metrics at one tier, each normalized to 0..1.
    `ref_outline_cov` is the outline coverage measured at the 1:1 reference
    tier — when given, keyline is OUTLINE SURVIVAL: does the black rim the
    original art has still read here, like it does at 1:1? (Owner feedback,
    2026-09-13: 'look harder for the outer black outline being legible like
    the original art.')"""
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

    # keyline = the dark outer outline, measured directly. Absolute half:
    # how much of the ring is legible dark outline AT THIS SIZE (0.7
    # coverage = full marks). Survival half: that coverage relative to what
    # the SAME art shows at the 1:1 reference — an outline the original has
    # must not dissolve on the way down.
    cov, _, _ = outline_coverage(im, target_px)
    abs_part = min(1.0, cov / 0.7)
    if ref_outline_cov is not None and ref_outline_cov > 0.05:
        surv_part = min(1.0, cov / ref_outline_cov)
        keyline = 0.5 * abs_part + 0.5 * surv_part
    else:
        keyline = abs_part

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
            "outline_cov": round(cov, 4), "solid_px": n}


# ───────────────────────── metric zoo (ART_LEGIBILITY_GATE_1 follow-up) ─────
# Owner, 2026-09-13: "build MANY potential metrics and find out which ones
# correspond to my actual visual experience." Nothing here replaces the gate
# metrics above; the zoo exists to be CORRELATED against the owner's graded
# sheet, and the winners get promoted. Research grounding: DPID (Weber 2016),
# PixelOE outline expansion, classic Lanczos+unsharp, edge-F1 / SSIM /
# RMS-contrast / silhouette-IoU / HF-ratio candidates.

def _premultiplied(im):
    """Straight → premultiplied RGBA float array; zero RGB where alpha=0 so
    no baked background bleeds into a blur/resample (the classic trap)."""
    a = np.asarray(im, dtype=np.float32)
    al = a[..., 3:4] / 255.0
    return np.concatenate([a[..., :3] * al, a[..., 3:4]], axis=-1)


def _unpremultiply(arr):
    al = np.clip(arr[..., 3:4], 1e-6, 255.0) / 255.0
    rgb = np.clip(arr[..., :3] / al, 0, 255)
    return np.concatenate([rgb, arr[..., 3:4]], axis=-1).astype(np.uint8)


def render_processed(im, target_px, chain):
    """Alternate downscale chains, all alpha-correct (premultiplied space).
    chain: 'box' (the plain GPU-like path), 'unsharp' (Lanczos + unsharp
    mask), 'dpid' (detail-preserving weighted resample, λ=1)."""
    if chain == "box":
        return render_tier(im, target_px)
    w, h = im.size
    s = target_px / max(w, h)
    tw, thh = max(1, round(w * s)), max(1, round(h * s))
    pm = Image.fromarray(_premultiplied(im).astype(np.uint8), "RGBA")
    if chain == "unsharp":
        from PIL import ImageFilter
        small = pm.resize((tw, thh), Image.LANCZOS)
        small = small.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=0))
    elif chain == "dpid":
        src = np.asarray(pm, dtype=np.float32)
        base = np.asarray(pm.resize((tw, thh), Image.BOX), dtype=np.float32)
        guide = np.asarray(Image.fromarray(base.astype(np.uint8), "RGBA")
                           .resize((w, h), Image.BILINEAR), dtype=np.float32)
        dev = np.sqrt(((src - guide) ** 2).sum(axis=-1))          # per-pixel deviation
        wgt = 1.0 + dev / (dev.mean() + 1e-6)                     # λ≈1 boost for outliers
        acc = np.zeros((thh, tw, 4), np.float64)
        wacc = np.zeros((thh, tw, 1), np.float64)
        ys = (np.arange(h) * thh // h); xs = (np.arange(w) * tw // w)
        np.add.at(acc, (ys[:, None], xs[None, :]), src * wgt[..., None])
        np.add.at(wacc, (ys[:, None], xs[None, :]), wgt[..., None])
        small = Image.fromarray(np.clip(acc / np.maximum(wacc, 1e-6), 0, 255)
                                .astype(np.uint8), "RGBA")
    else:
        raise ValueError(chain)
    st = Image.fromarray(_unpremultiply(np.asarray(small, dtype=np.float32)), "RGBA")
    comp = Image.new("RGBA", st.size, BG + (255,))
    comp.alpha_composite(st)
    return np.asarray(comp.convert("RGB"), dtype=np.float32), \
        np.asarray(st.split()[-1], dtype=np.float32)


def _sobel_edges(lum, thresh):
    gy, gx = np.gradient(lum)
    mag = np.hypot(gx, gy)
    return mag > thresh


def _dilate(m):
    d = m.copy()
    d[1:, :] |= m[:-1, :]; d[:-1, :] |= m[1:, :]
    d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]
    return d


def zoo_metrics(im, target_px, ref_px=96, chain="box"):
    """MANY candidate metrics at one tier for one processing chain. The
    reference is the SAME art rendered at ref_px then area-resized to the
    tier's geometry — 'what a bigger view of this art shows, brought to this
    size' — so every comparison is self-referential, needing no external
    ground truth. Tuned for 32px-scale inputs (Sobel threshold 24, 1px edge
    tolerance; photo-tuned defaults find nothing at this size)."""
    rgb, alpha = (render_tier(im, target_px) if chain == "box"
                  else render_processed(im, target_px, chain))
    lum = _lum(rgb); mask = alpha > ALPHA_SOLID
    ref_rgb, ref_alpha = render_tier(im, ref_px)
    rH, rW = lum.shape
    ref_small = np.asarray(Image.fromarray(ref_rgb.astype(np.uint8))
                           .resize((rW, rH), Image.BOX), dtype=np.float32)
    ref_lum = _lum(ref_small)
    ref_mask = np.asarray(Image.fromarray((ref_alpha > ALPHA_SOLID))
                          .resize((rW, rH), Image.NEAREST))

    out = {}
    # 1. edge-map F1: did the reference's edges survive at this size?
    e_ref = _sobel_edges(ref_lum, 24); e_out = _sobel_edges(lum, 24)
    tp = float((e_out & _dilate(e_ref)).sum())
    prec = tp / max(1.0, float(e_out.sum()))
    rec = float((e_ref & _dilate(e_out)).sum()) / max(1.0, float(e_ref.sum()))
    out["edge_f1"] = round(2 * prec * rec / max(1e-6, prec + rec), 4)
    # 2. SSIM (single-scale, 5px gaussian-ish box) on luminance
    def _blur(a):
        k = np.ones((3, 3)) / 9.0
        from numpy.lib.stride_tricks import sliding_window_view
        p = np.pad(a, 1, mode="edge")
        return (sliding_window_view(p, (3, 3)) * k).sum(axis=(-1, -2))
    mu_x, mu_y = _blur(lum), _blur(ref_lum)
    var_x = _blur(lum * lum) - mu_x ** 2; var_y = _blur(ref_lum * ref_lum) - mu_y ** 2
    cov = _blur(lum * ref_lum) - mu_x * mu_y
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    ssim = ((2 * mu_x * mu_y + c1) * (2 * cov + c2)) / \
           ((mu_x ** 2 + mu_y ** 2 + c1) * (var_x + var_y + c2))
    out["ssim"] = round(float(ssim[mask].mean()) if mask.any() else 0.0, 4)
    # 3. RMS local contrast inside the silhouette
    local_sd = np.sqrt(np.maximum(var_x, 0))
    out["rms_contrast"] = round(float(local_sd[mask].mean()) / 64.0, 4) if mask.any() else 0.0
    # 4. silhouette IoU vs reference shape
    inter = float((mask & ref_mask).sum()); union = float((mask | ref_mask).sum())
    out["sil_iou"] = round(inter / max(1.0, union), 4)
    # 5. high-frequency energy retention
    gy, gx = np.gradient(lum); go = np.hypot(gx, gy)
    gy, gx = np.gradient(ref_lum); gr = np.hypot(gx, gy)
    out["hf_ratio"] = round(min(2.0, float(go[mask].mean() / max(1e-6, gr[ref_mask].mean()))
                            if mask.any() and ref_mask.any() else 0.0), 4)
    # 6-9. the gate's own four, on this chain's render — measured through the
    # same code path so chains are comparable
    m = tier_metrics(im, target_px, ref_outline_cov=outline_coverage(im, ref_px)[0])
    out.update({f"gate_{k}": m[k] for k in ("keyline", "structure", "ground", "coverage")})
    # 10. keyline v1 (the ORIGINAL contrast-based metric, kept per the owner)
    inner = _erode(mask); boundary = mask & ~inner
    interior = _erode(inner) if inner.sum() > 8 else inner
    int_lum = float(lum[interior].mean()) if interior.any() else (float(lum[mask].mean()) if mask.any() else 0.0)
    bnd_lum = float(lum[boundary].mean()) if boundary.any() else int_lum
    rim_dark = max(0.0, (int_lum - bnd_lum) / 96.0)
    rim_vs_bg = abs(bnd_lum - BG_LUM) / 128.0
    out["keyline_v1"] = round(min(1.0, 0.6 * min(1.0, rim_dark) + 0.4 * min(1.0, rim_vs_bg)), 4)
    return out


def cmd_zoo(args):
    """Compute the whole metric zoo (× processing chains) for files → JSON."""
    tiers = [int(t) for t in args.tiers.split(",")]
    chains = args.chains.split(",")
    rows = []
    for f in _collect(args.paths, args.glob):
        try:
            im = trim(Image.open(f).convert("RGBA"))
            row = {"path": f, "chains": {}}
            for ch in chains:
                row["chains"][ch] = {str(t): zoo_metrics(im, t, chain=ch)
                                     for t in tiers if t != 96}
            rows.append(row)
            print(f"zoo {os.path.basename(f)}")
        except Exception as e:
            print(f"  skip {f}: {e}")
    with open(args.json, "w") as fh:
        json.dump(rows, fh, indent=1)
    print(f"written: {args.json} ({len(rows)} files)")
    return 0


def score_file(path, tiers):
    """The LARGEST tier is the 1:1 reference: its outline coverage is what
    the zoom-out tiers' keyline-survival is measured against."""
    im = trim(Image.open(path).convert("RGBA"))
    out = {"path": path, "src": list(im.size), "tiers": {}}
    ref_tier = max(tiers)
    ref_cov, _, _ = outline_coverage(im, ref_tier)
    out["ref_outline_cov"] = round(ref_cov, 4)
    for t in tiers:
        m = tier_metrics(im, t, ref_outline_cov=(None if t == ref_tier else ref_cov))
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


def fitted_score(im, model, drawsize=1.0):
    """Score one sprite with the owner-grade-fitted linear model
    (legibility_model_fitted.json — ridge on the 2026-09-13 graded sheet,
    LOO Spearman +0.81 vs his works/borderline/mud). Returns (score, parts).

    `drawsize` scales the tier ladder to the creature's real on-screen size:
    the model's tiers are per-CELL (96/32/18 px for a 1-cell creature), so a
    drawSize-3 beast is judged at 3× those pixels — what the game actually
    shows — never at vermin size. Effective tiers cap at the source's own
    resolution (no upscale). The model was CALIBRATED at drawsize 1.0; for
    other sizes this is the principled approximation until a size-stratified
    regrading exists."""
    cache = {}
    total = model["intercept"]
    parts = {}
    src_px = max(im.size)
    for f in model["features"]:
        t_nominal = int(f["tier"])
        t = min(src_px, max(8, round(t_nominal * drawsize)))
        if t not in cache:
            cache[t] = zoo_metrics(im, t, chain="box")
        v = cache[t][f["metric"]]
        total += f["weight"] * (v - f["mean"]) / f["std"]
        parts[f"{f['metric']}@{f['tier']}"] = v
    return total, parts


def cmd_gate(args):
    """3-band verdict per the owner's 2026-09-13 rulings when a fitted model
    exists (exit 0 = pass, 3 = borderline/reinforce, 1 = mud/regen);
    threshold-file 2-band behavior otherwise (0/1)."""
    model = None
    if args.model and os.path.isfile(args.model):
        with open(args.model) as fh:
            model = json.load(fh)
    if model:
        im = trim(Image.open(args.path).convert("RGBA"))
        ds = max(0.2, float(getattr(args, "drawsize", 1.0) or 1.0))
        s, parts = fitted_score(im, model, drawsize=ds)
        detail = " ".join(f"{k}={v:.2f}" for k, v in sorted(parts.items())[:4])
        # Deterministic FLOORS under the fitted model (locked 2026-09-13).
        # The regression was trained only on real art; degenerate inputs sit
        # outside its manifold and can score high on coverage/ground alone —
        # measured: a flat featureless color block scored 2.84 (a clean pass).
        # Floors, checked before the fitted bands:
        #   structure AND contrast both ~zero  -> featureless: REGEN, always
        #     (an outline stroke would only make an outlined blob);
        #   both keyline metrics ~zero         -> no outline at all: at BEST
        #     borderline, so the stroke gets its chance but a pass is
        #     impossible without a rim.
        structure = parts.get("gate_structure@32", 1.0)
        contrast = parts.get("rms_contrast@32", 1.0)
        key_a = parts.get("keyline_v1@32", 1.0)
        key_b = parts.get("gate_keyline@32", 1.0)
        if structure < 0.05 and contrast < 0.05:
            print(f"LEGIBILITY FAIL floor: featureless (structure={structure:.2f}, "
                  f"rms_contrast={contrast:.2f}) — regenerate; fitted={s:.2f} ignored")
            return 1
        if key_a < 0.05 and key_b < 0.05 and s >= model["works_line"]:
            print(f"LEGIBILITY BORDERLINE floor: no outline at all "
                  f"(keyline_v1={key_a:.2f}, gate_keyline={key_b:.2f}) — a pass "
                  f"needs a rim; reinforce then rescore; fitted={s:.2f}")
            return 3
        if s >= model["works_line"]:
            print(f"LEGIBILITY PASS fitted={s:.2f} >= works {model['works_line']} ({detail})")
            return 0
        if s >= model["mud_line"]:
            print(f"LEGIBILITY BORDERLINE fitted={s:.2f} in [{model['mud_line']}, "
                  f"{model['works_line']}) — reinforce the keyline, then rescore ({detail})")
            return 3
        print(f"LEGIBILITY FAIL fitted={s:.2f} < mud {model['mud_line']} — regenerate ({detail})")
        return 1
    with open(args.thresholds) as fh:
        th = json.load(fh)
    tiers = [int(t) for t in th["tiers"]]
    r = score_file(args.path, tiers)
    fails = []
    for t in tiers:
        m = r["tiers"][str(t)]
        line = th["tiers"][str(t)]["gate"]
        if m["score"] < line:
            weakest = min(W, key=lambda k: m[k])
            fails.append(f"{t}px: score {m['score']} < gate {line} "
                         f"(weakest metric: {weakest}={m[weakest]})")
    if fails:
        print("LEGIBILITY FAIL " + "; ".join(fails))
        return 1
    print("LEGIBILITY PASS " + "  ".join(
        f"{t}px={r['tiers'][str(t)]['score']}" for t in tiers))
    return 0


def cmd_reinforce(args):
    """Synthetic keyline reinforcement, v2 — a real outline STROKE.

    v1 darkened only fully-solid ring pixels, palest first, and was invisible
    at play zoom (owner, 2026-09-13: "I literally can't see any difference")
    because the anti-aliased fringe — which dominates the downscaled edge —
    was untouched. v2 strokes the silhouette the way an artist would:

      - the stroke band spans the VISIBLE edge (any alpha > 16), from just
        inside the solid body to the outer fringe, width ~width_frac of body;
      - stroke pixels' RGB moves toward near-black by `strength`;
      - stroke pixels' alpha is SOLIDIFIED (raised toward opaque), so the
        downscale blends a real dark line instead of a translucent fringe.

    v3 (owner, 2026-09-13: v2's inward band "started to hurt... the black
    outline should be on the OUTSIDE of the original graphic"): the stroke is
    painted entirely OUTSIDE the existing silhouette — a black ring in the
    dilated region — and the ORIGINAL image is composited on top of it.
    Solid artwork pixels are byte-identical to before; the anti-aliased
    fringe blends over black instead of over terrain (which is what a drawn
    outline does); the silhouette grows by the stroke width. `strength` is
    the outline's opacity. Clips at the canvas border if the art has no
    margin — the stroke never resizes the canvas (drawSize maps to it)."""
    im = Image.open(args.path).convert("RGBA")
    arr = np.asarray(im, dtype=np.float32)
    alpha = arr[..., 3]
    vis = alpha > 16
    solid = alpha > ALPHA_SOLID
    if solid.sum() < 16:
        print("no solid silhouette — nothing to reinforce")
        return 1
    body = int(max(np.ptp(np.nonzero(solid)[0]), np.ptp(np.nonzero(solid)[1])))
    ring_w = max(1, round(body * args.width_frac))
    grown = vis.copy()
    for _ in range(ring_w):
        grown = _dilate(grown)
    k = float(np.clip(args.strength, 0.0, 1.0))
    # Deterministic margin check (locked 2026-09-13): the ring the stroke
    # WANTED is the dilation on an edge-padded copy; the ring it can HAVE is
    # the in-canvas dilation. Lost fraction above --max-clip-frac = exit 4,
    # a distinct routable failure ("insufficient margin"), never a silent
    # flat-sided outline.
    pad = ring_w + 1
    vis_p = np.pad(vis, pad)
    grown_p = vis_p.copy()
    for _ in range(ring_w):
        grown_p = _dilate(grown_p)
    wanted = int(grown_p.sum() - vis_p.sum())
    have = int(grown.sum() - vis.sum())
    clip_frac = 0.0 if wanted <= 0 else max(0.0, (wanted - have) / wanted)
    if clip_frac > args.max_clip_frac:
        print(f"INSUFFICIENT MARGIN: {clip_frac:.0%} of the outline ring falls "
              f"outside the canvas (limit {args.max_clip_frac:.0%}) — the master "
              f"needs ~{ring_w}px of transparent margin; regenerate with margin")
        return 4
    outline = np.zeros_like(arr)
    outline[..., :3] = 12.0                       # near-black
    outline[..., 3] = np.where(grown, 255.0 * k, 0.0)
    base = Image.fromarray(outline.astype(np.uint8), "RGBA")
    base.alpha_composite(im)                      # ORIGINAL art over the ring
    base.save(args.out)
    print(f"outside-stroked: ring {ring_w}px of {body}px body, opacity {k}, "
          f"ring clipped {clip_frac:.0%} -> {args.out}")
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
            ref_cov, _, _ = outline_coverage(stored, max(tiers))
            for t in tiers:
                m = tier_metrics(stored, t,
                                 ref_outline_cov=(None if t == max(tiers) else ref_cov))
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
    p.add_argument("--model", help="fitted model JSON; when present, 3-band verdict (0 pass / 3 reinforce / 1 regen)")
    p.add_argument("--drawsize", type=float, default=1.0,
                   help="creature drawSize in cells; scales the tier ladder to real on-screen size")
    p.set_defaults(fn=cmd_gate)
    p = sub.add_parser("reinforce")
    p.add_argument("path"); p.add_argument("--out", required=True)
    p.add_argument("--strength", type=float, default=1.0,
                   help="outline opacity 0..1 (owner-approved default 1.0, 2026-09-13)")
    p.add_argument("--width-frac", type=float, default=0.02,
                   help="outside ring width as a fraction of body size (approved 2%%)")
    p.add_argument("--max-clip-frac", type=float, default=0.05,
                   help="fail (exit 4) when more than this fraction of the ring is lost at the canvas edge")
    p.set_defaults(fn=cmd_reinforce)
    p = sub.add_parser("resexp"); common(p)
    p.add_argument("--stored", default="128,256,512")
    p.set_defaults(fn=cmd_resexp)
    p = sub.add_parser("zoo"); common(p)
    p.add_argument("--chains", default="box,unsharp,dpid")
    p.set_defaults(fn=cmd_zoo)

    args = ap.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
