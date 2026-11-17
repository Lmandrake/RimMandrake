# RIMMANDRAKE_SPLIT_CARD_STAMP_FOUR_QUESTIONS_OVERFLOW_LEDGER_LINE

## spec

Measured 2026-11-16 11:38 PM PST: `rimflow note <ID> --by-card --text "..."` (bare, stamping the card just answered)
was refused for a four-question card: "event is 4770 bytes; O_APPEND is only atomic below 4096" even with a 50-byte
text. A full four-question card can never be recorded whole. The Conductor recorded it by hand as four
`--by-card "question → option"` notes. Fix: when the stamped card would pass the line limit, the stamp is split (one
event per question, each carrying that question, its picked option's description, his words and the other option
labels) or the card body goes to the card store with the event carrying its key; nothing of the card is dropped, and
`card_capture.py show <ID>` prints the whole card either way.

## verify

Acceptance test: a selftest that stamps a synthetic four-question card (each question 500 chars, three options of 340
chars) through the note and file paths: every event line is under 4096 bytes, and `card_capture.py show` returns all
four questions with the picked descriptions verbatim. Also: one-question card (unchanged, one event), a card with his
typed note, an empty card store (refuses by name). Fails on the base (the refusal above). Expected: all cases pass.

## criteria

- A card of the tool's maximum size records whole with a bare `--by-card`.

## refs

file: src/RimMandrake/rimflow/card_capture.py
