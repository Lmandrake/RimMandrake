# The GPT streamline review of 2026-11-20: what is done, and the rest

Item: `RIMMANDRAKE_ENACT_GPT_STREAMLINE_REVIEW_TRUST_NOT_SUSPICION`. The review:
`D:\ClaudeWork\rimmandrake\conductor\system_review_20261120\gpt_analysis.md`. Measured 2026-11-23, 6:10 to 7:10 PM PST, on
origin/main. His four card answers of 2026-11-20 (6:22 PM PST) are on the item and bind. DONE: built. PARTLY: some is
built. OVERTAKEN: a later ruling of his decides it. Each reading is [measured] unless the row says [guess ~N%].

## The 15 changes

| rank, change | state | evidence | what is left |
|---|---|---|---|
| 1 git publication off the metadata path | PARTLY | `74d8295d69` (a write lands its own shards); `8d9160362d` this run: `./publish --ledger` lands shards alone, past the clone lock, with no peer's commit. Before: 1,146 ledger landings, p50 17 s, p90 96 s, p99 677 s | a ledger write still costs one fetch and one push, and the `rimflow` write itself about 15 s at load 42 |
| 2 close consumes evidence | DONE | no close is refused for a missing pass since 2026-11-21 (`design/specs/2026-11-21-repair-at-the-refusal`); `8d9160362d`: `close --evidence` writes the pass with the close. Before: 357 of 364 code closes marked `uncheckedLifted` | none |
| 3 cards by reference | DONE | `3e224420d1` (`card_repair`: the launch adds the card's text and never refuses) | none |
| 4 delete sentence-based owed detection | PARTLY, the rest not recommended | the demand became a note (`3e224420d1`, `covered`). The note works: of 176 turns that showed it, 35 (20%) filed an owed item; of 1,860 other turns, 130 (7%) did. I read all 35: about 25 filed the act that the note named. His one-list rule of 2026-11-22 says that a debt in a reply must be filed | the kill queue half: 2 rows ever, both false, none filed. It goes with `RIMMANDRAKE_RETIRE_OR_REPAIR_OWED_SOURCES_KILLED_EVERY_TICK` |
| 5 readable titles and machine ids | OVERTAKEN, done as he ruled | his card: "Keep grammar, never refuse"; `9e5768e86f` | none |
| 6 executable delegation | OVERTAKEN | his card did not pick "Let helpers do Conductor acts"; he picked "Small acts directly" (`1cc795be16`). `CLAUDE.md` §Only five acts: no helper does these acts. Restamps: `repin` (`789e331d85`) and `concept_tree.py carry` exist, on his card or the Conductor's act | none |
| 7 enforcement at the operation's boundary | NOT DONE, low value | 15 PreToolUse hooks read each Bash call, 15 to 26 ms each; 4 of the checks also run in the git pre-push hook | a list of false blocks by hook would decide. No count exists |
| 8 known blockers, not full readiness | OVERTAKEN | his ruling 2026-11-19, §No mod runs forward on a broken pipeline: a component not looked at keeps the list from READY. A change loosens his rule | his or the Conductor's |
| 9 one whole-design review | OVERTAKEN twice | his card 2026-11-20 "Keep both gates as now"; his card 2026-11-23 "All three, as today" (`7ff1743b00`) | none |
| 10 review the repair at its scope | PARTLY | mod fixes: one fresh reader "reads only that fix, once". The Auditor queue is gone (`e0a979ce9f`). Pipeline code: `roles/code_review.md` line 33 still gives the fresh reader the whole file, by his rule of 2026-11-19 | his rule, so a proposal only |
| 11 an isolated tree for each writer | PARTLY | each detached run has its own pool clone (16 at most). In-window helpers share `/home/mandrake/rm/bench` | measure collisions first |
| 12 dedupe at admission | PARTLY | one live ledger run per mod (`design/specs/2026-11-23-one-live-run-per-mod`); one clone per item refuses a second run on the same item | two items with one cause are still two runs; no count exists |
| 13 spend stop fits the task, checkpoint first | PARTLY | no launched agent is told its spend; a cap stop resumes (`stop_resume.py`). One run was capped at half on 2026-11-23 (`RIMMANDRAKE_FINISH_SLACK_ICON_LAMP_CHECKS_CAPPED_AT_HALF`) | `spend_watchdog.py` gives no early checkpoint signal |
| 14 handoff as an automatic checkpoint | PARTLY | the wake prints his words, each mod now and his homeless messages (`c4f917ce9c`); detached runs survive a restart | the written handoff ritual stays (a user-level rule of his) |
| 15 stop process growth, prompt diet | NOT DONE, growing | the Auditor and its "a repeat error becomes an enforced rule" are gone (`e0a979ce9f`). `CHARTER.md` line 199 still says an enforced rule is a hook. A Conductor hand act still owes an item in a day (his words, 2026-11-15) | the diet, below |

## The ten contradictions

| conflict | state |
|---|---|
| reversible acts need no check, and code needs a red test | DONE: `CHARTER.md` §Posture now carries §Touching code has a cost beside "Act first" |
| no subagent writes shared state, and helpers write ledger events | FIXED this run (`CHARTER.md` §Windows) |
| each clone has one writer, and helpers share it | DONE: `GIT_WORKFLOW.md` line 11 names the window and the helpers that it runs in that clone |
| Test Pilot: never restore the mod list, and restore it | DONE `032f29fdc8` |
| Conductor backstop 400k and 200k | DONE: both files say 400k (2026-11-20) |
| never edit an old check, and repair a wrong check | FIXED this run (`rm-builder.md`, `rm-fixer.md`) |
| a restoration is never a build item, and file it as one | FIXED this run (`designer_write.md` §plan.md) |
| never `git pull --rebase`, and use it | FIXED: the "invisible until" bullet is gone; this run removed the last "pull/rebase" advice in §Traps |
| five acts are his, and new skills wait for him | DONE `571c429dd1` (skill proposals go in the weekly Crystallize report) |
| one whole-mod review for cleanse, two gates elsewhere | OVERTAKEN: his card of 2026-11-23, all three checks for a cleansed design too |

## The prompt diet

The Conductor's startup reading chain was 183.3 KB in the review. It is 199.3 KB now, plus `GUIDING_PRINCIPLES.md` (11.2 KB).
`CLAUDE.md` grew from 43.2 to 58.0 KB. The global file is 38.8 (38.3), the Charter 18.6 (18.3), the model policy 23.4
(22.2), Purpose 10.1 (9.4), the Conductor role with its pointer 50.4 (51.9). The six `rm-*` helper files are 79.8 KB
(about 73). `rm-consult.md` changes nothing, and still carries commit, ledger and progress-file rules. He deferred a length
ceiling for rule files to about 2026-12-05 (note of 2026-11-21).

## Recommended order for the rest

1. `RIMMANDRAKE_RETIRE_OR_REPAIR_OWED_SOURCES_KILLED_EVERY_TICK` (a failure that happens every tick; filed).
2. The helper-file diet: the six `rm-*` files share one common block, and `rm-consult.md` gets a read-only one. No rule of his
   changes. [guess ~80% that it removes about 25 KB]
3. Change 13: an early checkpoint signal before the spend stop.
4. Change 7: count the false blocks of each hook for one week, then move only the worst.
5. Change 12: count runs on two items with one cause for one week.
6. Changes 11 and 10: only after a measured collision or a measured rediscovery.
7. The `CLAUDE.md` diet: after he rules on the length ceiling (about 2026-12-05).

Tickets: one is filed (row 1). The other rows fail test 1 of §Touching code has a cost today: no failure was measured, except the one capped run in row 13, which resumed.
