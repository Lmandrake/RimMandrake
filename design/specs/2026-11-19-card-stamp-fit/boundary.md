# BOUNDARY: a stamped card always fits the ledger line, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/cli.py`, the card stamp in `_write_one`: `_split_card`, `_fit_card` and `_line_probe`.
Item: `RIMMANDRAKE_FIX_CARD_STAMP_OVER_LEDGER_LINE_LIMIT` (filed 2026-11-19 after a bare `rimflow file --by-card` was
refused four times: "event is 8772 bytes; O_APPEND is only atomic below 4096"), fixed by
`RIMMANDRAKE_KEY_AUTO_FILERS_ONE_FAULT_ONE_TICKET` on 2026-11-19. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_card_capture.py`. Each test except `a-card-that-fits-is-stamped-whole` (a
must-stay-green guard) was seen red on the code before the fix. Five planted faults in the code each turn at least one
test red. Tonight's real card (three questions, his typed answer on the first) is refused at 6855 bytes by the old code.
The new code records it, longest line 3492 bytes.

Cause: `_split_card` puts each question on its own event. But one question can be over the line by itself: his typed
answer is stored as both `answer` and `his_words`, and a bare `--by-card` copies it again into the `byCard` summary.

## ACCEPTS (the only inputs the stamp is built for)

- **an-answered-card.** A card from the card store (`card_capture.find`), with `questions` that each hold `question`,
  `answer`, `his_words`, `picked` (label and description) and `others`.

## DOES NOT SURVIVE (not promised)

- **picked-descriptions-over-a-line.** Picked descriptions are never cut, because the brief and close gates
  (`card_capture.descriptions`, `consequences`) read them on the events. One question whose picked descriptions alone
  are over a ledger line is still refused, as before.
- **the-side-file-is-local.** A fitted text keeps its head and a pointer on the event. The whole text is in the
  fulltext side store, which is on this host only. Other hosts get the whole card from the item's prose, which is
  committed with the shard. A closed item gets no prose.

## PROMISES (each one is owed a test of the same name)

- **a-card-over-one-line-records.** A card whose single question is over a ledger line records with a bare
  `--by-card`, as one event when the card has one question, and every ledger line stays under 4096 bytes. The question,
  answer and his words are fitted largest first, then the `byCard` summary, each as its head plus a pointer to the
  whole text.
- **the-whole-card-reaches-the-item-prose.** The item's prose holds the whole card (his whole typed answer, the whole
  question, every picked description), whether the card was split, fitted, or both.
- **picked-descriptions-stay-whole-on-the-events.** Each picked description is whole on an event card, including on
  a question that was fitted.
- **a-card-that-fits-is-stamped-whole.** A card that fits one line is stamped unchanged, with nothing cut.
