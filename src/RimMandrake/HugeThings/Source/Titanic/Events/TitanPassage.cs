using System.Collections.Generic;
using System.Linq;
using RimWorld;
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
    /// The incident only SCHEDULES: it picks a titan race some biome homes but this map's biomes do not, sends the tremor letter,
    /// and hands the passage to MapComponent_TitanPassages, which shakes the camera with growing force through the warning hours
    /// and then walks the titan across the map edge to edge (vanilla LordJob_ExitMapNear, the herd-migration shape). The wake
    /// does the rest. No race or biome is named: the rosters decide who comes.
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
        /// <summary>Card #5's gate, per race: RM_TitanicKernel.TitanEventEligible over the live biome commonalities.</summary>
        public static bool Eligible(PawnKindDef k, Map map, bool t3OnMap)
        {
            if (k?.race?.race == null || !k.RaceProps.Animal || k.RaceProps.Dryad) return false;
            int tier = (int)TitanicTierUtility.AdultTier(k.race);
            if (tier < RM_TitanicKernel.T2) return false;
            bool here = map.Biomes.Any(b => b.CommonalityOfAnimal(k) > 0f);
            bool some = DefDatabase<BiomeDef>.AllDefsListForReading.Any(b => b.CommonalityOfAnimal(k) > 0f);
            bool season = map.mapTemperature.SeasonAndOutdoorTemperatureAcceptableFor(k.race);
            return RM_TitanicKernel.TitanEventEligible(tier, here, some, season, t3OnMap);
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
            int dx = Mathf.Min(c.x, map.Size.x - 1 - c.x), dz = Mathf.Min(c.z, map.Size.z - 1 - c.z);
            if (dx < dz) return (c.x < map.Size.x / 2 ? "RM_TitanPassage_West" : "RM_TitanPassage_East").Translate();
            return (c.z < map.Size.z / 2 ? "RM_TitanPassage_South" : "RM_TitanPassage_North").Translate();
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
            // the warned edge is kept while it is still standable and reaches the far edge; otherwise a fresh route is found
            bool routeOk = s.IsValid && e.IsValid && s.InBounds(map) && s.Standable(map)
                           && map.reachability.CanReach(s, e, PathEndMode.OnCell, TraverseParms.For(TraverseMode.PassDoors));
            if (!routeOk) routeOk = TitanPassageUtility.TryFindStartAndEnd(map, out s, out e);
            if (!RM_HugeThingsSettings.TitanEventsActive || !TitanPassageUtility.Eligible(k, map, TitanPassageUtility.T3OnMap(map)) || !routeOk)
            {
                Messages.Message("RM_TitanPassage_Faded".Translate(), MessageTypeDefOf.NeutralEvent);
                return;
            }
            Pawn titan = PawnGenerator.GeneratePawn(new PawnGenerationRequest(k, null, PawnGenerationContext.NonPlayer, map.Tile));
            GenSpawn.Spawn(titan, CellFinder.RandomClosewalkCellNear(s, map, 8), map, Rot4.FromAngleFlat((map.Center - s).AngleFlat));
            LordMaker.MakeNewLord(null, new LordJob_ExitMapNear(e, LocomotionUrgency.Walk), map, new List<Pawn> { titan });
            arrived = titan;
            Find.LetterStack.ReceiveLetter("RM_TitanPassage_ArriveLabel".Translate(titan.LabelShortCap),
                "RM_TitanPassage_ArriveText".Translate(titan.LabelShort), LetterDefOf.ThreatSmall, titan);
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
