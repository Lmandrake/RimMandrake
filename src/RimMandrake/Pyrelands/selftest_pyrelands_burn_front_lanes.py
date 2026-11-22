#!/usr/bin/env python3
# selftest-timeout: 900
"""T_BURN_LANES: a burn line burns as a front, not as one-cell lanes (bar burn_line_walks: "a natural grass fire that moves").

Why it exists (RIMMANDRAKE_WIDEN_PYRE_FIRE_TRAILS_RUN_AS_RULER_STRAIGHT_LANES, Pyrelands in-game visit 5, 2026-11-22): the 24
hourly captures of burn_line showed many parallel, ruler-straight lanes one or two cells wide, a fire at the head of each and
unburned grass standing between them. Cause: the scar's arc lights every 3rd to 6th cell (RM_BurnKernel.ArcStride), each fire
carried one cell downwind and never aside, and the scar's wind lies on a compass step, so no lane ever leans. The fix is
RM_BurnKernel.CarryPlan (merge + one gap cell healed beside the carried cell); this check reads its model
(pyre_burn_sim.carry_plan, tied to the kernel by CarryPlanChecksum, which the C# fuzz asserts on its side).

The measure is the ticket's own proxy: the share of burned cells that are one-cell strands (both neighbours along x, or both
along z, unburned). A line of lanes reads 0.5 to 1.0; a front reads near the game's own even-spread fire on the same grass.

The range of situations (what the game can vary for this bar):
  lit shape   the scar's arc (the opening front: radius 35, 45 and 61 = 50 pushed out by YesterdayFireRagged, every
              ArcStride'th cell up to YesterdayFireArcFireCap, read from PyrelandsTuning.cs), its wind blowing inward from each
              of the 4 edges (RM_BurnKernel.WindFromScarEdge: 0/90/180/270, the on-compass case that walked ruler-straight);
              and the scheduled front (FireFrontWidthCells in one FrontLine across the wind) at every 15 degrees of bearing
  grass       cover 1.00 / 0.97 (a fresh map) / 0.80 / 0.70 (patchy regrowth); below that a line dies (T_BURN_ECOLOGY's
              "a fresh scar does not carry the line again")
  setting     freshBurnBonusEnabled on (the ash field stamps burned cells) and off (the heal reads live fires and
              MapComponent_BurnLine.CarriedAt only)
  seeds, time 2 seeds for arcs, 1 per bearing for lines; 24 game hours (the visit's 24 hourly captures)
Left out: weather (black rain puts fires out: T_BURN_ECOLOGY), regrowth during the day, rock and water blobs (the cover is
per-cell random; T_BURN_ECOLOGY's season runs blob maps), home areas and buildings (a lawful-cell matter, not the carry's),
two lines meeting, the in-game rendering (Stage 6: a judge shown the hourly captures, sc_burn_line_walks).

    python3 src/RimMandrake/Pyrelands/selftest_pyrelands_burn_front_lanes.py [--old] [--quick]
    --old runs the rule before the fix (no merge, no heal) where the shipped rule runs: its front row must go red.
"""
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pyre_burn_sim as M  # noqa: E402

KERNEL = os.path.join(HERE, "Source", "Kernel", "RM_BurnKernel.cs")
FUZZ = os.path.join(HERE, "Source", "SelfTest", "Fuzz", "PyrelandsFuzz.cs")
TUNING = os.path.join(HERE, "Source", "PyrelandsTuning.cs")
SIZE = 160
HOURS = 24
HOUR = 2500
PRE_FIX = dict(heal_reach=0, carry_merge=False)
# Our own rule, not a bar: a front may hold at most one burned cell in ten more as one-cell strands than the game's own
# even-spread fire leaves on the same grass (patchy grass leaves strands under any fire: vanilla's own share is 0.02 at full
# cover and 0.23 at 0.70, measured 2026-11-22). The defect read 0.48 to 1.00 on the arc at every cover.
STRAND_MARGIN = 0.10
rows = []


def row(name, ok, worst, limit, sampled):
    rows.append(ok)
    print("%-4s %-50s worst %-30s must %-40s | %s" % ("ok" if ok else "FAIL", name, worst, limit, sampled))


def const(path, name, kind="int"):
    m = re.search(r"const %s %s = ([\d.]+)f?;" % (kind, name), open(path, encoding="utf-8").read())
    return None if not m else (int(m.group(1)) if kind == "int" else float(m.group(1)))


def arc_cells(cx, cz, nx, nz, r, min_cos):
    """The scar's leading arc in bearing order: cells at radius r within acos(min_cos) of the inward normal."""
    seen = {}
    half = math.acos(min_cos)
    px, pz = -nz, nx
    for k in range(6001):
        a = -half + 2 * half * k / 6000.0
        x = int(round(cx + r * (nx * math.cos(a) + px * math.sin(a))))
        z = int(round(cz + r * (nz * math.cos(a) + pz * math.sin(a))))
        seen.setdefault((x, z), a)
    return sorted(seen, key=lambda c: seen[c])


def field(cover, seed):
    rng = np.random.default_rng(seed + 500)
    return np.where(rng.random((SIZE, SIZE)) < cover, np.where(rng.random((SIZE, SIZE)) < 0.79, 1, 2), 0).astype(np.int8)


def strand_share(burned):
    """The ticket's proxy: burned cells whose two x-neighbours, or two z-neighbours, are both unburned, over burned cells."""
    b = np.pad(burned, 1)
    c = b[1:-1, 1:-1]
    strand = c & ((~b[1:-1, :-2] & ~b[1:-1, 2:]) | (~b[:-2, 1:-1] & ~b[2:, 1:-1]))
    return strand.sum() / float(max(1, c.sum()))


def burn(shape, wind, cover, seed, rule, hours=HOURS):
    """One lit shape on a fresh field, burned `hours` with the sky clear. rule: dict of Sim options, or "vanilla" (even
    spread, the wind off). -> (strand share, widening in cells beyond the lit span across the wind, cells burned)."""
    plant = field(cover, seed)
    kw = dict(wind=None, carried=False) if rule == "vanilla" else dict(dict(wind=wind, carried=True, **CARRY), **rule)
    s = M.Sim(plant, np.ones_like(plant, bool), seed, weather=False, clock=False, keepalive=False, sprout_per_day=0,
              loss_per_day=0, **kw)
    r = math.radians(wind)
    wx, wz = math.sin(r), math.cos(r)
    if shape[0] == "arc":
        nx, nz = int(round(wx)), int(round(wz))
        cx, cz = SIZE // 2 - nx * (SIZE // 2 - 1), SIZE // 2 - nz * (SIZE // 2 - 1)
        # PyrelandsYesterdayFire.ArcCells keeps only rim cells that hold a plant and are lawful to light, then
        # LightScarArc lights every ArcStride'th of THOSE (a stride over bare cells too doubled the gaps on patchy grass)
        cells = [c for c in arc_cells(cx, cz, nx, nz, shape[1], ARC_MIN_COS)
                 if 0 <= c[0] < SIZE and 0 <= c[1] < SIZE and s.chance(c[1], c[0]) > 0]
        stride = max(ARC_STRIDE, -(-len(cells) // ARC_CAP))      # RM_BurnKernel.ArcStride
        lit = []
        for i in range(stride // 2, len(cells), stride):
            if len(lit) >= ARC_CAP:
                break
            x, z = cells[i]
            s.start(z, x, 0.35)
            lit.append((x, z))
    else:
        before = s.size > 0
        s.light_line(int(SIZE / 2 - 50 * wx), int(SIZE / 2 - 50 * wz), shape[1], 0.35, angle=wind + 90)
        zs, xs = np.nonzero((s.size > 0) & ~before)
        lit = list(zip(xs, zs))
    if not lit:
        return None
    while s.tick < hours * HOUR:
        s.beat()
    burned = s.burn >= 0
    across = lambda x, z: (np.asarray(x) - SIZE / 2.0) * wz - (np.asarray(z) - SIZE / 2.0) * wx
    a0 = across([p[0] for p in lit], [p[1] for p in lit])
    zs, xs = np.nonzero(burned)
    a = across(xs, zs)
    widen = max(float(a0.min() - a.min()), float(a.max() - a0.max()), 0.0)
    return strand_share(burned), widen, int(burned.sum())


def cases(quick):
    arc_seeds = (0,) if quick else (0, 1)
    out = []
    for cover in COVERS:
        for radius in (35, 45, 61):
            for wind in (0.0, 90.0, 180.0, 270.0):
                for sd in arc_seeds:
                    out.append((("arc", radius), wind, cover, sd))
        for wind in range(0, 360, 30 if quick else 15):
            out.append((("line", WIDTH), float(wind), cover, 0))
    return out


def sweep(rule, quick):
    """-> {cover: worst strand share}, worst widening, (worst case), cases read"""
    worst, widen, where, n = {}, 0.0, {}, 0
    for shape, wind, cover, sd in cases(quick):
        got = burn(shape, wind, cover, sd, rule)
        if got is None:
            continue
        n += 1
        share, wd, _ = got
        if share > worst.get(cover, -1.0):
            worst[cover], where[cover] = share, "%s r%s wind %.0f seed %d" % (shape[0], shape[1], wind, sd)
        widen = max(widen, wd)
    return worst, widen, where, n


def main(argv):
    quick, old = "--quick" in argv, "--old" in argv
    global CARRY, WIDTH, ARC_STRIDE, ARC_CAP, ARC_MIN_COS, COVERS
    CARRY = dict(carry_ticks=const(KERNEL, "WindCarryTicks"), carry_reach=const(KERNEL, "WindCarryReach"))
    WIDTH = const(TUNING, "FireFrontWidthCells")
    ARC_STRIDE, ARC_CAP = const(TUNING, "YesterdayFireArcStride"), const(TUNING, "YesterdayFireArcFireCap")
    ARC_MIN_COS = const(TUNING, "YesterdayFireArcMinCos", "float")
    COVERS = (1.0, 0.97, 0.80, 0.70)

    # ---- 1. the model's carry IS the kernel's ------------------------------------------------------------------------
    reach, recent = const(KERNEL, "HealReach"), const(KERNEL, "HealRecentTicks")
    row("the kernel's heal constants are the model's", reach is not None and recent is not None
        and reach == M.DEFAULTS.get("heal_reach") and recent == M.DEFAULTS.get("heal_recent"),
        "HealReach %s, HealRecentTicks %s" % (reach, recent),
        "== model %s, %s" % (M.DEFAULTS.get("heal_reach"), M.DEFAULTS.get("heal_recent")), "RM_BurnKernel.cs, pyre_burn_sim.DEFAULTS")
    want = re.search(r"CarryPlanChecksum = (\d+)L;", open(FUZZ, encoding="utf-8").read())
    got = M.carry_plan_checksum(heal_reach=reach) if hasattr(M, "carry_plan_checksum") and reach is not None else None
    row("the model's carry and heal equal RM_BurnKernel.CarryPlan", bool(want) and got == int(want.group(1)), str(got),
        "== %s (the fuzz asserts its side)" % (want.group(1) if want else "no CarryPlanChecksum"),
        "1,200 LCG neighbourhoods x bearings x rolls")

    shipped = PRE_FIX if old else {}
    label = "the rule before the fix (--old)" if old else "the shipped rule"

    # ---- 2. the reference fire and the instrument ---------------------------------------------------------------------
    vanilla = {}
    for cover in COVERS:
        vals = [burn(("arc", 45), 90.0, cover, sd, "vanilla", hours=6) for sd in (0, 1, 2, 3)]
        vanilla[cover] = max(v[0] for v in vals if v)
    limit = {c: vanilla[c] + STRAND_MARGIN for c in COVERS}
    lim_txt = ", ".join("%.2f: %.2f" % (c, limit[c]) for c in COVERS)
    print("     the game's own even-spread fire, strand share by cover: %s (arc r45, 6 h, 4 seeds)"
          % ", ".join("%.2f: %.2f" % (c, vanilla[c]) for c in COVERS))
    pre, pre_widen, pre_where, pre_n = sweep(PRE_FIX, True)
    row("RED CONTROL the rule before the fix burns lanes", all(pre[c] > limit[c] for c in COVERS),
        ", ".join("%.2f: %.2f" % (c, pre[c]) for c in COVERS), "> the limit at every cover (%s)" % lim_txt,
        "%d cases (quick range), no merge, no heal" % pre_n)

    # ---- 3. the bar: a front, not lanes, over the whole range ----------------------------------------------------------
    worst, widen, where, n = sweep(shipped, quick)
    bad = [c for c in COVERS if worst.get(c, 1.0) > limit[c]]
    row("the burn reads as a front, not lanes (%s)" % ("--old" if old else "burn_line_walks"), not bad,
        "; ".join("%.2f: %.2f (%s)" % (c, worst.get(c, -1), where.get(c, "-")) for c in COVERS),
        "<= vanilla + %.2f per cover (%s)" % (STRAND_MARGIN, lim_txt), "%d cases, %s" % (n, label))
    s_off, w_off, where_off, n_off = sweep(dict(shipped, burn_stamps=False), True)
    bad_off = [c for c in COVERS if s_off.get(c, 1.0) > limit[c]]
    row("the same with freshBurnBonusEnabled off (no ash stamps)", not bad_off,
        "; ".join("%.2f: %.2f" % (c, s_off.get(c, -1)) for c in COVERS), "<= the same limits", "%d cases (quick range)" % n_off)

    # ---- 4. the heal never widens a line --------------------------------------------------------------------------------
    full_pre_widen = sweep(PRE_FIX, quick)[1] if not quick else pre_widen
    row("the burn is no wider than under the carry alone", widen <= full_pre_widen,
        "%.1f cells beyond the lit span" % widen, "<= %.1f (the rule before the fix, same cases)" % full_pre_widen,
        "%d cases" % n)
    flood = sweep(dict(shipped, carry_splits=2), True)[1]
    row("PLANTED FAULT a carry that lights two probes widens", flood > full_pre_widen,
        "%.1f cells beyond the lit span" % flood, "> %.1f (the row above goes red)" % full_pre_widen, "carry_splits=2, quick range")

    bad = rows.count(False)
    print("%s: %d of %d rows hold" % ("PASS" if not bad else "FAIL", len(rows) - bad, len(rows)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
