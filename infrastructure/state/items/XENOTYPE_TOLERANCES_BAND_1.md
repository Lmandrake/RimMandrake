## spec
🔴 **The third and last leg of `NORMALIZE_TEMPERATURE_TOLERANCES_1`.** Plants shipped
(`PlantTolerances_Ashkarr.xml`, 577) and animals shipped (`AnimalTolerances_Ashkarr.xml`, 456).
**Xenotypes are untouched.** MEASURED 2026-08-23 by BUILD, from the def dump plus the
decompiled source; the numbers below are the whole basis for the work.

### The mechanism, confirmed from source — and it is NOT on the XenotypeDef
Tolerance is `StatDef ComfyTemperatureMin`/`Max` (`StatDefOf.cs:56`), read through
`GenTemperature.ComfortableTemperatureRange` (`GenTemperature.cs:58`).
🔑 **`SafeTemperatureRange` is comfy ±10 °C** (`GenTemperature.cs:86`) — that, not comfy, is
the hypothermia/heatstroke boundary, so it is the number to reason with.
Genes feed it in `StatWorker.GetValueUnfinalized` (`StatWorker.cs:184-207`) via `GeneDef`'s
`statOffsets`, `statFactors` and `conditionalStatAffecters`. Every shipped temperature gene
uses `statOffsets` only.

### The gap
⚠️ **A premise in the parent item is wrong.** "−17…+40 for a baseline human" is a **clothed**
human. Baseline naked `ThingDef Human` `statBases` is **ComfyTemperatureMin 16, Max 26** →
safe **6…36**.

| | |
|---|---|
| our 69 species, median comfy | **16…26** — i.e. exactly unmodified |
| **35 of 69** carry any temperature gene; **34 carry none** | offsets present are only ±4.5…±20 |
| ground | **−82.0 … +66.1 °C** |
| **cold shortfall** | 🔴 **88.0 °C** |
| **heat shortfall** | **30.1 °C** |
| best cold performer (Bothan/Chiss/Ortolan/Pantoran) | still **68 °C** short |
| best heat performer (Jawa/Falleen/Tusken) | still **10.1 °C** short |

The 34 with nothing: Abednedo, Anzati, Aqualish, Bith, Cathar, Cerean, Chagrian, Dathomirian,
Echani, Feeorin, Gamorrean, GeonosianVariants, Gungan, Herglic, Iridonian, Ithorian, Kaminoan,
KelDor, Lasat, Mimbanese, Muun, Nagai, Pyke, SithKissaiPureblood, SithMassassi, SithZ,
Sullustan, Taung, Togruta, Twilek, Ugnaught, YoderForceGremlin, Zeltron, Zygerrian.

## the three routes, and why route 1 is recommended
1. ⭐ **Patch `ThingDef Human` `statBases` ComfyTemperatureMin/Max.** ONE operation. Moves every
   humanlike — our 69, vanilla xenotypes, every NPC faction — and **preserves the existing gene
   offsets as relative flavour**, so Jawa stay the heat-hardy ones and Chiss the cold-hardy ones.
   🔑 It is the only route that reaches the 34 species with no temperature gene without touching
   them one by one, and it matches the precedent already set: plants and animals were both
   normalized by moving the BASE field, not by adding modifiers.
2. A new GeneDef plus 69 `PatchOperationAdd`s into each `<genes>`. Per-species control, but 69
   ops, a biostat cost each, and ⚠️ it must carry **no `MinTemperature`/`MaxTemperature`
   exclusionTag** or it silently conflicts with the 35 that already have one.
3. ⛔ Patch the Biotech `MinTemp_*`/`MaxTemp_*` `statOffsets`. Worst: reaches only 35 of 69 and
   changes those genes for every other mod's xenotypes and every gene-engineered colonist.

✅ `XenotypeDef.genes` is a plain `List<GeneDef>` (`XenotypeDef.cs:10`), so an `<li>` in a
`PatchOperationAdd` on `<genes>` is safe here — unlike `xenotypeChances`, which is
dictionary-keyed and discards the whole def.

## 🔴 WHY THIS IS FILED FOR DECIDE AND NOT DONE
**The band is a design decision, and the owner's 2026-08-23 ruling put offline renormalization
with DECIDE** — *"she authors the generator, the numbers and the patch and commits them; she
files them for BUILD with `--needs deploy`."* BUILD measured the gap; **choosing what band a
person survives on Ash'karr is not BUILD's call.** The parent item's own warning applies:
*"Do not widen tolerance to infinity. Temperature is what makes the nightside hostile and the
dayside lethal; a world where everything survives everywhere has no climate."*
⇒ Route 1 is a recommendation, not a decision, and the numbers to put in it are open.

## verify
A pawn of a species with no temperature gene (e.g. `Ugnaught`) survives a map at
`AB_PropaneLakes` (median −59.8) and at `AB_MechanoidIntrusion` (+62.5) without immediate
hypothermia/heatstroke. ⚠️ **Read `ComfortableTemperatureRange` off a SPAWNED pawn, not off the
def** — apparel, hediffs and any Harmony `StatPart` in the 580-mod stack shift it, and that was
explicitly NOT measured here.

## criteria
- [ ] A stated band, written down, with the reasoning for the numbers.
- [ ] All 69 species reach it, including the 34 carrying no temperature gene.
- [ ] Relative species character survives — the heat-hardy stay comparatively heat-hardy.
- [ ] Filed back to BUILD with `--needs deploy`.

## Watch out
⚠️ **UNMEASURED, and stated as such:** whether any mod in the 580 alters tolerance through a
Harmony patch or a `StatPart` rather than a gene. The assemblies were not censused and
`strings` on a DLL cannot answer it.
⚠️ Route 1 patches a **vanilla core def**, so its blast radius is every humanlike in the game,
raiders included. That is arguably correct for a shared planet, but it is a consequence to
accept deliberately rather than discover.

---

## 🔴 OWNER'S RULING 2026-08-23, AND IT IS BUILT — `HumanTemperatureBand_Ashkarr.xml`

Asked directly with the biome numbers in front of him. He chose **"Gear required at the
extremes"** over survivable-everywhere and over a modest widening.

⇒ **comfy −40 … +45, therefore safe −50 … +55.** Route 1: two `PatchOperationReplace` on
`ThingDef Human` `statBases`. Validated against the 580-mod set — both hit **Core:
Races_Humanlike.xml, 1 match each, 0 errors** — and deployed.

| Ash'karr extreme | median °C | a baseline naked pawn |
|---|---|---|
| `BMT_CrystalCaverns` | −62.4 | **needs gear** |
| `AB_PropaneLakes` | −59.8 | **needs gear** |
| `HorrorWastes` | −49.3 | survives |
| `AB_RockyCrags` | −45.3 | survives |
| `ExtremeDesert` | +48.2 | survives |
| `AB_MechanoidIntrusion` | +62.5 | **needs gear** |
| `ExtremeDesert` PEAK | +66.1 | **needs gear** |
| coldest ground | −82.0 | **needs gear** |

Four extremes demand clothing and shelter; the rest of the planet is livable. That is the
ruling expressed as a number.

🔑 **Gene offsets still stack, which is the whole reason route 1 was chosen.** The
distribution moves and the relative character survives: Jawa keep their heat gene and end up
able to work the dayside peak their own biome reaches, Chiss stay the cold-hardy ones,
`AG_ColdImmunity` (−273) and Outland's (−999) still make their carriers immune. And the 34
species with no temperature gene are reached without touching one of them.

⚠️ **Accepted deliberately:** this moves EVERY humanlike, raiders included. Correct for a
shared planet — the enemy lives here too.

## ⛔ This item is CLOSED by the build, not handed on
It was filed for DECIDE because the band was a design call. **The owner made that call
directly**, so there is nothing left for DECIDE to decide — `POLICY.md` is explicit that a
seat must never file an item asking another to ratify what the OWNER already said. What
remained was one two-operation patch, which is implementation and BUILD's outright.

## Still UNMEASURED, and it needs the load
- Nothing was read off a **spawned pawn**. Apparel, hediffs and any Harmony `StatPart` in the
  580-mod stack can shift the final number, and the assemblies were not censused.
- 🔑 **The reading:** dev-spawn a pawn of a species carrying NO temperature gene (`Ugnaught`,
  `Twilek`, `KelDor`) and read `ComfortableTemperatureRange` off the instance. **PASS = −40…+45.**
  Then a map at `AB_PropaneLakes` and one at `ExtremeDesert` — the first should hurt an
  unclothed pawn and the second should not.
