
## spec
`BiomeCast_Ashkarr.xml` was deployed 2026-08-27 to the game copy, byte-identical
(`fdb78659d233bada1903e845eb7a5e1c`). 28 operations, 801 animal entries, all 28
Ash'karr biomes. **Defs parse only at startup, so this is invisible until the next
cold load.**

## verify
```
python3 src/RimMandrake/Utils/biome_commonality_zeroed.py --ours
```
must report **0** entries at commonality 0 among the ones our patch writes, and no
Earth animal spawns in `BiomeCypreJungle`.

## criteria
- [ ] 0 zeroed entries among the ones this patch writes.
- [ ] No Earth fauna in `BiomeCypreJungle`.

## Watch out
- 🔑 **Three cast rows are deliberately absent** — `SWPotF_RaceDef_ysalamir`
  (Desert, ExtremeDesert) and `GiantAnt_Race` (PoisonForest) are ThingDefs, not
  PawnKindDefs, so the generator skipped them. Their absence is correct, not a hole.
- ⚠️ **The de-dup patches are a separate file and load AFTER this one.**
  `AnimalBiomeDuplicates_Generated.xml` and `AnimalBiomeDuplicates_Fix.xml` can
  still zero an entry this file wrote. A commonality-0 reading is not automatically
  this patch's fault — check which file last touched that biome/animal pair.
- ⚠️ A patch that matches nothing logs nothing. A biome renamed by another mod
  would silently drop its whole operation; the coverage count above was taken
  against the def capture, not against the running game.

## offline pre-answer — CHECK, 2026-08-27
Measured against the DEPLOYED patch (repo and game copy both `fdb78659…`, still
byte-identical to the fingerprint above — re-checked today), not against a running game.

- **Criterion 1 — PASSES at source.** `biome_commonality_zeroed.py --ours` finds
  193 zeroed entries across 28 biomes, and **not one is an entry our cast patch writes**
  (zero `*`-marked rows). The zeroes are all other mods' business.
- **Criterion 2 — PASSES against the list, and the LIST is the defect.**
  All 28 biomes are clean against every one of the 80 names in
  `design/Jawa/fauna/EARTH_FAUNA_EXCLUDED.txt`. But that list is Core/Odyssey defNames
  only, and the cast writes the **GRim "Colorful" retextures of four banned animals**,
  which are the same Earth species under a mod prefix:

  | written | biome | its vanilla twin, which IS banned |
  |---|---|---|
  | `GRimTortoise` | **BiomeCypreJungle**, LavaField | `Tortoise` |
  | `GRimCobra` | AB_FeraliskInfestedJungle, AB_MiasmicMangrove | `Cobra` |
  | `GRimMonitorLizard` | AB_MiasmicMangrove | `MonitorLizard` |
  | `GRimBullfrog` | SeaIce | `Bullfrog` |
  | `Wolf_Great` (Odyssey greatwolf) | AB_MycoticJungle | — not listed at all |

  🔑 `BiomeCypreJungle` is the biome this item's own criterion names, and it has a
  tortoise in it. **A live look will find Earth fauna there and the patch is doing
  exactly what it was told** — the exclusion list never heard of the retextures.
  ⇒ The fix is BUILD's: add the five names and re-run the allocator. It is not a
  live-check failure and should not be recorded as one.
- ⚠️ Still UNMEASURED offline: the de-dup patches load after this one and can zero an
  entry we wrote. Only the load answers that.
