#!/usr/bin/env python3
"""Mutation proof for the WreckedMachines fuzz: plants each defect in the kernel (RM_WreckedMachinesKernel.cs), demands the fuzz FAILS,
restores the file byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_wreckedmachines_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

# Equivalent mutant (not listed): dropping the Wrecked early return in EmanatorStage - min(grade - 1, top) is already -1 for grade 0.
KERNEL = "src/RimMandrake/WreckedMachines/Source/Kernel/RM_WreckedMachinesKernel.cs"
MUTATIONS = [
    ("refurbished can reach the original", "float r = Clamp(refurbished, 0f, RefurbishedMax);", "float r = Math.Max(0f, refurbished);"),
    ("refurbished below zero", "float r = Clamp(refurbished, 0f, RefurbishedMax);", "float r = Math.Min(refurbished, RefurbishedMax);"),
    ("kludged may exceed refurbished", "float k = Math.Min(Clamp(kludged, 0f, KludgedMax), r);", "float k = Clamp(kludged, 0f, KludgedMax);"),
    ("kludged slider range ignored", "float k = Math.Min(Clamp(kludged, 0f, KludgedMax), r);", "float k = Math.Min(Math.Max(0f, kludged), r);"),
    ("wrecked may exceed kludged", "float w = Math.Min(Clamp(wrecked, 0f, WreckedMax), k);", "float w = Clamp(wrecked, 0f, WreckedMax);"),
    ("wrecked slider range ignored", "float w = Math.Min(Clamp(wrecked, 0f, WreckedMax), k);", "float w = Math.Min(Math.Max(0f, wrecked), k);"),
    ("refurbished max 1.0", "RefurbishedMax = 0.95f", "RefurbishedMax = 1f"),
    ("kludged max 0.9", "KludgedMax = 0.6f", "KludgedMax = 0.9f"),
    ("wrecked max 0.2", "WreckedMax = 0.05f", "WreckedMax = 0.2f"),
    ("original is not exactly 1", "default: return 1f;", "default: return 0.99f;"),
    ("ratios mixed up", "case Kludged: return l.kludged;", "case Kludged: return l.refurbished;"),
    ("wrecked ratio mixed up", "case Wrecked: return l.wrecked;", "case Wrecked: return l.kludged;"),
    ("upper grade built on open ground", "return false;\n        }\n\n        /// <summary>Soothe stage", "return true;\n        }\n\n        /// <summary>Soothe stage"),
    ("any line counts as underneath", "if (otherLines[i] == line && otherGrades[i] < grade) return true;", "if (otherGrades[i] < grade) return true;"),
    ("equal grade counts as lower", "if (otherLines[i] == line && otherGrades[i] < grade) return true;", "if (otherLines[i] == line && otherGrades[i] <= grade) return true;"),
    ("higher grade counts as lower", "if (otherLines[i] == line && otherGrades[i] < grade) return true;", "if (otherLines[i] == line) return true;"),
    ("reinstall refused", "if (!requireLowerGrade || isReinstall) return true;", "if (!requireLowerGrade) return true;"),
    ("setting off still refuses", "if (!requireLowerGrade || isReinstall) return true;", "if (isReinstall) return true;"),
    ("wrecked refused", "if (!hasGradeExtension || grade == Wrecked) return true;", "if (!hasGradeExtension) return true;"),
    ("unlabelled def refused", "if (!hasGradeExtension || grade == Wrecked) return true;", "if (grade == Wrecked) return true;"),
    ("emanator stage not capped", "return Math.Min(grade - 1, stageCount - 1);", "return grade - 1;"),
    ("emanator stage off by one", "return Math.Min(grade - 1, stageCount - 1);", "return Math.Min(grade, stageCount - 1);"),
    ("consumer draw rewritten", "if (originalBase >= 0f) return null;", "if (originalBase > 0f) return null;"),
    ("producer left unscaled", "return originalBase * ratio;", "return originalBase;"),
    ("output scaled by the wrong sign", "return originalBase * ratio;", "return -originalBase * ratio;"),
    ("mood ignores the ratio", "return vanillaBaseMood * ratio;", "return vanillaBaseMood;"),
    ("material count can reach zero", "return Math.Max(1, (int)Math.Round(baseCount * factor));", "return (int)Math.Round(baseCount * factor);"),
    ("material count rounds up", "(int)Math.Round(baseCount * factor)", "(int)Math.Ceiling(baseCount * factor)"),
    ("research cost can reach zero", "return Math.Max(1f, baseCost * factor);", "return baseCost * factor;"),
    ("research ignores the factor", "return Math.Max(1f, baseCost * factor);", "return Math.Max(1f, baseCost);"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_wreckedmachines_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
