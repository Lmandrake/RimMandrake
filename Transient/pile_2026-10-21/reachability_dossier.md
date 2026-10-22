# Reachability dossier: CanReach says yes where walls + trench together cut the route (2026-10-21, BENCH helper)

Written for the owner's instruction of 2026-10-21 (~20:30 PDT): *"Document the issue thoroughly, the current solutions
that have been considered, the solutions offered here, and the specific problems being encountered. Then send it to GPT
for at least five complete solutions with relative tradeoffs made clear. Tell it to consider CPU load, latency, realism,
simplicity of code/design/tuning. … Especially include all the aspects likely to complexify it: dynamically changing pits
(drawbridges, pits being filled in or dug during transit, doors getting locked or opened, the ability to
jumpjet/teleport/fly, ladders being raised/lowered, carrying ladders or climbing gear, etc."*

Source read at commit `649aef87e1` (bench clone). `S/` = `src/RimMandrake/FlowWorks/Source/`. Vanilla = RimWorld 1.6
decompiled through RimSage. Line numbers are at that commit; another helper is editing FlowWorks, so they may drift.
Every claim is MEASURED from source unless marked UNMEASURED (not read) or INFERRED (follows from code read, not run).

## 0. Glossary (terms used below)

- **Depth D**: our per-cell dig depth in "levels" (0 = surface). A pit/trench/moat is cells with D > 0. Vanilla RimWorld
  knows nothing of depth: a dug cell is ordinary walkable ground to vanilla regions.
- **Climb limit K**: the tallest step up (in levels) a pawn can climb. Person K = 2. From body size (`RM_PitTrapMath.ClimbLimit`,
  `S/RM_PitTrapMath.cs:441`, edges 0.75/1.65/3.0 body size), plus race extension `RM_ClimbAbility`, capped at
  `MaxClimbLimit = 6` (`:436`). Climbing gear (apparel with `scalesAnyWall`) = climbs any wall.
- **Band**: one labelling per K = 1..6 (`ClimbBands = 7`, index 0 unused).
- **Pocket**: a connected component (4-neighbour steps allowed for K) with no cell at D = 0. A pawn in a pocket of its
  band with no usable ladder and room to stand is **held/trapped**. Owner ruling 1 (`PIT_SUPERDEEP_COLLAPSE_1`): *"a pawn
  is trapped when every N/S/E/W step out of its pocket is taller than it can climb"* — trapping is a DEPTH fact.
- **Region / district**: vanilla's coarse reachability graph. Regions split only on walkability/region type (walls, doors,
  fences), never on depth. `CanReach` is a BFS over regions with a per-region-pair cache.
- **Cliff masks**: our per-band copy of vanilla's per-cell A* connectivity byte with cliff edges removed
  (`S/Superdeep/RM_CliffMask.cs`). A* reads walls (from its cost grid) AND cliffs (from our mask) together, so **A* is
  correct**.
- **Pocket grid**: `RM_PocketGrid` / `RM_PocketGridMath.Label` — per-band component labels over ALL cells (walls
  included), depth-only.
- **Veto**: our Harmony postfix that can turn vanilla's `CanReach == true` into false.

## 1. The problem (mechanism, code citations)

### 1.1 What CanReach computes today
`Reachability.CanReach(start, dest, peMode, tp)` (vanilla `Verse/Reachability.cs:102-217`) =
1. `CanReachImmediate` → true; same-district shortcut for OnCell/Touch/ClosestTouch (non-water modes) → true.
2. `PassAllDestroyableThings*` modes first retry recursively as `PassDoors`; then use **cell-based** flood
   (`CheckCellBasedReachability`); all others use **region-based** BFS (`CheckRegionBasedReachability`), cached per
   region pair (`CanUseCache` is true for all modes except `PassAllDestroyableThingsNotWater` and
   `NoPassClosedDoorsOrWater`).
3. Note: it reads `map.pathing.For(traverseParams).pathGrid` — Normal or FenceBlocked, **never the Flying context**,
   even for a flying pawn (VERIFIED, `Verse/AI/Pathing.cs` `For(TraverseParms)`).

Then our postfix `RM_Patch_Reachability_SuperdeepVeto` (`S/Superdeep/RM_SuperdeepTrap.cs:890`) runs only when vanilla
said **true**, and calls `RM_SuperdeepTrap.RelativeVeto` (`:236`):
- early-outs: rule off; no dug cell on the map (`ClimbCellCount == 0`); a free pit traveller (flyer/jumper/floater);
  with the masks off, a pawn the hole does not capture; band 0 (climbs everything).
- `cs = ComponentOf(k, start)`; if dest (or, for Touch, any cell of its rect expanded by 1) is in `cs` → **no veto**.
- otherwise judges pocket-ness, width and ladders (`RM_PocketGridMath.ReachVetoedWhole`, ladder graph
  `JoinedByLadders`).
- Pawnless queries (vanilla `Pawn_PathFollower.StartPath` asks a pawnless `PassDoors` CanReach before every walk) are
  answered for the walking pawn via `RM_Patch_PathFollower_ReachWalker` (`:945`).

`RM_Patch_Reachability_SuperdeepMapEdge` (`:974`) does the same for `CanReachMapEdge`: veto if the start component is
trapped or (not a narrow walk-out pocket and) `!ReachesEdge` — again on the depth-only labels.

### 1.2 Why the AND is wrong
The pocket grid labels **every cell, walls included** (`S/RM_PocketGridMath.cs:16-17`): *"Walkability is deliberately NOT
an input: the grid is depth-only, so building or removing a wall never makes it stale. Vanilla reachability already
accounts for walls, and the reachability seam ANDs the two."*

So CanReach = (route exists in the walls-but-no-depth graph) AND (route exists in the depth-but-no-walls graph). Two
different routes can satisfy the halves while **no single route satisfies both**. Reachability is a property of the joint
graph; an AND of two projections is not that. A* (`FindPathNow`) reads the joint graph (vanilla cost grid with walls +
our per-band mask) and correctly finds nothing.

The error is always a **false yes**, never a false no, and needs all three:
1. a dug cell on the map (else early-out),
2. a pawn the veto applies to (every non-free-traveller while the cliff masks are on — the default),
3. walls and a cliff that cut a route **only together**.

### 1.3 Same shape elsewhere (found while reading)
- **Deep water for non-swimmers** (`S/Swimming/RM_Swim.cs:1011`, `RM_Patch_Reachability_NonSwimmer`): swim water is made
  walkable in the path grid so regions/reachability see open water (file header, `:14-25`); a non-swimmer is barred
  from crossing only by an A* offset grid (`RM_SwimPathing.Grid`, offsets ≥ 10000), and the CanReach postfix checks only
  whether the **destination** needs standing in deep water. So a non-swimmer behind a deep-water moat gets CanReach =
  true and A* = no path. INFERRED from source, UNMEASURED live. Same class of lie, any fix should cover it.
- Vanilla `CanReach` ignores the Flying pathing context (above), so for flyers vanilla's own answer is the walking one.

### 1.4 Cost of today's veto
Per query on a dug map: 2-3 `int[]` reads, a few cached-set lookups, sometimes the ladder graph (cached per band, pawn,
tick). Grids: up to 8 per map (plain + strides 1..3 for titans, + floor views 0..3 under suspension decks) × 6 bands,
each rebuilt only when `ClimbGeneration` moves, throttled to once per `RebuildMinTicks = 60` (`RM_PocketGrid.cs:31`;
`ForceRebuild` at `:177` bypasses it, used by drawbridges). Rebuild = one BFS per band over all n cells (62,500 on 250²).
Rebuild time in ms: UNMEASURED.

## 2. Concrete failures seen

### 2.1 Drawbridge winch, LOWER_ONLY_FROM_WINCH (MEASURED live)
Site A (origin 140,140), `S/../northstar/drawbridge_proof.py`: trench x=1..4, z=0 only; granite walls at z=±1 for
x=-2..9, caps at (-3,0)/(10,0); timber leaf (0,0)-(5,0) raised; winch at (-1,0); far pawn at (7,0).
- Vanilla regions: far bank → trench floor (walkable to vanilla) → lip → winch. Reachable.
- Pocket grid: at depth 0 the wall cells z=±1 join both banks round the trench ends. Same component, no veto.
- A*: no path (walls close the round-the-end route, the cliff closes the floor route).
- `Transient/pile_2026-10-21/drawbridge_live_rerun4.json` (mod_hash 5bdf2170…): `farLower: WORK job=True spot=winch`
  (the far pawn was offered the lower job), and `noWalkRound: behind=PATH found=False | lip=PATH found=False`.
  Status FAIL, class MOD.
- Symptom in play: job offered → `StartPath` → A* fails → `PatherFailed` → job ends → offered again next scan. A loop,
  and a costly one: a failing A* explores the whole reachable area before giving up.

### 2.2 The narrow fix already shipped
`WorkGiver_Drawbridge.JobOnThing` now requires `FindPathNow(...).Found` after the cheap checks
(`S/Pits/Drawbridge/RM_DrawbridgeControl.cs:230-241`, commit `93cdbdc40a`; harness tick-10 fix `7e904f0985`). Live
PASS: `Transient/pile_2026-10-21/drawbridge_winch_reach2.json` (farLower job=False, winchLower job=True, farRaise True).
Then 12/12 drawbridge rows PASS (`drawbridge_all_final2.json`). CanReach itself still lies; only this caller is gated.

Lesson from that run (harness): the 1.6 pathfinder reads its map data in `PathFinderMapData.GatherData` once per tick;
a scene built while paused is invisible to A* until ~10 ticks pass (`drawbridge_pair_night.md`). Any fix that compares
CanReach with A* must respect this.

### 2.3 CanReachMapEdge (INFERRED, not observed)
A walled compound whose only wall gap is cut by a trench "reaches the map edge" (depth-only `ReachesEdge` AND vanilla
regions). Flee / exit-map / visitor-leave logic would pick a plan that cannot be walked. No live row has shown it.

### 2.4 Other callers exposed (INFERRED)
Any job giver using CanReach: hauling, construction, rescue, doctor, warden walks, raider `GotoNearestHostile`,
`JobGiver_AIFightEnemy` reach checks, hunting. Vanilla callers cannot be spot-fixed one by one. Our raider logic
(`RM_RaiderTrench.TryCross`, `S/Superdeep/RM_RaiderTrench.cs:477`) decides "cross the trench" only when CanReach
(`PassAllDestroyableThings`) is false, so a false yes there means the raid walks into a path failure instead of
setting ladders. (In PassAllDestroyable modes walls are passable in both graphs, so the AND is closer to exact there.)

## 3. History

- **2026-10-12, design** `design/RimMandrake/relative_depth_climb_design_2026-10-12.md`:
  - §3: *"Regions split on … walkability, so a cliff edge between two walkable cells lies inside one region. This
    mismatch (pather says no, reachability says yes) is the classic 'job offered, path fails, job re-offered forever'
    loop."*
  - §8.3: *"keep a per-map component id over walkable cells … counting ramps but not ladders, and **using vanilla
    walkability**."* (Note: in the design, pockets themselves would be wall-aware too.)
  - §8.5 step 6: AND vanilla with "same band component"; *"The conservative false negative (vanilla's route crosses a
    cliff, ours crosses a locked door) is accepted and logged once per pawn."*
- **2026-10-13, build** `ae8d38f27c` (item `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP`): the labeller dropped walkability
  (comment quoted in 1.2). Reason stated: the grid never goes stale on wall changes. **No owner ruling found behind the
  change**; it was a build convenience whose premise ("ANDing is enough") the drawbridge site falsified.
- **2026-10-21**: drawbridge pair diagnosis (`Transient/pile_2026-10-21/drawbridge_pair_diagnosis.md`) found the mechanism;
  winch gate shipped; options memo (`Transient/pile_2026-10-21/relativeveto_options.md`, commit `adff09af28`);
  lesson `infrastructure/state/lessons/20261022T024230Z-BENCH-relativeveto-ands-vanilla-regions-walls-no.md`.

## 4. Solutions already considered (from the memo)

| | idea | fixes | main cost / risk |
|---|---|---|---|
| (a) | keep the AND; per-caller `FindPathNow` gate (winch done; raider winch and `RM_WallClimb` already gate) | our callers only | vanilla callers keep the loop forever; every new job giver must remember it |
| (b) | make the pocket grid itself wall-aware (design §8.3 literally) | every caller | pocket-ness becomes wall-dependent: a wall across a ramp top makes a pit a pocket → held, pit room, capture; contradicts ruling 1; save-visible; rebuild on every wall change |
| (c) | cut vanilla region links at cliffs (combined region overlay) | everything, inside vanilla's cache | 6 bands vs one pawn-independent region set; transpilers in region code; region count explodes on dug maps; highest risk, multi-day |
| (d) | a SECOND, wall-aware "reach labelling" per band, used only by the veto (memo's pick) | walls + cliffs for every caller incl. vanilla, CanReach and CanReachMapEdge | +rebuilds on walkability change (UNMEASURED ms); +memory 6×n ints per grid view; per-pawn doors/fences remain a residual |
| (e) | bounded A* confirm whenever the veto passes | exact incl. per-pawn doors | CanReach is called thousands of times per tick; failing A* floods; needs a hard-to-invalidate cache |

Memo recommendation: (d) + keep (a)'s winch gate. Draft ruling line in the memo.

## 5. Complications (every dynamic; how today's code handles it)

| # | dynamic | today (measured from source) | what a fix must decide |
|---|---|---|---|
| C1 | **Drawbridge raised/lowered** | Leaf toggle → `RM_Drawbridges.NotifyToggled` (`S/Pits/Drawbridge/RM_Drawbridges.cs:339`): recost path grid, `reachability.ClearCache()`, `BumpClimbGeneration`, swim bump, `RM_PocketGrid.ForceRebuild` (immediate, no 60-tick wait), `RepathOver` every pawn whose path crosses a changed square (`:359`). Leaf decks are ground in `EffectiveDepth`. | A wall-aware labelling must also rebuild at once on a toggle; the leaf's raised state is a depth change, not a walkability change. |
| C2 | **Drawbridge gate (a locking door)** | `Building_DrawbridgeGate.PawnCanOpen` (`RM_DrawbridgeControl.cs:340`): opens for nobody while its leaf is off its seat; while the map is LOCKED (a free hostile, R4) only when held open. Vanilla region BFS reads doors per query (`Region.Allows`, ByPawn → `CanPhysicallyPass`), but the region-pair result is CACHED; whether a lock/unlock clears that cache: UNMEASURED. | Doors are per-pawn; a pawn-independent label must treat doors as open (vanilla then decides doors). |
| C3 | **Pits dug or filled during transit** | Depth writes bump `ClimbGeneration` (`RM_MapComponent_Excavation.cs:320` and callers); grid rebuilt ≤ 60 ticks later. A walking pawn: vanilla `NeedNewPath` looks 20 nodes ahead for walkability/doors only (not depth). Our per-step floor (`RM_Patch_PathFollower_SuperdeepFloor`, `RM_SuperdeepTrap.cs:772`) refuses a now-illegal step, re-plans once per 60 ticks (`ResetToCurrentPosition`, `:833`), else `PatherFailed`. Cliff masks re-derive in `GatherData` the next tick. | Stale window ≤ 60 ticks for the reach labels (a false yes or false no for ≤ 1 s); the per-step floor is the backstop. |
| C4 | **Doors locked/opened; faction doors** | Vanilla `Building_Door.PawnCanOpen`: `CanOpenDoors`, factionless doors per race, `MachinesLike(faction)`; hostiles may bash (`canBashDoors`). Our `Building_RM_FlowDoor.PawnCanOpen` (`RM_FlowDoors.cs:40`): sluice/grate do not open for a pawn held in a pit. Ancient hackable/jammed doors are vanilla subclasses. | Per-pawn; residual for any pawn-independent label. |
| C5 | **Animal fences** | Vanilla: `Pathing.For(tp)` picks the FenceBlocked context for fence-avoiding pawns; region type Fence blocks them (`Region.Allows`). Our code: fences are fall rails (`RM_FallRails`) only; nothing reads `fenceBlocked`. | Per-pawn-class (two vanilla path grids: Normal, FenceBlocked). A fix could keep two passability inputs. |
| C6 | **Flyers (MaxFlightTime)** | `RM_PocketGrid.CanFly` (`:375`): flying now, or `MaxFlightTime` stat > 0 (Core 1.6). `FreePitTraveller` (`:396`) = flyer, or race `RM_PitTravelExtension` jumps/floats with the setting on. Free travellers skip the veto, the masks (`RM_CliffMask.Swap` gives them vanilla's array), the floor and falls. Vanilla: a flying pawn paths on the Flying path grid (`Pawn.GetPathContext`), but **vanilla CanReach never reads it**. | Flyers stay exempt; nothing new. A grounded flyer (on cooldown) still counts as free (owner rule "flyers never trapped"). |
| C7 | **Jump packs / jump abilities** | Vanilla `JumpUtility.OrderJump` picks a target by range + LOS with `reachable: false`; `ValidJumpTarget` needs walkable, unfogged, no closed door. Jumps are `PawnFlyer`s, not paths; reachability never sees them. Our raiders use `CastJump` across trenches (`RM_RaiderTrench.cs:325`); `RM_FallRails` stops throws (not jumps) at rails. Landing in a pocket strands (ruling 3). | Out of reachability; a planner that wants jumps must add them as its own edges (as RM_RaiderTrench does). |
| C8 | **Teleport / skip** | Our jump-into-pit order teleports (`RM_SuperdeepTrap.cs:~475`, `Notify_Teleported`) then resolves the fall. Vanilla skip abilities: target by range/LOS (UNMEASURED in detail). | Out of reachability (as C7). |
| C9 | **Ladders raised/lowered** | `RM_CompLadder.SetRaised` (`RM_LadderUtility.cs:380`) bumps `StateVersion` and `ClimbGeneration`. Ladders are NOT in the pocket grid; `LadderEdges` (per band, pawn, tick, StateVersion) joins components; prison-door rule per pawn (`RM_LadderRules.LadderLetsOut`: own faction / allowed). A* closes a ladder per pawn via an offset grid. | A wall-aware reach labelling must re-key ladder edges onto reach components (the ladder's square and its top square). |
| C10 | **Carried / portable ladders** | `RM_LadderPortable`: always down, spans only some levels (`EffectivelyRaised` false for portable, `:351`). Raiders set portable ladders of their faction (`RM_RaiderSetLadder`); their spawn bumps ClimbGeneration (`:396`, `:522`, `:536`). A ladder being carried is not a ladder until set. | Same as C9. A pawn carrying one could "plan to cross" — today only RM_RaiderTrench plans that. |
| C11 | **Climbing gear** | `ClimbLimitOf` → `ClimbLimitWithGear`: worn gear with `scalesAnyWall` = band 0 ("climbs every step") → veto skipped entirely; slow per level. Putting gear on/off changes the band instantly (read per query). | Gear wearers are band 0; nothing new. |
| C12 | **Sappers / breachers** | `PassAllDestroyable*` modes: vanilla does cell-based reachability with walls passable (`CheckCellBasedReachability`); our veto still runs (no mode check in `RelativeVeto`) on the depth-only labels, which is exact there (walls passable in both). `RM_DrawbridgeRaid.WinchJob` and `RM_WallClimb` already gate by `FindPathNow` in PassAllDestroyable modes. | A wall-aware check must SKIP these modes (walls are passable to them). |
| C13 | **Titans stepping over trenches** | `RM_TrenchStride`: per-stride bridged-depth grids and masks (`MaxStride = 3`); `RM_PocketGrid.ForPawn` picks the view. | Each stride view needs its own reach labels too (multiplies memory/rebuild). |
| C14 | **Suspension bridges / decks / covers / planks** | Decks are ground at their walking height (`EffectiveDepth`); spawn/despawn bumps ClimbGeneration (`Building_SpanDeck.cs:68,75`). Floor view vs deck view for pawns under a deck (`ReachGridView`). Raid planks (`RM_RaidPlanks`) are laid decks. Cover collapse = depth change. | Views multiply as C13. |
| C15 | **Deep water / swimming** | §1.3: same false-yes class for non-swimmers; crossing closed only in A*. Swim water is passable in regions. | A fix could add "deep water impassable for non-swimmers" as a per-swim-class input, or leave it. |
| C16 | **Ramps** | Ramp pairs join their squares for every band (`RM_PitRamp.Pairs`, used in `Build`). Spawn/despawn bumps ClimbGeneration. | Unchanged; also in reach labels. |
| C17 | **Walls built / destroyed (breach)** | Vanilla re-regions on walkability change; `ConnectivitySource.UpdateIncrementally` re-derives the 3×3 (our `RM_Patch_ConnectivitySource_Incremental`, `RM_CliffMask.cs:460`, already sees every delta). Vanilla's connectivity byte treats **destroyable impassable buildings as connected** (`ComputeCellConnectivity`); walls are closed in A* by the cost grid. The pocket grid ignores walls. | The new invalidation trigger; a breach must open the reach labels quickly (a false "unreachable" after a breach is visible). |
| C18 | **Gravships (Odyssey)** | `RM_DrawbridgeGravship`: bridges crossing the ship's edge collapse at launch. Launch/landing removes/adds substructure terrain (region rebuild). Depth under a landed ship: UNMEASURED. | Treat as terrain + depth changes. |
| C19 | **Map edge** | `CanReachMapEdge` postfix (`:974`) uses depth-only `ReachesEdge`; same false yes as 2.3. | Must use the same joint answer. |
| C20 | **Pawnless queries** | `StartPath`'s pawnless `PassDoors` query answered for the walker (`ReachWalker`); else person band, any lowered ladder counts. | Same rules for reach labels. |
| C21 | **Pawn too wide for a narrow pocket** | `WideEverywhere`/`RequiredWidth` (W = max(1, round(sqrt(BodySize)))): a pocket too narrow to hold it is walked out of; masks give it vanilla's array (`InOwnPocketTooNarrow`). | Unchanged. |
| C22 | **1.6 path batching latency** | Path jobs are batched; map data refreshed in `GatherData` once per tick; a scene staged while paused is invisible to A* for ~10 ticks (measured, harness). Drawbridge `RepathOver` also re-sends pending requests. | Any "confirm with A*" option inherits this; any label rebuild should not be read mid-region-build (`RM_PitRooms` reads `IsPersonPocketCell` mid-flood). |

## 6. Constraints any solution must keep

1. **Ruling 1**: trapping/held/pit rooms/capture stay a DEPTH fact (walls never trap a pawn).
2. **Ruling 4**: a ladder is a prison door (per-pawn permission), not a path cost.
3. **Flyers / jumpers / floaters never trapped** (design §8.2; `FreePitTraveller`).
4. Every mod ships Mod Settings (on/off per major feature, defaults = shipped behaviour).
5. Biome mechanics promised only inside our biomes, but FlowWorks pits work on any map.
6. A* (cliff masks + vanilla cost grid) is the ground truth for "can this pawn walk there"; the target is CanReach ==
   A*-found on every probe pair a proof can stage.
7. CanReach is vanilla's hottest reachability call (work scanners call it per candidate thing); per-query cost must stay
   O(1)-ish.
8. Per-pawn door/fence semantics belong to vanilla; the design already accepted a logged conservative residual there.
