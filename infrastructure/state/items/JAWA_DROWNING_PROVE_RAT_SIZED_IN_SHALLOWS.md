# JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS

Filed 2026-10-21 by FOUNDRY. Symptom: on the GSS power-theft live run (`validation_aerial.py --theft day`, result
`src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_theft_20261021.json`, governor log
`D:\ClaudeWork\rimmandrake\scratch\governor_stops.jsonl` 2026-10-21T08:08–08:10Z) Captain (Human470521, `RSW_Jawa`) went
"downed (health 1)" EIGHT times, ticks 75811, 77791, 81031, 82771, 84811, 86791, 88771, 90811, with RM_PitDrowning 0.6.
It was read as "pit avoidance (RM_PitPathing / RM_PitStepCost) is not steering pawns". **The evidence says it is not pits.**

## Findings (offline + one read-only bridge probe, 2026-10-21)

1. **No pit exists on that map.** The script digs nothing (`validation_aerial.py` has no excavation call), and
   `jawa/flowworks_excavation_report` on the same colony save reads `excavatedCellCount 0`. RM_PitPathing/RM_PitStepCost
   only act on cells with `ClimbDepthAt > 0` (dug, or a DRY natural bed), so they never ran for this.
2. **RM_PitDrowning is also the natural-water drowning hediff**: `Swimming/RM_Swim.cs` Tick ("the ONE drowning rule on
   natural water") adds it on any `IsWater` terrain. RM_Stillsand has `RM_WaterBrineShallow` pools (e.g. 178–180,149 on the
   current colony, `isSourceCell true depth 4 fill 4`); colonists run DBH `washAtCell` jobs targeting those cells. A job whose
   DESTINATION is the water cell is not steered by any path cost.
3. **A Jawa is rat-sized to the water rules.** `RM_Drowning.HeightOf` = 0.5 m for both `RSW_Jawa` and `RUT_Jawa_Colonist`
   (BodySize under the 0.75 band edge, `RM_RelativeRulesMath.HeightByBand[1]`). Head under at 0.45 m standing, 0.10 m lying;
   vanilla-passable shallow water without engine data reads 0.5 m (`RM_SwimWater.WaterMetresAt`). So every shallow pool is
   "deep swimming" for a Jawa (class Swimmer, endurance 0.86 h ≈ 2,150 ticks, then RM_SwimExhaustion 1 → drowning).
4. **Eight downs are one episode, not eight entries.** Spacing is a constant ~1,980–2,040 ticks. The harness
   (`_pt_calm`, PT_SITE_HEDIFFS) strips RM_PitDrowning and refills needs but leaves RM_SwimExhaustion at 1 and leaves the
   pawn where it lies; KeepsHeadUp is false while exhausted, so drowning restarts at once in the same cell.
5. **Unproven:** the actual cell Captain was in (no positions were logged; bridge_calls.jsonl keeps no result bodies) and
   whether he was lying (asleep/downed → 0.10 m threshold) or standing mid-pool with no shore in reach.

## What to do (one live sitting, game-up, bridge; ~15 min on the theft save)

1. Load the same colony (the `--theft` start state), `jawa/pawn_census` + `RM_Swim.ProofSwim "x,z"` and
   `RM_PitFillEffects.ProofDrown "x,z"` (static_call) at Captain's cell at the FIRST governor `downed` stop. Record cell,
   terrain, water metres, lying, exhaustion, job def. That settles 5.
2. Decide by the record:
   - natural brine + small-band Jawa → a DESIGN question for the owner (Jawa height on the size table; whether a colonist
     humanlike drowns in 0.5 m pools; whether `washAtCell`/drink destinations in over-the-head water are refused). Ask by
     question card; do not change HeightByBand unasked.
   - harness: `_pt_calm` must also remove RM_SwimExhaustion and move a downed pawn to the nearest dry standable cell, or
     it re-downs the same pawn every ~2,000 ticks (fix in `validation_aerial.py`, offline).
   - if a dug cell does turn up (ClimbDepthAt > 0), THEN reopen the pit-pathing question with `RM_PitPathing.ProofRoute`.
