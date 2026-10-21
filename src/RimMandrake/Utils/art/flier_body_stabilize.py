#!/usr/bin/env python3
"""flier_body_stabilize.py - READ-ONLY: where is the flier's BODY in each flip-book frame, and is it level?

Owner 2026-10-20 (relayed): "You will absolutely need a way to identify where the body is to ensure it's being level.
Simple stats about the entire image won't work. It's going to take edgefinding, parts of the body recognition, things
like that." So nothing here uses an alpha bbox, an alpha centroid, a whole-image statistic or a single opened mask.

The body is located the way video stabilisers locate the static scene, restricted to the body and with the moving
wings rejected as outliers, and three independent estimators must agree:

  ECC      OpenCV findTransformECC (Evangelidis & Psarakis 2008, "Parametric image alignment using enhanced
           correlation coefficient maximization"), MOTION_EUCLIDEAN, with inputMask = the BODY region of the
           reference frame, on edge-weighted grey (gradient magnitude), so the fit is driven by the body's edges and
           interior detail. Gives dx, dy, angle and the correlation rho (rho < 0.6 = the body is a different drawing).
  FEATURES SIFT keypoints (Lowe 2004) inside the body region, matched by descriptor (ratio test 0.8), then
           estimateAffinePartial2D with RANSAC (4-DOF similarity; wings and re-shaded pixels are rejected as
           outliers). The pipeline is the point-feature stabiliser of learnopencv
           (github.com/spmallick/learnopencv, VideoStabilization/video_stabilization.py: goodFeaturesToTrack ->
           calcOpticalFlowPyrLK -> estimateAffinePartial2D with RANSAC, then dx, dy, da = atan2(b, a)), with SIFT
           descriptors instead of optical flow because flip-book frames are not a smooth video.
  PARTS    body-part templates: the body region is split across its principal axis into a FRONT part and a BACK part
           (head/shoulders and hips/tail root), plus an optional named part box from the config ("parts":
           {"head": [x0, y0, x1, y1]}). Each part is found in every frame by masked template matching
           (TM_CCORR_NORMED with the part's own mask) over a +/-12 deg rotation sweep; the part-to-part line gives the
           body's pitch independently of the other two estimators.

The BODY region of the reference frame comes from the set's annotation (flyer_cutout_sets/<Set>.json `protect`
polygons, which a person drew around head, torso, legs and tail) intersected with alpha > 128. With no annotation
the tool refuses: it does not guess a body from image statistics.

Verdict per facing: LOCKED when every frame's body is within 1 px and 0.5 deg of the reference on ECC and FEATURES
(and PARTS within 1.5 px / 1 deg), DRIFT when a rigid body moved more than that, RE-POSED when the body is not the
same drawing (ECC rho < 0.6 or fewer than 8 feature inliers): no rigid transform describes it.

Usage (needs OpenCV; re-runs itself under <agent storage>/rimmandrake/build/cvenv when cv2 is missing):
  flier_body_stabilize.py --set Sketto [--src DIR] [--facing F] [--overlay OUT.png] [--json OUT.json]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

try:
    import cv2  # noqa: F401
except ImportError:                                      # re-exec under the agent-storage venv that has OpenCV
    if os.environ.get("RM_CV_REEXEC"):
        raise SystemExit("flier_body_stabilize: OpenCV (cv2) is not importable; UNMEASURED")
    root = subprocess.run([sys.executable, str(Path.home() / "dev/Lodestar/bin/lib/agent_storage.py")],
                          capture_output=True, text=True).stdout.strip()
    py = os.environ.get("RM_CV_PYTHON") or (str(Path(root) / "rimmandrake/build/cvenv/bin/python") if root else "")
    if not py or not Path(py).exists():
        raise SystemExit("flier_body_stabilize: no cv2 and no venv at <agent storage>/rimmandrake/build/cvenv "
                         "(python3 -m venv there; pip install opencv-python-headless numpy pillow); UNMEASURED")
    os.execve(py, [py, *sys.argv], {**os.environ, "RM_CV_REEXEC": "1"})

import cv2  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

sys.path.insert(0, str(HERE))
import flyer_cutout as FC  # noqa: E402

TOL_PX, TOL_DEG = 1.0, 0.5
PART_TOL_PX, PART_TOL_DEG = 1.5, 1.0
RHO_MIN, INLIERS_MIN = 0.6, 8


def grey_edges(rgba: np.ndarray) -> np.ndarray:
    """Grey over a mid background, plus its gradient magnitude: edges and interior detail carry the fit."""
    a = rgba[..., 3:4].astype(np.float32) / 255.0
    g = (rgba[..., :3].astype(np.float32) * a + 118.0 * (1 - a)).mean(-1)
    g = cv2.GaussianBlur(g, (3, 3), 0)
    gx, gy = cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1)
    e = np.sqrt(gx * gx + gy * gy)
    return (0.5 * g + 0.5 * np.clip(e, 0, 255)).astype(np.float32)


def _euclid(M) -> dict:
    a, b, tx = M[0]
    c, d, ty = M[1]
    return {"dx": float(tx), "dy": float(ty), "deg": math.degrees(math.atan2(c, a)), "scale": float(math.hypot(a, c))}


def body_motion_at(M, cx, cy) -> tuple[float, float]:
    """Displacement of the body's own centre (cx, cy) under 2x3 map M (so a rotation about the corner is not read
    as a big translation)."""
    x = M[0, 0] * cx + M[0, 1] * cy + M[0, 2]
    y = M[1, 0] * cx + M[1, 1] * cy + M[1, 2]
    return float(x - cx), float(y - cy)


def est_features(ref, frm, mask) -> dict:
    ak = cv2.SIFT_create(contrastThreshold=0.01)
    g1 = cv2.cvtColor(np.ascontiguousarray(ref[..., :3]), cv2.COLOR_RGB2GRAY)
    g2 = cv2.cvtColor(np.ascontiguousarray(frm[..., :3]), cv2.COLOR_RGB2GRAY)
    up = 2 if ref.shape[0] <= 256 else 1                 # small sprites: detect on a 2x upsample
    if up > 1:
        g1, g2 = (cv2.resize(g, None, fx=up, fy=up, interpolation=cv2.INTER_CUBIC) for g in (g1, g2))
    m1 = cv2.resize(mask.astype(np.uint8) * 255, None, fx=up, fy=up, interpolation=cv2.INTER_NEAREST)
    m2 = cv2.resize((frm[..., 3] > 128).astype(np.uint8) * 255, None, fx=up, fy=up, interpolation=cv2.INTER_NEAREST)
    k1, d1 = ak.detectAndCompute(g1, m1)
    k2, d2 = ak.detectAndCompute(g2, m2)
    if d1 is None or d2 is None or len(k1) < 4 or len(k2) < 4:
        return {"ok": False, "inliers": 0, "keypoints": len(k1 or [])}
    pairs = cv2.BFMatcher(cv2.NORM_L2).knnMatch(d1, d2, k=2)
    good = [p[0] for p in pairs if len(p) == 2 and p[0].distance < 0.8 * p[1].distance]
    if len(good) < 4:
        return {"ok": False, "inliers": 0, "keypoints": len(k1), "matches": len(good)}
    src = np.float32([k1[m.queryIdx].pt for m in good]) / up
    dst = np.float32([k2[m.trainIdx].pt for m in good]) / up
    M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=1.5, maxIters=5000,
                                         confidence=0.999)
    if M is None:
        return {"ok": False, "inliers": 0, "keypoints": len(k1), "matches": len(good)}
    n_in = int(inl.sum())
    return {"ok": n_in >= INLIERS_MIN, "M": M, "inliers": n_in, "matches": len(good), "keypoints": len(k1),
            "pts": dst[inl.ravel() == 1].tolist(), **_euclid(M)}


def est_ecc(ref, frm, mask, init=None) -> dict:
    t, i = grey_edges(ref), grey_edges(frm)
    W = np.eye(2, 3, dtype=np.float32) if init is None else init.astype(np.float32).copy()
    if init is not None:                                 # keep the init rigid (drop scale) for MOTION_EUCLIDEAN
        e = _euclid(init)
        r = math.radians(e["deg"])
        W = np.float32([[math.cos(r), -math.sin(r), e["dx"]], [math.sin(r), math.cos(r), e["dy"]]])
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6)
    try:
        rho, W = cv2.findTransformECC(t, i, W, cv2.MOTION_EUCLIDEAN, crit, mask.astype(np.uint8) * 255, 3)
    except cv2.error as exc:
        return {"ok": False, "rho": 0.0, "error": str(exc).splitlines()[-1][:120]}
    # findTransformECC's W maps template coords into the input image: the body's pose in this frame
    return {"ok": rho >= RHO_MIN, "rho": float(rho), "M": W, **_euclid(W)}


def split_parts(mask: np.ndarray) -> dict:
    """FRONT/BACK parts: the body region cut across its principal axis at its centre."""
    ys, xs = np.nonzero(mask)
    c = np.array([xs.mean(), ys.mean()])
    cov = np.cov(np.stack([xs - c[0], ys - c[1]]))
    w, v = np.linalg.eigh(cov)
    ax = v[:, np.argmax(w)]
    proj = (xs - c[0]) * ax[0] + (ys - c[1]) * ax[1]
    out = {}
    for name, sel in (("front", proj < 0), ("back", proj >= 0)):
        m = np.zeros_like(mask)
        m[ys[sel], xs[sel]] = True
        out[name] = m
    return out


def _rot(img, deg, centre):
    M = cv2.getRotationMatrix2D(centre, deg, 1.0)
    return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR)


def find_part(ref, frm, pmask) -> dict:
    """Masked template match of one part over a rotation sweep; returns its centre in FRM and the best rotation."""
    ys, xs = np.nonzero(pmask)
    if len(xs) < 30:
        return {"ok": False}
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    pad = 4
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(ref.shape[1], x1 + pad), min(ref.shape[0], y1 + pad)
    g_ref, g_frm = grey_edges(ref), grey_edges(frm)
    tpl0, msk0 = g_ref[y0:y1, x0:x1], pmask[y0:y1, x0:x1].astype(np.float32)
    cx0, cy0 = float(xs.mean()), float(ys.mean())
    best = (-1.0, 0, (0, 0))
    for deg in np.arange(-12, 12.01, 1.0):
        tpl = _rot(tpl0, deg, (cx0 - x0, cy0 - y0))
        msk = _rot(msk0, deg, (cx0 - x0, cy0 - y0))
        if msk.sum() < 20:
            continue
        r = cv2.matchTemplate(g_frm, tpl, cv2.TM_CCORR_NORMED, mask=msk)
        r = np.nan_to_num(r, nan=-1, posinf=-1, neginf=-1)
        _, mx, _, loc = cv2.minMaxLoc(r)
        if mx > best[0]:
            best = (mx, deg, loc)
    score, deg, loc = best
    # refine the location to sub-pixel with a parabola fit on the best rotation's score map
    tpl, msk = _rot(tpl0, deg, (cx0 - x0, cy0 - y0)), _rot(msk0, deg, (cx0 - x0, cy0 - y0))
    r = np.nan_to_num(cv2.matchTemplate(g_frm, tpl, cv2.TM_CCORR_NORMED, mask=msk), nan=-1)
    lx, ly = loc
    sx = sy = 0.0
    if 0 < lx < r.shape[1] - 1:
        a, b, c = r[ly, lx - 1], r[ly, lx], r[ly, lx + 1]
        sx = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) != 0 else 0.0
    if 0 < ly < r.shape[0] - 1:
        a, b, c = r[ly - 1, lx], r[ly, lx], r[ly + 1, lx]
        sy = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) != 0 else 0.0
    return {"ok": True, "score": float(score), "deg": float(deg), "ref_c": [cx0, cy0],
            "c": [lx + sx + (cx0 - x0), ly + sy + (cy0 - y0)], "box": [int(lx), int(ly), int(lx + x1 - x0), int(ly + y1 - y0)]}


def est_parts(ref, frm, parts: dict) -> dict:
    res = {n: find_part(ref, frm, m) for n, m in parts.items()}
    f, b = res.get("front", {}), res.get("back", {})
    out = {"parts": res}
    if f.get("ok") and b.get("ok"):
        a0 = math.degrees(math.atan2(f["ref_c"][1] - b["ref_c"][1], f["ref_c"][0] - b["ref_c"][0]))
        a1 = math.degrees(math.atan2(f["c"][1] - b["c"][1], f["c"][0] - b["c"][0]))
        out["deg"] = (a1 - a0 + 180) % 360 - 180
        out["shift"] = max(math.hypot(p["c"][0] - p["ref_c"][0], p["c"][1] - p["ref_c"][1]) for p in res.values() if p.get("ok"))
        out["min_score"] = min(p["score"] for p in res.values() if p.get("ok"))
    return out


def body_mask_from(cfg_facing: dict, ref: np.ndarray) -> np.ndarray:
    m = FC.poly_mask(ref.shape[:2], cfg_facing.get("protect")) & (ref[..., 3] > 128)
    return m


def measure_facing(frames: list[np.ndarray], mask: np.ndarray, named_parts: dict | None = None) -> dict:
    ref = frames[0]
    ys, xs = np.nonzero(mask)
    cx, cy = float(xs.mean()), float(ys.mean())          # centre of the ANNOTATED body, for reporting motion there
    parts = split_parts(mask)
    for n, box in (named_parts or {}).items():
        m = np.zeros_like(mask)
        m[box[1]:box[3], box[0]:box[2]] = True
        parts[n] = m & (ref[..., 3] > 128)
    rows = []
    for k, frm in enumerate(frames):
        feat = est_features(ref, frm, mask)
        ecc = est_ecc(ref, frm, mask, feat.get("M") if feat.get("ok") else None)
        prt = est_parts(ref, frm, parts)
        row = {"frame": k + 1, "features": {x: feat.get(x) for x in ("ok", "inliers", "matches", "dx", "dy", "deg", "scale")},
               "ecc": {x: ecc.get(x) for x in ("ok", "rho", "dx", "dy", "deg", "error")},
               "parts": {"deg": prt.get("deg"), "shift": prt.get("shift"), "min_score": prt.get("min_score")},
               "_feat": feat, "_ecc": ecc, "_parts": prt}
        for name, e in (("ecc", ecc), ("features", feat)):
            if e.get("M") is not None:
                mx, my = body_motion_at(e["M"], cx, cy)
                row[name]["body_px"] = round(math.hypot(mx, my), 3)
        rows.append(row)
    worst = {"ecc_px": 0.0, "ecc_deg": 0.0, "feat_px": 0.0, "feat_deg": 0.0, "parts_px": 0.0, "parts_deg": 0.0,
             "rho_min": 1.0, "inliers_min": 10 ** 9}
    reposed = False
    for r in rows[1:]:
        e, f, p = r["ecc"], r["features"], r["parts"]
        if not e.get("ok") or not f.get("ok"):
            reposed = True
        worst["rho_min"] = min(worst["rho_min"], e.get("rho") or 0.0)
        worst["inliers_min"] = min(worst["inliers_min"], f.get("inliers") or 0)
        if e.get("body_px") is not None:
            worst["ecc_px"] = max(worst["ecc_px"], e["body_px"]); worst["ecc_deg"] = max(worst["ecc_deg"], abs(e["deg"]))
        if f.get("body_px") is not None:
            worst["feat_px"] = max(worst["feat_px"], f["body_px"]); worst["feat_deg"] = max(worst["feat_deg"], abs(f["deg"]))
        if p.get("shift") is not None:
            worst["parts_px"] = max(worst["parts_px"], p["shift"]); worst["parts_deg"] = max(worst["parts_deg"], abs(p["deg"]))
    if reposed:
        verdict = "RE-POSED"
    elif (worst["ecc_px"] <= TOL_PX and worst["ecc_deg"] <= TOL_DEG and worst["feat_px"] <= TOL_PX
          and worst["feat_deg"] <= TOL_DEG and worst["parts_px"] <= PART_TOL_PX and worst["parts_deg"] <= PART_TOL_DEG):
        verdict = "LOCKED"
    else:
        verdict = "DRIFT"
    return {"verdict": verdict, "worst": {k: round(v, 3) for k, v in worst.items()}, "rows": rows,
            "body_centre": [round(cx, 1), round(cy, 1)]}


def overlay(frames: list[np.ndarray], mask: np.ndarray, res: dict, out: Path, title: str) -> None:
    """Every frame, with what the tool thinks is the body: the reference body outline mapped through ECC (green),
    the FRONT/BACK/named part boxes where they were found (yellow/cyan/magenta), the RANSAC inlier features (red)."""
    h, w = frames[0].shape[:2]
    k = max(1, 384 // w)
    cnts, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    sheet = Image.new("RGB", (w * k * len(frames), h * k + 34), (118, 118, 118))
    d = ImageDraw.Draw(sheet)
    cols = {"front": (255, 230, 0), "back": (0, 230, 255)}
    for i, (fr, row) in enumerate(zip(frames, res["rows"])):
        ox = i * w * k
        im = Image.fromarray(fr, "RGBA").resize((w * k, h * k), Image.NEAREST)
        sheet.paste(im, (ox, 0), im)
        M = row["_ecc"].get("M")
        if M is not None:
            for c in cnts:
                pts = c.reshape(-1, 2).astype(np.float32)
                mp = (pts @ M[:, :2].T + M[:, 2]) * k
                d.line([(ox + x, y) for x, y in mp] + [(ox + mp[0][0], mp[0][1])], fill=(0, 255, 0), width=1)
        for n, p in row["_parts"].get("parts", {}).items():
            if p.get("ok"):
                x0, y0, x1, y1 = p["box"]
                d.rectangle([ox + x0 * k, y0 * k, ox + x1 * k, y1 * k], outline=cols.get(n, (255, 0, 255)), width=1)
        for x, y in (row["_feat"].get("pts") or [])[:400]:
            d.point((ox + x * k, y * k), fill=(255, 40, 40))
        e, f = row["ecc"], row["features"]
        txt = (f"{i + 1}: ECC {e.get('body_px', '-')}px {e.get('deg') or 0:+.2f}deg rho {e.get('rho') or 0:.2f}"
               if e.get("dx") is not None else f"{i + 1}: ECC failed")
        d.text((ox + 3, h * k + 3), txt, fill=(255, 255, 255))
        d.text((ox + 3, h * k + 18), f"feat {f.get('body_px', '-')}px {f.get('deg') or 0:+.2f}deg in {f.get('inliers')}",
               fill=(255, 255, 255))
    d.text((3, 3), title, fill=(255, 255, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)


def load_set(name: str, src: Path | None, facing: str):
    cfg = json.loads((HERE / "flyer_cutout_sets" / f"{name}.json").read_text())
    folder = Path(src) if src else REPO / cfg["folder"]
    paths = FC.FL.frame_paths(folder, cfg["prefix"], facing)
    frames = [np.asarray(Image.open(p).convert("RGBA")) for p in paths]
    fc = cfg["facings"].get(facing, {})
    return cfg, fc, paths, frames


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--set", required=True, help="a flyer_cutout_sets/<Set>.json name (holds the body annotation)")
    ap.add_argument("--src", type=Path, help="read frames here instead of the set's Textures folder")
    ap.add_argument("--facing", choices=("north", "east", "south"))
    ap.add_argument("--ref", type=int, help="reference frame (default: the set's master for that facing, else 1)")
    ap.add_argument("--overlay", type=Path, help="write the body overlay strip(s); facing is appended")
    ap.add_argument("--json", type=Path)
    a = ap.parse_args(argv)
    out, worst_rc = {}, 0
    for facing in ([a.facing] if a.facing else ["north", "east", "south"]):
        cfg, fc, paths, frames = load_set(a.set, a.src, facing)
        if not fc.get("protect"):
            print(f"UNMEASURED {a.set} {facing}: no body annotation (protect polygons) in the set config")
            worst_rc = max(worst_rc, 2)
            continue
        sizes = {f.shape for f in frames}
        if len(frames) < 2 or len(sizes) != 1:
            print(f"UNMEASURED {a.set} {facing}: {len(frames)} frames, sizes {sorted(s[:2] for s in sizes)}")
            worst_rc = max(worst_rc, 2)
            continue
        ref = (a.ref or fc.get("master", 1)) - 1
        order = [ref] + [i for i in range(len(frames)) if i != ref]
        fr = [frames[i] for i in order]
        mask = body_mask_from(fc, fr[0])
        res = measure_facing(fr, mask, fc.get("parts"))
        for r, i in zip(res["rows"], order):
            r["frame"] = i + 1
        wv = res["worst"]
        print(f"{res['verdict']:8} {a.set} {facing} (ref frame {ref + 1}): ECC {wv['ecc_px']} px / {wv['ecc_deg']} deg "
              f"(rho min {wv['rho_min']}), features {wv['feat_px']} px / {wv['feat_deg']} deg (inliers min "
              f"{wv['inliers_min']}), parts {wv['parts_px']} px / {wv['parts_deg']} deg")
        if a.overlay:
            p = a.overlay.with_name(f"{a.overlay.stem}_{facing}{a.overlay.suffix}")
            overlay(fr, mask, res, p, f"{a.set} {facing}: {res['verdict']} (frames in order {[i + 1 for i in order]})")
            print("overlay", p)
        out[facing] = {"verdict": res["verdict"], "worst": wv, "ref": ref + 1,
                       "rows": [{k: v for k, v in r.items() if not k.startswith("_")} for r in res["rows"]]}
        worst_rc = max(worst_rc, 0 if res["verdict"] == "LOCKED" else 1)
    if a.json:
        a.json.write_text(json.dumps(out, indent=1, default=float))
    return worst_rc


if __name__ == "__main__":
    sys.exit(main())
