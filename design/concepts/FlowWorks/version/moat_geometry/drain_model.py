"""The moat's drain, by the mod's own kernel twin (northstar/level_water.py, differential-tested to the dL against RM_FlowKernel).

levels(W, plot, notches, sluices, pit) -> the moat surface in metres of water after each 250-tick pulse (index 0 = full).
`pit` is a list of (x, z) offsets from the moat's east bank at mid height (x=1 is the column beside the sluice column)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[os.pardir] * 5))
sys.path.insert(0, os.path.join(ROOT, 'src/RimMandrake/FlowWorks/northstar'))
sys.path.insert(0, os.path.join(ROOT, 'src/RimMandrake/Utils'))
sys.path.insert(0, os.path.join(ROOT, 'src/RimMandrake/Utils/modcheck'))
import validation_v2 as v          # noqa: E402

U = v.level_water.U                # dL of one 0.5 m notch on one square


def ring(W, plot):
    n = plot + 2 * W
    return [(i, j) for i in range(n) for j in range(n) if i < W or i >= n - W or j < W or j >= n - W]


def rect_pit(w, h):
    """The scene's pit: w columns by h rows from x=1, centred on the sluice row."""
    return [(1 + i, j - h // 2) for i in range(w) for j in range(h)]


def levels(W, plot, notches, pit, pit_notches=20, sluices=1, max_pulses=60, sluice_notches=None, water=None):
    n = plot + 2 * W
    mid = n // 2 - 1
    cells = ring(W, plot)
    gates = [(n, mid + k - sluices // 2) for k in range(sluices)]
    pits = [(n + dx, mid + dz) for dx, dz in pit]
    assert not set(pits) & set(gates), 'a pit square on a sluice'
    ox = oz = 25
    o = v.PulseOracle(n + 80, n + 60, {}, {}, per=1, budget=True)
    sh = lambda c: (c[0] + ox, c[1] + oz)       # noqa: E731
    for c in cells:
        o.D[sh(c)] = notches
        o.W[sh(c)] = notches * U if water is None else int(round(water / 0.5 * U))
    for c in gates:
        o.D[sh(c)] = sluice_notches or notches
        o.W[sh(c)] = 0
    for c in pits:
        o.D[sh(c)] = pit_notches
        o.W[sh(c)] = 0
    for c in o.D:
        o.F[c] = o.W[c] // U
    out = [notches * 0.5 if water is None else water]
    for _ in range(max_pulses):
        o.pulse()
        wet = [o.W[sh(c)] for c in cells]
        out.append(max(wet) * 0.5 / U)
        if not any(wet):
            break
    return out


# recorded live (visit_8 run 050452, ring 2 wide round an 8 x 8 plot, 6 notches, 7 x 7 pit 20 notches), dL per moat square
LIVE_2W = [59259, 56829, 49882, 39333, 26391, 15192, 5405, 0]

if __name__ == '__main__':
    # the scene's pit: x +13..+19 = 1..7 past the sluice column (+12), z +2..+8, sluice on row z +5
    got = levels(2, 8, 6, rect_pit(7, 7))
    print('model', [round(x / 0.5 * U) for x in got[1:]])
    print('live ', LIVE_2W)
