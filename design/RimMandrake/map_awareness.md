# Map awareness: who is on this map, and what do we actually know about why

Owner decisions by question card, 2026-10-10: build the whole programme (scene report, receipts, quiet world, incident
journal, thing lookup, pawn origin recorder); and in a validation or north-star run an unexpected visitor is
**recorded and removed** and the run carries on, a redo is owed only on **evidence** that the visitor disrupted the
criterion. Design and reviews: `Transient/foundry_map_awareness_{design,review_opus,review_gpt}_20261010.md`
(Transient, ~14 days; what binds is restated here).

Why it exists: Player.log records no incident firing and no pawn arriving (measured over three logs). Provenance is
not stored on a pawn, so it has to be observed when the pawn is generated and spawned.

## Pieces

| piece | where | items |
|---|---|---|
| detectors that name the pawn; `player_joiner`, `pawn_arrived` (set diff), `pawn_state_changed` (recruit/tame) | `src/RimMandrake/Utils/modcheck/detectors.py` | `VISITOR_DETECTORS_MEND_NAME_THE_STRANGER` |
| bounded per-test expectations (`max_count`), never by mod package | `detectors.Expectations`, `t.expect(..., max_count=N)` | same |
| run validity CLEAN / DISRUPTED / INDETERMINATE, disruption evidence, spawn receipts | `modcheck/contract.py`, `modcheck/watch.py` | same |
| scene report (batched reads, not atomic) | `modcheck/scene_report.py` | same |
| quiet-world profile with read-back | `modcheck/helpers.quiet_world` | same |
| first-look protocol | `skills/rimbridge/references/first_look.md` | same |
| `jawa/thing_explain`, `jawa/wild_spawner_block`, letter `lookTargetIds` | `bridgetools/JawaBench.BridgeTools/JawaBenchAwarenessTools.cs` | `THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER` |
| `jawa/incident_journal` | `JawaBenchAwareness.cs` (hooks) | `INCIDENT_JOURNAL_BUILD_CALLED_IS_NOT_FIRED` |
| `jawa/pawn_origin`, `jawa/awareness` (status, arm, switches, cost) | `JawaBenchAwareness.cs`, `JawaBenchAwarenessCore.cs` (pure) | `PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN` |
| live proof | — | `MAP_AWARENESS_PROVE_ON_A_QUIET_MAP` (needs bridge) |

`jawa/scene_report` as one atomic companion read was **not built**: the Python batch plus `jawa/pawn_origin` answers
every field, and the report states it is not atomic. Build it only if a live session shows the non-atomic read misleads.

## Laws

1. **Origin is unknown unless observed.** Report text comes from `JawaBenchAwarenessCore.Statement()`; the
   forbidden-upgrade table (in `first_look.md`) is enforced by `IsForbidden()`. A letter, a lord job or proximity is an
   association. "Called" is not "fired".
2. **The context is a chain, carried explicitly.** `bridge:jawa/fire_incident > incident:RaidEnemy` keeps our own raid
   ours. A thread-static token covers synchronous nesting; anything crossing a thread or a schedule carries the token
   (a queued incident's parms object carries it to `TryExecute`).
3. **Skip-safe and contained.** Prefix pushes, finalizer pops by token; `__runOriginal` (not a postfix firing) says
   whether the original ran. Hook bodies never throw; the game's exceptions propagate unchanged (void finalizers).
4. **Game-scoped and bounded.** A new Game opens a new epoch and forgets the old one. Tags, spawn and incident rings
   and the seen-set are capped; evictions are counted. After a seen-set eviction "first spawn" is reported `unknown`.
   Provenance does not survive save/load (a load is a new epoch); nothing is written into a save.
5. **Installed at bridge registration**, the TPS record's startup path, so first-map generation can be seen without a
   bridge call (UNVERIFIED live: acceptance A4).
6. **Disk only while armed.** `jawa/awareness action=arm minutes=N` writes kind `awareness` rows into the TPS record
   (`tps_record.py --at` shows them as `AWARE`); TTL 30 min default, 240 max.
7. **Every metric has an id, a switch and a measured cost** (`aware.*` rows in `game_health_record.md`). Switches:
   `JawaBench\tps\awareness_settings.json` at launch, `jawa/awareness action=switch` at run time.

## Selftests

- `src/RimMandrake/Utils/modcheck/selftest_awareness.py`: phase 1 acceptance rows offline (FakeWorld).
- `src/RimMandrake/Utils/selftest_map_awareness_core.py`: the production `JawaBenchAwarenessCore.cs` unit group,
  built by winbuild into `bridgetools/AwarenessSelfTest`.
