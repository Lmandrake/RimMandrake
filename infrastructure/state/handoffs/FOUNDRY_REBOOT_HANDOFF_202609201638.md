# FOUNDRY_REBOOT_HANDOFF_202609201638 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609201440`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

The owner said "Wake foundry and go belt" this wave, then separately said "Stop all
clean/dirty code review until Wednesday 3pm token reset please" mid-wave — that pause is
recorded in `infrastructure/state/items/DIRTY_CODE_REVIEW_STANDING_LOOP_1.md` and a
cross-session memory (`code-review-loop-paused-until-2026-09-23.md`), and **it survives
this reboot**: do not spawn or resume `DIRTY_CODE_REVIEW_STANDING_LOOP_1` (no full-file
review, no `mark-clean`, no bug-fix-under-that-item pass) before **2026-09-23 15:00**.
Everything else in BELT mode is unaffected.

## What the owner should see

- He gave two live rulings mid-wave that BENCH is now sitting on, uncommitted-work-wise
  synced but not yet acted on: `DESERT_FAMILY_PORT_EXECUTION_1` ("Yes. All of the desert
  sheet should be keep but replace with our own version of creature and art. Port. All of
  them. Now." — ~109 species) and the related `DONOR_DEFS_PORT_TO_OURS_1` /
  `NONCANON_BEAST_RENAME_1`. These are BENCH's queue, not re-scoped or touched here — flagging
  only because they're large, owner-personally-ruled, and worth his eye that they landed in
  the ledger correctly (`git show ca49354b3`).
- `TWILIGHT_DEEP_WATER_LAYER_1` closed on a live-data proof (biome def reads
  `maxFishPopulation=700`, deployed patch file byte-matches the repo) but a full live
  fishing catch was never actually attempted (the canonical colony's current map is
  `RUT_ExtremeDesert`, not Twilight Sea) — closed anyway as the data-level proof was judged
  sufficient. Worth a real look if he ever visits that biome in play.
- The art daemon was silently starved for hours (all 21 pending jobs misfiled to the
  gemini channel he permanently banned 09-11) before this wave caught and fixed it
  (`f022b2575`) — nobody had noticed. Might be worth a periodic sanity check on this in
  future waves rather than assuming "process running" means "producing."

## What is half-done, and where it stops

- STALE_GATE citation lint -- 250 of 277 originally-flagged citations remain unreviewed
  (18 real defects fixed across 4 passes today, hit rate dropped from ~19% to ~3% by the
  4th pass). NEXT: `python3 src/RimMandrake/rimflow/cli.py lint --citations`, continue
  sampling if a future wave has idle BELT capacity and nothing higher-value queued — this
  is genuinely low-value-per-hour now, not a backlog to feel obligated toward.
- UNKNOWN citation bucket (462, mostly legacy/noise) -- fuzzy-typo pass done once (found 9
  real mis-cited `DROIDWORKS_*` IDs, fixed at `a4fae45c5`). NEXT: none required; this
  was a one-shot sweep, not a standing loop.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` -- PAUSED by owner until 2026-09-23 15:00 (see "one
  thing to carry forward"). NEXT: resume normally after that time, starting from
  `infrastructure/state/CODE_REVIEW_STATUS.json`'s current CLEAN list — no other change.

## Traps learned

- Art daemon alive-but-starved reads identical to "working fine" from `pgrep` alone —
  always cross-check the most recent file timestamp in `artpipe/done/` against wall clock,
  not just process liveness (see: `infrastructure/artpipe/pending/*.json` re-channel fix,
  `f022b2575`).
- `get_defs` cannot read a `fishTypes`-shaped list field at all — returns the literal
  string `"(no such field)"`, which reads like a failure but is a scalar-only tooling
  limitation, not evidence the def is wrong (see: `rimbridge` skill, scalar-fields-only
  note; confirmed again this wave on `RUT_TwilightSea`).
- A doc correctly describing an item as "still open/blocked" can go stale within the SAME
  day the item closes — four of today's ~29 stale-citation fixes were same-day drift, not
  old rot (filed: LESSONS_INBOX).

## Closed since the last handoff (14)

- `CANONICAL_SAVE_SCENARIO_MISMATCH_1` — a85b9008e
- `MODLIST_RULED_CUTS_1` — 649f53406
- `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1` — 8f627e057
- `SLIME_STREAM_ROWS_1` — b2058c308
- `FURNACEBEAST_THERMAL_CYCLE_1` — 58a08013f
- `GRAFFITI_VARIANT_COUNTS_1` — f05a72988
- `ROT_HEALTH_SHARING_1` — 8c5c734e1
- `GIZKA_NEWGAME_NRE_FIX_1` — 9a2316798
- `QUICKGRASS_VISUAL_SCALE_2X_1` — 51867f432
- `DRILL_IMPASSABLE_FILLPERCENT_1` — df8288744
- `SCALD_DIVING_MOD_1` — d38274fb32f46b89d4628d761c61b41f3075bf49
- `TWILIGHT_DEEP_WATER_LAYER_1` — 6475330182110d5a1af447d0125d3e06ecfa5f0f
- `DROID_TILES_SOURED_TERRAIN_1` — 6475330182110d5a1af447d0125d3e06ecfa5f0f
- `ROT_PALE_TREE_1` — 6475330182110d5a1af447d0125d3e06ecfa5f0f

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
5a0b0f5c0 Repoint 21 desert droids at our own Droidworks defs - they were never unportable
32d3d3803 Owner ruling: replace everything - all donor species become ours
11f43da58 Star Wars Animal Collection port sheet: the 36 species outside the desert family
38569e7d9 File DESERT_FAMILY_PORT_EXECUTION_1: owner ruled all 109 desert rows REPLACE
a4fae45c5 Fix 9 mis-cited DROIDWORKS_ item IDs in DROID_PROGRAM_STATE_2026-09-06.md
f022b2575 artpipe: re-channel 20 stranded pending jobs from gemini to codex
a00b4a524 Fix stale gate: BirthHatchDemo's extraction gate closed 2026-09-09
4b647e35a File BIOME_ROSTER_DEAD_SPECIES_REFS_1: 23 species that silently never spawn
ba1f239c2 STALE_GATE sweep (design/): fix 6 live-gate citations pointing at closed/dropped/superseded items
5db958dd8 STALE_GATE sweep (FOUNDRY, infrastructure/observed/world/src scope): fix 3 defects
8942782ae Fix stale gate citation in FISH_BESTIARY_BUILD_1: TWILIGHT_DEEP_WATER_LAYER_1 closed
85c8d3b22 rimflow: sync ledger (DONOR_DEFS_PORT_TO_OURS_1, NONCANON_BEAST_RENAME_1 filed)
2e6cdd46e Owner rulings: port every donor def to ours, rename non-canon beasts, cut the stray mushroom
0e7015b36 STALE_GATE sweep: fix live gate citations pointing at now-closed items
5951c456e Closes: TWILIGHT_DEEP_WATER_LAYER_1, DROID_TILES_SOURED_TERRAIN_1, ROT_PALE_TREE_1
e4de8a4ae Fix 9 STATE_LIE citations: docs asserting live state for closed/dropped/superseded items
647533018 rimflow: sync ledger (ROT_FLORA_FAUNA_VERDICTS closed on owner approval)
1c903a07c File ROT_ROSTER_DEAD_DONOR_NAMES_1: a "18 unwired fauna" finding was backwards
50344869c Owner ruling: the world gets REPAINTED when all biomes are in
8c0e6d54d TWILIGHT_DEEP_WATER_LAYER_1: post-restart recheck, maxFishPopulation now 700
... 42 more: git log --oneline 81f457d03..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-20T15:58:28Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   FOUNDRY (auto-regenerated by code_review_status.py's health-rebuild trigger during today's code-review waves, before the pause)
MM Transient/codebase_health.json   FOUNDRY (auto-regenerated by code_review_status.py's health-rebuild trigger during today's code-review waves, before the pause)
 M Transient/codebase_health_artifact.html   FOUNDRY (auto-regenerated by code_review_status.py's health-rebuild trigger during today's code-review waves, before the pause)
 M deployed/config/ModsConfig.before-tier-pits.xml   FOUNDRY (modset_builder.py tier-testing backups from today's bridge-verification agents)
A  infrastructure/artpipe/daemon_run_20260916_bench_restart.log   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_kinrath_v1_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_kinrath_v1_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_kinrath_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_kreetle_v1_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_kreetle_v1_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_kreetle_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/nuitae_a_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/nuitae_a_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/nuitae_b_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/nuitae_b_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/rut_agelesscap_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/rut_agelesscap_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/yumbulbs_a_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/yumbulbs_a_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/yumbulbs_b_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/done/yumbulbs_b_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/failed/nysyllin_v1_r2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 M infrastructure/artpipe/failed/orray_v3_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
A  infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/facingrepair_dewback_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/facingrepair_grmolebear_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/facingrepair_kreetle_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/facingrepair_megatardi_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/facingrepair_orray_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/facingrepair_rutcathedralroach_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/facingrepair_rutscarroach_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/facingrepair_wyyyschokk_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_0.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_3.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_4.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_5.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/offbiome_fulgurite_v3.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
MM infrastructure/artpipe/registry.jsonl   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
MM infrastructure/artpipe/throughput.jsonl   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
 M infrastructure/dashboards/hub/data/health.json   FOUNDRY (auto-regenerated by code_review_status.py's health-rebuild trigger during today's code-review waves, before the pause)
 M infrastructure/state/CODE_REVIEW_STATUS.json   FOUNDRY (auto-regenerated by code_review_status.py's health-rebuild trigger during today's code-review waves, before the pause)
 M infrastructure/state/codebase_health_last.json   FOUNDRY (auto-regenerated by code_review_status.py's health-rebuild trigger during today's code-review waves, before the pause)
D  infrastructure/state/items/DROID_TILES_SOURED_TERRAIN_1.md   FOUNDRY (closed today, moved to items/closed/)
 D infrastructure/state/items/MYCOID_COLOSSUS_ART_MISROUTE_1.md   pre-existing before this wave -- not touched, leave for its owning seat
D  infrastructure/state/items/RESEARCH_TRIO_RETIRE_1.md   pre-existing before this wave -- not touched, leave for its owning seat
D  infrastructure/state/items/TWILIGHT_DEEP_WATER_LAYER_1.md   FOUNDRY (closed today, moved to items/closed/)
 M infrastructure/state/ledger/events.jsonl   FOUNDRY (ledger/queue render timestamp churn -- already re-synced and pushed once; any further diff is post-handoff daemon/render noise)
 M infrastructure/state/queue/BENCH.md   FOUNDRY (ledger/queue render timestamp churn -- already re-synced and pushed once; any further diff is post-handoff daemon/render noise)
 M infrastructure/state/queue/FOUNDRY.md   FOUNDRY (ledger/queue render timestamp churn -- already re-synced and pushed once; any further diff is post-handoff daemon/render noise)
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\claude-1000\\-mnt-d-Luke-dev-Rimworld\\84f9b274-abd5-4c73-81fd-7f936a8b3cc9\\scratchpad\\check_tile.py"   pre-existing scratch / another window's -- not this wave
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   pre-existing scratch / another window's -- not this wave
?? deployed/config/ModsConfig.before-tier-bridge.xml   FOUNDRY (modset_builder.py tier-testing backups from today's bridge-verification agents)
?? deployed/config/ModsConfig.before-tier-diving.xml   FOUNDRY (modset_builder.py tier-testing backups from today's bridge-verification agents)
?? deployed/config/ModsConfig.before-tier-oracle.xml   FOUNDRY (modset_builder.py tier-testing backups from today's bridge-verification agents)
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   FOUNDRY (modset_builder.py tier-testing backups from today's bridge-verification agents)
?? deployed/config/ModsConfig.before-tier-visibility.xml   FOUNDRY (modset_builder.py tier-testing backups from today's bridge-verification agents)
?? deployed/config/ModsConfig.before-tier-warlab.xml   FOUNDRY (modset_builder.py tier-testing backups from today's bridge-verification agents)
?? infrastructure/artpipe/active/offbiome_gualaar_v3_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/barbslinger_redesign_v1_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/barbslinger_redesign_v1_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/barbslinger_redesign_v1_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/barbslinger_redesign_v1_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/barbslinger_redesign_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/barbslinger_redesign_v1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_drinker_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_drinker_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_drinker_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_drinker_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_drinker_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_drinker_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_gembug_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_gembug_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_gembug_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_gembug_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_gembug_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_gembug_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_glowbulb_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_glowbulb_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_glowbulb_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_glowbulb_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_glowbulb_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_glowbulb_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_grabber_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_grabber_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_grabber_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_grabber_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_grabber_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_grabber_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_megapleura_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_megapleura_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_megapleura_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_megapleura_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_megapleura_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_megapleura_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_soulchime_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_soulchime_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_soulchime_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_soulchime_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_soulchime_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/deeps_soulchime_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_dewback_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_dewback_v1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_grmolebear_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_grmolebear_v1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_kreetle_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_kreetle_v1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_megatardi_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_megatardi_v1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_orray_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_orray_v1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_rutcathedralroach_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_rutcathedralroach_v1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_rutscarroach_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_rutscarroach_v1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_wyyyschokk_v1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/facingrepair_wyyyschokk_v1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_0.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_0.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_3.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_3.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_4.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_4.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_5.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_5.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_fulgurite_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_fulgurite_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_fulgurite_v3.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_fulgurite_v3.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_gualaar_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_gualaar_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_gualaar_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_gualaar_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_gualaar_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/offbiome_gualaar_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/pyrelands_ash_deep_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/pyrelands_ash_deep_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/pyrelands_ash_heavy_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/pyrelands_ash_heavy_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/pyrelands_ash_light_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/pyrelands_ash_light_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/pyrelands_ash_trace_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/pyrelands_ash_trace_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agarilux_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agarilux_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agariluxprime_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agariluxprime_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agariluxprime_v3.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agariluxprime_v3.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agelesscap_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_agelesscap_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_arpeau_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_arpeau_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_brightbell_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_brightbell_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_bryolux_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_bryolux_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_crimsoncap_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_crimsoncap_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_dewshrooms_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_dewshrooms_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_dribblingcap_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_dribblingcap_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_dulcisplant_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_dulcisplant_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_falsefruit_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_falsefruit_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_furnacecap_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_furnacecap_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_giantagarilux_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_giantagarilux_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_glowstool_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_glowstool_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_greylady_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_greylady_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_greylady_v3.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_greylady_v3.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_nogtyl_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_nogtyl_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_nuitae_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_nuitae_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_palemoss_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_palemoss_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_paletree_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_paletree_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_paletree_v3.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_paletree_v3.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_pusmelon_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_pusmelon_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_recurvedstropharia_v3.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_recurvedstropharia_v3.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_regenerantveil_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_regenerantveil_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_rustpuff_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_rustpuff_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_sagecrust_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_sagecrust_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_shinecap_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_shinecap_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_skulltop_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_skulltop_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_slimypholiota_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_slimypholiota_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_swarmling_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_swarmling_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_swarmling_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_swarmling_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_swarmling_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_swarmling_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_violetwimple_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_violetwimple_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_wildpawn_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_wildpawn_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_wildpawn_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_wildpawn_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_wildpawn_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_wildpawn_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_wildpod_v2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_wildpod_v2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_wildpod_v2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_wildpod_v2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_wildpod_v2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_wildpod_v2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_witchesoyster_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_witchesoyster_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_wrinklecap_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rot_wrinklecap_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_agelesscap_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_agelesscap_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_falsefruit_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_falsefruit_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_1_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_1_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_1_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_1_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_1_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_1_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_2_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_2_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_2_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_2_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_2_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_2_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_3_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_3_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_3_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_3_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_3_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_3_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_4_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_4_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_4_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_4_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_4_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_4_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_5_east.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_5_east.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_5_north.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_5_north.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_5_south.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_firehawk_flying_5_south.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_furnacecap_plant_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_furnacecap_plant_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_gene_furnaceblood_icon_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_gene_furnaceblood_icon_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_grownfurnace_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_grownfurnace_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_liveingredient_agelesscap_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_liveingredient_agelesscap_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_liveingredient_euphoriccrown_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_liveingredient_euphoriccrown_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_liveingredient_regenerantveil_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_liveingredient_regenerantveil_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_liveprep_toxicinjection_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_liveprep_toxicinjection_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_livingfurnacecap_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_livingfurnacecap_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_palemoss_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_palemoss_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_paletree_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_paletree_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_regenerantveil_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_regenerantveil_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_symbiont_mycoid_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_symbiont_mycoid_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_symbiont_nightwake_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_symbiont_nightwake_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_symbiont_quickflesh_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_symbiont_quickflesh_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_symbiont_sheenblood_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_symbiont_sheenblood_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_tea_agereversal_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_tea_agereversal_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_tea_bioregeneration_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_tea_bioregeneration_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_tea_pleasure_v1.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/done/rut_tea_pleasure_v1.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.manifest.json   FOUNDRY (artpipe daemon continuous churn — not manually authored; safe to commit in bulk under the daemon's own name)
?? infrastructure/state/.rimflow_conc_97j8px_9/   pre-existing scratch / another window's -- not this wave
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing scratch / another window's -- not this wave
?? src/RimStarWars/SWBestiary/Defs/DesertPort/   pre-existing scratch / another window's -- not this wave
```

