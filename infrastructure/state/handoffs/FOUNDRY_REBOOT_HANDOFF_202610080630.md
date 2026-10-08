# FOUNDRY_REBOOT_HANDOFF_202610080630 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202610071234`. Its "half-done" pointers that are not named
below still stand: read that file too.

**This handoff was written from outside the seat.** FOUNDRY did not hand off: the kernel
OOM-killed its Claude process at **2026-10-07 23:16:52 PDT**, about 4 hours into the
session, and nothing ran after that. The state below was reconstructed from git, `Transient/`,
the seat's transcript and the kernel journal. Everything listed is committed and pushed
unless a line says otherwise. **Game and bridge state is the last section; read it
before touching the game.**

## The one thing to carry forward

The seat died because of memory, not a bug. A subagent ran `git clone` of RimMandrake into
`/tmp/claude-1000/pushclone`. `/tmp` is a RAM disk (tmpfs), and its pages count against the
seat's 10G `MemoryMax` (`src/RimMandrake/Utils/claude_bounded.sh`) and **stay counted after
the writer dies**. The clone reached 12G. At the same time the full selftest suite ran with
**16 parallel workers** (python tests at 0.8–2.1G each). The kernel killed 23 processes
between 23:08 and 23:20, and Claude was one of them. The dead clone has been deleted.
**Until the fleet memory design lands:**
- Never clone or write large files under `/tmp`. Use a `git worktree` on ext4 under `~/rm/`.
- Run the selftest suite with at most 4 workers.

## What the owner should see

- GPT top-ten review: 9 of 10 written; **TerminalBiomes is missing**. None of the GPT claims
  in them are verified yet.
- The builders' unfixed design questions and provisional numbers are collected in
  `Transient/l0_design_observations_20261008.md`. They need his rulings.
- The fleet memory/clone/drive design pass is being written separately (by another session),
  to `docs/design/memory-clones-drives-2026-10-08.md` or the repo's design folder.

## What is half-done, and where it stops

- `ALL_MODS_L0_TESTS_1` — the 4 builders finished at 23:04 (42 mods: reports
  `Transient/l0_builder{1..4}_20261008.md`). The post-L0 selftest run
  (`Transient/selftest_after_l0_20261008.txt`) passed 329/336. 4 of the 7 failures were
  rc 137 OOM kills: `MandrakePatches/selftest_mandrakepatches.py`, `Utils/modcheck/selftest.py`,
  `StarWarsPatches/selftest_starwarspatches_semantics.py` and
  `UtinniPatches/selftest_utinnipatches_dump.py`. 3 are real failures, not yet sorted:
  `Utils/selftest_solarmirrors_fuzz.py`, `rimflow/selftest_items_glob_live.py` and
  `Utils/artpipe/selftest_artpipe_state.py`. The triage agent died before it reported.
  NEXT: rerun those 7 one at a time, then classify each failure as an L0 regression, a flake,
  someone's work in progress or a timeout, and fix the regressions.
- `WASTELAND_TOXIC_BUILDUP_NEVER_APPLIES_1`, `WASTELAND_LIVE_SUITE_FAILS_ACC_BIOMES_1`,
  `CONTAGION_LIVE_SUITE_FAILS_ACC_BIOMES_1` and the rest of the acc_biomes findings — the fixer
  started at 23:04 and died at 23:16. Nothing was fixed; `Transient/acc_biomes_fixes_20261008.md`
  is an empty skeleton (not committed). The findings are in
  `Transient/belt_acc_biomes_20261008.md`. The fixer's brief also covered the LeaningScrub
  bloom toggle, the Stillsand gravel and sunstruck bugs, the slime seeker marks, the
  RustCathedral setting, the aerosol screen and the linked-graphic null-reference.
  NEXT: relaunch one fixer: verify each finding in source, add a regression test, and drop the stale ones.
- L1/L2 acceptance on `acc_green_min` (no ledger item; progress in
  `Transient/belt_acc_green_20261008.md` and outputs in `Transient/acc_green/`, both pushed with
  this handoff). First pass at 22:50: GravshipLanding ALL_GREEN; Scarlands 26 pass, 0 fail;
  ShipVermin, Abyss, OasisMaker, Pyrinth and HugeThings had failures, triaged in that file. The
  Warcasket and Ninefold/LuminousPigment suites needed a rerun with `python -u`. The driver died
  at 23:16, and its live checks were not yet committed into each mod's `validation.py`.
  NEXT: take the bridge, finish the `acc_green_min` reruns, and commit the live checks into
  each mod's `validation.py`.
- Remaining L1/L2 tiers: `acc_green_min2`, `acc_l1x`, `acc_harness` and `flowworks` were never
  started. NEXT: run them in that order after `acc_green_min`, one bridge driver at a time.
- `GPT_FULL_REVIEW_TOP10_1` — 9 of 10 are in `design/RimMandrake/gpt_reviews/`: CreatureBehaviors,
  EnvironmentalHazards, FlowWorks, GimmeSomeSlack, Stillsand, DivingInteraction, Scarlands,
  LuminousPigment and FeverWood. The last five were rescued and pushed at `5438ed5d3`.
  TerminalBiomes' input `/tmp/gptreview_TerminalBiomes.txt` was built at 00:05, but no review
  came back. NEXT: run `design/RimMandrake/gpt_reviews/run_gpt_review.py` for TerminalBiomes
  alone (input staged on ext4, not `/tmp`), then verify the claims of all 10 reviews in source
  before acting on any of them.
- `CANON_FAUNA_FLORA_GPT_REVIEW_1` — all 12 batches were verified against Wookieepedia and the
  confirmed fixes merged. These were 14 unpushed commits, which were rebased and pushed from
  outside the seat. NEXT: on wake, `git pull --rebase` drops the local duplicates; then close the
  item if the proposals file needs no owner ruling.
- `SOLAR_MIRRORS_BUILD_1` — offline validation finished pass 3 (`232ef60dd`; report
  `Transient/solarmirrors_validation_20261008.md`). Pass 3 found and fixed 3 defects, so the
  ritual is not done; the validator died before pass 4. NEXT: run one more independent review
  pass and stop only on a pass that finds no new kind of problem; then the live criteria.

## Traps learned

- tmpfs writes are charged to the seat's cgroup and survive the writer's death; a dead
  `/tmp` clone pinned FOUNDRY at 9.2G of 10G all night (see: the fleet memory design doc above).
- Selftest fan-out of 16 workers inside one 10G seat OOM-kills tests and reports them as
  FAIL (rc 137) (see: `Transient/selftest_after_l0_20261008.txt`).
- A Claude process killed mid-session leaves its terminal in mouse-tracking mode; type
  `reset` in that window.

## Local tree state (FOUNDRY clone, `/home/mandrake/rm/foundry`)

- `main` is ahead of origin with the **pre-rebase** copies of the 14 canon commits; they are
  already on origin. Rebase; do not push them a second time as merges.
- Uncommitted, untouched by the rescue: rebuilt DLLs + `.srchash` for GelatinousSlime and
  Scarlands (Warscar), a SacredGraffiti assembly, FlowWorks `northstar/` and `art_source/`
  edits, `FOUNDRY.jsonl` ledger appends, and a lot of `Transient/` scratch. Whose they are
  is unknown; probably the acc_biomes fixer or the bridge drivers. Read the diff before
  committing or discarding.

## Game and bridge state

- At 06:30 PDT `RimWorldWin64.exe` was still running (pid 29948, ~3.3 GB), on tier
  **`acc_green_min`** (35 mods), launched by FOUNDRY's driver via `steam://rungameid`.
- FOUNDRY took the bridge at 22:32 and **never released it**; its holder is dead. Check the
  cross-clone bridge lock (`BRIDGE_LOCK_CROSS_CLONE_RACE_1`) and release or reclaim it on
  purpose before another window swaps tiers.
- HugeThings was redeployed during the sitting (the deployed copy was stale after the Titanic
  merge).
- The art pipeline (`rm-artpiped`) is independent of the seat and kept running all night: since
  23:00 it finished 213 jobs and failed 38.
