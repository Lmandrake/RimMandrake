# BENCH_REBOOT_HANDOFF_202609130215 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609121722`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

The BiomeCast Mantistanis op now carries TWO independent fixes and only one
survives a regeneration: BENCH's MayRequire chain lives in the GENERATOR
(gen_cast_patch.py LOADFOLDERS_GATED, 90d58be79 — regen-safe), but FOUNDRY's
PawnKindDef-existence guard (1f222320b) is a hand-edit inside the GENERATED
XML — the next `gen_cast_patch.py` run silently deletes it. Fold the
existence-guard into the generator's donor-op emission (or rule it redundant)
BEFORE anyone regenerates. Also: the deployed game copy predates 1f222320b —
redeploy UtinniPatches before the next verification load. Underlying trap is
filed in LESSONS_INBOX (LoadFolders IfModActive defs defeat owning-mod
MayRequire; dump packageId attribution cannot see the gate).

## What the owner should see

Four decision decks wait, none executed without your card:
- `GIDDYUP_KEEP_OR_CUT_1` — recommendation KEEP (we run the 3rd-gen rewrite;
  today's crashes were our cast data; Dewback/Bantha/Ronto/Fambaa/Mudhorn/
  Dalgo/Eopie mount-eligible free). Cards A–D on the item;
  `D:\Luke\dev\Rimworld\Transient\giddyup_keep_or_cut_2026-09-12.md`.
- `MODLIST_COMPLEXITY_AUDIT_1` — 12 ranked keep-or-cut candidates; top three
  cards: Caravan Adventures cut (three local defect trails), Dubs Performance
  Analyzer out of the standing list, Jurassic dinos cut after a texPath check.
  `D:\Luke\dev\Rimworld\Transient\modlist_keep_or_cut_shortlist_2026-09-12.md`.
- `CAMPAIGN_STORY_SITTING_1` Phase B — the arc gather is done and verified
  (71 entries, 20/20 blind quote check, all doubts closed); the sitting cards
  are ready to cut from its 21 GAPs + 8 contradictions.
  `D:\Luke\dev\Rimworld\design\Jawa\campaign\CAMPAIGN_ARC_GATHER.md`.
- `DUNGEON_SETPIECE_TEXT_1` — the 18 narrator readouts redrafted into your
  butler register, awaiting tune-or-bless (nine_voices_v1_lines.md).
Also flagged: both assignment-sheet sidecars read touchedBySheet:true from
BEFORE the verdict-sitting item was filed — do not let anyone consume them as
a finished review (noted on ASSIGNMENT_SHEETS_VERDICT_SITTING_1).

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `CAMPAIGN_STORY_SITTING_1` — Phase A COMPLETE, verified, committed
  (4843d58ae); doubt ledger fully closed. Stops at Phase B, which is an owner
  sitting: next action = cut cards from the gather's GAPs/contradictions,
  batch by act, NO-NEW-PLACES rule on every batch header.
- `DUNGEON_SETPIECE_TEXT_1` — butler-register redraft landed as DRAFT
  (43cfd4427). Stops at the owner's tune-or-bless; every other remaining
  bullet on the item is an owner sitting. No further AFK work exists on it.
- `GIDDYUP_NULLKEY_CRASH_1` — root-caused, fixed, validated, deployed
  (90d58be79), routed needs=bridge. Stops at live proof: next cold load must
  show zero 'No Verse.PawnKindDef named GR_Mantistanis' and zero Giddy-Up
  AllWildAnimals errors (baselines 1/1 in
  Transient/Player_log_before_giddyup_verify_restart_20260912.log). Restart
  was deliberately HELD - FOUNDRY's BIOME_WORLD_SWITCH_WAVE_1 was mid-flight
  on the live game. Before that restart: redeploy UtinniPatches (repo gained
  FOUNDRY's 1f222320b after my deploy). FOUNDRY's CORRECT_GIDDYUP_NULLKEY_1
  duplicates this item's finding - reconcile/close one of the two.

## Traps learned

- LoadFolders `IfModActive` subfolder defs defeat owning-mod MayRequire and
  the dump's packageId attribution (filed to LESSONS_INBOX, e50e62143).
- `validate_patch.py ... | tail -N` eats the WARN lines - warnings print
  before the summary; capture full output or grep for WARN explicitly.
- The artpipe selftest's 20 gemini failures were the TESTS being stale
  against the owner's 2026-09-11 gemini defund ($0 default budget), not the
  daemon - selftests that exercise a defunded channel must fund it
  explicitly per-run (fixed 5091a9bda, plus a test pinning the $0 default).
- `touchedBySheet: true` proves a sheet was worked in ONCE, ever - not that
  the review is complete; check the touch date against the item's filing.
- A concurrent seat can commit onto the same generated file between your
  deploy and your next look - deploy drift re-appearing minutes after
  "VERIFIED in sync" means a peer landed work, not a drvfs ghost.

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (4) — the next seat's queue

- `MOD_VALIDATION_RETROFIT_1` — modcheck full retrofit wave: every shipped mod gets a validation.steps.yaml and a green run (owner ruling 2026-09-12: full wave, not campaign-critical
- `CORRECT_GIDDYUP_NULLKEY_1` — GIDDYUP_NULLKEY_CRASH_1's null key is GR_Mantistanis (dead ref), not the RSW_ Wave-C names; fix applied, needs claim+close
- `GIDDYUP_KEEP_OR_CUT_1` — Giddy-Up keep-or-cut ruling: pros/cons analysis of the mounted-animal mods (fun to ride Star Wars animals; historically a bug confounder) — background
- `MODLIST_COMPLEXITY_AUDIT_1` — Keep-or-cut shortlist beyond Giddy-Up: which other mods in the full stack carry outsized breakage/complexity risk relative to their contribution to th

## Commits

```
4843d58ae CAMPAIGN_ARC_GATHER: close the last two doubts (G77 tones confirmed GAP, G85 kyber clean) — doubt ledger fully resolved, Phase B unblocked
c5676331a CAMPAIGN_STORY_SITTING_1 Phase A: the arc GATHER (71 entries, 20/20 quote spot-check) + mod keep-or-cut analyses
3acb4e6ba code-review: mark-clean 4 files (game_focus, selftest_sound_paths, rimbench/core, artpipe/fill_queue)
6b81019d0 BIOME_WORLD_SWITCH_WAVE_1: wildBiomes eviction ran (no ship, stale rosters found); icon regen has no script
a183faa48 ledger sync: GIDDYUP_NULLKEY_CRASH_1 diagnosis+deploy, DUNGEON_SETPIECE_TEXT_1 redraft, CAMPAIGN_STORY_SITTING_1 Phase A launch
e50e62143 lesson: LoadFolders-gated defs defeat owning-mod MayRequire (GIDDYUP_NULLKEY_CRASH_1)
43cfd4427 DUNGEON_SETPIECE_TEXT_1: redraft the 18 narrator silent-god readouts into the butler register
5091a9bda selftests green 50/50: exempt vanilla packed clips in sound_paths; fund gemini explicitly in artpipe tests
3703a4f0c FASCINATING_WORLD_JUNK_1: Phase 2 (IDEAS) complete — donor shapes mined
76541ba62 code-review: mark-clean 5 files (ChewAnchors, FrontCreep, DiveHunt, ScatterMineshaftPortal, canon_consistency.py)
7f2ff5541 selftests: flip canon water case to DENY (planet frozen 2026-09-12); route liquid-suite dump path through game_paths
1f222320b GIDDYUP_NULLKEY_CRASH_1: guard GR_Mantistanis, the real live null-key source
f90d660ae BIOME_WORLD_SWITCH_WAVE_1: repaint 17,667 Ash'karr tiles onto the owned RUT_ biomes
90d58be79 GIDDYUP_NULLKEY_CRASH_1: gate VGE Megafauna hybrids on Spino.Megafauna in the biome cast
f46d1345d FASCINATING_WORLD_JUNK_1: Phase 1 CENSUS complete
a7dc3f029 mark-clean: modcheck cli/floor/report/status, rimdrive verify
534c8feba code review: fix case-sensitive exclusion in modcheck.mod_hash; catch a second Reconnected during rimdrive.verify's idempotent retry
d434f1e8f rimflow: close MOD_VALIDATION_RUNNER_1 + MOD_VALIDATION_PIT_PILOT_1; update RETROFIT_1's status
bfd45d8b6 MOD_VALIDATION_PIT_PILOT_1: live run GREEN (3/3) after enabling Pits and fixing five real bugs
d27b960be artpipe template: bake downscale-legibility direction into every sprite prompt; default+warn resolution to 256 (frostmite pilot, 2026-09-12)
270c52a14 Enable mandrake.rm.pits for MOD_VALIDATION_PIT_PILOT_1's live proof (owner: "Take control, change the list, and keep going!")
47ffd6b92 MOD_VALIDATION_PIT_PILOT_1: record that Pits isn't enabled in the live mod list
4a16b143d rimflow: close RIMDRIVE_LIBRARY_BUILD_1
5e7f3ced5 RIMDRIVE_LIBRARY_BUILD_1: fix Session._ticks() (measured live), run the full live chain
2c8a9d471 Resolution parameter proof: frostmite v2 at 512/256/128 source, downscaled to on-screen tiers
e3d2b573f Frostmite redraw pilot: v2 (blue keyline, amber core, bold claws, no red) passes zoom gate
9bb9fbf5d MOD_VALIDATION_RUNNER_1 + PIT_PILOT: build modcheck on rimdrive, draft the pit mod's validation.py
43f865899 art_zoom_sim.py: downscale legibility test vs vanilla control; 2026-09-12 frostmite/lockjaw sheets
10b6cddda RIMDRIVE_LIBRARY_BUILD_1: build rimdrive L1 (Session) + L2 (verify), extract rimbench.core onto it
d22a07bc5 rimflow: close ART_REGEN_WAVE10_QUEUE_1
a4bb92cdd ART_REGEN_WAVE10_QUEUE_1: queue 14 more art:improve creatures, wave 9's named remainder
a976ff6a3 Art review sheet 2026-09-12: 148 validated creature renders for owner grading (keep/redraw/cut)
882c6d92f rimdrive ruled (owner, 2026-09-12): new package, UNVERIFIED-taint for channel-less writes, RIMDRIVE_LIBRARY_BUILD_1 filed ahead of modcheck
99785cb6e GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1: file the missing prose, record live proof the fix is incomplete
89dbfd0a0 LIGHTFALL_CHASM_AUTHORING_1: rename the existing tile-9023 chasm landmark to Lightfall
acf1c3c86 FOUNDRY reboot handoff 202609122103: fill carry-forward/owner/half-done/traps, file 2 lessons
07de1dcb9 rimdrive: bridge-library design deep-dive (owner-commissioned, 2026-09-12)
8f627e057 GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1: rename the dedup fix again, one file still beat it
745e14e42 modcheck: debug mode with declared chain checkpoints; smoke mode stays checkpoint-free (owner addendum, 2026-09-12)
dd2048e52 modcheck re-ruled (owner, 2026-09-12): per-mod Python on shared library, steps-YAML dropped; build-up/tear-down absolute (spec 1b)
0769a4d67 MEGAFAUNAYIELD_DEAD_GR_TARGETS_1: record the full investigation writeup
4ad33cdf8 Lesson: bridge driving cost is LLM turns, not the bridge (measured 2026-09-12)
34a6dc87d bridge_latency_bench.py: re-runnable A/B/C driving-cost benchmark (spawn / setup / per-call), read-only
36e0255c1 SCARROACH_CATHEDRALROACH_TEXTURES_MISSING_1: original sprite art for both roaches
935b29048 MEGAFAUNAYIELD_DEAD_GR_TARGETS_1: gate stat/resize/tolerance patches on target-def existence
cba1a4944 modcheck: scripts own their entire setup; chained components share state, downstream of a chain failure reads UNMEASURED (owner, 2026-09-12)
7f3fc2247 modcheck: minor-declare bounded to trivial no-gameplay-effect changes, diff recorded with the claim (owner, 2026-09-12)
f614eb5ba MLIE_ARTOVERRIDE_COLLISION_CHECK_1: fix live Dewback art-override regression
1a2cae364 modcheck: owner-designed pre-playtest validation system — spec + 3 items filed (owner sitting 2026-09-12)
770a328ed UTINNI_WORLDMAP_FLIGHT_ICON_1: replace vanilla gravship world-map sprite with the Utinni's own silhouette
95eb3bfe8 CATHEDRAL_ROACH_THINKTREE_GAP_1 + GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1 (in-list class)
18d8b11c7 Owner sitting 2026-09-12: biome repaint GO, fog reveal confirmed, sheets sitting marked done, FULL modlist captured at 593
539990920 GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1: strip duplicate wildBiomes entries across 14 RSW_ animals
c04320076 FOUNDRY reboot handoff 202609121737: fill carry-forward/owner/half-done/traps sections; file 4 lessons from tonight's session
7908f1a0e rimflow: sync ledger/queue views, file MLIE_ARTOVERRIDE_COLLISION_CHECK_1
8dc279c64 MLIE_FAUNA_ABSORPTION_1: port Dianoga, Dragonsnake, Eopie (77 -> 74 remaining)
5a8fc8c1c Fix: remove RSW_Anooba art files that silently regressed the verified-live AnoobaArtOverride
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-13T01:31:34Z

Uncommitted (attribution): NONE of the below is BENCH's - the rosters/*.json
edits are FOUNDRY's wildBiomes-eviction pass (6b81019d0 says stale rosters
found, their wave still `doing`), the artpipe pending/done/failed churn and
registry/throughput/health files belong to the artpipe daemon (live, PID
699477 at wrap) and the codebase-health publisher, and the Transient art
decisions file is the owner's art-review sheet. BENCH's own work is fully
committed and pushed.

```
M Transient/art_review_2026-09-12/decisions.json
 M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M design/Jawa/worldbuilding/biomes/rosters/arid_shrubland.json
 M design/Jawa/worldbuilding/biomes/rosters/desert.json
 M design/Jawa/worldbuilding/biomes/rosters/dune_sea_deep_desert.json
 M design/Jawa/worldbuilding/biomes/rosters/forsaken_crags.json
 M design/Jawa/worldbuilding/biomes/rosters/poison_forest.json
 M design/Jawa/worldbuilding/biomes/rosters/the_contagion.json
 M design/Jawa/worldbuilding/biomes/rosters/the_cracked_lands.json
 M design/Jawa/worldbuilding/biomes/rosters/the_fever_wood.json
 M design/Jawa/worldbuilding/biomes/rosters/the_forge.json
 M design/Jawa/worldbuilding/biomes/rosters/the_greentide.json
 M design/Jawa/worldbuilding/biomes/rosters/the_miasma.json
 M design/Jawa/worldbuilding/biomes/rosters/the_rot.json
 M design/Jawa/worldbuilding/biomes/rosters/the_rust_cathedral.json
 M design/Jawa/worldbuilding/biomes/rosters/the_scarlands.json
 M design/Jawa/worldbuilding/biomes/rosters/the_slime.json
 M design/Jawa/worldbuilding/biomes/rosters/the_sump.json
 M design/Jawa/worldbuilding/biomes/rosters/the_webwork.json
 M design/Jawa/worldbuilding/biomes/rosters/wasteland.json
 M design/Jawa/worldbuilding/biomes/rosters/weeping_stones.json
 D infrastructure/artpipe/pending/dactillion_v1_east.json
 D infrastructure/artpipe/pending/dactillion_v1_north.json
 D infrastructure/artpipe/pending/dactillion_v1_south.json
 D infrastructure/artpipe/pending/fanback_v1_east.json
 D infrastructure/artpipe/pending/fanback_v1_north.json
 D infrastructure/artpipe/pending/fanback_v1_south.json
 D infrastructure/artpipe/pending/grank_v1_east.json
 D infrastructure/artpipe/pending/grank_v1_north.json
 D infrastructure/artpipe/pending/grank_v1_south.json
 M infrastructure/artpipe/registry.jsonl
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
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
?? infrastructure/artpipe/done/ashrunner_v1_north.json
?? infrastructure/artpipe/done/ashrunner_v1_north.manifest.json
?? infrastructure/artpipe/done/bilespawn_v1_east.json
?? infrastructure/artpipe/done/bilespawn_v1_east.manifest.json
?? infrastructure/artpipe/done/bilespawn_v1_south.json
?? infrastructure/artpipe/done/bilespawn_v1_south.manifest.json
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
?? infrastructure/artpipe/done/dactillion_v1_east.json
?? infrastructure/artpipe/done/dactillion_v1_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_north.json
?? infrastructure/artpipe/done/dactillion_v1_north.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_south.json
?? infrastructure/artpipe/done/dactillion_v1_south.manifest.json
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
?? infrastructure/artpipe/done/fenshear_v1_south.json
?? infrastructure/artpipe/done/fenshear_v1_south.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_east.json
?? infrastructure/artpipe/done/fumeback_v1_east.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_north.json
?? infrastructure/artpipe/done/fumeback_v1_north.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_south.json
?? infrastructure/artpipe/done/fumeback_v1_south.manifest.json
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
?? infrastructure/artpipe/done/insectomorph_v1_east.json
?? infrastructure/artpipe/done/insectomorph_v1_east.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_north.json
?? infrastructure/artpipe/done/insectomorph_v1_north.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_south.json
?? infrastructure/artpipe/done/insectomorph_v1_south.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_east.json
?? infrastructure/artpipe/done/kinrath_v1_east.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_north.json
?? infrastructure/artpipe/done/kinrath_v1_north.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_south.json
?? infrastructure/artpipe/done/kinrath_v1_south.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_east.json
?? infrastructure/artpipe/done/mireflit_v1_east.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_north.json
?? infrastructure/artpipe/done/mireflit_v1_north.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_south.json
?? infrastructure/artpipe/done/mireflit_v1_south.manifest.json
?? infrastructure/artpipe/done/mireflitwarden_v1_east.json
?? infrastructure/artpipe/done/mireflitwarden_v1_east.manifest.json
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
?? infrastructure/artpipe/done/whisperbird_v1_east.json
?? infrastructure/artpipe/done/whisperbird_v1_east.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_north.json
?? infrastructure/artpipe/done/whisperbird_v1_north.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_south.json
?? infrastructure/artpipe/done/whisperbird_v1_south.manifest.json
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

