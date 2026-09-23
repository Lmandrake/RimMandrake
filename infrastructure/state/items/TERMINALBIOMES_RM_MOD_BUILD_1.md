# TERMINALBIOMES_RM_MOD_BUILD_1 — build RM_TheScald/RM_PropaneLake/RM_TwilightSea/RM_GreySea as its own RimMandrake mod

**FOUR biomes in ONE mod, each independently toggleable (owner ruling 7 Q1)**

Phase A row 11+24-26 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

🔑 **Four biomes, one mod, four independent toggles** (owner ruling 2026-09-21, §7 Q1):
the Scald, the Propane Lake, the Twilight Sea, the Grey Sea. ⛔ `RUT_Umbra` is NOT in this
mod and is not a biome — it is a region (`UMBRA_IS_A_REGION_NOT_A_BIOME_1`); its successor
`RUT_FuelSnows` is still `RUT_`-tier and gets its own row when the wave reaches it.

## 🔑 STATE — MEASURED 2026-09-23

### 1. Step table (per biome)

🔴 **Nothing is built. `src/RimMandrake/TerminalBiomes` does not exist** (MEASURED — `ls -d` errors,
and the folder is absent from the 39-entry listing of `src/RimMandrake/`). So steps 1–2 are OWED for
all four, and the table differs only in what each biome's step 2 has to carry.

| step | the Scald | the Propane Lake | the Twilight Sea | the Grey Sea |
|---|---|---|---|---|
| 1 scaffold | ⛔ OWED | ⛔ OWED | ⛔ OWED | ⛔ OWED |
| 2 copy content | ⛔ OWED — largest: own terrains + kit C# | ⛔ OWED — **donor terrain blocks it**, see §2 | ⛔ OWED — vanilla terrain only | ⛔ OWED — vanilla terrain only |
| 3 freeze the `RUT_` def | ⛔ OWED — header absent (MEASURED: `grep -l "carrying the world until the terminal paint"` over `Defs/BiomeDefs/*.xml` returns **only** `RUT_Greentide.xml`) | ⛔ OWED, same | ⛔ OWED, same | ⛔ OWED, same |
| 4 retarget | ⛔ OWED — §7 lists the real set | ⛔ OWED | ⛔ OWED | ⛔ OWED |
| 5 prove it loads | ⛔ OWED — Windows Desktop only; ⚠️ see §10 for two live blockers this step must not pretend to solve | same | same | same |
| 6 commit/push | owed with 2–5 | same | same | same |
| paint-list append | ⛔ OWED — `infrastructure/state/facts/biome_paint_list.md` has exactly **4** `RM_` rows (lines 52–55: Pyrelands, Greentide, FloodedCanyon, GelatinousSlime). The four `RUT_` rows are lines 33/37/44/45; no `RM_TheScald`/`RM_PropaneLake`/`RM_TwilightSea`/`RM_GreySea` row exists | same | same | same |

⚠️ §2b row 24 pairs this mod with `the_propane_lakes.md`, whose roster JSON `defNames` still lists
**`RUT_Umbra` and `RUT_PropaneLake` together** (`rosters/the_propane_lakes.json`). `RUT_Umbra` is a
region, not a biome (`UMBRA_IS_A_REGION_NOT_A_BIOME_1`, closed) — and that roster's `evictions` list
is **35 rows of Umbra-era snow/ice species** against only **6** `fauna` rows and **4** `flora` rows
(parsed counts). Read it with that in mind; most of it is not Propane Lake content.

### 2. The def today (four files)

All four parse clean (`xml.etree`), all four are a single `<BiomeDef>` with **no `ParentName`**, **no
`modExtensions`**, **no `diseases`**, **no `wildPlants`** (`hasVirtualPlants false`, water biomes), and
**no `terrainPatchMakers`**. `workerClass` is **`BiomeWorker_Ocean` on all four** — vanilla Core, *not*
a donor class ⇒ **§5 step 2's `RM_BiomeWorker_<X>` clause does NOT fire for this mod.**

| | the Scald | the Propane Lake | the Twilight Sea | the Grey Sea |
|---|---|---|---|---|
| path (`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/`) | `RUT_TheScald.xml` | `RUT_PropaneLake.xml` | `RUT_TwilightSea.xml` | `RUT_GreySea.xml` |
| lines | 178 | 158 | 132 | 104 |
| `workerClass` | `BiomeWorker_Ocean` ✅ vanilla | `BiomeWorker_Ocean` ✅ | `BiomeWorker_Ocean` ✅ | `BiomeWorker_Ocean` ✅ |
| `texture` | `World/Biomes/Ocean` (vanilla) | `World/Biomes/Jawa_SickWater` | `World/Biomes/Ocean` | `World/Biomes/Ocean` |
| terrain — `terrainsByFertility` | `RUT_ScaldWaterOceanDeep` −999..999 | 🔴 **`AB_PropaneLake`** −999..999 | `WaterOceanDeep` (vanilla) | `WaterOceanDeep` (vanilla) |
| terrain — water fields | `RUT_ScaldWaterShallow` / `…Deep` / `…MovingShallow` / `…MovingChestDeep` — ours, `Defs/TerrainDefs/RUT_ScaldWater.xml` | 🔴 `waterDeepTerrain AB_PropaneLake`, `waterShallowTerrain AB_SolidPropane` | none set | none set |
| weather (`baseWeatherCommonalities`) | `Clear` 14, `Fog` 8 | `Clear` 14, `Fog` 6 | `Clear` 12, `Fog` 7, `Rain` 4 | `Clear` 12, `Fog` 7, `Rain` 4 |
| diseases | none | none | none | none |
| `animalDensity` | 0.15 | (unset) | 0.1 | 0.1 |
| `impassable` / `isBackgroundBiome` | true / true | true / true | true / true | true / true |
| `fishTypes` on the def | ✅ `MayRequire="Ludeon.RimWorld.Odyssey"`, **5 species** (`RUT_Eesh` 1.5, `RUT_Muddal` 0.8 freshwater_Common; `RUT_Karrash` 1, `RUT_Saal` 0.5, `RUT_BladderboilCatch` 0.5 freshwater_Uncommon) + `rareCatchesSetMaker RUT_RareScaldCatches`; `maxFishPopulation` 30 | ⛔ absent | ⛔ absent **on the def** — but **8 species arrive by patch**, see below | ⛔ absent, nothing anywhere |
| `wildAnimals` rows | 4 | 2 | 2 | 2 |

🔴 **`AB_PropaneLake` / `AB_SolidPropane` are AlphaBiomes donor terrains — MEASURED: neither defName
is defined anywhere under `src/`** (`grep -rln` hits only consumers: `RM_LiquidBodyRegistry.xml`,
`LiquidIgnition.cs`, `RUT_FuelSnows.xml`, `RUT_Umbra.xml`, worldmap scripts). A donor TerrainDef in
`terrainsByFertility` and in `waterDeepTerrain`/`waterShallowTerrain` is exactly the hard dependency
§5 step 2 forbids the RimMandrake tier from assuming — so **`RM_PropaneLake` owes two TerrainDefs of
its own** (`RM_PropaneLakeDeep`, `RM_SolidPropane` or similar). That is this mod's one genuinely new
authoring task in step 2, and it is the reason the Propane Lake is not a copy-paste.

⚠️ **UNMEASURED, and it decides whether step 2's terrain work is bigger still:** whether the vanilla
`WaterOceanDeep` the Twilight and Grey Seas use is acceptable for a *hypersaline* sea, or whether
they too owe their own terrain. No sheet ruling says; do not assume either way.

### 3. wildAnimals split

🔑 **The rule is §3b's, not "every non-vanilla row is a patch".** §3b, verbatim: *"Non-Star-Wars
fauna … **Stay in the RimMandrake def.** The ruling says *only* Star Wars creatures become
patches."* So `AA_` (Alpha Animals, `MayRequire="sarg.alphaanimals"`) rows STAY. ⚠️ This item's
`## spec` step 2 below says only `RSW_`/`SW_`/`RUT_` move, which agrees; a reading that sweeps donor
rows out too would empty three of the four defs.

⚠️ All ten rows are written in the **shorthand** `<DefName MayRequire="…">commonality</DefName>`
form, not `<li><animal>`. Counted with `len(list(wildAnimals))`, per biome, not `findall('li')`.

| biome | defName | comm. | prefix class | verdict |
|---|---|---:|---|---|
| Scald | `RSW_SandoAquaMonster` | 0.03 | `RSW_` (ours, RimStarWars) | → `WildAnimals_TheScald.xml` |
| Scald | `RSW_ElderSando` | 0.005 | `RSW_` | → `WildAnimals_TheScald.xml` |
| Scald | `RSW_Faa` | 0.5 | `RSW_` | → `WildAnimals_TheScald.xml` |
| Scald | `RSW_Mee` | 0.5 | `RSW_` | → `WildAnimals_TheScald.xml` |
| Propane Lake | `AA_AuroraSylph` | 0.5 | donor (Alpha Animals) | **stays in `RM_PropaneLake`** |
| Propane Lake | `AA_Skyeel` | 0.5 | donor | **stays in `RM_PropaneLake`** |
| Twilight Sea | `AA_Aerofleet` | 0.05 | donor | **stays in `RM_TwilightSea`** |
| Twilight Sea | `RSW_Lanternwhale` | 0.005 | `RSW_` | → `WildAnimals_TwilightSea.xml` |
| Grey Sea | `AA_Aerofleet` | 0.05 | donor | **stays in `RM_GreySea`** |
| Grey Sea | `RSW_Reefback` | 0.005 | `RSW_` | → `WildAnimals_GreySea.xml` |

**6 rows move, 4 stay.** ⛔ **None of the three patch files exists.** MEASURED — the only
`WildAnimals_*` files in `src/RimUtinni/UtinniPatches/Patches/` are `WildAnimals_CrackedLands.xml`,
`WildAnimals_Greentide.xml`, `WildAnimals_Pyrelands.xml` and the generated
`ZZZ_BiomeWildAnimalDuplicates_Generated.xml`. `WildAnimals_Pyrelands.xml` is the shape to copy.
The Propane Lake needs **no** patch file at all.

🔴 **The consequence step 2 must answer, and it is a real design problem, not a bookkeeping one:**
after the move `RM_TheScald` has **zero** `wildAnimals` and `RM_TwilightSea` / `RM_GreySea` have
**one each** — against CLAUDE.md's standing ruling that *"the free mod must look the same as the
campaign one… 'Rich enough to stand alone' is a requirement on every `RM_` roster."* ⇒ These three
`RM_` defs need invented (non-canon, franchise-free) sea fauna of their own, which is exactly what
the sheets already commissioned as `new_defs` (§5). ⛔ Do **not** solve it by leaving the `RSW_` rows
in the `RM_` def.

### 4. wildPlants split

**Nothing to split: all four defs carry NO `wildPlants` element at all** (MEASURED, parsed — the
element is absent, not empty), and all four set `hasVirtualPlants false`. They are `impassable`
water biomes; the paint list's own rows say so (`biome_paint_list.md:33,37,44,45` — *"terrain +
fauna present, no plants … sea biome"*).

⇒ **No owner rejection applies and none is invented here.** The one flora-ish row in any of the four
rosters is `the_propane_lakes.json`'s 4-row `flora` list (`AB_CrystalHorn` 1.0, `AB_FrostLeaf` 0.6,
`AB_RimeNodules` 0.4, `PoisonShrub` 0.35) — ⚠️ but that list is **Umbra-era**, inherited from the
snow/ice region whose defName still sits in that roster's `defNames` (see §1). A liquid-propane
lake at ~−79 °C has no plants, and the def does not wire any. ⛔ Do not wire those four into
`RM_PropaneLake` on the strength of the roster file.

### 5. Roster vs def diff

Every roster def below was resolved by indexing `<defName>` across all XML under `src/` (parsed, not
grepped) and its art checked by testing `<texRoot>/<texPath>_south.png` on disk — **`_south.png`
only, never `_southm.png`**.

**Roster rows NOT wired into the def today — 28 across the four biomes.**

| biome | roster rows | wired today | unwired | of the unwired: ours (def + art present) | donor-only |
|---|---:|---:|---:|---|---|
| Scald | 8 fauna | 2 (`RSW_Faa`, `RSW_Mee`) | **6** | `JOE_Nautilant` ✅, `RSW_ColoClawFish` ✅, `RSW_ThornbackColo` ✅ — all three have a def of ours and a `_south.png` | `AA_Atispec`, `AA_LarvalAtispec`, `AA_RayHound` |
| Propane Lake | 6 fauna + 4 flora | 2 (`AA_AuroraSylph`, `AA_Skyeel`) | **8** | none | all 8 (`AA_*`/`AB_*`/`PoisonShrub`) — and 4 of them are the Umbra-era flora rows |
| Twilight Sea | 14 fauna | 2 (`AA_Aerofleet`, `RSW_Lanternwhale`) | **12** | `RSW_Laa`, `RSW_OpeeSeaKiller`, `RSW_MutatingTumorfishAdult`/`Fry`/`Spawn`, `RSW_AbyssalColo`, `RSW_CrimsonOpee`, `RSW_Starmaw`, `RSW_StormSando` — **9, every one with a def of ours and `_south.png` present** | `Yobshrimp`, `AA_ColossalAerofleet`, `StoneCrab` |
| Grey Sea | 8 fauna | 2 (`AA_Aerofleet`, `RSW_Reefback`) | **6** | `RSW_SiltLamprey` ✅, `RSW_ElderSando` ✅, `RSW_Polluwog` ✅ | `AA_ColossalAerofleet`, `Blixus`, `TetnissCrab` |

**Def rows NOT in the roster:** zero. Every one of the 10 wired `wildAnimals` rows appears in its
biome's roster. ✅ (Scald's `RSW_SandoAquaMonster`/`RSW_ElderSando` appear as `evictions`, not
`fauna` — wired on the def but ruled OUT by the roster: disposition `move:AB_MiasmicMangrove` and
`move:RUT_GreySea` respectively. Those two are **not** step-2 work; they are the eviction stream the
owner stopped — `BIOME_SPECIFIC_FAUNA_LAW_1`: *"Let's stop evictions right now."* ⛔ Do not execute
them here.)

⚠️ **UNMEASURED:** whether each unwired `RSW_` def's other facings (`_north`/`_east`) exist, and
whether any of the donor names is still in the live mod set. Neither is measurable offline for the
live list.

**New defs the sheets commissioned and nothing has built** (roster `new_defs`, counts parsed):
Scald **3** (thermophile mats, bubble-sailor jellyfish, silver shoal), Propane Lake **2** (polar
Burner ascendant, V-wake propane-native + kin), Grey Sea **5** (pillar-mason, ossuary shrimp, salt-
rimed blade flora Grey variant, shadow-lane detritivore + condensate drinker Grey, one rename
ledger row), Twilight Sea **7** (mold-mat roof organism, salt-rimed blade flora, shadow-lane
detritivore, condensate drinker, shore scavenger, one rename ledger row, one DEFERRED Deep set).
⇒ **17 rows, none built.** These are the franchise-free cast §3's standalone requirement needs, and
they are **not** blockers on steps 1–4 — see §10.

### 6. Content to move into the mod

🔑 **The kit C# does NOT move — it is already RimMandrake-tier and already shipped.** MEASURED by
reading every `Class=`/`workerClass`/`compClass` string in the Scald's own def files: they all
resolve to `RimMandrake.EnvironmentalHazards.*` in `mandrake.rm.environmentalhazards` (a §2d shared
library) — `RUT_IncidentWorker_SteamDevil`, `RUT_IncidentWorker_WalkerSurfacing`,
`RM_GenStep_PlacedSetPieces`, `RM_ScattererValidator_NearThingDef`, `RM_SetPieceElement_AnchoredPawn`,
`CompProperties_ResourceCondenser`, `WeatherPulseExtension`, `RUT_WeatherOverlay_ScaldSteam`. ⇒ **No
`.csproj` edit, no namespace move, no new assembly.** `TerminalBiomes` is XML + settings C# only, and
`loadAfter` is how it reaches them. (⚠️ Three of those classes carry a `RUT_` prefix *inside* the
RimMandrake namespace — a tier-naming oddity, filed nowhere; ⛔ not this item's work and not a
blocker.)

**MOVES into `src/RimMandrake/TerminalBiomes/`** — all paths relative to
`src/RimUtinni/UtinniPatches/`; each passes §3a (would make sense on a random planet, no Star Wars,
no Ash'karr):

- `Defs/BiomeDefs/RUT_TheScald.xml` · `RUT_PropaneLake.xml` · `RUT_TwilightSea.xml` ·
  `RUT_GreySea.xml` → `RM_*` — the four biomes themselves
- `Defs/TerrainDefs/RUT_ScaldWater.xml` · `RUT_ScaldMargin.xml` — the Scald's own water + cool ring
- `Defs/DamageDefs/RUT_Scald.xml` — scalding damage, no campaign content
- S1: `Defs/WeatherDefs/RUT_ScaldSteam.xml` · `Defs/GameConditionDefs/RUT_ScaldSteamLock.xml` ·
  `Defs/IncidentDefs/RUT_SteamDevilAppears.xml` · `Defs/ThingDefs_Misc/RUT_SteamDevil.xml` ·
  `Patches/RUT_ScaldSteamLock_BiomeWiring.xml` (⚠️ retarget its xpath to `RM_TheScald`)
- S2/S4: `Defs/ThingDefs_Buildings/RUT_SteamCatch.xml` · `RUT_ScaldVent.xml`
- S5: `Defs/IncidentDefs/RUT_WalkerSurfacing.xml` · `Defs/MapGeneration/RUT_ScaldSailScatterer.xml`
  + `Patches/RUT_ScaldSailScatterer_Register.xml`
- S6: `Defs/ThingDefs_Buildings/RUT_ScaldWrecks.xml` · `Defs/MapGeneration/RUT_ScaldWreckScatter.xml`
  + `Patches/RUT_ScaldWreckScatter_Register.xml` (both Registers target vanilla `Base_Player`
  genSteps — no campaign content)
- fish: `Defs/ThingDefs_Items/RUT_ScaldFish.xml` · `RUT_TwilightFish_Niim.xml` ·
  `Defs/ThingSetMakerDefs/RUT_RareScaldCatches.xml` · `RUT_RareTwilightCatches.xml` ·
  `Patches/BiomeFishTypes_TwilightDeep.xml` (⚠️ this is *content* — fold it into `RM_TwilightSea`'s
  own def rather than shipping a patch)
- `Languages/English/Keyed/RUT_Scald_Mechanics.xml` — the kit's keyed strings

**STAYS in Utinni, and why:**

| path | reason |
|---|---|
| `Patches/BiomeNames_Ashkarr.xml`, `BiomeDescriptions_Ashkarr.xml` | "the Scald", "the Twilight Sea" are Ash'karr's words. ✅ MEASURED: neither file carries a real op on any of the four — every hit is a **comment** (`BiomeNames:6`; `BiomeDescriptions:43,44,67,102`). All four `RM_` defs must therefore carry their own generic label + description natively, as `RM_Greentide` does |
| `Patches/MechClusterBiomes_AmbientDoctrine.xml` | campaign mech doctrine — real `<li>` rows at `:77,78,88,89` |
| `Patches/AncientDangerGenSteps_AmbientDoctrine.xml` | comments only (`:47,51`) — leave untouched |
| `Patches/FishTypesStrip_NoFishBiomes.xml` | donor-strip sweep; comments only for these four (`:50–51`) — but see §7's false statement |
| `Patches/BiomeFlora_Ashkarr.xml` | comments only (`:77,83`), in its deliberate "does NOT patch" block |
| `StructureInjectionsRUT/**` (Dark Tower, War Lab) | Ash'karr landmarks on Ash'karr tiles |
| the 6 `RSW_` fauna rows | Star Wars creatures — §3 |

### 7. References to the `RUT_` defNames

`grep -rl` over `src design infrastructure skills world`, then **each hit read**. Most are comments;
the Greentide exemplar's warning applies — ⛔ do not list a comment as owed work.

**(a) Retarget outright** — target need not be on the world:
- `design/Jawa/worldbuilding/biomes/rosters/the_scald.json` / `the_propane_lakes.json` /
  `the_grey_sea.json` / `the_twilight_sea.json` — the `defNames` key
- `design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md`, `biome_flora_rosters.md`
- `design/Jawa/worldbuilding/biomes/kits/scald_kit_spec.md`
- `design/validation_walks/RimUtinni/UtinniPatches.md:9,19` — the walk asserts 6 BiomeDefs load from
  UtinniPatches and step 2 reads `RUT_TheScald`/`RUT_GreySea` back. ⚠️ Both will still be TRUE after
  Phase A (step 3 keeps the twins), so this is retarget-**later**, at Phase B, not now
- `src/RimUtinni/UtinniPatches/Patches/RUT_ScaldSteamLock_BiomeWiring.xml:33,35` — moves with the file

**(b) Needs a SECOND op / second entry for the `RM_` name** (must keep working on the live world):
- 🔴 `src/RimMandrake/FlowWorks/Defs/LiquidTypes/LiquidBodyDefs/RM_LiquidBodyRegistry.xml:54,67,77,91`
  — four real `<li>` biome entries, one per sea, in a **RimMandrake-tier** registry. Add the `RM_`
  name beside each `RUT_` one
- `src/RimUtinni/UtinniPatches/Patches/MechClusterBiomes_AmbientDoctrine.xml:77,78,88,89` — real `<li>`
  rows for `RUT_PropaneLake` and `RUT_TheScald`
- `src/RimUtinni/LanternDeeps/Source/LanternDeepsMod.cs:60` (allowlist string) **and**
  `src/RimUtinni/LanternDeeps/validation.py:83` (`QUALIFYING_BIOMES`) — the Deeps inject beneath
  Propane Lake tiles; both need `RM_PropaneLake` added, not substituted
- `src/RimUtinni/StructureInjectionsRUT/Source/WarLab/WarLabCraterMutation.cs:25`
  — `private const string SourceBiomeDefName = "RUT_PropaneLake"`, a live world hook
- `src/RimMandrake/DivingInteraction/Patches/RM_ScaldDiveEligibleTerrain.xml:26,33,40` — targets the
  three Scald **terrain** defs by name; those terrains move, so this follows them (terrain names, not
  biome names — decide at the move whether they are renamed `RM_*`)

**(c) Comment / prose — LEAVE:** `BiomeNames_Ashkarr.xml:6` · `BiomeDescriptions_Ashkarr.xml:43,44,67,102`
· `AncientDangerGenSteps_AmbientDoctrine.xml:47,51` · `BiomeFlora_Ashkarr.xml:77,83` ·
`FishTypesStrip_NoFishBiomes.xml:50,51` · `selftest_deployed_biome_refs.py:193` ·
`ecosystem_pyramid_check.py:50` · `RiverColors/About/About.xml:21,24,25` and
`HarmonyPatch_RiverColors.cs:49,54` · `StructureInjectionsRUTSettings.cs:9` ·
`SitePartDefs_WarLab.xml:21` · `SitePartDefs_DarkTower.xml:12,21` ·
`JawaBenchWorldTools.cs:2942` · `LanternDeeps/About/About.xml:35` · `canon.yml` (tile record) ·
`world/**` (the frozen CSV record) · everything under `Transient/`.

⚠️ `Patches/BiomeAllowRoads_PropaneLakes.xml:11` targets the **donor** `AB_PropaneLakes` (plural), not
our `RUT_PropaneLake`. It is not a reference to this mod's content at all — ⛔ do not "retarget" it.

### 8. Mechanics / kit state

Only the Scald has a kit spec (`design/Jawa/worldbuilding/biomes/kits/scald_kit_spec.md`, 6
mechanics). The Propane Lake, Twilight Sea and Grey Sea have **no kit spec and no kit mechanics** —
their per-biome settings section is the biome toggle alone.

`rimflow show SCALD_MECHANICS_1` → **`doing`, owner FOUNDRY, needs offline, target v1**, filed
2026-09-07. Its own verdict line (item file, *"Continuation pass — 2026-09-18"*): *"kit is now
S1/S2/S4/S5/S6 fully landed with S1's own last in-scope gap closed; S3 … is the sole remaining
mechanic."*

| mechanic | state | where |
|---|---|---|
| S1 boil layer / steam sky | ✅ SHIPPED | `RUT_ScaldSteam.xml` (WeatherDef), `RUT_ScaldSteamLock.xml` + `_BiomeWiring.xml`, `RUT_SteamDevil.xml`, `RUT_SteamDevilAppears.xml`; C# `RUT_IncidentWorker_SteamDevil`, `RUT_WeatherOverlay_ScaldSteam`, `WeatherPulseExtension` — all in `mandrake.rm.environmentalhazards` |
| S2 steam-catch | ✅ SHIPPED | `RUT_SteamCatch.xml`; `RM_CompResourceCondenser` + `CompProperties_ResourceCondenser`, `RM_PlaceWorker_OnRequiredVentComp` (EnvironmentalHazards) |
| S3 margin fishing + baths | ⛔ **UNBUILT, and genuinely blocked** — `RUT_ScaldMargin.xml` (the terrain) exists; the *content* does not. Two blockers: `FISH_BESTIARY_BUILD_1`'s own build, and a bridge-only map-authoring step (the cove must be hand-placed; the terrain deliberately does not scatter itself) | — |
| S4 geyser / vent fields | ✅ SHIPPED (defs) | `RUT_ScaldVent.xml`. ⚠️ Actual vent **placement onto the Scald's map** is still owed and is bridge/world work |
| S5 sail + walker set-pieces | ✅ SHIPPED | `RUT_ScaldSailScatterer.xml` + `_Register.xml`, `RUT_WalkerSurfacing.xml`; C# `RUT_IncidentWorker_WalkerSurfacing`, `RM_GenStep_PlacedSetPieces`, `RM_SetPieceElement_AnchoredPawn`, `RM_ScattererValidator_NearThingDef` |
| S6 wreck salvage | ✅ SHIPPED (zero new C# — a measured finding) | `RUT_ScaldWrecks.xml`, `RUT_ScaldWreckScatter.xml` + `_Register.xml`. Loot `ThingSetMaker` deferred to an items pass |

⇒ **5 of 6 move now, as XML, with no code change. S3 must NOT be waited on** — it is blocked on two
things neither this mod nor FOUNDRY's offline pass can reach.

#### The sea-floor-and-catch half — read `SEA_FLOOR_AND_CATCH_PASS_1`, do not re-plan it

`rimflow show SEA_FLOOR_AND_CATCH_PASS_1` → **`proposed`, owner BENCH, needs game-up, target v1**.
It is 🛑 **STOPPED ON THE MAC by the owner, 2026-09-22**, pending one Desktop lookup (how a coastal
LAND map depicts ocean water), and it explicitly says *"land this before or with that build, not
after"*. Per-biome state, MEASURED here and matching that item:

| sea | floor animals (`wildAnimals`) | catch (`fishTypes`) | dive-eligible terrain |
|---|---:|---|---|
| Scald | 4 | ✅ 5 species on the def + `RUT_RareScaldCatches` | ✅ 3 terrains tagged `RM_DiveEligible` |
| Twilight Sea | 2 | ✅ 8 species **via `Patches/BiomeFishTypes_TwilightDeep.xml`**, hold lifted 2026-09-20 | ⛔ none — no shallow terrain def of any kind |
| Grey Sea | 2 | ⛔ none anywhere | ⛔ none |
| Propane Lake | 2 | ⛔ none anywhere; roster rules **no fish possible** (liquid propane at ~−79 °C) | ⛔ none |

⚠️ **UNMEASURED and not assertable offline:** whether `<wildAnimals>` spawn at all on an
`impassable=true` water biome. All four wire 2–4 animals, so somebody bet yes; that is a bet, not a
measurement, and RimSage is Desktop-only. ⛔ Do not state it either way in a commit message.

### 9. Dependencies & items building INTO this mod

`rimflow show` state lines, verbatim, for every live item that names one of the four defNames:

| item | state line | relation to this build |
|---|---|---|
| `BIOME_MOD_SPLIT_EXECUTION_1` | `doing · needs offline · v1` | parent |
| `SCALD_MECHANICS_1` | `doing · needs offline · v1` | content lands here; S3 must not be waited on (§8) |
| `SEA_FLOOR_AND_CATCH_PASS_1` | `proposed · needs game-up · v1` | its own spec step 6 says land it **before or with** this build; ⛔ stopped on the Mac by the owner |
| `FISH_BESTIARY_BUILD_1` | `doing · needs offline · v1` | owns the catch design; the Scald's 5 and the Twilight's 8 already ship from it. ⛔ do not re-derive |
| `QUICKTEST_RIVER_WATER_MISSING_1` | `doing · needs game-up · v1` | blocks *live proof* of any water work — step 5 only, not steps 1–4 |
| `ANCIENT_WAR_LAB_1` | `doing · needs offline · v1` | lands **later**; lives on Propane Lake tiles, campaign content, stays Utinni |
| `WAR_LAB_CRATER_HOOK_1` | `doing · BLOCKED · needs offline · v1` | owns `WarLabCraterMutation.cs:25`'s biome const — §7(b) |
| `LANTERNDEEPS_RM_MOD_BUILD_1` | `proposed · needs offline · v1` | owns the `QUALIFYING_BIOMES` / allowlist constants — §7(b); coordinate, do not duplicate |
| `WORLDMAP_LIQUID_TAGS_1` | `doing · needs deploy · v1` | later; worldTag authoring on the frozen map |
| `BIOME_WORLD_SWITCH_WAVE_1` | `doing · needs bridge · v1` | Phase **B** — painting. ⛔ not this item |
| `ECOSYSTEM_PYRAMID_LAW_1` | `proposed · needs deploy · v1` | judges rosters; lands later |
| `ROSTER_DEAD_BMT_NAMES_SWEEP_1` | `proposed · needs offline · v1` | per-species wire-or-drop, never bulk — lands later |
| `MOD_OPTIONS_RETROFIT_1` | `ready · BLOCKED · needs offline · v1` | the settings requirement §11 implements |
| `BIOME_PAINT_ONCE_AT_THE_END_1` · `WORLD_REMAKE_FINAL_STEP_1` | `proposed` | governing / paint-list destination |

⇒ **Nothing in this table blocks step 2.** The only two that touch step 2 at all —
`SEA_FLOOR_AND_CATCH_PASS_1` and `SCALD_MECHANICS_1` — are additive content items whose existing
output is already on disk and moves as-is.

### 10. Blockers

**Steps 1–4: NONE.** FOUNDRY can start tomorrow morning.

Everything below is a step-5 (live) or later-content concern and is **not** a reason to delay
scaffolding, copying, freezing or retargeting:

- Step 5 is Windows-Desktop only (a platform constraint, not a blocker of 1–4).
- `QUICKTEST_RIVER_WATER_MISSING_1` (`doing`) — quicktest maps generate zero water terrain, so **no
  live proof of any water behaviour is obtainable** even on the Desktop right now. ⇒ Say "authored,
  not live-proven" and mean it.
- Whether `wildAnimals` spawn on an `impassable` water biome — UNMEASURED offline (§8).
- The 17 commissioned `new_defs` (§5) and S3 (§8) are **later content**, tracked on their own items.
- ⚠️ One judgement call step 2 must make and cannot dodge: **`RM_PropaneLake`'s two donor terrains**
  (§2). Authoring `AB_PropaneLake`/`AB_SolidPropane` equivalents of our own is straightforward, but
  it changes what the biome looks like, so it is worth one line to the owner rather than a silent
  invention.

### 11. Concrete step plan

**1 — Scaffold.** `src/RimMandrake/TerminalBiomes/About/About.xml`, `packageId
mandrake.rm.terminalbiomes`.
`loadAfter`, derived from what the moved content actually references (cited):
- `mandrake.rm.environmentalhazards` — **required**: every kit class in §8 is
  `RimMandrake.EnvironmentalHazards.*`, named in `RUT_ScaldSteamLock.xml:73`,
  `RUT_WalkerSurfacing.xml:54`, `RUT_SteamDevilAppears.xml:34`, `RUT_SteamCatch.xml:77`,
  `RUT_ScaldSailScatterer.xml:123,130,136`.
- `mandrake.rm.divinginteraction` — **required**: `RM_ScaldDiveEligibleTerrain.xml` patches this
  mod's terrain defs with the `RM_DiveEligible` tag.
- `mandrake.rm.flowworks` — **required**: `RM_LiquidBodyRegistry.xml:54,67,77,91` lists all four seas.
- ⛔ **Not** `mandrake.rm.creaturebehaviors` and **not** `mandrake.rm.weathersuite` — MEASURED: no
  moved file names a class from either.
`src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs` + `…Settings.cs`, modelled on
`RM_GreentideMod.cs` (§6a's named template). `deploy_custom_mods.py --mod TerminalBiomes` dry run,
read the plan, then `--apply`.

**Settings — five toggles** (§6a master + §7 Q1's one per biome):

| # | toggle | default | note |
|---|---|---|---|
| 1 | `masterEnabled` — the mod on/off (defs still load; mechanics stop) | on | §6a Master row |
| 2 | `scaldEnabled` | on | §7 Q1 |
| 3 | `propaneLakeEnabled` | on | §7 Q1 |
| 4 | `twilightSeaEnabled` | on | §7 Q1 |
| 5 | `greySeaEnabled` | on | §7 Q1 |

Plus, per §6a's "one toggle per mechanic the kit spec names", the Scald section gets S1/S2/S4/S5/S6
sub-toggles (S3 is unbuilt — ⛔ do not ship a toggle for nothing), a cross-biome block
(`enabled`/`everywhere`/allowlist/coverage, default **off**), and a map-gen label on anything that
only takes effect on a new map. ⚠️ §6b: gate at the comp/MapComponent level, **never** at the def.

**2 — Copy the content in.** `Defs/BiomeDefs/RM_TheScald.xml`, `RM_PropaneLake.xml`,
`RM_TwilightSea.xml`, `RM_GreySea.xml` from the four sources in §2, plus the file list in §6.
In the same step:
- strip the 6 `RSW_` rows (§3) and write `src/RimUtinni/UtinniPatches/Patches/WildAnimals_TheScald.xml`
  (4 rows), `WildAnimals_TwilightSea.xml` (1), `WildAnimals_GreySea.xml` (1) — `PatchOperationAdd`
  onto `/Defs/BiomeDef[defName="RM_X"]/wildAnimals`, `MayRequire="mandrake.rsw.swbestiary"`,
  `WildAnimals_Pyrelands.xml` as the shape. ⛔ No file for the Propane Lake.
- keep the 4 `AA_` rows on the `RM_` defs (§3b).
- **author `RM_PropaneLakeDeep` + `RM_SolidPropane` TerrainDefs** and repoint
  `terrainsByFertility`/`waterDeepTerrain`/`waterShallowTerrain` off `AB_*` (§2).
- give every `RM_` def its **own generic label + description** — `BiomeNames_Ashkarr.xml` and
  `BiomeDescriptions_Ashkarr.xml` carry no op for these four (§6/§7c), so nothing would supply them.
- fold `Patches/BiomeFishTypes_TwilightDeep.xml`'s 8 species + `maxFishPopulation 700` into
  `RM_TwilightSea`'s own def rather than shipping it as a patch.
- ⛔ `workerClass` stays `BiomeWorker_Ocean` — no `RM_BiomeWorker_*` is owed (§2).

**3 — Freeze all four `RUT_` defs.** Byte-for-byte, one header comment each: *"carrying the world
until the terminal paint; content lives in `mandrake.rm.terminalbiomes`; do not edit here."*
`RUT_Greentide.xml` is the only file in that folder carrying the header today — copy its wording.

**4 — Retarget** exactly the §7(a) list; add second entries for exactly the §7(b) list. ⛔ Touch
nothing in §7(c).

**5 — Prove it loads** (Desktop): minimal list + `mandrake.rm.terminalbiomes` +
`mandrake.rm.environmentalhazards` + `mandrake.rm.divinginteraction` + `mandrake.rm.flowworks` +
`mandrake.rut.patches` + **all five expansions**. Grep `Player.log` for Config errors;
`validate_patch.py --live --defs` on the three new `WildAnimals_*.xml`; confirm from a post-load def
dump that the 6 rows landed (an unmatched `PatchOperationAdd` is silent).

**6 — Commit and push**, explicit paths, one commit; append four rows
(`RM_TheScald`/`RM_PropaneLake`/`RM_TwilightSea`/`RM_GreySea`, folder `src/RimMandrake/TerminalBiomes`,
packageId `mandrake.rm.terminalbiomes`) to `infrastructure/state/facts/biome_paint_list.md` beside
the existing four `RM_` rows at lines 52–55.

### False statements found elsewhere

BENCH to fix; ⛔ not edited by this pass.

1. **`src/RimUtinni/UtinniPatches/Patches/FishTypesStrip_NoFishBiomes.xml:50–51`** —
   *"the 5 `RUT_`-tier own-authored defs (RUT_TheScald/RUT_TwilightSea/RUT_GreySea/RUT_PropaneLake/
   RUT_NightsideIce) already ship `fishTypes` empty, documented, at authoring time."* **False on
   three counts, MEASURED by parsing:** `RUT_TheScald` ships a **populated** `fishTypes` (5 species +
   `rareCatchesSetMaker RUT_RareScaldCatches`, `maxFishPopulation 30`); `RUT_TwilightSea` receives a
   populated one by patch (`BiomeFishTypes_TwilightDeep.xml`, 8 species, `maxFishPopulation 700`,
   hold lifted 2026-09-20); and `RUT_GreySea`/`RUT_PropaneLake` ship **no `fishTypes` element at
   all** — absent, not "empty".
2. **`design/Jawa/worldbuilding/biomes/rosters/the_twilight_sea.json`, `fish.ruling`** — *"no surface
   fish … the silver shoals exist ONLY beneath the mat-roof … ride the deferred diving-mods
   implementation."* **Superseded and now false:** owner ruled 2026-09-20 (`TWILIGHT_DEEP_WATER_LAYER_1`,
   closed), verbatim *"Just make the surface fishable"*, and 8 species ship on the surface today.
3. **`design/Jawa/worldbuilding/biomes/rosters/the_propane_lakes.json`, `defNames`** — still lists
   `RUT_Umbra` beside `RUT_PropaneLake`; its 35 `evictions` rows and all 4 `flora` rows are Umbra-era
   snow/ice content. `UMBRA_IS_A_REGION_NOT_A_BIOME_1` (closed) ruled Umbra is not a biome; the roster
   has not been split.
4. ⚠️ **`design/RimMandrake/biome_mod_architecture.md` §2b rows 24–26 and this item's `## spec`** give
   tile counts (57 / 607 / 472) as identifying detail. Correct per the 2026-09-12 CSV export, but
   ⛔ per `BIOME_PAINT_ONCE_AT_THE_END_1` a tile count is evidence of nothing here. Not a correction
   request — a note that no reader should act on those numbers.

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.terminalbiomes`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_TheScald/RM_PropaneLake/RM_TwilightSea/RM_GreySea` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_TheScald/RM_PropaneLake/RM_TwilightSea/RM_GreySea`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.terminalbiomes`; do not edit here."* From that moment
   every content fix lands in `RM_TheScald/RM_PropaneLake/RM_TwilightSea/RM_GreySea` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_TheScald/RM_PropaneLake/RM_TwilightSea/RM_GreySea` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_TheScald/RM_PropaneLake/RM_TwilightSea/RM_GreySea` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.terminalbiomes` exists, deploys, and loads clean carrying `RM_TheScald/RM_PropaneLake/RM_TwilightSea/RM_GreySea` with its own content and its own
Mod Settings screen; the `RUT_` twin is frozen with its header and unchanged; the Star Wars
fauna ride a Utinni patch rather than the RimMandrake def; one commit, explicit paths, the
message naming what the twin got wrong; and the mod is appended to
`WORLD_REMAKE_FINAL_STEP_1`'s paint list.

## Watch out

- ⛔ **Do not paint, and do not cite a tile count as evidence about this biome.** The planet
  is painted ONCE, at the end. A def of ours carrying 0 tiles is the expected mid-migration
  state, not a defect.
- ⛔ **Do not delete the `RUT_` def.** Deleting a painted def before Phase B destroys the
  save.
- ⚠️ A `<li>` in the wrong place discards the WHOLE def, silently.
