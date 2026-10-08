# HugeThings rework (HUGE_THINGS_FOOTPRINT_1)

## Milestones
- [x] read code + evidence
- [x] measured draw transform (RimSage) -- see below
- [x] mask tool: src/RimMandrake/HugeThings/measure_huge_plant_masks.py (writes TheRot/Patches/RotGiants_HugeFootprint.xml)
- [x] C# rewritten (Extensions, FootprintMath, CompHugeFootprint, settings labels)
- [x] selftest 14/14 + validation.py STATIC PASS; DLL rebuilt 20:24
- [x] C1 pushed 61076dfdd (also pushed the stuck BENCH ledger commit 2a9e6152d)
- [x] build 20:21 (winbuild OK, srchash matches)
- [ ] commit

## Measured draw transform (decompiled 1.6)
Plant.Print (RimWorld/Plant.cs 950-1067), maxMeshCount==1:
- Rand.Seed = Position.GetHashCode(); center = TrueCenter = Position.ToVector3Shifted (GenThing.TrueCenter, 1x1)
- center += Gen.RandomHorizontalVector(0.05)  (2x Rand.Range)
- num2 = visualSizeRange.LerpThroughRange(growth); quad side = graphicData.drawSize.x * num2 (SQUARE, drawSize.y ignored)
- if center.z - num2/2 < Position.z: center.z = Position.z + num2/2  => bottom-anchored on root cell's south edge (z jitter erased)
- flipUv = Rand.Bool (horizontal mirror); Graphic_Random variant = Rand.Range(0, SubGraphicsCount)
- Graphic_Collection.Init orders sub-textures by name.
- Plant.Graphic: leaflessImmature / leafless / immature graphic overrides (RM_PaleTree has immatureGraphicPath TreeAnima_Immature).
- Root cell must stay free: GenSpawn.SpawningWipes -> an impassable edifice BlocksPlanting() and would wipe the plant.
- Printer_Plane.PrintPlane: flipUv uses DefaultUvsFlipped = x mirror. Graphic_Random.MatSingleFor uses thingIDNumber (no Rand), so the Rand sequence in Print is: RandomHorizontalVector (2 draws), Bool, Range(0,count) -- replicated at runtime.

## Measured contact cells (BASE_ROWS 0.10, BAND_DEPTH 0.5, CELL_COVER 0.25, cutoff alpha 0.5)
AgariluxPrime 118 | DribblingCap_A 28 | Nogtyl A/B/C 17/13/12 | Arpeau A/B 4/3 | ArbuscularMycorrhiza_A 16 | AgaricusDomeCap 11 | GiantAgarilux_A 2 | WitchesOyster 9 | PaleTree_A 3

## Coordinator addition (20:40): pure kernel + seeded fuzz + mutation set + def lint
- [x] Source/Kernel/RM_HugeFootprintKernel.cs (Verse-free); FootprintMath = Verse adapter
- [x] Source/SelfTest fuzz (net8.0) + Utils/selftest_hugethings_fuzz.py
- [x] Utils/mutations_hugethings_fuzz.json + mutate_hugethings_fuzz.py
- [x] Utils/selftest_hugethings_lint.py (4/4)

### Fuzz + mutation results (C1)
`python3 src/RimMandrake/Utils/selftest_hugethings_fuzz.py`: any 20000, full 5000, boundary 5000, symmetry 3000, determinism 500 -> ALL PASS.
`any` compares the compiled C# kernel against an independent double-precision FORWARD oracle written from Plant.Print (drawSize 0.5..2 included), excluding only cells within 2e-3 of an edge.
`python3 src/RimMandrake/Utils/mutate_hugethings_fuzz.py`: 13/13 CAUGHT (flip axis x2, anchoring removed, anchoring by side, root exemption, picture clip, selection-root, picture last column, row rounding, column ceil, scale anchor, jitter ignored, V0 ignored).
Dropped as equivalent: "selection forgets blocked cells" (blocked cells are clipped to the picture, which the selection already holds).
Growth nesting is NOT asserted (GPT #10); the first fuzz measured 13326/21000 random masks where half growth is not a subset of full.
Kernel rule added for the fuzz invariant "blocked never outside the silhouette": a cell blocks only if its centre is inside the drawn picture box; the tool applies the same rule (+0.06-cell jitter margin) so full growth still reproduces the data. Effect: AB_GiantAgarilux now 0 contact cells (its art touches the ground only in its own root cell); owner ruling 21:08 makes such a plant impassable on its own cell (below).

## GPT review + owner ruling #4 (20:38) -- plan
- C1 geometry unit: kernel + tool + data + fuzz with an INDEPENDENT double-precision forward oracle (drawSize != 1, boundary crossings), mutation set, lint. Strict growth nesting DROPPED as an invariant (GPT; also measured: halving growth is not a subset in ~63% of random masks).
- C2 game side: pure ClaimLedger (multi-owner claims, one blocker per cell, permutation-invariant) + pure TransactionPlanner (defer cells with items/pawns/protected interaction cells/door approaches; never enclose a pawn, cut off root access, or create a pocket) in the kernel and fuzzed; MapComponent map-wide blocker index + reconcile on load; staggered refresh, signature skip; dirty on growth/harvest/graphic; zones untouched; full cache signature; Rand restored in finally; union existing rect; opt-in renderer validation; mouse-candidate dedup.
- C3 cover + damage: owner ruled partial cover, shots damage the plant, dedup per explosion/projectile; gravship landing removes plants whose blockers it intersects.

## Collision note
origin had 3544bb42e (an L0 validation builder's HugeThings kernel/lint pinning the OLD trunk-rect design, same file names).
61076dfdd replaces it: their RM_FootprintKernel.cs and Utils/lint_hugethings_defs.py removed, their pawn-hitbox extraction
ported into RM_HugeFootprintKernel.PawnHitbox. Please keep L0 builders off HugeThings until this rework lands.

## Engine facts verified for C2/C3 (RimSage, decompiled 1.6)
- Thing.SpawnSetup -> !def.CanOverlapZones -> ZoneManager.Notify_NoZoneOverlapThingSpawned removes the cells and CheckContiguous (GPT #3 confirmed).
- StoreUtility.NoStorageBlockersIn refuses a cell holding a non-item thing with passability != Standable: stockpiles never store into a blocker cell even if the zone keeps it. Sowing: PlantUtility checks BlocksPlanting.
- GenUI.ThingsUnderMouse: cell things exclude only `list` (close pawns), so a plant at its root cell enters twice (cell + custom rect) (GPT #12 confirmed).
- Projectile.CheckForFreeIntercept: non-pawn things with fillPercent > 0.2 intercept with fillPercent*0.15 per cell en route, fillPercent*1 when adjacent to the destination; CanHit needs NonTargetWorld, not isTargetable. Impact -> TakeDamage once per projectile.
- Thing.TakeDamage -> PreApplyDamage(ref dinfo, out absorbed): absorbing there stops all damage to the cell.
- DamageWorker.ExplosionDamageThing keeps a per-explosion damagedThings list (DamageWorker_Vaporize overrides and calls base).
- GravshipPlacementUtility.ClearArea(map, root, clearCells, mode) clears cell by cell (ClearThingsAt).

## C2+C3 done (game side, cover/damage)
- Kernel/RM_HugeClaimsKernel.cs (Verse-free, fuzzed): ClaimLedger (#8), Planner (#1 #2 #6), FootprintSignature + SignatureCache (#16), DamageDedup (#4 ruling).
- MapComponent_HugeFootprints rewritten: map-wide blocker index + Reconcile on load (#5), staggered RefreshesPerTick=8 of changed plants only, pending retry every 250 ticks (#9), settings -> mark dirty (no synchronous flush).
- CompHugeFootprint: desired cells + selection from a full signature (#16), Rand restored in finally (#16), dirty on CompTickLong signature change and PlantCollected postfix (#14), MaxKeys from the real transform for the fixed planning window (#7).
- HugeThingsCore: union instead of overwrite (#16); ThingsUnderMouse dedup (#12); ZoneManager.Notify_NoZoneOverlapThingSpawned skipped for blockers (#3); renderer validation at opt-in: maxMeshCount 1, Plant.Print not overridden, drawSize.x 1, measuredSize == drawSize.x*visualMax, else selection only + one error (#7 #11); gravship ClearArea prefix removes giants whose blocker/root a landing clears (#15); ExplosionDamageThing prefix reroutes trunk cells to the plant via the blast's damagedThings (#4 ruling).
- Building_TrunkBlocker: PreApplyDamage absorbs and forwards to the primary owner once per (tick, instigator+weapon+damageDef, owner); DeSpawn notifies the map component; TickRare removes any blocker the component does not own.
- fillPercent 0.75 -> 0.4 (#4 ruling; reasoning in the def comment; lint pins 0 < fill < 1, holdsRoof false (#17)).
- Settings: scales clamped to [0.5, 1.5] and NaN-guarded on load.
- #13 (drag select / designators / float menus): not changed. Selection is the click contract only; no designator semantics were altered.

### Fuzz + mutations (C2)
Fuzz: any 20000, full 5000, boundary 5000, symmetry 3000, ledger 4000, planner 3000, cache 2000, damage 2000, determinism 500 -> ALL PASS.
Mutations: 22 total, ALL CAUGHT (13 geometry + 9 claims: overlap freeing, item cell, pocket, root access, single pass, cache scale, cache root, dedup reset, dedup owner).
Dropped as equivalent: "primary owner = max id" (still order-independent).
Found by the fuzz and fixed: the planner judged reachability in a window that shrank as cells closed and ran one greedy pass -> a second pass closed cells the first refused (134/3000). Now a fixed per-plant window (full-growth, max-setting footprint + 4) and a fixpoint loop.

## Needs owner
- Union fallback: an unmeasured picture (RM_PaleTree's immature graphic is vanilla TreeAnima_Immature) blocks the union of the measured variants, scaled; the selection is the whole quad.
- Planner cost at load: ~O(window cells x pending cells x passes) per giant (worst measured shape 118 cells, ~28x28 window); unbenchmarked in game.

## Status (C2 pushed ebf7b5d28)
run_selftests: 326/327; the one FAIL is bridgetools/selftest_tool_metadata.py (JawaBench DLL vs source, from ac8b24b82), not HugeThings.
All HugeThings C# files are DIRTY under code_review_status (no full-file review yet).
BENCH to see it live: python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod HugeThings (then --apply) and --mod for the Rot patch's mod (mandrake.rm.biomes / TheRot folder), with the game closed (DLL locked while running); cold load; on an existing save Reconcile re-takes every footprint on load.

## Owner rulings 21:08 (decision taken by question card) -- implemented
1. Root-only giants are solid on their own cell. Generic rule RootRule.RootImpassable (kernel): blocking on, renderer supported, and EVERY measured variant has 0 non-root contact cells -> the plant def's passability is set Impassable at startup (HugeThingsApi.ValidateRenderer). Today that is AB_GiantAgarilux only (pinned). Verified 1.6: PathGrid.CalculatedCostAt blocks for any thing whose def is Impassable; WorkGiver_PlantsCut and WorkGiver_GrowerHarvest use PathEndMode.Touch, JobDriver_PlantWork goes to Touch, and TouchPathEndModeUtility.AddAllowedAdjacentRegions reaches a 1x1 target from any allowed adjacent cell; GenSpawn.SpawningWipes returns false for a Plant. The planner already keeps every giant's root with an open reachable 4-neighbour. Takes effect after a restart if the footprint setting is toggled.
2. Large enclosures: ACCEPTED as a known limitation. The planner guarantees no new enclosure inside each giant's window (its full-growth, max-setting footprint + 4 cells). A chain of giants that together seal a region larger than any single window is not detected.
3. Items under a closing footprint are pushed, gently (ItemMover in the kernel; MapComponent.PlanItemMoves/MoveItems): a cell held only by items (no pawn, nothing protected) closes after ALL its items fit in the nearest free valid cells (BFS <= 12 cells over standable ground, capacity GetMaxItemsAllowedInCell - GetItemCount, shared across the pass), never in any claimed footprint cell, preferring the source's own storage (same SlotGroup). The same Thing is despawned and respawned (forbidden state, stack, quality kept); an item that cannot be placed goes back. At most once per 250 ticks per cell; no letters or messages. Otherwise the cell stays open. Pawns are never moved. New guard: a blocker never spawns over an item or pawn (an impassable spawn WIPES items, GenSpawn.SpawningWipes).
Fuzz: + items 4000 (half crowded) and root 2000 -> ALL PASS (any, full, boundary, symmetry, ledger, planner, items, root, cache, damage, determinism). Mutations: 26, all caught (+ item lands in footprint, capacity not shared, partial move, root rule any-vs-every).
