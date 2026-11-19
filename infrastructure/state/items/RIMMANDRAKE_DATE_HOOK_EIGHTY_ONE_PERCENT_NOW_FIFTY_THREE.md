# RIMMANDRAKE_DATE_HOOK_EIGHTY_ONE_PERCENT_NOW_FIFTY_THREE

## spec
`.claude/hooks/block_delegated_cards.py` `message()` says, for a `scope` card: "29 such cards in 3 weeks were answered
with the recommended choice 81% of the time." That figure is from a keyword classifier over the 3 weeks to 2026-10-26
(`design/RimMandrake/delegation_candidates_2026-10-26.md` §1). The card store starts 2026-11-08, so those 29 cards
cannot be re-measured, and the figure is not shown to be false; it is undated, so it reads as current.
Re-run 2026-11-19 with the hook's own classifier over the card store (136 cards, 324 questions, 2026-11-08..19): 18
`scope` questions, 17 offered a Recommended option, he took it alone on 9 (53%); the questions that reach him now have
passed the hook, so they are the contested ones. Report:
`D:\ClaudeWork\rimmandrake\conductor\crystallize_2026W47\CYCLE_REPORT.md` §4; data
`D:\ClaudeWork\rimmandrake\conductor\crystallize_2026W47\scan\card_agreement_by_class.txt`.
Proposed text (the Conductor's call on wording): "29 such cards in the 3 weeks to 2026-10-26 were answered with the
recommended choice 81% of the time; of the 17 ordering questions that still reached him 2026-11-08..19 (mostly beside
other questions), he took the recommended choice alone on 9."
The module docstring's "Measured: 29 ordering cards (81% agreement) … in 3 weeks" gets the same date.

## verify
`python3 .claude/hooks/selftest_block_delegated_cards.py` stays green (the message is not measured prompt text, so no
`--remeasure`).

## criteria
The refusal message and the docstring date the 81% figure; no number in them is changed without a new measurement.

## Acceptance test
`grep -c 'to 2026-10-26' .claude/hooks/block_delegated_cards.py` prints at least 2 (message and docstring). Watched on
base `a65af6b919`: prints 0, exit 1.

## refs
Filed by the W47 lexicon and cycle-report helper, item `RIMMANDRAKE_RULE_LEXICON_SEVEN_TERMS_FOUR_RETIRED_ENTRIES`.
