## spec
Owner, 2026-11-18: "If we just implemented 'a change I can veto' where it would be stopping currently known needed
work, then the rule we just implemented isn't useful. Please assess how it should actually be tuned given what we know,
or is the new rule actually harmful?"

MEASURED (read-only Opus replay 2026-11-18, evidence in `D:\ClaudeWork\rimmandrake\conductor\advance_rule_assessment_20261118\`):
- As coded the rule stops nothing. `refusal_contract.may_judge()` is read only by a selftest; `maturation.py advance`
  never asks it. A trip raises `REFUSAL_NOTHING_COULD_EVER_PASS` on `item:<mod>@<version>` and tells the Conductor.
- Limits: the 4th refused advance on a mod@version, or the 3rd refusal of the same check, with NO time window (the
  count lasts the version's life); family: over 70% refused of the last 20, or the last 8 all refused across 3 mods.
- Replay 2026-11-14 to 11-18: 34 advance results found, 33 moved, 1 refused (FlowWorks, check `order`), so it would
  never have tripped. 7 of 37 recorded stage moves were not found in transcripts: UNMEASURED; they cannot change
  the verdict (settle with `dispatcher\detached\*.out.json`).
- The suite's 0.75 reading is on a throwaway store and cannot ring the real alarm.
- It does not see the real loops of that week (Designer chaining Pyrelands 8 times; Pyrelands stage 4-5 spend).

FIX:
1. Pin `maturation_advance` as alarm-only: a trip tells the Conductor and never blocks an advance. Correct every
   comment and doc line that says it blocks.
2. Count per mod@version within a rolling 24 hours (4 refused in 24 h; the same check 3 times in 24 h), not for the
   version's life.
3. Do not count checks whose fix is a hand step waiting on a person (owner_said, steward_confirms,
   conductor_decision).
4. Family limits unchanged. The release verb is RIMMANDRAKE_EXPOSE_REFUSAL_RELEASE_VERB_CLEAR_UNREACHABLE.
RIMMANDRAKE_WIDEN_FAMILY_TRIP_MARGIN_SUITE_ALMOST_RANG is answered by this: the suite cannot ring the real alarm.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation

## criteria
Acceptance test, to be written first and watched failing on 13db68e8ed (not yet written): (a) 4 refusals 25 hours
apart do not trip; (b) 3 refusals of a hand-step check do not trip; (c) 4 refusals within an hour trip and tell the
Conductor, and a following passing advance still moves the stage; (d) empty history, an unreadable store and a
failed write each read as their own answer, never as "no trip".
