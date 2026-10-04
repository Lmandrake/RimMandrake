using System.Collections.Generic;
using System.Linq;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_ANT_THEFT_RAIDBACK_1 part A (the theft; the raid-back quest is part B, filed separately).
    // The kurreth raid steals instead of slaughtering: the ants fight as a plain assault, while up to a third of the
    // column peels off to stun a thornbug (then any tamed sap-sucker) non-lethally and carry it off the map ALIVE.
    // Pawn.ExitMap hands a carried pawn of another faction to the carrier's faction's KidnappedPawnsTracker, so the
    // animal stays a living world pawn held by the kurreth swarm (part B recovers it from there). When nothing is
    // left to take and something was taken, the rest of the column exits. No silent vanishing: one letter per column
    // names every animal taken and the direction it left, and a slime trail runs from the exit cell back along the
    // carrier's path. With antTheftEnabled off the lure keeps its plain LordJob_AssaultColony (RM_MapComponent_
    // TwoFrontLure.SpawnRaidWave).
    public static class RM_KurrethTheftUtility
    {
        /// <summary>Theft order: thornbugs first, then the tamed sap-suckers.</summary>
        public static readonly string[] TargetOrder = { "RM_Thornbug", "RM_Vaulm", "RM_Ollareth", "RM_Drommath" };

        public static int TargetRank(Pawn p)
        {
            if (p == null)
            {
                return -1;
            }
            int i = System.Array.IndexOf(TargetOrder, p.def.defName);
            return i >= 0 ? i : System.Array.IndexOf(TargetOrder, p.kindDef?.defName);
        }

        public static bool IsTheftTarget(Pawn p)
        {
            return p != null && p.Spawned && !p.Dead && p.Faction == Faction.OfPlayer && p.RaceProps.Animal && TargetRank(p) >= 0;
        }

        /// <summary>Eight-way compass word for a map-edge cell seen from the map centre.</summary>
        public static string Direction(IntVec3 cell, Map map)
        {
            return KurrethTheftMath.Compass(cell.x - map.Center.x, cell.z - map.Center.z);
        }
    }

    public static class KurrethTheftMath
    {
        private static readonly string[] Words = { "east", "north-east", "north", "north-west", "west", "south-west", "south", "south-east" };

        /// <summary>dx east, dz north. 0 deg = east, counter-clockwise, 45-degree sectors.</summary>
        public static string Compass(float dx, float dz)
        {
            if (dx == 0f && dz == 0f)
            {
                return "centre";
            }
            float a = Mathf.Atan2(dz, dx) * Mathf.Rad2Deg;
            if (a < 0f)
            {
                a += 360f;
            }
            return Words[Mathf.RoundToInt(a / 45f) % 8];
        }

        /// <summary>How many of a column of n may peel off to steal: a third, at least one.</summary>
        public static int MaxThieves(int n)
        {
            return n <= 0 ? 0 : Mathf.Max(1, Mathf.CeilToInt(n / 3f));
        }
    }

    public class RM_LordJob_KurrethTheft : LordJob
    {
        public const string MemoTheftDone = "RM_KurrethTheftDone";

        public RM_LordJob_KurrethTheft() { }

        public override bool GuiltyOnDowned => true;

        public override StateGraph CreateGraph()
        {
            StateGraph graph = new StateGraph();
            LordToil steal = new RM_LordToil_KurrethTheft();
            graph.AddToil(steal);
            LordToil exit = new LordToil_ExitMap(LocomotionUrgency.Jog, canDig: false, interruptCurrentJob: true);
            graph.AddToil(exit);
            Transition t = new Transition(steal, exit);
            t.AddTrigger(new Trigger_Memo(MemoTheftDone));
            graph.AddTransition(t);
            return graph;
        }

        public override void Notify_PawnLost(Pawn p, PawnLostCondition condition)
        {
            base.Notify_PawnLost(p, condition);
            // Pawn.ExitMap calls this BEFORE it hands the carried pawn to the faction's kidnap tracker, so the
            // victim is still in the carrier's hands here.
            if (condition != PawnLostCondition.ExitedMap || p.carryTracker?.CarriedThing is not Pawn victim
                || victim.Faction != Faction.OfPlayer || p.Map == null)
            {
                return;
            }
            p.Map.GetComponent<RM_MapComponent_KurrethTheft>()?.Notify_Stolen(victim, p, p.Position,
                RM_LordToil_KurrethTheft.PathOf(p));
        }

        public override void ExposeData() { }
    }

    public class RM_LordToil_KurrethTheft : LordToil_AssaultColony
    {
        private const int CheckInterval = 60;
        private const float SearchRadius = 60f;

        // Carrier path samples for the slime trail. Not saved: after a load the trail falls back to a straight
        // line inward from the exit cell.
        private static readonly Dictionary<int, List<IntVec3>> paths = new Dictionary<int, List<IntVec3>>();

        public RM_LordToil_KurrethTheft() : base(false, false) { }

        public static List<IntVec3> PathOf(Pawn p)
        {
            return p != null && paths.TryGetValue(p.thingIDNumber, out List<IntVec3> l) ? l : null;
        }

        private static bool IsThieving(Pawn p)
        {
            JobDef j = p.CurJobDef;
            return j != null && (j == RM_KurrethTheftDefOf.RM_KurrethStun || j == RM_KurrethTheftDefOf.RM_KurrethCarryOff);
        }

        public override void LordToilTick()
        {
            base.LordToilTick();
            if (Find.TickManager.TicksGame % CheckInterval != 0 || lord.ownedPawns.Count == 0)
            {
                return;
            }
            Map map = lord.Map;
            List<Pawn> targets = map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer).Where(RM_KurrethTheftUtility.IsTheftTarget).ToList();
            var claimed = new HashSet<Pawn>();
            int thieves = 0;
            foreach (Pawn p in lord.ownedPawns)
            {
                if (IsThieving(p))
                {
                    thieves++;
                    if (p.CurJob.targetA.Thing is Pawn v)
                    {
                        claimed.Add(v);
                    }
                    if (!paths.TryGetValue(p.thingIDNumber, out List<IntVec3> l))
                    {
                        paths[p.thingIDNumber] = l = new List<IntVec3>();
                    }
                    if (l.Count == 0 || l[l.Count - 1] != p.Position)
                    {
                        l.Add(p.Position);
                        if (l.Count > 40)
                        {
                            l.RemoveAt(0);
                        }
                    }
                }
            }
            if (targets.Count == 0)
            {
                if (thieves == 0 && map.GetComponent<RM_MapComponent_KurrethTheft>()?.StolenBy(lord) > 0)
                {
                    lord.ReceiveMemo(RM_LordJob_KurrethTheft.MemoTheftDone);
                }
                return;
            }
            int max = KurrethTheftMath.MaxThieves(lord.ownedPawns.Count);
            foreach (Pawn p in lord.ownedPawns.ToList())
            {
                if (thieves >= max)
                {
                    break;
                }
                if (!p.Spawned || p.Downed || IsThieving(p) || p.InMentalState)
                {
                    continue;
                }
                Job job = TheftJobFor(p, targets, claimed);
                if (job == null)
                {
                    continue;
                }
                claimed.Add((Pawn)job.targetA.Thing);
                p.jobs.StartJob(job, JobCondition.InterruptForced);
                thieves++;
            }
        }

        /// <summary>A downed target is carried off (found through RM_HaulVictimAIUtility, the kit's generalised
        /// kidnap finder); an upright one is stunned first. Best-ranked species first, then nearest.</summary>
        private static Job TheftJobFor(Pawn thief, List<Pawn> targets, HashSet<Pawn> claimed)
        {
            if (RM_HaulVictimAIUtility.TryFindGoodHaulVictim(thief, SearchRadius,
                    v => RM_KurrethTheftUtility.IsTheftTarget(v) && !claimed.Contains(v), out Pawn downed,
                    null, requireManipulation: false)
                && RCellFinder.TryFindBestExitSpot(thief, out IntVec3 exit))
            {
                Job carry = JobMaker.MakeJob(RM_KurrethTheftDefOf.RM_KurrethCarryOff, downed, exit);
                carry.count = 1;
                return carry;
            }
            Pawn upright = targets
                .Where(v => !v.Downed && !claimed.Contains(v) && thief.CanReserveAndReach(v, PathEndMode.Touch, Danger.Deadly))
                .OrderBy(RM_KurrethTheftUtility.TargetRank)
                .ThenBy(v => v.Position.DistanceToSquared(thief.Position))
                .FirstOrDefault();
            return upright == null ? null : JobMaker.MakeJob(RM_KurrethTheftDefOf.RM_KurrethStun, upright);
        }
    }

    [DefOf]
    public static class RM_KurrethTheftDefOf
    {
        public static JobDef RM_KurrethStun;
        public static JobDef RM_KurrethCarryOff;

        static RM_KurrethTheftDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_KurrethTheftDefOf));
        }
    }

    /// <summary>Records every animal the kurreth carry off from this map, lays the trail, and sends one letter per
    /// column. Part B (the raid-back) reads Thefts.</summary>
    public class RM_MapComponent_KurrethTheft : MapComponent
    {
        public class Theft : IExposable
        {
            public Pawn victim;
            public IntVec3 exitCell;
            public int tick;
            public int lordId = -1;

            public void ExposeData()
            {
                Scribe_References.Look(ref victim, "victim", true);
                Scribe_Values.Look(ref exitCell, "exitCell");
                Scribe_Values.Look(ref tick, "tick");
                Scribe_Values.Look(ref lordId, "lordId", -1);
            }
        }

        private const int LetterDelayTicks = 600;
        private const int TrailInwardCells = 15;

        private List<Theft> thefts = new List<Theft>();
        private List<Theft> pending = new List<Theft>();
        private int letterAt = -1;

        public RM_MapComponent_KurrethTheft(Map map) : base(map) { }

        public List<Theft> Thefts => thefts;

        public int StolenBy(Lord lord)
        {
            return lord == null ? 0 : thefts.Count(t => t.lordId == lord.loadID);
        }

        public void Notify_Stolen(Pawn victim, Pawn carrier, IntVec3 exitCell, List<IntVec3> path)
        {
            var t = new Theft { victim = victim, exitCell = exitCell, tick = Find.TickManager.TicksGame, lordId = carrier.GetLord()?.loadID ?? -1 };
            thefts.Add(t);
            pending.Add(t);
            if (letterAt < 0)
            {
                letterAt = Find.TickManager.TicksGame + LetterDelayTicks;
            }
            LayTrail(exitCell, path);
        }

        /// <summary>Insect slime on the carrier's last cells, or a straight line inward from the exit cell.</summary>
        public int LayTrail(IntVec3 exitCell, List<IntVec3> path)
        {
            ThingDef slime = DefDatabase<ThingDef>.GetNamedSilentFail("Filth_Slime");
            if (slime == null)
            {
                return 0;
            }
            IEnumerable<IntVec3> cells;
            if (path != null && path.Count >= 3)
            {
                cells = path;
            }
            else
            {
                Vector3 dir = (map.Center - exitCell).ToVector3().normalized;
                cells = Enumerable.Range(0, TrailInwardCells).Select(i => (exitCell.ToVector3Shifted() + dir * i).ToIntVec3());
            }
            int laid = 0;
            foreach (IntVec3 c in cells.Distinct())
            {
                if (c.InBounds(map) && c.Standable(map) && FilthMaker.TryMakeFilth(c, map, slime, 1))
                {
                    laid++;
                }
            }
            return laid;
        }

        public override void MapComponentTick()
        {
            if (letterAt < 0 || Find.TickManager.TicksGame < letterAt)
            {
                return;
            }
            letterAt = -1;
            if (pending.Count == 0)
            {
                return;
            }
            string names = pending.Select(t => t.victim?.LabelShort ?? "an animal").ToCommaList(true);
            string dir = RM_KurrethTheftUtility.Direction(pending[pending.Count - 1].exitCell, map);
            string text = "The kurreth did not come to kill. They have carried off " + names + ", alive, and the column "
                          + "left the map to the " + dir + ". A trail of slime leads off the edge there.\n\n"
                          + "A stolen animal is not dead: the kurreth keep what they take.";
            // FEVERWOOD_KURRETH_COLUMN_RAIDBACK_1: the raid-back quest (camp site, then the hive).
            Quest column = RM_KurrethColumnUtility.TryStartColumnQuest(map, pending.Select(t => t.victim).ToList());
            if (column != null)
            {
                text += " This column has made camp a few tiles off; the quest marks it.";
            }
            Find.LetterStack.ReceiveLetter("Carried off: " + pending.Count + (pending.Count == 1 ? " animal" : " animals"),
                text, LetterDefOf.NegativeEvent, new LookTargets(pending[pending.Count - 1].exitCell, map), null, column);
            pending.Clear();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref thefts, "thefts", LookMode.Deep);
            Scribe_Collections.Look(ref pending, "pending", LookMode.Deep);
            Scribe_Values.Look(ref letterAt, "letterAt", -1);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                thefts = thefts ?? new List<Theft>();
                pending = pending ?? new List<Theft>();
            }
        }
    }

    /// <summary>Proof hooks for the ant_theft chain (static_call, args "current").</summary>
    public static class RM_KurrethTheftProof
    {
        /// <summary>Spawns 3 tamed thornbugs near the centre and a kurreth column at the edge under the theft
        /// LordJob (the lure's route with the setting on). Step ticks, then ProofState.</summary>
        public static string ProofRaid(Map map)
        {
            map = map ?? Find.CurrentMap;
            PawnKindDef bug = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Thornbug");
            PawnKindDef ant = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Kurreth");
            FactionDef fd = DefDatabase<FactionDef>.GetNamedSilentFail("RM_FactionDef_KurrethSwarm");
            if (map == null || bug == null || ant == null || fd == null)
            {
                return "ERROR missing map/RM_Thornbug/RM_Kurreth/faction";
            }
            Faction f = Find.FactionManager.FirstFactionOfDef(fd);
            if (f == null)
            {
                f = FactionGenerator.NewGeneratedFaction(new FactionGeneratorParms(fd));
                Find.FactionManager.Add(f);
            }
            for (int i = 0; i < 3; i++)
            {
                Pawn b = PawnGenerator.GeneratePawn(bug, Faction.OfPlayer);
                GenSpawn.Spawn(b, CellFinder.RandomClosewalkCellNear(map.Center, map, 5), map);
            }
            if (!CellFinder.TryFindRandomEdgeCellWith(c => c.Walkable(map), map, CellFinder.EdgeRoadChance_Hostile, out IntVec3 edge))
            {
                return "ERROR no edge cell";
            }
            var ants = new List<Pawn>();
            for (int i = 0; i < 6; i++)
            {
                Pawn a = PawnGenerator.GeneratePawn(ant, f);
                GenSpawn.Spawn(a, CellFinder.RandomClosewalkCellNear(edge, map, 4), map);
                ants.Add(a);
            }
            LordMaker.MakeNewLord(f, new RM_LordJob_KurrethTheft(), map, ants);
            return "RAID ants=" + ants.Count + " thornbugs=3 edge=" + edge + " faction=" + f.GetUniqueLoadID();
        }

        public static string ProofState(Map map)
        {
            map = map ?? Find.CurrentMap;
            var comp = map?.GetComponent<RM_MapComponent_KurrethTheft>();
            FactionDef fd = DefDatabase<FactionDef>.GetNamedSilentFail("RM_FactionDef_KurrethSwarm");
            Faction f = fd == null ? null : Find.FactionManager.FirstFactionOfDef(fd);
            List<Pawn> held = f?.kidnapped?.KidnappedPawnsListForReading ?? new List<Pawn>();
            List<Pawn> onMap = map?.mapPawns.AllPawnsSpawned.Where(p => p.def.defName == "RM_Thornbug").ToList() ?? new List<Pawn>();
            int deadBugs = (map?.listerThings.ThingsInGroup(ThingRequestGroup.Corpse) ?? new List<Thing>())
                .OfType<Corpse>().Count(c => c.InnerPawn?.def.defName == "RM_Thornbug");
            return "thefts=" + (comp?.Thefts.Count ?? -1) + " heldByKurreth=" + held.Count(p => !p.Dead)
                   + " thornbugsOnMap=" + onMap.Count + " thornbugCorpses=" + deadBugs
                   + " stolenIds=" + string.Join(",", comp?.Thefts.Select(t => t.victim?.thingIDNumber.ToString() ?? "?") ?? Enumerable.Empty<string>())
                   + " letters=" + Find.LetterStack.LettersListForReading.Count(l => l.Label.ToString().StartsWith("Carried off"));
        }
    }
}
