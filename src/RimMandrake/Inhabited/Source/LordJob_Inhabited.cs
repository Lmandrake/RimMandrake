using Verse;
using Verse.AI.Group;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// The people who live here. Not a visitor arc, not a trade caravan: the
    /// default FATE is that nothing ends them.
    ///
    /// CreateGraph() returns exactly ONE toil and must keep returning exactly one
    /// forever. See LordToil_Inhabited for why -- the graph is serialised by
    /// positional index and re-created on load.
    /// </summary>
    public class LordJob_Inhabited : LordJob
    {
        private IntVec3 home;
        private IntVec3 work;
        private float homeRadius = 10f;
        private float workRadius = 14f;
        private int sleepStartHour = 22;
        private int wakeHour = 6;

        /// <summary>
        /// Scribe needs a parameterless ctor; it is never called by our own code.
        /// </summary>
        public LordJob_Inhabited()
        {
        }

        public LordJob_Inhabited(IntVec3 home, IntVec3 work, InhabitedPlaceDef place)
        {
            this.home = home;
            this.work = work;
            if (place != null)
            {
                homeRadius = place.homeRadius;
                workRadius = place.workRadius;
                sleepStartHour = place.sleepStartHour;
                wakeHour = place.wakeHour;
            }
        }

        public override StateGraph CreateGraph()
        {
            StateGraph graph = new StateGraph();
            graph.StartingToil = new LordToil_InhabitedRoutine(home, work, homeRadius, workRadius,
                sleepStartHour, wakeHour);
            return graph;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref home, "home");
            Scribe_Values.Look(ref work, "work");
            Scribe_Values.Look(ref homeRadius, "homeRadius", 10f);
            Scribe_Values.Look(ref workRadius, "workRadius", 14f);
            Scribe_Values.Look(ref sleepStartHour, "sleepStartHour", 22);
            Scribe_Values.Look(ref wakeHour, "wakeHour", 6);
        }
    }
}
