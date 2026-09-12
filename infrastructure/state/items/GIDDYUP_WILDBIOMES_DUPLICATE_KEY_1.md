# GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1 — Giddy-Up's BuildAnimalBiomeCache still throws

No prose file existed despite four commits against this ID
(`37182c7a7` file, `539990920` first dedup, `95eb3bfe8` in-list class,
`8f627e057` "rename the dedup fix again, one file still beat it"). Writing
one now because the live log proves the fix is still incomplete.

## live evidence (FOUNDRY, 2026-09-12, current running session)

`Player.log` around ctor 741-742/1563 (`GiddyUp.ResourceBank`/`GiddyUp.Setup`),
**this session, after `8f627e057`**:

```
[Giddy-Up] An error occured calling AllWildAnimals. ...
System.ArgumentNullException: Value cannot be null.
Parameter name: key
  at RimWorld.BiomeDef.CommonalityOfAnimal (Verse.PawnKindDef animalDef)
  at RimWorld.BiomeDef+<get_AllWildAnimals>d__94.MoveNext ()
  at GiddyUp.MountUtility.BuildAnimalBiomeCache ()

[Giddy-Up] An error occured calling AllWildAnimals. ...
System.ArgumentException: An item with the same key has already been added. Key: AA_Eyeling
  (same stack, repeats 3x — ref 862618C7)
```

Two distinct mechanisms, both still live:
1. **Null-key** — a PawnKindDef reference resolves to `null` somewhere in some
   biome's `AllWildAnimals` walk. This is `GIDDYUP_NULLKEY_CRASH_1`'s exact
   signature (filed separately, `needs: offline`) — same root class, not yet
   fixed by any GIDDYUP_WILDBIOMES commit.
2. **Duplicate key, new animal** — this session's collision is `AA_Eyeling`,
   not `RSW_Iriaz` (the one `539990920`/`8f627e057` targeted). The dedup so
   far has been whack-a-mole per-animal rather than closing the general case:
   an animal with both a donor `<wildBiomes>` block AND an independent
   `BiomeCast_*.xml` commonality entry on the same biome collides in
   `CommonalityOfAnimal`'s dictionary build. `AA_Eyeling` needs the same
   overlap check `RSW_Iriaz` got (grep its `<wildBiomes>` against every
   `BiomeCast_*.xml` for a shared biome), then decide once whether to fix
   these one-by-one as they surface or find every remaining overlap in one
   pass across the full animal roster.

## verify (unmet)
A cold load with zero `[Giddy-Up] An error occured calling AllWildAnimals`
lines. Not provable without a restart — each partial fix has only been
checked against the ONE animal it targeted, and the log above is proof that
approach keeps missing siblings. Left `doing`, not closed.
