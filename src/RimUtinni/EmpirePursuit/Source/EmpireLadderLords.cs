/* EMPIRE_ESCALATION_LADDER_1 P2/P3 — the two rungs that are NOT a stand-up fight.
 * Probe (design §3 rung 1): wander toward the colony's edge and scan; leave on a completed
 * sighting (memo) or after a day. Spotter (rung 2): stage at range, never assault; leave when
 * the call completes, the spotter falls, or the call times out. The sighting/call
 * accumulators themselves live in MapComponent_EmpireSearch, which sends the memos. */
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RuthlessPursuingMechanoids
{
    public class LordToil_ImperialProbeScan : LordToil
    {
        private readonly IntVec3 focus;
        private readonly float radius;

        public LordToil_ImperialProbeScan(IntVec3 focus, float radius)
        {
            this.focus = focus;
            this.radius = radius;
        }

        public override bool AllowSatisfyLongNeeds => false;

        public override void UpdateAllDuties()
        {
            foreach (Pawn p in lord.ownedPawns)
            {
                p.mindState.duty = new PawnDuty(DutyDefOf.WanderClose, focus, radius);
            }
        }
    }

    public class LordJob_ImperialProbe : LordJob
    {
        public const string MemoDone = "RUT_ProbeDone";
        private IntVec3 scanFocus;
        private int scanTicks = 60000;

        public LordJob_ImperialProbe() { }

        public LordJob_ImperialProbe(IntVec3 scanFocus, int scanTicks)
        {
            this.scanFocus = scanFocus;
            this.scanTicks = scanTicks;
        }

        public override StateGraph CreateGraph()
        {
            StateGraph graph = new StateGraph();
            LordToil scan = new LordToil_ImperialProbeScan(scanFocus, 10f);
            graph.AddToil(scan);
            LordToil exit = new LordToil_ExitMap(LocomotionUrgency.Jog, canDig: false, interruptCurrentJob: true);
            graph.AddToil(exit);
            Transition leave = new Transition(scan, exit);
            leave.AddTrigger(new Trigger_Memo(MemoDone));
            leave.AddTrigger(new Trigger_TicksPassed(scanTicks));
            graph.AddTransition(leave);
            return graph;
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref scanFocus, "scanFocus");
            Scribe_Values.Look(ref scanTicks, "scanTicks", 60000);
        }
    }

    public class LordJob_ImperialSpotter : LordJob
    {
        public const string MemoDone = "RUT_SpotterDone";
        private IntVec3 stagingLoc;
        private int stageTicks = 90000;

        public LordJob_ImperialSpotter() { }

        public LordJob_ImperialSpotter(IntVec3 stagingLoc, int stageTicks)
        {
            this.stagingLoc = stagingLoc;
            this.stageTicks = stageTicks;
        }

        public override StateGraph CreateGraph()
        {
            StateGraph graph = new StateGraph();
            LordToil stage = new LordToil_Stage(stagingLoc);
            graph.AddToil(stage);
            LordToil exit = new LordToil_ExitMap(LocomotionUrgency.Jog, canDig: false, interruptCurrentJob: true);
            graph.AddToil(exit);
            Transition leave = new Transition(stage, exit);
            leave.AddTrigger(new Trigger_Memo(MemoDone));
            leave.AddTrigger(new Trigger_TicksPassed(stageTicks));
            graph.AddTransition(leave);
            return graph;
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref stagingLoc, "stagingLoc");
            Scribe_Values.Look(ref stageTicks, "stageTicks", 90000);
        }
    }
}
