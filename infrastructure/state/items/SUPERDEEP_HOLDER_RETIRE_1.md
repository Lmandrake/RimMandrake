# SUPERDEEP_HOLDER_RETIRE_1 — Retire the hidden RM_SuperdeepPit holder; a D=4 cell traps a SPAWNED pawn by grid rule

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
Today `RM_SuperdeepCapture.EnsureHolder` spawns a `Building_SuperdeepPit : Building_OpenPit` on every D=4 cell and despawns captured pawns into its container. Owner, 2026-10-02: *"There's no 'pit' as a special thing, it's just a channel/canal dig."*
1. Delete `Source/Superdeep/Building_SuperdeepPit.cs`, `Source/Superdeep/RM_SuperdeepCapture.cs`, the `RM_SuperdeepPit` ThingDef, and the `SyncMap`/`EnsureHolder` calls in `RM_MapComponent_Excavation.cs` (lines ~253, ~399, ~755).
2. Trap rule as a grid fact: a spawned pawn on a D=4 cell cannot path or step to a cell with lower D unless a lowered ladder is in its cell or it leaves through a door opened from outside. Reachability veto (no job is taken that needs leaving) plus a hard per-move floor. Pathing INTO D=4 stays untouched. Seam from `SUPERDEEP_SEAM_MEASURE_1`.
3. Descent event (previous cell D < entered cell D) on a map component: mass-scaled blunt fall damage (existing setting names), then a hook for spikes. Covers walking in, pushed/blasted in, and the new **"Jump into pit"** gizmo (warn + confirm; strands the jumper).
4. Keep `superdeepCaptureEnabled` / `superdeepCapturesOwnFaction` / `ladderRequiredToExitEnabled` toggles, re-worded.
5. **Pit-width hold rule** ([J] as answered by owner Q4, 2026-10-02: *"The pit has to be as wide as the creature to hold it. Otherwise it gets out."*). Required width `W = max(1, round(sqrt(pawn.BodySize)))` (BodySize < 2.25 → 1, < 6.25 → 2, < 12.25 → 3; bands proposed for his word, Mod Setting multiplier). `PitWidthAt(map, c, W)` = some W×W square of D=4 cells contains c (≤ 81 depth reads at W=3). Held = `D==4 && PitWidthAt(c, W) && !(lowered ladder here && pawn may use it)`. The exit veto in step 2 applies ONLY to a held pawn; a pawn the pit is too narrow for walks out like any canal (normal path, depth movement cost, no roll, no job). Re-evaluated live: growth (life-stage BodySize) or a neighbour cell filled in can release a pawn. Downed pawns stay put. Pawns occupy one cell in RimWorld, so width is a rule on BodySize, never on `drawSize`. Flyers not covered. Inspect line on an unheld pawn: "too big for this pit".
6. Rewrite `RM_ExcavationDepth`'s LAW 2 docstring only when the room exception's wording lands (`SUPERDEEP_PRISON_ROOM_1`).

## verify
Bridge, minimal `flowworks` tier: a hostile spawned beside a D=4 cell and ordered/forced in stays **spawned**, takes fall damage, and has no reachable cell with D<4; with a ladder lowered in its cell it can reach the surface. No `RM_SuperdeepPit` def loads. Shooting rule (ruling 23) still restricts fire (it reads the grid, MEASURED). Width: a BodySize ~1 pawn is held in a 1×1 pit; a BodySize ≥ 2.25 pawn in the same 1×1 pit reaches a D<4 cell, and in a 2×2 pit it does not; a 1×5 trench does not hold it either.

## criteria
No Thing is created by digging. A trapped pawn is on the map, on terrain, and cannot leave.

## depends
`SUPERDEEP_SEAM_MEASURE_1` (items 1-2). Not on the oscillation fix — dry pits suffice.

## northstar
**First script must prove (Q4 width):** state component per pawn in pit — `BodySize`, required W, measured pit width at its cell, `held` flag, `can_reach` any D<4 cell; matrix of {small, large} × {1×1, 1×5 trench, 2×2} with expected held = {T,T,T; F,F,T}; plus a fill-in of one 2×2 cell flips the large pawn to not-held.
First-script change: plan rows S1 ("holder exists"), S7 ("spawned=false, in the holder"), S8 (holders shed/regrown) and O1 (`RM_SuperdeepPit drawerType None`) INVERT: S7 becomes "pawn spawned=true, dead=false, `can_reach` to any D<4 cell = false; colonist twin with ladder = true". Old rows' failure is recorded as a ruled-out theory, not deleted silently. `jawa/flowworks_pit_report` reads the grid, not a container.
