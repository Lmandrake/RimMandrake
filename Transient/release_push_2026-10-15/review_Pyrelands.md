# Pyrelands code review — 2026-10-15 (BENCH reviewer)

Scope: src/RimMandrake/Pyrelands/**, src/RimUtinni/PyrelandsMechanics/**, UtinniPatches/Patches/*_Pyrelands.xml, Utils/*pyrelands*.py. 105 .cs/.py/.xml/.csproj files; 27 DIRTY at start, rest CLEAN.

Pending, under edit (skipped): src/RimMandrake/Pyrelands/review/ (untracked), any human_review.py

| path | reachable | verdict | defects found/fixed | sha |
|---|---|---|---|---|
| src/RimMandrake/Pyrelands/About/About.xml | yes | CLEAN | none | 192949b062 |
| src/RimMandrake/Pyrelands/Defs/DamageDefs/RM_FlamefangVenomBite.xml | yes | CLEAN | FIXED: severityPerDamageDealt 0.06 put a colonist past lethalSeverity 1 in two power-10 bites (vanilla ToxicBite 0.015); now 0.02 + inverse-body-size scaling. Header named the wrong mod | 192949b062 |
| src/RimMandrake/Pyrelands/Defs/HediffDefs/RM_FlamefangVenom.xml | yes | CLEAN | header fixed (wrong mod; nonexistent Maneuvers/ folder) | 192949b062 |
| src/RimMandrake/Pyrelands/Defs/HediffDefs/RM_PyrelandsHediffs.xml | yes | CLEAN | none | 192949b062 |
| src/RimMandrake/Pyrelands/Defs/JobDefs/RM_PyrelandsJobs.xml | yes | CLEAN | none | 192949b062 |
| src/RimMandrake/Pyrelands/Defs/SandShovel/RM_ShovelSand.xml | yes | CLEAN | none | 192949b062 |
| src/RimMandrake/Pyrelands/Defs/ThingDefs_Items/RM_FurnaceHide.xml | yes | CLEAN | none | 192949b062 |
| src/RimMandrake/Pyrelands/Defs/ThingDefs_Races/RM_Ashwallow.xml | yes | CLEAN | header said UtinniPatches / cross-mod extension / wired via WildAnimals patch (all false); corrected | 192949b062 |
| src/RimMandrake/Pyrelands/Defs/ThingDefs_Races/RM_PyrelandsFauna.xml | yes | CLEAN | header said the mechanics live in another mod and are patched in from RUT_PyrelandsIgniters_Comps.xml (false); corrected | 192949b062 |
| src/RimMandrake/Pyrelands/Defs/ThinkTreeDefs/RM_BurrowOnFireThinkTree.xml | yes | CLEAN | none | 192949b062 |
| src/RimMandrake/Pyrelands/Defs/ThinkTreeDefs/RM_FireHawkThinkTree.xml | yes | CLEAN | none | 192949b062 |
| src/RimMandrake/Pyrelands/Defs/ThinkTreeDefs/RM_UllaiThinkTree.xml | yes | CLEAN | comment claimed thermal cycle is the only other node in the slot (firehawk 55, burrow 56 too); corrected | 192949b062 |
| src/RimMandrake/Pyrelands/Defs/ToolCapacityDefs/RM_FlamefangBite.xml | yes | CLEAN | header fixed (wrong mod) | 192949b062 |
| src/RimMandrake/Pyrelands/Patches/RM_PyrelandsIgniters_Comps.xml | yes | CLEAN | FIXED, significant: the comps were gated on FindMod 'RimUtinni Patches' although RM_FireHawk/RM_FurnaceBeast now live in Pyrelands, so a standalone Pyrelands had no ember-carrying, warmth, bed ignition or thermal cycle. Now unconditional; xpaths match 1 def each | 192949b062 |
| src/RimMandrake/Pyrelands/Patches/RM_ShovelSand_Orders.xml | yes | CLEAN | none | 192949b062 |
| src/RimMandrake/Pyrelands/Source/FireEcologyHook.csproj | yes | CLEAN | header: build line pointed at the read-only mirror and called the DLL a one-rule hook; now winbuild.py Pyrelands. csproj is not in .srchash, no rebuild | 192949b062 |
| src/RimMandrake/Pyrelands/Source/SelfTest/Fuzz/RimMandrakePyrelands.Fuzz.csproj | yes | CLEAN | none | 192949b062 |
| src/RimMandrake/Pyrelands/Source/SelfTest/RimMandrakePyrelands.FurnaceWarmth.SelfTest.csproj | yes | CLEAN | none | 192949b062 |
| src/RimMandrake/Utils/build_pyrelands_art_sheet.py | NO: one-off Sept review-sheet builder, cited only by a closed item and an evidence note; 4 rows point at moved/deleted textures (UtinniPatches FireHawk/FurnaceBeast) | NOT REVIEWED, stays DIRTY | dead-file candidate; neither ships nor tests Pyrelands | |
| src/RimMandrake/Utils/lint_pyrelands_defs.py | yes | CLEAN | FIXED: chk() raised TypeError on any unparsed constant (None <= x); now an ERROR row. pyrelands-turret check added to docstring. lint 0 ERROR; selftest_pyrelands_lint 28/28 | 192949b062 |
| src/RimMandrake/Utils/mutate_pyrelands_fuzz.py | yes | CLEAN | none | 192949b062 |
| src/RimMandrake/Utils/selftest_pyrelands_fuzz.py | yes | CLEAN | none | 192949b062 |
| src/RimMandrake/Utils/selftest_pyrelands_lint.py | yes | CLEAN | none | 192949b062 |
| src/RimUtinni/PyrelandsMechanics/About/About.xml | yes | CLEAN | garbled dependency sentence corrected | 192949b062 |
| src/RimUtinni/PyrelandsMechanics/Source/RimMandrake.Utinni.PyrelandsMechanics.csproj | yes | CLEAN | build line -> winbuild.py PyrelandsMechanics | 192949b062 |
| src/RimUtinni/PyrelandsMechanics/validation.py | yes | CLEAN | docstring: Harmony chain adds no rows (mod has no Harmony). STATIC PASS | 192949b062 |
| src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml | yes | CLEAN | header said eight residents; the BiomeDef has nine (ullai) | 192949b062 |
| src/RimMandrake/Pyrelands/validation.py | yes | pending, under edit (another agent's uncommitted change appeared mid-review) | not reviewed | |

Notes
- 78 of 105 scope files were already CLEAN at start (all .cs among them).
- modcheck mod_static reports Pyrelands' Kernel/*.cs and SelfTest/*.cs as 'not in FireEcologyHook.csproj': false positive (it does not resolve `Kernel\` subpaths; lint_pyrelands_defs confirms they are listed). modcheck belongs to another agent; not touched.
