# L2 failure triage 2026-10-07 (offline; nothing committed)

## (a) LuminousPigment glowtank_toggle: HARNESS (primary) + MOD DEFECT (secondary, fixed)
- Primary: `jawa/get_defs` OMITS null fields (a requested null field returns `fields: {}`; measured:
  `l2sweep_WreckedMachines.json` VFEFactory_AutomatedSmelter designationCategory -> `"fields": {}`).
  `_designation` (src/RimMandrake/LuminousPigment/validation.py:644-652) turned that into "(absent)", which is not
  in its null set, so a correctly nulled GlowTank read as "still in Production". ApplySettings
  (Source/LuminousPigmentMod.cs:505) does null it. Fix: "(absent)" now counts as null (typo'd names still answer
  "(no such field)" -> UNMEASURED). Same cause would hit press_unbuildable.
- Secondary, real: the architect menu is a cache. DesignationCategoryDef.ResolveDesignators (private, run once) builds
  the list; changing BuildableDef.designationCategory later does not touch it, so the tooltip "does not appear in the
  build menu" was false until relaunch. Fix: `RefreshBuildMenu()` in LuminousPigmentMod.cs (reflection call on the
  Production category, only while Playing), called from ApplySettings.
- Build: winbuild LuminousPigment OK (0 warnings/0 errors). DLL + .srchash left UNCOMMITTED.
- Re-check: live `modcheck run LuminousPigment` chain settings_apply (glowtank_toggle, then press_unbuildable,
  cuisine_recipes_toggle). Needs a game restart/deploy of the new DLL first. A human glance: toggle GlowTank off in
  Mod Settings, close, open Architect > Production; the tank should vanish without a relaunch.
- Not touched, other FAILs in that log: patches_applied (designator 'RuntimeType'), mat_alive_control, unlocked_after_sighting,
  press_is_a_powered_bench (watts vs per-tick unit mismatch, harness) remain as the part3 sheet classified.

## (b) Droidworks protocol_droid_shifts_prices: HARNESS/environment (likely, unconfirmed)
- `jawa/fire_incident` (JawaBenchTerrainTools.cs:4290-4366) calls CanFireNow then TryExecute directly. canFireNow=True
  but fired=False means TryExecuteWorker returned false (vanilla IncidentWorker_TraderCaravanArrival: SpawnPawns empty,
  or no reachable spot). The worker picked faction RUT_Jawa_DeepwaterCompact (response `faction`), whose Trader group
  needs `RSW_MonCalamari` (MayRequire mandrake.rsw.starwarsraces, UtinniPatches/Defs/FactionDefs/JawaDeepwaterCompact.xml:173-176)
  and Quarren guards; on the quicktest list that group can spawn empty. Cannot be proven offline.
- Fix made (src/RimStarWars/Droidworks/validation.py ~586-596): if the first fire fails, retry once with
  faction="OutlanderCivil" (vanilla trader faction). Check still fails if neither fires.
- Re-check: modcheck run Droidworks, chain protocol_trade_advantage. If it still fails, read Player.log right after the
  fire for the SpawnPawns/pawn-group errors, and `jawa/faction_relations_get` for OutlanderCivil existing in the world.
- ion_overload: EXPECTED (Jawa Ion mod absent), unchanged.

## (c) FallLineArrivals anywhere_allows: HARNESS (partly fixed; one cause remains)
- Not "no skyfaller cell": wreck_lands PASSED, and that real fire runs TryExecuteWorker which needs TryFindCell.
- Cause 1 (fixed): IncidentWorker.CanFireNow caches its result per TicksGame (`lastCheckCanRunTick`, decompiled).
  The game is paused, so the OFF-read just before returned the cached False. Added `t.wait_ticks(2)` after the
  setting flip in anywhere_allows and in wrecks_toggle_off_refuses (validation.py:96-107).
- Cause 2 (NOT fixed, likely): base CanFireNow returns false while `GenDate.DaysPassedSinceSettle < def.earliestDay`
  (RUT_FallArrival earliestDay=2, tick 8061 is day 0.13; RUT_LabRatFalls earliestDay=10). Dry-run uses CanFireNow, so it
  stays False on a fresh quicktest map, which also makes the passing off_fall_line_refused check vacuous.
  Proposed fix: add a `ProofGate` static method to FallLineArrivals calling FallLineGate.Allowed on the current map and
  assert that, or run the gate chain after advancing past day 2 (about 120000 ticks) on a boring world. Needs C#, not done.
- Re-check: modcheck run FallLineArrivals chain gate. If anywhere_allows still fails, cause 2 is confirmed.

## (d) WreckedMachines materialCostFactor/refurbishedRatio/kludgedRatio/wreckedRatio: HARNESS (fixed)
- The patcher does rewrite (Source/WreckedMachinesLadder.cs:190-192 mood stages, WreckedMachinesMod.cs:330 costList).
- `_def_field` (WreckedMachines/validation.py:330) called get_defs with the default deep=false, which returns each
  non-scalar list item as its bare type name (Scalars() docs, JawaBenchTerrainTools.cs ~4990): before and after both read
  ['ThingDefCountClass', ...] / ['ThoughtStage', ...] / ['CompProperties_Power', ...]. The check could not see a value.
- Fix: `deep=True` in that call. Non-list drives (researchCostFactor, skipRestorationResearch) unaffected (they PASSED).
- Residual risk: deep serialisation depth is 3; if costList items still show no count, read the def via jawa/get_def.
- allowDonorSmelter/allowFullRestoration UNMEASURED is the same null-omission quirk as (a): a null designationCategory
  `before` reads None. Not changed; the donor smelter ships with a category only when another mod provides one.
- Also in the sweep: spawns_and_inspects_clean x3 are real def config errors (minifiable not in a thing category;
  impassable buildable) - MOD DEFECT, not triaged here.
- Re-check: modcheck run WreckedMachines, the four setting_*_drives_def chains.

## (e) UnfinishedLine volunteer_offered: HARNESS FIXTURE (genuine precondition)
- UnfinishedLineWorld.cs:100 VolunteerBlocker requires Enclaves relation == Ally; docstring (validation.py:372) states
  the precondition but nothing established it.
- Fix (validation.py ~385): before w("volunteer"), `jawa/faction_relations_set faction=Player other=RUT_Jawa_FreeDroidEnclaves
  kind=Ally`, fail loudly if not success. Left as Ally for later components (they need it too).
- Re-check: modcheck run UnfinishedLine chain world; the 3 downstream UNMEASURED components should now run.
