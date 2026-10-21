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
    if score < 0:                                          # every rotation was skipped: nothing was matched
        return {"ok": False}
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


# ---------------------------------------------------------------------------------------------------------------
# Owner's line test (2026-10-20, card answer): "Draw a line through the eyes of each of these pictures, and then
# another line between their shoulders. Those lines should be level, not moving up and down with wing flaps."
#
# Anchor points are FOUND in the reference (master) frame, then each point is DETECTED AGAIN in every frame by a masked
# template match (TM_CCOEFF_NORMED on edge-weighted grey, sub-pixel parabola) - never copied from the config, never
# mapped through a transform, so a body that moves between frames moves the lines.
#   eye line       south: the two eyes; east (profile, one eye): the eye and the snout tip on the eye's row. Eye centres
#                  come from the set config's per-facing `eyes` (placed by a person on the master, like `hinge`); with
#                  none, a black-hat dark-spot detector guesses (it picked horns and crests on painted heads, so the
#                  six rebuilt sets carry placed eyes);
#                  north (from behind, eyes hidden): the two head-side edges one fifth down the head.
#   shoulder line  north/south: the two wing roots (the person-drawn `hinge` of each wing in the set config), each
#                  moved inward onto the body by up to 0.7 patch radius (the hinge itself sits on the body/wing edge);
#                  east (one wing visible): the wing root and the chest front on the same row.
# The match mask is the body (`protect` polygons, plus everything outside the `wings` polygons, background included so
# silhouette edges count); wing pixels never drive a match.
# Reported per frame: the line midpoint's vertical offset from the reference frame (px, + = down) and the change of
# the line's angle (deg). LEVEL when every frame is within LINE_TOL_PX and LINE_TOL_DEG.
LINE_TOL_PX, LINE_TOL_DEG = 1.0, 0.5
LINE_MATCH_MIN = 0.5


def _body_match_mask(fc: dict, shape) -> np.ndarray:
    prot = FC.poly_mask(shape, fc.get("protect"))
    wings = FC.poly_mask(shape, [w["poly"] for w in fc.get("wings", [])])
    return prot | ~wings


def _head_region(fc: dict, facing: str, ref: np.ndarray) -> np.ndarray:
    body = FC.poly_mask(ref.shape[:2], fc.get("protect")) & (ref[..., 3] > 128)
    ys, xs = np.nonzero(body)
    out = np.zeros_like(body)
    if not len(xs):
        return out
    if facing == "east":                                   # east faces right: the head is the front of the body
        x0 = xs.max() - 0.4 * (xs.max() - xs.min())
        out[ys[xs >= x0], xs[xs >= x0]] = True
    else:                                                  # north/south: the head is the top of the body
        y1 = ys.min() + max(12, 0.22 * (ys.max() - ys.min()))
        out[ys[ys <= y1], xs[ys <= y1]] = True
    return out


def _dark_spots(ref: np.ndarray, region: np.ndarray) -> list[tuple[float, int, int]]:
    """Local maxima of a black-hat (dark spot) response inside REGION, strongest first: (score, x, y)."""
    L = cv2.cvtColor(np.ascontiguousarray(ref[..., :3]), cv2.COLOR_RGB2GRAY).astype(np.float32)
    ys, xs = np.nonzero(region)
    hw = max(8, int(xs.max() - xs.min() + 1)) if len(xs) else 8
    k = max(5, (hw // 5) | 1)
    bh = cv2.morphologyEx(L, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    inner = cv2.erode(region.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    bh = cv2.GaussianBlur(bh, (3, 3), 0) * inner
    peaks = (bh == cv2.dilate(bh, np.ones((k, k), np.uint8))) & (bh > 0.3 * (bh.max() or 1))
    py, px = np.nonzero(peaks)
    return sorted(((float(bh[y, x]), int(x), int(y)) for x, y in zip(px, py)), reverse=True)


def eye_points(fc: dict, facing: str, ref: np.ndarray):
    head = _head_region(fc, facing, ref)
    ys, xs = np.nonzero(head)
    if len(xs) < 20:
        return None, "no head"
    alpha = ref[..., 3] > 128
    if facing == "north":                                  # eyes hidden from behind: the head's two side edges
        y = int(ys.min() + 0.2 * (ys.max() - ys.min()))
        row = np.nonzero(alpha[y] & _body_match_mask(fc, ref.shape[:2])[y])[0]
        axis = xs.mean()
        left, right = row[row < axis], row[row >= axis]
        if not len(left) or not len(right):
            return None, "no head edges"
        # contiguous run through the axis: the head itself, not a wing at the same row
        lx = int(axis)
        while lx - 1 >= 0 and alpha[y, lx - 1]:
            lx -= 1
        rx = int(axis)
        while rx + 1 < alpha.shape[1] and alpha[y, rx + 1]:
            rx += 1
        return [(float(lx), float(y)), (float(rx), float(y))], "head edges (eyes hidden from behind)"
    eyes = fc.get("eyes")                                  # person-placed eye centres in the master, when given
    if eyes and facing == "south" and len(eyes) >= 2:
        a, b = sorted(eyes[:2])
        return [(float(a[0]), float(a[1])), (float(b[0]), float(b[1]))], "eyes (placed on the master)"
    if eyes and facing == "east":
        ex, ey = int(round(eyes[0][0])), int(round(eyes[0][1]))
        tx = ex
        while tx + 1 < alpha.shape[1] and any(alpha[max(0, ey - 2):ey + 3, tx + 1]):
            tx += 1
        return [(float(eyes[0][0]), float(eyes[0][1])), (float(tx), float(eyes[0][1]))], \
            "eye (placed on the master) + snout tip"
    spots = _dark_spots(ref, head)
    if facing == "east":
        # the eye sits high in the head and behind the snout; the open mouth is low, the nostril at the tip
        xback = xs.max() - 0.3 * (xs.max() - xs.min())
        upper = [s for s in spots if s[2] <= np.median(ys) and s[1] <= xback]
        if not upper:
            return None, "no eye spot"
        _, ex, ey = upper[0]
        tx = ex
        while tx + 1 < alpha.shape[1] and any(alpha[max(0, ey - 2):ey + 3, tx + 1]):
            tx += 1
        return [(float(ex), float(ey)), (float(tx), float(ey))], "eye + snout tip (profile)"
    axis, hw = xs.mean(), xs.max() - xs.min() + 1
    best = None
    for i, (s1, x1, y1) in enumerate(spots[:30]):
        for s2, x2, y2 in spots[i + 1:30]:
            dx, dy = abs(x2 - x1), abs(y2 - y1)
            if (dx < 0.12 * hw or dx > 0.9 * hw or dy > 0.2 * dx or (x1 - axis) * (x2 - axis) >= 0
                    or abs((x1 + x2) / 2 - axis) > 0.12 * hw):    # two eyes: level-ish, either side of the head axis
                continue
            score = s1 + s2 - 0.5 * abs(s1 - s2) - 2.0 * abs((x1 + x2) / 2 - axis)
            if best is None or score > best[0]:
                best = (score, (x1, y1), (x2, y2))
    if best is None:
        return None, "no eye pair"
    a, b = sorted([best[1], best[2]])
    return [(float(a[0]), float(a[1])), (float(b[0]), float(b[1]))], "eyes"


def shoulder_points(fc: dict, facing: str, ref: np.ndarray):
    hinges = [w["hinge"] for w in fc.get("wings", []) if w.get("hinge")]
    if facing != "east":
        if len(hinges) < 2:
            return None, "fewer than two wing roots"
        a, b = sorted(hinges[:2])
        # the hinge sits ON the silhouette edge where body meets wing: a patch there slides along the edge (aperture
        # problem) and half of it is wing. Each point is moved inward along the shoulder line onto textured body.
        r = max(6, round(0.045 * ref.shape[1]))
        gap = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        k = min(0.7 * r, gap / 4) / gap
        ux, uy = (b[0] - a[0]) * k, (b[1] - a[1]) * k
        return [(float(a[0] + ux), float(a[1] + uy)), (float(b[0] - ux), float(b[1] - uy))], \
            "wing roots (just inside the body)"
    if not hinges:
        return None, "no wing root"
    hx, hy = map(int, hinges[0])
    alpha = ref[..., 3] > 128
    # In profile both shoulders sit on one spot, and the flapping wing covers the root itself on one stroke or the
    # other (it is squashed through the shoulder row across its whole x-range). So the line is drawn across the chest
    # AT the wing root, on body the wing never covers: the chest front on the root's row, and the chest underside
    # below a point one patch-radius behind it.
    x = hx
    while x + 1 < alpha.shape[1] and alpha[hy, x + 1]:
        x += 1
    r = max(6, round(0.045 * alpha.shape[1]))
    bx = min(x - 2, max(x - r, hx + r))
    by = hy
    while by + 1 < alpha.shape[0] and alpha[by + 1, bx]:
        by += 1
    if by - hy < 3:
        return None, "no chest below the wing root"
    return [(float(x), float(hy)), (float(bx), float(by))], "chest front + chest underside at the wing root (profile)"


def track_point(g_ref: np.ndarray, g_frm: np.ndarray, mmask: np.ndarray, pt, r: int, search: int) -> dict:
    h, w = g_ref.shape
    x, y = int(round(pt[0])), int(round(pt[1]))
    x0, x1, y0, y1 = max(0, x - r), min(w, x + r + 1), max(0, y - r), min(h, y + r + 1)
    tpl, msk = g_ref[y0:y1, x0:x1], mmask[y0:y1, x0:x1].astype(np.float32)
    if msk.sum() < 20:
        return {"ok": False}
    sx0, sy0 = max(0, x0 - search), max(0, y0 - search)
    win = g_frm[sy0:min(h, y1 + search), sx0:min(w, x1 + search)]
    if win.shape[0] < tpl.shape[0] or win.shape[1] < tpl.shape[1]:
        return {"ok": False}
    res = np.nan_to_num(cv2.matchTemplate(win, tpl, cv2.TM_CCOEFF_NORMED, mask=msk), nan=-1, posinf=-1, neginf=-1)
    _, mx, _, (lx, ly) = cv2.minMaxLoc(res)
    ox = oy = 0.0
    if 0 < lx < res.shape[1] - 1:
        a, b, c = res[ly, lx - 1], res[ly, lx], res[ly, lx + 1]
        ox = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) != 0 else 0.0
    if 0 < ly < res.shape[0] - 1:
        a, b, c = res[ly - 1, lx], res[ly, lx], res[ly + 1, lx]
        oy = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) != 0 else 0.0
    whole = {"score": float(mx), "pt": [sx0 + lx + ox + (pt[0] - x0), sy0 + ly + oy + (pt[1] - y0)]}
    # Occlusion vote: a flapping wing can cover part of the patch (east wing roots on the downstroke). The patch is
    # also cut into tiles, each matched on its own; the point moves by the MEDIAN displacement of the tiles that match
    # well, and needs a quorum that agree within 1 px. A whole-patch match the tiles disagree with is not used.
    t = max(6, (2 * r) // 3)
    votes = []
    for ty in range(y0, y1 - t + 1, max(2, t // 2)):
        for tx in range(x0, x1 - t + 1, max(2, t // 2)):
            tm = mmask[ty:ty + t, tx:tx + t].astype(np.float32)
            tp = g_ref[ty:ty + t, tx:tx + t]
            if tm.mean() < 0.6 or float(tp[tm > 0].std()) < 4.0:      # mostly wing, or featureless: cannot vote
                continue
            wx0, wy0 = max(0, tx - search), max(0, ty - search)
            sw = g_frm[wy0:min(h, ty + t + search), wx0:min(w, tx + t + search)]
            rr = np.nan_to_num(cv2.matchTemplate(sw, tp, cv2.TM_CCOEFF_NORMED, mask=tm), nan=-1, posinf=-1, neginf=-1)
            _, sc, _, (qx, qy) = cv2.minMaxLoc(rr)
            if sc >= 0.85:
                votes.append((wx0 + qx - tx, wy0 + qy - ty))
    if len(votes) >= 3:
        v = np.array(votes, np.float32)
        med = np.median(v, 0)
        agree = np.all(np.abs(v - med) <= 1.0, 1)
        if agree.sum() >= max(3, 0.4 * len(v)):
            dx, dy = v[agree].mean(0)
            wdx, wdy = whole["pt"][0] - pt[0], whole["pt"][1] - pt[1]
            if math.hypot(wdx - dx, wdy - dy) <= 1.0:            # whole-patch fit agrees: keep its sub-pixel value
                dx, dy = wdx, wdy
            q = _ecc_refine(g_ref, g_frm, mmask, pt, r, dx, dy)
            if q is not None:
                dx, dy = q
            return {"ok": True, "score": whole["score"], "votes": int(agree.sum()), "of": len(v),
                    "refined": q is not None, "pt": [pt[0] + float(dx), pt[1] + float(dy)]}
    return {**whole, "ok": False, "votes": 0, "of": len(votes)}


def _ecc_refine(g_ref, g_frm, mmask, pt, r, dx, dy):
    """Sub-pixel, rotation-aware refinement of one point: ECC (MOTION_EUCLIDEAN) over a disc of radius 2r around it,
    masked to the body, started from the matched translation. Kept only when it lands within 1 px of the match (a wing
    in the disc can pull ECC; the occlusion-voted match is the guard)."""
    h, w = g_ref.shape
    disc = np.zeros((h, w), np.uint8)
    cv2.circle(disc, (int(round(pt[0])), int(round(pt[1]))), 2 * r, 1, -1)
    m = (disc.astype(bool) & mmask).astype(np.uint8) * 255
    if m.sum() < 255 * 40:
        return None
    W = np.float32([[1, 0, dx], [0, 1, dy]])
    try:
        _, W = cv2.findTransformECC(g_ref, g_frm, W, cv2.MOTION_EUCLIDEAN,
                                    (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-5), m, 3)
    except cv2.error:
        return None
    nx = W[0, 0] * pt[0] + W[0, 1] * pt[1] + W[0, 2] - pt[0]
    ny = W[1, 0] * pt[0] + W[1, 1] * pt[1] + W[1, 2] - pt[1]
    if math.hypot(nx - dx, ny - dy) > 1.0:
        return None
    return float(nx), float(ny)


def line_check(frames: list[np.ndarray], fc: dict, facing: str, ref_idx: int) -> dict:
    """Eye line and shoulder line in every frame (frames in natural order; ref_idx = the master)."""
    ref = frames[ref_idx]
    W = ref.shape[1]
    r, search = max(6, round(0.045 * W)), max(12, round(0.12 * W))
    mmask = _body_match_mask(fc, ref.shape[:2])
    g_ref = grey_edges(ref)
    out = {"lines": {}, "worst": {}}
    for name, finder in (("eye", eye_points), ("shoulder", shoulder_points)):
        pts, label = finder(fc, facing, ref)
        if pts is None:
            out["lines"][name] = {"label": label, "ok": False}
            continue
        rows = []
        for k, frm in enumerate(frames):
            g = grey_edges(frm)
            tr = [track_point(g_ref, g, mmask, p, r, search) for p in pts]
            ok = all(t.get("ok") for t in tr)
            row = {"frame": k + 1, "ok": ok, "scores": [round(t.get("score", 0.0), 3) for t in tr]}
            if all("pt" in t for t in tr):
                (ax, ay), (bx, by) = tr[0]["pt"], tr[1]["pt"]
                ax, ay, bx, by = map(float, (ax, ay, bx, by))
                row.update(pts=[[round(ax, 2), round(ay, 2)], [round(bx, 2), round(by, 2)]], mid_y=(ay + by) / 2,
                           deg=math.degrees(math.atan2(by - ay, bx - ax)))
            rows.append(row)
        base = rows[ref_idx]
        wdy = wdeg = 0.0
        lost = False
        for row in rows:
            if "mid_y" not in row or "mid_y" not in base:
                lost = True
                continue
            row["dy"] = round(float(row["mid_y"] - base["mid_y"]), 2)
            row["ddeg"] = round(float((row["deg"] - base["deg"] + 180) % 360 - 180), 2)
            if not row["ok"]:                                # a point not found: no number from this frame
                lost = True
                continue
            wdy, wdeg = max(wdy, abs(row["dy"])), max(wdeg, abs(row["ddeg"]))
        out["lines"][name] = {"label": label, "ok": not lost, "ref_pts": [list(p) for p in pts],
                              "tilt_deg": round(base.get("deg", 0.0), 2), "rows": rows}
        bl = math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1])
        # a short line (close-set eyes, a profile chest) turns a sub-pixel wobble into degrees: the angle tolerance is
        # the larger of LINE_TOL_DEG and the angle that lifts one end by LINE_TOL_PX
        out["worst"][name] = {"dy_px": round(wdy, 2), "ddeg": round(wdeg, 2), "baseline_px": round(bl, 1),
                              "tol_deg": round(max(LINE_TOL_DEG, math.degrees(math.atan2(LINE_TOL_PX, bl or 1))), 2)}
    ws = out["worst"].values()
    if any(not v.get("ok") for v in out["lines"].values()):
        out["verdict"] = "UNMEASURED"
    elif all(v["dy_px"] <= LINE_TOL_PX and v["ddeg"] <= v["tol_deg"] for v in ws):
        out["verdict"] = "LEVEL"
    else:
        out["verdict"] = "MOVING"
    return out


def _font(sz: int):
    from PIL import ImageFont
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(p, sz)
        except OSError:
            pass
    return ImageFont.load_default(size=sz)


LINE_COLS = {"eye": (0, 235, 255), "shoulder": (255, 215, 0)}


def lines_sheet(set_name: str, facings: list[tuple[str, list[np.ndarray], dict, int]], tile: int = 256) -> Image.Image:
    """One contact sheet for a set: a row per facing, a column per frame; on every frame the eye line (cyan) and the
    shoulder line (yellow) drawn through the points found IN THAT FRAME and extended across the tile, the reference
    frame's line as a thin white guide, and the numbers printed underneath."""
    f_title, f_txt = _font(18), _font(13)
    ncol = max(len(fr) for _, fr, _, _ in facings) if facings else 1
    txt_h, head_h, title_h = 52, 22, 30
    sheet = Image.new("RGB", (ncol * tile, title_h + len(facings) * (head_h + tile + txt_h)), (40, 36, 32))
    d = ImageDraw.Draw(sheet)
    d.text((6, 5), f"{set_name}: eye line (cyan), shoulder line (yellow); white = master frame's line", fill=(255, 255, 255),
           font=f_title)
    y = title_h
    for facing, frames, lc, ref_idx in facings:
        wv = lc["worst"]
        summ = "  ".join(f"{n} worst {wv[n]['dy_px']}px {wv[n]['ddeg']}deg" for n in wv)
        d.text((6, y + 3), f"{facing.upper()}  {lc['verdict']}  (master frame {ref_idx + 1})  {summ}", fill=(255, 235, 200),
               font=f_txt)
        y += head_h
        for i, fr in enumerate(frames):
            ox = i * tile
            s = tile / fr.shape[1]
            bg = Image.new("RGBA", (fr.shape[1], fr.shape[0]), (118, 118, 118, 255))
            bg.alpha_composite(Image.fromarray(fr, "RGBA"))
            sheet.paste(bg.convert("RGB").resize((tile, tile), Image.LANCZOS), (ox, y))
            if i == ref_idx:
                d.rectangle([ox, y, ox + tile - 1, y + tile - 1], outline=(255, 255, 255), width=2)
            lines = []
            for n, L in lc["lines"].items():
                if not L.get("rows"):
                    lines.append(f"{n}: {L['label']}")
                    continue
                base, row = L["rows"][ref_idx], L["rows"][i]
                for rr, col, wdt in ((base, (255, 255, 255), 1), (row, LINE_COLS[n], 2)):
                    if "pts" not in rr or not rr.get("ok"):
                        continue
                    (ax, ay), (bx, by) = rr["pts"]
                    if math.hypot(bx - ax, by - ay) < 1e-6:
                        continue
                    # the line through both points, extended to 0.6 canvas widths about its midpoint
                    mx_, my_ = (ax + bx) / 2, (ay + by) / 2
                    ln = math.hypot(bx - ax, by - ay)
                    ux, uy = (bx - ax) / ln, (by - ay) / ln
                    half = max(ln / 2 + 8, 0.3 * fr.shape[1])
                    d.line([(ox + (mx_ - ux * half) * s, y + (my_ - uy * half) * s),
                            (ox + (mx_ + ux * half) * s, y + (my_ + uy * half) * s)], fill=col, width=wdt)
                for px, py in row.get("pts", []):
                    d.ellipse([ox + px * s - 3, y + py * s - 3, ox + px * s + 3, y + py * s + 3],
                              outline=LINE_COLS[n] if row.get("ok") else (255, 40, 40), width=2)
                lines.append(f"{n[:3]} dy {row.get('dy', float('nan')):+.2f}px  {row.get('ddeg', float('nan')):+.2f}deg"
                             + ("" if row.get("ok") else " LOST"))
            for j, t in enumerate([f"frame {i + 1}"] + lines):
                d.text((ox + 4, y + tile + 2 + j * 16), t, fill=(255, 255, 255), font=f_txt)
        y += tile + txt_h
    return sheet


def load_set(name: str, src: Path | None, facing: str):
    cfg = json.loads((HERE / "flyer_cutout_sets" / f"{name}.json").read_text())
    folder = Path(src) if src else REPO / cfg["folder"]
    paths = FC.FL.frame_paths(folder, cfg["prefix"], facing)
    frames = [np.asarray(Image.open(p).convert("RGBA")) for p in paths]
    fc = cfg["facings"].get(facing, {})
    return cfg, fc, paths, frames


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--set", required=True, nargs="+",
                    help="flyer_cutout_sets/<Set>.json name(s) (hold the body annotation); several only with --lines")
    ap.add_argument("--src", type=Path, help="read frames here instead of the set's Textures folder")
    ap.add_argument("--facing", choices=("north", "east", "south"))
    ap.add_argument("--ref", type=int, help="reference frame (default: the set's master for that facing, else 1)")
    ap.add_argument("--overlay", type=Path, help="write the body overlay strip(s); facing is appended")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--lines", type=Path, metavar="DIR",
                    help="owner's line test instead: eye line + shoulder line on every frame; writes DIR/<Set>_lines.png "
                         "per set, DIR/flier_lines_all.png when several sets, DIR/flier_lines.json")
    a = ap.parse_args(argv)
    if a.lines:
        return main_lines(a)
    out, worst_rc = {}, 0
    if len(a.set) != 1:
        ap.error("several --set names need --lines")
    a.set = a.set[0]
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
        if int(mask.sum()) < 30:
            print(f"UNMEASURED {a.set} {facing}: the protect polygons cover {int(mask.sum())} opaque px of frame {ref + 1}")
            worst_rc = max(worst_rc, 2)
            continue
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


def main_lines(a) -> int:
    a.lines.mkdir(parents=True, exist_ok=True)
    report, sheets, rc = {}, [], 0
    for name in a.set:
        facs = []
        for facing in ([a.facing] if a.facing else ["north", "east", "south"]):
            cfg, fc, paths, frames = load_set(name, a.src, facing)
            if len({f.shape for f in frames}) != 1 or len(frames) < 2:
                print(f"UNMEASURED {name} {facing}: {len(frames)} frames of mixed or single size")
                rc = max(rc, 2)
                continue
            ref_idx = (a.ref or fc.get("master", 1)) - 1
            lc = line_check(frames, fc, facing, ref_idx)
            facs.append((facing, frames, lc, ref_idx))
            wv = lc["worst"]
            print(f"{lc['verdict']:10} {name} {facing} (master {ref_idx + 1}): "
                  + "; ".join(f"{n} [{lc['lines'][n]['label']}] worst {wv[n]['dy_px']} px / {wv[n]['ddeg']} deg"
                              if n in wv else f"{n} [{lc['lines'][n]['label']}]" for n in lc["lines"]))
            report.setdefault(name, {})[facing] = {"verdict": lc["verdict"], "worst": wv, "master": ref_idx + 1,
                                                   "lines": lc["lines"]}
            rc = max(rc, {"LEVEL": 0, "MOVING": 1}.get(lc["verdict"], 2))
        sh = lines_sheet(name, facs)
        p = a.lines / f"{name}_lines.png"
        sh.save(p)
        sheets.append(sh)
        print("sheet", p)
    if len(sheets) > 1:
        W = max(s.width for s in sheets)
        big = Image.new("RGB", (W, sum(s.height for s in sheets)), (40, 36, 32))
        y = 0
        for s in sheets:
            big.paste(s, (0, y))
            y += s.height
        p = a.lines / "flier_lines_all.png"
        big.save(p)
        print("combined", p)
    (a.lines / "flier_lines.json").write_text(json.dumps(report, indent=1, default=float))
    return rc


if __name__ == "__main__":
    sys.exit(main())
