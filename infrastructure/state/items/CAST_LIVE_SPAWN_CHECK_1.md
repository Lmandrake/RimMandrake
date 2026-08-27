
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
