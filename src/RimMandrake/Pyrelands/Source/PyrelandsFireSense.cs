using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// People on a Pyrelands map keep clear of fire. Vanilla's only fire sense for a person is the path finder's: a burning cell
    /// costs extra to cross (Fire.pathfinderDangerous). Idle wander (RCellFinder.CanWanderToCell) and a walk for joy
    /// (JoyGiver_GoForWalk) never look at fire, and nothing moves a person whose cell the fire is about to reach. Where a wildfire
    /// is an event that costs nothing; here a burn line of some 300 fires crosses the map every day. On map x (pass 20, run 5), a
    /// fresh colony left alone: an old colonist wandered out while ~300 fires burned, went down with 8 burns and died in the
    /// grass. So, on a Pyrelands map only: wander and walk destinations stay WanderClear cells from any fire, and a person
    /// (JobGiver_RM_StepAwayFromFire, in the humanlike constant tree) steps off when fire reaches their cell or a neighbour on
    /// their side of a wall, unless they are fighting it, carrying someone, drafted, or on the player's own order.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class PyrelandsFireSense
    {
        /// <summary>A wander or walk destination at least this far from every fire (grass fire here spreads a cell in seconds).</summary>
        public const float WanderClear = 6f;
        /// <summary>A step-away destination at least this far from every fire.</summary>
        public const float SafeClear = 3f;

        static PyrelandsFireSense()
        {
            var h = new Harmony("mandrake.rm.pyrelands.firesense");
            try
            {
                h.Patch(AccessTools.Method(typeof(RCellFinder), "CanWanderToCell"),
                    postfix: new HarmonyMethod(typeof(PyrelandsFireSense), nameof(Postfix_CanWanderToCell)));
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] fire sense: wander patch FAILED, idle colonists wander into the burn: " + e.Message);
            }
            try
            {
                h.Patch(AccessTools.Method(typeof(JoyGiver_GoForWalk), nameof(JoyGiver_GoForWalk.TryGiveJob)),
                    postfix: new HarmonyMethod(typeof(PyrelandsFireSense), nameof(Postfix_GoForWalk)));
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] fire sense: walk patch FAILED, a walk for joy can lead into the burn: " + e.Message);
            }
        }

        internal static bool Applies(Map map)
        {
            return map != null && PyrelandsMechanicsGate.On && map.Biome != null && map.Biome.defName == "RM_Pyrelands"
                && map.listerThings.ThingsOfDef(ThingDefOf.Fire).Count > 0;
        }

        public static bool FireWithin(Map map, IntVec3 c, float radius)
        {
            int n = GenRadial.NumCellsInRadius(radius);
            for (int i = 0; i < n; i++)
            {
                IntVec3 x = c + GenRadial.RadialPattern[i];
                if (x.InBounds(map) && x.ContainsStaticFire(map)) return true;
            }
            return false;
        }

        static void Postfix_CanWanderToCell(IntVec3 c, Pawn pawn, int tryIndex, ref bool __result)
        {
            // Vanilla relaxes its own soft rules (sunlight, pollution) after 20 tries; so does this, so a wander still finds a cell.
            if (!__result || tryIndex >= 20 || pawn == null || !pawn.RaceProps.Humanlike || !Applies(pawn.Map)) return;
            if (FireWithin(pawn.Map, c, WanderClear)) __result = false;
        }

        static void Postfix_GoForWalk(Pawn pawn, ref Job __result)
        {
            if (__result == null || pawn == null || !Applies(pawn.Map)) return;
            Map map = pawn.Map;
            if (FireWithin(map, __result.targetA.Cell, WanderClear))
            {
                __result = null;
                return;
            }
            if (__result.targetQueueA == null) return;
            foreach (LocalTargetInfo t in __result.targetQueueA)
            {
                if (FireWithin(map, t.Cell, WanderClear))
                {
                    __result = null;
                    return;
                }
            }
        }
    }

    /// <summary>
    /// In the humanlike constant tree, after vanilla's explosion flee (Patches/RM_PyreStepAwayFromFire.xml): a non-hostile person
    /// whose cell or neighbour is burning, on their side of any wall, jogs to a cell clear of fire (RM_PyreStepAwayFromFire, a
    /// goto). A downed person who can crawl crawls to a nearer one: on map x the colonist who died had crawled ten cells towards
    /// the base before the grass fire caught him lying still. Vanilla's gate above it
    /// (ThinkNode_ConditionalCanDoConstantThinkTreeJobNow) already skips the burning (ExtinguishSelf is theirs), the asleep, the
    /// drafted, the mentally broken and the downed who cannot crawl.
    /// </summary>
    public class JobGiver_RM_StepAwayFromFire : ThinkNode_JobGiver
    {
        private static readonly List<Thing> fires = new List<Thing>();

        protected override Job TryGiveJob(Pawn pawn)
        {
            Map map = pawn.Map;
            if (!pawn.RaceProps.Humanlike || pawn.Drafted || !PyrelandsFireSense.Applies(map)) return null;
            bool crawl = pawn.Downed;
            if (crawl && !pawn.health.CanCrawl) return null;
            if (pawn.Faction == null || pawn.HostileTo(Faction.OfPlayer)) return null;
            Job cur = pawn.CurJob;
            if (cur != null && (cur.def == PyrelandsMechanicsDefOf.RM_PyreStepAwayFromFire || cur.def == JobDefOf.Flee || cur.def == JobDefOf.BeatFire || cur.def == JobDefOf.ExtinguishSelf
                || cur.playerForced || cur.workGiverDef?.workType == WorkTypeDefOf.Firefighter)) return null;
            if (pawn.carryTracker?.CarriedThing is Pawn || PawnUtility.PlayerForcedJobNowOrSoon(pawn)) return null;

            IntVec3 p = pawn.Position;
            Room room = p.GetRoom(map);
            fires.Clear();
            for (int i = 0; i < 9; i++)
            {
                IntVec3 c = p + GenRadial.RadialPattern[i];
                if (!c.InBounds(map) || c.GetRoom(map) != room) continue;
                Fire f = c.GetFirstThing<Fire>(map);
                if (f != null) fires.Add(f);
            }
            if (fires.Count == 0) return null;
            if (!TryFindClearCell(pawn, fires, crawl, out IntVec3 dest)) return null;
            Job job = JobMaker.MakeJob(PyrelandsMechanicsDefOf.RM_PyreStepAwayFromFire, dest);
            job.locomotionUrgency = LocomotionUrgency.Jog;
            job.expiryInterval = 600;
            return job;
        }

        /// <summary>A reachable standing cell 6-10 cells off (2-4 for a crawler), on the side away from the fires (fanning out to the
        /// flanks), with no fire within SafeClear (1.5 for a crawler, who cannot outrun a grass fire and is safest on a cell that
        /// has already burned). Vanilla's tool-user flee search last.</summary>
        private static bool TryFindClearCell(Pawn pawn, List<Thing> near, bool crawl, out IntVec3 dest)
        {
            Map map = pawn.Map;
            IntVec3 p = pawn.Position;
            Vector3 away = Vector3.zero;
            foreach (Thing f in near) away += (p - f.Position).ToVector3();
            float baseAngle = away.sqrMagnitude < 0.01f ? Rand.Range(0f, 360f) : away.AngleFlat();
            float clear = crawl ? 1.5f : PyrelandsFireSense.SafeClear;
            for (int d = crawl ? 2 : 6; d <= (crawl ? 4 : 10); d += crawl ? 1 : 2)
            {
                foreach (float off in new[] { 0f, 30f, -30f, 60f, -60f, 90f, -90f })
                {
                    IntVec3 c = p + IntVec3.FromVector3(Vector3Utility.HorizontalVectorFromAngle(baseAngle + off) * d);
                    if (Clear(pawn, c, clear))
                    {
                        dest = c;
                        return true;
                    }
                }
            }
            if (crawl)
            {
                dest = IntVec3.Invalid;
                return false;
            }
            dest = CellFinderLoose.GetFleeDest(pawn, near, 10f);
            return dest.IsValid && dest != p && Clear(pawn, dest, clear);
        }

        private static bool Clear(Pawn pawn, IntVec3 c, float clear)
        {
            Map map = pawn.Map;
            return c.InBounds(map) && c.Standable(map) && !c.IsForbidden(pawn) && !PyrelandsFireSense.FireWithin(map, c, clear)
                && pawn.CanReach(c, PathEndMode.OnCell, Danger.Some);
        }
    }
}
