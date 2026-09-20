# DESERT_PACK_ANIMALS_FOR_TRADERS_1 — allowedPackAnimals empty, trader caravans never spawn

## what is wrong

`allowedPackAnimals` is absent on both RUT_Desert and RUT_ExtremeDesert,
which the engine treats as an empty list. MEASURED (engine):
`PawnGroupKindWorker_Trader.CanGenerateFrom` returns false on every tile of
both biomes when `allowedPackAnimals` is empty — trader caravans never
arrive in either desert biome. The roster's herd beasts — "the pack and
draught animals the campaign runs on" — never appear under a trader. Vanilla
Core Desert has the same defect, so this is not a regression we introduced,
but it is still wrong for our biomes.

## why it matters

No trader caravans ever spawn in either desert biome, silently — there is no
UI signal, the same failure shape as `DESERT_FORAGEDFOOD_INERT_1`'s
forageability gap.

## the work

List the ported pack beasts (`RSW_Bantha`, `RSW_Ronto`, `RSW_Eopie`,
`RSW_Jamel`, `RSW_Falumpaset`) in `<allowedPackAnimals>` on RUT_Desert, after
verifying each race actually carries `packAnimal true`. On RUT_ExtremeDesert,
either list the same set or leave it empty by design (no roads, no trade fits
the biome's isolation) — this half is the owner's call, one card.

## Watch out

Which of the five ported herd beasts actually carry `packAnimal true` was
**not checked** in the source review. Instrument: `grep <packAnimal>` across
`SWBestiary/Defs/ThingDefs_Races/RSW_{Bantha,Ronto,Eopie,Jamel,Falumpaset}.xml`
before wiring any of them — do not assume all five qualify.

## verify

RUT_Desert's `allowedPackAnimals` lists only races confirmed `packAnimal
true`; a debug trader-caravan generation call on a Desert tile succeeds;
RUT_ExtremeDesert's field matches whatever the owner rules on the card.

## criteria

Trader caravans can generate on RUT_Desert; RUT_ExtremeDesert's behavior
matches an explicit owner ruling, not silent omission.
