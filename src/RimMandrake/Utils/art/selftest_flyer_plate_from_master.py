#!/usr/bin/env python3
"""selftest_flyer_plate_from_master.py — synthetic fixture: master = body ellipse + two wings (no legs);
donor = same body shifted (1,1) plus thin 1-px legs in a distinct colour, no wings.
Proves: wings are masked out; body pixels equal the master's; donor legs are pasted (donor colour);
the output is deterministic; the plate then passes flyer_lock's re-pose gate against the master."""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import flyer_lock as FL  # noqa: E402
import flyer_plate_from_master as PM  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    n = 128
    yy, xx = np.mgrid[:n, :n]
    body = ((xx - 64) / 14.0) ** 2 + ((yy - 64) / 9.0) ** 2 <= 1
    wing = (((xx - 64) / 40.0) ** 2 + ((yy - 40) / 8.0) ** 2 <= 1) & ~body
    rng = np.random.RandomState(1)
    tex = rng.randint(0, 20, (n, n, 1))
    master = np.zeros((n, n, 4), np.int16)
    master[body] = np.concatenate([np.array([150, 120, 90]) + tex[body], [[255]] * body.sum()], 1)
    master[wing] = [60, 90, 160, 255]
    donor = np.zeros_like(master)
    ds = ((xx - 65) / 14.0) ** 2 + ((yy - 65) / 9.0) ** 2 <= 1
    donor[ds] = [150, 120, 90, 255]
    legs = np.zeros((n, n), bool); legs[76:90, 60] = True; legs[76:90, 70] = True
    donor[legs] = [200, 30, 30, 255]
    p1, info = PM.derive(master, donor)
    p2, _ = PM.derive(master, donor)
    check(np.array_equal(p1, p2), "deterministic")
    a = p1[..., 3] > 128
    check(not (a & wing).any(), "no wing pixel survives")
    inner = a & body
    check(inner.sum() > 0.85 * body.sum(), f"body kept ({int(inner.sum())}/{int(body.sum())})")
    check((p1[inner & (p1[..., 0] != 200)][:, :3] == master[inner & (p1[..., 0] != 200)][:, :3]).all(), "body pixels are the master's")
    leg_red = a & (p1[..., 0] == 200)
    check(leg_red.sum() >= 20, f"donor legs pasted ({int(leg_red.sum())} px)")
    _, li = FL.lock_frame(p1, master)
    check(not li["rejected"] and li["alpha_cover"] >= 0.92, f"plate passes re-pose gate vs master ({li['alpha_cover']:.3f})")
    print(f"\n{'OK' if not FAILS else 'FAILED'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
