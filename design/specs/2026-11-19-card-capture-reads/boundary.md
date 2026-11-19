# BOUNDARY: card_capture.py's reads, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/card_capture.py`. **This page covers only its reads of the outside world**: the 1 place
the could-not-look lint (`src/RimMandrake/Utils/could_not_look_lint.py`) finds there, read and classed on 2026-11-19 by
`RIMMANDRAKE_LAUNCH_LINT_READS_AFTER_HE_RULES_PAGE_STRICTNESS` (parent
`RIMMANDRAKE_ARM_COULD_NOT_LOOK_LINT_299_PLACES_ALLOWED`), and one read the lint does not see (`load`). Each promise has
a test of its name in `src/RimMandrake/rimflow/selftest_card_capture_reads.py`, and a planted fault that turns that
test red in `src/RimMandrake/rimflow/acceptance/lint_reads_dispatch_trio_breaks_accept.py`. The place's class and
reason is in the lint's allowlist, `src/RimMandrake/Utils/could_not_look_allowlist.json`, under `reasons`.

Owner, by card 2026-11-19 (the item's "What the card said"): a rare failure that breaks a promise is listed below as
not handled, and no fix is built.

## ACCEPTS (the only inputs the reads are built for)

- **card-times-from-the-transcript.** A card's `answered` is the transcript record's timestamp cut to 19 characters
  plus `Z` (`from_transcript`); a ledger event's `ts` is written by rimflow as `%Y-%m-%dT%H:%M:%SZ`. On 2026-11-19, 0 of
  135 stored cards and 0 of 2,888 `--by-card` ledger events had a time `_epoch` cannot parse.
- **a-store-appended-a-line-at-a-time.** cards.jsonl is appended whole lines by `save`.

## DOES NOT SURVIVE (not handled)

- **a-card-time-that-does-not-parse.** `_epoch` reads it as None, and `match` then skips the card, the same as no card
  answered in the window: a `--by-card` relaying that card is stamped with no card.
- **an-unreadable-card-store.** `load` reads a store that cannot be opened as no cards (it does not lint: the except
  body is `pass`), and skips a line that does not parse; `match` then finds no card.

## PROMISES (each one is owed a test of the same name)

- **answer-time-parses-or-is-none.** `_epoch` returns the epoch second for an ISO time and None for one that does not
  parse; never 0.
- **a-card-without-a-readable-time-is-never-matched.** `match("", [card])` takes a card answered a minute ago, and
  returns None when that card's `answered` does not parse.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
