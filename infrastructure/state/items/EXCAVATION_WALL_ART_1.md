# EXCAVATION_WALL_ART_1 — Wall-face art for all four depths, spikes and ladder (Quarry perspective)

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
Rulings 19/33 + the depth ruling: every depth legible and different; depth read from the wall faces in Quarry's perspective; the camera angle must let some spike show. Shared rim + per-depth wall gradient (the cheap layered approach). Also: `RM_Spikes` and `RM_Ladder` art; no `TrapSpikeArmed` anywhere. **Search artpipe state and review-sheet decisions first** (`artpipe_state.py find`) — art may already exist.

## verify
Offline contact sheet of D=1..4 dry + one fluid; owner review sheet; deployed textures resolve (no magenta).

## criteria
`pit_depth_ladder_legible`, `pit_reads_as_hole`, `spikes_read_distinct`, `never_reads_as_building` can pass.

## depends
Can start now (art), wires after `CANAL_BOTTOM_SPIKES_1` / `LADDER_PRISON_DOOR_1` exist.

## northstar
Frame-judged bars only; the state side is the texPath census in O1.
