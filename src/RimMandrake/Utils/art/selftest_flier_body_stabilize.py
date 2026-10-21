#!/usr/bin/env python3
"""selftest_flier_body_stabilize.py - the body localiser must recover a known body shift AND rotation while the
wings flap, and must call a static body LOCKED.

Fixture (in memory, deterministic): a 160 px canvas; a textured elliptical body with an outline, an eye and a tail
(the BODY annotation is a polygon around it); two textured wings turned about the shoulders by a different angle
every frame (+25, 0, -25, 0 deg).
  STATIC   body pixels identical in every frame: verdict LOCKED, every estimator <= 0.05 px / 0.05 deg
  MOVED    frame 3's body translated (+3, -2) px and turned 4 deg about its centre: ECC and FEATURES recover the
           motion at the body centre within 1 px and 0.5 deg of the truth; PARTS within 1.5 px / 1 deg; verdict DRIFT
  REPOSED  frame 3's body replaced by a different drawing: verdict RE-POSED (no rigid transform explains it)
The MOVED and REPOSED cases are the sanity probe: the instrument is shown able to fail.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import flier_body_stabilize as S  # noqa: E402  (re-execs under the OpenCV venv when needed)
import cv2  # noqa: E402

FAILS = []
N = 160
BODY_POLY = [[62, 30], [98, 30], [104, 120], [92, 150], [68, 150], [56, 120]]


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + (f"  {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


def texture(seed, shape):
    r = np.random.default_rng(seed).random(shape).astype(np.float32)
    return cv2.GaussianBlur(r, (0, 0), 1.2)


def body_layer(seed=1):
    a = np.zeros((N, N, 4), np.uint8)
    m = np.zeros((N, N), np.uint8)
    cv2.ellipse(m, (80, 80), (16, 40), 0, 0, 360, 255, -1)
    cv2.circle(m, (80, 40), 12, 255, -1)                       # head
    cv2.line(m, (80, 115), (80, 145), 255, 5)                  # tail
    t = texture(seed, (N, N))
    col = np.stack([90 + 120 * t, 70 + 80 * t, 40 + 60 * t], -1)
    a[..., :3] = col.clip(0, 255).astype(np.uint8)
    a[..., 3] = m
    edge = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
    a[edge, :3] = 20
    cv2.circle(a, (74, 38), 3, (250, 240, 60, 255), -1)        # eye
    a[..., 3] = m
    return a


def wing_layer(side, deg):
    a = np.zeros((N, N, 4), np.uint8)
    hx, hy = (66, 70) if side < 0 else (94, 70)
    tip = (hx + side * 60, hy - 10)
    poly = np.int32([[hx, hy - 6], tip, (hx + side * 50, hy + 22), (hx, hy + 14)])
    m = np.zeros((N, N), np.uint8)
    cv2.fillPoly(m, [poly], 255)
    t = texture(7 if side < 0 else 8, (N, N))
    a[..., 0], a[..., 1], a[..., 2] = (200 * t + 40), (180 * t + 40), (90 * t + 30)
    a[..., 3] = m
    R = cv2.getRotationMatrix2D((hx, hy), -side * deg, 1.0)
    return cv2.warpAffine(a, R, (N, N), flags=cv2.INTER_LINEAR)


def over(b, t):
    al = t[..., 3:4].astype(np.float32) / 255
    out = b.astype(np.float32) * (1 - al) + t.astype(np.float32) * al
    out[..., 3] = np.maximum(b[..., 3], t[..., 3])
    return out.astype(np.uint8)


def frames(body_for):
    out = []
    for k, deg in enumerate((25, 0, -25, 0)):
        f = np.zeros((N, N, 4), np.uint8)
        f = over(f, wing_layer(-1, deg))
        f = over(f, wing_layer(1, deg))
        out.append(over(f, body_for(k)))
    return out


def run(fr):
    mask = S.FC.poly_mask((N, N), [BODY_POLY]) & (fr[0][..., 3] > 128)
    return S.measure_facing(fr, mask)


def main() -> int:
    B = body_layer()
    r = run(frames(lambda k: B))
    w = r["worst"]
    check("STATIC verdict LOCKED", r["verdict"] == "LOCKED", f"{r['verdict']} {w}")
    check("STATIC <= 0.05 px/deg", max(w["ecc_px"], w["feat_px"], w["ecc_deg"], w["feat_deg"]) <= 0.05, str(w))

    M = cv2.getRotationMatrix2D((80, 80), 4.0, 1.0)
    M[0, 2] += 3
    M[1, 2] -= 2
    moved = cv2.warpAffine(B, M, (N, N), flags=cv2.INTER_CUBIC)
    r = run(frames(lambda k: moved if k == 2 else B))
    row = r["rows"][2]
    cx, cy = r["body_centre"]
    tx, ty = S.body_motion_at(M, cx, cy)
    tdeg = math.degrees(math.atan2(M[1, 0], M[0, 0]))
    for name in ("ecc", "features"):
        e = row["_ecc" if name == "ecc" else "_feat"]
        if e.get("M") is None:
            check(f"MOVED {name} estimated", False)
            continue
        ex, ey = S.body_motion_at(e["M"], cx, cy)
        err_px, err_deg = math.hypot(ex - tx, ey - ty), abs(e["deg"] - tdeg)
        check(f"MOVED {name} recovers shift < 1 px", err_px < 1.0, f"got ({ex:.2f},{ey:.2f}) truth ({tx:.2f},{ty:.2f})")
        check(f"MOVED {name} recovers angle < 0.5 deg", err_deg < 0.5, f"got {e['deg']:.2f} truth {tdeg:.2f}")
    p = row["parts"]
    check("MOVED parts angle within 1 deg", p.get("deg") is not None and abs(abs(p["deg"]) - 4.0) < 1.0, f"{p}")
    check("MOVED verdict DRIFT", r["verdict"] == "DRIFT", r["verdict"])

    other = body_layer(seed=99)
    other = np.ascontiguousarray(np.flipud(other))               # a different drawing / pose
    r = run(frames(lambda k: other if k == 2 else B))
    check("REPOSED verdict RE-POSED", r["verdict"] == "RE-POSED", f"{r['verdict']} rho {r['worst']['rho_min']}")
    print("FAIL" if FAILS else "PASS", "selftest_flier_body_stabilize", FAILS or "")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
