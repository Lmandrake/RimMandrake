#!/usr/bin/env python3
"""selftest_pyrelands_regrow_rates: validation.regrow_rate_verdict (sc_grass_regreens, row regrow_dry_watered_vanilla)
decides the growth part of bar grass_carpets_and_regreens truly over the range of series the scene can read.

Item RIMMANDRAKE_TRACE_PYRE_EMBERGRASS_GROWS_TENTH_OF_ITS_RATE. The parent's decision (kept here as old_verdict, run with
`--old`) took the mean daily gain over all 5 days and called a day's gain above 1.5x the vanilla-scaled rate a "burst".
Once ember grass grows at x1 on dry ash it matures by about day 2, so that mean reads ~0.19 a day against the 0.369 asked,
watered and dry tie at 1.0, and the healthy first day reads as a "burst": the parent check cannot pass a correct mod.

The range of situations (what the live scene can vary for this row):
  - dry ember rate rd: 0.005 to 1.4 a day (fireDryMultiplier slider 0.01-2 x growDays 0.8 x the day's light, heat, fertility)
  - watered over dry: x0.8 to x1.6 (ash-field fertility 140% vs 70% and wet roots; the patch sits beside WaterShallow, and
    ExplosiveGrowth's RM_WetSources wets only a plant's own cell, so the watered patch never takes its x10)
  - vanilla Plant_Grass rate rv: 0.03 to 0.40 a day (its heat curve stops at 58 C; never mature inside the first day)
  - start growth 0.05 (the scene sows at 0.05), 5 daily reads after day 0, 16 plants a patch, each read in whole percents
  - a gentle burst at maturity (the plant restarts at 0.05) on any one patch whose plants take a day or more to mature,
    or none
Left out: plants grazed or burned mid-row (the scene isolates and firebreaks), unread days (the row is UNMEASURED before
the verdict runs), and a patch that cycles faster than once a day (ExplosiveGrowth x10 on an EG-wet cell: rain, a spill,
irrigation): a daily read aliases such a cycle into slow steady growth (measured by this sweep before the range was
bounded: 142 wrong verdicts, every one a sub-day cycle), the scene stages no EG-wet cell, and ordinary rain cannot fall
on the Pyrelands (bar no_ordinary_rain). Truth comes from the generator's own rates; a case within the
rounding margin of a threshold (2%) is counted and printed, not judged.

Also the recorded series of visit 4 (game a, 2026-11-22, x0.1 on dry ash, the fault): the verdict must FAIL on it.
`--old` must fail (the parent's decision is wrong on the fixed regime). Offline, WSL python3."""
import os, random, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [H, os.path.join(H, "..", "Utils"), os.path.join(H, "..", "Utils", "modcheck")]
import validation  # noqa: E402

NAME = "selftest_pyrelands_regrow_rates"
GD = {"RM_FE_Plant_EmberGrass": 0.8, "Plant_Grass": 2.5}
SCALE = GD["Plant_Grass"] / GD["RM_FE_Plant_EmberGrass"]
VISIT4 = {"dry": [0.05, 0.1, 0.16, 0.21, 0.26, 0.32], "watered": [0.05, 0.1, 0.16, 0.21, 0.26, 0.32],
          "vanilla": [0.05, 0.18, 0.29, 0.4, 0.52, 0.64]}   # visit_4/evidence/run_embergrass_regrow.log, daily growth note


# visit_9/evidence/run_regrow.log (2026-11-24): no ring, grazed. The dry patch's fifth day reads one plant at 0.68 beside
# fourteen mature: not a restart at 0.05 (the patch gains 0.51 a day), yet the parent counted a burst.
VISIT9 = {"dry": [[0.05] * 16, [0.17] + [0.56] * 7 + [0.57] * 5, [0.57, 0.71] + [1.0] * 12, [0.62] + [1.0] * 14, [1.0] * 15,
                  [0.68] + [1.0] * 14],
          "watered": [[0.05] * 16, [0.38, 0.56, 0.57, 0.57, 0.77, 0.77, 0.77], [0.3, 0.67, 0.67, 0.85] + [1.0] * 6,
                      [0.71, 0.9] + [1.0] * 9, [0.85] + [1.0] * 11, [0.58] + [1.0] * 11],
          "vanilla": [[0.05] * 16, [0.05] * 16, [0.12] * 16, [0.16] * 16, [0.2] * 16, [0.24] * 16]}   # vanilla: the log was cut; these reads are filled in


def old_verdict(series, gd):
    """The parent's inline decision (validation.py at 546cbfc199, _ten_embergrass_regrow), returned as failures."""
    means = dict((k, [x if isinstance(x, (int, float)) else sum(x) / len(x) for x in s]) for k, s in series.items())
    gains = dict((k, [b - a for a, b in zip(s, s[1:])]) for k, s in means.items())
    vanilla_day = sum(gains["vanilla"]) / len(gains["vanilla"])
    ember_rate = vanilla_day * gd["Plant_Grass"] / gd["RM_FE_Plant_EmberGrass"]
    bursts = dict((k, sum(1 for g in gs if g > 1.5 * ember_rate)) for k, gs in gains.items())
    bursts["vanilla"] = sum(1 for g in gains["vanilla"] if g > 1.5 * vanilla_day)
    f = []
    if sum(gains["dry"]) / len(gains["dry"]) < ember_rate:
        f.append("dry below vanilla rate")
    if not sum(gains["watered"]) > sum(gains["dry"]):
        f.append("watered not faster")
    if bursts["dry"] or bursts["vanilla"]:
        f.append("bursts off water")
    return {"failures": f, "unmeasured": []}


def patch_series(rate, rnd, burst=False, days=5, plants=16):
    """Per-plant whole-percent reads each day; each plant +-3% on the patch rate. burst: a plant that reaches maturity
    restarts at 0.05 and keeps growing (a gentle carpet cycles at every maturity). -> (series, restarted at least once)."""
    rows, any_restart = [], False
    for _ in range(plants):
        r = rate * rnd.uniform(0.97, 1.03)
        g, out = 0.05, []
        for d in range(days + 1):
            if d:
                g += r
                while burst and g >= 1.0:
                    g, any_restart = 0.05 + (g - 1.0), True
                g = min(1.0, g)
            out.append(1.0 if g >= 1.0 else round(g * 100) / 100.0)
        rows.append(out)
    return [sorted(c) for c in zip(*rows)], any_restart   # each day: the patch's plant reads, as the live reader returns


def sweep(decide, n=6000, seed=20261122):
    rnd = random.Random(seed)
    wrong, near, unm, worst = [], 0, 0, None
    for _ in range(n):
        rv = rnd.uniform(0.03, 0.40)
        rd = rnd.choice([rnd.uniform(0.005, 0.2), rnd.uniform(0.2, 1.4)])
        rw = rd * rnd.choice([rnd.uniform(0.8, 1.0), rnd.uniform(1.0, 1.3), rnd.uniform(1.3, 1.6)])
        burst = rnd.choice([None, None, "watered", "dry", "vanilla"])
        if burst and {"dry": rd, "watered": rw, "vanilla": rv}[burst] > 0.9:
            burst = None   # a sub-day cycle: out of the declared range (see the docstring)
        made = dict((k, patch_series(r, rnd, burst == k)) for k, r in (("dry", rd), ("watered", rw), ("vanilla", rv)))
        series = dict((k, v[0]) for k, v in made.items())
        burst_off_water = made["dry"][1] or made["vanilla"][1]   # truth: a restart that really happened off the water
        need = rv * SCALE
        true_fail = rd < need or not rw > rd or burst_off_water
        margin = min(abs(rd - need) / need, abs(rw - rd) / rd)
        # within 2% of a threshold the +-3% plant spread and whole-percent reads can flip the read; counted, not judged.
        # Measured (20000 cases, seed 7): 0 wrong verdicts with this margin at 0.02, 2 at 0.01, 22 at 0.
        if margin < 0.02 and not burst_off_water:
            near += 1
            continue
        v = decide(series, GD)
        if v["unmeasured"] and not v["failures"]:
            unm += 1
            continue
        got_fail = bool(v["failures"])
        if got_fail != true_fail:
            wrong.append((round(rd, 3), round(rw, 3), round(rv, 3), burst, v["failures"]))
        m = None if burst_off_water else margin
        if m is not None and (worst is None or m < worst):
            worst = m
    return wrong, near, unm, worst, n


def main():
    old = "--old" in sys.argv
    decide = old_verdict if old else validation.regrow_rate_verdict
    bad = 0
    # the recorded fault: x0.1 on dry ash must read FAIL (dry below its vanilla rate)
    v4 = decide(VISIT4, GD)
    ok = any("dry" in f for f in v4["failures"])
    bad += not ok
    print("%s visit-4 recorded series (x0.1, the fault) -> %r" % ("PASS" if ok else "FAIL", v4["failures"]))
    # the predicted x1 regime (rd ~0.62, watered +11%, grass as measured): must read clean
    pred = {"dry": [0.05, 0.67, 1.0, 1.0, 1.0, 1.0], "watered": [0.05, 0.74, 1.0, 1.0, 1.0, 1.0], "vanilla": VISIT4["vanilla"]}
    vp = decide(pred, GD)
    ok = not vp["failures"] and not vp["unmeasured"]
    bad += not ok
    print("%s predicted x1 series -> failures %r unmeasured %r" % ("PASS" if ok else "FAIL", vp["failures"], vp["unmeasured"]))
    # a burst on the dry patch (a matured plant restarted at 0.05) must read FAIL
    db = {"dry": [0.05, 0.67, 1.0, 0.94, 1.0, 1.0], "watered": pred["watered"], "vanilla": VISIT4["vanilla"]}
    vb = decide(db, GD)
    ok = any("burst" in f for f in vb["failures"])
    bad += not ok
    print("%s dry patch fell 1.0 -> 0.94 (a restart) -> %r" % ("PASS" if ok else "FAIL", vb["failures"]))
    # visit 9: plants left and came in, so a fall is no burst: UNMEASURED and no failure
    v9 = decide(VISIT9, GD)
    ok = not v9["failures"] and bool(v9["unmeasured"])
    bad += not ok
    print("%s visit-9 grazed series -> failures %r unmeasured %r" % ("PASS" if ok else "FAIL", v9["failures"], v9["unmeasured"]))
    # the same fall with every plant still there is a burst: one dry plant of 16 restarted
    full = {"dry": [[0.05] * 16, [0.57] * 16, [1.0] * 16, [1.0] * 16, [1.0] * 16, [0.5] + [1.0] * 15],
            "watered": [[0.05] * 16, [0.66] * 16, [1.0] * 16, [1.0] * 16, [1.0] * 16, [1.0] * 16],
            "vanilla": [[0.05 + 0.1 * d] * 16 for d in range(6)]}
    vf = decide(full, GD)
    ok = any("burst" in f for f in vf["failures"])
    bad += not ok
    print("%s one dry plant of sixteen restarted, none gone -> %r" % ("PASS" if ok else "FAIL", vf["failures"]))
    wrong, near, unm, worst, n = sweep(decide)
    ok = not wrong
    bad += not ok
    print("%s sweep: %d cases, %d wrong verdicts, %d within the 2%% rounding margin (not judged), %d UNMEASURED "
          "(a lower bound only), worst judged margin %.3f (limit 0.02)" % ("PASS" if ok else "FAIL", n, len(wrong), near,
                                                                          unm, worst if worst is not None else -1))
    for w in wrong[:5]:
        print("   wrong: rd %s rw %s rv %s burst %s -> %r" % w)
    print("%s%s: %d of 6 checks failed" % (NAME, " --old" if old else "", bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
