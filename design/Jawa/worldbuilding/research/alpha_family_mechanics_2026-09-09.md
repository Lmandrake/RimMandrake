<!-- status: DRAFT for the owner — ALPHA_FAMILY_SOURCE_REVIEW_1 is needs-owner and the
     replicate ruling is his to make. Nothing here is decided; no queue items were filed.
     Sources cloned to scratch only, never into src/. Fable seat, 2026-09-09. -->

# The Alpha family — mechanics inventory, license verdict, and what is worth owning

**What this is:** a study of Sarg Bjornson's (`juanosarg`) Alpha mods as a *source of
mechanisms*, per the owner's 2026-09-06 ask — *"not just to leverage their capabilities
but be inspired by them and broaden them."* It catalogs C# **mechanics**, not content,
and proposes generalized versions we would own under the tier grammar.

🔴 **The owner has not ruled.** Section 6 is a recommendation, not a plan.

---

## 1. Stack inventory — MEASURED

`ModsConfig.xml` (`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`),
read 2026-09-09: **595 active mods**, of which **7 are Sarg's**.

| In our stack (7) | Not in our stack (14 of the 21 Alpha repos) |
|---|---|
| `sarg.alphabiomes` · `sarg.alphaanimals` · `sarg.alphagenes` · `sarg.alphamechs` · `sarg.alphamemes` · `sarg.alphaskills` · `sarg.alphavehiclesneolithic` | AlphaArmoury · AlphaBees · AlphaBooks · AlphaCrafts · AlphaGenes-InsectoidMutations · AlphaImplants · AlphaMythology · AlphaPrefabs · AlphaProps-ParksAndGardens · AlphaProps-ShipParts · AlphaRandom · AlphaVehicles-AgeOfSail · AlphaVehicles-EarlyCars · AlphaVehicles-EarlyFlight |

Also active: `daria40k.alphaanimalspatchoutposts` (a third-party patch, not Sarg's).

`github.com/juanosarg` holds **83 public repos, 21 of them Alpha-named** (`gh api users/juanosarg/repos --paginate`).
Beyond Alpha he also owns GeneticRim, Megafauna, and 12 Vanilla Animals Expanded repos —
the same C# patterns recur across all of them, so this study generalizes past the two read.

**Size of the two repos read** (cloned to scratch, `--depth 1`):

| | C# files | defNames | Own-namespace `Class=` uses | VEF `Class=` uses |
|---|---|---|---|---|
| AlphaBiomes | 119 | 354 | 17 | 61 |
| AlphaAnimals | 137 | 904 | 80 | 428 |

---

## 2. License verdict — plainly

**The license forbids more, not permits more. It grants us nothing beyond reading.**

- **MEASURED:** all 21 Alpha repos report `NO-LICENSE` from the GitHub API. Neither clone
  contains a `LICENSE`, `COPYING`, or `README` file, and neither `About.xml` mentions
  licensing. Exactly one repo in the whole 83-repo account carries any license at all
  (`Jewelry`, `NOASSERTION`).
- **Consequence in law:** no license means default copyright — all rights reserved.
  Public visibility on GitHub grants viewing and in-platform forking only; it grants no
  right to copy, modify, or redistribute the code or the art. **So the C# source being
  published changes nothing about what we may legally ship** — it is readable, not reusable.
  Def *identities* (names, numbers, ideas, mechanisms) are not the copyrightable part;
  the expression — the source text and the PNGs — is.
- **Our standing ruling overrides this for private play.** Owner, 2026-08-15
  (`design/Jawa/mods/repurposed_graphics.md`): *"Licensing is SETTLED and is not a
  consideration… This is a private playthrough; nothing is published. Do not weight
  licences in any reuse decision."* The single carve-out is explicit: **if this ever
  ships publicly, that decision revisits everything reused.**
- **Practical rule this study lands on:** decide on engineering grounds, exactly as the
  owner said — and the engineering answer here happens to be the same as the cautious
  one. Alpha's C# is small, hardcoded to Alpha's own defNames, and mostly a thin skin
  over VEF and vanilla systems we already have. There is very little worth lifting, and
  a clean-sheet version is *better code* as well as the only kind that survives a
  publishing decision. **No file from either repo has been copied into `src/`.**

---

## 3. The structural finding — who actually owns these mechanics

The single most useful result of this review, and it saves most of the work:

> **Most of what reads as "an Alpha mechanic" is not Alpha's code at all.**
> It is Vanilla Expanded Framework (already active as `oskarpotocki.vanillafactionsexpanded.core`)
> or plain vanilla RimWorld. AlphaAnimals uses **428** VEF classes against **80** of its own.

Four mechanics the item named as prize targets turn out to cost us nothing:

| The mechanic we wanted | What actually implements it | Our cost |
|---|---|---|
| **Terrain that attacks** (the Gelatinous "slime in the eyes") | **Vanilla** `TerrainDef.<tools>` with capacity `KickMaterialInEyes`, applying a hediff. Same system as vanilla mud. | **XML only** |
| **Terrain that infects / heals** | `VEF.Maps.ActiveTerrainDef` + `TerrainCompProperties_HediffGiver` (`hediffsForHumanlike`, `hediffsForAnimals`, `hediffLimit`, `randomBodyParts`) / `TerrainCompProperties_Healer` | **XML only** |
| **Sensor-degrading fog** (the Forsaken weathers) | **Vanilla** `WeatherDef`: `accuracyMultiplier` (Alpha uses 0.3–0.9), `maxRangeCap`, `moveSpeedMultiplier`, `maxGlow`, `preventSkygaze`. Alpha writes no C# for this. | **XML only** |
| **Dormancy / wake-on-trigger** | **Vanilla** `CompCanBeDormant` + `CompWakeUpDormant` — signal tags, `wakeUpCheckRadius`, `wakeUpOnDamage`, `wakeUpOnThingConstructedRadius`, `onlyWakeUpSameFaction`, delayed wake, wake effecter. | **XML only** |

⚠️ **Two corrections to the item's framing, both load-bearing:**

1. **AlphaAnimals has no dormancy mechanic whatsoever.** No dormant/wake class, comp or
   hediff exists anywhere in its source or defs; the only occurrence of the word is
   flavour text about volcanoes. It is not the donor for that mechanic. Vanilla is.
2. **The "107 dormant rows" is not a count of our rows.** It comes from one string in
   `dune_sea_deep_desert.json` → `new_defs`: *"107 live VFEI2 dormant rows carry the
   mechanic"* — a count of **VFEI2's** rows, cited as a reskin target. Our own rosters
   carry **24 rows** mentioning dormancy in free text across 10 sheets, and **there is no
   structured dormancy field at all** (`_SCHEMA.md` rows are `def/commonality/action/band/law/note`;
   mechanics live only in prose). The 107 remains unverified against VFEI2 itself.

The corollary: **the sheets' mechanic wants are mostly not blocked on code.** They are
blocked on someone writing the XML. Where code *is* genuinely needed, it is the short
list in §4B.

---

## 4. The mechanics table

Effort is **replicate-from-scratch** effort for us: **S** = under ~60 LOC, no Harmony ·
**M** = 60–200 LOC or one Harmony patch · **L** = Harmony on a hot path, a map component,
or several cooperating classes.

### 4A — Already ours for free (do not build these)

| Mechanism | Owner | Sheets that want it (rows) |
|---|---|---|
| `TerrainDef.<tools>` / `KickMaterialInEyes` | vanilla | terrain attacks (the_forge, 1) |
| `CompCanBeDormant` + `CompWakeUpDormant` | vanilla | dormancy (24 rows, 10 sheets) |
| `WeatherDef.accuracyMultiplier` / `maxRangeCap` / `maxGlow` | vanilla | sensor fog (5: desert, arid_shrubland, the_twilight_sea, the_webwork, wasteland) |
| `GasType.BlindSmoke` — blocks turret LOS (`AttackTargetFinder`) and cuts accuracy (`ShotReport`) | vanilla | sensor fog, spore/gas cloud |
| `DeathActionWorker` → `IncidentDefOf.Eclipse` / `Tornado` / `Flashstorm` | vanilla incidents, ~15 LOC each | sun-blocking (Darkbeast pattern) |
| `VEF.Maps.TerrainCompProperties_HediffGiver` / `_Healer` | VEF | disease/infection (15), acid (1) |
| `VEF.AnimalBehaviours.CompProperties_Floating` | VEF | floating/gasbag (4) |
| `…CompProperties_Regeneration` (`rateInTicks`) | VEF | regeneration (4) |
| `…CompProperties_GasProducer` (on animals) | VEF | spore/gas cloud (4) |
| `…CompProperties_TerrainChanger` | VEF | terrain-changing (1) |
| `…CompProperties_CorpseDecayer` | VEF | corpse decay/dispersal (9) |
| `…CompProperties_DigWhenHungry` | VEF | burrowing (12) |
| `…CompProperties_Untameable` · `_AsexualReproduction` · `_EatWeirdFood` · `_Metamorphosis` · `_HighlyFlammable` · `_MakeOtherPawnsFlee` · `_Blink` · `_Electrified` · `_InitialAbility` · `_AnimalProduct` · `_LightSustenance` | VEF | roster-wide colour |
| `VEF.Maps.TileMutatorExtension` (41 uses in AB) · `VEF.Plants.DualCropExtension` | VEF | biome authoring |

### 4B — Alpha-owned C# worth generalizing and owning

| Alpha class | What it actually does | Our sheets that want it | Effort | Our generalized version (tier) |
|---|---|---|---|---|
| `AlphaBiomes.CompGasProducer` + `CompProperties_GasProducer` (`gasType`/`rate`/`radius`/`needsElectricity`) — on `AB_AgariluxPrime` | Every 512 ticks, rolls each cell in a radius and spawns a gas ThingDef there. ~50 LOC. Hardcodes a special case for its own plant's defName. | **The active-defender plant.** desert (defending shade plants), arid_shrubland (venomvine), spore/gas cloud (4), sensor fog (5) | **S** | **`RM_CompEmitGas`** — emits a gas ThingDef *or* a vanilla `GasType` (so `BlindSmoke` gives a real sensor fog); trigger modes: always / on-damage / on-approach-within-radius / on-harvest-attempt / by-daylight; `IsHashIntervalTick`, not a counter; `ThingDef` field, not a string lookup |
| `AlphaBiomes.Gas_Mycotic`, `AlphaBehavioursAndEvents.Gas_Frost`, `Gas_Ocular` | Three near-identical `Gas` subclasses. Mycotic: every 120 ticks, cut damage + toxic buildup to pawns in-cell and heavy cut damage to plants — **with a hardcoded four-defName immunity whitelist**. Frost: frostbite. Ocular: converts plants. | spore/gas cloud, venom (18), disease (15), sap (2) | **S** | **`RM_Gas_Harmful`** — one data-driven `Gas`: `damageDef`/`amount`, `hediff`+`severityPerPulse`, `plantDamage`, and immunity by **ThingDef list or tag**, not by hardcoded name. Absorbs all three. |
| `StatPart_DigestiveSurface` · `StatPart_QuiveringSurface` · `StatPart_SymbioticNutrients` | Three ~25-line StatParts, each hardcoding one tile-mutator + one multiplier + one subject test (deterioration ×n on natural terrain; movement ×0.8 for humanlikes; food need ×0.9). | temperature effect (66, the_forge 51), sun-blocking (27), regeneration | **S** | **`RM_StatPart_ConditionScaled`** — one class, config-driven: gate on tile mutator **or** biome **or** weather **or** game condition; subject filter (humanlike/animal/mechanoid/item); any stat, any multiplier. One class replaces their three and every future one. |
| `Harmony: GenCelestial.CurCelestialSunGlow` postfix — `__result *= 0.34f` on Rocky Crags, per-map cached | Dims a whole biome's daylight. **No XML field does this.** The one genuinely irreplaceable trick in AlphaBiomes. | **sun-blocking/shade (27 rows — desert 10, the_greentide 5, the_cracked_lands 5)**, the_twilight_sea, nightside_ice, forsaken_crags | **M** | **`RM_BiomeLightExtension { sunGlowFactor }`** — a `DefModExtension` on `BiomeDef` read by one cached postfix. Data-driven where Alpha hardcodes one biome. ⚠️ hot path — the per-map cache is mandatory, and Alpha's cache never evicts (a slow leak across map cycles); ours should key on map ID and clear on map removal. |
| `Harmony: PlantUtility.CanEverPlantAt` postfix + `PlantPropertiesExtension { fertilityMax }` | A **fertility ceiling** for plants — vanilla has `fertilityMin` only. Lets a plant refuse to grow where it is *too* rich. | Ash'karr flora generally: desert plants that must not colonise an oasis or a fall-line seep | **S** | **`RM_PlantEnvelopeExtension`** — `fertilityMax`, and while we are in there `rainfallMax`, `temperatureMax`. Same one-postfix shape. |
| `AlphaBiomes.HediffComp_GangreneWounds` | At two severity thresholds, on an MTB roll, damages/amputates a finger or toe with a custom damage def. Staged escalation. | disease/infection (15: the_contagion 5, the_miasma 2, poison_forest 2), acid, venom | **S** | **`RM_HediffComp_StagedBodyDamage`** — a list of `{severityThreshold, mtbTicks, chance, damageDef, bodyPartTag}` stages instead of two hardcoded ones. |
| `AlphaBiomes.MapComponentExtender` + `SpecialSpawnsDef` (`thingDef`, `numberToSpawn`, `terrainValidationAllowed/Disallowed`, `allowedBiome`, `allowOnWater`, `findCellsOutsideColony`) | A biome-scoped scatter pass at map init that vanilla scatterers cannot express — 3 Agarilux Primes only on mycotic grass, 25–35 Gallatross bones only on cracked mud. | wreck_fields, the_scarlands, the_cracked_lands, weeping_stones — every sheet whose character is *what is lying on the ground* | **M** | **`RM_ScatterDef` + one MapComponent** — the same data shape, plus per-biome weight and a rot/damage roll. This is the cheapest big win for biome *character*. |
| `AlphaBehavioursAndEvents.CompTerraform` / `CompCreateOcularPlants` | Spreading terrain conversion: sets terrain under itself, then periodically converts the nearest matching cell in a growing radius; the Ocular variant also flips plants and can force a weather. | terrain-changing (1, the_cracked_lands), the_slime, the_rot, the_greentide | **M** | **`RM_CompSpreadTerrain`** — source terrain → target terrain, radius curve, optional plant conversion, hard cell budget per map |
| `AlphaBehavioursAndEvents.Hediff_Stalking` | Snapshots the pawn's hediff count on add; removes itself the instant **any** new hediff appears — an invisibility that breaks on being touched at all. Clever and tiny. | stalking (1, the_rot), camouflage (9) | **S** | **`RM_Hediff_BreaksOnAnyHediff`** — same trick, no changes needed. Genuinely elegant. |
| `AlphaBehavioursAndEvents.HediffComp_TurnWhenDead` | On death above a severity threshold, spawns N pawns of another kind from the corpse (optionally manhunter), makes filth, destroys the corpse. | corpse decay/dispersal (9: the_scarlands 3, the_cracked_lands 2) | **M** | **`RM_HediffComp_SpawnOnDeath`** — pawnkind, count range, hostility, corpse disposition |
| `DeathActionWorker_PlantCacti` · `_MouseFission` · `_ExplodeAndSpawnEggs` | Death that *seeds*: plants 3–6 cacti in valid cells / splits into 3 of the next stage / drops eggs then detonates around them. | thorn (17), lure (6), the ecology sheets generally | **S each** | **`RM_DeathActionWorker_Seed`** — one worker: spawn a thing/plant/pawn list, count range, radius, optional explosion excluding the spawn |

### 4C — Alpha-owned, catalogued but **not** recommended

`Pawn_SwallowWhole` + `DamageWorker_SwallowWhole` (**L**, `IThingHolder` stomach — vanilla
Anomaly fleshbeasts already do this) · `PawnUtility_IsFighting` transpiler (**L**, IL rewrite
for one pawnkind list) · `DamageWorker_Berserk` (force-slows game speed on the player —
hostile design) · `GameCondition_AmbientRadiation` (grafts a random gene onto a colonist
every 900k ticks; would collide with the Jawa xenotype) · `CompAlcyoniteSolar`,
`CompRedAlcyioniteSolarConverter`, `CompCauseThoughtIfThoughtFound`, the Ancient Vent
comps, `Building_CoreSampleDrill`, `MagmaSprayer`/`TarSprayer` (content-specific, no
generalizable core) · `Web_Projectile` (**M**, but its "pick the second damage type by
reading my own defName" is exactly the anti-pattern our version must not copy — a def
field, not a name switch).

### 4D — Honest overlaps with TITANIC_CREATURES_MOD_1

The item says that stream wants nothing from here. Recording three real adjacencies
anyway, so nobody rediscovers them as new:

- `Hediff_Crushing` (**M**) — periodic radius damage to everything around a moving pawn,
  scaled by distance and target category, skipping thick roofs and natural rock. That is
  the same problem space as `CompTitanicWake` / `Patch_ThickRoofAvoidance`. Ours is
  event-driven off `Thing.Position` (cheaper); theirs is a ticking hediff. **Different
  meaning of "wake"** — ours is a movement trail, no naming collision to resolve.
- `DamageWorker_Siege` (**M**) — bespoke 8× HP-based damage against walls and natural rock,
  bypassing the injury pipeline. Relevant if a titan should *break* a wall rather than
  attack it.
- `Pawn_SwallowWhole` (**L**) — a devour mechanic, listed in 4C as not recommended.

---

## 5. Broaden — what these become on Ash'karr

The owner's ask was to broaden, not to port. The desert reframes almost all of it:

- **Spore cloud → dust defence.** The Agarilux pattern on a desert plant is not spores,
  it is a plant that *throws grit* — `BlindSmoke` in a radius, which on Ash'karr degrades
  the very thing raiders rely on (accuracy and turret tracking) while a Jawa who knows to
  approach from downwind walks in. That turns a hazard into terrain knowledge, which is
  the clan's whole identity.
- **Forsaken darkness → the shade economy.** `sunGlowFactor` on a biome is the mechanical
  spine of `desert.json`'s 10 shade rows and its `ShadeAt` MapComponent: shade is not
  decoration on a desert world, it is the resource. A canyon biome at 0.6 glow is a
  different *game*, not a different palette.
- **Gelatinous surface debuffs → the dune sea.** `RM_StatPart_ConditionScaled` gated on a
  tile mutator gives soft sand that slows, glass-crust that cuts, and salt pan that
  desiccates — three sheets' worth of character from one class and three XML blocks.
- **Gallatross bones → the wreck fields.** `RM_ScatterDef` is the same mechanism that
  makes a graveyard read as a graveyard; ours scatters hulls, not skeletons.
- **Fertility ceiling → the oasis boundary.** A flora envelope with a *maximum* is what
  stops the whole planet's plant list smearing across the fall line.

---

## 6. Recommendation — the top 5 to own first

1. **`RM_CompEmitGas`** (S) — the active-defender plant, and the one thing the desert and
   shrubland sheets are actually asking for. Emitting vanilla `BlindSmoke` also delivers
   sensor fog for free.
2. **`RM_StatPart_ConditionScaled`** (S) — one class retires Alpha's three and serves the
   largest want on the rosters (66 temperature rows, 27 shade rows).
3. **`RM_BiomeLightExtension` + the cached sun-glow postfix** (M) — the only mechanic here
   with no XML equivalent at all, and the spine of the shade economy. Cache must evict.
4. **`RM_ScatterDef` + MapComponent** (M) — the cheapest large gain in biome *character*;
   feeds wreck_fields, the_scarlands, the_cracked_lands, weeping_stones at once.
5. **`RM_Gas_Harmful`** (S) — pairs with #1; data-driven where all three Alpha gases
   hardcode their immunity lists.

**Everything in §4A should be written as XML this week and not queued as code.** Dormancy,
attacking terrain and fog-that-blinds are already paid for — by vanilla, and by VEF we
already load. All five above are tier **RimMandrake** (`RM_`): each passes the "would a
medieval-tribe player install this alone" test, and the Ash'karr content that uses them
stays `RUT_`.

---

## 7. What I did not check

- **Only two repos were read** (AlphaBiomes, AlphaAnimals). AlphaGenes, AlphaMechs,
  AlphaMemes and AlphaSkills are in our stack and were **not** opened — Genes and Memes
  in particular are likely to hold mechanisms relevant to the Jawa xenotype and the
  Salvation ideoligion.
- **VEF's own source was not read.** Every VEF comp in §4A is described from its name and
  from real XML usage in Alpha's defs, not from VEF's C#. Before relying on any field
  name in §4A, read the VEF source or the def that uses it — do not type a field from
  this table into XML unverified.
- **The 107 VFEI2 dormant rows were not verified against VFEI2.** A `measure` pass against
  the live def set is the instrument if that number is going to decide anything.
- **`CompCamo` (41 uses in AlphaBiomes) is a separate mod**, not VEF and not Alpha, and
  **no active packageId in our 595 contains "camo"** (MEASURED). All 41 uses sit in one
  mod-gated patch file (`1.6/Patches/PassiveCamouflagePatch.xml`), so nothing is being
  silently discarded — but camouflage (9 roster rows) has **no donor in our stack** and
  would need building or a new dependency. Not costed here.
- No performance measurement of any Alpha mechanic was made; the effort ratings are
  reading-the-code estimates, not benchmarks.
