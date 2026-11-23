# Result: `RIMMANDRAKE_REWRITE_PRODUCER_AND_AUDITOR_ROLES_SWITCHED_OFF`

Part of batch 13 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_PRODUCER_AUDITOR_INNOVATOR_ALL_SWITCHED_OFF`). Files:
`src/RimMandrake/rimflow/roles/producer.md`, `src/RimMandrake/rimflow/roles/auditor.md`. Run 2026-11-23.

Base: 63c47c201e56853fdf5ad28be1f26830e8c5fb8b

Special rule of the batch: the Producer, Auditor and Innovator roles are switched off. The launch of this item took the
obvious answer: do the rewrite now, and do not wait until a role is switched on.

## Scores

| measure | producer before | producer after | auditor before | auditor after |
|---|---|---|---|---|
| bytes | 15,407 | 16,804 | 18,709 | 20,609 |
| words in linted prose | 2,255 | 2,442 | 2,883 | 3,110 |
| STE violations per 100 words | 2.48 | 1.84 | 3.47 | 2.06 |
| sentences over 20 words | 23 | 13 | 42 | 5 |
| flagged lines (mechanical) | 4 | 3 | 7 | 7 |
| lines that a cold reader cannot act on (hand count, by the writer) | 10 | 0 that this run could resolve; 3 listed under "Could not determine" | 12 | 0 that this run could resolve; 3 listed under "Could not determine" |

The producer file grew by 9%. The auditor file grew by 10%.

### The long sentences that stay

| file | line | kind |
|---|---|---|
| both | the "Most project skills are not registered" line | a sentence that holds a command (shared word for word with every role file) |
| producer | the `**Off switch:**`, `**The daily list**` and `**No ticket is raised …**` lines | a bold lead that stays word for word (slogan), joined with its sentence |
| producer | `CUT DECISION` line (owner 2026-11-19) | a sentence that holds a command (the record format) |
| producer | the WIP-cap plan line, the stopping-point bullet, the status note line, the launch-mode line, the `## Ticket edits` line, the blind-view note line, the `review roles r2` gloss, the event-run line | a sentence that holds a command |
| auditor | the `blind_view.sensitive_word` bullet | a bold lead that stays word for word, joined with its command |
| auditor | the blind-view note line, the AU3 count line, the status-up note line | a sentence that holds a command |

The flags that stay: the `🔴` heading in each file (kept word for word: every role file carries it), and `bare-id`
flags on lines that hold P-1..P-9, AU-1..AU-7, DI3, D1(b), AU1, D3(a), RO5 and AU3. Each of DI3, MI1, AU1 and RO5
now has a gloss on the same line. D1(b) and D3(a) keep their pointers (see "Could not determine" and "Conflicts").

## Code that reads the files, and what the rewrite kept for it

- `selftest_lessons_corpus_rule.py` needs "corpus, not a queue", `RO5`, `AU3`, "recur", and "random slice runs first
  in each pass, before mandatory work" before `2. **Mandatory, every one:**`. All stay.
- `selftest_touching_code_cost_rule.py` needs `**When the audit is enough**`, "five picks in a row", "The danger the
  count of five guards" and "A DEFECT is filed only when it passes test 1", and no "No fixed count". All hold.
- `selftest_dispatcher.py` names both files as the `instructions` path. Every `## ` heading of both files stays word
  for word.
- `role_launch.py` and `audit_hardflag_file.py` cite "producer.md step 3", auditor.md "The daily audit" step 1 and
  "Before you stop". The step numbers and the bold leads stay.

## The hand count

| file | old line | what a cold reader lacks | state after |
|---|---|---|---|
| producer | "Part 3 (Orphan homes 3, 4)", "(Orphan home 3; …)" | what an orphan home is | gloss from `role_responsibilities_2026-10-26.md` §Orphan homes |
| producer | "Never talk to him." | who "him" is at first use | "the owner" at first use in each section |
| producer | "and the WIP cap" | what the WIP cap counts | gloss from the plan's own `WIP cap: <n> focus items open per seat` line |
| producer | "The caps are admission checks." | what an admission check does | gloss: the Dispatcher reads the caps before it starts a run |
| producer | "**The priority list** (DI3, MI1)" | two coded ids with no title | names the two requirements of `operating_requirements_2026-11-01.md` |
| producer | "The list reads distressed …" | what "distressed" is | gloss: an alarm reading of `ops_watch` (`ops_watch.py` lists distressed under ALARMED) |
| producer | "(review roles r2 #6)" | a coded id with no title | gloss: a past review of the roles; `git log --grep` finds its commits |
| producer | the `CUT LIST` state chain (one 110-word paragraph) | eight rules in one paragraph | moved to two bullet lists: the states, then the rules |
| producer | "Parts that a goal names … are listed by …" | the subject of the passive | the program is now the subject |
| auditor | "Item: … The pre-screen that you read: …" (one 7-line paragraph) | seven pointers in one paragraph | one bullet per pointer |
| auditor | "escapes" (finding 8 and later) | what an escape is | gloss: a defect that got past the checks into a closed item (`process_sim_findings_2026-10-27.md`: "escaped defects/week") |
| auditor | "His limit is two helpers …" | who "His" is | "'His' is the owner's." |
| auditor | "the interim holders in the activation table" | what an interim holder is | gloss from `role_responsibilities_2026-10-26.md` line 8 |
| auditor | "Your `pre_launch` rewrites the file" | what `pre_launch` is | gloss from the Auditor row of `dispatcher_schedule.json` |
| auditor | "(risk response T7)" | a coded id with no title | names `dispatcher_risk_response_2026-10-29.md`, where the line was folded into T7 |
| auditor | "the false red" | what a false red is | gloss: the failed check result that the verdict set aside |
| auditor | "(the AU1 instrument)" | a coded id with no title | gloss: the "audit yield" metric of `role_responsibilities_2026-10-26.md` |
| auditor | "(RO5)" | a coded id with no title | gloss: the requirement "Repeat errors become rules" of `operations_design_2026-11-01.md` |
| auditor | "review roles r2 #4/#7/#8" | coded ids with no title | gloss as for producer |
| auditor | the audit-line field list (one 50-word sentence) | eight fields in one sentence | one sub-bullet per field |
| auditor | "That is its business, never yours." (both files) | the subject of "That" | "Each refusal and each stop is the Dispatcher's business, never yours" |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy of the new auditor.md with `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` removed and "after three runs" changed to "after a few runs" | 1 lost (the id), exit 1. Check 1 did not see the lost "three". |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 2 lost (the code span and the named id), exit 1. Check 2 did not see the lost "three" either: "three" is a word, not a digit. |
| check 1 | final producer.md / auditor.md | 28 items, 0 lost, exit 0 / 41 items, 0 lost, exit 0 |
| check 2 | final producer.md / auditor.md | 134 spans, 0 lost, exit 0 / 128 spans, 0 lost, exit 0 |
| `rule_doc_lint.py selftest`, `checkable.py selftest`, `batch_done.py selftest` | — | PASS; 19 of 19; GREEN 12 planted cases |
| `selftest_dispatcher.py`, `selftest_lessons_corpus_rule.py`, `selftest_touching_code_cost_rule.py` | old, then new | PASS, then PASS |
| `selftest_retired_era_gone.py`, `src/RimMandrake/Utils/selftest_skills_by_work.py` | old, then new | PASS, then PASS |
| `design/specs/2026-11-19-touching-code-cost/acceptance_stop_rules_calibrated.py` | old, then new | FAIL 2/7, then FAIL 2/7. The same result: `auditor.md` is in no calibration family on the base too. The rewrite did not cause or change the failure. |

Neither check reads a number written as a word. So the meaning read was the only guard for "three runs", "five picks",
"two helpers", "two weeks" and "ten lines". The writer read the diff for each of them; each stays.

Names of people: this run read the diff for names. No person is named in either file. The Conductor, Operations, the
Designer, Efficiency, the Auditor and the Producer each stay at the same count or more. "the owner" rose (producer 7 to
14, auditor 10 to 12), because "him" became "the owner" at first use.

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) per file, one after the other. Each reader got the old and the new text
and no reasoning of the writer. The writer fixed every finding and took three polish lines.

| file | first draft | why it was wrong | repair |
|---|---|---|---|
| producer | "every unresolved replan request and every failed plan step" | the second "every" took "unresolved" off failed plan steps: a broader rule | "every unresolved replan request and failed plan step" (old wording) |
| producer | "`git log --grep "review roles r2"` finds it" | the command finds commits tagged with the name, not the review | "finds the commits tagged with that name" (also in auditor.md) |
| auditor | "an escape is a defect that … was found after the item closed" | narrower than the source: finding 8 counts escaped defects found or not | "a defect that got past the checks into a closed item" |

Polish taken: the orphan-home gloss now reads "the home given to a concern" (orphan home 2 has no holder); "Then fix
the kind" lost its "Then"; two "Then" lines in auditor.md became "So" (the old text gave a reason, not a time); "measure
two yields" became "measure the week's yields".

No second reader read the repairs. Each repair restores the old wording or narrows a gloss to the reader's own text.

## Conflicts (listed, not decided)

1. **Who sets `enabled: false`.** Both files: "Off switch: `enabled: false` … (the owner's)". Root `CLAUDE.md` §Only
   five acts stay his: the Conductor may do every act but five, and the off switch is not one of the five. The same
   conflict is in the Operations result file.
2. **Who rules a cut list.** producer.md: `CUT DECISION` is "The Conductor's decision (owner 2026-11-19, only five acts
   stay his …), or his". producer.md §Decides alone / hands / never: "cut, drop or reorder work on a cut list before
   he rules". The second line names only the owner.
3. **When a priority list reads distressed.** producer.md: the list reads distressed "if an entry is closed".
   `src/RimMandrake/rimflow/priority_list.py` docstring: "A listed item that has closed drops by itself … ops_watch reads
   distress only when no open entry is left (a spent list)".
4. **What ruling D1(b) says about a close.** auditor.md step 3: "(ruling D1(b), 2026-11-01): a close needs a pass".
   `design/RimMandrake/planning_session_design_2026-11-01.md` line 131: "Under ruling D1(b) a close with no verdict
   at all passes."
5. **The helper limit.** auditor.md: "His limit is two helpers at once across ALL roles". Root `CLAUDE.md` §Git: more
   than 4 writers at one time may use a pool of up to 16 clones. These can be two different limits. The Operations
   result file lists the same conflict.

## Could not determine

| file | line | question | who would know |
|---|---|---|---|
| producer | "Listed items launch first on the ring and the pool." | which pool: DI3 names "relentless's pool", and relentless is a retired era | the Conductor; the author of `list_dispatch.py` |
| producer | "FlowWorks + GSS", "GSS's open parts" | the full name of the GSS mod | the Conductor |
| producer | "Efficiency, Operations' economy pass" | whether Efficiency is still a seat or only the economy pass of Operations | the Conductor |
| auditor | "the escapes filed since your last run" | how an escape is marked when it is filed (kind, tag or prefix) | the Conductor; the author of `audit_prescreen.py` |
| auditor | "read the `rm-codebase-health` output" | where that output is written | the author of the `rm-codebase-health` unit |
| auditor | "`D:\ClaudeWork\rimmandrake\csuite\stats.txt`, tag R" | whether the csuite stats file is still written | the Conductor |

## What this run did not test

- No Producer or Auditor run read the new files. Both roles are switched off (`enabled: false` in
  `dispatcher_schedule.json`).
- No measurement shows that a Producer or Auditor run acts better on the new text.
- No second reader read the repairs of the meaning-read findings.
- `acceptance_stop_rules_calibrated.py` fails on the base and after the rewrite. No calibration family names
  `auditor.md`. This run did not calibrate it: the item does not ask for it, and the role is switched off.
