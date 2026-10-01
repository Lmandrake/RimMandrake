# WATCHER_CREATURES_MOD_1 — the watchers: shy creatures that peek, watch, and jerk away

Owner, 2026-09-30, typed during the Stillsand turn-3 sitting (after admitting the piinnok):
*"strikes me that there could be a new collection of creatures that just sit and watch and poke out
and then jerk away and hide when the players get near. Almost every biome could use this. It might
even be a mod of its own that now informs all of them."*

## spec

A cross-biome `RM_` mod (franchise-free tier): a shared behaviour kit, plus a family of small watcher
creatures, one or more per biome. The behaviour cycle is hidden → pokes out → watches (it faces the
nearest pawn) → jerks back and hides when a pawn comes within a radius → re-emerges after a delay.
Every biome's roster can draw on it.

Prior art to reuse, not re-invent (search done 2026-09-30):
- the piinnok (Stillsand, admitted the same sitting): its lens tracks pawns and sinks on a threat.
  It's the first member.
- `RM_JobDriver_Burrow` / `RM_BurrowOnFireExtension` (Pyrelands): burrow-to-hide.
- `RM_MurrekDrift` (Blue Desert).
- The Brine Crown's unbuilt two-state retraction (`RM_GreySeaFlora.xml`).

Constraints: no animal vanishes without a readable sign (a hole or mound shows where it hid); a
Mod Settings toggle per feature; every DLC is assumed present.

## criteria

- A design pitch is written and ruled by the owner: the kit mechanism, and a per-biome candidate
  member list drawn from existing rosters plus new creatures.
- The kit is built, and one member per biome is proven on a quicktest map.
