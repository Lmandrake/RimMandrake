# LIQUID_THIRST_CHAIN_1 — crude→household→industrial water cleaning, wired to DBH thirst

Filed by BENCH, 2026-09-13 (`design/RimMandrake/liquids_framework_design.md`
§4 "Thirst chain"). Replaces the deleted distilled/potable/fouled/toxic
bottled-water proposal; its detox chain survives as the `thirstQuality`
ladder on registry rows.

## spec

Conversion chain: crude (solar still, drip filter — slow, free, always
buildable) → household (fueled still / boiling — research-gated) → industrial
(found set-pieces only; see LIQUID_INDUSTRY_SETPIECES_1). Register bottles as
DBH drinkables by patch; patch the DBH water tag onto adopted terrains. With
DBH absent, bottles are plain ingestibles with a hydration thought — graceful
degrade.

## verify

MEASURED fact this rides on: `DBHThirst` NeedDef is in the frozen dump
(capture 2026-08-29) via the "Dubs Bad Hygiene – Thirst" add-on riding Lite.
Quicktest with DBH Lite + Thirst on the list: a thirsty pawn seeks and drinks
a bottle; a crude still slowly converts fouled→potable. A second run with DBH
absent: no errors, hydration thought fires.

## Watch out

- Depends on LIQUID_BOTTLE_LOOP_1.
- DBH patches must be PatchOperationFindMod-gated — both FindMod and
  Conditional return true on no match and log nothing; verify the patch
  actually landed via the live def, not the patch file.
