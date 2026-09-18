# FOUNDRY_REBOOT_HANDOFF_202609181937 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609181738`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

The debug menu's `Actions\Spawn Pawn...\<kindDef>` is not a reliable way to test
whether a PawnKindDef generates correctly — it can silently redress an existing
world pawn (wrong kindDef, sometimes incapable of violence) instead of generating
fresh. `jawa/spawn_pawn` does not have this problem (`kindActual`/`kindSubstituted`
prove it). This cost real time diagnosing BAREHANDED_MELEE_FALLBACK_1's last 5
kinds before the confound was found; full writeup in
`skills/rimbridge/references/traps.md`.

## What the owner should see

Nothing this wave — both closes this session (BAREHANDED_MELEE_FALLBACK_1,
VALIDATE_PATCH_FULL_TREE_SWEEP_1) were straightforward measurement/triage with no
ambiguous call for him.

## What is half-done, and where it stops

- `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1` — doing; unchanged this session (not
  touched). NEXT: re-check the null-key ArgumentNullException against a load on
  the NEXT restart's 636-mod list (weathersuite now included) — MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1
  is done (BENCH), so the modlist-gap theory is now testable, not theoretical.
- `GIZKA_NEWGAME_NRE_FIX_1` — doing/blocked; unchanged this session (not touched).
  NEXT: this needs a COLD LOAD with gizka reactivated (mod activation only takes
  effect on restart) — run the isolating bisection the item prescribes (gizka
  alone, mid-size list, FlowWorks fix already live) on the next restart, not a
  live-session test.
- `OASIS_LANDMARK_PLACEMENT_1` — ready, not started. Its item file was missing
  `## spec`/`## verify` headers (fixed, no content change). NEXT: this is NOT a
  solo FOUNDRY pickup — its own referenced spec (`weeping_stones.md` §12) says
  "none of it is ratified" and there are no pre-existing names for the 236 tiles
  to execute against; it needs an owner conversation first (matches the
  established "biome sheets are a conversation loop" pattern), not 236 invented
  names.

## Traps learned

- The debug menu's `Actions\Spawn Pawn...\<kindDef>` can redress an existing
  world pawn instead of generating fresh, landing the wrong kindDef (see: "the
  one thing to carry forward" above, and `skills/rimbridge/references/traps.md`).
- `jawa/list_pawns`/`jawa/pawn_get` report a bare pawn id; `rimworld/execute_debug_action`'s
  `pawnId` wants `Thing_<id>` even for a `ToolMapForPawns` kill action, and that
  action NRE'd silently on 2 of 34 kill attempts this session — fall back to
  `jawa/damage` looped until `dead:true`, since `amount` is a request not a
  result (filed: LESSONS_INBOX).

## Closed since the last handoff (2)

- `BAREHANDED_MELEE_FALLBACK_1` — d9a1b3fcb4625a5828fcdaedffdc09e713401d5e
- `VALIDATE_PATCH_FULL_TREE_SWEEP_1` — 0a61db589d80f37eaa97543ec7491dcde32989ed

## Filed and still open (3) — the next seat's queue

- `WORLDGEN_CLICK_RECONCILE_1` — Verify the 2026-09-12 canonical start save against what the gate docs said was owed at click time
- `FULL_LOAD_RESIDUE_TRIAGE_1` — Full-list load residue beyond the FlowWorks water fix: RSW patch failures, RSW_*Juv config errors, TYR Scribe refs
- `CAVERNS_PARITY_BUILD_1` — Donor-free crystal Deeps: M-tier parity build on the Lantern Deeps route - START NOW (owner timing ruling)

## Commits

```
859f4b40e Sync health-dashboard derived state after this session's closes
ce9682702 ledger: parity-build notes (build landed, incident suppression ruled+built, pre-cut list)
f0becf6f9 Lantern Deeps: suppress the donor's incident list underground (owner ruling, vanilla disallowedBiomes)
0c900c0be Close VALIDATE_PATCH_FULL_TREE_SWEEP_1: full triage, no hidden real defects
cd88cd08c CAVERNS_PARITY_BUILD_1: Lantern Deeps donor-free - RUT-owned biome/terrain/flora/GenSteps, DLL rebuilt clean
0a61db589 Close BAREHANDED_MELEE_FALLBACK_1: 5 undiagnosed kinds proven clean live
4b0b100a8 Deploy-sweep caveat: peer bestiary WIP rode the Maguana apply (lesson + attribution note)
d9a1b3fcb ledger: Maguana port executed, deployed; premise correction recorded
3b1db3f94 RSW_Maguana: port out of Biomes! Caverns, wired into the Forge (CAVERNS_PARITY_BUILD_1 r5)
9999d119d Research trio ruled: port the 4 ruled projects, retire the trio (route + spec on the item)
aef95f6c2 ledger: Maguana art accepted without review (owner ruling, crash-elimination speed)
f8fae43f4 Crash item closed (root cause + ruled remedy); parity build claimed by BENCH on owner priority
f40dfff4f Caverns: all six scoping rulings recorded; CAVERNS_PARITY_BUILD_1 filed for FOUNDRY (run now)
f53f7e8cc Caverns replacement scoping delivered (tier M, Lantern Deeps route); Jawa-in-RSW ruled and closed
94eff3de5 Bitterleaf ruled: island prison colony, deliberately roadless (owner verbatim recorded)
ba5a8b7a9 Worldmap pass measurements + rulings: 96 settlements live-canon stamped, rain-excuse doctrine, warm crags stand, roads authored, river sink verified
476aef3cb Decay sweep batches A+C: close 4 verified-done items, unblock livestock trio + desert wraps
4c7cec491 Decay sweep batch B: close MOD_CONSOLIDATION_SPRINT_1 + IKEE_MYNOCK_ART_REGEN_1 (done-unrecorded, verified), unblock WEAPONS_DONOR_RETIREMENT_1 (blocker chain dissolved; Armoury dep caveat noted)
f082d783e Worldmap pass rulings 6-9: shade hinge ratified, droid enclaves one faction, WeatherSuite enabled, region re-audit ordered
c7509bd3d Worldmap pass: worldgen click ruled DONE - gate docs become records; load-2 strings; deploy-plan lesson
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-18T19:25:40Z

Uncommitted (each line below now says whose it is —
yours, the other seat's, a subagent's):

```
?? defs.sqlite   BENCH — dump refresh from tonight's owner-ordered restart
?? deployed/config/ModsConfig.before-tier-oracle.xml   BENCH — tier-testing snapshots from tonight's restart, not mine
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   BENCH — tier-testing snapshots from tonight's restart, not mine
?? deployed/config/ModsConfig.before-tier-warlab.xml   BENCH — tier-testing snapshots from tonight's restart, not mine
?? infrastructure/artpipe/active/rut_agelesscap_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_brewingvessel_v1_south.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_euphoriccrown_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_falsefruit_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_furnacecap_plant_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_gene_furnaceblood_icon_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_grownfurnace_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_liveingredient_agelesscap_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_liveingredient_euphoriccrown_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_liveingredient_regenerantveil_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_liveprep_toxicinjection_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_livingfurnacecap_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_palemoss_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_paletree_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_regenerantveil_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_symbiont_mycoid_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_symbiont_nightwake_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_symbiont_quickflesh_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_symbiont_sheenblood_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_tea_agereversal_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_tea_bioregeneration_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/active/rut_tea_pleasure_v1.json   artpipe daemon — untracked in-flight job file, not mine
?? infrastructure/artpipe/daemon_run_20260916_bench_restart.log   artpipe daemon — old run log predating this session, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/twistingthornweed_v1_r2.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   artpipe daemon — untracked completed job file, not mine
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/codexcal_mantrap_r4.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/nysyllin_v1_r2.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   artpipe daemon — untracked failed job file, not mine
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow — concurrency scratch dir, not mine
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing since 2026-09-11, not mine
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Pufferpig.xml   BENCH/canon-art pipeline — new SWBestiary creature defs, not mine
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Qormot.xml   BENCH/canon-art pipeline — new SWBestiary creature defs, not mine
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Ronto.xml   BENCH/canon-art pipeline — new SWBestiary creature defs, not mine
?? src/RimStarWars/SWBestiary/Textures/swanimals/Pufferpig/   BENCH/canon-art pipeline — new SWBestiary creature defs, not mine
?? src/RimStarWars/SWBestiary/Textures/swanimals/Qormot/   BENCH/canon-art pipeline — new SWBestiary creature defs, not mine
?? src/RimStarWars/SWBestiary/Textures/swanimals/Ronto/   BENCH/canon-art pipeline — new SWBestiary creature defs, not mine
?? src/RimStarWars/SWBestiary/Textures/swresource/Meat_Ronto/   BENCH/canon-art pipeline — new SWBestiary creature defs, not mine
```

