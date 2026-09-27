# FOUNDRY_REBOOT_HANDOFF_202609272103 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609270423`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

`rimworld/load_game_ready` — the documented fallback for the known
`start_debug_game_ready` world-gen crash — is NOT safe either: it hits the identical
`SetupForQuickTestPlay`/`WorldPathGrid` `ArgumentOutOfRangeException` when loading a
real save on the full 629-mod list, confirmed on two different saves this session.
There is currently NO working path to a live-tested game state on the full mod list.
Filed as `LOAD_GAME_READY_MAPGEN_CRASH_1`. Anything gated on "load the game and check"
is blocked on this until it's root-caused — don't spend bridge time re-discovering it.

## What the owner should see

- `LOAD_GAME_READY_MAPGEN_CRASH_1` (above) — the live-testing pipeline is broken on the
  full mod list, not just the debug-game path. Needs Desktop-side engine investigation;
  nobody has started on root cause yet, only confirmed the symptom twice.
- A RimWorldWin64 process is currently RUNNING, left over from the crash diagnosis
  above — bridge is FREE (released cleanly), nobody is driving it. Worth a look before
  assuming it's safe to leave, or just close it.
- The subagent-concurrency cap you set this window (one at a time, until 2026-09-30
  15:00 PST) is still in effect — flagging so it's visible if you check in before then.

## What is half-done, and where it stops

- `GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1` — mechanism (Harmony postfixes on
  `GenSight.LineOfSight`, per-plant opt-in comp) already built by a prior session, this
  window found it built-but-undeployed, rebuilt clean and deployed it, sound on static
  inspection. Blocked on live proof by `LOAD_GAME_READY_MAPGEN_CRASH_1`. NEXT: once a
  working load path exists, run the built-in "Sight-block probe/stress" dev action and
  close.
- `MIASMA_SCUTTLER_PREDATION_1` — `RM_CompPlantPredator` built, deployed, statically
  verified (0 warnings, correct `tickerType Long` for a `Plant`-derived def) by an
  earlier session; left in `doing` on purpose rather than closed false, same live-proof
  blocker. NEXT: once a working load path exists, spawn a plant+scuttler, step ticks,
  confirm the kill+mote, then close.

## Traps learned

- `rimworld/load_game_ready` is not the safe fallback CLAUDE.md's engine-facts section
  implied — it hits the same world-gen crash as `start_debug_game_ready` on a real save
  (filed: LOAD_GAME_READY_MAPGEN_CRASH_1; see also LESSONS_INBOX.md).
- Windows Git Credential Manager crashes on every push from a WSL git worktree, hit
  identically across 8+ independent worktree agents this session — route around with a
  `gh auth token`-embedded push URL, never wait on a retry (filed: CLAUDE.md Git
  section, LESSONS_INBOX.md).
- `git reset --keep origin/main` is the correct fix when the shared main tree's local
  HEAD has commits that look "unpushed" but were actually already republished under new
  SHAs by someone else's `shared_sync.py` run — verify by commit-message search on
  `origin/main` before resetting, never assume the content is lost (see:
  `SHARED_SYNC_DROPS_PEER_COMMITS_1`).

## Closed since the last handoff (11)

- `BLUEDESERT_ORPHAN_LOAD_CRASH_1` — 99776e796566541029a8f0d8197051b79ec80c08
- `DIVING_STALE_DEPLOYED_FILES_1` — a20f0ddda
- `SUMP_TARVAULT_TICKER_NEVER_1` — b71a2efd249901c9a614c72b068905ecb99e7194
- `RUT_PROPANELAKE_FROZEN_DENSITY_1` — a20f0ddda4798c042140bdb61d5748780d803b04
- `WETBULB_IS_A_THIRD_EXPOSURE_ENGINE_1` — 34ba1c6d17ede64c6c77533e6eef18dd43cae385
- `HAZARD_PROTECTION_STATS_UNSEEN_BY_AI_1` — 504b6042e
- `PATCH_MAYREQUIRE_GUARD_INERT_1` — 45b8eb09cf4b504ea5920e87535a878ec4bc3575
- `ARTPIPE_SALVAGE_REJECTED_SIZE_MISMATCH_1` — d9b13fa9244c53f25a3ed451aa5ca3ba3b495762
- `LIQUID_TERRAIN_AUTHORED_TWICE_1` — 35ef9f6ae71889a25522e590d7038fb75f1d90ea
- `GREYSEA_CATCH_TIER_RENAME_1` — 27859b6eeea120f52464bf4b0fd1c49cda1e60b5
- `GREYSEA_SALTDOME_SCATTER_OOB_1` — ff27cd5bdbd4d8b9a989decc2e9a17a0ea68e2fd

## Filed and still open (7) — the next seat's queue

- `UTINNIPATCHES_ORPHAN_AUDIT_1` — Audit the full list of files deploy_custom_mods.py reports 'in game, not in repo' under UtinniPatches (and other mods) for stale/dangerous orphans vs.
- `TERMINALBIOMES_REVIEW_FIXES_1` — TerminalBiomes 29-file review fix wave: 2 dead tickerType mechanisms (vaulisk lure never springs, mobile glower never runs), 6 more BUGs, 6 RISKs, 4 N
- `WAVEGLASS_PANEL_REPLACES_FLOOR_PLANT_1` — Retire RM_MoldMatRoof: the waveglass is a sky, not a floor plant - replace it with a shed panel that drifts down and is harvested
- `TWILIGHT_TENANCY_PAPER_REMOVAL_1` — Remove the Twilight tenancy paper layer from shipped code: delete RM_SkylightRight, RM_WellChart, RM_ClaimBuoy, the poaching-standing tracker and char
- `LOAD_GAME_READY_MAPGEN_CRASH_1` — rimworld/load_game_ready also hits the SetupForQuickTestPlay map-gen crash on the full 629-mod list
- `RUT_RAREGREYCATCHES_DEFNAME_COLLISION_1` — Same defName RUT_RareGreyCatches (ThingSetMakerDef) exists in two separate mods
- `SELFTEST_FAILURES_TRIAGE_1` — Four pre-existing selftest failures found by a full run 2026-09-27 (none caused by that day's artpipe diff): (1) block_dll_source_mismatch 5/6 - 'DLL 

## Commits

```
67b5b1dae queue: re-render BENCH/FOUNDRY views
42356e90c RM_FlameStatuary: set tickerType Normal so CompTick actually fires
52a8aa664 ledger sync: BENCH seat-ready event (own append, found uncommitted in shared tree)
656a51d20 rimflow: close GREYSEA_SALTDOME_SCATTER_OOB_1 at ff27cd5bd
7eb6df165 GREYSEA_SALTDOME_SCATTER_OOB_1: Harmony-guard vanilla's cluster-centre scatter bug
41f910dd2 Fix stale text in closed PROPANE_LAKE_PIPE_MECHANICS_1: said "Nothing built yet"
cef0868a4 BENCH handoff: four-sea sitting closed, lease economy removed, facing chain live
5e7ef79d5 chore: artpipe state churn + 19 speculative renders; ledger union pre-handoff
5e29c1a42 Twilight docs: delete the lease economy per the 2026-09-27 removal ruling
47496b055 queue: re-render FOUNDRY view after rebase
cce5827b4 chore: health-dashboard auto-refresh; sight-block load_game_ready crash screenshots
86b7bd40b GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1: rebuild+deploy sight-block mechanism; live probe blocked
fa6bcf684 Ledger union + SPECULATIVE_ART_COMMISSION_1: 19 speculative jobs queued
58037e52d rimflow: file RUT_RAREGREYCATCHES_DEFNAME_COLLISION_1
c8a1695a6 Ledger sync: four-sea flora sitting rulings + tenancy removal filed
ed328bddf chore: health dashboard auto-rebuild artifacts
aa4fd4167 queue: re-render after second rebase-merge of the ledger
1ca51dd4a ledger: close GREYSEA_CATCH_TIER_RENAME_1
86e0bc3ef GREYSEA_CATCH_TIER_RENAME_1: Grey Sea catch items RUT_ -> RM_ (invented names, wrong tier)
07676bd1d ARTPIPE_FACING_COHERENCE_1 S2: north/south derive from the accepted east master
... 87 more: git log --oneline faba57a84..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : DOWN  → corrected to UP, measured now
- Bridge: FREE    since 2026-09-27T17:03:50Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
 M Transient/codebase_health.json   ambient -- health-publisher daemon, predates this window
 M Transient/codebase_health_artifact.html   ambient -- health-publisher daemon, predates this window
 M infrastructure/dashboards/hub/data/health.json   ambient -- health-publisher daemon, predates this window
 M infrastructure/state/codebase_health_last.json   ambient -- health-publisher daemon, predates this window
?? deployed/config/ModsConfig.before-tier-firehawk.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-leaningscrub.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_bluedesert.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_contagion.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_feverwood.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_floodedcanyon.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_forsakencrags.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_gelatinousslime.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_greentide.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_leaningscrub.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_longshade.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_miasma.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_nightsideice.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_poisonforest.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_pyrelands.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_rustcathedral.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_stillsand.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_terminalbiomes.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_theforge.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_therot.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_thesump.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_wasteland.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_webwork.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-proof_weepingstones.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? infrastructure/dashboards/hub/tabs/maturity.html   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? infrastructure/dashboards/hub/utinni_control_room_standalone.html   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? infrastructure/state/logs/harvested/   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260926_142047.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_restoring_seashores_bacta_2026-09-25T175356.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_seashores_enable_2026-09-25T133443.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? infrastructure/state/rescued/LanternDeeps_RUT/Assemblies/   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
?? src/RimMandrake/Utils/firehawk_flight_probe.py   pre-existing -- confirmed by wake-triage fork this window as predating this session, not mid-edit by anyone
```

