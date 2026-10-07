#!/usr/bin/env python3
"""Planted-bug check for the FeverWood fuzz: plants one defect at a time in a production kernel, runs
selftest_feverwood_fuzz.py, and requires it to FAIL; always restores the kernel byte-identical (and verifies it).

    python3 src/RimMandrake/Utils/mutate_feverwood_fuzz.py [N]      # N = only mutation number N (1-based)

Each mutation waits >=4 s before its run: winbuild's staged build can reuse a stale copy otherwise.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(os.path.dirname(HERE), "FeverWood", "Source", "Kernel")
FUZZ = os.path.join(HERE, "selftest_feverwood_fuzz.py")

MUTATIONS = [
    ("RM_BroodKernel.cs", "return Math.Min(c, 1f + Math.Max(0f, perYoung) * tally);", "return Math.Min(c, 1f + Math.Max(0f, perYoung) * tally * 2f);", "boldness doubles"),
    ("RM_BroodKernel.cs", "if (!enabled) return 1f;\n            float c", "float c", "boldness ignores the ransom switch"),
    ("RM_BroodKernel.cs", "while (reached < Thresholds.Length && tally >= Thresholds[reached])", "while (reached < Thresholds.Length && tally > Thresholds[reached])", "letter threshold off by one"),
    ("RM_BroodKernel.cs", "while (announcedLevel > 0 && tally < Thresholds[announcedLevel - 1])", "while (false)", "no quiet step-down (level sticks after the tally falls)"),
    ("RM_BroodKernel.cs", "if (hasOverride) return overrideYoung;", "if (hasOverride && overrideYoung > 0) return overrideYoung;", "an override of 0 is ignored"),
    ("RM_BroodKernel.cs", "return !alreadyFreed;", "return true;", "a freed display tank lowers the town every time"),
    ("RM_BroodKernel.cs", "return Math.Max(0f, weight * (hasMultiplier ? multiplier : 1f));", "return weight * (hasMultiplier ? multiplier : 1f);", "negative gift multiplier not floored"),
    ("RM_BroodKernel.cs", "float c = fixedChance >= 0f ? fixedChance : settingChance;", "float c = fixedChance > 0f ? fixedChance : settingChance;", "a fixed stock chance of 0 falls back to the setting"),
    ("RM_BroodKernel.cs", "if (weights[i] > 0f) candidates.Add(i);", "candidates.Add(i);", "zero-weight gift rows become candidates"),
    ("RM_BroodKernel.cs", "if (now < ticks[i]) continue;", "if (now <= ticks[i]) continue;", "a gift due this very tick waits another poll"),
    ("RM_TankKernel.cs", "return !(daysUnfed < thresholdDays);", "return daysUnfed > thresholdDays;", "neglect starts a tick late (> instead of >=)"),
    ("RM_TankKernel.cs", "unfedSinceTick = -1;\n                return false;", "return false;", "feeding does not reset the unfed clock"),
    ("RM_TankKernel.cs", "float c = chancePerHit / RiskMultiplier(riskSetting);", "float c = chancePerHit * RiskMultiplier(riskSetting);", "risk multiplier inverted on the damage roll"),
    ("RM_TankKernel.cs", "if (!occupied || !hasMap) return false;", "if (!hasMap) return false;", "an empty display tank frees its young again"),
    ("RM_TankKernel.cs", "if (!tankEnabled || !occupied || foreignDisplay) return false;", "if (!tankEnabled || !occupied) return false;", "a town's display tank ticks on the player"),
    ("RM_PoolKernel.cs", "return !(now < blockedUntil);", "return !(now <= blockedUntil);", "a respite lasts one tick too long"),
    ("RM_PoolKernel.cs", "public static int Extend(int blockedUntil, int until) { return until > blockedUntil ? until : blockedUntil; }", "public static int Extend(int blockedUntil, int until) { return until; }", "a short respite cuts a long one short"),
    ("RM_PoolKernel.cs", "long u = (long)now + ticks;", "long u = (long)(now + ticks);", "block clock wraps instead of saturating"),
    ("RM_PoolKernel.cs", "return kind == AmbientKind.Great ? 0 : pressure + 1;", "return pressure + 1;", "a Great Emergence does not spend the pressure"),
    ("RM_PoolKernel.cs", "hush = count == 1;", "hush = count >= 1;", "every sentinel hushes the chorus again"),
]


def main(argv):
    only = int(argv[0]) if argv else None
    caught = missed = 0
    for n, (f, old, new, label) in enumerate(MUTATIONS, 1):
        if only and n != only:
            continue
        p = os.path.join(K, f)
        orig = open(p, "rb").read()
        text = orig.decode("utf-8")
        if text.count(old) != 1:
            print(f"{n:2d} SKIP (pattern matches {text.count(old)}x) {label}")
            missed += 1
            continue
        try:
            open(p, "wb").write(text.replace(old, new).encode("utf-8"))
            time.sleep(4)
            os.utime(p, None)
            rc = subprocess.run([sys.executable, FUZZ], capture_output=True, text=True)
            out = rc.stdout + rc.stderr
            failed = rc.returncode != 0 and "selftest build FAILED" not in out
            first = next((l for l in out.splitlines() if l.startswith("FAIL")), "")
            print(f"{n:2d} {'CAUGHT' if failed else 'MISSED'} {label} | {first[:150]}")
            caught += failed
            missed += not failed
        finally:
            open(p, "wb").write(orig)
            assert open(p, "rb").read() == orig, "restore failed"
    print(f"mutations: {caught} caught, {missed} missed/skipped")
    return 1 if missed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
