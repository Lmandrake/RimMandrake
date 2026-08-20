# worldgen_interactive_def.md — the working definition of the world we are painting

Live working doc for the hand-built, frozen planet. Bullets only. Decisions land here
as they are made; new-content ideas go to `worldgen_interactive_build_concepts.md`.

> ⛔ **SAVEGAME WRITING IS OUT — 2026-08-19.** Everything below dated 2026-08-16/17
> describes a pipeline that wrote a painted planet into a `.rws`. **That route is dead**:
> it produced a dead load twice (owner, 2026-08-18) and its nine scripts —
> `apply_world.py`, `paint_ashkarr.py`, `populate_ashkarr.py`, `clean_ashkarr_hydrology.py`,
> `name_ashkarr_regions.py`, `name_ashkarr_factions.py`, `strip_ashkarr_factions.py`,
> `ashkarr_write.py`, `swap_faction_def.py` — were **deleted 2026-08-19**.
> **The map reaches the game over the live bridge** (`ASHKARR_WORLD_DEFINITION.md` §12).
> 🔑 The DESIGN rulings in this file (geometry, the three worlds, the four axes, the named
> regions, the wind, the scale doctrine, the faction placement) are **unaffected and still
> canon**; the current painter is `src/RimMandrake/Utils/ashkarr_paint.py` and the current
> map is `world/ashkarr_tiles.csv`. **Read this file for its rulings and its measurements,
> never for a command to run.**

## The geometry — FIXED, measured off the save

- `WORLDMAP_gen.rws`, seed `lada`, **subdivisions 7, coverage 1.0, 21,872 tiles**.
- `alienWorldsFrameworkPlanetType: TidallyLocked` — confirmed in the save.
- **Substellar point = (lon 0, lat 0). Terminator = longitude ±90°, any latitude.**
  Day side is `|lon| < 90`, night side `|lon| > 90`. **Not a latitude world** — any rule
  phrased as "north is colder" is wrong here.
- Angular distance from substellar drives everything:
  `d = acos(cos(lon)·cos(lat))` in degrees. 0° scorching · **40–57° the liveable ring** ·
  90° terminator · 180° antistellar.
- As generated: land 75% / ocean 25%. Temperature **−105.7 … +67.9 °C**, median −38.
- Land by band: **61.5% dead cold** (<−25) · 13.6% harsh · 11.0% temperate · 7.0% warm ·
  5.0% hot · 1.7% lethal. Arid core (AridShrubland/Wasteland/Desert/ExtremeDesert) 30.9%.
- 19 biome types present. **Treat the biome roster as fixed and good**; we choose which to
  use and where, not what exists.

## The three worlds — ratified fiction

| | DAYSIDE | THE TERMINATOR | NIGHTSIDE |
|---|---|---|---|
| light | unmoving sun | perpetual twilight | perpetual night |
| heat | scorching toward centre | temperate | cold |
| water | none at centre, rare oases | **all of it** — seas, rivers | frozen or absent |
| who | Empire at dead centre · droid factions in low volcanic mountains with poison springs · Hutts at the oases · Tuskens + Trade Moot in the near-desert | Deepwater Compact on the seas · Wildsteam on rivers, jungle, poison marsh · Homestead on the arable margin | the Forsakens' leavings · terrible fauna · the Forgotten Arsenal |
| player | where the work is | where the water is | where you go when you cannot be found |

- 🔴 **Water follows the TERMINATOR, not the poles.** This supersedes the old latitude rule.
- **Hiding is a place, not a mechanic.** Imperial pursuit lapses on the nightside; the price
  is no sun, no crops, cold, fauna, and half a planet of distance. No timer needs authoring.
- `AB_RockyCrags` (hardcoded 0.34 sun-glow, never clear weather) **is** the nightside, and
  its own description — an ancient race part-terraformed this world and left — is the
  Forsaken back-story.

## The tile rule — every terrain fills four axes

Abundant (why you come) · Scarce (what it denies, creating the next need) · Exotic (the
located, covetable thing) · Threat (the timer that forces you out).
**No tile is self-sufficient.** Deep desert is the sea you cross; oases, volcanic fields,
rivers, coasts and anomaly patches are the islands of purpose.

## What we can and cannot change offline

- ✅ Repaint freely, proven encodings: biome, temperature, rainfall, elevation, hilliness,
  swampiness, feature. Settlement positions (faction territory follows for free), landmark
  position and type.
- ❌ Cannot: add or remove tiles · roads and rivers (graphs, untouched) · pollution
  (encoding unproven, the tool refuses to write it).
- ⚠️ A biome edit alone leaves the old climate behind. Set temperature and rainfall with it,
  with per-tile jitter, or it renders as a paint-bucket blob.

## Name — RATIFIED

**`Ash'karr the Sundered`.** Owner, 2026-08-16. Written into the save's `<world><info><name>`.

## Axis 1 — RULED, 2026-08-16

### Nightside — ~50% of land, and it is a DESTINATION

- **Almost precisely 50%** of land is nightside. Not a wasteland to pad the map.
- **It gets its own internal geography** — outer twilight fringe, deep dark, antistellar core.
  It is a campaign exploration path, certainly.
- ⭐ **It takes the place of space/asteroids in this playthrough**, because orbit is heavily
  Empire-held. That is its structural role.
- 🔑 **You CAN stay and farm it** — as a difficult **end-game** goal, once the ship is very
  heavily equipped with heaters, weapons and survival gear. It is gated by preparation,
  not forbidden.
- Imperial pursuit lapses there in v1. *(v2 concept: pursuit reaches the nightside but far
  slower — possibly as a radius from the central Imperial holdings. Parked in
  `worldgen_interactive_build_concepts.md`.)*

### Temperature — a precipitous cliff, not a gradient

- **Substellar point ≈ +80 °C** — deliberately beyond normal RimWorld ranges.
- **Still sweltering right up to the dayside edge of the terminator**, because hot winds
  circulate the extreme heat outward. The dayside does not cool off gently.
- 🔴 **The drop across the actual terminator is precipitous** — very hot to very cold over
  a short arc. This cliff is the signature of the planet and must survive the repaint.
- **Nightside bottoms out at −80 °C** at the antistellar point.
- Chemistry thresholds that matter for later content:
  **propane** liquid −188…−42 · **ammonia** liquid −78…−33 · **ethane** liquid −183…−87.
- The **antipodal (coldest) point** carries **solid ammonia ice and solid CO₂**.
- ✅ **All other atmospheric gases stay gaseous across the whole frozen range** — the
  nightside is **breathable**. No vac suits. Insulation only. This is a deliberate scope cut.

### Water — four distinct systems

1. **Two near-terminator seas**, one per twilight zone, spanning both sides and nurturing
   abundant life. ⚠️ **NOT the full circumference** — long stretches of the terminator carry
   no sea at all, though small lakes and oases are possible there.
2. **One significant DAYSIDE ocean**, and it is the surprise: **not at the substellar point
   but ~35° from it**, in a punishingly hot region. **Fed and maintained by the planet's
   largest mountain range and volcanoes and their river system** — that is why it survives
   where it has no business existing.
3. **Frozen seas on the nightside** — deadlocked as **mineral ice**, no longer part of the
   water cycle at all.
4. The nightside instead runs a **methane / propane / ammonia chemistry cycle**.

### Rainfall — almost nowhere

- **Rain falls ONLY at the tops of dayside mountains**, at high altitude, in violent forms,
  in the few strange biomes that live up there.
- **The dayside terrains never rain. Ever.**
- **The terminator gets no rain either** — moisture arrives as **fog that descends at night
  and lifts in the morning, leaving dew**.
- **The nightside: no rain and no water snow.** Temperature collapses too fast and the air
  is too dry.
- **But ammonia, propane and ethane may fall there as rain or snow.**

### 🔴 sub7 is THE save — and sub8 was disqualified by absence, not by taste

Measured by inverting Alien Worlds' temperature curve to arc distance, both saves:

| arc from substellar | sub7 (cov 1.0) | sub8 (cov 0.5) |
|---|---|---|
| substellar core <40° | 523 | 1,291 |
| liveable ring 40–57° | 2,477 (1,791 land) | 7,907 |
| terminator 80–100° | 3,549 (3,094 land) | 6,011 |
| deep dark 100–120° | **3,301** | **0** |
| antistellar core >120° | **6,136** | **0** |

**Coverage 0.5 amputates the far side.** sub8 holds nothing past ~100° arc — no deep dark,
no antistellar core, no chemistry lakes, no endgame frontier. ⇒ **coverage 1.0 is not a
preference on this planet, it is a requirement**, and the tile budget must come out of
subdivisions alone.

⭐ sub7 already lands on the 50% ruling unaided: everything past 90° is ~11,200 tiles, 51%.
The nightside proportion needs no repaint.

⚠️ Band edges are blurred — this inverts temperature, it does not read true lat/lon. Exact
positions need `jawa/world_tile_export`. The zero rows are not blurred.

### Asymmetry is ALLOWED — owner, 2026-08-16

> *"It's also ok to make that temperature alteration not be 100% symmetric around the
> terminator, we can have regions of differing temperature ranges because of invisible
> climatic variation beyond the game's view. Do as the story needs."*

- Temperature need **not** be a clean function of arc distance. Regional pockets, tongues
  and gulfs are legitimate, justified as circulation the player never sees.
- ⭐ It has a physical reason already in the fiction: the **hot winds that circulate heat
  outward** are a superrotating flow, so heat piles up on one flank. **One twilight band
  runs hotter than the other**, and that is principled rather than arbitrary.
- Licence this unlocks, to be spent deliberately rather than as noise: a **cold tongue**
  reaching sunward that lets travel go further in than it should; a **warm gulf** reaching
  into the nightside as the only early-plausible beachhead on the frontier; and the
  **dayside ocean's shore** being survivable at 35° arc despite the heat.

### The named regions — RATIFIED, 2026-08-16

| region | what it is | where |
|---|---|---|
| **the Nightspill** | the **cold tongue** — night spilling sunward. Lets travel push closer to the substellar core than the arc should allow | reaches inward across the terminator, dayside |
| **the Sunreach** | the **warm gulf** — sun reaching into the dark. The only early-plausible beachhead on the nightside frontier | reaches outward past 90°, nightside |
| **the Rust Cathedral** | the mechanoid-intrusion landscape. **Already ruled 2026-08-15** (`the_forgotten_war.md`): the one mega-structure, a map **made of** metal rather than containing it, defended viciously, acid lakes | ⭐ **the substellar centre** |

⭐ **The Rust Cathedral is WHY the substellar centre is flat and baked.** The ancient
Rakatans began their great terraforming works there — the machinery that was once making
this world come alive. **Irregular in outline but ONE SOLID MASS**, and it survives at
**higher elevation**, where the sand never buried it. That single placement ties the
Forsaken back-story, the mechanoid biome, the Empire's seat at the dead centre and the
planet's flattest, deadest ground into one object.

### Wind — atmospheric energy is a first-class feature here

- The temperature gradients on this planet are extreme, so **there is far more atmospheric
  energy than a normal world**. Wind is a consequence of the physics, not decoration.
- 🔴 **High winds on the EDGES of the Nightspill and the Sunreach**, where hot and cold
  masses meet, and **near tall mountains**.
- 🔴 **Air is almost totally dead** in two places: **the nightside**, and **the substellar
  centre**, where everything is so flat and so baked that nothing moves.
- ✅ **Both are paintable today.** Vanilla Core ships **`WindyMutator`**; high winds are that
  mutator, and dead air is simply its absence. No new content needed.
  ⚠️ Mutators live in `tileMutatorTilesDeflate` / `tileMutatorDefsDeflate` — arrays, so
  writable in principle, but `worldmap.py` does not implement them yet.

## Axis 2 — elevation and the spine. RULED, 2026-08-16

### The named waters

| name | what |
|---|---|
| **The Scald** | the dayside ocean at ~35° arc. ⭐ **A degraded ancient impact crater**, with its own crater-rim mountains |
| **the Twilight Sea** | one near-terminator body |
| **the Gray Sea** | the other |

### The two ranges, and what they are for

- The Scald's **crater mountains join a larger VOLCANIC range** that **cradles one half of
  the subsolar horrific desert**.
- 🔴 **The bulk of BOTH ranges lies between the deepest desert and the water.** That is the
  load-bearing geometry: the mountains stand between the furnace and the sea, which is why
  the sea survives and why its far side is a rain shadow.
- These peaks are the **only place it rains on the planet** — so the strange high-altitude
  biomes live here and nowhere else.

### The substellar plateau

- ⭐ **The whole subsolar region is a PLATEAU — flat AND high.** Extremely flat *within* the
  plateau, and raised above everything around it.
- Its surface is **part ExtremeDesert, part the mechanoid-intrusion remnant**.
- 🔑 **The read: the desert sands are trying to enter and cover the intrusion, and have
  partially succeeded.** The Rust Cathedral is being buried, slowly, and losing.
- ✅ Paintable exactly as described: **elevation and hilliness are separate arrays**, so
  "high but flat" is high `tileElevation` with `tileHilliness` at its floor.

### The nightside surface

- **Vast flat ice and rounded hills** — old, not geologically young, **no longer making
  mountains**.
- A surface that has survived **countless impact craters and orbital war**, then been carved
  by **strange flowing chemical processes** into **trenches, canyons and deltas cut deep,
  Grand-Canyon fashion**.

### 🔴 The governing idea: Ash'karr is an OLD world

| | DAYSIDE | NIGHTSIDE |
|---|---|---|
| building | **active volcanism, still raising ranges** | none. *(cryovolcanism is a v2 idea)* |
| erosion | sand, violent winds, mountain rain — wearing structures down and **burying much of the planet in thick sand** | very little wind; **very active liquid cycles, but not water** |
| net | contested: built and destroyed at once | **much smoother and worn down** |

⇒ Relief is not uniform noise. The lit half is young rock under a sand blanket; the dark half
is an ancient, softened, deeply incised surface. **The planet's history is legible in its
elevation**, which is the cheapest storytelling available to us.

### Engineering consequences to carry into the repaint

- Rainfall drives biome scoring and plant growth, so near-zero dayside rainfall is doing
  double duty — it must be set, not left at Normal's ~950 mm median.
- The terminator cliff is only a few tiles wide at 21,872 tiles. **Measure how many tiles
  span 80°→100° arc before designing anything that needs room there.**
- Fog/dew, ammonia precipitation, mineral-ice mining and the chemistry cycle have no vanilla
  representation. Parked as build concepts; the repaint must not depend on them.

## Scale doctrine — RULED, 2026-08-16

**Two scales, and a concept is allowed to live at either.** Owner: *"Some of these concepts
will live only as tile mutators and live in the tilemaps, others will be at a coarser scale
we can paint on the worldmap biomes themselves. That's ok with us."*

- **Worldmap scale** — biome, temperature, rainfall, elevation, hilliness: the coarse strokes.
- **Local-map scale** — tile mutators and map generation: canyons, trenches, chemical deltas,
  the sand creeping over the Rust Cathedral. These need no worldmap representation at all.

⇒ **A feature with no worldmap encoding is not a gap.** It is simply a local-scale feature,
and the repaint neither owes it anything nor waits for it.

## Axis 3 — who sits where. RULED, 2026-08-16

### The Galactic Empire — three settlements, each for a reason

1. ⭐ **The capital.** On the **edge of the crater sea (The Scald)**, at the edge of the deep
   desert but **shielded from it by the mountains**, **along a river**. Deliberately **the
   ideal spot on the planet** — every advantage any colony could want. That is *why* they
   are there, and it is the capital of the world now.
2. **Overlooking the Hutt holdings** — the **spice mines, salvage yards and sarlacc grounds**
   strung **along the river that feeds the Twilight Sea**.
3. **Overlooking the abandoned silicax oxalate mines** and their ruins, on the **far side of
   the deep desert**.
   🔑 **This is the Jawa origin story.** The company sank a century into those mines and
   finally pulled out when the rebellion came. **The Jawa CLANS swarmed over the holdings and
   took the SANDCRAWLERS** — the founding wealth that makes the Jawa a faction at all.
   ⚠️ **CORRECTED 2026-08-17: that is not where the player's ship comes from.** The player
   faction steals **the ship** from a **Hutt vehicle salvage yard**, much later. Two thefts,
   two places, two generations — do not merge them.
   ⭐ Also here: **the Geonosian Foundry Hive's first outpost**, the indentured workforce the
   same company bought and abandoned. Its queen would not leave. See `FACTION_SPEC.md`.

### The Deepwater Compact — all the water, but not all of it freely

- They hold **every body of water on the planet**.
- **The Scald is badly oppressed by the Empire** — theirs on paper, policed in practice.
- **The Twilight Sea is their stronghold**: curated, defended, protected.
- **The Gray Sea is dying and too saline to be worth much** ⇒ terrible, wild and lawless.

### The nightside — all three at once

Ruled true together: **uninhabited ruin and monster country**, **outcast holdouts sheltering
in the Sunreach**, and ⭐ **something old still awake out in the deep dark**.

### Settlement pattern — clusters and vast empty spans

- **Mostly tight clusters with enormous emptiness between**, but the clusters are **not only
  the seas**: also **the rivers**, and **the old industrial holdings**.
- Smaller mountain clusters that generate only enough for **a tiny lake, or just an oasis**.
- ⭐ **Emergent springs and oases with no explanation at all.** It is a living world.
- **Many of these alien races are far hardier than humanity and settle deeper** than a human
  colony could — the independent droids especially.

### Named: the Trade Socket

The **independent droids' primary trading outpost with the rest of the planet**.
**Unpoisoned** — unlike their volcanic-spring homes — and **sited on a road**.
They sell, **sparingly**: volcanic and mountain materials, fresh ore, the **water the
mountains produce**, and their own technological and repair understanding.

### Solar fields

**Vast solar collection fields near many of the large settlements**, powering super-dense
Star Wars industrial technology. ⭐ And **rusted, broken versions of the same fields** out at
the abandoned industrial mining areas — the same technology, a century apart.

### ⚠️ Roads are not editable

Roads are graphs, deliberately untouched by our tooling. **"Near a road" is a siting
constraint on us, not an edit** — the Trade Socket and anything else road-dependent must be
placed where the generator already put roads.

### The named centres — CANON, 2026-08-16

**The Fall Line** ⭐ — a dayside belt **downwind of the plateau**, where the superrotating
winds drag re-entering debris down. The orbital war never stopped falling.
*Abundant:* fresh wreckage, **renewably** — the one salvage source that does not deplete.
*Denies:* everything else. *Exotic:* intact orbital tech. *Threat:* it is still falling, and
the Empire claims salvage rights it cannot enforce.

**The Dew Belt** — a **broad, canyon-like region of LOW elevation** running from the
terminator near the **Twilight Sea**, abutting one flank of the **Nightspill**.
🔑 **Two cooling mechanisms stack here**: the cold intrusion, and the elevation drop. Together
they pull temperature down out of the blistering surrounds **and let the rich fog form far
farther sunward than it has any right to.**
Well settled by the **moisture farmers** — their crops, their animals. Little industry, metal
or defence, but **many trading settlements** supplying the remote farmers who fill their
territory.

**The Salt** — the Gray Sea's retreating shore and its evaporite flats.
*Abundant:* salts and chemicals. *Denies:* food, water, law. *Exotic:* rare evaporite
reagents. *Threat:* lawlessness, and a coastline that walks away from your buildings.

**The Gusting** — the high-wind margins where hot and cold masses collide, on the flanks of
the **Nightspill** and the **Sunreach**.
*Abundant:* wind power, absurd amounts. *Denies:* structural peace. *Exotic:* the fastest
crossing between climate bands. *Threat:* the wind itself.
⚠️ It runs alongside the Dew Belt — **the farmers live one ridge from the most violent air on
the planet.**

**The Fuel Works** — a ⭐ **Junker stronghold** in the **Sunreach**, cutting fuel from the
chemistry lakes.
*Abundant:* propane and ammonia fuel. *Denies:* food, warmth, water. *Exotic:* cryogenic
reagents. *Threat:* the cold, and the Junkers.

_Proposed, not yet ruled: **the Listening Floor** (a Rakatan array still transmitting, on the
plateau's edge) and **the Crawler Graveyard** (where the stolen sandcrawlers go to die)._

**The Hopeless Call** ⭐ — a Rakatan array **out on the NIGHTSIDE**, forever repeating an
ancient code nobody understands any more. Sited where **nobody wants to bother with it even
if they have advanced starships, because it simply is not worth it.** Its inaccessibility is
the point, not an obstacle to be balanced.

⛔ **The Crawler Graveyard is DROPPED** — owner, 2026-08-16: the Jawa would salvage anything
long before abandoning it. 🔑 Keep the reasoning, it characterises them: **nothing Jawa-owned
is ever abandoned intact.** There are no Jawa ruins.

## Axis 4 — biome assignment. RULED, 2026-08-16

Palette is **65 installed BiomeDefs**, not the 19 that happened to generate.
⛔ Never paint the non-surface ones onto the planet: `Space`, `Orbit`, `Undercave`,
`CQF_Undercave`, `Underground`, `AM_UndergroundSpace`, `MetalHell`, `Labyrinth`,
`AG_PocketPlane`, `AG_NereidPocketPlane`, `VQEA_AncientComplex`.

### The nightside — one biome, many contents

- 🔴 **`AB_RockyCrags` DOMINATES the whole dark half** — everything past the nightward
  terminator transition, all the way to the umbra. It is the default; it is "everything else"
  out there.
- ⭐ **Variety comes from the CONTENTS of the tile, not the biome** — weather, the strange
  liquid lakes, mutators. This is the scale doctrine applied: the nightside's diversity lives
  at local-map scale.
- **`Glowforest` dwells mostly between the crags and the dark terminator region** — the band
  where lightless growth still finds a margin.

### The substellar plateau

`ExtremeDesert` plateau · one irregular solid mass of **`AB_MechanoidIntrusion`** (the Rust
Cathedral) · ⭐ **a ring of `Scarlands` around it** — ground the works themselves scorched,
neither sand nor machine, giving the Cathedral a halo and a buffer.

### The Dew Belt

**Still very arid** — `AridShrubland` and `Desert`. ⚠️ **The oases are TILE MUTATORS, not
biomes.** The trough's gift is fog and cool air, not wet ground; the water is pinpoint.

### Exotic biome placement — all four sets kept, each with a rule

| biome | where, and only there |
|---|---|
| **`AB_OcularForest`** | ⭐ **ONLY at the tops of mountains**, in tiny patches. It answers *"what if I COULD land my ship on solid mountain terrain — it would be like THIS."* |
| `PoisonForest` · `HorrorWastes` · `AB_MycoticJungle` · `BMT_FungalForest` · `AB_GelatinousSuperorganism` | **the terminator region** — none of them do well with sunlight. *(PoisonForest may be dropped after we see it in play; look first.)* |
| `AB_TarPits` | **adjacent to densely vegetated regions near rivers** |
| `AB_GallatrossGraveyard` | part of the **Pyreland set** |
| `AB_FeraliskInfestedJungle` | **only** in the dense vegetation along rivers |
| `Scarlands` | **wherever heavy industry has been active** — the abandoned mine areas, the ship salvage ground near the Hutts, and around the mechanoid incursion formation |

### ⚠️ One frozen note is superseded

`worldmap_elements.prefill.json` (FROZEN 2026-08-16, 386 whitelisted / 61 rejected) carries
on `VEE_Volcano`: *"volcanism ruled EXTINCT — flip if you want a Mustafar region."*
**Axis 2 supersedes it: dayside volcanism is ACTIVE and still raising ranges.**
✅ No harm done — `VEE_Volcano`, `LavaCrater`, `LavaFlow`, `LavaLake`, `VEE_VolcanicRichSoil`
and the geyser elements are all **whitelisted already**; only the note's reasoning is stale.
📌 `VEE_VolcanicSandDesert` ("black sand desert, long-dead volcanism") still fits — the
nightside and the worn dayside flanks are exactly where extinct volcanism belongs.

## Axis 5 — paint order and execution. RULED, 2026-08-16

- 🔴 **ANCHOR: The Scald first.** Place the impact-crater sea, then its rim mountains, then
  the volcanic range joining them, then the Empire's capital on its shore. Everything else on
  the planet is positioned relative to it.
- 🔴 **The superrotating wind runs toward the GRAY SEA.** This is now committed and it
  cascades:
  - **The Salt exists because the wind put it there** — heat piles on the Gray flank, driving
    the evaporation and the killing salinity. Its death has a cause.
  - **The Twilight Sea stays cool, calm and defensible** — which is why it is the Compact's
    stronghold, and why the **Dew Belt** (fog, farms) runs from the terminator near *it*.
  - ⇒ **Hot flank = salt and lawlessness. Cool flank = fog and farming.** The two terminators
    are opposites for one reason.
  - **The Fall Line lies downwind of the plateau**, on the Gray flank.
- **Jitter: MODERATE** — regions stay readable as regions, but borders fray and scalars wander
  within each. Not paint-bucket, not noise.
- **First draft: EVERYTHING AT ONCE**, then iterate. Paint the full planet — climate, biomes,
  regions, settlements — and review it by loading the world.

## ✅ TRUE COORDINATES — exported 2026-08-16, the blur is gone

`jawa/world_tile_export` ran for the first time and wrote **`world/world_tiles_lada.csv`** —
21,872 rows: `tile, lat, long, biome, elevation, temperature, rainfall, hilliness, swampiness`.
Full sphere: lat −88.8…88.8, long −180…180. **Committed, because regenerating it costs a
cold load.** From here the entire repaint is offline; the bridge is not needed again.

**The arc formula is CONFIRMED against the engine's own numbers:**
`d = acos(cos(long)·cos(lat))`, **correlation(arc, temperature) = −0.968**.

| arc | tiles | land | mean °C | published curve |
|---|---|---|---|---|
| 0–20° | 642 | 482 | **+55.9** | +70 at 0° |
| 20–40° | 1,938 | 1,423 | +33.2 | |
| **40–57° liveable ring** | **2,414** | **1,738** | **+9.0** | +21 at 40°, 0 at 57° |
| 57–80° | 4,018 | 2,917 | −14.1 | |
| **80–100° terminator** | **3,848** | **3,314** | **−38.9** | −37 at 90° ✅ |
| 100–120° deep dark | 3,534 | 2,527 | −63.2 | −70 at 120° |
| 120–150° | 4,032 | 2,969 | −77.3 | |
| 150–181° antistellar | 1,446 | 1,036 | −79.9 | −80 at 180° ✅ |

⭐ **Nightside (arc > 90°) = 10,828 tiles = 49.5%.** The owner's "almost precisely 50%" ruling
is met by the world as generated, with nothing to repaint. *(My earlier temperature-inversion
estimate said 51%; the true figure is 49.5%. That table is superseded by this one.)*

## ✅ FIRST DRAFT PAINTED AND LOADED — 2026-08-16

~~`src/RimMandrake/Utils/paint_ashkarr.py` — every region is a predicate over
`(arc, bearing, elevation)`, deterministic, re-runnable, `--dry` to preview.~~
⛔ DELETED 2026-08-19 — savegame writing is out; the map reaches the game over the live
bridge (`ASHKARR_WORLD_DEFINITION.md` §12). 🔑 **The technique survives in its successor**:
`src/RimMandrake/Utils/ashkarr_paint.py` is still every region as a predicate over
`(arc, bearing, elevation)`, deterministic and one-planet — it just writes a CSV, not a save.
**The engine loaded the result and its own `jawa/world_stats` reports the painted world.**

| region | tiles | | region | tiles |
|---|---|---|---|---|
| crags | 5,708 | | fall_line | 479 |
| terminator | 3,778 | | volcanic_range | 468 |
| outer_dayside | 2,985 | | propane_core | 445 |
| liveable_ring | 2,077 | | gray_sea | 296 |
| glow_band | 1,794 | | plateau | 285 |
| deep_desert | 1,181 | | twilight_sea | 240 |
| dew_belt | 847 | | scorch_ring / the_salt / scald_rim | 181 / 179 / 166 |
| frozen_sea | 511 | | cathedral / scald_sea | 129 / 123 |

- **Temperature −81.2 … +80.6 °C** — the ruled endpoints, hit by remapping the generated
  field's ends rather than replacing it, so the engine's own variation survives as jitter.
- **Rainfall by arc band:** 0–20° **55 mm** · 20–40° 177 (the range's peaks — the only rain on
  the planet, up to 1,500 mm) · 40–58° **51** · 58–80° **66** · 80–100° **219** (fog and dew)
  · nightside **38–55**. The dayside effectively never rains, as ruled.
- **25 biomes, zero unresolved hashes.** `AB_RockyCrags` 31% owns the dark; the arid core
  (AridShrubland/Desert/ExtremeDesert/Wasteland) is 45%; **`AB_OcularForest` is 19 tiles**,
  peaks only.
- ⚠️ **The world-object mask was the real trap** — 5 settlements and landmarks stood in newly
  painted water. Fixed by converting **their tiles to land**, never by moving the objects, so
  no ID or faction reference moved. **Any future repaint must redo this step.**
- 📌 The engine counts 1,849 water tiles against the 1,170 `Ocean`+`SeaIce` painted — it also
  classes the propane lakes, tar pits and oases as water. Not a defect; do not chase it.

## Second pass — 2026-08-16, owner's review notes actioned

~~**Pipeline is now two idempotent scripts, source → dest, no game needed:**
`world/WORLDMAP_source.rws` (pristine, never written) → `paint_ashkarr.py` →
`populate_ashkarr.py` → `world/WORLDMAP_gen.rws` → the game's Saves folder.~~
⛔ DELETED 2026-08-19 — savegame writing is out; the map reaches the game over the live
bridge (`ASHKARR_WORLD_DEFINITION.md` §12). Both scripts are gone and there is no
`.rws` output any more.
🔑 **The reason it needed a pristine source is still worth knowing**, and it generalises to
any non-idempotent paint: the temperature remap normalised the *generated* field's
endpoints, so running it over its own output compressed the range twice. `ashkarr_paint.py`
sidesteps this entirely — it derives temperature from arc, never from a prior field.

### 🔴 The magenta tiles — SOLVED, and it was ours

`AB_TarPits` rendered as missing-texture magenta. **Not a mod defect.** ReGrowth's
BiomesKit pack ships world-map textures per biome per hilliness, and three biomes
carry a `Forest/` set with **no `Hills/` set at all**: `AB_TarPits`,
`AB_IdyllicMeadows`, `AB_MiasmicMangrove`. The painter had given terminator tiles
hilliness 3, so BiomesKit looked for `AB_TarPits/Hills/LargeHills.png` and found
nothing. ⇒ **`FLAT_ONLY` in the painter clamps those biomes to hilliness ≤ 1.**
**Generalises: before painting any biome onto hilly ground, check its worldmap
texture set covers that hilliness.**

### The seas are fields now, not rectangles

Each sea is a **scalar field thresholded at zero** — distance from a centre, with its
radius modulated by 3–4 sinusoid harmonics in bearing and arc. That yields bays,
headlands, peninsulas and offshore islands instead of a strip following the
terminator. The Salt is defined as the Gray Sea's own coastal margin (`-0.5 < f ≤ 0`),
so it hugs whatever shape the sea took.

### Pollution — CALIBRATED, no longer a hypothesis

The pristine world's own `tilePollution` max is **exactly 65535** with **5% of tiles
non-zero**, matching its `pollution 0.05` generator setting. ⇒ `raw / 65535 → 0..1`
is confirmed. Painted: Rust Cathedral 0.55–0.95 · scorch ring 0.30–0.70 · Fall Line
0.08–0.35 · volcanic range 0.05–0.22 · The Salt 0.04–0.14, plus the dirty biomes
(PoisonForest, TarPits, HorrorWastes, Scarlands). **Ancient machinery leaks; nothing
else on this planet does.**

### Settlements — 66, all ours

Every settlement **converted** to a ratified faction, moved to a tile that faction
would hold, and renamed. ⛔ **Converted, never deleted** — removing a faction object
would tear the save's reference graph. Counts: Moisture Farmers 9 (Dew Belt) ·
Deepwater Compact 8 (Twilight shore) · Indigenous Tribes 7 · Hutt Cartel 6 (Twilight
shore) · Free Droid Enclaves 6 incl. **the Trade Socket** · Wildsteam 5 · Junkers 5
incl. **the Fuel Works** (Sunreach) · Rogue Droids 4 incl. **the Hopeless Call**
(deep dark) · Empire 3 incl. **Sunspire**, the capital on the Scald shore ·
Ascendant Helix 3 · Geonosian Foundry Hive 3 · CIS 3 · Binary Star Raiders 3 ·
OuterRim Galactic Empire 1.

### Region names — renamed BY TYPE ONLY

37 world features renamed off their generated fantasy names. ⚠️ **No geographic claim
is made.** A feature's `<drawCenter>` could not be decoded into lat/long — the
candidate mapping put `MountainRange` centres at −350 m, the sea floor — so names are
chosen by feature TYPE, not by where they sit. **Decoding `drawCenter` is open work.**

### ✅ Region names now sit ON their regions — the drawCenter convention, recovered

The floating territory labels are fixed, and the earlier "no geographic claim" caveat
is **withdrawn**. Two measurements did it:

1. **`tileFeature` is the exact tile → feature membership** (2 bytes/tile, `0xFFFF` =
   none). Nothing needs inferring from where a label happens to be drawn.
2. 🔑 **The `drawCenter` convention**, recovered by comparing every stored centre
   against the centroid of that feature's own member tiles:

   ```
   drawCenter = ( cosLat·sinLon,  sinLat,  −cosLat·cosLon ) × 100
   ```

   Game **x = east, y = north, z = NEGATIVE cosLat·cosLon**. The earlier failed guess
   used `long = atan2(x, z)` and missed that negation — which is exactly why it put
   MountainRange centres at −350 m and why the guess was thrown away rather than used.

~~`src/RimMandrake/Utils/name_ashkarr_regions.py` re-cuts all 37 feature slots to our
regions, names them, writes a centre that is the true centroid of each region's tiles,
and scales `maxDrawSizeInTiles` by √(tile count).~~ ⛔ DELETED 2026-08-19 — savegame
writing is out; the map reaches the game over the live bridge
(`ASHKARR_WORLD_DEFINITION.md` §12).
🔑 **The `drawCenter` formula above and the recipe here are the deliverable, not the
script** — the bridge importer must do exactly this: centroid of the member tiles,
`maxDrawSizeInTiles` scaled by √(tile count). See `ASHKARR_WORLD_DEFINITION.md` §12.5.
⚠️ The centre check below was measured by running the deleted script and re-loading the
save; it is a 2026-08-16 result, not something reproducible today:
**The Scald lands at lat −3.5 / long −35.2 = 35.3° arc** (designed: 35°), **The Anvil
at 0.4° arc**, **The Umbra at 180°**, the Nightspill on the Twilight flank and the
Sunreach on the Gray one.

Large regions are cut into four tracts by bearing quadrant — Gray / North / Twilight /
South — so a 5,000-tile crag field is not one label stretched across a hemisphere.

### Faction names, label crowding, and one bridge gap — 2026-08-16

- **All 55 faction names rewritten.** "Thiussia Compact" and "Hive of Ko'coclak" were
  FACTION names, not settlement names, and Faction Territories mode draws them across
  the planet — so they were the most-read text on the map. Our 14 keepers now carry
  their real names (**The Galactic Empire**, **The Deepwater Compact**, **The Hutt
  Cartel**, **The Dune Tribes**, **The Moisture Farmers**, **The Rust Choir**…); the
  other 41 keep existing — deleting a faction tears the reference graph — but are named
  to belong on this planet.
- **Label size is now vanilla-calibrated**: `0.44·√tiles`, capped 19.2, because the
  pristine world's own features run 2.4–19.2 at up to ~1,950 tiles. The first attempt
  used 2·√tiles and every label hit the cap, so they were all maximum size and collided.
- **Crowding rule:** labels are accepted **by CANON PRIORITY, then size**, and any whose
  centre falls within 11° of an accepted one is dropped. Sorting by size alone crowded
  out **The Scald** and **The Rust Cathedral** in favour of generic tracts — the places
  the world exists for. 28 of 37 slots now carry a name; the dropped ones (The Anvil,
  The Ashteeth, The Scorch) are nested inside larger named regions anyway.
- ⛔ **BRIDGE GAP: the world view cannot be opened from a loaded map.** `load_game_ready`
  lands in the colony map, `open_main_tab` NREs on the World tab (it has no window type),
  and both click tools refuse it — *"Main-tab targets are descriptive only."* ⇒ **CHECK
  cannot screenshot the world map by itself once a game is loaded.** Visual review of
  world-map work needs a human to press World, or a new companion verb.

### The foreign banners — it was the Sites, not the settlements

All 66 settlements were already ours, but **20 `Site` world objects still carried
foreign factions**, and the Faction Territories overlay draws a coloured claim and a
name for **any faction owning ANY world object** — so a dozen foreign banners sat on
the planet with no settlement behind them. Sites are now reassigned across the Dune
Tribes, Junkers, Hutt Cartel, Wildsteam, Binary Star Raiders and the Confederacy.

✅ **Measured after: exactly 14 factions own anything on Ash'karr, and all 14 are ours.**

⚠️ **Pipeline conflict, caught and removed:** `populate_ashkarr.py` also renamed world
features by type, which silently **undid** `name_ashkarr_regions.py` — it reverted 10
region names to generic type names on this run.
~~That step is deleted; the regions script owns the labels. **Run order is paint →
populate → regions → factions.**~~ ⛔ DELETED 2026-08-19 — all four scripts are gone;
savegame writing is out and the map reaches the game over the live bridge
(`ASHKARR_WORLD_DEFINITION.md` §12).
🔑 **The lesson outlives the pipeline and applies to the bridge importer:** exactly ONE
stage may own a field. Two stages that both touch feature names will silently fight, and
the later one wins without telling you.

📌 Region labels are vanilla-scaled now, so at full-globe zoom only the largest draw.
That is the shipped behaviour, not a defect — zoom in and the rest appear.
📌 To judge the *terrain*, switch the map mode OFF Faction Territories. The pastel hex
wash is an overlay from Map Mode Framework, not the world.

### 🔴 The doubled labels — unused feature slots were still drawing

Two region names printed on top of each other at the Fall Line. Cause: the regions
script writes into the 37 existing feature slots, and **the slots it does not use kept
the PREVIOUS run's name and drawCenter — and the game draws them.** So every earlier
naming pass left ghosts behind that piled onto the new labels.

⇒ Unused slots are now **blanked**: empty `<name>` and `maxDrawSizeInTiles 0.0001`.
**Generalises: when you rewrite a fixed-size table in a save, the entries you skip are
not empty — they are whatever was there before, and they are still live.**

### Can the bridge remove a faction? NO — measured, not assumed

- `Outputs\All Factions To Remove` (the engine's own list) returns **"0 factions found."**
  RimWorld will not garbage-collect any of them.
- The whole faction debug surface is `Execute raid with faction` · `RegenerateFactionLeaders`
  · `T: Set Faction` · `Set Faction Rect` · `Kill Faction Leader` · `Set Faction Relations`
  · `T: Make Faction Leader`. **None removes a faction.**
- Live state agrees with the file: **12 visible factions hold all 66 settlements, all ours**
  — but **31 zero-settlement factions are still VISIBLE**, and visibility is what draws a
  name and a territory. Owning nothing does not remove a faction from the map.

⇒ **Removing them is a worldgen-time act** (the ratified `WORLDGEN_FACTION_CHECKLIST.md`,
21 untick / 6 keep) **or a surgical save edit.** The bridge cannot do it.

**Live mitigations applied via mod settings** (`jaeger972.factionterritories`, read back):
- `defaultToFactionTerritoriesMapMode` **True → False** — the world no longer opens as
  political hexes; you see the planet.
- `minLabelConnectedTiles` **7 → 14** — suppresses the small foreign territory labels.
- 📌 `includeWaterTiles` was **already False**, so territory is not supposed to cover
  ocean; anything still drawn over water is stale render state, not new claims.

## Race → faction assignment — sheet built 2026-08-17

`design/Jawa/worldbuilding/review/race_faction_assignment.html` — 70 xenotypes, 12
factions plus "(no faction)", every row pre-filled with a proposed home. **14 contested**,
**6 moved** off their current faction, **2 deliberately unassigned**.

### What the audit found first

- **6 of 8 Jawa factions are already well wired** — `Inherit="False"`, chances summing to
  exactly 1.00, `MayRequire` guards, coherent rosters (Deepwater is entirely aquatic;
  Ascendant Helix is the geneticists).
- 🔴 **`Jawa_FreeDroidEnclaves` has `Inherit="True"` and ZERO xenotypes** — it inherits
  `OutlanderFactionBase`'s vanilla set, so a droid faction fields Hussars and Dirtmoles.
- ⚠️ **`Jawa_IndigenousTribes` also has `Inherit="True"`** — MandrakeJawa at 1.00 dominates
  in practice (C40 measured 6/6) but vanilla tribals are appended, so it is a latent leak.
- **37 of 69 species were fielded by nobody.** Two absurdities: **the Hutt Cartel
  contained no Hutts**, and **no faction fielded Tuskens** though the ratified fiction puts
  them in the near-desert.
- **The four vanilla reskins carry no `xenotypeChances` at all**, so Empire, the Homestead,
  the Deep Desert Tribes and Blackstar field vanilla xenohumans today. Any assignment to
  them is new content and needs a `Baseliner` share or they become 100% alien.

### 🔴 RULED, owner 2026-08-17: MandrakeJawa is canon

There are **two** Jawa xenotypes in the races mod — `MandrakeJawa` (in its own
`MandrakeJawaXenotype.xml`) and `RimMandrakeJawa` (24 genes, donor-generated).
**`MandrakeJawa` is the one the owner built in game and exported as the `.xtp`, and it is
canon.** `RimMandrakeJawa` is **CUT**. Never field both.

### ⏱ Not worldgen-gated

`xenotypeChances` is read when a faction's pawns are GENERATED, not when the world is
created. ⇒ the world can be generated now and the racial wiring fixed afterwards; it takes
effect for every pawn made after the next startup. **A restart is needed for the def edit,
but it does not block the worldgen run.**

## ✅ ASH'KARR IS BUILT — 2026-08-17, seed `viscera`

`world/WORLDMAP_gen.rws`, verified by loading it and reading the engine's own numbers.

| | |
|---|---|
| geometry | TidallyLocked · subdivisions 7 · **coverage 1.0** · **21,872 tiles** |
| climate | **−79.4 … +80.8 °C** · water 6.9% · 2,550 polluted tiles |
| biomes | `AB_RockyCrags` 6,526 (30%) · AridShrubland 5,290 · Desert 1,647 · Wasteland 1,213 · ExtremeDesert 971 · zero unresolved hashes |
| regions | **28 named** — The Scald, The Rust Cathedral, The Scald Spine, The Twilight Sea, The Gray Sea, The Dew Belt, The Fall Line, The Salt, The Nightspill, The Sunreach, The Umbra … |
| people | **37 settlements across 11 factions, every one ours** |
| integrity | 0 world objects in water · 0 non-ours owning anything · roads and rivers pruned of everything the repaint stranded |

Settlements: Homestead 5 · Deepwater Compact 5 · Deep Desert Tribes 4 · Hutt Cartel 4 ·
Empire 3 · Free Droid Enclaves 3 · Jawa Trade Moot 3 · Wildsteam 3 · Junkers 3 ·
Geonosian Foundry Hive 2 · Ascendant Helix 2.

### 🔴 THE ONE OUTSTANDING GAP: Blackstar Company is absent

`Pirate` did not generate, for the third world running. **Cause identified:** vanilla's def
is `<FactionDef Name="PirateBandBase">` with `<defName>Pirate</defName>` and
`<label>pirate gang</label>` — so in the faction panel it reads as a *stray*, not as one of
ours, and gets deleted during the whittling pass. `requiredCountAtGameStart 1` does not
save it.

⇒ **Fix before the next generation:** confirm `Jawa_Patches/Patches/BlackstarCompany.xml`
relabels it to **Blackstar Company** *in the panel*. The patch exists and throws no error,
but nobody has verified the panel shows the new label — if it still says "pirate gang", that
is why it keeps being deleted, and the label patch needs to land earlier.
📌 Everything else in the ratified 14 is present. The world is usable as it stands; Blackstar
is a missing antagonist, not a broken world.
