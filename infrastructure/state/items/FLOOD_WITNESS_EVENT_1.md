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

## Design state 2026-09-12 (corrected)
The design already existed:
`design/Jawa/worldbuilding/flood_witness_event_design.md` (2026-09-10) —
including OWNER-RULED choices: lethality has an injury+knockdown ceiling (no
outright deaths), and the witness route is the declinable Moisture Farmer
INVITATION with a re-offering scheduler (not a forced interception). A
duplicate draft made 2026-09-12 in ignorance of those rulings was deleted; its
one real salvage (vanilla Odyssey `Flood.cs` machinery, CONFIRMED against 1.6
source) is now the canonical file's machinery addendum.

## Restructured 2026-09-12 (owner): mechanism moves to a standalone mod
Owner's word (verbatim on FLOOD_CANYON_BIOME_1's filing event): the flood
mechanism becomes its own RimMandrake-tier biome mod — periodically flooded
canyons, chime mechanic included, not Star Wars specific. Filed as
FLOOD_CANYON_BIOME_1 (FOUNDRY). THIS item keeps the campaign plot beat per
the canonical design above (ruled invitation route, ruled lethality ceiling),
consuming that mod as a dependency.
