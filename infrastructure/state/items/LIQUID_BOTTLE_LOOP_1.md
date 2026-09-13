# LIQUID_BOTTLE_LOOP_1 — bottles as real items: fill, use, dirty, wash + special behaviors

Filed by BENCH, 2026-09-13 (`design/RimMandrake/liquids_framework_design.md`
§4 "Bottles are real items" + "Special behaviors").

## spec

Bottle chain: `RM_BottleEmpty` → fill job (terrain edge or tank) →
`RM_Bottle<Liquid>` (generator-emitted per row) → use → `RM_BottleDirty` →
wash job (consumes water) → empty. Buckets = larger bottle, same chain.
BARRELS too (owner-ruled 2026-09-13, "very scavenger"): ~25-unit big sibling,
same chain plus fill/empty bills at a tank; barrels are the vanilla-native
bulk trade route — every trader buys/sells them with zero patches.
Dirty stage behind a Mod Settings toggle, default ON in the campaign; off =
use returns a clean empty. Special behaviors as row data, no per-liquid C#:
revert timer (bottled boiling/icy → fresh), rot (bottled blood via
CompRottable; household recipe → hemopack before spoil). Bottles carry
cuisineTags ThingCategories so the future RSW cuisine mod cooks against tags,
never defNames. Blood is item-only in v1 — no blood terrain.

## verify

Quicktest: full loop observed (fill from a shore, drink, dirty appears, wash
returns empty). Timer checks: a boiling bottle becomes fresh; a blood bottle
rots on schedule and the hemopack recipe beats the clock. Settings-off run:
no dirty bottles anywhere, loop still whole.

## Watch out

- Depends on LIQUID_REGISTRY_CORE_1 (bottles are generator-emitted from rows).
- DBH drinkable registration is a separate item (LIQUID_THIRST_CHAIN_1) — this
  item's bottles must be drinkable-agnostic and work with DBH absent.
- The DBH bottle-inheritance bug ManyWaters hit (`ParentName="DBH_WaterBottle"`
  broken, worked around via `ResourceBasedMom`) — reuse that workaround.
