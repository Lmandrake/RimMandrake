# GREENTIDE_YEARNING_FRUIT_1 — digestive-accelerant fruit: def + hediff built, filth C# split out

## what

Resolves `COMMISSION_LEDGER_CLEANUP_1` ledger slug
`the_greentide:digestive-accelerant-fruit-the-fruit-that-yearns` —
the_greentide.md §4: "The fruit yearns to be eaten (owner): huge, sweet,
everywhere, loaded with digestive accelerants so the eater digests fast and
passes seed quickly — free calories with a tax (hunger returns fast, filth
follows, a brief waddle). The ground is carpeted in filth and sprouts,
which is the strategy *working*."

## built

- `RUT_YearningFruit` + `RUT_YearningFruitHarvested`
  (`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_YearningFruit.xml`)
  — a new wild fruit bush (not a reskin of the sheet's existing, unmodified
  Jogan/Muja fruit rows), eaten either raw off the plant or harvested.
- `RUT_DigestiveAccelerant`
  (`src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_YearningFruit_Hediffs.xml`)
  — real vanilla-stat mechanic: `HungerRateMultiplier` 1.6 and `MoveSpeed`
  0.75 for ~4 hours ("digests fast", "a brief waddle"), both real gameplay
  effects, zero new C#.
- Wired into `RUT_Greentide.xml`? **NO** — see "not wired" below.

## not wired into the biome yet

`RUT_Greentide.xml` is FROZEN (`GREENTIDE_RM_MOD_BUILD_1`, "content lives in
`mandrake.rm.greentide`; do not edit here") — the live world still runs on
that def until the terminal repaint. A prior pass in this same wave
mistakenly added a different new species (`RSW_CanopySwinger`) directly to
that frozen file; it has been reverted. `RUT_YearningFruit` needs the same
route: wiring belongs in
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Greentide.xml`-style
patch content targeting `RM_Greentide`'s `wildPlants` (that patch file
currently only covers `wildAnimals` — a plants patch is new scope) or
inside `GREENTIDE_RM_MOD_BUILD_1`'s own build pass, not invented here.
Cross-referenced to that item.

## split out

The "passes seed quickly, filth follows, ground sprouts" half needs a
genuinely new comp (same shape as `RUT_VorrelBrood`'s
`RM_HediffComp_ShadeStagger` — a germinate/filth-on-dispersal comp, but for
filth-and-seedling rather than shade-and-germinate). Filed as
`GREENTIDE_YEARNING_FRUIT_FILTH_1`.

## art

One job filed (`rutyearningfruit_v1`, a `Graphic_Random` plant, single job
not per-facing).

## naming

Working name only — no existing greentide shipping-names card was found;
one is owed alongside `RUT_YearningFruit`/`RUT_YearningFruitHarvested` and
(from earlier in this item's history) `RSW_CanopySwinger`.
