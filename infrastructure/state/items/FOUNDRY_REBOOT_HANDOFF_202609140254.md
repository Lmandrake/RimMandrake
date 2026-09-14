# FOUNDRY_REBOOT_HANDOFF_202609140254 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609132338`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

`ARMOURY_MW2_CUT_1`'s content work is fully done and committed — but its own
"21 root-tag defs" estimate was stale by a whole second absorbed pack (16
more files, `Defs/Absorbed_KotorWeapons/ModularPartDefs/`, not named
anywhere in the item text). Always verify a spec's file/def COUNT by
grep/inventory before trusting it as a checklist — this project's items
drift out of date with the actual tree faster than they're re-read.

## What the owner should see

- Cutting MW2 turned out bigger than filed: 25 files deleted (not 21), including
  a whole second absorbed pack (`Absorbed_KotorWeapons/ModularPartDefs/`, 16
  files, 160 part/mount defs + 62 AbilityDefs) the item never named. Verified
  genuinely MW2-exclusive before deleting; flagging because it's a bigger cut
  than what was ruled, even though the ruling ("cut MW2 entirely") covers it.
- 3 generator scripts (`gen_additionalmods_absorption.py`,
  `gen_kotorcore_absorption.py`, `gen_kotorweapons_absorption.py`) still
  reference ModularWeapons2 and would REGENERATE the deleted files if anyone
  re-runs them against the donor mods. Not guarded yet — real risk of
  silently undoing this whole cut later.
- Cherry Picker's live SHIP cut list had drifted to UNRECOGNISED before I
  swapped it (someone's in-game edit, predates this work) — auto-archived to
  `CherryPicker.PRESWAP.20260913_192926.xml`, not investigated further.
- Saves folder cleanup (separate request, done earlier this session): 34
  files (661MB) moved to `Saves\_cleanup_archive_2026-09-14\` — not deleted,
  just out of RimWorld's save browser. Only `CANONICAL_ASHKARR_START_2026-09-12.rws`
  is visible now. Say the word if that archive should be hard-deleted.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `ARMOURY_MW2_CUT_1` — steps 1-7 done and committed (16dd80708, 6d9788435,
  203df86d1, 593cde847). Only step 8 remains: cold-load verify + resave
  canonical. **A restart was triggered at 2026-09-14T02:54Z** (Steam
  relaunch, confirmed via bridge `get_game_info` -> `no_game` beforehand, so
  no active colony was killed) and is still loading as of this handoff —
  full 594-mod list, expect ~15-25min from trigger time. Bridge was
  released after triggering so the next session can take it fresh.
  **Exact next action**: `rimflow bridge take`, poll `Player.log` for
  `"Bridge token:"`, confirm 0 `TypeInitializationException` for
  ModularWeapons2 and 0 red errors for `guy762_*` weapons, spawn a pawn
  holding `guy762_brifle`/`guy762_vblade` to confirm render+fire (positive
  sighting, not just absence of errors), THEN back up the Saves folder's
  keeper and resave the canonical start (stat before/after, confirm a NEW
  file appeared and no existing one changed size). Only then `rimflow close
  ARMOURY_MW2_CUT_1 --sha <the verify commit>`.
- `SMYH_MODULARWEAPONS_PAWNGEN_CRASH_1` — not touched (BENCH's claim, per
  owner's own caution mid-session not to step on it). Its resolution rides
  on `ARMOURY_MW2_CUT_1` landing (MW2 gone + SMYH restored fixes the
  transpiler-vs-moved-target crash this item diagnosed) — once step 8 above
  confirms clean, this item's own verify criteria are also satisfied and it
  can likely close too, but that call belongs to whoever holds it.

## Traps learned

- **A PreToolUse hook refuses a WHOLE compound Bash command, including
  everything before the flagged part, when it touches the ledger.** Hit
  this twice: `rm -f .git/index.lock; git add <ledger-path>; ...` as one
  command silently never ran the `rm` at all (the hook message says so —
  "NOTHING IN THAT COMMAND RAN" — but it's easy to miss and assume partial
  execution). Fix: isolate a lock-file removal into its OWN standalone Bash
  call, never combined with a ledger write in the same command.
- **`git status`'s two-column format matters**: staged-but-uncommitted
  ledger/queue files can persist across a failed commit attempt (index.lock
  contention) — `git status --short` before re-adding, don't blindly re-run
  `git add`.
- A `TaskOutput` call with `block: false` on a `local_agent` task can still
  dump the full raw JSONL transcript into context if the agent is mid-tool-call
  when polled — the tool's own description warns "Do NOT Read the .output
  file" for local_agent tasks but `TaskOutput` itself isn't exempt from the
  same overflow risk. Prefer just waiting for the completion notification
  over polling a running local_agent task.
- The rimbridge `rimworld/get_game_info` call returning `{"status": "no_game"}`
  is the correct way to confirm no active colony is loaded before a restart
  (GAME_STATE_WORKFLOW.md's "cannot tell which is loaded" gate) — cheaper
  and more certain than inferring from `./game`'s coarse RUNNING/UP reading.

## Closed since the last handoff (1)

- `CANON_REFERENCE_LIBRARY_1` — 779938cbb2c43ab0390afd9e2d94d519367af707

## Filed and still open (8) — the next seat's queue

- `CANON_CREATURE_REGEN_1` — Regenerate every SW-canon creature from library guidance (gated on CANON_REFERENCE_LIBRARY_1 + pilot sheet grades); wyyyschokk blue-grey/yellow-cross 
- `PYRELANDS_CREATURE_RERENDER_1` — One dayside biome fully re-rendered: ALL Pyrelands creatures under the full 2026-09-13 lawset, deployed, owner walks it in game — model: opus
- `WYYYSCHOKK_FANG_PENDANT_1` — Wyyyschokk fang pendant: hunt trophy apparel, bravery social thoughts with Wildsteam/Blackstar/Deep Tribe (defNames VERIFY), trade good everywhere
- `SMYH_MODULARWEAPONS_PAWNGEN_CRASH_1` — ShowMeYourHands DrawHandsOnWeapon patch emits invalid IL into ModularWeapons2 type-init: PawnGenerator crashes, ANY new map on the current list dies a
- `ARMOURY_MW2_CUT_1` — Cut ModularWeapons2 out of Armoury entirely: strip 181 comps + 92 graphicClass swaps, delete 21 root-tag defs + workbench + 3 research + 2 gadgets, re
- `SELFTEST_GIT_FIXTURE_TEMPLATE_1` — Selftest git fixtures spawn ~185 git processes per pre-commit run: .claude/hooks/selftest_queue_lint.py (~29 cases x5 spawns) + selftest_warn_unclosed
- `MIGRATE_NAMES_BATCH_MV_1` — migrate_names.py stage_folders() does per-row 'git mv' (~71 rows in naming_rename_map.csv) against the SHARED repo cwd=ROOT — serial spawns AND index.
- `CODE_REVIEW_STATUS_MIGRATE_BATCH_1` — code_review_status.py migrate-hashes backfill (lines ~783-795) does per-entry 'git show' — collapse to one 'git cat-file --batch'. One-time migration 

## Commits

```
593cde847 rimflow: note MW2 cut cold-load restart triggered
203df86d1 rimflow: note ARMOURY_MW2_CUT_1 progress (steps 1-7 done, 8 pending bridge)
16dd80708 ARMOURY_MW2_CUT_1: strip ModularWeapons2 from Armoury (steps 1-4, 6)
6d9788435 rimflow: supersede ARMOURY_MW2_DEP_UNGATED_1, start ARMOURY_MW2_CUT_1
97ec6399e Canon reference library: owner rulings propagated (24/24)
cbd971316 Owner rules CUT MW2 entirely: file ARMOURY_MW2_CUT_1 for FOUNDRY
7eae9b863 Fix canon review sheet: duplicate esc() declaration broke the whole page
bcc5c3ff2 Pyrelands art regen: re-file reference-less after reskin-validate REJECTed all 21
1435bbe0e MW2 removal census: MW2 is load-bearing for our own KotOR Armoury (undeclared)
325e35117 Bacta Tank core mod: builds clean (RimStarWars tier, mandrake.rsw.bacta)
7c22684ab Diagnose SMYH x MW2 pawn-gen crash (confirmed from source); file Bacta Tank full-kit tickets
fc6dbb8f7 rimflow: close CANON_REFERENCE_LIBRARY_1
779938cbb Canon reference library: served review sheet for 24 disagreement rulings
e36c3f8b5 Pyrelands fauna wiring: ruled 15-animal roster into RM_FE_Pyrelands wildAnimals
135ecd2c8 Canon reference library: complete (43/43 creatures)
de8f3b807 Canon reference library: priority wave (9/43 creatures)
b7f4c45ea Pyrelands rerender: roster derived, 21 non-canon art jobs filed, drawsize backfill extended
c0e72c4bf File the canon-library, Pyrelands rerender, canon regen, and fang-pendant tickets
```

## Game / bridge / tree state at wrap

- **STALE READING, corrected by hand**: the script above probed before this
  handoff's own restart trigger. Actual state as of this handoff: a Steam
  relaunch of RimWorldWin64 was triggered at 2026-09-14T02:54Z (full 594-mod
  ModsConfig, MW2 removed / SMYH restored). It was NOT yet up when this
  handoff was written — do not trust "RUNNING" above to mean loaded; measure
  fresh with `./game` and `rimworld/get_game_info` before doing anything.
- recorded  : UP (ledger stamp, not re-verified post-restart)
- Bridge: FREE since 2026-09-14T02:54:13Z (released deliberately after
  triggering the restart, so the next session takes it fresh once the load
  finishes)

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M Transient/legibility_final_review_2026-09-13/decisions.json
 D infrastructure/artpipe/active/pyrelands_barbslinger_v1_east.json
 D infrastructure/artpipe/active/pyrelands_barbslinger_v1_north.json
 D infrastructure/artpipe/active/pyrelands_barbslinger_v1_south.json
 M infrastructure/artpipe/art_status.html
 M infrastructure/artpipe/art_status.json
 D infrastructure/artpipe/pending/alientreepolluted_v1.json
 D infrastructure/artpipe/pending/ambrosia_v1.json
 D infrastructure/artpipe/pending/aridgrass_v1.json
 D infrastructure/artpipe/pending/arpeau_v1.json
 D infrastructure/artpipe/pending/bindweed_v1.json
 D infrastructure/artpipe/pending/bloddle_v1.json
 D infrastructure/artpipe/pending/bloodbouquet_v1.json
 D infrastructure/artpipe/pending/brambles_v1.json
 D infrastructure/artpipe/pending/bubblespore_v1.json
 D infrastructure/artpipe/pending/bush_v1.json
 D infrastructure/artpipe/pending/chakroot_v1.json
 D infrastructure/artpipe/pending/creepstern_v1.json
 D infrastructure/artpipe/pending/crimsoncushion_v1.json
 D infrastructure/artpipe/pending/crystalflower_v1.json
 D infrastructure/artpipe/pending/dervish_v1.json
 D infrastructure/artpipe/pending/doomsprout_v1.json
 D infrastructure/artpipe/pending/eclipsusflower_v1.json
 D infrastructure/artpipe/pending/eclipsusleaves_v1.json
 D infrastructure/artpipe/pending/felucianglowspore_v1.json
 D infrastructure/artpipe/pending/firelavender_v1.json
 D infrastructure/artpipe/pending/flakespirefungus_v1.json
 D infrastructure/artpipe/pending/frostleaf_v1.json
 D infrastructure/artpipe/pending/gargantuanlithops_v1.json
 D infrastructure/artpipe/pending/giantseptimum_v1.json
 D infrastructure/artpipe/pending/giantstikehr_v1.json
 D infrastructure/artpipe/pending/gianttoxicflower_v1.json
 D infrastructure/artpipe/pending/glowinggrass_v1.json
 D infrastructure/artpipe/pending/graygrass_v1.json
 D infrastructure/artpipe/pending/grimmoss_v1.json
 D infrastructure/artpipe/pending/gutterplantain_v1.json
 D infrastructure/artpipe/pending/halfalientree_v1.json
 D infrastructure/artpipe/pending/hardygrass_v1.json
 D infrastructure/artpipe/pending/healroot_v1.json
 D infrastructure/artpipe/pending/heatsinkfungus_v1.json
 D infrastructure/artpipe/pending/hubbagourd_v1.json
 D infrastructure/artpipe/pending/magmacactus_v1.json
 D infrastructure/artpipe/pending/mangrovepalm_v1.json
 D infrastructure/artpipe/pending/martyr_v1.json
 D infrastructure/artpipe/pending/mortalmorel_v1.json
 D infrastructure/artpipe/pending/mujafruit_v1.json
 D infrastructure/artpipe/pending/nogtyl_v1.json
 D infrastructure/artpipe/pending/nuitae_v1.json
 D infrastructure/artpipe/pending/nysyllin_v1.json
 D infrastructure/artpipe/pending/parasiticmangrove_v1.json
 D infrastructure/artpipe/pending/poisonplanttallgrass_v1.json
 D infrastructure/artpipe/pending/poisonshrub_v1.json
 D infrastructure/artpipe/pending/polux_v1.json
 D infrastructure/artpipe/pending/poluxbush_v1.json
 D infrastructure/artpipe/pending/poxsorghum_v1.json
 D infrastructure/artpipe/pending/primordialgrass_v1.json
 D infrastructure/artpipe/pending/primordialtallgrass_v1.json
 D infrastructure/artpipe/pending/pusmelon_v1.json
 D infrastructure/artpipe/pending/pyrelands_boomsnake_v2_east.json
 D infrastructure/artpipe/pending/pyrelands_boomsnake_v2_north.json
 D infrastructure/artpipe/pending/pyrelands_boomsnake_v2_south.json
 D infrastructure/artpipe/pending/pyrelands_firehawk_v3_east.json
 D infrastructure/artpipe/pending/pyrelands_firehawk_v3_north.json
 D infrastructure/artpipe/pending/pyrelands_firehawk_v3_south.json
 D infrastructure/artpipe/pending/pyrelands_firewasp_v2_east.json
 D infrastructure/artpipe/pending/pyrelands_firewasp_v2_north.json
 D infrastructure/artpipe/pending/pyrelands_firewasp_v2_south.json
 D infrastructure/artpipe/pending/pyrelands_furnacebeast_v2_east.json
 D infrastructure/artpipe/pending/pyrelands_furnacebeast_v2_north.json
 D infrastructure/artpipe/pending/pyrelands_furnacebeast_v2_south.json
 D infrastructure/artpipe/pending/pyrelands_furnacebeast_v3_east.json
 D infrastructure/artpipe/pending/pyrelands_furnacebeast_v3_north.json
 D infrastructure/artpipe/pending/pyrelands_furnacebeast_v3_south.json
 D infrastructure/artpipe/pending/pyrelands_mantistanis_v1_east.json
 D infrastructure/artpipe/pending/pyrelands_mantistanis_v1_north.json
 D infrastructure/artpipe/pending/pyrelands_mantistanis_v1_south.json
 D infrastructure/artpipe/pending/pyrelands_mantistanis_v2_east.json
 D infrastructure/artpipe/pending/pyrelands_mantistanis_v2_north.json
 D infrastructure/artpipe/pending/pyrelands_mantistanis_v2_south.json
 D infrastructure/artpipe/pending/pyrelands_razorjack_v1_east.json
 D infrastructure/artpipe/pending/pyrelands_razorjack_v1_north.json
 D infrastructure/artpipe/pending/pyrelands_razorjack_v1_south.json
 D infrastructure/artpipe/pending/rainbowtongue_v1.json
 D infrastructure/artpipe/pending/ravennettle_v1.json
 D infrastructure/artpipe/pending/recurvedstropharia_v1.json
 D infrastructure/artpipe/pending/redbugloss_v1.json
 D infrastructure/artpipe/pending/redleaves_v1.json
 D infrastructure/artpipe/pending/redplantstall_v1.json
 D infrastructure/artpipe/pending/reeds_v1.json
 D infrastructure/artpipe/pending/rgtoxigrass_v1.json
 D infrastructure/artpipe/pending/rimenodules_v1.json
 D infrastructure/artpipe/pending/ripthorn_v1.json
 D infrastructure/artpipe/pending/sagecrust_v1.json
 D infrastructure/artpipe/pending/scorchedstars_v1.json
 D infrastructure/artpipe/pending/septimum_v1.json
 D infrastructure/artpipe/pending/sewerreed_v1.json
 D infrastructure/artpipe/pending/shinecap_v1.json
 D infrastructure/artpipe/pending/shrublow_v1.json
 D infrastructure/artpipe/pending/skulltop_v1.json
 D infrastructure/artpipe/pending/slimecasia_v1.json
 D infrastructure/artpipe/pending/slimyfern_v1.json
 D infrastructure/artpipe/pending/slimytree_v1.json
 D infrastructure/artpipe/pending/snaketails_v1.json
 D infrastructure/artpipe/pending/tallslimygrass_v1.json
 D infrastructure/artpipe/pending/talltoxigrass_v1.json
 D infrastructure/artpipe/pending/tangletea_v1.json
 D infrastructure/artpipe/pending/tentacular_v1.json
 D infrastructure/artpipe/pending/tinklegrass_v1.json
 D infrastructure/artpipe/pending/tooketrap_v1.json
 D infrastructure/artpipe/pending/toxibulb_v1.json
 D infrastructure/artpipe/pending/toxicivy_v1.json
 D infrastructure/artpipe/pending/toxipotato_v1.json
 D infrastructure/artpipe/pending/tropicalchokevine_v1.json
 D infrastructure/artpipe/pending/tumorbulbhyacinth_v1.json
 D infrastructure/artpipe/pending/twisteddandelion_v1.json
 D infrastructure/artpipe/pending/twistingthorngrass_v1.json
 D infrastructure/artpipe/pending/twistingthornweed_v1.json
 D infrastructure/artpipe/pending/violetwimple_v1.json
 D infrastructure/artpipe/pending/weepingtoxberry_v1.json
 D infrastructure/artpipe/pending/wildrashroot_v1.json
 D infrastructure/artpipe/pending/witchesoyster_v1.json
 D infrastructure/artpipe/pending/wrinklecap_v1.json
 M infrastructure/artpipe/registry.jsonl
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/dashboards/hub/data/artsheets.json
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/dashboards/hub/data/publish_ready.json
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/modcheck_status.json
 M src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll
 M src/RimMandrake/Utils/atomic_copy.py
 M src/RimMandrake/Utils/modcheck/runner.py
 M src/RimMandrake/Utils/modcheck/selftest.py
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-oracle.xml
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? deployed/config/ModsConfig.before-tier-warlab.xml
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? design/Jawa/worldbuilding/review/serve_homeless.log
?? infrastructure/artpipe/daemon_run_20260911_105041.log
?? infrastructure/artpipe/daemon_run_20260913_134734.log
?? infrastructure/artpipe/daemon_run_20260913_152021.log
?? infrastructure/artpipe/daemon_run_20260913_153234.log
?? infrastructure/artpipe/daemon_run_20260913_155045.log
?? infrastructure/artpipe/daemon_run_20260913_170729.log
?? infrastructure/artpipe/done/aa_frostmite_v1_east.json
?? infrastructure/artpipe/done/aa_frostmite_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.manifest.json
?? infrastructure/artpipe/done/aaklac_v1.json
?? infrastructure/artpipe/done/aaklac_v1.manifest.json
?? infrastructure/artpipe/done/abtoxigrass_v1.json
?? infrastructure/artpipe/done/abtoxigrass_v1.manifest.json
?? infrastructure/artpipe/done/agariluxprime_v1.json
?? infrastructure/artpipe/done/agariluxprime_v1.manifest.json
?? infrastructure/artpipe/done/aliengrass_v1.json
?? infrastructure/artpipe/done/aliengrass_v1.manifest.json
?? infrastructure/artpipe/done/alientree_v1.json
?? infrastructure/artpipe/done/alientree_v1.manifest.json
?? infrastructure/artpipe/done/alientreepolluted_v1.json
?? infrastructure/artpipe/done/alientreepolluted_v1.manifest.json
?? infrastructure/artpipe/done/ambrosia_v1.json
?? infrastructure/artpipe/done/ambrosia_v1.manifest.json
?? infrastructure/artpipe/done/anooba_toyfig_a_east.json
?? infrastructure/artpipe/done/anooba_toyfig_a_east.manifest.json
?? infrastructure/artpipe/done/anooba_toyfig_b2_east.json
?? infrastructure/artpipe/done/anooba_toyfig_b2_east.manifest.json
?? infrastructure/artpipe/done/aridgrass_v1.json
?? infrastructure/artpipe/done/aridgrass_v1.manifest.json
?? infrastructure/artpipe/done/arpeau_v1.json
?? infrastructure/artpipe/done/arpeau_v1.manifest.json
?? infrastructure/artpipe/done/ashrunner_v1_east_r2.json
?? infrastructure/artpipe/done/ashrunner_v1_east_r2.manifest.json
?? infrastructure/artpipe/done/ashrunner_v1_north.json
?? infrastructure/artpipe/done/ashrunner_v1_north.manifest.json
?? infrastructure/artpipe/done/ashrunner_v1_south_r2.json
?? infrastructure/artpipe/done/ashrunner_v1_south_r2.manifest.json
?? infrastructure/artpipe/done/bilespawn_v1_east.json
?? infrastructure/artpipe/done/bilespawn_v1_east.manifest.json
?? infrastructure/artpipe/done/bilespawn_v1_north_r2.json
?? infrastructure/artpipe/done/bilespawn_v1_north_r2.manifest.json
?? infrastructure/artpipe/done/bilespawn_v1_south.json
?? infrastructure/artpipe/done/bilespawn_v1_south.manifest.json
?? infrastructure/artpipe/done/bindweed_v1.json
?? infrastructure/artpipe/done/bindweed_v1.manifest.json
?? infrastructure/artpipe/done/bleedingtooth_v1.json
?? infrastructure/artpipe/done/bleedingtooth_v1.manifest.json
?? infrastructure/artpipe/done/bloddle_v1.json
?? infrastructure/artpipe/done/bloddle_v1.manifest.json
?? infrastructure/artpipe/done/bloodbouquet_v1.json
?? infrastructure/artpipe/done/bloodbouquet_v1.manifest.json
?? infrastructure/artpipe/done/boma_toyfig_a_east.json
?? infrastructure/artpipe/done/boma_toyfig_a_east.manifest.json
?? infrastructure/artpipe/done/boma_toyfig_b_east.json
?? infrastructure/artpipe/done/boma_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/boma_v1_east.json
?? infrastructure/artpipe/done/boma_v1_east.manifest.json
?? infrastructure/artpipe/done/boma_v1_north.json
?? infrastructure/artpipe/done/boma_v1_north.manifest.json
?? infrastructure/artpipe/done/boma_v1_south.json
?? infrastructure/artpipe/done/boma_v1_south.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_east.json
?? infrastructure/artpipe/done/borcatu_v1_east.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_north.json
?? infrastructure/artpipe/done/borcatu_v1_north.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_south.json
?? infrastructure/artpipe/done/borcatu_v1_south.manifest.json
?? infrastructure/artpipe/done/brambles_v1.json
?? infrastructure/artpipe/done/brambles_v1.manifest.json
?? infrastructure/artpipe/done/brightbells_v1.json
?? infrastructure/artpipe/done/brightbells_v1.manifest.json
?? infrastructure/artpipe/done/bryolux_v1.json
?? infrastructure/artpipe/done/bryolux_v1.manifest.json
?? infrastructure/artpipe/done/bubblespore_v1.json
?? infrastructure/artpipe/done/bubblespore_v1.manifest.json
?? infrastructure/artpipe/done/bush_v1.json
?? infrastructure/artpipe/done/bush_v1.manifest.json
?? infrastructure/artpipe/done/chakroot_v1.json
?? infrastructure/artpipe/done/chakroot_v1.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_east.json
?? infrastructure/artpipe/done/cinderwing_v1_east.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_north.json
?? infrastructure/artpipe/done/cinderwing_v1_north.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_south.json
?? infrastructure/artpipe/done/cinderwing_v1_south.manifest.json
?? infrastructure/artpipe/done/corronip_v1_east.json
?? infrastructure/artpipe/done/corronip_v1_east.manifest.json
?? infrastructure/artpipe/done/corronip_v1_north.json
?? infrastructure/artpipe/done/corronip_v1_north.manifest.json
?? infrastructure/artpipe/done/corronip_v1_south.json
?? infrastructure/artpipe/done/corronip_v1_south.manifest.json
?? infrastructure/artpipe/done/creepstern_v1.json
?? infrastructure/artpipe/done/creepstern_v1.manifest.json
?? infrastructure/artpipe/done/crimsoncap_v1.json
?? infrastructure/artpipe/done/crimsoncap_v1.manifest.json
?? infrastructure/artpipe/done/crimsoncushion_v1.json
?? infrastructure/artpipe/done/crimsoncushion_v1.manifest.json
?? infrastructure/artpipe/done/crystalflower_v1.json
?? infrastructure/artpipe/done/crystalflower_v1.manifest.json
?? infrastructure/artpipe/done/crystalhorn_v1.json
?? infrastructure/artpipe/done/crystalhorn_v1.manifest.json
?? infrastructure/artpipe/done/dactillion_toyfig_b_east.json
?? infrastructure/artpipe/done/dactillion_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_east.json
?? infrastructure/artpipe/done/dactillion_v1_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_north.json
?? infrastructure/artpipe/done/dactillion_v1_north.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_south.json
?? infrastructure/artpipe/done/dactillion_v1_south.manifest.json
?? infrastructure/artpipe/done/dervish_v1.json
?? infrastructure/artpipe/done/dervish_v1.manifest.json
?? infrastructure/artpipe/done/dewback_toyfig_a_east.json
?? infrastructure/artpipe/done/dewback_toyfig_a_east.manifest.json
?? infrastructure/artpipe/done/dewback_toyfig_b_east.json
?? infrastructure/artpipe/done/dewback_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/dewshrooms_v1.json
?? infrastructure/artpipe/done/dewshrooms_v1.manifest.json
?? infrastructure/artpipe/done/direwail_v1_east.json
?? infrastructure/artpipe/done/direwail_v1_east.manifest.json
?? infrastructure/artpipe/done/direwail_v1_north.json
?? infrastructure/artpipe/done/direwail_v1_north.manifest.json
?? infrastructure/artpipe/done/direwail_v1_south.json
?? infrastructure/artpipe/done/direwail_v1_south.manifest.json
?? infrastructure/artpipe/done/doomsprout_v1.json
?? infrastructure/artpipe/done/doomsprout_v1.manifest.json
?? infrastructure/artpipe/done/duskram_v1_east.json
?? infrastructure/artpipe/done/duskram_v1_east.manifest.json
?? infrastructure/artpipe/done/duskram_v1_north.json
?? infrastructure/artpipe/done/duskram_v1_north.manifest.json
?? infrastructure/artpipe/done/duskram_v1_south.json
?? infrastructure/artpipe/done/duskram_v1_south.manifest.json
?? infrastructure/artpipe/done/eclipsusflower_v1.json
?? infrastructure/artpipe/done/eclipsusflower_v1.manifest.json
?? infrastructure/artpipe/done/eclipsusleaves_v1.json
?? infrastructure/artpipe/done/eclipsusleaves_v1.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_east.json
?? infrastructure/artpipe/done/emberscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_north.json
?? infrastructure/artpipe/done/emberscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_south.json
?? infrastructure/artpipe/done/emberscythe_v1_south.manifest.json
?? infrastructure/artpipe/done/fanback_toyfig_a_east.json
?? infrastructure/artpipe/done/fanback_toyfig_a_east.manifest.json
?? infrastructure/artpipe/done/fanback_toyfig_b_east.json
?? infrastructure/artpipe/done/fanback_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/fanback_v1_east.json
?? infrastructure/artpipe/done/fanback_v1_east.manifest.json
?? infrastructure/artpipe/done/fanback_v1_north.json
?? infrastructure/artpipe/done/fanback_v1_north.manifest.json
?? infrastructure/artpipe/done/fanback_v1_south.json
?? infrastructure/artpipe/done/fanback_v1_south.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_east.json
?? infrastructure/artpipe/done/featherfeel_v1_east.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_north.json
?? infrastructure/artpipe/done/featherfeel_v1_north.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_south.json
?? infrastructure/artpipe/done/featherfeel_v1_south.manifest.json
?? infrastructure/artpipe/done/felucianglowspore_v1.json
?? infrastructure/artpipe/done/felucianglowspore_v1.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_east.json
?? infrastructure/artpipe/done/fenshear_v1_east.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_north_r2.json
?? infrastructure/artpipe/done/fenshear_v1_north_r2.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_south.json
?? infrastructure/artpipe/done/fenshear_v1_south.manifest.json
?? infrastructure/artpipe/done/firelavender_v1.json
?? infrastructure/artpipe/done/firelavender_v1.manifest.json
?? infrastructure/artpipe/done/firevine_fireweed_v1.json
?? infrastructure/artpipe/done/firevine_fireweed_v1.manifest.json
?? infrastructure/artpipe/done/firevinetree_v1.json
?? infrastructure/artpipe/done/firevinetree_v1.manifest.json
?? infrastructure/artpipe/done/flakespirefungus_v1.json
?? infrastructure/artpipe/done/flakespirefungus_v1.manifest.json
?? infrastructure/artpipe/done/frostleaf_v1.json
?? infrastructure/artpipe/done/frostleaf_v1.manifest.json
?? infrastructure/artpipe/done/fruitingbodies_v1.json
?? infrastructure/artpipe/done/fruitingbodies_v1.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_east.json
?? infrastructure/artpipe/done/fumeback_v1_east.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_north.json
?? infrastructure/artpipe/done/fumeback_v1_north.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_south.json
?? infrastructure/artpipe/done/fumeback_v1_south.manifest.json
?? infrastructure/artpipe/done/gargantuanlithops_v1.json
?? infrastructure/artpipe/done/gargantuanlithops_v1.manifest.json
?? infrastructure/artpipe/done/giantagarilux_v1.json
?? infrastructure/artpipe/done/giantagarilux_v1.manifest.json
?? infrastructure/artpipe/done/giantagaritox_v1.json
?? infrastructure/artpipe/done/giantagaritox_v1.manifest.json
?? infrastructure/artpipe/done/giantgamma_v1.json
?? infrastructure/artpipe/done/giantgamma_v1.manifest.json
?? infrastructure/artpipe/done/giantseptimum_v1.json
?? infrastructure/artpipe/done/giantseptimum_v1.manifest.json
?? infrastructure/artpipe/done/giantstikehr_v1.json
?? infrastructure/artpipe/done/giantstikehr_v1.manifest.json
?? infrastructure/artpipe/done/gianttoxicflower_v1.json
?? infrastructure/artpipe/done/gianttoxicflower_v1.manifest.json
?? infrastructure/artpipe/done/globularplant_v1.json
?? infrastructure/artpipe/done/globularplant_v1.manifest.json
?? infrastructure/artpipe/done/glowingagarilux_v1.json
?? infrastructure/artpipe/done/glowingagarilux_v1.manifest.json
?? infrastructure/artpipe/done/glowinggrass_v1.json
?? infrastructure/artpipe/done/glowinggrass_v1.manifest.json
?? infrastructure/artpipe/done/glowstool_v1.json
?? infrastructure/artpipe/done/glowstool_v1.manifest.json
?? infrastructure/artpipe/done/gomphoeria_v1.json
?? infrastructure/artpipe/done/gomphoeria_v1.manifest.json
?? infrastructure/artpipe/done/gorewalker_v1_east.json
?? infrastructure/artpipe/done/gorewalker_v1_east.manifest.json
?? infrastructure/artpipe/done/gorewalker_v1_north.json
?? infrastructure/artpipe/done/gorewalker_v1_north.manifest.json
?? infrastructure/artpipe/done/gorewalker_v1_south.json
?? infrastructure/artpipe/done/gorewalker_v1_south.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.manifest.json
?? infrastructure/artpipe/done/grank_v1_east.json
?? infrastructure/artpipe/done/grank_v1_east.manifest.json
?? infrastructure/artpipe/done/grank_v1_north.json
?? infrastructure/artpipe/done/grank_v1_north.manifest.json
?? infrastructure/artpipe/done/grank_v1_south.json
?? infrastructure/artpipe/done/grank_v1_south.manifest.json
?? infrastructure/artpipe/done/graygrass_v1.json
?? infrastructure/artpipe/done/graygrass_v1.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.manifest.json
?? infrastructure/artpipe/done/greenrockfern_v1.json
?? infrastructure/artpipe/done/greenrockfern_v1.manifest.json
?? infrastructure/artpipe/done/greylady_v1.json
?? infrastructure/artpipe/done/greylady_v1.manifest.json
?? infrastructure/artpipe/done/grimmoss_v1.json
?? infrastructure/artpipe/done/grimmoss_v1.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_east.json
?? infrastructure/artpipe/done/grubhorn_v1_east.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_north.json
?? infrastructure/artpipe/done/grubhorn_v1_north.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_south.json
?? infrastructure/artpipe/done/grubhorn_v1_south.manifest.json
?? infrastructure/artpipe/done/gutterplantain_v1.json
?? infrastructure/artpipe/done/gutterplantain_v1.manifest.json
?? infrastructure/artpipe/done/halfalientree_v1.json
?? infrastructure/artpipe/done/halfalientree_v1.manifest.json
?? infrastructure/artpipe/done/hardygrass_v1.json
?? infrastructure/artpipe/done/hardygrass_v1.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_east.json
?? infrastructure/artpipe/done/hawkbat_v1_east.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_north.json
?? infrastructure/artpipe/done/hawkbat_v1_north.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_south.json
?? infrastructure/artpipe/done/hawkbat_v1_south.manifest.json
?? infrastructure/artpipe/done/healroot_v1.json
?? infrastructure/artpipe/done/healroot_v1.manifest.json
?? infrastructure/artpipe/done/heatsinkfungus_v1.json
?? infrastructure/artpipe/done/heatsinkfungus_v1.manifest.json
?? infrastructure/artpipe/done/hubbagourd_v1.json
?? infrastructure/artpipe/done/hubbagourd_v1.manifest.json
?? infrastructure/artpipe/done/huskrunner_v1_east.json
?? infrastructure/artpipe/done/huskrunner_v1_east.manifest.json
?? infrastructure/artpipe/done/huskrunner_v1_north.json
?? infrastructure/artpipe/done/huskrunner_v1_north.manifest.json
?? infrastructure/artpipe/done/huskrunner_v1_south.json
?? infrastructure/artpipe/done/huskrunner_v1_south.manifest.json
?? infrastructure/artpipe/done/hydenocktree_v1.json
?? infrastructure/artpipe/done/hydenocktree_v1.manifest.json
?? infrastructure/artpipe/done/iashiphus_v1.json
?? infrastructure/artpipe/done/iashiphus_v1.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_east.json
?? infrastructure/artpipe/done/insectomorph_v1_east.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_north.json
?? infrastructure/artpipe/done/insectomorph_v1_north.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_south.json
?? infrastructure/artpipe/done/insectomorph_v1_south.manifest.json
?? infrastructure/artpipe/done/jogantree_v1.json
?? infrastructure/artpipe/done/jogantree_v1.manifest.json
?? infrastructure/artpipe/done/jungletree_v1.json
?? infrastructure/artpipe/done/jungletree_v1.manifest.json
?? infrastructure/artpipe/done/keeningcordax_v1.json
?? infrastructure/artpipe/done/keeningcordax_v1.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_east.json
?? infrastructure/artpipe/done/kinrath_v1_east.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_north.json
?? infrastructure/artpipe/done/kinrath_v1_north.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_south.json
?? infrastructure/artpipe/done/kinrath_v1_south.manifest.json
?? infrastructure/artpipe/done/largeslimytree_v1.json
?? infrastructure/artpipe/done/largeslimytree_v1.manifest.json
?? infrastructure/artpipe/done/lilacbeacon_v1.json
?? infrastructure/artpipe/done/lilacbeacon_v1.manifest.json
?? infrastructure/artpipe/done/magmacactus_v1.json
?? infrastructure/artpipe/done/magmacactus_v1.manifest.json
?? infrastructure/artpipe/done/mangrovepalm_v1.json
?? infrastructure/artpipe/done/mangrovepalm_v1.manifest.json
?? infrastructure/artpipe/done/mangrovetree_v1.json
?? infrastructure/artpipe/done/mangrovetree_v1.manifest.json
?? infrastructure/artpipe/done/martyr_v1.json
?? infrastructure/artpipe/done/martyr_v1.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_east.json
?? infrastructure/artpipe/done/mireflit_v1_east.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_north.json
?? infrastructure/artpipe/done/mireflit_v1_north.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_south.json
?? infrastructure/artpipe/done/mireflit_v1_south.manifest.json
?? infrastructure/artpipe/done/mireflitwarden_v1_east.json
?? infrastructure/artpipe/done/mireflitwarden_v1_east.manifest.json
?? infrastructure/artpipe/done/mireflitwarden_v1_north_r2.json
?? infrastructure/artpipe/done/mireflitwarden_v1_north_r2.manifest.json
?? infrastructure/artpipe/done/mireflitwarden_v1_south.json
?? infrastructure/artpipe/done/mireflitwarden_v1_south.manifest.json
?? infrastructure/artpipe/done/miremoth_v1_east.json
?? infrastructure/artpipe/done/miremoth_v1_east.manifest.json
?? infrastructure/artpipe/done/miremoth_v1_north.json
?? infrastructure/artpipe/done/miremoth_v1_north.manifest.json
?? infrastructure/artpipe/done/miremoth_v1_south.json
?? infrastructure/artpipe/done/miremoth_v1_south.manifest.json
?? infrastructure/artpipe/done/mortalmorel_v1.json
?? infrastructure/artpipe/done/mortalmorel_v1.manifest.json
?? infrastructure/artpipe/done/mujafruit_v1.json
?? infrastructure/artpipe/done/mujafruit_v1.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_east.json
?? infrastructure/artpipe/done/mycolith_v1_east.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_north.json
?? infrastructure/artpipe/done/mycolith_v1_north.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_south.json
?? infrastructure/artpipe/done/mycolith_v1_south.manifest.json
?? infrastructure/artpipe/done/nogtyl_v1.json
?? infrastructure/artpipe/done/nogtyl_v1.manifest.json
?? infrastructure/artpipe/done/nuitae_v1.json
?? infrastructure/artpipe/done/nuitae_v1.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_east.json
?? infrastructure/artpipe/done/ollopom_v1_east.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_north.json
?? infrastructure/artpipe/done/ollopom_v1_north.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_south.json
?? infrastructure/artpipe/done/ollopom_v1_south.manifest.json
?? infrastructure/artpipe/done/oozemaw_v1_east.json
?? infrastructure/artpipe/done/oozemaw_v1_east.manifest.json
?? infrastructure/artpipe/done/oozemaw_v1_north.json
?? infrastructure/artpipe/done/oozemaw_v1_north.manifest.json
?? infrastructure/artpipe/done/oozemaw_v1_south.json
?? infrastructure/artpipe/done/oozemaw_v1_south.manifest.json
?? infrastructure/artpipe/done/orray_v1_east.json
?? infrastructure/artpipe/done/orray_v1_east.manifest.json
?? infrastructure/artpipe/done/orray_v1_north.json
?? infrastructure/artpipe/done/orray_v1_north.manifest.json
?? infrastructure/artpipe/done/orray_v1_south.json
?? infrastructure/artpipe/done/orray_v1_south.manifest.json
?? infrastructure/artpipe/done/parasiticmangrove_v1.json
?? infrastructure/artpipe/done/parasiticmangrove_v1.manifest.json
?? infrastructure/artpipe/done/pekopeko_toyfig_b_east.json
?? infrastructure/artpipe/done/pekopeko_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_east.json
?? infrastructure/artpipe/done/pekopeko_v1_east.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_north.json
?? infrastructure/artpipe/done/pekopeko_v1_north.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_south.json
?? infrastructure/artpipe/done/pekopeko_v1_south.manifest.json
?? infrastructure/artpipe/done/poisonplanttallgrass_v1.json
?? infrastructure/artpipe/done/poisonplanttallgrass_v1.manifest.json
?? infrastructure/artpipe/done/poisonshrub_v1.json
?? infrastructure/artpipe/done/poisonshrub_v1.manifest.json
?? infrastructure/artpipe/done/polux_v1.json
?? infrastructure/artpipe/done/polux_v1.manifest.json
?? infrastructure/artpipe/done/poluxbush_v1.json
?? infrastructure/artpipe/done/poluxbush_v1.manifest.json
?? infrastructure/artpipe/done/poxsorghum_v1.json
?? infrastructure/artpipe/done/poxsorghum_v1.manifest.json
?? infrastructure/artpipe/done/primordialgrass_v1.json
?? infrastructure/artpipe/done/primordialgrass_v1.manifest.json
?? infrastructure/artpipe/done/primordialtallgrass_v1.json
?? infrastructure/artpipe/done/primordialtallgrass_v1.manifest.json
?? infrastructure/artpipe/done/pusmelon_v1.json
?? infrastructure/artpipe/done/pusmelon_v1.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v2_east.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v2_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v2_north.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v2_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v2_south.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v2_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v2_east.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v2_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v2_north.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v2_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v2_south.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v2_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_firehawk_v3_east.json
?? infrastructure/artpipe/done/pyrelands_firehawk_v3_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_firehawk_v3_north.json
?? infrastructure/artpipe/done/pyrelands_firehawk_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_firehawk_v3_south.json
?? infrastructure/artpipe/done/pyrelands_firehawk_v3_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_firewasp_v2_east.json
?? infrastructure/artpipe/done/pyrelands_firewasp_v2_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_firewasp_v2_north.json
?? infrastructure/artpipe/done/pyrelands_firewasp_v2_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_firewasp_v2_south.json
?? infrastructure/artpipe/done/pyrelands_firewasp_v2_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_furnacebeast_v3_east.json
?? infrastructure/artpipe/done/pyrelands_furnacebeast_v3_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_furnacebeast_v3_north.json
?? infrastructure/artpipe/done/pyrelands_furnacebeast_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_furnacebeast_v3_south.json
?? infrastructure/artpipe/done/pyrelands_furnacebeast_v3_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v2_east.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v2_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v2_north.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v2_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v2_south.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v2_south.manifest.json
?? infrastructure/artpipe/done/rainbowtongue_v1.json
?? infrastructure/artpipe/done/rainbowtongue_v1.manifest.json
?? infrastructure/artpipe/done/ravennettle_v1.json
?? infrastructure/artpipe/done/ravennettle_v1.manifest.json
?? infrastructure/artpipe/done/recurvedstropharia_v1.json
?? infrastructure/artpipe/done/recurvedstropharia_v1.manifest.json
?? infrastructure/artpipe/done/redbugloss_v1.json
?? infrastructure/artpipe/done/redbugloss_v1.manifest.json
?? infrastructure/artpipe/done/redleaves_v1.json
?? infrastructure/artpipe/done/redleaves_v1.manifest.json
?? infrastructure/artpipe/done/redplantstall_v1.json
?? infrastructure/artpipe/done/redplantstall_v1.manifest.json
?? infrastructure/artpipe/done/reeds_v1.json
?? infrastructure/artpipe/done/reeds_v1.manifest.json
?? infrastructure/artpipe/done/rgtoxigrass_v1.json
?? infrastructure/artpipe/done/rgtoxigrass_v1.manifest.json
?? infrastructure/artpipe/done/rimenodules_v1.json
?? infrastructure/artpipe/done/rimenodules_v1.manifest.json
?? infrastructure/artpipe/done/ripthorn_v1.json
?? infrastructure/artpipe/done/ripthorn_v1.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_east.json
?? infrastructure/artpipe/done/rotscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_north.json
?? infrastructure/artpipe/done/rotscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_south_r2.json
?? infrastructure/artpipe/done/rotscythe_v1_south_r2.manifest.json
?? infrastructure/artpipe/done/sagecrust_v1.json
?? infrastructure/artpipe/done/sagecrust_v1.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_east.json
?? infrastructure/artpipe/done/scarrend_v1_east.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_north.json
?? infrastructure/artpipe/done/scarrend_v1_north.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_south.json
?? infrastructure/artpipe/done/scarrend_v1_south.manifest.json
?? infrastructure/artpipe/done/scorchedstars_v1.json
?? infrastructure/artpipe/done/scorchedstars_v1.manifest.json
?? infrastructure/artpipe/done/septimum_v1.json
?? infrastructure/artpipe/done/septimum_v1.manifest.json
?? infrastructure/artpipe/done/sewerreed_v1.json
?? infrastructure/artpipe/done/sewerreed_v1.manifest.json
?? infrastructure/artpipe/done/shinecap_v1.json
?? infrastructure/artpipe/done/shinecap_v1.manifest.json
?? infrastructure/artpipe/done/shiro_v1_east.json
?? infrastructure/artpipe/done/shiro_v1_east.manifest.json
?? infrastructure/artpipe/done/shiro_v1_north.json
?? infrastructure/artpipe/done/shiro_v1_north.manifest.json
?? infrastructure/artpipe/done/shiro_v1_south.json
?? infrastructure/artpipe/done/shiro_v1_south.manifest.json
?? infrastructure/artpipe/done/shrublow_v1.json
?? infrastructure/artpipe/done/shrublow_v1.manifest.json
?? infrastructure/artpipe/done/skulltop_v1.json
?? infrastructure/artpipe/done/skulltop_v1.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_east.json
?? infrastructure/artpipe/done/slagmaw_v1_east.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_north.json
?? infrastructure/artpipe/done/slagmaw_v1_north.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_south.json
?? infrastructure/artpipe/done/slagmaw_v1_south.manifest.json
?? infrastructure/artpipe/done/slimecasia_v1.json
?? infrastructure/artpipe/done/slimecasia_v1.manifest.json
?? infrastructure/artpipe/done/slimyfern_v1.json
?? infrastructure/artpipe/done/slimyfern_v1.manifest.json
?? infrastructure/artpipe/done/slimytree_v1.json
?? infrastructure/artpipe/done/slimytree_v1.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_east.json
?? infrastructure/artpipe/done/sludrin_v1_east.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_north.json
?? infrastructure/artpipe/done/sludrin_v1_north.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_south.json
?? infrastructure/artpipe/done/sludrin_v1_south.manifest.json
?? infrastructure/artpipe/done/snaketails_v1.json
?? infrastructure/artpipe/done/snaketails_v1.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_east.json
?? infrastructure/artpipe/done/sporehulk_v1_east.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_north.json
?? infrastructure/artpipe/done/sporehulk_v1_north.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_south.json
?? infrastructure/artpipe/done/sporehulk_v1_south.manifest.json
?? infrastructure/artpipe/done/sugarfamewort_v1.json
?? infrastructure/artpipe/done/sugarfamewort_v1.manifest.json
?? infrastructure/artpipe/done/tallslimygrass_v1.json
?? infrastructure/artpipe/done/tallslimygrass_v1.manifest.json
?? infrastructure/artpipe/done/talltoxigrass_v1.json
?? infrastructure/artpipe/done/talltoxigrass_v1.manifest.json
?? infrastructure/artpipe/done/tanglerootmangrove_v1.json
?? infrastructure/artpipe/done/tanglerootmangrove_v1.manifest.json
?? infrastructure/artpipe/done/tangletea_v1.json
?? infrastructure/artpipe/done/tangletea_v1.manifest.json
?? infrastructure/artpipe/done/tentacular_v1.json
?? infrastructure/artpipe/done/tentacular_v1.manifest.json
?? infrastructure/artpipe/done/tinklegrass_v1.json
?? infrastructure/artpipe/done/tinklegrass_v1.manifest.json
?? infrastructure/artpipe/done/tooketrap_v1.json
?? infrastructure/artpipe/done/tooketrap_v1.manifest.json
?? infrastructure/artpipe/done/toxibulb_v1.json
?? infrastructure/artpipe/done/toxibulb_v1.manifest.json
?? infrastructure/artpipe/done/toxicgamma_v1.json
?? infrastructure/artpipe/done/toxicgamma_v1.manifest.json
?? infrastructure/artpipe/done/toxicivy_v1.json
?? infrastructure/artpipe/done/toxicivy_v1.manifest.json
?? infrastructure/artpipe/done/toxipotato_v1.json
?? infrastructure/artpipe/done/toxipotato_v1.manifest.json
?? infrastructure/artpipe/done/tropicalchokevine_v1.json
?? infrastructure/artpipe/done/tropicalchokevine_v1.manifest.json
?? infrastructure/artpipe/done/tumorbulbhyacinth_v1.json
?? infrastructure/artpipe/done/tumorbulbhyacinth_v1.manifest.json
?? infrastructure/artpipe/done/twisteddandelion_v1.json
?? infrastructure/artpipe/done/twisteddandelion_v1.manifest.json
?? infrastructure/artpipe/done/twistingthorngrass_v1.json
?? infrastructure/artpipe/done/twistingthorngrass_v1.manifest.json
?? infrastructure/artpipe/done/twistingthornwood_v1.json
?? infrastructure/artpipe/done/twistingthornwood_v1.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_east.json
?? infrastructure/artpipe/done/verdaunt_v1_east.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_north.json
?? infrastructure/artpipe/done/verdaunt_v1_north.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_south.json
?? infrastructure/artpipe/done/verdaunt_v1_south.manifest.json
?? infrastructure/artpipe/done/violetwimple_v1.json
?? infrastructure/artpipe/done/violetwimple_v1.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_east.json
?? infrastructure/artpipe/done/vornskyr_v1_east.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_north.json
?? infrastructure/artpipe/done/vornskyr_v1_north.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_south.json
?? infrastructure/artpipe/done/vornskyr_v1_south.manifest.json
?? infrastructure/artpipe/done/wastewing_v1_east.json
?? infrastructure/artpipe/done/wastewing_v1_east.manifest.json
?? infrastructure/artpipe/done/wastewing_v1_north_r2.json
?? infrastructure/artpipe/done/wastewing_v1_north_r2.manifest.json
?? infrastructure/artpipe/done/wastewing_v1_south_r2.json
?? infrastructure/artpipe/done/wastewing_v1_south_r2.manifest.json
?? infrastructure/artpipe/done/weepingtoxberry_v1.json
?? infrastructure/artpipe/done/weepingtoxberry_v1.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_east.json
?? infrastructure/artpipe/done/whisperbird_v1_east.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_north.json
?? infrastructure/artpipe/done/whisperbird_v1_north.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_south.json
?? infrastructure/artpipe/done/whisperbird_v1_south.manifest.json
?? infrastructure/artpipe/done/wildradagast_v1.json
?? infrastructure/artpipe/done/wildradagast_v1.manifest.json
?? infrastructure/artpipe/done/wildrashroot_v1.json
?? infrastructure/artpipe/done/wildrashroot_v1.manifest.json
?? infrastructure/artpipe/done/witchesoyster_v1.json
?? infrastructure/artpipe/done/witchesoyster_v1.manifest.json
?? infrastructure/artpipe/done/wrinklecap_v1.json
?? infrastructure/artpipe/done/wrinklecap_v1.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.manifest.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.manifest.json
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.json
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/ashrunner_v1_east.json
?? infrastructure/artpipe/failed/ashrunner_v1_east.manifest.json
?? infrastructure/artpipe/failed/ashrunner_v1_south.json
?? infrastructure/artpipe/failed/ashrunner_v1_south.manifest.json
?? infrastructure/artpipe/failed/bilespawn_v1_north.json
?? infrastructure/artpipe/failed/bilespawn_v1_north.manifest.json
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.json
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/fenshear_v1_north.json
?? infrastructure/artpipe/failed/fenshear_v1_north.manifest.json
?? infrastructure/artpipe/failed/mireflitwarden_v1_north.json
?? infrastructure/artpipe/failed/mireflitwarden_v1_north.manifest.json
?? infrastructure/artpipe/failed/nysyllin_v1.json
?? infrastructure/artpipe/failed/nysyllin_v1.manifest.json
?? infrastructure/artpipe/failed/rotscythe_v1_south.json
?? infrastructure/artpipe/failed/rotscythe_v1_south.manifest.json
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.json
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.json
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/twistingthornweed_v1.json
?? infrastructure/artpipe/failed/twistingthornweed_v1.manifest.json
?? infrastructure/artpipe/failed/wastewing_v1_north.json
?? infrastructure/artpipe/failed/wastewing_v1_north.manifest.json
?? infrastructure/artpipe/failed/wastewing_v1_south.json
?? infrastructure/artpipe/failed/wastewing_v1_south.manifest.json
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.json
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json
?? infrastructure/artpipe/registry.jsonl.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
?? infrastructure/state/items/PIT_TRAP_VISUAL_REDESIGN_1.md
```

