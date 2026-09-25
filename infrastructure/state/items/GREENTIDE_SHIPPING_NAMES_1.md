# GREENTIDE_SHIPPING_NAMES_1 — owner card: name two greentide working names

## what

Two new-def commissions from `COMMISSION_LEDGER_CLEANUP_1`'s the_greentide
sheet shipped with working (internal) defNames only:

- `RUT_YearningFruit` — the digestive-accelerant fruit bush, the_greentide.md
  §4's "the fruit that yearns to be eaten."
- `RSW_CanopySwinger` — the canopy-crossing prey animal, the_greentide.md
  §4's "the Swingers."

## watch out

- `RSW_CanopySwinger` is NOT wired into the live-carrying `RUT_Greentide.xml`
  (that def is FROZEN, `GREENTIDE_RM_MOD_BUILD_1`) — it reaches the campaign
  world via `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Greentide.xml`'s
  `PatchOperationAdd` onto `RM_Greentide`, filling the slot the dianoga
  vacated (owner ruling 2026-09-23). Renaming it only needs that one patch
  file's row changed plus the ThingDef/PawnKindDef's own defName/label — it
  does NOT touch the frozen `RUT_Greentide.xml` at all.
- `RUT_YearningFruit` is not wired anywhere in the live world yet (see
  `GREENTIDE_YEARNING_FRUIT_1`'s "not wired into the biome yet" section) —
  renaming it is a plain in-repo rename with no live-world side effect.

## needs

owner
