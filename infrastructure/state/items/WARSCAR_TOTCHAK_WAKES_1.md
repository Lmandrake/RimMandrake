# WARSCAR_TOTCHAK_WAKES_1 — the embankment that breathes: the totchak sleeps in the Last Line and eats walls

From `WARSCAR_BEDAZZLE_SITTING_1`. Design source:
`design/Jawa/worldbuilding/biomes/warscar_turn3_development_2026-09-30.md` §2.3. Ruled turn 2: the woken
totchak eats **ruins AND player walls**. Body and art: `WARSCAR_FREE_TIER_BODY_1`.

## spec

1. **Dormancy:** stock `CompCanBeDormant` + `CompWakeUpDormant` (`wakeUpOnDamage`,
   `wakeUpOnThingConstructedRadius`). Precedent: our `RUT_SealedSleeper` / `RUT_Emberscythe` XML.
2. **Demolition wake:** `RM_CompDemolitionWake` (shape of `RUT_CompWaterWakeTrigger`) fed by postfixes
   on `Mineable.DestroyMined`, `GenExplosion.DoExplosion` (empty-registry fast path: it fires a lot in
   combat), and `Thing.Destroy` filtered to `DestroyMode.Deconstruct`; wakes dormant totchaks within 12.
3. **Spawn as wall:** a genstep finds a straight run of `AncientFortifiedWall`, removes 3 cells, places
   the dormant totchak there (dormant graphic = a wall segment with a breathing bob). Waking leaves the
   breach.
4. **Eating walls:** `RM_GnawTargetExtension` gains `gnawWalls` and `factionWeights` (no-faction ruin
   walls 4, player walls 1); `biteDamage` scales with body size; nutrition from the wall's stuff mass;
   a gnawed wall drops slag chunks as it dies (the sign).
5. **Lie down again:** after N days, a JobGiver walks it to a wall line and `ToSleep()`s it there.
   Not hostile unless harmed; harmed, a siege-scale fight.
6. **Readable signs:** the breathing hump from day one; a waking letter (*"Part of the Last Line just
   stood up."*) with a look-target; the breach; bitten walls and slag; its prints in a Settling; its name
   on hover while dormant.
7. **Mod Settings:** totchak on/off · eats player walls on/off (default on, ruled) · wake radius ·
   wall-eating damage scale.

## criteria

- A Warscar quicktest with ruins places one dormant totchak inside a fortified-wall run.
- Mining or an explosion within 12 wakes it and raises the letter; the wall gap remains.
- It gnaws a ruin wall before a player wall when both are reachable; a player wall is eaten when it is
  the only wall in reach.
- After its grazing days it re-enters dormancy elsewhere.
