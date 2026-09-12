# FLOOD_WITNESS_EVENT_1 — the player sees the flood, once, on purpose

Owner, at the Cracked Lands enrichment sitting (verbatim on the filing event): the
flood mostly won't happen while the player is in the canyons, so the plot organizes
an event where they witness it at least once.

Spec source: `biomes/the_cracked_lands.md` — §3/§4b (the flood event chain: the
Contagion's storm on the peaks → smell of wet clay → the flats tick as the Sealed
wake → the water chimes ring up through the stone → the wall of red-brown water),
§10b (the explosive growth the flood triggers — this event is
`EXPLOSIVE_PLANT_GROWTH_1`'s guaranteed showcase), §11 (refuge ledges; NEVER build
the bottom).

Design constraints: the player must survive witnessing it (refuge ledges exist for
this), and it should sell both faces at once — disaster and fertilizer; death, then
soil, then the bloom. Timing rides the plot, not weather RNG. Quest/plot machinery
per `rimworld-quests` skill when it reaches authoring.

## Design draft done 2026-09-12 (BENCH belt wave, Fable agent)
`design/Jawa/flood_witness_event_draft.md` — 4 witness routes (Flood-News
salvage strike / Road Catches You interception / Farmer's Gallery invitation /
Layered offers-plus-backstop), phase-by-phase beat, plot integration, mechanism
sketch parameterized over EXPLOSIVE_PLANT_GROWTH_1's four unruled terminal
moments. Owner cards at the end (route choice + beats). Open engine questions
named inside (does Odyssey floodwater harm pawns; does accelerated Flood read
as a wall). Awaits the owner's cards; no build before the ruling.

## Restructured 2026-09-12 (owner): mechanism moves to a standalone mod
Owner's word (verbatim on FLOOD_CANYON_BIOME_1's filing event): the flood
mechanism becomes its own RimMandrake-tier biome mod — periodically flooded
canyons, chime mechanic included, not Star Wars specific. Filed as
FLOOD_CANYON_BIOME_1 (FOUNDRY). THIS item narrows to the campaign plot beat:
the guaranteed first witnessing (routes/cards in
design/Jawa/flood_witness_event_draft.md), consuming that mod as a dependency.
Route cards still await the owner's sitting.
