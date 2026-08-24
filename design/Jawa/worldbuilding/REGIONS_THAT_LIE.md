<!-- status: live -->
# Regions that lie about themselves — audit, 2026-08-23

Swept all 71 named regions of Ash'karr, comparing what each region's NAME promises
against what its tiles actually are. 13 fail. Four more were fixed earlier tonight
(Damp, Fever Wood, the Kiln pan, Dew Horn) and are not listed.

🔑 **`tile` is the jump target** — CHECK can put the camera on it directly with
`jawa/world_view {centerTile: N}`. The lat/lon is the LABEL position, derived from
`WorldFeature.drawCenter`, not the region's geometric centre; on a big region those
can be 20°+ apart.

| region | tiles | lat | lon | tile | what is wrong |
|---|---:|---:|---:|---:|---|
| **Deadstone** | 2051 | 30.22 | -158.08 | `11012` | name says ROCK; 0% hilliness>=4 and 10% rocky biome |
| **Dune Sea** | 1692 | 28.10 | -13.05 | `11298` | INCOHERENT: 13 different biomes |
| **Nightspill** | 853 | 11.02 | -117.29 | `12010` | INCOHERENT: 9 different biomes |
| **Twilight Sea** | 852 | 7.72 | -81.06 | `11840` | INCOHERENT: 8 different biomes |
| **Sunreach** | 795 | -32.57 | 110.73 | `10552` | name says HOT; hottest tile is 6.9C |
| **Gray Crags** | 577 | 14.04 | 111.26 | `11644` | INCOHERENT: 8 different biomes |
| **Thornbelt** | 502 | -57.06 | 38.68 | `10672` | name says VEGETATION; only 0% lush |
| **South Crags** | 433 | -50.38 | 173.68 | `10778` | name says ROCK; 9% hilliness>=4 and 5% rocky biome |
| **Dew Belt** | 362 | -5.42 | -82.45 | `11853` | INCOHERENT: 8 different biomes |
| **Anvil** | 349 | -13.79 | -6.28 | `11228` | INCOHERENT: 10 different biomes |
| **Sunward Scrub** | 154 | 58.43 | 64.82 | `10215` | name says VEGETATION; only 0% lush |
| **Cinderdark** | 153 | -26.19 | 137.33 | `9652` | name says HOT; hottest tile is -29.1C |
| **Thornend** | 61 | -20.87 | 136.51 | `11671` | name says VEGETATION; only 0% lush |

## How each fault was decided

- **name says VEGETATION** — name carries wood/forest/jungle/thorn/grass/scrub/bloom/fern/moss/green/leaf, but under 20% of tiles are a lush biome.
- **name says HOT / COLD** — name carries scald/kiln/pyre/ember/forge/cinder/blaze/sun/glare/scorch/fever/fire/anvil (or frost/ice/cold/night/umbra/dark/chill/glacier), and no tile reaches 25 °C (or none drops below 5 °C).
- **name says ROCK** — crag/spine/ridge/stone/scarp/cliff, but under 25% hilliness ≥4 AND under 25% a rocky biome.
- **INCOHERENT** — 8 or more different biomes in one named region. Dew Horn had ten before it was rebuilt as badlands.

⚠️ **Judgement, not a defect list.** `Cinderdark` at −29 °C may be deliberate — cold ash, not hot cinders. `Deadstone` is 1432 tiles of HorrorWastes, which is a fine thing for a place called Deadstone to be even if it is not literally stony. Read each one before changing it.
