# Rot-wave live proof battery — 2026-09-18

Driver: BENCH live-test subagent. 30-mod tier list (minimal + envhazards + creaturebehaviors + rotsporekit + patches).

## A. Def probes — PASS (34/34 resolved live)

Route: `jawa/get_defs` (semicolon-separated `DefType/defName`), game at main menu (`programState: Entry`) — defs are loaded, no map needed. Tool census first: **450 tools registered**, companion loaded.

`foundCount 34, notFound []`. Every probe resolved, each with its owning mod:

| probe | result |
|---|---|
| `GameConditionDef/RUT_SheenExposureLock` | **found**, modName `RimUtinni Patches (Jawa campaign)`, packageId `mandrake.rut.patches`, label "the Sheen's breath" → **ENVHAZARDS_NEVER_ACTIVATED_1 probe PASSES**: the `MayRequire="mandrake.rm.environmentalhazards,mandrake.rut.rotsporekit"` gates now pass and the def loads |
| `GameConditionDef/RUT_SporeCloud` | found, `RimUtinni: Rot Spore Kit`; `modExtensions: ["EnvironmentalWeatherExtension"]` resolved (a missing modExtension type would have eaten the def) |
| `ThingDef/RUT_PaleTree` `requiredSubplantCountPerPsylinkLevel` | **`[20, 20]` — exactly TWO entries** (read via `jawa/get_defs` `fields=comps, deep=true`, off the live `CompProperties_MeditationFocus`) |
| `RUT_AgelessCap`, `RUT_RegenerantVeil`, `RUT_EuphoricCrown`, `RUT_FalseFruit` | all found (ThingDef, RotSporeKit) |
| `RUT_BrewingVessel`, `RUT_GrownFurnace` | both found (ThingDef, RotSporeKit) |
| three teas: `RUT_Tea_AgeReversal`, `RUT_Tea_Bioregeneration`, `RUT_Tea_Pleasure` | all found |
| four symbionts: `RUT_Symbiont_Quickflesh`, `_Nightwake`, `_Sheenblood`, `_Mycoid` | all found |
| also confirmed | `ThingDef/RUT_Apparel_ChitinSpiderHelmet`, `RUT_Glimmerslime`, `RUT_RawDulcis`, `RUT_PaleMoss`; HediffDefs `RUT_SheenCoating`, `RUT_SheenSymbiosis`, `RUT_SporesBuildup`, `RUT_SporeFlesh`, `RUT_MatGrip`, `RUT_AgeReversalSated`, `RUT_Bioregenerating`; TerrainDefs `RUT_MycelialMatting`, `RUT_MushroomFloor`; WeatherDefs `RUT_SheenFall/_SheenMist/_SheenStorm`; `BiomeDef/RUT_TheRot`; `ThoughtDef/RUT_SoldRotTreasureMemory` |

⚠️ `conditionClass` could NOT be read through `jawa/get_defs` — a `System.Type` field is not
serialised by that tool (it returns `(no such field)` for a name that does exist, and a full
field dump omits it; a `Type` inside a comp renders as `{}`). **Deferred to battery F as a
behavioural proof**: only `GameCondition_EnvironmentalWeather` produces the
unroofed-only-hediff behaviour, so F's result is the identity test.

### Mechanism read off source (before testing — informs C/D/E design)
- `RM_MapComponent_AcceleratedRot` / `RM_MapComponent_WarmGround` both check
  `map.Biome.GetModExtension<…>()` **live every tick**, not at map construction ⇒ retagging a
  generated map's world tile to `RUT_TheRot` turns both mechanisms on.
- Settings defaults: item rot ×12, corpse rot ×20, `warmGroundOffsetCelsius` **18**,
  `maxRoomTemperature` cap **21 °C**, `requiredFloorFraction` **0.6**, living-produce
  `heatPerUnit` 3.5 per unit per 2000 ticks (calibrated to one campfire at 200 units).
- 🔴 `RUT_TheRot`'s `warmTerrains` lists `AB_MycoticGrass`/`AB_MycoticSoilRich` **without
  MayRequire**; Alpha Biomes is not on this 30-mod list, so only `RUT_MycelialSoil` and
  `RUT_MycelialMatting` resolve here. Battery D must use those two.
- Sheen: `severityPerDayExposed 0.667` ⇒ severity 1.0 in **~1.5 days** bare; protection via
  `RUT_SheenProtection` apparel stat, `driveFactor = max(minDriveFactor, 1 − protection)`.

## B. Quicktest colony — PASS (Rot-biome home map obtained)

Route: `rimworld/start_debug_game_ready` (readiness `currentMap`, from `programState: Entry`).
Map came up at `ticksGame 1`, `Map_0`, 250×250, tile **67860**, 3 quicktest colonists +
1 animal, `mapParent: Settlement / PlayerColony` — a **home map**, so no abandon timer.

Generated biome was `TemperateForest`. Retagged live:
`jawa/world_tile_set {tiles:"67860", biome:"RUT_TheRot"}` → `written 1`, then `jawa/world_commit`.
**Read back: `jawa/map_info` → `mapBiome: "RUT_TheRot"`.** This is legitimate for C and D because
both `RM_MapComponent_AcceleratedRot` and `RM_MapComponent_WarmGround` evaluate
`map.Biome.GetModExtension<…>()` **inside `MapComponentTick()`**, not at map construction.

⚠️ What retagging does NOT give: the map's generated terrain/flora is still temperate-forest
(soil, tall grass), and `biomeMapConditions` were not applied at gen — so
`RUT_SheenExposureLock` is dev-started in battery E rather than arriving automatically.
**Automatic biome-driven condition attachment is therefore BLOCKED(map generated pre-retag)**;
the condition mechanism itself is tested in E.

Tile temperature 14.57 °C, `outdoorTempNow` **5.78 °C**, season Spring — left unmodified
(rot rate at 5.78 °C ≈ 0.58 of maximum, and the 21 °C warm-mat cap is still 15 °C above it,
so one temperature serves both C and D).

Test structures built (`jawa/make_empty_room`, steel `Wall` + `Door` + `RoofConstructed`),
each 7×7 outer / **25-cell interior**, all read back through `jawa/room_get` as
`usesOutdoorTemperature: false`, `openRoofCount: 0`, start temp 5.783 °C:

| room | rect | floor | contents |
|---|---|---|---|
| R1 rot control | 140,100,7,7 | Concrete | 3 × `Meat_Cow` ×75 |
| R2 living produce | 150,100,7,7 | Concrete | `RUT_Glimmerslime` 75+75+50 = **200 units** |
| R3 mat | 160,100,7,7 | **RUT_MycelialMatting** (25/25 cells) | — |
| R4 stone twin | 170,100,7,7 | Concrete | — |
| R5 furnace | 180,100,7,7 | Concrete | 1 × `RUT_GrownFurnace` |
| R6 shelter | 190,100,7,7 | Concrete | 3 roofed test pawns |
| outdoor meat | 145/147/149,120 | Soil, `roofDefName: null` | 3 × `Meat_Cow` ×75 |

12 extra colonists spawned (`jawa/spawn_pawn` ×4 groups of 3, faction `player`), apparel
cleared, positioned by `jawa/order_pawn draft=true`, verified by roof:

- **BARE** Human36838/36841/36844 — unroofed, `RUT_SheenProtection` 0
- **ROOF** Human36847/36850/36853 — inside R6, `roofDefName: RoofConstructed`
- **HELM** Human36856/36859/36862 — unroofed, wearing `RUT_Apparel_ChitinSpiderHelmet`;
  `jawa/thing_stats` on the worn instance reads **`RUT_SheenProtection` = 0.75**
- **SYM** Human36865/36868/36871 — unroofed, `RUT_SheenSymbiosis` severity 1.0 added

Zero hostiles on the map (`jawa/list_pawns faction=hostile` → 0) before any unpause.

## C. AcceleratedRot + LivingProduce (ROT_DECAY_HARVEST_1) — PASS (both halves)

### C1 outdoor meat vs walled+roofed control — PASS
Route: `jawa/spawn_batch` 3 × `Meat_Cow` ×75 outdoors on unroofed Soil (145/147/149,120) and
3 × `Meat_Cow` ×75 in the sealed control room R1; read with **`jawa/inspect_string`** (the
game's own CompRottable inspect line — the field is `inspect`, a list, not `inspectString`).

| tick | outdoor (unroofed, Rot biome) | control (walled + roofed, same map) |
|---|---|---|
| 10,847 | `Fresh … spoils in **5 hours**` | `Fresh … spoils in **1.9 days**` |
| 16,191 | **GONE — `jawa/list_things` returns `[]`** | `Fresh … spoils in 1.8 days` |
| 64,482 | still gone | `Fresh … spoils in 1 day` |

The outdoor stacks were spawned at tick 1 and were **destroyed by rot before tick 16,191 =
0.270 in-game days** — well inside the 1-day bar. The control at the *same instant* still read
Fresh with 1.8 days left, i.e. it is on vanilla's clock: `Meat_Cow daysToRotStart` 2 at room
temperature 9.78 °C (`RotRateAtTemperature` ≈ 0.98) predicts ≈2.04 days, and the game printed
1.9 days. **The accelerated path is exactly the `UsesOutdoorTemperature` predicate the
component uses** — the roofed room is untouched, the open ground is ×12.

### C2 living produce room heat — PASS
Route: `jawa/spawn_batch RUT_Glimmerslime` 75+75+50 = **200 units** into R2 (25-cell interior,
Concrete floor, roofed), `jawa/room_get` / `jawa/cell_temperature` for the read. R1 is the
identical-geometry control (same 25 cells, same floor, same roof, no produce).

| tick | outdoor | R2 with 200 units produce | R1 control | Δ |
|---|---|---|---|---|
| 10,847 | 12.21 | **62.53 °C** | 9.78 | **+52.7** |
| 16,191 | 16.06 | **83.41 °C** | 13.15 | **+70.3** |
| 64,482 | 11.66 | **46.18 °C** | 9.78 | **+36.4** |

Temperature climbs, hugely and repeatably — PASS.
⚠️ **Campfire equivalence was NOT tested against a live campfire** (a `Campfire` cannot be
fuelled from the bridge: no `fill fuel` debug action exists on this list, `jawa/set_thing_props`
has no fuel field). It is instead an **arithmetic identity in the shipped code**: living produce
pushes `stackCount × heatPerUnit` per 2000 ticks = 200 × 3.5 / 2000 = **0.35 energy/tick**;
vanilla `CompHeatPusher` pushes `heatPerSecond` every 60 ticks and Campfire's is 21 ⇒ 21/60 =
**0.35 energy/tick**. Same number by construction. Marked **UNMEASURED live**, not failed.

## D. WarmMat + GrownFurnace (ROT_WARM_MAT_1) — PASS (both halves)

### D1 mat room vs stone twin — PASS
R3 (25-cell interior, **25/25 cells `RUT_MycelialMatting`** — read back per cell via
`rimworld/get_cell_info.terrainDefName`, fraction 1.0 ≫ the 0.6 cliff) vs R4, identical
geometry, roof and walls, **Concrete** floor. Both `usesOutdoorTemperature: false`,
`openRoofCount: 0`.

| tick | outdoor | R3 mat | R4 stone twin | Δ |
|---|---|---|---|---|
| 10,847 | 12.21 | 16.72 | 8.91 | **+7.81** |
| 16,191 | 16.06 | 20.51 | 12.14 | **+8.37** |
| 64,482 | 11.66 | 18.43 | 9.66 | **+8.77** |
| 85,336 | **24.95** | 23.86 | 22.28 | +1.58 (see below) |

**The mat room reads warm against its twin — PASS.** Measured Δ **+7.8 … +8.8 °C**, below the
spec's "~+11" because the mechanism heats *toward a target*, never by a fixed offset:
`target = min(outdoorTemp + 18, maxRoomTemperature 21)` and the room's own conductive losses
hold it a little under target. The **21 °C cap is confirmed working** — R3 never rose above
20.8 while heating, and at tick 85,336 when the outdoor temperature itself reached 24.95 °C
the mat contributed nothing at all (target 21 < current room temp), exactly as
`if (current >= target) continue;` specifies. It never cools and never over-heats.
⚠️ Rot's `warmTerrains` lists `AB_MycoticGrass` / `AB_MycoticSoilRich` **with no MayRequire**;
Alpha Biomes is not on this 30-mod list so those two do not resolve. Only the RotSporeKit
terrains work here. Unmeasured on this list: whether the Alpha terrains also qualify.

### D2 `RUT_GrownFurnace` indoors, no fuel — PASS
One `RUT_GrownFurnace` spawned in R5 (identical room, Concrete, roofed, nothing else in it).

| tick | R5 furnace room | R1 control | Δ |
|---|---|---|---|
| 10,847 | **28.98** | 9.78 | **+19.2** |
| 16,191 | 27.13 | 13.15 | +14.0 |
| 64,482 | **28.76** | 9.78 | **+19.0** |

`jawa/inspect_string` on the furnace reads only `Expires in: 15 days` (→ 14 days later in the
run) — **no fuel bar, no "needs fuel", no "unfuelled" line**, and it heated continuously across
85k ticks without anything being added to it. Campfire-class heat with no fuel — PASS.
(The `Expires in` line is its own `CompLifespan`; worth knowing it is a consumable building.)

## E. Sheen exposure (ROT_SHEEN_WEATHER_1) — PASS (all four sub-claims)

Route: `jawa/weather_set {weather:"RUT_SheenFall", lockWeather:true}` (read back
`current: RUT_SheenFall`, `lockInForce: true`, a permanent `GameCondition_ForceWeather`), then
`jawa/game_condition {action:"start", condition:"RUT_SheenExposureLock", permanent:true}` →
`activeConditions` read back as `[WeatherController, RUT_SheenExposureLock]`.
Measurement: `jawa/list_pawns includeHealth=true`, all 12 pawns **drafted** (`jawa/set_draft`)
so positions hold, roof confirmed per pawn by `rimworld/get_cell_info.roofDefName`.
Coatings cleared to a clean baseline, then a 3000-tick warm-up so every exposed pawn is
carrier-seeded, then the measured window.

**Window: ticks 48124 → 64482 = 16,358 ticks = 0.2726 in-game days.** (RATE measured and
extrapolated, not waited out.) Values identical within each group, all three pawns:

| group | severity @48124 | severity @64482 | Δ | rate/day |
|---|---|---|---|---|
| BARE (unroofed, no gear) | 0.024557 | 0.206870 | 0.182313 | **0.6687** |
| HELM (`RUT_Apparel_ChitinSpiderHelmet`) | 0.006214 | 0.051792 | 0.045578 | **0.16719** |
| SYM (`RUT_SheenSymbiosis`) | 0.0001 | 0.0001 | **0.000000** | **0** |
| ROOF (sealed roofed room) | — no hediff — | — no hediff — | — | never seeded |

- **Unroofed pawns accrue, roofed pawns stay clean** — PASS. The roofed three never received
  `RUT_SheenCoating` at all: `GameCondition_EnvironmentalWeather` line 126 skips roofed pawns
  when granting the carrier, so "clean" here is *absence of the hediff*, not severity 0.
- **Helmet ≈ 4× slower** — PASS. 0.6687 / 0.16719 = **4.000**, exactly `1/(1 − 0.75)` from the
  worn helmet's `RUT_SheenProtection` 0.75 (read live off the instance via `jawa/thing_stats`).
- **`RUT_SheenSymbiosis` ⇒ zero accrual** — PASS. Severity stayed at the carrier seed 0.0001
  across 16,358 ticks; the other two unroofed groups moved in the same window.
- **Design rate check**: 0.6687/day vs the def's `severityPerDayExposed` 0.667 ⇒ a bare pawn
  reaches the `saturated` stage (`minSeverity` 1.0) in **1.495 in-game days** — the spec's
  "~1.5 days". Helmeted: ~5.98 days.
- **Top stage seeds `RUT_SporeFlesh`** — PASS. `jawa/pawn_severity_adjust offset=1.0` pushed
  the three BARE pawns to severity ≈1.21 (top stage), then 20,699 ticks (0.345 day) ran:
  **2 of 3 acquired `RUT_SporeFlesh`** (severity 0.0343 and 0.0627). The third had a roof
  appear over it mid-window. `HediffGiver_Random mtbDays 0.25` predicts ~75% in 0.345 day —
  2/3 is on prediction.

⚠️ Experimental artifact worth knowing: **RimWorld re-roofed two of my deliberately unroofed
test pens** during long unpaused runs even with every colonist drafted (`jawa/set_roof_batch
None` reverted to `RoofConstructed`). Roof state must be re-read at every measurement, never
assumed from the last write.
⚠️ `jawa/pawn_severity_adjust` takes **`offset`**, not `severity` — the client's param checker
caught it; the bridge would have dropped the key and returned success.

## F. SporeCloud (ROT_SPORECLOUD_PORT_1) — PASS (flesh half); mech exemption see below

Route: `jawa/game_condition {action:"start", condition:"RUT_SporeCloud", permanent:true}` →
read back `activeConditions` containing `RUT_SporeCloud permanent ticksLeft -1`. Window
20,699 ticks (= 6 × the def's `damageIntervalTicks` 3451).

`RUT_SporesBuildup` severity at the end of the window, by roof state at measurement:

| pawns | roof | `RUT_SporesBuildup` |
|---|---|---|
| Human36838 / 36841 / 36856 / 36859 / 36862 / 36868 | none | **0.0918 – 0.1148** |
| Human36847 / 36850 / 36853 (sealed R6) | RoofConstructed | **absent (null)** |
| Human36865 / 36871 (roof appeared mid-window) | RoofConstructed | 0.0228 — one interval's worth, then it stopped |

0.1148 = exactly 5 × the def's `hediffSeverityPerInterval` 0.023; 0.0918 = 4 ×; 0.0228 = 1 ×.
**Unroofed gain, roofed do not** — PASS, and the partial cases land on exact multiples of the
configured step, which is the strongest form of the claim.

🔑 **This also settles battery A's unreadable `conditionClass`**: the def's declared class is
`RimMandrake.EnvironmentalHazards.GameCondition_EnvironmentalWeather`, and the observed
behaviour — a per-`damageIntervalTicks` `hediffToApply` step applied only to unroofed flesh —
is that class's `GameConditionTick`/`DoPawnEffects` and nothing else's. Vanilla
`GameCondition` would have done nothing at all. **PASS by behaviour.**

### Mechanoid exemption — PASS (checked, it was easy)
3 × `Mech_Scyther` and 3 × `Muffalo` spawned faction `none` at the far map corner, all six
unroofed, 9,523 ticks (2.8 × the interval):

| pawns | `isFlesh` | `RUT_SporesBuildup` | `RUT_SheenCoating` |
|---|---|---|---|
| Mech_Scyther ×3 | false | **absent** | **absent** |
| Muffalo ×3 | true | **0.03747** | 0.08192 |

`affects: Flesh` → `HazardTargeting.Affects` excludes mechanoids and includes animals, exactly
as the def's header claims. The three scythers were destroyed (`jawa/damage Bomb`) afterwards
so nothing hostile was left running on the map.

## G. Pale tree (ROT_PALE_TREE_1) — 🔴 **FAIL — `RUT_PaleTree`'s comps do not initialize**

Royalty confirmed active live: `jawa/pawn_psychic action=get` → `royaltyActive: true`, and
`RoyalTitleDef/Knight`, `HediffDef/PsychicAmplifier`, `MeditationFocusDef/Natural`,
`ThingDef/MeditationSpot` (modName **Royalty**) all resolve.

### The defect, with a same-session vanilla control
Spawning `RUT_PaleTree` logs, every single time:

```
Could not instantiate or initialize a ThingComp: System.MissingMethodException:
Default constructor not found for type Verse.ThingComp
  at Verse.ThingWithComps.InitializeComps ()
```

Attribution was measured, not guessed — nine defs were spawned one at a time and the
`Player.log` occurrence count was read after each:

| spawned | new error? |
|---|---|
| `RUT_GrownFurnace`, `RUT_BrewingVessel`, `RUT_AgelessCap`, `RUT_RegenerantVeil`, `RUT_FalseFruit`, `RUT_Glimmerslime`, `RUT_Tea_AgeReversal`, `RUT_Symbiont_Quickflesh` | no |
| **`RUT_PaleTree`** | **YES, every time** |
| vanilla `Plant_TreeAnima` (×3, same session, same map) | **no** |
| `RUT_PaleMoss`, vanilla `Plant_GrassAnima` | no |

**The consequence is visible in the game's own inspect pane** — `jawa/inspect_string` on four
separate mature instances of each, side by side:

| def | inspect lines |
|---|---|
| vanilla `Plant_TreeAnima` (3 instances) | `Ready to harvest.` · **`Total meditation today: 0h (progress multiplier 100%)`** · **`Anima grass: 0 (progress 0%)`** |
| `RUT_PaleTree` (4 instances) | `Ready to harvest.` — **and nothing else** |

Those two missing lines are `CompSpawnSubplant` and `CompPsylinkable`. **The pale tree has no
working meditation/subplant/psylink comps at runtime, so it cannot ever grow `RUT_PaleMoss`
and cannot ever grant a psylink.** This matches the observation: across ~45,000 ticks with a
psylink-1 colonist meditating (psyfocus rose 0 → 0.111 → 0.140, so meditation really happened),
**zero `RUT_PaleMoss` were ever created.**

### What is NOT the cause (each checked, each refuted)
- **Not the def data.** `jawa/get_defs fields=comps deep=true` on `RUT_PaleTree` and
  `Plant_TreeAnima` side by side returns **the same nine CompProperties classes in the same
  order with the same field keys** — `MeditationFocus, Glower, SpawnSubplant, Psylinkable,
  GiveThoughtToAllMapPawnsOnDestroy, PlaySoundOnDestroy, SelfhealHitpoints,
  ToggleDrawAffectedMeditationFoci, PlantPreventCutting`.
- **Not `maxRadius 0.0` / `subplantSpawnDays 0.0`** on `CompProperties_SpawnSubplant` — I
  suspected these; **vanilla `Plant_TreeAnima` carries the identical zeros**, measured in the
  same call. Refuted.
- **Not `RotPaleTree_WildSpawn.xml`** — that patch only appends a `wildPlants` entry.

🔑 **The one structural difference found**: `CompProperties_MeditationFocus.offsets` is
**`[]` on `RUT_PaleTree`** and a populated list (`radius 27.9` + curve, i.e.
`FocusStrengthOffset_ArtificialBuildings`) on vanilla. The def's own header says the
`FocusStrengthOffset_BuildingDefs` block was dropped on purpose. That is the prime suspect
and the place to start — **a code/def fix, owed to whoever owns ROT_PALE_TREE_1.**
⚠️ RimWorld's `InitializeComps` catch is around the loop, so one bad comp can kill every comp
in the list, which is consistent with all three comps being absent.

### What DOES pass
- `requiredSubplantCountPerPsylinkLevel` is **`[20, 20]` — two entries — live**, against
  vanilla's `[20,20,20,20,20,20]` in the same call. The **level-2 cap is correct in the data**
  (vanilla's `CompPsylinkable` derives its max level from this list's length). It is,
  however, **inert until the comp instantiates**, so the cap is proven in data, not in play.

### Also measured en route (useful, vanilla, not a defect)
`jawa/stat_explain` on the meditating colonist: `MeditationPlantGrowthOffset` reads
**−20% "Nearby artificial structures"** beside the colony and **0%** out in the clear. Any
future anima-style subplant test must be run well away from buildings.

### Route limitation worth recording
`jawa/ordered_job` exposes only `targetA`/`targetB`; vanilla's `Meditate` job carries the
meditation **focus in targetC**, so **a focused meditation cannot be ordered from this
bridge at all**. The autonomous path does not substitute — a colonist abandons a remote
meditation spot for its needs within a few thousand ticks.

## H. Guardian groves (ROT_GUARDIAN_GROVES_1) — PASS ×2, alarm BLOCKED(no carrier)

Three plants spawned on cleared Soil and grown with `Actions\T: Grow plant to maturity`
(⚠️ that debug action needs `x`/`z`; a bare `jawa/list_things` id is rejected — the
`rimworld/` tools want `Thing_<id>`), then harvested by `jawa/ordered_job jobDef=Harvest`
with `targetAId` = the plant.

### H1 `RUT_AgelessCap` — choking-spore gas, and it hurts the harvester — PASS
The gas is **continuous**, not harvest-triggered: `CompActiveGasEmitter` bursts every
`tickIntervalTicks` 400 within `radius` 5.9. After ~4 s of Ultrafast,
`jawa/list_things RUT_ChokingSpores` → **65 gas things**, clustered on (96–103, 132–139)
around the cap at (100,135). The harvester then walked into it:

| pawn | job | hediff delta |
|---|---|---|
| Human125 | harvested `RUT_AgelessCap` | **+`ToxicBuildup` 0.0399**, +`Scratch` ×2, +`BloodLoss` |
| Human128 | harvested `RUT_FalseFruit` | no ToxicBuildup |
| Human122 | harvested `RUT_RegenerantVeil` | no ToxicBuildup |

Only the Ageless Cap harvester took it, in the same window on the same map. 0.0399 /
`severityPerDamageDealt` 0.015 ≈ 2.7 damage — consistent with the `RUT_ToxicSpores` DamageDef's
`additionalHediffs → ToxicBuildup` at `damageAmount` 2 per hit. **Gas emitted, harvester hurt.**

### H2 `RUT_FalseFruit` mimic ⇒ `RUT_MatGrip` — PASS, 3 of 3
First attempt read a **false negative** because `RUT_MatGrip` carries
`HediffCompProperties_Disappears 360~600 ticks` and my sample was 4,258 ticks later. Re-run with
3 fresh fruits, 3 harvesters, and a ~123-tick sampling loop:

| pawn | `RUT_MatGrip` |
|---|---|
| Human122 | **0.5**, seen at samples 9–11, gone by 12 |
| Human128 | **0.5**, from sample 11 |
| Human125 | **0.5**, from sample 13 |

Each appeared on the tick the pawn collected its fruit (the fruit count fell 3→2→1→0 in step)
and expired within 2–4 samples ≈ 250–500 ticks, inside the def's 360–600 window. The hediff
sets `Moving setMax 0.05` — the immobilize. `RUT_Plant_FalseFruit.PlantCollected` fires.

### H3 `RUT_RegenerantVeil` alarm — **BLOCKED (no carrier)**, harvest itself is clean
- Harvest completed and **produced its yield** (`RUT_LiveIngredient_RegenerantVeil` ×1 on the
  ground). Spawning and harvesting it logged **nothing new** — the attribution sweep above
  spawned `RUT_RegenerantVeil` and the `Player.log` error count did not move.
- **Nothing can respond**: `grep -r RM_AlarmResponderExtension --include=*.xml src/` returns
  **0 hits**, as does `CompProperties_WoundLink` / `CompProperties_KinMending` /
  `RM_WoundLinkExtension`. The classes exist in `RimMandrake.CreatureBehaviors`; no def carries
  them. **BLOCKED(no carrier) — awaits `BIOME_FAUNA_ASSIGNMENT_SITTING_1`.**

## I. Live preparations (ROT_LIVE_PREPARATIONS_1) — PASS (trade seam UNMEASURED, as directed)

### I1 `CompTemperatureRuinable` ruin path below 8 °C — PASS
A sealed 25-cell room was built at (60,100,7,7) and forced cold with
`jawa/room_heat mode=set value=-15` (read back: `Room 64 temperature 19.0 -> -15.0 °C`,
`jawa/cell_temperature` 63,103 = −15.0). A `RUT_Tea_Bioregeneration` in the warm control room
R1 (18.5 °C) is the control.

| sample | cold-room temp | cold `RUT_Tea_AgeReversal` + `RUT_Symbiont_Mycoid` | warm control |
|---|---|---|---|
| 0 | 6.7 | **`Freezing: 0.18%`** · Expires in 2.4 days | Expires in 2.4 days |
| 1 | 7.5 | **`Freezing: 0.35%`** | (no Freezing line) |
| 2 | 8.8 | *(line vanishes above 8 °C)* | — |
| 3–9 | 7.8 → −14.0 | **0.62% → 0.83%, monotonically rising** | (never any Freezing line) |

The `minSafeTemperature` 8.0 cliff is exact: the line appears below 8 °C and disappears the
moment the room drifts above it. The warm control never shows it. **PASS.**

### I2 `CompLifespan` ≈ 2.5 days — PASS (read off the live defs and seen in-game)
`jawa/get_defs deep=true` over all seven live preps — three teas + four symbionts — returns
`lifespanTicks` **150000** and `minSafeTemperature` **8.0** for **every one**.
150000 / 60000 = **2.5 in-game days**, and the game printed `Expires in: 2.4 days` on a
freshly spawned one. Both `modExtensions` resolve live on all seven:
`RM_LivePrepExtension {preparationFamily: "RotLivePrep"}` and
`RM_TreasureMarkerExtension {treasureTag: "RotTreasure"}`.

### I3 Symbionts — both sides of every bargain — PASS
Ingested through `jawa/ordered_job jobDef=Ingest`; hediffs read back on the pawn, stage data
read live off the HediffDef with `deep=true`.

| symbiont | applied on the pawn | benefit (live stage) | cost (live stage) |
|---|---|---|---|
| `RUT_Symbiont_Quickflesh` → Human36859 | `RUT_Sym_Quickflesh` **1.0** | `naturalHealingFactor` **3.0** | `hungerRateFactor` **2.2** |
| `RUT_Symbiont_Nightwake` → Human36862 | `RUT_Sym_Nightwake` **1.0** | `restFallFactor` **0.0** | `statOffsets: MentalBreakThreshold +0.12` |
| `RUT_Symbiont_Sheenblood` → Human36844 | **`RUT_SheenSymbiosis` 1.0 AND `RUT_Sym_Sheenblood`** | the Sheen immunity proven in battery E | sun-scald comp live: `severityPerDayInSunlight 1.0 / severityPerDayShaded −2.0`, and its **severity had already climbed 0.01 → 0.068 in sunlight** by the read |

Both of Sheenblood's `IngestionOutcomeDoer_GiveHediff` entries fired. The scald severity moving
on its own is the live proof of `RM_HediffComp_SunlightScald`, not just its presence.
(`RUT_Sym_Mycoid` and `RUT_Bioregenerating` also read live: the latter `naturalHealingFactor 2.0`.)

### I4 Age-reversal tea — PASS on every clause
| pawn | before | after 1st cup | `RUT_AgeReversalSated` | after 2nd cup |
|---|---|---|---|---|
| Human36838 | 53 | **48** (−5) | **1.0** | (pawn died before cup 2) |
| Human42056 | 31 | **26** (−5) | **1.0** | **26 — unchanged** |
| Human42059 | 22 | **17** (−5) | **1.0** | **17 — unchanged** |
| Human36844 | 14 | **13** (−1, **clamped**) | — | — |

- **−5 biological years on the first cup**: 3 of 3 clean subjects, exactly −5.
- **`RUT_AgeReversalSated` applied** (live comp: `disappearsAfterTicks 3,600,000` = 60 days).
- **A second cup while sated does nothing**: two pawns, ages unchanged across 2,000 ticks, and
  the tea was consumed.
- **The adult floor binds**: Human36844 at 14 fell only to **13**, not 9 —
  `Math.Max(adultFloor, before − reversal)` with `AdultMinAge`. ⚠️ Note for the record: that
  floor is RimWorld's humanlike **adult life-stage minimum, 13**, not 18 — so a 22-year-old
  legitimately lands on 17.

### I5 Sell-conscience — join exists, trade seam **UNMEASURED** (not forced, as directed)
- `ThoughtDef/RUT_SoldRotTreasureMemory` resolves live (battery A).
- The marker side of the join resolves live on all seven preps:
  `RM_TreasureMarkerExtension {treasureTag: "RotTreasure"}` (and `RM_TreasureConscienceDef` /
  `RM_Patch_TreasureSaleConscience` ship in the assembly).
- **UNMEASURED**: no trader was summoned, so the actual sale → thought firing was not observed.

## J. WoundLink / KinMending (ROT_HEALTH_SHARING_1) — **BLOCKED (no carrier)**

As anticipated: content-blind, nothing carries them. No carrier was fabricated.

Measured over the whole repo's XML (`grep -rn … --include="*.xml" src/`): **0 hits** for every
one of `CompProperties_WoundLink`, `CompProperties_KinMending`, `RM_WoundLinkExtension`,
`RM_AlarmResponderExtension`. All four types exist and compile in
`src/RimMandrake/CreatureBehaviors/Source/` (`CompProperties_WoundLink.cs`,
`CompProperties_KinMending.cs`, `RM_WoundLinkExtension.cs`, `RM_AlarmResponderExtension.cs`).
The only mention anywhere in a def file is a **comment** in
`src/RimUtinni/RotSporeKit/Defs/ThingDefs_Races/RUT_Emberscythe.xml:37`
("RM_HediffComp_KinMending needs 2+ tagged kin nearby") — a comment, not a carrier.

**BLOCKED(no carrier — awaits `BIOME_FAUNA_ASSIGNMENT_SITTING_1`).** The same gap blocks
battery H's `RUT_RegenerantVeil` alarm responder.

## Summary

| battery | verdict | key number |
|---|---|---|
| **A** Def probes | **PASS** | 34/34 defs resolved live; `RUT_SheenExposureLock` present ⇒ **ENVHAZARDS_NEVER_ACTIVATED_1 gates now pass**; `requiredSubplantCountPerPsylinkLevel` = **[20, 20]** |
| **B** Quicktest colony | **PASS** | home map, tile 67860 retagged → `mapBiome: RUT_TheRot`; 6 sealed 25-cell test rooms, 12 positioned pawns |
| **C1** AcceleratedRot | **PASS** | outdoor meat **destroyed by tick 16,191 (0.27 day)**; roofed control read `spoils in 1.9 days` at the same instant |
| **C2** LivingProduce heat | **PASS** | 200 units → **+70.3 °C** over an identical empty room (peak 83.4 vs 13.2). Campfire equivalence is an arithmetic identity (0.35 energy/tick both); **live campfire control UNMEASURED** — no fuel route from the bridge |
| **D1** WarmMat | **PASS** | mat room vs stone twin **+7.8 … +8.8 °C**; 21 °C cap confirmed (contributed 0 once outdoor hit 24.95) |
| **D2** GrownFurnace | **PASS** | **+19.0 °C** over control, no fuel bar, sustained 85k ticks |
| **E** Sheen exposure | **PASS** (all four) | bare **0.6687/day**, helmet **0.16719/day** = **4.000× slower**, symbiont **0.000**, roofed never seeded. ⇒ saturation in **1.495 days**; top stage seeded `RUT_SporeFlesh` on **2 of 3** in 0.345 day |
| **F** SporeCloud | **PASS** | unroofed **0.0918–0.1148** = exact 4×/5× multiples of `hediffSeverityPerInterval` 0.023; roofed **absent**; **mechanoids absent, muffalo 0.03747** |
| **G** Pale tree | 🔴 **FAIL** | `RUT_PaleTree` throws `Could not instantiate or initialize a ThingComp` on **every** spawn (vanilla `Plant_TreeAnima` ×3 in the same session: clean). Its inspect pane is missing **`Anima grass:`** and **`Total meditation today:`** ⇒ no working SpawnSubplant/Psylinkable; **0 `RUT_PaleMoss` after ~45k ticks of real meditation**. Cap [20,20] correct in data but inert |
| **H1** AgelessCap gas | **PASS** | **65** `RUT_ChokingSpores` around the plant; only its harvester gained **`ToxicBuildup` 0.0399** |
| **H2** FalseFruit trap | **PASS** | `RUT_MatGrip` **0.5 on 3/3** harvesters, expiring in ~250–500 ticks (def: 360–600) |
| **H3** RegenerantVeil alarm | **BLOCKED** | harvest clean, yield produced, no new log line; **0 XML carriers of `RM_AlarmResponderExtension`** |
| **I** Live preparations | **PASS** | `Freezing: 0.18 → 0.83%` below 8 °C, absent above; `lifespanTicks` **150000 = 2.5 d** on all 7; Quickflesh **heal ×3 / hunger ×2.2**, Nightwake **restFall ×0 / breakThreshold +0.12**, Sheenblood **`RUT_SheenSymbiosis` + scald 0.01→0.068 in sun**; tea **−5 yr ×3 subjects**, sated blocks the 2nd cup (26→26, 17→17), adult floor clamps 14→**13**. Trade seam **UNMEASURED** |
| **J** WoundLink/KinMending | **BLOCKED** | **0** XML carriers of all four types; only a comment in `RUT_Emberscythe.xml:37` |

### The one thing to act on
🔴 **`RUT_PaleTree` is inert in play** (battery G). Reproducible, attributed by a same-session
vanilla control, and diagnosed down to one structural difference:
`CompProperties_MeditationFocus.offsets` is **`[]`** on ours and populated on vanilla
`Plant_TreeAnima`. RimWorld's `InitializeComps` catch wraps the whole loop, so one bad comp
takes every comp with it — which matches all three comps being missing. Owed to
ROT_PALE_TREE_1's owner as a code/def fix.

### Traps found that cost time here, for the next driver
- `jawa/pawn_severity_adjust` takes **`offset`**, not `severity`; `jawa/destroy_batch` takes
  **`rects`+`categories`**, not `thingIds`; `jawa/stat_explain` takes **`subject`+`stats`**.
  The client's param checker caught all three — the bridge would have dropped them and
  returned success.
- `jawa/inspect_string` returns the text under **`inspect`** (a list). `jawa/list_things`'s
  `rot` field is **rotation**, not rot progress, and its defName key is **`def`**.
- `jawa/ordered_job` / `jawa/order_pawn` with a `waitTicks` **hang on a paused game** and blow
  the client's 30 s timeout, desyncing the socket. Set a speed first, keep `waitTicks` small,
  and open a fresh connection after any timeout.
- **Drafting holds a pawn** across 8,600 Ultrafast ticks; an undrafted one wanders the map in
  minutes and silently invalidates a roofed/unroofed sample. Re-read roof state every sample.
- **RimWorld re-roofed deliberately unroofed rooms** during long runs even with every colonist
  drafted. `jawa/set_roof_batch None` is not durable.
- `jawa/spawn_batch` reported `Placed 0 … 1 failed` for `RUT_PaleTree` while the thing **was**
  created — always read back with `jawa/list_things`.
- `Actions\T: Grow plant to maturity` needs `x`/`z`; a bare companion thing id is refused
  ("Could not find current-map thing id"), the `rimworld/` tools want `Thing_<id>`.
- `jawa/drain_log` does **not** drain — it reads a deduped ring buffer. To attribute an error
  to one action, count occurrences in `Player.log` before and after.

### Map state left behind
Game **RUNNING, map PAUSED** at ticks ~207,246, `Map_0`, biome `RUT_TheRot`, weather locked to
`RUT_SheenFall`. `RUT_SporeCloud` and `RUT_SheenExposureLock` were **ended** after F so they
would stop killing test pawns. Nothing was saved; no existing save touched. Test structures,
plants and pawns are all still on the map. 2 test colonists died during the exposure runs
(`RUT_SporeFlesh` + malnutrition while drafted) — expected on a scratch map.
