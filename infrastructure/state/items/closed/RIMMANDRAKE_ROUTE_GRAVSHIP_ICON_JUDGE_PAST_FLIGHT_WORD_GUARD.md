# RIMMANDRAKE_ROUTE_GRAVSHIP_ICON_JUDGE_PAST_FLIGHT_WORD_GUARD

The ticket lane (list_dispatch.py) launched a judge run for UTINNI_WORLDMAP_FLIGHT_ICON_1. The brief told the judge to
claim a game and capture the globe with the gravship in flight. The same brief also says "never try to capture images
of flight". `game_lock.py claim a --for "judge captures for UTINNI_WORLDMAP_FLIGHT_ICON_1"` returned rc=3, "HIS HOLD: a
flyer's flight is his act" (2026-11-27 00:10 PST). `flight_purpose` (game_lock.py:82-95) refuses any purpose text that
holds a flight word. The item ID holds one, so every relaunch of this judge route is refused the same way.

## spec
- The Conductor (or the owner) makes one class call: does the flight rule (CLAUDE.md "If it flies in the fiction",
  written for creature flyers and `Pawn_FlightTracker`) cover a gravship world object in transit on the globe?
- If no: the captures come from the WB-game-ship step-3 chain (infrastructure/bundles/WB-game-ship-20261126-164518.md),
  under a purpose that the guard admits, or through a gravship exemption in game_lock.py with a selftest. Then the
  judge route of UTINNI_WORLDMAP_FLIGHT_ICON_1 reads the captures offline and claims no game.
- If yes: a gravship flight capture is his act 1, and the judge route waits for his sitting.

## verify
- A judge run for UTINNI_WORLDMAP_FLIGHT_ICON_1 finds its captures and is not refused at a game claim.

## criteria
- The class call is recorded on the ledger. The judge route of UTINNI_WORLDMAP_FLIGHT_ICON_1 no longer needs a game claim that the guard refuses.

## refs
file: src/RimMandrake/rimflow/game_lock.py
file: src/RimMandrake/rimflow/list_dispatch.py
