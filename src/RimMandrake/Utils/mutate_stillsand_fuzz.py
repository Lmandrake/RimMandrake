#!/usr/bin/env python3
"""Planted-bug check for the Stillsand fuzz: plants one defect at a time in a production kernel, runs
selftest_stillsand_fuzz.py, and requires it to FAIL; always restores the kernel byte-identical (and verifies it).

    python3 src/RimMandrake/Utils/mutate_stillsand_fuzz.py [N]      # N = only mutation number N (1-based)

Each mutation waits >=4 s before its run: winbuild's staged build can reuse a stale copy otherwise.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(os.path.dirname(HERE), "Stillsand", "Source", "Kernel")
FUZZ = os.path.join(HERE, "selftest_stillsand_fuzz.py")

MUTATIONS = [
    ('RM_LeviathanKernel.cs', 'return !(visitCount == 0 || now % Interval != 0);', 'return !(visitCount == 0);', 'the component processes its visits on every tick'),
    ('RM_LeviathanKernel.cs', 'return now < arriveTick ? RM_VisitClass.Rumble : RM_VisitClass.Arrive;', 'return now <= arriveTick ? RM_VisitClass.Rumble : RM_VisitClass.Arrive;', 'arrival waits one extra check'),
    ('RM_LeviathanKernel.cs', 'return fallbackFound ? RM_ArriveCell.UseFallback : RM_ArriveCell.Fail;', 'return RM_ArriveCell.Fail;', 'an unusable entry cell never falls back'),
    ('RM_LeviathanKernel.cs', 'return 1f - (x < 0f ? 0f : x > 1f ? 1f : x);', 'return 1f - (x > 1f ? 1f : x);', 'the rumble overshoots past the arrival'),
    ('RM_LeviathanKernel.cs', 'if (kills > killsAtArrival)\n            {\n                return RM_DiveReason.Fed;\n            }\n            if (burning)', 'if (burning)\n            {\n                return RM_DiveReason.Fire;\n            }\n            if (kills > killsAtArrival)\n            {\n                return RM_DiveReason.Fed;\n            }\n            if (false)', 'fire outranks a kill (the fed leviathan never takes the body)'),
    ('RM_LeviathanKernel.cs', 'if (now - arriveTick > maxStayTicks)', 'if (now - arriveTick >= maxStayTicks)', 'bored one check early'),
    ('RM_LeviathanKernel.cs', 'hardGroundTicks = onSand ? 0 : hardGroundTicks + Interval;', 'hardGroundTicks = onSand ? hardGroundTicks : hardGroundTicks + Interval;', 'sand never resets the hard-ground clock'),
    ('RM_LeviathanKernel.cs', 'if (hardGroundTicks > hardGroundGiveUpTicks)', 'if (hardGroundTicks >= hardGroundGiveUpTicks)', 'hard-ground give-up a check early'),
    ('RM_LeviathanKernel.cs', 'if (onSand || now - diveStartTick > DiveTimeoutTicks)', 'if (onSand || now - diveStartTick >= DiveTimeoutTicks)', 'the dive timeout a check early'),
    ('RM_LeviathanKernel.cs', 'return hasGotoJob ? RM_DiveStep.KeepSeeking : RM_DiveStep.SeekSand;', 'return RM_DiveStep.SeekSand;', 'a diving visitor re-issues its goto every check'),
    ('RM_LeviathanKernel.cs', 'return wasSubmerged && !submerged && !downed;', 'return wasSubmerged && !submerged;', 'a downed swimmer still breaches'),
    ('RM_LeviathanKernel.cs', 'return targetInvalid || now % HuntRetargetInterval == 0;', 'return targetInvalid;', 'the muurrok never re-appraises a live target'),
    ('RM_LeviathanKernel.cs', 'now - lastBeamTick >= beamCooldownTicks &&', 'now - lastBeamTick > beamCooldownTicks &&', 'beam cooldown one check long'),
    ('RM_LeviathanKernel.cs', 'hydration = Math.Max(0.05f, hydrationPercent);', 'hydration = hydrationPercent;', 'a parched body scores zero and is never hunted'),
    ('RM_LeviathanKernel.cs', 'return (player && !bestPlayer) || (player == bestPlayer && score > bestScore);', 'return (player == bestPlayer && score > bestScore);', "the muurrok does not prefer the colony's bodies"),
    ('RM_LeviathanKernel.cs', 'return (sand && !bestOnSand) || (sand == bestOnSand && distSq < bestDistSq);', 'return (sand == bestOnSand && distSq < bestDistSq);', 'the entry cell ignores swim ground'),
    ('RM_LeviathanKernel.cs', 'return Math.Min(1f + perDrill * drills, maxFactor);', 'return 1f + perDrill * drills;', 'the drill odds boost has no ceiling'),
    ('RM_LeviathanKernel.cs', 'return end == RM_VisitEnd.ArriveFailed || end == RM_VisitEnd.Dived;', 'return end == RM_VisitEnd.Dived;', 'a failed arrival vanishes without a sign'),
    ('RM_LedgerKernel.cs', 'float paid = Math.Min(litres, debt);', 'float paid = litres;', 'paying more than the debt drives it negative'),
    ('RM_LedgerKernel.cs', 'if (band > lastBand && goodwillPerBandUp != 0)', 'if (band != lastBand && goodwillPerBandUp != 0)', 'paying the debt down costs goodwill'),
    ('RM_LedgerKernel.cs', 'r.crossedOpening = before < openingThresholdLitres && debt >= openingThresholdLitres;', 'r.crossedOpening = debt >= openingThresholdLitres;', 'every draw past the threshold re-opens'),
    ('RM_LedgerKernel.cs', 'if (now - lastOpeningTick < minTicksBetweenOpenings)', 'if (now - lastOpeningTick <= minTicksBetweenOpenings)', 'opening throttle one tick long'),
    ('RM_LedgerKernel.cs', 'lastOpeningTick = now;\n            openingSerial++;', 'openingSerial++;', 'the opening throttle never arms'),
    ('RM_LedgerKernel.cs', 'if (debt >= bandLitres[i])', 'if (debt > bandLitres[i])', 'a band begins one litre late'),
    ('RM_LedgerKernel.cs', 'float hi = Math.Max(1f, maxWeight);', 'float hi = maxWeight;', 'a max weight below 1 would cut the incident odds'),
    ('RM_GaleKernel.cs', 'return (int)Math.Round(deg / 45f) & 7;', 'return (int)Math.Floor(deg / 45f) & 7;', 'the wind index truncates instead of rounding'),
    ('RM_GaleKernel.cs', 'if (!walkable(nx, nz))\n                {\n                    break;', 'if (false)\n                {\n                    break;', 'a carried pawn is blown through walls'),
    ('RM_GaleKernel.cs', 'if (!inBounds(nx, nz))\n                {\n                    r.offMap = true;', 'if (!inBounds(nx, nz))\n                {\n                    r.offMap = false;', 'the edge of the map is not a carry-off'),
    ('RM_GaleKernel.cs', 'int nx = x - wx, nz = z - wz;', 'int nx = x + wx, nz = z + wz;', 'a returning pawn walks further out instead of in'),
    ('RM_GaleKernel.cs', 'return Math.Abs(wx) >= Math.Abs(wz)', 'return Math.Abs(wx) > Math.Abs(wz)', 'a diagonal wind returns from the north/south edge but exits east/west'),
    ('RM_GaleKernel.cs', 'return !(count == 0 || now % CarriedScanInterval != 0);', 'return !(count == 0);', 'the carried book is scanned every tick'),
    ('RM_GaleKernel.cs', 'return returnTick <= now;', 'return returnTick < now;', 'a carried pawn returns a scan late'),
    ('RM_GaleKernel.cs', 'return weight > 0f && allowed && (!needsSkeleton || skeletonAvailable) && (!needsCave || caveFound);', 'return weight > 0f && allowed && (!needsSkeleton || skeletonAvailable);', 'an emergence row that needs a rock face is chosen on open sand'),
    ('RM_SunKernel.cs', 'return Clamp01((float)Math.Sin(elevationDeg * 0.01745329f));', 'return Clamp01((float)Math.Cos(elevationDeg * 0.01745329f));', 'the pinned sun is brightest at the horizon'),
    ('RM_SunKernel.cs', 'if (roofed)\n            {\n                reason = RM_SunReason.Roofed;', 'if (roofed && sun < 0.5f)\n            {\n                reason = RM_SunReason.Roofed;', 'a roof only blocks a low sun'),
    ('RM_SunKernel.cs', 'float sh = Clamp01(shade);', 'float sh = shade;', 'shade is not clamped'),
    ('RM_SunKernel.cs', 'return Math.Max(0.05f, factor) * workSpeedAtFullSun * multiplier;', 'return factor * workSpeedAtFullSun * multiplier;', 'a sun-starved table stops outright instead of crawling'),
    ('RM_SunKernel.cs', 'if (!hasFeed)\n            {\n                return 0f;', 'if (!hasFeed)\n            {\n                return progress;', 'a still keeps its cycle after the feed is taken out'),
    ('RM_SunKernel.cs', 'progress += stepTicks * rate / Math.Max(1, ticksPerCycle);', 'progress += stepTicks / Math.Max(1, ticksPerCycle);', 'the still ignores the sun and the pearl lens'),
    ('RM_SunKernel.cs', 'return Math.Max(1, (int)Math.Round(bodySize * litresPerBodySize));', 'return (int)Math.Round(bodySize * litresPerBodySize);', 'a tiny corpse wrings zero water'),
    ('RM_SunKernel.cs', 'return enabled && !(now - lastBeatTick < beatIntervalTicks) && hasFuel;', 'return enabled && !(now - lastBeatTick <= beatIntervalTicks) && hasFuel;', 'thumper beats one tick apart late'),
    ('RM_SunKernel.cs', 'if (c.distSq <= arriveRadius * arriveRadius)', 'if (c.distSq < arriveRadius * arriveRadius)', 'a swimmer already at the thumper is called again'),
    ('RM_SunKernel.cs', 'i < ordered.Count && called.Count < max', 'i < ordered.Count', 'the thumper calls every swimmer in range'),
    ('RM_SunKernel.cs', 'return glow < minSunGlow ? 0f : Clamp01(glow);', 'return Clamp01(glow);', 'the beam works in a dim sun'),
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
