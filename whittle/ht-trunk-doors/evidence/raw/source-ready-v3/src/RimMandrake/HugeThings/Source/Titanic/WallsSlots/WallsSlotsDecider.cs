using System.Collections.Generic;
using Verse;
using Verse.AI;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// BIG_CREATURES_DESIGN_WALLS_AND_SLOTS phase 1: the decision at a big creature's path start, replacing the tier-gated
    /// clearing decision while the walls-and-slots rule is on (TitanClearingUtility.TryStartClearing calls here first).
    ///
    /// Order (§5): a squeeze breaks nothing, so it is tried first (calm or not); then the breach: the first crossing along a
    /// PassAllDestroyableThings path (or the straight line when the breach search finds no path), judged whole by the kernel
    /// (hold / break through / smash / forbidden). A crossing it holds at is remembered and closed to its own path requests, and
    /// the breach search is run again for another crossing (at most MaxBreachTries), so the creature never keeps choosing an
    /// impossible shortcut (§6 "route, execution and breach must agree"). Whether it may break at all is the temperament gate
    /// (WallsSlots.MayBreak): calm creatures break nothing to reach an unreachable goal and only past the x6 cap otherwise.
    /// Giant trunks keep the tier-gated smash route: a crossing that meets one is left to the legacy decision.
    /// </summary>
    public static class WallsSlotsDecider
    {
        private const int MaxBreachTries = 3;
        private const int HeldSayTicks = 2500;

        private static readonly Dictionary<int, int> lastDetourCheck = new Dictionary<int, int>();
        /// <summary>HUGE_WALLS_FIX_DECIDER_RETRIES_FOREVER: a destination found unreachable and not opened is not decided again for a cooldown.</summary>
        private static readonly UnreachableMemo unreachable = new UnreachableMemo();
        private static int lastDetourPrune = int.MinValue;

        private static long DestKey(Map map, LocalTargetInfo t, PathEndMode mode)
            => ((long)map.uniqueID << 48) ^ ((long)t.Cell.x << 28) ^ ((long)t.Cell.z << 8) ^ (long)mode;

        private static bool Fail(bool reachable, int id, long key, int now)
        {
            if (!reachable) unreachable.Note(id, key, now);
            return false;
        }

        private static void PruneDetourMemo(int now)
        {
            bool back = now < lastDetourPrune;
            if (!back && lastDetourPrune != int.MinValue && now - lastDetourPrune < 2500) return;
            lastDetourPrune = now;
            if (back) { lastDetourCheck.Clear(); return; }
            List<int> old = null;
            foreach (KeyValuePair<int, int> kv in lastDetourCheck)
                if (now - kv.Value > TitanClearing.DetourCheckCooldownTicks || kv.Value > now) (old ?? (old = new List<int>())).Add(kv.Key);
            if (old != null) foreach (int k in old) lastDetourCheck.Remove(k);
            unreachable.Prune(now);
        }

        /// <summary>Main thread (the despawn prefix): these creatures' held crossings just lost a wall, so their goals are open to a
        /// fresh decision now, not after the unreachable cooldown.</summary>
        internal static void ForgetUnreachable(List<int> creatures)
        {
            foreach (int id in creatures) unreachable.Forget(id);
        }

        /// <summary>Null: no decision here, let the legacy clearing run (giant trunks). True/false: a job was started / not.</summary>
        public static bool? TryStart(Pawn pawn, LocalTargetInfo resolved, PathEndMode mode)
        {
            Map map = pawn.Map;
            int now = Find.TickManager.TicksGame;
            int id = pawn.thingIDNumber;
            if (WallsSlotsUtility.Breadth(pawn) <= 1) return null;
            unreachable.Sync(now);
            PruneDetourMemo(now);
            WallsSlotsUtility.PruneMemos(now);
            long key = DestKey(map, resolved, mode);
            if (unreachable.Blocked(id, key, now)) return false;

            bool reachable = map.reachability.CanReach(pawn.Position, resolved, mode, TraverseParms.For(pawn, Danger.Deadly, TraverseMode.ByPawn));
            float byPawn = -1f;
            if (reachable)
            {
                if (lastDetourCheck.TryGetValue(id, out int last) && last <= now && now - last < TitanClearing.DetourCheckCooldownTicks)
                    return false;
                lastDetourCheck[id] = now;
                using (PawnPath walk = map.pathFinder.FindPathNow(pawn.Position, resolved, pawn, null, mode))
                {
                    if (walk.Found) byPawn = walk.TotalCost;
                    else reachable = false;   // reachability and the body's own search disagree: treat as sealed
                }
            }
            bool full = WallsSlotsUtility.FullRule(pawn);
            float factor = RM_HugeThingsSettings.titanClearingDetourFactor;

            // 1. squeeze: breaks nothing
            if (RM_HugeThingsSettings.SqueezeActive)
            {
                TraverseMode doors = pawn.Faction != null ? TraverseMode.PassDoors : TraverseMode.NoPassClosedDoors;
                using (PawnPath body = map.pathFinder.FindPathNow(pawn.Position, resolved, TraverseParms.For(doors), null, mode))
                {
                    if (body.Found)
                    {
                        WallsSlotsUtility.SqueezePlan plan = WallsSlotsUtility.PlanSqueeze(pawn, WallsSlotsUtility.RouteOf(body));
                        if (plan != null)
                        {
                            float cost = body.TotalCost + plan.ticks;
                            if (TitanClearing.Worth(reachable, byPawn, cost, factor))
                            {
                                Job sq = JobMaker.MakeJob(RM_TitanicCreaturesDefOf.RM_TitanSqueeze, plan.cells[0]);
                                sq.targetQueueA = new List<LocalTargetInfo>();
                                foreach (IntVec3 c in plan.cells) sq.targetQueueA.Add(c);
                                sq.countQueue = new List<int>(plan.slots);
                                sq.expiryInterval = (int)(plan.ticks * 3f) + 2500;
                                sq.checkOverrideOnExpire = false;
                                Begin(pawn, sq);
                                return true;
                            }
                        }
                    }
                }
            }

            // 2. the breach
            for (int attempt = 0; attempt < MaxBreachTries; attempt++)
            {
                List<IntVec3> route = null;
                float throughCost = -1f;
                using (PawnPath through = map.pathFinder.FindPathNow(pawn.Position, resolved,
                           TraverseParms.For(pawn, Danger.Deadly, TraverseMode.PassAllDestroyableThings), null, mode))
                {
                    if (through.Found)
                    {
                        route = WallsSlotsUtility.RouteOf(through);
                        throughCost = through.TotalCost;
                    }
                }
                if (route == null)
                {
                    route = WallsSlotsUtility.LineRoute(pawn.Position, resolved.Cell);
                    IntVec3 d = resolved.Cell - pawn.Position;
                    throughCost = TitanClearing.StraightCost(d.x, d.z, pawn.TicksPerMoveCardinal);
                }
                WallsSlotsUtility.Crossing cr = WallsSlotsUtility.Probe(pawn, route);
                if (cr == null) return Fail(reachable, id, key, now);
                if (cr.trunk && cr.cells.Count == 0) return null;   // a giant's trunk: the legacy smash route decides
                if (WallsSlots.Breaks(cr.verdict))
                {
                    if (!WallsSlots.MayBreak(full, reachable, byPawn, throughCost, factor)) return Fail(reachable, id, key, now);
                    if (cr.walls.Count == 0) return Fail(reachable, id, key, now);
                    Thing first = NearestWall(pawn, cr);
                    if (TitanClearingUtility.GaveUpOnThing(id, first, now)) return Fail(reachable, id, key, now);
                    Job job = JobMaker.MakeJob(RM_TitanicCreaturesDefOf.RM_TitanClearObstacle, first);
                    job.count = (int)cr.verdict;
                    job.targetQueueA = new List<LocalTargetInfo>();
                    job.countQueue = new List<int>();
                    for (int i = 0; i < cr.walls.Count; i++)
                    {
                        job.targetQueueA.Add(cr.walls[i]);
                        job.countQueue.Add(cr.layer[i] * 2 + (cr.roofed[i] ? 1 : 0));
                    }
                    int layers = 1;
                    foreach (int l in cr.layer) if (l + 1 > layers) layers = l + 1;
                    job.expiryInterval = WallsSlots.SmashIntervalTicks * (WallsSlots.MaxBlowsPerLayer * layers + 10) + 2500;
                    job.checkOverrideOnExpire = false;
                    Begin(pawn, job);
                    return true;
                }
                if (cr.verdict == CrossVerdict.Hold || cr.verdict == CrossVerdict.Forbidden)
                {
                    WallsSlotsUtility.Say(pawn, "RM_WallsSlots_Held".Translate(cr.thickness), HeldSayTicks);
                    if (cr.cells.Count == 0) return Fail(reachable, id, key, now);   // nothing of ours to close: rock or protected only
                    WallsSlotsUtility.NoteHeld(pawn, cr.cells);
                    continue;   // the breach search now routes round the held crossing
                }
                return Fail(reachable, id, key, now);
            }
            return Fail(reachable, id, key, now);
        }

        private static Thing NearestWall(Pawn pawn, WallsSlotsUtility.Crossing cr)
        {
            Thing best = cr.walls[0];
            int bestLayer = int.MaxValue;
            float bestD = float.MaxValue;
            for (int i = 0; i < cr.walls.Count; i++)
            {
                float d = (cr.walls[i].Position - pawn.Position).LengthHorizontalSquared;
                if (cr.layer[i] < bestLayer || (cr.layer[i] == bestLayer && d < bestD))
                {
                    bestLayer = cr.layer[i];
                    bestD = d;
                    best = cr.walls[i];
                }
            }
            return best;
        }

        private static void Begin(Pawn pawn, Job job)
        {
            TitanClearingUtility.NoteStarted(pawn);
            pawn.pather.StopDead();
            pawn.jobs.StartJob(job, JobCondition.InterruptForced, null, resumeCurJobAfterwards: true);
        }
    }
}
