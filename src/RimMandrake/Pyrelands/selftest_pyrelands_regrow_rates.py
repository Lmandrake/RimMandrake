#!/usr/bin/env python3
"""selftest_pyrelands_regrow_rates: validation.regrow_step_verdict (sc_grass_regreens, row regrow_dry_watered_vanilla) decides
the growth part of bar grass_carpets_and_regreens truly over the range of one staged growth step.

The range (what the live scene can vary): dry ember gain 0.0005 to 0.25 in the step (fireDryMultiplier x growDays x the hour's
light and heat), watered over dry x0.8 to x1.6, vanilla grass gain 0.001 to 0.06, a burst on no patch or on any one, the soaked
control bursting or not, a plant taken from or brought into any one patch, the vanilla grass not growing at all (night).
Left out: an unread plant (the live reader returns no patch). The truth comes from the generator. A case within 2% of a
threshold is counted, not judged. `--old` runs a decision with no plant-identity read (the parent's blind spot) and must fail.
Offline, WSL python3."""
import os, random, re, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [H, os.path.join(H, "..", "Utils"), os.path.join(H, "..", "Utils", "modcheck")]
import validation as V  # noqa: E402

NAME = "selftest_pyrelands_regrow_rates"
GD = {"RM_FE_Plant_EmberGrass": 0.8, "Plant_Grass": 2.5}
SCALE = GD["Plant_Grass"] / GD["RM_FE_Plant_EmberGrass"]
CS = os.path.join(H, "..", "ExplosiveGrowth", "Source", "ExplosiveGrowthMod.cs")


def make(rd, rw, rv, rnd, burst=(), swap=None):
    """-> got. burst: patches where one plant restarts at 0.05; swap: a patch where one plant is replaced by another."""
    g = {"growDays": dict(GD), "before": {}, "after": {}, "last": {}}
    for k in V.REGROW_PATCHES:
        ids = ["%s%d" % (k, i) for i in range(16)]
        start = 1.0 if k.startswith("mature") else 0.05
        rate = {"dry": rd, "watered": rw, "vanilla": rv}.get(k, 0.0)
        b = dict((i, start) for i in ids)
        a = dict((i, min(1.0, start + rate * rnd.uniform(0.995, 1.005))) for i in ids)
        la = dict((i, min(1.0, a[i] + rate / 2)) for i in ids)
        if k in burst:
            la[ids[3]] = 0.05 if start == 1.0 else a[ids[3]] - 0.03
        if k == swap:
            la.pop(ids[5]); la["new"] = 0.68
        g["before"][k], g["after"][k], g["last"][k] = b, a, la
    return g


def no_identity(got):
    """The parent's blind spot: a swapped plant is matched by rank, so a newcomer reads as a fall."""
    got = dict(got)
    for k in ("before", "after", "last"):
        got[k] = dict((p, dict(("r%d" % n, v) for n, v in enumerate(sorted(got[k][p].values())))) for p in got[k])
    return V.regrow_step_verdict(got)


def truth(rd, rw, rv, burst, swap):
    if swap:
        return None
    if [k for k in burst if k in ("dry", "vanilla", "matureDry")]:
        return False
    if rv <= 0:
        return None
    if rd < rv * SCALE or not rw > rd:
        return False
    return True if "matureWet" in burst else None


def main():
    decide = no_identity if "--old" in sys.argv else V.regrow_step_verdict
    rnd, wrong, near, counts = random.Random(20261124), [], 0, {True: 0, False: 0, None: 0}
    n = 6000
    for _ in range(n):
        rv = rnd.choice([0.0, rnd.uniform(0.001, 0.06), rnd.uniform(0.001, 0.06)])
        rd = rnd.choice([rnd.uniform(0.0005, 0.25), max(rv, 0.001) * SCALE * rnd.uniform(0.8, 1.4)])
        rw = rd * rnd.uniform(0.8, 1.6)
        burst = tuple(k for k in V.REGROW_PATCHES if rnd.random() < (0.8 if k == "matureWet" else 0.06))
        swap = rnd.choice([None] * 9 + list(V.REGROW_PATCHES))
        if rd >= 0.9 or min(abs(rd - rv * SCALE) / max(rv * SCALE, 1e-9), abs(rw - rd) / rd) < 0.02:
            near += 1
            continue
        want, got = truth(rd, rw, rv, burst, swap), decide(make(rd, rw, rv, rnd, burst, swap))[0]
        counts[want] += 1
        if got is not want:
            wrong.append((round(rd, 4), round(rw, 4), round(rv, 4), burst, swap, want, got))
    bad = bool(wrong)
    print("%s sweep: %d cases (PASS %d, FAIL %d, UNMEASURED %d), %d wrong, %d within the 2%% margin (not judged)" % (
        "FAIL" if wrong else "PASS", n, counts[True], counts[False], counts[None], len(wrong), near))
    for w in wrong[:4]:
        print("   wrong:", w)
    empty = V.regrow_step_verdict({"growDays": GD, "before": {}, "after": {}, "last": {}})[0]
    ok = empty is None
    bad |= not ok
    print("%s an unread patch is UNMEASURED" % ("PASS" if ok else "FAIL"))
    m = re.search(r"static float chargeHours = ([0-9.]+)f", open(CS, encoding="utf-8").read())
    ok = bool(m) and float(m.group(1)) == V.EG_CHARGE_HOURS
    bad |= not ok
    print("%s EG_CHARGE_HOURS is the shipped chargeHours (%s)" % ("PASS" if ok else "FAIL", m.group(1) if m else "unread"))
    ok = V.REGROW_STEP_TICKS % 2000 == 0 and V.REGROW_STEP_TICKS + V.REGROW_BURST_TICKS > V.REGROW_CHARGE_HOURS * 2500
    bad |= not ok
    print("%s the step is whole long ticks and the watch outlasts the charge" % ("PASS" if ok else "FAIL"))
    print("%s: %s" % (NAME, "FAIL" if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
