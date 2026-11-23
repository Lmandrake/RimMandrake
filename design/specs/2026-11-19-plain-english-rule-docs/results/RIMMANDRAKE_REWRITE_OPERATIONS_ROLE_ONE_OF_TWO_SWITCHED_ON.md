# Result: `RIMMANDRAKE_REWRITE_OPERATIONS_ROLE_ONE_OF_TWO_SWITCHED_ON`

Batch 4 of `batch_plan.md`. File: `src/RimMandrake/rimflow/roles/operations.md`. Base commit: `d4d5729aeb`. Run 2026-11-19.

## Scores

| measure | before | after |
|---|---|---|
| bytes | 27,080 | 32,104 |
| words in linted prose | 4,015 | 4,765 |
| STE violations per 100 words | 4.38 | 1.97 |
| sentences over 20 words | 85 | 13 |
| flagged lines (mechanical) | 4 | 3 |
| lines that a cold reader cannot act on (hand count, by the writer) | 17 | 0 that this run could resolve; 6 listed under "Could not determine" |

The file grew by 19%. The worked example grew by 16%.

### The 13 long sentences that stay

| line | kind |
|---|---|
| 14, 18, 18 | an owner quote |
| 180 | an owner quote (the Throttle quote, inside the band sentence) |
| 172, 219, 235, 289, 458 | a sentence that holds a command |
| 168 | two short sentences that the lint joined (the second opens with the number 6) |
| 300 | two sentences that the lint joined at a bold lead |
| 303, 332 | a bold lead that stays word for word (slogan), joined with its parenthesis |

The 3 flags that stay: the `🔴` heading (kept word for word: `inline_by_mode` in `dispatcher_schedule.json` matches it), and two
`bare-id` flags on lines that hold `review U N2` and `OP3`. Each of the two ids now has a gloss on the same or the next line.

## Code that reads the file, and what the rewrite kept for it

- `role_launch.doc_sections` inlines sections by heading prefix (`inline_by_mode` in `dispatcher_schedule.json`). Every
  `## ` heading stays word for word.
- `selftest_role_start_package.py` needs `**Incident runs.**` inside "The running check". It stays.
- `selftest_dispatcher.py` Q6 needs "skips this whole run" and no "07:30 and 19:30 local". Both hold.
- The Dispatcher matches the `REPLAN REQUEST` prefix; the blind view passes `OP-<yyyymmddThhmmZ>`. Both stay.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "Item: … (your own: every other role but the Conductor is token-blind and reads …)" | one compressed parenthesis with three facts | split into three bullets |
| `review U N2`, `review V, V2`, `review roles r2 #1/#4/#6` | coded ids with no title | gloss: a finding of a past review; `git log --grep "review U"` finds it |
| "Record it `--per-ruling …`" | what "it" is | "Record a Conductor instruction that you act on" |
| "raises the Andon flags" | what an Andon flag is | gloss from the `ops_watch.py` docstring (FLAG: band, run, silent, target) |
| "It already fed the slot allocator" | the subject of "It" | "the readings of `ops_watch.py`" |
| "Steve-lane", "a filler brake" | what the lane and the brake are | gloss from the `brake_release.py` docstring |
| "`steve.incident_unclaimed_min` alarms past 30 min" | what passes 30 min | gloss from the `steve_incident_unclaimed` docstring in `ops_watch.py` |
| "Live promises." | what a live promise is | gloss from `CLAUDE.md` §An operational item is done only when it is running |
| "`OPS_*` under the parent item" | which item | `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE` (`alarm.parent` in `ops_watch_rules.json`) |
| the alarm-trigger table cell (about 90 words) | one cell holds eight rules | moved to bullets under "The alarm trigger" |
| "At 1,650,000 as a hard cap it admitted four runs a day" | the subject of "it" | "the daily cap" |
| "sending its incidents to his rung" | what "his rung" is | gloss: `OWNER_RUNG` in `incident.py` |
| "(OP3, …)" | what OP3 is | gloss from `design/RimMandrake/operating_requirements_2026-11-01.md` |
| "(strategy §3, step 7 …)" | which strategy | names `design/RimMandrake/operations_metronome_strategy_2026-11-02.md` |
| "is N matched to runway" | what N is | gloss: the slot count per seat (`slot_allocator.py`) |
| "file it" (silent series) | what to file | "File an item for the blind collector" |
| "Throttle … (above)" and "the economy pass below" | where "above" and "below" point in an inlined alarm run | the caps note names "When you run", the caps |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy with `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` removed and "(240)" changed to "(a few hours)" | 1 lost (the id), exit 1. Check 1 did not see the lost 240. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 4 lost (the code span, the id, 240, and one copy of 28 from a tokenizer artifact), exit 1 |
| check 1 | the final rewrite | 65 items, 0 lost, exit 0 |
| check 2 | the final rewrite | 252 spans, 0 lost, exit 0 |
| `rule_doc_lint.py selftest`, `checkable.py selftest` | — | PASS, 19 of 19 |
| `selftest_role_start_package.py` | old, then new | PASS 33 of 33, then PASS 33 of 33 |
| `selftest_dispatcher.py`, `selftest_restart_now.py`, `selftest_spend_blind_agents.py`, `selftest_agent_improve_steps.py` | old, then new | PASS, then PASS |
| `selftest_skills_by_work.py`, `selftest_retired_era_gone.py` | new | PASS |

A lint artifact: check 2 reads "2026-10-28," as the number "28," and "2026-10-28 " as "28". A moved comma read as a lost
number. This run removed the comma after the date in the Throttle line. The meaning does not change.

Names of people: this run read the diff for names. Steve, SteveDesktop, the Conductor, the Producer, the Auditor, the
Innovator and Codex each stay at the same count or more. The name of the retired dashboard in the owner quote stays.

## What the meaning read found

A fresh Opus reader (rm-judge, model opus) read the old and the new text. It did not get the writer's reasoning. It found
8 lines. The writer fixed all 8. The same reader then read only the repair diff: 8 of 8 fixed, 0 new findings.

| first draft | why it was wrong | repair |
|---|---|---|
| "token-blind: the instructions of those roles forbid token talk" | the old text says this only of Producer, Auditor and Innovator | clause removed |
| "You do not act on the code." (review ids) | a new rule | sentence removed |
| "Record each act on a Conductor instruction" | can mean more records than one per instruction | "Record a Conductor instruction that you act on" |
| "An Andon flag is a rule … that a MEASURED series broke" | a flag is what a broken rule raises; a silent flag is a series that stopped being MEASURED | "`ops_watch.py` raises an Andon flag when a series breaks a rule" |
| "If nobody claims the incident, … alarms past 30 min" | an invented condition; "the incident" pointed at nothing | gloss from the `ops_watch.py` docstring |
| "The alarm makes sure that the cost is fixed fast." | moved the duty off whoever must act | "The cost is then fixed fast, and you keep your runs cheap." |
| "The lessons below are for diagnosis." | narrowed bullets that bind every run | line removed |
| "File the cause." | narrower than the old "file it" | "File an item for the blind collector." |

After the repair check, the writer split three more long sentences (the `revisit_quiet` re-arm, the four cases of a
clerk run, and the forecast bullet). The checks and tests ran again after that edit. No reader read that last edit.

## Conflicts (listed, not decided)

1. **Who decides a bar cut.** "The economy pass": "north-star skepticism (propose cuts; a bar cut is always his)". "Decides
   alone / hands / never": a lowered bar goes to the Conductor, and "The Conductor decides it (owner 2026-11-19)". Root
   `CLAUDE.md`: "Only the Conductor may loosen a bar, as a mindful act". The file keeps both lines. The Conductor decides.
2. **Who restores a band.** "Throttle": "Restoring a band is the owner's." Root `CLAUDE.md` §Only five acts stay his: a band
   restore is not one of the five acts. The line can be a limit from before the Maturation Pipeline.
3. **Who sets `enabled: false`.** "Off switch": "(the owner's)". Root `CLAUDE.md` lets the Conductor do every act but five.
4. **The helper limit.** "Helpers": "His limit is two helpers at once across ALL roles". Root `CLAUDE.md` §Git: more than 4
   writers at one time may use a pool of up to 16 clones. These can be two different limits. This run did not determine it.

## A stale line fixed on sight

`dispatcher_schedule.json`, the Producer `_why`, said "operations.md must name this prefix, owed to its doc owner".
`operations.md` names the `REPLAN REQUEST` prefix (§The economy pass). The `_why` now says so.

## Could not determine

| line | question | who would know |
|---|---|---|
| "hand it to a lane ahead of new work" (Live promises) | what a "lane" is in the Maturation Pipeline | the Conductor; the author of `using-rimflow` §Done means running |
| "The running check, the economy pass and the weekly assessment" (Alarm runs) | no section of this file describes a weekly assessment | the Conductor |
| "ceremony on his attention" (economy pass) | what the economy pass measures for it | the Conductor |
| "build-cop group", "RerunGate" (held-nightly bullets) | code terms with no gloss | the authors of `ops_watch.py` |
| "a reach-repair unblock", "hands a binding back to its builder" (churn bullet) | Maturation Pipeline terms with no gloss here | the authors of `ops_watch.py` churn code and `maturation.py` |
| "a metric joins" (trigger line) | probably a reading with the same cause key that joins the incident (OP3) | the author of `incident.py` |

## What this run did not test

- No live Operations run read the new file. The inline extraction is tested only by `selftest_role_start_package.py`.
- No measurement shows that an Operations run acts better on the new text.
- The last split of three long sentences had no second meaning read.

## Second read of the repairs

Run 2026-11-23, item `RIMMANDRAKE_REREAD_REWRITE_REPAIRS_NO_READER_SAW_THEM`. One fresh Opus reader that made none of
these edits read each repair, restored line and late edit against the base text and the lines that travel with it. SAME
means that a reader of the new line acts as a reader of the old line. A gloss reads SAME when its source says the same.
His quotes: a script compared each quote of three words or more in the base with today's text, whitespace ignored. Quotes of the base that are not in today's file were moved by a later crystallize run. Each stands word for word in `roles.history.md` or `standing_rulings.md`.

| file | line read | verdict | what was done |
|---|---|---|---|
| operations.md (role) | the token-blind clause removed | SAME | none |
| operations.md (role) | the review-id sentence removed | SAME | none |
| operations.md (role) | "Record a Conductor instruction that you act on" | SAME | none |
| operations.md (role) | the Andon flag gloss | SAME | none |
| operations.md (role) | the 30-min reading gloss | SAME | none |
| operations.md (role) | "The cost is then fixed fast …" (removed later by the crystallize run) | SAME | none |
| operations.md (role) | "The lessons below are for diagnosis" removed | SAME | none |
| operations.md (role) | "File an item for the blind collector." | SAME | none |
| operations.md (role) | late split: the `revisit_quiet` re-arm | SAME | none |
| operations.md (role) | late split: the four cases of a clerk run | SAME | none |
| operations.md (role) | late split: the forecast bullet | SAME | none |
