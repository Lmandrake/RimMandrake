using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.AI.Group;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// TITAN_CAMPS_SCAVENGERS_EVENTS_1, card #5 (owner 2026-09-09): "Titans roam only where the rosters home them; anywhere else
    /// they arrive as scripted events/quests with warning (footfall tremors first). Wake damage applies to any structure including
    /// the player's - that is the point."
    ///
    /// The incident only SCHEDULES: it picks a titan from this map biome's own hints (its RM_TitanPassageExtension passage list,
    /// else its own roster; sea giants only on sea maps, land giants only on land; owner by card 2026-10-21), sends the tremor
    /// letter, and hands the passage to MapComponent_TitanPassages, which shakes the camera with growing force through the
    /// warning hours and then walks the titan across the map from the warned edge. The wake and clearing jobs do the damage.
    /// No race or biome is named in code: the biome data decides who comes.
    /// </summary>
    public class IncidentWorker_TitanPassage : IncidentWorker
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            Map map = parms.target as Map;
            if (map == null || !RM_HugeThingsSettings.TitanEventsActive) return false;
            MapComponent_TitanPassages comp = map.GetComponent<MapComponent_TitanPassages>();
            if (comp == null || comp.HasPending) return false;
            return TitanPassageUtility.TryFindTitanKind(map, out _) && TitanPassageUtility.TryFindStartAndEnd(map, out _, out _);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            if (!TitanPassageUtility.TryFindTitanKind(map, out PawnKindDef kind)) return false;
            if (!TitanPassageUtility.TryFindStartAndEnd(map, out IntVec3 start, out IntVec3 end)) return false;
            MapComponent_TitanPassages comp = map.GetComponent<MapComponent_TitanPassages>();
            if (comp == null) return false;
            comp.Schedule(kind, start, end, RM_TitanicKernel.WarningTicks(RM_HugeThingsSettings.titanEventWarningHours));
            SendStandardLetter("RM_TitanPassage_TremorLabel".Translate(), "RM_TitanPassage_TremorText".Translate(
                    TitanPassageUtility.EdgeName(map, start)), LetterDefOf.ThreatSmall, parms, new TargetInfo(start, map));
            return true;
        }
    }

    public static class TitanPassageUtility
    {
        private enum RouteCell : byte { Unknown, Open, Clearable, Closed }

        public const string SeabedLayerDefName = "RM_SeabedLayer";
        public const string SeabedFloorExtensionName = "RM_SeabedFloorExtension";

        /// <summary>The 2026-10-21 card's gate, per kind: RM_TitanicKernel.TitanEventEligible over the live biome commonalities.
        /// A calf kind qualifies by lineage ("Calves are ok"); only supported T3 stages trigger the existing-T3 veto.</summary>
        public static bool Eligible(PawnKindDef k, Map map, bool t3OnMap)
        {
            if (k?.race?.race == null || map == null || !k.RaceProps.Animal || k.RaceProps.Dryad) return false;
            if (k.race.GetModExtension<RM_TitanicExtension>()?.harnessOnly == true) return false;
            int tier = (int)TitanicTierUtility.AdultTier(k.race);
            if (tier < RM_TitanicKernel.T2) return false;
            bool optedOut = map.Biomes.Any(b => b?.GetModExtension<RM_TitanPassageExtension>()?.none == true);
            bool hasList = false, onList = false;
            foreach (BiomeDef b in map.Biomes)
            {
                List<PawnKindDef> list = b?.GetModExtension<RM_TitanPassageExtension>()?.passers;
                if (list == null || list.Count == 0) continue;
                hasList = true;
                if (list.Contains(k)) onList = true;
            }
            bool here = map.Biomes.Any(b => b.CommonalityOfAnimal(k) > 0f);
            bool season = map.mapTemperature.SeasonAndOutdoorTemperatureAcceptableFor(k.race);
            return RM_TitanicKernel.TitanEventEligible(tier, (int)TitanicTierUtility.SpacingTier(k.race), optedOut, IsSeaCreature(k), IsSeaMap(map), hasList, onList, here,
                season, t3OnMap);
        }

        /// <summary>A sea biome: a water biome (Grey Sea, Twilight Sea, the Scald, the Chill...) or a seabed floor, whose cast is
        /// its sea's (RM_SeabedFloorLife copies it at startup). The floor test is by extension type name on purpose: this
        /// assembly must not depend on DivingInteraction.</summary>
        public static bool IsSeaBiome(BiomeDef b)
        {
            if (b == null) return false;
            if (b.isWaterBiome) return true;
            if (b.modExtensions != null)
                foreach (DefModExtension e in b.modExtensions)
                    if (e != null && e.GetType().Name == SeabedFloorExtensionName) return true;
            return false;
        }

        /// <summary>A sea map: its own biome is a sea biome, or it lies on the seabed planet layer (name test, as
        /// RM_SurfaceHome.IsSeabedMap).</summary>
        public static bool IsSeaMap(Map map)
        {
            if (map == null) return false;
            if (map.Tile.Valid && map.Tile.Layer?.Def?.defName == SeabedLayerDefName) return true;
            return IsSeaBiome(map.Biome);
        }

        private static Dictionary<PawnKindDef, bool> seaCache;

        /// <summary>A sea creature: homed in at least one biome, and only ever in sea biomes. Cached per kind (rosters are fixed
        /// after def load).</summary>
        public static bool IsSeaCreature(PawnKindDef k)
        {
            if (k == null) return false;
            if (seaCache == null) seaCache = new Dictionary<PawnKindDef, bool>();
            if (seaCache.TryGetValue(k, out bool v)) return v;
            int sea = 0, land = 0;
            foreach (BiomeDef b in DefDatabase<BiomeDef>.AllDefsListForReading)
            {
                if (b.CommonalityOfAnimal(k) <= 0f) continue;
                if (IsSeaBiome(b)) sea++; else land++;
            }
            v = RM_TitanicKernel.IsSeaCreature(sea, land);
            seaCache[k] = v;
            return v;
        }

        public static bool T3OnMap(Map map)
        {
            return map.mapPawns.AllPawnsSpawned.Any(p => !p.Dead && TitanicTierUtility.GetTier(p) == TitanicTier.T3);
        }

        public static bool TryFindTitanKind(Map map, out PawnKindDef kind)
        {
            bool t3 = T3OnMap(map);
            return DefDatabase<PawnKindDef>.AllDefsListForReading.Where(k => Eligible(k, map, t3)).TryRandomElement(out kind);
        }

        /// <summary>The herd-migration route: an entry cell and the reachable edge cell farthest from it.</summary>
        public static bool TryFindStartAndEnd(Map map, out IntVec3 start, out IntVec3 end)
        {
            end = IntVec3.Invalid;
            if (!RCellFinder.TryFindRandomPawnEntryCell(out start, map, CellFinder.EdgeRoadChance_Animal)) return false;
            IntVec3 s = start;
            for (int i = 0; i < 8; i++)
            {
                if (!CellFinder.TryFindRandomEdgeCellWith(x => map.reachability.CanReach(s, x, PathEndMode.OnCell,
                        TraverseParms.For(TraverseMode.PassDoors)), map, CellFinder.EdgeRoadChance_Ignore, out IntVec3 r)) break;
                if (!end.IsValid || r.DistanceToSquared(start) > end.DistanceToSquared(start)) end = r;
            }
            return end.IsValid;
        }

        public static string EdgeName(Map map, IntVec3 c)
        {
            Rot4 edge = PassageEdge(map, c);
            if (edge == Rot4.West) return "RM_TitanPassage_West".Translate();
            if (edge == Rot4.East) return "RM_TitanPassage_East".Translate();
            return (edge == Rot4.South ? "RM_TitanPassage_South" : "RM_TitanPassage_North").Translate();
        }

        internal static Rot4 PassageEdge(Map map, IntVec3 c)
        {
            int dx = Mathf.Min(c.x, map.Size.x - 1 - c.x), dz = Mathf.Min(c.z, map.Size.z - 1 - c.z);
            if (dx < dz) return c.x < map.Size.x / 2 ? Rot4.West : Rot4.East;
            return c.z < map.Size.z / 2 ? Rot4.South : Rot4.North;
        }

        // Only slide along the named edge, with the outermost row of the body on that edge.
        internal static IEnumerable<IntVec3> EdgeAnchors(Map map, IntVec3 edgeCell, CellRect foot, int radius)
        {
            Rot4 edge = PassageEdge(map, edgeCell);
            int left = -foot.minX, right = map.Size.x - 1 - foot.maxX;
            int bottom = -foot.minZ, top = map.Size.z - 1 - foot.maxZ;
            if (left > right || bottom > top) yield break;
            bool horizontal = edge == Rot4.South || edge == Rot4.North;
            int x = horizontal ? Mathf.Clamp(edgeCell.x, left, right) : edge == Rot4.West ? left : right;
            int z = horizontal ? edge == Rot4.South ? bottom : top : Mathf.Clamp(edgeCell.z, bottom, top);
            for (int i = 0; i <= 2 * radius; i++)
            {
                int offset = i % 2 == 0 ? -i / 2 : (i + 1) / 2;
                int ax = horizontal ? x + offset : x, az = horizontal ? z : z + offset;
                if (ax >= left && ax <= right && az >= bottom && az <= top) yield return new IntVec3(ax, 0, az);
            }
        }

        internal static List<IntVec3> FindRoute(Pawn pawn, Map map, IEnumerable<IntVec3> entries, IEnumerable<IntVec3> exits,
                                               CellRect foot, out WallsSlotsUtility.Crossing crossing, out Thing obstacle)
        {
            crossing = null;
            obstacle = null;
            int w = map.Size.x, h = map.Size.z;
            TitanicTier tier = TitanicTierUtility.GetTier(pawn);
            bool avoidRoof = RM_HugeThingsSettings.RoofAvoidanceActive && tier != TitanicTier.None;
            bool clear = RM_HugeThingsSettings.TitanClearingActive && tier != TitanicTier.None && !pawn.Flying
                         && pawn.TryGetComp<CompTitanicWake>() != null;
            bool walls = clear && RM_HugeThingsSettings.WallsSlotsActive && WallsSlotsUtility.Breadth(pawn) > 1;
            PathGrid grid = map.pathing.For(pawn).pathGrid;
            var cells = new RouteCell[w * h];
            RouteCell Cell(int i)
            {
                if (cells[i] != RouteCell.Unknown) return cells[i];
                IntVec3 c = map.cellIndices.IndexToCell(i);
                if (avoidRoof && c.GetRoof(map)?.isThickRoof == true) return cells[i] = RouteCell.Closed;
                if (grid.Walkable(c) && c.GetEdifice(map)?.BlocksPawn(pawn) != true) return cells[i] = RouteCell.Open;
                if (c.GetTerrain(map).passability == Traversability.Impassable) return cells[i] = RouteCell.Closed;
                return cells[i] = clear && Obstacle(c) != null ? RouteCell.Clearable : RouteCell.Closed;
            }

            Thing Obstacle(IntVec3 c)
            {
                Building ed = c.GetEdifice(map);
                if (walls && WallsSlotsUtility.WallEligible(pawn, ed)) return ed;
                if (ed != null) return TitanClearingUtility.Classify(pawn, tier, ed) != ClearKind.None ? ed : null;
                return c.GetThingList(map).FirstOrDefault(t => TitanClearingUtility.Classify(pawn, tier, t) == ClearKind.Trunk);
            }

            int[] starts = entries.Where(c => c.InBounds(map)).Select(map.cellIndices.CellToIndex).ToArray();
            int[] ends = exits.Where(c => c.InBounds(map)).Select(map.cellIndices.CellToIndex).ToArray();
            if (starts.Length == 0 || ends.Length == 0) return null;
            List<IntVec3> Route(Func<int, bool> allowed) => TitanClearing.PassageRoute(w, h, starts, ends,
                foot.minX, foot.minZ, foot.maxX, foot.maxZ, allowed)?.Select(map.cellIndices.IndexToCell).ToList();
            List<IntVec3> walk = Route(i => Cell(i) == RouteCell.Open);
            if (walk != null || !clear) return walk;
            // Match the clearing decider: exclude a crossing that holds before trying another way through.
            for (int attempt = 0; attempt < WallsSlotsDecider.MaxBreachTries; attempt++)
            {
                List<IntVec3> anchors = Route(i => Cell(i) != RouteCell.Closed);
                if (anchors == null) return null;
                IntVec3 start = anchors[0];
                bool held = false;
                for (int n = 0; n < anchors.Count; n++)
                {
                    IntVec3 anchor = anchors[n];
                    Thing block = null;
                    foreach (IntVec3 c in foot.MovedBy(anchor))
                        if (Cell(map.cellIndices.CellToIndex(c)) == RouteCell.Clearable) { block = Obstacle(c); break; }
                    if (block == null) continue;
                    var group = walls ? WallsSlotsUtility.Probe(pawn, map, anchors, n, start, foot.MovedBy(start)) : null;
                    if (group != null && group.cells.Count > 0 && !WallsSlots.Breaks(group.verdict))
                    {
                        foreach (IntVec3 c in group.cells) cells[map.cellIndices.CellToIndex(c)] = RouteCell.Closed;
                        held = true;
                        break;
                    }
                    if (group != null && WallsSlots.Breaks(group.verdict))
                    {
                        if (obstacle == null && crossing == null && WallsSlotsUtility.WallEligible(pawn, block as Building))
                            crossing = group;
                        n = group.lastNode;
                    }
                    if (obstacle == null && crossing == null) obstacle = block;
                }
                if (!held) return anchors;
                crossing = null;
                obstacle = null;
            }
            return null;
        }
    }

    // A vanilla exit job first requires a reachable edge cell. Give clearing its goal directly, and exit when the body reaches it.
    public class JobDriver_TitanPassageCross : JobDriver_Goto
    {
        protected override IEnumerable<Toil> MakeNewToils()
        {
            Toil walk = Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);
            Action startPath = walk.initAction;
            walk.initAction = () =>
            {
                CellRect foot = pawn.OccupiedRect().MovedBy(-pawn.Position);
                var route = TitanPassageUtility.FindRoute(pawn, Map, new[] { pawn.Position }, new[] { job.targetA.Cell }, foot,
                    out WallsSlotsUtility.Crossing crossing, out Thing obstacle);
                if (crossing != null && WallsSlotsDecider.StartCrossing(pawn, crossing)) return;
                if (obstacle != null && TitanClearingUtility.StartPassageClearing(pawn, obstacle)) return;
                if (route == null || crossing != null || obstacle != null) EndJobWith(JobCondition.Incompletable);
                else startPath();
            };
            yield return walk;
            yield return Toils_General.Do(() =>
            {
                if (Map.CanEverExit && (!ModsConfig.AnomalyActive || MetalhorrorUtility.TryPawnExitMap(pawn)))
                    pawn.ExitMap(true, TitanPassageUtility.PassageEdge(Map, job.targetB.Cell));
            });
        }
    }

    /// <summary>The scheduled passages of one map: tremors through the warning, then the titan walks in.</summary>
    public class MapComponent_TitanPassages : MapComponent
    {
        private const int ShakeInterval = 300;
        private const int MessageInterval = 2 * GenDate.TicksPerHour;

        private PawnKindDef kind;
        private IntVec3 start = IntVec3.Invalid, end = IntVec3.Invalid;
        private int arrivalTick = -1, warnedTick = -1, warningTicks;
        private Pawn arrived;

        public MapComponent_TitanPassages(Map map) : base(map) { }

        public bool HasPending => kind != null && arrivalTick >= 0;
        public PawnKindDef PendingKind => kind;
        public int ArrivalTick => arrivalTick;
        public Pawn LastArrived => arrived;

        public void Schedule(PawnKindDef k, IntVec3 s, IntVec3 e, int warning)
        {
            kind = k; start = s; end = e; warningTicks = warning;
            int now = Find.TickManager.TicksGame;
            arrivalTick = now + warning; warnedTick = now;
        }

        /// <summary>Validation hook: bring the arrival forward to the next tick.</summary>
        public void DebugArriveNow() { if (HasPending) arrivalTick = Find.TickManager.TicksGame; }

        public override void MapComponentTick()
        {
            if (!HasPending) return;
            int now = Find.TickManager.TicksGame;
            if (now >= arrivalTick) { Arrive(); return; }
            if (now % ShakeInterval == 0 && Find.CurrentMap == map)
            {
                // Footfall: stronger the nearer it comes (0.3 at the first tremor, 1.5 at arrival).
                float progress = warningTicks > 0 ? 1f - (arrivalTick - now) / (float)warningTicks : 1f;
                Find.CameraDriver.shaker.DoShake(Mathf.Lerp(0.3f, 1.5f, Mathf.Clamp01(progress)));
            }
            if (now - warnedTick >= MessageInterval)
            {
                warnedTick = now;
                Messages.Message("RM_TitanPassage_TremorStronger".Translate(), new TargetInfo(start, map), MessageTypeDefOf.NeutralEvent);
            }
        }

        private void Arrive()
        {
            PawnKindDef k = kind;
            IntVec3 s = start, e = end;
            Clear();
            if (!RM_HugeThingsSettings.TitanEventsActive || !s.InBounds(map) || !e.InBounds(map)
                || !TitanPassageUtility.Eligible(k, map, TitanPassageUtility.T3OnMap(map)))
            {
                Messages.Message("RM_TitanPassage_Faded".Translate(), MessageTypeDefOf.NeutralEvent);
                return;
            }
            Pawn titan = PawnGenerator.GeneratePawn(new PawnGenerationRequest(k, null, PawnGenerationContext.NonPlayer, map.Tile));
            Rot4 rotation = Rot4.FromAngleFlat((map.Center - s).AngleFlat);
            CellRect foot = LargePawnsBridge.ArrivalFootprint(titan, rotation);
            var entries = TitanPassageUtility.EdgeAnchors(map, s, foot, 8).Where(
                a => foot.MovedBy(a).All(c => c.Standable(map) && c.GetFirstPawn(map) == null)).ToArray();
            var exits = TitanPassageUtility.EdgeAnchors(map, e, foot, (int)LordJob_ExitMapNear.DefaultRadius).Except(entries);
            var route = TitanPassageUtility.FindRoute(titan, map, entries, exits, foot, out _, out _);
            if (route == null)
            {
                Find.WorldPawns.PassToWorld(titan, PawnDiscardDecideMode.Discard);
                Messages.Message("RM_TitanPassage_Faded".Translate(), MessageTypeDefOf.NeutralEvent);
                return;
            }
            GenSpawn.Spawn(titan, route[0], map, rotation);
            LordMaker.MakeNewLord(null, new LordJob_ExitMapNear(e, LocomotionUrgency.Walk), map, new List<Pawn> { titan });
            arrived = titan;
            Find.LetterStack.ReceiveLetter("RM_TitanPassage_ArriveLabel".Translate(titan.LabelShortCap),
                "RM_TitanPassage_ArriveText".Translate(titan.LabelShort), LetterDefOf.ThreatSmall, titan);
            if (!map.CanEverExit) return;
            Job job = JobMaker.MakeJob(RM_TitanicCreaturesDefOf.RM_TitanPassageCross, route[route.Count - 1], e);
            job.locomotionUrgency = LocomotionUrgency.Walk;
            titan.jobs.StartJob(job, JobCondition.InterruptForced);
        }

        private void Clear()
        {
            kind = null; arrivalTick = -1; warnedTick = -1; start = IntVec3.Invalid; end = IntVec3.Invalid;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Defs.Look(ref kind, "rmTitanKind");
            Scribe_Values.Look(ref start, "rmTitanStart", IntVec3.Invalid);
            Scribe_Values.Look(ref end, "rmTitanEnd", IntVec3.Invalid);
            Scribe_Values.Look(ref arrivalTick, "rmTitanArrival", -1);
            Scribe_Values.Look(ref warnedTick, "rmTitanWarned", -1);
            Scribe_Values.Look(ref warningTicks, "rmTitanWarningTicks", 0);
            Scribe_References.Look(ref arrived, "rmTitanArrived");
            if (Scribe.mode == LoadSaveMode.PostLoadInit && kind == null) arrivalTick = -1;
        }
    }
}
