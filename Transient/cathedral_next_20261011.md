# Cathedral arc: next offline slice (2026-10-11)

## pick
CATHEDRAL_EXPOSURE_COMPLETION_1. Its prerequisites are on origin: item 1 (CATHEDRAL_REGARD_BLACKBOARD_1, built)
and item 3's linter (CATHEDRAL_STAGE_COMMENTARY_POOLS_1, built e1abc3b8b). It was the one item whose owed offline
work, a linter run over its own strings, could be proven without a bridge.

## why the others wait
- CATHEDRAL_MISSION_BOON_OFFERS_1 and CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1 are now unblocked on items 1 and 3,
  but both still depend on the CQF-vs-thin-config reconciliation (the quest surface), and the survey quest also
  needs the kyber §3 pursuit-spine Act I dressing. Their criteria are quicktest-only.
- CATHEDRAL_DESCENT_REVEAL_SITE_1 depends on item 4 (VOUCHED earnable), the restore-choice flag and structure
  injection through the bridge.

## build
- `src/RimMandrake/Utils/gm_blackboard_shadow.py`: 4 of 4 fall letters failed the linter (3 named the place,
  1 said "living memory" before the reveal). They are rewritten. The chain step is extracted to
  `ShadowBlackboard.advance_fall_chain` (no bridge). The toggle is `--disable-cathedral-fall` / `fall_enabled`.
- `src/RimMandrake/Utils/selftest_gm_cathedral_fall.py`: new.

## proof
selftest_gm_cathedral_fall.py 32/32: the strings lint clean, with failing controls. The ordering holds: no fall
without go-dark, none below the threshold, one stage per poll, completion once. The extraction is gated, priced,
floored and refusable. Faction-13 is never turned on the player. The toggle is off-clean.

## still owed
A live shadow-mode run on a quicktest campaign (bridge). The letters are not wired to an injection lane yet. The
ending handoff to CAMPAIGN_STORY_SITTING_1. The owner's one-line confirmation of the faction-13 scope split.
