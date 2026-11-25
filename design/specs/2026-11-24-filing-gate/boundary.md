# BOUNDARY: the filing gate (`filing_gate.py`), Design Version 0.3.0

Code: `src/RimMandrake/rimflow/filing_gate.py` (all of it); its two doors in `cli.py` (`_filing_door`, called by `_file`
and by `cmd_spawn`, with the flags `--not-now`, `--did-it` and `--not-worth-it`); the Stop hook
`.claude/hooks/filing_refusal_before_stop.py`; `detached_helper.filing_refusal_lines` and its use in `finish`.
Item: `RIMMANDRAKE_REFUSE_FILING_WITHOUT_EVIDENCE_WHY_NOT_FIX_IT_NOW`. Why: on 2026-11-24 three runs wrote up work in
place of doing the work. `CLAUDE.md` §Touching code has a cost (test 2) had the rule and no check. Each promise has a
test of its name in `src/RimMandrake/rimflow/selftest_filing_gate.py` (`t_`, and underscores for dashes), and each test
there is of a promise here. The hook has its own selftest, `.claude/hooks/selftest_filing_refusal_before_stop.py`.

## ACCEPTS (the only inputs this is built for)

- **a-filing.** The door (`file` or `spawn`), the id, the title, the kind of the ticket, the unit of the run that files
  it (`RM_ROLE_UNIT`, empty in a window), whether the filing carries the owner's authority (`--owner-said` or
  `--by-card`; `--per-ruling` alone is not his authority), the name of a program that files (`RM_FILING_PROGRAM`, set
  by the program in the env of its own cli call), and at most one of `--not-now`, `--did-it` and `--not-worth-it`.
- **a-headless-conductor-run.** A headless Conductor run carries `RM_ROLE_UNIT`, so the gate treats it as a helper. Only
  the Conductor window (no unit) is exempt.
- **the-state-folder.** `RM_DISPATCHER_STATE`, or else `/mnt/d/ClaudeWork/rimmandrake/dispatcher`. The refusals of a
  unit are in `<state>/filing_refusals/<unit>.jsonl`. A test process (`test_process.under_test()`) that has the real
  state folder files as a window: it writes no record into the real state. A test that brings its own state folder
  and sets a unit of its own gets the whole gate; the unit it inherited from its run (the `RM_ROLE_UNIT` in the launch
  env of its nearest test program, `/proc/<pid>/environ`) is not its own.
- **the-live-runs.** The units that `detached_helper` shows launching or running, or `None` when they cannot be read.
- **the-mod-folders.** A function that says if a folder of that name is in `design/concepts/` or `src/RimMandrake/`.
- **the-mod-of-the-run.** `RM_CONTROL_MOD` in the env of the filing unit's launch record (`detached_helper.py`; every
  maturation and Dispatch launch sets it), or `None` when the record cannot be read, has no such key, or says `none`.
- **a-sha.** For `--did-it`: what git says of it in the clone (`RIMFLOW_GIT_CWD`, or else the repository): it exists,
  it is on `origin/main`, and it changes a path that is not a ledger path. Or that git cannot be read.

## DOES NOT SURVIVE

- A run that gives false evidence in good form. The gate checks what a program can check. The count by class on the
  ledger shows a class that is used as a habit.
- An agent that sets `RM_FILING_PROGRAM` or `RM_UNDER_SELFTEST` in its own shell. The gate cannot tell that agent from
  a program or a test. The rule is that only a program sets them, in the env of its own cli call.
- A run that ends after the Stop hook let it go (two blocks). The run-end text still names each refusal.

## PROMISES

- **a-helper-work-ticket-with-no-evidence-is-refused.** A run with a unit files a work ticket with no `--not-now`:
  refused, exit 6. The refusal says to do the work now in this run, test first, and lists each class with one line.
- **the-refusal-is-a-path-to-pass.** The refusal text names the flag, each class and the form `<class>: <evidence>`.
- **evidence-of-a-known-class-files-the-ticket.** `--not-now "<class>: <evidence>"` with a class of the list and
  evidence of 12 characters or more that is not the class name again: filed, and the class and the evidence are
  recorded on the event (`not_now`).
- **an-unknown-class-is-refused.** A class outside the list is refused, "it is large" and "my work would not finish"
  included. The refusal lists the classes.
- **files-held-names-a-live-run.** Class `files-held` passes only when its evidence names a unit that is live.
- **other-mod-names-a-mod-folder.** Class `other-mod` passes only when its evidence names a mod folder that exists.
- **other-mod-refuses-the-mod-of-the-run.** Class `other-mod` whose evidence names only the mod of the filing run (any
  letter case) is refused (item `RIMMANDRAKE_REFUSE_OWN_MOD_HANDOFF_DRIVER_RENAMED_NOTHING`: on 2026-11-25 a visit
  driver filed the rename of 12 of its own mod's defNames as other-mod). The refusal says: fix the fault in this
  sitting, red test first; if the cause is unknown after a sincere attempt, file with `fix-unknown` and name what you
  tried. Evidence that also names another mod folder passes, and the other mod is recorded.
- **a-run-mod-that-cannot-be-read-is-not-a-refusal.** When the mod of the run cannot be read, `other-mod` is filed, the
  record says `could not look` (`own_mod`), and the door prints one note on stderr.
- **could-not-look-is-not-a-refusal.** When the live runs cannot be read, `files-held` is filed and the record says
  `could not look`.
- **the-owner-and-the-conductor-are-never-refused.** A filing with the owner's authority, and a filing from a window
  (no unit), pass with no flag.
- **per-ruling-alone-is-not-the-owner.** A helper that files with `--per-ruling` and no other flag is refused.
- **only-a-reminder-kind-passes-with-no-flag.** The kinds `owed`, `design`, `notice` and `alarm` pass with no flag: such
  a ticket holds a debt or a question, not work. Every other kind is work (`bug`, `task`, no kind, and each other word).
- **a-program-is-never-refused.** A filing by a named program (`RM_FILING_PROGRAM`) passes, and the name is recorded.
- **each-program-that-files-names-itself.** Each program that files through the cli sets `RM_FILING_PROGRAM` to its own
  module and function, in the env of that call, never in a shell.
- **the-door-calls-the-gate-before-it-writes.** `_file` and `cmd_spawn` call the one gate before they write the event,
  and record a resolution after it. Both doors take the three flags.
- **the-file-door-refuses-records-and-writes-nothing.** Through `cli.py file`: a refusal exits 6, records the refusal
  and writes no ledger event. Then a filing with evidence writes the event and resolves the refusal.
- **the-spawn-door-has-the-same-gate.** Through `cli.py spawn`: the same refusal, record and resolution.
- **every-refusal-is-recorded.** Each refusal writes one line `{"at", "unit", "id", "title", "kind", "why"}` to
  `<state>/filing_refusals/<unit>.jsonl`. A filing that passes writes no line.
- **a-record-that-cannot-be-written-never-changes-the-refusal.** When the line cannot be written, the refusal is the
  same, and one line on stderr says that the record failed.
- **filing-with-evidence-resolves-a-refusal.** A filing that passes, with the id of a refusal, records `filed`.
- **did-it-files-nothing-and-records-the-sha.** `--did-it <sha>` files nothing, prints
  `nothing filed: <ID> was done in this run at <sha>`, exits 0 and records `did`. A sha that does not exist, that is not
  on `origin/main`, or that changes only ledger paths is refused, exit 6.
- **did-it-reads-git-at-the-door.** Through `cli.py`, on a scratch git repository: a published work commit passes, and a
  ledger-only commit, a local commit and an unknown sha are refused.
- **a-sha-git-cannot-read-is-accepted-and-says-so.** When git cannot be read, `--did-it` is accepted, and the text and the
  record say `could not look`.
- **not-worth-it-files-nothing-and-records-why.** `--not-worth-it "<why>"` with a why of 12 characters or more files
  nothing, exits 0 and records `dropped`. A shorter why is refused.
- **one-way-at-a-time.** Two of the three flags at once: exit 2, nothing recorded.
- **unresolved-says-could-not-look.** `unresolved()` returns `None`, never an empty list, when the file cannot be read.
  A file that does not exist is no refusal.
- **a-test-with-the-real-state-files-as-no-run.** A test process with the real state folder files as a window.
- **a-unit-a-test-inherited-from-its-run-is-no-run.** A test process whose `RM_ROLE_UNIT` is the one that its nearest
  test program was launched with files as a window, with its own state folder too: a selftest run inside a helper
  inherits the helper's unit, and that unit is not the test's. A test that sets a unit of its own gets the whole gate.
- **the-run-end-names-each-unresolved-refusal.** `detached_helper.finish` adds one line
  `REFUSED FILING NOT RESOLVED: <id>: <title>` for each refusal not resolved, or `filing refusals: could not look (<why>)`,
  to its steps, its note and its wake.
- **the-stop-hook-keeps-the-run-until-each-refusal-is-resolved.** The Stop hook blocks a run that has a refusal not
  resolved, and names the id and the three ways. When each is resolved, it is silent.

## LIMITS

- Evidence of 12 characters or more, and a why of 12 characters or more. Danger: a one-word reason ("busy") passes.
  Evidence that it happens: none yet; the shortest true evidence is a unit name or a tool name with a verb, which is
  longer.
- The Stop hook blocks at most 2 times per unit (the same bound as `role_result_before_stop.py`). Danger: a run ends
  with a refusal not resolved. Then the run-end text names it to the Conductor.
- `--did-it` accepts a sha when git cannot be read. Danger: an unchecked sha. The record says `could not look`.
- A test that sets for its filing the same unit that its run has is read as a window. Danger: that test gets no gate.
  Evidence that it happens: none; the gate's own tests use units that no run has.
- Without `/proc` (not Linux), a test's launch env cannot be read, and a test with its own state folder that inherits a
  unit gets the whole gate. Danger: a red test on such a host. Evidence that it happens: none yet; the helpers seen
  here run on WSL2 Linux.
