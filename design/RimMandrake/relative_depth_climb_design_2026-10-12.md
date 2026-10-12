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

**Resolved (owner, 2026-10-12, §10; design §8):** trapping is relative and per creature. A pawn is trapped when no
chain of N/S/E/W steps it can climb leads to the surface, and its climb limit comes from its height (a person climbs
1 fast, 2 slow; 3 or more traps it; small creatures are trapped by 2). Gradual slopes never trap. A built ramp
spans up to 3 levels at walking speed; a ladder spans any depth, slowly. The implementation is Alternative A: per-band
connectivity masks plus a cached pocket grid. There is no elevation concept beyond the existing depth grid, and no
trap indicator in v1.

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

**Bottom line (feasibility, before the rulings): F (automatic ramp exits) is "not so bad" — it is a new kind of ladder in code we own. A is
"manageable but real work" (a vanilla array we would co-own, one derived mask per permission class). D is
"devastating" and unnecessary.** GPT's review (§9) found the draft's B underestimated: its reachability lemma was
false and its wall-scrambling is gameplay. Those findings moved the recommendation from B to F; they do not move the
verdict, because F avoids both.

## 5. Alternatives

### A. Exact per-edge climbing (connectivity mask + component traps) — the chosen shape, §8

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

### B. "A pit traps only if it has no gentle way out" (component flag; withdrawn, GPT #18)

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

### F. Automatic ramp exits (GPT #20; not chosen: the owner ruled a per-creature relative rule, §8)

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

## 8. Resolved design (owner rulings §10, 2026-10-12)

This section is the build spec. Numbers marked PROVISIONAL are ours, not his; each is a Mod Settings value.
§5's alternatives are the analysis that led here. Alternative A (exact per-edge climbing) is the shape he chose,
with a per-creature step limit instead of one K.

### 8.1 The rule

- Every cell has a depth `D` (0 = surface; dug cells 1..`MaxDepth`; a dry natural bed reads its bed depth through
  the one effective-depth accessor of the pond design, GPT #17).
- Between cardinal neighbours `a` and `b`, the **step** is `D(a) − D(b)` (positive = climbing up out of `a`).
- Each pawn has a **climb limit `K`**, the most levels it can climb in one step (8.2).
- A walked step from `a` to `b` is allowed when `|D(a) − D(b)| ≤ K`, or when a ramp or a ladder the pawn may use
  joins the two cells (8.4). Nobody walks *down* a step taller than `K` on purpose either (no voluntary cliff jumps).
  A forced arrival across such a step is a **fall** (8.6).
- **Diagonal steps** are allowed only when both cells and both cardinal corner cells are within `K` of each other.
  That rules out corner-cutting a cliff (GPT #7).
- A pawn is **trapped** when no chain of allowed steps leads from its cell to a cell at `D = 0`. Gradual slopes never
  trap anyone, because every step on them is ≤ `K`. Ladders and ramps are steps.
- The capture policy is unchanged. Today a colonist is only ever in a pit by jumping, by force, or down a ladder.
  The rule is now plain physics for everyone, so nothing about who is "captured" needs a separate flag.
- **Depth effects stay absolute**: shooting into and out of a pit, cover, exposure, fire and fill effects key on
  `D`, not on whether the pawn is trapped (§1.4, last-but-one row).
- **The W×W width rule stays**, measured over the cells of the pawn's own pocket (8.3), not over D 4 cells. A
  creature wider than the pocket braces across it and walks out, as ruled in September.

### 8.2 Climb limit by creature size (all PROVISIONAL)

Height is not a vanilla stat. We derive it from body size, using the draw scale that already exists
(`RM_PitDrawMath`: 0.3 cells per level, a person 1.0 cell feet to crown, RM_PitDrawMath.cs:28-34):

- height `H = 1.0 × sqrt(bodySize)` cells (life stage included, so a child is shorter);
- a pawn can climb a wall up to 70% of its height, so `K = max(1, floor(0.7 × H / 0.3))`;
- the formula only places the band edges below. Players read the bands, never the formula.

| band | body size | examples (vanilla) | K | trapped by a sheer step of |
|---|---|---|---|---|
| small | under 0.75 | rat, squirrel, hare, cat, dog, child | 1 | 2 or more |
| person-sized | 0.75 to 1.65 | human, most xenotypes, deer, wolf (warg) | 2 | 3 or more |
| large | 1.65 to 3.0 | muffalo, bear, tall aliens with a raised body size | 3 | 4 or more |
| huge | 3.0 and over | thrumbo, elephant, megasloth | 4 | never, while `MaxDepth` is 4 |

Modifiers (each a `DefModExtension` `RM_ClimbAbility { int extraLevels; bool leaper; }`, patched onto races; also
PROVISIONAL):
- **climbers** (insects and arachnids, monkeys, squirrels): +1 level;
- **leapers** (hares, cats, anything with a vanilla jump ability): +1 level;
- **flyers** (`MaxFlightTime` > 0, or flying right now): never trapped, as today.

Speed of a climb, for a step up of `s` levels (`s ≤ K`):
- `s < K`, or `K = 1`: a normal climb. Its cost is today's `DryStepBaseCost` climb cost, which charges the deeper
  cell's dry path cost.
- `s = K ≥ 2`: a **slow climb**, ×2 that cost (PROVISIONAL). So a person climbs 1 fast and 2 slow, as he ruled.
- Climbing down a step costs the same as climbing it up. Walking along equal depth costs 0 extra, as today.

**Player-facing text.** He ruled that the size table is stated, not hidden. The FlowWorks pit guide entry and the
Mod Settings tooltip print the table above, generated from the live band edges. The race's inspect pane carries
one line: "Climbs out of steps up to K deep."

### 8.3 Pockets: the cached trap grid

- For each band `K` = 1..4, keep a per-map component id over walkable cells. Two cells join when the step between
  them is allowed for `K` (8.1), counting ramps but not ladders, and using vanilla walkability. This is a union-find
  over the map, about 62,500 cells × 4 bands on a 250² map.
- A **pocket** for `K` is a component with no cell at `D = 0`. A pawn is held when it is in a pocket of its band,
  there is no ladder in that pocket it may use, it is not flying, and the pocket is at least W×W.
- **Invalidation** is by a generation counter (GPT #12, #14). The counter is bumped on any depth write (dig, fill,
  bed recede or restore), any ramp spawn or despawn, cover collapse, and any change to the climb settings. The grid
  is rebuilt lazily, at most once per 60 ticks, and only when the generation moved.
- This **replaces** `TryGetTrapRegion`'s per-pawn BFS and its 4000-cell cap (GPT #13). A dried deep lake is just a
  big component.
- Ladders stay a per-pawn read, as today (`RM_LadderRules.LadderLetsOut`). The pocket grid answers "is there any
  ladder in this pocket", and the pawn check answers "may this pawn use it".

### 8.4 Ramps and ladders

**Ramp (new building, `RM_PitRamp`)**
- 1×1, built on a dug cell, rotatable. Its rotation points uphill.
- It joins its own cell to the cardinal neighbour it faces, when that neighbour is 1 to 3 levels shallower. That
  step is allowed for **every** pawn, of any size, in both directions, with **no movement penalty**: the cost of a
  walk on flat ground. The owner's "swiftly (but not instantly)" is the normal walking tick cost.
- A deeper drop takes a second ramp, or a ramp then a climbable step: for example D 4 →(ramp)→ D 1 → D 0.
- Structural: it enters the pocket grid for every band. Enemies use it too. Deconstructing it re-seals the pit.
- Placement refuses a facing neighbour that is not 1 to 3 levels shallower, and a cell already holding a ladder.
- Cost and art PROVISIONAL: 25 wood or stone blocks, one build job. Art is owed through the art ledger, with a
  placeholder until then.
- Mod Settings: "Ramps" (on), "Levels a ramp spans" (1–3, default 3).

**Ladder (existing `RM_Ladder`, changed)**
- It now joins its cell to **any** shallower cardinal neighbour, whatever the depth difference. That is the
  owner's "arbitrarily deep".
- The step is slow: `LadderTicksPerLevel × levels` (PROVISIONAL: twice a normal climb per level), so a ladder is
  always slower than a ramp.
- Raise/lower and the prison-door rule are unchanged and per pawn.
- A ladder is not structural, so the pocket grid only records that a ladder is present.

### 8.5 Pathing, reachability and rooms: what changes in code

1. **`RM_PitTrapMath` (pure, selftested):**
   - `ClimbLimit(bodySize, extraLevels, settings)`;
   - `StepAllowed(fromD, toD, K, rampJoins, ladderJoinsForPawn)`;
   - `StepCost(fromD, toD, K, viaRamp, viaLadder)`;
   - `DiagonalAllowed(...)`.
   - These replace `StepBlocked(held, toDepth)` and `IsPitDescent`. Selftests: a dried pond (D 2 ring, D 4 core)
     never traps a person; a sheer D 3 pit traps a person and not a muffalo; a sheer D 2 pit traps a rat and not a
     person; a ramp D 4→D 1 frees everyone; a D 4 pit with one ramp still refuses a wall step; no diagonal cliff cut.
2. **Connectivity masks** (Alternative A, §3):
   - Keep four derived band masks, `vanilla & ~cliffEdges(K)`, with ramp and ladder edges restored.
   - Postfixes on `ConnectivitySource.ComputeAll` and `UpdateIncrementally` re-derive the affected 3×3 after vanilla
     has computed its own bits. Vanilla's array is never written.
   - **Per-request swap:** a prefix on `PathFinder.ParameterizePathJob(…, request)` notes the pawn, and a postfix on
     `PathFinderMapData.ParameterizePathJob` sets `job.connectivity` to that pawn's band mask.
   - Flyers get vanilla's mask. A pawnless request gets the person band, K = 2.
   - A ladder this pawn may not use is closed per request through the existing `IPathGridCustomizer` offset (custom
     ≥ 10000 on the ladder cell). That one floor cell is lost to that pawn, which is accepted.
   - Memory: 4 bytes per cell, about 250 KB on 250².
3. **`RM_PitPathing`:**
   - Delete the AvoidPits and StayInPit legs and the ladder-staging planner (`PlanRoute`); the masks make vanilla A*
     edge-correct.
   - Keep `GenerateNewPathRequest` only for the ladder offset. This also retires GPT #10 (the planner picked
     unreachable lips and its request replacement dropped other customizers) and GPT #14 (the per-tick signature
     rebuild).
4. **Per-step floor:** the `TryEnterNextPathCell` prefix (RM_SuperdeepTrap.cs:453-505) checks `StepAllowed` for
   every pawn, not only held ones. It is a guard against stale paths and other mods' movers. A refused step re-plans
   once per cooldown, then `Notify_PatherFailed`, as today.
5. **Walking speed:** `RM_Patch_PitStepCost` (RM_PitStepCost.cs:32-87) calls `StepCost` (slow climb at `s = K`,
   ramp 0, ladder slow).
6. **Reachability:**
   - Postfixes on `Reachability.CanReach` and `CanReachMapEdge` AND vanilla's answer with "same band component".
     A pocket can never reach the surface; two surface areas cut apart by a map-spanning trench are told apart too.
     That closes GPT #1.
   - The conservative false negative (vanilla's route crosses a cliff, ours crosses a locked door) is accepted and
     logged once per pawn.
   - Pawnless queries use K = 2 (GPT #9).
7. **Rooms:** a pit room is a person-band pocket (K = 2). That is pawn-independent (GPT #11), and a prison of a sheer
   D 3 pit now works. RM_PitRooms' five seams swap the predicate. Re-regioning fires for every cell whose pocket
   status flips, batched per generation.
8. **Falls:** `DescentFalls` becomes "a non-walked arrival whose drop is greater than this pawn's `K`". Fall damage
   scales by drop ÷ `MaxDepth` (PROVISIONAL), replacing today's flat drop into D 4.
9. **Jump gizmo:** it lands the jumper as a forced arrival, so the fall rule applies. A jump into a pocket of its band
   strands the jumper, as ruled.

**Mod Settings** (every mod ships superb ones):
- "Pits trap by relative height" (on; off = today's absolute D 4 rule, kept as a fallback branch);
- "Climb ability multiplier" (0.5–2, scales `H`);
- "Slow climb factor" (1–4, default 2);
- the ramp settings in 8.4;
- "Ladder speed".

**No trap indicator in v1** (Q4): the pit-lip art occlusion (`RM_PitLipOcclusion`, `RM_PitDrawMath`) is the cue.

### 8.6 Live proof script first (debug_process rule)

`src/RimMandrake/FlowWorks/northstar/` gains a climb proof. Each row reads the pawn's position and job and the
pocket grid; there are no flyer flight checks (standing rule). Rows:
- a person walks out of a dried pond (D 2 ring, D 4 core);
- a person is held in a sheer 3×3 D 3 pit, and a muffalo walks out of it;
- a rat is held in a sheer D 2 pit;
- a ramp built mid-capture frees the pit, and deconstructing it re-traps;
- a raider never crosses a ramped moat over its wall;
- a hauler fetches from a ramped pit floor;
- a ladder's prison-door rule still holds;
- a save and reload keeps every pocket identical.

### 8.7 Cost

About 3–5 agent-days, split into three build items:
1. the math, the pocket grid, holding, rooms and reachability;
2. the connectivity masks, the step floor and step cost, and retiring the staged planner;
3. ramps, ladder span and speed, settings and player text.

The live proof is written with item 1 and grows with each item.

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
| 9 | reachability vetoes skip pawnless queries, other starts; endpoint modes approximated | **ACCEPT as pre-existing**, closed by §8.5 step 6 because lake beds make it common. |
| 10 | ladder planner picks unreachable lips; StayInPit spans every pit; request replacement drops other customizers | **ACCEPT as pre-existing.** Ramp exits use the same planner, so fixing it is part of F's cost. |
| 11 | rooms cannot depend on per-pawn captivity | **ACCEPT.** F's room rule is structural (ramp exit or not); ladders do not unmake a room. |
| 12 | depth writes are not the only invalidation triggers | **ACCEPT.** Generation counter bumped by depth writes, cover collapse, ramp-cell obstruction and settings changes; ladders stay per-pawn reads. |
| 13 | 4000-cell cap reads as "escapable"; width check cost | **ACCEPT, top priority for lakes:** a dried deep lake core exceeds the cap. Cached component IDs with exit summaries. |
| 14 | per-tick signature rebuild retains ~625 MB on a 250×250 map under churn | **ACCEPT** (arithmetic plausible: 62,500 cells × 2 arrays × 2 bytes × up to 2500 retained ticks). Generation-gated rebuilds; retire by ownership. Pumping pulses every 250 ticks, not every tick, but the fix stands. |
| 15 | trap status is the wrong fall predicate | **ACCEPT.** F leaves falls as today (forced arrival into open D 4), not trap-ness. |
| 16 | W×W width over derived trap bits drifts | **ACCEPT.** F keeps width measured over D 4 cells, as today. |
| 17 | natural beds need one effective-depth accessor | **ACCEPT**, §8.1; also a prerequisite for parent Option B. |
| 18 | B's wall-scrambling is gameplay | **ACCEPT.** B withdrawn as the default (§5). |
| 19 | AI coverage asserted, not demonstrated | **ACCEPT.** The live proof script (§8.6) carries raiders, animals, fleeing, haul-and-return, rescue, denied ladders, blocked ramps and a topology change mid-job. |
| 20 | simpler approximation: D 4 components plus automatic ramp exits through the staged ladder planner | **ACCEPTED then overtaken:** F was the draft recommendation; the owner's §10 rulings chose a per-creature relative rule (§8), built as A. |

## 10. Owner rulings on §8 — 2026-10-12, 07:10 PDT (verbatim, by question card)

§8 is the design these produced. They reword the 2026-09-17 "you can't climb out. Period."

- **Q1 (which pits trap):** *"It was intended originally that a 3-deep trench can trap a normal person and a 4-deep trench can trap even tall aliens above human height and some large creatures. In truth it should simply be a function of creature height of course. Even a 2-deep trench could trap rat-sized creatures unless they can climb or leap great distances. And it should be relative height (the depth of the pit relative to its N, S, E, W, neighbors) so that gradual slopes never trap anyone."*
- **Q2 (step limit):** *"Human-sized pawns should climb two at a time (slow) or one a time (faster). Three or more traps. This changes depending on creature size. It isn't hard to communicate to a player in the text what sizes of creatures get trapped by what depth."*
- **Q3 (getting out):** *"Ramps are an interesting idea here... ramps & stairs could descend swiftly (but not instantly) without movement penalty. A ramp could take up 1 square but go down up to 3 levels at a time without movement penalty. A ladder can go down arbitrarily deep but still goes somewhat slow (4 or more even)."*
- **Q4 (showing it):** *"I really don't think it will be a surprise when they see the art occlusion. If you can't even see your pawn's body because of a cliff, it's no surprise when they can't walk through it. Let's try it without such indicators at first."*

Design consequences (now §8): the climbable step is a function of creature height (body size / climb-leap ability), judged against
the N/S/E/W relative step; a human climbs a 1-step fast and a 2-step slow, and 3+ traps them; a built ramp occupies 1 square and
spans up to 3 levels with no movement penalty; a ladder spans any depth, slowly; no trap indicator in v1; the size→depth table
is stated in player-facing text.
