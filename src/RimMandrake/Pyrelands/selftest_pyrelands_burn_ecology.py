#!/usr/bin/env python3
# selftest-timeout: 900
"""T_BURN_ECOLOGY: the Pyrelands burn as ONE whole-map system (fire, grass, weather), over a season, with the sky free.

Why it exists (RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE, 2026-11-16): every in-game scene stages one pad on
a site built with the fire mechanics off and the sky locked clear, so nothing ever watched the system run. In the visit-1
walk saves one opening front burned 78% of the map in 4 days. This check runs the whole-map model (pyre_burn_sim.py: vanilla
Fire, the weather chooser, the fire clock, the keep-alive, black rain, regrowth) and reads the EXPERIENCES the bars state:

  burn_line_walks              a line walks the map; it is never a flood; it is never out for long
  grass_carpets_and_regreens   the carpet stays; a fresh scar does not carry fire again at once
  three_skies                  black rain puts fires out, and the everyday line does not call it down

Rows print: what was sampled, the worst value, and the line it must hold. No row pins a tuning number of the mod: each
limit is either a comparison against a control run on the same map, or is derived from a bar's own words (named beside it).

It also proves the instrument: the model against the real game (the walk saves' burn grid), the flood shown red on vanilla's
even spread and on a planted fault (a fire that lights two cells), and the model's wind step equal to the game kernel's
(RM_BurnKernel.WindProbes), cell for cell, through a table both sides compute.

    python3 src/RimMandrake/Pyrelands/selftest_pyrelands_burn_ecology.py [--quick]
"""
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pyre_burn_sim as M  # noqa: E402

DAY = M.DAY
KERNEL = os.path.join(HERE, "Source", "Kernel", "RM_BurnKernel.cs")
FUZZ = os.path.join(HERE, "Source", "SelfTest", "Fuzz", "PyrelandsFuzz.cs")
FIXTURE = os.path.join(HERE, "testdata", "pyre_walk_visit1.npz")
rows = []


def row(name, ok, worst, limit, sampled):
    rows.append(ok)
    print("%-4s %-46s worst %-22s must %-34s | %s" % ("ok" if ok else "FAIL", name, worst, limit, sampled))


def kernel_const(name):
    m = re.search(r"const int %s = (\d+);" % name, open(KERNEL, encoding="utf-8").read())
    if not m:
        raise SystemExit("FAIL: %s not found in %s" % (name, KERNEL))
    return int(m.group(1))


def probe_checksum(reach):
    h = 0
    for b10 in range(0, 3600, 25):
        for r8 in range(8):
            for r2 in (0.25, 0.75):
                for dx, dz in M.wind_probes(b10 / 10.0, r8 / 8.0, r2, reach):
                    h = (h * 31 + (dx + 5) * 11 + (dz + 5)) % 1000000007
    return h


def season(seed, size, days, **kw):
    """A fresh map with a colony yard in the middle and yesterday's fire on the upwind edge, then `days` of ordinary play."""
    plant, plantable = M.synthetic_map(size, seed)
    c = size // 2
    home = (c - 20, c - 20, c + 20, c + 20)
    plant[home[1]:home[3], home[0]:home[2]] = 0
    s = M.Sim(plant, plantable, seed, home=home, **kw)
    wind = kw.get("wind") if kw.get("wind") is not None else 90.0
    r = math.radians(wind)
    ox, oz = c - (c - 45) * math.sin(r), c - (c - 45) * math.cos(r)      # the scar's leading arc, 45 cells in from upwind
    for i in range(32):                                                   # YesterdayFireArcFireCap fires along it
        a = math.radians(-60 + 120 * i / 31) + r
        x, z = int(ox - 45 * math.sin(r) + 45 * math.sin(a)), int(oz - 45 * math.cos(r) + 45 * math.cos(a))
        if s.lawful(z, x):
            s.start(z, x, 0.35)
    s.run(days)
    return s


def worst_day_burn(s):
    """The largest share of the open ground that caught fire in one game day."""
    return max(s.lit_by_day.values() or [0]) / float(s.plantable.sum())


def line_run(cover, seed, wind, carried=True, splits=1, size=250):
    rng = np.random.default_rng(seed)
    plant = np.where(rng.random((size, size)) < cover, np.where(rng.random((size, size)) < 0.79, 1, 2), 0).astype(np.int8)
    s = M.Sim(plant, np.ones_like(plant, bool), seed, weather=False, clock=False, keepalive=False, sprout_per_day=0,
              loss_per_day=0, wind=wind, carried=carried, carry_splits=splits, **CARRY)
    r = math.radians(wind)
    s.light_line(int(size / 2 - 100 * math.sin(r)), int(size / 2 - 100 * math.cos(r)), WIDTH, 0.35)
    lit = int((s.size > 0).sum())
    peak = lit
    while s.tick < 8 * DAY and (s.size > 0).any():
        s.beat()
        peak = max(peak, int((s.size > 0).sum()))
    zs, xs = np.nonzero(s.burn >= 0)
    reach = float(((xs - size / 2) * math.sin(r) + (zs - size / 2) * math.cos(r)).max() + 100) if len(xs) else 0.0
    return lit, reach, peak, s


def main(argv):
    quick = "--quick" in argv
    global CARRY
    CARRY = dict(carry_ticks=kernel_const("WindCarryTicks"), carry_reach=kernel_const("WindCarryReach"))
    tun = open(os.path.join(HERE, "Source", "PyrelandsTuning.cs"), encoding="utf-8").read()
    global WIDTH
    WIDTH = int(re.search(r"const int FireFrontWidthCells = (\d+);", tun).group(1))
    M.DEFAULTS["front_width"] = WIDTH          # the fire clock and the keep-alive light the shipped width

    # ---- 1. the model's wind step IS the kernel's -------------------------------------------------------------------
    want = re.search(r"WindProbeChecksum = (\d+)L;", open(FUZZ, encoding="utf-8").read())
    got = probe_checksum(2)
    row("wind step equals RM_BurnKernel.WindProbes", bool(want) and int(want.group(1)) == got, str(got),
        "== %s (the fuzz asserts its side)" % (want.group(1) if want else "?"), "2,304 bearing x roll cases, 6 probes each")

    # ---- 2. the model against the real game: the visit-1 walk saves ---------------------------------------------------
    F = np.load(FIXTURE)
    plant, plantable, mid = F["plant"], F["plantable"], F["mid_burn"]
    n = float(plantable.sum())

    def speed(b):
        bb = np.where(b >= 0, b.astype(float), np.nan)
        gy, gx = np.gradient(bb)
        g = np.sqrt(gx ** 2 + gy ** 2)
        sp = DAY / g[np.isfinite(g) & (g > 0)]
        return float(np.median(sp))

    game_cum = np.cumsum(np.bincount((mid[mid >= 0] // DAY).astype(int), minlength=8)[:7]) / n
    s = M.Sim(plant, plantable, 0, weather=False)
    for x, z in F["fires"]:
        s.start(z, x, 0.35)
    s.run(7.025)
    sim_cum = np.cumsum(np.bincount((s.burn[s.burn >= 0] // DAY).astype(int), minlength=8)[:7]) / n
    ratio = speed(s.burn) / speed(mid)
    gap = float(np.abs(sim_cum - game_cum).max())
    row("model front speed against the game's", 0.8 <= ratio <= 1.25, "ratio %.2f" % ratio, "within 0.80 .. 1.25",
        "the real walk's burn-stamp grid, day 7 (game 43 cells a day)")
    row("model burned share by day against the game's", gap <= 0.20, "gap %.2f" % gap, "<= 0.20 on every day 1..7",
        "cumulative burned share, same map, same 20 opening fires")
    flood_game = float(game_cum[3])
    flood_sim = float(sim_cum[3])
    # Bar grass_carpets_and_regreens: "largely green again within about a week". A fire that takes more than a seventh of
    # the open ground in a day outruns that regrowth: that is what "a flood" means here.
    FLOOD = 1.0 / 7.0
    row("RED CONTROL the game's even spread is a flood", flood_game > 0.5 and flood_sim > 0.5,
        "game %.2f model %.2f" % (flood_game, flood_sim), "> 0.50 of the map in 4 days (both)", "visit-1 walk, sky locked clear")

    # ---- 3. a line stays a line: every cover, bearing and seed --------------------------------------------------------
    seeds = (0, 1) if quick else (0, 1, 2)
    worst_reach, worst_peak, worst_case = 1e9, 0.0, ""
    for cover in (0.70, 0.80, 0.97):
        for wind in (0.0, 30.0, 90.0, 200.0, 315.0):
            for sd in seeds:
                lit, reach, peak, s = line_run(cover, sd, wind)
                if reach < worst_reach:
                    worst_reach, worst_case = reach, "cover %.2f wind %.0f seed %d" % (cover, wind, sd)
                worst_peak = max(worst_peak, peak / max(1, lit))
                assert s.carry_lit <= s.carries
    row("a lit line crosses the map (burn_line_walks)", worst_reach >= 200, "reach %.0f cells (%s)" % (worst_reach, worst_case),
        ">= 200 of the 200+ to the far edge", "%d-cell line, cover 0.70/0.80/0.97 x 5 bearings x %d seeds" % (WIDTH, len(seeds)))
    # each fire burns for about two carry intervals, so a line holds about two fires a lane, never a growing number
    row("a line never widens (no fire makes two)", worst_peak <= 3.0, "peak fires %.1f x cells lit" % worst_peak,
        "<= 3 x the cells lit", "the same 45 line runs")
    died = max(line_run(0.30, sd, 90.0)[1] for sd in seeds)
    row("a fresh scar does not carry the line again", died < 100, "reach %.0f cells" % died, "< 100 (it dies in thin regrowth)",
        "%d-cell line into 30%% cover x %d seeds" % (WIDTH, len(seeds)))
    lit, reach, peak, s2 = line_run(0.97, 0, 90.0, splits=2)
    row("PLANTED FAULT a fire that lights two cells is caught", peak / max(1, lit) > 3.0, "peak fires %.1f x cells lit" % (peak / max(1, lit)),
        "> 3 x (the row above goes red)", "the same line with carry_splits=2")

    # ---- 4. a season with the sky free ---------------------------------------------------------------------------------
    days = 20 if quick else 40
    cases = [(250, 90.0, 0), (250, 30.0, 1)] if quick else [(200, 90.0, 0), (250, 90.0, 1), (250, 30.0, 2), (325, 200.0, 3)]
    w_day, w_cost, w_gap, w_rain, w_fire = 0.0, 0.0, 0.0, 0, 0
    v_day, v_rain, cost_note = 1.0, 10 ** 9, ""
    for size, wind, sd in cases:
        base = season(sd, size, days, clock=False, keepalive=False, weather=False, wind=wind, carried=True, **CARRY)
        base_min = base.summary()["cover_min"]   # the same map with no fire lit after the opening: what grazing and die-off leave
        on = season(sd, size, days, wind=wind, carried=True, **CARRY)
        off = season(sd, size, days)       # vanilla's even spread: the control that must fail
        so, sf = on.summary(), off.summary()
        w_day = max(w_day, worst_day_burn(on)); v_day = min(v_day, worst_day_burn(off))
        cost_on, cost_off = base_min - so["cover_min"], base_min - sf["cover_min"]
        if cost_on / max(1e-9, cost_off) >= w_cost:
            w_cost, cost_note = cost_on / max(1e-9, cost_off), "line %.2f, flood %.2f of cover lost" % (cost_on, cost_off)
        w_gap = max(w_gap, so["longest_fireless_days"])
        w_rain = max(w_rain, so["black_rains"]); v_rain = min(v_rain, sf["black_rains"])
        w_fire = max(w_fire, int(so["max_fires"]))
        assert on.carry_lit <= on.carries
    what = "%d maps (sizes, bearings, seeds: %s), %d days, weather free" % (len(cases), cases, days)
    row("never a flood (burn_line_walks)", w_day < FLOOD, "%.3f of the open ground in one day" % w_day,
        "< 1/7 (a week's regrowth)", what)
    row("RED CONTROL even spread floods the same maps", v_day > FLOOD, "%.3f in one day at the least" % v_day, "> 1/7", what)
    # No number of the mod's: the line is held against the flood on the same maps. The same row run with the wind off reads
    # 1.00 by construction, so it cannot pass a flood.
    row("the carpet stays (grass_carpets_and_regreens)", w_cost < 0.5, "%.2f of the flood's cost (%s)" % (w_cost, cost_note),
        "under half what even spread costs the carpet", what)
    # Bar burn_line_walks, red: "by day three the map holds no fire".
    row("never out for long (burn_line_walks)", w_gap < 3.0, "%.1f days with no fire" % w_gap, "< 3 days (the bar's red)", what)
    row("the everyday line does not call the rain (three_skies)", w_rain < v_rain, "%d black rains, even spread %d" % (w_rain, v_rain),
        "fewer than under even spread", what)
    print("     (peak fires at once with the wind carrying: %d)" % w_fire)

    # ---- 5. black rain still puts a fire out (three_skies), wind or no wind ------------------------------------------
    def pad(rain, dousing):
        p = np.zeros((12, 12), np.int8); p[2:10, 2:10] = 1
        s = M.Sim(p, p > 0, 0, weather=rain, clock=False, keepalive=False, sprout_per_day=0, loss_per_day=0, dousing=dousing)
        if rain:
            s.weather = s.last_weather = "BlackRain"; s.w_age = 4500; s.w_dur = 10 ** 9; s.weather_beat = lambda: None
        zs, xs = np.nonzero(p); s.size[zs, xs] = 0.1
        while (s.size > 0).any() and s.tick < 5000:
            s.beat()
        return s.tick
    clear, rained, vanilla_rain = pad(False, 0), pad(True, 40.0), pad(True, 0.0)
    row("black rain puts a pad fire out (three_skies)", rained <= clear - 1000, "out at %d, clear sky %d" % (rained, clear),
        "1,000 ticks before the clear pad", "8 x 8 ember-grass pad, every cell lit (visit 1's rain_fire.py)")
    row("RED CONTROL vanilla rain alone does not", vanilla_rain > clear - 1000, "out at %d, clear sky %d" % (vanilla_rain, clear),
        "not 1,000 ticks sooner", "the same pad, dousing 0 (visit 1 measured both pads out at 2,250)")

    bad = rows.count(False)
    print("%s: %d of %d rows hold" % ("PASS" if not bad else "FAIL", len(rows) - bad, len(rows)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
