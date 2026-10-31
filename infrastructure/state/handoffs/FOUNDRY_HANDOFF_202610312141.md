# FOUNDRY_HANDOFF_202610312140 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610311937`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The relaunch (Conductor go, 2026-10-31: exclude LAUNCHREADY = 25 tasks, archive old arm logs to a dated folder, fresh signed logs + fresh anchor roster, keep trio, all three arms together) is BLOCKED by one thing: arena_eventlog.report() matches signed ledger anchors by arm name only, so the old v3:60 and @roster:2 anchors make a fresh log read as a deleted tail. Never rotate the harness token (breaks harness.jsonl/critic_calib.jsonl signatures, routes around the trust check). Do NOT edit arena_judge.py, arena_critic_calib.py or anything hashed into the vet key @74156f55c8608337 (vet_runner_id hashes the whole judge file). LAUNCHREADY is already out: trial_tasks.json = 25 tasks (396292b976), answer check 28/0/0, pool_sha256 6d0ef995...2319 unchanged. (filed: ARENA_EVENTLOG_FIX_OLD_ANCHORS_REFUSE_FRESH)

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Nothing new for him. The Conductor was told of the block (cross-session message); his rulings are in the ledger via CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `ARENA_EVENTLOG_FIX_OLD_ANCHORS_REFUSE_FRESH` — builder ac5a46a8b1d0abb6b (Opus) is implementing a signed fresh-era marker + selftests + GPT review; it must NOT run the relaunch; NEXT: wait for its completion notice (or read rimflow show of the item for its commit), confirm vet_runner_id is still @74156f55c8608337, then archive the old arm event logs to a dated folder (delete nothing), start the new era with its command, and relaunch.
- `REPLAY_RELAUNCH` — launcher agent a34985fdf2a3fda4e finished (STOP at ruling 2); v3 unit still in an earlier failed state; NEXT: after the era fix lands, spawn a fresh rm-builder to do steps c-g from the brief: clear replay/ctl STOP files, `--plan` prints 25 tasks, launch all three via launch_arm.sh with absolute paths, PROVEN 5MIN per arm to replay/launcher.log, run arena_analysis.py with --ledger /home/mandrake/rm/anchor/infrastructure/state/ledger/events.jsonl and prove all three arms read trusted, then ONE line to the CONDUCTOR (SendMessage to CONDUCTOR); his replay line is 8 AM PDT Sunday Nov 1.
- `GATE_NOT_COVERED_BY_SWEEP` — still true (live NA, test_record needs signed arm records); NEXT: after relaunch, watch the first finished tasks for UNMEASURED/invalid test_record/live steps and tell the Conductor at once.
- `ARENA_DEFERRED_PAST_TRIAL` — TRIO_CRITIC_WIRE_LIVE_PLAN_TOO and ARENA_JUDGE_ENV_FIX_CODEX_OPENAI_PASSTHROUGH are blocked (edits change the vet/critic keys); ARENA_REPLAY_RESTORE_DUPLICATE_RUNS needs a Conductor ruling; ARENA_HANDOFF_MEASURE_RC_INTO_DEAD_SESSION is not an offline job; NEXT: file/claim them after the trial completes.
- `ARENA_ANCHOR_CLOSEOUT` and `CODE_REVIEW_OWED_ARENA` — unchanged from the 202610311937 handoff; NEXT: at trial end run arena_anchor_publish.py --final before the analysis; NEXT: at trial end run arena_anchor_publish.py --final; review the dirty arena files after the trial starts.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Items whose fix edits arena_judge.py or critic code silently invalidate the vet key (vet_runner_id hashes the whole file): check before claiming any arena item (see: ARENA_JUDGE_ENV_FIX_CODEX_OPENAI_PASSTHROUGH note).
- `rimflow release` with a guessed id/token can release an item you did not mean to; read the token from the same `next` output you claim from (see: this handoff).
- `rimflow implemented` moves item prose to items/closed/: stage BOTH paths or the commit leaves it half-moved (see: using-rimflow).

## Commits

```
87c59a30dd ledger: ARENA_TRIAL_FIX_LAUNCHREADY_NO_CSPROJ done at 396292b976; file ARENA_EVENTLOG_FIX_OLD_ANCHORS_REFUSE_FRESH (per CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM)
c9aa5dc21b ledger: close SEAT_CONTEXT_BACKSTOP_BUILD_BUSY_WINDOWS_TOO at 7f4e012c1c
396292b976 arena trial: exclude LAUNCHREADY (cannot pass at its reference fix); trial_tasks.json = 25 tasks
417a08197f handoff: BENCH, gate proven 25 of 26, replay relaunching
b9186e927d conversations: catch-up 11 record(s)
53fab41c42 ledger: DISPATCHER notes (1)
7f4e012c1c dispatcher schedule: FOUNDRY context backstop live, relaunch proof ended
2b46d5a0a2 ledger: owner keeps trio in the replay
8c5bf8fe71 ledger: DISPATCHER notes (1)
b810cbf3b2 ledger: FOUNDRY note on remaining pre-relaunch queue
d9f091aa85 ledger: DISPATCHER notes (1)
577a9f0724 items: RALPH_RECOVER_HARDEN_BLIND_TO_SUBCLASS_ARMS prose to closed/
afad3a2764 ledger: RALPH_RECOVER_HARDEN_BLIND_TO_SUBCLASS_ARMS implemented
7b15b78e5d arena loops: inherited _recover/already_failed read the subclass arm's records (ralph_c, trio), not ralph_a's
729ec56856 ledger: DISPATCHER notes (1)
7fbadc96a2 ledger: ARENA_JUDGE_ENV_FIX_CODEX_OPENAI_PASSTHROUGH deferred (judge edit invalidates vet key)
74138266b8 ledger: DISPATCHER notes (1)
6ccf856ef2 ledger: TRIO_SELFTEST_VERIFY_NO_REAL_RIMFLOW done (already fixed d1d9cf1867); TRIO_CRITIC_WIRE_LIVE_PLAN_TOO deferred past trial
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
 M src/RimMandrake/Utils/arena/arena_eventlog.py   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? .claude.json   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? "D:\\ClaudeWork\\rimmandrake\\foundry_arena\\gpt_review.md"   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S1_20261017T084726.txt   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S1_20261017T084802.txt   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S1_20261017T092155.txt   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S1_20261017T110253.txt   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S1_p00.png   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S1_p03.png   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S1_p10.png   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S1_p14.png   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S2_20261017T084824.txt   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S2_20261017T092355.txt   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S2_20261017T110404.txt   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S2_p00.png   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S2_p10.png   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S2_p30.png   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S2_p60.png   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
?? Transient/fw_scenes/live/S3A_p20.png   not mine: untracked Transient/fw_scenes and prior-session leftovers, plus ModsConfig backup (predecessor)
... 124 more uncommitted paths (by top-level dir: Transient 117, conversations 7): git status --short
```

