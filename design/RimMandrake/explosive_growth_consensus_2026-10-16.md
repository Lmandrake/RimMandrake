# Explosive growth: the consensus model (2026-10-16)

Item: `EXPLOSIVE_GROWTH_RETHINK_SERIOUS_CONCERNS`. Status: **PROPOSAL** for an owner sitting. It feeds a further
design pass and a skeptical GPT review, so every number carries a tag:

- **MEASURED**: read from a file, a def or the 1.6 source, with `file:line` or the def path.
- **INFERRED**: worked out from measured values; the reasoning is given.
- **PROPOSED**: a number or rule this document invents. Nothing PROPOSED is ruled.
- **ASSUMPTION An**: a premise the model rests on. All of them are listed in §10, so a reviewer can attack them one
  by one.

Paths are relative to the repo root (`D:\Luke\dev\RimMandrake`). Today's measured build is in
`design/RimMandrake/explosive_growth_deep_dive_2026-10-16.md` §1. This document does not repeat it; it cites it as
"deep dive §n".

---

## 1. What the owner said today (verbatim, ledger `infrastructure/state/ledger/events/OWNER.jsonl`)

**The authoritative statement, 16:21.** It outranks every earlier document's framing:

> *"To be clear: the original design was simply me saying the dry-adapted alien plants of this world generally barely
> grow at all until they get access to water, then they grow x10 speed to take advantage of it. That's what I
> originally meant by 'explosive growth.' You heard that and misinterpreted it to mean they actually detonate, and I
> thought that was fascinating as a concept. So we accepted the exploratory idea that the plants grow and grow until
> at peak maturity they sometimes burst/die, resulting in many additional sprouts surrounding them. This was later
> adapted to a reduced growth factor in permanently wet areas and making fruit instead of bursting. I hope that
> clarifies the discussion that's been happening. Now we need to do a review of what's been planned and implemented
> here to bring everyone into consensus together."*

Three follow-ups the same afternoon, relayed by the coordinator (not yet ledger events at the time of writing):

> *"There are also outstanding questions about what constitutes plants 'getting watered' in Rimworld anyway. Rain vs.
> players dumping water on them vs. adjacency to permanent water. There needs to be a bit more worked out there."*
> (answered in §4)

> *"And a LOT of thought needs to be considered for what constitutes wet ground vs. mud vs. dry ground next to water,
> etc."* (answered in §5)

> *"There was also interaction/confusion between 'why aren't there any plants on the map' vs 'how fast do plants
> grow' since those numbers were linked previously but should not be. Each biome and its plants will likely need some
> tuning here, but hopefully not uniquely for each one."* (answered in §6)

**The statement's five claims, as this document reads them:**

| # | claim | reading used here |
|---|---|---|
| S1 | dry-adapted alien plants *"barely grow at all"* without water | a below-vanilla rate for those plants on dry ground |
| S2 | with access to water they grow *"x10 speed"* | ×10 vanilla-relative while watered; not ×10 on top of anything |
| S3 | the detonation was an agent misreading he found *"fascinating"*, accepted as exploratory: *"sometimes burst/die, resulting in many additional sprouts"* | bursting is optional spectacle, not the core; *"sometimes"* means not every plant, not every time |
| S4 | *"later adapted to a reduced growth factor in permanently wet areas"* | ground that is wet all the time grows slower than freshly watered ground |
| S5 | *"and making fruit instead of bursting"* | the normal peak-maturity outcome is fruit, not a burst |

---

## 2. Timeline of rulings and design changes

Each row: date, his words (verbatim, or marked when the record holds only agent prose), what it changed, and
**DRIFT** where an agent's reading moved away from his words.

| date | source | his words | what it changed | drift |
|---|---|---|---|---|
| 2026-08-15 | `design/Jawa/worldbuilding/PLANT_GROWTH_SPEC.md:4-9` (MEASURED: written "at the owner's instruction"; no verbatim quote in the file) | agent prose: *"every plant on this world grows at a rate that reads as obtrusive, aggressive, wrong"* | R-G2 (`:46-52`): **×4** wild plants and crops, **×2.5** trees, **×0.4** terminator, everywhere on the planet. `:60` also says *"on this world the limit on agriculture is WATER, not time"* | **DRIFT D2.** The spec states water is the limit, then builds a flat time multiplier that ignores water. His statement says dry plants *"barely grow"*; the spec makes every dry plant grow ×4 |
| 2026-08-15 | `design/Jawa/worldbuilding/hydrology_and_fire_ecology.md:139` (agent prose marked "Owner's ruling") | (not quoted) | R-H2b: the terminator poison forest is stunted; R-H3 (`:170`) makes fast growth the fuel of the Pyrelands fire loop | none on the terminator; R-H3 depends on D2 (see decision C5) |
| 2026-09-06 | `design/Jawa/worldbuilding/biomes/the_cracked_lands.md:271-283` | *"'OMG, what's going to happen?' should be the feeling near any water-soaked plant."* | Explosive growth becomes a world mechanic; the record adds *"It cannot grow forever, so what DOES happen at the top is a designed moment, meant to recur"* | **DRIFT D1.** Per his statement, "explosive" meant the ×10 speed; the "designed moment at the top" is where the detonation reading entered. He later accepted it as exploratory (S3), so it is drift he adopted, not drift to delete |
| 2026-09-09 | `design/Jawa/worldbuilding/explosive_plant_growth_design.md:44-48` (Fable draft) | none | 🄸 INVENTED: the soak multiplies the ×4 band (~×40). Burst is the default top | **DRIFT D3.** He said ×10 with water; the draft made it ×10 *on top of* ×4 = ×40 |
| 2026-09-10 | design doc §7 (`:334-361`) | *"All the jungle and river and miasma tiles should have the uncomfortable groaning swelling of ever shifting growth."* Pump: *"working as intended"* (record: *"No brake, no diminishing returns"*) | burst lethality capped at injury and knockdown; Fever Wood Flush in; stepped visuals; irrigation pump ruled as intended | the "No brake" was about water→food conversion, before the Churn existed (deep dive G4) |
| 2026-09-20 | design doc §8 (`:390-393`) | *"It's less about the biome and more about the plants IN that biome having different behaviors. … driven all by plant genetics / identity / adaptation to the intense sunlight and lack of water."* | the top is a property of the plant, not the biome; Burst sows ignoring zones; Slime and Tinder variants | none: this is the axis S1 uses ("dry-adapted plants") |
| 2026-09-21 | design doc §3, §9 | *"I fear that this entire capability has become distorted, and I'd like to restore its original intention."* · *"add sprouts next to it that keep going to keep the churn. And the fruit. So I guess this is a reversing back to the fruit burst at the top, plus the plant dies and makes babies too. Endless churn. That's good."* · *"Churn, fruit glut, let it be strange and alien and almost frightening. Just not explosive in the wet jungles."* · *"It's the same always-on, but stronger: x10 instead of x4 growth here."* · *"A dry plant in the greentide can burst."* · *"Support (2) but this would be VERY hard to weaponize and trigger properly. Support players who try."* · Rupture: *"Ruptures and turns towards the work of the Bioweapon contagion overdrive…"* | Churn (fruit + die + sprouts) becomes the default top; Burst only for dry-adapted plants; wet jungles ×10 ambient and *"x10 is enough"*; contaminated plants rupture | **Not drift: his own words** put death and sprouts into the Churn. Today's S5 (*"making fruit instead of bursting"*) does not mention death or sprouts. That tension is decision C2 |
| 2026-09-26/27 | item `infrastructure/state/items/EXPLOSIVE_PLANT_GROWTH_1.md:23`, Owed #7 (`:143-145`) | none | built: ×10 soak postfix **stacking** on the band; irrigation in a ×10 biome soaks and stacks (INVENTED default); every unlisted plant, trees included, defaults to Churn | **DRIFT D4.** Ruling 6 said the ×10 *replaces* soak-bursting in the jungles. The build gives ×100 there (deep dive G3), the opposite of S4's "reduced". **DRIFT D5.** Churn on a tree drops `harvestYield` wood: 25 logs per vanilla tree (deep dive G5). Fruit was meant, not lumber |
| 2026-09-26 | `src/RimMandrake/ExplosiveGrowth/Source/RM_SoakSources.cs:40,110` (MEASURED) | none | a dug channel re-soaks its strip every 2000 ticks, for 1 day each time: **permanent** soak | **DRIFT D6.** No difference between a fresh watering and permanently wet ground, so a channel becomes an endless 8-hour burst/churn engine (deep dive G4). S4 says permanently wet ground is the *reduced* case |
| 2026-09-26 | `src/RimMandrake/ExplosiveGrowth/Defs/ExplosiveGrowth/RM_ExplosiveGrowthRoster.xml:206` (MEASURED: `<soakWeathers />`) | none | rain never waters anything | **DRIFT D7.** "Access to water" in plain language includes rain. (In practice small: §4.2 shows our dry biomes have no rain weather) |
| 2026-10-16 04:00 | ledger | *"Please add the Explosive_plant_growth mod as part of the next sprint (three biomes + explosive)."* | in the sprint | |
| 2026-10-16 04:07 | ledger | *"Yes, Explosive Plant Growth should move into Baroque Biomes. It should only natively apply to plants within the Baroque Biomes, though option settings could allow it to apply to other plants from other mods or vanilla basegame (irrelevant in Utinni). Simpler."* | moved into Baroque Biomes; scope = our plants | |
| 2026-10-16 12:18 | ledger | *"It seems absolutely (2) because those mods are fusing! They were never meant to be apart. Especially because in dry places the plants won't be growing almost at all unless water is present, then they grow explosively. So yes, always together, fuse them as a single mod right now and let's tune them all together."* | Jawa Plant Growth fused into the engine (built `b9a689a8ab`) | **DRIFT D8.** The fusion kept the flat ×4 bands unchanged. His reason for fusing (*"won't be growing almost at all unless water"*) was recorded as a tuning note (kickoff §1.4 "dry ground near-still") instead of changing the model |
| 2026-10-16 12:23 | ledger | *"Yes, there should just be an option in Baroque Biomes to allow the accelerated plant growth and explosive growth to apply to other biomes, but we won't test or support that."* | scope option, off, unsupported | |
| 2026-10-16 12:49 | ledger, by card | "Should the everyday 4x plant growth be on by default for players who install Baroque Biomes without the campaign?" → **"Yes, on for everyone"** | ×4 on by default without the campaign | **DRIFT D9.** The card asked about *on/off*, framed around ×4. Its answer fixes "on by default for everyone"; it did not choose ×4 over a moisture model, which was never offered. This document keeps the answer (the growth system is on for everyone) and replaces the number (§3) |
| 2026-10-16 13:31 | ledger, by card | "Which water controls / landscape controls should I build?" → "Flood trigger + Soak zone (all eight picked)" | Soak Zone marker built (`src/RimMandrake/FloodedCanyon/Source/MapControls/Building_RM_SoakZone.cs`) | |
| 2026-10-16 14:59 | ledger, by card | "ExplosiveGrowth X1-X5 → Approve" | kickoff `design/RimMandrake/biome_sprint_kickoff_2026-10-15.md:489-501` approved | |
| 2026-10-16 15:53 | ledger, by card | "speed bar → at least 90%; EG loose ends → agree to all" | S0-6: TPS at speed 3 ≥ 90% of soak-off. S0-7 agreed: cut salted-ground refusal; defer the close-up layer and Fever Wood interior; keep invented roster defaults; add `RUT_`/`RM_Cauldron` to the stalled band and keep `RUT_ExtremeDesert` out of ×4; tune bands and soak together at the S2 walk (kickoff `:34`) | |
| 2026-10-16 15:53 | ledger | *"I have SERIOUS concerns about explosive growth…"* | this item | |
| 2026-10-16 16:21 | ledger | the statement (§1) | this document | |

**The drift in one paragraph.** He described a **water switch**: dry-adapted plants nearly stop, water makes them
grow ×10. The record turned it into a **time multiplier** (×4 everywhere, D2), then a **detonation** (D1, which he
liked and kept as exploratory), then **stacked** the two (D3, D4), never distinguished **fresh** water from
**permanent** water (D6), and fused the two mods without revisiting the model (D8, D9). The result is the opposite of
his description in dry places (deserts grow ×4 with no water) and in permanently wet places (×40 to ×100 plus a top
every 8 hours, where he asked for a reduced factor).

---

## 3. The consensus model

Plain language first, numbers after. Every number is PROPOSED unless tagged.

### 3.1 The rule in four sentences

1. **A dry-adapted alien plant on dry ground barely grows.**
2. **When its ground gets water, it grows ten times vanilla speed** for as long as the water is fresh.
3. **Ground that stays wet settles to a reduced rate**, because the plants there are no longer racing a short window.
4. **At peak maturity on freshly watered ground, a plant fruits.** A few dry-adapted plants sometimes burst instead,
   which is the exploratory spectacle he kept.

### 3.2 (a) Baseline: who counts as dry-adapted, and what "barely" is

**The plant classes** (a property of the plant, per his 2026-09-20 ruling, never of the tile):

| class | members | source of the list |
|---|---|---|
| **dry-adapted** (the default) | every plant def shipped by Baroque Biomes or the Utinni/Star Wars tiers (prefixes `RM_`, `RUT_`, `RSW_`, and the composed donor plants such as `RG_`, `RM_FE_`) that is not in another class | PROPOSED rule: alien flora is dry-adapted unless named otherwise. ASSUMPTION A1 |
| **wet-adapted** | plants native to the three wet jungles (`RM_Greentide`, `RM_Miasma`, `RM_FeverWood`) | the `wetAmbientBiomes` roster list (MEASURED, `RM_ExplosiveGrowthRoster.xml:212-216`) turned from a biome list into a plant list by reading each biome's `wildPlants` |
| **stunted** | terminator plants (`RM_Cauldron`, `RUT_Cauldron`, `PoisonForest` natives) | S0-7 agreed list, R-G3 |
| **exempt** | anima, Gauranlen, ambrosia, `growDays` < 1, cave plants and fungi, the three Blue Desert plants | today's exemptions (MEASURED, `RM_ExplosiveGrowthRegistry.cs:199-208`) |
| **imported** | vanilla and other-mod plants, player crops included | decision C4 |

**"Barely" = ×0.25 of vanilla** (PROPOSED, decision C6). INFERRED effect with the deep dive's daylight factor (plants
grow 55% of the day, deep dive §1.5): grass (2.5 growDays) takes about **18 calendar days**, a 6-day bush about
**44 days**. A dry map is visibly static over a season, which is his "barely grow at all". ×0.25 is lower than the
terminator's ×0.4 on purpose: the terminator is *stunted* (sick), a desert plant is *waiting*.

### 3.3 (b) Water → ×10

While a cell is **watered** (§4 defines it), a dry-adapted plant on it grows at **×10 vanilla**. This **replaces**
the baseline; nothing multiplies it (fixes D3/D4). Trees keep R-G2's ratio (*"wood stays a decision"*): watered
trees run ×6.25 (10 × 2.5/4). INFERRED effect: grass is grown in about half a calendar day, corn in about two days.

### 3.4 (c) Permanently wet → a reduced factor

A cell that has been watered **without a break for 3 days** becomes **settled-wet** (PROPOSED numbers, decision W3).
Dry-adapted plants on settled-wet ground grow at **×4** (trees ×2.5). That is the old planetary ×4, kept as the
number for ground that is always wet: riverbanks, a long-running channel, a 24-hour Soak Zone.

**Wet-adapted plants** (the three jungles' natives) grow at **×10 on their own ground, always**, which is ruling 6's
number. They are not dry-adapted, so S1/S2 do not apply to them. A watering adds nothing to them (no stacking, ever).
Whether S4's "reduced" means these jungles should drop below ×10 is decision C1.

How settled-wet is told apart from a fresh soak is in §4.4.

### 3.5 (d) Peak maturity: fruit, and where bursting still belongs

**The default outcome is Fruit** (PROPOSED shape, decision C2):
- It happens only on a **fresh** watering (§4.4), once per plant per watering event. Settled-wet ground never triggers
  it, which ends the 8-hour churn engine (D6).
- The plant swells and shows the tell ladder as today (deep dive §1.4 step 3), then **drops its fruit** (its
  `harvestedThingDef` × yield) and **lives on**, reset to 60% growth (Flush-shaped; PROPOSED).
- A plant whose harvest is wood, or that has no harvest, drops **nothing** (fixes D5: no self-felling trees).

**Bursting stays as the rare exploratory top** (S3 *"sometimes"*):
- Only **dry-adapted** plants, only on a **fresh** watering, with a **15% chance per plant per event** (PROPOSED,
  decision C3). It keeps today's content: pop, scattered produce, injury-and-knockdown ceiling, sprouts that ignore
  zones (2026-09-20).
- **Tinder** and **Slime** stay as Burst variants on the plants that carry them.
- **Rupture** (contaminated plants) stays as ruled 2026-09-21: it is a different fiction (the bioweapon), not the
  water rule.
- **Flush** (Fever Wood giants) is already fruit-and-live; it becomes the general shape of Fruit.

INFERRED consequence: a canyon flood still sets a valley off in a synchronised wave (every grown plant fruits about
6 h after the water, and roughly one in seven dry-adapted plants bursts). A permanently irrigated field grows fast
and fruits once, when its water first arrives, then settles.

### 3.6 (e) What happens to each piece of today's build

| today (deep dive ref) | consensus |
|---|---|
| everyday ×4 band, trees ×2.5 (§1.1) | **removed as a flat band.** ×4 / ×2.5 survive only as the settled-wet rate |
| wet-jungle ×10 band, trees ×6.25 | kept as the **wet-adapted plants' home rate**; never stacks |
| stalled band ×0.4 | kept for **stunted** plants; S0-7's Cauldron addition applies; stunted plants never take water events |
| `RUT_ExtremeDesert` ×4 exemption (S0-7) | becomes automatic: no water source there, so dry ×0.25; it also stays on the no-soak list, so HARD BAN 4 (*"No fast growth"*) holds |
| soak ×10 **multiplying** the band (§1.1, G3) | **replaced** by the cell's moisture state choosing one rate |
| the swelling and tell ladder (§1.4) | kept, once per plant per fresh watering, before Fruit or Burst |
| Churn: fruit + die + 2–4 sprouts, default for every plant (§1.4) | replaced by Fruit (decision C2 asks whether death and sprouts survive) |
| the extra sprout sown at arming | removed (it belonged to the Churn) |
| harvest jackpot ×(1 + charge) on any yield (G6) | harvest only (X4); the last-swing gamble starts at the first swell, not at 0.70, so the bonus always carries risk |
| trees → 25 logs (G5) | removed (wood is never a top drop) |
| suppression (grazing, blower) | kept: suppression dries a cell (§4) |

### 3.7 (f) Scope and settings

- **Scope** is unchanged: Baroque Biomes' own biomes; the off, unsupported option for others (12:23); the campaign
  roster's `scopeAllBiomes` puts every biome in for Utinni (04:07, *"irrelevant in Utinni"*). INFERRED consequence
  worth stating: with the campaign, vanilla biomes are judged by the same water rule, so a vanilla desert also
  stalls (ASSUMPTION A6).
- **On for everyone** (12:49 card) stays: the moisture model is on by default.
- **Settings** (replacing the band sliders, `src/RimMandrake/ExplosiveGrowth/Source/ExplosiveGrowthMod.cs:37-41,
  158-273`): dry rate; watered rate; settled-wet rate; tree factor; wet-adapted home rate; stunted rate; watered
  decay; settle days; dry-reset days (§4.4); a toggle per water source (§4.2); Fruit on/off; Burst chance; the
  existing Rupture, tell and suppression switches. One "classic" preset could restore today's flat ×4 for players
  who want it (PROPOSED; decision C6 option).

---

## 4. What counts as "watered"

*Self-contained section, per the owner's follow-up: "Rain vs. players dumping water on them vs. adjacency to
permanent water."*

### 4.1 What vanilla RimWorld 1.6 offers (MEASURED, 1.6 source via RimSage)

- **There is no soil-moisture grid in vanilla.** A search of the 1.6 source for `moisture`, `wetness` and similar
  finds none. Plant growth (`Plant.GrowthRate`) reads fertility, light and temperature only (deep dive §1, Plant.cs).
- **Rain is one number for the whole map**: `WeatherManager.RainRate`, lerped between the last and current weather's
  `WeatherDef.rainRate` (`Source/RimWorld/WeatherManager.cs:45`, `Source/Verse/WeatherDef.cs:37`). Vanilla uses it per
  cell only by checking the roof (for example `SteadyEnvironmentEffects.cs:124`, `StatPart_EnvironmentalEffects.cs:69`).
- **Floods exist in 1.6 (Odyssey)** as temporary terrain: `SeasonalFlood` and `TorrentialRainFlood` (both
  `Flood : Thing`, `Defs/Odyssey/ThingDefs_Misc/Ethereal_Various.xml:19,26`) lay `ShallowFloodwater` over cells with
  `TerrainGrid.SetTempTerrain` and queue its removal (`Source/RimWorld/SeasonalFlood.cs:96-97`,
  `TorrentialRainFlood.cs:93,104`).
- **Snow** is a per-cell depth grid (`map.snowGrid`, vanilla); a thaw lowers it. No vanilla code links snowmelt to
  plants (INFERRED from the absence of any moisture reader).
- **Wet terrains** are fixed TerrainDefs (`Mud`, `MarshyTerrain`, `SoilRich`, `Marsh`, `WaterShallow` and others,
  `Defs/Core/TerrainDefs/Terrain_Natural.xml:111,154,356`, `Terrain_Water.xml:52-164`). §5 inventories them.

So "watered" is new machinery in every case; vanilla gives us only the inputs.

### 4.2 Every way a cell could count as watered

Columns: how it is detected cheaply; how long the cell stays watered after the source stops; whether the source makes
a **fresh** event (eligible for the ×10 and the peak outcome) or only **sustains** wet ground (counts toward
settled-wet); and the cost.

| source | detection | stays watered after it stops | fresh or sustaining | cost | today |
|---|---|---|---|---|---|
| **Rain (water rain only)** | map scalar: an allow-list of water weathers (`Rain`, `FoggyRain`, `RainyThunderstorm`, `TorrentialRain`, `RSW_SW_RedFoggyRain`, `RUT_BoilingRain`?) × cell unroofed. No per-cell storage: the map keeps `lastWaterRainTick` | 12 h (PROPOSED) | **fresh** for every unroofed cell of the map that was dry ≥ dry-reset days | one map check per pass; the plant postfix tests "unroofed" (one grid read) | never (`<soakWeathers />`) |
| **Non-water rain** | the same allow-list excludes it | — | never | — | — |
| **Snowmelt** | a slice of `snowGrid` per pass; depth falling while above 0 °C | 12 h | fresh | a 1/8-map slice per 250 ticks, like irrigation | not built |
| **Players pouring water** | event-driven: the hose Outflow spill (`src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidSpill.cs:14-21`, MEASURED: a water spill on dry ground today makes filth only) calls the soak at the spill cell; a future "water plants" job calls it per cell | 1 day | fresh | zero polling | not built; no "water a plant" job exists (MEASURED: the bottle work-givers are fill, wash, empty-into-tank and fill-from-tank, `Defs/LiquidTypes/WorkGiverDefs/RM_LiquidBottleWorkGivers.xml:19-70`) |
| **Irrigation channel** | today's sweep: a dug FlowWorks cell holding fresh water or slime soaks itself and 8 neighbours (`RM_SoakSources.cs:98-112`) | 1 day after the last re-read (`RM_SoakSources.cs:40`) | fresh when the channel first fills; then sustaining, so it settles after 3 days | today's 1/8-map sweep | built (permanent soak) |
| **Permanent natural water nearby** | a bitset built at map load from each terrain's §5 moisture class (open water, shallow water, waterlogged, damp; never `IsWater`, §5.1) within **radius 2** (PROPOSED, decision W2), updated by a `TerrainGrid.SetTerrain` postfix | permanent | **sustaining only**: these cells are settled-wet from the start and never make a fresh event | one-off build; one bit read per plant | never (rivers and lakes never soak, `RM_SoakSources.cs`, per deep dive §1.3) |
| **Wet terrain itself** (waterlogged and damp classes, §5.3) | the same bitset (the cell's own terrain) | permanent while the terrain is there | sustaining | same | never |
| **Canyon flood** | today's kernel (`src/RimMandrake/FloodedCanyon/Source/Kernel/RM_FloodKernel.cs:163-166`) | flood + 4 days (MEASURED, deep dive §1.3) | fresh | today's | built |
| **Vanilla 1.6 floods** (`ShallowFloodwater`) | postfix on `TerrainGrid.SetTempTerrain` for flood terrains | the temp terrain's life + 1 day | fresh | event-driven | not built |
| **Miasma salt-line surge** | today's surge band (`RM_SoakSources.cs:114-132`) | 1 day | fresh | today's | built |
| **Bloom event** (`RUT_BloomBurst`) | today's incident | 24 h | fresh | event | built (campaign, quest-only) |
| **Soak Zone marker** | today's marker (`Building_RM_SoakZone.cs:83`) | its schedule | fresh on its first hours; a 24 h/day zone settles after 3 days; a zone set to pulse with gaps ≥ the dry-reset re-arms | today's | built |
| **Greentide extract** | item use, event-driven | 1 day | fresh | event | not built (no item) |

Saline, poisoned and non-water liquids never water anything (2026-09-09 design §1, MEASURED taxonomy rows); §5 lists
which terrains those are. Suppression (grazing, the dry-air blower) removes the watered state and blocks it, as today.

**MEASURED: rain hardly matters in our dry biomes.** Parsing `baseWeatherCommonalities` of every RM_ BiomeDef: Stillsand,
Long Shade, Wasteland, Cauldron, Leaning Scrub, Weeping Stones, Rust Cathedral, Blue Desert, The Sump and Nightside Ice
give every water rain weight 0. Water rain falls in Miasma (Rain 10, RainyThunderstorm 5, FoggyRain 4), Webwork,
Contagion, Gelatinous Slime, Greentide and Twilight Sea (Flooded Canyon no longer rains: owner 2026-10-16, no precipitation). Several rains are **not water**:
`RM_SheenFall/Storm/Mist` (The Rot, the Sheen), `RM_Weather_SlimeRain`, `RM_FE_BlackRain` (Pyrelands),
`RM_BoilingRain` (The Forge), `RM_ContagionBloom`, `ToxRain` (Warscar). Each has `rainRate` > 0 (MEASURED from their
WeatherDefs), so **a rule keyed on `rainRate` would water plants with sheen, slime and tox. The rule must be an
allow-list.** Whether `RM_ContagionBloom` counts as `red_water` (design §1 lists Contagion rain as a qualifying soak)
is open (ASSUMPTION A4).

### 4.3 The model: one moisture value per cell, two thresholds

PROPOSED. It replaces today's single "wet until" timer (`RM_ExplosiveGrowthKernel.cs:146`).

- **Storage.** Sparse, as today: per cell `wetUntil` (tick), `wetSince` (tick the current wet spell began) and
  `dryAt` (tick the last wet spell ended). Permanent-water cells are a separate bitset, not dictionary entries.
- **Sources** set `wetUntil = max(wetUntil, now + duration)` (today's rule, `RM_ExplosiveGrowthKernel.cs:165-173`).
- **Decay.** A cell is watered while `now < wetUntil`. When it lapses, `dryAt = wetUntil`.
- **Threshold 1, watered.** `now < wetUntil` (or the cell is in the permanent bitset, or rain applies to it).
- **Threshold 2, settled-wet.** In the permanent bitset, or `now − wetSince ≥ 3 days` (PROPOSED).
- **Fresh event.** A cell becomes watered after having been dry for at least **2 days** (`now − dryAt ≥ 2 days`),
  PROPOSED dry-reset. Only a fresh event sets `wetSince = now` and arms plants for the peak outcome.

The plant's rate is then one lookup:

| cell state | dry-adapted | wet-adapted | stunted | exempt |
|---|---|---|---|---|
| dry | ×0.25 | ×1 (PROPOSED: outside its jungle it grows at vanilla speed) | ×0.4 | ×1 |
| watered, fresh (< 3 days) | **×10** | ×10 | ×0.4 | ×1 |
| settled-wet | ×4 | ×10 | ×0.4 | ×1 |
| in a wet-adapted plant's home biome | (as above) | ×10 always | — | — |

### 4.4 Fresh versus permanently wet: why a timer and not terrain

His S4 contrast is in time, not in place: the same channel is a windfall on day 1 and the ground's normal state by
day 10. A timer captures that with three numbers and no new terrain. Terrain answers the other half: natural water and
mud are wet from the start, so they enter as settled-wet and never make a fresh event. INFERRED consequences:
- A player who wants repeated fruiting must **cycle** the water (wet, then dry ≥ 2 days). That costs water and
  labour, which is the water doctrine's tension, and matches ruling 7 (*"VERY hard"* to trigger, but possible).
- A flood or a rain on a long-dry map fires the whole map at once: synchrony, the "great moment".
- Perf worst case moves from "a 400-cell flood" to "a map-wide rain on a dry map" (§8, X2).

### 4.5 Owner decision lines for watering (card-ready)

**W1. Does rain water plants?**
1. *(Recommended)* **Yes, water rain only, and it is a fresh event for every unroofed dry cell.** A rare rain on a
   dry map makes the whole map shoot up and fruit. *Trade: the biggest perf case (X2 must test it); deserts with no
   rain weather are unaffected.*
2. Yes, but rain only sustains (counts toward settled-wet, no fruiting event). *Trade: no map-wide spectacle; safe.*
3. No, as today. *Trade: plain-language "access to water" excludes the commonest water.*
4. *(write your own)*

**W2. How close to permanent water does ground count as wet?**
1. Only the water and mud cells themselves. *Trade: banks look dead next to a river.*
2. *(Recommended)* **Within 2 cells**: a thin green riverbank and pond rim, settled-wet (×4), never fruiting from it.
3. Within 4–6 cells: a wide oasis. *Trade: rivers green a large part of a map.*
4. *(write your own)*

**W3. How long until watered ground counts as "permanently wet", and how long must it dry before water is "fresh"
again?**
1. *(Recommended)* **3 days to settle, 2 days dry to re-arm.** A watered field gets one burst of ×10 and one fruiting,
   then ×4.
2. 1 day to settle, 5 days to re-arm. *Trade: the ×10 window is short; cycling barely pays.*
3. 7 days to settle, 1 day to re-arm. *Trade: close to today's permanent churn.*
4. *(write your own)*

**W4. Should players be able to pour water on plants directly?**
1. *(Recommended)* **Yes, through FlowWorks' hose: water leaving an Outflow end onto open ground waters that spot.**
   Small, uses a built system. *Trade: a cross-mod hook into FlowWorks, which another agent owns.*
2. Yes, plus a "water plants" job with bottles. *Trade: a new job and work-giver.*
3. Not now; channels and the Soak Zone are enough.
4. *(write your own)*

---

## 5. Ground moisture taxonomy

*Owner: "And a LOT of thought needs to be considered for what constitutes wet ground vs. mud vs. dry ground next to
water, etc."*

Sources (MEASURED unless tagged): the 1.6 install's Core/Odyssey/Anomaly TerrainDefs; Alpha Biomes 1.6
(`workshop/294100/1841354677`, a hard dependency of `mandrake.rm.biomes`); every TerrainDef in `src/`. The
`biomes_sprint` tier is `ratchet_pilot` + HugeThings (`src/RimMandrake/Utils/modset_builder.py:620-690`). Other
workshop mods in the owner's full list were **not** swept (ASSUMPTION A11: they add no moisture-relevant terrain to
our biomes, because our BiomeDefs only name the terrains below).

### 5.1 What vanilla does with wet ground (MEASURED)

- **Mud is a fixed terrain, not a state.** `Mud` (fert 0, pathCost 14, tag `Mud`, `driesTo` Soil) is placed only by
  map generation (`Source/RimWorld/MapGenUtility.cs:240-244`). Nothing turns soil into mud after rain or a flood.
- **`driesTo` is one-way**, used by the moisture pump (`CompTerrainPumpDry.cs:64-72`) and road generation. Nothing
  re-wets ground.
- **Odyssey floods are an overlay.** `SeasonalFlood` and `TorrentialRainFlood` lay temporary terrain
  (`ShallowFloodwater`, or the source's `floodTerrain`, `MarshFlood` for Marsh) and remove it later
  (`SeasonalFlood.cs:96-97`, `TorrentialRainFlood.cs:93,104`). The base terrain comes back unchanged: **a flood leaves
  no mud and no wet state.**
- **`TerrainDef.IsWater` is only `HasTag("Water")`** (`Source/Verse/TerrainDef.cs:324`). It cannot tell fresh water
  from brine, poison, tar, slime or propane, and some non-water carries the tag: `RM_DeepSand` (a sand floor), and
  every FlowWorks `RM_Fill_*` overlay, oil and blood included. **No existing tag means "fresh water".**
- **Mud and marsh have fertility 0** (`Mud`, `Marsh`, `AB_DarkMud`, `AB_SlimyMud`): nothing sown grows on them.
  `MarshyTerrain` (fert 1.0, pathCost 14), `AB_FertileMud` (1.0, 12) and `AB_DenseMud` (0.8, 20) are the wet ground
  plants *can* stand on.

### 5.2 What our mods write (MEASURED)

| event | terrain written | where |
|---|---|---|
| dig a channel | base `RM_Channel_Empty/Mid/Deep/Superdeep` (fert 0, tag `Soil`) | `FlowWorks/Source/JobDriver_DigCanal.cs:74`; `RM_MapComponent_Excavation.cs:946-952`; `RM_ExcavationDepth.cs:84-90` |
| channel fills | temp overlay `RM_Fill_<Liquid>_<tier>` (tags `Water`, `Flood`) | `RM_MapComponent_Excavation.cs:2090-2118` |
| channel drains | overlay removed → bare dry trench; **no damp bank, no mud** | `:2114,2131` |
| channel filled in | the recorded original terrain, else a neighbour vote, else `Soil` | `:1296-1330,1500-1549` |
| pond recedes | base `RM_Lakebed_Shallow/Deep/Abyss` (fert 0, dry cracked bed) by default; vanilla `Mud` (or `AB_TarMud` for tar) only with the pond-hollow setting off | `:1552-1590`; `RimMandrakeFlowWorksMod.cs:126`; `Defs/Canals/FluidDefs/FlowWorks_Fluids.xml:37-162` |
| canyon flood | permanent base `WaterMovingShallow` | `FloodedCanyon/Source/RM_MapComponent_CanyonFlood.cs:485-494` |
| canyon flood recedes | every still-flooded cell becomes `SoilRich` (fert 1.4), whatever it was before (sand, gravel, mud, marsh) | `:557-575`; `Kernel/RM_FloodKernel.cs:296-300` |
| Twilight channels gen | `RM_BankSilt` (fert 0.9, pathCost 3) | `TerminalBiomes/Source/RM_GenStep_TwilightChannels.cs:157` |

Irrigation accepts a dug cell by its **fluid defName**, not its terrain (`src/RimMandrake/_Shared/FlowWorksIrrigation/FlowWorksIrrigationRead.cs:13-14,76-99`):
ExplosiveGrowth accepts `RM_Fluid_Water` and the four `RM_Fluid_Slime*` (`RM_ExplosiveGrowthRoster.xml:194-204`); the
Pyrelands ash field accepts water only (`Pyrelands/.../PyrelandsAshField.cs:58,286`).

**No mod writes a damp-ground or bank state.** "Damp" is new.

### 5.3 The terrains, by proposed class

Fert = fertility; pc = pathCost. Biomes are where our BiomeDefs place the terrain (MEASURED by the census's XML scan).

| proposed class | terrains (fert / pc) | our biomes using them |
|---|---|---|
| **open water (fresh)** | `WaterDeep`, `WaterMovingChestDeep` (– / 42), ManyWaters `RM_Water_{Rust,Verdigris,Amber,Violet,Chalk}`, `RM_WaterFrigid*` | rivers; Pyrelands; ManyWaters ponds |
| **shallow water (fresh)** | `WaterShallow` (– / 30), `WaterMovingShallow` (– / 30), `RM_Fill_Water_*`, `RM_Fill_IcyWater_*`, Odyssey `ShallowFloodwater`, `SpringFlood` | Pyrelands, Lantern Deeps, rivers, Flooded Canyon flood, dug channels |
| **waterlogged** (wet all the time; most grow nothing) | `Mud` (0 / 14), `Marsh` (0 / water), `MarshFlood`, `RM_Churnmud` (– / 60), `RM_GreentideChurnmud` (– / 34), `AB_DarkMud` (0 / 12), `AB_SlimyMud` (0), `AB_Quicksand`; **plantable:** `MarshyTerrain` (1.0 / 14), `AB_FertileMud` (1.0 / 12), `AB_DenseMud` (0.8 / 20), `AB_FertileMarsh` (0.7 / 1), `AB_WebbedMarshyTerrain` (0.75 / 25) | Miasma, Pyrelands, Webwork, Greentide (mud slot); Cauldron (Marsh); Warscar, Wasteland (MarshyTerrain) |
| **damp** (wet-ish soil by water) | `Riverbank` (1.4 / 4), `RM_BankSilt` (0.9 / 3), `RM_BankSilt_Rich` (1.4 / 3), `SWCPTerrain_junkyardgarbage_soggy` (0.25 / 16) | Cauldron, Greentide, Leaning Scrub, Pyrelands (riverbank slot); Twilight Sea channels |
| **dry soil** | `Soil` (1.0 / 2), `SoilRich` (1.4 / 2), `Gravel` (0.7 / 2), `GrasslandSoil`, `RM_CauldronSoil(Rich)`, `RM_FE_Ground_Soil(Rich)`, `RM_TheRotSoilRich`, `GU_AlienSand`/`GU_RichAlienSand` (0.9/1.2), `AB_ForsakenSand` (1.0), `AB_CrackedMud(Rich)` (0.8/1.2), `AB_ParchedEarth` (0.7 / 30) | most biomes |
| **arid** (sand, beds, trenches) | `Sand` (0.1 / 4), `SoftSand` (0 / 14), `RM_DeepSand` (0 / 300), `AB_FineSand`, `GU_AlienSandFine`, `AB_GrassySand` (0.1), `DryLakeBed`, `RM_Lakebed_*` (0), `RM_Channel_*` (0) | Stillsand, Long Shade, Leaning Scrub, Weeping Stones, Flooded Canyon, Contagion, Sump |
| **never waters** (non-fresh liquid or salt) | brine/brackish/mineral `RM_WaterBrine*`, `RM_WaterBrackish*`, `RM_WaterMineral*`, `RM_BrinePool*`; salt crusts `RM_SaltCrustShore`, `RM_MiasmaSaltCrust`, `RUT_Jawa_SaltCrust`; poisoned/toxic `RM_WaterPoisoned*`, `RM_WastesBrine*`, `RUT_WastesBrine*`, vanilla `ToxicWater*`, `ToxicFlood`; non-water `RM_{Acid,Ammonia,Coolant,FuelSap,Ichor,Ooze,Propane,ReactionLiquor,Tar}*`, `RUT_Scald*`, `AB_Tar`, `AB_LiquidLava`, `AB_Propane*`, `HotSpring`?; fills `RM_Fill_{Oil,Poison,Blood,Chemfuel,Astrofuel,Tar,BoilingWater}_*`; ocean `WaterOcean*` (salt on Ash'karr, ASSUMPTION A12) | Grey Sea, Twilight Sea, Wasteland, The Chill, The Scald |
| **slime** (watering by today's roster; ASSUMPTION A13) | `RM_Fill_Slime*`, `RM_Slime_{Rust,…}` pools, `RM_Slime_Liquid`/`Mud`, `AB_LiquidSlime` | Gelatinous Slime |

Open questions inside the table (ASSUMPTION A14): `HotSpring` and `RM_WaterBoiling*` (hot water: watering or
scalding?); `GU_RedWater*` and `AB_LightRedWater*` (Contagion red water: design §1 lists `red_water` as qualifying).

### 5.4 How each class is detected, and what it counts as

**Detection (PROPOSED):** a moisture class per TerrainDef, held as data in the roster (a `terrainMoisture` list, or
a small `DefModExtension` on the terrain), read once into a per-def array at startup. A cell's class is then one
array read of its top terrain (temp overlay first, then base). **Never `IsWater`** (§5.1). Unclassified terrain
counts as dry soil and is logged once at startup so new terrains surface.

| class | counts as (§4.3) | plants on the cell | its neighbours |
|---|---|---|---|
| open water | — (no plants) | — | settled-wet within the W2 radius |
| shallow water | — (no plants), except a temporary flood overlay: the cells under it are **fresh** when it lands | — | settled-wet within the W2 radius; a flood overlay instead makes its rim fresh |
| waterlogged | settled-wet | fert-0 kinds grow nothing; plantable kinds grow at the settled rate | settled-wet within the W2 radius |
| damp | settled-wet | settled rate | nothing extra |
| dry soil | dry unless a source (§4.2) waters it | dry rate | — |
| arid | dry unless watered; vanilla fertility (0–0.1) already keeps it near-empty | dry rate × its low fertility | — |
| never waters | blocks: a cell next to *only* never-water terrain stays dry | — | no effect (salt shore stays barren) |
| slime | today's roster waters with it; keep as fresh/settled like water (A13) | — | as shallow water |

### 5.5 Transitions: state or terrain?

**Recommendation: wetness is a state on the cell (§4.3's timer), not a terrain change**, with the two terrain writes
that already exist kept as they are:
- **Rain or a watering does not turn soil into mud.** It sets the moisture timer only. Reason: a terrain swap changes
  fertility (soil 1.0 → mud 0, so it would *kill* the plants it watered), pathCost (2 → 14) and floors, and fights
  vanilla's own fixed-mud design. (INFERRED from the fert/pc values above.)
- **Draining a channel or a pond recession** leaves the trench or lakebed as today; the cells and their ring stay
  **watered for the decay time** (1 day, then dry), PROPOSED. No damp terrain is written.
- **The canyon flood's recession to `SoilRich`** stays: it is the lasting gift of the flood (fertility 1.4 where sand
  was), and it is already built. That is a fertility change, not a wetness one; the wetness lasts 4 days, as today.
- **Ground near permanent water stays damp** by the W2 bitset, recomputed when terrain changes. No terrain write.
- **New machinery (not vanilla):** the terrain class table, the bitset, the timer fields (`wetSince`, `dryAt`).
  **Vanilla already provides:** fixed mud and marsh, floods as overlays, `driesTo` for moisture pumps (which then also
  remove settled-wet ground: a pump drying marsh to soil drops it out of the bitset by the terrain postfix).

Walk speed and fertility therefore change only where they already change today (dug channels, receded ponds, the
flood's SoilRich, a moisture pump). The moisture model touches growth rate only.

**T1. Should water ever turn soil into mud (or mud dry back to soil)?**
1. *(Recommended)* **No: wet is invisible state; terrain stays as it is.** Plants show the water by growing. *Trade:
   the ground does not look wet; the darkening "ground tell" filth (today's) is the only visible sign.*
2. Floods and channel spills leave a temporary mud overlay that dries back in a few days. *Trade: mud has fertility 0,
   so the plants under it stop; slower walking; new overlay code.*
3. A new "wet soil" overlay that keeps soil's fertility and adds a darker look and pathCost 4. *Trade: a new terrain
   per soil type; art.*
4. *(write your own)*

**T2. Hot water, red water and slime: do they water plants?**
1. *(Recommended)* **Slime yes (as today), Contagion red water yes (design §1), hot springs and boiling water no.**
2. Only plain fresh water, nothing else.
3. *(write your own)*

---

## 6. Plant density versus growth speed

*Owner: "There was also interaction/confusion between 'why aren't there any plants on the map' vs 'how fast do plants
grow' since those numbers were linked previously but should not be. Each biome and its plants will likely need some
tuning here, but hopefully not uniquely for each one."*

### 6.1 Two different questions

- **Density**: how many plants a map starts with and how fast empty ground refills. Vanilla inputs: `BiomeDef.plantDensity`,
  each `wildPlants` commonality, cell fertility, and `BiomeDef.wildPlantRegrowDays`.
- **Growth**: how fast a plant that already exists matures. Vanilla input: `growDays` × `Plant.GrowthRate`; ours: the
  rate in §4.3.

### 6.2 What vanilla 1.6 actually does (MEASURED, 1.6 source via RimSage)

- **Count** is density × fertility × saturation only. `WildPlantSpawner.cs:725-726`: desired plants at a cell =
  `plantDensity × plantDensityFactor × fertility`, times `GetBaseDesiredPlantsCountAt` (which reads fertility again),
  capped at 1. Saturation compares the map's plant count against the desired total (`:613-628`). No growth input.
- **Regrowth** uses the biome's `wildPlantRegrowDays` as a mean time between spawn attempts per cell (`:310-313`;
  default 25, `BiomeDef.cs:51`; caves 130). Not `growDays`, not `GrowthRate`.
- **Map generation** places plants with a random starting growth, 0.15–1.5 clamped to 1 (`GenStep_Plants.cs:14-19`,
  `WildPlantSpawner.cs:58,459`). That sets the *maturity mix* at gen, not the count.
- **No plant reproduction** in 1.6 outside blight (a search for `reproduceRate`/`PlantReproducer` finds only
  `Blight.TryReproduceNow`, `Plant.cs:1203`).
- **`plantDensity` 0 means no plants ever** (`:725`).

INFERRED consequence: **a `GrowthRate` multiplier cannot change how many plants a map holds**, in either direction.
Our ×0.25 dry rate will not empty a map: the spawner still fills it to density, with random growth at gen. What dry
growth changes is how fast a cleared or burnt patch looks green again (the new sprouts mature slowly), and how fast
crops ripen.

### 6.3 Where the two were linked in our history

| where | the link | file:line | cause | tag |
|---|---|---|---|---|
| `PLANT_GROWTH_SPEC.md` R-G4 | the regrowth lever (`wildPlantRegrowDays`) was to be divided by ~4 *"matching R-G2's default so the two levers agree"*: density refill tied to the growth band | `design/Jawa/worldbuilding/PLANT_GROWTH_SPEC.md:87-106` | 2026-08-15 spec; never built | MEASURED (text); unbuilt INFERRED from no patch found |
| `hydrology_and_fire_ecology.md` R-H3 | fast **growth** is cited as the reason the Pyrelands has standing fuel, which is a **density/refill** fact | `design/Jawa/worldbuilding/hydrology_and_fire_ecology.md:170-180` | 2026-08-15 | MEASURED (text) |
| Pyrelands | density raised to **16** (≈96% of plantable cells) and `wildPlantRegrowDays` 9 after *"Way too sparse"* (2026-09-18) and *"choked with grass. Barely any bare ground."* (2026-09-17) | `src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml:~115-134` | owner live reviews, quoted in the XML comments | MEASURED |
| Map Designer (`zylle.mapdesigner`, donor) | folds a density ratio into `wildPlantRegrowDays`, caps density at 1, and once wrote its startup density snapshot over the Grey floor copy (0 plants) | `Pyrelands.xml` comment; commit `32428ae6b1`; `RM_PyrelandsDensityEnforcer.cs` re-asserts density | 2026-09-18, 2026-10-06 | MEASURED (comment, commit); the enforcer was not read |
| Sea biomes | `plantDensity` unset → 0 plants; fixed to 0.22 / 0.5 / 0.18 | `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_GreySea.xml:135-165`, `RM_TwilightSea.xml:78-94`, `RM_TheChill.xml:95-101` | `TERMINAL_SEAS_FLOOR_DRESSING_1`, 2026-09-26 | MEASURED |
| The fused engine | growth only; touches neither density nor regrowth | `RM_ExplosiveGrowthPatches.cs:56-98` | 2026-10-16 | MEASURED |
| Conversation | "empty map" and "slow growth" were discussed as one problem (his 16:21-era remark) | — | — | his words; no ledger event found for empty-map complaints (a ledger search for `plantdensity`, `empty map`, `no plants`, `barren`, `sparse plant` found one unrelated hit) |

So in code the two are **already separate**; the link lived in the specs (R-G4, R-H3) and in how problems were
diagnosed. Not found: any density raised "because growth was slow", or the ×0.4 band used to explain an empty map
(INFERRED from the comment and commit trail, not a full item sweep).

### 6.4 Proposal: decouple, and tune by shared classes

**Rule.** Density answers *"how many plants does this place have"*; growth answers *"how fast does one mature"*. No
document or roster may set one to compensate for the other. R-G4's *"so the two levers agree"* and R-H3's growth-as-fuel
wording are rewritten on that basis (Δ15).

**Two class axes, both data on the biome or plant, no per-biome numbers:**

1. **Density class**, on the BiomeDef (PROPOSED numbers):

   | class | `plantDensity` | `wildPlantRegrowDays` | today's biomes that fit (INFERRED from current values) |
   |---|---|---|---|
   | barren | 0.01 | 35 | Stillsand (0.008/35), Long Shade (0.05/35) |
   | sparse | 0.15 | 25 | Wasteland (0.12/15), Warscar (0.15/20), Flooded Canyon (0.12/30), The Chill (0.18), Grey Sea (0.22) |
   | normal | 0.4 | 20 | Weeping Stones, The Forge, Contagion, Leaning Scrub, Blue Desert, The Sump, Scald, Cauldron, Abyss, Twilight Sea |
   | dense | 0.9 | 15 | Greentide (0.99/16), Webwork, Fever Wood, Miasma (0.7/13), The Rot, Gelatinous Slime (1.1/6) |
   | choked | 16 | 9 | Pyrelands only (owner-reviewed; Map Designer caveat) |
   | none | 0 | — | Rust Cathedral, Nightside Ice, Chill Crater, seabeds |

   MEASURED current values per biome are in the census (plantDensity from the BiomeDefs; `wildPlantRegrowDays` absent
   on Blue Desert, the seas and Nightside Ice, so 25). Lantern Deeps (2 / 5) does not fit a class and needs a look.

2. **Growth class**, on the plant (§3.2): dry-adapted, wet-adapted, stunted, exempt, imported. The rate comes from the
   plant class and the cell's water state (§4.3), never from the biome.

Moving a biome to a class changes its numbers slightly (for example Wasteland regrow 15 → 25). Each move is a row for
his review, not a silent edit (ASSUMPTION A10). A biome that genuinely needs its own number (Pyrelands) keeps it as a
named exception with the owner quote beside it.

**C7. Should biome plant numbers come from a few shared classes?**
1. *(Recommended)* **Yes: five density classes; any biome outside them is a named exception with your quote.**
   *Trade: about ten biomes shift slightly and need a look.*
2. Classes for new biomes only; existing numbers stay. *Trade: two systems side by side.*
3. Keep per-biome numbers. *Trade: what you said you hoped to avoid.*
4. *(write your own)*

---

## 7. Delta list: today's build → the consensus model

Size: **S** under half a day; **M** half a day to two days; **L** more. All INFERRED estimates.

| # | change | where | size |
|---|---|---|---|
| Δ1 | Replace the two multiplying postfixes with one rate lookup by plant class × cell state (§4.3 table) | `src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthPatches.cs:58-98`; `AmbientBand` at `Kernel/RM_ExplosiveGrowthKernel.cs:133-140` | M |
| Δ2 | Plant classes (dry-adapted default, wet-adapted from the three jungles' `wildPlants`, stunted, exempt, imported) | `RM_ExplosiveGrowthRegistry.cs:199-208`; both rosters | M (data + his review) |
| Δ3 | Soak grid gains `wetSince` and `dryAt`; settled-wet and fresh-event tests | `Kernel/RM_ExplosiveGrowthKernel.cs:146,165-173` | M |
| Δ4 | Arm only on a fresh event, once per plant per event | `Kernel/RM_ExplosiveGrowthKernel.cs:251-260`; `RM_MapComponent_ExplosiveGrowth.cs:210-287` | S |
| Δ5 | New default top **Fruit** (drop fruit, live, reset to 60%); wood never drops; remove the arming sprout | `RM_TopResolver.cs:110-114`; `RM_MapComponent_ExplosiveGrowth.cs:277-287` | M |
| Δ6 | Burst as a per-event chance for dry-adapted plants | `RM_TopResolver.cs:125-143`; rosters | S |
| Δ7 | Rain allow-list source (map scalar + unroofed) | `RM_SoakSources.cs` `PulseWeather`; roster `<soakWeathers>` (`RM_ExplosiveGrowthRoster.xml:206`) | S |
| Δ8 | Permanent-water bitset + terrain postfix | new file in `ExplosiveGrowth/Source` | M |
| Δ9 | Vanilla 1.6 flood hook (`SetTempTerrain` for `ShallowFloodwater`) | new patch | S |
| Δ10 | Hose Outflow spill waters its cell (if W4 = 1) | `src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidSpill.cs` (another agent's mod; coordinate) | S |
| Δ11 | Settings page rewrite (§3.7) and defaults | `ExplosiveGrowthMod.cs:37-92,158-273` | M |
| Δ12 | Campaign roster: stalled list adds `RUT_`/`RM_Cauldron` (S0-7, agreed); band lists replaced by class lists | `src/RimUtinni/UtinniPatches/Defs/ExplosiveGrowth/RUT_ExplosiveGrowthRoster.xml:75,89` | S |
| Δ13 | Jackpot on harvest only; gamble from the first swell | `RM_ExplosiveGrowthPatches.cs:185-213` | S |
| Δ14 | Pyrelands fire loop per decision C5 (burnt cell = fresh event) | `src/RimMandrake/Pyrelands` fire hook + Δ3 | M |
| Δ15 | Docs: design doc §0 and §9 restated on the water rule; `PLANT_GROWTH_SPEC.md` R-G2's flat ×4 deleted and pointed here; item Owed rewritten | `design/Jawa/worldbuilding/explosive_plant_growth_design.md`, `PLANT_GROWTH_SPEC.md`, `infrastructure/state/items/EXPLOSIVE_PLANT_GROWTH_1.md` | S each |
| Δ16 | Terrain moisture class table (§5.3) + startup log of unclassified terrains | roster or `DefModExtension`; `RM_ExplosiveGrowthRegistry.cs` | M (data, ~150 defs) |
| Δ17 | Density classes on BiomeDefs (§6.4, if C7 = 1); rewrite R-G4 and R-H3 wording | each biome's BiomeDef; `PLANT_GROWTH_SPEC.md:87-106`; `hydrology_and_fire_ecology.md:170-180` | M (data + his review) |

**Overall: L** (about 6–10 builder days, INFERRED from the sizes: 9 M, 8 S). Nothing here is a rewrite: the
soak grid, sources, tell ladder, tops, settings framework and suite harness all stay.

---

## 8. Tests and S0 rows that change

Suite chains (MEASURED names, `src/RimMandrake/ExplosiveGrowth/validation.py`, 59 rows per kickoff §1.4):

| chain | change |
|---|---|
| `bands_x4_default` | replaced by `rate_dry`, `rate_watered`, `rate_settled` (same plant, three cell states: ratios 0.25 / 10 / 4) |
| `soak_x10_default`, `soak_multiplier_tuned` | assert **replace**, not multiply: watered/dry ratio = 40 for a dry-adapted plant |
| `churn_cycle`, `churn_off` | become `fruit_cycle`, `fruit_off`: the plant survives, drops fruit, no wood from a tree |
| `top_burst`, `top_tinder`, `top_slime`, `burst_hurts_pawns` | arm only on a fresh event; Burst under a forced chance of 1.0 for determinism |
| `soak_length` | add `settle_after_3_days` and `fresh_needs_dry_reset` |
| new | `rain_waters_unroofed`, `rain_skips_roofed_and_sheen`, `riverbank_is_settled`, `vanilla_flood_is_fresh` |
| `probe_jackpot_*`, `probe_gamble_*` | harvest-only jackpot; gamble from the first swell (X4) |
| `scope_native_only`, `suppression_*`, `top_rupture`, `top_flush`, `master_switch_off` | unchanged |

Kickoff S0 rows (`design/RimMandrake/biome_sprint_kickoff_2026-10-15.md:489-501`):
- **X1**: the startup line changes from "Everyday bands: M plant defs scaled" to the class counts (dry-adapted /
  wet-adapted / stunted / exempt / imported) and the source list.
- **X2 / S0-6** (≥ 90% TPS, ruled 15:53): the bar stands; the **worst case changes** to a map-wide water rain on a
  long-dry, dense map (W1 = 1), plus the canyon flood.
- **X3**: adds rain, natural-water adjacency, vanilla flood and the settle transition; its "×10 wet-ambient band"
  clause becomes "wet-adapted plants ×10 at home, never stacked".
- **X4**: unchanged in intent; the gamble threshold moves.
- **X5**: unchanged.
- **S0-7** "tune bands and soak together at the S2 walk": becomes "tune the five rates and three timers at the S2
  walk".

---

## 9. Owner decision lines for the growth model (card-ready)

**C1. The three wet jungles: what does "reduced growth factor in permanently wet areas" mean for them?**
1. *(Recommended)* **Their own plants keep ×10 always (your 2026-09-21 number); "reduced" means no stacking and no
   bursting there.** Player-made wet ground elsewhere settles to ×4. *Trade: jungles stay the fastest places.*
2. Everything permanently wet, jungles included, runs one reduced number (×4). *Trade: drops your 09-21 "x10 instead
   of x4" for the jungles.*
3. *(write your own)*

**C2. At peak maturity on fresh water, what does an ordinary plant do?**
1. *(Recommended)* **Fruits and lives**: drops its fruit, shrinks back, grows on. *Trade: no new plants appear; the
   "endless churn" of 09-21 ends.*
2. Fruits, dies, and sows 2–4 sprouts (the 09-21 Churn, but only once per watering). *Trade: maps fill near water;
   trees must be excluded.*
3. Fruits and lives, and sows 1 sprout. *Trade: a slow spread along water.*
4. *(write your own)*

**C3. Where does bursting still belong?**
1. *(Recommended)* **Dry-adapted plants only, on a fresh watering, about 1 in 7 (15%).** Floods and rains still pop
   some plants; settled ground never does. *Trade: rarer than today.*
2. Every dry-adapted plant bursts on every fresh watering (ruling 4 taken literally). *Trade: every flood is a
   minefield; fruit only for wet-adapted plants.*
3. Only during floods and events, never from player water. *Trade: irrigation cannot trigger it (ruling 7's trigger
   verb narrows).*
4. Cut bursting. *Trade: drops what you called fascinating.*
5. *(write your own)*

**C4. Player crops and vanilla plants in our biomes: same water rule?**
1. *(Recommended)* **Yes: a crop on dry ground barely grows, watered ×10, settled ×4.** Farming a desert needs water.
   *Trade: a non-campaign player's first desert colony starves without irrigation; a first-colony letter is needed.*
2. Crops run vanilla speed dry, ×4 watered. *Trade: water helps but is not required.*
3. Crops and vanilla plants are left at vanilla speed. *Trade: the water rule only touches alien flora.*
4. *(write your own)*

**C5. The Pyrelands burn forever on fast regrowth (R-H3). Under the water rule its grass would barely grow. What
refuels it?**
1. *(Recommended)* **A burnt cell counts as a fresh event for fire-adapted plants**: ash flush, ×10 for 3 days.
   *Trade: one more source; fits "fire ecology".*
2. Pyrelands plants are a class of their own at a fixed ×4. *Trade: a biome exception by another name.*
3. The black rain counts as water there. *Trade: ties the fire loop to a weather that falls 3 of 88 weight.*
4. *(write your own)*

**C6. How slow is "barely grow at all"?**
1. ×0.1: dry ground is frozen in time (grass ~45 days).
2. *(Recommended)* **×0.25**: visibly static over a season (grass ~18 days).
3. ×0.5: slow but alive (grass ~9 days).
4. Keep a "classic ×4" preset in Mod Settings for players who want today's feel.
5. *(write your own)*

---

## 10. Assumptions register

| id | assumption | why it matters | how to check |
|---|---|---|---|
| A1 | All alien flora is dry-adapted unless named; "generally" in S1 allows exceptions | sets the default class for ~all our plants | his review of the class list (Δ2) |
| A2 | "x10 speed" is vanilla-relative and not on top of another multiplier | the stack (D3/D4) is removed on this reading | his words *"they grow x10 speed"* carry no base |
| A3 | "Reduced growth factor in permanently wet areas" names ruling 6 (×10 jungles, no bursting) reduced relative to the stack, or a lower number for settled ground | C1 | ask |
| A4 | `RM_ContagionBloom` rain is not plain water; `RUT_BoilingRain`/`RM_BoilingRain` and `RSW_SW_RedFoggyRain` are water | the rain allow-list | the weathers' own sheets |
| A5 | The 2026-09-10 "No brake" pump ruling is about water→food conversion, which the model keeps (watered fields grow ×10, then ×4) | Δ4 removes endless re-arming | deep dive G4 reasoning |
| A6 | With the campaign, vanilla biomes follow the same rule (dry = ×0.25 for dry-adapted only; vanilla plants per C4) | campaign deserts stall too | C4 answer |
| A7 | Plants grow 55% of the day (deep dive §1, Plant.cs:281) | every calendar-day figure here | MEASURED in source |
| A8 | Sizes in §7 are builder estimates, not measurements | planning | — |
| A9 | Today's suite has 59 rows (kickoff §1.4); the per-chain mapping in §8 is by chain name, not by reading each row | test delta | read each chain at build time |
| A10 | Moving a biome into a density class is a review row, not a silent edit | §6.4 | his review |
| A11 | Workshop mods outside `biomes_sprint` add no moisture-relevant terrain to our biomes | §5 inventory | our BiomeDefs name only the §5.3 terrains (MEASURED); terrain added at runtime by other mods is unchecked |
| A12 | Ocean water on Ash'karr is salt (never waters) | §5.3 | `water_taxonomy.csv` rows `sea_twilight` etc. (design §1) |
| A13 | Slime keeps watering (today's roster accepts the four slime fluids) | §5.3, T2 | his answer to T2 |
| A14 | Hot springs, boiling water and red water are undecided | §5.3, T2 | his answer to T2 |
| A15 | The W2 radius and settled-wet are computed from terrain only, not from FlowWorks fluid identity; a dug channel is read through the fluid list (§5.2) | detection | build-time check |
