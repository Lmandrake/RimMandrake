# RIMMANDRAKE_STAGE_PYRE_FLAMEFANG_BITES_LAND_ONCE_NOT_MAUL

Caused by RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO (Stage 6 visit 2, 2026-11-20). Class SITE (the staged bite).

## spec

`flamefang_venom` (sc_flamefang_venom, bar flamefang_bite_carries_venom), visit 2: 3 PASS, 3 UNMEASURED
(design/concepts/Pyrelands/version/in_game/visit_2/evidence/pv2_flamefang_venom.json).
- `venom_tended_vs_untended`: "the untended patient was never envenomed" (its health read holds only go-juice addiction).
- `venom_wait_out`: RESTART: colonist Colin (Human94711) died of BloodLoss during the row (the governor stopped
  safe_advance at tick 656784: "died: BloodLoss"). The flamefang kept attacking.
- `venom_immunity_read`: no bridge tool reads ImmunityRecord (in RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN).
Visit 1 met the same staging fault (the victim fled unbitten; fixed then by drafting and a narrower latch, db9b7d66).

The scene needs one bite that lands on each patient, then the flamefang removed or held, so venom is read and nobody is
mauled. Stage it: draft the patient beside the flamefang, latch until RM_FlamefangVenom appears, then despawn the flamefang
(or apply the hediff through the bite's own path, if the bar allows) before the hours run.

## verify

Each patient carries RM_FlamefangVenom after its bite; no colonist is downed or dead over the rows.

## criteria

- venom_tended_vs_untended and venom_wait_out read PASS or FAIL, never UNMEASURED for staging.

## Acceptance test

Live only. Red now: `... cli.py run ... --chains flamefang_venom` reads the two rows UNMEASURED as quoted (2026-11-20).
Green: both rows read PASS or FAIL, and the chain's vitals notes record no death.

## refs

file: src/RimMandrake/Pyrelands/validation.py
def: HediffDef/RM_FlamefangVenom
