# Explosive growth: a deep dive (2026-10-16)

Item: `EXPLOSIVE_GROWTH_RETHINK_SERIOUS_CONCERNS`. Owner, 2026-10-16 15:53: *"I have SERIOUS concerns about
explosive growth, so we need a deep dive on precisely what it's configured to do currently, what the original design
was, and where to take it."*

Read-only analysis of HEAD after the fusion commits `b9a689a8ab` and `1c9e7d4bbf`. Every number below comes from the
code or defs and has a `file:line`. Paths are relative to the repo root (`D:\Luke\dev\RimMandrake`). Where a number
is an estimate worked out from those values, it says **ESTIMATE**. Nothing here was measured in a running game.

Two vanilla facts the estimates rest on, read from the 1.6 source (`RimWorld/Plant.cs`):
- A plant grows `1 / (60000 × growDays) × GrowthRate` per tick (Plant.cs:346). The growth is added in one lump
  every 2000 ticks (about 48 in-game minutes) (Plant.cs:822).
- Plants **rest at night**: they grow only between 25% and 80% of the day (Plant.cs:281). That is about 13 of the
  24 hours, so a plant with "3 grow-days" needs about 5.5 calendar days at 100% conditions.

---

## 1. What it does today, precisely

### 1.1 What it is and where it lives

One engine, the `ExplosiveGrowth` member of **Baroque Biomes** (`mandrake.rm.biomes`). Its Mod Settings page is
called "Plant Growth (everyday and explosive)" (`src/RimMandrake/ExplosiveGrowth/Source/ExplosiveGrowthMod.cs:351`).
It has two tiers that **multiply each other**:

| tier | what it is | default numbers |
|---|---|---|
| **Everyday bands** (the former Jawa Plant Growth) | A constant speed-up on every plant's growth rate. Exactly one band applies per plant. | wild plants and crops **×4**, trees **×2.5**, wet jungles **×10** (trees ×6.25), "stalled" biomes **×0.4** (`ExplosiveGrowthMod.cs:37-41`) |
| **The soak** ("explosive growth") | A per-cell "wet" timer. A plant on a soaked cell grows faster again, then swells, then reaches a **top** (its final event). | **×10** on top of the band (`ExplosiveGrowthMod.cs:51`) |

The two growth-rate patches are separate postfixes on vanilla `Plant.GrowthRate`. Both multiply
(`src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthPatches.cs:70` and `:97`). A soaked plant therefore grows
at band × soak:

| where the plant stands | not soaked | soaked |
|---|---|---|
| ordinary Baroque biome, wild plant or crop | ×4 | **×40** |
| ordinary Baroque biome, tree | ×2.5 | **×25** |
| Greentide / Miasma / Fever Wood, plant | ×10 | **×100** |
| Greentide / Miasma / Fever Wood, tree | ×6.25 | **×62.5** |
| a "stalled" (terminator) biome | ×0.4 | ×4 (if soak is allowed there) |
| out of scope (vanilla or other-mod biome, default settings) | ×1 | ×1 (nothing soaks) |

All of these are multipliers on vanilla's own growth rate, so fertility, light, temperature and season still apply.
A frozen or out-of-season plant (`GrowthRate` 0) gets nothing from either tier.

### 1.2 Scope: which maps and which plants

- **Maps.** Both tiers run only on maps whose biome is shipped by Baroque Biomes
  (`src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthRegistry.cs:62-64`, home biomes collected at `:161-165`).
  That is 34 BiomeDefs today (MEASURED by XML parse of the member folders), among them deserts (Stillsand, Long Shade, Wasteland, Blue Desert), the Pyrelands,
  the Cauldron, the seas and the seabed floors.
- **Other biomes.** An option, **off** by default and labelled UNSUPPORTED, extends both tiers to every biome
  (`ExplosiveGrowthMod.cs:62`, `:220-223`).
- **The campaign.** The Utinni roster sets `scopeAllBiomes` (`src/RimUtinni/UtinniPatches/Defs/ExplosiveGrowth/RUT_ExplosiveGrowthRoster.xml:29`).
  While `mandrake.rut.patches` is loaded, **every biome on the planet is in scope**, vanilla ones included, and the
  option does nothing.
- **Plants.** Every plant def is in, apart from these exceptions (`RM_ExplosiveGrowthRegistry.cs:199-208`):
  - anima, Gauranlen and ambrosia;
  - plants with `growDays` under 1;
  - the three Blue Desert plants, which are left out of the bands and the soak;
  - cave plants and fungi, which never soak but **do** get the band;
  - about 75 roster rows set to top `None`. These still get the band but never soak.
- **Stalled band and soak carve-outs.**
  - The RM roster names **no** stalled biome and **no** soak carve-out. Only the wet three are listed
    (`src/RimMandrake/ExplosiveGrowth/Defs/ExplosiveGrowth/RM_ExplosiveGrowthRoster.xml:212-216`).
  - The campaign roster has one stalled biome, `PoisonForest` (`RUT_ExplosiveGrowthRoster.xml:89`).
  - The campaign roster's no-soak list (`:75`) is the Poison Forest / Cauldron names plus `RUT_ExtremeDesert`.

### 1.3 What "soak" is, and every way a plant gets soaked

**Soak is a timer on a map cell, not on a plant.** It is stored in a sparse dictionary of cell → "wet until tick"
(`src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs:146`). A new soak extends an existing one
and never shortens it (`:165-173`). It is refused on suppressed ground. Any plant standing on a wet cell gets the ×10.

Every route that soaks a cell today:

| route | how | how long | default |
|---|---|---|---|
| **Canyon flood** (FloodedCanyon) | every flooded cell, 40–400 cells (map area ÷ 20) (`src/RimMandrake/FloodedCanyon/Source/Kernel/RM_FloodKernel.cs:166`) | flood length + 4 days: **6 h + 4 days** (`RM_FloodKernel.cs:163`, `src/RimMandrake/FloodedCanyon/Source/RM_FloodedCanyonMod.cs:41,55`) | on |
| **Player irrigation** (FlowWorks) | a **dug** channel cell holding fresh water or a slime fluid soaks itself and its 8 neighbours. Rivers and lakes never soak. The map is swept 1/8 per 250 ticks (`src/RimMandrake/ExplosiveGrowth/Source/RM_SoakSources.cs:98-112`) | 1 day after each re-read (`RM_SoakSources.cs:40`). Re-read every 2000 ticks, so **permanent while the channel holds water** | on |
| **Soak Zone marker** (FloodedCanyon map control, built today) | a square around the marker, so many hours per day (`src/RimMandrake/FloodedCanyon/Source/MapControls/Building_RM_SoakZone.cs:83`) | set on the marker; 24 h/day by default | on (placed by the player) |
| **Miasma salt-line surge** (Environmental Hazards) | while a surge shift runs, cells with salinity 0.25–0.48 soak (`RM_SoakSources.cs:114-132`, band at `RM_ExplosiveGrowthKernel.cs:50-51,127`) | 1 day (`RM_SoakSources.cs:42`) | on |
| **Rain / weather** | only a weather named in a roster's `soakWeathers` | half a day (`RM_SoakSources.cs:43`) | **none named** (`RM_ExplosiveGrowthRoster.xml:206`), so **rain never soaks** |
| **Bloom event** `RUT_BloomBurst` (campaign only, quest-fired) | re-soaks every soaked cell, or a flood-shaped blob of 40–400 fertile cells, and sows bloomcrop on 60% of them | 24 h (`src/RimUtinni/UtinniPatches/Defs/ExplosiveGrowth/RUT_BloomBurst.xml`) | never fires on its own (base chance 0) |
| Greentide extract, red_water rain, scald melt | — | — | **not built** |

**The wet jungle band is not a soak.** It is the always-on ×10. A Greentide plant does not swell or reach a top
unless one of the routes above also wets its cell.

**Suppression** works the other way:
- Grazing animals suppress radius 1 for 3 days
  (`src/RimMandrake/EnvironmentalHazards/Source/RM_Patch_GrazingSuppressionHook.cs:31,61`).
- The dry-air blower also suppresses.
- Suppression wipes the soak, refuses a new one and blocks sprouts.

### 1.4 The charge, the swelling, the top

The map runs one pass every 250 ticks (`src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs:210-250`):

1. **Arming.** A plant on a soaked cell that is fully grown (growth ≥ 0.999) and growing (rate > 0) starts a charge
   (`RM_ExplosiveGrowthKernel.cs:251-260`). Its tops-off switch must be on, and its top must not be `None`.
   On arming, the ground darkens (water filth), and for Churn, Burst and Tinder plants **one extra sprout is sown
   next to it** (`RM_MapComponent_ExplosiveGrowth.cs:277-287`).
2. **Charging.** The charge goes 0 → 1 in **6 in-game hours** (`ExplosiveGrowthMod.cs:71`), ±10% per plant
   (`RM_MapComponent_ExplosiveGrowth.cs:273`). It moves only while wet and growing.
   - Wet but dormant: the charge holds.
   - Dry: it drains twice as fast, so 3 h back to nothing (`RM_ExplosiveGrowthKernel.cs:64-69`).
   - The charge uses `GrowthRate`, which ignores night, so **plants charge through the night** even though they
     only grow by day.
3. **What you see while it charges** (`RM_ExplosiveGrowthKernel.cs:42-46,84-98`):

   | charge | stage | how long in |
   |---|---|---|
   | ≥0.15 | starts swelling, up to **2× natural size** at full charge (`ExplosiveGrowthMod.cs:73`) | 0.9 h |
   | ≥0.45 | hue drifts toward bruised violet (red for contaminated plants) | 2.7 h |
   | ≥0.70 | trembles (±3.5% size flicker, dust puffs) | 4.2 h |
   | ≥0.85 | a creak sound plays | 5.1 h |
   | ≥0.95 | silence | 5.7 h |

   The plant is re-drawn every 250 ticks (`ExplosiveGrowthMod.cs:76`). Swelling is a step every 250 ticks, not
   a smooth animation.
4. **The top** at charge 1 (`src/RimMandrake/ExplosiveGrowth/Source/RM_TopResolver.cs`). "Produce" means
   `harvestYield × produceFactor` of the plant's `harvestedThingDef`. For vanilla trees that is **25 wood logs**
   (`Defs/Core/ThingDefs_Plants/Plants_Bases.xml:107-108`).
   - **Churn** (the default for every plant not listed):
     - drops its produce with no pawn labour (`RM_TopResolver.cs:110`);
     - dies, leaving a stump;
     - sows **2–4 copies of itself** at growth 5% within 1.9 cells, never on floors, buildings or indoors (`:114`).
   - **Burst** (dry-adapted plants):
     - drops 1.5× produce, scattered (`:125`), plus 3–6 hay (8–14 for Tinder);
     - deals 2–5 blunt damage and a short stun to pawns within 2.9 cells, but not to pawns already at ≤50% health;
     - sows 3–6 sprouts at growth 25–45% that **ignore zones and floors** (`:143`).
   - **Slime**: Churn-shaped, but 70% of the ring becomes slime ground.
   - **Rupture**:
     - releases a tox-gas cloud;
     - each of the two roster creatures has a 50% chance to spawn;
     - sows 2–4 sprouts;
     - for 1 h, pawns in the cloud without full vacuum resistance roll an **8% mutation chance every 250 ticks**
       (`ExplosiveGrowthMod.cs:92`).
   - **Flush** (Fever Wood giants): drops its produce and survives.
5. **Harvest jackpot.** While a plant has any charge, every yield it gives is multiplied by **(1 + charge)**, up to
   ×2 (`RM_ExplosiveGrowthPatches.cs:185-196`).
6. **Last-swing gamble.** Cutting or harvesting removes the charge. From charge 0.70, the swing has a 15% → 60%
   chance to set the top off instead (`RM_ExplosiveGrowthPatches.cs:205-213`).

### 1.5 How long until a plant visibly grows (ESTIMATE, ideal conditions)

Calendar time to full growth is `growDays ÷ (multiplier × 0.55)`, because plants only grow 55% of the day. Growth
lands in 48-minute lumps.

| plant (vanilla growDays) | vanilla | ×4 band | soaked ×40 | wet jungle soaked ×100 |
|---|---|---|---|---|
| grass (2.5) | 4.5 days | 1.1 days | ~2 daylight hours (2–3 lumps) | **one lump** |
| rice (3) | 5.5 days | 1.4 days | ~2.5 daylight hours | one lump |
| corn (11.3) | 20.5 days | 5.1 days | ~7 daylight hours | ~3 daylight hours |
| oak, tree (30) | 55 days (×1) / 22 days (×2.5) | — | ×25: ~2.2 days | ×62.5: ~0.9 days |

So on a soaked cell **a sprout shoots up within an afternoon**, in two or three visible jumps. It then swells for 6 h
and tops. A full Churn generation on a soaked cell (sprout → grown → charged → top → new sprouts) takes about
**8–9 h (ESTIMATE)**, so **2–3 generations per day**. Each generation sows 2–4 sprouts (plus one at arming) into
any empty, plantable cell nearby.

### 1.6 One plant, four kinds of map (defaults, Baroque Biomes without the campaign)

- **Wet jungle (Greentide).** A wild plant grows at ×10, always, so a 3-day plant is grown in about half a calendar
  day. Nothing swells unless a soak route reaches it, and inside the Greentide that means irrigation, a Soak Zone, or
  a flood. A soaked plant runs at ×100: a sprout is grown in a single 48-minute lump, then it charges 6 h and churns.
  Along an irrigation channel the strip becomes a permanent churn about 3 cells wide.
- **Stalled biome.** In the RM tier, **none exists**: no biome is on the stalled list, so the **Cauldron runs at ×4
  and soaks like anywhere else**. Only with the campaign roster does `PoisonForest` get ×0.4. Even then, `RM_Cauldron`
  and `RUT_Cauldron` are on the no-soak list but **not** the stalled list, so they still grow at ×4.
- **Desert with irrigation (Stillsand, Long Shade, Wasteland).**
  - Everywhere on the map: a ×4 band, the same as any other biome. Sand fertility still slows vanilla, but nothing
    in the engine treats a desert as dry.
  - Beside a dug, water-filled channel: ×40. Every grown plant on those cells arms, swells for 6 h, and churns.
  - A Burst plant (for example `RG_Plant_AridGrass`) instead **pops every ~8 h for as long as the channel holds
    water**, stunning pawns and sowing into floors.
- **Vanilla biome (temperate forest).** With defaults and no campaign: nothing at all, ×1, and no soak forms. With
  the campaign loaded: ×4 everywhere, and the same soak rules as above.

### 1.7 What happens to the map over 1 / 5 / 15 days (ESTIMATE)

The bands **do not add plants**. Wild plant density comes from vanilla's spawner, which reads the biome's
`plantDensity`, and R-G4, the regrowth lever, was never built. They make each plant reach maturity 4× (or 10×)
sooner. **Only the soak adds plants**, and only on soaked cells and their immediate ring.

| | after a canyon flood (≤400 cells, wet 4.25 days) | beside a player irrigation channel | the rest of the map |
|---|---|---|---|
| **Day 1** | every grown plant in the footprint arms at once and tops about 6 h later: a synchronised wave. Churn plants drop produce and sow 2–4 sprouts each. **Trees in the footprint fell themselves into 25 logs each.** Bare footprint cells start filling. | the 3-wide strip fills; its plants start cycling | crops ripen in about a quarter of the vanilla time |
| **Day 5** | about 10 generations have passed; the footprint is dense and constantly turning over; produce piles on the ground; the soak lapses about 6 h into day 5 and charges drain within 3 h | the strip has turned over 10–15 times; with a crop planted there, each cell drops roughly one harvest every 8–9 h without a pawn touching it | 4× growth, same density |
| **Day 15** | the footprint is left densely planted at the ambient band; nothing swells | unchanged, still cycling as long as there is water | same |

"Jungle choking the map" does **not** happen from the bands alone. Today's growth is a **local** problem: the
footprint and the strip. What does happen everywhere in scope is that every crop is ready ×4 sooner, and ×10 sooner in
the wet jungles.

### 1.8 Performance (UNMEASURED; reasoning from the code)

- **Every plant on the map**, once every 2000 ticks: two extra postfixes on `GrowthRate`. Together they cost one
  array read, three hash lookups and one dictionary lookup (`RM_ExplosiveGrowthPatches.cs:58-98`). Cheap.
- **Every 250 ticks:**
  - a pass over every soaked cell and every charging plant;
  - an irrigation sweep of 1/8 of the map;
  - a mesh rebuild request for **every soaked immature plant and every charging plant**
    (`RM_ExplosiveGrowthKernel.cs:253,312`).

  The rebuilds are the real cost: one map section is redrawn per touched section. A 400-cell flood touches roughly
  10–20 sections every 250 ticks.
- The perf gate the design required before any density promise (X2, bar "≥90% TPS", S0-6) **has not run**.

### 1.9 What the player sees and controls

**What happens without any action:**
- Crops ripen 4× faster (10× in the wet jungles).
- Wet ground darkens and sprouts.
- Plants visibly swell, turn violet, tremble and creak, then split, burst or rupture.
- Messages appear for a burst and a rupture, but not for a churn.

**Mod Settings** ("Plant Growth (everyday and explosive)", `ExplosiveGrowthMod.cs:158-273`), plus the engine's
toggle on the Baroque Biomes page:

| group | settings |
|---|---|
| Master | master switch |
| Everyday bands | on/off; sliders for wild/crop (1–8), tree (1–8), stalled (0.1–2), wet (1–20) and wet-tree (1–20); minimum grow-days |
| Soak | multiplier (1–30); on/off for irrigation, surge and weather; default soak length (2–96 h) |
| Scope | the unsupported other-biomes switch; minimum grow-days to soak; cave-plants switch |
| Charge | hours (1–24); max size (1–3×); redraw cadence; hue, sound and ground-tell switches |
| Tops | each top on/off; burst-hurts-pawns; rupture mutation chance |
| Player verbs | jackpot, gamble, suppression |

**What the page does not offer:**
- a cap on the combined multiplier;
- a "soak replaces the band" choice;
- any per-biome moisture setting;
- a limit on how often one cell can churn;
- any way to see what a biome is classed as, other than the counts line.

---

## 2. The original design

### 2.1 The planetary fact: PLANT_GROWTH_SPEC (2026-08-15)

`design/Jawa/worldbuilding/PLANT_GROWTH_SPEC.md`:
- *"every plant on this world grows at a rate that reads as obtrusive, aggressive, wrong."*
- R-G2 sets ×4 for wild plants and crops, ×2.5 for trees (*"wood stays a decision"*), and ×0.4 on the terminator.
- It adds *"on this world the limit on agriculture is WATER, not time."*
- R-G3 rules that the terminator exception *"must not be dropped."*
- It also says the fast growth is load-bearing for the Pyrelands' fire ecology (R-H3).
- R-G4 (wild regrowth, so a burnt map refills) was never built.

### 2.2 The explosive tier: `design/Jawa/worldbuilding/explosive_plant_growth_design.md`

**The owner's brief (§10b of the Cracked Lands sheet):**
- *"'OMG, what's going to happen?' should be the feeling near any water-soaked plant"*
- *"a great moment again and again."*

**What the design asked for:**
- **Soak is an event, not a rate.** It *"decays back to ambient as the ground dries (hours to a day)"* (§1).
- **Synchrony** is the great moment: *"every plant a flood soaked charges on the same clock, so a soaked landscape
  goes up like popcorn over an afternoon"* (§3).
- *"The player never fully owns the clock. Irrigation triggers it, but the big performances arrive on the water's
  schedule — flood, surge, storm"* (§6).
- The perf gate comes first: *"No sheet, item, or spec promises a soak density until this table exists"* (§5).

**The 2026-09-21 sitting** (§9). He opened it with: *"I fear that this entire capability has become distorted, and
I'd like to restore its original intention."* Eight rulings:
1. Broad growth, rare drama.
2. The Churn is the default (*"add sprouts next to it that keep going to keep the churn. And the fruit… Endless
   churn. That's good."*).
3. The Churn respects built ground; only the Burst violates it.
4. Water scarcity decides who bursts.
5. Contaminated plants rupture.
6. The wet biomes run ×10 ambient and never detonate: *"It's the same always-on, but stronger: x10 instead of x4
   growth here."* The design adds that it *"replaces soak-bursting in those biomes entirely — 'x10 is enough', because
   standing water there would otherwise fire a top over and over."*
7. All four player verbs are in, but trigger and weaponize stay *"VERY hard."*
8. *"A dry plant in the greentide can burst."*

**Earlier sittings:**
- 2026-09-20: *"It's less about the biome and more about the plants IN that biome having different behaviors."*
- 2026-09-10:
  - burst lethality capped at injury and knockdown;
  - the irrigation pump is *"working as intended… No brake, no diminishing returns"*;
  - the ambient register: *"All the jungle and river and miasma tiles should have the uncomfortable groaning swelling
    of ever shifting growth."*

**Carve-outs (§3, §8):**
- The terminator never soaks and stays stunted.
- The deep desert (`RUT_ExtremeDesert`) gets *"No fast growth"* (`deep_desert.md` §6, HARD BAN 4).
- Fungal biomes and saline shores never soak.

### 2.3 Today's rulings (2026-10-16, ledger `infrastructure/state/ledger/events/OWNER.jsonl`)

- 04:00: *"Please add the Explosive_plant_growth mod as part of the next sprint (three biomes + explosive)."*
- 04:07: *"Yes, Explosive Plant Growth should move into Baroque Biomes. It should only natively apply to plants
  within the Baroque Biomes, though option settings could allow it to apply to other plants from other mods or vanilla
  basegame (irrelevant in Utinni). Simpler."*
- 12:18: *"It seems absolutely (2) because those mods are fusing! They were never meant to be apart. **Especially
  because in dry places the plants won't be growing almost at all unless water is present, then they grow
  explosively.** So yes, always together, fuse them as a single mod right now and let's tune them all together."*
- 12:23: *"Yes, there should just be an option in Baroque Biomes to allow the accelerated plant growth and explosive
  growth to apply to other biomes, but we won't test or support that."*
- 12:49, by card: "Should the everyday 4x plant growth be on by default for players who install Baroque Biomes
  without the campaign?" → **"Yes, on for everyone"**.
- 14:59, by card: "ExplosiveGrowth X1-X5 → Approve". These are the sprint kickoff's lines in
  `design/RimMandrake/biome_sprint_kickoff_2026-10-15.md` §1.4.
  - S0-7 (Cauldron to the stalled band; keep the `RUT_ExtremeDesert` ×4 exemption; *tune bands and soak together at
    the S2 walk*) has no recorded answer in the ledger.
- 15:53: this item.

---

## 3. Gaps

**G1 — Dry places grow at ×4, not "almost at all".** His 12:18 sentence describes a **moisture model**: dry means
nearly no growth, water means explosive. The build has no notion of dry.
- Every Baroque biome that is not one of the three wet jungles gets ×4, Stillsand (plant density 0.008) and the
  Wasteland included (`AmbientBand`, `RM_ExplosiveGrowthKernel.cs:133-140`).
- The only below-vanilla band is "stalled". It has **zero members in the RM tier** and one (`PoisonForest`) in the
  campaign.
- The card at 12:49 approved "everyday ×4 on for everyone". That was answered before the moisture question was
  asked, and it is the exact number his sentence contradicts in dry biomes.

**G2 — Lost carve-outs.**
- R-G3 (the terminator stays stunted) is gone in the RM tier: the Cauldron runs ×4 and soaks.
- Deep-desert HARD BAN 4 (*"No fast growth"*) is broken in the campaign: `RUT_ExtremeDesert` is on the no-soak list
  but gets the ×4 band, and nothing exempts it. The item's own Owed #9 says this.

**G3 — The soak multiplies the band, so the wet jungles reach ×100.**
- Ruling 6 said the ×10 *replaces* soak-bursting there. The build stacks the soak on it: ×100 for plants, ×62.5 for
  trees.
- The item records this stacking as an invented reading (Owed #7).
- At ×100 a sprout is fully grown in one 48-minute growth step. The 6-hour charge is then the only brake on the
  churn.

**G4 — Irrigation makes a permanent churn engine, so the player owns the clock.**
- A dug water channel re-soaks its strip every 2000 ticks, forever.
- Every plant there cycles every ~8–9 h:
  - Crops harvest themselves: a full harvest dropped with no pawn labour, then reseeded.
  - Burst plants pop, stun and sow into floors about three times a day.
- This is *"standing water… fire a top over and over"*, the thing ruling 6 removed from the jungles, now available
  anywhere a player digs a channel. It inverts §6, *"the player never fully owns the clock."*
- The 2026-09-10 ruling (*"No brake"*) was about the **water→food conversion rate**. It predates the Churn (09-21),
  which added free produce and automatic reseeding.

**G5 — Trees fell themselves.**
- Every tree is a Churn plant unless a roster names it. Churn drops `harvestYield` of the `harvestedThingDef`, and for
  vanilla trees that is 25 logs (Plants_Bases.xml:107-108).
- So a flood over a forest turns the forest into log piles and oak sprouts in about 6 h. The giant-tree rows with
  `produceFactor` 2.5 drop about 62 logs.
- This contradicts R-G2's *"wood stays a decision"*, and Churn's own brief, which is "fruit", not lumber.

**G6 — The jackpot applies to any yield and is free below the tremble.**
- The ×(1 + charge) bonus applies to every yield from a charged plant, cutting included (X4 is approved but not
  built).
- The gamble only starts at charge 0.70, so a harvest at 0.69 takes **+69% with zero risk**. That makes "harvest
  just before the tremble" the dominant, safe play. The design wanted the jackpot window to carry the risk *"that it
  goes off in the harvester's face."*

**G7 — The swelling is stepped, and growth jumps.** Growth lands every 48 minutes, the swelling redraws every
250 ticks, and the smooth close-up layer was deferred. "Watch it grow" therefore reads as jumps, not motion. That is
acceptable for a time-lapse, but worth checking against the "OMG" brief in play.

**G8 — No perf number.** X2 and S0-6 (≥90% TPS) have not run. The design forbids promising soak density before
then, yet irrigation already allows unbounded soaked strips.

**G9 — Synchrony, the "great moment", needs a flood the player rarely sees.**
- The big performances are the canyon flood (one biome) and `RUT_BloomBurst`, which is quest-only and campaign-only.
- The everyday experience the player gets instead is the irrigation churn.
- So the build delivers the *least* designed part (an endless local churn) most often, and the *most* designed part
  (a valley going off in waves) rarely.

**G10 — The scope rule is two-faced.** "Baroque biomes only" holds without the campaign. With the campaign, every
vanilla and donor biome gets ×4 and the soak. That matches "irrelevant in Utinni", but it means the campaign's
deserts are fast too.

---

## 4. Where to take it

Four genuinely different directions. Each says what it keeps, what it changes, and which ruling it would move.

### A. Water is the only accelerant (his 12:18 sentence, made literal)

**The idea.** Delete the flat ×4. Each Baroque biome gets a **moisture class** as data:

| class | band | example biomes |
|---|---|---|
| dry | ×0.2–0.5 | Stillsand, Long Shade, Wasteland, Warscar, the Forge, the terminator, the deep desert |
| temperate | ×1–2 | |
| wet | ×10 | Greentide, Miasma, Fever Wood (and the Webwork?) |

The soak **replaces** the band with a single "watered" rate (for example ×20–40) instead of multiplying it. So a
watered desert plant goes from nearly nothing to explosive, which is exactly his line. A wet-jungle plant does not
jump to ×100.

**Gains.**
- It matches his words.
- It restores R-G3 and HARD BAN 4 for free: they become "dry".
- The water economy becomes real, because crops crawl unless watered.
- It removes the ×100 stack.

**Costs.**
- It reverses the 12:49 card (×4 for everyone) and R-G2's planetary ×4.
- The Pyrelands fire loop needs its own band, since it is not wet but needs fuel.
- It needs a moisture list for 34 biomes. That is data, not code: about a day of authoring plus his review.

### B. Keep the shape as built, add brakes

**The idea.** Keep ×4, ×10 and the ×10 soak, and add four limits:
1. A **cap on band × soak** (for example ×40 total), so the wet jungles stop at ×40, not ×100.
2. A **per-cell cool-down** after a top (for example 2–3 days before the cell can arm again). Irrigation then gives
   a cycle every few days, not three a day.
3. **Trees drop wood only through Flush or a harvest**, never through the Churn (fixes G5).
4. **The jackpot ramps with risk**: the gamble starts at the first swell, or the bonus only counts above the tremble
   (fixes G6).

**Gains.**
- Least change.
- Every ruling stands.
- It can all be done in Mod Settings and by a tuning pass at the S2 walk.

**Costs.**
- It does **not** answer "dry places won't be growing almost at all". Deserts stay ×4.
- It treats the symptoms, not the model.

### C. Local spectacle only: rare, scheduled soak events

**The idea.**
- Everyday growth stays modest (×2, or vanilla).
- The charge-and-top cycle only happens in **events**: flood, surge, bloom, storm, extract.
- Irrigation gives a steady "watered" boost (×4–10) with **no charge and no top**, so the field grows fast and safely.
- Events become more common and better signposted: a flood season, a bloom letter, the first-encounter alert from
  the 09-12 addendum.

**Gains.**
- It restores §6 (*"the water's schedule"*) and synchrony as the great moment.
- No endless churn farms.
- Perf is bounded per event.

**Costs.**
- It overturns ruling 7's TRIGGER verb (irrigation as a trigger) and narrows the 09-10 pump ruling.
- *"Intimidating anywhere water soaks a plant"* becomes "during events" only.
- It needs event authoring outside the Flooded Canyon.

### D. A and C combined: the moisture model plus event-only tops (the recommendation)

**The idea.**
- Use A's moisture classes for everyday growth: dry ≈ stalled, temperate ≈ ×1–2, wet ×10.
- Any water lifts a plant to a single "watered" rate that replaces the band, with no stacking. Irrigation, Soak Zone,
  flood, surge and rain all count.
- **The charge, the swelling and the top happen only when a cell receives a *pulse*** (a flood, a surge, a bloom, a
  storm, the extract, or a Soak Zone the player sets to pulse) **and then fire once per cell per pulse**.
- A permanently irrigated field grows explosively but does not detonate every 8 h. A flood still sets off the whole
  valley in waves.

**Why this one:**
- It is the only option that delivers all three of his lines together:
  - *"in dry places the plants won't be growing almost at all unless water is present, then they grow explosively"*
  - *"intimidating anywhere water soaks a plant"*, because watered plants visibly shoot up;
  - *"a great moment again and again"*, because pulses are events, and synchrony is kept.
- It closes G1–G5 and G9 by construction.
- It leaves the engine's soak grid, tops and tells as they are. The build change is:
  - one moisture list;
  - a "pulse" flag on the soak;
  - swapping the multiply for a replace.

**What he would be overturning:**
- the 12:49 "×4 for everyone" card, which becomes "×4 where it is not dry";
- R-G2's flat planetary ×4;
- the reading that steady irrigation is a trigger. The trigger verb survives through a pulsed Soak Zone, which is
  harder to set up, as ruling 7 asked.

### Question card draft

> **Explosive growth: what should water do?**
> Today every plant in our biomes grows 4× faster, deserts included (10× in the three jungles). Any wet cell makes
> plants grow another 10× and then split or burst about every 8 hours, forever, while the water stays. You said dry
> places should barely grow until water arrives.
>
> 1. **Water is the only accelerant.** Each biome is dry, temperate or wet. Dry barely grows, wet runs 10×, and any
>    water lifts a plant to one "watered" speed. Tops work as today. *Trade: drops the planet-wide 4× you approved
>    this morning; the Pyrelands needs its own number.*
> 2. **Keep today's numbers, add brakes.** Cap the combined speed, give each cell a few days' rest after a top, stop
>    trees churning into logs, make the harvest bonus risky. *Trade: smallest change, but deserts still grow 4×.*
> 3. **Spectacle only in events.** Modest everyday growth. Irrigation gives fast, safe growth. Swelling and bursting
>    happen only in floods, surges, blooms and storms. *Trade: irrigation is no longer a way to trigger bursts.*
> 4. **(Recommended) 1 + 3 together.** Dry, temperate or wet everyday growth. Any water makes plants grow
>    explosively. Swelling and bursting happen once per cell per water event, so a flood sets the valley off in waves
>    and a watered field grows fast without detonating all day. *Trade: replaces the 4× card and the "irrigation is a
>    trigger" reading.*
> 5. *(write your own)*

**Whichever he picks:**
- Fix G5 (trees churning into logs) and G6 (the risk-free jackpot). Both are defects under every option.
- Run the X2 perf gate before any density is promised.
