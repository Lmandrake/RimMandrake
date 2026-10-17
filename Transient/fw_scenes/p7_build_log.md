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

## Stage (e) — tests (SelfTest, oracle 3000 x all modes, vv_shipped_matrix, run_selftests --only)
- status: pending

## Stage (f) — publish
- status: pending

## Defaults chosen (veto list)
- pending
- stage (e) running: SelfTest 514/514 PASS; winbuild OK; oracle next
- oracle 3000/3000 x 7 modes PASS; vv_shipped_matrix next
- vv_shipped_matrix run 1: SHIPPED all 0 (kernel_fuzz 0/10000 ... hose 0/2798, trail 0/1500); OFF_edgeSinks 142/2000 (known); control build failed on the VV csproj list (added RM_RelativeRulesMath.cs to vv_shipped_matrix.py); rerun
- run 2: control build failed (RM_RelativeRulesMath referenced RM_FillEffectMath; made self-contained). SelfTest 514/514 again; vv run 3 next
- vv run 3: SHIPPED 0 everywhere; OFF_edgeSinks kernel_fuzz 142/2000 (known); control 194/2000; VERDICT FAIL only on AUTHORED Thirst_slime_last_resort_ruled (known); forced-flag SHIPPED suite fails = the identical 24 of P5's run 20261017T132450 (diff empty)
