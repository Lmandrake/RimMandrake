# GRAVSHIP_LANDING_FOG_REVEAL_1 — you cannot pick a landing spot you cannot see

Owner, 2026-09-12, after the hop toward Zeddo's Yard: *"when I tried to land my
gravship in the right spot, fog of war and/or CAI were obscuring the whole map except
for one tiny room in a large complex... so I was forced to land blind and crashed."*

## Mechanism (READ AT SOURCE, not guessed)
1. `GenStep_ReserveGravshipArea.SetStartSpot` picks `MapGenerator.PlayerStartSpot`
   near the map CENTRE (`TryFindCentralCell(map, 2, 30)`), minimising overlap cost with
   already-used rects — it never requires the spot to be outdoors or unenclosed.
2. `GenStep_Fog.Generate`: `SetAllFogged()`, then — because a start spot IS valid —
   `FloodFillerFog.FloodUnfog(startSpot)` only. The whole-map `UnfogMapFromEdge` path
   runs ONLY when no start spot exists. A flood from a cell inside an enclosed complex
   stops at its walls ⇒ exactly one room revealed. The "large complex" at the centre
   of a Zeddo's-Yard map is our own structure injection / ruin-field mutators.
3. On top of that, NWN Real Fog of War (`Mlie.NWNRealFogOfWar`) runs on every
   non-colony map (`onlyOutsideColony=True` in its live settings) and the arrival map
   is not a player home until the ship is down; CAI's `FogOfWar_DisableOnPlayerMap`
   strips fog on PLAYER maps only. So neither mod helps during the picker. (Memory:
   `real-fog-of-war-and-cai` — never fight it with `set_fog unfogAll`, it wedges.)

## spec
- Harmony postfix on `GenStep_Fog.Generate` (or a dedicated GenStep appended via the
  arrival path) for maps generated as a gravship landing target: additionally
  `FloodUnfog` from an edge-reachable unroofed cell (vanilla's own `UnfogMapFromEdge`
  logic) so every outdoor region is visible in the picker; leave mountain interiors
  fogged. Gate on "this map is being generated for a gravship arrival" — read
  `GravshipController` / `GenStep_ReserveGravshipArea` for the flag, do not infer it
  from `IsPlayerHome`.
- NWN: decide whether the landing picker should be treated as a colony map for
  `onlyOutsideColony` (a small patch on `MapComponentSeenFog.IsShown` for arrival
  maps) — measure first whether NWN's shading actually applies during the picker.
- Start site (`PLAYER_START_SITE_1` build): the injected junkyard complex must leave
  the reserved landing area (`GenStep_ReserveGravshipArea`, ship footprint +2) open;
  cost-minimisation puts the ship INSIDE a complex when nothing else fits. Author the
  injection with a central clearing at least the v2 hull's 92×86 + margin.
- Mod Settings toggle: "Reveal outdoors before gravship landing", default on.

## verify
- Load `FLIGHT_hop1_seas_cleaned_2026-09-12.rws` (parked mid-hop), fly to 17007, and
  the picker shows the whole outdoor map; screenshot for the owner. Land; ship intact.

## traps
- "Crashed" here means a blind landing onto obstacles, not a game crash; check the
  Player.log anyway before assuming.
- `FloodUnfog` respects `MakeFog` edifices; doors do not pass. Two flood roots are
  cheap; do not unfog cell-by-cell (62,500 SetFog calls wedged the game once).
