using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// TITAN_BREAKTHROUGH_CLEARING_1 (GPT review B3.4 / C3.5 / D3.2 / B1.3 / C1.3 / D1.3): a tiered titan whose path start is sealed
    /// (or much longer round than through) by something it may crush walks up to the first obstacle and strikes it, then resumes the
    /// job it had, which repaths. The decision is the Verse-free TitanClearing kernel; this class only gathers its inputs.
    ///
    /// Engine facts this rests on (decompiled 1.6):
    ///  - Pawn_PathFollower.StartPath calls PatherFailed when Reachability.CanReach(PassDoors) is false, before any step, so a
    ///    sealed lane never reaches the wake (the Thing.Position postfix). Patch_StartPath_TitanClearing intercepts exactly there.
    ///  - A PathFinder.FindPathNow with TraverseMode.PassAllDestroyableThings routes through destroyable FULL-fill edifices (walls)
    ///    at a cost for their hit points (PathGridJob.CostForCell); PawnPath.FirstBlockingBuilding names the first one, which is
    ///    how vanilla sappers and JobGiver_ExitMap(canDig) pick what to dig.
    ///  - That mode never passes a part-fill edifice: BuildingSource marks a cell as a building only for FillCategory.Full, so a
    ///    giant trunk (RM_HugeTrunkBlocker, fillPercent 0.4) stays impassable to it. The straight-line probe covers trunks.
    /// </summary>
    public static class TitanClearingUtility
    {
        private static readonly Dictionary<int, int> lastDetourCheck = new Dictionary<int, int>();
        private static readonly Dictionary<int, int> lastStart = new Dictionary<int, int>();
        private static readonly Dictionary<long, int> gaveUpUntil = new Dictionary<long, int>();

        /// <summary>Called from the StartPath prefix. True when a clearing job was started in place of the path.</summary>
        public static bool TryStartClearing(Pawn pawn, LocalTargetInfo dest, PathEndMode peMode)
        {
            if (!RM_HugeThingsSettings.TitanClearingActive) return false;
            if (pawn == null || !pawn.Spawned || pawn.Map == null || pawn.Dead || pawn.Downed || pawn.Flying) return false;
            if (!dest.IsValid || (dest.HasThing && dest.ThingDestroyed)) return false;
            Job cur = pawn.CurJob;
            if (cur == null || cur.def == RM_TitanicCreaturesDefOf.RM_TitanClearObstacle) return false;
            TitanicTier tier = TitanicTierUtility.GetTier(pawn);
            if (tier == TitanicTier.None) return false;
            Map map = pawn.Map;
            int now = Find.TickManager.TicksGame;
            int id = pawn.thingIDNumber;
            // One clearing start per titan per tick: a target that vanishes at once must not loop job starts within a tick.
            if (lastStart.TryGetValue(id, out int ls) && ls == now) return false;

            PathEndMode mode = peMode;
            LocalTargetInfo resolved = (LocalTargetInfo)GenPath.ResolvePathMode(pawn, dest.ToTargetInfo(map), ref mode);
            if (!resolved.IsValid) return false;
            bool reachable = map.reachability.CanReach(pawn.Position, resolved, mode, TraverseParms.For(TraverseMode.PassDoors));
            float byPawn = -1f;
            if (reachable)
            {
                // A stale value from an earlier game (last > now) never suppresses a check.
                if (lastDetourCheck.TryGetValue(id, out int last) && last <= now && now - last < TitanClearing.DetourCheckCooldownTicks)
                    return false;
                lastDetourCheck[id] = now;
                using (PawnPath walk = map.pathFinder.FindPathNow(pawn.Position, resolved, pawn, null, mode))
                {
                    if (!walk.Found) return false;
                    byPawn = walk.TotalCost;
                }
            }

            ClearKind breachKind = ClearKind.None;
            Thing breachThing = null;
            float breachCost = -1f;
            using (PawnPath through = map.pathFinder.FindPathNow(pawn.Position, resolved,
                       TraverseParms.For(pawn, Danger.Deadly, TraverseMode.PassAllDestroyableThings), null, mode))
            {
                if (through.Found)
                {
                    Thing blocker = through.FirstBlockingBuilding(out IntVec3 _, pawn);
                    if (blocker != null)
                    {
                        breachKind = Classify(pawn, tier, blocker);
                        breachThing = blocker;
                        breachCost = through.TotalCost;
                    }
                }
            }

            Thing probeThing = Probe(pawn, resolved.Cell, out ClearKind probeKind);
            IntVec3 d = resolved.Cell - pawn.Position;
            float probeCost = TitanClearing.StraightCost(d.x, d.z, pawn.TicksPerMoveCardinal);

            if (GaveUpOn(id, breachThing, now)) breachKind = ClearKind.None;
            if (GaveUpOn(id, probeThing, now)) probeKind = ClearKind.None;
            ClearSource pick = TitanClearing.Choose(reachable, byPawn, RM_HugeThingsSettings.titanClearingDetourFactor,
                breachKind, breachCost, probeKind, probeCost);
            Thing target = pick == ClearSource.Breach ? breachThing : (pick == ClearSource.Probe ? probeThing : null);
            if (target == null) return false;

            lastStart[id] = now;
            Job job = JobMaker.MakeJob(RM_TitanicCreaturesDefOf.RM_TitanClearObstacle, target);
            job.expiryInterval = TitanClearing.StrikeIntervalTicks * (TitanClearing.MaxStrikes + 10) + 2500;
            job.checkOverrideOnExpire = false;
            pawn.pather.StopDead();
            // The original job is suspended and resumed afterwards (JobDef.suspendable, true by default): it repaths, through the
            // gap. A non-suspendable job simply ends and the think tree picks the next one.
            pawn.jobs.StartJob(job, JobCondition.InterruptForced, null, resumeCurJobAfterwards: true);
            return true;
        }

        /// <summary>The first solid cell on the straight line to the destination, as an obstacle, or null at open ground's end.</summary>
        private static Thing Probe(Pawn pawn, IntVec3 to, out ClearKind kind)
        {
            kind = ClearKind.None;
            Map map = pawn.Map;
            IntVec3 from = pawn.Position;
            foreach (int[] xz in TitanClearing.LineCells(from.x, from.z, to.x, to.z, TitanClearing.ProbeMaxCells))
            {
                IntVec3 c = new IntVec3(xz[0], 0, xz[1]);
                if (!c.InBounds(map)) return null;
                Building ed = c.GetEdifice(map);
                if (ed != null && ed.BlocksPawn(pawn))
                {
                    kind = Classify(pawn, TitanicTierUtility.GetTier(pawn), ed);
                    return ed;
                }
                if (!c.Walkable(map))
                {
                    // A giant's solid root (a giant plant on its own cell) is the trunk route; anything else (rock without an
                    // edifice, deep water) ends the probe with nothing to clear.
                    List<Thing> things = c.GetThingList(map);
                    for (int i = 0; i < things.Count; i++)
                    {
                        if (things[i] is Plant p && p.TryGetComp<CompHugeFootprint>() != null)
                        {
                            kind = Classify(pawn, TitanicTierUtility.GetTier(pawn), p);
                            return p;
                        }
                    }
                    return null;
                }
            }
            return null;
        }

        /// <summary>Is this obstacle one this titan may strike right now, and by which route.</summary>
        public static ClearKind Classify(Pawn titan, TitanicTier tier, Thing t)
        {
            if (titan == null || t == null || t.Destroyed || !t.Spawned) return ClearKind.None;
            Plant giant = GiantOf(t);
            if (giant != null || t is Building_TrunkBlocker)
            {
                bool alive = giant != null && giant.Spawned && !giant.Destroyed;
                return TitanClearing.TrunkEligible((int)tier, RM_HugeThingsSettings.giantPlantSmashMinTier,
                    RM_HugeThingsSettings.GiantPlantSmashActive, alive, alive && IsQuestObject(giant)) ? ClearKind.Trunk : ClearKind.None;
            }
            if (!(t is Building b)) return ClearKind.None;
            bool natural = b.def.building != null && b.def.building.isNaturalRock;
            bool friendly = b.Faction != null && titan.Faction != null && (b.Faction == titan.Faction || !b.Faction.HostileTo(titan.Faction));
            return TitanClearing.BuildingEligible((int)tier, CrushTableUtility.IsCrushableAtTier(b, tier), b.def.destroyable, natural,
                IsQuestObject(b), friendly, false) ? ClearKind.Building : ClearKind.None;
        }

        /// <summary>The giant plant an obstacle stands for: a trunk cell's owner, or a giant plant itself.</summary>
        public static Plant GiantOf(Thing t)
        {
            if (t is Building_TrunkBlocker tb) return tb.owner;
            if (t is Plant p && p.TryGetComp<CompHugeFootprint>() != null) return p;
            return null;
        }

        private static bool IsQuestObject(Thing t) => t.questTags != null && t.questTags.Count > 0;

        /// <summary>
        /// One strike through the wake's crush rules. A giant takes the heavy blow through its own damage route
        /// (Building_TrunkBlocker.ForwardToPlant: the plant OWNER, never the blocker proxy); a building is destroyed outright at T3
        /// (RM_TitanicKernel.DestroysOutright) and takes crush damage below that. True if the strike landed.
        /// </summary>
        public static bool Strike(Pawn titan, TitanicTier tier, Thing obstacle)
        {
            float mult = RM_HugeThingsSettings.wakeCrushDamageMultiplier;
            Plant giant = GiantOf(obstacle);
            if (giant != null)
            {
                float dmg = GiantSmash.Damage(RM_TitanicKernel.CrushDamageHeavy, mult);
                return Building_TrunkBlocker.ForwardToPlant(giant, new DamageInfo(DamageDefOf.Crush, dmg, instigator: titan), false);
            }
            if (!(obstacle is Building b) || b.Destroyed || !b.Spawned) return false;
            if (RM_TitanicKernel.DestroysOutright((int)tier, true))
            {
                b.Destroy(DestroyMode.KillFinalize);
                return true;
            }
            b.TakeDamage(new DamageInfo(DamageDefOf.Crush, RM_TitanicKernel.CrushDamage((int)tier, mult), instigator: titan));
            return true;
        }

        /// <summary>Remember an obstacle a clearing job gave up on, so the resumed job does not pick it again at once.</summary>
        public static void NoteGaveUp(Pawn titan, Thing obstacle)
        {
            if (titan == null || obstacle == null) return;
            gaveUpUntil[Key(titan.thingIDNumber, obstacle.thingIDNumber)] = Find.TickManager.TicksGame + TitanClearing.GiveUpMemoTicks;
        }

        private static bool GaveUpOn(int titanId, Thing t, int now)
        {
            if (t == null) return false;
            if (!gaveUpUntil.TryGetValue(Key(titanId, t.thingIDNumber), out int until)) return false;
            return until > now && until - now <= TitanClearing.GiveUpMemoTicks;   // a stale value from another game never applies
        }

        private static long Key(int a, int b) => ((long)a << 32) ^ (uint)b;
    }
}
