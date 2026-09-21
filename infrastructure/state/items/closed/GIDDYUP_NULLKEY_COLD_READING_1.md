# GIDDYUP_NULLKEY_COLD_READING_1 — log reading owed on the next full-list load

Filed by BENCH 2026-09-13. GIDDYUP_NULLKEY_CRASH_1 closed at `1f222320b`
(GR_Mantistanis existence-guard in
`src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml`, deployed
byte-identical). Its criterion (c) — a fresh Player.log confirming the crash
is gone — could not be taken without a restart. This item carries the reading;
fold it into whatever run sheet covers the next full-list load.

## spec
On the next full-list cold load, in the fresh Player.log:

- EXPECT zero `Could not resolve cross-reference: No Verse.PawnKindDef named GR_Mantistanis`
- EXPECT zero `ArgumentNullException` at `RimWorld.BiomeDef.CommonalityOfAnimal`
  IL offset `0x0003d` (the `[Giddy-Up] An error occured calling AllWildAnimals`
  null-KEY family)

## verify
```
PROVE   both greps return 0 on the fresh log
LIES    GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1's duplicate-key crashes (offset
        0x000b2, e.g. AA_Eyeling) are a SEPARATE open item — their presence
        is not this fix failing. And a log captured before the load finished
        proves nothing (see the stale-capture red herring recorded in
        CORRECT_GIDDYUP_NULLKEY_1).
```

## criteria
Done when both EXPECT lines are measured zero on a Player.log from a full-list
load launched after 2026-09-13, and the result is noted on
GIDDYUP_NULLKEY_CRASH_1. If either grep is nonzero, reopen
GIDDYUP_NULLKEY_CRASH_1 instead of closing this quietly.
