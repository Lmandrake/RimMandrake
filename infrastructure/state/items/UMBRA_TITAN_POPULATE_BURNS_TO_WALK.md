# UMBRA_TITAN_POPULATE_BURNS_TO_WALK

Filed by `NIGHTSIDE_TITAN_JUDGE_GIANTS_IN_THE_DARK` (delegated: design). The call that a giant can live in `RUT_Umbra`, and its grounds: `design/RimMandrake/titan_passage_dark_side_calls_2026-11-05.md`.

## spec
1. At Umbra's roster sitting, invent a NEW native land giant (owner: a hole is filled with a NEW creature). Its adult body size must be 8 or more, so it is T2 (`RM_TitanicTierDef`). Give it an invented `RM_` name (Q11a).
2. Obey `design/Jawa/worldbuilding/biomes/the_propane_lakes.md` §4: nothing moves fluidly without burning, so it is always in flame when moving. Obey §6 too: no icy dayside analog, no kyber, no transportable natives, and the recognizability rule.
3. Home it on `RUT_Umbra`'s `wildAnimals`, at a rare commonality. With no passers list on the biome, that roster row is the titan passage's pool.
4. The art goes through the art-evaluation pipeline. The mod's functional script gains a row for the new creature.

## criteria
- `RUT_Umbra` homes a T2+ land animal. `TitanPassageUtility.Eligible` accepts it on an Umbra map, and `selftest_titan_passage_dark_side.py` still passes.
