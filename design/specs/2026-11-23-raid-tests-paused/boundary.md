# BOUNDARY: raid tests are paused (raid_pause.py), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/raid_pause.py` (the rule and the switch), `src/RimMandrake/rimflow/raid_pause.json` (the
switch), and its use in `src/RimMandrake/Utils/rimbridge_client.py` (every bridge call), `maturation.py` (`ingame_tests`,
`read_ingame_exit`, `ingame_facts`, the driver's brief, the walk brief, the pass), `src/RimMandrake/Utils/modcheck/suite.py`,
`runner.py` and `spoil_gate.py` (a chain, acceptance and verification), and `src/RimMandrake/Utils/testq/pipeline_admit.py`
(the test lane). Item `RIMMANDRAKE_ENACT_NO_RAID_TESTS_UNLESS_FORCED_CHEAPER_TEST_FIRST`. The rule:
`design/RimMandrake/standing_rulings.md` §The cheapest test that decides the bar. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_raid_pause.py`.

Words: a **raid** is a set of hostile pawns that attack by their own will: a raid incident, a mech cluster, or spawned pawns
under an assault or siege lord. A hostile pawn that a scene holds, places or moves by an order is not a raid. A **raid
scene** is a test of the test table whose `stages_raid` says what it stages. The **pause** is on while `raid_pause.json`
says `"paused": true`.

## ACCEPTS (the only inputs this is built for)

- **the-switch.** `raid_pause.json`: `paused` (true or false), `why`, `allow` (a list of item ids), `chains` (`{mod: {chain:
  what it stages}}`, the modcheck chains that stage a raid).
- **a-tagged-test.** `tests.<id>.stages_raid` of a test table: a text that says what the scene stages.
- **a-moved-part.** `bars_moved_to_next_version` and `scenes_moved_to_next_version` of a mod's `version/VERSION.json`: the ids
  of the bars and the scenes that left the version by his word (FlowWorks 0.1.0, 2026-11-23). The scenes are in no test table.
- **a-bridge-call.** A tool name and its arguments, as `RimBridge.call` takes them.

## DOES NOT SURVIVE (not promised)

- **a-raid-from-inside-a-mod.** A proof in a mod's C# that fires a raid itself makes no refused call. The table tag is the only
  stop for it.
- **a-call-inside-a-batch.** A raid call carried as data inside another tool's argument is read only when its text names the
  raid tool.
- **an-untagged-scene.** A raid scene with no tag starts, and stops at its first raid call with the PAUSED word. The tag
  is then owed on the table.
- **a-false-tag.** `stages_raid` is read as present, never as true.
- **a-fast-lift.** A process that read the switch before a lift keeps its reading until it ends.

## PROMISES (each one is owed a test of the same name)

- **raid-call-refused.** While the pause is on, the client refuses each of these before a byte is sent, with the word `PAUSED:
  raid tests wait for the tools`: `jawa/fire_raid` and `jawa/raid_shape_fire` unless `dryRun` is true; `jawa/fire_incident`,
  `jawa/storyteller_fire` and `jawa/incident_schedule` of a raid incident that are not dry runs; `jawa/spawn_mech_cluster`;
  `jawa/lord_assault_spawn`; `jawa/lord_set_job` to an assault or siege job; a debug action whose path names a raid.
- **other-calls-pass.** A dry run, a hostile pawn that is spawned or ordered, and a non-raid incident pass.
- **allowed-item-may-stage.** A process whose `RM_RAID_FOR` names an item of `allow` may stage a raid (the work that builds the
  raid tools). An item that is not in `allow` may not.
- **tagged-scene-does-not-start.** While the pause is on, a tagged stage-6 scene is not in `ingame_tests`, so no visit owes
  it, the driver's brief does not list it to run and names it as paused, its UNRUN lines are left out of the brief, and a
  visit that did not run it can meet its exit.
- **paused-is-its-own-word.** The exit reads a paused scene `PAUSED: raid tests wait for the tools`, in `paused_raids`, with its
  bars and the verdict of its last row. The word is none of PASS, FAIL and UNMEASURED. The scene makes no line, no
  undecided bar, no shortfall and no road back, so it spends no trial, turn, look or cycle, and does not pause its mod.
- **a-standing-pass-stands.** A paused scene whose last row is a PASS that the change since its commit does not touch, with no MOD
  FAILURE on that build and no UNRESOLVED run, reads `PASS stands`, and opens no bar. A same-build legacy `FAIL` classed `MOD`
  counts as a MOD FAILURE. A relation that cannot be read leaves the scene PAUSED.
- **open-raid-bar-holds-the-pass.** A bar that a raid scene decides is open while that scene has no standing pass, with the
  pause on or off. The version does not pass (`advance --to passed`) while a raid bar is open, unless
  `--conductor-decision` names each open bar.
- **walk-brief-names-it.** A walk brief that does not name each open raid bar is not written yet, and says which bar is missing.
- **moved-scene-is-owed-nothing.** A scene that moved to the next version is owed nothing, with the pause on or off: its UNRUN lines
  are left out of the brief, and an item that only its failed rows cite holds no visit (`visit_cited_items`).
- **walk-brief-names-moved-bars.** A walk brief that does not name each bar that moved to the next version is not written yet, and
  says which bar is missing.
- **chain-is-not-run.** While the pause is on, a chain listed in `chains` or stopped by a refused raid call records its
  skipped rows with `execution: not_run`. Those rows read `NOT_RUN` with the pause word in the acceptance report. The other
  chains go on, and verification counts only executed rows. The test lane refuses a job whose every chain is paused.
- **switch-unreadable-is-paused.** A switch that is missing or cannot be read is a pause, and its reason is named.
- **one-command-lifts.** `raid_pause.py lift --why`, `pause --why`, `allow ITEM --why` and `disallow ITEM --why` write the switch and
  land it. Exit 0 written and landed; 2 refused, nothing written (no why, or a role run); 4 written and not landed.
- **briefs-carry-the-rule.** The builder's, the driver's, the steward's and the Designer's briefs, the test pilot and the bridge driver
  carry the rule or its pointer.
- **census-lists-every-call.** `raid_pause.py census` lists each live script that names a raid call and each tagged test, with its
  bars and its last row. A script that cannot be read is named.

## LIMITS

None.

Lists beside this page: `polish.md`.
