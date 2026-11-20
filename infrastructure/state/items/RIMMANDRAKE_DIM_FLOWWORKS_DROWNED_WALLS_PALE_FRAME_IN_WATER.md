# RIMMANDRAKE_DIM_FLOWWORKS_DROWNED_WALLS_PALE_FRAME_IN_WATER

From his FlowWorks walk of 2026-11-20: `design/RimMandrake/validation_holding/flowworks_walk_20261120.md` row #1 (his words, the picture, the station).

## spec

A pit holding water shows a pale frame over its wall art (stations 5-6; strongest in 1 m of water over spikes). The drowned wall strips are drawn opaque and lit with a cream wash (255,248,232 at the wall-light alpha) under the water sheet; `SideUnder` (`src/RimMandrake/FlowWorks/Source/Superdeep/RM_ExcavationWalls.cs:547-550`) draws its face and wash the full cell height but its sheet only up to `wetTop`, so the north corners stay lit and unsheeted [measured]. That this is all of the frame [guess ~60%].

## verify

Zoomed captures of the dry and the wet spikes twins (stations 5 and 6) and of a 2 m in 4 m pit (station 33).

## criteria

Acceptance test: none, a look (his eye, or a judge that did not make it, on the captures above).

## absorbed

Absorbed by RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN (his card 2026-11-20, FlowWorks 0.1.0): the same draw layer is rebuilt; fix this there, in the same run, and close both on its sha.
