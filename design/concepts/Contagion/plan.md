# Contagion, Design Version 0.1.0: plan

Root approved by him 2026-11-15 (OWNER:1794772416196929336). Most of the mod is built; this plan is about proving it
and closing the five owed builds, not rebuilding it. The tree is `tree.json`, the scenes and showcases `scenes.json`.

## Structure and reuse

- Every scene runs from the saved Contagion site v3 (`src/RimMandrake/Contagion/prep_site.py`, `site_spec.py`) on the
  minimal list plus all five DLC, except the walk, which needs a lived-in save on the full list.
- The scenes are new named entry points `scene_<name>` in `src/RimMandrake/Contagion/validation.py`, built on its
  existing chains (`burn_forced`, `burn_natural`, `uv`, `touched`, `coalescence`, `genome`, `repulsor_clear`,
  `spawner`, `zhool_haze`, `settings_chain`) and their helpers (`_jump`, `_spawn`, `_burn_report`). Each scene adds the
  three parts the stage 0 audit found missing: an asserted start, a discriminating control, and a scene-begin/scene-end
  restore by reloading the site save. One build item owns all 24: RIMMANDRAKE_SCRIPT_CONTAGION_SCENES_EVERY_BURN_A_CONTROL.
- The Burn refuge reuses the shared shade geometry (`RM_MapComponent_ShadeGrid`, Sun and Shade); the Burn's own
  exact-cell tree test (`RM_ContagionSkyExtension.cs:95`) is removed, not kept beside it.

## Order

1. Owed builds, offline first, each with its selftest written in the same run (offline and live test built with the
   item): RIMMANDRAKE_BUILD_CONTAGION_BURN_REFUGE_READS_SHARED_SHADE, RIMMANDRAKE_FIX_SUNDASH_READ_WEATHER_COVER_HEAT_ALREADY_DOES
   (filed at stage 2), RIMMANDRAKE_SHOW_CONTAGION_BATCH_ODDS_BEFORE_THE_STAB, RIMMANDRAKE_BUILD_CONTAGION_PREBURN_DIVE_NATIVES_LEAVE_FIRST,
   RIMMANDRAKE_BUILD_CONTAGION_BODYPRINTS_SKIN_BEFORE_PRINT. Zhool'Iza stays on its own item, ZHOOLIZA_BUILD_FROM_JELLY_RENDERS.
2. The scene entry points, flagship first (`sc_burn_dash`), then the rest in showcase order.
3. A judge agent runs the flagship and the looks scenes before he sees anything; he sees the survivors as single images.

## Risks

- The flagship can fail on tuning alone: if the Burn dose makes a 20-cell dash lethal or harmless, the review stops by
  his own stop line. The scene's control (a colonist left standing out) separates "the Burn is too weak" from "the dash
  is too costly".
- Native Burn harm read FAIL on 2026-11-06 (c_proof); `sc_natives_take_burn` is the scene that settles it.
- The seven review fixes of 2026-10-17 are built on origin/main and owe their live proof (rimflow shows six `built`
  and CONTAGION_BURN_OFF_FIX_PAWN_WONT_WALK `proposed`). The inject, Wombpod, Dive-cell and Burn-off scenes are those
  proofs; c_open_fixes is resolved as "landed, not yet proven", not as a wrong read.
- COALESCENCE_STAGE_DIAGNOSE_STUCK_AT_ONE is closed done; `sc_coalescence_grows_and_breaks` counts absorption from
  arrivals so a cleanup cannot fake it.

## Out of 0.1.0

- Grown-limb costs, tuning and testing: RIMMANDRAKE_DESIGN_CONTAGION_LIMB_COSTS_FIVE_LIMBS_WAIT (0.2.0, his words
  2026-11-15). The limbs stay built; 0.1.0 checks only that one grows, shows and comes off.
- Rawshade is designed and unbuilt, scope not opened: not in this version.

## Rework against coverage verdict rm-coverage-judge-1794788108 (run rm-role-designer-1794819648)
- limb_still_grows left the 0.1.0 tree (his 2026-11-15 ruling); the built limbs are covered offline by limbs_stay_built.
- New offline leaves first: fauna_specials_declared, biome_def_declared, flora_yields_declared, limbs_stay_built.
- New scenes, all owed in RIMMANDRAKE_SCRIPT_CONTAGION_SCENES_EVERY_BURN_A_CONTROL: sc_sunbeam_fires, sc_wombpod_hatch, sc_helix_trade, sc_coalescence_forms, sc_mulched_soil; sc_zhooliza waits on ZHOOLIZA_BUILD_FROM_JELLY_RENDERS.
- Owed art: RIMMANDRAKE_DRAW_CONTAGION_FLIPBOOKS_TWO_FLYERS_HALF_DRAWN (Blisterfloat, Gorekite flip-books).
- shelter_in_lead tests the lead the tells give a player who orders his people in; no colonist shelter job is built or assumed.
- Risk: arms that depend on open fix items (inject, Wombpod, Coalescence stage) record UNMEASURED until those items close.
