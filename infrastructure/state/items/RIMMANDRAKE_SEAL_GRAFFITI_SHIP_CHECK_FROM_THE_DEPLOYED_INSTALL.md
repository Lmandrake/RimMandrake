# RIMMANDRAKE_SEAL_GRAFFITI_SHIP_CHECK_FROM_THE_DEPLOYED_INSTALL

## spec
Graffiti's offline test table row T_SHIP_CHECK (`python3 src/RimMandrake/Graffiti/ship_check.py`, kind offline) reads the
DEPLOYED install, not the repo: on 2026-11-22 (red census, RIMMANDRAKE_CENSUS_RED_TESTS_ON_ORIGIN_SEVEN_REPORTED_NONE_OWNED)
it exited 1 with "Drift found. Re-run with --apply to deploy" (Assemblies/RimMandrakeGraffiti.dll and its .srchash differ
from the Mods folder). So an offline decider is red or green by what happens to be deployed on this machine. Graffiti is
held by the owner (`mod_owner_hold.json`); nothing is changed while the hold stands.
Fix, when the hold lifts: either move T_SHIP_CHECK to the deployed tier (it is a deploy check by design), or make its
offline half compare the repo with itself and leave the drift read to a deploy-tier row.

## verify
Offline, then one deployed-tier run.

## criteria
Acceptance test: none, a decision (which tier the ship check belongs to) comes first. Red output:
/mnt/d/ClaudeWork/rimmandrake/conductor/red_census_20261122/offline_tables/Graffiti_T_SHIP_CHECK.txt

## refs
file: src/RimMandrake/Graffiti/ship_check.py
file: design/concepts/Graffiti/version/test_table.json
