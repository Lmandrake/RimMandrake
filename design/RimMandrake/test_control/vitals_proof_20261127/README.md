# Vitals governor live proof, 2026-11-27 (TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO, criterion A2 at L1)

- `archsmall_first_run_20261127T0339_stdout.txt`: the first run on ArchSmall (gimmesomeslack tier). Two rows read
  FAIL because the quicktest map held a dormant insect hive, so the governor rightly read UNMEASURED; the run then
  stopped at the raid pause. This is the known-bad scene state for the `fresh_map` threat clear.
- `proof_clock_modal_cluster_raid_downed_death_specimen_hostile_colonyloss_20261127T062257.json`: the full run on
  ArchBig (gimmesomeslack tier, companion built from 0d0fa37d), 17 of 18 rows PASS. The red telemetry alarms (telemetryd's `alerts.json`)
  `vitals:colonist_hostile` and `vitals:colony_dead` are rows here. The one FAIL was a wrong check (it required the
  map to hold no hostile pawn).
- `proof_cluster_20261127T062352_PLANTED_wall_no_faction.json`: the repaired cluster check on the planted fault in
  `planted_fault.diff` (the wall has no faction). It reads FAIL.
- `proof_cluster_20261127T062403.json`: the repaired cluster check on the real script. It reads PASS.
