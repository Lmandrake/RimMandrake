# PYRELANDS_RM_MOD_BUILD_1 — build RM_Pyrelands as its own RimMandrake mod

**the Pyrelands - twin pair, mod EXISTS; defName rename done at 84d42c63b, BUILT NOT DEPLOYED**

Phase A row 15 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

⚠️ **Live trap.** The `RM_FE_Pyrelands` → `RM_Pyrelands` rename is committed at
`84d42c63b` but **built and NOT deployed** — the game was running when it landed.
Deploy before testing anything here.

## 🔑 STATE — MEASURED 2026-09-23

🔴 **The header's "BUILT NOT DEPLOYED" live trap is FALSE and is discharged.** MEASURED this pass
by `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Pyrelands` (dry run): **`Pyrelands
mandrake.rm.pyrelands / in sync (46 files) / Everything in sync.`** Same verb on the three other
mods that `84d42c63b` touched: `PyrelandsMechanics in sync (11 files)`, `FlowWorks in sync (62
files)`, and `UtinniPatches` drifts on **Greentide files only** (`RUT_Greentide.xml`,
`WildAnimals_Greentide.xml`) — `WildAnimals_Pyrelands.xml` is deployed. ⇒ Nothing about the
Pyrelands is waiting on a deploy. BENCH: delete the trap paragraph above.

🔑 **§4c governs this row, and step 3 does not apply.** The loser is `ZBiome_Grasslands`, a *More
Vanilla Biomes* **donor** def — not ours, so there is nothing of ours to freeze and nothing of ours
to delete. **What replaces step 3:** leave the donor def untouched (we never edit it), and leave
the Utinni ops that target it in place until the terminal paint, at which point §4c deletes them.
The `.claude/hooks` WARN on `UtinniPatches/Defs/BiomeDefs/` (§7 Q7) is irrelevant here — this
biome has no file in that directory.

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⚠️ **PARTIAL** — `About/About.xml` has `packageId mandrake.rm.pyrelands`, `Defs/BiomeDefs/` present, `RM_PyrelandsSettings : ModSettings` + `SettingsCategory("Pyrelands")` + `DoSettingsWindowContents` present (`Source/RM_PyrelandsMod.cs:24,166,175`). ⛔ `loadAfter` is `brrainz.harmony` + `Ludeon.RimWorld` **only** — no §2d shared library, and **no master toggle and no cross-biome section** in the settings screen (§6a): MEASURED zero hits for `master`/`crossBiome` in `RM_PyrelandsMod.cs` |
| 2 copy content | ✅ **DONE** — 22 defs across 15 XML files + 5 `.cs` + `Assemblies/FireEcologyHook.dll` + 29 PNG already live in `src/RimMandrake/Pyrelands`; `<wildAnimals>` is 13 vanilla-Core rows with **zero** `RSW_`/`SW_`/`RUT_`, and the campaign cast already rides `UtinniPatches/Patches/WildAnimals_Pyrelands.xml` (see §3). ⛔ Owed at this step, not a new step: absorb `mandrake.rut.pyrelandsmechanics` (§6) and fix the broken biome texture (§2) |
| 3 freeze the twin | **N/A — see the §4c box above.** The painted def is a donor, not ours. Nothing to freeze, nothing to header, nothing to delete |
| 4 retarget / second op | ⚠️ **PARTIAL, and much smaller than the spec implies.** Already done: `AshStorms_Pyrelands.xml`, `FlowWorks_SubsurfaceLiquid_Ashkarr.xml` and `ManyWaters_RiverSteam_Ashkarr.xml` each already carry a **second `RM_Pyrelands` op beside the donor one** (MEASURED, xpaths read). Genuinely owed: **2 files** (§7) |
| 5 prove it loads | ⛔ **OWED — Windows Desktop only.** `validation.py` exists (269 lines) and drives live `jawa/get_def` on `RM_Pyrelands`; it has **no `shows=` bars** (MEASURED 0) and there is no north-star checklist `.md` for this mod, so `modcheck` cannot GREEN it either way |
| 6 commit/push | ⛔ owed with whatever steps 1/2/4 write |
| paint-list append | ⚠️ **PARTIAL — the row EXISTS but is STALE.** `infrastructure/state/facts/biome_paint_list.md:52` still keys the row on **`RM_FE_Pyrelands`**, and lines 59/73/108/109 repeat it. The defName has been `RM_Pyrelands` since `84d42c63b` (2026-09-21) |

### 2. The def today

`src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml` — **322 lines**, one `BiomeDef`, defName
**`RM_Pyrelands`**. MEASURED: **zero `RM_FE_Pyrelands` strings remain under `src/`** in any
`*.xml`/`*.cs`/`*.py` (`grep -rn`, empty result).

| field | value | note |
|---|---|---|
| `workerClass` | `RimMandrake.StarWars.FireEcology.BiomeWorker_Pyrelands` (:33) | ⛔ **NOT a donor class — it is OURS** (`Source/FireEcologyHook.cs:279`). Step 2's "donor `workerClass` → `RM_BiomeWorker_<X>`" clause has **nothing to do**. What is owed is the `.StarWars.` namespace fossil: **all 5 `.cs` files** declare `namespace RimMandrake.StarWars.FireEcology` |
| `texture` | `World/Biomes/RM_Pyrelands` (:34) | 🔴 **BROKEN.** The only PNG in `Textures/World/Biomes/` is **`RM_FE_Pyrelands.png`** — `84d42c63b` renamed the texPath string and never `git mv`'d the file, so the world-map tile binds nothing (a texture binds by texPath, not defName). 1-file fix, owed at step 2 |
| `modExtensions` | 1 — `RimMandrake.StarWars.FireEcology.PyrelandsBiomeRanges` (:56), shipped by **this mod** (`FireEcologyHook.cs:258`) | `temperature 25~60`, `rainfall 550~1000`, `elevation 0~2200`, `baseScore 30`, `degreeWeight 2.6`, `rainfallDivisor 120`. ⚠️ The def's own code-review note says the shipped constants put the AridShrubland crossover at T≈32.5–34.4 °C, not the documented ~25 °C — a tuning question, already recorded in the file |
| `extraGenSteps` | `RM_FE_ScorchRuins` | `Defs/GenStepDefs/PyrelandsGenSteps.xml` |
| `preventGenSteps` | `RockChunks`, `ScatterShrines` | owner 2026-09-14 |
| terrains | 7 ours — `RM_FE_Ground_{Sand,Gravel,Soil,SoilRich}`, `RM_FE_Ash_{Trace,Light,Heavy}` — plus vanilla `Riverbank`/`Mud`/`WaterShallow`/`WaterDeep`. `RM_FE_Ash_Deep` and `RM_FE_FirebreakLine` ship but are earned in play | all texturePaths resolve: 4 ash PNGs present, the 4 grounds + firebreak point at vanilla `Terrain/Surfaces/*` |
| weather | `Clear` 40, `DryThunderstorm` 20, `RM_FE_Weather_AshFall` 14, `RM_FE_Weather_Cinderfall` 4, `RM_FE_BlackRain` 3, `Fog` 2, `GrayPall` 1 (Anomaly), `Windy` 2 / `Overcast` 2 (Odyssey) | 3 weathers ours, `Defs/WeatherDefs/` |
| diseases | 8, all vanilla: `Disease_Flu` 100, `Disease_Plague` 100, `Disease_GutWorms` 60, `Disease_MuscleParasites` 60, `Disease_FibrousMechanites` 30, `Disease_SensoryMechanites` 30, `Disease_AnimalFlu` 100, `Disease_AnimalPlague` 100 | |
| other | `plantDensity 16`, `animalDensity 2.1`, `wildPlantRegrowDays 9`, `wildPlantsCareAboutLocalFertility false`, `foragedFood RawAgave`, `diseaseMtbDays 65`, `forageability 0.45` | |
| `fishTypes` | **absent** (parsed) | so `FishTypesStrip_NoFishBiomes.xml` needs no second op — same clearance the Greentide got |

⚠️ Both `<wildAnimals>` and `<wildPlants>` use the **shorthand dictionary form**
(`<Hare>1.2</Hare>`), never `<li><animal>`. `BiomeAnimalRecord.LoadDataFromXmlCustom` reads only
that form — a parser written for `<li>` reads this def as empty.

**Mod inventory (MEASURED, `find`, excluding `__pycache__`/`obj`):** 15 XML (22 defs: 1 BiomeDef,
1 GenStepDef, 9 TerrainDef incl. 2 abstract, 8 ThingDef, 3 WeatherDef), 5 `.cs` — **all 5 listed
in `Source/FireEcologyHook.csproj`**, which sets `EnableDefaultCompileItems false` — 1 `.csproj`,
1 `Assemblies/FireEcologyHook.dll`, 29 PNG, `validation.py`, `About/About.xml`, `LICENSE`.
**21 of the 22 defs still carry the `RM_FE_` infix** — the project-name fossil §4c names; only the
BiomeDef was renamed.

### 3. wildAnimals split — ✅ ALREADY DONE

`RM_Pyrelands`'s own `<wildAnimals>` = **13 rows, all vanilla Core, zero `RSW_`/`SW_`/`RUT_`**
(parsed with `xml.etree`): `Hare` 1.2, `Rat` 1.0, `Gazelle` 0.7, `Ostrich` 0.5, `Emu` 0.5,
`Dromedary` 0.4, `Iguana` 0.4, `Muffalo` 0.35, `Elephant` 0.25, `Rhinoceros` 0.2, `Cougar` 0.12,
`Fox_Fennec` 0.12, `Warg` 0.05 → **all 13 stay in the `RM_` def.** This is what §7 Q11 measured as
already compliant.

`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml` **exists** (215 lines, `wc -l`) and
since `84d42c63b` **all three of its ops target `Defs/BiomeDef[defName="RM_Pyrelands"]`** — not the
donor. **12 rows ride it:**

| op | gate | rows |
|---|---|---|
| 1 `PatchOperationReplace` (whole `wildAnimals` node) | conditional on the node existing | `RUT_FireHawk` 0.15, `RUT_FurnaceBeast` 0.08 |
| 2 `PatchOperationAdd` | `MayRequire="mandrake.rsw.swbestiary"` | `RSW_Anooba` 0.35, `RSW_Iriaz` 0.5, `RSW_Nuna` 0.5, `RSW_Orray` 0.25, `RSW_Zeer` 0.6, `RSW_Dalgo` 0.18, `RSW_Gizka` 1.0 |
| 3 `PatchOperationAdd` | `MayRequire="mandrake.rm.pyrelands"` | `RUT_Emberscythe` 0.05, `RUT_Sytheclaw` 0.2, `RUT_Barbslinger` 0.15, `RUT_FireWasp` 0.4, `RUT_Flamefang` 0.5 |

⇒ **0 wildAnimals rows are owed a move.** The split this item's step 2 asks for is finished.

🔴 **Two things to hand on, neither of them step 2's job:**
- Op 1 is a **`Replace` of the whole node**, so on the campaign world the 13 vanilla rows are
  *discarded*, not added to. That is the shipped intent ("replacing the deliberate core-only
  placeholder") but it sits against **§7 Q11a**, which requires the franchise-free mod to look *the
  same* as the campaign one. ⚠️ Flagged, not resolved — a roster row for the Pyrelands' own review
  sitting, per `BIOME_SPECIFIC_FAUNA_LAW_1` (no sweeping rule passes).
- **6 of the 12 are §7 Q10 movers** (`RUT_FireHawk`, `RUT_FurnaceBeast`, `RUT_Emberscythe`,
  `RUT_Sytheclaw`, `RUT_Barbslinger`, `RUT_FireWasp` — and `RUT_Flamefang` makes 7 of the 7 named
  in Q10, all Pyrelands). Q10 RULED 2026-09-21 that all seven move into their biome's RimMandrake
  mod renamed `RM_`; none is Star Wars IP. ⇒ Those rows eventually leave this patch and go inline
  in `RM_Pyrelands`. ⛔ **Do not do Q10 inside this ticket, and do not author against it.**

### 4. wildPlants split — ✅ nothing owed, and one trap

`RM_Pyrelands` `<wildPlants>` = **2 rows, both ours** (parsed): `RM_FE_Plant_EmberGrass` 9.0,
`RM_FE_Plant_Quickgrass` 3.8. Zero `RSW_`/`SW_`/`RUT_`, zero vanilla ⇒ **nothing moves to a patch.**

**Already-ruled rejections, cited not invented** — every non-grass vanilla row is already evicted
from this def and the def's own comment records it: `Plant_TreeDrago`, `Plant_Agave`,
`Plant_Dandelion` (owner 2026-09-14, *"the Pyrelands should be FILLED with grass… the only time it
isn't grass is when it's burned, and then it's ash"*, 692 live instances destroyed on PYRE_WALK3),
then `Plant_Bush` and `Plant_PincushionCactus` (owner, verbatim, *"No bush or pincushion in
pyrelands"*, `PYRELANDS_GRASS_SATURATION_1`, applied at `47aabd98c`). Generic grasses
`YellowGrass`/`YellowTallGrass`/`AB_HardyGrass` were evicted earlier (owner 2026-09-11, *"the grass
here has to be unique"*).

🔴 **`BiomeFlora_Ashkarr.xml:57` must NOT get a second op.** Its live op *replaces*
`ZBiome_Grasslands/wildPlants` with `RM_FE_Plant_Quickgrass` 4.0 **alone**. Pointed at
`RM_Pyrelands` it would **delete `RM_FE_Plant_EmberGrass`, the fuel bed the whole biome mechanism
rests on** — exactly the `BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1` failure, and exactly why the
Greentide is excluded from that file by name. ⛔ Leave it donor-only until the terminal paint.

### 5. Roster vs def diff

`design/Jawa/worldbuilding/biomes/rosters/the_pyrelands.json` (authored 2026-09-09): **14 fauna,
1 flora, 0 fish** (`fish.ruling`: *no fish — rain zero on 199 of 222 tiles*), 24 evictions,
18 `flora_purged`.

**Flora — the brief's question answered: YES, `RM_FE_Plant_Quickgrass` still exists.** The rename
at `84d42c63b` moved **only the BiomeDef defName**; the plant is still
`RM_FE_Plant_Quickgrass` in `Defs/ThingDefs_Plants/Quickgrass.xml`, texPath
`Things/Plant/RM_FE_Quickgrass`, art present (`RM_FE_QuickgrassA.png`, `...B.png`, plus
Sprout/Half stage sets and a Leafless set). ⚠️ Two diffs: the roster says commonality **4.0**, the
def ships **3.8**; and **`RM_FE_Plant_EmberGrass` is in the def at 9.0 and is not in the roster at
all** — the roster's own note excuses it (*"ember grass in ThingDefs_Plants remains the fuel
bed"*), so this is a roster-completeness gap, not a def defect. Art present (3 + 4 leafless PNGs).

**Fauna — every one of the 14 is wired, but 9 rows name a defName that no longer casts.** The
roster records the owner's *rulings* under the donor name he ruled on; `PYRELANDS_DONOR_PORT_4` and
`EMBERSCYTHE_MANTIS_REAUTHOR_1` re-authored them as ours at the same commonality, and
`WildAnimals_Pyrelands.xml` is the current mapping:

| roster def | commonality | cast today as | def of ours exists at |
|---|---|---|---|
| `Zeer` `Iriaz` `Nuna` `Gizka` `Anooba` `Orray` `Dalgo` | 0.6 / 0.5 / 0.5 / 1.0 / 0.35 / 0.25 / 0.18 | `RSW_Zeer` `RSW_Iriaz` `RSW_Nuna` `RSW_Gizka` `RSW_Anooba` `RSW_Orray` `RSW_Dalgo` | `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/` |
| `AA_FireWasp` | 0.4 | `RUT_FireWasp` | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsPortedFauna.xml` |
| `AA_Razorjack` | 0.2 | `RUT_Sytheclaw` | same file |
| `AA_Barbslinger` | 0.15 | `RUT_Barbslinger` | same file |
| `GR_Boomsnake` | 0.5 | `RUT_Flamefang` | same file |
| `GR_Mantistanis` | 0.05 | `RUT_Emberscythe` | `.../RUT_Emberscythe.xml` |
| `RUT_FireHawk` `RUT_FurnaceBeast` | 0.15 / 0.08 | unchanged | `.../RUT_PyrelandsFauna.xml` |

⇒ **0 roster fauna rows unwired; 9 roster rows carry a stale defName** (a roster-hygiene item, not
this ticket). ⚠️ **Art presence for the 14 fauna is UNMEASURED by this pass** — not checked, do not
read this as "present".

⚠️ **One open slot the roster itself flags**, `new_defs[2]`: *"burrower-grazer (dives under the
burn) — this slot stays OPEN for a third commission if the owner wants a dedicated grazer distinct
from Orray."* A question for him, not owed work.

### 6. Content to move into the mod

**Absorbed whole: `src/RimUtinni/PyrelandsMechanics` → `src/RimMandrake/Pyrelands`.** MEASURED: 31
files excluding `obj/`, of which **19 `.cs` — every one listed explicitly in
`Source/RimMandrake.Utinni.PyrelandsMechanics.csproj` (`EnableDefaultCompileItems false`, lines
52–70)**, assembly + namespace both `RimMandrake.Utinni.PyrelandsMechanics`, packageId
`mandrake.rut.pyrelandsmechanics`, `loadAfter` already includes `mandrake.rm.pyrelands`.
⚠️ Adding or moving a file in this assembly is always a **two-file** change.

**MOVES (§3a: works unchanged on a random planet with no Star Wars and no Ash'karr):**

| path | reason |
|---|---|
| `Source/PyrelandsTuning.cs` | every invented constant; holds `PyrelandsBiomeDefNames = {"ZBiome_Grasslands","RM_Pyrelands"}` (:29) — the "both defNames" fossil; keys on one name after the paint |
| `Source/MapComponent_BurnLine.cs`, `PyrelandsFireFront.cs` | the standing burn + burn-intelligence: a grass fire that walks, no franchise content |
| `Source/CompFireHawkSpread.cs`, `JobGiver_RUT_FireHawkCarryEmber.cs`, `JobDriver_RUT_FireHawkCarryEmber.cs` | ember-carrying is a generic animal behaviour; the creature itself is a §7 Q10 mover |
| `Source/CompFurnaceWarmthAura.cs`, `CompFurnaceBedIgnition.cs`, `CompFurnaceThermalCharge.cs`, `JobGiver_RUT_FurnaceThermalCycle.cs`, `Patch_FurnaceBeastHeatImmunity.cs` | the thermal circuit — a heat-hoarding megafauna mechanic, franchise-free |
| `Source/JobGiver_RUT_HarvestScorchFruit.cs` | harvesting our own `RM_FE_Plant_ScorchFruit` |
| `Source/PyrelandsMechanicsDefOf.cs`, `PyrelandsMechanicsMod.cs` | the DefOf + `Mod`/settings shell; folds into `RM_PyrelandsMod.cs`'s screen (§6a) |
| `Defs/HediffDefs/RUT_PyrelandsHediffs.xml`, `Defs/JobDefs/RUT_PyrelandsJobs.xml` | hediffs/jobs the comps above need; `RUT_` → `RM_` at the move |
| `Defs/ThinkTreeDefs/RUT_FireHawkThinkTree.xml`, `RUT_FurnaceBeastThinkTree.xml` | ride the Q10 creatures |
| `Patches/RUT_PyrelandsIgniters_Comps.xml` | attaches the comps above; retarget to the `RM_` creature names as Q10 lands |
| `Languages/English/Keyed/PyrelandsMechanics.xml` | the keyed strings for the above |

**STAYS IN UTINNI (fails §3a — names the campaign's people):**

| path | reason |
|---|---|
| `Source/PyrelandsFireRite.cs`, `LordJob_RUT_FireRite.cs` | the **Deep Desert Tribes'** fire rite — a campaign faction ritual |
| `Source/PyrelandsFactions.cs` | resolves the Tribes off vanilla `TribeCivil` as reskinned by `UtinniPatches/Patches/DeepDesertTribes.xml` — pure campaign wiring |
| `Source/IncidentWorker_FlameHarvest.cs`, `IncidentWorker_FireRaid.cs` | both are *"the Tribes answer the burn"*; they call `PyrelandsFactions` |
| `Defs/IncidentDefs/RUT_PyrelandsIncidents.xml`, `Defs/DutyDefs/RUT_PyrelandsDuties.xml` | the two incidents + the rite's duties |
| `Patches/RUT_Thornvine_Edible.xml` | patches a campaign plant that is not this biome's |

⇒ The kit splits **roughly 2/3 out, 1/3 stays**; the Utinni remnant keeps
`mandrake.rut.pyrelandsmechanics` (or folds into `mandrake.rut.patches`) and `loadAfter`
`mandrake.rm.pyrelands`, which it already declares.

⛔ **Nothing in `UtinniPatches/Defs/` moves.** The five Pyrelands creature defs
(`RUT_PyrelandsFauna.xml`, `RUT_PyrelandsPortedFauna.xml`, `RUT_Emberscythe.xml`) are **§7 Q10's
sweep, not this item's** — Q10 moves them, and doing it here would fork that ruling.

### 7. References to the donor / old defName across the repo

MEASURED with `grep -rl` then **each hit read**, and comment-vs-live separated by stripping
`<!-- -->` in Python (never `grep -c`).

**(a) Retarget outright — 2 files, the only genuinely owed step-4 work:**

| path | what |
|---|---|
| `src/RimStarWars/StructureInjectionsSW/Defs/TileMutatorDefs_Batch2.xml:44` | `RSW_HuntingLodge`'s `<biomeWhitelist>` lists `AridShrubland` + `ZBiome_Grasslands`. Add `<li>RM_Pyrelands</li>` — a **second** entry, the donor line stays until the paint |
| `src/RimStarWars/StructureInjectionsSW/validation.py:79` | `DEF_PAIRS` asserts that whitelist exactly; update in the same change or the validator fails |

**(b) Second op ALREADY PRESENT — nothing owed (verified by reading the xpaths):**
`UtinniPatches/Patches/AshStorms_Pyrelands.xml:90` (`PatchOperationAdd` onto
`RM_Pyrelands/baseWeatherCommonalities` beside the donor `Replace` ops),
`FlowWorks_SubsurfaceLiquid_Ashkarr.xml:116-139` (a whole second `PatchOperationFindMod` block for
`RM_Pyrelands`), `ManyWaters_RiverSteam_Ashkarr.xml:79+` (same shape).

**(c) Second op DELIBERATELY REFUSED — read the reason before "fixing" any of these:**
- `BiomeFlora_Ashkarr.xml:57` — would delete `RM_FE_Plant_EmberGrass` (see §4). ⛔
- `BiomeNames_Ashkarr.xml:111` — sets the donor's `<label>` to "the Pyrelands"; `RM_Pyrelands`
  already **ships that label natively** (:32), so a second op is a no-op.
- `BiomeDescriptions_Ashkarr.xml` — its own header records the decision: *"deliberately NOT ported
  onto ZBiome_Grasslands… `RM_Pyrelands` already existed"*. Nothing owed.
- `FishTypesStrip_NoFishBiomes.xml:234-242` — `RM_Pyrelands` has **no `fishTypes`** to strip.
- `AncientDangerGenSteps_AmbientDoctrine.xml:162` — adds `ScatterShrines` to the donor's
  `preventGenSteps`; `RM_Pyrelands` already ships `ScatterShrines` **and** `RockChunks` natively.
- `BiomeCastEvictions_WildBiomes.xml` (544 live donor refs), `AnimalBiomeDuplicates_Fix.xml` (2),
  `AnimalBiomeDuplicates_Generated.xml` (4), `ZZZ_BiomeWildAnimalDuplicates_Generated.xml` (8) —
  all three are **generated** and all operate on the **animal side** (`race.wildBiomes`) or on
  duplicate records inside the donor def. **Zero animal defs in the repo name `RM_Pyrelands` in
  `wildBiomes`** (MEASURED: the full `grep -rl RM_Pyrelands src/` hit list contains no
  `ThingDefs_Races` file), so the load-time padder has nothing to materialise into our def and
  these files are structurally unnecessary for it. ⛔ Do not regenerate them for `RM_Pyrelands`.
- `JawaWorld_BiomeMix.xml:102` — `biomeBlacklist` for the **source world Ash'karr was painted
  from**, worldgen-gated and already spent. Leave.

**(d) Comment/prose only — ⛔ do not touch:** `src/RimMandrake/FlowWorks/Source/ManyWaters/
RiverSteamHook.cs:15-20`, `src/RimMandrake/bridgetools/JawaBench.BridgeTools/
JawaBenchModSettingsFieldTools.cs:11`, `AnoobaDrawSize_Fix.xml:11-13`,
`AshkarrWeatherSuite/validation.py:47-49,138`, `AshkarrWeatherSuite/Defs/WeatherGeometryDefs/
WeatherGeometryDefs_Ashkarr.xml:28`, `AshkarrWeather_FolkSigns.xml:23-26`,
`SWBestiary/.../RSW_Nuna.xml:11`, `RSW_Orray.xml`, `UtinniPatches/Defs/ThingDefs_Races/
RUT_Emberscythe.xml`, and the eight `src/RimMandrake/Utils/ashkarr_*.py` / `worldview.py` /
`planet_portrait.py` / `build_landmark_density_sheet.py` world-tooling scripts (they read the
**record** CSV's donor name; the terminal paint updates them, not this ticket).

### 8. Mechanics/kit state

| mechanic | state | where |
|---|---|---|
| ash ladder (4 rungs), scorchable ground clones, firebreak | ✅ SHIPPED | `mandrake.rm.pyrelands`, `Defs/TerrainDefs/` |
| black rain / ash fall / cinderfall, fulgurite, loose-ash filth, scorch-fruit pod + yield, firefoam sprayer | ✅ SHIPPED | same mod, `FireEcologyHook.dll` |
| scorched ruins at mapgen, plant growth stages, wild-plant allowlist, density enforcer | ✅ SHIPPED | `FireEcologyHook.dll`; `PYRELANDS_SCORCHED_RUINS_1`, `PYRELANDS_FLORA_LEAK_1` both closed |
| burn-line presence + burn intelligence, fire-hawk twig, furnace-beast thermal circuit, flame harvest, fire raid, fire clock, fire rite | ✅ SHIPPED | `mandrake.rut.pyrelandsmechanics` (`PYRELANDS_MECHANICS_1` **done**, `6946c187`) |
| river steam | ⚠️ wired, visual unverified | `mandrake.rm.flowworks` + `ManyWaters_RiverSteam_Ashkarr.xml`; `RIVER_STEAM_ANIMATION_1` BLOCKED on a render-void, **not on this ticket** |
| fire-hawk flight **animation** | ⛔ UNBUILT, and the built version was REVERSED | `FIREHAWK_FLIGHT_BEHAVIOR_1` — needs the directional flip-book, not the Spastic wing tree |
| Mod Settings master toggle + cross-biome section | ⛔ UNBUILT | §1 above; 7 per-mechanic toggles DO exist |

⇒ **Everything this ticket needs already exists in code.** ⛔ Do not wait on
`FIREHAWK_FLIGHT_BEHAVIOR_1`, `RIVER_STEAM_ANIMATION_1`, `BARBSLINGER_SCORPION_REDESIGN_1` or Q10.

### 9. Dependencies & items building INTO this mod

| item | `rimflow show` state | relation |
|---|---|---|
| `PYRELANDS_GRASS_SATURATION_1` | `ready BLOCKED … needs offline` | def side CLOSED (`47aabd98c`); what is left is live-only (clear surviving `Plant_Bush`/`Plant_PincushionCactus` instances, look at ground fill) and rides `COLD_LOAD_RUN_SHEET_4`. **Lands later; blocks nothing** |
| `SW_FAUNA_NEVER_IN_RM_TIER_1` | `proposed … needs offline` | Q11's 97 rows. **Already satisfied for this biome** (§3) — this row is evidence, not work |
| `FIREHAWK_FLIGHT_BEHAVIOR_1` | `doing … needs offline` | v1 reversed; lands in whichever mod owns the creature after Q10. **Does not block** |
| `FURNACEBEAST_WORLD_MIGRATION_1` | `proposed … needs offline` | world-leg ThinkTree work on a Q10 creature. **Lands later** |
| `BARBSLINGER_SCORPION_REDESIGN_1` | `doing … needs game-up` | art + def redesign of a Q10 creature. **Lands later** |
| `RIVER_STEAM_ANIMATION_1` | `doing BLOCKED … needs offline` | visual only, blocked on a render-void. **Does not block** |
| `MOD_OPTIONS_RETROFIT_1` | the §6 authority | the master toggle + cross-biome gap in §1 is **this ticket's** step 1 |
| `WORLD_REMAKE_FINAL_STEP_1` / `BIOME_PAINT_ONCE_AT_THE_END_1` | paint list / paint-once law | the paint-list row exists but is stale (§1) |
| `BIOME_MOD_SPLIT_EXECUTION_1` | `proposed` | parent |

### 10. Blockers

**None.** Steps 1, 2, 4 and 6 are all offline and can start immediately. Step 5 is Desktop-only and
is not a blocker of 1–4. Nothing waits on the owner: §7 Q1–Q11a are all RULED.

### 11. Concrete step plan

**1 — scaffold (finish it).** `src/RimMandrake/Pyrelands/About/About.xml`:
- packageId stays `mandrake.rm.pyrelands` ✅.
- `loadAfter` — add **only what the moved content actually references.** MEASURED: the 5 existing
  `.cs` files use `HarmonyLib`, `RimWorld`, `Verse`, `UnityEngine` and **no** shared-library
  namespace; the 19 absorbed `.cs` files likewise (namespace `RimMandrake.Utinni.
  PyrelandsMechanics`, no `RimMandrake.EnvironmentalHazards`/`CreatureBehaviors`/`FlowWorks`
  reference). ⇒ **`loadAfter` gains nothing from §2d.** Keep `brrainz.harmony`, `Ludeon.RimWorld`.
  ⚠️ `mandrake.rm.flowworks` references `RM_Pyrelands` **by string, in a comment only**, and the
  river-steam extension is patched on from the Utinni side — the dependency runs the other way.
- `Source/RM_PyrelandsMod.cs` — add the §6a **master toggle** (`pyrelandsEnabled`, default on, the
  BiomeDef still loads) and the **cross-biome block** (`crossBiomeEnabled` / `crossBiomeEverywhere`
  / `crossBiomeBiomeList` / `crossBiomeCoverage`, all default off), modelled on
  `src/RimMandrake/Greentide/Source/RM_GreentideMod.cs`. Existing 7 toggles
  (`fulgurite`, `ashDusting`, `scorchFruit` + cap, `ashfallAccumulation` + rate,
  `biomeGeneration` [label worldgen-only], `wildPlantAllowlist`, `plantGrowthStages`,
  `scorchedRuins`) stay with their shipped defaults, and gain one per absorbed mechanic:
  `burnLineEnabled`, `fireHawkSpreadEnabled`, `furnaceThermalEnabled`, `fireClockEnabled`.
- Dry run `deploy_custom_mods.py --mod Pyrelands`, read the plan, then `--apply`.

**2 — copy the content in.** Four concrete jobs, all offline:
- 🔴 `git mv src/RimMandrake/Pyrelands/Textures/World/Biomes/RM_FE_Pyrelands.png` →
  `RM_Pyrelands.png`. One file; the world-map tile is broken until this lands.
- Move the 11 MOVES rows of §6 into `src/RimMandrake/Pyrelands/{Source,Defs,Languages}`, renaming
  `RUT_` → `RM_` on the hediff/job/thinktree/keyed defNames, and add each `.cs` to
  **`Source/FireEcologyHook.csproj`'s `<ItemGroup>`** — `EnableDefaultCompileItems` is `false`, so
  an unlisted file compiles into nothing with no error.
- Rename `namespace RimMandrake.StarWars.FireEcology` → **`RimMandrake.Pyrelands`** across all
  `.cs`, and with it the two XML class strings in `Defs/BiomeDefs/Pyrelands.xml:33` (`workerClass`)
  and `:56` (`modExtensions`), plus every `Class=` in the plant defs that names
  `PlantGrowthStages`/`Plant_GrowthStaged`. ⚠️ A missing modExtension type **discards the whole
  def**, silently — change XML and C# in one commit and rebuild.
- Leave `<wildAnimals>` and `<wildPlants>` **exactly as they are** (§3, §4).

**3 — N/A.** Donor def, nothing to freeze (see the §4c box).

**4 — retarget.** Exactly two files: `src/RimStarWars/StructureInjectionsSW/Defs/
TileMutatorDefs_Batch2.xml` (add `<li>RM_Pyrelands</li>` beside the donor) and
`.../StructureInjectionsSW/validation.py:79`. Then fix the **stale paint-list rows**
(`infrastructure/state/facts/biome_paint_list.md:52,59,73,108,109` — `RM_FE_Pyrelands` →
`RM_Pyrelands`). ⛔ Touch nothing in §7(c) or §7(d).

**5 — prove it loads (Desktop).** Minimal list + `mandrake.rm.pyrelands` +
`mandrake.rut.pyrelandsmechanics` + `mandrake.rut.patches` + **all five expansions**. Zero new
`Config error` in `Player.log` (grep it — `validate_patch.py` cannot see config errors);
`validate_patch.py src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml --live --defs`;
then confirm from a **post-load def dump** that all 12 rows landed (an unmatched
`PatchOperationAdd` is silent). Quicktest on a **scratch** world with the landing tile set to
`RM_Pyrelands` via `jawa/world_*` at `Page_SelectStartingSite` — ⛔ never the canonical save.
Also confirm the world-map tile now draws (the texture fix).

**6 — commit & push**, explicit paths, one commit; the message says the donor was carrying the
tiles and what the twin got wrong. Append/fix the `RM_Pyrelands` row on
`WORLD_REMAKE_FINAL_STEP_1`'s paint list.

### False statements found elsewhere — for BENCH

| path:line | says | correction |
|---|---|---|
| this item's header, ⚠️ Live trap ¶ | *"built and NOT deployed — deploy before testing"* | **All four affected mods are `in sync`** (deploy dry run, this pass). Delete the paragraph |
| `infrastructure/state/facts/biome_paint_list.md:52` (and 59, 73, 108, 109) | keys the Pyrelands row on **`RM_FE_Pyrelands`** | the defName is `RM_Pyrelands` since `84d42c63b`, 2026-09-21 |
| `design/RimMandrake/biome_mod_architecture.md:295` (§4c) | *"every op targeting `ZBiome_Grasslands` — **the one op in `WildAnimals_Pyrelands.xml`**"* | that file has had **zero** donor-targeting ops since `84d42c63b`; all three target `RM_Pyrelands` |
| `design/RimMandrake/biome_mod_architecture.md:290,302-306` (§4c heading + defects) | heads the row `RM_FE_Pyrelands` and calls the rename future work | the rename is **done**; what survives is the `.StarWars.` namespace and the `RM_FE_` infix on the other **21** defs |
| `design/Jawa/worldbuilding/biomes/the_pyrelands.md:19-20` (FROZEN) | *"the FireEcology mod already built at `src/RimStarWars/FireEcology/`"* | that path **does not exist**; the mod is `src/RimMandrake/Pyrelands`. (Its `## Owed` "FireEcology deploy collision" is also discharged — MEASURED: one folder, no collision) |
| `infrastructure/state/items/RIVER_STEAM_ANIMATION_1.md` BLOCKED note | *"`RM_FE_Pyrelands` now carries `RiverSteamBiomeExtension` live"* | stale defName — `RM_Pyrelands` |

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.pyrelands`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_Pyrelands` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_Pyrelands`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.pyrelands`; do not edit here."* From that moment
   every content fix lands in `RM_Pyrelands` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_Pyrelands` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_Pyrelands` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.pyrelands` exists, deploys, and loads clean carrying `RM_Pyrelands` with its own content and its own
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
