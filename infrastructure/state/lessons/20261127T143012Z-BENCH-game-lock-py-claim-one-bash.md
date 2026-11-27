game_lock.py claim in one Bash call holds the driver lock for the claude process, but a waitalive job runs outside that process tree, so its bridge calls are refused (DriverHeldError, then exit 75 from game_lock run). Do not release the claim and re-take it with game_lock run in a later call: another run took both games in that gap (2026-11-27, ArchSmall). Wrap the whole stop, deploy, launch and proof sequence in ONE game_lock run call from the start.
item: TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO
home: skills/rimbridge/SKILL.md
