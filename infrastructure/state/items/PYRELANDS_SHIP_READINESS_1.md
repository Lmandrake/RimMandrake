# PYRELANDS_SHIP_READINESS_1 — the SHIPPED rung for Pyrelands: art, review, settings, deploy

**For:** FOUNDRY. **Parent:** PYRELANDS_NORTHSTAR_TRIAL_1. **Plan:** `design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md` §5.
**Depends on:** BIOME_MOD_UNIFICATION_1 (it ships as part of `mandrake.rm.biomes`; the per-biome
toggle must gate mechanics, not only worldgen).

## acceptance (gaps MEASURED 2026-09-30)

- [x] **Ashwallow has art.** It is `RM_Ashwallow` now, and its three facings sit under
      `src/RimMandrake/Pyrelands/Textures/Things/Pawn/Animal/Pyrelands/Ashwallow/` (checked 2026-10-04).
- [x] **`RM_Emberscythe` is off the Megascarab placeholder.** `emberscythe_v1` (kept on the 2026-09-12
      art review sheet) is wired at `Textures/Things/Pawn/Animal/Pyrelands/Emberscythe/` (2026-10-04). Only the
      dessicated graphic still borrows Megascarab's.
- [x] `BARBSLINGER_SCORPION_REDESIGN_1` closed (BENCH, `642c53b46`, 2026-10-07).
- [ ] The FireHawk flight frames are judged in an owner-present session (`FIREHAWK_FLIGHT_BEHAVIOR_1`), never by an
      unattended hunt. **The only acceptance line left, and it is not offline work.**
- [x] Code review CLEAN for every file this item named (checked 2026-10-11 with `code_review_status.py check`):
      `RM_PyrelandsMod.cs`, `RM_JobGiver_BurrowOnFire.cs`, `RM_JobDriver_Burrow.cs`, `RM_BurrowOnFireExtension.cs`,
      `PyrelandsTuning.cs`, `PyrelandsMechanicsDefOf.cs`, `PyrelandsMechanicsGate.cs`, `BiomesShell/Source/RM_BiomesMod.cs`
      and `validation.py` (`a542f6539`). ⚠️ 19 other `Pyrelands/Source/*.cs` files are still DIRTY (content changed
      since their 2026-09-26 marks, or never marked: `RM_LightningBreaker.cs`, `RM_PyrelandsGiants.cs`,
      `RM_TerrainDig.cs`). They belong to the standing review loop, not this item.
- [x] Mod Settings: `settings_audit.py` reports every mod OK. Every Pyrelands toggle is labelled, and the
      worldgen-affecting ones are marked (pickAP). The gate census was run 2026-10-11: every one of the 34
      `RM_PyrelandsSettings` fields is read only from files that also consult `PyrelandsMechanicsGate.On` (master
      AND shell "Pyrelands" toggle). The exceptions are the breaker fields (`RM_LightningBreaker.cs`) and the
      sand-shovel fields (`RM_TerrainDig.cs`), which are exactly the ones the "Mod enabled" tooltip names as
      running on their own switches. The census is file-level. Proof per call site is the offline `MechanicsOn`
      kernel test (`a820b692e`). The live proof of the gate waits on unification wave 2.
- [x] The composed `mandrake.rm.biomes` deploys at 0 diff (2026-10-11). `deploy_custom_mods.py --compose biomes`
      reports "in sync (3374 files)". `dll_source_stamp.py check` MATCHes `RimMandrake.Biomes.dll` and
      `FireEcologyHook.dll`, and the deployed `FireEcologyHook.dll` bytes equal the `# dll:` header (`84a92fbb…`).
- ⛔ 0 tiles on Ash'karr is expected (painted once at the end). It is not a gap.
