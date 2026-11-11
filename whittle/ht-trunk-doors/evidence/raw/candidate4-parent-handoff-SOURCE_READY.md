# Source ready — candidate4 Python-only tier correction

C# remains exactly committed/built candidate3 ef5821d580764928453e41abb2f4903c5f8eb739. Production build rc0,0warnings/0errors. No rebuild required: all54 runtime inputs unchanged; v3/v4 compiled-input manifests are byte-identical.

Only new production path since candidate3: src/RimMandrake/HugeThings/northstar/trunk_doors_live.py (exact loaded tier17, registered VEF required). Parent may commit that delta and update SOURCE_COMMITTED metadata.

Rationale: composed Biomes donor XML references VEF classes without declaring dependency. Existing registered builder documents this exact fact; fresh pilot2 concurs. Adding registered VEF through modset_builder preserves baseline closure and unchanged log/preflight gates. No unrelated mod source changed.

Exact complete current feature paths/hashes: SOURCE_READY_INPUTS.json. Runtime manifests: evidence/raw/source-ready-v3-compiled-inputs.json and evidence/raw/source-ready-v4-compiled-inputs.json. Exact source snapshots retained in their corresponding directories.

Paths:

- design/RimMandrake/giant_footprint_design_2026-10-07.md
- design/RimMandrake/huge_footprints_perf.md
- design/RimMandrake/hugethings_codex_2026-11-09/QUESTIONS.md
- design/RimMandrake/hugethings_codex_2026-11-09/REVIEW.md
- design/RimMandrake/hugethings_codex_2026-11-09/record.json
- src/RimMandrake/HugeThings/Defs/JobDefs/RM_JobDefs.xml
- src/RimMandrake/HugeThings/Defs/WorkGiverDefs/RM_WorkGivers.xml
- src/RimMandrake/HugeThings/Source/CompHugeFootprint.cs
- src/RimMandrake/HugeThings/Source/HugePlantCutting.cs
- src/RimMandrake/HugeThings/Source/Kernel/RM_HugeClaimsKernel.cs
- src/RimMandrake/HugeThings/Source/MapComponent_HugeFootprints.cs
- src/RimMandrake/HugeThings/Source/PlantCutToilRewrite.cs
- src/RimMandrake/HugeThings/Source/RM_HugeThings.csproj
- src/RimMandrake/HugeThings/Source/SelfTest/FootprintBudget/Program.cs
- src/RimMandrake/HugeThings/Source/SelfTest/FootprintBudget/Stubs.cs
- src/RimMandrake/HugeThings/Source/SelfTest/HugeThingsFuzz.cs
- src/RimMandrake/HugeThings/Source/SelfTest/TrunkDoors/Program.cs
- src/RimMandrake/HugeThings/Source/SelfTest/TrunkDoors/TrunkDoors.csproj
- src/RimMandrake/HugeThings/Source/TrunkDoorValidationHooks.cs
- delete src/RimMandrake/HugeThings/northstar/p1_live.py
- src/RimMandrake/HugeThings/northstar/trunk_doors_live.py
- src/RimMandrake/HugeThings/northstar/workload_corpse_live.py
- src/RimMandrake/HugeThings/selftest_hugethings_footprint.py
- src/RimMandrake/HugeThings/validation.py
- src/RimMandrake/HugeThingsTestRaces/Defs/ThingDefs_Plants/RM_TestContactPlant.xml
- src/RimMandrake/Utils/selftest_hugethings_budget.py
- src/RimMandrake/Utils/selftest_hugethings_lint.py
- src/RimMandrake/Utils/selftest_hugethings_trunk_doors.py
