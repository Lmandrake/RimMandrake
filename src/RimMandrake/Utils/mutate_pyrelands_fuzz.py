#!/usr/bin/env python3
"""Planted-bug check for the Pyrelands fuzz: plants one defect at a time in a production kernel, runs
selftest_pyrelands_fuzz.py, and requires it to FAIL; always restores the kernel byte-identical (and verifies it).

    python3 src/RimMandrake/Utils/mutate_pyrelands_fuzz.py [N]      # N = only mutation number N (1-based)

Each mutation waits >=4 s before its run: winbuild's staged build can reuse a stale copy otherwise.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(os.path.dirname(HERE), "Pyrelands", "Source", "Kernel")
FUZZ = os.path.join(HERE, "selftest_pyrelands_fuzz.py")

MUTATIONS = [
    ('RM_BurnKernel.cs', 'return (now + mapId) % intervalTicks == 0;', 'return now % intervalTicks == 0;', 'maps measure on the same tick'),
    ('RM_BurnKernel.cs', 'cx = sumX / count;', 'cx = sumZ / count;', "the burn centre's x is its z"),
    ('RM_BurnKernel.cs', 'if (ticks.Count > 0 && now - ticks[ticks.Count - 1] < intervalTicks)', 'if (ticks.Count > 0 && now - ticks[ticks.Count - 1] <= intervalTicks)', 'history samples one tick further apart'),
    ('RM_BurnKernel.cs', 'while (ticks.Count > 0 && now - ticks[0] > keepTicks)', 'while (ticks.Count > 0 && now - ticks[0] > keepTicks * 2)', 'the burn history is never pruned in time'),
    ('RM_BurnKernel.cs', 'if (ticks[i] <= cutoff)', 'if (ticks[i] < cutoff)', 'a sample exactly as old as asked for is skipped'),
    ('RM_BurnKernel.cs', 'return ticks.Count > 0 ? 0 : -1;', 'return -1;', 'no fallback to the oldest burn sample'),
    ('RM_BurnKernel.cs', 'return hasInstigator && instigatorHasFaction && factionIsPlayer;', 'return !hasInstigator || (instigatorHasFaction && factionIsPlayer);', "lightning is the colony's fault"),
    ('RM_BurnKernel.cs', 'return Math.Min(cap, debt + playerFires * perFirePerCheck);', 'return debt + playerFires * perFirePerCheck;', 'arson debt has no cap'),
    ('RM_BurnKernel.cs', 'return Math.Max(0f, debt - decayPerCheck);', 'return debt - decayPerCheck;', 'arson debt goes negative'),
    ('RM_BurnKernel.cs', 'return Math.Min(threshold, cap);', 'return threshold;', 'a raid threshold above the cap can never be reached'),
    ('RM_BurnKernel.cs', 'if (ticksSinceAnyFire < quietTicks)', 'if (ticksSinceAnyFire <= quietTicks)', 'the standing burn waits one check longer'),
    ('RM_BurnKernel.cs', 'if (now - lastAttemptTick < retryTicks)', 'if (now - lastAttemptTick <= retryTicks)', 'reseed retry a check longer'),
    ('RM_BurnKernel.cs', 'ticksSinceAnyFire = 0;\n                return RM_ReseedDecision.FiresPresent;', 'return RM_ReseedDecision.FiresPresent;', 'a fire does not reset the quiet clock'),
    ('RM_BurnKernel.cs', 'if (inHomeArea)', 'if (false)', 'the biome lights fires inside the home area'),
    ('RM_BurnKernel.cs', 'return distSq < minDistFromColony * minDistFromColony;', 'return distSq <= minDistFromColony * minDistFromColony;', 'a cell exactly at the minimum distance is too close'),
    ('RM_BurnKernel.cs', 'nextFrontTick = -1;\n                return RM_FrontAction.Disabled;', 'return RM_FrontAction.Disabled;', 'a switched-off fire clock keeps its stale deadline'),
    ('RM_BurnKernel.cs', 'if (now < nextFrontTick)', 'if (now <= nextFrontTick)', 'the front fires a tick late'),
    ('RM_BurnKernel.cs', 'nextFrontTick = now + schedule();\n            return RM_FrontAction.Fire;', 'return RM_FrontAction.Fire;', 'a fired front is never re-armed'),
    ('RM_BurnKernel.cs', 'float days = minDays + roll01 * (maxDays - minDays);', 'float days = minDays + roll01 * maxDays;', 'fronts scheduled past the maximum interval'),
    ('RM_BurnKernel.cs', 'double ux = sx / m, uz = sz / m;', 'double ux = sx, uz = sz;', 'a diagonal front folds onto too few cells'),
    ('RM_BurnKernel.cs', 'for (int i = -half; i < width - half; i++)', 'for (int i = -half; i <= half; i++)', 'an even-width front is one cell too wide'),
    ('RM_BurnKernel.cs', 'if (debt < EffectiveRaidThreshold(threshold, cap))', 'if (debt <= EffectiveRaidThreshold(threshold, cap))', 'the raid needs one point more debt'),
    ('RM_BurnKernel.cs', 'return hostile || hasGoodwill;\n        }\n\n        /// <summary>TryExecuteWorker, first half', 'return hostile;\n        }\n\n        /// <summary>TryExecuteWorker, first half', 'a neutral tribe can never be soured into a raid'),
    ('RM_BurnKernel.cs', 'return hasGoodwill ? RM_RaidPlan.InsultFirst : RM_RaidPlan.Refuse;', 'return RM_RaidPlan.InsultFirst;', 'a faction with no goodwill is insulted'),
    ('RM_BurnKernel.cs', 'return Math.Max(minPoints, points * factor);', 'return points * factor;', 'a small raid has no floor'),
    ('RM_BurnKernel.cs', 'if (!anyBurn || fireCount < minFires)', 'if (!anyBurn || fireCount <= minFires)', 'the harvest needs one fire more than asked'),
    ('RM_BurnKernel.cs', 'return tribesPresent && !hostile;', 'return tribesPresent;', 'hostile tribes still send a harvest'),
    ('RM_BurnKernel.cs', 'return enabled && !(roll01 >= fraction);', 'return enabled && !(roll01 > fraction);', 'the rite roll is inclusive'),
    ('RM_BurnKernel.cs', 'hi = max < min ? min : max;', 'hi = max;', 'a rite party range with max below min'),
    ('RM_FurnaceKernel.cs', 'float over = Math.Min(ambient - chargeAmbientC, chargeSpanC);', 'float over = ambient - chargeAmbientC;', 'a freak reading fills the beast in one check'),
    ('RM_FurnaceKernel.cs', 'step = -bleedPerCheckAtFullCold * (under / bleedSpanC);', 'step = bleedPerCheckAtFullCold * (under / bleedSpanC);', 'cold charges the beast'),
    ('RM_FurnaceKernel.cs', 'return charge < 0f ? 0f : charge > 1f ? 1f : charge;', 'return charge > 1f ? 1f : charge;', 'charge below zero'),
    ('RM_FurnaceKernel.cs', 'return averageCharge >= avoidAbove || ticksAtLeg >= maxLegDwellTicks;', 'return averageCharge >= avoidAbove && ticksAtLeg >= maxLegDwellTicks;', 'the herd waits for charge AND the max dwell'),
    ('RM_FurnaceKernel.cs', 'return averageCharge <= seekBelow || ticksAtLeg >= maxLegDwellTicks;', 'return averageCharge >= seekBelow || ticksAtLeg >= maxLegDwellTicks;', 'the terminator leg ends when the herd is still charged'),
    ('RM_FurnaceKernel.cs', 'case FurnaceHerdLeg.Pyrelands: return FurnaceHerdLeg.Terminator;', 'case FurnaceHerdLeg.Pyrelands: return FurnaceHerdLeg.DeepDesert;', 'the herd skips the terminator'),
    ('RM_FurnaceKernel.cs', 'if (visited.Add(key(scratch[i])))', 'if (true)', 'the tile search revisits tiles'),
    ('RM_FurnaceKernel.cs', 'while (queue.Count > 0 && scanned < cap)', 'while (queue.Count > 0 && scanned <= cap)', 'the tile search looks at one tile too many'),
    ('RM_FurnaceKernel.cs', 'return slept < minRestTicks ? RM_RestOutcome.WokeTooShort : RM_RestOutcome.WokeRested;', 'return slept <= minRestTicks ? RM_RestOutcome.WokeTooShort : RM_RestOutcome.WokeRested;', 'a rest of exactly the minimum is too short'),
    ('RM_FurnaceKernel.cs', 'restingTicks = 0;\n            return slept', 'return slept', 'the rest clock survives waking'),
    ('RM_FurnaceKernel.cs', 'return Math.Max(0.25f, baseSize / classicBodySize);', 'return baseSize / classicBodySize;', 'a small beast has no size floor'),
    ('RM_FurnaceKernel.cs', 'spread = Math.Max(1.5f, 1.5f * sizeRatio);', 'spread = 1.5f * sizeRatio;', 'a small beast smoulders in a pinpoint'),
    ('RM_FurnaceKernel.cs', 'return now - lastSortieTick >= cooldownTicks;', 'return now - lastSortieTick > cooldownTicks;', 'the hawk sortie cooldown a tick long'),
    ('RM_FurnaceKernel.cs', 'if (MatchesAny(biomeDefName, pyrelandsNames))', 'if (MatchesAny(biomeDefName, terminatorNames))', 'a Pyrelands biome routes to the terminator leg'),
    ('RM_FurnaceKernel.cs', 'StringComparison.Ordinal', 'StringComparison.OrdinalIgnoreCase', 'biome names match case-insensitively'),
    ('RM_BreakerKernel.cs', 'if (!inNet(n) || visited.Contains(n))', 'if (visited.Contains(n))', 'the fault spreads outside the power net'),
    ('RM_BreakerKernel.cs', 'if (armedBreaker(n))\n                    {\n                        boundary.Add(n);\n                        continue;', 'if (false)\n                    {\n                        boundary.Add(n);\n                        continue;', 'the flood passes through armed breakers'),
    ('RM_BreakerKernel.cs', 'return visited.Contains(battery) || (hasParent && visited.Contains(parent));', 'return visited.Contains(battery);', 'batteries on the faulted conduits are all spared'),
    ('RM_BreakerKernel.cs', 'return boundaryCount > 0 && protectedBatteries > 0;', 'return boundaryCount > 0;', 'a trip with nothing to spare'),
    ('RM_BreakerKernel.cs', 'if (e > 20f)', 'if (e >= 20f)', '20 Wd is enough to blow'),
    ('RM_BreakerKernel.cs', 'return r < 1.5f ? 1.5f : r > 14.9f ? 14.9f : r;', 'return r < 1.5f ? 1.5f : r;', 'the blast radius has no ceiling'),
    ('RM_BreakerKernel.cs', '(!hasHopper || fuel >= tripCost)', '(!hasHopper || fuel > tripCost)', 'a breaker with exactly the trip cost is not armed'),
    ('RM_FireEcoKernel.cs', 'if (rainfall < rMin || rainfall >= rMax)', 'if (rainfall < rMin || rainfall > rMax)', 'rainfall band is closed at the top'),
    ('RM_FireEcoKernel.cs', 'if (mountainousOrImpassable)', 'if (false)', 'the grassland biome wins mountain tiles'),
    ('RM_FireEcoKernel.cs', 'if (rate <= 0f)\n            {\n                return 0;', 'if (rate < 0f)\n            {\n                return 0;', 'a zero ash rate still deposits one'),
    ('RM_FireEcoKernel.cs', 'rate = cinderFactor;', 'rate = 1f;', 'cinderfall drops full ash'),
    ('RM_FireEcoKernel.cs', 'if (rolled.Count > bound)', 'if (false)', 'the roll set is never cleared'),
    ('RM_FireEcoKernel.cs', 'if (trimmed.Length > 0)', 'if (true)', 'blank biome-list entries are kept'),
    ('RM_FireEcoKernel.cs', 'return pyrelandsEnabled || !pyrelandsGround;', 'return pyrelandsEnabled;', 'stillsand fulgurites need the Pyrelands on'),
    ('RM_FireEcoKernel.cs', '!spawned || attachedToPawn)', '!spawned)', 'a burning pawn seeds scorch-fruit'),
    ('RM_FireEcoKernel.cs', 'n == "Gravel" ||', '', 'gravel is not scorchable'),
    ('RM_FireEcoKernel.cs', 'if (!enabled || !hasBiome || isNative)', 'if (!enabled || !hasBiome)', 'the native biome counts as cross-biome'),
    ('RM_FireEcoKernel.cs', 'StartsWith("RM_FE_", StringComparison.Ordinal);\n        }\n\n        public static bool IsScorchableGround', 'StartsWith("RM_FE", StringComparison.Ordinal);\n        }\n\n        public static bool IsScorchableGround', 'the ground prefix loses its underscore'),
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
            rc = subprocess.run([sys.executable, FUZZ, "--fuzz-scale", "0.5"], capture_output=True, text=True)
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
