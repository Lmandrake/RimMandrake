# PAINTED_TILES_WITH_NO_CAST_1 — 1,086 painted tiles carry no fauna at all

## what is wrong

MEASURED 2026-09-20 during `BIOME_BINDINGS_TABLE_STALE_1`'s regeneration, by
parsing every `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/*.xml` and every
`<xpath>` in the patch files, against the painted world
(`world/ASHKARR_WORLDMAP_tiles.csv`, 21,872 tiles, 27 biomes):

**26 of 27 biomes declare `wildAnimals` inline in their own BiomeDef. Two of
those declarations are EMPTY — `<wildAnimals />`.**

| def | painted tiles | cast |
|---|---:|---|
| `RUT_BlueDesert` | 1,029 | empty |
| `RUT_PropaneLake` | 57 | empty |

**1,086 painted tiles on which no wild animal can ever spawn.**

(`ZBiome_Grasslands`, 222 tiles, is the 27th — it has no local override at all,
only duplicate-removal patch ops. That is a different shape and belongs to
`PYRELANDS_WRONG_BIOME_DEF_1`, not here.)

## why it matters

An empty `<wildAnimals />` is **valid XML that loads clean**. Nothing errors,
nothing warns, and every check the biome's own work runs will pass. The player
walks into a place with no animals in it and there is no log line to explain it.

This is the same family as the three defects in the 2026-09-20 handoff: content
correct from inside the mod, wrong from inside the game.

## the split — these are two different problems

1. **`RUT_BlueDesert` (1,029 tiles) is ALREADY FILED** as
   `BLUE_DESERT_LIFE_AUTHORING_1` — its hydrocarbon biology (Swallowers,
   Burners, Pickers, the transparent fractal flora) was ratified by the owner and
   never built. ⛔ **Do not duplicate that work here.** This item records only
   that the empty cast is measured and real.
2. **`RUT_PropaneLake` (57 tiles) is NOT filed anywhere** and is the actual new
   work. 57 tiles is small, but it is a named, painted place with a sheet
   (`the_propane_lakes.md`), and it currently has nothing alive in it.

## the work

For `RUT_PropaneLake` only:

1. Read `design/Jawa/worldbuilding/biomes/the_propane_lakes.md` and
   `rosters/the_propane_lakes.json` — the roster may already hold a ruled cast
   that was simply never wired, which would make this a one-commit job. 🔑
   **Check before authoring anything: this repo absorbs and ports routinely, and
   an existing ruled roster is the common case.**
2. If a cast exists, wire it — guarded `MayRequire` per the owning mod, since
   the biome defs are `mandrake.rut.patches` and the species usually are not.
3. If none exists, this becomes a small design item, not a build one — hand the
   owner a cast proposal rather than inventing one.

## Watch out

- 🔴 **`MayRequire` tests whether the MOD is active, not whether the DEF is
  present.** It will not protect a ref against a stale deployed build. See
  `DESERT_TABLES_DEPLOYED_AHEAD_OF_SPECIES_1`.
- ⚠️ **Biome wild tables are ELEMENT-KEYED, not `<li>`-keyed.** A `<li>` parser
  returns zero rows for every biome — a failure that reads as a finding.
  Recorded in `infrastructure/state/facts/biome_rosters.md`.
- ⚠️ An empty cast may be deliberate for a lethal biome. The propane lakes are
  flammable and toxic, so "almost nothing" is plausible design — but **"almost
  nothing" and "nothing" are different**, and only the sheet can say which was
  meant.
- ⚠️ Tile counts come from the painted CSV, **one instrument**.
  `GRASSLANDS_TILES_CSV_STALE_1` is open against that same file, though it bites
  the Grasslands row, not these two.

## verify

Every painted biome either declares a non-empty `wildAnimals`, or carries a
comment naming the ruling that says it should be empty. A selftest asserts it.

## criteria

No player stands on painted ground that silently cannot hold life.
