# Decision strings — FOUNDRY overnight batch, full 621-mod load, 2026-09-19

Written BEFORE launch per rimworld-load-round §2/§3. Five assemblies ride this one load
(JawaRules, FireEcologyHook/Pyrelands, RimMandrakeFlowWorks, RimMandrake.CreatureBehaviors,
RimMandrakeProperty) plus the JawaBench companion DLL and one XML-only gene (StarWarsRaces).
Per the owner's standing three-assembly waiver, batching is affordable only because each
assembly's failure mode is distinguishable — written down here first.

## Per-assembly distinguishing signature (if it breaks, this is what names it)
- JawaRules (`Patch_RedressPawn_ForceKind`): `Log.WarningOnce` hash `0x4A57A3`,
  text names "pawnkind-redress-fix" and before/after kind. Startup arm line:
  `[RimMandrake.StarWars.JawaRules] pawnkind-redress-fix: armed;`
- FireEcologyHook (`WildPlantAllowlist`): no startup line expected (silent unless it fires);
  failure mode is an exception naming `WildPlantAllowlist` or `CalculatePlantsWhichCanGrowAt`.
- FlowWorks (`RM_WorldComponent_LiquidTags`/`RM_GenStep_LiquidShores`): a config error or
  crossref naming `RM_LiquidBodyDef`, `RM_GenStep_LiquidShores`, or `RM_LiquidBodyRegistry`.
- CreatureBehaviors (Grabber/Drinker/Soulchime comps): an exception naming
  `RM_CompGrappler`, `RM_CompFluidSacs`, `RM_CompProximityPsychicStun`, or
  `RM_CompShardArmor`.
- RimProperty (Bribe/HirePlaceless/Pickpocket): an exception naming
  `FloatMenuOptionProvider_Bribe`, `FloatMenuOptionProvider_HirePlaceless`, or
  `FloatMenuOptionProvider_Pickpocket`.
- JawaBench companion (`--gm` build, RunMapFinalizeSteps): tool list should show
  `jawa/do_bill_now`, `jawa/droid_format_tier`, `jawa/fire_incident`, `jawa/send_letter`.
  Absence of any = a build/deploy problem specific to that tool, not the others.

## Per-item decision strings (written before launch)

1. KCSG_PAWNKIND_COLONIST_FALLBACK_1 — `jawa/kcsg_place structure RUT_Ashfall_Spire` x5.
   PASS: all 5 pawn-symbol cells per placement show Helix kind + faction xenotype (never
   `Colonist`/`Baseliner`). Needs a stocked Ascendant Helix world-pawn pool first (redress
   only fires with candidates in `Find.WorldPawns`).
2. PYRELANDS_FLORA_LEAK_1 — generate a Pyrelands map. PASS: `jawa/list_things` (or census)
   shows 0x `AB_SessileMechanoid`, 0x `AB_GiantStikehr`.
3. DEEPS_FAUNA_MECHANICS_1/2 — spawn RSW_BovineBeetle (Grabber), RSW_BloodropMoth (Drinker),
   RSW_FacetMothLarvae (Soulchime) + test pawns. PASS: grapple hediff `RM_Grappled` applies
   and torso damage ticks; Drinker feed applies `RM_FluidSacks` gauge and poisons on
   normal-blood victim; Soulchime proximity stun (`PsychicShock`) fires on approach.
4. WORLDMAP_LIQUID_TAGS_1 — confirm 0 config errors naming `RM_LiquidBodyDef`/
   `RM_GenStep_LiquidShores`/`RM_LiquidBodyRegistry`. No world-tile writes.
5. AQUATIC_WATER_BREATHING_GENE_1 — add `RSW_WaterBreathing` gene to a test pawn via bridge.
   PASS: no exception; pawn card shows the gene's effect description; if riggable, immune to
   `RM_PitDrowning`.
6. SETTLEMENT_VERBS_WAVE_1 — two pawns, right-click. PASS: Bribe/HirePlaceless/Pickpocket
   float-menu options appear under correct gates and execute with no exception.
7. BRIDGE_MAPGEN_STALE_FINALIZE_1 — `--list-tools` shows `jawa/do_bill_now` and
   `jawa/droid_format_tier`. Destroy a plant via `world_tile_map_generate` reuse path (no
   `map_commit`), screenshot. PASS: renders correctly, not stale.
8. MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1 — re-check candidates post-full-load; no force-enable.
9. LONGHUNGER_QUICKTEST_1 — per `design/validation_walks/RimUtinni/LongHunger.md`: def
   read-backs (RUT_LongHunger, RUT_Groundcaller, RUT_LongHungerSurfaces,
   RUT_LongHungerContract, RUT_DuneHaze), spawn RUT_LongHunger, eruption explosion,
   tremor pulses, submerge at ~2500 ticks + loot, quest offer/fire.
10. FULL_LOAD_RESIDUE_TRIAGE_1 — harvest_log.py full sweep; pull DEAD MODS(1)/DISCARDED
    DEFS(5) threads if time allows.

Baseline standing counts (pre-existing, not this pass's concern unless they move):
patchfail should now read 0 (was 10, fixed offline). configerror should now read ~17
(was 93, fixed offline, minus RM_FE_Ground_SoilRich which is expected/accepted).
