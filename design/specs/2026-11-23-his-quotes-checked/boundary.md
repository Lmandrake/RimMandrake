# BOUNDARY: the check of the owner's quoted words

Code: `design/specs/2026-11-23-his-quotes-checked/extract_quotes.py`. Tests:
`design/specs/2026-11-23-his-quotes-checked/selftest_his_quotes_checked.py`. The procedure: `procedure.md`. The results
of 2026-11-23: `census.md` and `questions.md`. The calibration: `cases.md`.

His order, 2026-11-23: *"We should also have a dedicated process that checks my own quoted statements. They are not
immune from imprecise language."*

## ACCEPTS

- Markdown files of guiding prose (rule files, role files, judge briefs) that a person names on the command line.
- Three shapes of quote: ITALIC (`*"..."*`), PLAIN (`"..."` of three words or more near his name), CARD (the same near
  the word "card", or with an arrow).

## DOES NOT SURVIVE

- His words with no quote marks round them. The extractor does not list them.
- A PLAIN quote in a paragraph that never names him, and one of fewer than three words.
- A wrong date. The date that the extractor prints is the nearest date in the text. The ledger date is in `census.md`.
- A quote from before the records (September 2026 and earlier) often has no source left. Such a quote reads "source not found".

## PROMISES

- **three-shapes-are-found.** Each of the three shapes is listed.
- **a-bold-lead-never-swallows-a-quote.** A bold lead that starts with a quote mark is not an ITALIC quote, and a quote that
  closes inside bold is listed.
- **could-not-look-is-not-zero.** A file that cannot be read exits 2 by name. An empty file exits 0 with a measured zero.

By the procedure, not by a program (no test): no character of a quote changes; a TWO READINGS quote is never settled
without a source; a repair names the source that settles the reading.

## LIMITS

- Three words for a PLAIN quote. Danger: one-word and two-word terms flood the list. Evidence: the flood was not
  measured; the guard costs only short quotes that are not italic.

## Design note, not built: the same check at the moment a ruling is recorded

The cheapest moment to fix a loose word is while he is still in the conversation. Today a loose word waits for a later
pass, and its context is gone. The Conductor window does this when it records a new `--owner-said` ruling:

1. Name the kind: order, opinion, invitation or question. Only an order is recorded as a ruling. Anything else is a note.
2. Bind each noun, pronoun, bracketed number and time word to a thing on the screen: the item, the card option, the mod.
3. Look for earlier words on the subject: `owner_rulings.py --last 0 --grep <subject>`. Name each one that the new
   words replace or narrow.
4. Read the precise reading back to him at once, in one line, in the reply that he is already getting. Form: "I read
   that as: <the act>, on <the things>, until <when>. It replaces <date, words>." Add "Say no if I have it wrong." Do not
   wait for an answer, and do not ask a card for it.
5. If two readings lead to different acts, the line is a question with both acts in it. It goes to him in that same reply.
6. Record his words as he typed them (`--owner-said`). Record the reading beside them (`--why`). Record also: the words that
   an ellipsis removes, and the text of any card option that he names by number.
7. Write the rule line from the reading, in the same commit that quotes him. A correction from him replaces the reading.

It refuses nothing. The act goes on (`standing_rulings.md` §His word and the Conductor's act are not refused). Seven of
the faults of 2026-11-23 would have been caught by step 3 alone. Where it joins: the write-time prose check,
`RIMMANDRAKE_CHECK_GUIDING_PROSE_AT_WRITE_NO_SEARCHING_FOR_MEANING`, after that check is built.
