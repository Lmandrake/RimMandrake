using System;
using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Watchers
{
    /// <summary>
    /// WATCHER_CREATURES_MOD_1. The shared queries and the two state changes (hide, emerge), so the
    /// job, the comp and the flush all ask and do the identical thing.
    /// </summary>
    public static class RM_WatcherUtility
    {
        public static float FlinchRadius(RM_WatcherExtension ext)
        {
            return ext.flinchRadius * RM_WatchersSettings.flinchRadiusScale;
        }

        /// <summary>Nearest spawned pawn that is not its own kind within the watch radius, and
        /// whether any such pawn is inside the flinch radius. "Its own kind" = same race def.</summary>
        public static Pawn NearestOther(Pawn watcher, RM_WatcherExtension ext, out bool inFlinch)
        {
            inFlinch = false;
            Map map = watcher.Map;
            if (map == null)
            {
                return null;
            }
            float watchSq = ext.watchRadius * ext.watchRadius;
            float flinch = FlinchRadius(ext);
            float flinchSq = flinch * flinch;
            Pawn best = null;
            float bestSq = float.MaxValue;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == watcher || p.def == watcher.def)
                {
                    continue;
                }
                float d = (p.Position - watcher.Position).LengthHorizontalSquared;
                if (d > watchSq)
                {
                    continue;
                }
                if (d <= flinchSq)
                {
                    inFlinch = true;
                }
                if (d < bestSq)
                {
                    bestSq = d;
                    best = p;
                }
            }
            return best;
        }

        // CreatureBehaviors' RM_SandSwimUtility.SubmergedSwimmersNear(Map, IntVec3, float, float, List<Pawn>)
        // (src/RimMandrake/CreatureBehaviors/Source/RM_CompSandSwim.cs, "§8, the piinnok hook"), bound by
        // reflection: that assembly ships inside mandrake.rm.biomes and this mod is standalone.
        private static bool geophoneResolved;
        private static Func<Map, IntVec3, float, float, List<Pawn>, int> geophoneQuery;

        public static bool GeophoneAvailable
        {
            get
            {
                ResolveGeophone();
                return geophoneQuery != null;
            }
        }

        private static void ResolveGeophone()
        {
            if (geophoneResolved)
            {
                return;
            }
            geophoneResolved = true;
            Type t = GenTypes.GetTypeInAnyAssembly("RimMandrake.CreatureBehaviors.RM_SandSwimUtility");
            MethodInfo m = t?.GetMethod("SubmergedSwimmersNear", BindingFlags.Public | BindingFlags.Static, null,
                new[] { typeof(Map), typeof(IntVec3), typeof(float), typeof(float), typeof(List<Pawn>) }, null);
            if (m != null && m.ReturnType == typeof(int))
            {
                geophoneQuery = (Func<Map, IntVec3, float, float, List<Pawn>, int>)
                    Delegate.CreateDelegate(typeof(Func<Map, IntVec3, float, float, List<Pawn>, int>), m);
            }
        }

        public static bool GeophoneFires(Pawn watcher, RM_WatcherExtension ext)
        {
            if (!RM_WatchersSettings.geophone || ext.geophoneMinBodySize <= 0f || watcher.Map == null)
            {
                return false;
            }
            ResolveGeophone();
            return geophoneQuery != null
                && geophoneQuery(watcher.Map, watcher.Position, ext.watchRadius, ext.geophoneMinBodySize, null) > 0;
        }

        public static bool OnMedium(Pawn p, RM_WatcherExtension ext)
        {
            return p.Map != null && ext.IsMedium(p.Position.GetTerrain(p.Map));
        }

        public static bool IsHidden(Pawn p, RM_WatcherExtension ext)
        {
            return ext.hiddenHediff != null && p.health?.hediffSet != null && p.health.hediffSet.HasHediff(ext.hiddenHediff);
        }

        /// <summary>Go under: hediff on, sign on the cell, a puff. Returns the sign.</summary>
        public static RM_WatcherSign Hide(Pawn p, RM_WatcherExtension ext)
        {
            Map map = p.Map;
            if (map == null)
            {
                return null;
            }
            if (!IsHidden(p, ext))
            {
                p.health.AddHediff(HediffMaker.MakeHediff(ext.hiddenHediff, p));
            }
            FleckMaker.ThrowDustPuff(p.Position, map, ext.puffScale);
            var sign = (RM_WatcherSign)ThingMaker.MakeThing(ext.signDef);
            sign.owner = p;
            GenSpawn.Spawn(sign, p.Position, map);
            return sign;
        }

        /// <summary>Come up (or clean up on any job exit): hediff off, sign gone with any order on it.</summary>
        public static void Emerge(Pawn p, RM_WatcherExtension ext, ref RM_WatcherSign sign, bool puff)
        {
            if (ext?.hiddenHediff != null && p?.health?.hediffSet != null)
            {
                Hediff h = p.health.hediffSet.GetFirstHediffOfDef(ext.hiddenHediff);
                if (h != null)
                {
                    p.health.RemoveHediff(h);
                }
            }
            if (sign != null && !sign.Destroyed)
            {
                sign.MapHeld?.designationManager.RemoveAllDesignationsOn(sign);
                sign.Destroy();
            }
            sign = null;
            if (puff && p != null && p.Spawned)
            {
                FleckMaker.ThrowDustPuff(p.Position, p.Map, ext.puffScale);
            }
        }

        public static int ActiveWatchers(Map map)
        {
            int n = 0;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                if (pawns[i].CurJobDef == RM_WatchersDefOf.RM_WatcherWatch)
                {
                    n++;
                }
            }
            return n;
        }

        /// <summary>Nearest reachable standable medium cell within 40 (the radial pattern's reach).</summary>
        public static bool TryFindMediumCell(Pawn p, RM_WatcherExtension ext, out IntVec3 cell)
        {
            cell = IntVec3.Invalid;
            Map map = p.Map;
            if (map == null || !ext.HasMedium)
            {
                return false;
            }
            int reachFailures = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(p.Position, 40f, false))
            {
                if (!c.InBounds(map) || !ext.IsMedium(c.GetTerrain(map)) || !c.Standable(map))
                {
                    continue;
                }
                if (p.CanReach(c, PathEndMode.OnCell, Danger.Some))
                {
                    cell = c;
                    return true;
                }
                if (++reachFailures > 30)
                {
                    return false;
                }
            }
            return false;
        }

        /// <summary>Q4 (ruled 2026-10-03, flush only): the flusher reached the sign. The watcher comes
        /// up and bolts; while it bolts it cannot hide and can be hunted.</summary>
        public static void Flush(Pawn watcher, Pawn flusher)
        {
            if (watcher == null || !watcher.Spawned || watcher.Dead)
            {
                return;
            }
            RM_CompWatcher comp = watcher.GetComp<RM_CompWatcher>();
            RM_WatcherExtension ext = comp?.Ext;
            if (ext == null)
            {
                return;
            }
            comp.boltUntilTick = Find.TickManager.TicksGame + ext.boltTicks;
            // Starting the flee ends the watch job, whose finish action removes the hediff and the sign.
            IntVec3 dest = CellFinderLoose.GetFleeDest(watcher, new List<Thing> { flusher }, 16f);
            Job flee = JobMaker.MakeJob(JobDefOf.Flee, dest, flusher);
            flee.locomotionUrgency = LocomotionUrgency.Sprint;
            watcher.jobs.StartJob(flee, JobCondition.InterruptForced);
            if (IsHidden(watcher, ext))
            {
                RM_WatcherSign none = null;
                Emerge(watcher, ext, ref none, true);
            }
            Map map = watcher.Map;
            // Designator_Hunt's own faction rule (RimSage 1.6): never mark a tamed or humanlike-faction animal.
            if (RM_WatchersSettings.flushMarksHunt && flusher.Faction == Faction.OfPlayer
                && (watcher.Faction == null || !watcher.Faction.def.humanlikeFaction)
                && map.designationManager.DesignationOn(watcher, DesignationDefOf.Hunt) == null)
            {
                map.designationManager.AddDesignation(new Designation(watcher, DesignationDefOf.Hunt));
            }
            Messages.Message("RM_Watchers_Bolts".Translate(watcher.LabelShort), watcher, MessageTypeDefOf.NeutralEvent, false);
        }
    }
}
