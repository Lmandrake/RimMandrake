# Results: the rule files compressed the way crystallize compresses CLAUDE.md

Item `RIMMANDRAKE_CRYSTALLIZE_RULE_FILES_DOUBLED_IN_EIGHT_DAYS`. The map is `map.md` beside this file. Each claim is
tagged `[measured]` or `[guess ~N%]`. State at 2026-11-21, 6:40 AM PST.

## The answer in short

Yes, the crystallize method works on the rule files, and it is done. It does not undo the growth. The four files are
4% shorter, and nothing was lost. Most of the eight days of growth is rules that are each different, not copies:
163 of 302 sections had no sentence that could change. The larger cut is still ahead, and it waits for one live run
(see "What was not cut").

## Lines before and after

| file | lines at the start | lines now | words at the start | words now |
|---|---|---|---|---|
| root `CLAUDE.md` | 727 | 720 | 7,617 | 7,546 |
| `design/RimMandrake/standing_rulings.md` | 1,831 | 1,777 | 25,935 | 25,443 |
| `infrastructure/agents/CHARTER.md` | 300 | 264 | 3,062 | 2,619 |
| `src/RimMandrake/rimflow/roles/*.md` (21 files) | 4,097 | 3,900 | 51,018 | 47,909 |
| all four | 6,955 | 6,661 | 87,632 | 83,517 |

All cells `[measured]` with `wc` on `git show 542106e641:<file>` and on the files now.

- The cut is 294 lines (4.2%) and 4,115 words (4.7%). Words are the honest measure: some helpers also wrapped
  80-column text to 120 columns, which removes lines and no content.
- During the run another run (`f5c8bd66e9`, one lock per game) changed 93 lines of the root, `standing_rulings.md`
  and `roles/conductor.md`. Its change is merged in and is counted in "now" (it removed 7 lines).
- About 4,500 words were not deleted. They moved, word for word, to two history files: `design/RimMandrake/roles.history.md`
  (new, 3,859 words) and `design/RimMandrake/CLAUDE.history.md` (629 words added) `[measured]`. So the repo as a
  whole is not smaller. What an agent must read to act is smaller.
- No rule file is longer than at the start `[measured by the check]`.

## What kind of thing was cut

The 302 sections were classed by seven Opus helpers that read every line. Rows that hold each class: KEEP 285,
DUPLICATE 52, MOVE 51, MERGE 37, TOOL DOES IT 14. 163 rows read "unchanged" `[measured from the map]`.

1. **History and his words inside role files, moved to a history file (the largest kind).** Example:
   `roles/operations.md` §The running check kept its rule lines and one pointer. Its six lesson stories and their
   measurements (the 84 reds, the 4 h 18 min stall) are now in `roles.history.md`. Example: `roles/runner_options.md`
   kept its nine operating steps; the 20-row table of one run's stalls moved.
2. **The same rule in two files, now one home and one pointer.** Example: `standing_rulings.md` §What is where held a
   second copy of the folder tree of the root `CLAUDE.md` (38 lines, now 24). Example: `CHARTER.md` §How we debug
   (18 lines, now 9) points at the root, and the root gained the 4 rule lines that only `CHARTER.md` had.
3. **A line that only restates a tool, deleted after the tool was watched (14 readings, 21 spans).** Example: the
   root line "Never use `git add -A`, `git add .` or `git commit -a`" went after `block_blanket_git_stage.py` refused
   four planted commands; "Commit explicit paths only" stays. Example: `roles/designer_exam.md` listed what
   `designer_stage.py check` refuses; the check refused 36 of 36 planted faults in a temp folder, and each rule stays
   as a rule. The real text that each tool printed is in the "Tools watched" tables of `map.md`.
4. **Two false statements, deleted on sight.** `roles/conductor.md` said that Quick mode "refuses a brief without"
   the card text; the launcher adds the words and never refuses (`3e224420d1`). `roles/designer_lock.md` said a hole
   stays open "until" an item that was dropped on 2026-11-18.

## What was not cut, and why

- **The sections of principles 1 and 3 (a stop the work did not cause; a fault of form).** This run left them while
  `RIMMANDRAKE_REPAIR_AT_THE_REFUSAL_NO_STOP_FOR_UNTIED_SHOES` was live. A second run merged them after it closed: see
  "The second run" below.
- **The section of principle 6 ("After a change, only the checks that the change touches run again").** Its run has
  ended and `rerun_relation.py` is on origin/main. The helper read the module and kept the section: each bullet names
  a stage or a case that the module does not print. The nightly and blind-cycle bullets were not traced: UNMEASURED.
- **Text that its reader cannot get from a pointer.** Subagents, judges that run in a temp folder and Codex runs do
  not get the root `CLAUDE.md` `[measured in `role_launch.py` and `coverage_calibration.py`]`. So the three judge
  briefs, `criteria_fixer.md` and the Codex cleanse lines keep full text.
- **Everything on the do-not-touch list**, and every sentence, heading or mark that a test or tool reads.
- **Nine sections of `standing_rulings.md` that looked like cuts by title.** On reading, each held a clause found
  nowhere else. The review's count (592 lines in 16 sections, classed by title) was too high: this file gave about 50 lines.
- **Rules that no home holds.** About 30 role-file lines `[guess ~60%]` have no copy in any home file (for example "Never treat
  UNMEASURED as zero" beside the sanity probe; the token-blind rule). They stay in the role files. Each is named in
  `map.md` as "home lacks".

## The lose-nothing check, red and green

`python3 src/RimMandrake/Utils/selftest_rule_files_lose_nothing.py check`. It was written before the first edit.

- **Red, planted on a fixture** (bare run, part of the selftest): a deleted rule with no map row: FAIL ROW; a deleted
  rule in a row marked unchanged: FAIL SENTENCE; a reworded quote: FAIL QUOTE; a renamed section that a file cites:
  FAIL POINTER; a longer file: FAIL LONGER. An excused span and a moved, re-wrapped quote stay green `[measured]`.
- **Red, planted on the real result** (`planted`): the same five losses, planted in a copy of the final files, each
  FAIL of the right kind `[measured, last line "every planted loss was caught"]`.
- **Red for real, during the run:** 302 ROW losses before the map was filled; LONGER on two files while helpers
  edited; 19 losses (17 SENTENCE, 2 SPAN) when the other run's commit arrived and this clone had not merged it.
- **Green on the real result:** "lines: 6948 at the base f5c8bd66e9, 6661 now. lose-nothing check: PASS, 0 losses"
  `[measured]`.
- **What the check did not see, and what did.** It reads spans, quotes, pointers and length, not meaning.
  - A helper removed `CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` from two Conductor files. The id lived on in other
    files, so the check passed. `selftest_conductor_authority.py` went red and the id is back.
  - A separate meaning read (below) found 6 changed meanings that the check had passed.
- **Tests.** 98 selftests and acceptance programs read the rule files. 96 pass. 2 fail, and both failed before the
  first edit: `selftest_flagship_contract.py` and `acceptance/code_review_brief_accept.py` `[measured]`.

## What the fresh reader found

- **The fresh reader** (one Opus that made no edit) read the map and ten sections of its own choice across seven
  files. It found 0 significant findings `[measured: its report]`. Two of its small notes were narrowed wordings; both
  are restored (`roles/conductor.md`, the scope of the stopping-level rule; `roles/designer_exam.md`, "never a reason
  to end the run blocked").
- **The meaning read.** Fourteen role files were also rewritten into plain English in the same pass. The batch plan
  requires a second reader for that. Three Opus readers compared old and new text, every hunk. They found 6 changed
  meanings and 8 doubtful ones `[measured: their reports]`. Examples: the exam's third pass condition (every
  Challenger miss accounted for) had become a separate chore; "a sanity probe for a round, zero or alarming count"
  had become "probe each count"; "never a stash or a reset" had vanished behind a pointer whose home does not say it.
  12 are restored to the old meaning. 1 is kept on purpose (the dropped item above). 2 doubtful ones are lines on
  `polish.md`.
- Not read by any second reader: the sections outside those ten in the files that were compressed without a rewrite
  (the Conductor files, `operations.md`, `fable_rescue.md`, `standing_rulings.md`, `CHARTER.md`, the root).

## The plain-English batches: done, changed, still owed

Of the eleven batches that were left in `design/specs/2026-11-19-plain-english-rule-docs/batch_plan.md`:

| batch | state now |
|---|---|
| Designer packet files (7) | Done in this pass, with its meaning read. Lint per 100 words went from 3.2-5.4 to 1.3-4.7. Four files are still above the 2.5 target (`designer.md` 2.93, `designer_cleanse.md` 3.47, `designer_dialogue.md` 3.07, `designer_examples.md` 4.68): owed, small. |
| Untested judge role files (3) | Rewritten, with its meaning read (3.9-4.6 to 2.9-3.7). Still owed: the calibration of both judge families. Both rows read UNTESTED before and after, so no state changed. |
| Producer, Auditor, Innovator, runner options (4) | Done in this pass, with its meaning read. `producer.md` 2.48 and `runner_options.md` 1.68 meet the target; `producer.md`, `auditor.md` and `innovator.md` were deleted 2026-11-23 (the roles are retired). |
| `standing_rulings.md` | Changed, still owed. 11 of 70 sections were compressed and written plainly. The other sections wait for the batch; 6 of them also wait for the refusal run. |
| Judge briefs; biome, delegation and debug docs; trap fact files; git, game and purpose docs; the maturation spec; undated fact files; other docs; skills | Not touched. Still owed, unchanged. |

The four batches that were done before this run (subagent files, Conductor files, CHARTER and Agent_Policy,
Operations, rescue and walk) stay done: their files were compressed without a rewrite, and their lint did not get
worse except the root by one violation (128 to 129) `[measured]`.

## Conflicts between rules: settled 2026-11-23

Item `RIMMANDRAKE_DECIDE_TWELVE_RULE_CONFLICTS_THE_COMPRESSION_LISTED`. "Earlier" names the commit of another run.

1. Two helpers across all roles: deleted earlier (`032f29fdc8ce`). `Agent_Policy.md` "3 per unattended seat" was stale
   too: it now names the spawn hook and `slot_rules.json`.
2. Settled: `roles/innovator.md` was deleted 2026-11-23 (the role is retired).
3. Settled: `roles/producer.md` was deleted 2026-11-23 (the role is retired).
4. Loosening a bar: the Conductor may, mindfully (his ruling of 2026-11-19). `CHARTER.md` earlier (`3c98eed8162c`); the
   same sentence in `role_responsibilities_2026-10-26.md` is now deleted.
5. `CHARTER.md` §Git now says what the root says: the seat clone, or the helper clone that the brief names.
6. Program-read output goes to scratch under the agent storage root (his ruling of 2026-10-19). The root earlier
   (`131dbbc5a6a8`); the `/tmp` path in `runner_options.md` is now scratch.
7. A full-list cold load is about 15 minutes (14.5 measured 2026-11-21). `GAME_STATE_WORKFLOW.md`,
   `connect-and-claim.md` and `rimworld-load-round` no longer say 25. Helper types: earlier (`3c98eed8162c`).
8. The restart publishes the shard itself (code of 2026-11-15). The "publish your shard" lines of
   `conductor_restart.md` and `helper_checkpoint.py` and the "states each rule once" line are deleted.
9. `opened_by_conductor` also opens a scope (`designer_stage.py` `OPENED_SCOPES`, 2026-11-18). `designer.md` and
   `designer_grounding.md` now say so.
10. `selftest_flagship_contract.py` follows the 2026-11-19 ruling since `f4f9d7e11d`: red on a planted "stays his",
    green on the tree.
11. Hot water is physics, not a Scald exception (his card of 2026-11-21). No text states the exception as a rule.
12. Conductor pairs: earlier (`032f29fdc8ce`). Fresh reader: two scopes, each now named. Worldgen label: the
    label names a newly generated map, as the item that asked for it says; there is no worldgen feature.

Also settled, from the second run below: the root self-fix case now points at the list in §Touching code has a cost.

Three more findings that are not conflicts: no program reads the `on_request` entry of the Designer manifest, so no
run ever receives `designer_examples.md`; `infrastructure/agents/CONDUCTOR.md` has a copy of "Start of turn" without
`--owed`; `selftest_case_four_rules_two_looks` fails at the start commit too (rule 4 is missing from
`designer_write.md`).

## The one change to how rules get written

**Proposed, not enacted: a rule file has a ceiling, and it is today's length.** A commit that makes one of the four
rule files longer is returned at `./publish` to the same agent, in the same run, with the repair: merge the new rule
into the section that it is a case of; or put its evidence (his words, the date, the measurement, the story) in the
history file; or cut as many lines elsewhere in that file. The history files have no ceiling.

- Why this one: of what could be cut today, most was evidence written beside the rule, and second copies. A ceiling
  makes the writer do that move at writing time, when the writer still holds the context. It is cheap: the LONGER
  branch of the check above is the whole program.
- The danger that the ceiling guards, and the evidence: a rule tree that agents stop reading. The four files grew
  from 3,556 to 6,866 lines in eight days (`design/specs/2026-11-21-generalize-pipeline-repairs/review.md`), and
  about 56 commits in that time only added rule text.
- It is a fault of form, so it never stops work: the gate names the repair and the agent does it at once.
- Success criterion, fixed now: on 2026-12-05 the four files hold at most 6,661 lines and 83,517 words
  (`wc` on origin/main), with no owner objection about rule growth in `owner_objections.py` for those 14 days.
- Review date: 2026-12-05. If the criterion fails, the ceiling was pressed past by hand or was wrong: say which.

## Where things are

- The map, 302 rows, with "Deleted spans" and "Tools watched" tables: `map.md`.
- The polish list (wording nits and unsure cuts; no ticket): `polish.md`.
- The check: `src/RimMandrake/Utils/selftest_rule_files_lose_nothing.py` (`check`, `planted`, bare selftest).
- Moved evidence: `design/RimMandrake/roles.history.md`, `design/RimMandrake/CLAUDE.history.md`.
- Commits: map and check `0c159d7cfd`; role files `2ef5cf2273`; `standing_rulings.md` `19fd1ffcb1`; `CHARTER.md`
  `3b5575f82f`; root `46b285bb7a`; the restored meanings, the folded map and this report in the commit after.

## The second run: the twelve sections of principles 1 and 3, merged (2026-11-21)

Item `RIMMANDRAKE_MERGE_TWELVE_REFUSAL_RULE_SECTIONS_THAT_WAITED`, after the refusal run closed at `78ebf9918d`.

| file | lines before | lines after |
|---|---|---|
| root `CLAUDE.md` | 720 | 705 |
| `design/RimMandrake/standing_rulings.md` | 1,777 | 1,762 |

Both `[measured]` with `wc -l`, base `cea8d0bae6`. The sum went from 2,497 to 2,467.

- **What changed.** Each file now has one section per principle. "Stops that the work did not cause: system failures,
  pipeline defects and asks for the owner" holds No trial is spent, The pipeline fixes its own defects and
  Evidence-for-Ask. "A fault of form is repaired where it is found" holds His word and the Conductor's act are not
  refused, and A refusal carries its path to pass. In `standing_rulings.md` the six old headings stay word for word as
  `###` cases, because 3 to 28 files cite each one. In the root the cases are bold lines.
- **Moved word for word** to `design/RimMandrake/CLAUDE.history.md`: three incident paragraphs.
- **Deleted after the tool was watched:** four lines of §His word and two sentences of §A fault of form. The readings
  are in `D:\ClaudeWork\rimmandrake\merge12_watch\` and in the "Tools watched (merge_twelve)" table of `map.md`.
- **The cut is 30 lines, not the 150 that was guessed** `[guess ~50%]` above. On reading, the six cases do not repeat
  one another: each holds rules that the others lack. His quotes stay in `standing_rulings.md`, the home of his words,
  as the first run kept them.
- **Kept, and why.** The fix-in-the-sitting half of "Touching code has a cost": each bullet changes what a judge or a
  driver does, `selftest_touching_code_cost_rule.py` pins six of its sentences, and a move would cut no line. The
  rules for the tick and the fault loop: 26 of the 48 gates in the census are not converted, so their rule lines stay.
  The five acts, the holds, the stops, the spend and the account lines: full text, unchanged in all three places.
- **The meaning read.** One fresh Opus that made no edit compared every merged sentence with its sources. It found 2
  changed meanings, 1 new rule and 1 lost sentence `[measured: its report]`. All four are restored:
  1. The root's first line gave the pipeline-only scope of the self-fix case to all three cases. Each case has its own
     scope again.
  2. The intro of the new `standing_rulings.md` section stated the self-fix case without its conditions. The intro now
     only names its cases.
  3. The first heading, "...and starts its own repair", promised a repair that no case promises. The heading now names
     the three kinds of stop and states no rule.
  4. "It applies the named repair itself" (the tick) was lost behind a pointer whose page does not say it. It is back,
     word for word.
  One of its five wording notes was a false statement (the owner-words page lists promises, not gates). It is fixed.
- **Checks.** The acceptance test was red before (2,497 lines, exit 1) and is green after (2,467; the lose-nothing
  check PASS with 0 losses at base `cea8d0bae6`; its `planted` mode caught every planted loss). The crystallize
  instrument `checkable.py compare` found 0 of 84 (root) and 0 of 544 (`standing_rulings.md`) checkable items
  unfindable. The 19 tests that read both files give the same results as before: 18 pass, and
  `acceptance/code_review_brief_accept.py` fails before and after. Two tests changed in the same commit, because they
  read only `##` headings: `selftest_self_fix_rule.py` and `selftest_rule_homes_in_briefs.py`. Each was seen to fail
  on a planted loss and pass on the real files.
- **A conflict found here** (the root self-fix case listed fewer reasons to hand off than its home) was settled 2026-11-23:
  the root points at §Touching code has a cost.

