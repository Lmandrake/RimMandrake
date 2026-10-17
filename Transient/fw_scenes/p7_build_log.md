# P7 build log — PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE (FOUNDRY offline builder, 2026-10-17)

Base: origin/main 8e5c81b02 (P5/P6 DLL cb8194587). No bridge, no game.
Ruling (owner 2026-10-17, by card, R7): drowning, fall damage, spikes, shooting become relative to the height
difference; pit rooms by person-band pocket without the 2 m clause. P12 (swim) shares the drowning rule.

## Stage (a) — read docs, re-grep the P5 hit-list at HEAD
- status: DONE. Hit-list holds at 8e5c81b02. Extra finds: jump gizmo (JumpTargetFor/TryJumpInto) keyed to D4; LiquidFire
  shove exemption keyed to D4; pit-room CONFLICT: card 2026-10-16 PIT_PRISON_JUDGE_D3_ROOMS ("Superdeep only, as designed")
  vs V6 (any depth). Resolved as a setting `pitRoomMinDepthMetres` (0 = V6 default, 2 = the 10-16 card), noted on the item.

## Stage (b) — relative math (Verse-free, in SelfTest): drop, head cover, line-walk, spikes
- status: BUILT. `RM_RelativeRulesMath.cs`: TallestWallOver/SheerDropAt (V4), FallScale by metres (V3), HeightByBand +
  HeadUnder + ExitInReach + DrowningPerCheck (V2), ShotBlocked Bresenham across a cliff (V5), PitRoomCell (V6),
  StepIsAFall (DryStepBaseCost). Old absolutes DELETED: RM_PitTrapMath.FallDropScale, RM_FillEffectMath.DrowningPerCheck.

## Stage (c) — wire the rules: spikes, shooting, drowning, falls, rooms, exposure, fire, trap/pathing, step cost, cover, label
- status: BUILT (uncommitted at this line). Spikes placeworker (V4) + translation key RMFlow_SpikesNeedDrop; shooting PairAllowed
  (V5, ClimbDepth with covers as ground, early-outs before any closure); drowning RM_Drowning (V2) with the P12 hook
  `RM_Drowning.keepsHeadUp`; falls FallScaleFor (V3) in both climb modes; jump gizmo by drop > climb; rooms PitRoomCell (V6)
  + RM_PitRooms.IsPitFloor used by lip service, capture-down, exposure, pit-room temperature, liquid fire, knock-back;
  cover placeworker = 2 m sheer drop; wet-pit planning = own dry band; DryStepBaseCost by the drop; LabelOf no 'pit';
  proof key lipSuperdeep -> lipInPit (extensions.py). OFF branch (relative climb off) trap/pathing stays the documented
  absolute legacy mode.

## Stage (d) — settings
- status: BUILT. shootingCliffMetres 2, pitRoomMinDepthMetres 0, fallDamagePerMetrePast2 0.5, fallDamageCap 4,
  pitDrowningHeadFraction 0.9, pitDrowningLyingFraction 0.2, spikeMinDropMetres 2 (floats under existing toggles; no new
  bool, so the 150-toggle count holds). Changing the room minimum rebuilds rooms.

## Stage (e) — tests
- status: DONE. SelfTest 514/514 (+8 Relative_*: spikes on a sheer drop incl. ledge 3 m inside a 7 m core; falls by metres
  incl. 8 m = 4x and the 4/7/7/4 drops; drowning by head incl. water over a ledge (56,000 L: ring 1 m wades, core 4 m drowns,
  no exit up the 3 m wall) and brim-full; shooting across a cliff incl. two on one wide pit floor (the P5 finding), the
  ledge/core, the 4/7/7/4 square; line-walk cost MEASURED 0.060 us/ask (79,800 asks on a 250x250 map, 60 pits, 400 pawns);
  rooms by pocket incl. a sheer 1.5 m pocket; DryStepBaseCost by the drop; call-site wiring and settings).
- Updated (ruling changed, not a regression): ReviewBatch56 PitRooms case (superdeep-only -> setting depth), RewireChecks
  wet-pit cost and sheet-drowning, GptFixesA C4-F7 pattern, PocketGrid/DeepBed/DeepDig fall-scale asserts, Program drowning case.
- Oracle differential 3000/3000 x 7 modes. vv_shipped_matrix --skip-ep: SHIPPED 0 everywhere; OFF_edgeSinks kernel_fuzz
  142/2000 (known); VERDICT FAIL only on AUTHORED Thirst_slime_last_resort_ruled (known); forced-flag SHIPPED suite fails
  identical to P5's run (24, diff empty).
- run_selftests --only (FlowWorks python + settings): green except known human_review still_water_one_surface_height and
  settings_screens SWBestiary#BeastMechanics (not FlowWorks; untouched).

## Stage (f) — publish
- status: DONE. Source 01c6d2e01, DLL 38aa4ddb6 built on it (not behind origin; no scratch clone needed). PUBLISHED 38aa4ddb6.
- Ledger notes: PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE (built, conflict), DEPTH_DEFAULTS_ASK_ELEVEN_VETOES (two card lines).

## Defaults chosen (veto list; each has a Mod Setting)
- V2 drowning: head under at 0.9 H standing / 0.2 H lying; H by climb size band 0.5 / 1.75 / 2.5 / 3.5 m (PROVISIONAL);
  no drowning while standing beside a climbable step into water under the head; rate = today's brim rate (about an hour).
- V3 falls: linear to 2 m, +50% of the 2 m fall a metre, cap 4x (8 m); applies with relative climb on AND off.
- V4 spikes: a sheer drop >= 2 m to any of 8 neighbours, at any depth. Pit cover: the same 2 m drop (constant).
- V5 shooting: blocked when a square strictly between stands >= 2 m above the LOWER end (reading of "higher than both ends"
  that keeps ruling 23's "from the edge only"); adjacent always allowed.
- V6 pit rooms: person-band pocket at any depth (setting 0); CONFLICTS with the 2026-10-16 card; 2 m restores it.
- Wet-pit planning cost: a wet dug square costs at least its own dry band (no-op under 2 m with shipped costs).
- Not changed: the OFF branch (relative climb off) trap/pathing stays absolute by design (it IS the absolute legacy mode).

## P12 hook
- `RM_Drowning.keepsHeadUp` (Func<Pawn, IntVec3, float waterMetres, bool>), default = swimmer graphic. P12 sets it to its swim
  rule (ability, exhaustion, apparel) and calls `RM_Drowning.PerCheck(map, eng, pawn, cell, waterMetres)` for natural deep
  water too; head/lying/exit/rate stay in one place. Proof: `RM_PitFillEffects.ProofDrown("x,z")`.

## Left (not P7's or live)
- L2 live rows (P10): a pawn falls 7 m and takes 3.5x; a sheer 1.5 m pocket holds a prisoner; drowning/shooting live rows.
- canal_spikes live chain still names its component spikes_only_on_superdeep (its asserts still hold).
