# RIMMANDRAKE_SHIELD_PYRE_WALK_FROM_FULL_LIST_EVENTS

## spec
`sc_walk` (walk_season, PYRE_WALK=1) on his 315-mod list, Pyrelands visit 2, 2026-11-21 01:54-02:01 PST, site
NS_Pyrelands_site_1_bf7f9e1fe4_visit2full (tile 38, gate B CLEAN). The run lasted 458 s and all 8 parts were UNMEASURED. The vitals guard
stopped safe_advance on three events from other mods on that list, none from Pyrelands:
1. tick 589361 (about 2.5 game days in): colonist Dietrich (Human76048) downed at health 1. The cause was not read. Heatstroke
   [guess ~40%]; a full-list mod's need or hediff [guess ~40%].
2. tick 592541: a hostile arrival, `VRESaurids_TownGuard_Saurid` (humanlike), under the quiet storyteller.
3. ticks 593021 and 593081: colonist Human76045 "hurt": health 1 -> 0.87 -> 0.73, newest hediff `SEX_Penis/SEX_Reproduction`
   age 0. That is a body-part hediff a full-list mod adds, which the guard reads as damage.
Evidence: design/concepts/Pyrelands/version/in_game/visit_2/evidence/pv2_walk_season.json, and the GOVERNOR_STOP lines
in the driver log (run_walk_season.log, Transient on the run's clone).
Fix: read cause 1 first (the downed pawn's hediffs at the stop). Then stage the walk colony against full-list events
(the arrival source, and a guard that does not count a hediff with no injury as hurt). The walk must not change.
## verify
python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains walk_season
(PYRE_WALK=1 through WSLENV, game a on his full list, a full-list site): walk_reload_keeps_the_state ends PASS or FAIL,
never "RESTART"/"surprise".
## criteria
Acceptance test: none offline. The events come only from his full list, live. The command above is red today (8 of 8 UNMEASURED,
measured 2026-11-21).
## refs
file: src/RimMandrake/Pyrelands/validation.py
file: src/RimMandrake/Utils/modcheck/governor.py
