# Remote work: tickets an offline builder can take

Written by the Conductor 2026-11-17 about 5:45 PM PST, on the owner's offer of another model that can build but cannot
run the game. This file is a work order, not a record: each ticket's authority is its item in the ledger
(`python3 src/RimMandrake/rimflow/cli.py show <ID>` prints the full text and every note). When a ticket lands, its
entry is deleted from this file.

## Rules for the builder

1. **One ticket, one commit, one branch.** Branch `remote/<ticket id in lower case>` cut from current `origin/main`.
   Never push to `main`; never force-push. The Conductor reviews each branch (an independent reviewer reads it), runs
   the ticket's verify command, and lands it.
2. **Read first:** `CLAUDE.md` at the repo root, then the item (`cli.py show <ID>`), then the files it names. Never guess
   a name, a field or a path: read it.
3. **Stay inside the ticket.** Minimal diff, only the files the ticket names plus its selftest. No refactor, no
   drive-by fixes. If the ticket turns out to need a wider change, stop and say so in the branch's last commit message
   instead of widening it.
4. **Test first.** Write the acceptance case, watch it FAIL on the base, then fix. The commit message states the verify
   command, what it read on the base (failing) and what it reads now. Cover the input kinds the ticket's contract
   defines (empty, missing, invalid), not only the example given.
5. **Write no ledger events** (nothing under `infrastructure/state/ledger/`), run no `rimflow` verb that writes, start
   no game, touch no file under `C:\`, and do not run `modcheck run` (it rewrites the live mod list).
6. **"Could not look", "failed", "zero" and "empty" are four different answers** in every return value and message you
   write. A tool that cannot answer exits non-zero and says why.
7. Commit identity for this repo: `Lukas Mandrake <lukas.mandrake@gmail.com>`.

## Tickets, in the order the Conductor would like them

### 1. `RIMMANDRAKE_UNBLOCK_PUBLISH_UNTRACKED_FILE_EQUALS_ORIGIN_COPY`

**Why this one suits remote work:** Small, self-contained, hit twice today.

**Ticket text:** ./publish REFUSED twice 2026-11-17 4:29 PM PST: 'git reset --keep failed: Untracked working tree file conversations/2026-11-17-2328-2c2a405a.md would be overwritten', when another lander (seat_dirt) had already landed a byte-identical copy (22215 bytes both). Hand workaround: moved the local copy aside. Fix: before the branch move, an untracked file whose content equals origin's blob is removed (or parked) by publish itself. Acceptance: a new case in src/RimMandrake/Utils/selftest_publish.py: fixture clone with an untracked file identical to the incoming commit's file publishes (fails on base with REFUSED); a DIFFERENT untracked file still refuses or parks, never silently lost

### 2. `OPS_WRAPUP_SKIP_CLONES_OF_LIVE_FLEET_RUN`

**Why this one suits remote work:** Small, one tool, a false alarm that cost a hand-clear.

**Ticket text:** wrapup.debris_standing alarmed on cleanse-Greentide, a clone of a still-running designer_cleanse fleet (pid 2245702): 2 rows (stray root models.md draft) stood ~40 min until a hand-clear. Acceptance test: a wrap-up row for a session whose clone is owned by a live fleet process is not counted standing until the fleet exits; selftest_wrapup fails on base.

### 3. `RIMMANDRAKE_TEST_WALK_FRAME_JUDGE_OFFLINE_TWO_MUTANTS_LIVED`

**Why this one suits remote work:** Plain Python test work; no game needed.

**Ticket text:** ExplosiveKnockback Polish (walk_storeroom_raid): PF_V_FRAME_OVER_LOOSE (10% -> 50%) and PF_V_FRAME_ROW_ALWAYS_PASS in validation.py survived every offline suite: the judging is plain Python but no offline test feeds it two arms. Fix: a --selftest in validation.py (or a selftest file) that calls the FRAME_BUDGET judge with fixed arm dicts. Acceptance test: none, a new offline case the fix writes; see smallest_fix. Evidence: design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_5/lane2/faults.json

### 4. `RIMMANDRAKE_EXTEND_GRAFFITI_FUZZ_SIX_RULES_LANE_ONE_CAUGHT`

**Why this one suits remote work:** Plain Python test work on the Graffiti kernel; no game needed.

**Ticket text:** Graffiti T_FUZZ misses six kernel rules the blind lane 1 catches (budget cap, visit cap, numb good, craft Normal, scrawl ceiling, fight from nothing). Polish. Acceptance test: plant_faults.py --expect-caught on those six exits 0; watched FAIL on 8c4bced9e (6 missed).

### 5. `RIMMANDRAKE_TRACE_REPIN_FROM_FIRST_PIN_B_CHANGE_SKIPPED`

**Why this one suits remote work:** A Codex attempt was STOPPED on this today; read the item's notes for the narrower 'what would pass' (record the pin sha in stage.json) before starting.

**Ticket text:** designer_stage.py l.2239-2243 input_changes uses the LAST occurrence of the pinned hash (A->B->A->C returns only C's change), so the automatic re-pin (cd86ab4735) can succeed without sources for the B change. Anchor to the commit that RECORDED the pin, never to commit dates (review 2 of the parent found a date-trusting fix wrong). ONLY this one finding, minimal diff inside src/RimMandrake/rimflow/designer_stage.py, no refactor, no change to dispatcher.py or role_launch.py. Acceptance: one new case in selftest_designer_stage.py or selftest_designer_repin.py that fails on base and passes after; verify: python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_designer_repin selftest_designer_stage_land. Reusable failing cases exist in D:\ClaudeWork\rimmandrake\conductor\codex_lane\RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS.attempt2_fix_first\patches.

### 6. `RIMMANDRAKE_CHECK_SCOPE_SOURCE_EVENT_EXISTS_FAKE_ID_OPENS`

**Why this one suits remote work:** A Codex attempt was STOPPED on this today; read the item's notes for the narrower 'what would pass' (no git reads; UNMEASURED when the ledger is unreadable).

**Ticket text:** designer_stage.py l.505-507 scope_source is only prefix-checked for OWNER:, so a nonexistent OWNER:999999 opens a capability's scope. The cited event must exist in the ledger (read it from origin/main as well as the working tree, so a sparse clone does not lose it). ONLY this one finding, minimal diff inside src/RimMandrake/rimflow/designer_stage.py, no refactor, no change to dispatcher.py or role_launch.py. Acceptance: one new case in selftest_designer_stage.py or selftest_designer_repin.py that fails on base and passes after; verify: python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_designer_repin selftest_designer_stage_land. Reusable failing cases exist in D:\ClaudeWork\rimmandrake\conductor\codex_lane\RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS.attempt2_fix_first\patches.

### 7. `RIMMANDRAKE_RESTART_GAME_AFTER_MAPDATA_TIMEOUT_THREE_JOBS_BURNED`

**Why this one suits remote work:** Python in the test-queue worker; build and prove it with a faked game process, never a real one.

**Ticket text:** worker.py keeps a game process whose quicktest map can never generate: after a job ends with readiness 'mapData' timed out (or Player.log shows 'Error in WorldGenStep' / a failed static constructor), stop the game so the next job loads a fresh one. 2026-11-14: one bad process (AlienRace.HarmonyPatches type initializer threw) failed three jobs in a row and braked the lane 57 min until rw_game.sh down by hand. Also: brake_release.py takes over 120 s a pass (per-mod fill_plan), so brake_release.json ran 38 min stale and steward.json missed its heartbeat twice. Acceptance test: not drafted (capped steward session); owed: a selftest_steve_worker case where a kept game answers the probe but the prior result note carries readiness 'mapData' and the worker must call rw_game.sh down before load, failing on the base commit.

## Coming shortly (not ready to take yet)

Three tickets from the owner's 2026-11-17 ruling "The judge refuses flaws, not polish"
(`design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md`) are being filed now, each with an
acceptance test watched failing: a finding rated polish must not block; a repaired gap closes without a claim form; the
four rules as judge prompt text with the two-look limit. The Conductor adds them here when they exist. The first two
are good remote work; the prompt-text one changes what the judge may refuse and is taken only on the owner's say.

## Deliberately NOT offered

- Anything C# (mod code needs the Windows build and a game load to prove).
- Anything that needs the live game, SteveDesktop, or the bridge.
- `RIMMANDRAKE_RERUN_TEST_TABLE_BEFORE_MOD_LANDING_CENSUS_SKIPPED`, `RIMMANDRAKE_OWN_RED_SUPPORTING_TEST_SIXTEEN_HOURS_UNSEEN`
  and the unsplit maturation-autonomy and designer-stage review findings: three build attempts on these failed review
  today; each needs a design or a split per finding before another build.
- Tickets on the six biome mods the owner holds (`src/RimMandrake/rimflow/mod_owner_hold.json`).
