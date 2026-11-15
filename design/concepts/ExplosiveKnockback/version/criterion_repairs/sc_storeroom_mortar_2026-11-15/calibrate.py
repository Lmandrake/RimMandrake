#!/usr/bin/env python3
"""Calibrate sc_storeroom_mortar's goods-factor criterion, old against repaired, on the kernel's own rounding.

The kernel (RM_KnockbackMath.Cells): cells = round-half-away(raw), capped at maxCells, 0 below 1; a good's kernel cells
round raw, its wild cells round raw x 1.6 (WildCells; GoodsThrowWild = 1.6, pinned by T_JOURNAL_JOLT). A good with kernel
cells 0 is skipped too_weak (the rim) and has no move line. Every raw throw from 0.5 to cap + 2 (step 0.0005) is one good.
    python3 calibrate.py [--cap 6]
rc 0 when: a correct build (factor 1.6) fails the OLD criterion on some goods (the flaw) and passes the NEW one on every
good; and each wrong factor (1.0, 1.25, 2.0, 2.5) fails the NEW one on some good: a factor too low on a good with kernel
cells 3 or more under the cap (why the scene must stage one), a factor too high on a good of kernel cells 1 or 2."""
import argparse, math, sys


def cells(raw, cap):
    c = int(math.floor(abs(raw) + 0.5)) * (1 if raw >= 0 else -1)   # MidpointRounding.AwayFromZero
    c = min(c, cap)
    return 0 if c < 1 else c


def old_ok(k, w):
    return 1.3 <= w / k <= 2.0


def band(k, cap, f=1.6):
    """-> (lo, hi): the wild cells a throw that rounds to k cells can round to at factor f, capped."""
    if k >= cap:
        return cap, cap
    return max(k, cells(f * (k - 0.5), cap)), cells(f * (k + 0.5), cap)


def new_ok(k, w, cap):
    lo, hi = band(k, cap)
    return lo <= w <= hi


def goods(cap, f):
    n = int((cap + 2 - 0.5) / 0.0005)
    for i in range(n + 1):
        raw = 0.5 + i * 0.0005
        k, w = cells(raw, cap), cells(raw * f, cap)
        if k >= 1:
            yield raw, k, w


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cap", type=int, default=6); cap = ap.parse_args().cap
    bad = []
    g = list(goods(cap, 1.6))
    old_fail = [x for x in g if not old_ok(x[1], x[2])]
    new_fail = [x for x in g if not new_ok(x[1], x[2], cap)]
    print("cap %d; bands at 1.6: %s" % (cap, ", ".join("%d->%d-%d" % ((k,) + band(k, cap)) for k in range(1, cap + 1))))
    print("factor 1.6 (correct): OLD fails %d of %d goods (%.1f%%), e.g. kernel %s; NEW fails %d" % (
        len(old_fail), len(g), 100.0 * len(old_fail) / len(g),
        sorted({"%d wild %d" % (k, w) for _, k, w in old_fail})[:6], len(new_fail)))
    if not old_fail:
        bad.append("the old criterion passes every correct good: no flaw to repair")
    if new_fail:
        bad.append("the new criterion fails a correct build: %s" % new_fail[:3])
    for f in (1.0, 1.25, 2.0, 2.5):
        gf = list(goods(cap, f))
        caught = sorted({k for _, k, w in gf if not new_ok(k, w, cap)})
        where = range(3, cap) if f < 1.6 else range(1, 3)
        print("factor %.2f (wrong): NEW fails goods with kernel cells %s" % (f, caught or "none"))
        if not [k for k in caught if k in where]:
            bad.append("factor %.2f is not caught at any kernel cells %s" % (f, list(where)))
    print("calibration: %s" % ("PASS" if not bad else "FAIL -- " + "; ".join(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
