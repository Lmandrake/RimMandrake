#!/usr/bin/env python3
"""selftest_flyer_lock.py — flyer_lock.py's guarantees (FLYER_STABLE_BODY_GATE_1).

The fixture is a synthetic painterly body plate with a textured ellipse, neck, head and long tail, plus
three "generated" frames. Each frame is the body redrawn with sub-threshold repaint noise, a few re-shading
speckles, a known shift and a different wing pose. Fixtures are written under
/home/mandrake/rm/scratch/BENCH/flyer_lock/selftest, never /tmp.
Proves the following:
  - lock recovers the shift;
  - locked frames keep the plate byte-identical wherever no wing is, and pass the floor;
  - frame 4 is a byte copy of frame 2;
  - speckle is dropped;
  - a re-posed body is REJECTED.
SANITY PROBE: `check` must FAIL the raw unlocked frames, so the checker is shown able to fail.
compose (the layer recipe) passes, and the CLI exit codes are 0 for a pass and 1 for a failure.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import flyer_lock as FL  # noqa: E402

ROOT = Path("/home/mandrake/rm/scratch/BENCH/flyer_lock/selftest")
FAILS = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:300]}]"))
    if not cond:
        FAILS.append(msg)


def body_plate(rng) -> np.ndarray:
    a = np.zeros((256, 256, 4), np.int16)
    yy, xx = np.mgrid[0:256, 0:256]
    body = ((xx - 140) / 46.0) ** 2 + ((yy - 128) / 16.0) ** 2 <= 1
    head = ((xx - 196) / 14.0) ** 2 + ((yy - 120) / 11.0) ** 2 <= 1
    tail = (xx >= 30) & (xx <= 100) & (np.abs(yy - 130) <= 3)
    m = body | head | tail
    tex = rng.integers(0, 50, (256, 256))
    a[..., 0] = 200 + tex // 2
    a[..., 1] = 160 + tex // 3
    a[..., 2] = 120 + tex // 4
    a[..., :3] = np.clip(a[..., :3], 0, 255)
    a[..., 3] = np.where(m, 255, 0)
    a[~m, :3] = 0
    return a


def wing_layer(angle_deg: float) -> np.ndarray:
    """A pale membrane quad from the shoulder at (150,124), length 70, at ANGLE (0 = level, +90 = up)."""
    a = np.zeros((256, 256, 4), np.int16)
    yy, xx = np.mgrid[0:256, 0:256]
    t = np.deg2rad(angle_deg)
    ux, uy = np.cos(t) * 0.35, -np.sin(t)          # mostly vertical travel; a little sideways
    n = np.hypot(ux, uy); ux, uy = ux / n, uy / n
    px, py = xx - 150, yy - 124
    along = px * ux + py * uy
    across = np.abs(-px * uy + py * ux)
    m = (along >= 8) & (along <= 78) & (across <= 9)
    a[m] = (240, 225, 150, 255)
    return a


def generated(plate, wing, rng, dx, dy, speckle=True) -> np.ndarray:
    """What an edit model hands back: same body repainted with noise (L1 < 60), shifted, wings composited."""
    f = plate.copy()
    pm = plate[..., 3] > 0
    noise = rng.integers(-8, 9, (256, 256, 3))
    f[..., :3] = np.where(pm[..., None], np.clip(f[..., :3] + noise, 0, 255), 0)
    if speckle:   # isolated re-shading on the body, L1 > 60, not joined to any wing
        for (y, x) in ((128, 120), (126, 160), (131, 100)):
            f[y, x, :3] = np.clip(f[y, x, :3] - 40, 0, 255)
    wm = wing[..., 3] > 0
    f[wm] = wing[wm]
    return FL.shift(f, dx, dy)


def main() -> int:
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir(parents=True)
    rng = np.random.default_rng(7)
    plate = body_plate(rng)
    wings = [wing_layer(80), wing_layer(5), wing_layer(-60)]
    shifts = [(3, -2), (-1, 4), (0, 0)]
    raw = [generated(plate, w, rng, dx, dy) for w, (dx, dy) in zip(wings, shifts)]
    FL.save(plate, ROOT / "plate_east.png")
    for i, r in enumerate(raw, 1):
        FL.save(r, ROOT / f"gen{i}_east.png")

    # alignment
    for r, (dx, dy) in zip(raw, shifts):
        got = FL.align(plate, r)
        check(got == (-dx, -dy), f"align recovers shift {(dx, dy)}", got)

    # lock via the CLI (the path BENCH will run)
    out = ROOT / "locked"
    rc = FL.main(["lock", "--plate", str(ROOT / "plate_east.png"), "--frame", str(ROOT / "gen1_east.png"),
                  "--frame", str(ROOT / "gen2_east.png"), "--frame", str(ROOT / "gen3_east.png"),
                  "--facing", "east", "--prefix", "Test_Flying_", "--out", str(out),
                  "--report", str(ROOT / "lock_report.json")])
    check(rc == 0, "lock CLI exits 0 on a good set", rc)
    paths = FL.frame_paths(out, "Test_Flying_", "east")
    check(len(paths) == 4, "3 poses -> 4 frames (ping-pong)", [p.name for p in paths])
    fr = [FL.load(p) for p in paths]
    check(np.array_equal(fr[3], fr[1]), "frame 4 is a byte copy of frame 2")
    rep = FL.check(fr, "east", plate)
    check(rep["pass"], "locked set passes check", rep)
    check(rep.get("plate_free_identical") == 1.0, "plate pixels outside wings identical in every frame", rep)
    check(rep["locked_share"] >= FL.FLOORS["east"], f"locked share {rep['locked_share']} >= east floor", rep)
    wing_union = np.logical_or.reduce([w[..., 3] > 0 for w in wings])
    for (y, x) in ((128, 120), (126, 160), (131, 100)):
        if not wing_union[y, x]:
            check(all((f[y, x] == plate[y, x]).all() for f in fr), f"speckle at {(y, x)} replaced by plate")
    # wings really did come through
    check(all(((f[..., 3] > 0) & ~(plate[..., 3] > 0)).sum() > 300 for f in fr[:3]),
          "every locked frame carries its wing outside the body")

    # SANITY PROBE: the unlocked frames (aligned, so only repaint differs) must FAIL the plate-identity gate
    raw_al = [FL.shift(r, -dx, -dy) for r, (dx, dy) in zip(raw, shifts)]
    unlocked = FL.pingpong(raw_al)
    rep_raw = FL.check(unlocked, "east", plate)
    check(not rep_raw["pass"] and rep_raw.get("plate_free_identical", 1) < 1.0,
          f"SANITY: check FAILS unlocked frames (identity {rep_raw.get('plate_free_identical')})", rep_raw)
    # and heavy repaint (a redrawn body) fails the share floor even without a plate
    heavy = [r.copy() for r in raw_al]
    for h in heavy:
        h[..., :3] = np.clip(h[..., :3] + rng.integers(-60, 61, h[..., :3].shape), 0, 255)
    rep_heavy = FL.check(FL.pingpong(heavy), "east")
    check(not rep_heavy["pass"], f"SANITY: redrawn bodies fail the share floor ({rep_heavy['locked_share']})",
          rep_heavy)

    # re-posed body is rejected: the tail moves 30 px down, beyond the ±8 search
    reposed = generated(plate, wings[1], rng, 0, 0)
    tail = (reposed[..., 3] > 0) & (np.mgrid[0:256, 0:256][1] < 100)
    moved = reposed.copy(); moved[tail] = 0
    moved[np.roll(tail, 30, axis=0)] = reposed[tail]
    _, info = FL.lock_frame(plate, moved)
    check(info["rejected"], f"re-posed frame rejected (alpha cover {info['alpha_cover']})", info)
    FL.save(moved, ROOT / "gen_reposed_east.png")
    rc = FL.main(["lock", "--plate", str(ROOT / "plate_east.png"), "--frame", str(ROOT / "gen1_east.png"),
                  "--frame", str(ROOT / "gen_reposed_east.png"), "--frame", str(ROOT / "gen3_east.png"),
                  "--facing", "east", "--prefix", "Test_Flying_", "--out", str(ROOT / "locked_bad")])
    check(rc == 1 and not FL.frame_paths(ROOT / "locked_bad", "Test_Flying_", "east"),
          "lock CLI exits 1 and writes nothing when a frame is re-posed", rc)

    # compose (layer recipe), wings over the body
    for i, w in enumerate(wings, 1):
        FL.save(w, ROOT / f"wing{i}_east.png")
    rc = FL.main(["compose", "--body", str(ROOT / "plate_east.png"), "--wing", str(ROOT / "wing1_east.png"),
                  "--wing", str(ROOT / "wing2_east.png"), "--wing", str(ROOT / "wing3_east.png"),
                  "--order", "over", "--facing", "east", "--prefix", "Comp_Flying_", "--out", str(ROOT / "comp")])
    check(rc == 0, "compose CLI exits 0", rc)
    rc = FL.main(["check", "--dir", str(ROOT / "comp"), "--prefix", "Comp_Flying_", "--facing", "east",
                  "--plate", str(ROOT / "plate_east.png")])
    check(rc == 0, "check CLI exits 0 on the composed set", rc)

    # option C: body-colour noise inside the plate is NOT wing; a wing sweeping across the body IS (near the wing)
    f0 = plate.copy()
    pm0 = plate[..., 3] > 0
    nz = np.zeros((256, 256), bool); nz[120:140, 60:180] = True   # a big body-interior patch, L1 > 60, no wing
    f0[nz & pm0, :3] = np.clip(f0[nz & pm0, :3] - 50, 0, 255)
    f0[nz & pm0, 3] = 255
    out0, i0 = FL.lock_frame(plate, f0)
    check(i0["body_px_as_wing"] == 0 and np.array_equal(out0, plate),
          f"C: body-colour patch inside plate is not wing ({i0['body_px_as_wing']} px)", i0)
    # a wing attached to the body and crossing it: outside part + its membrane over the body, far-from-wing body stays plate
    fw = plate.copy()
    sweep = wings[0][..., 3] > 0
    fw[sweep] = wings[0][sweep]
    far_nz = nz.copy(); far_nz[:, 140:] = False                  # a distant patch (x 60..140), well beyond wing depth
    fw[far_nz & pm0, :3] = np.clip(plate[far_nz & pm0, :3] - 50, 0, 255)
    outw, iw = FL.lock_frame(plate, fw)
    inside_wing = sweep & pm0 & (np.abs(outw - plate).sum(-1) > 0)
    check(inside_wing.sum() > 0 and (outw[sweep & ~pm0] == fw[sweep & ~pm0]).all(),
          f"C: a wing sweeping across the body is kept ({int(inside_wing.sum())} px over the body)", iw)
    check((outw[far_nz & pm0] == plate[far_nz & pm0]).all(), "C: body noise far from the wing stays plate")
    old = FL.lock_frame(plate, fw, wing_far=0, wing_depth=10**6)[1]["body_px_as_wing"]
    check(iw["body_px_as_wing"] <= old, f"C is stricter than the old rule ({iw['body_px_as_wing']} <= {old})")

    print(f"\n{'OK' if not FAILS else 'FAILED'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
