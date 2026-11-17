# RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO

## spec
His words, 2026-11-17, after asking "What is step 7 in the maturation pipeline other than redundancy with
just-passed judges?": "Leave it as is, I justed wanted to understand. I approve your changes to the Step 6->Step 7
transition and preparation." (OWNER shard, this item's file event.) The Conductor's brief named this item
RIMMANDRAKE_FOLD_STAGE_SEVEN_JUDGE_INTO_WALK_BRIEF_NO_VETO; namecheck refused it (too long), so JUDGE was dropped.

The approved change, four points:
1. Stage 7 stops being a judging gate: no refusing verdict, no road back, no loop.
2. The BUILD MATCH is a program, no model, at the Stage 6 exit. Every in-game verdict records the game, the mod's
   source sha, a hash of its deployed folder, the active mod list (ModsConfig.xml activeMods, parsed, in order) and
   the game build. A verdict whose mod hash or game build differs from the build he walks does not count; its line
   item is re-run. A full-list test must match his walk's list exactly; a minimal-list test must match the list
   `modset_builder.py` builds for its tier from the same commit. Tests first: an offline selftest with a failing-first
   case and mutants.
3. ONE fresh read, by an agent that made none of the evidence writes, writes his walk brief: what to open, what changed
   since his last look, "known, not fixed: you need not report these", what it noticed first. No veto: findings go
   into the brief or onto a ticket.
4. Version numbering is unchanged; the rc count per arrival at Stage 7 stays.

Stage numbers stay. No mod design and no live game is touched.

## built
- `src/RimMandrake/rimflow/build_match.py` (`identity --mod M (--tier T | --full)`, `check --mod M [--visit N]`), read
  by `maturation.read_ingame_exit` and the `build_match` clause of `advance` out of `in_game`. Selftest
  `src/RimMandrake/rimflow/selftest_build_match.py` (`--mutants`).
- `maturation.py`: Stage 7 label "Walk brief", `pre_human` has no road back, its exit is the `walk_brief` clause
  (`read_walk_brief`, `evidence_writers`); role `src/RimMandrake/rimflow/roles/walk_brief.md`; autonomy steward line.
- Spec `design/specs/2026-11-13-maturation-pipeline.md` §2, §3, §4 Stages 6 and 7, §7; design doc
  `design/RimMandrake/maturation_pipeline.md`.

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_build_match.py
src/RimMandrake/rimflow/selftest_maturation.py src/RimMandrake/rimflow/selftest_maturation_autonomy.py
src/RimMandrake/rimflow/selftest_maturation_dispatch.py`, plus `selftest_build_match.py --mutants` and
`selftest_maturation.py --ingame`.

## criteria
- a row on another mod hash, game build or mod list does not count at the Stage 6 exit, and the exit names "re-run it";
- an unreadable walk build refuses the exit;
- `advance` from `pre_human` to `his_walk` refuses no brief, a missing or empty heading, no `written_by`, and a writer
  that made a move or an in-game row; it passes a valid brief with no `--steward-confirms`;
- `pre_human` has no road back; arrivals are still counted;
- every mutant of `build_match.py` is caught.

## not done (filed separately)
- The live drivers and SteveDesktop queue jobs do not yet merge the `build_match.py identity` fields into their rows;
  until they do, every existing in-game row reads "re-run it", as ruled.
