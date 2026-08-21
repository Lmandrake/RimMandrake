## spec
🔴 **The design spec already exists — it is in `## notes` below, dated 2026-08-19, and it
is good.** This section RATIFIES it with four corrections measured 2026-08-21, one of which
would have destroyed seven BiomeDefs if built as written.

### ⛔ CORRECTION 1 — the 🪤 line in the notes is backwards, and it is the dangerous one

The notes say: *"`weatherCommonalities` is a LIST of
`<li><weather>X</weather><commonality>N</commonality></li>`. NOT the dictionary shorthand."*

**Both halves are wrong.**
- ⛔ **There is no field called `weatherCommonalities`.** The field is
  **`baseWeatherCommonalities`**, and a grep of every vanilla `BiomeDef` returns zero hits
  for the shorter name.
- ⛔ **It IS dictionary-keyed**, and the `<li>` form is exactly the mistake this project
  already made and documented at length in
  `src/Jawa/Jawa_Patches/Patches/SWDesertWeather_Attach.xml` — it produced
  *"No Verse.WeatherDef named li found"*, **discarded seven whole BiomeDefs** including
  three Core ones, and orphaned ~950 animal cross-references on a desert-planet campaign.

✅ **The correct shape, and our own shipped patch is the reference:**
```xml
<baseWeatherCommonalities>
  <SW_RedFoggyRain>5</SW_RedFoggyRain>
</baseWeatherCommonalities>
```

### ⭐ CORRECTION 2 — half the violent-weather work is already shipped

The notes propose authoring the exception onto `SW_RedFoggyRain` and `AB_VolcanicAshRain`.
**`SW_RedFoggyRain` is ours and already exists** —
`src/Jawa/Jawa_Patches/Defs/WeatherDefs/SWDesertWeather.xml:186`, `rainRate 1`, label
*"red foggy rain"* — and it is **already attached**, to `Volcano` at commonality 5
(`SWDesertWeather_Attach.xml:159`).

⇒ **What is actually missing is one curve.** Its `commonalityRainfallFactor` is
`(0,0) (1300,1)` — the *same* curve as vanilla `Rain`, so it is not altitude-locked at
all. Steepening it to `(0,0) (800,0) (1200,1)` is what makes it *"physically incapable of
occurring anywhere except the high country"*, which is the notes' own idea and the best
thing in them.

### 🔴 CORRECTION 3 — the ban is NOT mostly ratification. 433 wet tiles are not mountains.

Re-measured over all 21,872 rows, 2026-08-21:

| band | tiles | where they are |
|---|---|---|
| ≤ 49 mm | 17,588 (80.4%) | ✅ already effectively rainless |
| 600–1299 mm | 254 | rain at 46–100% strength |
| **≥ 1300 mm** | **683 (3.1%)** | 🔴 **full vanilla rain**, max 1668 mm |

Of the **937** tiles at ≥600 mm, only **504** are `hilliness` 4–5. **433 are not
mountains**, and their median elevation is **696 m**.

⇒ 🔴 **The 1668 mm stamp lands on biomes that contradict it.** 596 tiles carry exactly
that value; only 271 are `AB_FeraliskInfestedJungle`. The other **325** are
`ZBiome_Badlands` 78 · `ExtremeDesert` 52 · `ZBiome_DesertOasis` 52 · `ZBiome_Grasslands`
36 · **`AB_PyroclasticConflagration` 31** · `Desert` 28 · **`Volcano` 23**. **235 of them
are in The Dune Sea.** A volcano and a sand sea at tropical-rainforest rainfall fail the
owner's own first test — *does it read as a photograph of a real planet.*

### ⚠️ CORRECTION 4 — the jungle count in the notes is wrong, and one runtime consumer was missed

- The notes say `AB_FeraliskInfestedJungle` is **1,561** tiles. Measured today: **534**.
- The notes' grep concluded rainfall's only runtime consumer is `WeatherDecider.cs:191`.
  ✅ **True, and re-verified** — nothing reads it for plant growth, fertility or yield, so
  there is no economy cost and no floor to agonise over. ⚠️ **But
  `WorldGenStep_Rivers.cs:131` does `flow[tileId] += tile.rainfall`.** That is worldgen, and
  our `river_flow` column is authored and stamped, so it does not bite — **do not "fix"
  river flow after zeroing rainfall.**
- ⭐ **One thing that could have broken the ban and does not:** `WeatherDecider.cs:185`
  multiplies a rain weather's commonality by **15** when `LargeFireDangerPresent`. At
  rainfall 0 the product is still 0, so the ban holds through fires. At the current 18 mm
  it does not — 18 mm is a 98.6% suppression, not a ban, and rises to ~2.3% of rolls during
  a large fire. **That is the argument for 0 over 18.**

### ⚠️ CORRECTION 5 — `AB_VolcanicAshRain` does not rain, and snow is in scope

Census of all 24 painted biomes and every `WeatherDef` they name, 2026-08-21:

- ⛔ **`AB_VolcanicAshRain` has NO `rainRate` node** (Alpha Biomes
  `Defs/WeatherDefs/Weathers.xml:92`) ⇒ `rainRate` 0. It is ash with rain *art*, not rain,
  it is unaffected by the rainfall curve, and it cannot carry the owner's *"torrential,
  boiling"* brief. **`SW_RedFoggyRain` is the only real candidate**, and it is ours to tune.
- 🔴 **Zeroing rainfall also bans SNOW, and that is wanted.** `SnowGentle` and `SnowHard`
  both carry `rainRate 1` and the curve `(0,0) (300,0.5) (1300,1)`, and **`Desert` and
  `AridShrubland` list them at commonality 4 — twice their `Rain`.** Snow on Tatooine is
  currently possible, rarely. `rain_mm = 0` removes it with no extra work.
- ✅ **No painted biome is left with nothing to do.** The one real risk of a global rain ban
  is a biome whose entire weather table is rain-gated. Checked all 24: the driest cases
  still hold a non-rain entry — `AB_RockyCrags` keeps `AB_ForsakenNight:20`,
  `PoisonForest` keeps `PoisonForestSpores:18`, `BMT_FungalForest` keeps
  `BMT_FungalCavern:100`, `AB_PropaneLakes` keeps `Clear:12`.
- ⚠️ **The wettest painted biomes are not deserts.** `AB_MycoticJungle` (1,939 tiles) lists
  `Rain:10 · RainyThunderstorm:10 · FoggyRain:10` and `AB_MiasmicMangrove` lists
  `Rain:10 · RainyThunderstorm:5`. Both sit at 18 mm today, so they are already dry — ⭐ **which
  is the proof that the rainfall column, not the biome table, is the lever.**

### ⇒ THE RULING

1. ✅ **`rain_mm = 0`** on every tile with `hilliness` < 4. Zero exactly — `(0,0)` is the
   first point of every rain curve in the game, so 0 makes the multiplier **exactly** zero
   and rain becomes unselectable rather than rare.
2. ✅ **Keep the authored rainfall on `hilliness` 4 and 5.** The per-tile rainfall IS the
   per-tile gate; no mutators, no worldgen.
3. ✅ **Steepen `SW_RedFoggyRain`'s `commonalityRainfallFactor`** to `(0,0) (800,0)
   (1200,1)` and attach it, dictionary-keyed, to the biomes that occupy the high country.
4. 🔴 **The 433 non-mountain wet tiles are the owner's call, not mine** — see
   `## needs the owner` below.

## verify
- `awk`-level check on `world/ASHKARR_WORLDMAP_tiles.csv`: **zero** rows with
  `hilliness < 4` and `rain_mm > 0`
- every remaining `rain_mm > 0` row has `hilliness` 4 or 5
- `SW_RedFoggyRain`'s curve reads `(0,0) (800,0) (1200,1)`
- `validate_patch.py` clean on `SWDesertWeather_Attach.xml`, and ⛔ **every weather entry it
  adds is dictionary-keyed** — a single `<li>` in a `baseWeatherCommonalities` block fails
  this item outright

## criteria
On a lowland map, rain never occurs — not rarely, never, including during a large fire.
On a mountain map, what falls is red and violent.

## needs the owner
🔴 **Ruling 1 dries 433 tiles that are currently wet and are not mountains, and the map has
already been ACCEPTED for v1.** 235 of them are in The Dune Sea. I am not repainting an
accepted map on my own authority.

**The choice is narrow:**
- **(a) Apply the rule as ruled** — the Dune Sea, the volcano and the badlands go dry, and
  the wet retreats to the 504 mountain tiles. Most faithful to *"ban rainfall"* and to
  realism.
- **(b) Apply it everywhere EXCEPT `AB_FeraliskInfestedJungle`** — the river jungles keep
  1668 mm. ⚠️ Costs nothing visually and contradicts nothing: the notes already argue the
  jungles are fed by rivers, not sky, so they do not NEED the rainfall — but leaving it
  means jungle tiles still rain.
- **(c) Ratify what is there** — accept that 3.1% of the planet has tropical rainfall,
  including a volcano.

**DECIDE recommends (a).** The rainfall column is invisible on the world map, so drying it
changes no picture the owner accepted — it changes only whether water falls out of the sky
on a sand sea.

## notes
**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

⭐ **v1 — OWNER RULING 2026-08-19.** *"Ban rainfall: v1 (but might still happen
on highly mountainous terrain!)"* ⇒ The ban is v1 content and the mountain
exception is CONFIRMED as part of it, not a maybe.
⚠️ **The `D-V2-` in this item's name is now wrong and is kept anyway** — POLICY
forbids retitling an item, because the board counts items by name out of git.
Read the state line, not the name.
**What v1 owes, and it is small because the route changed:**
(a) **The ban is one authored column.** Rainfall is set per tile in
    `world/ASHKARR_WORLDMAP_tiles.csv` and stamped over the bridge. No mutators,
    no worldgen, no per-tile placement work. DECIDE picks the value.
(b) **The mountain exception is a predicate over two columns we already author**
    — `tileElevation` and `tileHilliness`. "Highly mountainous" is computable, so
    the wet band is drawn, not hand-placed.
(c) **The violent weather is ONE patch**, the same shape as the Pyrelands ash
    storm: `weatherCommonalities` on the biomes that occupy the high country,
    plus label/description work. `weatherCommonalities` is read at RUNTIME, so it
    needs nothing from worldgen and can land any time.
⛔ **Still out, and the line has not moved:** anything that makes the GENERATOR
produce this. The rule is authored into our tiles and our defs; it is not a
worldgen feature and must not become one.
🔑 **The one open question is the number, and it is an economy question, not a
biome one.** Biome eligibility no longer keys off rainfall for us — we assign
biomes directly — so the old worry ("which biomes survive at zero rainfall") is
void. What survives: plant growth and fertility read rainfall during PLAY, so a
hard 0 may starve the Jawa economy. DECIDE proposes a floor.

**owner:** 2026-08-16, verbatim: *"spec out banning rainfall on any biome except those
          that occur in high mountain areas where instead it is torrential, boiling, red,
          or otherwise violent and bizarre, otherwise we have to add mutators everywhere
          to enact this (v1 approach)."*

the idea:  On a Tatooine-grade desert world rain should essentially not exist. The
          exception is the high country, where what falls is not rain as anyone would
          recognise it — **torrential, boiling, red, violent, bizarre**. Rain becomes a
          rare, frightening, altitude-locked event rather than weather.

why v1's shape is wrong:
          v1 can only express this by hanging a mutator on every tile that should be dry,
          and another on every tile that should be violent. That is thousands of
          placements to say one planetary rule, and it breaks the moment the world is
          regenerated. **The rule belongs in worldgen and in the biome/weather defs, not
          in per-tile decoration.**

what we already know, so the spec starts from fact not guesswork:
          · ⛔ ~~Rainfall is a per-tile array in the save… already writable offline —
            `worldmap.py`, verified.~~ **DEAD 2026-08-19 — `worldmap.py` refuses to write
            and the save-writers are deleted.** ⭐ **REPLACED BY SOMETHING STRONGER:
            rainfall is AUTHORED PER TILE in `world/ASHKARR_WORLDMAP_tiles.csv` and
            stamped into the live world over the bridge.** Land on a test world spanned
            233–2584 mm.
          🔴 **⇒ THIS ITEM'S REASON FOR BEING v2 IS GONE.** It was parked because *"v1 can
            only express this by hanging a mutator on every tile that should be dry"* —
            thousands of placements to say one planetary rule. **We now set all 21,872
            tiles' rainfall by hand, in one column of a CSV.** The dry half of this spec
            is a v1 authoring decision costing one edit. Only the violent-mountain-rain
            half needs building, and that is a `weatherCommonalities` patch of exactly the
            shape already specced for the Pyrelands ash storm. ⚠️ Question 4 below ("which
            biomes survive at zero rainfall") is **also void** — biome eligibility is not
            computed any more; we assign biomes directly. What survives of question 4 is
            the real one: **plant growth and fertility read rainfall during PLAY**, so the
            Jawa economy is the constraint, not biome legality. ⇒ DECIDE owes the owner a
            v1/v2 call on this rather than leaving it parked on a dead premise.
          · **Biome selection keys off rainfall.** Zeroing it does not just change a
            number; it changes which biomes are eligible, which is the real lever and
            also the real risk.
          · Altitude is available too: `tileElevation` (raw − 8192 → metres) and
            `tileHilliness`. "High mountain" is therefore a computable predicate, not a
            hand-drawn region.
          · The tidally-locked planet mod rewrites **temperature** but leaves rainfall
            alone — so rainfall is ours to define with no conflict.
          · `VEE_FertileRains` already occurs **124 times**; whatever we do must
            out-rank or remove that.

the spec should answer:
          1. Does "ban" mean rainfall 0, or a low non-zero floor? 0 may make some biomes
             ungenerable and could break plant life the campaign needs.
          2. Are the violent rains a **WeatherDef** (an event you live through), a
             **GameConditionDef**, a biome property, or a mutator confined to high tiles?
             Only the first three scale; the fourth is the v1 shape we are rejecting.
          3. What does "boiling" and "red" mean mechanically — damage, temperature spike,
             toxic buildup, terrain change? Flavour without mechanics will not survive
             contact with play.
          4. Which biomes survive at zero rainfall, and do we still get the plant cover
             the Jawa economy assumes?
          5. Does it read from orbit? A planet with one wet band in the mountains should
             be VISIBLE on the world map, or the rule is invisible to the player.

⛔ do not start:  this is a design spec, not a build. It also touches worldgen, which is
          OUT of every version by standing ruling — the write-up must stay on the design
          side of that line.

━━━ 📐 SPEC, DECIDE 2026-08-19. Measured, and it is smaller than anyone thought ━━━

🔴 **CORRECTION FIRST, because I told the owner otherwise and he would have decided on it.**
I said *"plant growth and fertility read rainfall during PLAY, so the Jawa economy is the
constraint."* **That is FALSE.** Grepped the full 1.6 decompile: the ONLY runtime consumer
of `Tile.rainfall` is `WeatherDecider.cs:191` —
`num *= weather.commonalityRainfallFactor.Evaluate(map.TileInfo.rainfall)` — plus
`WITab_Terrain` (a UI label) and the `BiomeWorker_*` scorers, which are worldgen-only and
which we overwrite anyway. ⇒ **Tile rainfall does not touch plant growth, fertility, crop
yield or food at all. It only weights which WEATHERS can be selected.** There is no economy
question and no floor to agonise over. Zeroing it costs nothing.

⭐ **AND THE BAN IS ALREADY MOSTLY AUTHORED.** Measured over all 21,872 rows of
`world/ASHKARR_WORLDMAP_tiles.csv`:
```
rain    0-50   : 17588   80.4%      elev_m   -30 .. 2266
rain   50-100  :  2589   11.8%      rain_mm   18 .. 1668, mean 96
rain  100-200  :   396    1.8%      Mountainous+Impassable: 1459 tiles (6.7%)
rain  200-400  :   244    1.1%        their rain: 18-1668, mean 571
rain  400-800  :   224    1.0%      tiles >=400mm: 1055, of which 555 are
rain  800-2000 :   831    3.8%        Mountainous or Impassable
```
The map is already a rainless desert whose wet is already concentrated high. The ruling is
mostly a **ratification plus a tightening**, not new work.

**THE MECHANISM — the shipped curve does the whole job.** Every vanilla rain weather's
`commonalityRainfallFactor` starts at **`(0, 0)`** and ramps to `(1300, 1)`. ⇒ **at tile
rainfall 0 a rain weather's commonality is multiplied by ZERO and it can never be
selected.** The ban is not a suppression hack; it is the field's designed behaviour.

**(a) THE BAN.** In the authored CSV set `rain_mm = 0` on every tile whose `hilliness` is
below 4. ⛔ Not 18, not "low" — **0**, because 0 is what makes the multiplier exactly zero.

**(b) THE EXCEPTION, and the discriminator is elegant.** Keep the authored rainfall on
`hilliness` 4 (`Mountainous`) and 5 (`Impassable`) — 1,459 tiles, 6.7% of the planet,
mean 571 mm. ⭐ **The per-tile rainfall IS the per-tile gate**, which solves the problem a
`weatherCommonalities` patch cannot: those biomes also exist at low elevation, and a
BiomeDef patch is per-biome, but `commonalityRainfallFactor` is evaluated **per tile**. So
author the violent weather with a curve like `(0,0) (800,0) (1200,1)` and it becomes
**physically incapable of occurring anywhere except the high country** — no mutators, no
per-tile placement, no new system.

**(c) THE VIOLENT WEATHER — do not author one.** Same lesson as the sandstorm: it is
already installed. Of 73 live `WeatherDef`s the two that match the owner's words
(*"torrential, boiling, red, or otherwise violent and bizarre"*) are **`SW_RedFoggyRain`**
("red foggy rain") and **`AB_VolcanicAshRain`** ("volcanic ash with rain"). Add them to the
`weatherCommonalities` of the biomes that appear in the high country — measured as
`ExtremeDesert` 320 · `AB_FeraliskInfestedJungle` 240 · `AB_RockyCrags` 171 · `Desert` 151
· `ZBiome_Badlands` 123 · `AB_PropaneLakes` 86 — and let the rainfall curve confine them.
🪤 `weatherCommonalities` is a LIST of `<li><weather>X</weather><commonality>N</commonality></li>`.
NOT the dictionary shorthand that killed `biomeConfigs`.

⭐ **A CONSEQUENCE WORTH KEEPING, not a problem to fix:** the river jungles
(`AB_FeraliskInfestedJungle`, 1,561 tiles) will be lowland tiles at rainfall 0 — **jungle
where it never rains.** That is not a defect, it is the setting stating itself: on Ash'karr
the water comes from the rivers and the seas, never from the sky. The owner's own brief was
*"coat the rivers in jungles"*. Leave it.

⛔ **Still out, unchanged:** anything that makes the GENERATOR produce this. The rule is
authored into our tiles and our defs. It is not a worldgen feature and must not become one.
