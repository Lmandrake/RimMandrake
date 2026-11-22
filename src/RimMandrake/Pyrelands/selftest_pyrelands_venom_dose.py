#!/usr/bin/env python3
"""T_VENOM_DOSE (RIMMANDRAKE_TUNE_PYRE_FLAMEFANG_BITE_KILLS_BEFORE_IMMUNITY): a healthy colonist throws off one untended
flamefang bite. Bar flamefang_bite_carries_venom: the venom smoulders worse over the hours "until treated or thrown off".

Visit 3 (game b, 2026-11-21) measured one untended bite at 0.434 and a death by day 2. Cause: the fauna normalization's
Law 3 patch raised the venom-fangs' power from 10 to 22.5, so 0.02 a point of damage made 0.45 a bite, and the course
(+0.35/day until immunity at 0.5/day x a per-instance 0.8..1.2 factor) added 0.58..0.88 more. This test reads the
SHIPPED defs and patches through venom_dose.py (vanilla's arithmetic is cited there).

The range it reads (the grid), for one landed, untended bite on a healthy colonist (an adult baseliner, body size 1,
ImmunityGainSpeed 1 or above):
  the damage roll        0.8 .. 1.2, step 0.01 (Verb_MeleeAttackDamage)
  the immunity factor    0.8 .. 1.2, step 0.01 (ImmunityRecord, seeded per hediff)
  ImmunityGainSpeed      1.0, 1.1, 1.2 (bed rest and good health only raise it)
  armour let-through     1.0, 0.5 (armour only lowers the damage)
  the attacker factor    1.0, 0.75 (an adult flamefang's mouth at full efficiency; a hurt or young one bites softer)
  the rise factor        the def's severityPerDayNotImmuneRandomFactor ends
Left out, each printed as a reading, not a verdict: a child or small colonist (vanilla scales the dose by inverse body
size, as it does for every venom); a colonist whose ImmunityGainSpeed is below 1 (sick, starving, old); two or more
bites (the Designer's open question RIMMANDRAKE_WEIGH_PYRE_TWO_FLAMEFANG_BITES_KILL_UNTENDED).

Calibration: with the visit-3 build's dose (0.02 a point), the model's dose range must hold the two venom severities
visit 3 read on a fresh bite (0.4549 and 0.4344). A model that ignores the Law 3 patch (the old flat 0.2) cannot.

  python3 <this file>          exit 0 = every check PASS, 1 = any FAIL, 2 = the defs could not be read
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import venom_dose as vd  # noqa: E402

NAME = "selftest_pyrelands_venom_dose"
VISIT3_PER_DAMAGE = 0.02                 # RM_FlamefangVenomBite on the visit-3 build
VISIT3_FRESH_DOSES = (0.454911947, 0.4343684)   # visit_3/evidence/run_flamefang_venom_repaired4.log, at the bite
STEPS = [0.8 + 0.01 * i for i in range(41)]
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, (" (%s)" % detail) if detail and not ok else ""))
    return ok


def sweep(v):
    """(worst peak, its case, cases read) over the declared grid."""
    worst, case, n = -1.0, None, 0
    for roll in STEPS:
        for f in STEPS:
            for g in (1.0, 1.1, 1.2):
                for armour in (1.0, 0.5):
                    for att in (1.0, 0.75):
                        for rf in v["rise_factor"]:
                            n += 1
                            p = vd.peak(v, vd.dose(v, roll, armour, att), g, f, rf)
                            if p > worst:
                                worst, case = p, dict(roll=roll, f=f, g=g, armour=armour, attacker=att, rise_factor=rf)
    return worst, case, n


def verdicts(v, label, quiet=False):
    """The three bar checks on venom numbers `v` -> {name: bool}."""
    worst, case, n = sweep(v)
    out = {}
    out["thrown_off"] = worst < v["lethal"]
    out["smoulders"] = v["rise"] * min(v["rise_factor"]) > 0
    out["falls_once_immune"] = v["fall"] < 0
    if not quiet:
        lt = v["life_threatening"]
        print("%s: worst one-bite peak %.3f (limit < lethalSeverity %.3g; life-threatening stage from %s); "
              "%d cases read; worst case %r" % (label, worst, v["lethal"], lt, n, case))
        print("%s: rise %+.4f an hour untended (limit > 0); after immunity %+.3f a day (limit < 0)"
              % (label, v["rise"] / 24.0, v["fall"]))
    return out, worst


def main():
    try:
        v = vd.read()
    except vd.DefError as e:
        print("UNMEASURED %s: the venom defs could not be read: %s" % (NAME, e))
        return 2
    print("read: power %.4g from %s; %.4g a point of damage; nominal dose %.4f; immunity %.3g/day (%.2f days)"
          % (v["power"], v["sources"]["power"], v["per_damage"], vd.dose(v), v["immunity"], vd.days_to_immune(v)))
    got, worst = verdicts(v, "shipped")
    check("one untended bite on a healthy colonist is thrown off: peak below lethal over the grid", got["thrown_off"],
          "worst %.3f >= %.3g" % (worst, v["lethal"]))
    check("the venom smoulders worse every hour while untended (rise > 0)", got["smoulders"])
    check("the venom falls once immunity completes (severityPerDayImmune < 0)", got["falls_once_immune"])

    # calibration against the live game: the visit-3 build's dose per point, the shipped power
    v3 = dict(v, per_damage=VISIT3_PER_DAMAGE)
    lo, hi = vd.dose(v3, vd.DAMAGE_RANDOM[0]), vd.dose(v3, vd.DAMAGE_RANDOM[1])
    check("calibration: visit 3's fresh-bite readings %r lie in the model's dose range %.3f..%.3f"
          % (VISIT3_FRESH_DOSES, lo, hi), all(lo <= d <= hi for d in VISIT3_FRESH_DOSES))
    flat = dict(v3, power=v["base_power"])
    flo, fhi = vd.dose(flat, vd.DAMAGE_RANDOM[0]), vd.dose(flat, vd.DAMAGE_RANDOM[1])
    check("calibration: a model blind to the Law 3 patch (base power %.3g) cannot hold them (%.3f..%.3f)"
          % (v["base_power"], flo, fhi), not all(flo <= d <= fhi for d in VISIT3_FRESH_DOSES))

    # planted faults: each must turn its check red
    for what, mut, key in (("the visit-3 dose (0.02 a point)", dict(per_damage=VISIT3_PER_DAMAGE), "thrown_off"),
                           ("immunity as slow as visit 3's (0.5/day)", dict(immunity=0.5), "thrown_off"),
                           ("a venom that never rises", dict(rise=0.0), "smoulders"),
                           ("a venom that never falls", dict(fall=0.0), "falls_once_immune")):
        res, w = verdicts(dict(v, **mut), "planted", quiet=True)
        check("planted: %s -> %s FAIL (worst peak %.3f)" % (what, key, w), res[key] is False)

    # the readings outside the range (no verdict)
    d_max = vd.dose(v, vd.DAMAGE_RANDOM[1])
    g_min = v["rise"] * max(v["rise_factor"]) / (v["immunity"] * vd.IMMUNITY_RANDOM[0] * (v["lethal"] - d_max)) \
        if d_max < v["lethal"] else float("inf")
    print("reading: the worst one-bite case kills a colonist whose ImmunityGainSpeed is below %.2f" % g_min)
    for size in (0.75, 0.5, 0.3):
        print("reading: a colonist of body size %.2g: nominal peak %.3f, worst %.3f"
              % (size, vd.peak(v, vd.dose(v, victim_body_size=size)),
                 vd.peak(v, vd.dose(v, 1.2, victim_body_size=size), f=0.8)))
    print("reading: two untended bites, healthy adult: nominal peak %.3f, worst %.3f (lethal %.3g)"
          % (vd.peak(v, 2 * vd.dose(v)), vd.peak(v, 2 * d_max, f=0.8), v["lethal"]))
    bad = RESULTS.count(False)
    print("%s: %d of %d checks failed" % (NAME, bad, len(RESULTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
