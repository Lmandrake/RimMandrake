# PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN

Map awareness phase 3 (companion C#). Doc: `design/RimMandrake/map_awareness.md`. Origin recorder: context chain with
explicit immutable tokens, PawnGenerator.GeneratePawn observation (new vs reused from nextThingID), Pawn.SpawnSetup
observation (never on load), classification firstObservedSpawn | observedRespawn | mapTransfer | unknown, bounded
stores with eviction counters, epochs per Game, installed at bridge registration, disk rows only while armed,
statements that never upgrade (GPT s3 table). `jawa/pawn_origin`, `jawa/awareness`. Built, NOT deployed.

## criteria

- A1 L0: selftest_map_awareness_core.py green (chain, threads, skip-safe pops, epochs, reuse, classification, lint, switches, TTL)
- A2 L2: after a cold launch with no bridge call, jawa/awareness reports startedBy bridge-registration and the first map's wildlife reads a mapgen > wild-spawner chain
- A3 L2: a drop-pod raid's pawns, spawned ticks after TryExecute returned, still read generation chain incident:RaidEnemy
- A4 L2: a pawn leaving on a caravan / gravship and coming back reads mapTransfer or observedRespawn, never firstObservedSpawn
- A5 L2: save + load: every pawn reads origin unknown (new epoch), no PRE_LOAD claim
- A6 L2: jawa/awareness meters give a per-hook cost for every aware.* id; the cost is copied into game_health_record.md
