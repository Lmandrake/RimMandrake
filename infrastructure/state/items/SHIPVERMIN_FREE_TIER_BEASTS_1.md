# SHIPVERMIN_FREE_TIER_BEASTS_1 — ShipVermin (RM tier) must not depend on the Star Wars bestiary; free-tier beasts, canon creatures patched in when it is active

Found by the dependency lint (`src/RimMandrake/Utils/lint_def_type_refs.py`, 2026-10-07): `mandrake.rm.shipvermin` (RM tier) hard-depends on `mandrake.rsw.swbestiary` (RSW tier), which breaks the tier rule (RM must be franchise-free and never depend on RSW/RUT; see CLAUDE.md "Star Wars style naming is NOT Star Wars IP").

## owner ruling (card, typed, 2026-10-07)

*"Make the free tier have its own beasts that get patched by the Star Wars bestiary when active. Same mechanics same mod otherwise."*

## spec

1. Remove the hard dependency on `mandrake.rsw.swbestiary` from ShipVermin's About.xml (and its loadAfter if only for that).
2. ShipVermin ships its OWN invented, franchise-free beasts (`RM_` defs, invented exotic names per Q11a) as the free-tier cast. A hole is filled with a NEW creature, never a neighbour's.
3. The Star Wars creatures it used to reference move behind the Utinni/RSW patch layer: when `mandrake.rsw.swbestiary` is active, a patch (PatchOperationFindMod-guarded, in the swbestiary or UtinniPatches patch layer, whichever already carries `WildAnimals_*` style patches) adds/swaps the canon creatures into the same slots with the same mechanics.
4. Same mechanics, same mod otherwise: the infestation/spawn/behaviour logic is unchanged; only the creature cast is split by tier. Every canon-vs-free pair uses the same behaviour tuning.
5. Franchise-free tier must be rich enough alone (Q11a): no thin fallback roster.

## criteria

- A1 (L0): `lint_def_type_refs.py` reports no RM to RSW dependency or type reference for ShipVermin; About.xml has no swbestiary entry.
- A2 (L1): on the free-tier list (no mandrake.rsw.*), ShipVermin loads with no red errors and its free beasts resolve via get_defs.
- A3 (L2): with swbestiary also loaded, the canon creatures appear in the same slots (get_defs/roster read) and the free beasts are replaced or joined as the patch says.
- A4 (L4): owner approves the free-tier beast list and art.

## NEXT

Read `src/RimMandrake/ShipVermin` (Defs, Source, Patches, About) and list every reference to swbestiary content; pick the free beast for each; keep mechanics identical.
