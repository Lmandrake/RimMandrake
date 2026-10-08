# HugeThings rework (HUGE_THINGS_FOOTPRINT_1)

## Milestones
- [x] read code + evidence
- [x] measured draw transform (RimSage) -- see below
- [x] mask tool: src/RimMandrake/HugeThings/measure_huge_plant_masks.py (writes TheRot/Patches/RotGiants_HugeFootprint.xml)
- [x] C# rewritten (Extensions, FootprintMath, CompHugeFootprint, settings labels)
- [x] selftest 14/14 + validation.py STATIC PASS; DLL rebuilt 20:24
- [ ] run_selftests (all) + commit  (C1 committing now)
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
Kernel rule added for the fuzz invariant "blocked never outside the silhouette": a cell blocks only if its centre is inside the drawn picture box; the tool applies the same rule (+0.06-cell jitter margin) so full growth still reproduces the data. Effect: AB_GiantAgarilux now 0 contact cells (its art touches the ground only in its own root cell) -- see Needs owner.

## Needs owner
- AB_GiantAgarilux (vokkun pillar): its stem is ~1.2 cells wide and stands on its own root cell, which can never carry a blocker (the edifice would wipe the plant). Today it blocks nothing. Options: accept a walk-through pillar, or make the def itself PassThroughOnly/Impassable (a def change in TheRot, not HugeThings).

Note: run_selftests 303/304 before this step; the 1 FAIL is src/RimMandrake/bridgetools/selftest_tool_metadata.py (JawaBench DLL lacks kill_hostiles/world_tile_cache_reset from ac8b24b82) -- not HugeThings.

## GPT review + owner ruling #4 (20:38) -- plan
- C1 geometry unit: kernel + tool + data + fuzz with an INDEPENDENT double-precision forward oracle (drawSize != 1, boundary crossings), mutation set, lint. Strict growth nesting DROPPED as an invariant (GPT; also measured: halving growth is not a subset in ~63% of random masks).
- C2 game side: pure ClaimLedger (multi-owner claims, one blocker per cell, permutation-invariant) + pure TransactionPlanner (defer cells with items/pawns/protected interaction cells/door approaches; never enclose a pawn, cut off root access, or create a pocket) in the kernel and fuzzed; MapComponent map-wide blocker index + reconcile on load; staggered refresh, signature skip; dirty on growth/harvest/graphic; zones untouched; full cache signature; Rand restored in finally; union existing rect; opt-in renderer validation; mouse-candidate dedup.
- C3 cover + damage: owner ruled partial cover, shots damage the plant, dedup per explosion/projectile; gravship landing removes plants whose blockers it intersects.
