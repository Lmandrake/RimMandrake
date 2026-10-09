#!/usr/bin/env python3
"""Planted-defect selftest for lint_sacredgraffiti_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_sacredgraffiti_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack_lint_harness as H  # noqa: E402

M = "Defs/SacredMarks.xml"
R = "Defs/RitualOutcomeEffects.xml"
S = "Source/RM_SacredGraffitiMod.cs"
PLANTS = [
    ("worker class typo", R, "RimMandrake.SacredGraffiti.RitualOutcomeEffectWorker_PlaceSacredMark</workerClass>", "RimMandrake.SacredGraffiti.RitualOutcomeEffectWorker_PlaceSacredMar</workerClass>", "class-resolves"),
    ("stale category name", M, "<category>Devotional</category>", "<category>Sacred</category>", "sacredgraffiti-marks"),
    ("god that is not in the Ninefold", M, "<godSatiationHook>Ishko</godSatiationHook>", "<godSatiationHook>Ishka</godSatiationHook>", "sacredgraffiti-marks"),
    ("viewer thought undefined", M, "<viewerReactionThought>RM_ViewedSacredMark_Ishko</viewerReactionThought>", "<viewerReactionThought>RM_ViewedSacredMark_Ishka</viewerReactionThought>", "sacredgraffiti-marks"),
    ("mark with no graffiti parent", M, 'ParentName="RM_BaseGraffiti"', 'ParentName="RM_BaseGraffit"', "sacredgraffiti-marks"),
    ("mark that burns", M, "<Flammability>0</Flammability>", "<Flammability>0.5</Flammability>", "sacredgraffiti-marks"),
    ("devotional mark that is ugly", M, "<Beauty>6</Beauty>", "<Beauty>-3</Beauty>", "sacredgraffiti-marks"),
    ("texture path with no png", M, "SacredMark/SacredMark_Ishko", "SacredMark/SacredMark_Ishk", "sacredgraffiti-marks"),
    ("quality roll on a livery mark", M, "<supportsQuality>false</supportsQuality>", "<supportsQuality>true</supportsQuality>", "sacredgraffiti-marks"),
    ("ritual spawns a def that is not a mark", R, "<filthDefToSpawn>RM_SacredMark_Ishko</filthDefToSpawn>", "<filthDefToSpawn>Filth_Dirt</filthDefToSpawn>", "sacredgraffiti-marks"),
    ("zero marks per ritual", R, "<filthCountToSpawn>1~1</filthCountToSpawn>", "<filthCountToSpawn>0~1</filthCountToSpawn>", "sacredgraffiti-marks"),
    ("outcome chances do not sum to one", R, "<chance>0.6</chance>", "<chance>0.7</chance>", "sacredgraffiti-marks"),
    ("no positive outcome", R, "<positivityIndex>1</positivityIndex>", "<positivityIndex>-1</positivityIndex>", "sacredgraffiti-marks"),
    ("settings key differs from field", S, 'Scribe_Values.Look(ref markCountMultiplier, "markCountMultiplier", 1f);', 'Scribe_Values.Look(ref markCountMultiplier, "markMult", 1f);', "settings-scribed"),
    ("setting never saved", S, '            Scribe_Values.Look(ref sacredMarkEnabled, "sacredMarkEnabled", true);\n', "", "settings-scribed"),
    ("a source file missing from the csproj", "Source/SacredGraffiti.csproj", '    <Compile Include="RM_SacredGraffitiMod.cs" />\n', "", "compile-listed"),
]

if __name__ == "__main__":
    sys.exit(H.run("SacredGraffiti", "lint_sacredgraffiti_defs.py", PLANTS, keep=("Textures",)))
