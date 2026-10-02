# SUPERDEEP_PRISON_ROOM_1 — An enclosed superdeep area is a room; a prisoner bed makes it a prison; capture down / convert down from the lip

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
- LAW 2 exception [D]: depth may bound a room. Implement at the seam `SUPERDEEP_SEAM_MEASURE_1` found (likely a Harmony patch on region building if regions never read terrain). Word the exception narrowly, then rewrite `RM_ExcavationDepth`'s LAW 2 docstring to match.
- Bare enclosed D=4 area: a room holding **trapped enemies**, not prisoners.
- With a vanilla prisoner bed in it: a **prison room** on vanilla's terms; wardens feed and tend from the lip (no one enters).
- **Capture down** and **convert down**: jobs done by a warden **adjacent to the lip** ([B-item]); being trapped makes capture easy. Accepted risk: an armed occupant can shoot the adjacent warden.
- Read Prisoner Realism for the "adequate confinement" shape.

## verify
Bridge: a 3×3 D=4 area reads as one room; adding a prisoner bed sets its role to prison; a downed or trapped hostile is captured by an adjacent warden who never stands on D=4; recruitment interaction works from the lip.

## criteria
No job in this feature requires a pawn to enter the pit.

## depends
`SUPERDEEP_SEAM_MEASURE_1` (items 3, 4, 7), `SUPERDEEP_HOLDER_RETIRE_1`.

## northstar
State components: room id/role for the area before and after the bed; warden position never D=4 during capture; prisoner status after.
