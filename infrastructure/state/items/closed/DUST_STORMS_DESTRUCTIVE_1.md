# DUST_STORMS_DESTRUCTIVE_1 — dust storms that damage structures and move light objects

Owner's ask, 2026-08-31: "Meaningful dust storms that damage structures and
move light objects." Spec by BENCH, mechanisms MEASURED from 1.6 source.

## spec
The engine gives no data-only route (WeatherDef and GameCondition are empty
hooks) — but **`Tornado : ThingWithComps` still ships complete in 1.6**: a
self-ticking Thing dealing `TornadoScratch` damage to pawns/buildings/items/
plants in radius and dropping roofs via `RoofCollapserImmediate`. The design:

1. **`RM_DustDevil`** — a Tornado-shaped Thing of our own (C#, small; the
   vanilla class is the template, ours is rewritten): weaker, wandering,
   shorter-lived; damages EXPOSED structures (skip roofed/indoor), flings
   light items (mass cap) a few cells downwind, shreds plants.
2. **Wired through weather, the shipped way:** our sandstorm WeatherDefs get
   an `eventMakers` entry — a `WeatherEventMaker` whose `WeatherEvent`
   subclass spawns 1–3 devils per storm on an MTB, so severity scales with
   storm duration. Ordinary sandstorms stay cosmetic; the DESTRUCTIVE tier is
   a rarer WeatherDef (`RM_Sandstorm_Scouring`).
3. Ties: SANDSTORM_WEATHER_TUNING_1 (legacy) folds into this; Zizzik's
   event-audit gains a natural entry (a devil through the yard is his kind of
   week); Ta'Baa doctrine text writes itself.

Caveat carried: no vanilla IncidentWorker wires Tornado — reachability is
def-side ours anyway (weather event, not incident), so the gap doesn't bind.

## verify
Quicktest on the 22s list: force `RM_Sandstorm_Scouring`, PROVE a devil
spawns and EXPECT an unroofed wood wall section takes damage while a roofed
one does not, and a steel slag chunk moves ≥1 cell. LIES: damage attributed
to the storm may actually be the devil's pawn-panic fires — check the damage
log, not the aftermath.

## criteria
Storm tier ships with devils; ordinary sandstorms unchanged; indoor colonies
untouched; owner sees a devil cross a test map and calls the violence level.
