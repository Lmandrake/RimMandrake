# MOVING_DUNES_ENGINE_1

## Spec
Owner spark, verbatim (2026-09-09): "In the extreme limit, it would be
fun to have it pile up so much this becomes a moving dune mod..."

Context: Odyssey's loose-material deposition (snow/sand/ash/ice) piles
against structures but is static once landed. The idea: a generic RM
aeolian-transport engine — accumulated material erodes from windward
cells and deposits leeward along the map's wind vector, so deep drifts
CREEP across the map over days; buildings cast wind shadows, walls
become dune fences, an unattended map slowly buries.

Seeds that exist: Pyrelands' MapComponent_PyrelandsAshfall (deposition
cadence pattern), the ash filth ladder, Odyssey's sand channel (DLC-
gated). Engine+data-pack doctrine applies: RM engine, material packs
per scenario (ash for Pyrelands, sand for the desert campaign).

DESIGN-FIRST: this is an idea capture, not a build order. A Fable
design pass sizes it (perf: per-cell transport on 250x250 maps is the
hard part — likely chunked/amortized like the ashfall batches).

## Verify
A design spec exists and the owner has ruled build/park on it.

## Criteria
No code before the spec ruling.
