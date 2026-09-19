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

## ⏳ THE GENERATOR GUARD IS WRITTEN AND HAS NEVER RUN — 2026-08-26, BUILD

`design/Jawa/fauna/gen_cast_patch.py` now unions its disk walk with the newest def dump capture,
so a `wildBiomes` entry that only a PatchOperation creates can no longer hide from its de-dup pass.
Its docstring's claim that *"the def dump cannot help, because it does not serialise wildBiomes at
all"* is corrected in place — a capture does carry `ThingDef.fields.race.wildBiomes`, measured.

⛔ **UNPROVEN.** The regeneration was started and killed before it finished (the disk walk over
1,254 workshop mods takes minutes), so the guard has never produced output.
`src/Jawa/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml` is **untouched** — 26 operations, byte-identical
to `1631b4d4`, confirmed after the kill.

**To finish it:**
```
python3 design/Jawa/fauna/gen_cast_patch.py          # minutes; rewrites the cast patch
git diff src/Jawa/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml
```
🔑 **Read that diff before shipping it.** The generator REPLACES the wildAnimals roster of 26
biomes; the only intended change is that its DE-DUP section should now emit ~27 removals instead of
the handful a disk-only scan finds. **A change to the cast rosters themselves is not intended** —
if the diff shows one, stop and say so. `git checkout --` restores it; the committed copy is the
authored planet.

---

## ✅ THE GENERATOR GUARD HAS NOW RUN — 2026-08-26 19:15, BUILD. Commit `46a3cfa7`.

It took **8 minutes** (the disk walk over the workshop mods on a `/mnt/d` mount), and it
did exactly what the "to finish it" block above asked for.

```
animal-side: +6814 pair(s) only the capture could see (2026-08-26T14-20-04Z)
wrote design/Jawa/fauna/BiomeCast_Ashkarr.xml: 26 biomes, 746 records, 56 duplicate pair(s) de-duped
⚠️ 2 cast entries SKIPPED - not PawnKindDefs: Desert/SWPotF_RaceDef_ysalamir, PoisonForest/GiantAnt_Race
```

**29 → 56 de-dup pairs**, which is exactly the disk-only 29 plus the capture-only 27. The
guard works.

### The invariant the block above demanded, measured rather than eyeballed

> *"A change to the cast rosters themselves is not intended — if the diff shows one, stop
> and say so."*

Parsed both copies into `{biome: {animal: commonality}}` and compared:

```
biomes old/new           26 / 26
records old/new         744 / 744
biome set differs        none
biomes with a cast change   0
```

**Zero.** The only change in the file is the de-dup section. Nothing to stop for. (The
generator's own "746 records" is its pre-skip count; the two unresolvable entries were
skipped before this run too, which is why 744 is unchanged.)

### 🔴 Nothing new to deploy — and the reason is a trap worth more than the run

All 56 pairs are **already covered** by the shipped `AnimalBiomeDuplicates_Fix.xml` (34)
+ `AnimalBiomeDuplicates_Generated.xml` (27) = 61. But **five shipped pairs are NOT in
the 56**:

```
AridShrubland x Armadillo · Desert x Armadillo · Scarlands x AA_CrystallineCaracal
TropicalSwamp x Titan     · ZBiome_DesertOasis x TYR_KangarooRat
```

🔑 **They are absent because our own removal already worked.** The capture is taken after
every PatchOperation, so **a pair we have already fixed is invisible in it — the fix hides
its own evidence.**

⛔ **So the de-dup section this generator emits is a FLOOR, not a roster.** Had anyone
shipped it *as* the de-dup file, those five removals would have been dropped and the five
pairs would return on the next load with nothing in any log naming them. The shipped set
must stay the **union of every pair ever found**. Written into
`design/Jawa/fauna/gen_cast_patch.py`'s docstring and into the comment it emits, so the
next person to run it reads it before the diff.

### What is still owed, and it is unchanged

The `## verify` block above, on the **next load's log** — `harvest_log.py` DEAD MODS back
to 0, zero `same key has already been added`, then `biome_animal_conflicts.py` = 0 pairs
against the new capture. That is `needs: harvest`; no bridge, no clicking.

---

## 🔴 STILL LIVE ON THE 2026-08-27 LOAD — and the cause is the cast regeneration

**The `## verify` block above FAILS.** Scored from the log of the running game, which is the
channel that block asked for:

    grep -c "same key has already been added"   ->  12     (criterion: 0)
    distinct keys: Purussaurus · Procoptodon · JRWWonambi · JRWTorosaurus · AA_RipperHound
                   AA_Metallovore · AA_FissionMouse · AA_Feralisk · AA_CrescendoAnole
                   AA_BedBug · AA_ArcticLion · AA_AcanthamoebaGiganteaSmall
    `Error in static constructor of ChooseWildAnimalSpawns.Main` still present.

✅ **Both de-dup files ARE deployed and byte-identical to the repo** — checked, not assumed.
✅ **Load order is NOT the cause** — Jawa Patches is **573**, well after More Vanilla Biomes
(232) and Alpha Animals (422), so our removals run last. I checked this because it was my first
hypothesis and it is wrong.

## 🔑 The cause: the cast grew after the de-dup union was computed
`BiomeCast_Ashkarr.xml` was regenerated at **`c325daad`, 2026-08-26 21:02** — from 26 biomes /
744 rows to **28 biomes / 801 rows, 0 removals** — and deployed at 20:59. The shipped de-dup
union was computed against the **old** cast. Every (biome, animal) pair the new rows introduced
is uncovered.

**Measured from source rather than from a capture, deliberately.** A pair our own removal has
already cured is invisible in a post-patch capture — the fix hides its own evidence — so a
capture can only ever yield a floor. Computing (a row in our shipped cast XML) ∩ (that animal's
`race.wildBiomes` naming that biome):

    46 collisions across 16 biomes
    21 already covered by the two shipped files
    25 NOT covered  <- appended to AnimalBiomeDuplicates_Generated.xml, union style

✅ **The method validates:** it independently reproduces **8 of the 12** keys the live log
names. The other four — `JRWTorosaurus`, `JRWWonambi`, `Procoptodon`, `Purussaurus` — are pairs
another mod's `PatchOperationAdd` creates, which neither side of this computation can see.

## ⚠️ THIS IS NOT PROVEN TO CLOSE IT, AND MY FIRST DIAGNOSIS WAS UNSOUND

🔴 **I reported "the shipped removals do not work" and then withdrew it. Read why before
repeating either.**

The evidence looked damning: `AA_ArcticLion` still declares `AB_PropaneLakes` in the capture,
`AA_Feralisk` still declares `AB_MiasmicMangrove`, `JRWTorosaurus` still declares
`ZBiome_Badlands` — and a correctly-formed, validated removal for each is shipped
(`AnimalBiomeDuplicates_Generated.xml:84`). Load order is not the excuse: Jawa Patches is
**573**, Alpha Animals **422**, More Vanilla Biomes **232**, and nothing after 573 touches
biomes. The adding patch even uses the **identical named-child form** our xpath expects
(`<AB_PropaneLakes>0.1</AB_PropaneLakes>` into `/race/wildBiomes`), so a shape mismatch is out.

⛔ **But the capture cannot testify about the fix.** `AnimalBiomeDuplicates_Generated.xml` was
written **2026-08-26 09:04**; the capture is **2026-08-26T14:20**. A capture is written by a
running game, and **defs parse only at startup** — if that process launched before 09:04 (the
run sheet records a load at 06:36 that day) it never loaded the file, and every "still declares
it" reading above is a reading of a game with no fix in it. **I did not establish the launch
time, so I cannot say which.**

⚠️ **And a second self-inflicted error nearly shipped as a finding.** An earlier pass here
reported `JRWTorosaurus` as *already fixed* — because it tested `isinstance(wildBiomes, dict)`
when `wildBiomes` is a **list** of `AnimalBiomeRecord`. The type check failed and returned a
clean `False`, which reads exactly like "the entry is gone". 🔑 **Print the value, not a
predicate over it**, the first time you touch an unfamiliar field.

## What IS established
1. The 2026-08-27 load throws **12** duplicate-key errors. The `## verify` criterion FAILS.
2. Both de-dup files are deployed and byte-identical to the repo.
3. `BiomeCast_Ashkarr.xml` was regenerated at `c325daad` (26 biomes/744 rows → **28/801**,
   0 removals) and deployed **2026-08-26 20:59** — after the capture and after the de-dup union
   was computed. New cast rows create pairs the union was never asked about.
4. Source-side, 46 collisions exist, 21 already covered, **25 were not**; those 25 are appended
   here, union style, and validate **0 errors / 0 warnings**. Several report "0 nodes on disk",
   which is expected for a pair another mod's patch creates.

## ⛔ What settles it, and nothing short of this will
**A def dump taken from a process launched AFTER 2026-08-26 20:59.** The newest is
`2026-08-26T14-20-04Z`. Until then, "still declares it" cannot be told from "never loaded the
fix", and a clean log on the next load cannot be told from luck. The dumper is one of the two
assemblies in `DOWN_WINDOW_ASSEMBLY_DEPLOY_1`.
