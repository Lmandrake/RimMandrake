# RelativeVeto options: CanReach is an AND of two projections (2026-10-21, BENCH helper, read-only design memo)

Sources read: `src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs` (RelativeVeto L236-282, the CanReach postfix
L887-934, the CanReachMapEdge postfix L971-1022), `Superdeep/RM_PocketGrid.cs`, `RM_PocketGridMath.cs`,
`Superdeep/RM_CliffMask.cs`, `Superdeep/RM_PitRooms.cs`, `design/RimMandrake/relative_depth_climb_design_2026-10-12.md`
(§1.4, §3, §8.3, §8.5, §9, §10), item `PIT_SUPERDEEP_COLLAPSE_1`, `Transient/pile_2026-10-21/drawbridge_pair_diagnosis.md`.
No code edited, nothing built, no game.

## Was this already designed or decided? Partly, and the build moved away from the design

- **The design said wall-aware.** `relative_depth_climb_design_2026-10-12.md` §8.3: *"keep a per-map component id over
  walkable cells … counting ramps but not ladders, and **using vanilla walkability**."* §8.5 step 6 accepted the one
  error that design leaves: *"The conservative false negative (vanilla's route crosses a cliff, ours crosses a locked
  door) is accepted and logged once per pawn."* GPT #1 and #2 (§9) named walls, doors and fences as the gap.
- **The build dropped walkability.** Commit `ae8d38f27c` (2026-10-13), `RM_PocketGridMath.cs` L16-17: *"Walkability is
  deliberately NOT an input: the grid is depth-only, so building or removing a wall never makes it stale. Vanilla
  reachability already accounts for walls, and the reachability seam ANDs the two."* The closed item
  `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` repeats it. **I found no owner ruling behind that change**; it was a build
  convenience (no invalidation on wall changes), and its premise ("ANDing is enough") is what the drawbridge pair falsified.
- No item, design note or lesson proposes a fix beyond the diagnosis's two one-line ideas. The lesson
  `infrastructure/state/lessons/20261022T024230Z-BENCH-relativeveto-ands-vanilla-regions-walls-no.md` records the defect.
- Owner constraint that bounds every option: `PIT_SUPERDEEP_COLLAPSE_1` ruling 1 (owner, 2026-10-12): a pawn is trapped
  *"when every N/S/E/W step out of its pocket is taller than it can climb"*. **Trapping is a depth fact.** Pocket-ness
  (held, trapped, pit rooms, capture-down) must stay on depth. Only *reachability* needs walls.

## Mechanism

- `Reachability.CanReach(start, dest, peMode, tp)` → vanilla region BFS (sees walkability, doors per TraverseParms; sees
  no depth: a cliff between two walkable cells lies inside one region, design §3). Then the postfix
  `RM_Patch_Reachability_SuperdeepVeto` runs only when vanilla said **true**, and calls `RelativeVeto`.
- `RelativeVeto` (L236): early-outs (rule off, no dug cell `ClimbCellCount == 0`, flyer / not captured with the masks
  off, band 0). Otherwise `cs = ComponentOf(k, start)`; if dest is in `cs` (or touches it, for Touch): **no veto**.
  If not, it judges pockets, narrowness and ladders (`ReachVetoedWhole`, `JoinedByLadders`).
- The pocket grid (`RM_PocketGridMath.Label`) is one BFS per band K = 1..6 over 4-neighbour steps that pass
  `StepAllowed(d, d', K, ramp)`. **Every cell is a node, walls included.** Rebuilt from the map tick at most once per
  60 ticks when `ClimbGeneration` moves (dig, fill, cover, ramp, settings), never mid-query.
- So CanReach = (route exists in walls-but-no-depth graph) AND (route exists in depth-but-no-walls graph). Two
  different routes can satisfy the two halves while no route satisfies both. A* (`FindPathNow`) reads the joint graph:
  vanilla walkability/cost plus `RM_CliffMask`'s per-band connectivity (vanilla's bits AND `StepAllowed`), so A* is right
  and CanReach is wrong.
- `RM_Patch_Reachability_SuperdeepMapEdge` (`CanReachMapEdge`, L971) has the same shape: `ReachesEdge` on the depth-only
  grid AND vanilla's region answer. A walled compound whose only gap is cut by a trench "reaches the map edge".
- Per-query cost today on a map with holes: two or three `int[]` reads, a few cached-set lookups, sometimes the ladder
  graph. Cheap. The cost of any fix is in REBUILDS, not in queries, unless the fix runs A*.

## Where it lies

The lie is always a **false yes** (never a false no) and needs all three of: (1) a dug cell somewhere on the map (else
the early-out), (2) a pawn the veto applies to (every non-flyer while the cliff masks are on, which is the default with
the relative rule), (3) walls and a cliff that cut a route **only together**: the walled route crosses a cliff and the
cliff-free route crosses a wall.

- **The moat-and-wall gate** (drawbridge R7 layout, site A in the pair diagnosis): measured, rerun4 `CanReach=True`,
  `FindPathNow found=False`. This is the standard defensive layout FlowWorks is built to enable, so it is common in play.
- **Any job giver**, vanilla or ours: hauling to/from across the line, construction, rescue, doctor, warden walks,
  raider `GotoNearestHostile`, `AIFightEnemy`'s `NeedReachable…`, animal hunting. Vanilla callers cannot be spot-fixed.
- **Symptom:** job offered → `StartPath` → A* fails → `PatherFailed` → job ends → the same giver offers it next scan.
  A loop, and an expensive one: **a failed A* is the most expensive A* there is** (it exhausts the reachable area before
  giving up). On a large walled colony with a moat, every looped job is a full-flood A* every few ticks.
- **Map edge:** a walled base whose wall gap is behind a trench reads as "reaches the edge", so flee/exit-map logic
  (raiders retreating, visitors leaving, `CanReachMapEdge` gating) picks a plan that cannot be walked.
- **Not affected:** the pocket/held/trapped/room logic itself (depth-only by ruling, correct); flyers; sappers and
  breachers in `PassAllDestroyableThings` modes (walls are passable to them in both graphs, so the AND is exact there).
- Residual lies that no option below removes without a per-pawn graph: **per-faction locked doors** and **fences for
  animals** combined with a cliff (vanilla sees them per pawn; any pawn-independent label must treat them as open). The
  design already accepted the mirror of this (§8.5.6).

## Options

### (a) Status quo plus per-caller `FindPathNow` gates
- **What it fixes:** only the callers we own and gate: the drawbridge winch (the diagnosis's narrow fix), raider
  winch (already, `RM_DrawbridgeRaid.WinchJob`), `RM_WallClimb` (already). Nothing vanilla.
- **Perf:** one A* per gated job offer; a failing one is expensive, so each gate needs ordering (cheap checks first) and
  ideally a per-pawn negative cache. Vanilla job loops keep their failing-A* cost.
- **Risk:** low per change; the class of bug stays open forever and every new FlowWorks job giver must remember it.
- **Size:** ~10 lines per caller; 3 callers today.
- **Proof row:** `drawbridge_proof.py --fresh_map --only LOWER_ONLY_FROM_WINCH`: `farLower job=False`, `winchLower job=True`
  (as in the diagnosis). Cannot prove vanilla jobs; CanReach itself still says True.

### (b) Make the pocket grid itself wall-aware (design §8.3 as written)
- **What it fixes:** walls + cliff for every caller, CanReach and CanReachMapEdge both.
- **What it breaks:** pocket-ness becomes wall-dependent. A wall across a pit's ramp top would make the pit a pocket:
  the pawn becomes "held", `RM_PitRooms` re-regions it as a pit room, capture-down unlocks. That contradicts ruling 1
  (trapping is the steps, not the walls) and moves room/prison behaviour on every wall build. Walls also have no
  `D = 0` question: a walled-in patch of surface would need special casing.
- **Perf:** rebuild on every walkability change on a map with holes (see (d) for numbers); the room re-region flips
  multiply it (each flipped person-band cell is `NotifyPitnessChanged`).
- **Risk:** high (semantic change to trapping and rooms, save-visible).
- **Size:** small in the labeller (one `passable[]` input), large in the fallout.
- **Proof row:** as (d), plus every pit-room and held row in `climb_proof.py` re-run, because they would move.

### (c) A combined region overlay (cut region links at cliffs)
- **What it fixes:** in principle, everything, inside vanilla's own CanReach and its cache.
- **Why not:** regions are pawn-independent and there are 6 climb bands; a link that is a cliff for a person is a step
  for a muffalo. It needs either 6 region sets or a per-band link filter inside vanilla's region BFS
  (`Reachability.CheckRegionBasedReachability`) **and** regions split at every cliff edge (today `RM_PitRooms` splits
  only at person-band pocket boundaries and deliberately keeps them LINKED). Region counts rise sharply on dug maps,
  the reachability cache keys gain a band, and vanilla/other-mod region code meets regions that are not what it built.
- **Perf:** worst of all at re-region time; per-query cost rises inside vanilla's hottest loop.
- **Risk:** highest (transpilers into region code, mod compatibility, `RM_PitRooms`' five seams).
- **Size:** largest (multi-day).
- **Proof row:** as (d); plus a region-count/perf row.

### (d) A second, wall-aware labelling used only by the reach veto (recommended)
- **Shape:** keep the depth-only labels for everything they serve now (pockets, held, trapped, rooms, ladders-in-pocket,
  width). Add per band a **reach labelling**: the same `RM_PocketGridMath.Label` BFS with one more input, a
  `passable[]` byte grid (cell walkable by anyone, the same test vanilla's `ConnectivitySource` uses; doors count as
  passable). That is the graph A* reads, minus per-pawn doors/fences. `RelativeVeto` and the CanReachMapEdge postfix
  first run exactly as today; **then**, if not vetoed, veto when the reach labels put start and dest (Touch: any
  neighbour) in different reach components **and** no ladder way joins them (ladder edges re-keyed from depth
  components onto the ladders' cells' reach labels).
- **Traverse modes:** `PassAllDestroyableThings` / `PassAllDestroyablePlayerOwnedThings` skip the reach check (walls
  are passable to them; the AND is exact there). Sappers and breachers are untouched.
- **Invalidation:** a `WalkGeneration` counter bumped from the **existing** `RM_CliffMask` postfix on
  `ConnectivitySource.UpdateIncrementally` when a delta cell's walkability flipped (that seam already sees every
  building spawn/despawn and terrain change). Rebuild throttled like today (60 ticks). Stale window: wall built →
  up to 1 s of today's lie (harmless); wall destroyed (a breach) → up to 1 s of a false "unreachable". If that
  matters, a removal can force the rebuild at once (as `UpdatePaused` does).
- **What it fixes:** walls + cliff for **every** caller, vanilla included, in CanReach and CanReachMapEdge; the job
  loop and its failing-A* cost go away for that class. Leaves only the per-pawn door/fence residual (above).
- **Perf:** per CanReach query: one more `int[]` read per end (and ≤ 9 for Touch) when the first check passes. No A*.
  Rebuild: 6 BFS passes over n cells (62,500 on 250²) — the same work as today's grid rebuild, now also triggered by
  walkability changes, and only while the map has a dug cell. UNMEASURED in ms; the build must add a `Stopwatch` to
  `Build` and expose it through `ProofPocket`. Memory: +6 × n ints (1.5 MB on 250²); could halve with `ushort` labels.
- **Risk:** low-medium. Trapping, rooms and capture semantics are untouched by construction; the new check can only turn
  a vanilla `true` into `false`, so a bug shows as a false "unreachable" (pawns refusing work across a wall gap) —
  visible and provable. Behind the existing "Superdeep pits trap" patch feature, plus its own Mod Setting
  ("Reachability sees walls and cliffs together", on) per the superb-settings rule.
- **Size:** ~150-250 lines C# (`passable[]` input to `Label`, reach labels in `RM_PocketGrid`, WalkGeneration bump in
  `RM_CliffMask`, the extra test in two postfixes, ladder re-key) + pure selftests. ~0.5-1 agent-day.
- **Proof rows:**
  - Selftest (`SelfTest/PocketGridChecks.cs`, pure): site A's geometry (trench x=1..4, walls z=±1, caps) — depth labels
    join the banks, reach labels separate them at K=2; open a wall cell → joined; a door cell → joined; a ramp → joined.
  - Live, `drawbridge_proof.py --fresh_map --only LOWER_ONLY_FROM_WINCH`, with the diagnosis's optional diagnostic made
    a row: **far pawn `CanReach(winch, Touch, Deadly)` = False** (rerun4: True) and it **agrees** with `ProofPath found=False`;
    winch pawn True / True. Bar: CanReach == A* found on every probe pair in the scene.
  - Breach row: deconstruct one wall cell, advance ≤ 60 ticks → far pawn CanReach flips True and A* agrees.
  - Sapper row: a `PassAllDestroyableThings` query across the wall stays True.
  - Perf row: reach rebuild ms on a 250² map with holes, and rebuilds per 1000 ticks during a build-heavy minute.

### (e) Bounded A* confirm when the veto passes
- **What it fixes:** everything, exactly (it is the joint graph), including per-pawn doors.
- **Why not as the general fix:** CanReach is called thousands of times per tick by work scanners; an A* per call (and a
  failing one floods) is unaffordable. A cache keyed by (start district, dest district, band, ClimbGeneration,
  WalkGeneration, traverse mode) makes it plausible but large and hard to invalidate. It is (a) generalised; keep it
  only as the per-caller tool (a).

## Recommendation

**(d), and keep the drawbridge winch's `FindPathNow` gate (a) as well.** (d) closes the class for every job giver at a
query cost of one array read, restores what the design (§8.3) specified for reachability without moving trapping or
rooms off depth (ruling 1), and reuses seams that already exist (`Label`, `RM_CliffMask`'s incremental postfix, the two
reach postfixes). The winch gate stays because it costs nothing in normal play and also covers the per-pawn door
residual at the one place a lie loops visibly. (b) is the design's literal text but would make walls trap pawns; (c)
fights vanilla's region system per band; (e) cannot afford the hot path. The first build step must measure the rebuild
time; if it is over a few ms on 250², the fallback inside (d) is to rebuild reach labels only for bands in use by live
pawns on the map.

## Draft ruling line

**"Yes: reachability sees walls and depth together — a second, wall-aware component map used only by the reach check
(trapping, rooms and ladders stay depth-only, sappers exempt), the winch path gate kept, proved by CanReach agreeing
with A* on the moat-and-wall site and a rebuild-time row."**
