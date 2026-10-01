## Scope built (Eyeburst, Caudal Spring, Bellows; offline-checkable)

Same pattern as Pillar Arm and Lash (`CONTAGION_GROWN_LIMBS_BUILD_1`), all in `src/RimMandrake/Contagion/`:

- Hediffs `RM_Eyeburst` (Eye), `RM_CaudalSpring` (Spine, replaces it), `RM_Bellows` (Lung) in `Defs/HediffDefs/RM_GrownLimbHediffs.xml`, stats per the sheet. Stage fields (`restFallFactor`, `totalBleedFactor`) checked against decompiled `HediffStage`.
- Items `RM_EyeburstItem`, `RM_CaudalSpringItem`, `RM_BellowsItem` and install recipes (`Recipe_InstallArtificialBodyPart` via `SurgeryInstallBodyPartArtificialBase`).
- Abilities `RM_CaudalLeap` (Longjump shape, no hemogen, range 12, 1 day) and `RM_BellowsExhale` (Anomaly `CompProperties_AbilityReleaseGas`, BlindSmoke, 20 cells, 2 days) in `Defs/AbilityDefs/RM_GrownLimbAbilities.xml`, granted by `HediffCompProperties_GiveAbility`.
- Removal: the existing `HediffComp_UnfinishedEmerge`.
- The Monstrous gestation roll now draws from all five limbs; Mod Settings `grownLimbsEnabled` tooltip updated.
- Sample-order gap from BUILD_1 FIXED: `AmoebaHostUtility.FindSampleToInject` returns a Monstrous sample first; the inject job and float menu both use it.

## Not built, filed or owed

- Live checks (game up): install recipes appear, abilities show and fire, Unfinished spawns on removal, a missing spine's effect on Moving was NOT measured (the description says it leaves no spine).
- Art: Eyeburst reuses vanilla's bionic-eye wound texture tinted pink, Caudal Spring reuses Anomaly's TentacleLimbA, Bellows has no render node, item icons are tinted vanilla HealthItem. All bespoke art: `CONTAGION_GROWN_LIMBS_ART_1`. Ability icons are vanilla's.
- Caudal Spring attaches to Spine (the sheet's default); the Torso-addition alternative was not built.
- The sheet's owner `Rule:` lines are still blank; built to its recommendations.
- Selftests: 78/81 pass; the failures are the known `selftest_walklint.py` and `selftest_sound_paths.py`.
