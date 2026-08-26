# T3 and the temperature system — 2026-08-26, seat CHECK

T3 wants an unclothed pawn to take hypothermia on `AB_PropaneLakes` (−59.8 °C) and *not* overheat on
`ExtremeDesert` (+48.2 °C). There is no bridge route to a map on a chosen tile, so I went at the
mechanism instead. What came out is a bigger capability than the row.

## 🔑 THE FINDING: you can drive a live map's temperature to anything, via its WORLD TILE

A `ColdSnap` on a temperate map is useless for this — measured, it fell **0.9 °C per 1,000 ticks**
and would bottom out around −10, nowhere near a Jawa's −50 comfyMin. So instead:

```
jawa/world_tile_get 18393     -> temperature 14.72,  biome ZBiome_Grasslands
jawa/world_tile_set 18393 temperature=-60
jawa/world_commit             -> true
   +1000 ticks   map outdoor -66.3   seasonal -57.5
   +11000 ticks  map outdoor -50.3   seasonal -57.2
restore to 14.72 + commit      -> map outdoor +24.3   seasonal +17.6
```

⇒ **`world_tile_set` + `world_commit` propagates straight into the running map's weather**, both ways,
and it is reversible. That is a far stronger lever than `jawa/game_condition` for any test that needs
a specific climate, and it is how a `HorrorWastes` or `ExtremeDesert` temperature can be reproduced
on whatever map you happen to have.

⚠️ **Finding the map's tile is the awkward part: NO tool reports it.** A regex over all 291 tool
descriptions for "current map's tile" returns nothing. The workaround is
`jawa/world_objects_get` → the `Settlement` whose faction is `PlayerColony` → its `tile`.
Here that was **18393**.

## What the cold actually did

At −50 to −66 °C the map became lethal. Before: 70+ pawns. After 11,000 ticks:

```
jawa/list_pawns includeCorpses=true  ->  14 pawns, 4 of them dead
   3 x Drifter (Baseliner) + Human58021, my Baseliner farm subject
rimworld/list_colonists              ->  4 alive, all of them indoors
```

The pawns that survived were the ones inside a shelter. That is the temperature system working.

## ⛔ But T3 is UNMEASURED, and the reason is a trap worth more than the row

**Hypothermia was never observed as a hediff.** My two stripped subjects — a `MandrakeJawa`
(comfyMin −50) and a `Baseliner` (−40) — read `-` for eleven consecutive polls and then turned out
to be **absent from the map entirely**, not even present as corpses.

```
jawa/pawn_get Human58390 -> xenotype null, position {}, hediffs null, dead null
jawa/list_pawns includeCorpses=true -> ABSENT
```

🔴 **`FindPawn` searches `mapPawns.AllPawnsSpawned`, so a dead pawn stops resolving by id — and a
FILTERED read of a subject that no longer exists returns an empty list that looks exactly like a
clean negative.** My loop printed "no hypothermia" eleven times about a pawn that had been dead for
most of them.

🔑 **The fix for any timed test: check the subject still EXISTS before believing an empty filter.**
`pawn_get` returning nulls across the board is the tell — not `hediffs: []`, but
`position: {}` and `xenotype: null` on a pawn you spawned yourself.

⇒ T3's stated criterion is **not passed and not failed**. What is established is that the climate can
be driven to the target values, that the map is lethal at them, and that shelter is what separates
the living from the dead.

## Housekeeping

The tile was **restored to its original 14.7229729 °C** and committed; the map reads +24.3 outdoor
again. This is a throwaway quicktest map and most of its wildlife was killed by the cold — recorded
so nobody reads that population as a finding about anything else.
