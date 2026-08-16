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

## Open — the current axis

**Axis 1: biome layout, temperature, rainfall.** Questions in play, answers land here.

## Name

- TBD this session. Currently the save carries the default `Crashlanded`.
