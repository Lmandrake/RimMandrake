#!/usr/bin/env python3
"""flier_frame_registration.py - READ-ONLY audit: does the rigid BODY hold still across a flier's flip-book frames?

FLIER_FRAMES_AUDIT_BODY_NOT_WING_EXTREMES (owner 2026-10-20): bodies stay static while wings flap; the image
extremes (alpha bbox) must not drive registration. For every PawnKindDef with flyingAnimationFramePathPrefix this
finds `<prefix><N>_<north|east|south>.png`, derives the rigid body per frame, and reports its drift.

BODY MASK: alpha > ALPHA, then a morphological OPENING with a square of side k = 2*round(OPEN_FRAC*sqrt(area))+1
(thin wings, tails and legs are thinner than k and vanish), then the largest 4-connected component. Drift is
measured on that body's centroid and bbox centre. The ALPHA-BBOX CENTRE is also reported - the WRONG metric, kept
only to show how much a bbox-registering tool would move the body.

  body_drift_px     max centroid distance between any two frames of a facing (span), worst facing
  step_px           max centroid distance between consecutive frames (loop wrap included)
  body_frac         body_drift_px / body size (median body bbox major side)
  bbox_drift_px     same span, on the alpha-bbox centre (wrong metric)
  open_px           the opening-centroid span (cross-check; unstable for multi-part bodies)
  body_px/step_px   are the MASK-OVERLAP registration span/step (mask_shift: the translation that maximises each
                    frame's opened-body overlap with frame 1's). Primary figure. col_px/col% = colour-match
                    registration (match_shift) and its worst matched share: only trustworthy when col% is high
                    (repainted frames share no pixel colours, so it then locks onto noise).

Verdict: OFFENDER when span >= OFFEND_PX and >= OFFEND_FRAC of body size; MARGINAL at >= HALF of both; else OK.
Sets with no frame files in the repo are MISSING. Single-frame sets are SINGLE (no animation, nothing to jitter). Never writes art. Usage:
  flier_frame_registration.py [--json OUT.json] [--strip-dir DIR] [--worst 3] [--set Name_substr]
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[4]
ALPHA = 127
OPEN_FRAC = 0.10
KEEP_FRAC = 0.25
OFFEND_PX, OFFEND_FRAC = 2.0, 0.02
DIRS = ("north", "east", "south")


def _box_sum(m: np.ndarray, k: int) -> np.ndarray:
    """Sum of m over every k x k window (valid positions only) via an integral image."""
    c = np.pad(m.astype(np.int32), ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    return c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]


def opening(m: np.ndarray, k: int) -> np.ndarray:
    """Binary opening with a k x k square: erode (all window pixels set), then dilate back."""
    if k <= 1:
        return m.copy()
    h, w = m.shape
    pad = k // 2
    p = np.pad(m, pad)
    er = _box_sum(p, k) == k * k                    # shape (h, w): window centred on each pixel
    pe = np.pad(er, pad)
    return _box_sum(pe, k) > 0


def largest_component(m: np.ndarray, keep_frac: float = 0.0) -> np.ndarray:
    """The largest 4-connected component; with keep_frac > 0, every component at least that fraction of the largest
    (a body of head + thorax + abdomen opens into several blobs, and the biggest one flips between frames)."""
    h, w = m.shape
    lab = np.zeros((h, w), np.int32)
    best, best_n, n = 0, 0, 0
    sizes = {}
    for sy, sx in zip(*np.nonzero(m)):
        if lab[sy, sx]:
            continue
        n += 1
        stack, cnt = [(sy, sx)], 0
        lab[sy, sx] = n
        while stack:
            y, x = stack.pop()
            cnt += 1
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n
                    stack.append((ny, nx))
        sizes[n] = cnt
        if cnt > best_n:
            best, best_n = n, cnt
    if not best:
        return np.zeros_like(m)
    keep = [i for i, c in sizes.items() if c >= max(keep_frac * best_n, 1) and (keep_frac > 0 or i == best)]
    return np.isin(lab, keep)


def body_of(alpha: np.ndarray, open_frac: float = OPEN_FRAC) -> np.ndarray:
    m = alpha > ALPHA
    area = int(m.sum())
    if area == 0:
        return m
    f = open_frac
    while True:                                  # a slim body can vanish under the opening: halve it until something stays
        k = 2 * int(round(f * np.sqrt(area))) + 1
        out = largest_component(opening(m, k), KEEP_FRAC)
        if out.any() or k <= 3:
            return out if out.any() else m
        f /= 2


def stats(m: np.ndarray) -> dict | None:
    ys, xs = np.nonzero(m)
    if not len(ys):
        return None
    return {"cx": float(xs.mean()), "cy": float(ys.mean()),
            "bx": (xs.min() + xs.max()) / 2.0, "by": (ys.min() + ys.max()) / 2.0,
            "major": int(max(xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)), "area": int(len(ys))}


def _span(pts: list[tuple[float, float]]) -> float:
    return max((np.hypot(a[0] - b[0], a[1] - b[1]) for a in pts for b in pts), default=0.0)


def _step(pts: list[tuple[float, float]]) -> float:
    n = len(pts)
    return max((np.hypot(pts[i][0] - pts[(i + 1) % n][0], pts[i][1] - pts[(i + 1) % n][1]) for i in range(n)), default=0.0)


MATCH_L1 = 60          # RGB L1 (sum of 3 channels) under which two opaque pixels count as the same body pixel


def _score(ref, fr, dx, dy):
    """Pixels of FR shifted by (dx, dy) that sit on an opaque REF pixel of near-equal colour."""
    h, w = ref.shape[:2]
    r = ref[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)]
    f = fr[max(0, -dy):h - max(0, dy), max(0, -dx):w - max(0, dx)]
    both = (r[..., 3] > ALPHA) & (f[..., 3] > ALPHA)
    return int((both & (np.abs(r[..., :3].astype(np.int16) - f[..., :3]).sum(-1) <= MATCH_L1)).sum())


def match_shift(ref: np.ndarray, fr: np.ndarray, radius_frac: float = 0.2) -> tuple[tuple[int, int], float]:
    """Translation (dx, dy) that lays FR's colour-matching pixels over REF's, wings being the pixels that do not
    match: coarse search on a downscale, then a full-resolution refine. Returns (shift, matched share of REF's
    opaque area). This is the body-anchored measurement (cf. flyer_lock.align); it needs no body mask at all."""
    h, w = ref.shape[:2]
    f = max(1, w // 128)
    if f > 1:
        small = lambda a: np.asarray(Image.fromarray(a).resize((w // f, h // f), Image.BOX))
        rs, fs = small(ref), small(fr)
    else:
        rs, fs = ref, fr
    R = max(2, int(radius_frac * w / f))
    best, bs = (0, 0), -1
    for r in range(R + 1):                       # rings outward: ties keep the smaller shift
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if max(abs(dx), abs(dy)) != r:
                    continue
                sc = _score(rs, fs, dx, dy)
                if sc > bs:
                    best, bs = (dx, dy), sc
    cx, cy = best[0] * f, best[1] * f
    best, bs = (cx, cy), -1
    for dy in range(cy - f - 1, cy + f + 2):
        for dx in range(cx - f - 1, cx + f + 2):
            sc = _score(ref, fr, dx, dy)
            if sc > bs or (sc == bs and abs(dx) + abs(dy) < abs(best[0]) + abs(best[1])):
                best, bs = (dx, dy), sc
    opaque = max(1, int((ref[..., 3] > ALPHA).sum()))
    return best, bs / opaque


def _mscore(r, f, dx, dy):
    h, w = r.shape
    a = r[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)]
    b = f[max(0, -dy):h - max(0, dy), max(0, -dx):w - max(0, dx)]
    return int((a & b).sum())


def mask_shift(ref: np.ndarray, fr: np.ndarray, radius_frac: float = 0.2) -> tuple[int, int]:
    """Translation of binary body mask FR that maximises its overlap with REF (coarse on a 1/f downscale, then
    refine). Shape-based, so it works when frames are repainted and no pixel colours match."""
    h, w = ref.shape
    f = max(1, w // 128)
    if f > 1:
        cut = lambda m: m[:h // f * f, :w // f * f].reshape(h // f, f, w // f, f).mean((1, 3)) > 0.5
        rs, fs = cut(ref), cut(fr)
    else:
        rs, fs = ref, fr
    R = max(2, int(radius_frac * w / f))
    best, bs = (0, 0), -1
    for r in range(R + 1):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if max(abs(dx), abs(dy)) != r:
                    continue
                sc = _mscore(rs, fs, dx, dy)
                if sc > bs:
                    best, bs = (dx, dy), sc
    cx, cy = best[0] * f, best[1] * f
    best, bs = (cx, cy), -1
    for dy in range(cy - f - 1, cy + f + 2):
        for dx in range(cx - f - 1, cx + f + 2):
            sc = _mscore(ref, fr, dx, dy)
            if sc > bs or (sc == bs and abs(dx) + abs(dy) < abs(best[0]) + abs(best[1])):
                best, bs = (dx, dy), sc
    return best


def measure_frames(alphas: list[np.ndarray], rgbas: list[np.ndarray] | None = None) -> dict:
    """Drift of the rigid body and (for comparison) the alpha-bbox centre over one facing's frames. With RGBA
    frames the primary figure is the colour-match registration (match_*); the opening centroid is the cross-check."""
    body = [stats(body_of(a)) for a in alphas]
    big = [stats(body_of(a, OPEN_FRAC * 1.5)) for a in alphas]
    full = [stats(a > ALPHA) for a in alphas]
    if any(s is None for s in body + big + full):
        return {"error": "blank frame or body lost by opening"}
    bp = [(s["cx"], s["cy"]) for s in body]
    gp = [(s["cx"], s["cy"]) for s in big]
    fp = [(s["bx"], s["by"]) for s in full]
    size = float(np.median([s["major"] for s in body]))
    m = {}
    if rgbas is not None:
        bm = [body_of(a) for a in alphas]
        sh = [(0, 0)] + [mask_shift(bm[0], b) for b in bm[1:]]
        pts = [(float(x), float(y)) for x, y in sh]
        cm = [match_shift(rgbas[0], r) for r in rgbas[1:]]
        cpts = [(0.0, 0.0)] + [(float(c[0][0]), float(c[0][1])) for c in cm]
        m = {"match_span": _span(pts), "match_step": _step(pts), "match_shifts": sh,
             "colour_span": _span(cpts), "colour_share": float(min((c[1] for c in cm), default=1.0))}
    return {**m, "body_span": _span(bp), "body_step": _step(bp), "sens_span": _span(gp),
            "bbox_span": _span(fp), "bbox_step": _step(fp), "body_size": size,
            "body_frac": _span(bp) / size if size else 0.0}


def verdict(r: dict) -> str:
    if r.get("frames", 0) == 0:
        return "MISSING"
    if r.get("frames", 0) < 2:
        return "SINGLE"
    if r.get("error"):
        return "UNMEASURED"
    if r["body_px"] >= OFFEND_PX and r["body_frac"] >= OFFEND_FRAC:
        return "OFFENDER"
    if r["body_px"] >= OFFEND_PX / 2 and r["body_frac"] >= OFFEND_FRAC / 2:
        return "MARGINAL"
    return "OK"


def measure_set(files_by_dir: dict[str, list[Path]]) -> dict:
    """files_by_dir: facing -> frame files in order. Worst facing wins. body_px = colour-match registration span
    (primary); open_px = opening-centroid span (cross-check); bbox_px = alpha-bbox centre span (the wrong metric)."""
    per, worst = {}, None
    for d, files in files_by_dir.items():
        if len(files) < 2:
            continue
        rg = [np.asarray(Image.open(f).convert("RGBA")) for f in files]
        sizes = sorted({x.shape[:2] for x in rg})
        if len(sizes) > 1:                       # frames of different canvas size cannot share a body anchor
            per[d] = {"error": "mixed canvas sizes " + ",".join(f"{w}x{h}" for h, w in sizes)}
            continue
        r = measure_frames([x[..., 3] for x in rg], rg)
        per[d] = r
        if "error" not in r and (worst is None or r["match_span"] > per[worst]["match_span"]):
            worst = d
    nframes = max((len(v) for v in files_by_dir.values()), default=0)
    if worst is None:
        errs = [v["error"] for v in per.values() if v.get("error")]
        return {"frames": nframes, "note": "; ".join(errs), "error": "no measurable facing" if nframes > 1 else None, "per": per}
    w = per[worst]
    out = {"frames": nframes, "facing": worst, "body_px": w["match_span"], "step_px": w["match_step"],
           "body_frac": w["match_span"] / w["body_size"] if w["body_size"] else 0.0,
           "colour_px": w["colour_span"], "colour_share": w["colour_share"],
           "open_px": w["body_span"], "bbox_px": max(v["bbox_span"] for v in per.values() if "bbox_span" in v),
           "sens_px": w["sens_span"], "body_size": w["body_size"], "shifts": w["match_shifts"], "per": per}
    out["verdict"] = verdict(out)
    return out


# ---------------------------------------------------------------- discovery

def _enclosing_name(root: ET.Element, el: ET.Element, fallback: str) -> str:
    pm = {c: p for p in root.iter() for c in p}
    cur = el
    while cur in pm:
        cur = pm[cur]
        dn = cur.find("defName")
        if dn is not None and dn.text:
            return dn.text.strip()
    return fallback


def discover(repo: Path = REPO) -> list[dict]:
    tex_roots = [p for p in (repo / "src").rglob("Textures") if p.is_dir()]
    rows = []
    for x in (repo / "src").rglob("*.xml"):
        try:
            if b"flyingAnimationFramePathPrefix" not in x.read_bytes():
                continue
            root = ET.parse(x).getroot()
        except (ET.ParseError, OSError):
            continue
        counts = {el.tag: el for el in root.iter() if el.tag == "flyingAnimationFrameCount"}
        for el in root.iter():
            if el.tag not in ("flyingAnimationFramePathPrefix", "flyingAnimationFramePathPrefixFemale") or not (el.text or "").strip():
                continue
            pre = el.text.strip()
            name = _enclosing_name(root, el, x.stem)
            cnt_el = next((c for c in root.iter("flyingAnimationFrameCount")), None)
            declared = int(cnt_el.text) if cnt_el is not None and (cnt_el.text or "").isdigit() else None
            files = {d: [] for d in DIRS}
            folder = None
            for tr in tex_roots:
                for d in DIRS:
                    n = 1
                    while (tr / f"{pre}{n}_{d}.png").is_file():
                        files[d].append(tr / f"{pre}{n}_{d}.png")
                        folder = tr / Path(pre).parent
                        n += 1
            rows.append({"def": name, "mod": x.relative_to(repo / "src").parts[1] if len(x.relative_to(repo / "src").parts) > 1 else "?",
                         "prefix": pre, "female": el.tag.endswith("Female"), "declared": declared,
                         "folder": str(folder.relative_to(repo)) if folder else None,
                         "xml": str(x.relative_to(repo)), "files": files})
    seen, out = set(), []
    for r in rows:                                   # one row per (def, prefix)
        k = (r["def"], r["prefix"])
        if k not in seen:
            seen.add(k)
            out.append(r)
    return sorted(out, key=lambda r: (r["def"], r["prefix"]))


# ---------------------------------------------------------------- contact strip

def strip(files: list[Path], out: Path, scale: int = 2) -> None:
    """Frames side by side on grey; red cross = rigid-body centroid, blue cross = alpha-bbox centre; a green
    horizontal/vertical line at frame 1's body centroid runs through every cell so drift reads at a glance."""
    ims = [Image.open(f).convert("RGBA") for f in files]
    w, h = ims[0].size
    sheet = Image.new("RGBA", (w * len(ims) * scale, h * scale), (118, 118, 118, 255))
    d = ImageDraw.Draw(sheet)
    ref = None
    for i, im in enumerate(ims):
        a = np.asarray(im)[..., 3]
        b, f = stats(body_of(a)), stats(a > ALPHA)
        ox = i * w * scale
        sheet.alpha_composite(im.resize((w * scale, h * scale), Image.NEAREST), (ox, 0))
        if b is None or f is None:
            continue
        ref = ref or b
        d.line([(ox, ref["cy"] * scale), (ox + w * scale, ref["cy"] * scale)], fill=(0, 200, 0, 255))
        d.line([(ox + ref["cx"] * scale, 0), (ox + ref["cx"] * scale, h * scale)], fill=(0, 200, 0, 255))
        for (x, y), col in (((b["cx"], b["cy"]), (255, 0, 0, 255)), ((f["bx"], f["by"]), (60, 90, 255, 255))):
            X, Y = ox + x * scale, y * scale
            d.line([(X - 6, Y), (X + 6, Y)], fill=col, width=2)
            d.line([(X, Y - 6), (X, Y + 6)], fill=col, width=2)
        d.text((ox + 3, 3), f"{i + 1}", fill=(255, 255, 255, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json")
    ap.add_argument("--strip-dir")
    ap.add_argument("--worst", type=int, default=3)
    ap.add_argument("--set", default="")
    a = ap.parse_args(argv)
    res = []
    for r in discover():
        if a.set and a.set.lower() not in (r["def"] + r["prefix"]).lower():
            continue
        m = measure_set(r["files"])
        if m.get("frames", 0) == 0:
            m["verdict"] = "MISSING"
        m.update({k: r[k] for k in ("def", "mod", "prefix", "female", "declared", "folder")})
        m["found"] = {d: len(v) for d, v in r["files"].items()}
        m["_files"] = r["files"]
        res.append(m)
    res.sort(key=lambda m: -(m.get("body_frac") or 0))
    print(f"{'def':22}{'mod':12}{'fr':>3}{'face':>6}{'body_px':>8}{'frac':>7}{'step':>6}{'open_px':>8}{'col_px':>7}{'col%':>5}{'bbox_px':>8}  verdict")
    for m in res:
        if m.get("frames", 0) < 2 or "body_px" not in m:
            print(f"{m['def'][:21]:22}{m['mod'][:11]:12}{m.get('frames', 0):>3}  {m.get('verdict', 'SINGLE' if m.get('frames', 0) < 2 else 'UNMEASURED')} {m.get('note') or ''}")
            continue
        print(f"{m['def'][:21]:22}{m['mod'][:11]:12}{m['frames']:>3}{m['facing']:>6}{m['body_px']:8.1f}{m['body_frac']:7.3f}"
              f"{m['step_px']:6.1f}{m['open_px']:8.1f}{m['colour_px']:7.1f}{m['colour_share']*100:5.0f}{m['bbox_px']:8.1f}  {m['verdict']}")
    if a.strip_dir:
        for m in [x for x in res if "body_px" in x][: a.worst]:
            out = Path(a.strip_dir) / f"{m['def']}{'_f' if m['female'] else ''}_{m['facing']}.png"
            strip(m["_files"][m["facing"]], out)
            m["strip"] = str(out)
            print("strip", out)
    if a.json:
        Path(a.json).write_text(json.dumps([{k: v for k, v in m.items() if k != "_files"} for m in res], indent=1, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
