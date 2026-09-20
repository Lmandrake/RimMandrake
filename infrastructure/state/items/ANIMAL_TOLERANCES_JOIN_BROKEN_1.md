# ANIMAL_TOLERANCES_JOIN_BROKEN_1 — animal_tolerances.py's biome join is dead, and re-running it would DELETE a live safety net

## Found while closing `BIOME_CAST_PATCH_DEAD_NAMES_1`, 2026-09-20 FOUNDRY

That item confirmed `src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` (the
fauna cast patch) targeted 22 pre-migration biome defNames that `BIOME_OWNERSHIP_WAVE_1`
(2026-09-09) replaced with `RUT_`-prefixed BiomeDefs — zero of those 22 names are
painted on any of the frozen world's 21,872 tiles (MEASURED against
`world/ASHKARR_WORLDMAP_tiles.csv`), so the file was pure no-op dead weight and was
deleted (design + src + deployed copies, `HEAD` at close time).

**`design/Jawa/fauna/animal_tolerances.py` has the exact same root-cause defect, but
its consequence is the opposite of harmless.**

- `animal_tolerances.py`'s `homes()` reads `cast_assignment.csv`'s `biome` column
  (the SAME pre-migration names: `Desert`, `ExtremeDesert`, `AB_MycoticJungle`, …)
  and looks each one up in `biome_flora.py`'s `_tile_temps()`, which keys off
  `world/ASHKARR_WORLDMAP_tiles.csv`'s `biome` column — now exclusively `RUT_`-
  prefixed names. **Every lookup misses.** Run `homes()` today and it returns empty
  for all ~652 animals.
- The deployed `src/RimUtinni/UtinniPatches/Patches/AnimalTolerances_Ashkarr.xml`
  (16,103 lines, 401 `PatchOperationConditional`s = ComfyTemperatureMin/Max for
  ~200 animals) is **NOT dead** — unlike the biome cast, its xpath targets the
  ANIMAL's own `ThingDef/statBases` directly
  (`/Defs/ThingDef[defName="X"]/statBases`), never a biome defName, so it keeps
  applying regardless of the biome-name migration. Its content was last touched at
  `935b29048` (2026-09-12, `MEGAFAUNAYIELD_DEAD_GR_TARGETS_1`, an existence-gating
  wrap, not a full regenerate) and appears to trace to the original 2026-08-23 ruling
  (`NORMALIZE_TEMPERATURE_TOLERANCES_1`) — i.e. it was almost certainly computed
  from real tile temperatures joined against the OLD biome names, back when
  `cast_assignment.csv` and the tiles CSV still agreed. Ash'karr's actual geography
  (elevation, `temp_c` per tile) did not move when `BIOME_OWNERSHIP_WAVE_1` renamed
  biome defs — only the label changed — so the shipped widened bands are very likely
  still substantively correct for the physical ground these ~200 animals are cast
  onto. **This item does not re-verify that; it only establishes that the join used
  to produce it is now broken.**

## Why this is more dangerous than the dead cast file, not less

The cast patch's failure mode was "xpath never matches → silent no-op → nothing
happens." This generator's failure mode, if re-run blind, is the opposite: `homes()`
returns empty → `compute()` iterates zero rows → `emit()` writes a `<Patch>` with
**zero Operations** → the regenerated `AnimalTolerances_Ashkarr.xml` **deletes all
401 existing temperature-tolerance widenings** the moment someone runs
`python3 design/Jawa/fauna/animal_tolerances.py` expecting a routine refresh (e.g.
after any future cast-roster edit). Per the file's own docstring, `ComfyTemperatureMin`/
`Max` are a **hard spawn gate** (`WildAnimalSpawner.cs:47/111`, strict inequality,
buffer 0) — losing the widened band silently reintroduces "animal never spawns wild,
nothing logs it" for however many of those ~200 animals actually needed the widening
to survive their real (`RUT_`) biome's climate.

⛔ **Do not regenerate `AnimalTolerances_Ashkarr.xml` until this is fixed.** Not
touched this pass — confirming it, not fixing it, was as far as this pass's scope
(`BIOME_CAST_PATCH_DEAD_NAMES_1`) went, and the fix is a design call (see below), not
a mechanical one.

## Also now-stale, cosmetic, do NOT hand-fix

`AnimalTolerances_Ashkarr.xml`'s own generated header still reads *"⛔ Assumes
BiomeCast_Ashkarr.xml SHIPS ... Deploy both or neither."* `BiomeCast_Ashkarr.xml` is
now retired, so that line is false. **Do not hand-edit the generated file** (its own
banner says so, correctly) — fix `animal_tolerances.py`'s `emit()`/docstring text in
the same pass as the real fix below, then regenerate once, so the false banner and
the broken join are corrected together instead of the banner being patched over a
still-broken generator.

## Owed

1. **Fix the join.** `homes()` needs to resolve each `cast_assignment.csv` biome name
   to its live `RUT_` successor before calling `_tile_temps()` — either via
   `BIOME_OWNERSHIP_WAVE_1`'s old→new mapping (if recorded anywhere machine-readable)
   or by rebinding `cast_assignment.csv`'s `biome` column to the new defNames
   directly (the more durable fix, and the one `BIOME_CAST_PATCH_DEAD_NAMES_1`
   already established the CSV's provenance role doesn't forbid — it remains the
   historical cast record either way).
2. **Prove no regression before shipping a regenerate**: diff the newly-generated
   file's per-animal min/max against the currently-deployed 401 operations. Any
   animal whose band would NARROW versus today's shipped value is a bug in the fix,
   not a data update — this file's own rule is WIDEN ONLY, NEVER NARROW.
3. Once fixed, correct the stale "Deploy both or neither" banner in the same commit
   (see above) and re-deploy.

## Not this item's job

Whether the ~200 widened bands are still numerically RIGHT for the `RUT_` biome each
animal now actually spawns in (versus merely still non-empty) is a follow-on
question once the join itself is repaired — flag it there, not here.
