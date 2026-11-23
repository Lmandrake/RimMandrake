# Result: `RIMMANDRAKE_REWRITE_INNOVATOR_AND_RUNNER_OPTIONS_ROLE_FILES`

Part of batch 13 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_PRODUCER_AUDITOR_INNOVATOR_ALL_SWITCHED_OFF`). Files:
`src/RimMandrake/rimflow/roles/innovator.md`, `src/RimMandrake/rimflow/roles/runner_options.md`. Run 2026-11-23.

Base: beebcb2c0624aa37fea6bc6de4f424a7e1abd559

Special rule of the batch: the roles are switched off. The launch of this item took the obvious answer: do the rewrite
now.

## Scores

| measure | innovator before | innovator after | runner_options before | runner_options after |
|---|---|---|---|---|
| bytes | 17,452 | 19,232 | 10,472 | 11,445 |
| words in linted prose | 2,630 | 2,854 | 1,367 | 1,499 |
| STE violations per 100 words | 3.31 | 1.89 | 1.68 | 1.53 |
| sentences over 20 words | 36 | 6 | 4 | 2 |
| flagged lines (mechanical) | 5 | 4 | 0 | 0 |
| lines that a cold reader cannot act on (hand count, by the writer) | 13 | 0 that this run could resolve; 3 listed under "Could not determine" | 7 | 0 that this run could resolve; 3 listed under "Could not determine" |

The innovator file grew by 10%. The runner_options file grew by 9%.

### The long sentences that stay

| file | line | kind |
|---|---|---|
| innovator | the "Most project skills are not registered" line | a sentence that holds a command (shared word for word with every role file) |
| innovator | the `**No trial starts without a watchdog …**` line | a bold lead that stays word for word, joined by the lint with its sentence |
| innovator | the "`concept` or `mod` proposal that cannot be trialled" line | 21 words; the lint counts the bracketed examples |
| innovator | the "Merges and splits" bullet, two bullets of "Decides alone / hands / never" | a bold lead or a list, joined by the lint |
| runner_options | the Designer launch line | a sentence that holds a command |
| runner_options | the stall-table pointer | a sentence that holds a path and a heading that other files cite |

The flags that stay in innovator.md: the `🔴` heading (every role file carries it), and `bare-id` on I-1..I-4, I3 and
I1. I1 and I3 now have a gloss on the same line. I-1..I-4 carry the file and part that hold their titles.

## Code that reads the files, and what the rewrite kept for it

- No test names `innovator.md` or `runner_options.md`. Nineteen tests read the role folder or role files. Each `#` heading of
  both files stays word for word (measured: a diff of the heading lines is empty).
- `selftest_conductor_authority.py` needs the ruling name in each role file. Both files hold it.
- `selftest_skills_by_work.py` reads the paths under `## Read first`. That section is unchanged.
- `selftest_retired_era_gone.py` needs each line that names Whittle to say that the thing is retired. See "Checks".
- `design/RimMandrake/roles.history.md` and ten lessons cite `runner_options.md`. The four cited headings stay.

## The hand count

| file | old line | what a cold reader lacks | state after |
|---|---|---|---|
| innovator | "(Orphan homes 2 and 3)" | what an orphan home is | gloss from `role_responsibilities_2026-10-26.md` §Orphan homes |
| innovator | "design §3" | which design | gloss in the header: the dispatcher design |
| innovator | "him" and "he" at first use | who he is | one line in the header |
| innovator | "the parent item" | which item | one line in the header |
| innovator | the proves-itself block (one 60-word sentence) | two conditions in one sentence | two bullets |
| innovator | the "His, always" block | eight acts in one sentence | a list |
| innovator | "(review roles r2 #4)", "(review roles r2 #3, #5)" | a coded id with no title | gloss: a past review of the roles |
| innovator | the watchdog paragraph (fourteen sentences) | the rules and the cases run together | a bullet list, with the cases (a), (b), (c) |
| innovator | "GSS work" | the full name of the mod | gloss: GimmeSomeSlack (`design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md` line 104) |
| innovator | "and its word" | what the word of a metric is | gloss: the label of its reading |
| innovator | "(… the I3 instrument)", "(the I1 instrument)" | a coded id with no title | gloss: the metrics "innovations he takes" and "trials" |
| innovator | the trial fields (one 130-word sentence) | seven fields in one sentence | one sub-bullet per field |
| innovator | "That is its business, never yours." | the subject of "That" | "Each refusal and each stop is the Dispatcher's business, never yours." |
| runner_options | "An unreadable meter, or >90% used, refuses." | what refuses what | "the launch is refused" |
| runner_options | "No automatic sandbox relaxation …", the model and effort line | several facts in one line | one bullet per fact |
| runner_options | "The Windows-launch workspace-write failures above" | where "above" is | names the section |
| runner_options | the operator's duties (two 60-word bullets) | many duties in one sentence | labelled bullets and sub-bullets |
| runner_options | "The operator and the CLI own those contracts" | what a contract is here | "own these duties" |
| runner_options | "It uses Steam and waits …" | the subject of "It"; false for a named game | names the function; corrected (see "Conflicts") |
| runner_options | the 9 steps (up to 90 words each) | many acts in one paragraph | one sub-bullet per act |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy of each new file with the ruling name removed, and "14 days" (innovator) or ">90% used" (runner_options) changed to words | 2 lost in each copy, exit 1 |
| check 2 (`rule_doc_lint.py keep`) | the same copies | 3 lost in each copy (the code span, the number, the id), exit 1 |
| check 1 | innovator.md / runner_options.md | 36 items, 0 lost / 19 items, 0 lost |
| check 2 | innovator.md / runner_options.md | 100 spans, 0 lost / 86 spans, 0 lost |
| `rule_doc_lint.py selftest`, `checkable.py selftest`, `batch_done.py selftest` | none | PASS; 19 of 19; GREEN 12 planted cases |
| the nineteen tests that read the role folder or role files | old, then new | 18 PASS, then 18 PASS, after the repair below |
| `selftest_conductor_authority.py` | old, then new | FAIL, then FAIL, with the same FAIL lines. The FAIL lines name `list_shape.md`, `maturation.py`, `build.py` and `wake_words.py`, not these files |

`selftest_retired_era_gone.py` failed on the first draft. The old sentence ran over two lines, so the test did not see
the word. The draft put "Whittle judge" on one line with no "retired". The line now says "(the Whittle loops are retired)".

Names of people: this run read the diff for names. No person is named in either file. The role names stay at the same
count or more (Conductor 16 to 18, Dispatcher 4 to 6 in innovator.md).

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) per file, one after the other. Each reader got the old and the new text and
no reasoning of the writer.

| file | first draft | why it was wrong | repair |
|---|---|---|---|
| innovator | the `**Reverting:**` rules nested in step 1 | a revert in step 2 no longer fell under them | moved before the numbered list; "in step 1 and in step 2" |
| innovator | "stop reading the file. Never quote the figure." | the old text bars any quote from that file | "Never quote the file." |
| runner_options | none | the reader found no changed rule | none |

Polish taken in innovator.md: "Never commit with a stash or a reset"; "Then run `./publish`"; "one or more of these"; the
bracketed examples restored; `killed` back in the chain; the reason sentence joined to "So the blind view is a closed
type"; the design doc named in its bullet; "what git holds under that name"; "The filing is part of the I3 instrument".
Polish taken in runner_options.md: the gloss on "settings/snapshot debts" deleted; "reports >90% used"; the old "No
automatic sandbox relaxation or Claude fallback is attempted" restored; "Other Claude … guards" without "The".

No second reader read the repairs, the later splits of long sentences, the retired-Whittle note, the GSS gloss,
or the two corrections (Steam, scratch).

## Conflicts (listed, not decided, except the two corrected lines)

1. **Corrected: how the game launches.** runner_options.md step 5 said that `launch_and_wait()` "uses Steam".
   `src/RimMandrake/Utils/northstar_driver/live_session.py` and `game_instance.py` `fire_a` start any game other than
   ArchBig directly, and start ArchBig directly when Steam does not take the launch. The line now says so.
2. **Corrected: when the drive-local scratch is used.** runner_options.md said without a condition that ext4 work runs from
   the drive-local Codex scratch. `src/RimMandrake/Utils/agent_runner.py` (line 4 and line 225) uses the scratch only for
   Windows Codex. Linux Codex works directly in the clone. The line now says so.
3. **The two blocking items are dropped.** innovator.md waits "until that item is closed" for
   `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` and until `INNOVATOR_BUILD_EXPIRY_WATCHDOG_REVERTS` "is closed and its program
   runs". The ledger reads both items as dropped. So, on the text, the Innovator can never run a helper or a trial.
4. **Who sets `enabled: false`.** innovator.md: "(the owner's)". Root `CLAUDE.md` §Only five acts stay his: the off switch is
   not one of the five. The same conflict is in the Operations and Producer result files.
5. **Who says yes.** innovator.md: "His, always" lists a bar, the vision, canon, `CLAUDE.md`, the bridge and any game.
   Root `CLAUDE.md` §Only five acts stay his gives most of those acts to the Conductor. `map.md` of the crystallize run lists the
   same conflict.
6. **Silencing a role.** innovator.md: "his or the Conductor's (owner 2026-11-19)". `dispatcher_design_2026-10-26.md` §3:
   "silencing a role goes to him". The "His, always" list of innovator.md still holds "silencing or moving a role".
7. **How big the helper limit is.** innovator.md: two helpers at once across ALL roles. Root `CLAUDE.md` §Git: more than
   4 writers at one time may use a pool of up to 16 clones. These can be two different limits.
8. **The run budget field.** The Innovator row of `dispatcher_schedule.json` says in `_run_budget_why`
   "claude --max-budget-usd". Root `CLAUDE.md` §No launched agent is told its spend forbids that flag.
   `role_launch.py` uses `spend_watchdog.wrap` instead. So only the note is stale.

## Could not determine

| file | line | question | who would know |
|---|---|---|---|
| innovator | "accepted items a day when its reading is MEASURED, otherwise name another" | whether accepted items a day is a required default guard or an example (`polish.md` of the crystallize run calls the line garbled) | the Conductor |
| innovator | "his frustration tags" | which file or tool holds the tags | the Conductor; the author of `ops_watch` |
| innovator | "puts one line on his card" | whether the card is the owner's card or the Conductor's card | the Conductor |
| runner_options | "source-first decisions" | what decision the operator makes source first | the author of the 2026-11-10 live run |
| runner_options | "settings/snapshot debts" | which settings and snapshots are owed (the reader: the debt register can track more than step 9 names) | the author of the 2026-11-10 live run |
| runner_options | "Obtain a fresh independent Whittle judge" | which judge takes its place, because the Whittle loops are retired | the Conductor |

## What this run did not test

- After the two corrections, only `selftest_retired_era_gone.py`, the lint and the no-loss check ran again.
- No Innovator run read the new file. The role is switched off (`enabled: false` in `dispatcher_schedule.json`).
- No Codex run or Codex game session used the new runner_options.md.
- No measurement shows that a run acts better on the new text.
- The launch commands in step 2 to step 6 were not run.
