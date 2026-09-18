# BENCH_REBOOT_HANDOFF_202609180411 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609180208`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

The night's theme, twice over: **a value the game reads is not the value you
wrote, and nothing errors.** Two independent silent rewriters found in one
sitting: (1) `mandrake.rm.environmentalhazards` was deployed but NEVER in any
mod list, so every MayRequire-gated def riding it (RC1–RC6, Miasma/Greentide
locks, the whole Rot wave) has silently not existed in any load, ever — zero
log lines, because MayRequire vanishes quietly; (2) an unidentified startup
mod caps `BiomeDef.plantDensity` at 1.0 and rescales `wildPlantRegrowDays` by
the ratio (measured: Pyrelands 1.55→1.0, regrow 9→9/1.55), which is why every
density nudge the owner ordered read "still too bare". Fixes shipped: the mod
is activated in both lists, and `RM_PyrelandsDensityEnforcer` re-asserts our
numbers after all mods load, logging when it catches the thief. 🔑 The
instrument that finds this class: `jawa/get_defs` raw-field read-back against
the XML you think is live.

## What the owner should see

- **Nothing awaits a ruling — he ruled everything live tonight** (6 rot
  cards, EnvironmentalHazards + gizkastowaway activations, density ×3, gizka
  global breeding, guardian conscience). Two things await his EYE only:
- **Ten Pyrelands north-star bars** still need his yes:
  `modcheck/cli.py validate Pyrelands --owner-said` re-binds them.
- **FireHawk wing-flap** was staged live but the generated map hit the
  abandon-timer cull before a confirmed look; the staging survives in
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\PYRELANDS_REVIEW_20260918.rws`
  (5 FireHawks at map center, garrison cleared, wild herd intact).

## What is half-done, and where it stops

- **The next load verifies THREE activations at once**: EnvironmentalHazards
  (gated defs must actually appear — probe RUT_SheenExposureLock etc.),
  mandrake.rsw.gizkastowaway (live proof battery on the item), and Pyrelands
  plantDensity 3.0 (enforcer line in Player.log + `jawa/get_defs` read-back
  3.0 + fresh-map vegetation screenshot for him). Lists are live 634 / FULL
  635, verified by re-parse.
- **BEFORE that load, at the shutdown window**: `deploy_custom_mods.py --mod
  Pyrelands --apply` — FireEcologyHook.dll (carries the density enforcer) is
  built+committed but was LOCKED by the running game; without it the rewriter
  eats the XML's 3.0 again. `PYRELANDS_DENSITY_TRIPLE_1` tracks this.
- **All eight Rot builds owe live quicktest proof** (FOUNDRY's spore cloud /
  decay / wound-link + tonight's sheen / warm mat / pale tree / groves /
  live preparations) — each item's note has its battery. KinMending: set
  the aura in the 2–4 sev/day range at quicktest (vanilla base is 8/day,
  MEASURED, on ROT_HEALTH_SHARING_1).
- **Wave-C dangling PawnKindDefs** (RSW_Falumpaset/FeralGrazer/Fanback — the
  OTHER window's uncommitted fauna work) still null-key Desert/CypreJungle/
  DesertOasis wildAnimals and degraded GiddyUp this session; noted on
  MLIE_FAUNA_ABSORPTION_1, theirs to finish.
- **Art owed pile**: rot content (~20 placeholders across the five tickets),
  RUT_Emberscythe (ember-tinted Megascarab), RSW_GizkaBait (tinted kibble).
- **selftest_art_checks.py fixtures are stale** (Zeer/Orray/Anooba/Nuna
  expectations broken by the Mlie passes) — fauna lane recalibrates; 57/58
  otherwise green.

## Traps learned

- **`Build succeeded 0/0` is true of the files LISTED, not the files
  written**: EnvironmentalHazards' csproj has EnableDefaultCompileItems=false
  and b5b947fe9 shipped four .cs files without Compile entries — the DLL
  never contained its mechanism. Fixed + rebuilt; check the compile list on
  every explicit-list csproj commit.
- **MayRequire on def nodes deletes content with zero log lines** when the
  named mod is inactive — census the mod LIST, never the log, to prove a
  gated def exists.
- **A startup def-rewriter can eat XML values silently** (plantDensity cap
  1.0 + regrow rescale, culprit unidentified) — raw-field read-back via
  `jawa/get_defs` is the instrument; a late-running enforcer
  (LongEventHandler.ExecuteWhenFinished + GameComponent.FinalizeInit) is the
  countermeasure.
- **`rimworld/jump_camera_to_cell` reports success while the WORLD view stays
  up** — the screenshot shows the planet. Check `get_camera_state`.`mapId`
  and use `jawa/world_view {show:false}` first.
- **Bridge-generated maps are culled by the abandon timer once time runs**
  (re-confirmed: tile-672 map died after ~50k ticks of speed-1) — save
  BEFORE unpausing anything on a no-colonist map.
- **The shared-tree sweep is real and fast**: the other window's 2cd0ebcb1
  committed my subagent's in-flight cast-file edits mid-build, leaving a
  pushed patch referencing an uncommitted def for several minutes. Commit a
  new def the moment its referencing patch might travel.

## Closed since the last handoff (2)

- `PYRELANDS_ANIMALS_GENSTEP_1` — 211b2f0c821f9b099d4ed66d372a6b537cdd97f1
- `PYRELANDS_FAUNA_WIRING_1` — 211b2f0c821f9b099d4ed66d372a6b537cdd97f1

## Filed and still open (2) — the next seat's queue

- `ENVHAZARDS_NEVER_ACTIVATED_1` — mandrake.rm.environmentalhazards has NEVER been in any mod list — every MayRequire-gated mechanic riding it has silently not existed in any load
- `PYRELANDS_DENSITY_TRIPLE_1` — Pyrelands plantDensity tripled to 3.0 with a C# enforcer — DLL deploy + live verification owed at next shutdown/load

## Commits

```
aa75a54b8 GIZKA_TRIBBLE_ADAPTATION_1: the gizka stowaway (mandrake.rsw.gizkastowaway)
4f2f1d54d rimflow: file+close DIRTY_CODE_REVIEW_LOOP_RESTART_11 (this wave's continuity note)
c9670a07a rimflow: ledger sync (CATHEDRAL_EXPOSURE_COMPLETION_1 offline pass note)
37522c959 CATHEDRAL_EXPOSURE_COMPLETION_1: offline item-8 completion chain (full discovery, warzone flip, priced Hutt extraction, mourning register)
6d0c2bc2a Code review wave: EnvironmentalHazards + WreckedMachines smelter defs (7 files, clean)
c7102709a stage_review.py: route LocalLow paths through the game_paths seam
fab58c094 rimflow: ledger sync (DIRTY_CODE_REVIEW_LOOP_RESTART_10 Oracle-wave note)
50e731832 Code review wave: Oracle post-fallback-fix files (4 files, clean)
c830d86bb FOUNDRY reboot handoff 202609180351: BELT wave (fauna, code-review, structure/liquids builds)
3cedfdca9 rimflow: ledger sync (LIQUID_BOTTLE_LOOP_1 tank pass note)
52b9c584e LIQUID_BOTTLE_LOOP_1: build the universal-tank v1 slice — fill/drain at RM_LiquidTank
82cf04e80 EMBERSCYTHE_MANTIS_REAUTHOR_1: RUT_Emberscythe race+kind (the dead GR_Mantistanis, ours now)
0c86c019b rimflow: ledger sync (MLIE_FAUNA_ABSORPTION_1 Pass 12 note)
2cd0ebcb1 MLIE_FAUNA_ABSORPTION_1 Pass 12: port Gizka, Grank, GreaterKraytDragon, Hawkbat (56 -> 51 remaining); remove stale Nuna worklist entry
3f33928de rimflow: ledger sync (water-breathing design note, PYRELANDS_DENSITY_TRIPLE_1 filing)
d47ab4874 AQUATIC_WATER_BREATHING_GENE_1: design brief — one GeneDef + one CanSwim clause
1d55fa45d Pyrelands: plantDensity 3.0 + enforcer that beats the startup rewriter (owner: "three times that. No more small nudges")
e4c3d18dd rimflow: ledger sync (DIRTY_CODE_REVIEW_STANDING_LOOP_1 FlowWorks wave note)
6bc642cb9 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean 71 FlowWorks files this wave
d0b0d6b7b DIRTY_CODE_REVIEW_STANDING_LOOP_1: FlowWorks wave, 5 real bugs fixed across 71 files reviewed
c94704c67 CHARTER: any seat may close a genuinely-done item (owner ruling 2026-09-18); close NINEFOLD_GRAVSHIP_HOOK_SCOPE_1; record mod-enable ruling; file AQUATIC_WATER_BREATHING_GENE_1
9bf9ccf4e Activate mandrake.rm.environmentalhazards in both mod lists (owner: "Yes, both lists")
b8d87d692 ROT_LIVE_PREPARATIONS_1: brewing vessel, 3 teas, 4 symbionts, sale conscience (cards 1+6)
296d1dd83 rimflow: ledger sync (NINEFOLD_MISSING_EVENT_HOOKS_1 / NINEFOLD_GRAVSHIP_HOOK_SCOPE_1 notes)
e0ba9648e NINEFOLD_MISSING_EVENT_HOOKS_1: offline re-verify pass, no wiring gap found
1f1b0ec8c rimflow: ledger sync (MLIE_FAUNA_ABSORPTION_1 Pass 11 note)
bab45edca MLIE_FAUNA_ABSORPTION_1 Pass 11: port IridonianReek, Jakobeast, Jamel, Jimvu (60 -> 56 remaining)
b59ff976f rimflow: file MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1 (three inactive custom mods found this wave)
00da90518 VAULT_DUNGEON_BUILD_1: offline re-verify pass, no drift, one new finding
6bc5c684a DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean the 4 fixed RotSporeKit/AftermathRites files
562ae2718 DIRTY_CODE_REVIEW_STANDING_LOOP_1: RotSporeKit + AftermathRites/RaidRedesigner validation wave
785100e16 rimflow: pyrelands checkout closes 2 items; ENVHAZARDS_NEVER_ACTIVATED_1 filed; rot wave notes; bridge released
211b2f0c8 ROT_GUARDIAN_GROVES_1: three defended tea-source mushrooms + false-fruit lure (card 6: confession toggle)
1659c1793 rimflow: ledger sync (BELT wave notes: Mlie pass 10, Armoury review, liquid bottle art, xenotype fixes, structure batch)
e8aec8b25 TILE_STRUCTURE_DESIGNS_1: whisper batch 2 - Listening Dark + Sarlacc Sign (3/22 -> 5/22)
06dd34811 MLIE_FAUNA_ABSORPTION_1 Pass 10: port Gutkurr, Hrumph, Hssiss, Igitz (64 -> 60 remaining)
a63dc4d2a Rot wave shared wiring + FIX: b5b947fe9 shipped no code (csproj compile list)
94f1139bc ROT_WARM_MAT_1: warm-ground map component + grown furnace + Furnaceblood gene (card 3: free forever)
35680b323 ROT_SHEEN_WEATHER_1: Sheen weather reskin + exposure ladder (card 5: gear slows 4x, symbiont only full immunity)
4eab208d6 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark 58 Armoury files clean
0fc737f9d DIRTY_CODE_REVIEW_STANDING_LOOP_1: Armoury wave, two real bugs
512d1fb57 ROT_PALE_TREE_1: RUT_PaleTree anima reskin, psylink cap 2 (owner card 4) + RUT_PaleMoss
cbe48fdf7 LIQUID_BOTTLE_LOOP_1: real art for the bottle/bucket/barrel line + tank concept
5d5a16577 Xenotypes: give Sith Massassi the caste's own nameMaker (XENOTYPE_NONCOSMETIC_FIXES_1)
eaef4cf04 rimflow: drop FLUID_CANAL_MECHANIC_1 (absorbed into FLOWWORKS_BUILD_PROGRAM_1)
ae93947dd rimflow: bridge take/release (ROT-kit quicktests deferred, no restart this pass)
bc894b2ab Rot kit: all six owner cards RULED at the bench (spec + ledger)
cd237a4ac FOUNDRY reboot handoff 202609180218: Liquids/Rot wave, and a recovered dead agent
948c21d3b MSEDroidFix: add validation.py (VALIDATION_SCRIPT_BACKFILL_1); rimflow ledger sync
48b72ac41 MLIE_FAUNA_ABSORPTION_1 Pass 9: port Gelagrub, Gorg, Gornt, GraniteSlug (68 -> 64 remaining)
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-18T03:58:39Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
 M src/RimStarWars/SWBestiary/Defs/AbilityDefs/RSW_MlieWaveC_Abilities.xml
 M src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml
 M src/RimStarWars/SWBestiary/Defs/ThingDefs_Items/RSW_MlieWaveC_Resources.xml
 M src/RimStarWars/SWBestiary/Defs/ThoughtDefs/RSW_Bantha_Thoughts.xml
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-oracle.xml
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? deployed/config/ModsConfig.before-tier-warlab.xml
?? infrastructure/artpipe/active/rotscythe_v1_south.json
?? infrastructure/artpipe/active/twistingthornweed_v1.json
?? infrastructure/artpipe/active/wastewing_v1_north.json
?? infrastructure/artpipe/daemon_run_20260916_bench_restart.log
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json
?? infrastructure/state/.rimflow_conc_97j8px_9/
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
?? src/RimStarWars/SWBestiary/Textures/UI/Abilities/Ability_AnimalWeb.png
?? src/RimStarWars/SWBestiary/Textures/UI/Abilities/WebShot.png
?? src/RimStarWars/SWBestiary/Textures/swanimals/Fambaa/
?? src/RimStarWars/SWBestiary/Textures/swanimals/Horax/
?? src/RimStarWars/SWBestiary/Textures/swanimals/Kinrath/
?? src/RimStarWars/SWBestiary/Textures/swresource/EggNodule/
?? src/RimStarWars/SWBestiary/Textures/swresource/EggSlime/
?? src/RimStarWars/SWBestiary/Textures/swresource/Leather_Heavy/
?? src/RimStarWars/SWBestiary/Textures/swresource/Trophies/HoraxMaw.png
```

