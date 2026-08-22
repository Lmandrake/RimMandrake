# Xenotype temperature tolerance on Ash'karr — XENOTYPE_TEMPERATURE_TOLERANCE_AUDIT_1

_Measured 2026-08-22 by BUILD against the live 578-mod def dump and
`world/ASHKARR_WORLDMAP_tiles.csv` (21,872 tiles) + `ASHKARR_WORLDMAP_settlements.csv`
(120 settlements). No number here came from a grep._

Baseline human comfy band: **16.0 .. 26.0 C** (`Human` statBases, read from the dump).


## 🔴 THE ANSWER, IN ONE LINE

**Eleven of the twelve authored factions field xenotypes whose comfort band cannot cover
their own ground. The Jawa Trade Moot is the only clean one — and it is the player's.**

`MandrakeJawa` runs **20.5 .. 46.0 C** against tiles of 24.4 .. 28.1 C. Every other faction
rolls species that are outside their comfort band somewhere on their own territory, and
`Ascendant Helix` is the mirror image: all fifteen of its xenotypes are too cold for tiles
running -36.5 to -2.3 C.

### ⚠️ COMFY IS NOT SURVIVABLE, AND THIS TABLE MEASURES COMFY
`ComfyTemperatureMin/Max` is where a pawn is CONTENT. Outside it a pawn takes a rising
heatstroke or hypothermia hediff and a mood penalty; apparel insulation, an indoor room and
a cooler all close the gap, and none of that is in these numbers. **"Too hot for 19" does
not mean nineteen species die.** It means nineteen are uncomfortable outdoors at that
faction's hottest site, which is a productivity and mood problem and a reason to build.

### ⚠️ THREE MORE THINGS THIS TABLE IS NOT
1. **`temp_c` is the ANNUAL MEAN.** RimWorld swings a map by season and by hour around it,
   so the lived maximum on a hot tile is well above the figure here. Every "too hot" count
   is a FLOOR.
2. **NPC pawns on the world map take no temperature damage.** This bites when the player
   raids or visits a settlement, and it bites the player's own colony continuously. A
   Deepwater Nautolan is not dying in his own town today.
3. **Droids are exempt and the Free Droid Enclaves row is a false alarm.** Their pawns are
   RACES, not human xenotypes: `OuterRim_ImperialLaborDroid`, `BattleDroid`, `KXSecurityDroid`
   and `ProtocolDroid` all read comfy **-250 .. 250 C**. The 64.7 C tile is fine. The
   "none declared" in the table means the FactionDef names no xenotypeSet, which is correct
   for a droid faction and not a gap.

### 🔑 AND THE COLD NURSERY IS NOW A MEASURED TENSION, NOT A PREDICTION
`MandrakeJawa` adults are comfortable to **46.0 C**. A Jawa egg ruins above **32 C**
(`CompProperties_TemperatureSensitiveHumanEgg`). ⇒ **there is a 14-degree window in which
the clan is perfectly comfortable and its own clutch cooks**, and the Trade Moot's tiles
(24.4 .. 28.1 annual mean) sit right under it — close enough that a summer afternoon crosses
32 while the adults never notice. That is exactly the pressure `jawa_society.md` §4.3a
describes, and it is now a number rather than a guess.

## The population
- 139 XenotypeDefs; **128 reachable** (named in a FactionDef or PawnKindDef xenotypeSet).
- **56 of the reachable carry NO temperature gene at all** and sit on the bare human band.

## Faction by faction — can its own xenotypes cover its own ground?

| faction | settlements | coldest tile | hottest tile | xenotypes | too hot for | too cold for |
|---|---|---|---|---|---|---|
| Free Droid Enclaves | 12 | -80.2 | 64.7 | *none declared* | — | — |
| Geonosian Foundry Hive | 5 | 32.4 | 62.8 | 1 | **1** | **0** |
| Deep Desert Tribes | 9 | 50.9 | 58.3 | 10 | **10** | **0** |
| The Galactic Empire | 3 | 31.9 | 54.3 | 4 | **4** | **0** |
| Homestead Defense League | 37 | -3.6 | 45.0 | 14 | **14** | **11** |
| Deepwater Compact | 5 | 22.5 | 44.7 | 11 | **11** | **0** |
| Hutt Cartel | 19 | 17.2 | 40.1 | 21 | **19** | **7** |
| Wildsteam Clan | 4 | 19.5 | 36.3 | 8 | **8** | **0** |
| Blackstar Company | 4 | 21.6 | 33.4 | 12 | **11** | **0** |
| the Junkers | 8 | 0.5 | 29.8 | 17 | **16** | **16** |
| Jawa Trade Moot | 7 | 24.4 | 28.1 | 1 | **0** | **0** |
| Ascendant Helix | 7 | -36.5 | -2.3 | 15 | **0** | **15** |

## The named lists

### Geonosian Foundry Hive  — hottest tile 62.8 C, coldest 32.4 C
**Comfy max below the hottest tile (1):** `RimMandrakeGeonosianVariants` 26.0

### Deep Desert Tribes  — hottest tile 58.3 C, coldest 50.9 C
**Comfy max below the hottest tile (10):** `Baseliner` 26.0, `RimMandrakeIridonian` 26.0, `RimMandrakeLasat` 26.0, `RimMandrakeMimbanese` 26.0, `RimMandrakeNagai` 26.0, `RimMandrakeNelvaanian` 26.0, `RimMandrakeTaung` 26.0, `RimMandrakeKaleesh` 36.0, `RimMandrakeTogorian` 36.0, `RimMandrakeTusken` 46.0

### The Galactic Empire  — hottest tile 54.3 C, coldest 31.9 C
**Comfy max below the hottest tile (4):** `RimMandrakeChiss` 21.5, `Baseliner` 26.0, `RimMandrakeChadraFan` 26.0, `RimMandrakeEchani` 26.0

### Homestead Defense League  — hottest tile 45.0 C, coldest -3.6 C
**Comfy max below the hottest tile (14):** `RimMandrakeAbednedo` 26.0, `Baseliner` 26.0, `RimMandrakeIthorian` 26.0, `RimMandrakePantoran` 26.0, `RimMandrakeBothan` 26.0, `RimMandrakeSullustan` 26.0, `RimMandrakeTogruta` 26.0, `RimMandrakeChadraFan` 26.0, `RimMandrakeDuros` 26.0, `RimMandrakeKelDor` 26.0, `RimMandrakeOrtolan` 26.0, `RimMandrakeTwilek` 26.0, `RimMandrakeUgnaught` 26.0, `RimMandrakeMirialan` 36.0

**Comfy min above the coldest tile (11):** `RimMandrakeMirialan` 20.5, `RimMandrakeDuros` 20.5, `RimMandrakeAbednedo` 16.0, `Baseliner` 16.0, `RimMandrakeIthorian` 16.0, `RimMandrakeSullustan` 16.0, `RimMandrakeTogruta` 16.0, `RimMandrakeKelDor` 16.0, `RimMandrakeTwilek` 16.0, `RimMandrakeUgnaught` 16.0, `RimMandrakeChadraFan` 6.0

### Deepwater Compact  — hottest tile 44.7 C, coldest 22.5 C
**Comfy max below the hottest tile (11):** `RimMandrakeMonCalamari` 21.5, `RimMandrakeNautolan` 21.5, `RimMandrakeSelkath` 21.5, `RimMandrakeChagrian` 26.0, `RimMandrakeHerglic` 26.0, `Baseliner` 26.0, `RimMandrakeBith` 26.0, `RimMandrakeBothan` 26.0, `RimMandrakeDuros` 26.0, `RimMandrakeGungan` 26.0, `RimMandrakeQuarren` 36.0

### Hutt Cartel  — hottest tile 40.1 C, coldest 17.2 C
**Comfy max below the hottest tile (19):** `RimMandrakeAqualish` 26.0, `RimMandrakeDevaronian` 26.0, `RimMandrakeGamorrean` 26.0, `RimMandrakePyke` 26.0, `RimMandrakeRodian` 26.0, `RimMandrakeTrandoshan` 26.0, `RimMandrakeTwilek` 26.0, `RimMandrakeZeltron` 26.0, `Baseliner` 26.0, `RimMandrakeBothan` 26.0, `RimMandrakeFeeorin` 26.0, `RimMandrakeKubaz` 26.0, `RimMandrakeMuun` 26.0, `RimMandrakeOrtolan` 26.0, `RimMandrakeUgnaught` 26.0, `RimMandrakeZygerrian` 26.0, `RimMandrakeHutt` 36.0, `RimMandrakeKlatoonian` 36.0, `RimMandrakeNikto` 36.0

**Comfy min above the coldest tile (7):** `RimMandrakeNikto` 20.5, `RimMandrakeDevaronian` 20.5, `RimMandrakeFalleen` 20.5, `RimMandrakeRodian` 20.5, `RimMandrakeTrandoshan` 20.5, `MandrakeJawa` 20.5, `RimMandrakeKubaz` 20.5

### Wildsteam Clan  — hottest tile 36.3 C, coldest 19.5 C
**Comfy max below the hottest tile (8):** `RimMandrakeLasat` 26.0, `RimMandrakeWookiee` 26.0, `RimMandrakeEwok` 26.0, `RimMandrakeIthorian` 26.0, `RimMandrakeTogruta` 26.0, `Baseliner` 26.0, `RimMandrakeCathar` 26.0, `RimMandrakeTogorian` 36.0

### Blackstar Company  — hottest tile 33.4 C, coldest 21.6 C
**Comfy max below the hottest tile (11):** `RimMandrakeNagai` 26.0, `RimMandrakeZygerrian` 26.0, `RimMandrakeAnzati` 26.0, `Baseliner` 26.0, `RimMandrakeDefel` 26.0, `RimMandrakeCathar` 26.0, `RimMandrakeDuros` 26.0, `RimMandrakePyke` 26.0, `RimMandrakeRodian` 26.0, `RimMandrakeTaung` 26.0, `RimMandrakeTwilek` 26.0

### the Junkers  — hottest tile 29.8 C, coldest 0.5 C
**Comfy max below the hottest tile (16):** `RimMandrakeChadraFan` 26.0, `RimMandrakeFeeorin` 26.0, `RimMandrakeGamorrean` 26.0, `RimMandrakeGand` 26.0, `RimMandrakeAqualish` 26.0, `Baseliner` 26.0, `RimMandrakeRodian` 26.0, `RimMandrakeSnivvian` 26.0, `RimMandrakeTrandoshan` 26.0, `RimMandrakeUgnaught` 26.0, `RimMandrakeWeequay` 26.0, `RimMandrakeDuros` 26.0, `RimMandrakeKubaz` 26.0, `RimMandrakePantoran` 26.0, `RimMandrakeTwilek` 26.0, `RimMandrakeZygerrian` 26.0

**Comfy min above the coldest tile (16):** `RimMandrakeGand` 20.5, `RimMandrakeNikto` 20.5, `RimMandrakeRodian` 20.5, `RimMandrakeTrandoshan` 20.5, `RimMandrakeWeequay` 20.5, `RimMandrakeDuros` 20.5, `RimMandrakeKubaz` 20.5, `RimMandrakeFeeorin` 16.0, `RimMandrakeGamorrean` 16.0, `RimMandrakeAqualish` 16.0, `Baseliner` 16.0, `RimMandrakeUgnaught` 16.0, `RimMandrakeTwilek` 16.0, `RimMandrakeZygerrian` 16.0, `RimMandrakeChadraFan` 6.0, `RimMandrakeSnivvian` 6.0

### Jawa Trade Moot  — hottest tile 28.1 C, coldest 24.4 C
_Clean — every xenotype it rolls covers every tile it holds._

### Ascendant Helix  — hottest tile -2.3 C, coldest -36.5 C
**Comfy min above the coldest tile (15):** `RimMandrakeNeimoidian` 20.5, `RimMandrakeUmbaran` 20.5, `RimMandrakeIktotchi` 20.5, `RimMandrakeKubaz` 20.5, `Baseliner` 16.0, `RimMandrakeBith` 16.0, `RimMandrakeCerean` 16.0, `RimMandrakeKaminoan` 16.0, `RimMandrakeMuun` 16.0, `RimMandrakeKelDor` 16.0, `RimMandrakeRakata` 16.0, `RimMandrakeSithKissaiPureblood` 16.0, `RimMandrakeSithMassassi` 16.0, `RimMandrakeSithZ` 16.0, `RimMandrakeArkanian` 6.0

