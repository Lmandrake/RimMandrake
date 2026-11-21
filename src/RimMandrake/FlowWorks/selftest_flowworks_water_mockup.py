#!/usr/bin/env python3
"""selftest_flowworks_water_mockup.py — RIMMANDRAKE_MOCK_FLOWWORKS_WATER_BY_DEPTH_ON_REAL_GROUND.

WHY: the owner picks the water target from offline mockups (model/water_mockup.py). A pick means something only if the
mockup's SHIPPED row is what the game draws today. This keeps that true:
  1. SHIPPED over a 4 m pit floor at 2 m reproduces the colour measured in the 2026-11-12 capture BP3 (within 0.02 a
     channel; it was 0.011 when written);
  2. SHIPPED hides exactly what RM_UnderLiquid.Seen hides (via model/underliquid.py) at every mockup depth, and the
     figures the item quotes (6% at 0.2 m, 15% at 0.5 m, 30% at 1 m, 56% at 2 m, 90% at 5 m);
  3. every candidate is a different look (no two hide the same at every depth with the same colour), each hides more
     with depth (never clearer deeper), and the dry case is untouched.
CAN IT FAIL: a planted halved law and a planted pale body colour must each turn check 1 red (run in this file).
Textures are not needed: the checks read the laws only.
    python3 src/RimMandrake/FlowWorks/selftest_flowworks_water_mockup.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "model"))
import underliquid as ul  # noqa: E402
import water_mockup as wm  # noqa: E402

ITEM_FIGURES = {0.2: 0.06, 0.5: 0.15, 1.0: 0.30, 2.0: 0.56, 5.0: 0.90}


def calibration_error(law):
    floor = np.array((0.358, 0.289, 0.225), np.float32) * wm.floor_brightness(8)
    got = law(floor[None, :], np.array([2.0], np.float32))[0]
    return float(np.abs(got - np.array(wm.CAPTURE["water 2 m over a 4 m pit floor"], np.float32)).max())


def main():
    fails = []
    err = calibration_error(wm.law_shipped)
    print(f"1 calibration: worst {err:.4f} limit 0.02 cases 1")
    if err > 0.02:
        fails.append(f"SHIPPED misses the BP3 capture by {err:.4f}")

    worst, n = 0.0, 0
    for d in wm.DEPTHS[1:]:
        want = 1.0 - ul.seen(ul.REFERENCE_CLARITY, d)
        worst = max(worst, abs(wm.hides(wm.law_shipped, d) - want))
        n += 1
    for d, fig in ITEM_FIGURES.items():
        worst = max(worst, abs(round(wm.hides(wm.law_shipped, d), 2) - fig))
        n += 1
    print(f"2 SHIPPED = RM_UnderLiquid.Seen and the item's figures: worst {worst:.4f} limit 0.005 cases {n}")
    if worst > 0.005:
        fails.append(f"SHIPPED hides differ from the law by {worst:.4f}")

    sigs, mono_bad, dry_bad = {}, [], []
    grey = np.array([[0.5, 0.5, 0.5]], np.float32)
    for key, _n, fn, _d in wm.CANDIDATES:
        h = [round(wm.hides(fn, d), 3) for d in wm.DEPTHS[1:]]
        sigs.setdefault((tuple(h), tuple(wm.colour_at(fn, 1.0))), []).append(key)
        if any(b < a - 1e-6 for a, b in zip(h, h[1:])):
            mono_bad.append(key)
        if np.abs(fn(grey, np.array([0.0], np.float32)) - grey).max() > 1e-6:
            dry_bad.append(key)
    same = [v for v in sigs.values() if len(v) > 1]
    print(f"3 candidates: {len(wm.CANDIDATES)} read, identical groups {same}, clearer-deeper {mono_bad}, wet-when-dry {dry_bad}")
    if same or mono_bad or dry_bad:
        fails.append(f"candidates: identical {same}, clearer deeper {mono_bad}, wet when dry {dry_bad}")

    # 4. a thing's cover equals the law for every plain-sheet law (the game draws a thing's cover as one colour at one
    #    alpha; only CLEAR needs the stand-in)
    rng = np.random.default_rng(7)
    rgb, m = rng.random((200, 3)).astype(np.float32), (rng.random(200) * 8).astype(np.float32)
    off = {k: float(np.abs(wm.as_cover(fn)(rgb, m) - fn(rgb, m)).max()) for k, _n, fn, _d in wm.CANDIDATES}
    bad = [k for k, v in off.items() if k != "CLEAR" and v > 1e-5]
    print(f"4 thing cover = law for plain sheets: worst {max(v for k, v in off.items() if k != 'CLEAR'):.2e} limit 1e-5 "
          f"cases {200 * (len(off) - 1)}; CLEAR stand-in differs by {off['CLEAR']:.3f}")
    if bad:
        fails.append(f"thing cover differs from the law for {bad}")

    # can it fail: two planted faults must each turn check 1 red
    body = wm.BODY_SHIPPED

    def halved(rgb, m):
        s = np.vectorize(lambda x: ul.seen_halved(ul.REFERENCE_CLARITY, float(x)))(m).astype(np.float32)[..., None]
        return body + (rgb - body) * s

    def pale(rgb, m):
        s = np.vectorize(lambda x: ul.seen(ul.REFERENCE_CLARITY, float(x)))(m).astype(np.float32)[..., None]
        p = np.array(ul.WATER_COLOUR, np.float32)
        return p + (rgb - p) * s

    for name, law in (("halved law", halved), ("pale body", pale)):
        e = calibration_error(law)
        print(f"  planted {name}: calibration worst {e:.4f} -> {'RED (good)' if e > 0.02 else 'GREEN (blind!)'}")
        if e <= 0.02:
            fails.append(f"check 1 is blind to a planted {name}")

    if fails:
        print("FAIL: " + "; ".join(fails))
        return 1
    print("PASS selftest_flowworks_water_mockup")
    return 0


if __name__ == "__main__":
    sys.exit(main())
