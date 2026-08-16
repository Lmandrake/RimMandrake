# worldgen_interactive_def.md — the working definition of the world we are painting

Live working doc for the hand-built, frozen planet. Bullets only. Decisions land here
as they are made; new-content ideas go to `worldgen_interactive_build_concepts.md`.

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

### Engineering consequences to carry into the repaint

- Rainfall drives biome scoring and plant growth, so near-zero dayside rainfall is doing
  double duty — it must be set, not left at Normal's ~950 mm median.
- The terminator cliff is only a few tiles wide at 21,872 tiles. **Measure how many tiles
  span 80°→100° arc before designing anything that needs room there.**
- Fog/dew, ammonia precipitation, mineral-ice mining and the chemistry cycle have no vanilla
  representation. Parked as build concepts; the repaint must not depend on them.
