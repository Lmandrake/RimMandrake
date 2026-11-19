# BOUNDARY: designer_stage.py's reads, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/designer_stage.py`. **This page covers only its reads of the outside world**: the 38
places the could-not-look lint (`src/RimMandrake/Utils/could_not_look_lint.py`) finds there, each read and classed on
2026-11-19 by `RIMMANDRAKE_LAUNCH_LINT_READS_AFTER_HE_RULES_PAGE_STRICTNESS` (parent
`RIMMANDRAKE_ARM_COULD_NOT_LOOK_LINT_299_PLACES_ALLOWED`). The Designer's stage machine has no page of its own yet; its
loop ceiling's void counting is on `design/specs/2026-11-19-void-counters/boundary.md`. Each promise has a test of its
name in `src/RimMandrake/rimflow/selftest_designer_stage_reads.py`, and a planted fault that turns that test red in
`src/RimMandrake/rimflow/acceptance/lint_reads_promise_breaks_accept.py`. Each place's class and reason is in the
lint's allowlist, `src/RimMandrake/Utils/could_not_look_allowlist.json`, under `reasons`.

Owner, by card 2026-11-19 (the item's "What the card said"): a rare failure that breaks a promise is listed below as
not handled, and no fix is built.

## ACCEPTS (the only inputs the reads are built for)

- **concept-files-written-whole.** stage.json is written by `write_json` (a temp file, then `os.replace`); record.json,
  tree.json and the rest are written by runs and refused by `read_json` when they do not parse.
- **timestamps-this-module-writes.** Every `at`, `loop_since` and park time is `%Y-%m-%dT%H:%M:%SZ` (`now_iso`).
  Measured 2026-11-19: 0 of 527 such fields in the bench clone's stage.json files are in another format.

## DOES NOT SURVIVE (not handled)

- **an-owner-shard-with-no-readable-copy.** When neither the working tree's nor origin/main's OWNER.jsonl can be read,
  `owner_uncited` returns None and its callers read that as no uncited words (`or []`): `reopen_if_stale` adds none to
  `must_cite`, and the must-cite checks of `result_errors` (stage 2) and `close_run` pass.
- **an-off-format-stage-timestamp.** `epoch` and `_epoch` read a time in another format as None, and the callers read
  that as epoch 0: a charge or round is left out of the loop's spend, refusals and ceiling (`loop_spend`,
  `loop_void_spend`, `refusals_since_loop`, `ceiling_crossed_at`), a release before a rejection is missed
  (`rejection_parked`), and a park with no readable time counts every word of his (`his_word_since_park`,
  `pending_turn`).
- **an-unreadable-designer-schedule.** `designer_clone` reads None when `dispatcher_schedule.json` cannot be read, so
  `concepts_root` reads this clone's concepts.
- **a-concept-file-unreadable-but-present.** A file that exists but cannot be opened reads as absent: `sha_file` None
  (an input hash), `_read_sheet` None (an empty sheet in the control copy), `turn_file` None, and
  `entry_point_exists` False (the scene is refused with the wrong cause).

## PROMISES (each one is owed a test of the same name)

- **absent-is-default-unparseable-refuses.** `read_json(p, default)` returns `default` for an absent file and raises
  `Refused` for one that does not parse, so `read_json(...) or {}` reads only absence as empty.
- **unread-owner-shard-is-none.** `owner_uncited` returns None when no copy of OWNER.jsonl can be read, and `[]` when
  one was read and nothing is uncited for the item.
- **unread-ledger-is-said-in-the-packet.** When `done_items` cannot read the ledger, `built_evidence` adds the note
  "ledger UNMEASURED: done items not read" (`built_section` prints it beside `related_titles`, which reads the same
  memo); a read ledger with no done items adds no such note.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
