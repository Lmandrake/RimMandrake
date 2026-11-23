## spec
The rule: `design/RimMandrake/standing_rulings.md` §Live tests have three kinds (owner, 2026-11-23). Today the Stage 6 exit
reader (`maturation.read_ingame_exit`, `line_class`) knows three verdict words (PASS, FAIL, UNMEASURED) and three classes
(MOD, HARNESS, SITE). The rule then binds only in the prose of the driver's brief and of the skill
`live-debugging-proof-harness` (§The scene contract holds the interim way to write a row). This ticket makes the code read
the rule. What must change:

- **The kind tag on a test-table row.** `tests.<id>.test_kind` (A, B, C; absent is A), `tag_evidence`, `budget`, `x_of_y`.
  `kind` is taken (`live`, `live_full`). The exit refuses a B or C tag whose evidence is empty. The Designer's
  `roles/designer_scene_contract.md` and the pre-flight name the fields.
- **The seven outcomes in a row.** `outcome`, `spoiled_by`, `forbidden` in `rows.jsonl`. An unknown word is refused by name.
  An ENVIRONMENT FAULT with no `spoiled_by` reads UNRESOLVED. A forbidden effect reads MOD FAILURE in any run. RANDOM MISS
  exists only on a scene that is random by design. `build_match.carried_rows` keeps only the LAST row of an earlier visit:
  an UNRESOLVED row under a later one must still be seen.
- **INCONCLUSIVE as a scene verdict**, never PASS and never FAIL. The steward (`maturation_autonomy.steward_brief`) and the
  road back send such a scene to no earlier stage: the scene runs again, or the Conductor decides.
- **A spoiled last run** reads "run that scene again" (`spoiled`), not unclassed, not undecided bar, not a road back.
- **Kind C is out of the exit.** `ingame_tests` callers leave it out of the required checks and out of `to_run`.
- **The hunt's announcement.** `hunt_open.py ITEM --what --why-it-matters --next-step --cost`: one `HUNT OPENED` line,
  RAISE FIRST, in the Conductor log, plus the note on the item; a blank field is refused. Today the skill gives two commands.
- **Per-scene exits.** Built for earlier visits (`carried_rows`, `ingame_to_run`). Left: a visit that only waits on one
  scene names that scene; the list in `design/specs/2026-11-20-wrong-check-fixed-in-sitting/boundary.md` follows.
- **Repeats on one code version.** `src/RimMandrake/Utils/testq/retest.py` refuses a second run on one code version without
  `--retest-why`. A budgeted kind B run and a hunt step pass without it.
- **The loaded build.** `build_match.py identity` hashes the deployed folder. The rule asks for the build that the game had
  loaded. Acceptance test: none, the reading needs the live game.
- The boundary page for the new code comes first (CLAUDE.md §Code is clean when its promises are tested).

Found while the rule was propagated (RIMMANDRAKE_ENACT_THREE_TEST_KINDS_FORCED_COUNTED_HUNTED_NOT_STARS_ALIGNED). The
driver's brief already carries the kinds and no longer says "re-run EVERY check" (done there). Set down because it is a
change of the exit reader with a page of its own, and that run's brief says not to rebuild it.

## verify
`python3 design/specs/2026-11-23-three-test-kinds/accept_exit_reader_kinds.py` exits 0 with 16 rows ok.

## criteria
- Acceptance test, watched on the base 2026-11-23: 14 of 16 rows FAIL, the two `must_stay` rows ok. After the brief change
  of the same day, 13 of 16 FAIL.
- `selftest_wrong_check_fixed_in_sitting.py` and `selftest_maturation.py` stay green.
