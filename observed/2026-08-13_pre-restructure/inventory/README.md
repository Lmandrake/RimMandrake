# observed/2026-08-13_pre-restructure/inventory/ — generated animal reference for the live 562-mod stack

_Generated 2026-08-10 by `src/RimMandrake/Utils/animal_inventory.py` **v1.4** against
`Config/ModsConfig.xml` (RimWorld 1.6.4871 rev590). Regenerate with:_

```
python src/RimMandrake/Utils/animal_inventory.py --out observed/2026-08-13_pre-restructure/inventory
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
| `animals.csv` | 1,243 | an animal ThingDef, 115 columns (identity, inheritance, temperament, combat, physiology, temperature, reproduction, production, ecology, trade) |
| `animal_attacks.csv` | 3,614 | one attack tool |
| `animal_lifestages.csv` | 3,345 | one life stage |
| `biome_animals.csv` | 4,618 | one (biome, animal) pair, **from both directions** |
| `conflicts.csv` | 3 | a duplicate (biome, animal) pair — the crash class |
| `patch_watch.csv` | 1,873 | a PatchOperation whose xpath touches an animal or biome |

**1,243 rows = 1,196 distinct defNames + 47 rows with a blank defName.** The 47
are **abstract base defs** (`<ThingDef Name="AnimalThingBase" Abstract="True">`),
which carry a `Name` but no `defName`; they are kept because they are what
inheritance resolves against.

Mod-vs-mod overrides are a *separate* and much smaller thing: exactly **3
contested defNames** — `Armadillo` and `Penguin` (Beasts of the Rim (Continued)
vs Odyssey) and `AA_Eyeling` (Alpha Animals vs Alpha Memes). The
`duplicateDefName` column names every mod involved; last in load order wins.

_(Corrected 2026-08-10. This section previously read "1,197 distinct defNames,
the 46-row gap is mods redefining each other's animals", conflating abstract
bases with overrides and overstating the override count by 15×. The
`duplicateDefName` column was always right; the prose misread it.)_

## Trust boundary — read before relying on a number

**This reads base XML. PatchOperations have not run.** Anything another mod's
patch creates, edits or deletes is invisible. That is not theoretical: the five
dangling `wildAnimals` entries that kept Choose Wild Animal Spawns dead exist
only *after* Primordial Geysers' patch applies, so they appear in **no** CSV
here. `patch_watch.csv` is the mitigation — it tells you where to look, not what
the result was. For post-resolution truth you need a live dump via RimBridge.

`<ParentName>` inheritance **is** now resolved cross-mod (v1.3), with RimWorld's
own merge semantics. What remains approximate: duplicate abstract `Name`s across
mods (last-in-load-order wins here; the game's winner is not guaranteed to
match), `MayRequire` gating on inherited list nodes (not evaluated, so an
inherited `comps` list can include Anomaly-gated entries a real load would
drop), PawnKindDef inheritance (not resolved, so `combatPower` /
`ecoSystemWeight` / `wildGroupSize*` still read own-XML only), and
`shortHashCandidate` (correct algorithm, but the game resolves collisions across
the whole loaded set — treat as a candidate until cross-checked live).

## v1.3 / v1.4 — two independent fixes, 2026-08-10

**v1.3 resolved `<ParentName>` inheritance.** v1.2 recorded `parentName` as a
column and then read every field off the def's *own* element, so most animals
reported blank for fields their abstract base supplies. Coverage moved a long
way: `mass` 0.6 % → 100 %, `tickerType` 1 % → 100 %, `thinkTreeMain` 7 % → 99.7 %,
`bloodDef` 11 % → 99.4 %, `hasGenders` 10 % → 98.7 %, `toxicResistance` 9 % →
98.5 %, `lifeExpectancy` 86 % → 98.4 %, `moveSpeed` 93 % → 98.3 %, `comfyTempMin`
87 % → 98.1 %, `trainability` 80 % → 91.7 %. Attacks and life stages grew with it
(3,353 → 3,614 and 3,169 → 3,345) because inherited `tools` / `lifeStageAges`
now resolve. Row count is unchanged at 1,243, and `unresolvedParent` is empty
for every row.

**v1.4 fixed four dead xpaths** — unrelated to inheritance, and the more
instructive bug. These columns read fields RimWorld 1.6 no longer uses, so they
showed near-0 % coverage and were misread as an inheritance problem:

| Column | Was reading | 1.6 reality |
|---|---|---|
| `wildness` | `race/wildness` (1 def) | a **StatDef**: `statBases/Wildness` (1,054 defs) → now **89.1 %** |
| `deathActionWorker` | `race/deathActionWorkerClass` (0 defs) | `race/deathAction`, as a `workerClass` **child** (63) or `Class` **attribute** (14) → now **6.2 %** |
| `nameOnNuzzleChance` | `race/nameOnNuzzleChance` (0 defs) | gone entirely; **column removed** |
| `insulationCold/Heat` | `statBases/Insulation_*` (0 defs) | apparel-only stats; no animal has one |

Consequence of the last row: `effectiveTempMin/Max` are always exactly
`comfyTempMin/Max`. The derivation is kept (it is correct, and would pick up a
modded insulation stat) but it is **not** evidence that insulation was
accounted for.

The `deathAction` fix is worth remembering as a shape lesson: the first
correction read only the `Class` attribute and silently lost 63 of 77 defs —
including Boomalope and every other explode-on-death animal, the exact class
most worth flagging. **A 0 % column is far more likely to be a dead xpath than a
genuinely empty field.**

### One behaviour change worth knowing

Three defs in *Mythic Ages: Megafauna Bestiary* (`MA_Plastemmoth`,
`MA_PlastemmothAlpha`, `MA_Harpeagle`) declare `<comps>` **twice** in one
ThingDef. RimWorld assigns the field per node, so the last block wins and the
first is dead XML. v1.2 concatenated both and reported yields that do not exist
in game (Plastemmoth is not shearable; Harpeagle does not lay eggs). v1.3+
reproduces last-wins. Note this only applies to defs that *have* a parent, so it
is not a general duplicate-node fix.

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

- `src/RimMandrake/Utils/rimworld_loadset.py` — the shared resolver these CSVs are built on.
  `validate_patch.py` carries an intentional copy (it ships as a portable skill).
- `vendor/wisdom/benign_log_errors.md` — what the live log says, triaged.
- `observed/2026-08-13_pre-restructure/live_mod_inventory.md` — the human-readable mod list.
