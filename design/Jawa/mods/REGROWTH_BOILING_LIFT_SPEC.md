# REGROWTH_BOILING_LIFT_SPEC.md — the boiling water and the boiling rain, kept; the mod, dropped

DECIDE owns this. **Owner's ruling, 2026-08-15.** `RG_BoilingForest` is CUT
(`observed/inventory/decisions_biomes.json`). The owner wants the good parts of
`ReGrowth: Boiling` (`regrowth.botr.boilingforest`) anyway — *"Boiling Rain,
boiling surfacewater, their effects... that's pretty cool."*

This document says what those parts actually **do**, rules how we get them, and
names the exact biomes that receive them.

Companion documents: `design/Jawa/worldbuilding/hydrology_and_fire_ecology.md`
(R-H0/H1/H4/H7 are the reason any of this matters),
`design/Jawa/worldbuilding/tidally_locked_world.md` (biome placement).

⚠️ **This is a private playthrough. Nothing here ships publicly, so licensing is
not a factor in any ruling below.** (Recorded once for the file: the donor is
CC BY-NC-ND 4.0, patches and translations permitted, re-upload not.)

---

## R-B0 · What was measured, and where

Everything below was read off the mod's own XML at
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3565675704` and
off the **live, fully-patched** def dump at
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs`.
The live dump is the authority here, because the mechanics are **not in the def
files** — they arrive by patch (R-B2).

---

## 🔴 R-B1 · The boiling water terrain does NOTHING. It is a cyan glow.

This is the single most important finding in the document and it changes the
recommendation.

The six `BoilingWater*` TerrainDefs inherit `WaterShallowBase` / `WaterDeepBase` /
`WaterChestDeepBase` and, in the resolved live defs, differ from vanilla water in
**exactly three ways**:

| | boiling water | vanilla water |
|---|---|---|
| `glowColor` | `(2,154,229)` — cyan | `(0,0,0,0)` |
| `glowRadius` | `2` | `0` |
| `label` | "**spectral** shallow water" | "shallow water" |

**Everything else is identical.** Measured, not assumed:

| field | `BoilingWaterShallow` | `WaterShallow` |
|---|---|---|
| `pathCost` | 30 | 30 |
| `extinguishesFire` | true | true |
| `traversedThought` | `SoakingWet` | `SoakingWet` |
| `burnDamage` / `burnIntervalTicks` | **0 / 0** | 0 / 0 |
| `texturePath` | `Terrain/Surfaces/WaterShallowRamp` | `Terrain/Surfaces/WaterShallowRamp` |

⇒ **No hediff. No damage. No heat. No pathing penalty. The same vanilla texture.**
A pawn wading "boiling" water gets the ordinary *soaking wet* thought. The word
"boiling" appears nowhere in the def's behaviour; the mod's own label for it is
**"spectral"**, which is honest — it was authored as a *Owl House* colour effect,
not a hazard.

### 🔴 And in OUR stack it is strictly WORSE than vanilla water

Two silent regressions, because the mods that improve vanilla water patch the
**vanilla defNames** and never reach the copies:

- **It is missing the `dbh_water` tag.** `dubwise.dubsbadhygiene.thirst` and
  `.lite` are both ACTIVE. A river of boiling water is **not a Dubs Bad Hygiene
  water source** — pawns cannot drink from it or draw from it.
- **It is missing `Biomes_PlantControl`** (Biomes! Core, ACTIVE), which vanilla
  water carries. Water plants from the Biomes! family will not grow on it.

⇒ **Painting our rivers with this def as-is would quietly break drinking water on
a world whose entire design is that water is currency.** That alone disqualifies
route (a).

### ⭐ The levers that WOULD make hot water hot are vanilla, and Odyssey uses them

`TerrainDef` already carries `burnDamage` + `burnIntervalTicks`, and Odyssey ships
working reference values:

| terrain | `burnDamage` | `burnIntervalTicks` | `pathCost` | `avoidWander` | `traversedThought` |
|---|---|---|---|---|---|
| `LavaShallow` (Odyssey) | **3** | **120** | 300 | true | — |
| `HotSpring` (Odyssey) | 0 | 0 | 100 | true | **`HotSpring`** |
| `SpringFlood` (Odyssey) | 0 | 0 | 100 | true | `HotSpring` |
| `BoilingWaterShallow` (donor) | 0 | 0 | 30 | false | `SoakingWet` |

⇒ **Near-boiling meltwater sits between `HotSpring` and `LavaShallow`, and both
ends of that bracket are vanilla fields.** We do not need C# and we do not need
the donor.

---

## R-B2 · The boiling weather is real, is not ReGrowth's engineering, and is TINY

The four `RG_Boiling*` WeatherDefs *do* carry a mechanical payload — but it is not
in `Weathers-Boiling.xml`. It is added at load time by
`1.6/Patches/_ModSettings/Toggleable-Patches.xml`, and the class that carries it is
**`VEF.Weathers.WeatherEffectsExtension` — Vanilla Expanded Framework**
(`vanillaexpanded.vfecore`, ACTIVE), not a ReGrowth class.

Confirmed present in the **live resolved def**, so the patch does apply in our
current stack (the `ModSettingsFramework.PatchOperationModOption` operation
resolves because `0ModSettingsFramework.dll` ships inside **ReGrowth: Core**).

| weather | `rainRate` | burn damage | interval | % pawns hit | `killsPlants` | `isBad` |
|---|---|---|---|---|---|---|
| `RG_BoilingDrizzle` | 0.5 | 0.1 – 0.3 | 400–700 t | 10 % | false | false |
| `RG_BoilingRain` | 1 | 0.1 – 0.5 | 300–600 t | 10 % | false | false |
| `RG_BoilingFoggyRain` | 1 | 0.1 – 0.5 | 300–600 t | 10 % | false | true |
| `RG_BoilingRainyThunderstorm` | **1** | 0.3 – 0.9 | 200–500 t | 10 % | false | true |

All four: `worksOnNonFleshPawns` false, `worksIndoors` false, `causesRotting`
false, `damageToApply` `Burn`.

### ⚠️ The burn is flavour, not a hazard — say it plainly

At the rain's own numbers a given pawn takes roughly **4 points of burn per full
game day** standing outdoors in it. That is a scratch. **The burn is a texture
effect with a damage number attached.** Anyone reading the def's description
("makes people and animals suffer from burn damage") and expecting a threat will
be disappointed, and anyone balancing around it will balance around nothing.

### 🔴 The mechanically LOUD field is `rainRate`, and it points the wrong way

`rainRate` ≥ 0.5 means the vanilla fire system treats this as rain: **it
extinguishes fires and suppresses spread.** The donor says so itself —
`RG_BoilingRainyThunderstorm`'s description is *"the lightning will start fires,
but the boiling rain will put it out."*

⇒ **That is the exact opposite of R-H4.** The Pyrelands run on dry thunderstorms —
lightning with no water behind it, feeding a standing burn that migrates forever.
A wet thunderstorm dropped into `ZBiome_Grasslands` would *end the fire ecology*.

**Vanilla already ships what R-H4 wants: `DryThunderstorm`, `rainRate` 0** — and
`ZBiome_Grasslands` already carries it at commonality 2. The Pyrelands need that
number raised, not a new weather.

### Other fields that must be rewritten, not copied

- **`commonalityRainfallFactor` bottoms out at `(0, 0)`** and only reaches 1 at
  rainfall 1300. Sekkoth's desert and volcanic tiles are nowhere near 1300, so
  **these weathers would essentially never roll on our planet** if referenced
  as-shipped. This is not a tuning nicety; it is the difference between the
  feature existing and not.
- `temperatureRange` `0~100` — fine for peaks, wrong for nothing else we use.
- `RG_BoilingRain` has `isBad: false` and `favorability: Neutral`, so it does not
  read as weather worth sheltering from.

---

## 🔴 R-B3 · THE RULING: author our own. Drop the mod. — route (b)

**DECIDE rules route (b): author six TerrainDefs and three WeatherDefs in
`src/Jawa/Jawa_Patches`, and remove `regrowth.botr.boilingforest` from the mod
list.** Not hedged. Five reasons, in order of weight.

**1. Every C# class the effects need survives the drop.** This is the fact that
settles it.

| class / def we need | ships in | still active after the drop? |
|---|---|---|
| `VEF.Weathers.WeatherEffectsExtension` (the burn) | `vanillaexpanded.vfecore` | ✅ yes |
| `VEF.Weathers.WeatherOverlay_Effects` | `vanillaexpanded.vfecore` | ✅ yes |
| `ReGrowthCore.WeatherExtension_FogMotes` (steam splashes) | `regrowth.botr.core` | ✅ yes |
| `ReGrowthCore.WeatherOverlay_FogMotes` | `regrowth.botr.core` | ✅ yes |
| `RG_HotSpringSand` (the beach terrain) | `regrowth.botr.core` | ✅ yes |
| `burnDamage` / `burnIntervalTicks` / `traversedThought` | Core + Odyssey | ✅ yes |

**`regrowth.botr.core` is ACTIVE and stays active regardless** — `Biomes! Polluted
Lands` and `Comigo's Greater Swamps (Continued)` both load after it, and neither
is being removed. So dropping ReGrowth: **Boiling** costs us **no class, no
texture and no terrain we want**. There is nothing here we cannot rebuild.

**2. There is almost nothing to author.** The terrains are six ten-line
`ParentName` inherits whose entire content is a label and a `glowColor`, over
**vanilla textures**. The weathers are ordinary WeatherDefs plus one modExtension.
What we are lifting is ReGrowth's *idea*, not its engineering — the engineering is
VEF's and Ludeon's, and we already have both.

**3. Route (a) drags 41 defs to reach 10, and two of them are actively harmful.**
Referencing the donor means loading the cut `RG_BoilingForest` BiomeDef, **14
plants** (`RG_Plant_TreeBoilingBirch`, `RG_Plant_BoilingTreePine`,
`RG_Plant_SpikedBoilingTreePine` — the coniferous and deciduous trees the owner
does not want — plus grasses, moss, bush, brambles, berry, cushion, two flowers,
edaku), **3 of which are sowable** (`RG_Plant_Edaku`, `RG_Plant_LuzincFlower`,
`RG_Plant_AmitisFlower`) and therefore appear in the **growing-zone selector**
whether the biome generates or not. Plus `RG_RawBoilberries`,
`RG_Filth_LeavesBoilingTree`, and a mod-settings category. **That is ~17 new
Cherry Picker entries on top of 1308**, bought purely to reach six terrain defs
that do nothing and three weathers whose numbers we would have to patch anyway.

**4. The values are wrong for our planet in three separate places** (R-B1's
missing `dbh_water`, R-B2's `commonalityRainfallFactor`, R-B2's zero
`burnDamage`). Route (a) means stacking three corrective `PatchOperation`s onto
defs we do not own — more XML than authoring the defs outright, and each patch is
a silent-failure surface (`PatchOperationConditional` returns true on no match).

**5. A Steam workshop update can change any of the ten defs mid-campaign.** The
donor was last versioned `1.64566.9384.225224`. Our own defs cannot move under us.

⚠️ **The one honest cost of (b):** we give up the donor's authored *look* — but
the look is a cyan glow over a vanilla texture, and we are copying the number
`(2,154,229)` either way.

---

## R-B4 · What we author, and where each piece goes on Sekkoth

Host mod: **`src/Jawa/Jawa_Patches`** (`mandrake.jawa.patches`) — it already has
`Defs/` and `Patches/`, and it loads at the very END of `ModsConfig.xml`, after
every biome mod. New defs in `Defs/TerrainDefs/` and `Defs/WeatherDefs/`;
biome edits in `Patches/`.

Naming: **`Jawa_` prefix throughout.** No `RG_`, no bare `BoilingWater*` — a bare
name would collide with the donor if it is ever re-enabled.

### 4a · The terrains — R-H1's flash-flood rivers and brief wetlands

Six defs, mirroring the donor's shape because RimWorld's biome override fields
require all six slots:

| new def | inherits | replaces |
|---|---|---|
| `Jawa_ScaldWaterShallow` | `WaterShallowBase` | `WaterShallow` |
| `Jawa_ScaldWaterDeep` | `WaterDeepBase` | `WaterDeep` |
| `Jawa_ScaldWaterMovingShallow` | `WaterShallowBase` | `WaterMovingShallow` |
| `Jawa_ScaldWaterMovingChestDeep` | `WaterChestDeepBase` | `WaterMovingChestDeep` |
| `Jawa_ScaldWaterOceanShallow` | `WaterShallowBase` | `WaterOceanShallow` |
| `Jawa_ScaldWaterOceanDeep` | `WaterDeepBase` | `WaterOceanDeep` |

Values, all set deliberately rather than inherited from the donor:

- `glowColor (2,154,229)`, `glowRadius 2` — the donor's cyan, kept. It is the one
  thing worth taking verbatim.
- 🔴 **`burnDamage 1`, `burnIntervalTicks 300`** on the shallow and moving defs;
  **`burnDamage 2`, `burnIntervalTicks 240`** on the deep and chest-deep. Bracketed
  by Odyssey: `HotSpring` is 0/0 and `LavaShallow` is 3/120. This is the entire
  point of the lift — *near-boiling* has to mean something.
- `traversedThought` **`HotSpring`** (Odyssey's, already loaded) rather than
  `SoakingWet`.
- `avoidWander true` — pawns should not idle in it.
- 🔴 **Carry the `dbh_water` tag** on every one of them (R-B1). This water is still
  the water people drink; that is R-H1's whole economy.
- Keep `extinguishesFire true` — it is water.
- `waterBodyType Saltwater` + `Ocean` tag on the two ocean defs, per R-H2's
  hypersaline seas.
- `pathCost` unchanged from the vanilla parents. The hazard is the burn, not a
  wading penalty.

⚠️ **`dbh_water` must be verified against Dubs Bad Hygiene's own reader before it
is relied on** — it is a tag string, and a tag that is merely *present* proves
nothing about which mod consumes it.

### 4b · Where the scald water goes — the high and volcanic tier only

🔴 **Ruling: boiling water is an ALTITUDE-and-VOLCANISM fact, not a river fact.**
R-H1 says the meltwater comes off the peaks steaming; R-H7 says it is potable
again by the time it reaches the lowland desert rivers. So the lowland rivers of
`Desert`, `ExtremeDesert`, `ZBiome_Badlands` and `ZBiome_Grasslands` stay
ordinary water. **Keeping it rare is what makes it read.**

| surviving biome | gets | why |
|---|---|---|
| `IronScruff_PrimordialGeysers` | all six | R-H0's geothermal. Boiling water here is not a conceit, it is what a geyser field *is*. The strongest fit in the roster |
| `Volcano` (Advanced Biomes) | all six | R-H0. Currently `riverbankTerrain: Riverbank`, ordinary water |
| `LavaField` (Odyssey) | all six | R-H0 |
| `AB_PyroclasticConflagration` | all six | R-H0. Currently inherits vanilla water defaults |
| `ZBiome_DesertOasis` | shallow + deep only; **moving stays vanilla** | R-H1 step 3 — the brief wetland where the flood lands. The *standing* pool is what steams; the through-river is already cooling |
| `COMIGO_GreaterSwamp_Tropical` | shallow + deep only | R-H1 step 3 — the brief jungle. Same reasoning |

🔴 **DO NOT touch `AB_OcularForest`'s water.** It already overrides all four slots
with `GU_RedWaterShallow` / `GU_RedWaterDeep` / `GU_RedWaterMovingShallow` /
`GU_RedWaterMovingChestDeep` (Alpha Biomes), which **is R-H7's red-flowing water,
verbatim, already in the game.** Overwriting it with scald water would delete the
best-fitting terrain we own to install a worse one. This is the single most likely
mistake in the whole job.

### 4c · The weathers — three, not four

| new def | modelled on | payload |
|---|---|---|
| `Jawa_ScaldDrizzle` | `RG_BoilingDrizzle` | `rainRate` 0.5, burn 0.3–0.8 / 400–700 t |
| `Jawa_ScaldRain` | `RG_BoilingRain` | `rainRate` 1, burn 0.5–1.5 / 300–600 t, **`isBad true`** |
| `Jawa_ScaldFog` | `RG_BoilingFoggyRain` | `rainRate` 1, burn 0.5–1.5 / 300–600 t, `isBad true` |

- Payload is one `VEF.Weathers.WeatherEffectsExtension` per def, plus
  `VEF.Weathers.WeatherOverlay_Effects` in `overlayClasses`, plus
  `ReGrowthCore.WeatherExtension_FogMotes` (`fogSize` 0.5, `fogSpawnRate` 0.5) and
  `ReGrowthCore.WeatherOverlay_FogMotes` for the steam splashes. All four classes
  are already loaded (R-B3 table). Guard both ReGrowth extensions with
  `MayRequire="regrowth.botr.core"`.
- 🔴 **`percentOfPawnsToDealDamage` raised from 0.10 to 0.35 and the damage range
  roughly tripled.** Per R-B2 the donor's numbers amount to ~4 damage per pawn per
  day; at these values it is ~30–40, which is a reason to go indoors without being
  a death sentence. **These numbers are DECIDE's proposal, not a ruling — they are
  the first thing to re-tune after they are seen in play.**
- 🔴 **`commonalityRainfallFactor` must be rewritten for a desert planet.** Anchor
  it near `(0, 1)` / `(500, 1)` rather than the donor's `(0, 0)` / `(1300, 1)`, or
  these weathers will never roll on any tile we own. **This is the field most
  likely to make the whole feature silently do nothing.**
- `isBad true` on all three (the donor has it false on drizzle and rain) so they
  read as weather to shelter from.

### 4d · Where the scald weather goes — the only two rain-canon places

R-H1: rain falls **only at the greatest altitudes**. R-H7: the ocular forests are
where that rain lands and pools. Nowhere else on Sekkoth may have it.

| surviving biome | `Jawa_ScaldDrizzle` | `Jawa_ScaldRain` | `Jawa_ScaldFog` | note |
|---|---|---|---|---|
| `AB_OcularForest` | 6 | **8** | 4 | 🔴 **The rain biome.** R-H7's near-perpetual high-valley rain. Currently `Rain` 1 / `RainyThunderstorm` 1 / `FoggyRain` 1 against `AB_RedFog` 17 — the vanilla rains get **removed** and replaced by these |
| `IronScruff_PrimordialGeysers` | 4 | 3 | 3 | The other high/geothermal tile. Currently carries `Rain` 2, `RainyThunderstorm` 1, `TorrentialRain` 0.5, `Blizzard` 1 — **all four removed** |
| `Volcano` | 2 | 2 | 1 | R-H0 peaks. `Rain` 2 and `RainyThunderstorm` 1 removed |
| **every other surviving biome** | — | — | — | 🔴 **nothing.** And their ordinary `Rain` / `RainyThunderstorm` / `FoggyRain` / `TorrentialRain` entries are a separate, already-owed job (R-H1's "strip rain from the weather tables") — do not do it inside this item |

### 4e · 🔴 The thunderstorm is WET. It is NOT lifted.

`RG_BoilingRainyThunderstorm` has `rainRate 1` and `isBad true`, and its own
description says the rain puts the fires out. **R-H4's Pyrelands need DRY
thunderstorms.** A wet one in `ZBiome_Grasslands` would extinguish the standing
burn that the entire savanna design rests on.

⇒ **We author no thunderstorm.** Vanilla `DryThunderstorm` (`rainRate 0`) already
exists and `ZBiome_Grasslands` already carries it at commonality **2**. Raising
that number is R-H4's job and belongs to the biome-weather item, not here. Do not
let a wet storm anywhere near the Pyrelands.

---

## R-B5 · What we do NOT lift, and why

| not lifted | count | why |
|---|---|---|
| **The plants** — `RG_Plant_TreeBoilingBirch`, `RG_Plant_BoilingTreePine`, `RG_Plant_SpikedBoilingTreePine`, `RG_Plant_BoilingGrass`, `RG_Plant_TallBoilingGrass`, `RG_Plant_PurpuraCushion`, `RG_Plant_BramblesBoiling`, `RG_Plant_BoilingMoss`, `RG_Plant_BoilingBush`, `RG_Plant_Boilberry`, `RG_Plant_LuzincFlower`, `RG_Plant_AmitisFlower`, `RG_Plant_Edaku`, `RG_Edaku` | 14 | **Owner does not want the coniferous and deciduous trees**, and the rest are an *Owl House* palette that belongs to a biome we cut. Three are sowable and would show up in the growing-zone selector regardless of worldgen |
| **The items** — `RG_RawBoilberries`, `RG_Filth_LeavesBoilingTree`, `RG_EggOwlbeastFertilized`, `RG_EggOwlbeastUnfertilized` | 4 | Downstream of the plants and the animal. The two eggs are already on the Cherry Picker list |
| **`RG_Owlbeast`** + corpse, meat, 4 sound defs | ~8 | **Already cut**, 2026-08-15 |
| **`RG_BoilingForest`** BiomeDef | 1 | **Cut by owner's ruling.** Nothing in this spec revives it |
| **`RG_HotSpringSand`** | 1 | Not lifted because it does not need to be — it lives in **ReGrowth: Core**, which stays active. Reference it by name for `lakeBeachTerrain` / `riverbankTerrain` on the geyser and volcano tiles |
| **`RG_BoilingSettings`** ModOptionCategoryDef + the two sliders | 3 | Mod-settings plumbing for a mod we are removing |
| **`RG_BoilingRainyThunderstorm`** | 1 | R-B4e — wet, and wrong for R-H4 |

---

## What BUILD owes

1. `src/Jawa/Jawa_Patches/Defs/TerrainDefs/Terrain_ScaldWater.xml` — the six
   `Jawa_ScaldWater*` defs at R-B4a's values.
2. `src/Jawa/Jawa_Patches/Defs/WeatherDefs/Weather_Scald.xml` — the three
   `Jawa_Scald*` weathers at R-B4c's values.
3. `src/Jawa/Jawa_Patches/Patches/Biomes_ScaldWater.xml` — the six-biome terrain
   assignment of R-B4b, using `waterShallowTerrain` / `waterDeepTerrain` /
   `waterMovingShallowTerrain` / `waterMovingChestDeepTerrain`. **`PatchOperationAdd`
   where the biome has no such field, `PatchOperationReplace` where it does** — four
   of the six already set some of these and the wrong operation will fail silently.
4. `src/Jawa/Jawa_Patches/Patches/Biomes_ScaldWeather.xml` — the three-biome
   weather table edits of R-B4d, each one **removing the vanilla rain entries it
   replaces** in the same operation.
5. Remove `regrowth.botr.boilingforest` from
   `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.
   🔴 **Do NOT remove `regrowth.botr.core`** — R-B3 depends on it, and so do
   Biomes! Polluted Lands and Comigo's Greater Swamps. Route it through
   `skills/rimworld-start-prep`; a mod-list edit while the game runs is thrown away.
6. Deploy `Jawa_Patches` with `src/RimMandrake/Utils/deploy_custom_mods.py`
   a bare dry run first. **The repo copy is not what the game loads.**

⚠️ **Nothing here touches `ZBiome_Grasslands`.** R-H4's dry-thunderstorm raise and
R-H1's global rain-stripping are separate, already-owed items. Do not fold them in.

## Verify — offline, no game load

- `python3 skills/rimworld-modding/scripts/validate_patch.py` over both new patch
  files with **BOTH `--live` and `--defs`**. Every xpath resolves to the exact
  expected count: **6 biomes × 4 terrain fields = 24 terrain hits**, and **3 biomes**
  for the weather file. Not 23, not 25. ⚠️ A patch that matches nothing logs nothing.
- The six terrain defs and three weather defs parse, and `grep` proves the string
  `dbh_water` appears **6 times** in `Terrain_ScaldWater.xml`.
- `grep -c "RG_"` in everything BUILD writes returns **0** except for the three
  permitted references: `regrowth.botr.core` in a `MayRequire`, and
  `RG_HotSpringSand` in the beach/riverbank fields.
- `grep` proves `rainRate` is **> 0** in all three new weathers and that the string
  `Thunderstorm` appears **0 times** in `Weather_Scald.xml`.
- After the next load: `python3 src/RimMandrake/Utils/refresh.py`, then confirm the
  nine `Jawa_Scald*` defs exist in the dump with the burn fields resolved, and that
  `AB_OcularForest.waterShallowTerrain` still reads **`GU_RedWaterShallow`**.

## Criteria

**A pawn who wades a river in the geyser fields or on a volcano gets burned and
knows why; a pawn caught in the open in an ocular-forest valley runs for cover;
and every other tile on the planet is as dry as R-H1 says it is.** The Pyrelands
still burn, because no wet storm was ever added to them. And
`regrowth.botr.boilingforest` is gone from the mod list without a single red error
at load.
