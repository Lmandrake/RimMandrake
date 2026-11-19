# BOUNDARY: the close-out's matching of his sentences to ledger quotes, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/conductor_closeout.py` (`covered`, `ledger_quotes`, `unquoted`). Item:
`RIMMANDRAKE_FIX_FOUR_SMALL_DEFECTS_FOUND_AT_TODAYS_WAKE`, written 2026-11-19. At that day's wake `check` reported his
message "No need to track Augur. Drop that. Acts census. Two cards. Phone alert discussion. Then Crystallize for real
this time." as "partly on the ledger; no quote for: drop that / acts census / ..." although OWNER.jsonl held the whole
message word for word (2026-11-19T20:06:10Z, item `RIMMANDRAKE_REVIEW_OWNER_ONLY_ACTS_WITH_HIM_THEN_CRYSTALLIZE`): the
negation guard compared each short sentence with the whole quote, whose "No need" made the counts differ. A message
whose ledger copy had a phone typo fixed ("mosto f" to "most of") was listed as a full gap for the same reason (its
"don't" sat in one sentence of the quote). Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_conductor_closeout.py`. This page covers only the matching; the rest of the close-out
(transcript reading, dismissals, the restart request) has no page yet.

## ACCEPTS (the only inputs this is built for)

- **his-message-text.** One message of his as the transcript holds it, cut into sentences at `. ! ? ; :` followed by
  space, or at a line break; a question is not owed a quote.
- **owner-said-quotes.** Every `ownerSaid` string on every ledger shard, with its event time, read the same way: the
  whole quote and each of its sentences.

## DOES NOT SURVIVE (not promised)

- **a-short-sentence-with-a-split-typo-and-other-errors.** A sentence under four words whose quote fixes a typo other
  than where a space falls stays a gap until dismissed (the safe side).
- **a-quote-rephrased.** A quote that says his meaning in other words is not his words; it stays a gap.

## PROMISES (each one is owed a test of the same name)

- **a-short-sentence-inside-a-quoted-whole-matches.** A sentence of his message, of any length, that is a sentence of a
  ledger quote made at or after it is recorded, even when another sentence of that quote holds a negation his sentence
  does not ("Drop that." inside "No need to track Augur. Drop that.").
- **a-typo-fixed-quote-matches.** A sentence whose quote differs only by fixed typos is recorded: four or more words in
  the same order at a word ratio of 0.85 or more against one sentence of the quote or the whole quote, or the same
  letters with only the spaces moved ("mosto f" for "most of"), also when the quote holds his other sentences.
- **a-message-absent-from-the-ledger-is-a-gap.** A message none of whose sentences is on the ledger at or after it is
  listed as a gap (exit 1), whatever other quotes the ledger holds.
- **a-quote-that-loses-his-negation-does-not-match.** A quote, or a quote sentence, whose count of negations differs from
  his sentence never records it unless it is word for word the same sentence ("Drop that." is not recorded by "Never drop
  that.").

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
