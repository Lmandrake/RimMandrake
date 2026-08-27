# 🔴 THE DIAGNOSIS BELOW IS WRONG. Measured 2026-08-26 19:5x by BUILD, from the capture and the 1.6 source.

**The falsifiable prediction this item wrote down has been settled early, and it fails.**
That is the prediction doing its job — read it, then read this.

## What the diagnosis claimed, and the one check that kills it

It claimed the 181 zeros are `BiomeDef.CommonalityOfAnimal`'s half-built cache returning
`0f`, published by `DefDumper.cs:526`.

⛔ **`DefDumper.cs:526` does not write the field the 181 were measured in.** That line
writes the `biomeAnimals` block of `animals.json`. The 181 zeros are in
`defs/BiomeDef.json`, under `fields.wildAnimals[].commonality` — the **record's own
field**, produced by plain reflection over `List<BiomeAnimalRecord>`.

⛔ **And `CommonalityOfAnimal` never writes back into a record.** Read from
`RimWorld/BiomeDef.cs`, lines 340-360: it only ever *reads* `wildAnimals[i].commonality`
into its dictionary. No path in it can zero the record.

⇒ The broken cache cannot be the cause, so *"remove the 27 duplicate pairs and the next
capture must show 744 of 744 non-zero"* would have failed, and the failure would have been
blamed on the de-dup patch.

## What is actually true, measured

`AridShrubland`, our patch writes 29 entries, every one non-zero. The capture holds
exactly those 29 — none added, none dropped — and **16 read `commonality: 0`** in the
record. Same XML shape, same comment placement, same indentation for the zeros and the
non-zeros; nothing in our file distinguishes them.

🔑 **The zeroing is a property of the ANIMAL, not of the biome or of our patch.** Across
all 67 biomes in the capture that carry a `wildAnimals` list:

```
distinct animals                                   736
zeroed in EVERY biome they appear in               168
MIXED - zero in one biome, non-zero in another     154

Tiger         zero in  7 biomes, non-zero in 0
Gazelle       zero in 12,                     0
Fox_Fennec    zero in 12,                     0
PrairieDog    zero in  6,                     0
MonitorLizard zero in  4,                     0
Megavole / Cougar / Urusai / Torton      our values intact
```

⚠️ The mixed count also **contradicts this item's own claim** that *"not one animal is
zeroed in one biome and fine in another"* — that was true only within the 26 biomes we
patch, and it does not generalise.

### Ruled out, each by a check rather than by argument

- **Not the cache** — the record is not written by `CommonalityOfAnimal` (source).
- **Not our XML** — the zeros and the non-zeros are byte-identical in shape; the deployed
  game copy was read, not the repo copy.
- **Not "the value moved to the animal side"** — `race.wildBiomes[AridShrubland]` is
  absent for all 16 zeros *and* all 13 non-zeros in the capture.
- **Not a parse failure on our comments** — the comment sits after the closing tag, so
  `xmlRoot.FirstChild` is the text node; and it is identical on the entries that read fine.

## What is NOT yet known, and must not be guessed

**Which mod zeroes them.** The shape — vanilla Earth fauna (Tiger, Gazelle, fennec fox,
prairie dog, monitor lizard) zeroed in *every* biome — reads like a deliberate suppression
of Earth animals on a Star Wars planet, which would make a large share of the 181
**intended** rather than a defect. ⛔ **That is a hypothesis and nothing more.** A search of
the 1,254-mod workshop tree is running; until it names a file and a line, nobody should act
on it.

## What changes for the reader right now

- ⛔ **Do not treat "744 of 744 non-zero in the next capture" as this item's pass condition.**
- ✅ **The next capture answers it directly anyway**, because `DUMPER_SWALLOWS_CACHE_THROW_1`
  is fixed (`85e3ced2`): every `biomeAnimals` row now carries **`commonalityDeclared`**
  (the record) beside **`commonalityEngine`** (the computed answer), and
  `commonalityEngineError` when the engine throws. A zero that is the record's own value
  and a zero that is a dead cache stop looking alike.
- ✅ `BIOME_DUPLICATES_STILL_LIVE_1` is unaffected. The duplicate crash is real, its fix is
  deployed, and its own log-based verify stands. These were never one item; treating them
  as one is what produced the wrong diagnosis.

---

## ✅ DIAGNOSED, 2026-08-26, from the source — SAME BUG as `BIOME_DUPLICATES_STILL_LIVE_1`

Not a second defect. **These 181 zeros are the blast radius of the duplicate-animal crash**, and
they are the first measurement of how much of the planet's cast it actually costs.

**The mechanism, read not inferred** — `RimWorld/BiomeDef.cs`, `CommonalityOfAnimal`:

```csharp
if (cachedAnimalCommonalities == null)
{
    cachedAnimalCommonalities = new Dictionary<PawnKindDef, float>();   // assigned FIRST
    for (int i = 0; i < wildAnimals.Count; i++)
        cachedAnimalCommonalities.Add(wildAnimals[i].animal, wildAnimals[i].commonality);
    foreach (PawnKindDef allDef in DefDatabase<PawnKindDef>.AllDefs) { ...wildBiomes... }
}
if (cachedAnimalCommonalities.TryGetValue(animalDef, out var value)) return value;
return 0f;                                     // <- everything the build never reached
```

1. The dictionary is **assigned before the loop**, so when `Add` throws on the duplicate key it is
   left **partially built and non-null**.
2. Every later call skips the rebuild (non-null) and **returns 0f** for every animal the loop
   never reached.
3. `RimDefDump/Source/DefDumper.cs:526` serialises `b.CommonalityOfAnimal(pk)` — the *engine's
   answer*, not the record's field. So the capture is reporting exactly what the game believes.
4. `AllWildAnimals` yields only kinds whose commonality is `> 0f`. **An animal stuck at 0 is not
   in the biome's animal list at all.**

🔑 **This also explains the one thing that made no sense: the zeroing is per-ANIMAL, never
per-biome.** 157 distinct animals are zeroed in *every* biome we place them in, and **not one**
animal is zeroed in one biome and fine in another. That is what a truncated build looks like when
every biome's list is written by the same generator in the same order — the cut falls in the same
place each time.

## The prediction this makes, and it is falsifiable

Once `AnimalBiomeDuplicates_Generated.xml` removes all 27 duplicate pairs, the cache build no
longer throws, so it completes:

> **The next capture must show 744 of 744 non-zero** for the 26 biomes `BiomeCast_Ashkarr.xml`
> writes — up from 563. `python3 src/RimMandrake/Utils/biome_animal_conflicts.py` must
> simultaneously report **0 pairs**.

⛔ **If the pairs go to 0 and the zeros do NOT, this item is a real second defect after all** and
the diagnosis above is wrong. That is the whole point of writing the prediction down first.

---

# BIOME_CAST_COMMONALITIES_ZEROED_1 — 181 of the planet's 744 animal weights read 0 in the live game

Measured 2026-08-26 by BUILD against the def dump capture `2026-08-26T14-20-04Z` (582 mods,
post-patch, taken from the running game). **Not yet diagnosed — this item is the measurement.**

## The measurement, and it is clean

`src/Jawa/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml` writes the `wildAnimals` roster of 26
biomes: **744 (biome, animal) entries**, every one with a non-zero commonality — the generator
writes no zeros at all (33 distinct values, from `1.0` down to `0.0086`).

In the capture, for those same 26 biomes:

```
entries our patch writes          744
present in the live biome list    744      <- nothing was dropped
value matches ours exactly        563
value DISAGREES with ours           0      <- nothing was overwritten with a different number
value reads 0                     181
entries in those biomes NOT ours    3
```

🔑 **Zero mismatches and 181 zeros.** So it is not "another mod rewrote our numbers" — the
entries are either exactly ours or zero.

## Why it matters

`BiomeAnimalRecord.commonality` is the weight `BiomeDef.CommonalityOfAnimal` returns.
**A commonality of 0 means the animal is registered in the biome and can never be chosen.**
If these 181 are genuinely zero at runtime, roughly a quarter of the planet's hand-authored
animal cast does not spawn — and nothing anywhere reports it, because the def is present, the
patch applied, and the entry exists.

## What has been ruled OUT already, so nobody repeats it

- **Not dropped entries.** 744 written, 744 present.
- **Not our generator writing zeros.** It writes none; measured over the file.
- **Not a within-list duplicate.** Zero biomes in the whole capture have the same animal twice
  in one `wildAnimals` list.
- **Not the shape trap.** `BiomeAnimalRecord.LoadDataFromXmlCustom` reads
  `xmlRoot.FirstChild.Value`, i.e. `<AnimalName>0.4</AnimalName>` — which is exactly what the
  generator emits. Read from the 1.6 source, not assumed.
- **Not confined to us.** 65 of 67 biomes in the capture carry zero-commonality entries,
  including ones this project never patches (`GlacialPlain` 129 of 183, `Glowforest` 104 of 181).
  ⇒ **A zero in a biome list may well be normal and mean something**; that is the first thing to
  settle, because if it is normal this item is a false alarm.

## What to do next, in order
1. **Read the mechanism.** `BiomeDef.CommonalityOfAnimal` and how `cachedAnimalCommonalities` is
   built — does a 0 in `wildAnimals` mean "never", or is the weight taken from somewhere else
   (the animal's own `wildBiomes`, a pollution/coastal list, a `MayRequire` that did not apply)?
   ⛔ Do not fix anything before this is answered. One negative is not a mechanism.
2. If 0 really means never: find what distinguishes the 181 from the 563. Sample to start with —
   `Volcano` has exactly one, `VAEWaste_Pestigator`; `AridShrubland` has 16 of 29.
3. Only then decide whether the generator, the load order, or another mod is responsible.

## criteria
- [ ] A sourced answer to "what does commonality 0 mean here", written down.
- [ ] If it means never: the 181 explained, and either fixed or accepted with a reason.
- [ ] A live check that at least one of the 181 does or does not spawn in its biome.
