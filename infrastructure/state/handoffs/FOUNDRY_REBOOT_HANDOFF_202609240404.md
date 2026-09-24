# FOUNDRY_REBOOT_HANDOFF_202609240404 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609240213`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

The recurring "rebase nonsense" in this repo had two distinct causes, and only one
of them needed new architecture: (1) `events.jsonl` being one file both seats
append to and commit — fixed by sharding per seat into
`infrastructure/state/ledger/events/<SEAT>.jsonl`, so two seats' appends can never
land in the same git-tracked file again (`model.append()`/`model.read()` in
`src/RimMandrake/rimflow/model.py`, currently UNCOMMITTED, see below); and (2) the
health-publisher regenerating 5 tracked artifacts mid-rebase because the
post-commit hook and `_trigger_health_rebuild` both fire on every replayed
commit — fixed by a rebase/merge guard in `codebase_health_publish.py`, already
committed and pushed (`580ff317a`). Per-agent worktree isolation for subagents
(`isolation: "worktree"` on the `Agent` call) already existed as a platform
capability the whole time — the gap was nobody defaulting to it, not missing
code; CHARTER now says to default to it for multi-file/long subagents
(`580ff317a`).

## What the owner should see

**The events.jsonl sharding change is sitting uncommitted, on his explicit
instruction to pause before I committed it.** 14 files touched (`model.py`,
`cli.py`, `render.py`, `live_proof_lint.py`, several other ledger readers the
Opus subagent found and fixed, and 4 selftest files). Selftests: 74/75 green,
the 1 failure (`selftest_deployed_biome_refs.py`, a dangling `RSW_Korrum` ref
in `RUT_Scarlands.xml`) is a pre-existing content defect unrelated to this
change. Render before/after matches. The change is ALREADY functionally live
in practice, not just staged in theory — BENCH's own window picked it up
mid-session purely from the on-disk `.py` edits (no commit needed for that;
git state and running-code state are different things on a shared
filesystem) and has already committed 2 real events through the new
`infrastructure/state/ledger/events/BENCH.jsonl` shard itself (commit
`1e95238fe`), with 1 more line appended since. This needs a decision: review
+ commit now (recommended — it's already validated by real use), or hold
longer. I have not committed it. See "half-done" below for the exact next
action.

## What is half-done, and where it stops

- EVENTS_JSONL_SHARDING_1 -- proposed, needs owner; NEXT: review the diff across
  the 14 touched files (`git status --porcelain -- src/RimMandrake/rimflow/
  src/RimMandrake/Utils/broadcast.py src/RimMandrake/Utils/codebase_health.py
  src/RimMandrake/Utils/handoff.py src/RimMandrake/Utils/modcheck/doctor.py
  src/RimMandrake/Utils/project_maturity_dashboard.py
  src/RimMandrake/Utils/repair_torn_ledger.py .claude/hooks/queue_lint.py
  .claude/hooks/selftest_queue_lint.py`), then `git add`/`git commit` by
  explicit path including `infrastructure/state/ledger/events/BENCH.jsonl`
  (tracked, 1 uncommitted line -- do not lose it) and the re-rendered
  `infrastructure/state/queue/{BENCH,FOUNDRY}.md`, then push. `events.jsonl`
  itself (the 10,890-line legacy file) needs NO action -- it stays exactly as
  committed, forever.

## Traps learned

- The post-commit hook and `_trigger_health_rebuild` both fire per replayed
  commit during a rebase, so a mid-rebase health-artifact write -- not a real
  leftover conflict -- was the actual "rebase looks stuck" cause (filed:
  LESSONS_INBOX).
- `Agent(isolation:"worktree")` already existed the whole time this repo was
  hand-working around worktree-agent merge conflicts; the gap was nobody
  defaulting to it (filed: LESSONS_INBOX).

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
1e95238fe Webwork sitting 2026-09-23: Ollathrix owner-and-nest record; flora/fauna rosters are SKELETONS
b97f64217 BENCH handoff 202609240332: shoreline mechanism + four sea catch tables; two traps filed
580ff317a Refuse health-artifact rewrites mid-rebase/merge; default subagents to worktree isolation
84aa218ff Ledger sync: SEA_FLOOR_AND_CATCH_PASS_1 propane-suite note; two lessons filed
f392edb17 SEA_FLOOR_AND_CATCH_PASS_1: propane shore uses FlowWorks propane suite; duplicate RUT_PropaneShallow deleted (owner card)
fdd63cb72 Merge remote-tracking branch 'origin/main'
f9dca8846 Ledger sync: SEA_FLOOR_AND_CATCH_PASS_1 card answers note
d5acd7993 SEA_FLOOR_AND_CATCH_PASS_1: propane catch refinery bill (owner card), three card answers recorded
efd136422 Handoff: correct a reference to a commit the rebase skipped
32860682b Handoff: four times this sitting the answer was already built
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-24T01:17:37Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M .claude/hooks/queue_lint.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M .claude/hooks/selftest_queue_lint.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M Transient/codebase_health.html   -- FOUNDRY, ambient health-publisher regen output
 M Transient/codebase_health.json   -- FOUNDRY, ambient health-publisher regen output
 M Transient/codebase_health_artifact.html   -- FOUNDRY, ambient health-publisher regen output
 D infrastructure/artpipe/pending/RSW_Cindermite_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Cindermite_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Cindermite_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Dunegrass.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Dunestalker_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Dunestalker_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Dunestalker_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Ferroclaw_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Ferroclaw_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Ferroclaw_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Sandhorn_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Sandhorn_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Sandhorn_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Sandmaw_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Sandmaw_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Sandmaw_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Sandstrider_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Sandstrider_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Sandstrider_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Spineroller_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Spineroller_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Spineroller_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Stareling_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Stareling_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Stareling_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_SweetbarkTree.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Tuskcoil_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Tuskcoil_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Tuskcoil_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_VellaraBloom.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Voltmaw_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Voltmaw_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/RSW_Voltmaw_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/bluedesert_dorrak_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/bluedesert_dorrak_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/bluedesert_dorrak_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/bluedesert_krissek_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/bluedesert_krissek_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/bluedesert_krissek_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/bluedesert_vekkit_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/bluedesert_vekkit_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/bluedesert_vekkit_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/desertportb_convor_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/desertportb_falumpaset_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/desertportb_falumpaset_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 D infrastructure/artpipe/pending/rm_greatbole_v1.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 M infrastructure/artpipe/registry.jsonl   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 M infrastructure/artpipe/throughput.jsonl   -- artpipe daemon (background, pre-existing this session, not this wave's work)
 M infrastructure/dashboards/hub/data/health.json   -- FOUNDRY, ambient health-publisher regen output
 M infrastructure/state/codebase_health_last.json   -- FOUNDRY, ambient health-publisher regen output
 M src/RimMandrake/Utils/broadcast.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M src/RimMandrake/Utils/codebase_health.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M src/RimMandrake/Utils/handoff.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M src/RimMandrake/Utils/modcheck/doctor.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M src/RimMandrake/Utils/project_maturity_dashboard.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M src/RimMandrake/Utils/repair_torn_ledger.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M src/RimMandrake/rimflow/cli.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M src/RimMandrake/rimflow/live_proof_lint.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M src/RimMandrake/rimflow/model.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M src/RimMandrake/rimflow/render.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M src/RimMandrake/rimflow/selftest_cli.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M src/RimMandrake/rimflow/selftest_concurrency.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M src/RimMandrake/rimflow/selftest_items_glob_live.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
 M src/RimMandrake/rimflow/selftest_model.py   -- FOUNDRY -- EVENTS_JSONL_SHARDING, PAUSED uncommitted per owner instruction
?? infrastructure/artpipe/daemon_run_20260923_owner_100pct.log   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Cindermite_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Cindermite_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Cindermite_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Cindermite_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Cindermite_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Cindermite_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Dunegrass.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Dunegrass.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Dunestalker_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Dunestalker_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Dunestalker_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Dunestalker_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Dunestalker_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Dunestalker_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Ferroclaw_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Ferroclaw_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Ferroclaw_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Ferroclaw_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Ferroclaw_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Ferroclaw_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandhorn_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandhorn_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandhorn_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandhorn_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandhorn_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandhorn_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandmaw_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandmaw_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandmaw_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandmaw_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandmaw_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandmaw_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandstrider_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandstrider_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandstrider_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandstrider_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandstrider_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Sandstrider_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Spineroller_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Spineroller_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Spineroller_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Spineroller_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Spineroller_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Spineroller_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Stareling_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Stareling_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Stareling_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Stareling_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Stareling_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Stareling_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_SweetbarkTree.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_SweetbarkTree.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Tuskcoil_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Tuskcoil_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Tuskcoil_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Tuskcoil_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Tuskcoil_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Tuskcoil_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_VellaraBloom.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_VellaraBloom.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Voltmaw_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Voltmaw_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Voltmaw_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Voltmaw_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Voltmaw_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/RSW_Voltmaw_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_boma_v1_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_boma_v1_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_boma_v1_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_boma_v1_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_boma_v1_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_boma_v1_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_dewback_v1_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_dewback_v1_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_dewback_v1_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_dewback_v1_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_insectomorph_v1_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_insectomorph_v1_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_insectomorph_v1_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_insectomorph_v1_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_shiro_v1_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_shiro_v1_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_shiro_v1_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_shiro_v1_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_shiro_v1_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_shiro_v1_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_vornskyr_v1_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_vornskyr_v1_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_vornskyr_v1_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_vornskyr_v1_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_vornskyr_v1_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_vornskyr_v1_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_whisperbird_v1_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_whisperbird_v1_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_whisperbird_v1_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_whisperbird_v1_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_whisperbird_v1_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_whisperbird_v1_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_zakkeg_v1_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_zakkeg_v1_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_zakkeg_v1_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_zakkeg_v1_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_zakkeg_v1_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/canon_zakkeg_v1_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_convor_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_convor_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_falumpaset_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_falumpaset_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_falumpaset_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_falumpaset_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_falumpaset_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_falumpaset_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_feralgrazer_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_feralgrazer_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_feralgrazer_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_feralgrazer_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_feralgrazer_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_feralgrazer_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_feralnerf_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_feralnerf_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_feralnerf_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_feralnerf_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_feralnerf_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_feralnerf_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_graniteslug_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_graniteslug_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_graniteslug_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_grank_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_grank_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_grank_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_grank_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_grank_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_grank_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_horax_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_horax_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_horax_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_horax_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_horax_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_horax_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_jakobeast_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_jakobeast_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_jakobeast_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_kraytdragon_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_kraytdragon_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_kraytdragon_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_kraytdragon_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_krykna_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_krykna_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_krykna_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_mossbeetle_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_mossbeetle_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_mossbeetle_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_nerf_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_nerf_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_nerf_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_pikobis_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_pikobis_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_pikobis_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_pikobis_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_plant_bloddle.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/rm_greatbole_v1.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/done/rm_greatbole_v1.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/RSW_Voltmaw_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/RSW_Voltmaw_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_dorrak_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_dorrak_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_dorrak_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_dorrak_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_dorrak_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_dorrak_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_krissek_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_krissek_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_krissek_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_krissek_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_krissek_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_krissek_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_vekkit_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_vekkit_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_vekkit_north.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_vekkit_north.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_vekkit_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/bluedesert_vekkit_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/canon_dewback_v1_south.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/canon_dewback_v1_south.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/canon_insectomorph_v1_east.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/artpipe/failed/canon_insectomorph_v1_east.manifest.json   -- artpipe daemon (background, pre-existing this session, not this wave's work)
?? infrastructure/state/.rimflow_conc_97j8px_9/   -- pre-existing selftest debris (mtime 2026-09-17, not this wave)
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   -- pre-existing (2026-09-11), not this wave
?? infrastructure/state/handoffs/BENCH_REBOOT_HANDOFF_202609240404.md   -- BENCH's own handoff, concurrent window, not FOUNDRY's to commit
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   -- FOUNDRY, earlier this session's own routine backups, pre-existing before this wave
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   -- FOUNDRY, earlier this session's own routine backups, pre-existing before this wave
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   -- FOUNDRY, earlier this session's own routine backups, pre-existing before this wave
```

