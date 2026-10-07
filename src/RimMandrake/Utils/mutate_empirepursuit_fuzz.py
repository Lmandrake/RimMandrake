#!/usr/bin/env python3
"""Mutation proof for the EmpirePursuit fuzz: plants each defect in the ladder kernel (or EmpireLadderMath), demands the
fuzz FAILS, restores the file byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_empirepursuit_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimUtinni/EmpirePursuit/Source/Kernel/EmpireLadderKernel.cs"
MATH = "src/RimUtinni/EmpirePursuit/Source/EmpireLadderMath.cs"
WRAPPER = "selftest_empirepursuit_fuzz.py"

KERNEL_MUTATIONS = [
    ("spacing off by a tick", "if (sinceStoryteller < StorytellerSpacingTicks) return", "if (sinceStoryteller <= StorytellerSpacingTicks) return"),
    ("spacing one day not two", "public const int StorytellerSpacingTicks = 2 * TicksPerDay;", "public const int StorytellerSpacingTicks = 1 * TicksPerDay;"),
    ("fires while terminal", "if (contactLive || terminal) return 0;", "if (contactLive) return 0;"),
    ("fires while a contact is live", "if (contactLive || terminal) return 0;", "if (terminal) return 0;"),
    ("Resolve ignores the floor", "nextRung = EmpireLadderMath.NextRungAfter(firedIndex, empireSucceeded, floor);", "nextRung = EmpireLadderMath.NextRungAfter(firedIndex, empireSucceeded, 0);"),
    ("top success is not terminal", "if (firedIndex >= EmpireLadderMath.TopRung && empireSucceeded) terminal = true;", ""),
    ("failure also climbs", "nextRung = EmpireLadderMath.NextRungAfter(firedIndex, empireSucceeded, floor);", "nextRung = EmpireLadderMath.NextRungAfter(firedIndex, true, floor);"),
    ("Resolve leaves progress behind", "contactStartTick = -1;\n            progressTicks = 0;\n            nextIonTick = -1;", "contactStartTick = -1;\n            nextIonTick = -1;"),
    ("Begin forgets lastLadderFireTick", "aftermathOutcome = null;\n            lastLadderFireTick = now;", "aftermathOutcome = null;"),
    ("disabled cordon still fires", "if (kind == EmpireRungKind.Cordon && !g.cordonEnabled) return false;", ""),
    ("disabled probe still fires", "if (kind == EmpireRungKind.Probe && !g.probesOpen) return false;", ""),
    ("rung table walk stops short", "while (r <= EmpireLadderMath.TopRung)", "while (r < EmpireLadderMath.TopRung)"),
    ("probe success needs > not >=", "if (progressTicks >= successTicks)\n            {\n                visibilityDelta = 8f;\n                lastProbeBlind = false;", "if (progressTicks > successTicks)\n            {\n                visibilityDelta = 8f;\n                lastProbeBlind = false;"),
    ("probe blind flag inverted", "lastProbeBlind = !anyProbeDestroyed;", "lastProbeBlind = anyProbeDestroyed;"),
    ("probe timeout without the extra day", "elapsed > timeoutTicks + TicksPerDay", "elapsed > timeoutTicks"),
    ("spotter timeout >= ", "if (elapsed > timeoutTicks) return ContactOutcome.EmpireFails;\n            return ContactOutcome.Continue;\n        }\n\n        /// <summary>Cordon", "if (elapsed >= timeoutTicks) return ContactOutcome.EmpireFails;\n            return ContactOutcome.Continue;\n        }\n\n        /// <summary>Cordon"),
    ("cordon volley without a standing cordon", "if (standing && nextIonTick > 0 && now >= nextIonTick)", "if (nextIonTick > 0 && now >= nextIonTick)"),
    ("cordon success one check early", "if (elapsed >= successTicks) return ContactOutcome.EmpireSucceeds;", "if (elapsed > successTicks) return ContactOutcome.EmpireSucceeds;"),
    ("aftermath verdict inverted", "return aftermathOutcome != \"Repelled\" ? ContactOutcome.EmpireSucceeds : ContactOutcome.EmpireFails;", "return aftermathOutcome == \"Repelled\" ? ContactOutcome.EmpireSucceeds : ContactOutcome.EmpireFails;"),
    ("bombardment not terminal", "public void BombardmentLanded() { bombardTick = -1; terminal = true; }", "public void BombardmentLanded() { bombardTick = -1; }"),
    ("lower rung ignores the floor", "nextRung = EmpireLadderMath.Clamp(nextRung - Math.Max(0, by), floor);", "nextRung = EmpireLadderMath.Clamp(nextRung - Math.Max(0, by), 0);"),
    ("lower rung keeps terminal", "terminal = terminal && nextRung >= EmpireLadderMath.TopRung;", ""),
    ("lower rung never reports a revival", "revived = wasTerminal && !terminal;", "revived = false;"),
    ("floor can fall", "int v = Math.Max(currentFloor, floor);", "int v = floor;"),
    ("memory ignores the setting", "if (!rememberRungs || !tileValid || !hasEntry) return -1;", "if (!tileValid || !hasEntry) return -1;"),
    ("storyteller block ignores live contact", "return contactLive || now - lastLadderFireTick < StorytellerSpacingTicks;", "return now - lastLadderFireTick < StorytellerSpacingTicks;"),
    ("timer floor under an hour", "raidTimer = now + Math.Max((int)Math.Round(raw * factor), TickInterval);", "raidTimer = now + (int)Math.Round(raw * factor);"),
    ("warning after the raid", "? Math.Max(now + TickInterval, raidTimer - (int)Math.Round(warningHours * TicksPerHour))", "? Math.Max(now + TickInterval, raidTimer + (int)Math.Round(warningHours * TicksPerHour))"),
    ("tick rounding floors", "return (timer + TickInterval - 1) / TickInterval * TickInterval;", "return timer / TickInterval * TickInterval;"),
    ("warn fires with the raid", "&& now == warnTick && warnTick != raidTick;", "&& now == warnTick;"),
    ("EnsureInit re-rolls", "if (nextRung >= 0) return;\n            nextRung = EmpireLadderMath.StartingRung", "nextRung = EmpireLadderMath.StartingRung"),
]
MATH_MUTATIONS = [
    ("60% rule 50%", "return deadOrDowned >= (int)Math.Ceiling(raiders * 0.6);", "return deadOrDowned >= (int)Math.Ceiling(raiders * 0.5);"),
    ("climb past the top", "if (rung > TopRung) rung = TopRung;", ""),
    ("decay rounds up", "(int)Math.Floor(seasonsAway)", "(int)Math.Ceiling(seasonsAway)"),
    ("starting rung ignores a remembered tile", "if (remembered > start) start = remembered;", ""),
]

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rc = run_mutations(KERNEL, WRAPPER, KERNEL_MUTATIONS, only)
    rc |= run_mutations(MATH, WRAPPER, MATH_MUTATIONS, only)
    sys.exit(rc)
