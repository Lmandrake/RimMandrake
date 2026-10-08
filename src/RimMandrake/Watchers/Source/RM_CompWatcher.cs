using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Watchers
{
    public class RM_CompProperties_Watcher : CompProperties
    {
        public RM_CompProperties_Watcher()
        {
            compClass = typeof(RM_CompWatcher);
        }
    }

    /// <summary>
    /// WATCHER_CREATURES_MOD_1, design §3. Injected on every race carrying RM_WatcherExtension.
    /// Two jobs: the medium backstop (the RM_CompWaterLocked shape: found off its medium while
    /// idling, walk back; this also covers a wild spawn on a non-medium cell), and the orphan guard
    /// (a hidden hediff with no watch job holding it is removed: the hidden state can never outlive
    /// the job). If no medium cell is reachable it gives up and lives as a plain animal that never
    /// hides (it only ever hides on its medium), re-checking now and then.
    /// Tamed members obey the same lock (owner ruling Q3, 2026-10-03: a tamed piinnok always stays
    /// on deep sand: it lives in a pen with deep sand or heads back to it).
    /// </summary>
    public class RM_CompWatcher : ThingComp
    {
        private const int CheckInterval = RM_WatcherKernel.CheckInterval;
        private const int NoMediumRecheckTicks = RM_WatcherKernel.NoMediumRecheckTicks;

        public int boltUntilTick = -1;
        public int noMediumUntilTick = -1;
        private RM_WatcherExtension ext;

        public RM_WatcherExtension Ext => ext ?? (ext = parent.def.GetModExtension<RM_WatcherExtension>());

        public bool Bolting => Find.TickManager.TicksGame < boltUntilTick;

        public bool NoMediumReachable => Find.TickManager.TicksGame < noMediumUntilTick;

        // Idle jobs the backstop may interrupt. Fleeing, eating, sleeping, being led or carried are left alone.
        private static readonly HashSet<string> IdleJobs = new HashSet<string> { "Wait", "Wait_Wander", "GotoWander", "Goto", "Wait_MaintainPosture" };

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref boltUntilTick, "rmWatcherBoltUntil", -1);
            Scribe_Values.Look(ref noMediumUntilTick, "rmWatcherNoMediumUntil", -1);
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.IsHashIntervalTick(CheckInterval))
            {
                return;
            }
            var pawn = parent as Pawn;
            RM_WatcherExtension e = Ext;
            if (pawn == null || e == null || !pawn.Spawned || pawn.Dead)
            {
                return;
            }
            JobDef cur = pawn.CurJobDef;
            if (cur != RM_WatchersDefOf.RM_WatcherWatch && RM_WatcherUtility.IsHidden(pawn, e))
            {
                RM_WatcherSign none = null;
                RM_WatcherUtility.Emerge(pawn, e, ref none, false);
                RemoveStraySigns(pawn, e);
            }
            if (!RM_WatcherKernel.ShouldSeekMedium(RM_WatchersSettings.watchersEnabled, RM_WatchersSettings.stayOnMedium, e.HasMedium,
                    pawn.Downed, pawn.InMentalState, Bolting, NoMediumReachable, RM_WatcherUtility.OnMedium(pawn, e),
                    cur != null, cur != null && IdleJobs.Contains(cur.defName)))
            {
                return;
            }
            if (RM_WatcherUtility.TryFindMediumCell(pawn, e, out IntVec3 cell))
            {
                Job go = JobMaker.MakeJob(RM_WatchersDefOf.RM_WatcherRelocate, cell);
                go.locomotionUrgency = LocomotionUrgency.Walk;
                pawn.jobs.StartJob(go, JobCondition.InterruptForced);
            }
            else
            {
                noMediumUntilTick = Find.TickManager.TicksGame + NoMediumRecheckTicks;
            }
        }

        private static void RemoveStraySigns(Pawn pawn, RM_WatcherExtension e)
        {
            if (e.signDef == null)
            {
                return;
            }
            List<Thing> things = pawn.Map.listerThings.ThingsOfDef(e.signDef);
            for (int i = things.Count - 1; i >= 0; i--)
            {
                if (things[i] is RM_WatcherSign s && s.owner == pawn && !s.Destroyed)
                {
                    pawn.Map.designationManager.RemoveAllDesignationsOn(s);
                    s.Destroy();
                }
            }
        }

        public override string CompInspectStringExtra()
        {
            return Bolting ? "RM_Watchers_InspectBolting".Translate().ToString() : null;
        }
    }

    /// <summary>Gives every race carrying RM_WatcherExtension its RM_CompWatcher (the
    /// RM_SandSwimStartup pattern), so a member writes one extension and nothing else.</summary>
    [StaticConstructorOnStartup]
    public static class RM_WatcherStartup
    {
        static RM_WatcherStartup()
        {
            foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (def.race == null || !def.HasModExtension<RM_WatcherExtension>())
                {
                    continue;
                }
                if (def.comps == null)
                {
                    def.comps = new List<CompProperties>();
                }
                if (!def.comps.Exists(c => c is RM_CompProperties_Watcher))
                {
                    def.comps.Add(new RM_CompProperties_Watcher());
                }
                AuditMedium(def, def.GetModExtension<RM_WatcherExtension>());
            }
        }

        /// <summary>The water half of the medium lock (owner ruling 2026-10-08: media are ground AND water). A water medium works on
        /// the kit as built (the sign is Ethereal, so it spawns on any terrain; relocation and wander only need Standable cells) as long
        /// as the terrain is passable, the race is waterSeeker where the terrain is avoidWander, and no swimming sprite hides the peek.</summary>
        private static void AuditMedium(ThingDef race, RM_WatcherExtension ext)
        {
            if (ext == null || !ext.HasMedium)
            {
                return;
            }
            bool impassable = false, avoidWander = false, water = false;
            foreach (TerrainDef t in ext.mediumTerrains)
            {
                if (t == null)
                {
                    continue;
                }
                impassable |= t.passability == Traversability.Impassable;
                avoidWander |= t.avoidWander;
                water |= t.IsWater;
            }
            bool swimSprite = false;
            foreach (PawnKindDef k in DefDatabase<PawnKindDef>.AllDefsListForReading)
            {
                if (k.race != race || k.lifeStages == null)
                {
                    continue;
                }
                foreach (PawnKindLifeStage ls in k.lifeStages)
                {
                    swimSprite |= ls?.swimmingGraphicData != null;
                }
            }
            var errors = new List<string>();
            var warnings = new List<string>();
            RM_WatcherKernel.MediumAudit(impassable, avoidWander, water, race.race.waterSeeker, swimSprite, errors, warnings);
            foreach (string e in errors)
            {
                Log.Error("[Watchers] " + race.defName + ": " + e);
            }
            foreach (string w in warnings)
            {
                Log.Warning("[Watchers] " + race.defName + ": " + w);
            }
        }
    }
}
