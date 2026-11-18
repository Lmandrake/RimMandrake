## spec
The auto re-pin (designer_stage.repin_sources -> commit_cards) never cites a card of his given AFTER the commit it approves, so its own refusal's smallest fix ("a ledger event on the card's item naming its sha") is not attainable for an after-the-fact approval. Measured 2026-11-18 on Graffiti, in a throwaway clone: with the note "carried out by 6c7d175b5270" on RIMMANDRAKE_REPIN_GRAFFITI_SOAK_FIX_AFTER_WEDNESDAY_RESETS (his card OWNER:1794965084756269804, 01:24:44Z, after the 18:35Z commit), a hand `repin --dry` passes (stages [3, 4]) but repin_sources still refuses "1 of 1 commits ... carry out no card of his".

Fix: in commit_cards, a card given after the commit is cited by the third tie only (a ledger event on its item naming the sha), only when that event was written after the card (the record that this card approves that commit), and only when no card given before the commit ties. The exam-card guard of check 6 (a later card on the same item never borrows an earlier note) stays.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_repin.py   # rc 0, no FAIL line; group 8 red on base a907fc6756 (2 FAIL)

## criteria
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_designer_repin.py` — new check group 8 (late_approval_checks). Watched failing on base a907fc6756: 2 FAIL ("8 after the note on his late card's item, the auto re-pin cites that card", "8 the late card's source passes repin itself"); "8 a note older than the card cites nothing" passes on base and must stay passing. Pass = rc 0, no FAIL line.
