## spec
`selftest_static_game_state` is red at 09e5483823b2 (3/144 FAIL), on three static fields that hold per-game state and
are not in its REVIEWED list:
- `src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs:352` `Map cachedMap` and `:353` `MapComponent_BurnLine cachedBurn`
  (added in 49e11870b4).
- `src/RimMandrake/FlowWorks/Source/Superdeep/RM_RaiderFetchFallen.cs:37` `Dictionary<int, (int tick, IntVec3 lip)> fetchLips`.
A static that holds a Map or map ids survives a load into a different game and then reads a stale map.
Fix: guard each one on `Current.Game` (or move it to a Map/GameComponent), then list it in REVIEWED with the reason.

## verify
Run the acceptance test below; no game needed.

## criteria
Acceptance test: `python3 src/RimMandrake/Utils/selftest_static_game_state.py` exits 0 (144/144). It was seen red at
09e5483823b2 with exactly these 3 FAIL lines.

## refs
file: src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs
file: src/RimMandrake/FlowWorks/Source/Superdeep/RM_RaiderFetchFallen.cs
file: src/RimMandrake/Utils/selftest_static_game_state.py
