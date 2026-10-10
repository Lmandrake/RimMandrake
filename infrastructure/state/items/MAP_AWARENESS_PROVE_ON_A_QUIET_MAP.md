# MAP_AWARENESS_PROVE_ON_A_QUIET_MAP

needs: bridge (and the game DOWN for the companion deploy: `taskkill`, `python3 src/RimMandrake/bridgetools/build.py --gm --apply`).

The live half of map awareness (`design/RimMandrake/map_awareness.md`). Everything below is built and unit-tested
offline; nothing has run in a game. Run on a quiet quicktest map (minimal list is fine; all five DLCs on) and record
each result against its item with `rimflow verify`:

- `VISITOR_DETECTORS_MEND_NAME_THE_STRANGER` A2-A4: substituted-spawn receipt; abort_proof (`modcheck/live_queue`)
  hostile_raid recorded+removed and CLEAN, predator case DISRUPTED; `scene_report.py` with a manhunter and a joiner.
- `THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER` A2-A5: OBSERVED vs CANDIDATE provider on a creature whose texture path two
  mods hold; ambiguous cell/name; wild-spawner block skips and releases; raid letter lookTargetIds.
- `INCIDENT_JOURNAL_BUILD_CALLED_IS_NOT_FIRED` A2-A5: forced raid chain; worker-false incident; queued incident keeps
  the bridge chain; armed disk rows visible in `tps_record.py --at`.
- `PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN` A2-A6: cold-launch autostart sees first-map wildlife as mapgen; drop-pod raid
  keeps incident:RaidEnemy; caravan/gravship return is a transfer/respawn; load is a new epoch; per-hook costs copied
  into `game_health_record.md`'s `aware.*` rows.

GPT review s7 also asks, and these are owed here too: another mod's prefix skipping TryExecute (journal says
outerBodyRan false, no invented effects); a mod-under-test extra pawn stays a violation; ring overflow counted;
a new game while rows are pending does not mix epochs; recorder on/off overhead compared on a repeated workload.
