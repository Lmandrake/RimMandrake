# BOUNDARY: ./publish returns a helper's polish line about its own changed file, Design Version 0.1.0

Code: `src/RimMandrake/Utils/polish_door.py`, called by `src/RimMandrake/Utils/publish.py` (`polish_door_check`, in
`_publish` before the door checks). Item: `RIMMANDRAKE_CLOSE_POLISH_AND_FOOTER_DOORS_SIXTEEN_FENCES_CONTRADICT`. Rule:
`CLAUDE.md` §Touching code has a cost (the polish rule). Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_polish_door.py`.

## ACCEPTS (the only inputs this is built for)

- **a-clone-with-an-origin.** A git clone whose landing target (`origin/main`) exists. With no such ref the run's own
  changes are unknown, and the door returns nothing.
- **bullet-lines.** A polish line is a Markdown bullet (`- ` or `* `) in a file named `polish.md`.

## DOES NOT SURVIVE (not promised)

- **a-line-that-names-a-file-by-its-stem.** A line that names `work_bundle` and not `work_bundle.py` (or the repo path)
  does not name the file, so it passes.
- **a-reworded-old-line.** A line that the run edits reads as new. If it names a changed file with no `risk:` part, it
  is returned like a new line.

## PROMISES (each one is owed a test of the same name)

- **a-helper-line-on-its-own-changed-file-is-returned.** A new polish line with no `risk:` part, that names a file the
  run changed (repo path, or file name as a whole word), is returned with the rule and the repair.
- **a-line-on-an-unchanged-file-passes.** A line that names only files the run did not change passes.
- **a-line-with-a-risk-part-passes.** A line with a `risk:` part (any letter case) passes.
- **a-record-line-passes.** A line that starts `record:` (the record of a done act, such as a removed check) passes.
- **a-run-that-is-not-a-helper-is-not-checked.** With neither `RM_ROLE_UNIT` nor `RM_DETACHED_UNIT` set (the Conductor,
  the owner), nothing is returned.
- **the-door-reads-only-the-runs-own-commits.** The door reads the lines and files of the local commits since
  `origin/main`, never an older line.
- **a-refused-landing-leaves-the-files-as-written.** `./publish` refuses, takes the run's commit off HEAD, and leaves the
  files as written. After the run does the polish, the same paths land.

## LIMITS

- Each git read has the call hang guard `time_budget.CALL_S` (a local read takes under 1 s): a hung git would hold a
  landing with no end.
