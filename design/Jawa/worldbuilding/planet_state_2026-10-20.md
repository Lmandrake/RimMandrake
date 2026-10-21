# State of the planet, end of 2026-10-20 (read this cold)

Written by FOUNDRY (documentation pass, offline) from the repo, the ledger and the files in the game's Mods folder.
Nothing here was measured in a running game by this pass. Every row cites a file or a sha; **UNMEASURED** marks what
the evidence does not reach. Repo paths are relative to the seat clone `/home/mandrake/rm/foundry`
(mirror `D:\Luke\dev\RimMandrake`). Saves live in
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\`. Agent scratch is
`D:\ClaudeWork\rimmandrake\scratch\`.

Source documents: `design/Jawa/worldbuilding/{worldmap_in_game_audit,mountain_system,parity_causes,world_paths_readable}_2026-10-20.md`,
`design/RimMandrake/{world_physics_audit,glow_consumers,factions_unwanted_and_lingering,flier_frame_registration_audit}_2026-10-20.md`,
`design/RimStarWars/head_envelope_2026-10-20.md`, `Transient/wme_analysis_2026-10-20.md` (untracked, ~14 days).

**Deploy-state key and how it was measured (2026-10-20, about 19:55 local).** A dry-run
`deploy_custom_mods.py --compose biomes` showed exactly one differing mod file: `RimMandrake.Biomes.dll` (+ `.srchash`). The
game's copy has mtime 19:38 and contains the strings `worldSoftHills` and `RM_WorldPaths` but **not** `RM_WorldLandmarks`/
`worldSoftLandmarks`; so everything committed up to the soft-hills commit `aba208ccc` is on disk and the landmark commit
`caba4437a` is not. `deploy_custom_mods.py --mod StarWarsRaces` reported "in sync (1111 files)". `--mod UtinniPatches` showed
`Patches/FactionSlate/BannedFactions.xml` differing. **"On disk" is not "loaded":** no game load after 19:38 is recorded, so
anything marked *deployed, not yet loaded* is UNMEASURED live. Re-run the dry runs; they cost nothing.

## 1. Mechanisms and settings

"Card" = the owner chose an option on a question card; "said" = his words in chat. Toggles are Mod Settings entries; "[now]"
means it takes effect without a restart. Verify ids are ledger items (`python3 src/RimMandrake/rimflow/cli.py show <ID>`).

### 1a. How the planet looks

| mechanism | what it is, file | Mod Settings toggle, default | owner ruling | deploy state | verify item |
|---|---|---|---|---|---|
| Sea-floor layer hidden from the planet | Harmony postfix on `WorldDrawLayer.Visible` hides a coplanar draw layer when another layer on the same sphere is selected; second postfix ignores hidden coplanar terrain layers when deciding "dirty" (fixes endless GeneratingPlanet). `src/RimMandrake/DivingInteraction/Source/Patch_SeabedLayerCoplanarHide.cs`; `a69ed8110`, `6a182f352`, `03d0f5d41` | none (no toggle found) | said 2026-10-20 "The honeycomb looks bizarre" (phone review) | deployed and live-verified (honeycomb gone, playable in ~1 min on second load; audit §5) | `SEABED_BLEED_VERIFY_SEAS_WET_AGAIN` (done) |
| Water biomes get the ocean shader | `RM_WorldTerrainShader.cs` gives every `isWaterBiome` BiomeDef of ours the WorldOcean material; Grey, Twilight, Scald faces point back at vanilla `World/Biomes/Ocean`, the Chill at our `Jawa_SickWater`. `a69ed8110` | none | said (same review: "water should look like water") | deployed; Player.log `world ocean shader on 8 water biomes`; seas read as flat slate-navy, no depth, no sheen | same item |
| Flat colour biome faces, calmed | `src/RimMandrake/Utils/art/biome_worldfaces.py`; 57 faces generated to a WME-derived spec with no donor bytes (`0f01bd5f7`), 13 crust-family faces calmed against mid-zoom stipple (`fce7ac7b4`) | none | spec is the agents'; WME/GRimTerra stay OFF the list pending his card (section 4) | deployed in the evening Baroque Biomes compose; the stipple is still visible live (`V_rust_stipple.png`) | `WORLDMAP_BIOME_APPEARANCE_1` (blocked) |
| Soft borders between land biomes | `src/RimMandrake/BiomesShell/Source/RM_WorldLook.cs`, overlay submeshes on `Custom/WorldOverlayTransparentLit`, queue 3505, 9,453 overlays on 7,567 tiles; `4d3d87e64` | "Planet: soft borders between biomes [now]" (`worldBorderBlend`), on | none recorded (agent build); look judged by owner later | deployed; `blendLift` 0.003 (`e7adc75e3`) is in the 19:38 DLL | `RIVER_BLEND_DEPLOY_UNDER_THE_WATERLINE` |
| Seas deepen away from the coast | same file; teal film fades out over 1 tile, navy film fades in over 4; 1,448 water tiles | "Planet: seas deepen away from the coast [now]" (`worldSeaDepth`), on | none recorded | deployed | none filed |
| Soft hill shading | our `World/RM_Hills` atlases (`src/RimMandrake/TerminalBiomes/Textures/World/RM_Hills/`, `world_hill_decals.py`) swapped onto the four shared vanilla hill materials by `RM_WorldLook.ApplyHills`; `aba208ccc`, `08512defb` | "Planet: soft hill shading [now]" (`worldSoftHills`), on | none recorded | on disk (DLL string present); not loaded since | `HILL_DECALS_VERIFY_NO_MORE_COOKIE_CUTTERS` |
| Soft landmark icons | `RM_WorldLandmarks.cs`: postfix on `WorldDrawLayerBase.Alpha` for the landmark layer plus quad shrink; eases back to vanilla between altitude 0.20 and 0.05; `caba4437a` | "Planet: soft landmark icons [now]" (`worldSoftLandmarks`), on; size 60% | card 2026-10-20 "Fade and shrink icons" (item `LANDMARK_ICONS_DECIDE_THE_REAL_SPECKLE`) | **built, not deployed** | `LANDMARK_ICONS_DEPLOY_FADE_THE_CONFETTI` |
| Readable roads and rivers | `RM_WorldPaths.cs`: dark casing, umber dirt, slate stone, gold highway; river width and bank colour; colours in `world_paths_readable_2026-10-20.md` section 3; `fe729e485` | "Planet: readable roads and rivers [now]" (`worldReadablePaths`), on | said 2026-10-20 "It is absolutely not ready yet" | deployed; live ON/OFF toggle checked both ways | `WORLD_PATHS_VERIFY_CASED_IN_GOLD` (done) |
| Darker river gradient | FlowWorks River Colours, middle `#7A7A2E`->`#2E2E00`, end `#3D4A52`->`#00293D`; `ae7ff3c7c`, `src/RimMandrake/FlowWorks/Source/RiverColors/RM_RiverColors.cs` | FlowWorks river colour settings (live file holds no saved colours, so defaults apply) | card 2026-10-20 "River gradient blends into land -> Darken, same hues" | deployed (FlowWorks in the evening compose); seen in `V_rivers_85.png` | `RIVER_COLOURS_DEPLOY_DARKER_WATER_AT_LAST` (done) |
| Roads allowed on Stillsand, Umbra, Slime | `allowRoads=true` on `RM_Stillsand` (`6d8692254`), `RUT_Umbra` and `RM_GelatinousSlime` (`632771031`) | none | Stillsand: said 2026-10-20 "For now just replicate where we had roads before." Umbra and Slime: card 2026-10-20 (reverses the older `RUT_UMBRA_ROADS_RULING_1`) | deployed; roads drawn live | `UMBRA_SLIME_ROADS_VERIFY_FINALLY_DRAWN` (done) |
| Region labels at 70% displayed width | `labels70_plan.py`, `world/ASHKARR_LABELS70_2026-10-20_plan.json`, bundle size scale; `292e1ef21` | none (data, applied through the bridge) | card 2026-10-20 | planned, **not applied live** | `LABELS_SHRINK_APPLY_LIVE_SEVENTY_PERCENT` |
| Planet world icons (Mutator World Icons) calm settings | staged settings file, install is live work; `770a012d8` | n/a (other mod) | none recorded | staged, not installed | `WORLD_ICONS_INSTALL_CALM_SETTINGS_ONE_SLIDER` |

### 1b. How the planet is laid out (data in the world, applied through the bridge)

| change | file and sha | owner ruling | applied to | verify item |
|---|---|---|---|---|
| Mountains pass 1 (concentric belts rebuilt as ridges, Impassable only on Cratercrown, river heads on high ground, 1,939 purposeless SmallHills to Flat) | `mountain_system_2026-10-20.md`, plan `world/ASHKARR_MOUNTAINS_2026-10-20_plan.json`; applied `15bc6ca1a` | said 2026-10-20 "make the world's mountains make sense ... the single most distracting feature" | `_MOUNTAINS` and every later save | n/a |
| Mountains pass 2 (Ashfall ridge-and-valley, 12 Ashteeth teeth, 23 orphan river heads reset; 805 hilliness + 4 elevation) | plan `world/ASHKARR_MOUNTAINS2_2026-10-20_plan.json`; `bbcc75f54` | said 2026-10-20 "better ... keep working on these biome and mountain and river and road issues" | **applied** in `_PARITY` (audit section 6: read-back 0 mismatches; commit `79f95ccf1`). Ledger still says `proposed`: lag | `MOUNTAINS2_PLAN_DEPLOY_805_TILES_PACKED` |
| Record links restored (326 river + 1,242 road; vanilla worldgen leftovers cleared) | `ASHKARR_DEV_START_2026-10-20_RECORDLINKS.rws` | n/a (record is canon) | `_RECORDLINKS` onward | n/a |
| Labels: 71 sizes + centres restored (the audit's frame was mirrored) | `parity_causes_2026-10-20.md` U1, `world/_parity_apply_2026-10-20.py`; stamp side `0c00860d7` (`featuresPath` on `world_features_import`) | label curve is his 2026-10-09 card `WORLD_LABEL_SIZE_HIERARCHY_1` | applied in `_PARITY`; stamp deploy (JawaBench) owed | `WORLD_LABELS_RESTORE_SIZES_MIRROR_WAS_OURS`, `STAMP_LABELS_DEPLOY_DOOR_STILL_SHUT` |
| Mutators: 28,280 rolled stowaways removed, 123 restored | U2; stamp stage 4a | frozen-world rule | applied in `_PARITY` | `WORLD_MUTATORS_PRUNE_28K_STOWAWAYS` |
| Rivers laid mouth-first (canonical `riverDist`) | U4; `world/ASHKARR_PARITY_U4_*` | frozen-world rule | applied in `_PARITY` | `WORLD_RIVERS_REPAIR_DOWNHILL_AT_LAST` |
| Home map size 325 | `jawa/world_info_set initialMapSize=325` (scribed `WorldInfo.initialMapSize`) | card 2026-10-20 "Back to 325" | `_PARITY_QUIET` only | `HOME_MAP_SIZE_RESTORE_ROOM_TO_STRETCH` (done) |

### 1c. Physics of the tidally locked planet

| mechanism | file | toggle, default | owner ruling | deploy state | verify item |
|---|---|---|---|---|---|
| The lock itself | Alien Worlds' Harmony patches, active only while its PlanetTypeDef is current. With Worldbuilder loaded the type comes from the save's `<worldPresetName>`, so the save needs `TidallyLocked` in BOTH `<worldPresetName>` and `<alienWorldsFrameworkPlanetType>` (`world_physics_audit` section 1) | n/a | said 2026-10-20 "ensure we are in fact Tidally Locked" | `_LOCKED` onward carry both fields; the original `DEV_START` loads **Default** on the full list. No load-time guard yet | `TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING` |
| Light follows the sun | `src/RimMandrake/CreatureBehaviors/Source/RM_TidalSunGlowPatch.cs` + `RM_TidalSunGlowMath.cs`; glow 0.6 at horizon to 1.0 from 30 degrees, 0 past the dusk band; `3742c2b6b` | "Tidally locked world: light follows the sun" (`tidalSunGlowByGeometry`), on | card 2026-10-20 "Light follows the sun" | deployed (CreatureBehaviors in sync); live: scratch maps match the formula | `TIDAL_GLOW_DEPLOY_FOLLOWS_THE_SUN` (done) |
| Dusk band 12 degrees | slider `tidalTwilightBandDegrees`, default 12 (was 6); `5a1b7076e` | slider 0..18, default 12 | card 2026-10-20 "12 degrees (Recommended)" | on disk (19:38), not loaded | `DUSK_BAND_DEPLOY_TWELVE_DEGREES_OF_GLOAMING` |
| No seasons | `RM_TidalNoSeasonsPatch`, `Priority.Last` postfix on `GenTemperature.SeasonalShiftAmplitudeAt` returning 0 while locked (`0f76174bd`); the XML patch `RM_TidalLock_NoSeasons.xml` (`3742c2b6b`) only reaches the standalone backend | "Tidally locked world: no seasons" (`tidalLockNoSeasons`), on | card 2026-10-20 "Remove the swing" | on disk (19:38), not loaded; the XML-only version measurably did nothing | `LOCKED_SEASONS_DEPLOY_CALENDAR_GOES_FLAT` |
| Stars hold still / drift yearly | `RM_WorldStarsPatch.cs`, `RM_WorldStarsMath.cs`; `de96af398` | "Planet view: stars hold still" (`worldStarsPinned`), on; "Stars drift once a year" (`worldStarsYearlyDrift`), on | card 2026-10-20 (drift once a year) | CreatureBehaviors in sync; whether the evening load ran it is UNMEASURED (ledger item still `proposed`) | `WORLD_STARS_REPAIR_STILL_SPINNING_FOR_NOBODY` |
| Sunless flora keep growing | `growMinGlow 0` AND `growOptimalGlow 0` on sunless plants; selftest refuses the half-set; `48f2c1ad9` | none | none recorded (agent fix from `glow_consumers` section A) | on disk if its mod is in the evening compose; no 8-night readback | `DARK_FLORA_VERIFY_EIGHT_NIGHTS_NO_WILT` |
| Direct Sun and tree shade | geometry only (`RM_MapComponent_PinnedSun.SunGeometry`), unchanged today; independent of the glow patch | existing settings | CLAUDE.md "One Direct Sun" | deployed earlier | none new |
| The Rings | RW - Planet Atmosphere with `deployed/config/Mod_3272330410_AtmosphereMod.TRUE-GLORIOUS-RING.xml` (md5 ac1e8fa4) and `deployed/atmosphere_ring/ring_debris.png` hand-copied into the Workshop folder; back on FULL.LATEST (`e5c10aa8a`); limb A/B config `33cd4b1f9` | n/a | said 2026-10-20 "add back the Rings when we bring back the larger mod list" | live: ring draws, no errors; memory delta vs Rings-off UNMEASURED | `PLANET_RINGS_RESTORE_DEBRIS_STILL_IN_ORBIT` |

### 1d. Factions and creatures

| mechanism | file | owner ruling | deploy state | verify item |
|---|---|---|---|---|
| Banished factions: Tallmere Combs (`RM_Faction_CombHolds`), Space Exchange (`TradersGuild`), Sacrileg Hunters (`CASacrilegHunters`) | registry `src/RimMandrake/Utils/factions/banned_factions.json`, checker `src/RimMandrake/Utils/banned_factions.py` (selftest 17/17), def side `src/RimUtinni/UtinniPatches/Patches/FactionSlate/BannedFactions.xml`; `58488adc0` | said 2026-10-20 "We don't want those ... same with the Space Exchange" | def side live (hidden in `jawa/list_factions`); save side applied in `_FACTIONS` and later (`check-save` PASS) | `UNWANTED_FACTIONS_SILENCE_NOT_DELETED` |
| Celestial Rogues (`Salvagers`) banished | same registry; `71fe243ab` | card 2026-10-20 "Ban Celestial Rogues" | **not deployed** (UtinniPatches `BannedFactions.xml` differs); saves still list it LIVE | `CELESTIAL_ROGUES_SILENCE_GROUNDED_IN_ORBIT` |
| Painted heads fitted on the skull mass | `src/RimMandrake/Utils/art/fit_head_canvas.py`, envelope `head_envelope.json`; `cb6e354c2`, Ortolan ear `e44d193f0` | said 2026-10-20 "center the head regardless of additional appendages ... bulk of the head" | deployed and loaded in the evening live check | `HEADS_VERIFY_SHRUNK_TO_FIT_THE_HATS` |
| On-screen head size tuned in the def | `SM_HeadSize_Cosmetic` on `RSW_LasatHead` 0.88 and `RSW_NelvaanianHead` 0.95 (`src/RimStarWars/StarWarsRaces/Defs/GeneDefs/SW_Genes.xml`); `47a707a35`, `e6e219f0f` | card 2026-10-20 "Tune in the def" | files in sync with game at 19:55; not loaded | `HEAD_SIZES_MEASURE_SKULLS_ON_THE_RULER` |
| Size genes real again | `gen_races_mod.SIZE_GENES_REAL` (`47a707a35`); `7707a6aca`'s regeneration had reverted `1c3a673fe` | none (regression fix) | in sync | `SIZE_GENES_RECONCILE_LOST_IN_REGEN` (done) |
| Flier flip-books: six sets body-locked | `src/RimMandrake/Utils/art/flyer_cutout.py`, localiser `flier_body_stabilize.py`; installed `842bca0ec` (Sketto, PekoPeko f, FireHawk, Uvak, Hawkbat m/j) | said 2026-10-20 "Their bodies should be kept static while the wings flap" and card "Fliers: rebuild all 18 now" | installed and in the evening compose | `FLIER_FRAMES_AUDIT_BODY_NOT_WING_EXTREMES` |
| Flier tool guards | `src/RimMandrake/Utils/art/flier_guard.py`: bbox-rewriting tools refuse `_Flying_` sets; `64786704a` | said (same ruling) | repo only | none |
| Donor flight frames for Brezak, Drexl, Thranta, Tibidee | 48 PNGs through `art.py install`; `7ffc34bba` | card 2026-10-20 "Install donor art" | art ledger install done; loaded: UNMEASURED | `FLIER_FRAMES_FILL_FIVE_GHOST_FLOCKS` |
| Leaning Scrub wind, Gale dust A, Cauldron soils, pit-cover riders, hose pathing, plant-band retargets | `RM_TheLean.cs` (`1ec532ea1`), `660d437a6`/`ed99fbee6`, `86e8a90bf`, `e3607489c` | cards 2026-10-20 (`biome_bars_sitting_2026-10-20.md`) | mixed; see each item | `SCRUB_WIND_BUILD_LEAN_ON_PURPOSE`, `CAULDRON_SOILS_BUILD_DIRT_THAT_BREATHES`, `PIT_COVER_BUILD_DECONSTRUCT_DROPS_TOO`, `HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE`, `PLANT_BANDS_DEPLOY_VERIFY_FINALLY_RM_TWINS` |
| Drawbridge and pipes-across-pits | designs only: `design/RimMandrake/flowworks_drawbridge_design_2026-10-20.md`, `flowworks_pipes_across_pits_design_2026-10-20.md` (both ruled by cards 2026-10-20) | cards | **planned**, nothing built | `DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS` |
| World tools in JawaBench | `JawaBenchWorldTools.cs`, `JawaBenchWorldArgsCore.cs`; `be8bc721b`, `484a643c0` | n/a | built, not deployed or driven | `WORLDTOOLS_DEPLOY_BUILT_NOT_YET_DRIVEN` |

## 2. The saves

There is **no single pointer** naming the dev start (`TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING` step 1 asks for one). The newest
chain, and the one every live check of the evening used, is `_PARITY` then `_PARITY_QUIET`. The frozen
`CANONICAL_ASHKARR_START_2026-09-12.rws` is untouched (`infrastructure/state/CANONICAL_SAVE.md`).

| save (`...\Saves\`) | what it contains | trust |
|---|---|---|
| `ASHKARR_DEV_START_2026-10-20.rws` | the remake's first dev world, made on PAINT (no Worldbuilder): no `worldPresetName`, map size 250 | loads **Default** (sun moves) on the full list. Do not use |
| `..._LOCKED.rws` | the above, fixed live so both lock fields read `TidallyLocked` | base for the mountain pass |
| `..._MOUNTAINS.rws` | LOCKED + mountains pass 1 (sha256 `3e2e04aab10f24af...`) | superseded; still carries the 1,309 leftover links |
| `..._RECORDLINKS.rws` | MOUNTAINS + links reset to the record (326 + 1,242; sha256 `104641ed18f38d0f...`) | base of pass 2 |
| `..._FACTIONS.rws` | the factions step alone (Comb Holds and Space Exchange hidden + defeated, "Luminary Dock" removed) | intermediate |
| `..._PARITY.rws` | everything above + mountains pass 2 + labels (71) + mutators prune + rivers mouth-first + factions (13.56 MB, sha256 `894120f8939deb8e...`, `check-save` PASS) | the world as it should look |
| `..._PARITY_QUIET.rws` | PARITY + `initialMapSize` 325 + VEF `ignoredFactions` (63 entries) so the three VEF pop-ups stay quiet | the newest; de facto dev start |
| `..._SHIP`, `_LANDED`, `_FOUNDERS_2026-10-20.rws` | staged remake states, written 01:04-01:07; lack `TradersGuild`/`Salvagers` (they appear on first load) | contents UNMEASURED here; see `design/RimMandrake/world_remake_2026-10-19/06_remake_runbook.md` |

Cautions: all of these predate the Celestial Rogues banish, so `check-save` reports `Salvagers` LIVE in START, FACTIONS and
PARITY_QUIET. A save made while the 325 list is loaded and Rings are on is the only kind with the Rings; the lock needs the
Worldbuilder preset name.

## 3. Facts that surprise

1. **Worldbuilder bypasses the seasonal curve.** With `ferny.worldbuilder` loaded (every full list), its prefix on
   `GenTemperature.SeasonalShiftAmplitudeAt` returns false, so the original body and Alien Worlds' transpiler never run; its
   postfix sets the amplitude from an axial-tilt table (8.649 C at the home tile). Patching the TidallyLocked def's
   `seasonalTempVariationCurve` therefore did nothing. Only a `Priority.Last` postfix works (`world_physics_audit` section 8).
2. **The vanilla ocean shader ignores depth.** `Custom/WorldOcean` exposes only `_MainTex` and `_MacroTex` and ignores UV0: a sea fed
   depths from 0 to -100,000 m drew byte-identical pixels. Our flat -350 m seas cannot be shaded through it; shore and deep
   shading is a separate overlay (`RM_WorldLook.cs`) (`worldmap_in_game_audit` section 6).
3. **Two terrain meshes on one sphere cause the honeycomb.** `WorldDrawLayer.Visible` defaults to true for an unselected layer; no
   vanilla layer shares the surface radius, until `RM_SeabedLayer`. Hiding it makes it permanently Dirty, which loops
   GeneratingPlanet for ~10 minutes unless the dirty check ignores hidden coplanar layers.
4. **The river overlay sat at hill height.** The border blend (+0.01) shared the rivers' height and writes depth, so on 7,567 border
   tiles it hid the river: "dashes" with whole links underneath. Blend is now +0.003, under hills (+0.005) and rivers
   (`e7adc75e3`). Roads (+0.02) were never hidden.
5. **The white speckle at mid zoom is landmark icons, not hills.** 155 of Rust Cathedral's 236 tiles carry an Odyssey landmark, and a
   landmark tile draws no hill. That is why the soft-landmark mechanism exists.
6. **Size genes were reverted by a generator.** `7707a6aca` regenerated the race mod and turned `RSW_BodySizeGene_*` back to cosmetic;
   the fix lives in the generator (`gen_races_mod.SIZE_GENES_REAL`), so hand edits to `SW_Genes.xml` would be lost again.
7. **A stored road is not a drawn road.** `SurfaceTile.Roads` is null when the biome has `allowRoads=false`. 196 record road links on
   Stillsand never drew until `6d8692254`.
8. **A clock rewind freezes the glow reading.** PerformanceOptimizer caches `CurCelestialSunGlow`; after the clock is set back, reads
   return the stale value (the "0.7535 at all times" was a cache, not the lock). Read scratch maps or step forward only.
9. **`growMinGlow 0` alone does not make a sunless plant.** The light factor is `InverseLerp(min, optimal, glow)`, 0 at glow 0 while
   optimal stays 1.0; the plant counts as unlit and dies at 7.5 days. Set `growOptimalGlow 0` too (vanilla Glowstool's pattern).
10. **The 52 "wrong" labels were an instrument error.** `feature_drawcenter_audit.py` used a reflection, fitted on two labels, that
    the engine's `LongLatOf` is not; on 2026-10-09 it moved 60 canonical labels off their regions. The corrected frame is a
    90-degree rotation (`parity_causes` U1).
11. **`world_links_import clearFirst` clears only the tiles the file touches.** Vanilla worldgen's 983 river and 489 road links
    survived the earlier stamp. And rivers must be laid mouth-first or `riverDist` comes out wrong on 335 of 335 tiles.
12. **Rolled mutators are not authored content.** 28,616 mutator entries were rolled by world generation before the stamp; the stamp only
    adds, it never subtracts (stage 4a now strips).
13. **A faction with no settlement can never be defeated,** and Odyssey recreates `TradersGuild` and `Salvagers` on every load whatever
    the def says; banish, do not delete (`factions_unwanted_and_lingering` section 1).
14. **Flip-books are body-locked, not bbox-registered.** Registering on the alpha bbox couples wing motion to body motion. The shipped
    frames were repaints, not translations: 18 of 22 sets drift, most because the body is redrawn per frame.
15. **A head's drawn size is its alpha fraction of the canvas times Big and Small's render scale** (1.5-cell mesh regardless of pixel
    size). Only Lasat and Nelvaanian have a scale; Ortolan and Mimbanese just look different.
16. **The previous grey seas came from a donor.** In September the navy seas were World Map Enhanced's `Ocean.png` replacing the vanilla
    path; WME (textures only, 229 PNGs, no code) is off the list. Its hill sets would also replace the vanilla blots.

## 4. Open owner decisions

1. **Return World Map Enhanced and/or GRimTerra World Map?** Cosmetic, donor art; needs his card (`worldmap_in_game_audit` section 4,
   `Transient/wme_analysis_2026-10-20.md`).
2. **Which atmosphere shell?** The original `TRUE-GLORIOUS-RING` config is kept; the LIMB-TEST gives a blue limb but hides the near ring and
   dulls surface colours (`world_physics_audit` section 9).
3. **Which save is the dev start,** and whether a load-time guard should force the preset name (`TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING`).
4. **The three VEF offers** (Junkers, Mercenaries, Roaming monstrosities): add, ban or ignore in the shipped world (currently ignored in
   `_PARITY_QUIET`).
5. **Celestial Rogues' pawns at Odyssey orbital sites** (`OrbitalFugitive` quest, wreck guards): kept by default.
6. **Who farms the Scrub's vaporators** (default `OutlanderCivil`).
7. **The big "Dune Sea" label sits over Anvil and Rust Cathedral** after the label restore: canonical centre or canon error? He should look.
8. **The Ancient Asphalt Highway is 46 pieces of 1-9 tiles in the record itself;** re-route the record or accept dashes.
9. **The Scald sits at arc 23-51 and 7.8 C under the curve, not arc 0-30:** on `BIOME_PAINT_ONCE_AT_THE_END_1`.
10. **Look-and-feel judgements only he can make:** the Dune Sea tract, the hills, the mid-zoom face stipple, the soft borders and sea films (their
    committed values have not been confirmed by eye on a final-DLL load).
11. **Drawbridge and pipes:** the two pending question cards were answered the same evening; remaining is the pipe/hose width spec to judge in
    game first (pipes design, answer 8).

## 5. Live-verification queue (in this order, one game-down window then one game-up session)

**Game down (deploy):** `python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes --apply`, then the same without `--compose`
for UtinniPatches (Celestial Rogues). Then one cold load of `_PARITY_QUIET` on the 325 list.

| check | pass looks like | item |
|---|---|---|
| Seasons flat | `seasonal` = 40.4 at every sampled point; `jawa/harmony_patches Verse.GenTemperature` lists the `Priority.Last` postfix (`...\scratch\seasonsdusk\verify.py`) | `LOCKED_SEASONS_DEPLOY_CALENDAR_GOES_FLAT` |
| Dusk band 12 | glow at -12 degrees sits at 0; Sump median 0.02 | `DUSK_BAND_DEPLOY_TWELVE_DEGREES_OF_GLOAMING` |
| Stars | two planet screenshots a game day apart show ~6 degrees of drift, sun vector identical | `WORLD_STARS_REPAIR_STILL_SPINNING_FOR_NOBODY` |
| Border blend lift | rivers whole on border tiles in the shipped DLL | `RIVER_BLEND_DEPLOY_UNDER_THE_WATERLINE` |
| Hills | no brown outlined blots at Dew Horn or Gray Crags | `HILL_DECALS_VERIFY_NO_MORE_COOKIE_CUTTERS` |
| Landmarks | Rust Cathedral at `V_rust_stipple.png` zoom, then closer | `LANDMARK_ICONS_DEPLOY_FADE_THE_CONFETTI` |
| Banish | `banned_factions.py check-dump` PASS, then `check-save` PASS on every dev save | `CELESTIAL_ROGUES_SILENCE_GROUNDED_IN_ORBIT`, `UNWANTED_FACTIONS_SILENCE_NOT_DELETED` |
| Dark flora | Sump flora `growOptimalGlow` 0; a night-side plant alive after 8 days (state read) | `DARK_FLORA_VERIFY_EIGHT_NIGHTS_NO_WILT` |
| Heads | four species, bare and helmeted, beside a vanilla pawn on all facings; skulls 1.20 / 1.05 / 1.00 / 1.00 | `HEAD_SIZES_MEASURE_SKULLS_ON_THE_RULER`, `HEADS_VERIFY_SHRUNK_TO_FIT_THE_HATS` |
| Label sizes | apply the 70% plan, read back 0 mismatches | `LABELS_SHRINK_APPLY_LIVE_SEVENTY_PERCENT` |
| Label stamp | JawaBench `featuresPath` deployed | `STAMP_LABELS_DEPLOY_DOOR_STILL_SHUT` |
| Rings memory | one load without Rings for the working-set delta (currently UNMEASURED) | `PLANET_RINGS_RESTORE_DEBRIS_STILL_IN_ORBIT` |
| Null-texture flood | find the stack behind the loading-screen `null texture passed to GUI.DrawTexture` lines | `WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR` |
| Pit cover, hose, Scrub wind, plant bands, Cauldron soils | rows owed per item | see section 1d |

**Ledger lag found while writing this:** `MOUNTAINS2_PLAN_DEPLOY_805_TILES_PACKED`, `WORLD_LABELS_RESTORE_SIZES_MIRROR_WAS_OURS`,
`WORLD_MUTATORS_PRUNE_28K_STOWAWAYS` and `WORLD_RIVERS_REPAIR_DOWNHILL_AT_LAST` read `proposed` although `worldmap_in_game_audit` section 6
records them applied with 0-mismatch read-backs in `_PARITY`.
