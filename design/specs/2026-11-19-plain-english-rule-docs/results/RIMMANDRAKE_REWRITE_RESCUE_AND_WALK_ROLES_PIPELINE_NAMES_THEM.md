# Result: RIMMANDRAKE_REWRITE_RESCUE_AND_WALK_ROLES_PIPELINE_NAMES_THEM

Batch 5 of `design/specs/2026-11-19-plain-english-rule-docs/batch_plan.md`. Run 2026-11-19. Base commit `9850da2ca2`.

Files:
- `src/RimMandrake/rimflow/roles/fable_rescue.md`
- `src/RimMandrake/rimflow/roles/walk_brief.md`
- `src/RimMandrake/rimflow/roles/criteria_fixer.md`

Special rule: `maturation.py` quotes the marked block in `fable_rescue.md` step 2. The marks
(`<!-- offline-model: begin ... -->` and `<!-- offline-model: end -->`) are kept word for word. The text inside the
marks is rewritten. So `maturation.OFFLINE_MODEL` now carries the new text into the offline builder's brief and the
road-back fixer's brief. `selftest_offline_model_rule.py` reads nine phrases in the block. All nine stay.

## Scores

Measured with `rule_doc_lint.py lint`. "STE" is violations per 100 words. "long" is the count of sentences over 20
words.

| file | bytes before | bytes after | words before | words after | STE before | STE after | long before | long after | flagged before | flagged after |
|---|---|---|---|---|---|---|---|---|---|---|
| `fable_rescue.md` | 19,456 | 21,760 | 3,261 | 3,550 | 4.57 | 2.28 | 67 | 23 | 3 | 0 |
| `walk_brief.md` | 3,485 | 3,797 | 396 | 456 | 2.53 | 1.10 | 7 | 2 | 0 | 0 |
| `criteria_fixer.md` | 2,535 | 2,957 | 385 | 456 | 4.68 | 1.54 | 8 | 3 | 1 | 1 |

The flag that stays in `criteria_fixer.md` is `bare-id` on "L4". The new text gives L4 its title beside it ("the
level of the owner's own review", `infrastructure/VALIDATION_LADDER.md` §L4). The lint flag is mechanical.

### The long sentences that stay

`fable_rescue.md` (23):
- owner quotes: 5 (the "Yup, do the Rescue brief." line with its item id; the two quotes under "What the owner wants
  from you"; the "rescue builder" quote; the "WHY DID FABLE STOP" quote);
- the owner's positive-steps bullet, kept word for word by rule: 1 ("Think outside the box: ...");
- the shared "Read first" line, the same in each role file and agent file: 1;
- the "Authority" line, the same in each role file: 1;
- two short sentences that the lint joined at a bold lead or at the HTML comment of the marks: 11;
- sentences that hold a command: 4 ("Each one is fixed, proved done and closed, or brought to the owner ...", kept in
  the old words after the meaning read; "Before any fix or tuning, build what lets you SEE the problem ...";
  "Ask when evidence defeats the obvious answer ..."; the `PICTURE:` line of the question form).

`walk_brief.md` (2): the shared "Read first" line; the "Authority" line.

`criteria_fixer.md` (3): the owner quote; the task line in bold that `selftest_criteria_fixer.py` reads ("known-bad
case fails and the known-good case passes"), joined by the lint with the next sentence; the line that holds the
command "Only two acts can loosen an owner bar".

## Hand count: lines that a cold reader could not act on

### `fable_rescue.md` (12 before, 0 after)

| old line | what a cold reader lacks | state after |
|---|---|---|
| "v2 folds in the Slack Fable's review from inside the work" | who the "Slack Fable" is | "the review that the Slack rescue's Fable agent wrote from inside the work" |
| "The launcher pastes everything below the line" | who the launcher is | names the Conductor. Source: `maturation_rescue.py` prints "launch a Fable Rescue (roles/fable_rescue.md) ... nothing was launched" to the Conductor's log. |
| "Polish is listed, not built." and "(his move, or the Conductor's act, owner 2026-11-19)" | what "his move" moves | "Moving work to a later version is his move, or the Conductor's act" |
| "That is the gradient." | what "the gradient" is | gloss from the line itself: "a number changed until a check turns green" (the second meaning read removed "in small steps", which the old line does not say) |
| "all of it may be merged, split, replaced or deleted" | the subject (the list came after the verb) | the reader is the subject: "You may merge, split, replace or delete any of the following" |
| "the certificate's red came from a fifth pair" | a fifth pair of what | adds the source's own words: `pipeline_view_from_fable.md`: "1.4 slack against the seated plug" |
| "A long measurement holds the shared build stage" | what the build stage is | "The build stage is the folder on D: where `src/RimMandrake/Utils/winbuild.py` builds a mod." (`winbuild.stage_dir`) |
| "the one experiment that separates the suspects early: the simplest case ..." | the subject after the colon | "That experiment is the simplest case ..." |
| "New bars are proposed on your sheet" | which sheet | "your rescue sheet (`inventions.md`, step 9)" |
| "its art through the art ledger" | which command | adds "(`art install`)" from `CLAUDE.md` §Art |
| "A pick passes when the benefit is shown ..., no old check went red, no bar moved, and ..." | four conditions in one sentence | a list of four conditions, all required |
| "Each such case is fixed; or proved unreachable ...; or brought to the owner" | three outcomes in one sentence, mixed with the trigger | the trigger first, then a list of the three outcomes |

### `walk_brief.md` (3 before, 0 after)

| old line | what a cold reader lacks | state after |
|---|---|---|
| "never advance anything but the one move below" | where "below" is | "the one `advance ... --to his_walk` move at the end of 'What you write'" |
| "No `--steward-confirms`: the brief is the stage's only exit check." | whether this is a command | the slogan stays, then "do not pass that flag, because ..." |
| "(the last `his_walk` move in the record; with none, the version's first move)" | what "with none" refers to | "If the record has no `his_walk` move, use the version's first move." |

### `criteria_fixer.md` (3 before, 0 after)

| old line | what a cold reader lacks | state after |
|---|---|---|
| "anything tagged L4" | what L4 is | "the level of the owner's own review, `infrastructure/VALIDATION_LADDER.md`" |
| "two calibration cases" | which two | "one known-bad case and one known-good case" (named in the task line of the same file) |
| "and is not how your repair is judged: calibration is." | the subject of the last clause | "Calibration judges your repair, not the result of the item." |

## The no-loss checks

The plant: in each file, one named id or path removed and one number changed (`/tmp/rescue_plant/`).

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | the planted copy of each file | exit 1 for each of the 3 files; each lists the lost id or path |
| check 2 (`rule_doc_lint.py keep`) | the planted copy of each file | exit 1 for each of the 3 files; each lists the lost id or path and the lost number |
| check 1 | the real rewrite | `fable_rescue.md` 33 items, 0 lost; `walk_brief.md` 19, 0 lost; `criteria_fixer.md` 7, 0 lost; exit 0 each |
| check 2 | the real rewrite | `fable_rescue.md` 68 spans, 0 lost; `walk_brief.md` 44, 0 lost; `criteria_fixer.md` 15, 0 lost; exit 0 each |

The plant run also caught two losses in the first draft. Both were false spans: check 2 pairs a quote mark or a
backtick across two sentences. In `fable_rescue.md` a new comma broke the span from `"21 of 288 poses found no lay"`
to the owner quote. In `walk_brief.md` the span `. No ` sits between the end of the `advance` command and
`--steward-confirms`. The rewrite restored the old joins. So both checks pass on the text as written, not by an edit
to a check.

Names of people: I read the diff for names. The names are "the owner", "the Conductor", "GPT", "Fable" and "Opus".
No name was lost or added.

## Tests that read the files

Each test passed on the base and on the new text:

- `src/RimMandrake/Utils/selftest_positive_steps_one_source.py` (each line of `.claude/rm_positive_steps.md` is in
  `fable_rescue.md`)
- `src/RimMandrake/rimflow/selftest_bar_holds_rule.py` (no bare "the family")
- `src/RimMandrake/rimflow/selftest_offline_model_rule.py` (the marked block, its nine phrases, no spend words)
- `src/RimMandrake/rimflow/selftest_criteria_fixer.py` (the fixer packet starts from `criteria_fixer.md`)
- `src/RimMandrake/rimflow/selftest_conductor_authority.py` (each role file names the Conductor ruling)
- `src/RimMandrake/Utils/selftest_skills_by_work.py` (each "Read first" path exists)
- `src/RimMandrake/rimflow/selftest_bench_word_prose.py`
- `src/RimMandrake/rimflow/selftest_maturation.py`
- `src/RimMandrake/rimflow/selftest_maturation_record.py`
- `src/RimMandrake/rimflow/selftest_retired_era_gone.py` (new text only)

## Meaning read

One fresh Opus reader per file (agent type `rm-judge`, model opus). Each reader got the old text and the new text
only, with no reasoning from the writer. The first spawn as `general-purpose` was refused by a hook (unbounded
context), and the helper-slot allocator refused the next two spawns while 3 of 3 slots were in use. The reads ran when
slots were free.

### `fable_rescue.md`: 10 findings, 8 repaired, 3 kept as true glosses

| finding | kind | action |
|---|---|---|
| "Each one ends in one of three ways: fixed; proved done and closed; brought to the owner ..." splits "fixed, proved done and closed", which can be one ending | WEAKENED | restored the old words: "Each one is fixed, proved done and closed, or brought to the owner with evidence ...". The ambiguity of the old line stays; see "Could not determine". |
| "Today the Conductor is the launcher" | INVENTED | kept as a gloss from code, reworded to what the code shows: "`maturation_rescue.py` only proposes a rescue, to the Conductor's log, and launches nothing. The Conductor launches the run." (`maturation_rescue.py` `log_line` and `conductor_log_path`) |
| "These positive steps (the bullet above)" narrows the protection to one bullet | CHANGED | removed "(the bullet above)"; the old scope stays |
| the "fifth pair" gloss adds "1.4 slack against the seated plug" | INVENTED | kept: a quote of the source report `pipeline_view_from_fable.md` in the worked-example folder, with its path |
| "The build stage is the folder on D: where `winbuild.py` builds a mod" | INVENTED | kept: from `winbuild.stage_dir` and `BUILD_ROOT` in `src/RimMandrake/Utils/winbuild.py` |
| "(`art install`)" after "the art ledger" | INVENTED | kept: from `CLAUDE.md` §Art ("Art goes in through the art ledger's `art install` only") |
| "You can meet other things off that path: another mod, or a redesign ..." reads as a closed list | CHANGED | "File anything else that you meet off that path with its evidence. Examples are ..." |
| "That change is one of these: ..." makes three examples a closed list | CHANGED | "Examples of that change: ..." |
| "Other runs already tried more effort" names an actor that the old line does not | INVENTED | restored "More effort on the same path was already tried." |
| small shifts: "truly" lost on the owner-decision case; "The owner ruled on v2"; "v2 adds two reviews"; "Nobody tells the agent its spend" lost "never" | WEAKENED / CHANGED | each restored: "a case that truly needs the owner's decision"; "v2 folds them in by the owner's ruling of ..."; "v2 folds in two things"; "The agent is never told its spend." |

The reader also named a risk: the offline-model block is reworded. `selftest_offline_model_rule.py` passed on the
repaired text.

A second fresh Opus reader read the repaired `fable_rescue.md` against the old text. It found 1 change: the gloss of
"the gradient" said "a number moved in small steps", and the old line does not say "small steps". The gloss now reads
"a number changed until a check turns green". The second reader found no other change. It checked hardest the move of
work to a later version, the stopping conditions, and the offline-model block.

### `walk_brief.md`: no findings

The reader checked hardest: the definition of an evidence write, the "one move" that the role may advance, and the
`--steward-confirms` line.

### `criteria_fixer.md`: 1 finding, kept

| finding | kind | action |
|---|---|---|
| the gloss of L4 ("the level of the owner's own review, `infrastructure/VALIDATION_LADDER.md`") is not in the old text | INVENTED (the reader checked it as accurate) | kept: `VALIDATION_LADDER.md` line 54 reads "## L4 — Human (the owner) — reserved" |

## Conflicts found (not resolved here)

1. `criteria_fixer.md` says a declared loosen needs "a second reader before it lands". The guard
   (`refusal_contract.py diffguard`, line 789) accepts a loosen with a card reference OR a second-read reference. The
   spec (`2026-11-12-refusal-contract-for-judges-and-gates.md`, "What it may not change") says the second reader is
   GPT, and otherwise the loosen becomes a card. The role file names only the second reader. The new text keeps the
   role file's line. The Conductor decides.
2. `criteria_fixer.md` says an owner bar "goes to him as a card". `CLAUDE.md` §Only five acts stay his lets the
   Conductor window loosen a bar as a mindful act. The last paragraph of `criteria_fixer.md` already names that act.
   So the two lines agree in effect, but "goes to him as a card" reads as the only route. Kept as written.
3. `fable_rescue.md` says "that the method transfers beyond Slack is not yet shown". The same file cites the
   Explosive Knockback rescue (2026-11-17), a second rescue that used the offline model. Whether that rescue shows the
   method transfers is a judgment for the Conductor. Kept as written ("Nobody has shown yet that the method works
   beyond Slack.").

## Could not determine

- `fable_rescue.md`: "Each one is fixed, proved done and closed, or brought to the owner ...". The line can name two
  endings ("fixed, proved done and closed" is one sequence) or three. The old words stay. The owner's quote above it
  ("implement all the tickets") suggests two. The Conductor would know.

- `fable_rescue.md`: "a 2026 snap check". The source report (`pipeline_view_from_fable.md`) uses the same words. I
  could not determine if "2026" is a year, a test number or a name. The example stays word for word. The Slack
  rescue's report and the Conductor would know.
- `fable_rescue.md`: "the cuts of GPT's review". "Cuts" can mean the parts that the brief adopted, or the cuts that GPT
  proposed. I did not read the review file to decide. The phrase stays word for word. The Conductor would know.
- `fable_rescue.md`: "use a separate build stage folder for it if you can". `winbuild.py` on the command line has no
  option for a stage name. `winbuild.stage_build(..., stage_name=...)` takes one in Python. The line stays as an
  instruction, with no route added.

## What this batch did not test

- No measurement shows that a rescue run, a walk-brief run or a fixer run behaves better after the rewrite.
- No live rescue, walk-brief or fixer run read the new text.
- The new offline-model block now reaches the offline builder's and road-back fixer's briefs. Only
  `selftest_offline_model_rule.py` read those briefs.

## Second read of the repairs

Run 2026-11-23, item `RIMMANDRAKE_REREAD_REWRITE_REPAIRS_NO_READER_SAW_THEM`. One fresh Opus reader that made none of
these edits read each repair, restored line and late edit against the base text and the lines that travel with it. SAME
means that a reader of the new line acts as a reader of the old line. A gloss reads SAME when its source says the same.
His quotes: a script compared each quote of three words or more in the base with today's text, whitespace ignored. Two quotes of the base moved to `roles.history.md` in a later crystallize run, word for word.

| file | line read | verdict | what was done |
|---|---|---|---|
| fable_rescue.md | "Each one is fixed, proved done and closed, or brought …", restored | SAME | none |
| fable_rescue.md | `maturation_rescue.py` only proposes; the Conductor launches | SAME | none |
| fable_rescue.md | "These positive steps", old scope | SAME | none |
| fable_rescue.md | the fifth pair, with its source | SAME | none |
| fable_rescue.md | the build stage gloss | SAME | none |
| fable_rescue.md | "(`art install`)" | SAME | none |
| fable_rescue.md | "Examples are another mod, or a redesign …" | SAME | a later rule edit joined this line; "Do not build it" still binds |
| fable_rescue.md | "Examples of that change: …" | SAME | none |
| fable_rescue.md | "More effort on the same path was already tried." | SAME | none |
| fable_rescue.md | "truly needs", "is never told its spend" | SAME | none |
| fable_rescue.md | the gradient gloss, the last repair | SAME | none |
| criteria_fixer.md | the L4 gloss | SAME | none |
