## spec
Thin when filed — no spec/verify/criteria in the queue entry itself, but
fully specced as packet B5 of
`design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` §5 (inputs: unit 7,
the resentment stub already built by `DROIDWORKS_BOLT_CORE_1`; outputs:
aura thought; resentment ≥ threshold → rebellion `MentalState` on removal;
shear-on-damage; un-bolt-each-other job; verify: "bolt 30 days, remove →
rebels; damage shears"; after: A1). The three `// TODO` comments already
sitting on `RSW_DW_BoltResentment`/`RSW_DW_RestrainingBolt` in
`HediffDefs_Droidworks.xml` since `DROIDWORKS_BOLT_CORE_1` named exactly
this scope. Built directly, FOUNDRY, 2026-09-08.

## Built
- **Mood aura** (`ThoughtDefs/ThoughtDefs_Droidworks.xml` +
  `Source/Droidworks/ThoughtWorker_NearBoltedDroid.cs`): `RSW_DW_
  NearBoltedDroid`, a situational thought (live-scanned, never a memory,
  same as vanilla's own `NeedFood`/`NeedRest`) — active for any pawn within
  12 tiles of a spawned pawn wearing `RSW_DW_RestrainingBolt`. "Depressing
  to be around" — `design/Jawa/droid_system_spec.md` §7.
- **Shear on damage** (`HediffCompProperties_DWBoltShear` on
  `RSW_DW_RestrainingBolt` itself, `Source/Droidworks/
  HediffComp_DWBoltShear.cs`): `Notify_PawnPostApplyDamage` rolls
  `1-(1-0.02)^damage` per hit; on a hit, the bolt is removed uncontrolled.
  `RSW_DW_BoltResentment` is untouched either way — resentment survives
  however the bolt comes off.
- **Rebellion on removal past threshold** (`Recipe_RemoveRestrainingBolt.cs`,
  extended): after removing the bolt, if `RSW_DW_BoltResentment.Severity >=
  0.6` (`RebellionThreshold`, FOUNDRY's own number — nothing in the design
  doc gives one), triggers vanilla's own `MentalStateDefOf.Berserk` via
  `TryStartMentalState` (not forced — respects the normal
  `StateCanOccur`/blocked-breaks gates). Reused vanilla Berserk rather than
  a bespoke `MentalStateDef` — FOUNDRY's own scope call.
- **Un-bolt-each-other job** (`RSW_DW_UnclampBolt` JobDef +
  `Source/Droidworks/JobDriver_DWUnclampBolt.cs`): the removal counterpart
  to `DROIDWORKS_BOLT_CORE_1`'s own `JobDriver_DWClampBolt` — 300 ticks, no
  Downed gate (cooperative, not coercive), no bill, no ingredient. Same
  "driver correct, WorkGiver/float-menu wiring is follow-up" precedent that
  file's own header already set for `RSW_DW_ClampBolt`. Deliberately does
  NOT roll the rebellion check — the field route is a quieter un-bolting,
  not the deliberate shop procedure (FOUNDRY's own scope call).

## verify (live, minimal 25-mod list + quicktest, FOUNDRY 2026-09-08)
Build: `dotnet build Droidworks.csproj -c Release` — 0 errors, first try.

- **Mood aura, live**: bolted a spawned Protocol droid next to an existing
  colonist (Cait), read her thoughts via `jawa/pawn_thoughts` —
  `RSW_DW_NearBoltedDroid`, label "A bolted droid nearby", moodOffset
  **-2.0**, present in the live list.
- **Shear on damage, live**: bolted a fresh droid, dealt five 10-damage
  `jawa/damage` hits (`allowColonists: true` — the tool otherwise skips a
  pawn already on the player faction, a real trap this session hit and
  fixed). The bolt was still present after hits 1-4 and **gone after hit
  5** — `jawa/pawn_get`'s hediff list dropped `RSW_DW_RestrainingBolt`
  entirely, matching the authored per-hit roll.
- **Un-bolt-each-other job, live**: bolted a third fresh droid, unpaused
  (`rimworld/set_time_speed Normal` — the previous item had left the game
  paused, which the first attempt at this test silently no-opped:
  `jawa/ordered_job` reported `pausedDuringWait: true, ticksElapsed: 0` and
  its own docs are explicit that this "proves NOTHING"), then
  `jawa/ordered_job` (`pawnId: Cait, jobDef: RSW_DW_UnclampBolt, targetAId:
  <droid>, waitTicks: 800`). After 800 ticks Cait's job had moved on to
  `GotoWander` and `jawa/pawn_get` on the droid confirmed
  `RSW_DW_RestrainingBolt` **no longer in its hediff list** — the full
  goto→work→remove sequence ran and completed for real, not just accepted.
- **Rebellion on removal**: not driven live — `Recipe_RemoveRestrainingBolt`
  is a `Recipe_Surgery` (health-tab medical bill), and no bridge tool
  forces a `Bill_Medical`/surgery job to completion (same limitation A1,
  B3, B4a and B4b's own items already hit and recorded). The trigger call
  (`MentalStateHandler.TryStartMentalState`) is a real, unmodified vanilla
  API traced against its own source (`mcp__rimsage__read_csharp_symbol`),
  called with `forced: false` so it still respects every normal vanilla
  gate — verified by code review only, the one piece of this item's own
  verify line not reached live.
- **Player.log, literal check**: same 12 pre-existing `Config error in`
  lines throughout (before and after every change, across all four live
  tests) — zero new errors or exceptions from this item's defs or C#.

## Assumptions recorded (Charter: "record what you assumed")
1. `RebellionThreshold = 0.6` (60% of `RSW_DW_BoltResentment`'s max
   severity) — FOUNDRY's own number.
2. Rebellion reuses vanilla `MentalStateDefOf.Berserk` rather than a
   bespoke `MentalStateDef` — the design doc names the consequence
   ("rebellion"), not a mechanism.
3. `shearChancePerDamage = 0.02` per point of damage — FOUNDRY's own curve;
   the mood aura radius (12 tiles) and `-2` mood offset are likewise
   FOUNDRY's own numbers.
4. The field un-bolt job does not roll the rebellion check the surgery
   route does — a deliberate asymmetry (quiet field removal vs. the formal
   shop procedure), not specified either way by the design doc.
