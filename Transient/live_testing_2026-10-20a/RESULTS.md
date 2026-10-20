# Retirement Wave 2 — deployment transaction and cold load (FOUNDRY helper, 2026-10-20)

Authority: owner 2026-10-19 *"retire all the mods we don't need so we can repaint the world, then build slowly back"*;
prep `design/RimMandrake/world_remake_2026-10-19/08_wave2_prep.md` (3da7bf3bf). Bridge holding = blanket authorization (CLAUDE.md).

## Status
- [x] 1 bridge take
- [x] 2 backups (ModsConfig, Cherry Picker, Player.log)
- [x] 3 game down (PID 44116 killed by PID; stamped going-down, down)
- [x] 4 deploys (dry run, apply)
- [x] 5 ModsConfig 380 + Cherry Picker WAVE2 swap
- [x] 6 cold load + harvest (load #1 aborted, #2 READY 684 s, #3 verification READY 806 s)
- [x] 7 owed rows on a test map (rhossak A1 A2 PASS, A3 FAIL; WAVE1 A3 needs a save edit)
- [ ] 8 release, commit, publish

## Transaction
- `git pull`: up to date at e9d3ca356 (every deployed file = origin/main; the Ummisk helper's uncommitted TheForge
  Source is not deployed: Source/ is skipped and no TheForge DLL was built).
- Backups: live ModsConfig (498, == FULL.LATEST) → `infrastructure/state/modlists/ModsConfig.LIVE_BACKUP_20261020_pre_wave2.xml`;
  SHIP Cherry Picker → `CherryPicker.SHIP_pre_wave2.xml` (here); live CP archived by the swap as
  `infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20261019_193709.xml`; last 498-run Player.log → `playerlog_pre_shutdown_498.txt`.
- Whole-tree deploy plan (`deploy_plan_all.txt`): drift only in the 10 mods 08 §5 names. Applied 26 files
  (`deploy_apply.txt`), all VERIFIED: 9 About.xml, ResearchRetag patch, 9 SWBestiary textures (committed art), 7 UtinniPatches
  (5 BiomeDefs incl. RUT_TheForge = the stale RM_TinkleGrass copy, Cauldron_Rename, JawaWorld_BiomeMix). Kept (no --prune):
  game-only `UtinniPatches/Defs/IdeoSymbolDefs_placeholder`.
- JawaBench companion (`JAWABENCH_BRIDGETOOLS_DLL_REBUILD_OWED`): `build.py --gm` plan showed NO tool removal with --gm
  (fire_incident/send_letter in DLL, closure scan clean); `--apply` deployed (`jawabench_build_*.txt`).
- Cherry Picker: WAVE2_CANDIDATE → SHIP → live, 2,329 → 1,747 cuts; `--status` LIVE == SHIP (15ba0497).
- Live ModsConfig = `ModsConfig.FULL.WAVE2_380_2026-10-19.xml`: parsed 380, 0 dupes, sha equal.

## Cold load (380)
- **Load #1 ABORTED (19:37-19:46, killed by PID).** First error (line 829): `Could not resolve cross-reference: No
  Verse.PawnKindDef named RM_Rhossak` (+ RM_GalledRhossak), then `ConfigErrors() of RUT_Cauldron` NRE and Giddy-Up's
  `BiomeDef.CommonalityOfAnimal` ArgumentNullException: one root cause. The UtinniPatches deploy put the new RUT_Cauldron
  (names the rhossak) live, but the rhossak defs live in the COMPOSED `RimMandrake.Biomes` mod, which the whole-tree plan
  does not cover (`--compose biomes` is a separate plan). Deploy owed since d69358451. Log: `playerlog_load1_aborted.txt`.
  🔑 Lesson: a Wave deploy must plan BOTH `deploy_custom_mods.py` and `--compose biomes`.
- Fix: `--compose biomes --apply`, 26 files VERIFIED (`deploy_apply_biomes.txt`): Cauldron rhossak defs/art/DLL, the
  Ummisk helper's COMMITTED TheForge DLL + RM_Ummisk defs (4b30e8676 — committed, so deployed; the only game-down window),
  Greentide/Miasma/LeaningScrub/Wasteland/WeepingStones def+art drift. Game-only AB_TinkleGrass stand-in PNGs kept (no prune).
- **Load #2: READY in 684 s** (498 list: 962 s), pid 35076 (`launch_receipt.txt`). Running mods **380**, expected-list
  missing 0 / extra 0, retired packageIds loaded: none (`running_mods_menu.json`, `harvest_menu.txt` vs Wave 1 menu harvest).
  - Exceptions 3 (498: 5), all pre-existing: CannibalPirate / PirateYttakin ConfigErrors, `brtrue`. **Ours 0, 0 new signatures.**
  - Xref naming ours 0 (498: 1, the stale RM_TinkleGrass — fixed). Texture misses ours 0. Config errors 14 (498: 21);
    ours 1 = `RM_UmmiskBody: no parts vulnerable to frostbite` — the concurrent Ummisk helper's new BodyDef (4b30e8676),
    not Wave 2; left for that helper.
  - **Patch failures 21 (498: 4), ours 18 — NEW, caused by Wave 2.** 16 `WeaponTags_Renormalise.xml` rows (BS_/BX_/DA_/DV_/IW_
    weapons of dropped mods), `AncientArsenal_Ashkarr.xml` AncientSoldierBoss, `Waterline_Lane1.xml` DA_LeviathanCrab. Cause:
    08 §2's scan counted "a Conditional on that def" as a guard, but these Conditionals test a CHILD of the def and their
    nomatch Adds to the def itself, which fails once the def is gone. Fix c674b7832: wrapped in a def-exists Conditional
    (113 generated rows + the 2 hand rows; generator `weapon_tag_audit.py` emits the same shape); validate_patch 0 errors on the
    380 load set; deployed live (`deploy_apply_guards.txt`). **Takes effect at the next cold load — not yet seen live.**
- Save `RM_TestSite_calm_v1_AREAFIX2`: `save_def_census` 0 unresolved thing defs (85 other refs, same 20 defs as Wave 1);
  `save_class_census` 7 sites, 0 fatal. Loaded in 35 s (load_areafix2.py with the name given explicitly: `test_site_saves`
  now names `calm_v2`, for which no _AREAFIX2 exists — the first try waited 420 s on a non-existent save). Its "unverified" =
  site-tile mismatch vs v2 + `jawa/quiet_site` refused in the CAMPAIGN profile (harness, not mod). Load exceptions: the same
  10 classes as Wave 1, Scribe 'Could not load reference' 3,090 = Wave 1 3,090. Dialogs closed.
- 2 × 30 s at Superfast to tick 20,369: **0 exceptions**; spam is the pre-existing Beer (2,023) / Intimacy warnings.

- **Load #3 (verification): READY in 806 s**, running 380, missing/extra 0. Exceptions 3 (same three pre-existing), ours 0;
  xref ours 0; texture misses ours 0; **patch failures 3, ours 0** (498: 4), so the c674b7832 guards work live; config
  errors 14, ours 1 (the Ummisk BodyDef again). 0 new signatures vs load #2 (`harvest_menu3.txt`).
- Def dump `DefDump/captures/2026-10-20T03-35-54Z` (380 mods). `selftest_researchretag.py`: only the known techprint-gate
  row FAILs (RG_/VFEI2_), as 08 §2 expects. Then I dropped the 16 retired packageIds from ResearchRetag's forceLoadAfter (44 left)
  and deployed it. Live `ResearchRetag` chain `retag_rows_vs_dump`: 5/5 PASS, including `force_load_after_names_every_donor_owner`.
- `ModsConfig.FULL.LATEST.xml` is now the 380 list. The old 498 copy is `ModsConfig.FULL.PRE_WAVE2_498.xml` (here) and
  also the LIVE_BACKUP.

## Owed rows
- **Companion profile:** the first rhossak run was all UNMEASURED — `jawa/safe_advance` refused, CAMPAIGN profile: the TEST
  grant in `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench\companion_profile.json`
  expired 2026-10-19T20:00Z (not the DLL rebuild). Renewed with the same keys to `2026-10-20T06:30:00Z` (old copy:
  `companion_profile_before.json`). Handshake: effectiveProfile test.
- **Cauldron rhossak chain** (`python.exe Transient/acc_biomes/run_live_suite.py Cauldron --chains=rhossak`, no list swap),
  run twice, same verdicts (`cauldron_rhossak_run2.txt`, `_run3.txt`; sheets `Transient/modcheck/Cauldron_20261020T0321*Z.html`):
  - A1 `rhossak_binds_to_thornwood` **PASS** (both read "Bound to twisting thornwood" 600 ticks after spawn).
  - A2 `rhossak_stays_by_its_tree` **PASS** (neither beyond tether+4 after 5000 ticks).
  - A3 `rhossak_bind_off_unbinds` **FAIL**, reproducible: with `rhossakBindEnabled` off the pane still reads "Bound to
    twisting thornwood". Probed: the static reads back False and stays False across ~3 s of ticking; the deployed
    `RimMandrake.Cauldron.dll` srchash matches source; `CompInspectStringExtra` returns null when the setting is off and is
    the only "Bound to" string in src; `jawa/inspect_string` calls `GetInspectString` directly. Mechanism UNRESOLVED (next:
    read the pane of a freshly spawned rhossak with the setting already off, to split "comp ignores the static" from
    "the pane string is cached per pawn"). Not a Wave 2 effect.
  - A4-A7 not scripted (owed live rows per the item). Recorded: `rimflow verify` A1/A2 pass, A3 fail.
- **WAVE1_MODLIST_RETIRE_37_IN_ONE_LOAD**: only A3 is still owed, and it needs the pre-edited canonical start save
  (`wave1_save_preedit.py`). That save edit was not done here, so nothing was recorded. Wave 2's 118 drops change what that
  pre-edit has to strip, so A3 should be re-scoped to the 380 list before anyone runs it.

## Rollback
`ModsConfig.LIVE_BACKUP_20261020_pre_wave2.xml` (498) + `CherryPicker.PRESWAP.20261019_193709.xml` (2,329).

## End state
Game UP on the 380 list (load #3, healthy, main menu), Cherry Picker 1,747. Bridge released. Companion TEST grant expires
2026-10-20T06:30Z. Pointers:
- `RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD`: A3 FAIL; NEXT: spawn a rhossak with rhossakBindEnabled already off and read its pane, to find whether the comp ignores the static or the pane is cached.
- Ummisk (FORGE_SNAILHOLE…): config error `RM_UmmiskBody: no parts vulnerable to frostbite`; NEXT: the Ummisk helper gives the BodyDef a frostbite-vulnerable part.
- `WAVE1_MODLIST_RETIRE_37_IN_ONE_LOAD` A3: NEXT: re-scope the canonical start-save pre-edit to the 380 list, then run C1-C7.
- No Wave 2 ledger item exists; NEXT: file one, or attach this RESULTS to WORLD_REMAKE, and record L2 verify against it.
