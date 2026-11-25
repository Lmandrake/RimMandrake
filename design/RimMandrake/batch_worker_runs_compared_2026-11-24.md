# One worker, many tickets, one context: the batch runs compared (2026-11-24)

Items: `RIMMANDRAKE_REPORT_BATCH_WORKER_RUNS_TWO_TRIED_NOW_COMPARE` (first version, written 2026-11-24 about 9:25 PM
PST) and `RIMMANDRAKE_ADD_KNOCKBACK_SWEEP_TO_BATCH_REPORT_OWNER_RECALLED` (this version, written about 9:45 PM PST). For
Mandrake.

His request (2026-11-24, about 9:03 PM PST): "I would like to request a report on our analysis of what happens when we
ask a worker to "take several tickets and just keep working to solve them all together, then even take them to the live
game and prove it out." We've done this twice recently now. Let's compare and report."
His correction (about 9:35 PM PST): "I thought Explosive Knockback we did this experiment too".

**What the first version missed, and why.** The first version missed the Explosive Knockback ticket sweep of 2026-11-22.
It missed the sweep for three reasons:
- My census of run records started at 4:00 PM PST on 2026-11-22, and the sweep started at 3:06 PM.
- I searched his words for "batch", "together" and "same context". His words were "Clean house", "Find. Adjudicate.
  Eradicate the stale."
- The sweep did not touch the game in its own run, so it did not pass my "taken to the live game" filter.

Tags: `[measured]` means read from a run record, a transcript, the ledger or git. `[guess ~N%]` is my estimate.
UNMEASURED means I could not read it, and the cause is named.

## 1. What happened, in five lines

1. **The experiment is two runs.** The first is the Explosive Knockback ticket sweep (2026-11-22, one Opus context, 34 tickets). The second is the Gimme Some Slack 0.2.0 close-out (2026-11-24, one Fable context, 18 tickets). The Pyrelands after-pass run stays in the table as a contrast only: it closed no ticket.
2. **The batch runs were cheap per ticket.** Each run ended its list in one session, with no death and no compaction. The Knockback sweep ended 30 of 34 tickets in 109 min for 2.40M weighted tokens. The Slack close-out ended 18 of 18 in 73 min for 6.44M [measured].
3. **Most tickets needed no code, in both runs.** In the Knockback sweep, 22 of 34 were done, stale or not worth the touch. In the Slack close-out, 12 of 18 were [measured]. This is now a pattern.
4. **The live proof was the expensive part, in both runs.** The Knockback sweep took nothing to the game. Its road from the sweep to the pass took 20 more runs, 24.1M weighted tokens and 47 h. The Slack close-out proved 3 of 4 fixes live, but recording its pass took 3 more runs and 2.35M weighted tokens [measured].
5. **The verdict is the same as before, with a firmer first half.** Build the native batch with a program-run reality sort first (now ~85%). Keep the fixes and their proofs in one run (still ~70%; the Knockback sweep adds no evidence for or against this half).

## Which runs, and how sure I am

- **Run A, the Slack close-out:** `RIMMANDRAKE_CLOSE_SLACK_VERSION_ALL_REAL_WORK_ONE_RUN_ONE_CONTEXT`, unit
  `rm-detached-bench-rimmandrake-close-slack-version-all-real-1795546503`, 2026-11-24 10:55 AM to 12:08 PM PST.
  - His order: "DO NOT treat each of them as an individual fix. Do batches with the same agent and the same context."
  - Certain.
- **Run B, the Knockback sweep:** `RIMMANDRAKE_SWEEP_KNOCKBACK_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE`, unit
  `rm-detached-bench-rimmandrake-sweep-knockback-tickets-merg-1795388777`, 2026-11-22 3:06 PM to 4:55 PM PST.
  - His order (2026-11-22 about 3:02 PM PST): "Let's clean up all this crap. Please do that now. Find. Adjudicate.
    Eradicate the stale. Merge the modern. Apply/build them RIGHT NOW if they're valuable, after adjudicating if they
    are part of the current or next version. Clean house on advancing mods please!"
  - About 85% sure that this is the run he means [guess ~85%]. He named the mod, and no other Knockback run took many
    tickets in one context.
  - His order made five sweep runs at once: FlowWorks, HugeThings, Explosive Knockback, Pyrelands and Gimme Some Slack.
    They are listed below.
  - Its brief ordered "do not switch the mod on, launch its stages or run a visit". So the live game came after the run,
    through the pipeline. The "then the live game" half of the experiment is the road to the 0.1.0 pass on 2026-11-24
    at 3:43 PM PST, not this run.
- **Run C, the Pyrelands settle (a contrast, not the experiment):** `RIMMANDRAKE_SETTLE_PYRE_AFTER_PASS_REVIEW_SAVE_PENS_ART_KEPT`,
  2026-11-24 7:29 PM to 8:32 PM PST.
  - It worked five parts of one order and closed no ticket.
  - It stays in the table for one reason: it is the one run that kept its proofs (red first, then live) inside the
    batch.

Other one-context runs of the same week, not reported in full:

| run (item) | shape | live game in the run | weighted tokens | wall |
|---|---|---|---|---|
| `RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE` | sweep from the same order, 3 fixes built | not read | 10,663,733 | 142 min |
| `RIMMANDRAKE_SWEEP_PYRELANDS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE` | sweep from the same order, 53 tickets | not read | 2,832,299 | 77 min |
| `RIMMANDRAKE_SWEEP_SLACK_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE` | sweep from the same order, nothing built | no | 2,286,068 | 42 min |
| `RIMMANDRAKE_SWEEP_HUGETHINGS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE` | sweep from the same order, 26 tickets to 7, nothing built | no | 1,699,093 | 84 min |
| `RIMMANDRAKE_FIX_SLACK_WALL_LAMPS_FACE_INTO_WALL_CORDS_STOP_AT_HOLE` | 1 ticket, 3 walk defects | yes, captures | 3,150,590 | 80 min |
| `RIMMANDRAKE_BATCH_KNOCKBACK_SCENES_FIFTY_FIVE_SETTINGS_RESETS` | test harness, 1 ticket, Sonnet, 2 sessions | UNRUN | 351,330 | 40 min |
| `RIMMANDRAKE_FEED_CODEX_AGAIN_STEVEN_BURNS_TWICE_THE_PACE` | 4 pipeline tickets through Codex | no game | 1,134,909 | 79 min |

All figures in that table are [measured] from the run records in `D:\ClaudeWork\rimmandrake\dispatcher\detached\`.

## 2. Side by side

**The baseline** is the eight Opus one-ticket fix runs on Gimme Some Slack, Pyrelands and Explosive Knockback,
2026-11-22 to 2026-11-24, that changed code:

- `RIMMANDRAKE_SMOOTH_SLACK_GROUND_CORD_KINKS_AT_STATION_THREE`
- `RIMMANDRAKE_WIDEN_SLACK_STYLE_BUTTON_REACH_ITEM_RUN_OR_WHOLE_MAP`
- `RIMMANDRAKE_FINISH_SLACK_ICON_LAMP_CHECKS_CAPPED_AT_HALF` (2 sessions; the first stopped at its spend cap)
- `RIMMANDRAKE_STRAIGHTEN_SLACK_CORD_WHERE_IT_LEAVES_WALL_PLUG_HE_SAW_IT_LIVE`
- `RIMMANDRAKE_FIX_SLACK_WALL_LAMPS_FACE_INTO_WALL_CORDS_STOP_AT_HOLE`
- `RIMMANDRAKE_SPARE_PYRE_FURNACE_BARN_ROOF_FROM_TITAN_WAKE`
- `RIMMANDRAKE_WIDEN_PYRE_LONE_FIRE_INTO_A_FRONT`
- `RIMMANDRAKE_STOP_GAS_SHOVE_PAST_WALL_CORNER_UNSEEN`, added in this version. It is the one current-version Knockback
  fault that the sweep kept and that a later run fixed.

Two of those runs closed a second, related ticket as well. The Conductor's earlier figure of "830k weighted tokens and
40 min per ticket" names no runs, so I could not check it and do not use it.

| line | A: Slack close-out | B: Knockback sweep | C: Pyrelands settle (contrast) | baseline: 8 one-ticket runs |
|---|---|---|---|---|
| model | Fable 5.2, with 2 Opus helpers (art judge, fresh reader) | Opus 5.5, no helpers | Opus 5.5, with 1 Opus builder and 1 Sonnet search | Opus 5.5 |
| brief | his whole order, an 18-line work list: reality first, then batches by shared code, one live pass, a fast walk | his order: find, class, drop the stale, merge the rest, build the valuable offline; no game, no stage move | his order in 5 parts | one ticket each |
| tickets in | 18 | 34 (82 open items name the mod; 34 are about it) | 7 read (art tickets of the 16 kinds) | 8 launched; 10 fixed (9 closed, 1 still open) |
| fixed and proven live | 3 (auto-link triangle, pole lamp cord end, battery looks) | 0 | 0 tickets; the new pens step 16 of 16 live | 2 of 10 (wall lamps by captures; gas corner on ArchSmall) |
| fixed, not proven live | 1 (ship-to-ground snap; flight UNRUN) and 2 text fixes that need no game | 2, both test-side (a selftest and the fuzz mutants); no mod code changed | 1 small fix (VEF type guard), live UNRUN with its command | 8 of 10 (offline only) |
| found done or stale, closed | 6 | 16 (15 done, 1 stale) | 0 | 0 |
| dropped as not worth the touch | 6 | 6 | 0 | 0 |
| merged | 0 | 6 tickets into 2 new modern tickets | 0 | 0 |
| left open | 0 | 3 for 0.1.0, 3 for the next version | 7, each with its reason | 1 (wall lamps: open today, waits on a fresh read) |
| what became of the kept 0.1.0 tickets | none kept | 1 fixed live by a later run; 2 dropped later as not worth the touch | not applicable | not applicable |
| work done that had no ticket | 4 polish and next-version lines fixed | none | 5 next-version lines, 1 polish line | none recorded |
| wall time | 73 min | 109 min | 64 min | 16.9 h in total, 102 min per ticket fixed |
| weighted tokens | 6,440,338 | 2,396,327 | 2,350,668 | 22,725,336 in total, 2.27M per ticket fixed |
| per ticket ended | 0.36M and 4 min | 0.08M and 3.6 min (30 ended) | no ticket ended | 2.27M and 102 min per ticket fixed |
| resumes, cap stops, deaths | 0, 0, 0 | 0, 0 (no cap set), 0 | 0, 0, 0 | 1 cap stop in 9 sessions |
| context at start, at half, at end | 81k, 320k, 480k; no compaction | 68k, 246k, 324k; no compaction | 82k, 208k, 301k; no compaction | not read |
| PROGRESS notes written | 0 in 73 min | 1 in 109 min | 5, one after each part | not read |
| commits | 2 code commits (80 files) and 1 ledger commit with 15 writes | 2 test commits, 1 sweep record (`d33f515241`), ledger closes | 5 commits, one for each part | not counted |
| what it proved live | 6 of 6 live reads PASS on ArchBig, with captures | nothing; no game was touched, by its brief | pens 16 of 16 on ArchSmall; review save byte-equal on ArchSmall, ArchBig and storage | 2 of 10 |
| faults that a later run or his walk found | 1 wrong gate check (gate O6 did not know battery looks; repaired at `1cc2c1b3aa`). His walk found 0 faults | visit 4: one blast-spared check FAIL. His look of 2026-11-23: gun lockers show their guns, tox gas at station 10, pit covers broken. His walk of 2026-11-24: PASS, "Very fun!". Whether any of these was a ticket that the sweep dropped is UNMEASURED | UNMEASURED: nothing has read this run's work yet | 0 reopened of 9 closed |
| step-ins by the Conductor or by him | the Conductor fixed a red Stage 6 block check after the run. The red came before the run's commits | 1 card to him (where thrown goods land in a pit), answered the same evening; the Conductor switched the mod on on his word. At least 8 pipeline-defect tickets that name the mod were filed on the road to the pass | 0 | not read |
| cost after the run, to the version pass | 3 runs to record the pass and tag v0.2.0: 2,350,729 weighted tokens, 151 min | 20 runs: 24,102,543 weighted tokens, 22.9 h of run time, 47 h by the clock. Not counted: 1 killed judge run (its record holds no tokens) and the pass record written in the Conductor window | none owed (the version passed before the run) | each offline fix still owes a Stage 6 row |

Sources:
- `D:\ClaudeWork\rimmandrake\dispatcher\detached\<unit>.json` and `.out.json`: tokens, wall time, turns and helpers.
- The three session transcripts: context per request.
- The ledger shards in `D:\Luke\dev\RimMandrake\infrastructure\state\ledger\events\`: closes, drops and supersedes by
  `role_unit`, and the tickets filed between the sweep and the pass.
- Git: commits and tags.
- The Knockback sweep record: `D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\ticket_sweep_2026-11-22.md`.

Notes on the table:

- **Model price.** Fable costs about twice Opus for each token in `MODEL_PRICES`. On Opus, run A's work would read
  lower, but I cannot say by how much.
- **The three runs did different kinds of work.** Run B mostly classified tickets. Run A mostly fixed them. Run C
  built new tooling. So run B's 0.08M per ticket ended is the price of a sort, not of a fix.
- **What run B's after-cost holds.** The 24.1M weighted tokens after the sweep are mostly the mod's ordinary stages:
  blind cycle 6, in-game visits 4 to 6, the steward and the walk save. How much the sweep saved or added there is
  UNMEASURED.

## 3. What worked, what failed, what was the same

A pattern now needs to show in at least two of the batch runs A, B and C. Something seen in one run is an anecdote.

**Patterns:**

- **Each run finished in one session (A, B and C).** No run died, resumed, hit a cap or compacted. Context grew about
  linearly, to between 301k and 480k. All three stayed far below the 1M window.
- **The reality sort paid for itself (A and B).** In run A, 12 of 18 tickets needed no code. In run B, 22 of 34 did
  not (15 done, 1 stale, 6 not worth the touch), and 6 more merged into 2 [measured]. On these mods, about two thirds of
  an open list is already settled.
- **A kept ticket is still not proven real (B, and A by its own sort).** Run B kept 3 tickets for 0.1.0. Later runs
  dropped 2 of them as not worth the touch, and only 1 was a real fault (the gas corner). So a sort keeps too much. The
  live game or his walk is what settles the rest.
- **The live part cost more than the batch (A and B).** Run A's pass took 2.35M more weighted tokens. Run B's road to
  the pass took 24.1M. The batch itself cost 6.44M and 2.40M. Run C is the exception, because it had no pass to reach.
- **Progress notes were sparse unless the brief asked for one per part (A and B).** Run A wrote 0 `PROGRESS:` notes in
  73 min, and run B wrote 1 in 109 min. If either had died late, a fresh session would have had only the brief. Run C's
  brief asked for a note after each part, and it wrote 5.

**Anecdotes (one run only):**

- **Skipped proofs came back as cost (A only).** Run A's brief said "do NOT perform ceremony". The run did not run its
  new snap check red first, ran no Stage 6 rows, and left one gate check wrong. Runs B and C ran their checks red first.
  So the skip came from run A's brief, not from batching.
- **His walk passed at the first try (A only).** For Knockback, his partial look of 2026-11-23 found three things. His
  walk of 2026-11-24 passed after visits 4 to 6.
- **The batch was alone in the mod (B only).** Run B started no helper. Runs A and C each started two.

**What failed:**

- Run A did not look at one capture (station 36), and it has no final shot of stations 32 and 33.
- Run B's sweep left the mod switched off. The Conductor had to switch it on before any live proof could start, and the
  road then met at least 8 pipeline defects.
- Run C closed no ticket, though his words were "Mark it, close tickets". The run was right not to close them, but
  "close tickets" was not the result.

## 4. What the pipeline would need to do this natively

The open ticket `RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET` asks for one command.
The command names a mod, checks each ticket for reality, closes the stale ones and launches one run with the rest. The
three runs support that design, with five additions:

1. **A reality sort as a program, before the launch.** Runs A and B did the sort by hand. A program can close the
   tickets whose fixing commit and green check exist, at no token cost. This is the ticket's acceptance test already.
2. **The fix run follows the sort at once, and takes the kept list to the game.** Run B stopped at the sort by its brief.
   Its kept tickets then waited for the pipeline. Two of the three turned out not to be real. One live pass in the
   batch run would have settled all three.
3. **Proofs inside the batch, not after it.** Each fix runs its check red first and green after. One fresh reader
   reads the batch's commits once, at the end. The Stage 6 rows that the changed code touches run in the batch's one
   live pass. Run C did this. Run A did not, and paid 3 more runs.
4. **A note and a publish after each part.** Without this guard, one death loses the whole context, and runs A and B
   wrote almost no notes. Run C shows the guard: a `PROGRESS:` note and a publish after each part. This is a guard on
   progress, not a limit on size.
5. **A brief section for the live pass.** The section names the free game, the one live pass and the walk staging.
   Runs A and C did this well from hand-written briefs. Today no template writes it.

Risks:

- **Context growth.** 480k at the end of 18 tickets is about half the window [measured]. A list of 40 tickets that are
  all fixed, not only sorted, could reach the window [guess ~50%]. Split by shared code before the list gets that long.
  Do not split by a cap.
- **One death loses more.** No batch run has died yet (0 of 3), so the size of this risk is UNMEASURED. Item 4 above is
  the guard.
- **Reality checks done badly.** A sort can close a real fault as "done", and that hides the fault. In run A, his walk
  found no such case. For run B, whether any later fault was a ticket that the sweep dropped is UNMEASURED.
- **Proofs skipped under "lightning mode".** Run A's brief told it not to perform ceremony, and the run skipped its
  red-first runs. The pipeline must tell ceremony (forms, stamps, a plan file) from a proof (a red-first run, a live
  read). A batch drops the ceremony and keeps the proofs.

## 5. Recommendation

**Build the native batch now. Put the reality sort first, and keep the fixes and their proofs in the same run.**

- **The reality sort first: ~85% [guess ~85%], up from the first version's ~70%.** The sort is now seen in two batch
  runs on two mods, and in both, most of the list needed no code. A program can do most of the sort for no tokens.
- **The fixes and proofs in one run: ~70% [guess ~70%], unchanged.** Run B adds no evidence for or against it, because
  run B fixed nothing in the mod and touched no game. The evidence is still run A (cheap per fix, but it skipped proofs)
  and run C (proofs inside, but no tickets).
- **The direction does not change.** The plan gains one step from run B: the kept list goes to the game in the same run,
  so that the game settles the tickets that a sort keeps by mistake.

My rating of the idea: it is not new. It is how a person works through a bug list. But for this pipeline it is a large
change, because the pipeline was built on "one gap, one fixer". The gains are plain and explain the numbers:
- reading the shared code once for many fixes (run A);
- finding that two thirds of a list is already settled (runs A and B).

The weak point also shows in two runs: a batch run feels finished before its proofs exist.

**One measurement that would change the recommendation:** one Opus batch run on a mod's open list of at least 10 real
tickets. The run does the sort, the fixes, the red-first checks, a fresh reader and the touched Stage 6 rows. Count its
weighted tokens and wall time up to the version tag. Then compare with the per-ticket runs of the same week, also
counted to the tag. If the batch's cost per ticket at the tag is not lower, the gain was only the sort and the skipped
proofs. Then the recommendation becomes: keep one run per ticket, and add only the program-run sort.

## Side findings (one line each, no ticket)

- `RIMMANDRAKE_FIX_SLACK_WALL_LAMPS_FACE_INTO_WALL_CORDS_STOP_AT_HOLE` is still `doing` and waits on a fresh read. His
  12:19 PM walk passed stations 33 and 12, which hold its three fixes [measured].
- Run C's part-4 `PROGRESS:` note cites commit `2172908674`. No commit has that hash. The real commit is `217290867c`
  [measured].
- Each run's clone was bundled as "work no remote had". Neither of the two bundles that I checked (runs A and C) is in
  `/home/mandrake/rm/relentless/store/orphans/bundles/` now, so what they held is UNMEASURED. Every detached run of the
  week writes this note, so the note does not come from batching.
