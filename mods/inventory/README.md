# mods/inventory/ — generated animal reference for the live 562-mod stack

_Generated 2026-08-10 by `Utils/animal_inventory.py` **v1.2** against
`Config/ModsConfig.xml` (RimWorld 1.6.4871 rev590). Regenerate with:_

```
python Utils/animal_inventory.py --out mods/inventory
```

_Takes about 3 seconds. **Re-run after any mod add, remove, or update** — these
CSVs are a snapshot of a mod set, not of RimWorld._

---

## Why this is committed

This is the offline ground truth for "does this animal actually exist, and where
does it come from". It exists so we can answer that **without spending a
23-minute game load**, and so patches reference animals that are really there.
It already paid for itself: it predicted the Armadillo/Titan duplicate crash
before the game ever threw it.

## What is in here

| File | Rows | One row is |
|---|---|---|
| `animals.csv` | 1,243 | an animal ThingDef, ~112 columns (identity, temperament, combat, physiology, temperature, reproduction, production, ecology, trade) |
| `animal_attacks.csv` | 3,353 | one attack tool |
| `animal_lifestages.csv` | 3,169 | one life stage |
| `biome_animals.csv` | 4,618 | one (biome, animal) pair, **from both directions** |
| `conflicts.csv` | 3 | a duplicate (biome, animal) pair — the crash class |
| `patch_watch.csv` | 1,873 | a PatchOperation whose xpath touches an animal or biome |

**1,243 rows but 1,197 distinct defNames.** The 46-row gap is mods redefining
each other's animals; the `duplicateDefName` column names every mod involved.
Last mod in load order wins, so that column is where override surprises live —
e.g. `Armadillo` is listed as `Beasts of the Rim (Continued) | Odyssey`.

## Trust boundary — read before relying on a number

**This reads base XML. PatchOperations have not run.** Anything another mod's
patch creates, edits or deletes is invisible. That is not theoretical: the five
dangling `wildAnimals` entries that kept Choose Wild Animal Spawns dead exist
only *after* Primordial Geysers' patch applies, so they appear in **no** CSV
here. `patch_watch.csv` is the mitigation — it tells you where to look, not what
the result was. For post-resolution truth you need a live dump via RimBridge.

Also approximate: `<ParentName>` inheritance (best-effort, one graph) and
`shortHashCandidate` (correct algorithm, but the game resolves collisions across
the whole loaded set — treat as a candidate until cross-checked live).

## What v1.2 fixed, and why the count went UP

v1.1 resolved mod folders with a hardcoded `("1.6", "1.5", "Common", "")` list
and never read `LoadFolders.xml`. It was wrong in **both** directions —
85 defs out of ~1,200, about 7%:

**24 phantom animals removed.** Defs that are on disk but that the game never
loads. Both clusters are ones we independently hit as live bugs today:

- **12 from Vanilla Animals Expanded** — its `1.6NotOdyssey` folder, excluded by
  `<li IfModNotActive="Ludeon.RimWorld.Odyssey">`. Includes exactly the
  `AEXP_Badger` / `Moose` / `Muskox` / `Porcupine` whose absence produced the
  null-key crash fixed by `BiomeAnimalDanglingRefs_Fix.xml`.
- **12 from Biomes! Caverns** — 1.5-only defs, dropped in 1.6. These are the
  `BMT_*` names that TraderGen and Primordial Geysers still reference
  (`benign_log_errors.md` §1.11).

**61 real animals added.** Nested and conditional folders v1.1 could not see —
Alpha Mechs (20), Vanilla Genetics Expanded (18), Big and Small (9), Caravan
Adventures (6), Alpha Animals (3) and others. Those were simply missing before.

The lesson generalises past this tool: **the filesystem is a superset of the load
set, and the gap is not random.** See
`skills/rimworld-modding/references/traps.md`.

## Related

- `Utils/rimworld_loadset.py` — the shared resolver these CSVs are built on.
  `validate_patch.py` carries an intentional copy (it ships as a portable skill).
- `mods/benign_log_errors.md` — what the live log says, triaged.
- `mods/live_mod_inventory.md` — the human-readable mod list.
