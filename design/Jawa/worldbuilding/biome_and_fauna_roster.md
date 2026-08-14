# biome_and_fauna_roster.md — which biomes, which beasts, and what makes each tile feel like itself

_Authored 2026-08-13 by **AGENT WORLD**, overnight, on the owner's brief: "Decide
which Biomes are in and out. Decide which beasts are in/out for each Biome,
rigorously and thoroughly. Think about the specific tilemap enhancements we could
sprinkle into each biome that would make them uniquely stand out."_

**Status: a proposal, not applied.** Nothing in this document has been written to
any config or shipped as a patch. Every number is here to be argued with. See
§6 for exactly what applying it would involve.

**Companion docs — this one does not repeat them:**
`design/Jawa/worldbuilding/biome_terrain_palette.md` (which biomes and terrains EXIST, and
their roles) · `design/Jawa/worldbuilding/desert_world_design.md` (the world premise) ·
`design/Jawa/worldbuilding/Alien_Bestiary.md` · `design/Jawa/mods/forbidden_mods.md` (the in/out test
this document applies to fauna).

This document is the missing **numeric and per-species layer** under the palette.
`biome_terrain_palette.md` §4 open item 6 says, in its own words: *"Decide final
commonality weights per biome — this palette lists roles, not the numeric profile
yet."* That item is still open, and this is the pass that closes it.

---

## 0. What I found before deciding anything — the levers are installed and unused

Both mechanisms this proposal needs already exist in the stack. Neither has been
meaningfully configured, and one is actively full of junk.

| lever | packageId | load | state |
|---|---|---|---|
| **Choose Biome Commonality** | `mlie.choosebiomecommonality` | 95 | ⚠️ **config exists but is 3/4 junk** |
| **Choose Wild Animal Spawns** | `mlie.choosewildanimalspawns` | 97 | ⬜ **never configured** |

⚠️ **`Mod_2582875043_ChooseBiomeCommonality_Mod.xml` is not "partly done" — it is
mostly stale.** Read 2026-08-13, game down:

- **64 keys, and only 4 carry a non-default value.**
- **3 of those 4 are for biomes that are not installed** — `VQE_AncientSilo`
  (3.61), `AE_BloodLakeBiome` (2.42) are from mods no longer in the stack. The
  fourth live one is `AM_UndergroundSpace` (3.99), which as §1 shows is not even
  worldgen-selectable, plus `AG_NereidPocketPlane` pinned to 0.
- **8 stale keys total**: `VQE_AncientSilo`, `RG_AspenForest`, `AE_BloodLakeBiome`,
  `AE_ChristmasTreeBiome`, `Duskwood`, `pphhyy_LightlessEmpyrean_Biome`,
  `TemperateGuldenForest`, `UV_SpaceUndercave`.
- **10 live biomes are absent from the config entirely** — all three
  `BMT_*` caverns, all three `COMIGO_*` swamps, `CQF_Undercave`, `HorrorWastes`,
  `IronScruff_PrimordialGeysers`, `VQEA_AncientComplex`.

⇒ **The desert world's biome weighting has never actually been set.** The world
we have been planning around is, mechanically, the default RimWorld distribution.
That is the single most consequential thing in this document.

⚠️ **Per tonight's own lesson, absence proves less than presence.** No
`Mod_*ChooseWildAnimalSpawns*.xml` exists, and that proves only that nobody has
opened its settings — not that the mod cannot do the job.

### ✅ BOTH LEVERS VERIFIED FROM THEIR ASSEMBLIES, 2026-08-13

I first wrote this section saying the schema was unverified and that it gated
§3–§4. The game is down, so I read the assemblies instead of leaving it open.
**Both questions resolve, and one of them confirms §1 rather than breaking it.**

**`ChooseWildAnimalSpawns.dll` — §3 and §4 ARE buildable as written:**

```
CustomSpawnRates          SaveableDictionary   per-animal commonality
CustomDensities                                per-BIOME animal density
currentBiomeAnimalDensity
biomeDefName + animalDef + Split               composite keys, both directions
AnimalBiomeRecord / BiomeAnimalRecord          edit by animal OR by biome
ReverseSettingsMode
```

⭐ **`CustomDensities` is the one that matters.** It makes the oasis idea in §4
directly expressible — "life crowds the water" is a per-biome density value, not
a hack. That was open question 3 and it is now closed, in favour of the design.

**`ChooseBiomeCommonality.dll` — my §1 claim is CONFIRMED, not refuted:**

```
BiomeWorker_GetScore      BiomeWorkersDictionary      workerClass
```

The mod works by **patching the biome worker's `GetScore`**. A biome with no
`workerClass` has no `GetScore` to patch, so a commonality set on one is
genuinely inert. **The existing config's `AM_UndergroundSpace = 3.99` is
confirmed junk**, and the nine biomes in §1 are confirmed non-decisions.

---

## 1. Nine of the sixty-six are not decisions at all

**66 live `BiomeDef`s. Nine have no `workerClass`**, which means worldgen never
offers them — they are quest, structure and pocket-dimension biomes reached
through content, not through the world map.

```
AG_NereidPocketPlane   AG_PocketPlane      AM_UndergroundSpace
CQF_Undercave          Labyrinth           MetalHell
Undercave              Underground         VQEA_AncientComplex
```

**Setting a commonality on any of these is a no-op**, which is exactly what makes
the existing config's `AM_UndergroundSpace = 3.99` misleading: it looks like a
deliberate, strong preference and it does nothing whatsoever.

⇒ **57 real decisions.** Everything below is about those.

---

## 2. The in/out decision — 57 biomes

The premise, from `desert_world_design.md` and `biome_terrain_palette.md` §3: a
**mostly-desert, highly volcanic world with rare water, and vicious jungle rings
where water occurs**. The test applied to each biome is a single question:

> **Does a traveller crossing this world plausibly walk into this tile — and does
> finding it tell them something true about the planet?**

A tile that fails the second half is worse than a missing tile. It is a
contradiction the player has to explain away.

### Tier 1 — the desert sea. This IS the planet. (weight 8–10)

| biome | weight | why |
|---|---:|---|
| `ExtremeDesert` | **10** | The dune sea. Should be the modal tile and the thing that makes the gravship necessary. |
| `Desert` | **9** | The habitable margin of the same sea. |
| `AridShrubland` | **8** | The "almost liveable" fringe — where surface settlement is possible at all. |

Together these should dominate. If the world generates and these three are not
the overwhelming majority of tiles, the profile has not taken.

### Tier 2 — desert dialects. Variety WITHIN the premise. (weight 3–5)

| biome | weight | why |
|---|---:|---|
| `ZBiome_Badlands` | **5** | Eroded rock desert. The best "ancient ruin" backdrop on the list. |
| `ZBiome_CoastalDunes` | **4** | Only where water exists; the sand-meets-water read. |
| `Savanna` | **4** | Dry grass. The grazing fringe that justifies herd fauna. |
| `ZBiome_DesertOasis` | **3** | ⭐ **The rare-water payoff.** Deliberately low: an oasis is only special if it is scarce. |
| `Wasteland` | **3** | Dead ground. Reads as ruined rather than merely dry. |

### Tier 3 — the volcanic character. (weight 2–3)

`biome_terrain_palette.md` §3 asks for "low-but-present". These deliver the
obsidian/lava terrain families without becoming the world.

| biome | weight | why |
|---|---:|---|
| `AB_PyroclasticConflagration` | **3** | ⭐ The palette's named pick for volcanic character. |
| `Volcano` | **2** | Advanced Biomes' version; complements rather than duplicates. |
| `LavaField` | **2** | Odyssey. Also carries 33 Star Wars animals (§3), which is a bonus. |
| `Scarlands` | **2** | Odyssey toxic. The blighted-industrial read; 52 SW animals. |

### Tier 4 — alien strangeness, sprinkled. (weight 1)

| biome | weight | why |
|---|---:|---|
| `AB_TarPits` | **1** | Rare, memorable, thematically dry-adjacent. |
| `AB_RockyCrags` | **1** | "Forsaken crags" — good ruin/ambush terrain. |
| `IronScruff_PrimordialGeysers` | **1** | Geothermal oddity; pairs with the volcanic strand. |

### Tier 5 — the jungle ring. RARE, and only because water is rare. (weight 1)

The palette explicitly wants "vicious jungle around scarce water". These are the
ring, not a region.

| biome | weight | why |
|---|---:|---|
| `TropicalRainforest` | **1** | The baseline ring. |
| `AB_FeraliskInfestedJungle` | **1** | ⭐ The *vicious* half. Earns its place by being dangerous. |
| `AB_MiasmicMangrove` | **1** | Water-edge, alien, hostile. |

### Tier 6 — water bodies. Few, per the premise. (weight 1–2)

| biome | weight | why |
|---|---:|---|
| `Ocean` | **2** | Cannot build a base; existence is what matters. |
| `Lake` | **1** | The scarce-water anchor. |
| `ZBiome_Sandbar_NoBeach` | ⚠️ **see note** | Sand + water, on-theme — but `canAutoChoose` is **False**. |

⚠️ **Caught in self-review, and it is the same mistake this document criticises
in §0.** I initially gave `ZBiome_Sandbar_NoBeach` a weight of 1. It has
`canAutoChoose: False`, meaning worldgen does not auto-select it — it is placed
by its own worker's logic (adjacent to water), exactly as `AM_UndergroundSpace`
is unreachable by weighting. **A commonality on it may well be a no-op**, which
is precisely the "looks deliberate, does nothing" trap the existing config fell
into. I have not verified whether `Choose Biome Commonality` overrides
`canAutoChoose` or respects it. **Leave it unset until someone checks**; the
biome will still appear via its own placement rule.

⚠️ **`Ocean` and `Lake` report 0 `wildAnimals`.** That is expected, not a defect —
water biomes draw from `cachedCoastalAnimalCommonalities`, a different field.
Noted so nobody "fixes" it.

### Tier 7 — dark and underground. VERY rare, per the palette. (weight 1)

The palette says "keep dark biomes RARE" twice. Weight 1 each, and I would not
argue against 0.

| biome | weight |
|---|---:|
| `BMT_CrystalCaverns` · `BMT_EarthenDepths` · `BMT_FungalForest` | **1** each |

### ⛔ OUT — weight 0

**Everything cold or temperate.** Not because the biomes are bad, but because on
a desert world each one is a contradiction the player must explain away:

```
BorealForest        TemperateForest     TemperateSwamp      TropicalSwamp
ColdBog             Tundra              IceSheet            SeaIce
GlacialPlain        ZBiome_GlacialShield  ZBiome_AlpineMeadow  ZBiome_CloudForest
ZBiome_Marsh        ZBiome_Grasslands   Grasslands          ZBiome_Iceberg_NoBeach
Wetland             COMIGO_GreaterSwamp_Cold / _Temperate / _Tropical
```

**Off-premise or tonally wrong:**

```
AB_IdyllicMeadows          — an idyll on this world is a lie
AB_MycoticJungle           — jungle without the water justification
AB_OcularForest            — strong flavour, wrong flavour
AB_GelatinousSuperorganism — ditto
AB_GallatrossGraveyard     — ditto
Glowforest                 — beautiful, and not this planet
RG_BoilingForest           — forest
PoisonForest               — forest; Scarlands covers toxic better
HorrorWastes               — only 3 live animals; tonal outlier
AB_PropaneLakes            — canAutoChoose already false
AB_MechanoidIntrusion      — canAutoChoose already false; let it stay event-driven
Space · Orbit              — not surface tiles; leave to Odyssey's own systems
```

⚠️ **`Space` and `Orbit` are marked OUT here only in the sense of "not a surface
worldgen weight".** The Directorate's power is explicitly *vertical*
(`faction_roster_v2.md` §2 — ~7–8 orbital holdings), so the orbital layer matters
enormously to the campaign. It is simply not governed by this table.

---

## 3. Fauna — the rule, before the lists

322 animals can spawn in `AridShrubland` alone. **Hand-judging thousands of
species is not rigour, it is unreviewable.** A rule with named exceptions can be
checked by someone else in ten minutes; a list of 322 verdicts cannot.

So the policy is by **source**, with per-species exceptions called out.

### The test, and it is the owner's own

`design/Jawa/mods/forbidden_mods.md` records the Mythological Creatures ruling in the owner's
words: *"primitive, off-genre, and poorly implemented."* Applied consistently to
every fauna source in the desert set, that test does most of the work.

### Source verdicts

| source | desert-set species | verdict |
|---|---:|---|
| **Star Wars Animal Collection** | 49 / 71 / 109 | ✅ **KEEP ALL.** This is the theme. It also *oversupplies*, which is what makes cuts elsewhere free. |
| **Core / Odyssey** | 5–18 | ✅ KEEP. Baseline credibility. |
| **Alpha Animals** | 31 / 52 / 67 | ✅ KEEP. Alien, strange, outer-rim — exactly right for a frontier world. |
| **Vanilla Animals Expanded** | 12–15 | ✅ KEEP. |
| **Megafauna** | 7 / 10 / 23 | ✅ KEEP. Large alien beasts read as "this world is dangerous". |
| **Mythic Ages: Megafauna Bestiary** | 4 / 6 / 11 | ✅ **KEEP** — checked the actual species (Simbakub, direhorse, scarodon, sivatherium, worhin, harpeagle). These are invented megafauna, not fantasy monsters. No dragons, no unicorns. Passes the test. |
| **Cephaloids** | 2 | ✅ KEEP — cephalope, nautilant. Alien-strange. |
| **Giant Snake (Continued)** | 2 | ✅ KEEP — giant snake, white viper. Deserts have snakes. |
| **Beasts of the Rim** | 2–6 | ✅ KEEP. |
| **Dark Ages: Beasts and Monsters** | 3 | 🟡 **TRIM** — "black scribe", "karabal", "pilgrim". Named like fantasy, small footprint. Cut unless the owner likes them; nothing depends on them. |
| **Grimstone: Beasts** | 3 | 🟡 **TRIM `grimshadow`**, keep belloceros and emperor vulture. |
| **Erin's Final Fantasy Animals** | 2 | ⛔ **CUT.** A **chocobo** on a Star Wars desert world fails the owner's test on all three counts. This is the clearest call in the document. |
| **Mythological Creatures** | 5 | ⛔ **already gone** — unsubscribed 2026-08-13. Entries in the biome defs are now dead and will vanish on the next load. Listed only so nobody re-finds them. |
| **Jurassic Rimworld — Dinosaurs Only** | **4 / 32 / 44** | 🔴 **THE BIG ONE — see below.** |

### 🔴 The dinosaur question, which is the largest fauna decision on this world

⚠️ **CORRECTED 2026-08-13 after peer review by PROJECT. My first version of this
section measured the wrong unit and reached a stronger conclusion than the data
supports.** I counted **species listed**; what a player actually meets is
governed by **commonality-weighted share**. A mod can contribute 84 species that
each spawn almost never. Both numbers are below, because the gap between them is
the point.

| biome | species | **spp %** | commonality | **COM %** ⭐ | SW COM % |
|---|---:|---:|---:|---:|---:|
| `ZBiome_Badlands` | 84 | 32% | 4.05 / 16.74 | **24.2%** | **12.9%** |
| `ZBiome_DesertOasis` | 32 | 15% | 2.81 / 24.91 | **11.3%** | — |
| `ZBiome_CoastalDunes` | 32 | 15% | 2.81 / 29.10 | **9.6%** | — |
| `Desert` | 32 | 14% | 2.81 / 35.76 | **7.8%** | — |
| `AridShrubland` | 44 | 14% | 3.86 / 70.10 | **5.5%** | — |
| `ExtremeDesert` | 4 | 3% | 0.40 / 20.32 | **2.0%** | — |

**The correction cuts both ways, and it splits the recommendation in two.**

🔴 **`ZBiome_Badlands` — the problem is REAL and worse than a species count
shows.** Dinosaurs are **24.2%** of everything that spawns, against Star Wars
Animal Collection at **12.9%**. **You meet two dinosaurs for every Star Wars
creature.** Source breakdown: Core 26.2%, **Jurassic 24.2%**, SW 12.9%, Odyssey
9.4%, Alpha Animals 8.3%.
⇒ **Cut Jurassic from `ZBiome_Badlands`.** This is the one clear call.

🟢 **The core desert tiles — I over-stated it and withdraw the general cut.** At
**2.0%** in `ExtremeDesert` and **5.5%** in `AridShrubland`, dinosaurs are a rare
curiosity, not a tone problem. My original "one dinosaur for every two Star Wars
creatures" was an artefact of counting species. **A blanket Tier 1–2 cut is not
justified by this data and I withdraw it.**

⇒ **REVISED RECOMMENDATION — the partial cut, which I originally offered only as
a fallback, is now the primary:**

1. **Cut Jurassic from `ZBiome_Badlands`** outright. 24.2% is a genre problem.
2. **Elsewhere, cut only the ~20 most recognisably Earth-prehistoric names**
   (`Tyrannosaurus`, `Triceratops`, `Velociraptor`, `Stegosaurus`,
   `Ankylosaurus`, `Archaeopteryx`…). At 2–8% total share, the obscure remainder
   reads as alien megafauna to anyone who is not a palaeontology enthusiast.
3. **Keep the mod.** It is competent, and at these weights it is doing no harm
   outside the badlands.

**The surviving argument, unchanged:** the names break the fiction where the
silhouettes do not. A large reptilian grazer is perfectly Star Wars — that is a
dewback. The player does not see a silhouette, they see *"Carcharodontosaurus"*
in the inspect pane. That remains true; it is simply only *frequent enough to
matter* in the badlands.

⚠️ **Note on the 262-vs-1,088 discrepancy PROJECT raised.** Both are right and
they count different things: every biome lists **1,088** `wildAnimals` entries
because mods register their species against all biomes, **most at commonality
0**. Filtering to commonality > 0 gives 262 for `ZBiome_Badlands`. The filtered
figure is the correct one for "can this spawn here", and the commonality-weighted
figure above is the correct one for "how often".

### ⚠️ Thin biomes — flagged in self-review, deliberately kept

Six of the 24 IN biomes carry very few live species. This is **not** an argument
against including them, but it is a fact the fauna emphasis in §4 has to respect:

| biome | live species | reading |
|---|---:|---|
| `AB_RockyCrags` | **15** | Sparse is correct for crags. Fine. |
| `BMT_EarthenDepths` | **15** | Cave. Sparse is the point. Fine. |
| `Wasteland` | **29** | Dead ground. Sparse is the point. Fine. |
| `BMT_CrystalCaverns` | 38 | Fine. |
| `Ocean` / `Lake` | 0 | Expected — see the Tier 6 note. |

⇒ **Do not "enrich" these to match the desert tiles.** Emptiness is content on
this world, and `ExtremeDesert` is deliberately the emptiest thing on it.

### ⛔ Do NOT cut on "manhunter" or "predator" grounds

A desert world should be dangerous. The fauna cuts above are **tone** cuts, not
difficulty cuts. Nothing in this section should be used to make the planet safer.

---

## 4. Per-biome fauna character — what each tile's animals should SAY

Cuts alone produce a uniform soup. What makes tiles feel distinct is which
*surviving* species are common where. Proposed emphasis per biome — this is the
`Choose Wild Animal Spawns` layer, and it is **the part most in need of the
schema check flagged in §0.**

| biome | should read as | emphasise | suppress |
|---|---|---|---|
| `ExtremeDesert` | **Almost nothing lives here** | A handful of SW desert specialists at low commonality. Total density LOW. | Herds, anything requiring grazing |
| `Desert` | Sparse, large, dangerous | SW large reptilian grazers + their predators | Small woodland fauna |
| `AridShrubland` | The liveable fringe — herds | SW herd animals, pack-capable species | Aquatic, cold-adapted |
| `ZBiome_Badlands` | Ambush country, scavengers | Predators, carrion birds (emperor vulture ✅) | Grazers — nothing to graze |
| `ZBiome_DesertOasis` | ⭐ **Life crowds the water** | HIGHEST density on the planet. Everything comes to drink. | Nothing — this is the exception tile |
| `ZBiome_CoastalDunes` | Shore scavengers | Amphibious, shorebirds | Deep-desert specialists |
| `Savanna` | Grazing herds and their hunters | Megafauna herds | Cave/dark fauna |
| `AB_PyroclasticConflagration` · `Volcano` · `LavaField` | Heat-adapted, few | Alpha Animals heat species | Anything furred |
| `Scarlands` | Blighted, mutated | Waste Animals, toxic-adapted | Healthy megafauna |
| `AB_TarPits` | Death trap | Very low density; scavengers at the edge | Herds |
| jungle ring (Tier 5) | ⭐ **Vicious** — the water is guarded | `AB_FeraliskInfestedJungle`'s own predators, HIGH threat | Docile grazers |
| `BMT_*` caverns | Blind, pale, wrong | Cave fauna only | Anything sighted/surface |

⭐ **The single highest-value fauna decision in this table is the oasis.** If
water is scarce and the one wet tile is *also* where all the animals are, the
player learns the planet's rule without being told it. That is worth more than
any individual species call above.

---

## 5. Tilemap enhancements — making each biome unmistakable

The owner's stretch goal. These are **sketches for evaluation, not authored
work** — most need `Map Designer` (`zylle.mapdesigner`, load 202) or `Geological
Landforms` (`m00nl1ght.geologicallandforms`, 154), both installed.

**The design rule I would apply:** a tile should be identifiable from **one
screenshot with the biome label hidden**. If two biomes are distinguishable only
by their temperature readout, one of them is not earning its slot.

| biome | the one thing that should make it unmistakable |
|---|---|
| `ExtremeDesert` | **Emptiness as a feature.** Near-zero rock cover, no chunks, occasional wind-scoured bedrock shelf. The horror is that there is nothing to build with and nothing to hide behind. |
| `Desert` | Scattered rock outcrops that read as **navigation landmarks** — the only way to tell one dune from another. |
| `AridShrubland` | Dry watercourses — **wadis** that are visibly channels with no water in them. Tells the story of a world that used to be wetter. |
| `ZBiome_Badlands` | Deep erosion channels and mesas; `Geological Landforms` is built for exactly this. Best ruin-siting terrain on the planet. |
| `ZBiome_DesertOasis` | ⭐ **Concentric rings** — water, then green, then scrub, then sand, in visible bands. The most legible tile on the world and it should look designed. |
| `ZBiome_CoastalDunes` | Salt flats and tidal wrack where dune meets water. |
| `Savanna` | Sparse large trees at wide spacing — the classic silhouette. |
| `AB_PyroclasticConflagration` | Active lava veins + ash fall; obsidian flats from the `AB_*` terrain family (`biome_terrain_palette.md` §B3). |
| `Volcano` / `LavaField` | Cooled flows in visible *layers*, newest on top. Reads as geological time. |
| `Scarlands` | Toxic pooling in low ground, dead standing trunks. Blight that clearly *happened to* somewhere. |
| `AB_TarPits` | Tar seeps with **visible bones** — Biomes! Fossils (`biomesteam.biomesfossils`, load 80) is installed and this is its perfect home. |
| `AB_RockyCrags` | Vertical relief, narrow defiles. Ambush geometry. |
| jungle ring | Dense canopy *right up to* the waterline, then hard-stop to sand. **The contrast IS the content** — the ring should be visibly thin. |
| `BMT_*` caverns | Darkness as the mechanic. Keep rare; the palette warns twice. |

⚠️ **Scope honesty:** every row above is a *sketch*. Map Designer's actual
capability surface has not been checked against any of them, and I did not check
it because the game is down. **None of §5 should be quoted as achievable until
someone reads that mod's settings.** Treat this section as a wish list with
reasons, which is what the owner asked for.

---

## 6. What applying this would actually take

| step | effort | risk |
|---|---|---|
| 1. Verify `Choose Wild Animal Spawns` settings schema from its assembly | 10 min, offline | none |
| 2. Clean the 8 stale keys from the biome-commonality config | 5 min | low — but back it up; it is a live game config |
| 3. Write the §2 weights into that config | 20 min | reversible |
| 4. Apply §3 fauna cuts | depends on step 1 | reversible |
| 5. §4 per-biome emphasis | larger; do after 1–4 land | reversible |
| 6. §5 tilemap work | real design effort; **v2** | — |

⚠️ **All of this changes WORLDGEN, so it only affects a world generated
afterwards.** It cannot be validated on the current save, and it is not a
v1-blocking item — `V1_SCOPE.md` gives VISION one authored faction, Faction
Control suppression, three terrain overrides, and the Jawa xenotype. **This
document is v2 unless the owner pulls it forward**, and the reason to write it
now is that it was the largest un-done piece of world design, not that it is
urgent.

---

## 7. Open questions I could not answer offline

1. **`Choose Wild Animal Spawns` schema** — §0, and it gates §3–§4 being applicable.
2. **Dinosaurs: full cut or the ~20-name partial cut?** Owner's call. I lean partial.
3. **Does the oasis density idea survive contact with RimWorld's spawner?** Biome
   animal density is a biome-level field; "everything crowds the water" may need
   the per-biome commonalities rather than a density multiplier.
4. **`Space` / `Orbit`** — out of scope here, but the Directorate's orbital layer
   needs its own treatment and nothing currently covers it.
5. **Dark Ages / Grimstone trims** — small, taste-dependent, listed for a yes/no.
