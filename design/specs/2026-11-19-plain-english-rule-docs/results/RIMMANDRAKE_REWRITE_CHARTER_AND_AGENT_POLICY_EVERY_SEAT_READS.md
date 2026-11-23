# Result: `RIMMANDRAKE_REWRITE_CHARTER_AND_AGENT_POLICY_EVERY_SEAT_READS`

Batch 3 of `batch_plan.md`. Base commit `d4d5729aeb`. Files: `infrastructure/agents/CHARTER.md`,
`infrastructure/agents/Agent_Policy.md`. Run on 2026-11-19 by a detached BENCH helper (Opus 5.5 writer).

## Scores

| measure | CHARTER before | CHARTER after | Agent_Policy before | Agent_Policy after |
|---|---|---|---|---|
| bytes | 15,405 | 16,963 | 21,688 | 23,026 |
| words in linted prose | 2,193 | 2,489 | 2,756 | 2,915 |
| STE violations per 100 words | 4.10 | 2.13 | 4.32 | 2.44 |
| sentences over 20 words | 37 | 8 | 50 | 17 |
| flagged lines (mechanical) | 8 | 8 | 10 | 7 |
| lines that a cold reader cannot act on (hand count, by the writer) | 15 | 4 | 12 | 5 |

Each heading stays word for word. `.claude/hooks/bench_mode.py` prints the `## Posture` section verbatim, and the
heading stays. The quoted ladder block, each owner quote and the escalation clause (a prompt text that other prompts
copy) stay word for word.

### The long sentences that stay

CHARTER (8):

- owner quote: line 22 ("See it, fix it, then"), line 165 (the pre-Maturation limit), line 213 (the testing policy);
- two short sentences that the lint joined at a bold lead: lines 76, 92, 138, 208;
- a sentence that holds a command: line 229 (the Test Pilot slogan, kept word for word).

Agent_Policy (17):

- two short sentences that the lint joined at a bold lead: lines 106, 125, 137, 139, 152, 180, 203, 226, 235, 252,
  264, 271, 274, 288, 292;
- a sentence that holds a command: line 255 (the transcript slogan, kept word for word);
- a list that the lint reads as one sentence: line 80 (the Opus list, semicolon-separated).

## Hand count

### CHARTER

| old line | what a cold reader lacks | state after |
|---|---|---|
| "He opts work *into* rigor ..., never out of it" | what "never out of it" asks the reader to do | left; could not determine |
| "Batch questions; write the Player.log strings that will decide each before launch" | what "each" is | names "each question" |
| "sweep dependents" (expensive list item 3) | which dependents, and what a sweep does | left; could not determine |
| "Our own proven-unread, pushed leftovers: archive, delete, digest" | the condition and the three acts | rewritten as a condition and three acts |
| "spec/verify prose only here" | where "here" is | "Only items on this list get spec/verify prose" |
| "`SUBJECT_INTENT_TWIST · lane · the ask`" | what a lane is | left; could not determine |
| "his words in CLAUDE.md" (Evidence-for-Ask) | a false pointer (see "Errors fixed") | fixed |
| "a §2 hold stays his with its evidence on the ask" | the subject | rewritten |
| "Stuck → GPT early" | the act | "When you are stuck, go to GPT early" |
| "`broadcast.py` is his, with that single carve-out" | what the carve-out is | names it, from `standing_rulings.md` and CLAUDE.md |
| "never flyer flight" (bridge parenthesis) | the act | "Never fly a flyer on the bridge" |
| "On a seat with a restart the phrase fires it" | what "it" is | names the restart |
| "it REFUSES rather than guess", "it lands `conversations/`" | what "it" is | names `handoff.py` |
| "never for one more generation just to re-check" | what a generation is | left; could not determine |
| "Ownership gates work in flight (...), never the three terminal verbs" | the subject of the second half | names "Ownership" twice |

### Agent_Policy

| old line | what a cold reader lacks | state after |
|---|---|---|
| "you are on row 3" (twice) | a false pointer (see "Errors fixed") | fixed |
| "TWILIGHT_BOTTOM_CAST_1" | a legacy id with no title | title added from `rimflow show` |
| "11.2M in ALMOST_OUT" | what ALMOST_OUT is | meaning added from `design/RimMandrake/operating_modes_2026-10-26.md` |
| "(folded in 2026-10-01; see below)" | the old "see below" points at nothing | names the event (Haiku struck, commit `063612964a`) |
| "This is the ONLY file" | the subject | names `Agent_Policy.md` |
| "Measure: `token_census.py --since <UTC>`" | what to measure | "To measure helper use" |
| "Helper A's mark-clean lines ..." (one long sentence) | the order of cause and effect | split into steps |
| "The routing axis is measured, not argued." | which axis | left; could not determine |
| "Escalate the model, never the ceremony: the same short leash." | what "the same short leash" is | left; could not determine |
| "v3 had simply finished" | v3 of what | left; could not determine |
| "Cutting claims from a doc" | what the task is | left; pointer to `efficient-subagents` |
| "Burn days", "the framework-guided day", "pure leak" | what each term names | left; could not determine |

## Errors fixed

1. **CHARTER, Decisions: "his words in CLAUDE.md".** CLAUDE.md now holds no provenance, and its Evidence-for-Ask
   section holds no quote. His words are at `design/RimMandrake/standing_rulings.md` §Evidence-for-Ask (line 896). The
   pointer now names that file. The meaning reader confirmed the fix.
2. **Agent_Policy, "row 3" (twice).** Commit `063612964a` (2026-10-01) put the OS-level search row at the top of the
   catcher table. Before that commit, row 3 was "Nobody" (opus). After it, row 3 is "Another agent" (sonnet). So a
   literal reader picked sonnet where the rule meant opus. Both lines now name the **Nobody** row. The meaning reader
   confirmed the fix from `git log -p`.
3. **Agent_Policy, "(folded in 2026-10-01; see below)".** The "see below" target was a Haiku note that a later edit
   removed. The line now names the event instead.
4. **CHARTER, "`broadcast.py` is his".** `design/RimMandrake/standing_rulings.md` §The bridge (owner 2026-11-19)
   says that `broadcast.py` is the owner's tool and the Conductor's, and that no other seat or helper runs it. The
   repair-check reader found the old line out of date. The line now says so.

## The checks

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | CHARTER with "(48/48 selftests)" made vague, the hook name and one date removed | 1 lost (the date), exit 1. Check 1 did not see the lost 48 or the hook name. |
| check 2 (`rule_doc_lint.py keep`) | the same plant | 7 lost, incl. 48 and the date, exit 1. Check 2 did not see the lost hook name (see below). |
| check 1 | Agent_Policy with "at most 3", `RM_SPAWN_RESERVE_S=0` and one owner quote changed | 1 lost (the quote), exit 1 |
| check 2 | the same plant | 5 lost (the code span, the id, the quote, 0 and 3), exit 1 |
| hand span check (paragraph-local backtick pairs, below) | CHARTER plant with the hook name removed | 1 lost (`block_agent_coded_name.py`) |
| check 1 | the real CHARTER | 66 items, 0 lost, exit 0 |
| check 1 | the real Agent_Policy | 63 items, 0 lost, exit 0 |
| check 2 | the real CHARTER | 157 spans, 3 "lost", exit 1: all three are artifacts (below) |
| check 2 | the real Agent_Policy | 183 spans, 1 "lost", exit 1: the deliberate "row 3" fix |
| hand span check | both real files | 99 and 115 spans, 0 lost |
| `checkable.py selftest` / `rule_doc_lint.py selftest` | | 19 of 19 / PASS |

**A blind area of check 2, found in this batch.** On the old CHARTER, `keep` pairs backticks across paragraphs and
gets out of step after the stale-drop command. It then reads prose as a code span and a code span as prose. So
`keep` missed the planted loss of `block_agent_coded_name.py`. The batch ran a second span check that pairs backticks
inside each paragraph only. That check caught the plant and found 0 lost spans in both real files.

The 3 CHARTER "losses" of check 2:

- `23,`: the number pattern takes the comma after `2026-09-23,`. The new text has `2026-09-23.`; the date is kept.
- one "code span" and one "quote": text between two mispaired backticks or quote marks, not a real span.

The 1 Agent_Policy "loss" of check 2: "3" occurs 6 times before and 4 after. The two "row 3" pointers became "the
**Nobody** row" (error 2).

Neither check reads people's names. The writer read the diff: neither file names a person except "the owner".

## Tests that read the files

| test | result |
|---|---|
| `src/RimMandrake/rimflow/selftest_testpilot_model.py` (quotes the Fable order, the `rm-testpilot` row) | 7/7 PASS |
| `src/RimMandrake/Utils/selftest_scratch_clone.py` (`--sparse` and `scratch_clone.py` in Agent_Policy) | OK |
| `src/RimMandrake/rimflow/selftest_conductor_authority.py` (CHARTER names the ruling) | 0 failures |
| `.claude/hooks/bench_mode.py` with "I am here" (prints `## Posture`) | prints the new Posture section |
| `src/RimMandrake/Utils/selftest_skills_by_work.py` | PASS |
| `src/RimMandrake/rimflow/selftest_retired_era_gone.py` | PASS |
| `src/RimMandrake/rimflow/selftest_items_glob_live.py` | 1 FAIL, `real_glob_is_clean`: 6 done items keep prose in `items/`, not `items/closed/`. The test reads the live `items/` folder, not these two files. This batch did not cause it and did not fix it. |

## What the meaning read found

A fresh Opus (`rm-judge` type, model opus) read old and new text of each file. It did not get the writer's reasoning.

CHARTER: 6 findings.

| finding | repair |
|---|---|
| Expensive list item 5: "can be proven unread and pushed" dropped the condition | "A leftover can be our own, proven unread and pushed. If all three are true, ..." |
| Posture: the examples of "anything git can undo" read as a closed list | "Anything git can undo gets ... Examples: ..." |
| Queue: "may put v2 ideas" weakened "v2 ideas go" | "v2 ideas go straight to ..., from any window, with no permission." |
| Correctness: "the next checkout erased such a fix" became a history claim | "The next checkout can erase such a fix, and nobody is told." |
| Evidence-for-Ask pointer | correction, judged right |
| `broadcast.py` carve-out named | definition, judged right |

Agent_Policy: 6 findings.

| finding | repair |
|---|---|
| "row 3" (twice) | correction, judged right |
| "The Conductor classifies each item" gave the Conductor a job that the old text left without an owner | restored the passive: "Each item is classified by the rule below." |
| "see "Sonnet vs Opus" below" pointed at a section that does not explain the fold | names the event (Haiku struck) |
| "The routing axis (the one question ...)" invented a meaning | restored the old sentence; listed under "could not determine" |
| 5.2M and 11.2M read as day totals | "per closed item" added to each |

The writer re-ran both checks, the lint and the tests after the repairs. Then a second fresh Opus per file checked the
repairs and read the whole file again:

- CHARTER: the four repairs ok. 1 new finding: "Never fly a flyer on the bridge" narrowed the old "never flyer
  flight". Repair: "Never run a flyer's flight". It also found the out-of-date `broadcast.py` line (error 4).
- Agent_Policy: the four repairs ok, 0 findings. One borderline point: the one-hour alarm in its own sentence could
  read wider than the old clause. Repair: the alarm joins the two-helper clause again, as in the old text.

No third read checked those last two repairs.

## Conflicts (listed, not picked)

1. **Deleting others' work.** CHARTER expensive list item 5: warn, "then only with the owner's word". CLAUDE.md "Only
   five acts stay his": the Conductor may delete work that is not ours, with `lost:` and `undo:` in `--why`.
2. **Loosening a bar.** CHARTER "How we debug": "Loosening a bar stays his." CLAUDE.md "How we debug": "Only the
   Conductor may loosen a bar, as a mindful act." A looser bar is not one of the five acts.
3. **Re-freezing the `official` dump.** CHARTER: "Only the owner re-freezes it." CLAUDE.md: the Conductor window may
   do every act that once needed him, except the five. A re-freeze is not one of the five.
4. **v2 ideas.** CHARTER: v2 ideas go straight to `design/V2_DREAMS.md`, any window, no permission. The Design
   Version rule (`~/.claude/CLAUDE.md`, CLAUDE.md "Each mod has its own Design Version"): a Divergent change is a
   ticket with its acceptance test, for the next version, and which kind a change is is his call at filing.
5. **The helpers the Conductor launches.** CHARTER "Windows": `rm-builder`, `rm-judge`. Agent_Policy "Helpers in this
   repo": five `rm-*` types, including `rm-fixer`, `rm-bridge`, `rm-testpilot`.
6. **Fable blank-page design.** Agent_Policy's Fable row: Fable does "design from a blank page" and is "never a
   helper". The same file: the Conductor (the Fable seat) "does not do design in-window" and backgrounds design to
   Opus. The Opus row: design "always as a backgrounded subagent". No seat is left to do Fable blank-page design.
7. **Where the ladder lives.** CLAUDE.md: the model ladder is in `Agent_Policy.md` "and nowhere else". The quoted
   block in `Agent_Policy.md`: "Ladder source of truth: `~/dev/Lodestar/claude/global/45-subagents.md`."
8. **The Conductor's model.** Agent_Policy: the Conductor runs on Fable 5.2.
   `src/RimMandrake/rimflow/selftest_dispatcher.py` check F7: the Conductor role in the dispatcher schedule is opus,
   citing "Agent_Policy.md, the one ladder".
9. **"This file does not grow."** CHARTER's header says that a new line must delete the line it replaces.
   `batch_plan.md` says that a file can grow. This rewrite adds no rule; CHARTER grew from 15,405 to 16,894 bytes.

## Could not determine

| line | file | who would know |
|---|---|---|
| "never out of it" (he opts work into rigor) | CHARTER | the owner |
| "sweep dependents" (unattended mod-list experiment) | CHARTER | the Conductor; `rimworld-start-prep` does not say |
| "lane" in `SUBJECT_INTENT_TWIST · lane · the ask` (`rimflow file` has no lane field now) | CHARTER | the Conductor |
| "one more generation" (a build run?) | CHARTER | the Conductor |
| "The routing axis is measured, not argued" (the one question, or `bin/delegate route`?) | Agent_Policy | the Conductor |
| "the same short leash" | Agent_Policy | the Conductor |
| "v3 had simply finished" | Agent_Policy | the seat that wrote the lesson; git blame |
| "Burn days", "the framework-guided day", "pure leak" | Agent_Policy | the Conductor; the token census that made the figures |

## What this batch did not test

- No agent read the new text and acted on it. No measurement shows that an agent behaves better after the rewrite.
- No reader checked the last three repairs (the flyer line, the `broadcast.py` line, the alarm clause).
- `selftest_dispatcher.py` did not run. It cites Agent_Policy by name but reads the schedule, not the file.
- The `rule_doc_lint.py` blind area above is not fixed in the tool. It is filed as
  `RIMMANDRAKE_FIX_KEEP_CHECK_MISPAIRS_BACKTICKS_ON_CHARTER`, with its acceptance test (watched to fail on the base).

## Second read of the repairs

Run 2026-11-23, item `RIMMANDRAKE_REREAD_REWRITE_REPAIRS_NO_READER_SAW_THEM`. One fresh Opus reader that made none of
these edits read each repair, restored line and late edit against the base text and the lines that travel with it. SAME
means that a reader of the new line acts as a reader of the old line. A gloss reads SAME when its source says the same.
His quotes: a script compared each quote of three words or more in the base with today's text, whitespace ignored. Four quotes of the base CHARTER are not in today's file. A later crystallize run moved three to history files, where they stand word for word; the fourth is a command template.

| file | line read | verdict | what was done |
|---|---|---|---|
| CHARTER | expensive list item 5, the leftover condition | SAME | none |
| CHARTER | "Anything git can undo … Examples: …" | SAME | none |
| CHARTER | "v2 ideas go straight to …" | SAME | none |
| CHARTER | "The next checkout can erase such a fix …" | SAME | none |
| CHARTER | the Evidence-for-Ask pointer | SAME | none |
| CHARTER | "Never run a flyer's flight", a last repair | SAME | none |
| CHARTER | the `broadcast.py` line, a last repair | SAME | true by `standing_rulings.md` §The bridge |
| Agent_Policy | the **Nobody** row (2 lines) | SAME | none |
| Agent_Policy | "Each item is classified by the rule below." | SAME | none |
| Agent_Policy | "(folded in 2026-10-01 when Haiku was struck …)" | SAME | none |
| Agent_Policy | "The routing axis is measured, not argued." | SAME | none |
| Agent_Policy | "per closed item" (2 figures) | SAME | none |
| Agent_Policy | the one-hour alarm clause, a last repair | SAME | none |
