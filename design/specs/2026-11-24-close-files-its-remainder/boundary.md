# BOUNDARY: a close that names unbuilt spec parts files them first, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/close_remainder.py` (all of it); `src/RimMandrake/rimflow/cli.py` (`_remainder_gate`, the
`close` flags `--remainder` and `--no-remainder`); `src/RimMandrake/rimflow/detached_helper.py` (`file_remainder`, called by
`finish`, and the footer line); `src/RimMandrake/rimflow/model.py` (the `close` fields `remainder` and `noRemainder`).
Item: `RIMMANDRAKE_STOP_CLOSE_WHEN_RUN_SAYS_SPEC_PARTS_ARE_NOT_BUILT`. Why: twice on 2026-11-24 a detached run closed its
item on an acceptance check that tested less than the spec, and its own words listed spec parts as not built. The close
read the check alone. The remainder reached the list only because the Conductor filed it by hand. Each promise has a test
of its name in `src/RimMandrake/rimflow/selftest_close_remainder.py`.

## How it runs

At `rimflow close`, a program reads the closer's words (`--evidence`, `--no-code`, `--reason`, `--why`) and the last note
on the item since its last start. When they name unbuilt parts and no remainder is linked:

- a launched run gets a refusal that carries its repair: the filled `file` command and the same close again;
- the list tick and every other program close have no agent to answer, so the close files the remainder itself;
- the owner and the Conductor window get one NOTE line, and the close goes on.

At the end of a detached run that closed its item, `finish` reads the run's report. A report that declares unbuilt parts
with no remainder linked gets one ticket, filed by the program, with the report in a note on it.

## ACCEPTS (the only inputs this is built for)

- **the-closers-words.** English text of the ledger: the close's own flags, the run's last note, the run's report.
- **a-linked-remainder.** An item that the close names with `--remainder`, an item that the naming text names by its id,
  or an item `caused_by` this one, filed since its last start, whose id or title says remainder, unbuilt, unwired, not
  built or finish. A dropped item is not a remainder.

## DOES NOT SURVIVE (not promised)

- **a-silent-run.** A run that leaves a part unbuilt and says nothing. No program here compares the spec with the code.
- **other-words.** A part named as unbuilt in words outside the list in `close_remainder.py`.
- **a-false-no-remainder.** A run that says `--no-remainder` and is wrong. The reason is on the close event.
- **a-report-of-a-killed-run.** Only a run that ended success and closed its item is read at its end.

## PROMISES (each one is owed a test of the same name)

- **a-run-whose-evidence-names-unbuilt-parts-is-answered-with-the-repair.** The close is refused, the item is unchanged,
  and the answer holds the filled `file` command with `--caused-by` and the close again.
- **a-run-whose-last-note-names-unbuilt-parts-is-answered.** Only the last note since the last start is read; a `DETACHED
  run` note and an older note are not.
- **an-untested-spec-part-is-answered.** `Untested: a, b` is read only against the item's `## spec`: a part that shares two
  words with one line of the spec is asked about. An untested thing that the spec does not name is not.
- **the-same-close-passes-after-the-remainder-is-filed.** A filed `caused_by` remainder, `--remainder <ID>`, or the id in the
  words lets the same close pass. `--remainder` with no such item, a dropped item or the item itself is refused.
- **no-remainder-closes-with-its-reason-recorded.** `--no-remainder "<why>"` closes, and the event holds the reason. An
  empty reason is refused.
- **words-that-name-nothing-unbuilt-close-as-before.** "no part is unbuilt", "nothing left unbuilt" and plain evidence
  close with no extra step.
- **a-program-close-files-the-remainder-itself-and-closes.** The list tick's close writes one `file` (and a note with the
  words) and then the `close`.
- **the-owner-and-the-conductor-window-are-never-refused.** Their close goes on, with the note on the event.
- **a-run-end-files-the-remainder-its-report-declares-once.** One ticket for a done item whose report declares unbuilt
  parts. None with a remainder linked, with `noRemainder` on the close, for an item still open, or for a report that
  only mentions the word. A failure to file is named in the run's steps and never stops the finish.
