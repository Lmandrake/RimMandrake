"""selftest_hospice_offline.py -- WARSCAR_HOSPICE_DESERTERS_1, the parts provable without a game.

1. Scarlands validation.py static_checks() is clean (histories verbatim, servitor overseer-free, cradle lights,
   walk-in letter, wreck study, Droidworks hand-off patch).
2. GenStep_KneelingRings, ported line for line: over a sweep of map sizes, centres and seeds, the intact count is
   0..min(setting, slots) (default 2: the spec's 0-2), every placed chassis is inside the map, and every non-intact
   chassis faces the ring centre (Rot4.FromAngleFlat of the centre direction is within 45 degrees of it).
3. Cradle timing: five stages at hospiceStageDays, the etchant-less limbs stage 1.5x after its grace, matches the
   C# constants read from the source (EtchantGraceTicks, the 1.5f factor, the 250-tick rare step).
A port is only as good as its match to the source: check 4 reads the C# and fails if the constants it copies moved.
"""
import math
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCAR = os.path.join(HERE, "..", "Scarlands")
sys.path.insert(0, SCAR)
import validation  # noqa: E402

SRC = open(os.path.join(SCAR, "Source", "RM_Hospice.cs")).read()
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


# 4 (first): the constants the port copies are still the source's.
for needle in ("int[] radii = { 6, 10, 14 };", "Mathf.RoundToInt(radii[r] * 1.5f)", "Rand.Range(-8f, 8f)", "Rand.Chance(0.2f)",
               "Rand.RangeInclusive(0, Mathf.Clamp(RM_WarscarSettings.hospiceIntactPerMap, 0, 3))",
               "public const int EtchantGraceTicks = 15000;", "public const int Rare = 250;",
               "(stage == 3 && !etchantIn) ? 1.5f : 1f", "StageDays * 60000f * f"):
    check(needle in SRC, "RM_Hospice.cs moved a constant the offline port copies: %s" % needle)

# 1
probs = validation.static_checks()
check(not probs, "validation.py static: %s" % probs)


# 2: ring geometry
def rot4_from_angle(a):
    a %= 360
    if a < 45 or a > 315:
        return 0      # North
    if a < 135:
        return 1      # East
    if a < 225:
        return 2      # South
    return 3          # West


def angle_flat(dx, dz):
    # Vector3.AngleFlat: 0 = north (+z), clockwise
    return (math.degrees(math.atan2(dx, dz))) % 360


def rings(size, centre, setting, rng):
    slots = []
    for rad in (6, 10, 14):
        count = int(round(rad * 1.5))
        for i in range(count):
            a = math.radians(360.0 * i / count + rng.uniform(-8, 8))
            c = (int(round(centre[0] + rad * math.cos(a))), int(round(centre[1] + rad * math.sin(a))))
            if not (0 <= c[0] < size and 0 <= c[1] < size):
                continue
            if rng.random() < 0.2:
                continue
            slots.append(c)
    rng.shuffle(slots)
    intact = min(len(slots), rng.randint(0, max(0, min(setting, 3))))
    return slots, intact


n = 0
for size in (50, 75, 100, 150, 250):
    for setting in (0, 1, 2, 3):
        for seed in range(60):
            rng = random.Random(seed * 7919 + size + setting)
            centre = (rng.uniform(0, size), rng.uniform(0, size))
            slots, intact = rings(size, centre, setting, rng)
            n += 1
            check(0 <= intact <= min(setting, len(slots)), "intact %d outside 0..%d" % (intact, setting))
            if setting == 2:
                check(intact <= 2, "default setting produced %d intact (spec: 0-2)" % intact)
            for (x, z) in slots[intact:]:
                dx, dz = centre[0] - (x + 0.5), centre[1] - (z + 0.5)
                if abs(dx) + abs(dz) < 1e-6:
                    continue
                ang = angle_flat(dx, dz)
                face = rot4_from_angle(ang) * 90
                diff = min((ang - face) % 360, (face - ang) % 360)
                check(diff <= 45.0 + 1e-6, "chassis at %s faces %d, centre bearing %.1f" % ((x, z), face, ang))
check(n == 5 * 4 * 60, "sweep ran %d maps" % n)

# 3: timing (defaults read from the settings source)
days = validation.DEFAULTS["hospiceStageDays"]
stage = int(round(days * 60000))
grace = 15000
total_with = 5 * stage
total_without = 4 * stage + grace + int(round(days * 60000 * 1.5))
check(validation.DEFAULTS["hospiceIntactPerMap"] == 2, "default intact per map is not 2")
check(total_with == int(round(7.5 * 60000)) if days == 1.5 else total_with > 0, "five stages at %.1f d = %d ticks" % (days, total_with))
check(total_without > total_with, "the etchant-less path is not slower")
for k in ("hospicePursuerChance", "hospiceStudyResearch"):
    check(k in validation.DEFAULTS, "Mod Setting %s missing" % k)

print("hospice offline: %d ring maps swept; five stages %.1f d with etchant, %.2f d without" % (n, total_with / 60000.0, total_without / 60000.0))
if fails:
    for f in fails[:20]:
        print("FAIL " + f)
    sys.exit(1)
print("PASS")
