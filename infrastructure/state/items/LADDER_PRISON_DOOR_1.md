# LADDER_PRISON_DOOR_1 — Ladder raise/lower works like a prison door; ladder art

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
- `RM_Ladder` gains a raised/lowered state, toggled from the lip (outside), never from inside a D=4 cell.
- Who may climb a lowered ladder: **DEFAULT** — like a vanilla door: your colonists and anyone you allow climb; trapped enemies and prisoners do not, except on a prison break. (Owner question on ladders may change this to "anyone climbs when lowered".)
- Raising the ladder with a colonist below strands them — by design (*"jump into pit… stuck there too"*).
- Replace the `TrapSpikeArmed` placeholder: ladder art drawn in perspective on the wall (Quarry reference), via artpipe — search existing art first.

## verify
Bridge: colonist below, ladder lowered → can reach surface; raised → cannot. Hostile below with ladder lowered → cannot (DEFAULT). Inspect string shows the state.

## criteria
`ladder_state_legible` has a state predicate to stand on.

## depends
`SUPERDEEP_HOLDER_RETIRE_1`.

## northstar
Fixes the script plan's WRONG row: the ladder is placed IN the D=4 cell, not beside it; component S9 reads raised/lowered and reachability for both states.
