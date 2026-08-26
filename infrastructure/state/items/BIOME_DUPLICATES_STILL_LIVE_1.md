# BIOME_DUPLICATES_STILL_LIVE_1 — the duplicate-animal crash survived its own close

`BIOME_CAST_DUPLICATE_ANIMALS_1` (BiomeCast_Ashkarr reintroduced the duplicate-animal crash)
is recorded **done, closed at `36f5c4b4`**. It is not fixed. Measured in the 2026-08-26 08:53
load, full 582-mod stack:

```
Error in static constructor of ChooseWildAnimalSpawns.Main:
  System.ArgumentException: An item with the same key has already been added. Key: JRWTorosaurus
  at RimWorld.BiomeDef.CommonalityOfAnimal (Verse.PawnKindDef animalDef)
```

`harvest_log.py` scores DEAD MODS **2, above baseline 0** — and a dead mod is the highest-priority
finding in any log. The same error is in the 06:35 log, so it is not new to this load.

## Why the close looked right and was not

The detector named in the 2026-08-10 fix file — `Utils/animal_inventory.py` — reads every active
mod's **Defs**. It reports **3** conflicts, and `observed/2026-08-13/inventory/conflicts.csv`
(regenerated 2026-08-26 07:01, current fingerprint) still says 3. None of them is JRWTorosaurus.

🔑 **Most of these collisions do not exist on disk.** They are created by PatchOperations at load:

```
More Vanilla Biomes/Patches/Jurassic Rimworld.xml
    PatchOperationAdd -> /Defs/ThingDef[defName="JRWTorosaurus"]/race/wildBiomes
                         ZBiome_Badlands 0.0375          <- the (b) side
our own Jawa_Patches/Patches/BiomeCast_Ashkarr.xml
    -> /Defs/BiomeDef[defName="ZBiome_Badlands"]/wildAnimals
                         JRWTorosaurus 0.21              <- the (a) side
```

Neither def says so in its own file. **A pre-patch reader cannot see it, and it reported a clean
number instead of an UNMEASURED.** That is the failure mode this project has a register for.

## What was built, 2026-08-26 by BUILD

`src/RimMandrake/Utils/biome_animal_conflicts.py` asks the same question of the **def dump
capture**, which is taken from the running game after every patch has applied.

**27 duplicate (biome, pawnKind) pairs across 12 biomes**, against the log's 12 keys.
🔑 **The log can only ever name 12** — one per biome — because each biome's cache throws at its
FIRST collision and stops. Fixing what the log names would have surfaced the remaining 15 one
load at a time. Validation: all 12 keys the game named appear in the 27, in the same 12 biomes.

`src/Jawa/Jawa_Patches/Patches/AnimalBiomeDuplicates_Generated.xml` — 27 conditional removals of
the ANIMAL-side entry, the same design as the hand-written 2026-08-10 file (the animal still
spawns there at the biome's own commonality; only the duplicate registration goes). Deployed.
`validate_patch.py` against the full 582: **0 errors, 0 warnings**.

⚠️ **17 of the 27 xpaths hit on disk; 10 match nothing there** — those are exactly the pairs a
patch creates, and the validator reads pre-patch XML. Their evidence is the capture, not the
validator. ⛔ Do not read those ten as broken ops.

## verify
Next load, on the log alone — no bridge needed:
- `harvest_log.py` DEAD MODS back to **0** (baseline), and no `ChooseWildAnimalSpawns` static-ctor error.
- `grep -c "same key has already been added"` = **0** (it was 12 distinct keys).
- Then re-run `biome_animal_conflicts.py` against the NEW capture: **0 pairs**. A non-zero there
  means a pair this pass did not reach, not that the patch failed.

## criteria
- [ ] Choose Wild Animal Spawns loads (no static-ctor exception).
- [ ] Zero duplicate-key exceptions in `Player.log`.
- [ ] `biome_animal_conflicts.py` reports 0 against a capture taken after the fix.
- [ ] `harvest_log.py` DEFS DISCARDED explained separately — 4 of the 6 are
      `GeneTattooTagFilter.ModExtension_GeneTattooTagFilter` from `SW_Genes.xml`, which is a
      DIFFERENT defect and needs its own item.
