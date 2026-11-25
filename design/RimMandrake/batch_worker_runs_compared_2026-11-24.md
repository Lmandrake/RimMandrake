# One worker, many tickets, one context: the two runs compared (2026-11-24)

Item: `RIMMANDRAKE_REPORT_BATCH_WORKER_RUNS_TWO_TRIED_NOW_COMPARE`. Written 2026-11-24, about 9:40 PM PST, for Mandrake.

His request (2026-11-24, about 9:03 PM PST): "I would like to request a report on our analysis of what happens when we
ask a worker to "take several tickets and just keep working to solve them all together, then even take them to the live
game and prove it out." We've done this twice recently now. Let's compare and report."

Tags: `[measured]` means read from a run record, a transcript, the ledger or git. `[guess ~N%]` is my estimate.
UNMEASURED means I could not read it, and the cause is named.

## 1. What happened, in five lines

1. The Gimme Some Slack close-out took 18 tickets in one Fable context and ended all 18 in 73 minutes for 6.44M weighted tokens. 6 were fixed, 6 were already fixed and 6 were dropped. 3 of its 4 code fixes were proven live, and his walk passed every station [measured].
2. The Pyrelands after-pass run did 5 parts of his order in one Opus context in 64 minutes for 2.35M weighted tokens. It proved its new pens step live (16 of 16 pens), but it closed no ticket. It read 7 tickets and found that his look settled none of them whole [measured].
3. The same week's one-ticket fix runs on those two mods spent 2.41M weighted tokens and 106 minutes per ticket fixed, and 1 of 9 fixes was proven live [measured].
4. The Slack batch was cheap partly because it skipped proofs. The pass after it took 3 more runs and 2.35M weighted tokens to add a red-first run, repair a gate check and run Stage 6 visit 4 [measured]. I cannot say how much of that the pipeline would have spent anyway (UNMEASURED).
5. Verdict: batch the open work of one mod in one run, with a reality sort first and the proofs inside the batch. Build `RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET`. Confidence ~70%.

## Which two runs, and how sure I am

- **Run A, the Slack close-out:** `RIMMANDRAKE_CLOSE_SLACK_VERSION_ALL_REAL_WORK_ONE_RUN_ONE_CONTEXT`, unit
  `rm-detached-bench-rimmandrake-close-slack-version-all-real-1795546503`, 10:55 AM to 12:08 PM PST. His order said "DO NOT
  treat each of them as an individual fix. Do batches with the same agent and the same context." This run is certain.
- **Run B, the Pyrelands settle:** `RIMMANDRAKE_SETTLE_PYRE_AFTER_PASS_REVIEW_SAVE_PENS_ART_KEPT`, unit
  `rm-detached-bench-rimmandrake-settle-pyre-after-pass-revie-1795577337`, 7:29 PM to 8:32 PM PST. Its brief says "You are
  one run with one context for all the parts below". It ended 31 minutes before your request. I am about 70% sure that
  this is the second run you mean [guess ~70%]. It is a poor match on "several tickets": it worked five parts of one
  order and closed no ticket.
- Other runs of the same shape on 2026-11-24, not reported in full:

| run (item) | shape | live game | weighted tokens | wall |
|---|---|---|---|---|
| `RIMMANDRAKE_FIX_SLACK_WALL_LAMPS_FACE_INTO_WALL_CORDS_STOP_AT_HOLE` | 1 ticket, 3 walk defects | yes, captures of 4 looks × 4 facings | 3,150,590 | 80 min |
| `RIMMANDRAKE_BATCH_KNOCKBACK_SCENES_FIFTY_FIVE_SETTINGS_RESETS` | test harness, 1 ticket, Sonnet, 2 sessions | live rerun UNRUN | 351,330 | 40 min |
| `RIMMANDRAKE_FEED_CODEX_AGAIN_STEVEN_BURNS_TWICE_THE_PACE` | 4 pipeline tickets through Codex | no game | 1,134,909 | 79 min |
| `RIMMANDRAKE_WIRE_PLAN_READERS_NOBODY_READS_BURN_MODE_YET` | 7 parts of pipeline machinery | timers live, no game | 8,195,762 | 140 min |

All figures in that table are [measured] from the run records in `D:\ClaudeWork\rimmandrake\dispatcher\detached\`.

## 2. Side by side

The baseline is the seven Opus one-ticket fix runs on Gimme Some Slack and Pyrelands, 2026-11-22 to 2026-11-24, that
changed code:

- `RIMMANDRAKE_SMOOTH_SLACK_GROUND_CORD_KINKS_AT_STATION_THREE`
- `RIMMANDRAKE_WIDEN_SLACK_STYLE_BUTTON_REACH_ITEM_RUN_OR_WHOLE_MAP`
- `RIMMANDRAKE_FINISH_SLACK_ICON_LAMP_CHECKS_CAPPED_AT_HALF` (2 sessions; the first stopped at its spend cap)
- `RIMMANDRAKE_STRAIGHTEN_SLACK_CORD_WHERE_IT_LEAVES_WALL_PLUG_HE_SAW_IT_LIVE`
- `RIMMANDRAKE_FIX_SLACK_WALL_LAMPS_FACE_INTO_WALL_CORDS_STOP_AT_HOLE`
- `RIMMANDRAKE_SPARE_PYRE_FURNACE_BARN_ROOF_FROM_TITAN_WAKE`
- `RIMMANDRAKE_WIDEN_PYRE_LONE_FIRE_INTO_A_FRONT`

Two of those runs closed a second, related ticket as well. The Conductor's earlier figure of "830k weighted tokens and
40 min per ticket" names no runs, so I could not check it and do not use it.

| line | A: Slack close-out | B: Pyrelands settle | baseline: 7 one-ticket runs |
|---|---|---|---|
| model | Fable 5.2, with 2 Opus helpers (art judge, fresh reader) | Opus 5.5, with 1 Opus builder and 1 Sonnet search | Opus 5.5 |
| brief | his whole order, an 18-line work list, "reality first, then batches by shared code, one live pass, a fast walk" | his order in 5 parts: review save, pens step, walk-brief rule, art keeps, next-version lines | one ticket each |
| tickets in | 18 | 7 read (art tickets of the 16 kinds) | 7 launched; 9 fixed (8 closed, 1 still open) |
| fixed and proven live | 3 (auto-link triangle, pole lamp cord end, battery looks) | 0 tickets; the new pens step 16 of 16 live | 1 of 9 (wall lamps, by captures) |
| fixed, not proven live | 1 (ship-to-ground snap; flight UNRUN) and 2 text fixes that need no game | 1 small fix (VEF type guard), live check UNRUN with its command | 8 of 9 (offline only) |
| found stale, closed | 6 (already fixed by earlier commits) | 0 | 0 |
| dropped with a reason | 6 | 0 | 0 |
| left open | 0 | 7, each with its reason | 1 (wall lamps: open today, waits on a fresh read) |
| work done that had no ticket | 4 polish and next-version lines fixed (fallen-wire corners, Futuristic glow, menu count, a stale line) | 5 next-version lines written, 1 polish line | none recorded |
| wall time | 73 min | 64 min | 15.9 h in total, 106 min per ticket fixed |
| weighted tokens | 6,440,338 | 2,350,668 | 21,710,992 in total, 2.41M per ticket fixed |
| per ticket ended | 0.36M and 4 min | no ticket ended | 2.41M and 106 min per ticket fixed |
| resumes, cap stops, deaths | 0, 0, 0 | 0, 0, 0 | 1 cap stop in 8 sessions |
| context at start, at half, at end | 81k, 320k, 480k; no compaction | 82k, 208k, 301k; no compaction | not read |
| PROGRESS notes written | 0 in 73 min | 5, one after each part | not read |
| commits | 2 code commits (80 files) and 1 ledger commit with 15 writes | 5 commits, one for each part | not counted |
| what it proved live | 6 of 6 live reads PASS on ArchBig, with captures | pens 16 of 16 on ArchSmall; review save byte-equal on ArchSmall, ArchBig and storage | 1 of 9 |
| faults that a later run or his walk found | 1 wrong gate check (gate O6 did not know battery looks; repaired at `1cc2c1b3aa`). His walk found 0 faults | UNMEASURED: nothing has read this run's work yet | 0 reopened of 8 closed |
| step-ins by the Conductor or by him | the Conductor fixed a red Stage 6 block check after the run. The red came before the run's commits | 0 | not read |
| cost after the run, to the version pass | 3 runs to record the pass and tag v0.2.0: 2,350,729 weighted tokens, 151 min | none owed (version passed before the run) | each offline fix still owes a Stage 6 row |

Sources: `D:\ClaudeWork\rimmandrake\dispatcher\detached\<unit>.json` and `.out.json` (tokens, wall time, turns, helpers);
the two session transcripts (context per request); the ledger shards in
`D:\Luke\dev\RimMandrake\infrastructure\state\ledger\events\` (closes and drops by `role_unit`); git.

Notes on the table:

- **Model price.** Fable costs about twice Opus for each token in `MODEL_PRICES`. On Opus, run A's work would read
  lower, but I cannot say by how much. Fable may also take fewer turns.
- **Unlike work.** Run A was many small visual faults in shared code. Run B was mostly new tooling and records. The
  baseline runs were harder single faults, and one of them took 4.9 h. So the per-ticket figures are not a clean
  experiment.

## 3. What worked, what failed, what was the same

**Patterns (seen in both runs):**

- **Each run finished in one session.** Neither run died, resumed, hit its cap or compacted. Context grew about
  linearly, to 480k and 301k. Both stayed far below the 1M window.
- **Each run proved its live part in the same run, on a free game.** Run A used ArchBig and run B used ArchSmall. Each
  run named the one thing that it left UNRUN, with the command.
- **"One agent" still meant helpers.** Run A started an art judge and a fresh reader, as its brief allowed. Run B
  started a builder and a search. Neither run did the work alone, and neither run should have: an independent judge
  stays independent.

**Anecdotes (seen in one run only):**

- **The reality sort paid for itself (run A only).** 12 of 18 tickets needed no code: 6 were already fixed and 6 were
  not worth the touch. Run A closed 5 of the stale tickets in its first 15 minutes, and the rest at its end. In run B the sort found no ticket to close. The value
  of the sort depends on how stale the list is.
- **His walk passed at the first try (run A only).** The morning walk of 0.2.0 failed at stations 33 and 12. The walk
  after run A passed every station.
- **Skipped proofs came back as cost (run A only).** Run A wrote the snap check with the fix and did not run it red
  first. It did no Stage 6 rows. Its gate check did not know the battery looks. The pass after it took 3 runs. One of
  those runs was cut by a Conductor stop order. Another started fresh, because the earlier context was over 150k. Run B
  ran its checks red first (an ImportError, then 4 planted faults), and so it owes nothing after.
- **No progress notes (run A only).** Run A wrote no `PROGRESS:` note in 73 minutes. If it had died at minute 60, a
  fresh session would have had only the brief. Run B wrote a note after each part.

**What failed:**

- Run A did not look at one capture (station 36), and it has no final shot of stations 32 and 33. Its brief said to
  look at every capture.
- Run B closed no ticket, though his words were "Mark it, close tickets". The run was right not to close them: each of
  the 7 asks for something that his look did not cover. But "close tickets" was not the result.

## 4. What the pipeline would need to do this natively

The open ticket `RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET` asks for one command.
The command names a mod, checks each ticket for reality, closes the stale ones and launches one run with the rest. The
two runs support that design, with four additions:

1. **A reality sort as a program, before the launch.** Run A did most of the sort by hand, in its first 15 minutes, with
   `git log` and the existing checks. A program can close the tickets whose fixing commit and green check exist, at no
   token cost. This is the ticket's acceptance test already.
2. **Proofs inside the batch, not after it.** Each fix in the batch still runs its check red first and green after.
   One fresh reader reads the batch's commits once, at the end, not once for each fix. The Stage 6 rows that the
   changed code touches run in the batch's one live pass. Run A shows the cost of the alternative: 3 more runs and
   2.35M weighted tokens.
3. **A note and a publish after each batch.** The danger is that one death loses more work than in a one-ticket run.
   The guard is the one that run B used: a `PROGRESS:` note and a publish after each part. Then a death loses at most
   one part. This is a guard on progress, not a limit on size.
4. **A brief section for the live pass.** The section names the free game, the one live pass and the walk staging.
   Both runs did this well from a hand-written brief. Today no template writes it.

Risks:

- **Context growth.** 480k at the end of 18 tickets is about half the window [measured]. A list of 40 tickets could
  reach the window [guess ~50%]. Split by shared code before the list gets that long. Do not split by a cap.
- **One death loses more.** No batch run has died yet (0 of 2), so the size of this risk is UNMEASURED. Item 3 above is
  the guard.
- **Reality checks done badly.** A sort that closes a real fault as "already fixed" hides it. In run A, his walk found
  no such case. That is one run, not proof.
- **Proofs skipped under "lightning mode".** Run A's brief told it not to perform ceremony, and it skipped the red-first
  runs. The pipeline must tell ceremony (forms, stamps, a plan file) from a proof (a red-first run, a live read). The
  batch drops the first and keeps the second.

## 5. Recommendation

**Build the native batch now. Make the proofs part of the batch.** Confidence ~70% [guess ~70%] that it ends a mod's
open work for fewer weighted tokens and less wall time per ticket than one run per ticket, counted all the way to the
version pass.

Why it is not higher:

- Run A ran on Fable and the baseline on Opus.
- 12 of run A's 18 tickets were stale or dropped.
- Run A's after-cost is real, and I cannot split it from the ordinary cost of a pass.
- Run B is a poor second example, because it closed no tickets.

My rating of the idea: it is not new. It is how a person works through a bug list. But for this pipeline it is a large
change, because the pipeline was built on "one gap, one fixer". The real gain in run A came from two things: the reality
sort, and reading the shared code once for many fixes. Both gains are plain and explain the numbers. The weak point is
that a batch run feels finished before its proofs exist.

**One measurement that would change the recommendation:** one Opus batch run on a mod's open list of at least 10 real
tickets, with red-first checks, a fresh reader and the touched Stage 6 rows inside the run. Count its weighted tokens and
wall time to the version tag, and compare with the per-ticket runs of the same week, also counted to the tag. If the
batch's cost per ticket at the tag is not lower, the gain was only the skipped proofs. Then the recommendation becomes:
keep one run per ticket, and add only the reality sort.

## Side findings (one line each, no ticket)

- `RIMMANDRAKE_FIX_SLACK_WALL_LAMPS_FACE_INTO_WALL_CORDS_STOP_AT_HOLE` is still `doing` and waits on a fresh read. His
  12:19 PM walk passed stations 33 and 12, which hold its three fixes [measured].
- Run B's part-4 `PROGRESS:` note cites commit `2172908674`. No commit has that hash. The real commit is `217290867c`
  [measured].
- Each run's clone was bundled as "work no remote had". Neither bundle is in
  `/home/mandrake/rm/relentless/store/orphans/bundles/` now, so what they held is UNMEASURED. Every detached run of the
  day writes this note, so the note does not come from batching.
