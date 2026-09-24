# BENCH_REBOOT_HANDOFF_202609242041 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609241818`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

The engine already answers "who started it": every hit carries
`DamageInfo.Instigator` AND `InstigatorGuilty`, and vanilla sets guilt by
drafted-ness (`Bullet.cs:22`, `Verb_MeleeAttackDamage.cs:50` — undrafted
self-defense is NOT guilty). So water-truce retribution needs no
"don't fight back" rule — key on the first GUILTY hit in the truce radius.
Full citations in `infrastructure/state/items/WATER_TRUCE_RETRIBUTION_1.md`;
this generalizes to any future "aggressor detection" mechanic.

## What the owner should see

Nothing pending his eye — all 14 rulings today were his own cards and typed
words, recorded verbatim (Weeping Stones sitting close `af3eaa622`, shine
verdicts `bef32f63e`, second round `1ebd0b644`). One inherited flag worth his
awareness, not mine to rule: FOUNDRY's 2026-09-24 live test proved the Rust
Cathedral wall-tier GenStep places ZERO cathedral walls on real Base_Player
maps — a genuine shipped-content bug, recorded on `RUST_CATHEDRAL_MECHANICS_1`.

## What is half-done, and where it stops

- `STOCKED_POOL_BUILD_1` / today's roster art (~20 new subjects: 10 flora + 10
  fauna rows all marked OWED, + 8 pool bestiary) — nothing queued yet;
  NEXT: sweep `infrastructure/artpipe/done/` + `_artsrc/` + registry for
  existing renders BEFORE filing any fill_queue.py job (standing owner rule).
- `WEEPINGSTONES_RM_MOD_BUILD_1` — proposed, now carries the ruled cast note;
  NEXT: FOUNDRY claims it alongside the three flagship items (`STOCKED_POOL_BUILD_1`,
  `OASIS_MAKER_BUILD_1`, `WATER_TRUCE_RETRIBUTION_1`) — pool-body bookkeeping
  (`RM_MapComponent_PoolStock`) is shared between the first two, build it once.
- Docs' "Open questions" sections (stocked-pool + oasis spec + both rosters)
  hold only BENCH-settled smalls and deferred lanes; NEXT: nothing — none
  blocks any build, they resolve inside the builds that own them.

## Traps learned

- "Terramorph" on disk is our art override for the AA_Terramorph CREATURE, not
  a terraforming mod; the real donor is Fertile Fields 1.6, license unstated —
  pattern only (filed: LESSONS_INBOX; recorded in OASIS_MAKER_BUILD_1).
- `block_forged_owner_said` refuses a genuine quote from the session-OPENING
  message (the /clear caveat wrapper hides it from the transcript check) —
  take the guard's prescribed exit, don't retry (filed: LESSONS_INBOX).
- `json.dump` on a hand-formatted 93-line roster JSON exploded it to 543 lines;
  restored from backup and patched textually instead (see: memory
  patch-a-curated-artifact — this is its JSON face).
- Peer `index.lock` contention hit 3 of ~8 commits this session; a 5-30 s
  bounded wait loop cleared every one (see: commit `f07f3a1fb`, the index.lock trap's durable home).

## Closed since the last handoff (1)

- `WEEPING_STONES_DESIGN_SITTING_1` — af3eaa622

## Filed and still open (3) — the next seat's queue

- `WATER_TRUCE_RETRIBUTION_1` — Water-truce retribution (owner typed 2026-09-24): first GUILTY hit in truce radius turns wildlife on the aggressor faction; engine attribution MEASURE
- `STOCKED_POOL_BUILD_1` — Build the Stocked Pool kit: 8-row pool bestiary, husbandry loop (pen zones, PoolStock bookkeeping), doubt-meat mood economy, cuisine hooks - all rulin
- `OASIS_MAKER_BUILD_1` — Build the oasis-maker machine: ring-growth to real water at center, shade+rock placement floor with projected-footprint overlay, sold-very-expensive +

## Commits

```
3afd996db DIRTY_CODE_REVIEW wave 62: fix 4 real bugs in never-entered Utils tools
50c52e632 Ledger sync: NONCANON_BEAST_RENAME_1 Phase 1 (land) complete, gated to owner
06b5b2abf NONCANON_BEAST_RENAME_1: batch 3 drafts close Phase 1 for every land biome
00ecc5b7d Ledger sync: XENOTYPE_NONCOSMETIC_FIXES_1 closed, AQUATIC_WATER_BREATHING_GENE_1 re-gated to bridge
b90029e23 NONCANON_BEAST_RENAME_1: resolve 3 duplicate-name pairs, keep the earlier name
f53b7fa38 Ledger sync: design items superseded by their FOUNDRY build successors
1ebd0b644 Second card round ruled: wild-gentle/stocked-nasty, doubt-meat mood economy, real water at oasis center, sold-very-expensive acquisition
aab6045c5 Stocked Pool design draft: 8-row pool bestiary, husbandry loop, cuisine hooks
7b9ac3956 Oasis-maker spec drafted; Terramorph misidentification corrected to Fertile Fields
bd39b17cc rimflow: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 61 ledger note
8b3cc5a83 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 61 note
9c6a17531 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 61: mark 5 more files CLEAN
9d2e88945 Fix: RM_Patch_LeachmossWildSpawnGate.cs was missing from RM_EnvironmentalHazards.csproj
bef32f63e Shine portfolio ruled: fish husbandry greenlit, oasis-makers + retribution redirected, 2 options dead
80fe48b93 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 61: mark 3 EnvironmentalHazards files CLEAN
fd960504b rimflow: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 60 ledger note
ceb853672 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 60: mark 8 EnvironmentalHazards files CLEAN
69c2b356a Ledger sync: NONCANON_BEAST_RENAME_1 batch 2 note
7bb3fec38 NONCANON_BEAST_RENAME_1: batch 4 drafts (poison forest, miasma, desert, scarlands, rot, dune sea, wasteland, cracked lands)
ba59d465f rimflow: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 59 ledger note
... 44 more: git log --oneline f07f3a1fb..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-24T15:03:39Z

Uncommitted — NONE of it is this window's; grouped by owner, left in place:

- `infrastructure/artpipe/{active,pending,done,failed}/*` + `registry.jsonl` +
  `throughput.jsonl` (~280 paths, desertportb wave + rm_* v1 jobs) — the artpipe
  DAEMON's live churn; it moves jobs pending→active→done continuously. Do not
  commit mid-flight; the daemon's own sync handles it.
- `Transient/codebase_health*` + `infrastructure/dashboards/hub/data/health.json`
  + `infrastructure/state/codebase_health_last.json` — the health publisher's
  rebuild artifacts (re-dirtied by every code_review_status.py call).
- `infrastructure/state/CODE_REVIEW_STATUS.json` — FOUNDRY's standing review
  loop (waves 59-62 ran concurrently this session).
- `infrastructure/state/modlists/ModsConfig*backup*` (4 files) + cherrypicker
  PRESWAP + `infrastructure/state/ledger/events/OWNER.jsonl` — Desktop live-test
  tooling backups (Rust Cathedral / bacta enables) + the owner's own shard;
  theirs to commit or cull.

