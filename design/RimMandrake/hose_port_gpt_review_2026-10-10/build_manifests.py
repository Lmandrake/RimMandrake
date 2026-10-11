#!/usr/bin/env python3
"""Write one manifest per consult (repo-relative paths) and print sizes. Every FlowWorks
source/def/patch/About/validation/northstar file lands in exactly one consult; the v2 design
and its review ride in all of them. Re-run from the repo root."""
import glob, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
os.chdir(ROOT)
OUT = Path(__file__).parent
S = "src/RimMandrake/"
FW = S + "FlowWorks/"
GSS = S + "GimmeSomeSlack/"
def g(*pats):
    r = []
    for p in pats:
        r += sorted(x for x in glob.glob(p, recursive=True)
                    if os.path.isfile(x) and "/bin/" not in x and "/obj/" not in x and "__pycache__" not in x)
    return r
COMMON = ["design/RimMandrake/hose_port_to_flowworks_design_v2_2026-10-10.md",
          "design/RimMandrake/hose_port_to_flowworks_review_2026-10-10.md"]
fw_all = set(g(FW+"Source/**/*.cs", FW+"Source/**/*.csproj", FW+"Defs/**/*.xml", FW+"Patches/**/*.xml",
               FW+"About/*.xml", FW+"Languages/**/*.xml", FW+"validation*.py", FW+"northstar/*.py"))
c = {}
c["C1_flow_and_hose"] = COMMON + ["design/RimMandrake/liquids_framework_design.md"] + g(
    GSS+"Source/Hose/**/*.cs", GSS+"Defs/Hose/*.xml",
    FW+"Source/Machinery/**/*.cs", FW+"Source/LiquidTypes/**/*.cs", FW+"Source/RM_PumpMath.cs",
    FW+"Defs/Machinery/**/*.xml", FW+"Defs/LiquidTypes/LiquidDefs/*.xml")
c["C2_settings_save_deps_tests"] = COMMON + g(
    FW+"Source/RimMandrakeFlowWorksMod.cs", FW+"Source/RimMandrakeFlowWorks_DefOf.cs", FW+"Source/RM_Patch_SuperdeepShooting.cs",
    FW+"Source/*.csproj", FW+"Source/SelfTest/*.csproj", FW+"Source/SelfTest/*.cs", FW+"Source/Debug/*.cs",
    FW+"About/*.xml", FW+"Languages/**/*.xml",
    S+"_Shared/HarmonyResilience/*.cs", S+"_Shared/SettingsKit/*.cs", S+"EnvironmentalHazards/Source/RM_DefAliases.cs",
    GSS+"Source/GimmeSomeSlackMod.cs", GSS+"Source/CordMaterials.cs", GSS+"Source/Core/LegacyName.cs",
    GSS+"Source/Core/DrawOrder.cs", GSS+"Source/Core/CordMath.cs", GSS+"Source/Core/CordWorld.cs",
    GSS+"Source/Core/CordPlanner.cs", GSS+"Source/Core/CordLayer.cs", GSS+"Source/Aerial/StylePicker.cs",
    GSS+"Source/Aerial/AerialStyles.cs", GSS+"Source/*.csproj", GSS+"Source/SelfTest/*.csproj",
    GSS+"Source/SelfTest/HoseSelfTest.cs", GSS+"Source/SelfTest/HoseCarryChecks.cs", GSS+"Source/SelfTest/HoseLiveChecks.cs",
    GSS+"About/About.xml")
used = set(x for k in c for x in c[k])
rest_root = [x for x in g(FW+"Source/*.cs") if x not in used]
c["C3_flowworks_root_source"] = COMMON + rest_root + g(FW+"Patches/**/*.xml")
used = set(x for k in c for x in c[k])
c["C4_flowworks_subsystems_defs"] = COMMON + [x for x in g(FW+"Source/**/*.cs", FW+"Defs/**/*.xml") if x not in used]
used = set(x for k in c for x in c[k])
c["C5_harness"] = COMMON + g(FW+"validation*.py", FW+"northstar/*.py", GSS+"validation_hose.py",
                             GSS+"validation_style_hose.py", GSS+"northstar/proof_all.py")
used = set(x for k in c for x in c[k])
missing = sorted(fw_all - used)
for k, files in c.items():
    (OUT / ("%s.files.txt" % k)).write_text("\n".join(files) + "\n")
    print("%-32s %3d files %8d chars" % (k, len(files), sum(os.path.getsize(f) for f in files)))
print("FlowWorks files in no consult:", missing or "none")
