# BIOME_CAST_DUPLICATE_ANIMALS_1 The Ash'karr cast reintroduced the duplicate-animal crash fixed on 08-10

## spec

### This is a regression, not a discovery

`D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Patches\AnimalBiomeDuplicates_Fix.xml`,
authored 2026-08-10, describes this exact defect in full, fixes three pairs, and ends with
an instruction nobody followed:

> *"Found by Utils/animal_inventory.py, which reads every active mod's Defs and
> cross-references (a) against (b) in BOTH directions. Exactly 3 duplicate (biome, animal)
> pairs existed across 1,168 animals. **Re-run that script after any mod update to
> re-check.**"*

`BiomeCast_Ashkarr.xml` was generated 2026-08-22 and replaces the `wildAnimals` roster of
**26 biomes**. The detector was not re-run. The 08-10 fix file still says three pairs exist.

### Mechanism — CONFIRMED from source

`RimWorld/BiomeDef.cs:341`, `CommonalityOfAnimal`, builds
`Dictionary<PawnKindDef,float> cachedAnimalCommonalities` with two plain `.Add()` calls and
no overwrite check. An animal reaches a biome from two directions:

- **(a) biome side** — `BiomeDef/wildAnimals`. This is what our patch REPLACES.
- **(b) animal side** — `PawnKindDef.RaceProps.wildBiomes` naming that biome.

Same animal from both directions for the same biome ⇒ `ArgumentException`. Our generator
picks animals purely on the biome side and never consults (b), so it walked straight into it.

### 🔴 The impact is silent and it outlives the exception

`cachedAnimalCommonalities` is assigned **before** the loops that fill it. When loop 2
throws, the field is left non-null and **partially populated**, so the `== null` guard never
rebuilds it. Loop 1 completed; loop 2 aborted at the first collision. **Every animal that
would have registered via `wildBiomes` after that point returns commonality 0 and never
spawns wild in that biome — for the rest of the session, with no further error.**

Third-party casualties, observed live on 2026-08-10 and recorded in the fix file's own
header — the same three will be hit again:

- **Choose Wild Animal Spawns** — static ctor throws; the CLR caches that, so the mod is
  **dead for the whole session**. Confirmed again in today's log.
- **Giddy-Up** — catches and skips; its biome mount cache never builds.
- **Biome Compatibility Project** — throws inside `LongEventHandler`, **aborting the rest
  of the post-load queue**. This is the dangerous one: whatever was queued behind it also
  did not run, and nothing says what.

## The numbers, and what is actually measured

⚠️ Three different counts are in play. Do not collapse them.

| count | value | status |
|---|---|---|
| distinct duplicate keys in today's log | **18** | MEASURED, `observed/logs/2026-08-23_Player.log.final` |
| (animal, biome) pairs enumerated by the tracing pass | **23** | reported, NOT independently verified |
| true number of colliding pairs across the live stack | — | **UNMEASURED** |

The log undercounts by construction: each biome's cache build throws at its **first**
collision, so a biome hiding three duplicates reports one. 18 is a floor, not a total.
⛔ Do not quote 18 as the size of this problem. The only instrument that can answer it is
`src/RimMandrake/Utils/animal_inventory.py`, and it has not been run since 08-10.

The 18 animals seen in the log: Diprotodon · Gigantophis · Cannok · Bardelot · AA_ArcticLion ·
DA_ArcticOwlcat · AA_CrystallineCaracal · TYR_KangarooRat · AA_BedBug ·
AA_AcanthamoebaGiganteaSmall · AA_CrescendoAnole · AA_Feralisk · AA_Metallovore ·
AA_RipperHound · JRWTorosaurus · JRWWonambi · Procoptodon · Purussaurus.
All are third-party animals (Megafauna, Alpha Animals, Beasts of the Rim, Little Critters,
Dark Ages, Star Wars Animal Collection, Jurassic Rimworld); the defect is ours, in which
animals we cast where.

## Fix

**① Measure first.** `python3 src/RimMandrake/Utils/animal_inventory.py` → `conflicts.csv`.
That is the real list. Everything below is sized off it.

**② Fix the generator, not the XML.**
`D:\Luke\dev\Rimworld\design\Jawa\fauna\gen_cast_patch.py` (source: `cast_assignment.csv`)
must refuse to cast an animal into a biome that animal's race already claims via
`wildBiomes` — resolved **after** PatchOperations, since third-party patches add
`wildBiomes` entries a raw def scan will not see. Regenerate and re-run ①; it should come
back empty.

**③ Or, as a stopgap, extend the existing fix file** —
`AnimalBiomeDuplicates_Fix.xml`, following its own stated design: always remove the
**(b)** animal-side `wildBiomes` entry, never the biome's list, each op wrapped in
`PatchOperationConditional` so an absent mod is a silent no-op. Nothing is lost in play —
the animal still spawns via the biome's own roster. This is a patch over a generator bug;
it does not close ②.

## verify

- `animal_inventory.py` reports **zero** duplicate (biome, animal) pairs.
- Next load's Player.log: zero `An item with the same key has already been added`, and
  **no** `Error in static constructor of ChooseWildAnimalSpawns.Main`.
- 🔑 Prove the silent half too, not just the loud half: pick one biome that was throwing,
  and confirm an animal that registers via `wildBiomes` actually appears in its wild animal
  table. The exception going away does not by itself prove the truncated cache is gone.

## Watch out

- 🔴 **`AnimalBiomeDuplicates_Fix.xml` currently states "exactly 3 pairs" as settled fact.**
  It is now wrong and it is the first thing a future reader will find. Correcting it is part
  of this item, not optional.
- The 08-10 file says **"Load this mod LAST"**. If the stopgap route is taken, that ordering
  constraint still holds and is easy to lose.
- Three further mods (Primordial Geysers, Biomes! Caverns, Star Wars Animal Collection) add
  these same animals into biomes our cast does **not** replace. They are not implicated
  today, but a de-dup pass in the generator has to consider them or the next cast
  regeneration reintroduces this in a different biome.
- Whether the Ash'karr campaign actually uses the 18 affected biomes is **UNMEASURED**. It
  changes the urgency, not the correctness.
- Filed by REP from a log reading plus a source read. No game test was run, and the pair
  enumeration came from a tracing pass, not from the detector.

---

## 🔴 MEASURED 2026-08-23 by BUILD — **the number is 30**, and step ① of this item is WRONG

**Do not run `animal_inventory.py` to size this.** It reports **3** — the original 08-10
pairs, unchanged — and that is a *true answer to a different question*. The script says so
itself at `src/RimMandrake/Utils/animal_inventory.py:130`: *"PatchOperation results. Patches
apply at load; this reads base XML."* ⇒ **It cannot see `BiomeCast_Ashkarr.xml`**, which is
the file that caused this regression. This item's *"① Measure first … That is the real list"*
would have had a reader conclude the regression was already fixed.

**The measurement that works:** cross the rosters `BiomeCast_Ashkarr.xml` REPLACES (26
biomes) against every `animal.wildBiomes` row in `biome_animals.csv`, which
`animal_inventory.py` does emit and which *is* the (b) side.

| count | value | what it is |
|---|---|---|
| `animal_inventory.py` conflicts.csv | **3** | ⛔ blind to our patch. Not this defect. |
| distinct duplicate keys in the log | **18** | floor — each biome throws at its FIRST collision |
| **our patched rosters × animal-side wildBiomes** | **30** | ✅ the list that was fixed |

**30 is ALSO a floor**, deliberately: a third-party `PatchOperation` that *adds* a
`wildBiomes` entry is invisible to a raw def scan. That gap cannot be closed offline today —
the def dump does not serialise `wildBiomes` at all (a `Dictionary<BiomeDef,float>`, dropped
like `wildPlants`), so there is no post-patch source to read. **Score the remainder from the
next load.**

Spread: `IceSheet` 10 · `ExtremeDesert` 10 · `AridShrubland` 6 · `SeaIce` 2 · `Desert`,
`ZBiome_DesertOasis`, `Scarlands` 1 each. By mod: Star Wars Animal Collection 15, Alpha
Animals 4, Megafauna 3, Mythic Ages 3, Beasts of the Rim 2, Dark Ages 2, Little Critters 1.

## What is DONE and what is NOT

- ✅ **③ the stopgap is shipped.** `AnimalBiomeDuplicates_Fix.xml` now carries 33 operations —
  the original 3 plus these 30 — each a `Conditional`+`Remove` on the **animal side**, never
  on our roster. Validated against the 580-mod set: **33/33 hit exactly one match, 0 errors,
  0 warnings.** Every pair has exactly one animal-side registration, so no `[2]` predicate is
  needed anywhere in the new block.
- ✅ The *"exactly 3 pairs"* header correction is in the file.
- ⛔ **② IS NOT DONE and this item stays open for it.** `design/Jawa/fauna/gen_cast_patch.py`
  still picks purely on the biome side and will reintroduce this on the next regeneration.
  🔑 That file is under `design/`, so under the owner's 2026-08-23 ruling the generator fix is
  **DECIDE's** to author and file back with `--needs deploy`.
