# RimMandrake: Lore Stages — validation walk
subject: src/RimMandrake/LoreStages  (packageId `mandrake.rm.lorestages`)
deps: none beyond core (engine; content mods such as RimUtinni ScarlandsLadder depend on it)
list: engine only; ships no defs and no ladder
status-hint: LORE_STAGES_FIRST_SCRIPT_1 — first script drafted, never run live

Sources: `src/RimMandrake/LoreStages/About/About.xml` description, `Source/RM_LoreStagesMod.cs`, `Source/GameComponent_LoreStage.cs`, `Source/LoreStageApplier.cs`, `Source/RM_LoreStageTableDef.cs`, `Source/LoreStageDebugActions.cs`, `Source/SelfTest/Program.cs`; consumer `src/RimUtinni/ScarlandsLadder/Defs/LoreStageTableDefs/RUT_ScarlandsLadder.xml`.

## must be true
- The mod ships no defs and a bogus def name reads notFound (the probe can say absent). → defs_resolve.control_probe_can_say_absent
- The one Mod Setting, `stagedTextEnabled` (default on), round-trips get/set/get/restore; the type resolving also proves the assembly loaded. → settings_roundtrip.stagedTextEnabled_round_trips
- A loaded consumer ladder carries a ladderId and a positive maxStage. → consumer_ladder.ladder_table_loaded_with_id_and_cap (UNMEASURED on a tier without RUT_ScarlandsLadder)
- The def a ladder rewrites resolves and has a non-empty shipped description (the baseline the applier restores). → consumer_ladder.ladder_target_def_resolves_with_text (UNMEASURED on a tier without the target)
- Setting a ladder's rung rewrites the staged field to that rung's text, and going back down restores the shipped text. → stage_walk.rung_up_changes_text_and_down_restores_shipped (UNMEASURED: no bridge tool reaches SetStage)
- ThingDef and HediffDef private description caches are cleared on every apply. → stage_walk.thing_and_hediff_caches_cleared_on_apply (UNMEASURED: no bridge reader; offline `Source/SelfTest`)
- With the master toggle off every ladder reads stage 0 (shipped text) while the real stage keeps being tracked. → stage_walk.master_toggle_off_reads_stage_zero_text (UNMEASURED: settings set via the bridge does not Reapply)
- Loads and does nothing when no `RM_LoreStageTableDef` is present. → UNCOVERED: needs a tier with no consumer mod; the source and the SelfTest are the evidence
- A ladder's stage persists in the save per ladderId. → UNCOVERED: needs save/load, a boundary (debug_process §4: save migration)

## the walk
1. [D] `jawa/get_defs` on a control name reads notFound   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on `RM_LoreStagesSettings`   # settings_roundtrip
3. [D] `jawa/get_defs RM_LoreStageTableDef/RUT_ScarlandsLadder` and `BiomeDef/RUT_Scarlands`   # consumer_ladder
4. [B] stage changes, caches, toggle-off effect   # stage_walk (UNMEASURED until a SetStage tool exists)

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "an empty ladder read means a broken mod" — the engine loads and does nothing with no table; consumer_ladder records UNMEASURED, never FAIL, when no ladder is in the tier.
RULED OUT: "a settings set through the bridge exercises the toggle" — `Reapply()` runs only from the settings window's checkbox change; the round trip proves the field only.
