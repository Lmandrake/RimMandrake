# GREENTIDE_YEARNING_FRUIT_1 — digestive-accelerant fruit: def + hediff + filth C# built, wired into RM_Greentide

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
- Wired into `RUT_Greentide.xml`? **NO, and never will be** — that def is
  FROZEN (`GREENTIDE_RM_MOD_BUILD_1`); new campaign fauna/flora for the
  Greentide is wired only onto `RM_Greentide` from now on.
- Wired into `RM_Greentide`'s `wildPlants`? **YES**, 2026-09-26 — see below.
- Filth/pass-seed comp: **built**, `GREENTIDE_YEARNING_FRUIT_FILTH_1`
  (closed `e399e17ca`) — `RM_HediffComp_SeedPassage`
  (`RimMandrake.CreatureBehaviors`), wired onto `RUT_DigestiveAccelerant` via
  a `RM_HediffCompProperties_SeedPassage` comp block. Drops `Filth_AnimalFilth`
  and rolls a chance to germinate a `RUT_YearningFruit` seedling at the
  eater's cell when the hediff naturally ends. Works on any pawn, colonist
  or wild grazer alike.

## wired into the biome

`RUT_YearningFruit` is NOT one of the 8 Star Wars donor plants blocked on
`DONOR_DEFS_PORT_TO_OURS_1` — it's a wholly new plant defined inside
UtinniPatches itself, so it needed no `MayRequire` gate, same posture as the
`RUT_Sytheclaw` wildAnimals row. Added as a new `PatchOperationConditional`
+ `PatchOperationAdd` operation in
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Greentide.xml` (that file
already anticipated a future wildPlants section — see its own "DELIBERATELY
NOT IN THIS FILE YET" note), targeting `RM_Greentide`'s `wildPlants` at
commonality 1.2 (matching the weight the roster's own annotation gave this
design line before it split into its own plant). Validated with
`validate_patch.py --defs --live` against the 2026-09-26T01-08-12Z capture:
xpath matches 1 node, 0 errors, 0 warnings on the patch file itself.

## art

One job filed (`rutyearningfruit_v1`, a `Graphic_Random` plant, single job
not per-facing).

## naming

Working name only — no existing greentide shipping-names card was found;
one is owed alongside `RUT_YearningFruit`/`RUT_YearningFruitHarvested` and
(from earlier in this item's history) `RSW_CanopySwinger`.
