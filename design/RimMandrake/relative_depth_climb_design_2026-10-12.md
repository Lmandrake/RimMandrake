# Relative depth and climbing out — design pass (2026-10-12)

Item: `POND_BED_DESIGN_LAKES_ARE_TALL_CANALS` (BENCH). Design only: no C#, defs, game or bridge were touched.
Parent: `design/RimMandrake/natural_bodies_as_canals_design_2026-10-11.md` (owner rulings at its end).
GPT review: `design/RimMandrake/relative_depth_climb_gpt_review_2026-10-12.md`; dispositions are §9 here.

## 0. Owner's question (verbatim, question-card write-in, 2026-10-12)

> *"It should be yes to all deep but there is a wrinkle. A deep ditch shouldn't stop you from climbing one or two
> levels higher but by bit. So if there is a gradual change of height then the player should be able to simply walk
> out even a deep pit. Please do a design pass about this. I am loathe to make a whole elevation grid concept but it
> feels like we're heading towards that. Assess how hard it would be to handle this in the game. Is this not so bad
> or utterly devastating new development to have characters trapped in pits that are "relatively deep" rather than an
> absolute approximation. If it's too terrible, we will have to make some approximations and limitations. Suggest
> several alternatives and ask got while you're at it. Natural ponds and lakes when pumped dry would leave just such
> gradual terrain so no chance to fall in and get stuck. But then we have the same issue when players dig wide
> gradual pits too."*

## Summary (one screen)

**Verdict: not so bad.** Two facts make it so.

1. **We already have the elevation grid.** The excavation depth grid (`D` = 0..4 per cell,
   `RM_MapComponent_Excavation.depthGrid`, RM_MapComponent_Excavation.cs:45) *is* a height map for every dug cell,
   and every undug cell is height 0. A whole-map elevation concept (hills, mounds, line of sight by height) is NOT
   needed to answer this question, and is not recommended.
2. **The trap is already one predicate in a handful of seams.** Holding, the per-step veto, the reachability veto,
   the escape route planner, "keep out of open pits" for outsiders, pit rooms and the fall detector all key on one
   test: "this cell is dug to D = 4" (`IsSuperdeepExcavation`, RM_MapComponent_Excavation.cs:177). Changing what
   "trapped" means is mostly changing that test for the *trap* seams, not rewriting them.

And one fact about RimWorld 1.6 makes the fully exact version possible too: **the 1.6 pathfinder has a per-cell,
per-direction connectivity mask** (`ConnectivitySource`, a `CellConnection` byte of 8 direction bits per cell) that
the Burst A* job reads on every step (`PathFinderJob.Execute`: `connectivity[element]` / `connections.HasBit`). The
mask is computed by plain managed code (`ConnectivitySource.ComputeCellConnectivity`), so a Harmony postfix can
remove the single direction "from this cell up to that cell" without touching the Burst code. **A per-edge climbing
rule is expressible in 1.6, map-wide.** It was not in 1.5, where the pathfinder was purely cell-cost based.

**Recommendation (revised after the GPT review): Alternative F, "automatic ramp exits", now.** Keep the pit
exactly as it is (a D = 4 component, held, vetoed, routed, roomed as today) and add one thing: **any D = 4 cell that
touches a D 2 or D 3 cell along a side is a ramp exit, a ladder that everyone may use and nobody can raise.** The
existing ladder planner already walks a pawn inside the pit to its way out and steps it up; a ramp exit is one more
way out. Walls stay walls: nobody scrambles up a sheer side because the pit has a ramp elsewhere (that was the
flaw GPT showed in B, the first recommendation). A dried pond never traps (its deep core always touches its 2-deep
ring), a sheer player pit still traps, and a player who wants an escapable pit digs one step. **No global cliff
mask, no new grid, no elevation concept.** Rough cost: F about 1.5–3 agent-days including the large-lake work it
inherits; A (exact climbing at every depth) only if the owner wants sheer 3-deep ditches to trap too (Q1); a full
elevation grid weeks and devastating.

## 1. The core problem, stated precisely

### 1.1 Today: an ABSOLUTE rule

A pawn the hole captures (enemies by default; own faction only if it jumped or was forced in) is **held** on a cell
when (RM_SuperdeepTrap.cs:96-118, RM_PitTrapMath.cs:95-112):

- the cell is dug to **D = 4** and not under an intact cover, and
- no ladder in the cell lets this pawn climb, and
- some W×W square of D = 4 cells contains it (W from body size).

A held pawn **may step only onto another D = 4 cell** (`StepBlocked(held, toDepth) = held && toDepth < 4`).
D = 1..3 are path cost only (owner, 2026-09-17, answer 2: *"Only SUPERDEEP traps"*).

So **a gradual bowl 0 → 1 → 2 → 3 → 4 traps anything that reaches its D = 4 core today**: the 4 → 3 step is
refused, though it is one level. A dried deep pond under the 2026-10-12 rulings (shallow → D 2 ring, deep → D 4
core) would trap every enemy that wanders to its middle. That is the wrinkle.

### 1.2 Wanted: a RELATIVE rule

Let `K` be the most levels a pawn can climb in one step (owner: *"one or two levels"*). An **edge** between
neighbours `a` and `b` is a **cliff** when `|D(a) − D(b)| > K`. A pawn may walk along any non-cliff edge. A pawn is
**trapped** when no chain of non-cliff edges (plus ladders and covers, which stay exits) leads from its cell to the
surface.

The question is no longer "how deep is this cell" but **"is there a gentle way up from here"**. That is a property
of a connected region of cells, not of one cell, and it is decided by edges, not cells.

### 1.3 Two readings of "yes to all deep" (owner decision Q1)

| rule | what is limited | consequence |
|---|---|---|
| **R-deep** (hybrid) | only steps **out of a D = 4 cell** are limited to K; from D ≤ 3 anyone climbs anything, as today | keeps *"Only SUPERDEEP traps"*: a D = 4 area traps iff no D 4 cell in it touches a D 2 or D 3 cell (with K = 2). Simplest; one local check. |
| **R-all** (pure relative) | every step up of more than K is impossible, everywhere | physically honest; but with K = 2 a sheer **D 3 trench** (every neighbour D 0) also traps, which reverses the 2026-09-17 answer 2. |

`K` must be **2**, not 1, for the owner's pond sentence to hold: under ruling 3 the shore step is 0 → 2. With K = 1
every dried shallow pond would trap. (Or K = 1 plus auto-ramps at the shore: rejected as needless.)

### 1.4 What changes, subsystem by subsystem

| subsystem | today | under a relative rule |
|---|---|---|
| **pathing (A\*)** | 1.6 `PathFinderJob`: per-cell cost grid (`PathGridJob`, Burst) + per-cell 8-direction connectivity mask; edge-blind except the mask. Our pit legs: `RM_PitPathing` swaps the follower's request (`Pawn_PathFollower.GenerateNewPathRequest` prefix) and adds a per-request offset grid (`PathRequest.IPathGridCustomizer`; `PathGridJob.CellIsPassable` refuses offset ≥ 10000) to keep outsiders off open D 4 cells (AvoidPits) and held pawns inside (StayInPit). | B: same legs, keyed on *trap cells* instead of D 4 cells; non-trap D 4 cells become ordinary costly ground. A: plus the connectivity mask removes cliff edges, so vanilla A* walks ramps, never walls. |
| **reachability** | vanilla `Reachability.CanReach` is region-based and knows nothing of pits; we veto true → false outside its cache (RM_SuperdeepTrap.cs:507-560) for a trapped pawn, and `OutsiderBarredFromFloor` vetoes outsiders whose target needs a trap floor. | ~~Lemma: non-trap cells are mutually reachable iff vanilla says so.~~ **False** (GPT #1): a map-spanning sheer trench leaves both banks non-trap but cut apart, and walls, doors and fences can cut a ramp off. That gap exists today (AvoidPits already blocks open pits that vanilla reachability crosses). Under F nothing new is cut: F only *adds* exits, so the existing vetoes stay correct in the same places and wrong in the same places; the pre-existing gaps (GPT #9, #13) are listed in §9 as owed work. |
| **regions / rooms** | regions split along "D 4 vs not" (RM_PitRooms.cs patches 1-5) so an enclosed D 4 area is a room (prison); links stay, so pathing is untouched. | The room boundary should be "trap vs not": a gentle bowl is not an enclosure, a prisoner walks out. Predicate swap; the re-region trigger widens (a single dig can flip a whole component). |
| **job givers / hauling** | covered by the reachability veto + entry veto (hauler not offered an item on an unreachable pit floor). | Unchanged seam, new predicate. Items on a non-trap pit floor become plainly haulable (walk down the ramp). |
| **raiders, animals, wander, flee** | vanilla AI over vanilla reachability; pits are high-cost cells avoided by AvoidPits for outsiders; falls only when forced. | B: raiders walk into gentle bowls freely and out again; sheer pits still trap only by force/cover. A: also never walk down a cliff edge. Flee/wander destinations: no new failure, because non-trap ⇒ reachable. |
| **rescue / doctor / warden** | barred from trap floors unless a ladder lets them; capture/convert "down" from the lip. | Same, for trap cells only; a downed pawn in a gentle bowl is rescued on foot. |
| **falls** | `IsPitDescent(from, to) = to ≥ 4 && from < 4`; walked steps never fall, forced arrivals do (RM_PitTrapMath.cs:103-137). | A fall is an arrival on a trap cell from a non-trap cell (B), or a forced move across a cliff edge (A). Walking down a ramp into D 4 is never a fall. |
| **depth effects** | shooting from/into pits, exposure, fire, fill effects, knockback also read `IsSuperdeepExcavation`. | **Stay absolute.** Being 4 deep shields you and exposes you whether or not there is a ramp. Only "can you get out" becomes relative. (Census: 49 call sites in 13 files; ~33 are trap seams — RM_SuperdeepTrap 12, RM_PitPathing 13, RM_PitRooms 6, RM_PitTrapMath 2 — and ~14 are depth effects that stay.) |
| **performance** | trap component BFS per pawn per tick (`TryGetTrapRegion`, cap 4000 cells); open-pit grid rebuilt on signature change. | Trap flags become a cached per-map bit grid, recomputed only when a depth changes (dig, fill, bed recession), over the dug cells only. Cheaper per query than today's BFS. A's connectivity update is local (3×3, vanilla already does it on `TerrainChanged`, which every Deepen/FillIn fires via `SetTerrain`). |

## 2. What the code does today (evidence)

- Depth grid: `byte[] depthGrid`, 0 = surface, 4 = SUPERDEEP (RM_MapComponent_Excavation.cs:45; `Superdeep = 4`,
  RM_ExcavationDepth.cs:38-40). Every level change rewrites the cell's terrain (`DryTerrainFor`,
  RM_ExcavationDepth.cs:80-90) so vanilla's `TerrainChanged` event fires.
- Natural water reads as D = 4/F = 4 through a read-through adapter; `ExcavatedDepthAt` returns the *dug* depth only
  (RM_MapComponent_Excavation.cs:186). Option B of the parent design gives dry bed cells a real D (2 or 4); the
  trap must read that bed depth too (§8 note).
- Hold predicate: `RM_SuperdeepTrap.IsHeldAt` (RM_SuperdeepTrap.cs:96-118) → `RM_PitTrapMath.Held`.
- Per-step floor: prefix on `Pawn_PathFollower.TryEnterNextPathCell` (RM_SuperdeepTrap.cs:453-505); refuses a held
  pawn's step to `toD < 4`, re-plans once per cooldown, else `Notify_PatherFailed`.
- Trap component: `TryGetTrapRegion` (RM_SuperdeepTrap.cs:131-178), 8-connected D 4 BFS; "trapped" only if held on
  every cell of it.
- Reachability veto: postfixes on `Reachability.CanReach` and `CanReachMapEdge` (RM_SuperdeepTrap.cs:507-560).
- Route planner: `RM_PitTrapMath.PlanRoute` (RM_PitTrapMath.cs:223-326) + `RM_PitPathing.TryPlan`
  (RM_PitPathing.cs:207-260): legs Vanilla / AvoidPits / StayInPit / WalkTo… / StepTo; offset grids rebuilt on a
  signature of the open-pit set (RM_PitPathing.cs:66-150).
- Walking speed is already **edge-based**: `RM_Patch_PitStepCost` prefixes `PathGrid.CalculatedCostAt` with the
  previous cell (RM_PitStepCost.cs:32-87): 0 along equal depth, the deeper cell's dry cost for a climb. Route
  *planning* still sees cell costs only (its own docstring says so).
- Rooms: RM_PitRooms.cs:14-41 (five region/district/room seams, all on "superdeep or not").

## 3. How RimWorld 1.6 pathing works (grounding, decompiled via RimSage)

- **Cost grid:** `PathGridJob : IJobParallelFor` (Burst) builds one int per cell per request from
  `pathGridDirect` (terrain + things), water, fences, avoid grid, faction costs, fog, and **`custom`** — our
  `IPathGridCustomizer` offsets. `CellIsPassable` returns false for `custom[i] >= 10000`. Cell-based only.
- **Search:** `PathFinderJob : IJob` (Burst), plain A* over cells. For each expanded cell it loops the 8 directions
  **present in `connectivity[element]`**; then cost of the *destination cell* (`IndexCost`), diagonal corner checks
  on the two orthogonal cells' cost and buildings, plus `moveTicksCardinal/Diagonal`. The per-step cost does not
  depend on the source cell — but **whether the step exists does**, through the mask.
- **The mask:** `ConnectivitySource : SimplePathFinderDataSource<CellConnection>`, one of 13 sources owned by
  `PathFinderMapData`. `ComputeCellConnectivity(cell)` (managed C#) sets a direction bit when the neighbour is in
  bounds and walkable by anyone (or a destroyable building). `UpdateIncrementally` recomputes the 3×3 around every
  delta cell; deltas come from `map.events.TerrainChanged` and `PathCostRecalculate`. `ComputeAll` sets
  `AllNeighbours` minus map edges (it does not call `ComputeCellConnectivity`; a postfix must cover both).
  `PathFinderMapData.ParameterizePathJob` hands the array to every A* job (PathFinder.cs:398, :591).
  The mask is **directional** (a bit on cell a for "a → b" is independent of b's bit for "b → a") and **map-wide**
  (one array for every pawn: flyers, own faction and enemies alike).
- **Reachability** is region-based (`Reachability.CanReach` over `Region`/`RegionLink`), cached per region set, and
  knows nothing of the mask. Regions split on `RegionTypeUtility.GetExpectedRegionType` (walkability), so a cliff
  edge between two walkable cells lies *inside* one region. This mismatch (pather says no, reachability says yes) is
  the classic "job offered, path fails, job re-offered forever" loop, and it is why every relative rule needs the
  reachability side settled (the §1.4 lemma settles it for non-trap cells).
- **The follower** asks for a path in `GenerateNewPathRequest` (we already prefix it) and walks it in
  `TryEnterNextPathCell` (we already prefix it); walking speed comes from `CostToMoveIntoCell` →
  `PathGrid.CalculatedCostAt(c, false, prevCell)` (we already prefix it).

Why a per-edge rule matters: a cell-only rule can say "this cell is closed" but not "this cell is closed *from that
side*". A D 4 cell beside both a D 2 cell and a D 0 cell is enterable from one and not the other; only the mask (or
our own search) can say so.

## 4. Feasibility: from "not so bad" to "devastating"

| piece | difficulty | why |
|---|---|---|
| decide trapped-ness by component (B) | **easy** | One cached bit grid over dug cells. A flood from every surface-touching / ladder / cover exit across non-cliff edges; whatever is not reached is a trap cell. Recompute on depth change only. Every trap seam already takes "is this a pit cell" as a predicate. |
| route planning for B | **easy** | `PlanRoute` and the offset grids already take `isPit` as a delegate; pass `isTrap`. |
| reachability for B | **easy** | Lemma §1.4: only trap components need the veto, and the veto exists. |
| pit rooms for B | **moderate** | Predicate swap, but the re-region trigger widens: one dig can flip trap-ness for a whole component, so `NotifyPitnessChanged` must fire for every flipped cell, batched. |
| exact per-edge climbing (A) | **moderate, real risk** | The mask exists and is patchable, but it is map-wide: flyers, own-faction pawns (not captured by default), and ladder users all share it. Each needs a per-request swap to an unmasked array (prefix on the private `PathFinder.ParameterizePathJob(…, request)` to note the request, postfix on `PathFinderMapData.ParameterizePathJob` to swap `job.connectivity`), and the second array must be kept in step. Diagonal steps across a cliff corner need a rule. |
| body-size-dependent K | **moderate** | Trap grid becomes per size band (2–3 bands, cached); the mask in A cannot be per pawn without the swap above. |
| whole-map elevation grid (D) | **devastating** | Natural hills, LOS by height, projectile arcs, cover, roofs, rendering, mapgen, saves; every vanilla system assumes a flat map. Not needed: undug ground is uniformly height 0 for this question. |

**Bottom line: F (automatic ramp exits) is "not so bad" — it is a new kind of ladder in code we own. A is
"manageable but real work" (a vanilla array we would co-own, one derived mask per permission class). D is
"devastating" and unnecessary.** GPT's review (§9) found the draft's B underestimated: its reachability lemma was
false and its wall-scrambling is gameplay. Those findings moved the recommendation from B to F; they do not move the
verdict, because F avoids both.

## 5. Alternatives

### A. Exact per-edge climbing (connectivity mask + component traps)

Everything in B, plus a Harmony postfix on `ConnectivitySource.ComputeCellConnectivity` and `ComputeAll` clearing
the direction bit `a → b` whenever `D(a) − D(b) > K` (a climb: D is depth, so going up means D falls) or
`D(b) − D(a) > K` (a drop; pawns never walk off a cliff on purpose; a forced arrival is still a fall). GPT #5: a
ladder user or flyer cannot simply be handed the unmasked array (that frees every cliff); each permission class
needs its own derived mask with only its authorised ladder edges restored, both directions. Ladder cells keep their bits (the ladder's prison-door
rule stays in the existing per-pawn floor and route planner). A per-request swap gives flyers and exempt pawns an
unmasked array.

- **Plus:** physically exact; pawns walk ramps, never walls; raiders route around cliffs; reachability stays right
  by the lemma; the A* does the work, no custom search for most cases.
- **Minus:** a global vanilla array we co-own; the per-request swap is two private-method patches and a second
  array kept in sync; new failure mode if the mask and the trap grid disagree (mitigated: both derive from the same
  `D` and `K` in one math class, selftested together).
- **Cost:** B + ~1–2 agent-days. **Risk:** medium.

### B. "A pit traps only if it has no gentle way out" (component flag; first recommendation, withdrawn — see GPT #18 below)

Compute, per map, a **trap bit** for every dug cell: not reachable from the surface by steps of at most K levels
(rule R-deep or R-all, Q1), with ladders a pawn may climb and intact covers counting as exits as today. Replace
"D = 4" with "trap cell" in the *trap* seams only (hold, per-step floor, trap component, reachability veto, entry
veto, AvoidPits/StayInPit grids, pit rooms, fall detector, jumpers). Leave depth effects absolute.

- **Plus:** small; every seam reused; exactly the owner's sentence ("a gradual change of height ... simply walk
  out"); dried ponds never trap by construction (2 → 4 → 2 → 0 are all K = 2 steps); a player who wants an
  escapable pit digs a step — the ramp is free, no new building.
- **Minus:** in an escapable pit, a pawn may still be routed straight up a sheer wall (the planner is cell-based),
  because "escapable" is a property of the whole pit. Cosmetic, not a trap bug. Mitigation inside B: the existing
  walking-speed patch charges the full climb, so wall-scrambling is visibly slow.
- **Cost:** ~1–2 agent-days (one math class + selftest, one cached grid, ~33 call-site swaps, a live proof:
  bowl escapes, sheer pit holds, ramp dug mid-capture frees). **Risk:** low.

**GPT #18 (accepted): B's flaw is gameplay, not cosmetic.** With one ramp, every wall of the pit becomes crossable
(`AvoidPits` lifts for a non-trap component and `DryStepBaseCost` charges 0 for a step down into D 4): a moat with a
sally ramp stops being a moat for raiders, fleeing animals and haulers alike. That rules B out as the default.

### F. Automatic ramp exits (recommended; GPT #20)

Keep every pit seam on "open D = 4 cell" exactly as today. Add a **ramp exit**: a D = 4 cell with a *cardinal*
neighbour of depth ≥ 4 − K (with K = 2: a D 2 or D 3 neighbour; R-deep). Treat it in every seam the way a lowered
ladder is treated today, except that it lets **everyone** through and cannot be raised:

- **hold:** a pawn on a ramp-exit cell is not held there; the component is "trapped" only if no cell of it is a
  ramp exit or a usable ladder (`TryGetTrapRegion` already BFSes the component; add one neighbour read).
- **per-step floor:** a step out of D 4 is allowed only to a cardinal neighbour of depth ≥ 4 − K, or from a usable
  ladder cell (the edge rule lives in the `TryEnterNextPathCell` prefix, which already knows both cells). Walls stay
  walls even in an escapable pit.
- **route planner:** `PlanRoute`'s "walk inside to the way out, then StepTo" leg takes ramp exits as ways out; its
  "down a ladder or not at all" descent leg takes them as ways in. Vanilla legs keep `AvoidPits`, so A* never walks a
  wall; the staged planner is the edge-aware layer, and it already exists.
- **rooms:** an open D 4 component with any ramp exit is not enclosed, so not a room; ladders still do not count
  (a prison door does not unmake a cell). Pawn-independent, as GPT #11 requires.
- **falls:** unchanged (a forced arrival into open D 4 is a fall); walking down a ramp-exit edge is a walked step.
- **diagonals:** ramp exits are cardinal only, so no corner-cutting case exists (GPT #7).

**Plus:** smallest change that answers the owner; reuses the ladder machinery the pit already has; no global mask;
no new per-map grid; walls stay honest. **Minus:** only D 4 is ever a pit (R-deep); a pawn on a D 3 ledge beside D 0
walks up as today (D 3 is not a trap by the September ruling). Inherits today's large-lake and reachability gaps
(GPT #9, #13, #14), which a dried deep lake makes real, so they are in scope. **Cost:** ~1.5–3 agent-days.
**Risk:** low–medium.

### C. Ramps as an explicit exit (absolute traps kept)

Keep "D = 4 traps"; add a **ramp** that, like a lowered ladder that cannot be raised, makes its D 4 component
exitable for everyone. Dried pond beds get ramps automatically along their D 2 ring.

- **Plus:** tiny (reuses ladder code); legible; no new rule to explain.
- **Minus:** does not answer "gradual change of height" — a player's hand-dug gradual pit still traps unless he
  builds a ramp; the auto-ramp for beds is special pleading; two kinds of exit thing.
- **Cost:** ~0.5–1 day. **Risk:** low.

### D. Full elevation grid

A height per map cell (natural terrain included), movement by height difference, line of sight and shooting by
height, rendering.

- **Plus:** the "real" model; would carry hills and mounds later.
- **Minus:** devastating scope (see §4); contradicts nothing today but buys nothing this question needs.
- **Cost:** weeks to months. **Risk:** very high.

### E. Status quo plus a bed exemption

Keep "D = 4 traps"; dry pond beds are never traps (their D 4 cells skip the trap seams).

- **Plus:** hours.
- **Minus:** fails the owner's second sentence — a player's wide gradual pit still traps; and a bed cell the player
  digs (ruling 6: it leaves the pond) suddenly becomes trap-eligible, so a pond gains traps by being edited.
- **Cost:** ~0.25 day. **Risk:** low, but the inconsistency is permanent.

## 6. The player-dug wide gradual pit

Under B (and A), it is not a special case: the rule is the same for nature and the player.

- **Sheer pit** (every edge from D 4 to the outside is a > K rise): traps, as today.
- **Stepped pit** (a ring or a ramp of D 2/D 3 cells reaching the surface): no trap; enemies walk in and out.
- **A trap pit with one ramp** (the player's sally port): no trap, unless the ramp is cut. That is a real design
  lever: *dig a ramp to let them out, fill one square to seal it*. Filling is already a job (`FillIn`), so this is a
  door made of dirt — slow, permanent, and the ladder stays the fast, per-pawn door.
- **Digging order matters:** a pit dug level by level is gradual while it is being dug, and only becomes a trap when
  its last edge crosses the cliff line. Anything inside at that moment is trapped — consistent with "the trap
  closes when the wall is finished". The cell that closes it should read clearly (a cliff-edge outline, see Q4).
- **Width rule:** today's W×W body-size square is measured over D 4 cells; under B it is measured over trap cells.
  A big creature in a narrow trap pocket still gets out, as the owner ruled.

## 7. Recommendation

**F now (automatic ramp exits, K = 2, only D 4 traps); A only if the owner wants sheer 3-deep ditches to trap too;
never D.**

1. `RM_PitTrapMath`: `IsRampExit(depthHere, cardinalNeighbourDepths, K)` and the generalised step rule
   `StepBlocked(held, fromDepth, toDepth, K, ladderHere)`. Selftest: dried pond (D 2 ring, D 4 core) never holds;
   sheer 3×3 D 4 holds; the same with one D 2 cell to the surface frees; a ramp exit only diagonal does not free;
   a held pawn on an escapable pit cannot step straight from D 4 to D 0.
2. Seams (all existing): `IsHeldAt` / `TryGetTrapRegion` (ramp exit = way out), `TryEnterNextPathCell` floor (edge
   rule), `PlanRoute` / `PitFloorEnterable` (ramp exits as ways out and in), `RM_PitRooms` (component with a ramp
   exit is not a room; re-region every cell of a component whose ramp-exit status flips).
3. Owed work F inherits and a dried deep lake makes real (GPT #9, #13, #14): component IDs cached by generation
   instead of per-pawn BFS with a 4000-cell cap that reads "escapable" when it runs out; open-pit grid rebuilt on a
   generation counter, not a per-tick signature scan, and old arrays retired by ownership, not by 2500-tick age.
4. Parent Option B's bed cells read through one effective-depth accessor (GPT #17) before any of this sees them.
5. Mod Settings: "Gentle slopes are a way out of pits" (on; off = today), "Levels a pawn can climb in one step"
   (1–3, default 2).
6. A live proof script first (debug_process rule): pond-bed walk-out, sheer hold, ramp dug mid-capture frees, ramp
   filled re-traps, a raider never crosses a ramped moat over its wall.

**Supersession owed (on his confirmation only):** the 2026-09-17 ruling *"If you're in a superdeep pit, you can't
climb out. Period."* and the item line "Superdeep traps absolutely" (`PIT_SUPERDEEP_COLLAPSE_1.md` lines 77, 204)
would read "a superdeep pit with no gentle step out traps absolutely". Not edited here: the owner has not chosen.

## 8. Owner decisions (card-ready)

**Q1. Which pits can trap?**
- *Only 4-deep pits (recommended).* A 3-deep ditch never holds anyone, as ruled in September. Simplest.
- *Any pit whose walls are too tall to climb.* A sheer 3-deep ditch would also hold people. More realistic; changes
  a September ruling.

**Q2. How many levels can a pawn climb in one step?**
- *Two (recommended).* Dried ponds never trap (their shore is 2 deep, their middle 4).
- *One.* Steeper feel, but every dried pond would trap unless we add ramps at the shore.
- *Depends on body size* (small animals 1, people 2, huge creatures 3). Richer; a bit more work and harder to read.

**Q3. How do people get out of a pit that has a gentle side?**
- *Only by walking up the gentle side (recommended).* A 2- or 3-deep square beside the pit works like a ladder
  everyone can use; the steep walls stay walls. Small change, reuses the ladder code.
- *Once a pit has any gentle side, they can climb out anywhere.* Simplest idea, but one ramp turns a moat into
  something raiders cross wherever they like.
- *Keep pits absolute; ramps are something you build.* Smallest; a dried pond or a hand-dug gradual pit still traps
  unless you build one.

**Q4. How should a player see whether a pit traps?**
- *A cliff-edge outline on walls too tall to climb* (drawn only where a step is too high).
- *A small trap icon over trapping pits only.*
- *Nothing new; learn by watching.*

## 9. GPT review — dispositions

Review: `design/RimMandrake/relative_depth_climb_gpt_review_2026-10-12.md` (20 points, verbatim). GPT read our
source but not vanilla's; its 1.6 claims were checked against the decompiled source in §3.

| # | point | disposition |
|---|---|---|
| 1 | reachability lemma false (a sheer trench cuts two non-trap banks apart) | **ACCEPT.** Lemma struck in §1.4. The gap is pre-existing (AvoidPits already blocks what vanilla reachability crosses); F adds exits only, so it neither opens nor closes it. Filed as owed. |
| 2 | a terrain flood is not pawn reachability (walls, doors, fences, corners) | **ACCEPT** for F: a ramp exit counts only if its D 2/D 3 cell is standable; the full fix (route-validated exits) is owed with #10. |
| 3 | one map-wide trap bit cannot include selective ladders | **ACCEPT.** F keeps ladders per pawn exactly as today; only ramp exits (which everyone may use) are structural. |
| 4 | covers are not ramps | **ACCEPT.** A cover is never an exit in F; production already refuses a held pawn's climb onto a cover. |
| 5 | A needs per-class edge permissions, not wholesale unmasking | **ACCEPT**, written into A. One more reason A is not the default. |
| 6 | mask snapshots vs job lifetimes and other mods' restrictions | **ACCEPT** for A (A not recommended now). |
| 7 | diagonal escape rule missing | **ACCEPT.** F's ramp exits are cardinal only. |
| 8 | R-deep is directional; A's climb/drop labels were reversed | **ACCEPT.** Labels fixed (D is depth). F's step rule is explicitly `from D 4 to depth ≥ 4 − K`, directional, and escape is decided by "any ramp exit in the component", which needs no reverse flood. |
| 9 | reachability vetoes skip pawnless queries, other starts; endpoint modes approximated | **ACCEPT as pre-existing**, owed work in §7 step 3 because lake beds make it common. |
| 10 | ladder planner picks unreachable lips; StayInPit spans every pit; request replacement drops other customizers | **ACCEPT as pre-existing.** Ramp exits use the same planner, so fixing it is part of F's cost. |
| 11 | rooms cannot depend on per-pawn captivity | **ACCEPT.** F's room rule is structural (ramp exit or not); ladders do not unmake a room. |
| 12 | depth writes are not the only invalidation triggers | **ACCEPT.** Generation counter bumped by depth writes, cover collapse, ramp-cell obstruction and settings changes; ladders stay per-pawn reads. |
| 13 | 4000-cell cap reads as "escapable"; width check cost | **ACCEPT, top priority for lakes:** a dried deep lake core exceeds the cap. Cached component IDs with exit summaries. |
| 14 | per-tick signature rebuild retains ~625 MB on a 250×250 map under churn | **ACCEPT** (arithmetic plausible: 62,500 cells × 2 arrays × 2 bytes × up to 2500 retained ticks). Generation-gated rebuilds; retire by ownership. Pumping pulses every 250 ticks, not every tick, but the fix stands. |
| 15 | trap status is the wrong fall predicate | **ACCEPT.** F leaves falls as today (forced arrival into open D 4), not trap-ness. |
| 16 | W×W width over derived trap bits drifts | **ACCEPT.** F keeps width measured over D 4 cells, as today. |
| 17 | natural beds need one effective-depth accessor | **ACCEPT**, §7 step 4; also a prerequisite for parent Option B. |
| 18 | B's wall-scrambling is gameplay | **ACCEPT.** B withdrawn as the default (§5). |
| 19 | AI coverage asserted, not demonstrated | **ACCEPT.** The live proof script (§7 step 6) carries raiders, animals, fleeing, haul-and-return, rescue, denied ladders, blocked ramps and a topology change mid-job. |
| 20 | simpler approximation: D 4 components plus automatic ramp exits through the staged ladder planner | **ACCEPT — adopted as the recommendation (F).** The 1–2-day estimate for B is withdrawn; F is 1.5–3 days with the inherited lake work. |
