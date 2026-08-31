using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// Sleeps at night SPECIFICALLY, rather than when tired.
    ///
    /// RimWorld already does this for animals -- JobGiver_GetRest gives a
    /// non-humanlike pawn TimeAssignmentDefOf.Sleep outside 07:00-21:00 -- but a
    /// humanlike pawn with no timetable falls through to Anything, so a lorded
    /// NPC only ever sleeps once its rest need is genuinely low. A refinery crew
    /// that wanders the yard at 03:00 does not read as people who live there.
    ///
    /// This sits above the needs subtree in the resident duty, so it wins during
    /// the sleeping window and is silent the rest of the day.
    /// </summary>
    public class JobGiver_SleepAtNight : ThinkNode_JobGiver
    {
        /// <summary>Hour they turn in. Overridable per duty in XML.</summary>
        public int sleepStartHour = 22;

        /// <summary>Hour they get up.</summary>
        public int wakeHour = 6;

        /// <summary>
        /// Only consulted if this node is ever nested under a
        /// ThinkNode_PrioritySorter. The resident duty uses ThinkNode_Priority,
        /// which takes its subnodes in ORDER, so placement in the XML is what
        /// actually decides when this wins.
        /// </summary>
        private const float SleepPriority = 7f;

        public override ThinkNode DeepCopy(bool resolve = true)
        {
            JobGiver_SleepAtNight copy = (JobGiver_SleepAtNight)base.DeepCopy(resolve);
            copy.sleepStartHour = sleepStartHour;
            copy.wakeHour = wakeHour;
            return copy;
        }

        public override float GetPriority(Pawn pawn)
        {
            return ShouldTurnIn(pawn) ? SleepPriority : 0f;
        }

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!ShouldTurnIn(pawn))
            {
                return null;
            }

            // A bed if the place has one. RestUtility applies the ownership and
            // reachability rules for us; a cast that owns bedrolls uses them.
            Building_Bed bed = RestUtility.FindBedFor(pawn);
            if (bed != null)
            {
                return JobMaker.MakeJob(JobDefOf.LayDown, bed);
            }

            // Otherwise they lie down where they live. The duty's focus is the
            // barracks at this hour, set by LordToil_Inhabited.
            IntVec3 anchor = pawn.mindState.duty != null && pawn.mindState.duty.focus.IsValid
                ? pawn.mindState.duty.focus.Cell
                : pawn.Position;
            if (TryFindSleepSpot(pawn, anchor, out IntVec3 cell))
            {
                return JobMaker.MakeJob(JobDefOf.LayDown, cell);
            }
            return null;
        }

        private bool ShouldTurnIn(Pawn pawn)
        {
            if (pawn == null || pawn.Dead || pawn.needs == null || pawn.needs.rest == null)
            {
                return false;
            }
            if (!pawn.Awake())
            {
                return false;
            }
            if (!RestUtility.CanFallAsleep(pawn))
            {
                return false;
            }
            if (RestUtility.DisturbancePreventsLyingDown(pawn))
            {
                return false;
            }
            if (Find.TickManager.TicksGame < pawn.mindState.canSleepTick)
            {
                return false;
            }
            return InhabitedRoute.IsSleepingHour(GenLocalDate.HourOfDay(pawn), sleepStartHour, wakeHour);
        }

        private static bool TryFindSleepSpot(Pawn pawn, IntVec3 anchor, out IntVec3 cell)
        {
            Map map = pawn.Map;
            if (map == null)
            {
                cell = IntVec3.Invalid;
                return false;
            }
            if (IsValidCell(pawn, anchor))
            {
                cell = anchor;
                return true;
            }
            for (int i = 0; i < 2; i++)
            {
                int radius = (i == 0) ? 4 : 12;
                if (CellFinder.TryRandomClosewalkCellNear(anchor, map, radius, out IntVec3 result,
                        (IntVec3 c) => IsValidCell(pawn, c)))
                {
                    cell = result;
                    return true;
                }
            }
            cell = IntVec3.Invalid;
            return false;
        }

        private static bool IsValidCell(Pawn pawn, IntVec3 cell)
        {
            if (!cell.IsValid || !cell.InBounds(pawn.Map))
            {
                return false;
            }
            if (cell.IsForbidden(pawn) || cell.GetTerrain(pawn.Map).avoidWander)
            {
                return false;
            }
            return pawn.CanReserve(cell);
        }
    }
}
