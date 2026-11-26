# BOUNDARY: the card re-ask gate, Design Version 0.1.0

Code: `.claude/hooks/block_reasked_card.py` (PreToolUse on AskUserQuestion) and `src/RimMandrake/rimflow/card_reask.py`
(the match and the census). Item: `OWNER_CARDS_HARDEN_DECISION_RECEIPTS`. Each promise has a check of the same name in
`.claude/hooks/selftest_block_reasked_card.py`, on real cards in `.claude/hooks/block_reasked_card_fixture.json`.

The receipt of an answer is its record in the card store that `card_capture.py` writes (every question, every option,
his pick and his words; the card's `key` and the question's index are the decision id). This gate reads those receipts
before a card reaches him. A question that asks again on purpose carries `[revision: <what changed since his answer>]`,
and the owner reads that reason on the card.

## ACCEPTS

- **an-askuserquestion-payload.** `tool_input.questions` is a list of objects with `header` and `question`.
- **the-card-store-of-this-host.** cards.jsonl under the agent storage root (`RM_CARDS_STORE` overrides), one card per
  line, as `card_capture.save` appends it.

## DOES NOT SURVIVE (not handled)

- **a-reask-in-other-words.** The match is word overlap (Jaccard of header + question content words, at least 0.25).
  On 2026-11-19 "Rounds" re-asked "Review loop" at 0.13 and would go through. A Sonnet read of the 3 closest
  lower-scoring questions was measured on 2026-11-25 and removed: it missed Rounds and refused 1 of 30 sampled
  questions that were right to ask.
- **a-ruling-he-gave-in-typed-words.** Only card answers are in the store. A ruling typed in a window is not read.
- **a-ruling-on-another-host.** Each host has its own store.
- **a-follow-up-that-shares-many-words.** Measured on the store 2026-11-25: 9 of 437 questions reach 0.25 against an
  earlier answered one; 2 are re-asks and 7 are follow-ups or new evidence. A follow-up pays one `[revision: ...]`
  marker.

## PROMISES

- **a-reask-of-an-answered-card-is-refused.** The 2026-11-19T03:14Z Judge order card, against the 00:34Z Gate order
  answer, exits 2.
- **the-refusal-shows-his-answer-and-the-path-to-pass.** The refusal names his answer, the card key and the
  `[revision:` path.
- **a-revision-marker-passes.** A `[revision: ...]` of 12 or more characters lets the question through.
- **a-bare-marker-is-refused.** A shorter `[revision: ...]` does not.
- **owner-asked-passes.** `[owner-asked]` lets the question through.
- **one-reask-among-new-questions-refuses-the-card.** The refusal names only the re-asked question.
- **an-unrelated-question-passes.**
- **an-unanswered-card-is-not-a-ruling.** A question he skipped (`[User did not answer`) does not count.
- **an-unreadable-store-lets-the-card-through-and-says-so.** Exit 0, with the cause on stderr.
- **an-unparseable-payload-passes.**
- **census-counts-an-already-ruled-answer.** `card_reask.py census` exits 1 and prints each answer in the window whose
  words say he had already ruled.
- **census-reads-zero-when-no-answer-says-so.** Exit 0.
- **census-could-not-look-with-no-answer-in-the-window.** Exit 2: no chance to see a re-ask is not zero re-asks.
- **census-could-not-look-on-an-unreadable-store.** Exit 2.
