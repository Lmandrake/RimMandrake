#!/usr/bin/env python3
# selftest-timeout: 900
"""T_FIRE_PACE_MODEL_OFFLINE: the fire catches and runs (bar fire_catches_and_runs, vision.md line 11; his walk of 0.1.0,
2026-11-24: "The fire barely catches, to be honest. I had expected faster spread." and "next version puts more aggressive
fire"). A spark in standing grass takes; on the day it is lit it is a front the player must answer; the head walks downwind
faster than 0.1.0's, and it is still the walking line of line 3, never a flood.

The instrument is the whole-map model pyre_burn_sim.py, tied to RM_BurnKernel by the fuzz's CarryPlanChecksum and
FlankPlanChecksum (FlankPlanChecksum hashes RM_BurnKernel.CarryAge at the slider's low end, its default and its high end, so the
pace arithmetic is one on both sides). One cell is lit at fire size 0.1 in standing ember grass under a clear sky, on the upwind
side of a 250 x 250 map (pyre_burn_sim.synthetic_map's size, the walk site's), so the grass runs on to the map edge downwind.

The range of situations (what the game can vary for this bar):
  pace      RM_PyrelandsSettings.firePacePercent: 0.1.0's pace (the slider's low end, RM_BurnKernel.FirePacePercentMin), the
            shipped default (FirePacePercentDefault), the high end (FirePacePercentMax); 0.1.0's own constants are written below
  grass     cover 1.00 / 0.97 (a fresh map) / 0.80 / 0.70 (patchy regrowth), the 0.79 ember / quickgrass mix; open ground, and
            the site's rock and water blobs (synthetic_map blobs=14, about 17% of the map) for the share row
  wind      every 15 degrees of bearing (on a compass step, diagonal, between); seeds 0..2 at full and fresh cover, 0 when patchy
  time      hourly through the day it is lit, then each day end of four days, the sky clear
Left out: weather (black rain puts fires out; its call rate under the faster pace is T_BURN_ECOLOGY's season rows, which run at
the shipped pace), the wind carry switched off (vanilla's even spread: the slider is not read), whether a live 0.1 fire gutters
(vanilla's roll: Stage 6 sc_fire_catches_and_runs), the fire clock's and the scar's lit shapes (T_BURN_LANES at the shipped pace),
home areas and buildings, two lines meeting.

Rows (each prints its worst value, its limit and how many cases it read):
  ties       the model's pace is the kernel's: fire_pace / fire_pace_min / fire_pace_max == FirePacePercentDefault / Min / Max, the
             low end is 0.1.0's pace (the paced carry at FirePacePercentMin is 0.1.0's 1,200 + 0..400 ticks)
  catches    the burn the spark started still burns at hour 1 and at the day end, on every case
  front      it grows into a front at least FlankWidth cells wide (FlankPlan's own measure: live fire across the snapped
             perpendicular, gaps up to HealReach passed) within FRONT_HOURS, on every case
  pace       the day-one head travel downwind at the shipped pace beats 0.1.0's on the same cases by 0.1.0's whole spread: the
             slowest shipped head is longer than the fastest 0.1.0 head
  share      at each day end of four days the burned share of open ground is at or under SHARE_MAX, at the default and the high end
  line       at each day end the burn is still a line: its one-cell strand share is at or under the game's own even-spread fire on
             the same map plus T_BURN_LANES's STRAND_MARGIN (the lanes check's own measure, imported), on open ground: a burn that
             threads rock and water reads strands under any rule (0.1.0's own constants read 0.264 against the 0.174 limit at
             0.97 cover, measured 2026-11-26), so the blob maps read the share row only, as T_BURN_LANES leaves blobs out

    python3 src/RimMandrake/Pyrelands/selftest_pyrelands_fire_pace.py [--old] [--quick]
    --old runs 0.1.0's constants where the shipped pace runs: the pace row must go red.
"""
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pyre_burn_sim as M  # noqa: E402
import selftest_pyrelands_burn_front_lanes as L  # noqa: E402  (strand_share and STRAND_MARGIN: the T_BURN_LANES reads)

KERNEL = os.path.join(HERE, "Source", "Kernel", "RM_BurnKernel.cs")
SIZE = 250            # pyre_burn_sim.synthetic_map's default, the walk site's 250 x 250
HOUR, DAY = 2500, 60000
DAYS = 4              # the decider's "every day end of four days"
FRONT_HOURS = 24      # bar fire_catches_and_runs: "on the day it is lit it is a front"
SHARE_MAX = 0.5       # the decider's "the burned share of open ground stays at or under half" (bar: "never a flood")
LIT_SIZE = 0.1        # the decider's spark: one cell lit at fire size 0.1 (FireUtility.TryStartFireIn's own size)
# 0.1.0's constants (RM_BurnKernel.cs at tag mod/Pyrelands/v0.1.0: WindCarryTicks 1200, WindCarryExtraTicks 400, WindCarryReach 2;
# no pace: every fire carried at 1,200 + 0..400 ticks)
OLD = dict(carry_ticks=1200, carry_extra=400, carry_reach=2, fire_pace=100)
rows = []


def row(name, ok, worst, limit, sampled):
    rows.append(ok)
    print("%-4s %-52s worst %-34s must %-44s | %s" % ("ok" if ok else "FAIL", name, worst, limit, sampled), flush=True)


def kconst(name):
    m = re.search(r"const int %s = (\d+);" % name, open(KERNEL, encoding="utf-8").read())
    return int(m.group(1)) if m else None


def origin(plant, wind):
    """The spark's cell: ember grass nearest the point 0.4 of the map upwind of its centre."""
    r = math.radians(wind)
    wx, wz = math.sin(r), math.cos(r)
    cx, cz = int(SIZE / 2 - 0.4 * SIZE * wx), int(SIZE / 2 - 0.4 * SIZE * wz)
    for d in range(40):
        c = [(cx + dx, cz + dz) for dz in range(-d, d + 1) for dx in range(-d, d + 1)
             if 0 <= cx + dx < SIZE and 0 <= cz + dz < SIZE and plant[cz + dz, cx + dx] == 1]
        if c:
            return c[0]
    return None


def front_width(size, wind, heal_reach):
    """FlankPlan's measure of the burn's width: live fire projected on the perpendicular of the wind's snapped compass step
    (a diagonal step counts one cell per two units of x + z), the longest run with gaps up to heal_reach passed."""
    step = int(math.floor((wind % 360.0) / 45.0 + 0.5)) % 8
    px, pz = M.DIRS8[(step + 2) % 8]
    zs, xs = np.nonzero(size > 0)
    if not len(xs):
        return 0
    a = np.unique((xs * px + zs * pz) // (2 if px and pz else 1))
    best = run = 1
    for i in range(1, len(a)):
        run = run + (a[i] - a[i - 1]) if a[i] - a[i - 1] <= heal_reach + 1 else 1
        best = max(best, run)
    return int(best)


def spark(rule, wind, cover, seed, days=DAYS, blobs=0, flank_width=10, heal_reach=5):
    """One spark under a clear sky. -> dict: alive at hour 1 and at the day end, first hour the front is flank_width wide,
    day-one head travel downwind, and per day end the burned share of open ground and the strand share; None if no ember grass."""
    plant, plantable = M.synthetic_map(SIZE, seed, cover=cover, blobs=blobs)
    o = origin(plant, wind)
    if o is None:
        return None
    x0, z0 = o
    s = M.Sim(plant, plantable, seed, weather=False, clock=False, keepalive=False, wind=wind, carried=True, **rule)
    r = math.radians(wind)
    wx, wz = math.sin(r), math.cos(r)
    s.start(z0, x0, LIT_SIZE)
    out = dict(alive1=False, alive24=False, front_h=None, head=0.0, share=[], strand=[])
    while s.tick < days * DAY:
        s.beat()
        if s.tick % HOUR >= M.BEAT:
            continue
        h = s.tick // HOUR
        live = s.size > 0
        if h == 1:
            out["alive1"] = bool(live.any())
        if h == FRONT_HOURS:
            out["alive24"] = bool(live.any())
        if out["front_h"] is None and h <= FRONT_HOURS and front_width(s.size, wind, heal_reach) >= flank_width:
            out["front_h"] = int(h)
        if s.tick % DAY < M.BEAT:
            burned = s.burn >= 0
            if h == 24:
                zb, xb = np.nonzero(burned)
                out["head"] = float(((xb - x0) * wx + (zb - z0) * wz).max())
            out["share"].append(float(burned[plantable].mean()))
            out["strand"].append(float(L.strand_share(burned)))
        if days == 1 and h >= 24:
            break
    return out


def vanilla_strands(cover, seeds, blobs=0):
    """The game's own even-spread fire (the wind off) from the same spark on the same map, 6 h (the lanes check's reference age:
    a small fire holds more strands than a large one): its worst strand share over the seeds."""
    worst = 0.0
    for sd in seeds:
        plant, plantable = M.synthetic_map(SIZE, sd, cover=cover, blobs=blobs)
        o = origin(plant, 0.0)
        s = M.Sim(plant, plantable, sd, weather=False, clock=False, keepalive=False, wind=None, carried=False)
        s.start(o[1], o[0], LIT_SIZE)
        while s.tick < 6 * HOUR:
            s.beat()
        worst = max(worst, float(L.strand_share(s.burn >= 0)))
    return worst


def main(argv):
    quick, old = "--quick" in argv, "--old" in argv
    pace = {k: kconst("FirePacePercent" + k) for k in ("Default", "Min", "Max")}
    flank_width, heal_reach = kconst("FlankWidth"), kconst("HealReach")
    base = dict(carry_ticks=kconst("WindCarryTicks"), carry_extra=kconst("WindCarryExtraTicks"), carry_reach=kconst("WindCarryReach"))

    # ---- 1. the model's pace is the kernel's -------------------------------------------------------------------------------
    want = dict(Default=M.DEFAULTS.get("fire_pace"), Min=M.DEFAULTS.get("fire_pace_min"), Max=M.DEFAULTS.get("fire_pace_max"))
    off = ["FirePacePercent%s %s != model %s" % (k, pace[k], want[k]) for k in pace if pace[k] is None or pace[k] != want[k]]
    row("the kernel's pace is the model's", not off, "; ".join(off) or "all equal", "== pyre_burn_sim.DEFAULTS", "3 constants")
    paced = getattr(M, "paced", None)
    low = (paced(base["carry_ticks"], pace["Min"]), paced(base["carry_extra"], pace["Min"])) if paced and pace["Min"] else None
    row("the slider's low end is 0.1.0's pace", low == (OLD["carry_ticks"], OLD["carry_extra"]) and base["carry_reach"] == OLD["carry_reach"],
        "carry %s + 0..%s ticks, reach %s" % (tuple(low or ("-", "-")) + (base["carry_reach"],)),
        "0.1.0's %d + 0..%d, reach %d" % (OLD["carry_ticks"], OLD["carry_extra"], OLD["carry_reach"]), "RM_BurnKernel.cs at FirePacePercentMin")

    shipped = dict(OLD) if old else dict(base, fire_pace=pace["Default"] or 100)
    label = "0.1.0's constants (--old)" if old else "the shipped pace %s%%" % shipped["fire_pace"]
    high = dict(base, fire_pace=pace["Max"] or 100)
    seeds_full = (0,) if quick else (0, 1, 2)
    bearings = range(0, 360, 45 if quick else 15)
    cases = [(c, w, sd) for c in (1.0, 0.97) for w in bearings for sd in seeds_full] + \
            [(c, w, 0) for c in (0.80, 0.70) for w in bearings]

    # ---- 2. a spark takes and is a front on the day it is lit ---------------------------------------------------------------
    runs = {k: spark(shipped, float(k[1]), k[0], k[2], flank_width=flank_width, heal_reach=heal_reach) for k in cases}
    dead1 = [k for k, r in runs.items() if not r["alive1"]]
    dead24 = [k for k, r in runs.items() if not r["alive24"]]
    row("the spark's burn still burns at hour 1 and hour 24", not dead1 and not dead24,
        "%d out at hour 1, %d at hour 24 %s" % (len(dead1), len(dead24), (dead1 + dead24)[:3]), "0 of %d" % len(runs),
        "%d cases, %s" % (len(runs), label))
    fh = {k: (r["front_h"] if r["front_h"] is not None else 999) for k, r in runs.items()}
    wk = max(fh, key=fh.get)
    hours = sorted(fh.values())
    row("it is a front FlankWidth wide on the day it is lit", fh[wk] <= FRONT_HOURS,
        "%s h at cover %.2f bearing %d seed %d (p50 %s h)" % ((fh[wk] if fh[wk] < 999 else "never",) + wk + (hours[len(hours) // 2],)),
        "<= %d h, width >= FlankWidth %s" % (FRONT_HOURS, flank_width), "%d cases, %s" % (len(runs), label))

    # ---- 3. the head walks downwind faster than 0.1.0's ---------------------------------------------------------------------
    oldruns = {k: spark(OLD, float(k[1]), k[0], k[2], days=1, flank_width=flank_width, heal_reach=heal_reach) for k in cases}
    new_head = {k: r["head"] for k, r in runs.items()}
    old_head = {k: r["head"] for k, r in oldruns.items()}
    kn, ko = min(new_head, key=new_head.get), max(old_head, key=old_head.get)
    row("the day-one head beats 0.1.0's by 0.1.0's whole spread", new_head[kn] > old_head[ko],
        "slowest %.0f cells (cover %.2f, %d deg, seed %d)" % ((new_head[kn],) + kn),
        "> 0.1.0's fastest %.0f (cover %.2f, %d deg, seed %d)" % ((old_head[ko],) + ko),
        "%d cases; means %.0f vs 0.1.0's %.0f; %s" % (len(cases), np.mean(list(new_head.values())), np.mean(list(old_head.values())), label))

    # ---- 4. never a flood: the share and the line, at the default and the high end, open ground and the site's blobs ----------
    ref = {c: vanilla_strands(c, (0, 1) if quick else (0, 1, 2)) for c in (1.0, 0.97, 0.80, 0.70)}
    hcases = [(c, w, 0) for c in (1.0, 0.97, 0.80, 0.70) for w in range(0, 360, 90 if quick else 45)]
    hruns = {k: spark(high, float(k[1]), k[0], k[2], flank_width=flank_width, heal_reach=heal_reach) for k in hcases}
    bcases = [(0.97, w, sd) for w in range(0, 360, 90 if quick else 30) for sd in ((0,) if quick else (0, 1))]
    bruns = {k: spark(shipped, float(k[1]), k[0], k[2], blobs=14, flank_width=flank_width, heal_reach=heal_reach) for k in bcases}
    bruns = {k: r for k, r in bruns.items() if r is not None}
    for name, rr, rule in (("the default", runs, label), ("the high end", hruns, "pace %s%%" % high["fire_pace"]),
                           ("the site's blobs", bruns, label)):
        share = {(k, d): v for k, r in rr.items() for d, v in enumerate(r["share"])}
        ks = max(share, key=share.get)
        row("burned share <= half at each day end (%s)" % name, share[ks] <= SHARE_MAX,
            "%.3f (cover %.2f, %d deg, seed %d, day %d)" % ((share[ks],) + ks[0] + (ks[1] + 1,)), "<= %.2f" % SHARE_MAX,
            "%d cases x %d day ends, %s" % (len(rr), DAYS, rule))
        if rr is bruns:
            continue     # a burn threading rock and water reads strands under any rule (0.1.0's own: 0.264 at 0.97, measured)
        lim = lambda k: ref[k[0]] + L.STRAND_MARGIN
        over = {(k, d): v - lim(k) for k, r in rr.items() for d, v in enumerate(r["strand"])}
        kl = max(over, key=over.get)
        row("still a line at each day end (%s)" % name, over[kl] <= 0,
            "%.3f (cover %.2f, %d deg, seed %d, day %d)" % ((over[kl] + lim(kl[0]),) + kl[0] + (kl[1] + 1,)),
            "<= vanilla + %.2f = %.3f there" % (L.STRAND_MARGIN, lim(kl[0])), "%d cases x %d day ends" % (len(rr), DAYS))

    bad = rows.count(False)
    print("%s: %d of %d rows hold" % ("PASS" if not bad else "FAIL", len(rows) - bad, len(rows)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
