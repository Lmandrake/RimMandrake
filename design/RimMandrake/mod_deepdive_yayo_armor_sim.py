"""Per-hit, single armour layer: vanilla Verse.ArmorUtility.ApplyArmor vs Yayo's
yayoCombat.ArmorUtility.applyArmor (advArmor on, armorEf 50 -> s_armorEf 0.5).
Transcribed from RimSage (vanilla 1.6) and emipa606/YayosCombat3 @4f436d1 (DLL byte-identical
to the installed workshop 2854006492 copy). Output: expected damage fraction, P(no damage),
armour HP lost per point of incoming damage. Monte Carlo, fixed seed."""
import random

R = random.Random(1)
N = 200000


def vanilla(ap, rating):
    eff = max(rating - ap, 0.0)
    tot = zero = 0.0
    for _ in range(N):
        u = R.random()
        if u < eff * 0.5:
            d = 0.0
        elif u < eff:
            d = 0.5
        else:
            d = 1.0
        tot += d
        zero += d == 0
    return tot / N, zero / N, 0.25


def yayo(ap, rating, hp=1.0, mult=1.0, armor_ef=0.5):
    num = ap * mult
    left = max(rating - num, 0.0)
    admg = min(max((num - rating * 0.15) * 5.0, 0.0), 1.0)
    wear = 0.2 + admg * 0.5
    defence = max(rating * 0.9 - num, 0.0)
    gethit = 1.0 - armor_ef
    tot = zero = 0.0
    for _ in range(N):
        u = R.random()
        if u * gethit < defence * hp:
            if R.random() < min(left, 0.9):
                d = 0.0
            else:
                d = 0.25 + admg * 0.25
        elif u < left * (0.5 + hp * 0.5):
            d = 0.5
        else:
            d = 1.0
        tot += d
        zero += d == 0
    return tot / N, zero / N, wear


CASES = [
    # label, ap, rating, tech multiplier Yayo applies (weapon tech vs armour tech)
    ("assault rifle (Yayo AP 0.19) vs flak vest 1.00", 0.19, 1.00, 1.0),
    ("assault rifle (vanilla AP 0.165) vs flak vest 1.00", 0.165, 1.00, 1.0),
    ("assault rifle 0.19 vs flak jacket 0.55", 0.19, 0.55, 1.0),
    ("assault rifle 0.19 vs marine armour 1.06 (spacer; industrial gun, no mult)", 0.19, 1.06, 1.0),
    ("charge rifle 0.35 vs marine armour 1.06", 0.35, 1.06, 1.0),
    ("great bow ~0.2 (neolithic) vs marine armour 1.06 (x0.35)", 0.2, 1.06, 0.35),
    ("longsword ~0.3 (medieval melee) vs marine armour 1.06 (x0.5)", 0.3, 1.06, 0.5),
    ("lightsaber AP 0 (ultra melee) vs flak vest 1.00", 0.0, 1.00, 1.0),
    ("lightsaber AP 0 vs cortosis 2.00", 0.0, 2.00, 1.0),
    ("vibro AP 0.90 vs warcasket ~1.06", 0.90, 1.06, 1.0),
    ("vibro AP 1.60 vs cortosis 2.00", 1.60, 2.00, 1.0),
    ("slug AP 0.85 vs flak vest 1.00", 0.85, 1.00, 1.0),
]

if __name__ == "__main__":
    print("| case | vanilla E[dmg] | vanilla P(0) | Yayo E[dmg] @100% HP | Yayo P(0) | Yayo E[dmg] @50% HP | armour wear/dmg vanilla -> Yayo |")
    print("|---|---|---|---|---|---|---|")
    for lab, ap, r, m in CASES:
        v = vanilla(ap, r)
        y = yayo(ap, r, 1.0, m)
        y5 = yayo(ap, r, 0.5, m)
        print("| %s | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f -> %.2f |" % (lab, v[0], v[1], y[0], y[1], y5[0], v[2], y[2]))
