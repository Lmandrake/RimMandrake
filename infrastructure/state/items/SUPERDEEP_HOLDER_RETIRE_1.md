# SUPERDEEP_HOLDER_RETIRE_1 — Retire the hidden RM_SuperdeepPit holder; a D=4 cell traps a SPAWNED pawn by grid rule

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
Today `RM_SuperdeepCapture.EnsureHolder` spawns a `Building_SuperdeepPit : Building_OpenPit` on every D=4 cell and despawns captured pawns into its container. Owner, 2026-10-02: *"There's no 'pit' as a special thing, it's just a channel/canal dig."*
1. Delete `Source/Superdeep/Building_SuperdeepPit.cs`, `Source/Superdeep/RM_SuperdeepCapture.cs`, the `RM_SuperdeepPit` ThingDef, and the `SyncMap`/`EnsureHolder` calls in `RM_MapComponent_Excavation.cs` (lines ~253, ~399, ~755).
2. Trap rule as a grid fact: a spawned pawn on a D=4 cell cannot path or step to a cell with lower D unless a lowered ladder is in its cell or it leaves through a door opened from outside. Reachability veto (no job is taken that needs leaving) plus a hard per-move floor. Pathing INTO D=4 stays untouched. Seam from `SUPERDEEP_SEAM_MEASURE_1`.
3. Descent event (previous cell D < entered cell D) on a map component: mass-scaled blunt fall damage (existing setting names), then a hook for spikes. Covers walking in, pushed/blasted in, and the new **"Jump into pit"** gizmo (warn + confirm; strands the jumper).
4. Keep `superdeepCaptureEnabled` / `superdeepCapturesOwnFaction` / `ladderRequiredToExitEnabled` toggles, re-worded.
5. Per-depth max body size on `RM_ExcavationDepth` ([J]); with D=4 = no limit (DEFAULT — owner question on body size may change this).
6. Rewrite `RM_ExcavationDepth`'s LAW 2 docstring only when the room exception's wording lands (`SUPERDEEP_PRISON_ROOM_1`).

## verify
Bridge, minimal `flowworks` tier: a hostile spawned beside a D=4 cell and ordered/forced in stays **spawned**, takes fall damage, and has no reachable cell with D<4; with a ladder lowered in its cell it can reach the surface. No `RM_SuperdeepPit` def loads. Shooting rule (ruling 23) still restricts fire (it reads the grid, MEASURED).

## criteria
No Thing is created by digging. A trapped pawn is on the map, on terrain, and cannot leave.

## depends
`SUPERDEEP_SEAM_MEASURE_1` (items 1-2). Not on the oscillation fix — dry pits suffice.

## northstar
First-script change: plan rows S1 ("holder exists"), S7 ("spawned=false, in the holder"), S8 (holders shed/regrown) and O1 (`RM_SuperdeepPit drawerType None`) INVERT: S7 becomes "pawn spawned=true, dead=false, `can_reach` to any D<4 cell = false; colonist twin with ladder = true". Old rows' failure is recorded as a ruled-out theory, not deleted silently. `jawa/flowworks_pit_report` reads the grid, not a container.
