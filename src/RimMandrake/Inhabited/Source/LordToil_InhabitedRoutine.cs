using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.Inhabited
{
    /// <summary>Where the cast should be right now.</summary>
    public class LordToil_InhabitedRoutine : LordToil
    {
        /// <summary>How often the stance is re-read. Roughly every ten seconds of
        /// game time -- an hour boundary is never missed and nothing is recomputed
        /// 60 times a second.</summary>
        private const int ReassessIntervalTicks = 600;

        private readonly IntVec3 home;
        private readonly IntVec3 work;
        private readonly float homeRadius;
        private readonly float workRadius;
        private readonly int sleepStartHour;
        private readonly int wakeHour;

        /// <summary>
        /// Deliberately NOT serialised. On load CreateGraph() rebuilds this toil
        /// and the field returns to its default, so the first reassess after load
        /// always reassigns. Self-healing, and it keeps LordToilData -- which IS
        /// index-serialised -- out of this class entirely.
        /// </summary>
        private RouteStance lastStance = (RouteStance)(-1);

        public override IntVec3 FlagLoc => home;

        public LordToil_InhabitedRoutine(IntVec3 home, IntVec3 work, float homeRadius, float workRadius,
            int sleepStartHour, int wakeHour)
        {
            this.home = home;
            this.work = work;
            this.homeRadius = homeRadius;
            this.workRadius = workRadius;
            this.sleepStartHour = sleepStartHour;
            this.wakeHour = wakeHour;
        }

        public override void UpdateAllDuties()
        {
            RouteStance stance = CurrentStance();
            lastStance = stance;
            for (int i = 0; i < lord.ownedPawns.Count; i++)
            {
                AssignDuty(lord.ownedPawns[i], stance);
            }
        }

        public override void LordToilTick()
        {
            base.LordToilTick();
            if (Find.TickManager.TicksGame % ReassessIntervalTicks != 0)
            {
                return;
            }
            RouteStance stance = CurrentStance();
            if (stance == lastStance)
            {
                return;
            }
            UpdateAllDuties();
        }

        private void AssignDuty(Pawn pawn, RouteStance stance)
        {
            if (pawn == null || pawn.Dead)
            {
                return;
            }
            switch (stance)
            {
                case RouteStance.Defending:
                    // Wherever they stand. A cast under fire does not walk to the
                    // barracks because the clock says so.
                    pawn.mindState.duty = new PawnDuty(InhabitedDefOf.Inhabited_Resident, pawn.Position, 0f);
                    pawn.mindState.duty.radius = workRadius;
                    break;
                case RouteStance.AtRest:
                    pawn.mindState.duty = new PawnDuty(InhabitedDefOf.Inhabited_Resident, home, 0f);
                    pawn.mindState.duty.radius = homeRadius;
                    break;
                default:
                    pawn.mindState.duty = new PawnDuty(InhabitedDefOf.Inhabited_Resident, work, 0f);
                    pawn.mindState.duty.radius = workRadius;
                    break;
            }
        }

        private RouteStance CurrentStance()
        {
            return InhabitedFateKernel.Stance(lord != null, Find.TickManager.TicksGame,
                lord != null ? lord.lastPawnHarmTick : 0,
                InhabitedRoute.IsSleepingHour(GenLocalDate.HourOfDay(Map), sleepStartHour, wakeHour));
        }
    }

    public static class InhabitedRoute
    {
        public static bool IsSleepingHour(int hour, int sleepStartHour, int wakeHour)
        {
            return InhabitedFateKernel.IsSleepingHour(hour, sleepStartHour, wakeHour);
        }
    }
}
