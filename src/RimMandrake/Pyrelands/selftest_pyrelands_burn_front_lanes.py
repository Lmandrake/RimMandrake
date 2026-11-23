#!/usr/bin/env python3
# selftest-timeout: 900
"""T_BURN_LANES: a burn burns as a front, not as one-cell lanes or a straight-edged band (bar burn_line_walks: "a natural grass
fire that moves").

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
  lone fires  (RIMMANDRAKE_WIDEN_PYRE_LONE_FIRE_INTO_A_FRONT, visit 7: single fires away from the front walked one-cell lanes)
              one lit cell and a lightning strike's blob (radius 1.9), bearings every 15 degrees, the same covers, 2 seeds each;
              read against the game's own lone fire burned to the same size (6 h: 180 to 730 cells, the carry's 24 h: 270 to
              970; a small fire holds more strands than a large one)
  extinction  a 24-cell front pinched to 1-8 lanes past a lake; one cell lit 0, 2 or 4 cells from a scar under a day old
  edges       the 24-cell front and a 60-cell one under a wind on a compass step: the longest run of rows a flank stands at
              one lane, the longest run of lanes the head stands at one row; held under half of what the carry alone leaves
              (its flanks stood 46 of 46 rows at full cover), read at cover 1.00 and 0.97 where that rule was straight
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
PRE_FIX = dict(heal_reach=0, carry_merge=False, flank=False)      # 2026-11-22's rule before the lanes fix
PRE_FLANK = dict(flank=False)                                      # 2026-11-23's rule before the lone-fire fix
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


def lone_cells(blob):
    c = SIZE // 2
    return [(c + dx, c + dz) for dx in range(-2, 3) for dz in range(-2, 3) if dx * dx + dz * dz <= (3.61 if blob else 0)]


def lone(blob, wind, cover, seed, rule, hours=HOURS):
    """A lone fire (one cell) or a lightning strike's blob in open grass. -> (strand share, cells burned)."""
    plant = field(cover, seed)
    kw = dict(wind=None, carried=False) if rule == "vanilla" else dict(dict(wind=wind, carried=True, **CARRY), **rule)
    s = M.Sim(plant, np.ones_like(plant, bool), seed, weather=False, clock=False, keepalive=False, sprout_per_day=0,
              loss_per_day=0, **kw)
    for x, z in lone_cells(blob):
        if s.chance(z, x) <= 0:
            s.plant[z, x] = 1
            s.hp[z, x] = M.HP[1]
        if blob:
            s.hp[z, x] -= M.STRIKE_DAMAGE      # the strike's flame burst hits the grass it lights
        s.start(z, x, 0.35)
    while s.tick < hours * HOUR:
        s.beat()
    burned = s.burn >= 0
    return strand_share(burned), int(burned.sum())


def lone_sweep(rule, quick):
    """-> {cover: worst strand share}, {cover: where}, {cover: least cells burned}, cases read"""
    worst, where, least, n = {}, {}, {}, 0
    for cover in COVERS:
        for blob in (False, True):
            for wind in range(0, 360, 45 if quick else 15):
                for sd in (0, 1):
                    share, cells = lone(blob, float(wind), cover, sd, rule)
                    n += 1
                    if share > worst.get(cover, -1.0):
                        worst[cover], where[cover] = share, "%s wind %d seed %d" % ("strike" if blob else "one cell", wind, sd)
                    least[cover] = min(least.get(cover, 10 ** 9), cells)
    return worst, where, least, n


def longest_flat(v):
    best = n = 0
    prev = None
    for x in v:
        n = n + 1 if x == prev else 1
        prev = x
        best = max(best, n)
    return best


def edges(width, wind, cover, seed, rule):
    """A front lit across a compass-step wind, burned 24 h. -> the longest straight run of its flanks (rows), of its head (lanes)."""
    plant = field(cover, seed)
    s = M.Sim(plant, np.ones_like(plant, bool), seed, weather=False, clock=False, keepalive=False, sprout_per_day=0,
              loss_per_day=0, **dict(dict(wind=wind, carried=True, **CARRY), **rule))
    r = math.radians(wind)
    s.light_line(int(round(SIZE / 2 - 50 * math.sin(r))), int(round(SIZE / 2 - 50 * math.cos(r))), width, 0.35, angle=wind + 90)
    while s.tick < HOURS * HOUR:
        s.beat()
    b = s.burn >= 0                                                # turned so the wind blows toward +column
    b = {0: b.T, 90: b, 180: b.T[:, ::-1], 270: b[:, ::-1]}[int(wind)]
    cols, lanes = np.nonzero(b.any(0))[0], np.nonzero(b.any(1))[0]
    # two rows in from the lit line and from the head, where the front is whole
    lo = [int(np.nonzero(b[:, c])[0].min()) for c in range(cols[0] + 2, cols[-1] - 2) if b[:, c].any()]
    hi = [int(np.nonzero(b[:, c])[0].max()) for c in range(cols[0] + 2, cols[-1] - 2) if b[:, c].any()]
    head = [int(np.nonzero(b[z])[0].max()) for z in lanes]
    return max(longest_flat(lo), longest_flat(hi)), longest_flat(head)


def edge_sweep(rule, quick):
    """-> {cover: mean of the longest straight flank run}, {cover: the same of the head}, cases read"""
    flank, head, n = {}, {}, 0
    for cover in (1.0, 0.97):
        got = [edges(w, wind, cover, sd, rule) for w in (24, 60) for wind in (0.0, 90.0, 180.0, 270.0)
               for sd in ((0,) if quick else (0, 1, 2))]
        n += len(got)
        flank[cover], head[cover] = float(np.mean([g[0] for g in got])), float(np.mean([g[1] for g in got]))
    return flank, head, n


def pinch(gap, seed, rule):
    """A 24-cell front meets a lake 20 cells long that leaves `gap` lanes of grass beside it. -> did fire enter
    the gap, and reach the far side? (a flank that wandered in before the lake never enters a narrow gap: that is not a fire put out)"""
    rng = np.random.default_rng(seed)
    p = (rng.random((100, 130)) < 0.97).astype(np.int8)
    p[50 - 12 + gap:80, 40:60] = 0
    s = M.Sim(p, np.ones_like(p, bool), seed, weather=False, clock=False, keepalive=False, sprout_per_day=0, loss_per_day=0,
              **dict(dict(wind=90.0, carried=True, **CARRY), **rule))
    s.light_line(20, 50, 24, 0.35, angle=180.0)
    while s.tick < 72 * HOUR and (s.size > 0).any():
        s.beat()
    b = s.burn >= 0
    return bool(b[:, 45:60].any()), bool(b[:, 120:].any())


def beside_scar(gap, seed, rule):
    """One cell lit `gap` cells from ground burned less than a day ago. -> did its fire run 60 cells?"""
    rng = np.random.default_rng(seed)
    p = (rng.random((100, 130)) < 0.97).astype(np.int8)
    p[50:80] = 0
    s = M.Sim(p, np.ones_like(p, bool), seed, weather=False, clock=False, keepalive=False, sprout_per_day=0, loss_per_day=0,
              **dict(dict(wind=90.0, carried=True, **CARRY), **rule))
    s.burn[50:80] = 0
    s.plant[49 - gap, 20] = 1
    s.hp[49 - gap, 20] = M.HP[1]
    s.start(49 - gap, 20, 0.35)
    while s.tick < 48 * HOUR and (s.size > 0).any():
        s.beat()
    return True, bool((s.burn[:50] >= 0)[:, 80:].any())


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

    # RIMMANDRAKE_WIDEN_PYRE_LONE_FIRE_INTO_A_FRONT: the same tie for the flank rule and the carry's age
    ties = dict(WindCarryTicks="carry_ticks", WindCarryExtraTicks="carry_extra", FlankWidth="flank_width", FlankLeanCap="flank_cap",
                FlankNarrow="flank_narrow", FlankRows="flank_rows", FlankLook="flank_look", FlankBeside="flank_beside",
                FlankFuel="flank_fuel", FlankPatch="flank_patch", PacePatch="pace_patch", FuelSpentHp="fuel_spent")
    off = ["%s %s != %s" % (k, const(KERNEL, k), M.DEFAULTS.get(v)) for k, v in ties.items() if const(KERNEL, k) != M.DEFAULTS.get(v)]
    row("the kernel's flank constants are the model's", not off, "; ".join(off) or "all equal", "== the model's", "%d constants" % len(ties))
    want = re.search(r"FlankPlanChecksum = (\d+)L;", open(FUZZ, encoding="utf-8").read())
    got = M.flank_plan_checksum() if hasattr(M, "flank_plan_checksum") else (None, 0, 0)
    row("the model's flank and carry age equal RM_BurnKernel's", bool(want) and got[0] == int(want.group(1)), str(got[0]),
        "== %s (the fuzz asserts its side)" % (want.group(1) if want else "no FlankPlanChecksum"),
        "2,000 LCG neighbourhoods, %d open, %d close" % got[1:])

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

    # ---- 5. a lone fire is a fire, not a lane; a front's edges are not ruled ----------------------------------------------
    van = {c: max(lone(False, 0.0, c, sd, "vanilla", hours=6)[0] for sd in range(6)) for c in COVERS}
    lone_lim = {c: van[c] + STRAND_MARGIN for c in COVERS}
    lim_txt = ", ".join("%.2f: %.2f" % (c, lone_lim[c]) for c in COVERS)
    flankless = PRE_FIX if old else PRE_FLANK
    w0, at0, _, n0 = lone_sweep(PRE_FLANK, True)
    row("RED CONTROL before the fix a lone fire is a lane", all(w0[c] > lone_lim[c] for c in COVERS),
        ", ".join("%.2f: %.2f" % (c, w0[c]) for c in COVERS), "> the limit at every cover (%s)" % lim_txt, "%d cases, flank off" % n0)
    lone_rule = flankless if old else {}
    w1, at1, least, n1 = lone_sweep(lone_rule, quick)
    row("a lone fire burns as a fire, not a lane (burn_line_walks)", all(w1[c] <= lone_lim[c] for c in COVERS),
        "; ".join("%.2f: %.2f (%s)" % (c, w1[c], at1[c]) for c in COVERS),
        "<= the game's own lone fire + %.2f (%s)" % (STRAND_MARGIN, lim_txt),
        "%d cases, least burned %s cells" % (n1, min(least.values())))
    w2, _, _, n2 = lone_sweep(dict(lone_rule, burn_stamps=False), True)
    row("the same with freshBurnBonusEnabled off", all(w2[c] <= lone_lim[c] for c in COVERS),
        "; ".join("%.2f: %.2f" % (c, w2[c]) for c in COVERS), "<= the same limits", "%d cases (quick range)" % n2)
    # the fix's fresh reader: the flank's close put out the last live lanes past a lake and beside a fresh scar; a strike's
    # damaged grass was gone before the slowest carry. Each is held to what the carry alone does on the same maps.
    nseed = 6 if quick else 20
    hold, txt = [], []
    for name, fn, gaps in (("past a lake", pinch, (1, 2, 3, 5, 8)), ("beside a scar", beside_scar, (0, 2, 4))):
        for g in gaps:
            got, base = [fn(g, sd, lone_rule) for sd in range(nseed)], [fn(g, sd, PRE_FLANK) for sd in range(nseed)]
            a, b0 = [x[1] for x in got if x[0]], [x[1] for x in base if x[0]]
            hold.append(len(a) >= nseed // 4 and sum(a) / len(a) >= sum(b0) / len(b0) - 0.05)
            txt.append("%s %d: %d of %d (%d of %d)" % (name, g, sum(a), len(a), sum(b0), len(b0)))
    row("the last lane of a burn is not put out by its flank", all(hold), "; ".join(txt),
        ">= the carry alone's share (in brackets) less 0.05", "%d runs a case; of those that entered" % nseed)
    least_strike = min(lone(True, w, 0.97, sd, lone_rule, hours=12)[1] for w in (0.0, 90.0, 240.0) for sd in range(nseed // 2))
    row("a strike's fire leaves its blob", least_strike > 3 * len(lone_cells(True)), "%d cells in 12 h" % least_strike,
        "> 3 x the %d cells lit" % len(lone_cells(True)), "%d strikes, grass at 18 of 28 hit points" % (3 * (nseed // 2)))
    f0, h0, _ = edge_sweep(PRE_FLANK, quick)
    f1, h1, ne = edge_sweep(lone_rule, quick)
    row("a front's flanks and head are not ruled straight", all(f1[c] < f0[c] / 2 and h1[c] < h0[c] / 2 for c in f1),
        "; ".join("%.2f: flank %.1f rows, head %.1f lanes" % (c, f1[c], h1[c]) for c in f1),
        "< half the carry alone's (%s)" % "; ".join("%.2f: %.1f, %.1f" % (c, f0[c], h0[c]) for c in f0),
        "%d fronts of 24 and 60, mean of each front's longest straight run" % ne)

    bad = rows.count(False)
    print("%s: %d of %d rows hold" % ("PASS" if not bad else "FAIL", len(rows) - bad, len(rows)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
