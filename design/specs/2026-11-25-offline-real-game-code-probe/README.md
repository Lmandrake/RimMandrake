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

## Not measured here

- A diff of the real `GenSight.LineOfSight` against Explosive Knockback's own model over that mod's enumerated lanes.
- A headless real-game replay of a sample of the enumerated situations on SteveDesktop (the item's second question).
Both are held by the remainder item named in the close.
