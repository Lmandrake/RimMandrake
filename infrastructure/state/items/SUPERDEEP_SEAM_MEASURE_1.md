# SUPERDEEP_SEAM_MEASURE_1 — Measure the engine seams the pit collapse needs (Desktop, RimSage)

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
Desktop only (RimSage). Read, do not build. Record each answer with the decompiled member cited, in a `## measured` section here.
1. `Verse.AI.PathFinder.FindPath` / `Pawn_PathFollower.TryEnterNextPathCell` / `CostToMoveIntoCell`: is the cell being LEFT available when a move is costed or taken? (Decides where the D=4 exit veto and the descent-into-cell event live.)
2. `Reachability.CanReach` + `ReachabilityCache`: does the cache key include the start cell, so a per-start veto ("standing on D=4, cannot reach D<4") is cacheable?
3. `RegionMaker` / `RegionAndRoomUpdater` / `District` / `Room`: do regions ever split on `TerrainDef`, or only on edifices/`Fillage`? (Decides whether an enclosed D=4 area can be a room without a Harmony patch on region building.)
4. `Building_Door.PawnCanOpen` and the prisoner-escape path: the shape to copy for "openable from outside, never from inside".
5. Unroofed-room temperature: how vanilla equalises an unroofed room with outdoor temperature, and where a stronger coupling multiplier would attach.
6. The beggar-rejection thought(s) and which traits/precepts null them — the structure "Exposed Prisoner" must copy.
7. `legator.prisonerrealism` (Prisoner Realism): how it judges adequate confinement.

## verify
Each of the 7 answers cites a type and member from the decompiled 1.6 source. "UNMEASURED" is an allowed answer only with the reason.

## criteria
The holder-retire, prison-room and temperature items can each name their patch point without guessing.

## depends
Nothing. First in line.

## northstar
None — this is measurement. Its answers become `## anti-guessing notes` lines in the FlowWorks walk.

## measured
2026-10-02, FOUNDRY helper. Decompiled 1.6 via RimSage; our source at HEAD `6cfcf530d`; live read-back = validation_v2 run `validation_v2_result_20261002T093135.json` (row `S1p_holder_at_D4_only` PASS: D=4 cell has a holder with 0 occupants, D=3 cell has none) and the before-run of this pass.

**0. How a D=4 cell is represented today, and who holds a pawn.**
- The cell: `RM_MapComponent_Excavation.depthGrid` (byte per `CellIndices`, scribed `RM_excavationDepthGrid`) = 4 (`RM_ExcavationDepth.Superdeep`), base terrain `RM_Channel_Superdeep` (dry) set by `Deepen`. Capture/shooting read `IsSuperdeepExcavation(c)` = grid byte >= 4 (never `DepthAt`, which reports natural liquid as 4). `superdeepCellCount` is kept incrementally.
- The holder: `RM_SuperdeepCapture.EnsureHolder` spawns one `RM_SuperdeepPit` (`Building_SuperdeepPit : Building_OpenPit`, faction = player, `DepthTier = Chasm`) per D=4 cell. Callers: `Deepen` (l.405), `FillIn` -> `RemoveHolder` (l.482), `FinalizeInit` -> `SyncMap` (l.259), `MapComponentTick` toggle watcher -> `SyncMap` (l.761). It holds a pawn by `Building_OpenPit.Spring`: fall damage, `RM_PinnedInPit`, **DeSpawn into `innerContainer`**, struggle clock (`PitEscapeUtility`) gated by `EscapeBlocked` = ladder setting && no `RM_Ladder` in cell.
- Readers of the holder: `Designator_FillInCanal.CanDesignateCell` (`HolderAt(..).Sprung` refusal, l.83); bridge tool `jawa/flowworks_pit_report` (`HolderAt` + `innerContainer` + `EscapeBlocked/Assisted` by reflection); `validation_v2.py` O1 (`RM_SuperdeepPit drawerType None`) and S1p; `RimMandrakeFlowWorks_DefOf.RM_SuperdeepPit`. `RM_Patch_SuperdeepShooting` reads only the grid (unaffected).
- Replacement: the grid alone. `held(pawn)` = setting on && D(pos)==4 && faction captured && W×W square of D=4 cells contains pos (W = max(1, round(sqrt(BodySize)))) && no ladder in pos.

**1. Exit-veto seam.** `Verse.AI.Pawn_PathFollower.TryEnterNextPathCell()` (private, Pawn_PathFollower.cs l.586-685): on entry `pawn.Position` is still the cell being LEFT and the private field `nextCell` is the target; it then does `lastCell = pawn.Position; pawn.Position = nextCell`. So both cells are available at the one place every walked step is committed -> a Harmony **prefix** there is the hard per-move floor (and descent detection can compare old/new D). `CostToMoveIntoCell(Pawn, IntVec3)` (l.746) has the leaving cell only implicitly as `pawn.Position` (used for diagonal cost); it only prices, it cannot refuse. PathFinder is not needed.
**2. Reachability cache.** `Verse.Reachability.CanReach(IntVec3 start, LocalTargetInfo dest, PathEndMode, TraverseParms)` (l.102) is the funnel every overload calls; its cache (`GetCachedResult(traverseParams)`) is keyed on start/dest REGIONS, not the start cell, so a per-start-cell veto cannot live inside the cache — it must be a **postfix on that public overload** (outside the cache, only narrows true->false). `CanReachMapEdge(IntVec3, TraverseParms)` (l.455) is a separate region BFS and needs the same postfix.
**3. Regions on terrain.** `RegionTypeUtility.GetExpectedRegionType` (l.17): door -> Portal, fence -> Fence, `WalkableByNormal` -> Normal, else Fillage Full -> None. Terrain only matters via walkability; a walkable D=4 cell is the same region type as its lip, so **an enclosed D=4 area is NOT a room without a patch** on region building (or an edifice ring). Decision for `SUPERDEEP_PRISON_ROOM_1`.
**4. Door permission.** `RimWorld.Building_Door.PawnCanOpen(Pawn)` (l.428; virtual, overridden by `Building_JammedDoor`/`Building_HackableDoor`): CanOpenDoors -> map doorsAlwaysOpen -> CanOpenAnyDoor -> fence/roamer -> factionless -> released guest -> `GenAI.MachinesLike(Faction, p)`. "Openable from outside, never from inside" = override `PawnCanOpen` to also require `p.Position` not on a D=4 cell (or the reachability veto above).
**5. Unroofed room temperature.** `Verse.RoomTempTracker.EqualizeTemperature()` (l.176): `room.UsesOutdoorTemperature` -> `Temperature = mapTemperature.OutdoorTemp` outright; otherwise `NoRoofEqualizationTempChangePerInterval()` = `TempDiffFromOutdoorsAdjusted() * noRoofCoverage * 0.0007f * 120f` (l.277-281). A stronger coupling multiplier attaches as a postfix on that method (scale for rooms made of D=4 cells).
**6. Beggar thoughts.** `CharityRefused_{Essential,Important,Worthwhile}_Beggars[_Betrayed]` (Ideology `Precepts_Charity.xml`, parent `CharityBase`, 8 days) are issued by `PreceptComp_KnowsMemoryThought` on the Charity precepts (eventDef `CharityRefused_Beggars`). They are nulled by IDEOLIGION (no charity precept -> no thought), not by traits. "Exposed Prisoner" copies this: a HistoryEvent + per-precept `PreceptComp_KnowsMemoryThought`; the psychopath exclusion needs a `nullifyingTraits` on the ThoughtDef.
**7. Prisoner Realism** (`legator`, workshop 3760196312, `Source/Core/PrisonerRealismUtility.cs` l.199 `IsPrisonRoom`): a room is prison if `!room.TouchesMapEdge` and (`room.IsPrisonCell` || painted Commons || work area || `CommonsUtility.IsGenuinePrisonCell`). It judges confinement by vanilla Room, so it follows item 3's answer; escape is vanilla `JobGiver_PrisonerEscape` with its own grace/setback prefixes.
