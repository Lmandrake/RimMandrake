# Boundary: the fixing run files the fresh reader of its fix (`src/RimMandrake/rimflow/fresh_reader.py`)

Item RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX, part 7. His answer by card, 2026-11-26: "The fixing run files it
(Recommended)": a binding rule in every brief; the run files the reader as a ticket, and the ticket lane launches the
reader. Why: 5 of 6 fresh-reader runs in the 7 days to 2026-11-26 were launched by hand (the stuck-items study).

Code: `src/RimMandrake/rimflow/fresh_reader.py` (all of it), `src/RimMandrake/rimflow/fixer_rule.py` (`READER_LINE`,
`READER_RULE`), `src/RimMandrake/rimflow/list_dispatch.py` (`_reader`).

## ACCEPTS

- **a-fix.** The published sha of the fix and the repo paths of the files it fixed; the fixing run's unit
  (`RM_ROLE_UNIT`, else `RM_DETACHED_UNIT`).

## DOES NOT SURVIVE

- **a-run-that-does-not-file.** The rule binds by brief; a run that ignores it files no reader. The footer carries it to
  every detached brief.

## PROMISES

- **the-fixing-run-files-one-reader-ticket.** `file_argv` gives one `rimflow file` line: the id
  `RIMMANDRAKE_READ_FIX_<SHA>_WITH_FRESH_EYES` (a name that parses), a title that names the files, the sha and the
  maker, the check `fresh_reader.py holds`, and `--not-now independent: ...` (the filing gate's class).
- **the-lane-offers-the-reader-ticket.** The lane decides `launch` on a reader ticket whose check fails, and its Work
  brief carries the reader part: each file with its boundary page and tests, "You are not <maker>", and "Do NOT read
  the diff" and the earlier findings.
- **the-check-holds-on-a-review-record.** `holds` exits 0 when each file has a review record on its present bytes
  (READ-CLEAN, or FLAGGED by a reader that fixed), 1 when one lacks it, 2 when the record could not be read.
- **the-rule-is-in-every-brief.** `fixer_rule.READER_RULE` is in `detached_helper.FOOTER`; `READER_LINE` is word for word
  in `CLAUDE.md` and `design/RimMandrake/standing_rulings.md`.

## LIFE CYCLES

- **a fixing run:** publishes its fix → `fresh_reader.py file --fix <sha> <paths>` → a ticket with a failing check.
- **a lane tick:** `list_dispatch.decide` → `launch` → `brief_text` + `_reader` → one fresh Work run reads and marks.

Later lists beside this page: `polish.md` (none yet).
