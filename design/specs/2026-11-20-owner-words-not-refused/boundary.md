# BOUNDARY: the owner's word and the Conductor's act are not refused for provenance, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/detached_helper.py` (`card_repair`, the I3 step in `_launch`),
`src/RimMandrake/rimflow/promise_scan.py` (`covered`, `scan(owed_items=)`), `src/RimMandrake/rimflow/owed.py`
(`safe_banner_and_items`), `.claude/hooks/conductor_goodbye.py` (`untracked_lines`), `src/RimMandrake/rimflow/model.py`
(`his_or_conductor`, `close_refusals(word=)`, `_fold_close_gate`) and `src/RimMandrake/rimflow/cli.py` (`_close_gate`,
`cmd_close`, `_check_owner_said`), `src/RimMandrake/Utils/conductor_authority.py` (`carried`, `words`).
Item: `RIMMANDRAKE_STOP_GATES_DEMANDING_OWNER_WORDS_HE_ALREADY_SPOKE`, written 2026-11-20. Rule:
`design/RimMandrake/standing_rulings.md` §His word and the Conductor's act are not refused. Census of every site:
`D:\ClaudeWork\rimmandrake\conductor\night_20261120\owner_words_gates_census.md`. Each promise has a test of its name
in `src/RimMandrake/rimflow/selftest_owner_words_not_refused.py`.

## ACCEPTS (the only inputs this is built for)

- **a-by-card-item.** An item with a `card` on a ledger event (`card_capture.item_cards`), and any brief for it.
- **an-open-owed-item.** A BENCH item of kind `owed`, open, with a title and an optional `caused_by`.
- **a-close.** `rimflow close <ID> --sha <sha>` with `--owner-said`, `--by-card`, `--per-ruling <ref>` or none of them,
  from the Conductor window (seat BENCH, no `RM_ROLE_UNIT`) or from a launched run.

## DOES NOT SURVIVE (not promised)

- **an-older-reader.** A clone whose `model.py` predates this page folds a lifted close (`uncheckedLifted`) as an
  error, and the item stays open there until that clone syncs.
- **a-paraphrased-promise.** A promise worded far from its owed item's title, and not naming its `caused_by` item, is
  still shown in the note.

## PROMISES (each one is owed a test of the same name)

- **launch-adds-card-text.** `detached_helper.launch` never refuses a brief because it lacks the card's words, for any
  caller. `card_repair` appends `## What the card said` and the card's whole spend-free text when a picked description
  is missing, leaves a brief that carries it unchanged, and leaves an item with no card untouched.
- **note-silent-if-covered.** `promise_scan.scan` stays silent on a promise that names the `caused_by` item of an open
  owed item, or holds most of an open owed item's title words. A promise no owed item covers still shows. The
  per-prompt hook prints it as a note (`NOTE, nothing blocked: …`), never as a demand to file or to answer.
- **close-conductor-act.** A close from the Conductor window with `--per-ruling
  RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`, or with his `--owner-said` or `--by-card`, is not refused for a
  missing level-tagged pass; the close event records `uncheckedLifted: true`. Since 2026-11-21 no closer is refused
  for it (a fault of form: design/specs/2026-11-21-repair-at-the-refusal/boundary.md): a seat's own close and a close
  citing another ruling go too, recorded the same way. Still refused (planted in the test): a launched run citing the
  Conductor's ruling (that ruling's own gate).
- **his-question-is-recorded.** `rimflow … --owner-said "<his words>"` records his words as typed, a quote ending in
  "?" and a bare assent ("yes") included; neither is refused. An assent with no `--why` prints one note line.
- **either-conductor-ruling.** `conductor_authority.carried` takes `CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` or
  `RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS` with the Conductor's text; any other ruling, or no text,
  carries nothing.

Later lists beside this page: `polish.md` (none yet).
