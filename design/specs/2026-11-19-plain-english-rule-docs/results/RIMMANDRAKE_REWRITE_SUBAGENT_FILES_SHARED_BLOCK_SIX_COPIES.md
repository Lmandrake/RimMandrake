# Result: RIMMANDRAKE_REWRITE_SUBAGENT_FILES_SHARED_BLOCK_SIX_COPIES

Batch 1 of `batch_plan.md`. Base commit `25c18fb733`. Run 2026-11-19, one detached BENCH helper (Opus writer).

## What changed

- `.claude/rm_agent_shared_block.md` is rewritten once. A script copies the block word for word into each of the six
  `.claude/agents/rm-*.md` files.
- The "## Repo hygiene" lines and the Conductor-authority paragraph come after the block in each agent file. They are
  rewritten once and are the same in all six files. The only exception is the subagent line of `rm-builder.md`.
- Each agent file's own text is rewritten: the opening, "How a bar is shown to hold", and the Test Pilot sections.
- The front matter of each agent file is byte for byte the same. Each "## Read first" list keeps its paths, in its
  place.
- `.claude/rm_positive_steps.md` is NOT changed. The file holds the owner's words
  (`selftest_positive_steps_one_source.py`: "holds his words"). Its score stays 5.80 by design.
- `.claude/commands/broadcast.md`: one sentence is split, and one passive verb is removed. The front matter and the
  command line are the same.
- One heading-level change in `rm-testpilot.md`: "## Beyond the checklist" is again a numbered list, rules 1 to 5. Two
  lines of the file cite "rule 4 of 'Beyond the checklist'". That rule existed until a later edit made the section one
  paragraph, so the pointer went dead. Git history shows that old rule 4 was the filing rule (`git log -S'rule 4 of
  "Beyond the checklist"' -- .claude/agents/rm-testpilot.md`). The new rule 4 is the filing rule again, so the pointer
  is live.

## Scores

STE is violations per 100 words (`rule_doc_lint.py lint`). "long" is sentences over 20 words.

| file | bytes before | bytes after | STE before | STE after | long before | long after | flagged before | flagged after |
|---|---|---|---|---|---|---|---|---|
| `.claude/rm_agent_shared_block.md` | 4,227 | 4,919 | 5.47 | 2.02 | 8 | 0 | 0 | 0 |
| `.claude/agents/rm-bridge.md` | 6,441 | 7,414 | 4.88 | 2.09 | 11 | 2 | 0 | 0 |
| `.claude/agents/rm-builder.md` | 8,921 | 10,096 | 4.69 | 2.10 | 22 | 5 | 0 | 0 |
| `.claude/agents/rm-consult.md` | 6,136 | 7,016 | 5.02 | 2.21 | 10 | 2 | 0 | 0 |
| `.claude/agents/rm-fixer.md` | 7,510 | 8,496 | 4.62 | 2.22 | 13 | 3 | 0 | 0 |
| `.claude/agents/rm-judge.md` | 6,379 | 7,285 | 4.67 | 1.86 | 11 | 2 | 0 | 0 |
| `.claude/agents/rm-testpilot.md` | 20,852 | 23,392 | 5.42 | **3.33** | 51 | 16 | 3 | 2 |
| `.claude/commands/broadcast.md` | 351 | 352 | 3.70 | 0.00 | 0 | 0 | 0 | 0 |
| `.claude/rm_positive_steps.md` | 404 | 404 | 5.80 | 5.80 | 1 | 1 | 0 | 0 |

### `rm-testpilot.md` misses the 2.5 target

- The file is at 3.33, against the target of 2.5 or less.
- The owner quotes hold about 28 of the 116 violations. Without the quotes, the file scored 3.06 on a draft of this
  run.
- Most of the rest are `-ing` words that are the file's own terms. A rename of these terms would break the names that
  other files grep for:
  - "sitting" (19 times: the `test-pilot-sitting` skill, `TESTPILOT_SAT`, `--sitting`);
  - "failing" (4 times: "the failing moment");
  - "ALARMING" (5 times: a score label of `surprise_book.py`);
  - "MEASURING SURPRISE" (a heading that the owner's words name).
- The Conductor can accept 3.33, or order a rename of the terms. This run did not rename them.

### The long sentences that stay

Each long sentence that stays is one of the three kinds that the plan allows (`rule_doc_lint.py lint --show`).

- Each of the six agent files has the same two long sentences in the common tail. Both hold a command:
  - "Never use `git add -A/./-a` (…), `--force`, … or worktrees.";
  - "File every finding before you report it: …".
- `rm-bridge.md` (2): only the two tail commands.
- `rm-consult.md`, `rm-judge.md` (2 each): only the two tail commands.
- `rm-fixer.md` (3): the two tail commands, and the owner's positive steps (an owner quote).
- `rm-builder.md` (5): the two tail commands; the positive steps (an owner quote); the "what the game can vary" list
  item (a command); and the "it cannot be done" tag (a command).
- `rm-testpilot.md` (16):
  - 5 owner quotes: the positive steps, and the 2026-11-04 quotes on surprise, the surprise book, causal links, and
    "Beyond the checklist";
  - 11 that hold a command: the "it cannot be done" tag, "Vary one thing", the offline-copy line, the reload-rule
    line, the score line, the `testpilot_reload.py` line, the neighbour-expectations check, the `rimflow note` stamp,
    the return list, and the two tail commands.

## Hand count: lines that a cold reader could not act on

| old line | what a cold reader lacked | state after |
|---|---|---|
| shared block: "your PROGRESS FILE is your memory. Write it as a skeleton first; …" | what "it" is, among four actions in one sentence | each action is its own line, and each names the progress file |
| shared block: "A human reads it once → `Transient/`; a program reads it → scratch." | what "it" is | "If a human reads the output once, …" |
| shared block: "provenance flags `--owner-said` (his words) / `--by-card` / `--per-ruling` / `--why` (yours)" | two of the four flags had no meaning | each flag has its meaning, taken from `CLAUDE.md` §Owner authority on the ledger |
| shared block: "the Conductor launches every FlowWorks and GSS build" | what GSS is | "GSS is Gimme Some Slack", from `design/concepts/GimmeSomeSlack/` |
| tail: "never `git add -A/./-a`" | what `-a` is (`git add` has no `-a`) | the span stays. The gloss "`git add -A`, `git add .` or `git commit -a`" comes from `CLAUDE.md` §Git |
| `rm-bridge.md`: "Hold the bridge through rimflow" | which command | names `rimflow bridge take` and `rimflow bridge release` (`CLAUDE.md` §The bridge is passed through one file) |
| `rm-testpilot.md`: "filed under rule 4 of "Beyond the checklist"" (2 lines) | rule 4 did not exist | the section is a numbered list again. Rule 4 is the filing rule, as in git history |
| `rm-testpilot.md`: "stays a PROGRESS note past the cap" | which cap | "Past the cap of that rule (about 5 new items per sitting)" |
| `rm-testpilot.md`: "A RETIRED key scores EXPECTED …" | what a key is | "A key of the book is one kind slug in one context", from the header of `surprise_book.py` ("A (kind, context) RETIRES …") |
| `rm-testpilot.md`: "This restarts the Test Pilot rule's count" | what the Test Pilot rule is | "That rule (`rimflow pilot`) sends an item to a pilot after 3 non-pass runs in a row", from the file's own front matter |
| `rm-testpilot.md`: "A running testq job holds a host's guard." | what testq is | "(a job of `testq.py`)" |
| `rm-testpilot.md`: "the mod's functional script" next to "the walk's `## anti-guessing notes`" | that the two are one thing | "the mod's functional script (the walk)", from `design/RimMandrake/debug_process.md` §0 rule 4 |
| `rm-testpilot.md`: "Its header defines a useful test." | whose header | "The header of `testpilot_reload.py` …" |

## The checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | `rm-judge.md` with `D:\ClaudeWork` removed, "1500 px" changed to "a few px", and one copy of a ruling id removed | 1 lost (the path), exit 1 |
| check 2 (`rule_doc_lint.py keep`) | the same planted copy | 2 lost (`D:\ClaudeWork`, one copy of 1500), exit 1. The removed id has other copies in the file, so it is not a loss. |
| `rule_doc_lint.py selftest` | — | 18 of 18 PASS, after the fix below |
| `checkable.py selftest` | — | 19 of 19 |
| check 1 | each of the 8 changed files | exit 0, 0 lost (`rm-testpilot.md`: 60 items before, 0 unfindable) |
| check 2 | each of the 8 changed files | exit 0, 0 lost (`rm-testpilot.md`: 173 spans) |

**Check 2 had a false quote, and this run fixed the tool.**

- Before the fix, check 2 said that `rm-testpilot.md` lost 1 "quote". `keep` had paired the `"` in
  `find("activeMods")` with the `"` in `ssh "$STEVE_WSL"`. The result was a 200-character "quote": the old run-on
  bullet, which the rewrite splits into sub-bullets.
- The fix is in `design/specs/2026-11-19-plain-english-rule-docs/rule_doc_lint.py`. `keep` now masks each code span
  before it looks for quotes. A code span is still checked whole, as a code span.
- Two new selftest cases cover the fix. "keep reads no quote across two code spans" failed on the old parser, and it
  passes now. "keep still sees a lost code span that holds a quote mark" passes on both parsers.
- The other batches use the same tool. A re-run of `keep` on `CLAUDE.md` and on `roles/artist.md` against
  `25c18fb733` still reads 0 lost.
- The cost of the fix: a quote that holds a code span is now read in two parts. This run did not measure how often
  that happens.

**Names.** Neither check reads the names of people. This run compared the capitalized words of each old and new file.
Only sentence-start words differ ("Foreground", "Writes", "Resetting" …). No name of a person is lost.

## Tests that read these files

| test | result after |
|---|---|
| `src/RimMandrake/Utils/selftest_skills_by_work.py` (shared block word for word in six files; each Read first list) | PASS |
| `src/RimMandrake/Utils/selftest_positive_steps_one_source.py` | PASS |
| `src/RimMandrake/rimflow/selftest_bar_holds_rule.py` (reads `rm-builder.md`, `rm-fixer.md`) | PASS |
| `.claude/hooks/selftest_block_unbounded_agent.py` | PASS |
| `src/RimMandrake/rimflow/selftest_retired_era_gone.py` | PASS |

`selftest_skills_by_work.py` plants a fault by an edit of the line "Load a skill only when the step needs it, once.".
A first draft reworded that line, and the test went red. The line keeps its old words. It was already plain.

## What the meaning read found

One fresh Opus reader (`rm-judge`, Opus) read each changed file: 8 readers in total. Each reader got only the old text
and the new text. The shared block had its own reader. The agent-file readers read the rest of their files.

| file | what the reader found | what this run did |
|---|---|---|
| shared block | "Write the ledger only through" narrowed the old "Ledger only through" to writes | restored to "Use the ledger only through" |
| shared block | the reset/clean-up sentence moved out of the standing-rulings bullet | put back as a separate sentence inside that bullet, as in the old text |
| shared block | "A reset is never …" dropped clean-up | "A reset or clean-up is never …" |
| shared block | "a file that you write in the repo" narrowed "writing a file is not deploying it" | restored to "So writing a file is not deploying it." |
| shared block | the `--by-card`, `--per-ruling` and GSS meanings are new | kept, because each has a source: `CLAUDE.md` §Owner authority on the ledger, and `design/concepts/GimmeSomeSlack/` |
| shared block | "Crop to the subject" became a flat command | kept. The reader rated this one minor |
| `rm-testpilot.md` | "Those regimes are …" made a list of examples read as complete | restored to the old colon list |
| `rm-testpilot.md` | the testq gloss "the test queue" has no source | cut to "(a job of `testq.py`)" |
| `rm-testpilot.md` | the key, cap, Test Pilot rule, walk and rule-4 additions are new | kept. The reader found that each is supported by the old text or by a named source |
| common tail | "If your brief holds a factual error" narrowed "Flag a factual error" | restored to "Flag a factual error instead of refusing." |
| common tail | "file writes" narrowed "writes" | restored to "Keep writes and commits in separate Bash calls." |
| common tail | the `git commit -a` gloss is new | kept, from `CLAUDE.md` §Git |
| `rm-builder.md`, `rm-fixer.md` | "the two bars in conflict" settled what the old "the two" left open | restored to "the two" |
| `rm-bridge.md` | splitting the script line made the table read as a description, not as the script's duty | joined again into one line |
| `rm-bridge.md` | the `rimflow bridge take` / `release` names are new | kept, from `CLAUDE.md` §The bridge is passed through one file |
| `rm-judge.md` | "a cosmetic change" may be narrower than "cosmetic" | kept. `CLAUDE.md` §Art says "art and cosmetic changes" |
| `rm-consult.md` | NO MEANING CHANGES FOUND | — |
| `broadcast.md` | NO MEANING CHANGES FOUND | — |

### The check of the repairs

A second round of fresh readers (`rm-judge`, Opus) read the repaired text. One reader read each file that had a repair:
the shared block, `rm-testpilot.md`, `rm-builder.md`, `rm-fixer.md` and `rm-bridge.md` (the whole file).

| file | what the second reader found | what this run did |
|---|---|---|
| `rm-testpilot.md` | "The reads are …" made a list of example reads read as complete | "Example reads: …" |
| `rm-testpilot.md` | the pit example read as facts, not as expectations to check | "check these expectations: …" |
| `rm-builder.md` | the range read and the dense re-sweep left the "Before you change any code" bullet, so their timing was lost | "Then, still before you change any code, read that range …", inside that bullet |
| shared block (read by the `rm-fixer.md` reader) | the owner citation (2026-11-13 and 2026-11-18) covered only the second of the two clauses that it covered before | the citation is on both clauses |
| shared block, all files | "`--why`: your own words" gives "yours" to `--why` alone; the old "(yours)" was ambiguous | kept. `CLAUDE.md` §Owner authority on the ledger defines each flag, and says that a `--by-card` label is "our text" but the decision is his |
| all readers | the sourced additions (GSS, `--by-card`, `--per-ruling`, `git commit -a`, `rimflow bridge take`/`release`, `testq.py`, key, cap, walk, rule 4) | kept, each with the source named above |

After the last repairs, the `rm-bridge.md` reader read the whole file, shared block included. That reader found only
sourced additions and the `(yours)` reading. No reader checked the three last repairs in `rm-testpilot.md`,
`rm-builder.md` and the citation line. Each of these repairs puts back an old scope word, or moves a line back under
its old bullet.

## A pipeline defect found and fixed on the way

- The first reader spawn was refused by `block_agent_over_slots.py`: "CONDUCTOR already has 3 helper(s) running … N=3".
  The refusal came three times, 2026-11-19 15:47-15:52 PST.
- Rewrite batches had no allowance of their own. So all 17 batches and the Conductor window shared N=3.
- The fix: `src/RimMandrake/Utils/slot_rules.json` `role_runs` gets `rm-detached-bench-rimmandrake-rewrite-: 1`. The
  item is `RIMMANDRAKE_ALLOW_REWRITE_BATCH_ITS_ONE_MEANING_READER`.
- The test: 3 new cases in `src/RimMandrake/rimflow/selftest_designer_exam_slots.py`. Before the rules change, the
  test printed RED, 3 failed. After it, the test printed GREEN, 0 failed. `.claude/hooks/selftest_block_agent_over_slots.py`
  is GREEN too.

## Conflicts (listed, not picked)

1. **Program output: `/tmp` or scratch.**
   - The shared block says: "a program reads it → scratch", and scratch is `D:\ClaudeWork`.
   - `CLAUDE.md` §Transient says: "If a program reads it, put it in `/tmp`, never the repo."
   - The rewrite keeps "scratch".
2. **Test Pilot: restore the mod list, or never.**
   - `rm-testpilot.md` "Hard limits at the bridge" says: "🔴 Never restore the owner's mod list … there is no
     restore-before-release step."
   - The same file, "Ending the sitting" step 4, says: "Leave the game as you found it (restore the list, game down)."
   - `CLAUDE.md` §Facts you cannot guess agrees with the hard limit.
   - The rewrite keeps both lines.
3. **Test Pilot: game up or game down.**
   - "The sitting" step 7 says: "Keep the game up."
   - "Ending the sitting" step 4 says: "game down".
   - The two may not conflict: step 7 covers the time during a sitting, and step 4 covers its end. They are listed for
     the Conductor to confirm.
4. **The judge's brief path.**
   - `rm-judge.md` says that art judging reads `skills/rimworld-art-evaluation/SKILL.md`, and that cosmetic judging
     reads `design/RimMandrake/art_judge_brief.md`.
   - `CLAUDE.md` §Art says that a second agent judges "art and cosmetic changes" against `art_judge_brief.md`.
   - This run did not determine whether the two differ for art.

## Could not determine

| line | what is unknown | who would know |
|---|---|---|
| shared block: "FOUNDRY is retired (BENCH takes only needs=owner live looks)" | which work BENCH takes: items with `needs=owner` that also need a live look, or every live look that needs the owner. The line is kept word for word. | the Conductor (the FOUNDRY retirement, 2026-11-18) |
| `rm-builder.md`: "a case your own report lists as failing, unlaid, …" | what "unlaid" means for a case that is not FlowWorks. In `measurement_report.py` it means a fitting that the build did not lay. The word is kept. | the author of commit `68bf672a17` (builders/fixers: how a bar is shown to hold) |
| shared block: "≈600 s of silence kills you" | which process kills the helper. `tool_traps.md` names the subagent watchdog, but this run did not tie the number to it. The line is kept word for word. | `infrastructure/state/facts/tool_traps.md` owner, the Conductor |

## What this run did not test

- No agent was launched with the new files to see whether its behaviour changes. The plan says that no measurement
  shows this (`batch_plan.md` §What this plan does not prove).
- No third reader checked the last repairs (see "The check of the repairs").
- How often a real quote holds a code span. Since the `keep` fix, such a quote is read in two parts.

## Acceptance state of the item

The item's acceptance test has four parts.

| part | state |
|---|---|
| both no-loss checks find 0 lost, after they fail on a planted loss | met: 8 of 8 files, both checks |
| the STE target of the plan is met | NOT met for `rm-testpilot.md` (3.33 against 2.5). Met for the 6 other changed files and `broadcast.md`. `rm_positive_steps.md` is his words and stays 5.80. |
| the tests that read the files pass | met: 5 of 5 |
| a fresh reader finds no changed meaning | met with one limit: after the repairs, the last readers found only sourced additions. No reader checked the three last repairs. |

The item stays open on one decision for the Conductor:

- accept 3.33 for `rm-testpilot.md`, because the rest is owner quotes and the file's own terms; or
- order a rename of "sitting", "failing", "ALARMING" and "MEASURING SURPRISE". A rename touches the
  `test-pilot-sitting` skill, `TESTPILOT_SAT` and `surprise_book.py`.

## Second read of the repairs

Run 2026-11-23, item `RIMMANDRAKE_REREAD_REWRITE_REPAIRS_NO_READER_SAW_THEM`. One fresh Opus reader that made none of
these edits read each repair, restored line and late edit against the base text and the lines that travel with it. SAME
means that a reader of the new line acts as a reader of the old line. A gloss reads SAME when its source says the same.
His quotes: a script compared each quote of three words or more in the base with today's text, whitespace ignored. No quote differs.

| file | line read | verdict | what was done |
|---|---|---|---|
| shared block | "Use the ledger only through" | SAME | none |
| shared block | the reset and clean-up sentences | SAME | none |
| shared block | "So writing a file is not deploying it." | SAME | none |
| shared block | the `--by-card`, `--per-ruling` and GSS glosses | SAME | none |
| shared block | "Crop to the subject." | SAME | none |
| shared block | the owner citation on both clauses, a last repair | SAME | none |
| rm-testpilot.md | the regimes, colon list | SAME | none |
| rm-testpilot.md | "(a job of `testq.py`)" | SAME | none |
| rm-testpilot.md | "Example reads: …", a last repair | SAME | none |
| rm-testpilot.md | "check these expectations: …" | SAME | none |
| common tail | "Flag a factual error instead of refusing." | SAME | none |
| common tail | "Keep writes and commits in separate Bash calls." | SAME | none |
| common tail | the `git commit -a` gloss | SAME | none |
| rm-builder.md, rm-fixer.md | "the two", restored | SAME | none |
| rm-builder.md, rm-fixer.md | "Then, still before you change any code, read that range …" (builder), a last repair | SAME | none |
| rm-bridge.md | the script line, joined | SAME | none |
| rm-bridge.md | the `rimflow bridge take` and `release` names | SAME | none |
| rm-judge.md | "a cosmetic change" | SAME | none |
