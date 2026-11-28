# Boundary: a writing run files the blind review of new machinery

Code: `src/RimMandrake/rimflow/new_machinery_review.py`.
Tests: `src/RimMandrake/rimflow/selftest_new_machinery_review.py`.

## ACCEPTS

- **published-additions.** The writing run supplies its own published commit SHAs, oldest first, before it ends.
  A path is new when one of those commits adds it to origin/main and it is still present there. The current
  `pipeline_files` patterns define which paths are pipeline machinery. Detached runs identify themselves by unit.

## DOES NOT SURVIVE

- **a-run-that-does-not-file.** As with the fresh reader, the standing lines in the brief bind the writing run to
  file before it ends.
- **a-filing-that-cannot-land.** The tool returns the filing refusal. Retry with the same published commits.

## PROMISES

- **a-run-that-adds-a-pipeline-script-files-one-review-ticket.** One filing covers the run's new matching paths.
  It leaves out READ-CLEAN and FLAGGED paths and repeats of the same filing. Every brief carries the rule.
- **a-run-that-only-edits-files-none.** Modifications alone file nothing. Unmatched paths and paths no longer on
  origin/main file nothing.
- **the-lane-offers-the-review-ticket.** With room and the normal gates open, the lane starts a separate Opus Work
  run. The brief names the files, their boundary pages and their tests, and assigns `roles/code_review.md`.
  The dispatcher reads the page and test locations. The reviewer runs the tests and starts without the writer's
  history or diff.
- **the-ticket-check-holds-on-a-review-record.** Every named path must have a READ-CLEAN record on its present
  bytes or a FLAGGED record. The check distinguishes review debt from a reading it could not make.
- **the-writing-run-is-never-the-reviewer.** The ticket carries the writer's identity. The review starts in a new
  run, and its independence check refuses the writer.

## LIFE CYCLES

- The writer publishes its changes and files one ticket. The lane starts the blind review. A clean read records
  READ-CLEAN. A significant fix goes through the existing fresh-reader ticket. When every file has a record,
  the lane can close the initial review ticket.
