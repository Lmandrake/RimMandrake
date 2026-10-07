# CAULDRON_ENRICHMENT_VISUALS_1 build — 2026-10-06 (FOUNDRY, offline)

## sweep
- Footprint grid EXISTS: CreatureBehaviors RM_MapComponent_TrackGrid (84a377bf0, b39816766). Public RecordPrint(cell,pawn,surface), ClearCell, TryGetPrint. No age expiry, no hover, no maker stored. Cauldron does NOT depend on CreatureBehaviors -> reach it by reflection (Warscar RM_TrackGridLink precedent).
- CAULDRON_ENRICHMENT_AUDIO_1 is DROPPED (owner 2026-10-03: vanilla sounds, no retuning). Audio here = vanilla cleaningSound on the new filth only.
- Accent plants now HAVE base art (7/7 on disk). No dew-variant, fleck-overlay, bead or vexxiss-print art anywhere in artpipe (find: dewfall/flecks_/assay/vexxissprint/dewbead = 0).
- Dewfall: weather def only, no effect today. Plant.Print overrides wholesale (comps never print) - RimSage. MapMeshFlagDefOf.Things exists (1.6).

## built (uncommitted, PROVISIONAL numbers)
- V4 prints: Source/RM_VexxissPrints.cs (reflection bridge to CB RM_MapComponent_TrackGrid.RecordPrint/ClearCell/TryGetPrint; saved ledger RM_MapComponent_VexxissPrints = 1-day expiry eraser + hover label via MapComponentOnGUI). Comp hook in RM_CompVexxissBehaviour.CompTick (print every 1.5 cells, natural land only). No terrain tagged: only the vexxiss prints. No CB = no prints.
- V1 beads: RM_Filth_DewBeads (Defs/ThingDefs_Filth/RM_CauldronFilth.xml, Filth_Water template, Spatter tinted toxic green-amber, 0.5-1 day, cleaningSound Interact_CleanFilth_Fluid) spawned by RM_MapComponent_CauldronDewfall (6/250 ticks x density, cap 400, unroofed outdoor standable land, NOT home area).
- V2 saturation: RM_DewfallGraphicExtension + Plant.Graphic postfix + one Things remesh per transition. DORMANT (no dew art; no XML ext added; patch not installed when no variant resolves).
- V3 flecks: RM_AssayFlecksExtension on both trees + Plant.Print postfix replaying Plant.Print's Rand seed for registration; RM_CompMetalYield.GradeFraction(). DORMANT until Flecks_Light/Heavy exist.
- Settings: dewfallBeadsEnabled, dewfallBeadDensity, dewfallSaturationEnabled, assayFlecksEnabled (nested under assay grade), vexxissPrintsEnabled; remesh on toggle.

## art
- None finished for any of this (artpipe find). Nothing installed. Owed: RM_DewBeads a..c 128px; Flecks_Light/Heavy 256px; RM_VexxissPrint 128px (then set comp printTexPath); dew variants per chosen accent plant 256px.

## validation
- winbuild Cauldron: 0 warn 0 err. selftest_cauldron: 63/63 PASS, 54 breaks OK (expectations 27/22 settings, 44 defs updated; 4 roundtrip components + walk lines). validate_patch: 0 errors (warnings = owed fleck paths + vanilla Spatter not loose). selftest_sound_paths 0/898 unresolved.

## deferred / open
- Audio A1-A3 not built: CAULDRON_ENRICHMENT_AUDIO_1 is dropped.
- Live bead chain owed; no bridge reader for prints. Owner pick of which accent plants get dew variants.
