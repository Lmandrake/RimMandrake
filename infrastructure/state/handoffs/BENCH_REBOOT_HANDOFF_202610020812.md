# BENCH_REBOOT_HANDOFF_202610020812 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610020550`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The git workflow was replaced overnight (owner: *"implement this absolutely fully"*). **`D:\Luke\dev\RimMandrake` is now a read-only mirror with no `.git`**, refreshed every 5 min by `rm-mirror.timer`. Seats work in `/home/mandrake/rm/bench` and `/home/mandrake/rm/foundry` with plain git (`./publish -m … <paths>`). Everything else follows from that: `design/RimMandrake/GIT_WORKFLOW.md` is the operating doc.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. **Relaunch the fleet** (desktop "Start Agent Fleet" or the AGENT BENCH / AGENT FOUNDRY profiles): both now open in the ext4 clones. FOUNDRY's old window was closed at 08:02Z (idle 2 h+). The old D:\ BENCH window (this one) should be closed too.
2. **Kept until you say delete:** `D:\Luke\dev\_rm_old_git_2026-10\` (the old `.git`), `D:\Luke\dev\_rm_old_worktrees_2026-10\` (91 dirty worktrees, all archived as `archive/dirty/*` tags), `D:\Luke\dev\_rm_shared_tree_leftovers_2026-10\leftovers.tar` (596 MB, 3,497 files + sha256 manifest). 112 `archive/*` tags on GitHub hold every unique commit (116/116 verified).
3. **Measured result:** 14-day replay conflict rate at a 5-commit-stale base 43.6% → 10.8% (pre-shard ledger counted as non-conflicting; 21.2% if counted). `git status` 15.3 s on D:\ → 0.06 s on the clone.
4. **You can veto:** queue pages are no longer in git (read via `rimflow queue <seat>` or the hub); the art daemon is now the `rm-artpiped` service and the Artist tab just shows its log; `codex.exe` callers default to `-m gpt-5.5` (your `config.toml` still says `gpt-6.1-sol`, which `codex exec` refuses on a ChatGPT account — untouched).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `GIT_WORKFLOW_MIGRATION_1` — all 9 phases implemented and pushed; only the plan's multi-day live bars remain (≤1 manual rebase/day, 0 Claude writes to D:\ for 3 days, pool telemetry); NEXT: on 2026-10-05 read `/home/mandrake/rm/pool/telemetry.jsonl` and the ledger-sync commit count, record them in the plan §4 and close the item.
- `GIT_WORKFLOW_MIGRATION_1` (pool rescues) — rescue events go to `/home/mandrake/rm/pool/rescues.jsonl`, not the ledger; NEXT: add a rimflow `rescue` event + `rimflow next` listing so open rescues reach a seat.
- `GIT_WORKFLOW_MIGRATION_1` (selftests) — 110/115; 4 fail identically on pre-migration origin (walklint, one_path_seam, sound_paths, items_glob_live); NEXT: file one item for the four and fix them.
- `BAROQUE_BEDAZZLE_PROGRAM_1` — carried from the previous handoff, untouched tonight; NEXT: file `BLACKCRAGS_BEDAZZLE_SITTING_1` and background its movement 1–2 review to Opus.
- `CONTAGION/WASTELAND/BLUEDESERT/FLOODEDCANYON_BEDAZZLE_SITTING_1` — carried, untouched; NEXT: read each sitting's ledger notes against the program's four movements and close the complete ones.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- codex.exe fails from ext4 and is flaky from D:\; inline inputs, `-m gpt-5.5`. (filed: lessons/20261002T081258Z-BENCH-codex-exe-needs-inline-inputs.md)
- WorktreeCreate's real stdin differs from the docs; WorktreeRemove never fires. (filed: lessons/…-worktreecreate-hook-real-contract.md)
- A push into a repo can start auto-gc there; use `-c gc.auto=0`. (filed: lessons/…-push-into-repo-triggers-auto-gc.md)
- drvfs reports 0755 everywhere → `core.fileMode=false`; mirror clean check needs `./mirror status`. (filed: lessons/…-drvfs-filemode-mirror-index.md)

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (1) — the next seat's queue

- `GIT_WORKFLOW_MIGRATION_1` — Git workflow migration: guard D:\ writes, per-seat ext4 clones, generated views out of git, ledger union+dedupe, worktree drain to archive tags, helpe

## Commits

```
327d7342e Git migration Phase 6B: D:\ frozen as mirror export, artpipe on systemd
7f4eaffc6 Phase 8: docs, skills and memory describe the seat-clone workflow; add GIT_WORKFLOW.md
6b87accbe winbuild.py: executable bit
4eb6e8e0a codex staging on D: for ext4 callers; default -m gpt-5.5; gpt_consult.py
4ec60b49e Drain Phase 6A done: 116/116 commits reachable from origin, 4 worktrees removed, leftovers tarred
bd53866dd Phase 5 report: artpipe section
abf0aadb4 artpipe: queue state leaves git for D:\Luke\dev\_artpipe (migration Phase 5)
11ff3d20f mirror.py: bare-repo export of origin/main to D:, flock + MIRROR_STALE; systemd unit written, not enabled
2f2680dc7 Drain: 13 archive + 96 dirty-snapshot tags; never let a push start gc in D:\
f8231153c Phase 5 report: lint coverage, residual risks
5e3e1472c ledger_lint: also lint the append-only code-review records (code_review/*.jsonl)
ee58c4c53 Phase 5 migration report (in progress)
d8e029fc2 DIRTY_CODE_REVIEW_STANDING_LOOP_1: wave write-ups move to one file per wave
aefcca607 Lessons inbox: one file per lesson under state/lessons/ [no-drain]
eb6c38e90 Code review status: append-only per-seat records replace CODE_REVIEW_STATUS.json
f20abbea0 Drain: census results; safe-ignored set widened to runtime lock/log/BRIDGE/derived
3532bfb22 Git plan Phase 4: union ledger shards, reader invariant, ledger lint, generated views out of git
688b41245 drain_worktrees.py: census/archive/snapshot/shared/remove/verify for the D:\ worktree drain
f40d2b99f Wire WorktreeCreate/WorktreeRemove to the worktree pool (Phase 7)
344f36af5 Phase 7: subagent worktree pool, local rescue refs, seat-side landing of submit refs
... 14 more: git log --oneline 2e9bd361f..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-10-02T05:40:53Z

Working tree clean apart from untracked `Transient/`.

