<!-- status: design brief — nothing here is built -->
# The Blue Desert's life — BLUE_DESERT_LIFE_AUTHORING_1, step 1 (design brief)

_Design brief, 2026-09-21, Fable pass (backgrounded from BENCH per
`infrastructure/agents/Agent_Policy.md`: design is drafted by Fable, never in-window).
This doc **specifies**; it writes no ThingDef, no PawnKindDef, no C#, no texture. Format
precedent: `creatures/goo_boom_commission.md` (the vhessk). Every field, worker class,
comp, number and engine claim below was read from the file it cites — RimSage on the
installed 1.6 source and Core/DLC defs, or a repo file by path. Nothing is guessed; where
a number is a design choice rather than a measurement it says so._

**The commission (owner, 2026-09-20):** *"Blue desert should have some life. I thought we
had commissioned some hydrocarbon based strange life growing there. No?"* He was right —
the cast was ratified on the frozen sheet and never built. `RUT_BlueDesert` carries
`animalDensity 0`, `plantDensity 0`, `<wildAnimals />`, and three donor plants that (§1c
below) cannot spawn there anyway.

---

## 0. What this brief obeys, and what it found already existing

### 0a. The three rules

1. **The sheet is the target.** `biomes/the_blue_desert.md` is FROZEN; §3 "Hydrocarbon
   biology" and §4 "How the biology adapted" are ratified design. This brief adds detail
   and changes no ruling. One thing on the sheet is engine-FALSE and is corrected in §1c
   (the "very hard to ignite" line is authored, not free — see there).
2. **The admission test — hydrocarbon-metabolic, cold-stable, warm-reactive** — and the
   three bans (sheet §6 #1–#3): no water-based plant or animal; no cultivation of the
   flora; no warm-safe hydrocarbon organic. Every def and every product below carries
   the warm-reactivity or it is a violation.
3. **Not a fire — an explosive chain reaction.** Cold makes them hard to ignite; once
   they go, they go all at once. §2 is the single mechanism family that makes this true
   for plants, creatures and products alike.

### 0b. Prior work this brief adopts rather than duplicates

- **`creatures/RUT_hydrocarbon_ecology_commission.md` §6 already carded the Blue Desert
  flora**: `glassfern` (the fern), `chimeglobe` (the dandelion-head), `palefloss` (the
  fuzzball), plus a fourth kind the owner did not commission on the sheet — the
  `dovvik`, a proboscis "defuser" that siphons plants dry — and, in §14g, the shared
  butchery/harvest product **cold wax**. The owner ruled on that brief by card (§13,
  2026-09-10) and did not strike any of those names. **This brief keeps the three flora
  names and cold wax exactly, and gives them the mechanical spec §6 there did not
  (temperature bands, spawn fields, hit points, the charge comp, life-stage behaviour).**
  The dovvik is NOT re-specified here: it is that brief's own commission, it is not one
  of the four kinds the sheet ratifies, and adding a fourth resident fauna is the
  owner's call, not this pass's (§10). No ledger item exists for
  `HYDROCARBON_ECOLOGY_COMMISSION_1` in `items/` or `items/closed/`; its rulings live in
  the doc's own §13.
- **Art: none exists.** Searched 2026-09-21: `infrastructure/artpipe/registry.jsonl`
  (0 lines matching glassfern/chimeglobe/palefloss/dovvik/swallower/burner/picker/blue
  desert/butane/fractal), `artpipe/done/`, `artpipe/_artsrc/`, `art_status.json`,
  and `src/RimUtinni/AshkarrFlora/_artsrc/` — all empty for these subjects. Nothing to
  reuse; every sprite is genuinely owed (step 2 of the item).
- **No other item is mid-design on this biology.** `grep -il` over
  `infrastructure/state/items/*.md` for the subject words returns only this item, the
  mod-build item `BLUEDESERT_RM_MOD_BUILD_1`, and unrelated deep-sea/desert items.

### 0c. 🔴 Tier correction — these are RimMandrake defs, not RimUtinni

The commission and the item both say `RUT_`. **That is superseded**:
`design/RimMandrake/biome_mod_architecture.md` §3a (the ruled test, *"would it make
sense, unchanged, on a randomly generated planet with no Star Wars mod and no Ash'karr
loaded? Yes → RimMandrake"*) explicitly lists *"plants … hediffs, mechanics, Mod Settings,
and every creature whose own def lives in a RimMandrake mod"*, and row 7 of its Phase A
table says outright: **`BLUE_DESERT_LIFE_AUTHORING_1` builds INTO `mandrake.rm.bluedesert`,
not into UtinniPatches.** Nothing in this biology names a Star Wars thing. So:

| | value |
|---|---|
| mod | `mandrake.rm.bluedesert` (`src/RimMandrake/BlueDesert/`, per `BLUEDESERT_RM_MOD_BUILD_1`) |
| def prefix | `RM_` |
| C# namespace | `RimMandrake.BlueDesert` |
| naming register | `Alien_Bestiary.md` §1 — one or two syllables, hard stop, doubled consonants, the name never describes the mechanic; the salvager nickname carries the warning |

The earlier brief's `RUT_Glassfern` / `RUT_Chimeglobe` / `RUT_Palefloss` / `RUT_ColdWax`
become `RM_Glassfern` / `RM_Chimeglobe` / `RM_Palefloss` / `RM_ColdWax`. The `RUT_`
spellings there are the pre-migration form, not a competing ruling. The Utinni layer
keeps only what names the campaign: the biome's Ash'karr label and the roster patch that
adds Star Wars fauna (`Vapaad`, `AA_Thunderbeast`) to the biome's `wildAnimals`.

---

## 1. Engine facts that shape every def below (MEASURED from source)

These are the findings the build must not rediscover. Each names the file it was read from.

### 1a. Nothing spawns on ice unless a wild plant ignores fertility

`TerrainDef Ice` has `<fertility>0</fertility>` (`Core/TerrainDefs`, merged). The biome's
`terrainsByFertility` is Ice from −999 to 999, so **every cell is fertility 0**.
`WildPlantSpawner.CheckSpawnWildPlantAt` (`Source/RimWorld/WildPlantSpawner.cs:413`)
refuses a cell when `!HaveAnyPlantsWhichIgnoreFertility && FertilityAt(c) <= 0`, and
`GetDesiredPlantsCountAt` (line 720) multiplies the biome's `plantDensity` by cell
fertility — **0 × anything = 0 desired plants** — unless
`HaveAnyPlantsWhichIgnoreFertility`, which is `AllWildPlants.Any(p => p.plant.completelyIgnoreFertility)`
(line 212), in which case fertility is treated as 1.

⇒ **Every Blue Desert plant sets `<completelyIgnoreFertility>true</completelyIgnoreFertility>`.**
Without it, restoring `plantDensity 0.33` changes nothing and the biome stays bare with a
number that reads healthy. This is also why the three donor plants currently in
`RUT_BlueDesert.wildPlants` (`AB_ToxiGrass`, `AB_CrystalHorn`, `PoisonPlantTallGrass`)
have never spawned and never will on their own — they are ordinary fertility plants.
(Once OUR plants make the map-wide flag true, the donor rows become spawnable in
principle; whether they *should* be there at all is the §6 ban-1 tension the def's own
comment flags, and it is the owner's — §10.)

### 1b. 1.6 plants carry their own temperature band; the default kills anything at −42 °C

`PlantProperties` (`Source/RimWorld/PlantProperties.cs`): `minGrowthTemperature 0`,
`minOptimalGrowthTemperature 6`, `maxOptimalGrowthTemperature 42`, `maxGrowthTemperature 58`
are per-def fields. `PlantUtility.GrowthRateFactorFor_Temperature` lerps between them.
And `Plant.LeaflessTemperatureThresh = minGrowthTemperature + Rand(−18, −10)`
(`Plant.cs:526`); below it the plant goes leafless, and with `dieIfLeafless` it dies.
The biome's median is −42.6 °C (sheet §0), summer maximum below 0 °C on every tile.

⇒ Our plants write the whole band below the phase line (§6). `dieIfLeafless false`,
`growMinGlow 0` + `growOptimalGlow 0` (the cave-plant idiom, `Plants_Cave.xml:7–8`;
`PlantUtility.GrowthRateFactorFor_Light` returns 1 when min == optimal == glow), and
`dieIfNoSunlight false` (default is TRUE — `Plant.cs:214` kills a plant unlit for
450,000 ticks). ⛔ **Not** `cavePlant true`: cave plants are only offered where
`GoodRoofForCavePlant` (`WildPlantSpawner.cs:415`), i.e. under thick roof.

### 1c. Vanilla fire does not know it is cold — "hard to ignite" is authored

`Source/Verse/FireUtility.cs` contains no reference to temperature or snow (searched).
Ignition and spread run on the `Flammability` stat. The sheet's *"cold enough that
starting them burning is very hard"* is therefore **not free from the engine**; it is
written as a low `Flammability` on every native def (§6: `0.05`; fauna §3–§5: `0.1`).
That is the correction §0a rule 1 allows: the sentence stays true in play only because
the defs make it true. Nothing else on the sheet was found engine-false.

### 1d. Two ways to explode a pawn on death — and only one ignores life stage

- `race.deathAction.workerClass = DeathActionWorker_BigExplosion`
  (`Source/RimWorld/DeathActionWorker_BigExplosion.cs`, re-read 2026-09-21): radius is
  `1.9 / 2.9 / 4.9` chosen by `ageTracker.CurLifeStageIndex == 0 / == 1 / else`, damage
  `Flame` at def default, **no XML knob**. `goo_boom_commission.md` §3b's trap holds
  unchanged: a def with fewer than three `lifeStageAges` never reaches 4.9.
- `HediffCompProperties_ExplodeOnDeath` (`Source/RimWorld/HediffCompProperties_ExplodeOnDeath.cs`):
  `explosionRadius`, `damageDef`, `damageAmount (−1 = def default)`, `destroyGear`,
  `destroyBody`. Its worker `Notify_PawnKilled` calls
  `GenExplosion.DoExplosion(Pawn.Position, Pawn.Map, Props.explosionRadius, Props.damageDef, Pawn, Props.damageAmount)`
  — **a fixed radius, no life-stage term**. No vanilla XML uses it (searched all
  `Defs/**/*.xml`), so there is no precedent def to copy, but the class is Core and
  the fields are as listed.
- A hediff can be given at generation with zero C#: `PawnKindDef.startingHediffs`
  (`Source/Verse/PawnKindDef.cs:253`, `List<StartingHediff>`; `StartingHediff` has
  `def`, `severity?`, `chance?`, `durationTicksRange?`), applied by
  `PawnGenerator.cs:1269` for every non-newborn generation.

⇒ **Fauna detonation uses `startingHediffs` → a hediff carrying
`HediffCompProperties_ExplodeOnDeath`.** This is the reuse of the vhessk finding: pick
the mechanism whose radius is not a function of `CurLifeStageIndex`, and then the
three-stage workaround is unnecessary. The cost is that a juvenile detonates at the
adult radius (§10 lists it as open).

### 1e. `CompExplosive` cannot go on a plant, and on a pawn it is a trap

- `CompProperties_Explosive.ConfigErrors` yields `"CompExplosive requires Normal ticker type"`
  (`CompProperties_Explosive.cs`); plants tick `Long` (`Plants_Bases.xml:13`) and
  `Plant` overrides only `TickLong` (`Plant.cs:810`). A red config error per def, and
  the wick would never count down anyway (`CompExplosive.CompTick` only).
- On a pawn: `Thing.hitPointsInt` is initialised to **−1** (`Thing.cs:37`) and
  `Thing.PostMake` only sets HitPoints when `def.useHitPoints` (`Thing.cs:777`), which
  every animal has `false`. `CompExplosive.PostPostApplyDamage` then reads
  `parent.HitPoints (−1) <= StartWickThreshold` as TRUE on the first scratch and lights
  the wick. Vanilla's one pawn with the comp, `Mech_Apocriton`
  (`Biotech/Races_Mechanoids_SuperHeavy.xml:97`), sidesteps it with
  `chanceNeverExplodeFromDamage 1` + `explodeOnKilled true`, i.e. it uses the comp
  purely as a death hook.

⇒ Plants get a small custom comp (§2b); pawns use the hediff route (§1d). `CompExplosive`
is used only on the **item** (§7), where it is the right tool and vanilla's own.

### 1f. Warm-reactivity on fauna is free: it is heatstroke

`OrganicStandard` (`HediffGiverSetDef`) carries `HediffGiver_Heat` → `Heatstroke`.
`HediffGiver_Heat.OnIntervalPassed` (`Source/Verse/HediffGiver_Heat.cs`) raises severity
whenever `AmbientTemperature > SafeTemperatureRange().max`, and
`GenTemperature.SafeTemperatureRange` = comfortable range ± 10 (`GenTemperature.cs:87`).
Heatstroke kills; death fires §1d. **So a native with `ComfyTemperatureMax −11` gets
heatstroke above −1 °C — butane's boiling point (sheet §3) — and detonates when it dies
of it.** Bring one indoors and the room does the rest. Vanilla precedents for the cold
end: `ComfyTemperatureMin −100` on `Races_Mechanoid.xml:11`, `Odyssey/Races_Drones.xml:11`,
`Anomaly/Races_Entities_Misc.xml:9`; on organics, Penguin −70 (`Odyssey/Races_Animal_Birds.xml:1245`),
Thrumbo/Moose −65.

### 1g. Grazing, cutting and killing are three different destroy modes

- Eating: `Thing.Ingested` → `IngestedCalculateAmounts` (`Plant.cs:603`: whole plant
  taken when `nutritionWanted >= growth × Nutrition`) → `Destroy()` with the default
  `DestroyMode.Vanish` (`Thing.cs:2005ff`).
- Cutting/harvesting: `Plant.PlantCollected` → `Destroy(DestroyMode.KillFinalizeLeavingsOnly)`
  (`Plant.cs:652`).
- Damage to 0 HP: `DamageWorker.Apply` → `victim.Kill(dinfo)` → `Plant.Kill` →
  `KillFinalize` (`DamageWorker.cs:116ff`, `Plant.cs:706`).

⇒ The charge comp (§2b) fires **only on `KillFinalize`**. A Swallower swallowing a plant
whole (Vanish) is safe; a colonist cutting one (LeavingsOnly) is safe; a bullet, a
flame, a neighbouring blast (KillFinalize) is not. That is the sheet's whole
Swallower mechanism — *"keeping oxygen, and hence the risk, away until the anaerobic
gut"* — expressed as destroy modes, with no special case.

### 1h. Flame explosions heat rooms

`DamageDef Flame` carries `explosionHeatEnergyPerCell 15` (merged def). A detonation
inside an enclosure warms it, which pushes every other native in the room across §1f's
line. That is the chain reaction indoors, for free.

---

## 2. The shared mechanism — "the charge"

One family, three carriers, so every def below cites this section instead of inventing
its own chemistry. All C# lives in `RimMandrake.BlueDesert`; line estimates are honest
guesses at size, not promises.

### 2a. Fauna: `RM_HydrocarbonCharge` (HediffDef) — zero C#

```xml
<HediffDef>
  <defName>RM_HydrocarbonCharge</defName>
  <hediffClass>HediffWithComps</hediffClass>
  <label>hydrocarbon charge</label>
  <isBad>false</isBad>  <everCurableByItem>false</everCurableByItem>
  <comps>
    <li Class="HediffCompProperties_ExplodeOnDeath">
      <explosionRadius>R</explosionRadius>   <!-- per species, §3–§5 -->
      <damageDef>Flame</damageDef>
      <damageAmount>40</damageAmount>         <!-- §2d: the chain number -->
      <destroyBody>false</destroyBody>        <!-- §2e -->
    </li>
  </comps>
</HediffDef>
```

Given by `PawnKindDef.startingHediffs` (§1d) on every native kind. One def, three
radii — or three defs if the build prefers one hediff per species; either is zero C#.

### 2b. Flora: `RM_CompPlantCharge` (ThingComp, C#, ~40 lines)

- `CompTickLong` (plants tick Long, §1e): if `parent.AmbientTemperature > Props.detonateAbove`
  on two consecutive long ticks (≈ 66 s of game time — one long tick is 2000 ticks;
  the second read is there so a single warm gust from a nearby blast does not chain
  the whole field), call `parent.Kill(new DamageInfo(DamageDefOf.Flame, 99999f))`.
- `PostDestroy(DestroyMode mode, Map map)`: if `mode == DestroyMode.KillFinalize` and
  `map != null`, call `GenExplosion.DoExplosion(parent.Position, map, Props.radius, DamageDefOf.Flame, instigator: null, damAmount: Props.damage, chanceToStartFire: Props.fireChance)`
  (the named-argument form `goo_boom_commission.md` §3d already cites from
  `Verse/GenExplosion.cs`). `Vanish` and `KillFinalizeLeavingsOnly` do nothing (§1g).
- Props: `detonateAbove` (°C), `radius` (cells), `damage`, `fireChance`. Per card in §6.

### 2c. Items: vanilla comps plus one signal listener (C#, ~10 lines)

`RM_ColdWax` (§7) carries `CompProperties_Explosive` in chemfuel's exact shape
(`Core ThingDef Chemfuel`, raw: `explosiveRadius 1.1`, `explosiveDamageType Flame`,
`explosiveExpandPerStackcount 0.037`, `startWickOnDamageTaken Flame`,
`startWickHitPointsPercent 0.333`, `preExplosionSpawnThingDef Filth_Fuel`,
`wickTicks 70~150`, `tickerType Normal`) **plus** `CompProperties_TemperatureRuinable`
(`Source/RimWorld/CompProperties_TemperatureRuinable.cs`: `minSafeTemperature`,
`maxSafeTemperature`, `progressPerDegreePerTick 1E-05`), which broadcasts the comp
signal `"RuinedByTemperature"` when `ruinedPercent` reaches 1
(`CompTemperatureRuinable.cs:33`). `CompExplosive` does not listen for it, so:
`RM_CompRuinedDetonator : ThingComp` overrides `ReceiveCompSignal(string signal)`
(`ThingComp.cs:23`, virtual) and on that signal calls
`parent.GetComp<CompExplosive>().StartWick()` (public, `CompExplosive.cs`).

Arithmetic at `maxSafeTemperature −1`: a stack at +20 °C accrues
`21 × 1E-05 = 2.1E-04` per tick → ruined in ≈ 4,760 ticks ≈ 79 s real time at 1× (about
1.3 in-game hours), then a 70–150-tick wick. Long enough to notice the "Overheating: 63 %"
inspect line `CompTemperatureRuinable.CompInspectStringExtra` prints, short enough that
"you never bring one indoors" (sheet §6 ban 3) is literally enforced.

### 2d. The chain number: 40 Flame

Every native detonation deals **40 `Flame`** (Flame's def default is 10;
`DoExplosion`'s `damAmount −1` means "use the default", so 40 is passed explicitly).
Every flora card sets `MaxHitPoints ≤ 40` (§6), so one blast kills every plant in its
radius → each dies by `KillFinalize` → each detonates (§2b) → the field goes.
`DamageWorker.Apply` multiplies plant damage by `dinfo.Def.plantDamageFactor`
(`DamageWorker.cs:143`); the merged `Flame` def sets no override, so the class default
applies — ⚠️ **build verifies that default is 1.0 before trusting 40 ≥ 40.** Pawns take
40 Flame with Heat armour applying; the fauna's `ArmorRating_Heat` is 0 on purpose
(§3–§5) so a native caught in a neighbour's blast is a casualty, not a survivor.

### 2e. Corpses, and the one place ban 3 is not yet closed

`HediffComp_ExplodeOnDeath.destroyBody` (`Notify_PawnDied → Pawn.Corpse.Destroy()`) is
**false** for all three fauna, because sheet §7 rules *"Burner fuel glands / Swallower
gut-oil"* as harvestable — a corpse must exist to butcher. Butchery is
`Corpse.ButcherProducts → InnerPawn.ButcherProducts` (`Corpse.cs:355`), so the yield is
set on the race def: `MeatAmount 0`, `LeatherAmount 0`, no `leatherDef`, and
`butcherProducts` = cold wax (§7). ⚠️ **The corpse ThingDef itself is generated
(`ThingDefGenerator_Corpses`) and does not carry `RM_CompRuinedDetonator`; a warm corpse
is therefore the one warm-safe hydrocarbon organic left.** Closing it needs a def-gen
patch that adds the comps to corpses of races carrying an `RM_HydrocarbonNative`
`DefModExtension`. Filed in §10 as owed build work, not decided here, because the
default (a corpse that merely rots) is a ban-3 gap the owner should see named rather
than have silently papered.

### 2f. The eater's side: `RM_ButaneGut`

Our flora inherit `PlantBase`'s `<ingestible><foodType>Plant</foodType>` (`Plants_Bases.xml:39`),
so any `VegetarianRoughAnimal` grazes them — a colonist's muffalo included. Ban 3 says
that must not be safe. `ingestible.outcomeDoers` runs on every ingestion
(`Thing.cs` `Ingested`, after `IngestedCalculateAmounts`); `IngestionOutcomeDoer_GiveHediff`
(`Source/RimWorld/IngestionOutcomeDoer_GiveHediff.cs`: `hediffDef`, `severity`) has no
per-race exemption, so: `RM_IngestionOutcomeDoer_ButaneGut : IngestionOutcomeDoer_GiveHediff`
(C#, ~8 lines) skips pawns whose `def` has `RM_HydrocarbonNative`, and otherwise gives
`RM_ButaneGut` — a `ToxicBuildup`-shaped hediff (severity per meal, `lethalSeverity 1`,
slow natural decay) that itself carries `HediffCompProperties_ExplodeOnDeath`
(radius 1.9, Flame 40). Natives eat freely; a water-based grazer that keeps eating the
field dies of it and takes the barn with it. The Swallower's "anaerobic gut" is the
exemption, in code.

---

## 3. The Swallower — `dorrak`

| field | value |
|---|---|
| defName (ThingDef + PawnKindDef) | `RM_Dorrak` |
| label | `dorrak` |
| nickname (description only) | "cask" — a sealed barrel of fuel on legs; salvager slang |
| name grammar | `-rak` ursine-heavy clade root (`Alien_Bestiary.md` §1: "big, slow, dangerous"), doubled `rr`, hard stop. Collision-swept 2026-09-21 against `creature_names_ashkarr.md`, the fish commission, the hydrocarbon commission and every biome sheet: no hit |

**Description (player-facing, salvager register — what a crew calls it and what they saw):**

> A slab of a beast on six short legs, plated like a boiler and about as talkative. It
> walks up to a glassfern, closes its whole face over it like a lid, pulls the thing out
> of the ice roots and all, and stands there a while. The crews call them casks and
> give them the road. Nobody who has shot one in the belly has described it afterwards.

### 3a. Body and numbers

Anchors read this pass: Thrumbo `ArmorRating_Sharp 0.6 / Blunt 0.4 / Heat 0.3`,
`baseBodySize 4`, `MoveSpeed 5.5` (Core `Thrumbo`, merged); Moose `baseBodySize 2.5`,
`baseHealthScale 2.1`, `MoveSpeed 4.7` (`Odyssey/Races_Animal.xml:1132ff`); Penguin
`MoveSpeed 2` as the vanilla slow floor (`Races_Animal_Birds.xml`). Laws applied:
`creature_normalization_doctrine.md` (drawSize = body length in metres, 60 kg per bodySize,
health ∝ mass), `beast_normalization_spec.md` Law 3 (best hit ≈ 12–15 × bodySize for
bs ≥ 1, 3–4 s cooldowns).

| field | proposed | grounding |
|---|---|---|
| `baseBodySize` | **1.6** (≈ 96 kg) | mid bin: big enough that its blast matters, small enough for "plants stay small" to be its food |
| `drawSize` (adult) | **1.8** | 1.8 m long; `creature_size_model.md` §4 canvas: `1.8 × 128 = 230` → 256 px |
| `baseHealthScale` | **1.6** | ∝ mass (ruling 3), no discount — the counterplay is *where* you hit it, not how much |
| `ArmorRating_Sharp / Blunt / Heat` | **0.6 / 0.4 / 0** | Sharp/Blunt at Thrumbo's ceiling — "sealed, armoured"; Heat 0 on purpose (§2d) |
| `MoveSpeed` | **1.8** | below Penguin; a cask on legs |
| `body` | `QuadrupedAnimalWithHoovesAndHump` | reused for its **Hump**, `coverage 0.10`, `height Top` (`Bodies_Animal_Quadruped.xml:588`): the sealed gut is a hittable 10 % of the body with no new BodyDef (the vhessk precedent). Cosmetic "hoof" labels in injury text accepted, or a bespoke BodyDef later (§10) |
| `foodType` / `baseHungerRate` | `VegetarianRoughAnimal` / **0.35** | grazes our flora (§2f); hunger low so a small field feeds it |
| `ComfyTemperatureMin / Max` | **−100 / −11** | §1f: heatstroke above −1 °C |
| `Flammability` | 0.1 | §1c |
| `Wildness` / `trainability` | 1.0 / `None` | untameable by default (§10 open) |
| `manhunterOnDamageChance` | 0.5 | slow and armoured: it turns on you, and you have time to regret it |
| `lifeExpectancy` | 30 | |
| `MeatAmount` / `LeatherAmount` | 0 / 0; `butcherProducts` → `RM_ColdWax` × 12 | §2e; the "gut-oil" of sheet §7 |
| PawnKindDef `combatPower` | 120 | between Moose-class and the vhessk's 200 |
| `ecoSystemWeight` | 1.0 | |
| `wildGroupSize` | 1~2 | |
| `lifeStageAges` | Baby 0 / Juvenile 0.4 / Adult 0.8 | ordinary three stages; radius does not depend on them (§1d) |

**Melee (Law 3, bs 1.6 → best hit 19–24):** `crush` Blunt **22**, cooldown 3.2,
`HeadAttackTool` + `ensureLinkedBodyPartsGroupAlwaysUsable`; `maw` Bite **12**,
cooldown 2.2, `Teeth`.

### 3b. Mechanic — "wound one in the wrong place"

- Carries `RM_HydrocarbonCharge` (§2a) with `explosionRadius 3.9` — the gut is a
  whole plant-load of butane plus its own blood: the biggest blast on the roster.
  Fires on death by any cause, heatstroke included (§1f).
- **The wrong place:** `RM_HediffComp_ExplodeOnPartDestroyed : HediffComp` (C#, ~25
  lines) on the same hediff, overriding `Notify_PawnPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)`
  (`Source/Verse/HediffComp.cs:97`, virtual): if `dinfo.HitPart?.def.defName == "Hump"`
  and `Pawn.health.hediffSet.PartIsMissing(dinfo.HitPart)` (`HediffSet.cs:569`) — i.e.
  the gut has just been destroyed — call `Pawn.Kill(dinfo)`. Death then runs §2a. A
  hump shot through but not destroyed is a wound like any other; a hump *destroyed* is
  the sheet's sentence. With coverage 0.10 an unaimed shot finds it one time in ten;
  a hunter who reads the health tab can avoid it, which is the counterplay.
- ⚠️ **Verify step (quicktest):** `jawa/damage` on the Hump to destruction on a spawned
  dorrak; count scorched cells — 3.9 is ~47 cells; then kill one by the head and confirm
  the same blast; then let one graze a glassfern and confirm nothing happens (§1g).

---

## 4. The Burner — `krissek`

| field | value |
|---|---|
| defName | `RM_Krissek` |
| label | `krissek` |
| nickname | "torch" — the crews say it from a long way off |
| name grammar | `kr-` initial (apex, "the ones with names people whisper"), `-ss-` sibilant (the heat clade), `-ek` (small, quick). One thing that is all three. Collision-swept: no hit |

**Description:**

> Low, long, all haunch and jaw, running in a colour you only see at the edge of a
> welding arc. Standing still it is a grey thing on grey ice; the moment it runs or
> fights, blue fire stands off its whole body like a coat. They do not live long and
> they do not seem to mind. When one is hurt past a certain point it does not fall
> over — it goes, all at once, and the field goes with it. The crews call them torches
> and never, ever go for the body shot.

### 4a. Body and numbers

Anchors: Snowhare `MoveSpeed 6`, `baseBodySize 0.2`, `baseHealthScale 0.4`,
`lifeExpectancy 8` (Core `Snowhare`, merged) — the fastest Core small animal; Snowhare
kind `combatPower 33`, `ecoSystemWeight 0.25`.

| field | proposed | grounding |
|---|---|---|
| `baseBodySize` | **0.9** (≈ 54 kg) | a sprinter: predator-class reach, hare-class mass |
| `drawSize` | **1.4** | 1.4 m; canvas 256 px |
| `baseHealthScale` | **0.6** | deliberately BELOW ∝ mass (0.9): "die young", and the design wants it *droppable from range before it closes* — the same discount the vhessk took, for the same reason (§10 open) |
| `MoveSpeed` | **6.5** | faster than Snowhare — the fastest thing on the nightside |
| `ArmorRating_Heat` | 0; `Flammability` 0 | it does not *catch* fire; it *is* one. Flame damage still lands (§2d) |
| `ComfyTemperatureMin / Max` | −100 / −11 | §1f |
| `foodType` | `CarnivoreAnimal` | `FoodTypeFlags.CarnivoreAnimal = 0xB0A` includes `Corpse (8)` (`Source/RimWorld/FoodTypeFlags.cs`): it eats what it kills and what falls |
| `predator` / `maxPreyBodySize` | true / **0.6** | hunts vekkit (§5) and anything that size that wanders in; never a dorrak (bs 1.6 — and a dorrak hit in the hump would take the krissek with it) |
| `manhunterOnDamageChance` | 1.0 | "fight hard" |
| `Wildness` / `trainability` | 1.0 / None | |
| `lifeExpectancy` | **4** | "run hot and die young" — half a snowhare's |
| `MeatAmount` / `LeatherAmount` | 0 / 0; `butcherProducts` → `RM_ColdWax` × 6 | sheet §7 "Burner fuel glands"; corpse kept (§2e) |
| `combatPower` | 90 | a hazard that closes fast, not a sustained fighter |
| `ecoSystemWeight` | 0.6 | |
| `wildGroupSize` | 1~3 | a pack of torches is the biome's set-piece |
| `lifeStageAges` | Baby 0 / Juvenile 0.15 / Adult 0.3 | short, like its life |

**Melee (bs < 1 — Law 3's linear band starts at 1; anchored on Snowhare bite 3.4 at bs 0.2
and the sublinear DPS rule):** `jaws` Bite **14**, cooldown 1.6; `claw` Scratch **8**,
cooldown 1.2. Fast, chippy, and the danger is not the bite.

### 4b. The halo — blue fire when it runs or fights

Vanilla attaches a continuous effecter to a pawn with `CompProperties_Effecter`
(`Mech_Apocriton`, `Races_Mechanoids_SuperHeavy.xml:104`: `effecterDef ApocrionAttached`);
`CompEffecter.CompTick` (`Source/RimWorld/CompEffecter.cs`) spawns
`Props.effecterDef.SpawnAttached(parent, map)` whenever `ShouldShowEffecter()`, which is
**`protected virtual`** and by default "spawned and on the current map".

⇒ `RM_CompEffecter_Halo : CompEffecter` (C#, ~15 lines) overrides `ShouldShowEffecter`:
base && (`pawn.pather.MovingNow` (`Verse/AI/Pawn_PathFollower.cs:85`) &&
`pawn.CurJob?.locomotionUrgency >= LocomotionUrgency.Jog` (`Verse/AI/Job.cs:55`, default Jog)
|| `pawn.InAggroMentalState` (`Verse/Pawn.cs:1571`) || `pawn.mindState.enemyTarget != null`).
Grazing-walk: no halo. Hunting, fleeing, fighting: halo. No hediff, no tick cost beyond
the comp vanilla already pays on the Apocriton.

The `EffecterDef RM_KrissekHalo` copies `ApocrionAttached`'s shape (merged def read this
pass): a `SubEffecter_SprayerContinuous` child, `attachToSpawnThing true`,
`spawnLocType OnSource`, `ticksBetweenMotes` ~6, `positionRadius 0.5`, with a new
`MoteDef` whose texture is the art pass's — a soft blue-white flame ring in the biome
accent `#55c0f0` (`palettes/biome_palette_anchors.json`, `the_blue_desert.accent`:
"blue-fire halo (Burners)" — the one saturated colour the biome owns, sheet §9: *"the
only warm light for a hundred kilometers"*). A real `CompGlower` light is NOT specified:
`TWINKLE_FLORA_SPIKE_1` (closed) is the standing verdict on per-thing glow cost and a
pawn-attached glower is its own spike (§10).

### 4c. Detonation — "explodes if wounded too greatly"

`RM_HydrocarbonCharge` with `explosionRadius 2.9`, Flame 40, `destroyBody false`
(§2e). Death is "wounded too greatly"; heatstroke is death (§1f); the blast kills every
plant within 2.9 cells (§2d) and the field carries it outward. ⚠️ **Verify:** kill one
in a palefloss field from range and watch the chain; kill one on bare ice and count
~28 scorched cells; put one in a 20 °C room and time the heatstroke.

---

## 5. The Picker — `vekkit`

| field | value |
|---|---|
| defName | `RM_Vekkit` |
| label | `vekkit` |
| nickname | "linewalker" — it works the ablation line where the sky's debris surfaces (sheet §2, §5) |
| name grammar | `-ik`/`-it` small-quick clade, doubled `kk`, hard stop; no `vh-` (it is not apex). Collision-swept: no hit (`rukka` was rejected — it collides with the Rot's `rukka cap`, `biome_flora_rosters.md:198`) |

**Description:**

> A knee-high thing that walks like a folding chair, two long jointed forelimbs ending
> in hooks it uses to pick a frozen carcass apart one flake at a time. You find them on
> the line where the ice gives things up: a dozen of them standing around a fallen hull
> or a freeze-dried spacer, working, patient, not interested in you unless you are
> lying down. The crews call them linewalkers and follow them to the good salvage.

### 5a. Body and numbers

| field | proposed | grounding |
|---|---|---|
| `baseBodySize` | **0.45** (≈ 27 kg) | small bin; below the krissek's prey ceiling on purpose |
| `drawSize` | **1.0** | 1 m; canvas 256 px (the floor, `creature_size_model.md` §4) |
| `baseHealthScale` | 0.45 | ∝ mass |
| `MoveSpeed` | 4.2 | |
| `foodType` | `CarnivoreAnimal` | corpse-eater (`Corpse` flag, §4a); `predator false` — it never hunts, it finds |
| `ComfyTemperatureMin / Max` | −100 / −11 | §1f |
| `Flammability` | 0.1 | |
| `Wildness` / `trainability` | 0.9 / None | |
| `manhunterOnDamageChance` | 0.05 | flees; the roster's harmless one |
| `herdAnimal` / `wildGroupSize` | true / **3~7** | "where there is one there is a dozen" |
| `lifeExpectancy` | 10 | |
| `MeatAmount` / `LeatherAmount` | 0 / 0; `butcherProducts` → `RM_ColdWax` × 2 | thin, like it |
| `combatPower` | 30 | |
| `ecoSystemWeight` | 0.3 | |
| `lifeStageAges` | Baby 0 / Juvenile 0.2 / Adult 0.4 | |

**Melee:** `hook` Stab **6**, cooldown 2.0; `beak` Bite 4, cooldown 1.8. It is not a
fighter.

### 5b. Mechanic

`RM_HydrocarbonCharge` at **`explosionRadius 1.1`** (chemfuel's own radius): a small
pop, enough to be a hazard when a pack is butchered warm, not enough to be a weapon.
Sheet §5 *"every native organic is a fuel charge"* is honoured; the design decision is
that a vekkit's charge is the one you can survive standing next to.

**The ablation-line behaviour is placement, not AI.** The sheet's "fall debris fields"
(§8) are injected set-pieces (`STRUCTURE_INJECTIONS_RUT` territory, out of scope here);
vanilla corpse-seeking food AI (`JobGiver_GetFood` on a `Corpse`-flagged foodType)
already walks a scavenger to the nearest carcass, so wherever the injection leaves
freeze-dried dead, vekkit gather. No custom job. If the owner wants them to *reveal*
salvage (dig up the buried), that is a new mechanic and is filed open (§10).

---

## 6. The transparent fractal flora — the register and three cards

Names and slots adopted from `RUT_hydrocarbon_ecology_commission.md` §6 (register header,
ladder, one-accent law); this section adds the engine spec. Sheet §3: *"transparent,
needing no light … fractal branches for gas exchange in place of leaves — ferns,
dandelions, fuzzballs … plants stay small"*; §6 bans 1–3.

### 6a. Fields every card shares (read against §1a–§1c, §1g)

```xml
<plant>
  <completelyIgnoreFertility>true</completelyIgnoreFertility>   <!-- §1a: or nothing spawns on Ice -->
  <fertilityMin>0</fertilityMin>
  <minGrowthTemperature>-90</minGrowthTemperature>               <!-- §1b: the band sits below the phase line -->
  <minOptimalGrowthTemperature>-60</minOptimalGrowthTemperature>
  <maxOptimalGrowthTemperature>-20</maxOptimalGrowthTemperature>
  <maxGrowthTemperature>-1</maxGrowthTemperature>                <!-- butane's boiling point, sheet §3 -->
  <growMinGlow>0</growMinGlow>  <growOptimalGlow>0</growOptimalGlow>   <!-- Plants_Cave.xml:7–8 idiom; NOT cavePlant -->
  <dieIfNoSunlight>false</dieIfNoSunlight>
  <dieIfLeafless>false</dieIfLeafless>
  <dieFromToxicFallout>false</dieFromToxicFallout>
  <neverBlightable>true</neverBlightable>
  <!-- sowTags: NONE. An empty sowTags list is never offered to a grow zone: ban 2 -->
  <harvestTag>Standard</harvestTag>
  <harvestedThingDef>RM_ColdWax</harvestedThingDef>
  <harvestMinGrowth>0.65</harvestMinGrowth>
  <lifespanDaysPerGrowDays>8</lifespanDaysPerGrowDays>
</plant>
<statBases>
  <Flammability>0.05</Flammability>   <!-- §1c: "very hard to ignite", authored -->
</statBases>
<ingestible>  <!-- inherits PlantBase foodType Plant -->
  <outcomeDoers>
    <li Class="RimMandrake.BlueDesert.RM_IngestionOutcomeDoer_ButaneGut">   <!-- §2f -->
      <hediffDef>RM_ButaneGut</hediffDef> <severity>0.25</severity>
    </li>
  </outcomeDoers>
</ingestible>
<comps>
  <li Class="RimMandrake.BlueDesert.CompProperties_PlantCharge">   <!-- §2b -->
    <detonateAbove>5</detonateAbove>   <!-- °C sustained; a warm room, not a warm breath -->
    <damage>40</damage>  <fireChance>0.2</fireChance>
    <!-- radius per card -->
  </li>
</comps>
```

`growDays` is deliberately long (below) — *"without the polar water molecule, transport
and chemistry are simply less efficient"* — ⚠️ but `mandrake.rut.plantgrowth`
(`src/RimUtinni/PlantGrowth/Source/Patch_Plant_GrowthRate.cs`) multiplies every
non-exempt plant's `GrowthRate` by 4.0 (`PlantGrowthConfig.DEFAULT_MULTIPLIER`) unless
its biome is on the terminator list (× 0.4). The build must either add these defs to
`PlantGrowthSettingsDef.exemptPlants` or add `RM_BlueDesert` to `terminatorBiomes`;
the numbers below assume **exempt** (vanilla rate).

### 6b. The cards

| | `RM_Palefloss` · fuzzball · ground cover | `RM_Glassfern` · fern · mid | `RM_Chimeglobe` · dandelion-head · mid |
|---|---|---|---|
| the read | a fist of transparent filaments hugging the ice — the biome's sparse "grass" | a hand-high fractal frond, all edge and refraction | a clear stalk carrying one spherical lattice head that sheds glittering seed-lattices to the wind |
| `MaxHitPoints` | **20** | **30** | **40** — all ≤ the chain number (§2d) |
| `Nutrition` | 0.15 | 0.3 | 0.35 |
| `growDays` | 6 | 9 | 12 |
| `harvestYield` (cold wax) | 2 | 4 | 5 |
| `harvestWork` | 40 | 120 | 160 |
| `visualSizeRange` | 0.35~0.55 | 0.6~0.9 | 0.8~1.1 — "plants stay small": nothing above 1.1 cells |
| `maxMeshCount` | 9 (Grass idiom) | 1 | 1 |
| `wildClusterRadius` / weight | none (lawn) | 3 / 5 | 5 / 3 |
| `wildOrder` | 1 | 2 | 2 |
| `charge.radius` | **1.1** | **1.9** | **2.9** |
| `altitudeLayer` | LowPlant | LowPlant | LowPlant |
| `graphicClass` | Graphic_Random, 3 variants, near-symmetric | Graphic_Random, 3 | Graphic_Random, 2 |
| `selectable` | false | true | true |
| `BeautyOutdoors` | 2 | 4 | 5 — "staggeringly beautiful" (sheet §3), and the only beauty on the plateau |

**The chain, as designed:** palefloss is the carrier — high commonality, low HP, small
radius, everywhere. A krissek dying in a floss field (2.9) kills every floss within it;
each floss pops at 1.1 and kills the next ring; a glassfern in the path pops at 1.9; a
chimeglobe at 2.9 restarts the whole thing. The field is a fuse laid by the spawner.
**Cutting is safe** (LeavingsOnly, §1g) — a crew that clears a firebreak with knives is
doing the right thing; a crew that clears it with a flamethrower is the sound in sheet
§9's last line.

### 6c. Wiring on the biome (step 4 of the item, stated so the build has one source)

`plantDensity` **0.33** and `animalDensity` **0.5** are the item's numbers (the donor read),
not this brief's. `wildPlants`: `RM_Palefloss 1.0`, `RM_Glassfern 0.5`, `RM_Chimeglobe 0.25`.
`wildAnimals`: `RM_Vekkit 0.8`, `RM_Dorrak 0.5`, `RM_Krissek 0.35`. The roster's two
owner-ruled Star Wars rows (`rosters/the_blue_desert.json`: `Vapaad 0.5`,
`AA_Thunderbeast 0.005`) ride the Utinni patch, not this mod (§0c) — and the live def's
`<wildAnimals />` currently drops them, which is a roster-vs-def gap the build closes,
not a ruling for this brief. `forageability` stays 0 (there is nothing a human can
forage that will not detonate in a pack).

---

## 7. The product — `RM_ColdWax`

Adopted from `RUT_hydrocarbon_ecology_commission.md` §14g ("cold wax … refines to
chemfuel at a cold-handled recipe … warm storage detonates it"), given its comps here
(§2c). One item for every native's butchery and every plant's harvest — the sheet's
*"Burner fuel glands / Swallower gut-oil"* and *"hydrocarbon flora as fuel"* (§7) are
flavour on one def, not three.

| field | value |
|---|---|
| `thingCategories` | `Manufactured` (chemfuel's) — NOT a food category; nothing eats it |
| `stackLimit` | 75 |
| `MaxHitPoints` / `Flammability` / `Mass` | 50 / 2 / 0.05 (chemfuel's) |
| `tickerType` | Normal (`CompExplosive` requires it, §1e) |
| comps | `CompProperties_Explosive` (chemfuel shape, §2c) · `CompProperties_TemperatureRuinable` `minSafeTemperature −273`, `maxSafeTemperature −1`, `progressPerDegreePerTick 1E-05` · `RM_CompRuinedDetonator` |
| recipe | `RM_ColdWax` ×5 → `Chemfuel` ×10 at the refinery; **no recipe-level temperature gate** — none exists on `RecipeDef`, and none is needed: a warm workroom ruins the input stack before the bill finishes (§2c arithmetic) |
| `MarketValue` | **not set here** — the prior brief parked pricing on `ECONOMY_TRADE_SWEEP_1`; same |

"Cold-handled only" (sheet §7) is therefore a fact about rooms, not a rule in a recipe:
store it outside or in an unheated shed, refine it in a cold room, and it is ordinary
fuel; heat the room and it is a bomb with a countdown line in its inspect pane.

---

## 8. Art direction (the brief for the sprite pass — step 2 of the item)

Follow `skills/generating-rimworld-sprites/SKILL.md` end to end. What this brief adds:

- **Canvases:** dorrak 256 (drawSize 1.8), krissek 256 (1.4), vekkit 256 (1.0); three
  facings each (`_south/_east/_north`); a `Dessicated_` variant for dorrak and krissek
  (their corpses persist, §2e). Flora: 3/3/2 `Graphic_Random` variants at 128 px
  (all under 1.1 cells), per `creature_size_model.md` §4's floor rule applied to plants
  as the flora template does.
- **Palette:** `biome_palette_anchors.json` `the_blue_desert` family `#1c2430 → #d2dde6`,
  accent `#55c0f0` **owned by the krissek halo only** (the flora register leaves its
  accent slot empty — prior brief §6 header, and the anchors file's own note that
  transparent flora is "what refraction TINTS, not body colour"). Fauna bodies grey-on-grey:
  dorrak the darkest step (a boiler), vekkit one step lighter (a moving shadow),
  krissek mid-grey at rest so the halo is the only colour it ever has.
- **What a render must show** (item step 2, verbatim): **transparency and fractal
  branching.** For the flora that means edges, refraction highlights and the ice
  visible *through* the body; a card that reads as a white plant on ice fails.
- **The vhessk brief's recognisability rule holds** (`creature_recognizability_rule.md`):
  no Earth-nameable silhouette. Dorrak is a six-legged boiler with a lid, not a
  tortoise; krissek is haunch-and-jaw with no ears and no tail; vekkit is a folding
  chair with hooks.

Prompts are the sprite pass's to write from the descriptions in §3–§5; this brief does
not pre-write them, because the prior brief's flora cards already carry the shape
language and the generator prompt must be iterated against the validator, not drafted
blind.

---

## 9. Mod Settings (step 5 of the item; `MOD_OPTIONS_RETROFIT_1` is the standard)

`mandrake.rm.bluedesert`'s settings screen, per the standing rule (every shipped
mechanic gets a toggle; defaults = shipped behaviour; all-off degrades gracefully):

| toggle | default | off means |
|---|---|---|
| **Native detonations** (fauna `RM_HydrocarbonCharge`) | on | the hediff is not given at generation — natives die like animals |
| **Flora chain reactions** (`RM_CompPlantCharge`) | on | plants die like plants; warm rooms do nothing to them |
| **Warm-reactive products** (`RM_ColdWax` temperature ruin → wick) | on | cold wax behaves as inert chemfuel-precursor |
| **Butane gut for foreign grazers** (§2f) | on | the outcome doer is a no-op |
| **Burner halo VFX** | on | `ShouldShowEffecter` returns false — purely cosmetic, listed because a player on a weak GPU will want it |
| **Warm-detonation threshold** (slider, −1…+15 °C) | +5 | tuning: how warm a room must be before flora and wax go |

No worldgen-affecting toggle exists here (nothing in this mod paints a tile); none is
labelled as such. The sheet's bans are NOT toggles — "no cultivation" is enforced by
the absence of `sowTags`, and a setting that added them would be a ban-2 violation.

---

## 10. What this brief explicitly does NOT decide

Left for the owner / BENCH, with the default that ships if nobody rules:

| open call | default here | why it is open |
|---|---|---|
| **The dovvik** (prior brief §6 card 8) — fourth resident fauna? | not rostered by this brief | not one of the sheet's four kinds; adding a resident is a sheet-level call |
| **Corpse warm-reactivity** (§2e) | corpses rot, do not detonate | ban-3 gap; closing it is a def-gen patch on generated corpse defs — real C#, filed as owed, named rather than hidden |
| **Juvenile blast radius** (§1d) | adult radius at every age | `HediffComp_ExplodeOnDeath` has no life-stage term; a per-stage radius would need a custom comp — or the owner may prefer that a calf-sized dorrak simply pops smaller |
| **krissek `baseHealthScale` 0.6** (§4a) | 0.6 | below the ∝-mass law on purpose (droppable from range); the owner may want it tougher and closer |
| **Tameability** | all three untameable | sheet §7 says harvest "at the fauna's own risk"; a tamed dorrak is a walking bomb in a barn, and a krissek pet is a torch in the kitchen. If he wants ranching, `RM_ButaneGut` and §1f already make the barn temperature the whole game |
| **The three donor plants in `wildPlants`** (§1a) | left as they are; `plantDensity` restore makes them live too once our plants set the map flag | the def comment flags this ban-1 tension itself and defers it; this brief does not resolve another seat's flag |
| **Pickers revealing buried salvage** (§5b) | no — they eat what is exposed | a new mechanic (dig-up job) tied to the debris-field injection, which is its own item |
| **A real light on the krissek** (§4b) | painted halo via effecter, no `CompGlower` | pawn-attached glow cost is unmeasured; spike it on one pawn first (the `TWINKLE_FLORA_SPIKE_1` pattern) |
| **`Hump` as the gut vs a bespoke BodyDef** (§3a) | reuse `QuadrupedAnimalWithHoovesAndHump` | cosmetic injury labels vs a small BodyDef build |
| **Ice-fog / drift interaction** | none | weather is the sheet's engine-feasibility line, separate owed work |
| **Pricing of cold wax** | unset | `ECONOMY_TRADE_SWEEP_1` |

---

## 11. Sources read for this brief

- `infrastructure/state/items/BLUE_DESERT_LIFE_AUTHORING_1.md`; `BLUEDESERT_RM_MOD_BUILD_1.md`;
  `design/RimMandrake/biome_mod_architecture.md` §3a and Phase A row 7; `MOD_OPTIONS_RETROFIT_1.md` (exists, standard)
- `design/Jawa/worldbuilding/biomes/the_blue_desert.md` (whole sheet; §0, §3, §4, §5, §6, §7, §9);
  `biomes/rosters/the_blue_desert.json`; `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_BlueDesert.xml`
- `creatures/goo_boom_commission.md` (format; §3b life-stage trap; §3d `DoExplosion` named args);
  `creatures/RUT_hydrocarbon_ecology_commission.md` §1, §6, §12–§14
- `Alien_Bestiary.md` §1; `design/NAMING_SCHEME_PLAN.md` (via the vhessk citation); `creature_names_ashkarr.md`
  (collision sweep); `biome_flora_rosters.md` (the `rukka cap` collision)
- `creature_normalization_doctrine.md`; `creature_size_model.md` §1, §4; `beast_normalization_spec.md` Law 3;
  `flora_commission_template.md` (size bins, one-accent law); `palettes/biome_palette_anchors.json`
- `src/RimUtinni/PlantGrowth/Source/Patch_Plant_GrowthRate.cs`, `PlantGrowthConfig.cs`
- `infrastructure/state/items/closed/TWINKLE_FLORA_SPIKE_1.md` (glow-cost verdict, cited not restated)
- Art census: `infrastructure/artpipe/registry.jsonl`, `done/`, `_artsrc/`, `art_status.json`, `src/RimUtinni/AshkarrFlora/_artsrc/`
- RimSage, installed 1.6 source: `CompProperties_Explosive`, `CompExplosive` (whole class),
  `CompTemperatureRuinable` + props, `PlantUtility.GrowthRateFactorFor_Temperature` / `_Light`,
  `PlantProperties` (fields 1–140), `Plant.cs` (lines 208–253, 350–375, 526, 598–728, 728–773, 810),
  `DeathActionWorker_BigExplosion`, `HediffCompProperties_ExplodeOnDeath` + comp, `HediffCompProperties_Effecter` + comp,
  `CompEffecter`, `CompProperties_EffecterBase`, `StartingHediff`, `PawnKindDef.cs:253`, `PawnGenerator.cs:1269`,
  `Thing.cs` (`hitPointsInt`, `PostMake`, `Ingested`), `DamageWorker.Apply`, `DamageWorker_Flame.Apply`,
  `HediffGiver_Heat`, `GenTemperature.SafeTemperatureRange`, `HediffComp.Notify_PawnPostApplyDamage`,
  `HediffSet.PartIsMissing`, `ThingComp.ReceiveCompSignal`, `Corpse.ButcherProducts`,
  `IngestionOutcomeDoer_GiveHediff`, `FoodTypeFlags`, `Pawn_PathFollower.MovingNow`, `Pawn.InAggroMentalState`,
  `Job.locomotionUrgency`, `WildPlantSpawner.cs` (lines 204–214, 408–438, 700–740), `FireUtility.cs` (negative search)
- RimSage, defs: `Ice` (TerrainDef), `Plant_Grass`, `Plants_Bases.xml`, `Plants_Cave.xml:7–9`, `Chemfuel` (raw),
  `Flame` (DamageDef), `Snowhare` (ThingDef + PawnKindDef), `Thrumbo`, `Moose` (`Odyssey/Races_Animal.xml:1132ff`),
  `Penguin` (`Odyssey/Races_Animal_Birds.xml:1237ff`), `Mech_Apocriton` (`Races_Mechanoids_SuperHeavy.xml:60–120`),
  `ApocrionAttached` (EffecterDef), `OrganicStandard` (HediffGiverSetDef), `Bodies_Animal_Quadruped.xml:582–595`,
  `Anomaly/Hediffs_Global_Misc.xml:20–60`, and the `ComfyTemperatureMin` sweeps across all `Defs/**/*.xml`
