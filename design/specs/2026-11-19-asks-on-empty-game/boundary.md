# BOUNDARY: the certificate's asks_on_empty_game clause, Design Version 0.1.0

Code: `_asks_on_empty_game` in `src/RimMandrake/rimflow/judge_certificate.py` and its adapters in
`src/RimMandrake/Utils/scene_empty_game.py`. Items: `RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED` (the clause,
FlowWorks adapter) and `RIMMANDRAKE_ADAPT_SUITE_SCENES_TO_EMPTY_GAME_FLOWWORKS_ONLY` (the modcheck Suite adapter and its
sandbox). Written 2026-11-19, when the Suite adapter extended the clause; it covers this clause only, not the rest of
judge_certificate.py. Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_asks_on_empty_game.py`,
each seen red on a deliberate break (the Suite adapter absent; the sandbox call removed). The clause keeps no state
between calls, so the page has no LIFE CYCLES.

## ACCEPTS (the only inputs the clause is built for)

- **a-version-test-table.** `design/concepts/<Mod>/version/test_table.json` with a `tests` map and a `bars` list; a bar's
  `decides` names live tests by id, each with a `file` and an `entry`.
- **two-scene-harnesses.** FlowWorks' `concept_scenes.py` (`STAGE3_SCENES`), and a mod file with a module-level modcheck
  `suite` (`validation.py`) whose live chain the test names as its entry. Anything else is named did_not_run.

## DOES NOT SURVIVE (not promised)

- **a-chain-that-needs-a-write.** A chain whose setup writes, deletes, spawns or connects is refused that act
  (PermissionError) and may list too few vacuous rows; the act is named in did_not_run, but its rows are not looked at.
- **a-file-that-spawns-at-import.** A suite file that runs a subprocess when loaded does not load: did_not_run, named.
- **a-sandbox-bypass.** ctypes, an already-open descriptor, or a C extension writing directly: the audit hook does not
  see them. No mod file here does either (2026-11-19).
- **a-chain-that-hangs-without-sleeping.** A busy loop outside the virtual clock runs to the child's timeout and reads
  did_not_run.

## PROMISES (each one is owed a test of the same name)

- **suite-run-writes-and-launches-nothing.** A Suite chain run on an empty game writes no file, makes no directory and
  starts no process, while its vacuous row still refuses the bar it decides.
- **refused-act-is-named.** Every act the sandbox refused is named in did_not_run, with its count; a refusal is never
  silent.
