# INCIDENT_JOURNAL_BUILD_CALLED_IS_NOT_FIRED

Map awareness phase 2 (companion C#). Doc: `design/RimMandrake/map_awareness.md`. `jawa/incident_journal`: every
IncidentWorker.TryExecute call with called / outerBodyRan (__runOriginal) / returned / exception (observed, not
swallowed) / workerEntered (false only on the established requireColonistsPresent branch, else unknown), the context
chain, and pawns generated/spawned during the call; bounded ring; rows into the TPS record while armed.
Built, NOT deployed.

## criteria

- A1 L0: selftest_map_awareness_core.py green (statements, epochs, bounds)
- A2 L2: a forced RaidEnemy via jawa/fire_incident journals chain bridge:jawa/fire_incident > incident:RaidEnemy, returned true, pawns generated > 0
- A3 L2: an incident whose worker returns false is journaled with returned false and no "fired" wording
- A4 L2: a queued incident (jawa/incident_schedule) fired later by the queue keeps the bridge chain via the parms token
- A5 L2: armed for 5 minutes, the TPS record holds kind awareness rows and tps_record.py --at prints them; disarmed, none
