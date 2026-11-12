using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // The sentinels' only lord: one toil, a slow loop of waypoints, no transition anywhere else. No assault, no flee,
    // no raid: the graph has nothing to switch to.
    public class LordJob_CathedralDescentPatrol : LordJob
    {
        public List<IntVec3> waypoints = new List<IntVec3>();
        public DutyDef duty;

        public LordJob_CathedralDescentPatrol()
        {
        }

        public LordJob_CathedralDescentPatrol(List<IntVec3> waypoints, DutyDef duty)
        {
            this.waypoints = waypoints;
            this.duty = duty;
        }

        public override bool AddFleeToil => false;

        public override StateGraph CreateGraph()
        {
            StateGraph graph = new StateGraph();
            graph.StartingToil = new LordToil_CathedralDescentPatrol(waypoints, duty);
            return graph;
        }

        public override void ExposeData()
        {
            Scribe_Collections.Look(ref waypoints, "waypoints", LookMode.Value);
            Scribe_Defs.Look(ref duty, "duty");
        }
    }

    public class LordToilData_CathedralDescentPatrol : LordToilData
    {
        public int index;
        public int waited;
        public int sinceAdvance;

        public override void ExposeData()
        {
            Scribe_Values.Look(ref index, "index");
            Scribe_Values.Look(ref waited, "waited");
            Scribe_Values.Look(ref sinceAdvance, "sinceAdvance");
        }
    }

    // Every pawn's duty focus is the loop's current waypoint. When all of them have stood near it for a while (or the
    // walk stalls), the next waypoint becomes the focus.
    public class LordToil_CathedralDescentPatrol : LordToil
    {
        private const int CheckEvery = 120;
        private const float NearRadius = 5f;
        private const int PauseTicks = 600;
        private const int StallTicks = 9000;

        private readonly List<IntVec3> waypoints;
        private readonly DutyDef duty;

        public LordToil_CathedralDescentPatrol(List<IntVec3> waypoints, DutyDef duty)
        {
            this.waypoints = waypoints ?? new List<IntVec3>();
            this.duty = duty;
            data = new LordToilData_CathedralDescentPatrol();
        }

        private LordToilData_CathedralDescentPatrol Data => (LordToilData_CathedralDescentPatrol)data;

        public override bool AllowSatisfyLongNeeds => false;

        public override void UpdateAllDuties()
        {
            if (waypoints.Count == 0 || duty == null)
            {
                return;
            }
            IntVec3 focus = waypoints[Data.index % waypoints.Count];
            foreach (Pawn pawn in lord.ownedPawns)
            {
                pawn.mindState.duty = new PawnDuty(duty, focus);
            }
        }

        public override void LordToilTick()
        {
            if (waypoints.Count == 0 || Find.TickManager.TicksGame % CheckEvery != 0)
            {
                return;
            }
            IntVec3 focus = waypoints[Data.index % waypoints.Count];
            bool allNear = true;
            foreach (Pawn pawn in lord.ownedPawns)
            {
                if (pawn.Spawned && !pawn.Position.InHorDistOf(focus, NearRadius))
                {
                    allNear = false;
                    break;
                }
            }
            Data.sinceAdvance += CheckEvery;
            Data.waited = allNear ? Data.waited + CheckEvery : 0;
            if (Data.waited >= PauseTicks || Data.sinceAdvance >= StallTicks)
            {
                Data.index = (Data.index + 1) % waypoints.Count;
                Data.waited = 0;
                Data.sinceAdvance = 0;
                UpdateAllDuties();
            }
        }
    }

    // RUT_CathedralDescent_Patrol's only node: walk (never run) to the duty focus, idle when there.
    public class JobGiver_CathedralDescentPatrol : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            PawnDuty duty = pawn.mindState?.duty;
            if (duty == null || !duty.focus.IsValid)
            {
                return null;
            }
            IntVec3 focus = duty.focus.Cell;
            if (pawn.Position.InHorDistOf(focus, 3f) || !pawn.CanReach(focus, PathEndMode.ClosestTouch, Danger.Deadly))
            {
                Job wait = JobMaker.MakeJob(JobDefOf.Wait);
                wait.expiryInterval = 90 + pawn.thingIDNumber % 60;
                return wait;
            }
            Job go = JobMaker.MakeJob(JobDefOf.Goto, focus);
            go.locomotionUrgency = LocomotionUrgency.Walk;
            go.expiryInterval = 2500;
            go.checkOverrideOnExpire = true;
            return go;
        }
    }
}
