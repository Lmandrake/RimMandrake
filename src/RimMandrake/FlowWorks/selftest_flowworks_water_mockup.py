#!/usr/bin/env python3
"""selftest_flowworks_water_mockup.py — RIMMANDRAKE_MOCK_FLOWWORKS_WATER_BY_DEPTH_ON_REAL_GROUND.

WHY: the owner picks the water target from offline mockups (model/water_mockup.py). A pick means something only if the
mockup's SHIPPED row is what the game draws today. This keeps that true:
  1. SHIPPED over a 4 m pit floor at 2 m reproduces the colour measured in the 2026-11-12 capture BP3 (within 0.02 a
     channel; it was 0.011 when written);
  2. SHIPPED hides exactly what the 11-13 law hid (model/underliquid.py seen_approved_1113, shipped until 2026-11-20) at
     every mockup depth, and the figures the item quotes (6% at 0.2 m, 15% at 0.5 m, 30% at 1 m, 56% at 2 m, 90% at 5 m);
     and FIRM, the picked target, hides exactly what RM_UnderLiquid.Seen (model seen) hides now;
  3. every candidate is a different look (no two hide the same at every depth with the same colour), each hides more
     with depth (never clearer deeper), and the dry case is untouched.
  5. (second pass, RIMMANDRAKE_RESEARCH_FLOWWORKS_WATER_LOOK_FIRM_ALREADY_PICKED) the ground and surface effects do what
     their rows say, on a synthetic scene: no effect touches a dry pit; WET's submerged floor and the bank round a
     brim-full pit are darker than FIRM's; RIPPLE and BLEND move (frame 1 differs from frame 2) and their floor varies
     more than FIRM's at 0.2 m; every candidate names how the game would draw it.
CAN IT FAIL: a planted halved law and a planted pale body colour must each turn check 1 red; a planted dry wetten
(WET_VALUE = WET_SAT = 1) and a planted frozen animation must each turn check 5 red (run in this file).
Textures are not needed: the checks read the laws, and check 5 draws on flat synthetic ground.
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


class _StubSprites:
    """Flat stand-ins for the vanilla sprites (check 5 needs a scene, not the art)."""
    def __init__(self):
        def block(h, w, c):
            a = np.zeros((h, w, 4), np.float32)
            a[h // 4:-h // 4, w // 4:-w // 4] = (*c, 1.0)
            return a
        self.pawn = block(176, 128, (0.3, 0.4, 0.7))
        self.corpse = block(128, 176, (0.7, 0.3, 0.3))
        self.table = block(128, 128, (0.5, 0.4, 0.3))
        self.chair = block(64, 64, (0.5, 0.4, 0.3))
        self.steel = block(64, 64, (0.6, 0.6, 0.65))
        self.ladder = block(128, 64, (0.5, 0.45, 0.4))


def _scene():
    rng = np.random.default_rng(3)
    def ground(c):
        t = np.ones((1024, 1024, 4), np.float32)
        t[..., :3] = np.clip(np.array(c, np.float32) + rng.normal(0, 0.06, (1024, 1024, 1)), 0, 1)
        return t
    grounds = {k: (ground((0.62, 0.52, 0.40)), (1, 1, 1)) for k, *_ in wm.GROUNDS}
    grounds["_gravel"] = (ground((0.36, 0.29, 0.22)), (1, 1, 1))
    return grounds, _StubSprites()


def effects_check():
    """Check 5; returns the list of failures (empty = pass)."""
    grounds, sp = _scene()
    laws = {k: fn for k, _n, fn, _d in wm.CANDIDATES}
    x0, z0, x1, z1 = (v * wm.PX for v in wm.PIT)
    floor = (slice(z1 - wm.PX + 8, z1 - 8), slice(x1 - 2 * wm.PX + 8, x1 - 8))     # an open floor patch, south-east
    bank = (slice(z0 - 6, z0 - 2), slice(x0 + wm.PX, x1 - wm.PX))                  # just north of the rim
    def draw(k, d, frame=0):
        return wm.tile("sand", sp, grounds, laws[k], d, seed=4, fx=wm.fx_of(k), frame=frame)[0]
    bad = []
    firm_dry, firm1 = draw("FIRM", 0.0), draw("FIRM", 1.0)
    firm02 = draw("FIRM", 0.2)
    for k in wm.FX:
        if np.abs(draw(k, 0.0) - firm_dry).max() > 1e-6:
            bad.append(f"{k} changes a dry pit")
    for k, v in wm.FX.items():
        img = draw(k, 1.0)
        if v["wet"]:
            if not img[floor].mean() < firm1[floor].mean() - 0.01:
                bad.append(f"{k} floor under 1 m not darker than FIRM ({img[floor].mean():.3f} vs {firm1[floor].mean():.3f})")
            if not img[bank].mean() < firm1[bank].mean() - 0.02:
                bad.append(f"{k} bank at the rim not darker than FIRM ({img[bank].mean():.3f} vs {firm1[bank].mean():.3f})")
        if v["frames"] > 1:
            if np.abs(draw(k, 1.0, 1) - img).mean() < 0.002:
                bad.append(f"{k} does not move (frame 2 = frame 1)")
            if not draw(k, 0.2)[floor].std() > firm02[floor].std() + 0.005:
                bad.append(f"{k} floor at 0.2 m varies no more than FIRM's")
    missing = [k for k, *_ in wm.CANDIDATES if not wm.MECHANISM.get(k)]
    if missing:
        bad.append(f"no mechanism named for {missing}")
    return bad


def plant_dry_wetten():
    old = (wm.WET_VALUE, wm.WET_SAT)
    wm.WET_VALUE = wm.WET_SAT = 1.0
    def undo():
        wm.WET_VALUE, wm.WET_SAT = old
    return undo


def plant_frozen():
    wf, rl = wm.wave_field, wm.ripple_lines
    wm.wave_field = lambda h, w, t, ox=0, oy=0: wf(h, w, 0.0, ox, oy)
    wm.ripple_lines = lambda h, w, t, ox=0, oy=0, **kw: rl(h, w, 0.0, ox, oy, **kw)
    def undo():
        wm.wave_field, wm.ripple_lines = wf, rl
    return undo


def main():
    fails = []
    err = calibration_error(wm.law_shipped)
    print(f"1 calibration: worst {err:.4f} limit 0.02 cases 1")
    if err > 0.02:
        fails.append(f"SHIPPED misses the BP3 capture by {err:.4f}")

    worst, n = 0.0, 0
    for d in wm.DEPTHS[1:]:
        want = 1.0 - ul.seen_approved_1113(ul.REFERENCE_CLARITY, d)
        worst = max(worst, abs(wm.hides(wm.law_shipped, d) - want))
        worst = max(worst, abs(wm.hides(wm.law_firm, d) - (1.0 - ul.seen(ul.REFERENCE_CLARITY, d))))
        n += 2
    for d, fig in ITEM_FIGURES.items():
        worst = max(worst, abs(round(wm.hides(wm.law_shipped, d), 2) - fig))
        n += 1
    print(f"2 SHIPPED = the 11-13 law and the item's figures, FIRM = RM_UnderLiquid.Seen: worst {worst:.4f} limit 0.005 cases {n}")
    if worst > 0.005:
        fails.append(f"SHIPPED hides differ from the law by {worst:.4f}")

    sigs, mono_bad, dry_bad = {}, [], []
    grey = np.array([[0.5, 0.5, 0.5]], np.float32)
    for key, _n, fn, _d in wm.CANDIDATES:
        h = [round(wm.hides(fn, d), 3) for d in wm.DEPTHS[1:]]
        sigs.setdefault((tuple(h), tuple(wm.colour_at(fn, 1.0)), repr(sorted(wm.fx_of(key).items()))), []).append(key)
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

    # 5. the second pass's effects, on a synthetic scene (no texture files)
    bad5 = effects_check()
    print(f"5 effects: {'; '.join(bad5) if bad5 else 'WET darker floor and bank, RIPPLE/BLEND move and vary, dry untouched, mechanisms named'}")
    if bad5:
        fails.append("effects: " + "; ".join(bad5))
    for name, plant in (("dry wetten", plant_dry_wetten), ("frozen animation", plant_frozen)):
        undo = plant()
        try:
            got = effects_check()
        finally:
            undo()
        print(f"  planted {name}: check 5 -> {'RED (good)' if got else 'GREEN (blind!)'}")
        if not got:
            fails.append(f"check 5 is blind to a planted {name}")

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
