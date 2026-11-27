# C24 standing health check: memory and TPS over time, beside load health and log-error counts

Filed by FOUNDRY 2026-10-11 from `design/RimMandrake/mod_audit/OWNER_RULINGS.md` (C24). The item file was written
2026-11-27 by work bundle WB-pipeline-operations-20261127-182008, from the built code, so that preflight can read it.

## refs

file: src/RimMandrake/Utils/game_health_check.py
file: src/RimMandrake/Utils/selftest_game_health_check.py
file: src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSessionHealth.cs
file: design/RimMandrake/game_health_record.md

## spec

Each game session records memory (private, Unity reserved and allocated, graphics) and TPS as a function of time,
beside the log-error and log-warning counts, in the companion's TPS `context` rows. `game_health_check.py` reads the
sessions, records them, reports them over time, and names a session that breaks a threshold in
`game_health_thresholds.json` for a debug. The design record is `design/RimMandrake/game_health_record.md`.

## verify

Offline: `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_game_health_check`.
Live (criterion A1): `python3 src/RimMandrake/Utils/game_health_check.py fields` on a game whose deployed companion
holds JawaBenchSessionHealth.cs, after a map has played at least 2 minutes.

## criteria

- A1 L2: the newest TPS session's latest `context` row carries privateMB>0, unityReservedMB>0, unityAllocMB, upS>0,
  logErr and logWarn as numbers (gfxMB may read 0 in a release player).
