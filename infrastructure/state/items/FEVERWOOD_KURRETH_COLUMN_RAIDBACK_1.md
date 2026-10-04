## spec
Split from FEVERWOOD_ANT_THEFT_RAIDBACK_1 spec 3-4; part A built 62913db1a.
What exists: `src/RimMandrake/FeverWood/Source/RM_KurrethTheft.cs`. A stolen animal leaves the map in a kurreth's
hands; `Pawn.ExitMap` hands it to `RM_FactionDef_KurrethSwarm`'s `KidnappedPawnsTracker` (alive world pawn), and
`RM_MapComponent_KurrethTheft.Thefts` records victim, exit cell, tick and lord id per map. Vanilla also sends its
own per-animal kidnap letter (`KidnappedPawnsTracker.Kidnap`, player-faction pawn).

1. **The raid-back:** when a theft is recorded, a site appears on the world map (`QuestScriptDef`
   `RM_Quest_KurrethColumn`; read the `rimworld-quests` skill first): a column camp within a few tiles holding the
   stolen animals alive (downed-and-bound or penned; take them out of the kidnap tracker when the camp map
   generates), guarded by kurreth. Raiding the camp recovers them. Ignored for a fixed time, the column reaches its
   hive and the animals are carried into the nearest hive dungeon (`RM_MapComponent_AntHive`), still recoverable
   there; gone only if the hive is left for a long while (letter when that happens). All timers `// INVENTED`.
2. **Mod Settings:** the column timers and the hive hold time (antTheftEnabled already exists). Every field read
   by the code it claims to gate.

## criteria
- `jawa/get_defs` `QuestScriptDef/RM_Quest_KurrethColumn`: `foundCount` 1.
- Live after a theft (`RM_KurrethTheftProof.ProofRaid` then step): the quest's site holds the stolen thornbug's
  `thingIDNumber` (site map pawns, or the quest part's list).
- Raiding the site and returning: the thornbug with the same `thingIDNumber` is back on a player map, alive.
