#!/usr/bin/env python3
"""Planted-bug check for the TheForge fuzz: plants one defect at a time in a production kernel, runs
selftest_theforge_fuzz.py, and requires it to FAIL; always restores the kernel byte-identical (and verifies it).

    python3 src/RimMandrake/Utils/mutate_theforge_fuzz.py [N]      # N = only mutation number N (1-based)

Each mutation waits >=4 s before its run: winbuild's staged build can reuse a stale copy otherwise.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(os.path.dirname(HERE), "TheForge", "Source", "Kernel")
FUZZ = os.path.join(HERE, "selftest_theforge_fuzz.py")

MUTATIONS = [
    ("RM_CycleKernel.cs", "return frozenCount > 0 ? ForgeCyclePhase.Growth : ForgeCyclePhase.StillHeat;", "return ForgeCyclePhase.Growth;", "an empty freeze still runs growth, cracks and melt"),
    ("RM_CycleKernel.cs", "leaving == ForgeCyclePhase.Melt;", "leaving == ForgeCyclePhase.Freeze;", "the freeze is counted as the closed cycle"),
    ("RM_CycleKernel.cs", "return now + Math.Max(CycleInterval, (int)Math.Round(hoursRolled * TicksPerHour));", "return now + (int)Math.Round(hoursRolled * TicksPerHour);", "no one-step floor on a phase"),
    ("RM_CycleKernel.cs", "phaseEndTick - now <= leadHours * TicksPerHour", "phaseEndTick - now < leadHours * TicksPerHour", "hiss lands a tick late"),
    ("RM_CycleKernel.cs", "return now + (wavesLeft > 0 ? span / (wavesLeft + 1) : span);", "return now + span;", "every wave after the first waits for the phase end"),
    ("RM_CycleKernel.cs", "return Math.Max(1, (int)Math.Ceiling(remaining / (float)batchesLeft));", "return Math.Max(1, (int)Math.Floor(remaining / (float)batchesLeft));", "batch rounds down and the queue outlives its share"),
    ("RM_CycleKernel.cs", "int room = Math.Max(0, maxFrozen - frozen.Count);", "int room = int.MaxValue;", "the freeze ignores its cell cap"),
    ("RM_CycleKernel.cs", "if (!isOurs(c)) continue;", "", "the melt strips someone else's temp terrain"),
    ("RM_CycleKernel.cs", "                frozen.Remove(c);\n", "", "melted cells stay in the frozen set"),
    ("RM_CycleKernel.cs", "if (!needsCrack(c)) continue;", "", "cracking overwrites foreign terrain"),
    ("RM_CycleKernel.cs", "int n = Math.Min(Queue.Count, batch);", "int n = Queue.Count;", "the gentle melt-back ignores its batch limit"),
    ("RM_CycleKernel.cs", "return cycleActive && pulseGateOpen;", "return cycleActive;", "the pulse gate is ignored by the cycle"),
    ("RM_PlumeKernel.cs", "cx >= width || cz >= height", "cx > width || cz >= height", "a front survives one cell past the east edge"),
    ("RM_PlumeKernel.cs", "ExpiryTicks = StepTicks * 3;", "ExpiryTicks = StepTicks * 2;", "plume cells expire a step early"),
    ("RM_PlumeKernel.cs", "Expiry.TryGetValue(cell, out int exp) && exp >= now;", "Expiry.TryGetValue(cell, out int exp) && exp > now;", "a plume cell expires on its last tick"),
    ("RM_PlumeKernel.cs", "if (kv.Value < now) dead.Add(kv.Key);", "if (kv.Value <= now) dead.Add(kv.Key);", "prune removes an entry still live this tick"),
    ("RM_PlumeKernel.cs", "return enabled && liveFronts < MaxFronts;", "return enabled && liveFronts <= MaxFronts;", "a sixth front"),
    ("RM_DhokkurKernel.cs", "now - last < cooldownTicks) return false;", "now - last <= cooldownTicks) return false;", "wear cooldown one tick long"),
    ("RM_DhokkurKernel.cs", "if (now - last < periodTicks) continue;", "if (now - last <= periodTicks) continue;", "fade waits one tick extra"),
    ("RM_DhokkurKernel.cs", "if (w < RM_DhokkurKernel.Passes(passesSetting) && isPolished(i))", "if (w <= RM_DhokkurKernel.Passes(passesSetting) && isPolished(i))", "a track un-polishes one pass early"),
    ("RM_DhokkurKernel.cs", "if (!sealedNow && rainingNow) return DhokkurTransition.Wake;", "if (rainingNow) return DhokkurTransition.Wake;", "a dhokkur that just sealed 'wakes' in the rain"),
    ("RM_DhokkurKernel.cs", "if (mode <= 1 && minifiable && minify())", "if (mode <= 0 && minifiable && minify())", "minify-first mode never minifies"),
    ("RM_DormancyKernel.cs", "now - s.awakeSinceTick < minAwakeHours * TicksPerHour", "now - s.awakeSinceTick <= minAwakeHours * TicksPerHour", "a woken pawn re-seals one check late"),
    ("RM_DormancyKernel.cs", "left <= slowFinalHours * TicksPerHour;", "left < slowFinalHours * TicksPerHour;", "slowing starts a tick late"),
    ("RM_DormancyKernel.cs", "f = slowFactor + (1f - slowFactor) * t;", "f = 1f + (slowFactor - 1f) * t;", "the scuttle speeds up toward the end of the run"),
    ("RM_DormancyKernel.cs", "if (!first) e |= VoiceEvent.Stinger;", "e |= VoiceEvent.Stinger;", "the very first frame plays a stinger"),
    ("RM_DormancyKernel.cs", "if (awakeDuringFlashWindow && flashWindowOpen) return flashEnd;\n            if (awakeDuringRain && cycleActiveAndRaining) return phaseEnd;", "if (awakeDuringRain && cycleActiveAndRaining) return phaseEnd;\n            if (awakeDuringFlashWindow && flashWindowOpen) return flashEnd;", "run end prefers the rain over the flash window"),
    ("RM_SkyKernel.cs", "return !(dist < min || dist > max);", "return dist > min && dist < max;", "the stoop band edges are exclusive"),
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
