# FOUNDRY helper notes 2026-10-05 — liquid-looks port

## Step 1 port

## Step 2 build/tests/commit

## Step 3 queue
- crash branch: only ed3d0b527 unique; staged build tree D:\Luke\dev\_rmbuild\FlowWorks held the untracked crash sources (extended RM_LiquidSurface, FaceMaterial, LipOcclusion).
- took crash/staging versions of files origin had not touched since 157482540 (WallFaceMath, ExcavationWalls, FaceMaterial, PitLipOcclusion, LiquidSurface, SelfTest, PitDepthDraw, registry/PitFluids xml, generate_liquid_suite, decisions.json [owner ask_ladder pickA], art_checks, NS trial site json).
- hand-merged settings Mod.cs (+3 settings, UI, view 10800), csproj (+RM_LiquidLooks.cs), site_spec (+3), toggle check 80->83.
- build OK (winbuild); C# SelfTest 92/92; all FlowWorks + modcheck python selftests exit 0 (incl. selftest_liquid_looks, northstar 83 toggles).
