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
  `RIMMANDRAKE_READ_FIX_<SHA>_WITH_FRESH_EYES` (a name that parses; or the twin id that `resolve` names), a title that names the files, the sha and the
  maker, the check `fresh_reader.py holds`, and `--not-now independent: ...` (the filing gate's class).
- **the-lane-offers-the-reader-ticket.** The lane decides `launch` on a reader ticket whose check fails, and its Work
  brief carries the reader part: each file with its boundary page and tests, "You are not <maker>", and "Do NOT read
  the diff" and the earlier findings.
- **the-check-holds-on-a-review-record.** `holds` exits 0 when each file has a review record: READ-CLEAN on its present
  bytes, or FLAGGED (by the reader that fixed, on its present bytes; or before a later fix changed it, since nobody
  reviews a FLAGGED file again and its weekly examination reads it), 1 when one lacks it, 2 when the record could not be
  read.
- **a-reviewed-file-is-owed-no-reader.** `file` leaves out each file whose `holds` is 0 already (READ-CLEAN on its
  present bytes, or FLAGGED). When no file is left, it files nothing, prints `no reader owed`, and exits 0. The filing
  gate would refuse that ticket, because its check holds when it is filed.
- **a-second-filing-for-one-fix-is-not-a-refusal.** Before it files, `file` reads the reader tickets of the ledger, in
  any state (`reader_tickets`), and `resolve` takes out each file that a reader ticket of the same fix names already.
  When none is left, it files nothing, prints `already filed: <ticket>`, and exits 0. The files left are filed under the
  fix's own id, or, when a reader of that fix took that id already, under its twin
  `RIMMANDRAKE_READ_FIX_<SHA>_<6 hex of the files>_WITH_FRESH_EYES` (a name that parses). A ledger that cannot be read
  leaves the filing under the fix's own id. Seen 2026-11-27: the reader of b553269938 existed, and the bundle's filing and
  the hand act that it named were both refused, exit 2, the name exists.
- **the-rule-is-in-every-brief.** `fixer_rule.READER_RULE` is in `detached_helper.FOOTER`; `READER_LINE` is word for word
  in `CLAUDE.md` and `design/RimMandrake/standing_rulings.md`.

## LIFE CYCLES

- **a fixing run:** publishes its fix → `fresh_reader.py file --fix <sha> <paths>` → a ticket with a failing check.
- **a lane tick:** `list_dispatch.decide` → `launch` → `brief_text` + `_reader` → one fresh Work run reads and marks.

Later lists beside this page: `polish.md` (none yet).
