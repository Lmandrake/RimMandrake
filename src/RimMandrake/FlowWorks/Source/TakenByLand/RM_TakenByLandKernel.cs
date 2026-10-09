using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.TakenByLand
{
    public enum TakenOutcome { LostMissing, LostDead, SpawnAlive, SpawnThenKill }

    /// <summary>
    /// TAKEN_BY_LAND_SERVICE_1 (X-10). Verse-free decisions of the one hold-and-return service (the river's swept-away and the
    /// dune gale's carry were the same mechanism built twice). Also compiled by the FlowWorks SelfTest.
    /// </summary>
    public static class RM_TakenByLandKernel
    {
        /// <summary>The book is scanned only when it holds something, and then only on every <paramref name="interval"/>th tick.</summary>
        public static bool ShouldScan(int count, int now, int interval) => !(count == 0 || interval <= 0 || now % interval != 0);

        public static bool IsDue(int returnTick, int now) => returnTick <= now;

        /// <summary>Tick a taken pawn is due back: <paramref name="days"/> from now, never earlier than the next tick.</summary>
        public static int ReturnTick(int now, float days, int ticksPerDay)
        {
            if (float.IsNaN(days) || days < 0f) days = 0f;
            double t = now + (double)days * ticksPerDay;
            return t >= int.MaxValue ? int.MaxValue : Math.Max(now + 1, (int)t);
        }

        public static TakenOutcome Decide(bool pawnMissing, bool mapMissing, bool dead, bool aliveRoll)
        {
            if (pawnMissing || mapMissing) return TakenOutcome.LostMissing;
            if (dead) return TakenOutcome.LostDead;
            return aliveRoll ? TakenOutcome.SpawnAlive : TakenOutcome.SpawnThenKill;
        }

        /// <summary>Remove and return (last to first) every record the predicate selects.</summary>
        public static List<T> TakeWhere<T>(IList<T> book, Func<T, bool> pick)
        {
            var taken = new List<T>();
            for (int i = book.Count - 1; i >= 0; i--)
            {
                if (pick(book[i]))
                {
                    taken.Add(book[i]);
                    book.RemoveAt(i);
                }
            }
            return taken;
        }

        /// <summary>Is a record a "storm's end" return: taken from this map by an EARLIER event than the one that just ended?</summary>
        public static bool EarlierEventOnMap(int recordMapId, int recordTakenTick, int mapId, int eventStartTick) =>
            recordMapId == mapId && recordTakenTick < eventStartTick;
    }
}
