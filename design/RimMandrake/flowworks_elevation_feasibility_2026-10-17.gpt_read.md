**I would keep 0.5 m steps, support 8 m digging first, and reserve 125 m for natural beds or an advanced setting.** The requested square is feasible without a z-level engine. Making it reliable is substantially more work than increasing `MaxDepth`: my estimate is **5–9 agent-days for dry terrain**, or **13–24 including the proposed water model and basic revegetation**.

1. **All three depth limits fit the storage; these are the risks, ranked.**

   **Movement correctness comes first.** RimWorld 1.6 has multithreaded, batched pathfinding. A per-request mask swap needs proof that the scheduled job retains the correct array, that another request cannot replace its input, and that rebuilding cannot modify arrays still being read. Compiling successfully proves none of those. [Ludeon’s 1.6 announcement](https://ludeon.com/blog/2025/06/announcing-odyssey-and-update-1-6/).

   Test mixed-K simultaneous requests, diagonals, Touch destinations, actorless reachability, ladder permissions, already-issued paths, and depth changes under moving pawns. A 60-tick rebuild delay also needs immediate edge validation or another explicit invalidation mechanism.

   Two architecture corrections are essential:

   - Build grids for **supported climbing capabilities**, currently K=1..5, rather than every depth index. At 125 m, the current formula creates 249 bands instead of three: **83× as many band passes**. On a 300×300 map, four-byte component labels plus byte connectivity masks alone would occupy approximately **112 MB**, versus **2.25 MB for five bands**, excluding scratch space.
   - “K ≥ MaxDepth needs no grid” is unsafe when `MaxDepth` means the digging cap but drained natural beds exceed it. Use the actual supported elevation range or always use the relevant capability grid.

   **Water topology is second.** Histogram inversion is straightforward; correctly merging, splitting and spilling basins is harder. Adjacent floors separated by a dry saddle must not equalize prematurely. Arbitrary conserved volumes require fractional-notch surfaces: integer `fillGrid` cannot remain authoritative while guaranteeing exact levelness. Use body volume and surface as authority, with derived cell depths. Use **64-bit decilitres**: a 300×300×125 m reservoir holds **112.5 billion dL**, assuming 1 m² cells.

   **Depth authority is third.** The workgiver, designator and job driver must read grids. Adding 16, 40 or 250 terrain variants merely preserves the coupling. Keep substrate, depth and water state separate; retain old terrain definitions for loading existing saves.

   **Regions and rooms are fourth.** Your pockets do not automatically become vanilla rooms. Vanilla room assembly groups districts by region type; it has no knowledge of your depth grid. Bed ownership, room statistics and temperature therefore need explicit integration. Also, “vanilla reachable AND same pocket” is only a necessary condition: the two graphs can permit different routes without sharing any valid route. Permission-sensitive ladders further complicate a single undirected component grid. [Room updater source](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/RegionAndRoomUpdater.cs).

   **Rendering and environmental consistency follow.** Existing face arrays fail beyond four-notch drops; clamped pawn sinking makes deeper floors visually indistinguishable. Roofs remain per-cell roof definitions without physical ceiling heights. Your mesh creates no automatic cliff shadows, lowered light sources, LOS obstruction or cover. Those require separate rules. [Roof grid](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/RoofGrid.cs), [glow grid](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/GlowGrid.cs).

   **Plants require deliberate substrate rules.** Normal revegetation needs fertile terrain and eligible biome plants, light, temperature and roof conditions. `WildPlantSpawner` schedules regrowth; waiting does not create soil. Inspected code also allows fertility-ignoring plants, so zero fertility is not universally sufficient. Terrain changes perform fertility/tag-based plant cleanup; changing only your water grid bypasses that cleanup. Explicitly handle flooding and aquatic exceptions. [Fertility](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/FertilityGrid.cs), [spawner](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/WildPlantSpawner.cs), [terrain transitions](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/TerrainGrid.cs).

   **Save size is minor.** Five byte grids on 300×300 consume **450 kB raw** regardless of depth cap; incompressible data becomes roughly **600 kB base64**, plus framing. Compression depends on spatial variation. Rebuild path caches instead of saving them.

   Confidence boundary: the supplied architecture and official 1.6 threading change are firm; public decompiled sources support the subsystem observations but are not verified against your exact installed assembly. Harmony compatibility, job lifetime and live performance remain unproven.

2. **Choose simulation precision, digging limit and artwork independently.**

   Keep **0.5 m digging steps**. They already distinguish small-animal, human and large-animal traversal. One-metre steps lose useful distinctions; 0.25 m doubles orders and states without clear benefit for storage or containment. Human K=2 already permits a 1 m instantaneous step: this is an abstract climbing rule, not ordinary walking.

   Set **8 m default digging, 20 m advanced maximum**. At speed 1, one cell costs approximately **7.25 / 43.73 / 1,673.33 continuous workdays** to reach 8 / 20 / 125 m. Under the current curve, 125 m digging is practically inaccessible.

   Use **six dry visual classes**, such as shallow, knee, waist, person-deep, deep and abyssal. Use **four water classes**: film, shallow, wading and deep. Show exact numbers through inspection/overlays. Draw boundary faces from relative drops, with compressed apparent height beyond approximately 2 m. A 1.7 m person supplies a useful nearby scale; the oblique camera cannot legibly depict a literal 20–125 m shaft inside one tile.

3. **My natural complexity tiers are below.** Estimates are incremental, include coding/selftests, exclude live-game time, and assume the reported built features are reusable.

| Tier | Added agent-days | Risk | Save impact |
|---|---:|---|---|
| Reliable dry relief to 8 m: grid authority, five capability bands, connector/invalidation audit, generalized faces | **5–9** | High until live proof | Keep byte grids and legacy defs; rebuild caches |
| Level-water basins plus basic vegetation/flood transitions | **8–15** | High: topology and conservation | Versioned body data; migrate old fill volumes |
| Digging to 20 m, clearer overlays, permissions and gameplay polish | **3–6** | Medium | Same depth encoding; preserve depths when settings decrease |
| Player digging to 125 m, scale/overflow/performance audit and balance | **3–7** | Medium–high | Same bytes; audit arithmetic and new records |
| Stacked occupancy, tunnels beneath floors, bridges over occupied pits, physical vertical combat | **60–150+** | Very high; low-confidence estimate | Major new spatial/save model |

   The major boundary is **multiple usable spaces at one horizontal coordinate**, not 8 versus 20 m. Numeric 125 m support is relatively cheap after refactoring; convincing physical presentation is not included.

4. **The 4/7/7/4 square works as a two-tier basin.**

   Its twelve ring cells are D=8; four central cells are D=14:

   `12 × 115,200 + 4 × 336,000 = 2,726,400 work`

   That is **45.44 continuous workdays** at speed 1, with **152 notch-completion jobs**. Travel, sleep and access construction increase elapsed time.

   Surface-to-ring is an eight-notch step; ring-to-centre is six. Neither is passable even at K=5. Flat movement within each terrace remains allowed. The symmetric absolute-difference rule forbids jumping down as well as climbing out.

   Existing ramps span three notches. Crossing 4 m needs at least **three ramp transitions with intermediate landing depths**; crossing another 3 m needs **two**. The one-cell-wide ring provides insufficient radial space while preserving the exact requested depths. Ladder-enabled crossings at both boundaries can work; confirm whether one ring-cell installation can represent both links or requires different locations. A local-edge ladder cannot simply skip the ring.

   Assuming 1 m² cells, water first fills the centre: **12 m³** raises it from −7 to −4 m. It then spreads across the ring; another **64 m³** reaches ground level. Total capacity is **76 m³**, or **760,000 dL**, before overflow.

   Render 4 m outer faces and 3 m inner faces with compressed projection and depth labels. Current sink clamping alone will not communicate the difference. The centre cannot coexist with a walkable surface directly above it under this architecture.

5. **The strongest gameplay comes from access and changing water levels.**

   Terraced reservoirs, drainage reclamation, controlled prison access and flood-sensitive maintenance offer useful decisions. Regrowth can make abandoned drained beds feel alive if fertile sediment is retained or added.

   The largest degeneracy already exists near **1.5 m**: ordinary humans cannot cross that step unaided. Extra depth adds storage and expense, not proportionate containment. Unrestricted ramps defeat containment; privileged ladders become extremely powerful prison doors.

   The absolute D≥4 shooting rule also becomes conspicuous: two pawns far apart on the same flat depressed terrace cannot exchange fire. Revisit it explicitly alongside relative movement.

   Storage is finite and increasingly expensive under quadratic work, but deep natural hollows provide enormous inexpensive capacity. Pump throughput, access and spill management may matter more than excavation cost. Flat-cost ramps can likewise become universal shortcuts. Raiders need live tests for inaccessible targets and repeated failed jobs; valid pathfinding alone does not teach them to understand or attack a terraced defence.