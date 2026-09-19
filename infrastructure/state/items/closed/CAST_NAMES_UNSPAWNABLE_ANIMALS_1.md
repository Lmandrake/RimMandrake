# ✅ THE CAUSE IS ANSWERED: the owner cut them himself, with Cherry Picker.

Updated 2026-08-26 21:0x by BUILD. **This is no longer "a mod switched them off" — it is that
our roster cast animals the owner had already removed from the game.**

`Config/Mod_3521312241_Mod_CherryPicker.xml` is his own selection: **1,342 cuts.** Over the
whole population, **167 of the 168 always-off animals are on it, and 0 of the 414 always-alive
animals are.** Cherry Picker suppresses a cut animal by setting its biome commonality to 0 and
leaving the entry in place — and ⛔ **its cuts are invisible to the def dump**, so every animal
is still PRESENT as ThingDef and PawnKindDef.

## What this changes about the decision below

- ⛔ **"Un-suppress them" is off the table entirely.** These are the owner's deliberate cuts;
  re-enabling one contradicts him, not a mod.
- ✅ **The question narrows to one thing: what replaces each slot.** The lore filter is already
  applied — he cut Badger, Bluebird, Cat, YorkshireTerrier and 1,338 others on purpose.
- ⚠️ **The losses that still need answering are the deliberate Star Wars picks** —
  `AA_CrystallineCaracal`, `Dinopithecus`, `JRWTorosaurus`, `Titanoboa`, `MA_Capryak`. If he cut
  those, the cast was designed against a roster he had already narrowed, and the biomes need
  refilling from what survives. `ZBiome_Badlands` is 13 of 29 down; `Wasteland` 9 of 30.
- ✅ **The generator can no longer do this silently.** `gen_cast_patch.py` reads the cut list,
  comments the entry out, names it, and prints the per-biome loss.

---

# CAST_NAMES_UNSPAWNABLE_ANIMALS_1 — a quarter of the authored animal cast cannot appear

Measured 2026-08-26 by BUILD against capture `2026-08-26T14-20-04Z` (582 mods, post-patch).
Re-runnable: `python3 src/RimMandrake/Utils/biome_commonality_zeroed.py --ours --animal`

## spec

**A quarter of Ash'karr's hand-authored animal cast is registered in its biomes and can
never be chosen.** DECIDE decides what replaces each one, or that the slot stays empty.

## The measurement

`src/Jawa/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml` writes **744** (biome, animal) entries
across 26 biomes, every one at a non-zero weight. In the live game:

```
alive                          566
commonality 0                  181      <- registered, and can never be chosen
distinct animals ALWAYS OFF    157      (0 in every biome we place them in)
```

🔑 **`BiomeDef.AllWildAnimals` only yields kinds whose commonality is `> 0f`.** A zeroed
animal is not in the biome's animal list at all. The def is present, the patch applied, the
entry exists, and **nothing anywhere reports it.**

## Why this is a CONTENT question and not a bug to fix

⛔ **The zeros are almost certainly deliberate, and not ours to undo.** Fauna-replacement mods
suppress vanilla animals by REPLACING the commonality with 0 rather than removing the entry.
Proven on `TemperateForest`, a vanilla biome this project never patches: Core declares 36
animals and **9 read 0** — Badger, Bluebird, Crow, Gazelle, Mink, Porcupine, Sparrow, Swan,
Tortoise — while the other 27 keep their vanilla values exactly.

⇒ Suppressing Earth fauna is what those mods exist to do, and it is what a Star Wars desert
world wants. **The defect is that our roster did not know**, so it spent a quarter of its
weight on animals that were switched off underneath it.

⛔ **Two explanations are DEAD; do not propose either.** It is not
`BiomeDef.CommonalityOfAnimal`'s duplicate-key cache — that method only ever READS a record.
It is not a dumper defect — these zeros are in `defs/BiomeDef.json`'s record field, not the
computed value in `animals.json`. Full argument: `BIOME_CAST_COMMONALITIES_ZEROED_1`.

## The decision this needs

**For each of the 157: replace it in the roster, or leave the slot empty.** The shape of the
list is what makes this DECIDE's rather than BUILD's — it is which creatures inhabit Ash'karr.

⚠️ **Some are obviously right to lose** (Badger, Bluebird, Cat, YorkshireTerrier, Alphabeaver
on a Star Wars desert world). ⚠️ **Others are not** — `AA_CrystallineCaracal`, `Dinopithecus`,
`JRWTorosaurus`, `Titanoboa`, `MA_Capryak` were chosen deliberately and their loss thins the
biomes they were casting for. `ZBiome_Badlands` loses **13 of 29**, `Wasteland` **9 of 30**.

## verify
`biome_commonality_zeroed.py --ours` against a capture taken after the roster is revised:
the count of `*`-marked zeros falls by however many were replaced, and no biome the revision
touched gains one.

## criteria
- [ ] Every one of the 157 is either replaced by a spawnable animal or accepted as lost, with the reason.
- [ ] No biome ends with fewer live entries than it had before the revision.
- [ ] ⛔ The revision does not attempt to un-suppress a zeroed animal — that fights a mod's own design and is out of scope until someone decides otherwise.

## Watch out
- 🔑 **A zero can only be seen from a CAPTURE**, never from mod XML: the value is set by a
  PatchOperation after our own replace runs. `animal_inventory.py` and any disk-only reader
  will report the roster as healthy.
- ⚠️ **Which mod does the zeroing is not yet known.** It does not block the content decision —
  the animals are off either way — but it decides whether "un-suppress it" is ever an option.
- ⚠️ `biome_commonality_zeroed.py --animal` without `--ours` shows 322 animals carrying a zero
  across all 67 biomes, 168 always off. **Most of those are not ours and are not a defect.**

---

# CLOSED 2026-08-28 by BENCH — already done; verified offline

The decision this item waited on was made and executed on 2026-08-27:
- `b02c2fcd` refilled the 181 dead slots WITHOUT re-casting (refill_cast.py, patch-not-reallocate).
- `1e7cf0ec` / `72b602fc` put the art rejections and the no-Earth-animals rule into the generator as data.
- `0d7f5001` gave the two cast-less biomes their casts.

Verified today, offline:
- `refill_cast.py` dry-run against the LIVE Cherry Picker settings: 804 rows carried, **vacated 0** — no current row names a cut, art-rejected, or Earth creature. MEASURED.
- Deployed `BiomeCast_Ashkarr.xml` is byte-identical to the repo copy (`cmp`). MEASURED.
- The headline "157 always off" reads the 2026-08-26 capture, which predates the fix — the fingerprint rule, not a live defect.

Criteria: replaced-or-accepted ✅ (refill + exclusion data) · no biome thinner ✅ (804 rows carried, zero vacated) · no un-suppression ✅ (refill only ever fills; the cut list is an input).

**Live proof is NOT this item's**: `CAST_LIVE_SPAWN_CHECK_1` owns the post-deploy capture check.
Incidental repair: restored `design/Jawa/fauna/dumppath.py`, deleted by kruft pass `9960d4bf` while still imported by `biome_commonality_zeroed.py` and `refill_cast.py`.
