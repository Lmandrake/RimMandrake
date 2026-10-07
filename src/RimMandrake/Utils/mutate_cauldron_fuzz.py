#!/usr/bin/env python3
"""Planted-bug check for the Cauldron fuzz: plants one defect at a time in a production kernel, runs
selftest_cauldron_fuzz.py, and requires it to FAIL; always restores the kernel byte-identical (and verifies it).

    python3 src/RimMandrake/Utils/mutate_cauldron_fuzz.py [N]      # N = only mutation number N (1-based)

Each mutation waits >=4 s before its run: winbuild's staged build can reuse a stale copy otherwise.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(os.path.dirname(HERE), "Cauldron", "Source", "Kernel")
FUZZ = os.path.join(HERE, "selftest_cauldron_fuzz.py")

MUTATIONS = [
    ("RM_VentKernel.cs", "if (silencedUntil < 0) return 1f;", "if (silencedUntil < 0) return 0f;", "a never-silenced vent has no output"),
    ("RM_VentKernel.cs", "return silencedUntil >= 0 && now < silencedUntil;", "return silencedUntil >= 0 && now <= silencedUntil;", "silence lasts one tick too long"),
    ("RM_VentKernel.cs", "return curIsBloom && !ApproximatelyOne(lerp);", "return curIsBloom;", "a vent falters through the whole bloom"),
    ("RM_VentKernel.cs", "if (faltering) return falterOutput;\n", "", "a matching weather row beats the hush before a bloom"),
    ("RM_VentKernel.cs", "if (!bloomSeen) { bloomSeen = true; lastBlowoutTick = now; }", "{ bloomSeen = true; lastBlowoutTick = now; }", "every bloom tick counts as a fresh blowout"),
    ("RM_VentKernel.cs", "return now - lastBlowoutTick < window;", "return now - lastBlowoutTick <= window;", "a blowout is recent one tick longer"),
    ("RM_VentKernel.cs", "t == RM_VentTemperament.Stable && !recentlyBlewOut;", "t == RM_VentTemperament.Stable;", "a stable ring vent that just blew out stays in the stable ring"),
    ("RM_VentKernel.cs", "if (suppression < 1f) return false;", "if (suppression <= 1f) return false;", "the meter needs to pass 1 rather than reach it"),
    ("RM_VentKernel.cs", "now + (int)Math.Round(silenceDays * jitter * 60000f)", "now + (int)Math.Round(silenceDays * 60000f)", "silence ignores its jitter"),
    ("RM_VentKernel.cs", "Math.Max(0f, suppression - 250f * decayPerDay / 60000f)", "Math.Max(0f, suppression - 250f * decayPerDay / 6000f)", "suppression decays ten times too fast"),
    ("RM_VentKernel.cs", "public const float ExposureFloor = 0.1f;", "public const float ExposureFloor = 0.2f;", "the far-from-every-vent floor is 0.2"),
    ("RM_VentKernel.cs", "best = Math.Max(best, Proximity(distances[i]) * recoveries[i]);", "best += Proximity(distances[i]) * recoveries[i];", "exposure sums vents instead of taking the best"),
    ("RM_VentKernel.cs", "return Math.Min(MaxVents, Math.Max(MinVents, n));", "return Math.Min(MaxVents, n);", "a small map can get fewer than 2 vents"),
    ("RM_VentKernel.cs", "if (!stable) temps[0] = RM_VentTemperament.Stable;", "", "a map of only leaking vents"),
    ("RM_VentKernel.cs", "if (silenced[i] || output[i] <= 0.05f) continue;", "if (silenced[i] || output[i] < 0.05f) continue;", "a vexxiss drinks a vent that is barely breathing"),
    ("RM_VentKernel.cs", "if (now < nextDrinkTick) return false;", "if (now <= nextDrinkTick) return false;", "drink cooldown one tick long"),
    ("RM_YieldKernel.cs", "if (growth < harvestMinGrowth) return 0f;", "if (growth <= harvestMinGrowth) return 0f;", "a trunk at exactly its minimum growth yields nothing"),
    ("RM_YieldKernel.cs", "return frac >= 0.95f ? 3 :", "return frac >= 0.9f ? 3 :", "lode grade starts at 90%"),
    ("RM_YieldKernel.cs", "if (frac >= heavyFrom) return hasHeavy ? RM_AssayBand.Heavy : hasLight ? RM_AssayBand.Light : RM_AssayBand.None;", "if (frac >= heavyFrom) return hasHeavy ? RM_AssayBand.Heavy : RM_AssayBand.None;", "a heavy tree with no heavy art shows nothing instead of the light overlay"),
    ("RM_YieldKernel.cs", "amount *= Math.Max(1f - toxicResistance, 0f);", "amount *= 1f - toxicResistance;", "toxic resistance above 1 makes a negative dose"),
    ("RM_YieldKernel.cs", "if (animal && nativeAnimal) return false;", "", "native fauna take the vent bloom's metal load"),
    ("RM_YieldKernel.cs", "return density > 0f && existing < cap;", "return density > 0f && existing <= cap;", "one bead over the cap"),
    ("RM_YieldKernel.cs", "return initialised && dew != lastDew;", "return dew != lastDew;", "the first tick after load counts as a weather flip"),
    ("RM_YieldKernel.cs", "if (home) return false;\n            return !hasRoom", "return !hasRoom", "dew beads in the home area"),
    ("RM_YieldKernel.cs", "return !onNamedTerrain && anyNeighbourNamed;", "return anyNeighbourNamed;", "the water itself counts as its own shore"),
    ("RM_VexxissKernel.cs", "if (ByCell.TryGetValue(cellOf(e), out E cur) && ReferenceEquals(cur, e))", "if (ByCell.TryGetValue(cellOf(e), out E cur))", "an old print clears a newer print's grid cell"),
    ("RM_VexxissKernel.cs", "expiresOf(Entries[0]) <= now", "expiresOf(Entries[0]) < now", "a print lives one tick past its expiry"),
    ("RM_VexxissKernel.cs", "while (Entries.Count > maxEntries)", "while (Entries.Count >= maxEntries)", "the ledger holds one fewer than its cap"),
    ("RM_VexxissKernel.cs", "return !lastValid || !(distSq < stepCells * stepCells);", "return !lastValid || !(distSq <= stepCells * stepCells);", "a print needs more than the step distance"),
    ("RM_VexxissKernel.cs", "if (distSq > chaseRadius * chaseRadius) return false;", "if (distSq >= chaseRadius * chaseRadius) return false;", "an igniter at exactly the chase radius is ignored"),
    ("RM_VexxissKernel.cs", "if (attacksIgniterSetting && igniterAttackable) return WardChoice.AttackIgniter;", "if (igniterAttackable) return WardChoice.AttackIgniter;", "the attack-the-igniter setting is ignored"),
    ("RM_VexxissKernel.cs", "return !(now - lastLetterTick < cooldownTicks);", "return !(now - lastLetterTick <= cooldownTicks);", "the poisoned-water letter cooldown is one tick long"),
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
