# Expected-failure signatures — RESTART_7 deploy-debt batch, written 2026-09-04 BEFORE launch (BENCH)

Supersedes the Armoury batch #2 entry (2026-09-04, FOUNDRY) — that batch rode
its restart and was verified earlier tonight.

This batch is the RESTART_7 handoff's deploy debt: **four assemblies + one XML**,
one over the three-assembly waiver, accepted because every one is a REBUILD of an
already-live assembly carrying reviewed fixes, and the four fail in four
distinguishable namespaces. Each signature below was written before the game
closed.

| cargo | commit | expected-ABSENT signature (failure looks like) | expected-PRESENT check |
|---|---|---|---|
| `JawaBench.BridgeTools.dll` (companion, `--gm` build → `RimWorld\BridgeTools\JawaBench\`) | 9681117f + 6 more review commits | any `TypeLoadException`/`ReflectionTypeLoadException` naming `JawaBench` | `build.py --gm` plan says game copy = this build's commit; bridge `tools/list` still carries `jawa/fire_incident` + `jawa/send_letter` (gm) and `jawa/map_zones` (RESTART_7 called it `jawa/world_zones`; the live name is `jawa/map_zones`); first tool call succeeds (init line is lazy — call one, don't just look) |
| `RimDefDump.dll` (mod `mandrake.rm.rimdefdump`) | c6ede2aa | exception naming `RimDefDump` or `JsonWriter` | `[RimDefDump]` startup line present as usual (dump NOT armed this load) |
| `Inhabited.dll` (mod `mandrake.rm.inhabited`) | a03bc3e0 | exception naming `Inhabited` or `RM_InhabitedPlace`; XML unknown-field errors on CastRoster files | mod loads silent; no `Could not resolve cross-reference` naming RM_Inhabited* |
| `JawaArmoury.dll` (mod `mandrake.rsw.armoury`) | 8afa5bb0 (MinePocket dead-content drop) | exception or Harmony patch-failure naming `JawaArmoury`; `Could not resolve cross-reference` naming any MinePocket def (would mean something live still referenced the dropped content) | mod loads silent |
| `ScorchableGround.xml` (mod `mandrake.rsw.fireecology`) | FIRE_ECOLOGY_LOOP_1 tree | red XML/def error naming `ScorchableGround` or the mod's TerrainDefs | silent load; config-warning baseline already ACCEPTED by owner (cfd0b038) — do not re-flag those |

General: `harvest_log.py` full sweep after the load, triage by consequence.
Zone-deletion fix (`jawa/world_zones`) and the WorldEdit2 stale-modal fix ride
the companion — after this deploy those two known-live bugs are CLOSED as
live hazards.
