## spec
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/MandrakeJawaXenotype.xml` gives `RSW_MandrakeJawa` a
`<nameMaker>RSW_KoTOR_NamerJawa</nameMaker>` and NO `<chanceToUseNameMaker>`. Decompiled 1.6
`PawnBioAndNameGenerator.GenerateFullPawnName` uses the xenotype's nameMaker only when
`Rand.Value < xenotype.chanceToUseNameMaker`, and `XenotypeDef.chanceToUseNameMaker` is a bare `float`
(default 0). So the Jawa namer can never be chosen.

MEASURED live 2026-10-01 (StarWarsRaces suite, chain `jawa_naming`): 3 of 3 pawns spawned with
`xenotype=RSW_MandrakeJawa` got human names ("Chris Madsen", "Unkow 'Schlitzer' Manus", "Danielle Wagner"),
none in `SWX/Jawa/First.txt`. Not a suite bug; the suite's assertion is correct and stays.

Fix: add `<chanceToUseNameMaker>999</chanceToUseNameMaker>` (the value `RSW_RimMandrakeChiss` uses).

SIBLINGS (MEASURED by an XML scan 2026-10-02): 43 of the 48 XenotypeDefs under `src/` that declare a
`nameMaker*` carry no `chanceToUseNameMaker` (`RimMandrakeXenotypes.xml` holds most). Each one is a
decision (a species may be meant to draw human names); do not sweep, check per species.

## verify
Re-run `modcheck run StarWarsRaces`: `namer_draws_from_jawa_wordlist` PASS.

## criteria
Spawned Jawa draw their first name from `SWX/Jawa/First.txt`.
