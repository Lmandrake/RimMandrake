"""Worked numbers for design/RimMandrake/mod_deepdive_yayo_full.md.

Exact expectations (no Monte Carlo) for one armour layer, vanilla 1.6 Verse.ArmorUtility.ApplyArmor
against Yayo's Combat 3 yayoCombat.ArmorUtility.applyArmor (emipa606/YayosCombat3 @4f436d1, DLL
byte-identical to workshop 2854006492), plus a seeded multi-hit wear run, accuracy and melee tempo.
GenMath.RoundRandom is expectation-preserving, so it is omitted from expectations.
stdlib only; runs in about a second:  python3 design/RimMandrake/mod_deepdive_yayo_full_sim.py
"""
import random

ARMOR_EF = 0.5            # Yayo armorEf 50 -> s_armorEf; getHitRating = 1 - 0.5
QUAL = ["awful", "poor", "normal", "good", "excellent", "masterwork", "legendary"]
VAN_ARMOR_Q = [0.6, 0.8, 1.0, 1.15, 1.3, 1.45, 1.8]       # ArmorRating_* StatPart_Quality (RimSage)
SQS_ARMOR_Q = [0.2, 0.6, 1.0, 1.3, 1.6, 1.9, 2.35]        # kas.strongerscaling ArmorRatingBase


def vanilla_layer(dmg_frac_in, ap, rating):
    """Returns (expected damage out as fraction of input, P(zero), armour HP lost per input point)."""
    eff = max(min(rating, 2.0) - ap, 0.0)
    p0 = min(eff * 0.5, 1.0)
    phalf = max(min(eff, 1.0) - p0, 0.0)
    return (1 - p0 - phalf) + 0.5 * phalf, p0, 0.25


def yayo_layer(ap_eff, rating, hp=1.0, apparel=True):
    """Yayo applyArmor, ap_eff = AP after the tech multiplier. hp = armour HP fraction (apparel) or the
    pawn's SummaryHealthPercent (natural armour)."""
    rating = min(rating, 2.0)
    left = max(rating - ap_eff, 0.0)
    admg = min(max((ap_eff - rating * 0.15) * 5.0, 0.0), 1.0)
    wear = (0.2 + admg * 0.5) if apparel else 0.0
    defence = max(rating * 0.9 - ap_eff, 0.0)
    a = min(defence * hp / (1.0 - ARMOR_EF), 1.0)        # branch 1: u < a
    pblock = min(left, 0.9)
    partial = (0.25 + admg * 0.25) if apparel else (0.25 + admg * 0.5)
    b = min(left * (0.5 + hp * 0.5), 1.0)                 # branch 2: a <= u < b
    p2 = max(b - a, 0.0)
    p3 = 1.0 - a - p2
    e = a * (1 - pblock) * partial + p2 * 0.5 + p3 * 1.0
    p0 = a * pblock
    return e, p0, wear


def tech_mult(weapon_tech, weapon_is_melee, armour_tech, wearer_is_mech=False):
    order = ["Undefined", "Animal", "Neolithic", "Medieval", "Industrial", "Spacer", "Ultra", "Archotech"]
    w, a = order.index(weapon_tech), order.index(armour_tech)
    if a >= order.index("Spacer") or wearer_is_mech:
        if weapon_is_melee:
            return 0.5 if w <= order.index("Medieval") else 1.0
        return 0.35 if w <= order.index("Medieval") else 1.0
    if a >= order.index("Industrial"):
        if weapon_is_melee:
            return 0.75 if w <= order.index("Neolithic") else 1.0
        return 0.5 if w <= order.index("Medieval") else 1.0
    return 1.0


def table_quality():
    print("\n## A. Assault rifle (11 dmg) vs flak jacket (0.55 sharp, Industrial) by apparel quality")
    print("| quality | rating vanilla curve | rating SQS | CLEAN VANILLA: vanilla engine, AP 0.165, vanilla curve | LIVE: Yayo engine, AP 0.19, SQS, armour 100% HP | LIVE at 50% HP | Yayo engine, vanilla curve, 100% HP |")
    print("|---|---|---|---|---|---|---|")
    for q, vq, sq in zip(QUAL, VAN_ARMOR_Q, SQS_ARMOR_Q):
        rv, rs = 0.55 * vq, 0.55 * sq
        cv = vanilla_layer(1, 0.165, rv)[0]
        ly = yayo_layer(0.19, rs, 1.0)[0]
        ly5 = yayo_layer(0.19, rs, 0.5)[0]
        yv = yayo_layer(0.19, rv, 1.0)[0]
        print("| %s | %.2f | %.2f | %.2f (%.1f) | %.2f (%.1f) | %.2f (%.1f) | %.2f (%.1f) |" % (
            q, rv, rs, cv, cv * 11, ly, ly * 11, ly5, ly5 * 11, yv, yv * 11))


def table_wear(seed=7, runs=4000):
    print("\n## B. Wear: one pawn, normal flak jacket (200 HP, 0.55), torso hit by assault-rifle bullets (11 dmg)")
    print("Mean damage reaching the body per hit, by hit number; and the jacket's mean remaining HP.")
    rnd = random.Random(seed)

    def run(engine, ap):
        dmg_by_hit = [0.0] * 40
        hp_by_hit = [0.0] * 40
        for _ in range(runs):
            hp = 200.0
            for i in range(40):
                if hp <= 0:
                    d = 11.0
                else:
                    u = rnd.random()
                    if engine == "van":
                        hp -= 11 * 0.25
                        eff = max(0.55 - ap, 0)
                        d = 0.0 if u < eff * 0.5 else (5.5 if u < eff else 11.0)
                    else:
                        r = 0.55
                        left = max(r - ap, 0)
                        admg = min(max((ap - r * 0.15) * 5, 0), 1)
                        hp -= 11 * (0.2 + admg * 0.5)      # wear first: the code reads HP after TakeDamage
                        hpper = max(hp, 0) / 200.0
                        defence = max(r * 0.9 - ap, 0)
                        if u * 0.5 < defence * hpper:
                            d = 0.0 if rnd.random() < min(left, 0.9) else 11 * (0.25 + admg * 0.25)
                        elif u < left * (0.5 + hpper * 0.5):
                            d = 5.5
                        else:
                            d = 11.0
                dmg_by_hit[i] += d
                hp_by_hit[i] += max(hp, 0)
        return [x / runs for x in dmg_by_hit], [x / runs for x in hp_by_hit]

    vd, vh = run("van", 0.165)
    yd, yh = run("yayo", 0.19)
    print("| hits | vanilla dmg/hit | vanilla jacket HP after | Yayo dmg/hit | Yayo jacket HP after |")
    print("|---|---|---|---|---|")
    for lo, hi in [(0, 5), (5, 10), (10, 20), (20, 30), (30, 40)]:
        print("| %d-%d | %.1f | %.0f | %.1f | %.0f |" % (lo + 1, hi, sum(vd[lo:hi]) / (hi - lo), vh[hi - 1],
                                                      sum(yd[lo:hi]) / (hi - lo), yh[hi - 1]))
    print("cumulative body damage after 10 / 20 / 40 hits: vanilla %.0f / %.0f / %.0f, Yayo %.0f / %.0f / %.0f" % (
        sum(vd[:10]), sum(vd[:20]), sum(vd[:40]), sum(yd[:10]), sum(yd[:20]), sum(yd[:40])))


def table_melee():
    print("\n## C. Melee, per landed hit, armour at 100% HP; then sustained DPS with the tempo patch")
    cases = [
        # label, dmg, ap, weapon tech, melee?, armour rating, armour tech
        ("steel longsword stab 23, AP 0.345 vs flak jacket 0.55 (Industrial)", 23, 0.345, "Medieval", True, 0.55, "Industrial"),
        ("steel longsword stab 23, AP 0.345 vs recon armour 0.92 (Spacer)", 23, 0.345, "Medieval", True, 0.92, "Spacer"),
        ("spear stab ~26, AP 0.39 (Neolithic) vs flak jacket 0.55", 26, 0.39, "Neolithic", True, 0.55, "Industrial"),
        ("knife/club vs tribalwear 0.0x: no armour", 10, 0.15, "Neolithic", True, 0.0, "Neolithic"),
        ("fist 8.2, AP 0.12 (race def, Undefined) vs flak jacket 0.55", 8.2, 0.123, "Undefined", False, 0.55, "Industrial"),
    ]
    print("| case | tech multiplier | vanilla E[dmg] | Yayo E[dmg] | Yayo P(no dmg) |")
    print("|---|---|---|---|---|")
    for lab, dmg, ap, wt, melee, r, at in cases:
        m = tech_mult(wt, melee, at)
        v = vanilla_layer(1, ap, r)[0]
        y = yayo_layer(ap * m, r)
        print("| %s | x%.2f | %.1f | %.1f | %.2f |" % (lab, m, v * dmg, y[0] * dmg, y[1]))
    base_cd = 2.6
    print("tempo: longsword cooldown %.1f s -> E[%.2f s] (x0.7 x U[0.35,1.65]); attacks per 60 s %.1f -> %.1f (+%.0f%%)" % (
        base_cd, base_cd * 0.7, 60 / base_cd, 60 / (base_cd * 0.7), (1 / 0.7 - 1) * 100))


def table_animal():
    print("\n## D. Animals and mechs")
    cases = [
        # label, dmg, ap, mult, rating, apparel?, hp
        ("thrumbo horn 23, AP 0.345 vs flak jacket 0.55 (race def -> non-melee, Undefined: x0.5)", 23, 0.345, 0.5, 0.55, True, 1.0),
        ("thrumbo horn 23 vs recon armour 0.92 (Spacer: x0.35)", 23, 0.345, 0.35, 0.92, True, 1.0),
        ("warg-size bite 15, AP 0.225 vs flak jacket 0.55 (x0.5)", 15, 0.225, 0.5, 0.55, True, 1.0),
        ("assault rifle 11, AP 0.19 vs healthy thrumbo natural 0.60", 11, 0.19, 1.0, 0.60, False, 1.0),
        ("assault rifle 11, AP 0.19 vs thrumbo at 50% health", 11, 0.19, 1.0, 0.60, False, 0.5),
        ("assault rifle 11, AP 0.19 vs lancer: vanilla 0.40 natural; Yayo x1.3 = 0.52", 11, 0.19, 1.0, 0.52, False, 1.0),
        ("assault rifle 11, AP 0.19 vs centipede: vanilla 0.72; Yayo 0.936", 11, 0.19, 1.0, 0.936, False, 1.0),
        ("charge rifle 15, AP 0.35 vs centipede 0.936 (Yayo) / 0.72 (vanilla)", 15, 0.35, 1.0, 0.936, False, 1.0),
    ]
    van_rating = {"lancer": 0.40, "centipede": 0.72}
    print("| case | vanilla E[dmg] | Yayo E[dmg] | Yayo P(no dmg) |")
    print("|---|---|---|---|")
    for lab, dmg, ap, m, r, app, hp in cases:
        rv = r
        for k, v in van_rating.items():
            if k in lab:
                rv = v
        ap_v = 0.165 if ap == 0.19 else ap          # clean vanilla: the rifle's derived AP, not Yayo's 0.19
        v = vanilla_layer(1, ap_v, rv)[0]
        y = yayo_layer(ap * m, r, hp, apparel=app)
        print("| %s | %.1f | %.1f | %.2f |" % (lab, v * dmg, y[0] * dmg, y[1]))


def table_accuracy():
    print("\n## E. Shooter accuracy factor (ShootingAccuracyPawn curve, healthy pawn), vanilla -> Yayo")
    # Per-tile ShootingAccuracyPawn for a healthy pawn, from mod_deepdive_yayo_acc_sim.py (RimSage curve).
    # Range-band factors (ShootingAccuracyFactor_*) are 1 for an unmodified human and are omitted.
    per_tile = {0: 0.890, 5: 0.945, 10: 0.970, 15: 0.982, 20: 0.990}
    print("| skill | per-tile vanilla | per-tile Yayo | @12 vanilla -> Yayo | @25 | @40 |")
    print("|---|---|---|---|---|---|")
    for lvl, acc in per_tile.items():
        boosted = min(acc + lvl / 20 * (1 - acc), 1.0)
        y = acc + (boosted - acc) * 0.6
        print("| %d | %.3f | %.3f | %.2f -> %.2f | %.2f -> %.2f | %.2f -> %.2f |" % (
            lvl, acc, y, acc ** 12, y ** 12, acc ** 25, y ** 25, acc ** 40, y ** 40))


if __name__ == "__main__":
    table_quality()
    table_wear()
    table_melee()
    table_animal()
    table_accuracy()
