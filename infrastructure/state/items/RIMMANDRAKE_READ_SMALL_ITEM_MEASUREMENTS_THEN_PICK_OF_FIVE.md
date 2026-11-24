# RIMMANDRAKE_READ_SMALL_ITEM_MEASUREMENTS_THEN_PICK_OF_FIVE

For the Conductor. Read the 7-day measurements of the five small items of the agent-work census, then decide which of the
five waiting items goes next. The owner, 2026-11-23, evening PST: *"let's accept the small ones into the build pipeline,
while postponing the medium and large items until we learn from the small ones."* Source:
`design/specs/2026-11-23-agent-work-to-code/` (`one_page.md`, `analysis.md`, `census/`, `acceptance/`).

## spec

**Small items, in the build pipeline now:**

| rank | item | reading (census/window.py key) | baseline, week to 2026-11-23 7:56 PM PST `[measured]` | guessed saving in a week | must not get worse |
|---|---|---|---|---|---|
| 3 | `RIMMANDRAKE_FILL_COMMANDS_INTO_BRIEFS_HELP_ASKED_2807_TIMES` | `help`, `help_ledger_verbs` | 2,807 turns 51.3M; 1,136 turns 23.0M | 20M `[guess ~50%]` | wrong-flag turns: 346, 6.1M |
| 5 | `RIMMANDRAKE_CARRY_RESULT_IN_CONDUCTOR_WAKE_408_FILES_OPENED` | `fetch_result`, `report_after_fetch`, `state_reads`, `wake_reading` | 408, 170, 560, 564 turns; 54.8M | 18M `[guess ~55%]` | results that nobody acted on (the builder counts the baseline) |
| 6 | `RIMMANDRAKE_PASTE_ITEM_HISTORY_INTO_BRIEFS_1503_SHOWS_CUT` | `show`, `raw_ledger` | 1,615 turns 41.9M; 814 turns 15.5M | 15M `[guess ~50%]` | work done twice (the builder counts the baseline) |
| 7 | `RIMMANDRAKE_LENGTHEN_WAITS_UNDER_ONE_HOUR_CACHE_DIES_AFTER` | `wait`, `wait_repeat` | 2,260 turns 43.0M; 501 turns 7.9M | 8M `[guess ~40%]` (12M in the analysis, before the cache was measured) | `cache_rebuilt_after_gap`: 23 turns, about 18.5M; hung jobs found late |
| 10 | `RIMMANDRAKE_TIE_LIFE_SIGN_TO_PROCESS_484_HAND_NOTES` | `progress_note`, `lease_renew` | 484 turns 14.3M; 202 turns 7.5M | 8M `[guess ~55%]` | leases that lapsed under a live run; stopped runs with no state |

The baseline has 1,908 runs. Compare per 100 runs, never the bare sum of a week. The ten pools overlap: the savings do not
add up.

**Waiting items, for this decision:**

| rank | item | size | guessed saving in a week |
|---|---|---|---|
| 1 | `RIMMANDRAKE_BUILD_ONE_LANDING_COMMAND_215_FORM_REFUSALS` | medium | 35M `[guess ~60%]` |
| 2 | `RIMMANDRAKE_BUILD_VISIT_AND_CYCLE_KITS_SEVENTEEN_COPIES_TODAY` | large | 22M `[guess ~55%]` |
| 4 | `RIMMANDRAKE_BUILD_ONE_TEST_CALL_PARENT_FIX_AND_FAULT` | medium | 20M `[guess ~50%]` |
| 8 | `RIMMANDRAKE_MOVE_STAGES_BY_PROGRAM_REVERSES_A_WRITTEN_NEVER` | medium; also needs a ruling, because it reverses "the program never advances" | 10M `[guess ~50%]` |
| 9 | `RIMMANDRAKE_GATHER_ALARM_FACTS_BY_PROGRAM_MOST_END_ACKED` | medium | 10M `[guess ~50%]` |

**The act.**

1. For each small item that closed at least 7 days ago, run the command of its section "How we measure that it helped". An
   item that is not built, or not 7 days old, reads "not measured yet", with its date. A count that could not be made reads
   "could not look", with the cause; it is not "no saving".
2. Write `design/specs/2026-11-23-agent-work-to-code/small_items_measured.md`: one row for each item (baseline, after, the
   change per 100 runs, the number that must not get worse, and what was learned about how good the guesses were).
3. Decide which waiting item goes next, with the guesses corrected by what the small items showed. Write one line that
   starts `DECISION:`. Then `rimflow unwait` that item, so the List Pipeline starts it; move the dated wait of the others.
4. Rank 8: if the decision is to build it, ask for the ruling or make it as the Conductor's act, and shape the item again
   without its routed part. Its prose quotes the five lines that it reverses.

Tell him the result in his daily digest.

## verify

`path-has:design/specs/2026-11-23-agent-work-to-code/small_items_measured.md::DECISION:` (the file does not exist on
2026-11-23, so the check fails: seen). Acceptance test of the reading itself: none, it is a judgement over measured counts.

## criteria

- Each small item has a row: a measured change, "not measured yet" with its date, or "could not look" with its cause.
- The file holds the line `DECISION:`, and the waits of the five items agree with it.
