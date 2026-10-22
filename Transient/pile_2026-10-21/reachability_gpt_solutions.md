**I recommend a separate reachability graph made of wall-and-cliff-aware chambers joined by permission-controlled doors and ladders—solution 2 below.** Keep `RM_PocketGrid` exclusively responsible for depth-only trapping, held status, capture and pit rooms.

The memo’s second wall-aware grid is a useful baseline, but treating doors as open and ANDing its answer with vanilla still permits the same two-route false yes. Meeting the stronger proof bar requires evaluating walls, cliffs, water and permissions on **one graph**.

**Common requirements for all five designs**

These are five different ways to maintain that joint graph: full replication, gate factorisation, spatial hierarchy, vanilla-region refinement, and incremental connectivity.

- **Separate meanings.** A pawn can be untrapped yet unable to reach somewhere because of walls. Never feed reach components into `Trapped`, `WideEverywhere`, capture or `RM_PitRooms`.
- **Match the actual path request.** Freeze climb band, stride, floor/deck view, pathing context, swim class, traversal mode and permissions. Gear’s band 0 and the too-narrow exemption select their actual A* connectivity; they must still respect walls.
- **Match edges, not just walkable cells.** Use the path cost grid, connectivity bytes, diagonal restrictions and permission offsets together. `ConnectivitySource` alone admits destroyable walls. Verify whether offsets such as 10000 mean impassable or merely expensive under each mode.
- **Match destinations.** `Touch` is not simply “any cell in an expanded rectangle”; large things, corners and interaction geometry matter. Reuse the pathfinder’s endpoint rules. **UNSURE:** the exact reusable 1.6 endpoint-evaluator symbol.
- **Replace the answer where authoritative.** A postfix that only vetoes cannot repair vanilla’s flying-context false negatives. Use a prefix on the supplied `Reachability.CanReach(...)` overload and `CanReachMapEdge(...)`, returning the indexed answer for supported requests. Preserve `Pawn_PathFollower.StartPath` walker context.
- **Precompute permissions.** A profile represents an exact vector of door/ladder permissions plus traversal semantics—not merely faction. Prepare/intern profiles outside `CanReach`; do not scan all doors during each query. Arbitrary mod predicates can make every pawn a separate profile.
- **Publish snapshots.** Coordinate updates with `PathFinderMapData.GatherData` and the existing `ConnectivitySource.ComputeAll` / `UpdateIncrementally` seams. Never rebuild inside a query or while pit-room region generation is running.

The supplied API names are my basis for the seams below. Ludeon confirms that 1.6 pathfinding is batched and multithreaded; its announcement does not establish internal API signatures. [Official 1.6 announcement](https://store.steampowered.com/news/posts/?appgroupname=RimWorld&appids=294100&enddate=1752076799&feed=steam_community_announcements).

**Cost notation.** \(N=62,500\); six bands × eight views = 48 structural atlases. That is three million cell labels: **12 MB** using `int`, before metadata, extra pathing classes or double buffering. Let \(H\) be distinct permission profiles, \(P\) chamber/portal nodes and \(E\) graph edges. Fence/swim/traversal classes multiply whichever structural data cannot be shared.

A full 48-atlas pass examines roughly **12–24 million neighbour directions**. As an illustrative throughput assumption—not a benchmark—50–250 million edge tests/second implies **48–480 ms**, plus setup and allocation. Benchmark before accepting any millisecond estimate.

All connectivity designs also need an initial symmetry test. If legal movement is directed, ordinary component equality is insufficient: use SCCs plus indexed reachability through their condensation DAG. Dense bitsets cost \(P^2/8\) bytes per profile; the pathological uncompressed 48-map case approaches **23.4 GB**. Do not silently assume the existing undirected labeller proves A* symmetry.

**1. Full joint component atlases per permission profile**

This is the simplest exact reference implementation: build the complete legal cell graph separately for each distinct profile, then label it. Doors and ladders participate according to that profile.

Data: `labels[view, band, pathClass, profile]`, component edge flags, immutable epoch metadata. Keep the existing depth labels separate.

Seams: the common reachability prefixes, `GatherData`, existing connectivity hooks, and existing mod notifications for depth, bridge, ladder, deck, ramp and settings changes. Observe `Building_Door.PawnCanOpen` / `CanPhysicallyPass` semantics when preparing profiles; merely patching those methods does not detect every state change.

```text
Query(request):
    a = committedAtlas[preparedProfile(request), selectedView(request)]
    return any LegalEndpoint(request) has a.label == a.label[start]

PrepareEpoch(changes):
    freeze path-grid, connectivity and permission inputs
    for each affected, currently required atlas:
        flood using exactly LegalCell and LegalEdge
        compute legal-map-edge flags
    publish complete epoch
```

**CPU and memory.** Query: a few array reads, plus endpoint enumeration—effectively O(1) for ordinary targets; cache large target endpoint sets. Full rebuild: \(O(HN)\) per affected view/band. The pessimistic 48-atlas case is 12 MB per \(H\); twenty distinct profiles mean **240 MB of labels**, potentially twice that during publication. Twenty complete rebuild sets could take roughly 1–10 seconds under the illustrative throughput assumption. Build only actually used combinations, but measure how many that really are.

**Latency and realism.** Choose publication at the next compatible path-data epoch, rather than the existing 60-tick throttle. Before publication, blocking changes can produce false yes; opening changes can produce false no. Budgeted rebuilding extends that window and must expose its age. Players otherwise see correct work eligibility, including permission-sensitive routes.

**Simplicity.** Lowest design complexity: “one graph per actual movement policy.” Moderate implementation complexity because extracting that policy is difficult. Few tuning knobs beyond active-profile retention and rebuild scheduling.

**Risk and proof.** Profile explosion and missed invalidation dominate; vanilla regions and saves need not change. Derived atlases should not be saved. Selftest: enumerate door/ladder permission combinations in a small map and compare labels with an independent flood. Live row: the winch scene, then a second cliff-free route behind a faction-locked door; both permission outcomes must equal A*-found.

This is an excellent correctness baseline, but potentially expensive as the production architecture.

**2. Static chambers plus permission-controlled gate graph — recommended**

Factor the graph rather than duplicate the whole map per pawn. Build wall-and-cliff-aware **chambers**, excluding conditionally traversable door cells and ladder transitions. Represent those as explicit gate vertices/edges. Reconstruct all their legal incident transitions, including diagonals where applicable.

A door-cell vertex is important: a pawn may start on it or target it. A ladder edge connects its actual bottom/top cells; “some usable ladder exists in this pocket” is insufficient.

Data: shared `cell → chamber/port` arrays; gate records; adjacency; per-profile connectivity labels over this much smaller graph; edge-sink flags.

```text
Query(request):
    g = committedGraph[selectedStructuralClass(request)]
    p = preparedPermissionProfile(request)
    return any LegalEndpoint maps to a node
           with profileLabels[p][node] == profileLabels[p][startNode]

PrepareEpoch(changes):
    geometry changed:
        rebuild affected structural chamber maps and gate attachments
    permission changed:
        reevaluate affected gate predicates
    for affected profiles:
        label graph using only allowed gates
        include a virtual legal-map-edge sink
    publish
```

Seams are the common ones. Gate predicates mirror `Region.Allows`, `Building_Door.CanPhysicallyPass`, `PawnCanOpen`, `RM_LadderRules.LadderLetsOut` and the drawbridge gate’s rules. They are sampled into a coherent profile; this does not inject a new cache into vanilla’s region-pair cache.

**CPU and memory.** Query remains O(1)-ish. Geometry rebuild has solution 1’s structural cost, without full cell duplication for every permission vector. Permission-only rebuild is \(O(H(P+E))\). Shared labels cost roughly 12 MB per structural-class set; profile labels cost \(4HP\). For illustration, 2,000 graph nodes per atlas gives \(P=96,000\) across 48 atlases: twenty profiles add **7.68 MB**, rather than 240 MB. Gate-heavy mazes can approach the cell graph’s size.

**Latency and realism.** Permission changes can publish at the next epoch without rescanning the whole map. Geometry changes still require structural work. False yes/no during the unpublished window have the same directions as solution 1. Once published, a forbidden ladder behaves as a prison door, and a locked door cannot secretly supply the cliff-free half of an AND.

**Simplicity.** Three central concepts: depth pockets, structural chambers, permission gates. Moderate code; modest tuning. No search budgets or magic reach-distance thresholds are required.

**Risk and proof.** The principal risks are omitted gate transitions, incomplete permission profiles and collapsing a conditional route into a supposedly unconditional chamber. Selftest: two alternative routes, one cut by a cliff and the other by a denied door; then enumerate all door/ladder states. Live row: hostile and friendly pawns querying the same drawbridge gate before/after locking, plus prisoner ladder permission changes. Require equality for every pair.

This closes the reported class and its door analogue while retaining cheap queries.

**3. Fixed spatial tiles with exact portals and a global connectivity index**

Partition the map into, for example, 16×16-cell tiles. Within each tile, compute exact local chambers. Every legal boundary crossing becomes a portal connection; doors and ladders remain permission gates. Maintain profile connectivity labels over the resulting portal/chamber graph.

This is a spatial update architecture: edits rebuild bounded local geometry instead of whole-map chambers.

```text
Query(request):
    s = localNode(start)
    for t in LegalEndpoints:
        if globalProfileLabel[s] == globalProfileLabel[localNode(t)]:
            return true
    return false

PrepareEpoch(changes):
    dirty tiles = dependency footprint(changes), including neighbouring tiles
    rebuild local chambers and exact boundary crossings there
    replace affected portal/gate records
    relabel affected global profile graphs
    publish local maps and global labels together
```

Seams: common reachability/path-data hooks. Feed dirty cells from `ConnectivitySource.UpdateIncrementally` and mod notifications. **Do not assume every feature has a one-cell footprint:** stride-derived depths, deck views and ramp dependencies determine the dirty halo.

**CPU and memory.** Query: two levels of array lookup. Initial build: \(O(48N)\), plus global graph work. A single ordinary edit initially touches about 256 cells per affected atlas, then global relabelling costs \(O(H(P+E))\). A 250² map has 256 partially/full tiles and about **7,500 cardinal boundary crossing pairs** before coalescing; diagonal crossings add more.

Cell-local labels still cost approximately 12 MB. Portal records, adjacency and profile labels add potentially tens of MB. Keeping only tile-local connectivity matrices can become quadratic in portal count; local chamber labels avoid that.

**Latency and realism.** Next-epoch publication is more plausible under frequent construction because local rebuilding is bounded. Global profile rebuilding can still dominate. Players see the same intended answers as solution 2; tile seams must be completely invisible.

**Simplicity.** More code and concepts: local components, portal attachments, global components and transactionally consistent publication. Tile size is a real tuning knob; avoid adding numerous adaptive thresholds initially.

**Risk and proof.** Boundary diagonals, ladder endpoints crossing tiles and nonlocal stride invalidation are the characteristic bugs. Selftest: move the identical moat/wall/door geometry through every offset modulo tile size; answers must remain unchanged. Live row: build/breach exactly on a tile corner, lower a bridge across that corner, and compare all staged pairs after each epoch.

Choose this when measured structural rebuilding—not permissions—is the bottleneck.

**4. Refine vanilla regions into private multi-band reach graphs**

Use vanilla regions as the starting partition. For every relevant view/band/class, split each native region internally wherever the joint movement graph disconnects. Reconnect fragments only through actual legal cell transitions and permission gates.

**Filtering existing `RegionLink`s alone cannot work:** a cliff can disconnect two cells inside one vanilla region.

Keep these graphs private. Do not make native rooms or `RM_PitRooms` consume the refined regions.

```text
Query(request):
    s = privateFragmentAt(start, selectedView)
    return any legal target fragment shares s's profile connectivity label

PrepareEpoch(changes):
    wait until native region rebuilding is complete
    regenerate fragments inside changed native regions
    replace incident fragment links using exact cell-edge legality
    refresh permission-profile connectivity
    publish
```

Seams: common reachability prefixes; `Region.Allows` for inherited policy semantics; connectivity/path-data hooks. A completion hook on `RegionAndRoomUpdater.TryRebuildDirtyRegionsAndRooms` is a candidate, but **UNSURE: exact 1.6 method/signature and safe completion point**. Verify against the target assembly before selecting it.

**CPU and memory.** Query remains indexed O(1)-ish; do not run native/private BFS per candidate. Rebuild cost is proportional to cells in affected native regions plus profile graph relabelling. One small edit may invalidate a large native region, so locality is less predictable than tiles.

The cell-to-fragment maps again approach 12 MB across 48 atlases. Graph metadata costs \(O(P+E)\); managed region-like objects can consume tens or hundreds of MB. Worst case, fragmentation approaches one node per cell. Measure object allocation and GC, not just flood time.

**Latency and realism.** Publication waits for both native region completion and path-data compatibility. Native region backlog may extend staleness beyond one tick; no fixed bound should be promised before observing scheduling. Blocking/opening changes have the usual false-yes/false-no directions.

**Simplicity.** Familiar vanilla terminology, but substantial lifecycle complexity: native region identity, private fragments, gates and multiple views. Little numerical tuning; many integration assumptions.

**Risk and proof.** Highest dependence on native region lifecycle and other region patches. Stale native-region references are dangerous; use epoch-owned mappings. Selftest: split one otherwise connected native region with a cliff, without changing any native region links. Live row: repeat the winch proof while also recording native/private region counts and pit-room identities through wall construction, breach and save/load.

This is defensible for a team already maintaining region machinery, but offers little advantage over solution 2 unless native-region reuse benchmarks well.

**5. Maintain connectivity incrementally using spanning forests and replacement edges**

Maintain the full joint graph as an evolving connectivity certificate, rather than periodically relabelling it from scratch. For each profile, retain a spanning forest, non-tree edges and explicit component labels.

On an insertion, merge components. On removal of a tree edge, find a replacement crossing edge; if none exists, split the component and relabel the affected side. This handles deletions correctly; union-find alone does not.

```text
Query(request):
    return any LegalEndpoint shares explicitComponent[start]

CommitChanges(changes):
    derive every inserted/deleted legal edge
    insert edge:
        if components differ: link forests; relabel smaller component
        else: retain as non-tree edge
    delete edge:
        remove it
        if tree edge:
            cut tree
            search one resulting side for a replacement crossing edge
            if found: link replacement
            else: assign separate component labels
    update component edge flags; publish transaction
```

Seams: common reachability hooks and the exact edge deltas derived at `GatherData`; existing mod notifications identify additional affected edges. An Euler-tour tree or similar structure helps maintain forest partitions, but no suitable vanilla helper is established here. This is custom algorithmic machinery.

**CPU and memory.** Explicit labels keep query cost O(1); the expensive work is charged to edits. Small merges/splits can be cheap. An adversarial deletion or repeated bridge toggle can still scan \(O(N+E)\) per profile. Initialization costs at least solution 1’s flood.

Packed forest, membership and edge metadata might require **24–64 bytes per cell/profile**, or roughly **72–192 MB** across three million atlas cells per profile, before publication copies. Managed objects can be worse. Compression onto solution 2’s chambers is possible, but that becomes a combined architecture.

For directed movement, this forest is insufficient: fall back to rebuilding the SCC/reachability index after directed changes.

**Latency and realism.** Ordinary edge transactions can publish next epoch; large cuts can stall publication. Players should see identical semantics to solution 1. The practical danger is a rare connectivity corruption that persists indefinitely, rather than ordinary one-epoch staleness.

**Simplicity.** Highest algorithmic complexity; few gameplay knobs, but several maintenance/performance thresholds. It is substantially different from a global rebuild, and substantially harder to trust.

**Risk and proof.** Missed deltas, incorrect replacement edges, component edge-flag bookkeeping and transaction rollback. Selftest: thousands of seeded random insertions/deletions, comparing after every transaction against a fresh independent flood. Live row: repeatedly toggle the only bridge, alternately breach/rebuild two wall gaps, and compare indexed results, fresh-flood results and A*-found.

Consider only after profiling proves rebuild-based architectures insufficient.

**All 22 complications**

The common contracts above apply to every column. “Rebuild” below means publish coherently with the corresponding path-data epoch, not rebuild inside `CanReach`.

| Complication | 1: Dense profiles | 2: Chambers/gates | 3: Tiles/portals | 4: Region fragments | 5: Dynamic forest |
|---|---|---|---|---|---|
| **C1 Drawbridge** | Rebuild affected view atlases. | Rebuild changed chamber geometry/attachments. | Rebuild leaf/dependency tiles. | Refragment affected regions. | Insert/delete leaf-derived edges. |
| **C2 Drawbridge gate** | Per-profile gate-cell legality. | Explicit gate predicate includes seat/lock/held-open state. | Same predicate on gate vertex. | Same predicate between fragments. | Gate permission changes edges per profile. |
| **C3 Dig/fill in transit** | Rebuild depth-affected atlases. | Rebuild affected chambers. | Dirty full derived-depth footprint. | Refragment depth-affected regions. | Update all affected cliff edges. All retain the per-step floor/repath backstop. |
| **C4 Doors/faction locks** | Exact permission vectors; no faction-only shortcut. | Per-pawn gate predicates. | Conditional portal/local gates. | Preserve `Region.Allows` semantics through gates. | Per-profile door-edge transactions. |
| **C5 Animal fences** | FenceBlocked structural class. | FenceBlocked chambers. | FenceBlocked local maps. | Fence-sensitive fragmentation. | Separate fence-sensitive graph. |
| **C6 Flyers** | Atlas uses actual Flying context. | Flying chambers bypass cliff gates. | Flying local/portal graph. | Flying fragmentation must use flying passability. | Flying graph edges. All remain never trapped, including owner-defined grounded flyers. |
| **C7 Jump packs** | No speculative jump edge. | Same. | Same. | Same. | Same. Ability planning remains separate; actual landing refreshes context. Pack possession alone is not the free-jumper exemption. |
| **C8 Teleport** | No teleport edge in walking graph. | Same. | Same. | Same. | Same. Teleport/fall resolution remains separate. |
| **C9 Raised ladders** | Rebuild permission-dependent atlases. | Remove/disable actual ladder gate edge. | Update endpoint tiles/gate. | Update fragment attachments/gate. | Delete ladder edge. Permission is boolean, never merely a cost. |
| **C10 Portable ladders** | Carried item adds no edge; deployment rebuilds. | Deployment creates gate. | Deployment updates local graph. | Deployment adds fragment link. | Deployment inserts permitted edge. |
| **C11 Climbing gear** | Switch to prepared unrestricted-cliff atlas. | Select band-0 chambers. | Select band-0 local maps. | Select band-0 fragments. | Select corresponding graph. Walls/water still apply. |
| **C12 Sappers/breachers** | Mode-specific legal building traversal. | Destroyable obstacles become mode-eligible transitions. | Mode-specific tile graphs. | Mode-specific fragments/links. | Mode-specific edge sets. Never blanket-skip cliff/water checks. |
| **C13 Titan strides** | Separate selected stride atlas. | Separate structural chamber view. | Stride-dependent dirty halo. | Separate stride fragments. | Stride-specific edge deltas. |
| **C14 Decks/covers/planks** | Match request’s floor/deck view. | Matching chamber view. | Matching local view and dependencies. | Matching fragment view. | Matching graph; collapse removes relevant edges. |
| **C15 Deep water** | Non-swimmer atlas excludes forbidden crossings. | Swim-class chamber input. | Swim-class local maps. | Swim-sensitive fragmentation. | Swim-specific edge legality. Destination-only checks are insufficient. |
| **C16 Ramps** | Include exact ramp transitions. | Structural ramp connection. | Include across tile boundaries. | Include across fragment boundaries. | Ramp insertion/removal updates edges. |
| **C17 Walls/breaches** | Rebuild affected atlases. | Rebuild structural chambers. | Rebuild dirty tiles. | Wait for native rebuild, then refine. | Delete/insert legal edges; search replacement on cuts. |
| **C18 Gravships** | Bulk terrain/depth invalidation. | Bulk chamber rebuild. | Dirty launch/landing footprint. | Native rebuild plus fragmentation. | Bulk transaction; full rebuild fallback. Under-ship depth remains **UNMEASURED** for all. |
| **C19 Map edge** | Component has legal edge endpoint. | Same graph’s virtual edge sink. | Sink attached to legal boundary portals. | Sink attached to legal boundary fragments. | Maintain component edge counts/flags. |
| **C20 Pawnless** | Prepared structural mode profile; use walker when established. | Structural gate profile otherwise. | Same policy on portals. | Same policy on links. | Same policy in graph selection. Handle pawnless map-edge queries too. |
| **C21 Too wide** | Select actual mask-exempt graph. | Select matching structural graph. | Select matching local maps. | Select matching fragments. | Select matching edge set. Never interpret this as walking through walls. |
| **C22 Batching** | Epoch-tagged atlas publication. | Epoch-tagged geometry and profiles. | Publish local/global maps atomically. | Wait for region and path-data completion. | Commit deltas transactionally at barrier. Never compare mismatched epochs. |

**Latency and residual lies**

None of these can simultaneously promise instantaneous live-world changes and agreement with an older A* snapshot. Raising a bridge can leave an old false yes; lowering it can leave an old false no. A coherent next-epoch answer is preferable to independently “immediate” labels and stale path data. Measure the exact scheduling order; the paused-scene ten-tick observation is not a universal latency bound.

The acceptable residual is a short, instrumented transition window protected by the step floor. Persistent door/cliff false yes is unacceptable. Persistent false no after a breach is also unacceptable. Flyers remaining untrapped does not require promising a walking route that their actual selected path context cannot execute.

Also distinguish **graph reachability** from A* failing because of search/resource limits. Every staged proof still needs equality, but a mismatch caused by a search cutoff must be diagnosed rather than concealed by changing connectivity.

**Proof and comparison**

For every design, run a common pure harness over small maps: enumerate ordered start/endpoint pairs, movement profiles, diagonal corner cases and permission states; compare the index against an independent legal-edge flood. Include the supplied moat geometry, water moat, two ladders, denied door alternative, narrow-pocket exemption and all traversal modes.

The live proof should log: map/path epoch, selected context/view/band, profile identifier, endpoints, CanReach, A*-found and publication age. Advance until the relevant `GatherData` epoch is confirmed; then require **CanReach == A*-found on every staged probe pair**, including reverse direction and map-edge probes. Repeat after each mutation, through save/load, and with feature toggles off/on.

All five use disposable derived caches and a Mod Settings toggle for joint reachability, while respecting every existing feature toggle. Toggling rebuilds the relevant snapshots. Pit-room labels and held/capture results must remain identical across wall-only edits.

Agent-days below include implementation and proof after an API/semantics spike; they are rough estimates.

| Solution | CPU | Latency | Realism | Code simplicity | Design simplicity | Tuning simplicity | Risk | Agent-days |
|---|---|---|---|---|---|---|---|---|
| **1 Dense profiles** | Cheapest query; expensive profile rebuilds | Next epoch or rebuild backlog | Exact prepared profiles | Best | Best | Good | Medium; memory/profile explosion | 4–7 |
| **2 Chambers/gates** | Cheap query; cheap permission updates | Usually next epoch | Exact gate semantics | Good | Good | Good | Medium; gate completeness | 7–12 |
| **3 Tiles/portals** | Cheap query; local geometry updates | Best predictable geometry locality | Exact if boundaries correct | Moderate | Moderate | Tile size matters | Medium–high | 12–20 |
| **4 Region fragments** | Cheap query; native rebuild dependent | Native lifecycle dependent | Exact if refinement complete | Difficult | Moderate | Few knobs | High compatibility/lifecycle | 15–25 |
| **5 Dynamic forest** | Cheap query; variable edit cost | Fast common edits, expensive cuts | Exact if certificates correct | Hardest | Hardest | Maintenance thresholds | Highest algorithmic risk | 20–35 |

**Recommendation and first work**

Ship toward **solution 2**, with solution 1 as the independent reference implementation. It shares expensive cell geometry across pawns while representing the owner’s prison-door permissions explicitly. Retain the winch A* gate during rollout.

First spend an API/profiling spike on three questions:

1. **What graph does A* actually search?** Verify diagonals, symmetry, endpoint rules, destruction modes, hard versus expensive offsets, flying context and narrow-pocket selection.
2. **How large is the factored graph?** Measure chambers, gates, distinct permission vectors and mutation frequency on representative colonies—not just empty maps.
3. **Can publication meet the tick budget?** Measure p50/p95/max rebuild time, allocations, query volume and stale age on the 250², six-band/eight-view case.

That evidence decides whether solution 2 is sufficient or needs solution 3’s spatial updates. Running A* per query, even “bounded,” should remain a diagnostic or narrowly gated caller tool: budget exhaustion cannot safely mean unreachable, and cold failing searches violate the hot-path requirement.