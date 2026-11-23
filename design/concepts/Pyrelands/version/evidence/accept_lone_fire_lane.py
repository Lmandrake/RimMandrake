#!/usr/bin/env python3
"""Acceptance test of RIMMANDRAKE_WIDEN_PYRE_LONE_FIRE_INTO_A_FRONT (Pyrelands in-game visit 7, 2026-11-23).

A lone fire (a fire-hawk's dropped ember, a lightning strike, a camp fire's stray spark) lit in open ember grass under the
burn line's wind carry must burn like the game's own even-spread fire on the same grass, not as a one-cell-wide strand. The
case T_BURN_LANES (selftest_pyrelands_burn_front_lanes.py) leaves out: one lit cell. Same model (pyre_burn_sim, the shipped
kernel's carry), same proxy (strand_share) and the same margin (vanilla's own share + 0.10) as T_BURN_LANES; winds 0, 45, 90
and 135 degrees, covers 1.00 and 0.80, 24 game hours, calm sky. Live measure that filed it: the burn_line_walking save's
trails read one cell every ~1,300 ticks along x (evidence/script_line_speed.log).
PASS (exit 0) when every case holds; FAIL (exit 1) otherwise; UNMEASURED (exit 2) when the model cannot be loaded."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, *[".."] * 5))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Pyrelands"))
try:
    import numpy as np
    import pyre_burn_sim as M
    import selftest_pyrelands_burn_front_lanes as L
except Exception as e:   # noqa: BLE001 - a model that does not load is not a verdict
    print("UNMEASURED: %r" % (e,)); sys.exit(2)
CARRY = dict(carry_ticks=L.const(L.KERNEL, "WindCarryTicks"), carry_reach=L.const(L.KERNEL, "WindCarryReach"))
MARGIN = L.STRAND_MARGIN


def lone(rule, wind, cover, seed=0, hours=24):
    plant = L.field(cover, seed)
    kw = dict(wind=None, carried=False) if rule == "vanilla" else dict(wind=wind, carried=True, **CARRY)
    s = M.Sim(plant, np.ones_like(plant, bool), seed, weather=False, clock=False, keepalive=False, sprout_per_day=0,
              loss_per_day=0, **kw)
    c = L.SIZE // 2
    if s.chance(c, c) <= 0:
        plant[c, c] = 1
    s.start(c, c, 0.35)
    while s.tick < hours * L.HOUR:
        s.beat()
    burned = s.burn >= 0
    return L.strand_share(burned), int(burned.sum())


bad = 0
for cover in (1.0, 0.8):
    for wind in (0.0, 45.0, 90.0, 135.0):
        vs, vn = lone("vanilla", None, cover)
        cs, cn = lone("carried", wind, cover)
        ok = cs <= vs + MARGIN
        bad += not ok
        print("%-4s cover %.2f wind %5.1f carried: strand share %.3f, %d cells burned | vanilla %.3f, %d cells" % (
            "ok" if ok else "FAIL", cover, wind, cs, cn, vs, vn))
print("%s: %d of 8 cases hold" % ("PASS" if not bad else "FAIL", 8 - bad))
sys.exit(0 if not bad else 1)
