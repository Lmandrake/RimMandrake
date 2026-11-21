# BOUNDARY: card text that reaches a launched agent carries no spend talk, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/card_capture.py` (`for_brief`, `flatten(brief=True)`, `brief_missing`, `show`),
`src/RimMandrake/rimflow/spend_talk.py` (`strip`), and the two places that use them:
`stop_resume.with_card_text` and `detached_helper.card_refusal`. Item:
`RIMMANDRAKE_STRIP_SPEND_TALK_FROM_CARD_BRIEFS_HAND_CUT`, written 2026-11-19. On the Explosive Knockback rescue
(2026-11-17) the launch refused a brief that lacked the picked option's description verbatim, so the whole description
went in, and "keeps the accounts alive to Wednesday" reached the helper; a helper cut two other sentences by hand.
Owner 2026-11-16: no launched agent is told its spend. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_card_brief_spend.py`.

## ACCEPTS (the only inputs this is built for)

- **a-card-on-a-ledger-event.** A `card` dict on a ledger event of the item (`card_capture.item_cards`): questions with
  `question`, `picked` options (`label`, `description`), `others` (labels) and `his_words`.

## DOES NOT SURVIVE (not promised)

- **spend-talk-in-other-words.** `spend_talk.SPEND` matches dollar, token and percent-left figures, the words spend,
  spending, budget, quota and runway, a spend/token/budget cap, account levels and named accounts. A sentence that
  speaks of spend in other words ("it is cheap") passes. "Cost" and "spent" alone are not matched: a card's
  "Costs:" line is a trade-off, and "no trial is spent" is a ruling.
- **a-hand-written-brief.** A brief the Conductor writes is not filtered; only card text the tools paste or demand is.

## PROMISES (each one is owed a test of the same name)

- **show-gives-the-brief-text-without-spend.** `card_capture.py show <ITEM>` prints the card with every spend, token
  and account sentence out, and the rest of the card (question, labels, description, other options) kept.
- **show-whole-keeps-the-whole-card.** `show <ITEM> --whole` prints the card as answered, for a person.
- **with-card-text-adds-no-spend-sentence.** The text `stop_resume.with_card_text` adds to a brief holds no spend,
  token or account sentence.
- **every-needs-x-reaches-the-brief.** Each "needs X" a picked description states reaches the `show` text and the
  `with_card_text` brief, even when it stands in a spend sentence.
- **the-launch-asks-only-for-spend-free-text.** `detached_helper.card_refusal` passes a brief that carries the
  spend-free description, and the text it names as missing is only spend-free text. The launch itself never refuses
  for it: `card_repair` adds the text (design/specs/2026-11-20-owner-words-not-refused/boundary.md).

Later lists beside this page: `polish.md` (none yet).
