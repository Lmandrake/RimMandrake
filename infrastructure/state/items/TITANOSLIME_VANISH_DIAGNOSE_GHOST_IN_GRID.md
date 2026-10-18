# TITANOSLIME_VANISH_DIAGNOSE_GHOST_IN_GRID — a vanished titanoslime stays in the cell grid

## what is wrong (MEASURED 2026-10-17, BENCH, 22-mod walk list + neku.largepawns + mandrake.rm.hugethings, quicktest map)

`Destroy(DestroyMode.Vanish)` on a living `RM_Titanoslime` (`jawa/pawn_force_incapacitate action=vanish`, which calls
exactly that) leaves something behind in the cells around where it stood:

- any later `jawa/spawn_pawn` in the 3x3 around it fails with an NRE in
  `Verse.PawnCollisionTweenerUtility.GetPawnsStandingAtOrAboutToStandAt` (a Muffalo too, not just slimes);
- `Root level exception in Update()` (draw: `DynamicDrawManager.ComputeCulledThings` -> `Pawn_DrawTracker.DrawPos` ->
  `PawnCollisionPosOffsetFor`) and `in OnGUI()` then throw every frame, and because the draw pass dies mid-way every later
  spawn/despawn logs "Cannot register drawable X while drawing is in progress" (1,200+ `AB_MycoticSpores` lines in one run).
  `Exception in BreadthFirstTraverse` from `ReachabilityWithinRegion.ThingFromRegionListerReachable` also appears: the
  destroyed pawn is still in region listers.

Repro matrix, 9 neighbour cells respawned with a Muffalo after the end action (2026-10-17):

| subject | end | respawn ok |
|---|---|---|
| titanoslime stage 1, no mass change | vanish | 1/9 |
| titanoslime stage 1 (mass re-set) | vanish | 0/9 |
| titanoslime stage 2 / 3 | vanish | 4/9, 4/9 |
| titanoslime stage 4 (mass 28) | vanish | 9/9 |
| titanoslime stage 1 / stage 4 | **kill** | 9/9, 9/9 |
| titanoslime stage 1, alive | none | 9/9 |
| Thrumbo, Elephant, Muffalo, RM_Gelatid | vanish | 9/9 each |

So it is titanoslime-specific and vanish-specific. No exception is logged at the destroy itself.

## mechanism (code read 2026-10-17, BENCH offline; confirmed live by gate g8 2026-10-17)

Decompiled with ilspycmd: Large Pawns 0.24.16 (`LargePawns.dll`) and the 1.6 `Assembly-CSharp.dll`.

1. `Thing.SpawnSetup` calls `map.thingGrid.Register(this)` and `RegionListersUpdater.RegisterInRegions` BEFORE
   `ThingWithComps.SpawnSetup` runs the comps' `PostSpawnSetup`. So the titanoslime is registered at the
   **PawnGenerator's random-age life stage** (lifeExpectancy 1000, minAges 0/100/200/300/400: any of the five).
2. Large Pawns' `ThingGrid_Register_SquarePatch` adds the pawn to EVERY cell of `OccupiedSquare(pawn)`, sized by
   `GetSize` from the live BodySize; `ThingGrid_Deregister_SquarePatch` removes it from the square sized by
   `GetSizeForDeregister` — also the live BodySize. **Nothing remembers the square it registered.** Same shape for
   region listers. Squares are nested (`GenAdj.OccupiedRect` sizes 2⊂3⊂4), so growth is safe and **shrinking is not**.
3. `RM_CompEngulfer.PostSpawnSetup` -> `ApplyStage` -> `LockCurrentLifeStageIndex` then changes BodySize while the
   pawn is registered. Footprints: stage 1 BodySize 6 -> 2x2, stages 2-3 (10/16) -> 3x3, stages 4-5 (24/40) -> 4x4.
   A lock to a smaller square than the rolled one leaves the outer ring in `thingGrid` (and region listers) forever;
   every later move deregisters only the current square too.
4. Vanish vs kill: both leave the ring. `PawnCollisionTweenerUtility.GetPawnsStandingAtOrAboutToStandAt` skips any
   pawn whose `GetPosture() != Standing` — a dead ghost is skipped. A vanished ghost is not dead, is "Standing", and
   `Pawn.DeSpawn` -> `PawnComponentsUtility.RemoveComponentsOnDespawned` set its `pather = null` -> NRE on
   `pawn.pather.MovingNow`, every frame via the draw path. (A dead ghost is still a leak; it just does not throw there.)

The repro table fits exactly: stage 1 (2x2, the smallest square) is ghosted by almost any roll (0-1/9); stages 2/3 (3x3)
only by a stage-4/5 roll (4/9); stage 4 (4x4, the ceiling) can never shrink (9/9); other large animals never change
size while spawned (9/9).

## false theories (kept, they were reasonable)

- **"Huge Things holds the ghost."** Its titan tier / wake / footprint code touches no cell grid for pawns
  (`CompHugeFootprint` is the plant claims grid; the wake only reads `Position`). Not it.
- **"A cached occupied rect in our mod."** `RM_CompEngulfer` keeps no rect and patches nothing; the ghost lives in
  Large Pawns' unrecorded registration.
- **"Vanish deregisters differently from kill."** Both go through `Pawn.DeSpawn` -> `Thing.DeSpawn` ->
  `thingGrid.Deregister`; the difference is only what a ghost of each kind does to its readers.
- The NEXT this item first carried (restart without `neku.largepawns`) would have pointed at Large Pawns, but the
  fix belongs to the mod that changes size under a registered pawn: ours.

## fix (built 2026-10-17; deployed and VERIFIED live 2026-10-17, gate g8)

`RM_CompEngulfer.LockStageReregistering` (`src/RimMandrake/GelatinousSlime/Source/Titanoslime.cs`): every stage lock
while spawned is wrapped in `DeregisterInRegions` + `thingGrid.Deregister` (at the OLD size) ... `thingGrid.Register` +
`RegisterInRegions` (at the NEW size) — the `Thing.Position` setter's own move pattern. Without Large Pawns it is a
one-cell deregister/register. `ApplyStage` now also locks when the index already matches but is unlocked (a
same-stage roll used to stay unlocked and keep ageing). Proof surface: `RM_TitanoslimeProof.ProofGhostScan`
(whole-map thingGrid scan for destroyed/unspawned/out-of-square pawns).

## live result (2026-10-17, BENCH, 22-mod list incl. neku.largepawns + mandrake.rm.hugethings, quicktest map)

`mandrake.rm.biomes` composed and deployed (GelatinousSlime DLL + .srchash), game relaunched via Steam.
`titanoslime_gates.py --only g8`: 6/6 PASS (3x stage 1, stage 2, stage 3, shrink 4->1): ghosts=0 before and after
vanish, Muffalo respawn 9/9 every case (0-4/9 before the fix), log budget +0 exceptions. Gates 1-6 + g8 with the
script's cleanup switched back to VANISH: 33/33 rows PASS (`Transient/afk_2026-10-17/titanoslime_g8_final_run.log`).

Harness defects found on the way (both HARNESS, fixed in the script): g3's absorb arm never removed its three slimes,
which stayed manhunter and logged 100+ "Resolved path returned no nodes ... for RM_Titanoslime" into every later
gate's log budget; g3's mass bar assumed an adult victim (1.0) but a random Colonist is sometimes a
HumanlikeTeenager, BodySize 0.8 (4 of 11 runs). The mod gains the victim's BodySize, correctly.

## NEXT

None — closed. TITANOSLIME_SLIME_BIOME_1's gates 1-6 still PASS after the fix; its gate 7 (art) awaits the owner.
