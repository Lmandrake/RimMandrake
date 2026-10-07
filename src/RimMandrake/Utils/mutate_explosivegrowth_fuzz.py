#!/usr/bin/env python3
"""Mutation proof for the ExplosiveGrowth fuzz (and the engine the other three validation mutators import).

Plants each defect in the production kernel, waits (winbuild's stale-DLL trap: >= 4 s between a mutation and its run),
runs the fuzz wrapper, demands a FAIL, restores the file byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_explosivegrowth_fuzz.py [name-substring]
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def run_mutations(kernel_rel, wrapper, mutations, only=None):
    kernel = os.path.join(REPO, kernel_rel)
    orig = open(kernel, "rb").read()
    text = orig.decode("utf-8")
    caught, missed = 0, []
    try:
        for name, old, new in mutations:
            if only and only not in name:
                continue
            if text.count(old) < 1:
                print("MUTATION TARGET NOT FOUND:", name)
                missed.append(name + " (target missing)")
                continue
            open(kernel, "wb").write(text.replace(old, new, 1).encode("utf-8"))
            time.sleep(5)
            os.utime(kernel, None)
            p = subprocess.run([sys.executable, os.path.join(HERE, wrapper)], capture_output=True, text=True)
            out = p.stdout + p.stderr
            built = "Build succeeded" in out or "fuzz " in out
            if p.returncode != 0 and built and "FAIL" in out and "error CS" not in out:
                first = [l for l in out.splitlines() if l.startswith("FAIL")][:1]
                print("CAUGHT  %-34s %s" % (name, (first[0][:110] if first else "")))
                caught += 1
            else:
                print("MISSED  %-34s rc=%s built=%s" % (name, p.returncode, built))
                missed.append(name)
    finally:
        open(kernel, "wb").write(orig)
        time.sleep(5)            # rsync --modify-window=2: a restore inside 2 s of the last mutation would be skipped (stale staged copy)
        os.utime(kernel, None)
    print("%d caught, %d missed; kernel restored" % (caught, len(missed)))
    return 0 if not missed else 1


MUTATIONS = [
    ("StepCharge dormant decays", "if (wet) return charge;", "if (wet) return charge - dt / (chargeTicks * 0.5f);"),
    ("StepCharge dry decays at wet rate", "return charge - dt / (chargeTicks * 0.5f);", "return charge - dt / chargeTicks;"),
    ("Suppress keeps the soak", "                soakUntil.Remove(c);\n            }\n        }\n\n        public float GrowthFactor", "            }\n        }\n\n        public float GrowthFactor"),
    ("TrySoak ignores suppression", "if (IsSuppressed(c, now)) return false;\n            int until = now + Math.Max(1, ticks);\n            int prior;\n            if (!soakUntil", "int until = now + Math.Max(1, ticks);\n            int prior;\n            if (!soakUntil"),
    ("TrySoak shortens an existing soak", "|| prior < until) soakUntil[c] = until;\n            return true;", "|| true) soakUntil[c] = until;\n            return true;"),
    ("arm without GrowthRate>0", "if (!charges.ContainsKey(c) && sink.GrowthRate(c) > 0f)", "if (!charges.ContainsKey(c))"),
    ("arm an immature plant", "if (growth < RM_ExplosiveGrowthKernel.MatureGrowth)", "if (growth < 0.5f)"),
    ("stale plant id kept", "id != rec.plantId)\n                    {\n                        charges.Remove(c);", "false)\n                    {\n                        charges.Remove(c);"),
    ("fire leaves the record", "charges.Remove(c);\n                        sink.OnFire(c);", "sink.OnFire(c);"),
    ("StageFor Hue threshold >", "charge >= HueAt ? RM_TellStage.Hue", "charge > HueAt ? RM_TellStage.Hue"),
    ("Hue floors instead of ceils", "return (float)Math.Ceiling(h * 4f) / 4f;", "return (float)Math.Floor(h * 4f) / 4f;"),
    ("slice off by one", "end = Math.Min(n, start + slice);", "end = Math.Min(n, start + slice + 1);"),
    ("surge band excludes its edge", "return !(salinity < SurgeFreshMin || salinity > SurgeFreshMax);", "return !(salinity <= SurgeFreshMin || salinity > SurgeFreshMax);"),
    ("EffectiveTop Tinder falls to None", "case 3: return tinder ? top : fallback;", "case 3: return tinder ? top : (byte)6;"),
    ("prune keeps entries due now", "if (kv.Value <= now) tmp.Add(kv.Key);", "if (kv.Value < now) tmp.Add(kv.Key);"),
    ("GrowthFactor ignores the plant", "if (!plantSoaks) return 1f;", ""),
    ("PassDelta unclamped", "Math.Min(Math.Max(now - lastPassTick, 1), PassInterval * 8)", "Math.Max(now - lastPassTick, 1)"),
]

if __name__ == "__main__":
    sys.exit(run_mutations("src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs",
                           "selftest_explosivegrowth_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
