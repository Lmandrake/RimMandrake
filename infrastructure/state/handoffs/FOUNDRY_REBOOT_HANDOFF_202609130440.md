# FOUNDRY_REBOOT_HANDOFF_202609130440 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609130316`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

Both FOUNDRY standing lanes are genuinely caught up right now, not just quiet:
`code_review_status.py list --show-untracked` shows **zero DIRTY files** anywhere
in the tree, and the flora `art:improve` channel from `ART_REGEN_FLORA_WAVE1_QUEUE_1`
is **fully queued** (all 89 remaining rows filed across four waves this session,
50 already generated with zero failures, `AB_SlimyPholiota` deliberately skipped
— dual verdict, still owner/BENCH-gated). The daemon (`artpiped.py -N 3`, PID
699477, confirmed sole instance throughout) will keep draining `pending/` on its
own; there is no need to re-feed it until that channel is exhausted or a new
one is opened. Next seat: check `pgrep -af artpipe` for exactly one PID before
assuming it needs restarting, and check DIRTY count before assuming there's a
review backlog — both were empty at this wrap.

## What the owner should see

- `WORLD_NAME_FIXES_1`'s re-save into the canonical slot had a side effect worth
  his eye: the canonical save had **not** carried `BIOME_WORLD_SWITCH_WAVE_1`'s
  17,667-tile repaint (that pass saved to its own separate slot). Re-saving live
  state into canonical for the name-fix promoted that repaint into canonical too.
  This is consistent (the canonical `ASHKARR_WORLDMAP_tiles.csv` was already
  rebased onto those biomes, so save and CSV now agree) and nothing was lost —
  backup at `CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-world-name-fixes-2026-09-13`
  reverses it if the promotion was unwanted. Flagged, not undone.
- One of my dispatched subagents (art-regen wave 4) internally spawned its own
  parallel forks; one fork ignored an explicit "draft only, do not touch git"
  instruction and independently filed+committed+pushed the real work while the
  parent was still analyzing. End state was correct (no duplicate jobs, working
  tree clean, everything pushed) — logged as model-behavior feedback, not a
  data problem, but worth knowing if a similar pattern shows up again.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `GIDDYUP_NULLKEY_COLD_READING_1` — folded into `COLD_LOAD_RUN_SHEET_4` as ENTRY 7
  (also folds in `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1`'s own restart-verify
  criterion, same load, no extra cost). Left `doing` on purpose — the actual
  measurement needs a full-list restart, not run this session per "batch
  game-up work before restarting." Next action: on the next full-list load,
  grep the fresh Player.log per ENTRY 7's two EXPECT lines, note the result on
  `GIDDYUP_NULLKEY_CRASH_1` and `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1` respectively.
- `TILEGEN_SILENT_REUSE_1` — not started fresh this window (already open,
  filed 2026-09-05), but materially advanced: three independent static-tracing
  passes (this session's included) now agree the root cause isn't findable from
  source alone. Added `[TILEGEN_SILENT_REUSE_1]`-tagged diagnostic logging
  around `WorldTileMapGenerate` in `JawaBenchSocietyTools.cs` (committed
  `36521df01`). Next action: build+deploy the companion DLL on the next restart
  (game is up now, can't rebuild it live), then reproduce the original
  two-distinct-tile repro and grep Player.log for the tag to see what call 2
  actually does. Left `doing`.
- `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1` — also not started fresh (already fixed
  by earlier work this session, commits `95eb3bfe8`/`8f627e057`, already
  pushed before this window began); I only independently re-verified the root
  cause against vanilla `BiomeDef.CommonalityOfAnimal` source and confirmed no
  remaining `RSW_Iriaz`/`RSW_Anooba` overlap. Left `doing` — its own verify
  criterion (zero `AllWildAnimals` errors on a fresh cold load) now rides the
  same restart as the entry above.

## Traps learned

- The owner's stale `infrastructure/state/MODE` file read `afk` at session
  start even though he was live in the window talking to me ("Wake foundry.
  Full belt. Go go go") — rimflow's own `why` gating on `needs=owner` items
  silently suppressed a fully-specified, ready-to-execute item
  (`WORLD_NAME_FIXES_1`) under that stale mode. There is no CLI setter for
  `MODE` (it's a plain file `rimflow/cli.py` reads, never writes) — updated it
  to `belt` by hand. Next seat: if `rimflow next`/`why` seems to be
  under-offering work while the owner is actively present, check
  `infrastructure/state/MODE` isn't stuck on a prior session's `afk`.
  Filed to `LESSONS_INBOX.md`.
- A nested subagent scope violation (see "What the owner should see" above) —
  filed to `LESSONS_INBOX.md` as: parallel forks spawned BY a dispatched
  subagent do not reliably respect that subagent's own "draft only" scoping
  of them; if a task's correctness depends on a fork NOT touching git, brief
  the parent to verify before it reports success, don't rely on the fork's
  instructions alone.

## Closed since the last handoff (2)

- `ART_REGEN_FLORA_WAVE1_QUEUE_1` — 4e3af6dc6
- `WORLD_NAME_FIXES_1` — 1df76373c26d7edf426355d2f48d3c1a3e526313

## Filed and still open (1) — the next seat's queue

- `GIDDYUP_NULLKEY_COLD_READING_1` — Cold-load log reading for the GR_Mantistanis null-key fix (1f222320b): add to the next run sheet

## Commits

```
0c8f0ad9d artpipe housekeeping: daemon consuming wave-4 flora batch
456a2125d rimflow: note on ART_REGEN_FLORA_WAVE1_QUEUE_1 (wave 4, final)
96cf1c4d3 ART_REGEN_FLORA_WAVE1_QUEUE_1: wave 4 (final), queue remaining 89 flora art:improve jobs
781209c58 rimflow: note on ART_REGEN_FLORA_WAVE1_QUEUE_1 (wave 3 summary)
e8f026dd8 ART_REGEN_FLORA_WAVE1_QUEUE_1: wave 3, queue 15 more flora art:improve jobs
470049dc6 artpipe housekeeping: wave 2 + retry batch fully drained
e835603cb BENCH reboot handoff 202609130408: AFK wave wrap — Mantistanis resolved, two decision decks merged from double-blind analyses
b8fafc737 ledger: pre-check note on MODLIST_COMPLEXITY_AUDIT_1
7b80d69fa MODLIST_COMPLEXITY_AUDIT_1: save placed-things pre-check — 7/8 cut candidates DIRTY in canonical start save
f3476da1c artpipe/ledger housekeeping: daemon claimed retried jobs, render sync
838cd5cdb rimflow: note on DIRTY_CODE_REVIEW_STANDING_LOOP_1 (2026-09-12 wave)
7dbb80b82 ART_REGEN_FLORA_WAVE1_QUEUE_1: wave 2, queue 15 more flora art:improve jobs + requeue 9 failed fauna jobs
b982f6b02 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark ashkarr_settle.py and JawaBenchSocietyTools.cs clean
e82a4ea05 MODLIST_COMPLEXITY_AUDIT_1: ranked 12-mod shortlist report (Fable)
77b83b31c COLD_LOAD_RUN_SHEET_4: fold in ENTRY 7 (Giddy-Up null-key + duplicate-key restart verify)
dc90b5b6d FOUNDRY BELT wave wrap: sync ledger/artpipe/review-status housekeeping
160e1e685 rimflow: close WORLD_NAME_FIXES_1
1df76373c WORLD_NAME_FIXES_1: apply and verify all 7 world renames live
efb2f02ad selftest_block_canon_contradiction: cover the write-time refusal path
bff684833 rimflow: close ART_REGEN_FLORA_WAVE1_QUEUE_1 at 4e3af6dc6
4e3af6dc6 ART_REGEN_FLORA_WAVE1_QUEUE_1: queue 14 flora art:improve jobs (daemon drained)
36521df01 TILEGEN_SILENT_REUSE_1: add live-repro diagnostic logging to world_tile_map_generate
655d3369f GIDDYUP_KEEP_OR_CUT_1: background analysis report (Fable) — recommends keep GU2 trimmed, cut RunAndGun
41608694e BENCH: start ASSIGNMENT_SHEETS_VERDICT_SITTING_1 — sheets served, awaiting owner
67f908c08 BENCH AFK wave: close GIDDYUP_NULLKEY_CRASH_1 + carrier, file cold reading, start keep-or-cut analyses
b83e7ff49 FOUNDRY wake: mode -> belt, sync ledger/artpipe/dashboard housekeeping
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-13T03:48:43Z

Uncommitted (say for each whether it is yours or another seat's):

```
M infrastructure/artpipe/registry.jsonl
 M infrastructure/artpipe/throughput.jsonl
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? design/Jawa/worldbuilding/review/serve_homeless.log
?? infrastructure/artpipe/daemon_run_20260911_105041.log
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
?? infrastructure/artpipe/done/bleedingtooth_v1.json
?? infrastructure/artpipe/done/bleedingtooth_v1.manifest.json
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
?? infrastructure/artpipe/done/brightbells_v1.json
?? infrastructure/artpipe/done/brightbells_v1.manifest.json
?? infrastructure/artpipe/done/bryolux_v1.json
?? infrastructure/artpipe/done/bryolux_v1.manifest.json
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
?? infrastructure/artpipe/done/crimsoncap_v1.json
?? infrastructure/artpipe/done/crimsoncap_v1.manifest.json
?? infrastructure/artpipe/done/crystalhorn_v1.json
?? infrastructure/artpipe/done/crystalhorn_v1.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_east.json
?? infrastructure/artpipe/done/dactillion_v1_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_north.json
?? infrastructure/artpipe/done/dactillion_v1_north.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_south.json
?? infrastructure/artpipe/done/dactillion_v1_south.manifest.json
?? infrastructure/artpipe/done/dewshrooms_v1.json
?? infrastructure/artpipe/done/dewshrooms_v1.manifest.json
?? infrastructure/artpipe/done/direwail_v1_east.json
?? infrastructure/artpipe/done/direwail_v1_east.manifest.json
?? infrastructure/artpipe/done/direwail_v1_north.json
?? infrastructure/artpipe/done/direwail_v1_north.manifest.json
?? infrastructure/artpipe/done/direwail_v1_south.json
?? infrastructure/artpipe/done/direwail_v1_south.manifest.json
?? infrastructure/artpipe/done/duskram_v1_east.json
?? infrastructure/artpipe/done/duskram_v1_east.manifest.json
?? infrastructure/artpipe/done/duskram_v1_north.json
?? infrastructure/artpipe/done/duskram_v1_north.manifest.json
?? infrastructure/artpipe/done/duskram_v1_south.json
?? infrastructure/artpipe/done/duskram_v1_south.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_east.json
?? infrastructure/artpipe/done/emberscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_north.json
?? infrastructure/artpipe/done/emberscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_south.json
?? infrastructure/artpipe/done/emberscythe_v1_south.manifest.json
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
?? infrastructure/artpipe/done/fenshear_v1_east.json
?? infrastructure/artpipe/done/fenshear_v1_east.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_north_r2.json
?? infrastructure/artpipe/done/fenshear_v1_north_r2.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_south.json
?? infrastructure/artpipe/done/fenshear_v1_south.manifest.json
?? infrastructure/artpipe/done/firevine_fireweed_v1.json
?? infrastructure/artpipe/done/firevine_fireweed_v1.manifest.json
?? infrastructure/artpipe/done/firevinetree_v1.json
?? infrastructure/artpipe/done/firevinetree_v1.manifest.json
?? infrastructure/artpipe/done/fruitingbodies_v1.json
?? infrastructure/artpipe/done/fruitingbodies_v1.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_east.json
?? infrastructure/artpipe/done/fumeback_v1_east.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_north.json
?? infrastructure/artpipe/done/fumeback_v1_north.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_south.json
?? infrastructure/artpipe/done/fumeback_v1_south.manifest.json
?? infrastructure/artpipe/done/giantagarilux_v1.json
?? infrastructure/artpipe/done/giantagarilux_v1.manifest.json
?? infrastructure/artpipe/done/giantagaritox_v1.json
?? infrastructure/artpipe/done/giantagaritox_v1.manifest.json
?? infrastructure/artpipe/done/giantgamma_v1.json
?? infrastructure/artpipe/done/giantgamma_v1.manifest.json
?? infrastructure/artpipe/done/globularplant_v1.json
?? infrastructure/artpipe/done/globularplant_v1.manifest.json
?? infrastructure/artpipe/done/glowingagarilux_v1.json
?? infrastructure/artpipe/done/glowingagarilux_v1.manifest.json
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
?? infrastructure/artpipe/done/grubhorn_v1_east.json
?? infrastructure/artpipe/done/grubhorn_v1_east.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_north.json
?? infrastructure/artpipe/done/grubhorn_v1_north.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_south.json
?? infrastructure/artpipe/done/grubhorn_v1_south.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_east.json
?? infrastructure/artpipe/done/hawkbat_v1_east.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_north.json
?? infrastructure/artpipe/done/hawkbat_v1_north.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_south.json
?? infrastructure/artpipe/done/hawkbat_v1_south.manifest.json
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
?? infrastructure/artpipe/done/mangrovetree_v1.json
?? infrastructure/artpipe/done/mangrovetree_v1.manifest.json
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
?? infrastructure/artpipe/done/mycolith_v1_east.json
?? infrastructure/artpipe/done/mycolith_v1_east.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_north.json
?? infrastructure/artpipe/done/mycolith_v1_north.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_south.json
?? infrastructure/artpipe/done/mycolith_v1_south.manifest.json
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
?? infrastructure/artpipe/done/pekopeko_v1_east.json
?? infrastructure/artpipe/done/pekopeko_v1_east.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_north.json
?? infrastructure/artpipe/done/pekopeko_v1_north.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_south.json
?? infrastructure/artpipe/done/pekopeko_v1_south.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_east.json
?? infrastructure/artpipe/done/rotscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_north.json
?? infrastructure/artpipe/done/rotscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_south_r2.json
?? infrastructure/artpipe/done/rotscythe_v1_south_r2.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_east.json
?? infrastructure/artpipe/done/scarrend_v1_east.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_north.json
?? infrastructure/artpipe/done/scarrend_v1_north.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_south.json
?? infrastructure/artpipe/done/scarrend_v1_south.manifest.json
?? infrastructure/artpipe/done/shiro_v1_east.json
?? infrastructure/artpipe/done/shiro_v1_east.manifest.json
?? infrastructure/artpipe/done/shiro_v1_north.json
?? infrastructure/artpipe/done/shiro_v1_north.manifest.json
?? infrastructure/artpipe/done/shiro_v1_south.json
?? infrastructure/artpipe/done/shiro_v1_south.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_east.json
?? infrastructure/artpipe/done/slagmaw_v1_east.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_north.json
?? infrastructure/artpipe/done/slagmaw_v1_north.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_south.json
?? infrastructure/artpipe/done/slagmaw_v1_south.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_east.json
?? infrastructure/artpipe/done/sludrin_v1_east.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_north.json
?? infrastructure/artpipe/done/sludrin_v1_north.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_south.json
?? infrastructure/artpipe/done/sludrin_v1_south.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_east.json
?? infrastructure/artpipe/done/sporehulk_v1_east.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_north.json
?? infrastructure/artpipe/done/sporehulk_v1_north.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_south.json
?? infrastructure/artpipe/done/sporehulk_v1_south.manifest.json
?? infrastructure/artpipe/done/sugarfamewort_v1.json
?? infrastructure/artpipe/done/sugarfamewort_v1.manifest.json
?? infrastructure/artpipe/done/tanglerootmangrove_v1.json
?? infrastructure/artpipe/done/tanglerootmangrove_v1.manifest.json
?? infrastructure/artpipe/done/toxicgamma_v1.json
?? infrastructure/artpipe/done/toxicgamma_v1.manifest.json
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
?? infrastructure/artpipe/done/whisperbird_v1_east.json
?? infrastructure/artpipe/done/whisperbird_v1_east.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_north.json
?? infrastructure/artpipe/done/whisperbird_v1_north.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_south.json
?? infrastructure/artpipe/done/whisperbird_v1_south.manifest.json
?? infrastructure/artpipe/done/wildradagast_v1.json
?? infrastructure/artpipe/done/wildradagast_v1.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.manifest.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.manifest.json
?? infrastructure/artpipe/failed/ashrunner_v1_east.json
?? infrastructure/artpipe/failed/ashrunner_v1_east.manifest.json
?? infrastructure/artpipe/failed/ashrunner_v1_south.json
?? infrastructure/artpipe/failed/ashrunner_v1_south.manifest.json
?? infrastructure/artpipe/failed/bilespawn_v1_north.json
?? infrastructure/artpipe/failed/bilespawn_v1_north.manifest.json
?? infrastructure/artpipe/failed/fenshear_v1_north.json
?? infrastructure/artpipe/failed/fenshear_v1_north.manifest.json
?? infrastructure/artpipe/failed/mireflitwarden_v1_north.json
?? infrastructure/artpipe/failed/mireflitwarden_v1_north.manifest.json
?? infrastructure/artpipe/failed/rotscythe_v1_south.json
?? infrastructure/artpipe/failed/rotscythe_v1_south.manifest.json
?? infrastructure/artpipe/failed/wastewing_v1_north.json
?? infrastructure/artpipe/failed/wastewing_v1_north.manifest.json
?? infrastructure/artpipe/failed/wastewing_v1_south.json
?? infrastructure/artpipe/failed/wastewing_v1_south.manifest.json
?? infrastructure/artpipe/registry.jsonl.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
```

