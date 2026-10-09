# Species surnames wiring 2026-10-09
Defect: donor namers draw `lastGenerated` from [Name<X>] (first-name list) while the shipped
`LastName<X>` keyword (.../Last.txt) was never referenced.
Fix: `lastGenerated->` rules now use [LastName<X>] in `src/RimStarWars/StarWarsRaces/Defs/RulePackDefs/SW_NameMakers.xml`
(41 packs, 82 lines; measured 41 not 39: Pureblood + SandP also qualified). Already wired before: Aqualish, Arkanian, 3 Hutt.
No Last keyword (untouched): Chiss, Gand. Word-list contents unchanged.
Generator: `wire_surnames()` in `src/RimMandrake/Utils/gen_races_mod.py` (called from apply_overrides); NOT regenerated (needs donor dump) - XML edited with the identical transform.
Selftest: `src/RimMandrake/Utils/selftest_namer_surnames.py` (old XML: FAIL on 41; new: PASS 46).
Suite: 345/348 pass, only utinnipatches_dump fails (known stale dump).
Live check owed: generate pawns of 3 species, read names.
