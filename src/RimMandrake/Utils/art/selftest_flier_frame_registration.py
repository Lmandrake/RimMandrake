#!/usr/bin/env python3
"""selftest_flier_frame_registration.py - the instrument must SEE body jitter and must IGNORE wing flap.

Fixture: a 20x14 rigid body block plus a thin (3 px) wing whose length and height change every frame.
  STATIC  body fixed, wing flapping: body drift 0, but the alpha-bbox centre drifts (the wrong metric moves).
  JITTER  same wings, body shifted 3 px right in frame 3: body drift ~3 px, verdict OFFENDER.
Sanity probe: the JITTER case must fail where STATIC passes, so the instrument is shown able to fail.
In-memory only; no files written.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import flier_frame_registration as F  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + (f"  {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


def frame(wing_len, wing_dy, body_dx=0, size=96):
    a = np.zeros((size, size), np.uint8)
    bx, by = 38 + body_dx, 40
    a[by:by + 14, bx:bx + 20] = 255                                    # rigid body
    y = by + 5 + wing_dy
    a[y:y + 3, bx + 20:bx + 20 + wing_len] = 255                       # thin wing, right
    a[y:y + 3, max(0, bx - wing_len):bx] = 255                         # thin wing, left
    return a


POSES = [(30, -22), (18, -8), (6, 6), (18, 20)]
static = [frame(l, dy) for l, dy in POSES]
jitter = [frame(l, dy, 3 if i == 2 else 0) for i, (l, dy) in enumerate(POSES)]

s = F.measure_frames(static)
j = F.measure_frames(jitter)
check("static body: body drift is 0", s["body_span"] < 0.5, f"{s['body_span']:.2f}px")
check("static body, flapping wing: bbox centre DOES drift (the wrong metric moves)", s["bbox_span"] > 5, f"{s['bbox_span']:.1f}px")
check("jittering body: drift ~3 px", 2.0 <= j["body_span"] <= 4.0, f"{j['body_span']:.2f}px")
check("sensitivity (1.5x opening) agrees on the static set", s["sens_span"] < 0.5, f"{s['sens_span']:.2f}px")


def as_result(m):
    return {"frames": 4, "body_px": m["body_span"], "body_frac": m["body_frac"]}


check("verdict OK on static", F.verdict(as_result(s)) == "OK")
check("verdict OFFENDER on jitter (sanity probe: instrument can fail)", F.verdict(as_result(j)) == "OFFENDER")
check("verdict SINGLE on one frame", F.verdict({"frames": 1}) == "SINGLE")
b = F.body_of(frame(30, -22))
check("opening removes the thin wing (body mask is the block)", int(b.sum()) == 20 * 14, f"area {int(b.sum())}")

def rgba(a, dx=0):
    o = np.zeros(a.shape + (4,), np.uint8)
    o[..., 3] = a
    o[..., :3] = np.where(a[..., None] > 0, 120, 0)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    o[..., 0] = (((xx - dx) * 7 + yy * 13) % 200) * (a > 0)      # texture so the match has something to lock to
    return o


sm = F.measure_frames(static, [rgba(a) for a in static])
jm = F.measure_frames(jitter, [rgba(a, 3 if i == 2 else 0) for i, a in enumerate(jitter)])
check("mask-overlap: static body, flapping wings -> ~0 px", sm["match_span"] < 1.5, f"{sm['match_span']:.2f}px")
check("mask-overlap sanity probe: 3 px body jitter is seen", 2.0 <= jm["match_span"] <= 4.5, f"{jm['match_span']:.2f}px")

print("PASS" if not FAILS else f"FAILED: {FAILS}")
sys.exit(1 if FAILS else 0)
