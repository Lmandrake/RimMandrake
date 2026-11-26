# How much real game code an offline test can run (probe, 2026-11-25)

Item: `RIMMANDRAKE_PROBE_OFFLINE_MODEL_LINKING_REAL_GAME_CODE`. Brainstorm before it:
`design/specs/2026-11-17-offline-testing-with-real-game-code-gpt-brainstorm.md` (its first spike: run the real
`GenSight.LineOfSight` on a hand-built map shell).

## Method

`probe/Program.cs` is a .NET 8 console program (`probe/probe.csproj`). It links the game's own `Assembly-CSharp.dll`
and `UnityEngine.CoreModule.dll` from RimWorld 1.6.4871 rev590 (SteveDesktop, `D:\SteamLibrary\...\Managed`). It has
no Unity player and no loaded game. It calls each piece of game code once and prints RUNS or THROWS with the first
cause. Run: `dotnet run -c Release` in a copy of `probe/`, with the HintPaths pointed at a RimWorld install.
Output: `probe/result_2026-11-25.txt` (18 RUNS, 5 THROWS).

## Result

Runs offline, with correct answers:

- `IntVec3`, `CellRect`, `GenMath`, `GenRadial.RadialCellsAround`, `GenSight.PointsOnLineOfSight`.
- Seeded `Rand` (`PushState(42)` gives the same value each run).
- Unity's managed maths (`Mathf.Sqrt`, `Vector3`).
- A hand-built `Map` shell: `new Map()`, `info.Size`, `CellIndices`, `EdificeGrid`.
- A hand-made wall: a `ThingDef` and a `Building` made as uninitialized objects (`RuntimeHelpers.GetUninitializedObject`),
  with `fillPercent`, `category`, `size` and `Position` set, and registered in the `EdificeGrid`.
- The real `GenSight.LineOfSight` on that shell: False through the wall, True beside it, True on the empty map.

Throws offline:

- Unity engine calls: `Mathf.PerlinNoise`, `Time.realtimeSinceStartup` (SecurityException: ECall methods).
- A `ThingDef` made by its constructor, and `ThingMaker.MakeThing` (the same ECall, from a field initialiser).
- `Map.ConstructComponents()` (it needs loaded defs: "Constructed DefMap ... without defs being initialized").
- `Find.TickManager` with no `Game` (NullReferenceException). `DefDatabase` is empty, as nothing loads defs.

## What this changes

The offline model rule in `src/RimMandrake/rimflow/roles/fable_rescue.md` said "no Verse types". It now says: keep the
decision runnable offline, on real game code wherever it runs. That means real geometry and sight lines, with Unity
calls, def loading, `ThingMaker` and `Find.*` kept at the edge.

## The real sight line against Explosive Knockback's copy, measured (2026-11-26)

Item: `RIMMANDRAKE_REPLAY_ENUMERATED_SITUATIONS_IN_HEADLESS_REAL_GAME`. The situation map's assumption A5 is a hand copy of
`GenSight.LineOfSight(start, end, map, skipFirstCell: true)`. That is the overload that `DamageWorker.ExplosionCellsToHit`
and `GasBurst` call. The 3-argument overload is a different line, with its own error term.
`src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_los_real.py` builds the map with `Source/SelfTest/LosReal/`,
which links the game's Assembly-CSharp. It asks the real line of every sight line on a hand-built Map shell that mirrors the
model's walls and closed doors. The shell holds uninitialized `Building` and `Building_Door` objects of one Full-fill def.

- The map: 0 of 999,162 sight lines differ (121,920 enumerated lanes, 2,496 spared, 38,874 rooms, cases, settings).
- A dense sweep: 2,000 seeded wall and door layouts, every line within radius 9.9. 0 of 610,000 lines differ.
- Planted faults in the copy: the sweep sees a dropped tie rule (12,017 lines) and a closed door left out (62,406).
- The map's own situations seldom test the copy. Over the whole map, a dropped tie rule changes 2 lines and a door left
  out changes 14, and no bar breaks on either. The sweep is what makes a geometry fault in the copy visible.
- Run time: about 50 s with Windows dotnet and a RimWorld `Managed` folder. Without them the script says UNMEASURED.

## A headless real game, measured (2026-11-26)

`headless/headless_probe.py` (Windows python.exe on SteveDesktop) starts RimWorld 1.6 with `-batchmode -nographics`. The
game has its own `-savedatafolder`, `-logfile`, bridge port and token. It touches no other game's config, saves or `Mods`.

- Small list (Harmony, Core, the five expansions, RimBridgeServer): the bridge port line came at 24 s and a quicktest map
  reached `Playing` at 46 s. 600 ticks ran (`ticksGame` 0 to 613).
- `start_debug_game_ready` (readiness `mapData`) returns while `programState` is still `MapInitializing`. A step sent then
  runs no tick (0 to 0, measured). Wait for `Playing` first.
- Graphics code throws and the game goes on: about 2,200 log lines name an exception. The first is a
  `NullReferenceException` in `GlobalTextureAtlasManager.TryInsertStatic` (no textures under `-nographics`),
  `headless/player_log_excerpt_2026-11-26.txt`. A screenshot or anything that reads a rendered frame cannot work.
- Replay of the model against the game: a scratch install (`D:\ClaudeWork\rimmandrake\scratch\headless_probe\install`:
  junctions to the game's `Data`, `RimWorldWin64_Data`, `MonoBleedingEdge` and `BridgeTools`, its own `Mods` with
  FlowWorks and an Explosive Knockback proof build). `proof/map_agreement.py` ran there on the map's 125 exported
  situations: **125 of 125 agree**, in 187 s, with no window and no tokens. The game reached `Playing` at 101 s.
  Readings: `headless/map_agreement_2026-11-26.txt`, `headless/agreement_2026-11-26.jsonl`,
  `headless/result_2026-11-26_agreement.json`.

So a headless real game on SteveDesktop can check a mod's offline model against the game. The route is the mod's own
export of situations, staged through its proof build and read back through the bridge, for any mod whose checks read
state and not pixels. Each headless game is one more RimWorld process beside Steve1 and Steve2.
