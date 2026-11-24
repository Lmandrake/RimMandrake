# BOUNDARY: the scene size check (scene_size.py), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/scene_size.py`, its list `src/RimMandrake/rimflow/scene_size_known.json`, and its use in
`src/RimMandrake/rimflow/maturation.py` (the in-game driver's brief) and `src/RimMandrake/Utils/publish_tree_checks.json` (the door).
Item `RIMMANDRAKE_SPLIT_PYRELANDS_SEASON_WALK_TO_MINIMUM_TESTS`. The rule: `design/RimMandrake/standing_rulings.md` §The cheapest test
that decides the bar. Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_scene_size.py`.

Words: a **live test** is a stage-6 entry of a test table with a kind that starts with `live`. An **oversized** live test plays more
than one game day, runs on the full list, or holds more than one claim. Its **evidence** is the field `cheaper_why`.

## ACCEPTS (the only inputs this is built for)

- **a-test-table.** A `design/concepts/<Mod>/version/test_table.json` with a `tests` object.
- **a-declared-size.** `claims` (a list of sentences) and `game_days` (a number) on an entry.
- **a-python-scene.** An entry whose `file` is a .py file and whose `entry` is a function in it.

## DOES NOT SURVIVE (not promised)

- **a-false-cheaper-why.** The evidence is read as present, never as true. A reviewer reads what it says.
- **a-span-outside-the-file.** Waits in another file, in C#, or of a length that is no constant are not counted. The span is a floor.
- **claims-in-prose.** An entry that declares no `claims` and has fewer than five clauses reads as one claim.

## PROMISES (each one is owed a test of the same name)

- **old-walk-is-red.** The Pyrelands table of 2026-11-23 reads `sc_walk` oversized by its span, its list and its claims.
- **new-scenes-are-green.** The Pyrelands table now reads none of `sc_reload_keeps_the_burn`, `sc_fire_sense` and
  `sc_full_list_smoke` as owing evidence. The span and the single claim of the reload scene are small by themselves.
- **evidence-clears.** A test with a `cheaper_why` that is not empty owes nothing.
- **span-is-counted.** Constants, loops with a constant count and called helpers count. A loop or a wait that is no constant
  counts as unread. A missing file, function or syntax reads UNMEASURED.
- **declared-size-wins.** `game_days` and `claims` replace what is read.
- **one-day-and-one-claim-pass.** Exactly one game day, and one claim, are not oversized.
- **full-list-is-refused.** A test that asks for the full list is refused, whatever its evidence and whatever the known list says. The one
  exemption list, `FULL_LEFT`, names a test that still stands, with its reason.
- **known-is-not-new.** A listed test is not new. A listed test that grows is new.
- **tree-is-clean.** The tables in this tree hold no new oversized test.
- **unreadable-is-could-not-look.** A table or a list that cannot be read exits 2, never 0.
- **brief-names-them.** The in-game brief lists each oversized test of the mod with its repair, and shows a test's `cheaper_why`.

## LIMITS

- **SPAN_DAYS, one game day.** Danger: past a day, needs, wild animals and arrivals spoil the scene. Evidence: Pyrelands visits 2,
  5 and 8; the comment beside the number.
- **CLAUSES, five.** Danger: a scene that decides many things loses them all when one is spoiled. Evidence: `sc_walk`, seven
  clauses, every part UNMEASURED in visit 2 and in visit 8 run 1.

Lists beside this page: `polish.md`.
