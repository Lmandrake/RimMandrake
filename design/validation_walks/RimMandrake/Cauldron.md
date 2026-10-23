# RimMandrake: The Cauldron — validation walk
subject: src/RimMandrake/Cauldron  (packageId `mandrake.rm.cauldron`)
deps: none required (Genetic Rim, Alpha Animals, Alpha Memes, Horrors rows are individually `MayRequire`); ships composed inside the Baroque Biomes mod (Biomes.compose.json, wave 0)
list: baroque_wave0
status-hint: a low, wet-black forest in permanent dusk over gas-breathing ground — four owned weathers (scatter-dusk, vapour bank, dewfall, vent bloom), the vent bloom's metal load, metal-sweating trees with an assay line, the vexxiss (fire warden, poisons water, shears vexxith), the suush (floats, detonates when shot), nettles that colonise toxic shores; script = `src/RimMandrake/Cauldron/validation.py`, plan = `northstar_plan.py`, selftest = `selftest_cauldron.py`

## must be true
Every line ends in `→ chain.component` (a suite component that reads the state back) or `→ UNCOVERED: why`. Sources: the mod's About.xml description, `RM_CauldronMod.cs`, the mechanic `.cs` headers, the def XML headers, `CAULDRON_RULED_CONTENT_1`, `CAULDRON_MECHANICS_BUILD_1`, `CAULDRON_GPT_ENRICHMENT_1`, `SUUSH_CAULDRON_DRIFTER_1`, `CAULDRON_ENRICHMENT_LIVE_PROOF_1`, `design/Jawa/worldbuilding/biomes/cauldron.md`.

Load and wiring
- Every def this mod ships (4 weathers, the metal-load hediff, 2 soils, 2 items, 11 plants, 4 creatures and their 4 kinds, the biome) resolves in the live game; none is silently discarded for a missing comp or extension type. → load.defs_resolve
- The mod's six runtime classes (settings, biome worker, vent-bloom map component, condensate-gardens map component, vexxiss comp, metal-yield comp) resolve inside the game, ride in `mandrake.rm.biomes`, and the loaded DLL is the file on disk. → load.types_resolve
- `RM_Cauldron` runs its own four weathers (scatter-dusk standing, vent bloom rare) and carries no stock Clear, Fog, rain or snow commonality (the biome never rains, snows or clears). → load.biome_weather_table
- `RM_Cauldron` has `animalDensity` above 0 and its four owned natives (suush, vexxiss, zisska, eskith) plus all 11 owned plants are spawning (not zeroed, not absent) in its resolved roster. → load.biome_roster
- The biome places itself with the mod's own `RM_BiomeWorker_Cauldron` (never the donor BiomesPlus worker) and grows on its own two soils, plain below fertility 1.0 and rich above. → load.biome_worker_and_terrain
- The raven nettle carries `RM_CondensateHabitatExtension` (the colonising pass reads it). → load.nettle_habitat_wired
- The biome worker scores tiles, and rarity 0 means the Cauldron never generates on a new planet. → UNCOVERED: `BiomeWorker.GetScore` needs a Tile + PlanetTile and no bridge tool calls it; only the worker class (load.biome_worker_and_terrain) and the setting's read/write (settings.biomeRarityFactor_roundtrip) are checked. Proposed tool: CAULDRON_WORKER_PROBE_1
- All 11 Mod Settings fields exist and read their shipped defaults; a nonexistent field fails loudly. → settings.defaults
- The log carries no Cauldron error, no Config error and no cross-reference error naming one of this mod's defs (the 2026-09-30 cold load's Config errors on creature tool groups, plant nutrition and trainability were this class). → log.log_clean

The four weathers
- Each weather sets and reads back as itself. → weather.weathers_selectable
- None of the four rains, snows or storms sand, and every one carries wind (no calm). The vent bloom is a bad weather that leaves vanilla `doToxicBuildup` off (its only tax is the metal load, no double tax); scatter-dusk is not bad. → weather.weather_defs_laws
- The vent bloom's overlay, the dusk light, the missing shadows. → UNCOVERED: visual; left to the judge pass (debug_process §4)

The vent bloom's metal load
- Under the vent bloom, an outdoor unroofed colonist gains `RM_VentMetalLoad` at a positive severity on the exposure tick (every 3451 ticks, after the weather transition ends). → bloom.bloom_loads_exposed
- The same colonist does not also gain vanilla `ToxicBuildup`. → bloom.bloom_no_double_tax
- A colonist inside a roofed room does not gain it. → bloom.bloom_spares_roofed
- A native animal of the map's biome (read live from its resolved roster) does not gain it while a non-native animal beside it does. → bloom.bloom_spares_natives
- With `ventBloomExposureEnabled` off no one gains it; the bloom is weather only. → bloom.bloom_toggle_off
- `ventBloomExposureFactor` 2.0 doubles the severity one exposure tick adds. → bloom.bloom_factor_scales
- Toxic-resistant gear keeps the load off. → UNCOVERED: needs a worn toxic-resistant suit (no cheap fixture; ToxicResistance/ToxicEnvironmentResistance math is vanilla's own copied formula, source header of `RM_VentBloomExposure.cs`)
- The load sheds slowly and its stages cripple but never kill. → UNCOVERED: a multi-day decay; only the def resolves (load.defs_resolve)

Metal-infused trees
- A full-grown martyr tree harvested by a colonist pays about 6 steel beside its wood. → yield.harvest_pays_metal
- `metalYieldFactor` 2.0 doubles it. → yield.yield_factor_scales
- With `metalYieldEnabled` off the harvest pays wood only. → yield.yield_toggle_off
- A twisting thornwood's inspect text reads its assay grade: unripe below harvestMinGrowth, fair at mid growth, lode when full grown at about 12 steel. → flora.assay_grades
- With `assayGradeEnabled` off the assay line is gone. → flora.assay_toggle_off
- `metalYieldFactor` 2.0 doubles the steel the assay line promises. → flora.assay_factor_scales
- Every owned plant (the two trees and nine others) stands when placed. → flora.flora_spawns

The vexxiss
- Wading in shallow water turns the water it stands in, and the cells touching it, to toxic water. → water.water_poison_on
- A letter "Vexxiss poisoning water" arrives when it first does so on a map with a colonist. → water.water_letter_arrives
- A second poisoning by the same vexxiss within a day raises no second letter (and only counts if the poisoning DID repeat). → water.water_letter_cooldown
- With `vexxissWaterLetter` off a new vexxiss poisons water and no new letter arrives. → water.water_letter_toggle_off
- With `vexxissPoisonsWater` off a vexxiss wades and no cell turns toxic. → water.water_poison_toggle_off
- A vexxiss near a standing fire takes a BeatFire job. → fire.fire_warden_beats_fire
- With `vexxissFireWardenEnabled` off it does not. → fire.fire_warden_toggle_off
- It attacks whoever lit the fire, and a tame vexxiss never attacks its own faction. → UNCOVERED: no bridge tool sets `Fire.instigator` (proposed tool CAULDRON_FIRE_INSTIGATOR_TOOL_1); `vexxissAttacksIgniter` exists, defaults on and is writable (settings.vexxissAttacksIgniter_roundtrip)
- It carries the fire-warden/poison comp and a vexxith shear comp (woolDef `RM_Vexxith`) and NO explosion comp alive or dead (owner: "too many exploding giant beasts"). → items.suush_and_vexxiss_comps
- Shearing a tame vexxiss yields vexxith every 60 days. → UNCOVERED: 60 in-game days of fullness ticking on a tamed animal; only the comp is read (items.suush_and_vexxiss_comps)
- It inhales a vent / pries at gas-tap scaffolds / shears wild. → UNCOVERED: not built (About.xml: "Not yet built"); no check can exist yet

The suush, zisska, eskith
- Each of the four kinds spawns a living wild pawn of that kind. → fauna.fauna_spawns
- The suush can float (`MaxFlightTime` above 0, `canEverFly`). State read only; flight in the air is never live-tested unattended. → fauna.suush_can_fly
- The suush carries `CompProperties_Explosive`. → items.suush_and_vexxiss_comps
- A suush hit by melee damage lives. → suush.suush_ignores_melee
- A suush hit by a Bullet detonates (is gone within 400 ticks) while the melee-hit one beside it lives. → suush.suush_detonates_when_shot
- The suush is docile and tamable. → UNCOVERED: taming is a work-job chain against Wildness 0.5 (statistical); defs only
- A zisska butchers into steel and its meat is `RM_ZisskaMeat`, which gives `ToxicBuildup` when eaten. → items.zisska_yields_and_toxic_meat
- A real butchering of a zisska pays that steel. → UNCOVERED: needs a built butcher table + bill (no cheap fixture yet)
- While the vents falter ahead of a vent bloom, a wild eskith holds still (`Wait_MaintainPosture`); with `faunaHushEnabled` off it does not. → vents.fauna_hush_in_falter

Vexxith ignores acid (VEXXITH_CLOSED_LOOP_BUILD_1)
- `RM_Vexxith` carries `RM_AcidImmuneExtension` and is both Metallic and `RM_VexxithPlate`; `RM_VexxithDoor` accepts `RM_VexxithPlate` and nothing else; the mod's patch marks vanilla `AcidBurn` as acid. → load.acid_wiring_shape
- A vexxith wall and a vexxith door hit by AcidBurn keep every hit point while a steel wall beside them loses some (the control). → acid.vexxith_acid_proof
- With `vexxithAcidImmunityEnabled` off a vexxith wall loses hit points to the same AcidBurn. → acid.vexxith_acid_toggle_off
- Warscar's `RM_BloomAcid` (source folder Scarlands, composed beside this biome) is marked acid too, by a patch guarded on the def existing. → load.acid_wiring_shape
- `vexxithDoorEnabled` exists, defaults on and is writable (it hides the door from the architect menu at the next launch). → settings.vexxithDoorEnabled_roundtrip

Nettles on toxic shores
- Raven nettles colonise land beside toxic water: some at map creation, more over the following weeks. → UNCOVERED: the live pass samples 40 random cells per 2500 ticks over the whole map and only runs where the map biome's roster names the nettle, so it needs days of ticks and a Cauldron-biome map; only the wiring is read (load.nettle_habitat_wired). Proposed tool: CAULDRON_CONDENSATE_SWEEP_HOOK_1
- `condensateGardensEnabled` exists, defaults on and is writable. → settings.condensateGardensEnabled_roundtrip
- `biomeRarityFactor` exists, defaults to 1 and is writable. → settings.biomeRarityFactor_roundtrip

Enrichment visuals (CAULDRON_ENRICHMENT_VISUALS_1)
- During dewfall, chemical-dew beads (`RM_Filth_DewBeads`) form on unroofed outdoor land outside the home area and evaporate within a day. → UNCOVERED: needs hours of locked `RM_Dewfall` over unroofed non-home ground and a filth count; no chain written yet (the def itself resolves under load). `dewfallBeadsEnabled` exists, defaults on and is writable. → settings.dewfallBeadsEnabled_roundtrip
- During dewfall, accent plants with an installed dew variant swap to it and swap back when it lifts. → UNCOVERED: dormant until dew-variant art exists (none installed), and appearance. `dewfallSaturationEnabled` exists, defaults on and is writable. → settings.dewfallSaturationEnabled_roundtrip
- Fair, rich and lode thornwood and martyr trees carry light or heavy metal flecks. → UNCOVERED: dormant until the two fleck overlays exist (none installed), and appearance. `assayFlecksEnabled` exists, defaults on and is writable. → settings.assayFlecksEnabled_roundtrip
- A walking vexxiss lays prints on the CreatureBehaviors footprint grid that clear after about a day and name their maker on hover. → UNCOVERED: no bridge tool reads the grid's records or the Cauldron print ledger. `vexxissPrintsEnabled` exists, defaults on and is writable. → settings.vexxissPrintsEnabled_roundtrip

Vent gas, the gas tap and the ruin kit (CAULDRON_MECHANICS_BUILD_1 parts 3/4/5)
- A breathing vent fills the air around it with vent gas (its own gas type: the vent's line reads cells and a peak), and none of it reads as vanilla tox gas until it burns; with `ventGasEnabled` off the cloud thins. → gas.vent_gas_emits
- A fire beside a thick cloud burns it (the vent's burned count rises) and leaves vanilla tox gas behind; with `ventGasIgnites` off the same fire burns none. → gas.vent_gas_burns_toxic
- A gas-tap scaffold on a vent caps it (the vent reads capped) and banks condensate into a tank touching it; with `gasTapBanksCondensate` off it banks nothing more. → gas.gas_tap_caps_and_banks
- A wild vexxiss drinking at a capped vent damages the scaffold; with `vexxissPriesTaps` off it drinks without harming it. → gas.vexxiss_pries_tap
- A corroded filter rig dresses its own site on first spawn: battered tanks and corroded pipe beside it. → gas.ruin_kit_dresses
- The cloud's drift heading turns once a day and is seeded per map (read from the live assembly, not from this script's model). → drift.gas_heading_is_daily_and_map_seeded
- Wind sets the drift: calm air does not drift, a stronger wind drifts at least as often, capped at 0.75. `ventGasDrifts` exists, defaults on and is writable. → drift.gas_drift_chance_follows_wind
- The cloud's physical displacement downwind (INFERRED from the two lines above and the kernel selftest's drift-conserves fuzz). → UNCOVERED: no bridge tool reads a vent-gas cell's density; the vent's inspect line counts cells in a radius, not a direction. A static readout (centroid) in the mod DLL would close it. → settings.ventGasDrifts_roundtrip
- With `ventGasToxicSmoke` off the gas burns clean. → UNCOVERED: the ON arm's vanilla tox residue masks the OFF arm unless the suite waits it out. → settings.ventGasToxicSmoke_roundtrip
- A freshly generated Cauldron map holds a corroded filter rig (the ruin scatter runs at mapgen; `ruinKitEnabled` exists, defaults on and is writable). → ruins.ruin_rig_at_mapgen
- That rig's site is dressed at mapgen: battered tanks (one holding toxic water), corroded pipe, and nothing on the rig's interaction cell. → ruins.ruin_site_dressed_at_mapgen
- Studying the rig unlocks `RM_FilterWorksResearch`. → UNCOVERED: the study is an analysis job the bridge cannot order; the research and the build are skipped by building the works directly, so the works rows prove the machine, not the unlock path. The defs resolve under load (load.defs_resolve).
- A powered, cartridge-fed Filter-Works with a condensate tank touching it refines the condensate into vent reagent (and with no cartridge makes none). → works.works_refines_condensate
- The same works turns toxic water into fresh water in a second tank. → works.works_filters_toxic_water
- Without power the works stops converting. → works.works_stops_without_power
- Oomo's grudging shrine (Utinni layer, patched into the kit's shrine slot) stands beside each rig on a Cauldron map; usability as a Natural meditation focus is INFERRED from the def. → ruins.oomo_shrine_at_mapgen

## the walk
1. [B] Tier: `python3 src/RimMandrake/Utils/modset_builder.py --tier baroque_wave0 --apply` (Windows-side seat only), deploy the composed mod (`deploy_custom_mods.py --compose biomes --apply`), launch via Steam, wait for `Bridge token:` in Player.log, start a quicktest map (150 cells or larger). One command does all of it: `python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod Cauldron --tier baroque_wave0 --plan src/RimMandrake/Cauldron/northstar_plan.py --compose`.
2. [B] `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Cauldron --plan src/RimMandrake/Cauldron/northstar_plan.py` → results JSON in `Transient/northstar/`.
3. [L] Player.log after load has no `Config error` naming an `RM_` Cauldron def and no cross-reference error naming one   # load-time
Offline: `python3 src/RimMandrake/Cauldron/selftest_cauldron.py` runs the suite against a scripted fake game: healthy, then once per mod behaviour broken, each of which must turn exactly its own component red.

## north star
state: DRAFT
validated-hash:

Seeded 2026-10-01 by an agent (NORTH_STAR_WALK_AUTHORING_1) from this walk's
`## must be true` and the mod's shipped sprites, defs and settings, on the owner's
ruling that day: *"You are mostly seeding the field right now with reasonable
initial guesses for refinement later through debugging needs or live feedback."*
Every line is an agent guess for him to accept, edit or cut; `(guess)` marks the
least certain. `### the experience` is his to dictate.

### the experience  (OWNER'S WORDS)
"The sky roils with eternal anger and lightning yet no rain ever falls. Water is acid, animals are minerals, and life twists under the load… including you."
(typed by the owner, 2026-10-20)

### must show

**Permanent dusk**
- [ ] `cauldron_reads_wet_black_dusk` — an `RM_Cauldron` map at noon reads as a low,
      wet-black forest in dusk light, never full daylight.
- [ ] `cauldron_vent_bloom_reads_as_gas` — under the vent bloom the air visibly
      thickens with a coloured haze. (guess)
- [ ] `cauldron_no_rain_or_snow` — no rain, snow or clear-sky day is ever on
      screen.

**Metal-sweating trees and the soils**
- [ ] `cauldron_trees_read_metallic` — the martyr and thornwood trees read as
      sweating metal, distinct from vanilla trees. (guess)
- [ ] `cauldron_soils_read_dark` — the biome's two soils read as dark, gassy ground,
      the rich one visibly different from the plain one. (guess)

**Natives**
- [ ] `cauldron_natives_distinct` — the suush (`RM_Suush`), the vexxiss
      (`RM_Vexxiss`) and the other two natives read as four different animals.
- [ ] `cauldron_suush_floats` — the suush reads as floating above the ground, not
      walking. (guess)

### cannot show

- [ ] `cauldron_never_bright_day` — a Cauldron map in bright noon light with hard
      shadows.
- [ ] `cauldron_never_magenta` — a magenta square for any plant, creature or
      item.

## anti-guessing notes
- RULED OUT: "`jawa/get_defs` returns `wildAnimals`/`wildPlants` for a BiomeDef" — they are private (`Scalars()` reads public fields only); the roster is read with `jawa/biome_probe` (`findResults[].state`: spawning / zeroed / absent), and that probe is itself sanity-checked with an absent name (JawaBenchTerrainTools.cs, `jawa/biome_probe` header).
- RULED OUT: "`baseWeatherCommonalities` comes back as rows without `deep`" — a list of non-scalar objects comes back as bare type names unless `deep=true`; load.biome_weather_table passes it and records UNMEASURED if the rows are not dicts.
- RULED OUT: "the vent bloom hediff appears the moment the weather is set" — `RM_MapComponent_VentBloomExposure` runs only at `TicksGame % 3451 == 0` and only once `TransitionLerpFactor` is 1, so the bloom chain waits out the transition, then sets the clock to 5 ticks before the next multiple and steps 40 (`_next_interval_jump`). A reading taken before that is a harness error, not a mod defect.
- RULED OUT: "a map in a different biome breaks the native-animal check" — the check reads THIS map's resolved roster with `biome_probe` and picks a native and a non-native stock herbivore from it, and records UNMEASURED when the map offers no such pair.
- RULED OUT: "`list_pawns` hides invisible hediffs" — `RM_VentMetalLoad`'s first stage has `becomeVisible` false; the tool lists every hediff in `hediffSet.hediffs` with severity (source: JawaBenchTerrainTools.cs ListPawns), so the trace stage is readable. The health block is NESTED (`row['health']['hediffs']`), which the helper `_hediff` reads.
- RULED OUT: "the water letter can only be tested once per run" — the cooldown is per vexxiss (`lastWaterLetterTick`, fresh -999999 on a new animal), so each arm spawns its own vexxiss in its own pond and the cooldown arm re-lays shallow water under the SAME animal.
- RULED OUT: "the Suush needs a gun to detonate" — `startWickOnDamageTaken` matches the DamageDef, so `jawa/damage` with `Bullet` starts the wick; the Cut-hit control suush is the guard that melee does not.
- UNPROVEN live shapes (first run settles them; each reads `UNMEASURED`, never PASS, when absent): `site_state.weather.transition` as a 0..1 number; `get_defs deep=true` rendering `race`, `ingestible`, `butcherProducts` and `outcomeDoers` as dicts with the field names used; `get_def` `comps[].fields.woolDef` and `extra.terrainsByFertility`; the `Harvest` JobDef accepted on a tree (the chain falls to UNMEASURED if no wood lands in 5000 ticks); `list_things defName=Fire` counting fires; the job name `BeatFire` in `site_state` rows; `letter_list` labels.
- MOD (live 2026-10-23, fixed 637645762): "vent flowers are no denser near vents than in control rects" was real. The three vent flowers are also on the biome's wild roster (0.5 / 0.4 / 0.08) and the gardens' `MapGenerated` runs after the plant genstep, so the ring roll refused nearly every (already planted) ring cell. A mapgen ring roll now replaces a wild non-tree plant (`RM_VentKernel.RingPlantAction`); `vent_gardens.vent_flowers_ring_vs_control` reads ring vs far-control density and is UNMEASURED on a map generated before the fix (`ringPass=0`, e.g. `RM_TestSite_cauldron_v2`).
- ASSUMED (source comment, not measured here): a wild vexxiss awake at the moment of the fire scan. The chain fills Food and Rest first; a sleeping animal would read as a missing BeatFire.
- Not driven because no cheap fixture: the biome worker's placement score (CAULDRON_WORKER_PROBE_1), nettle colonising (CAULDRON_CONDENSATE_SWEEP_HOOK_1), the igniter attack (CAULDRON_FIRE_INSTIGATOR_TOOL_1), a Cauldron-biome map, the Utinni roster layer (UtinniPatches owns it).
