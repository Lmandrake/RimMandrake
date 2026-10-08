#!/usr/bin/env python3
"""Mutation proof for the LoreStages fuzz: plants each defect in the kernel (RM_LoreStageKernel.cs), the applier (LoreStageApplier.cs) and
the table def (RM_LoreStageTableDef.cs), demands the fuzz FAILS, restores each file byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_lorestages_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

B = "src/RimMandrake/LoreStages/Source/"
KERNEL = B + "Kernel/RM_LoreStageKernel.cs"
APPLIER = B + "LoreStageApplier.cs"
TABLE = B + "RM_LoreStageTableDef.cs"
KERNEL_MUTATIONS = [
    ("rung at the stage excluded", "if (rungStages[i] <= stage && rungStages[i] > bestStage)", "if (rungStages[i] < stage && rungStages[i] > bestStage)"),
    ("rung above the stage shown", "if (rungStages[i] <= stage && rungStages[i] > bestStage)", "if (rungStages[i] > bestStage)"),
    ("lowest rung wins", "rungStages[i] > bestStage", "rungStages[i] < bestStage || bestStage == int.MinValue"),
    ("last of a tie wins", "rungStages[i] > bestStage", "rungStages[i] >= bestStage"),
    ("text-less rung shown", "if (!hasText[i]) continue;", ""),
    ("no rung gives rung 0", "int best = -1;\n            int bestStage", "int best = rungStages.Count > 0 ? 0 : -1;\n            int bestStage"),
    ("clamp above max dropped", "if (maxStage > 0 && stage > maxStage) stage = maxStage;", ""),
    ("clamp applies at max 0", "if (maxStage > 0 && stage > maxStage) stage = maxStage;", "if (stage > maxStage) stage = maxStage;"),
    ("clamp below zero dropped", "if (stage < 0) stage = 0;", ""),
    ("toggle inverted", "return stagedTextEnabled ? storedStage : 0;", "return stagedTextEnabled ? 0 : storedStage;"),
    ("toggle off keeps stage", "return stagedTextEnabled ? storedStage : 0;", "return storedStage;"),
    ("ladder key ignores the id", "return string.IsNullOrEmpty(ladderId) ? defName : ladderId;", "return defName;"),
    ("ladder key inverted", "return string.IsNullOrEmpty(ladderId) ? defName : ladderId;", "return string.IsNullOrEmpty(ladderId) ? ladderId : defName;"),
    ("duplicate rung unreported", "if (!seen.Add(rungStages[i])) found.Add", "if (seen.Add(rungStages[i]) && false) found.Add"),
    ("negative rung unreported", "if (rungStages[i] < 0) found.Add", "if (rungStages[i] < -1) found.Add"),
    ("unreachable rung unreported", "if (maxStage > 0 && rungStages[i] > maxStage) found.Add", "if (maxStage > 0 && rungStages[i] > maxStage + 1) found.Add"),
    ("text-less rung unreported", "if (!hasText[i]) found.Add", "if (false) found.Add"),
]
APPLIER_MUTATIONS = [
    ("pass 1 reset dropped", "b.field.SetValue(b.def, b.pristine);\n                touched.Add(b.def);", "touched.Add(b.def);"),
    ("pass 1 forgets to touch", "b.field.SetValue(b.def, b.pristine);\n                touched.Add(b.def);", "b.field.SetValue(b.def, b.pristine);"),
    ("ladder with nothing to say erases another's text", "if (pick < 0) continue;", "if (pick < 0) { fi.SetValue(def, baseline.pristine); touched.Add(def); continue; }"),
    ("staged def not touched", "fi.SetValue(def, target.stages[pick].text);\n                    touched.Add(def);", "fi.SetValue(def, target.stages[pick].text);"),
    ("staged count dropped", "touched.Add(def);\n                    applied++;", "touched.Add(def);"),
    ("wrong rung text", "fi.SetValue(def, target.stages[pick].text);", "fi.SetValue(def, target.stages[0].text);"),
    ("stage read from the def name", "int stage = stageOf(table.LadderId);", "int stage = stageOf(table.defName);"),
    ("thing cache not cleared", "ThingDefDetailedCache.SetValue(def, null);", ""),
    ("hediff cache not cleared", "HediffDefDescriptionCache.SetValue(def, null);", ""),
    ("cache pass skipped", "foreach (Def def in touched)\n            {\n                ClearStaleCaches(def);\n            }", ""),
    ("baseline key ignores the field", "+ \"|\" + target.field;", ";"),
    ("baseline recaptured every time", "if (!Baselines.TryGetValue(key, out Baseline baseline))", "Baseline baseline;\n                    if (true)"),
    ("non-string fields accepted", "if (fi == null || fi.FieldType != typeof(string))", "if (fi == null)"),
    ("missing def warns every time", "private static void WarnOnce(Action<string> warn, string key, string message)\n        {\n            if (WarnedKeys.Add(key))", "private static void WarnOnce(Action<string> warn, string key, string message)\n        {\n            if (true)"),
    ("incomplete target accepted", "if (target.defType.NullOrEmpty() || target.defName.NullOrEmpty() || target.field.NullOrEmpty())", "if (target.defType.NullOrEmpty() || target.field.NullOrEmpty())"),
    ("null table crashes", "if (table?.targets == null) continue;", "if (table.targets == null) continue;"),
]
TABLE_MUTATIONS = [
    ("config: null target not guarded", "if (t == null)\n                {", "if (false)\n                {"),
    ("config: no-stages not reported", "if (t.stages == null || t.stages.Count == 0)\n                {", "if (t.stages == null)\n                {"),
    ("config: duplicate message lost", "duplicate stage {s.stage}", "repeat {s.stage}"),
    ("config: unreachable message lost", "is above maxStage {maxStage}", "is high {maxStage}"),
    ("config: ladder id fallback gone", "RM_LoreStageKernel.LadderKey(ladderId, defName)", "ladderId"),
]

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rc = 0
    for f, muts in ((KERNEL, KERNEL_MUTATIONS), (APPLIER, APPLIER_MUTATIONS), (TABLE, TABLE_MUTATIONS)):
        rc |= run_mutations(f, "selftest_lorestages_fuzz.py", muts, only)
    sys.exit(rc)
