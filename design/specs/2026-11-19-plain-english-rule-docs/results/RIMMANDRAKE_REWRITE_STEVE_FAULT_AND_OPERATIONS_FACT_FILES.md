# Result: `RIMMANDRAKE_REWRITE_STEVE_FAULT_AND_OPERATIONS_FACT_FILES`

Part of batch 15 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_UNDATED_FACT_FILES_DATED_ONES_STAY`). Files:
`infrastructure/state/facts/steve_fault_diagnosis.md`, `operations.md`, `README.md`. Run 2026-11-23.

Base: bc042932f16cb1781cc11564f359eb6d579e719c

Special rule: the fact files are homes for evidence. Each measurement stays. The STE target binds only the rule bullets.

## Scores

| measure | steve_fault_diagnosis.md | operations.md | README.md |
|---|---|---|---|
| bytes | 29,065 → 31,178 | 15,273 → 16,150 | 1,294 → 1,334 |
| words in linted prose | 4,189 → 4,495 | 2,161 → 2,262 | 211 → 221 |
| STE violations per 100 words | 3.22 → 2.31 | 3.79 → 1.72 | 2.84 → 2.26 |
| sentences over 20 words | 79 → 45 | 44 → 14 | 2 → 1 |
| flagged lines | 20 → 18 | 3 → 3 | 5 → 5 |
| lines a cold reader cannot act on (hand count, by the writer) | 7 → 0 that this run could resolve | 5 → 0 that this run could resolve | 1 → 0 |

The long sentences that stay:

- `steve_fault_diagnosis.md`, 45: one holds a command (line 8); 3 are headings that stay word for word; the others are a
  measurement that stays whole, or a bold lead that the lint joined with the next sentence.
- `operations.md`, 14: line 1 is the fixed HISTORY line (`era_text.py`); line 13 holds the owner's quote; line 133 is the
  code-review finding list, kept as one; the others are a measurement, a list of names, or a bold lead that the lint
  joined with the next sentence.
- `README.md`: a bold lead that the lint joined with the next sentence.

## The hand count

| file | old line | what a cold reader lacks | state after |
|---|---|---|---|
| steve | "RPCONTROL ok=1", "RPFAULT" | what the two log words mean | a "Terms" list, from `regprobe.c` |
| steve | "the watch", "the lane", "Steve" | which program, lane or machine | the "Terms" list |
| steve | "this boot", "today" (live catch) | which boot and day | one sentence under the heading |
| steve | "16 of 16 AVX holds" | whether right or wrong | "were wrong", from the class `upper_half_loss` on that line |
| steve | "by the 20-min rule" | what the rule is | gloss from `steve_lane_launch_audio.md`, line 6 of the record |
| steve | "(line 46)" | which text has that line | names the text and the new lead of the lines |
| steve | "this line read …" (one paragraph, six claims) | where each claim starts | one bullet for each claim |
| operations | runtime data, seat OOM, ops_watch, Steve lane, the retired Ralph loop (one paragraph each) | where each instruction starts | one sub-bullet for each claim or instruction |
| README | "a fact … append it here" | the subject of "it" | names the fact |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 2 (`rule_doc_lint.py keep`) | one planted copy of each file, two losses in each | exit 1 for all three; each planted loss listed |
| check 1 (`checkable.py compare`) | the same copies | exit 1 for `operations.md` (2 lost) and `README.md` (1 lost) |
| check 1 | the planted `steve_fault_diagnosis.md` copy (a count with no known unit, a window id) | exit 0: check 1 is blind to both losses; check 2 saw both |
| check 2 | the final files | 337, 220 and 11 spans; 0 lost |
| check 1 | the final files | 131, 111 and 4 items; 0 unfindable |
| `batch_done.py selftest` | — | GREEN: 0 failed (12 planted cases) |
| `selftest_retired_era_gone.py` (reads each fact file) | the new files | PASS |

No other test reads these files. The selftests that name `operations.md` read `src/RimMandrake/rimflow/roles/operations.md`.
Names of people: this run read the diff. No name was added or removed. "Steve" in these files is the machine; `sjlewis`
stays.

## What the meaning read found

Three fresh Opus readers (rm-judge), one file each, one at a time. They got the old and the new text and no reasoning.

`steve_fault_diagnosis.md`: 81 entries, 3 real findings and 10 marginal. All 13 repaired:

| first draft | why it was wrong | repair |
|---|---|---|
| Terms: `RPCONTROL` and `RPFAULT` "in the probe log" | the file calls `watch.log` the probe log | "in `regprobe.log`" |
| heat and the 2026-11-21 remark as bullets under "Not excluded" | heat is excluded | a paragraph after the list, as before |
| "The fault needs … mixer." split from its `[guess ~80%]` | the claim read as a fact | joined again |
| "In the boots where …" split from its `[guess ~70%]` | the tag covered less | joined again |
| "Inside a window the bad CPU wanders" as its own bullet | left the caveat of the line before | back in the bullet |
| "(line 46 at that date …)" | not proven | `git show` of commit `f8f0d1953d`: line 46 was that line in the text before the correction. The line now says so. |
| "The same holds on every CPU and day" | could read as each CPU was wrong | old clause restored |
| "A CPU acquires the fault … and holds" | the bad CPU wanders | passive form restored |
| "the tailnet container on the Desktop" | not in the old text | removed |
| "an active RimWorld" (and two like it) | "running" in the old text | restored |
| "BIOS fan curves control the cooling" | lost the change | "cooling falls back to" restored |
| "Only after that time does zero mean anything" | stronger | old sentence restored |
| "The table holds … 3898 cycles" | the table rows sum to 2326 cycles | old lead restored |

`operations.md`: 35 entries, 1 real finding and 5 marginal:

- Real: an added gloss of "held chain" did not cover Test Pilot chains (`gaps.py`). Removed.
- Marginal, repaired: the caveat "name the population" left the list of measurements; the four-file finding list is one
  block again, with "Check each" at its end; "unbudgeted" restored.
- Marginal, kept: "rimflow refuses `bench`" and "rimflow offers a `needs: bridge` item". The reader checked the first in
  `cli.py`. This run read `priority.py`, which makes the offer. So the actor is true.

`README.md`: 10 entries, 0 real and 2 marginal. Both repaired: "holding area" restored; the pointer instruction is back in
the sentence with its condition.

No reader read the repairs. Most repairs restore the old words.

## Conflicts (listed, not decided)

1. **Append or replace.** `README.md` says "Append. Never rewrite, reorder or prune" in `facts/`. `operations.md` says to
   replace a superseded line and never append a correction. This rewrite was ordered by the batch plan.
2. **Soak reader exit codes.** `steve_fault_diagnosis.md` lists exit 0 to 3. `soak_read.py` now also has exit 4 (the
   script exited and took no step).
3. **Vendor drivers in two states.** The sections above "Result" were written before the cause was known. The heading
   "Hypothesis under test: vendor software holding CPU state" is falsified by the section "Result". "The fault's shape"
   still lists a CPU defect and Hyper-V. The top section names the cure.
4. **`cli.py:255` and the dead mode words.** `operations.md` cites `cli.py:255` for the mode precedence. That line now holds
   other code; the precedence is in `_ctx`. The rule itself still holds. `interactive` and `autonomous` are "dead words"
   in the file, but `cli.py` still maps both to `belt`.
5. **Findings on deleted files.** `operations.md` says that four files are "still DIRTY". The deleted `relentless_live.py` and
   `relentless_game.py` were deleted with the retired era (commit `b28e0d6975`). Two of the four are left.
6. **The pulse checkout.** `operations.md` names `/mnt/d/ClaudeWork/rimmandrake/pulse-deploy`. The folder does not exist
   on 2026-11-23. The two debts of that entry look dead; this run did not close or file them.
7. **"The one live game is the bottleneck."** `CLAUDE.md` now says that there are several live games. The census is dated
   2026-10-26. The Ralph loop units are retired; none is loaded on 2026-11-23.
8. **Canary recovery.** `operations.md` gives `rw_game.sh down/init/up --wait`, then `testq.py resume`.
   `infrastructure/stevedesktop/RUNBOOK.md` gives `rw_game.sh down`, then `testq.py resume`.

## Could not determine

| line | question | who would know |
|---|---|---|
| "the pre/post split over all 3898 cycles" | the table rows sum to 2326 cycles; which cycles the 3898 adds | the author of the 2026-11-20 report (`REPORT.md`) |
| "Before tonight, 7 of 7 boots" and "13 of 13 boots before" | which boots are counted | the authors of `steve_driver_unload.md` and `steve_audio_default_test.md` |
| "BUILT 343, 496 and the verify backlog 521" | what population 496 is | the author of the 2026-10-26 census (`csuite\evidence.md`) |
| "Net +567 … (recomputed 609 …)" | which of the two to use | the same author |
| "The art judge sends 74% to REGEN" | which judge version | the same author |
| "Ralph C+sub" (the Ralph loop is retired), "TestPilot-plus", "v2/v3 world" | what each simulated design is | the author of `testpilot_sim.py` |

## What this run did not test

- No agent run read the new files and acted on them.
- No reader read the repairs.
- `check_refs.py` did not finish in 120 s; this run stopped it. Its answer is unknown.
- This run did not check the fact files' claims against the live SteveDesktop.

## Second read of the repairs

Run 2026-11-23, item `RIMMANDRAKE_REREAD_REWRITE_REPAIRS_NO_READER_SAW_THEM`. One fresh Opus reader that made none of
these edits read each repair, restored line and late edit against the base text and the lines that travel with it. SAME
means that a reader of the new line acts as a reader of the old line. A gloss reads SAME when its source says the same.
His quotes: a script compared each quote of three words or more in the base with today's text, whitespace ignored. No quote differs.

| file | line read | verdict | what was done |
|---|---|---|---|
| steve | "in `regprobe.log`" (2 terms) | SAME | none |
| steve | the heat paragraph after the list | SAME | none |
| steve | the `[guess ~80%]` claim joined | SAME | none |
| steve | the `[guess ~70%]` claim joined | SAME | none |
| steve | "Inside a window the bad CPU wanders …" in its bullet | SAME | none |
| steve | "(line 46 of the text before this correction …)" | SAME | none |
| steve | "on every CPU and day", restored | SAME | none |
| steve | the passive form of the fault, restored | SAME | none |
| steve | "the tailnet container", short form | SAME | none |
| steve | "running" restored in three lines | SAME | none |
| steve | "cooling falls back to BIOS fan curves" | SAME | none |
| steve | "Only then is zero meaningful." | SAME | none |
| steve | "over all 3898 cycles", old lead | SAME | none |
| operations | "held chains", gloss removed | SAME | none |
| operations | "name the population" in the list | SAME | none |
| operations | the four-file finding list, one block | SAME | none |
| operations | "unbudgeted" | SAME | none |
| operations | "rimflow refuses `bench`" | SAME | the reader of the batch checked `cli.py` |
| README | "holding area" | SAME | none |
| README | the pointer instruction in its sentence | SAME | none |
