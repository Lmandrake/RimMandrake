using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // LEANINGSCRUB_GPT_ENRICHMENT_1 part 1 — venomvine as distinct rooms.
    //
    // Two of the five forms owed new behaviour here (the twitcher lash is
    // RM_TwitcherLash.cs, the hollow stand's small-body galleries are the
    // EnvironmentalHazards body-size barrier with a wider free band, and the
    // base thicket's man-high wall is that same barrier):
    //
    //   Dripping stand  a TIMED harvest: taking the amber venom no longer
    //                   kills the stand, it drops back to a set growth and
    //                   beads again. Vanilla mechanism, read from the
    //                   decompiled 1.6 Plant.PlantCollected: a plant whose
    //                   def.plant.harvestAfterGrowth > 0 is reset to that
    //                   growth instead of destroyed (PlantProperties.
    //                   HarvestDestroys => harvestAfterGrowth <= 0). The value
    //                   lives on RM_RegrowingHarvestExtension and is applied
    //                   to the def at startup only while the Mod Setting is on,
    //                   so switching it off restores the one-shot harvest.
    //
    //   Crown stand     draws dustflutter clouds during the Stall. A
    //                   MapComponent (plants only TickLong) sends idle wild
    //                   mobbers within range flying to the crown while the
    //                   map's weather is RM_Stall; once there, the Stall
    //                   freeze (RM_WindCalendar) holds them in place, which IS
    //                   the cloud. When the wind returns they wander off.
    // ════════════════════════════════════════════════════════════════════

    public class RM_RegrowingHarvestExtension : DefModExtension
    {
        // Growth the plant drops back to after a harvest. 0 = harvest destroys.
        public float harvestAfterGrowth;
    }

    [StaticConstructorOnStartup]
    public static class RM_RegrowingHarvest
    {
        static RM_RegrowingHarvest()
        {
            Apply();
        }

        // Called at startup and whenever the Mod Settings are written.
        public static void Apply()
        {
            if (DefDatabase<ThingDef>.AllDefsListForReading.NullOrEmpty())
            {
                return;
            }
            bool on = RM_WindCalendar.On(RM_LeaningScrubSettings.drippingRegrowEnabled);
            foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (def.plant == null)
                {
                    continue;
                }
                RM_RegrowingHarvestExtension ext = def.GetModExtension<RM_RegrowingHarvestExtension>();
                if (ext != null)
                {
                    def.plant.harvestAfterGrowth = on ? ext.harvestAfterGrowth : 0f;
                }
            }
        }
    }

    public class RM_StallMobExtension : DefModExtension
    {
        // The animal race drawn to this plant while the Stall holds.
        public ThingDef mobber;
        // How far away a mobber may be to answer the draw (cells).
        public float drawRadius = 40f;
        // Mobbers settle within this many cells of the stand.
        public float settleRadius = 3f;
        // Most mobbers one stand will hold at once.
        public int maxMobbers = 30;
    }

    public class RM_MapComponent_CrownMob : MapComponent
    {
        // TUNED: every 250 ticks (~4 s) is often enough that a cloud gathers
        // within the first in-game hour of a Stall, and the sweep is a lister
        // read plus one distance test per spawned pawn.
        private const int MobInterval = 250;

        private readonly List<Thing> tmpStands = new List<Thing>();
        private readonly List<Pawn> tmpPawns = new List<Pawn>();

        public RM_MapComponent_CrownMob(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % MobInterval != 0
                || !RM_WindCalendar.On(RM_LeaningScrubSettings.crownMobEnabled)
                || !RM_WindCalendar.IsStall(map))
            {
                return;
            }
            tmpStands.Clear();
            foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.Plant))
            {
                if (t.def.HasModExtension<RM_StallMobExtension>())
                {
                    tmpStands.Add(t);
                }
            }
            if (tmpStands.Count == 0)
            {
                return;
            }
            tmpPawns.Clear();
            tmpPawns.AddRange(map.mapPawns.AllPawnsSpawned);
            for (int s = 0; s < tmpStands.Count; s++)
            {
                Thing stand = tmpStands[s];
                RM_StallMobExtension ext = stand.def.GetModExtension<RM_StallMobExtension>();
                if (ext.mobber == null)
                {
                    continue;
                }
                int held = 0;
                float drawSq = ext.drawRadius * ext.drawRadius;
                float settleSq = (ext.settleRadius + 1f) * (ext.settleRadius + 1f);
                for (int i = 0; i < tmpPawns.Count && held < ext.maxMobbers; i++)
                {
                    Pawn p = tmpPawns[i];
                    if (p.def != ext.mobber || !p.Spawned || p.Dead || p.Downed || p.Faction != null)
                    {
                        continue;
                    }
                    float distSq = (p.Position - stand.Position).LengthHorizontalSquared;
                    if (distSq <= settleSq)
                    {
                        held++;
                        continue;
                    }
                    if (distSq > drawSq || !IsIdle(p) || HeadingTo(p, stand, settleSq))
                    {
                        continue;
                    }
                    if (TrySendToStand(p, stand, ext))
                    {
                        held++;
                    }
                }
            }
            tmpStands.Clear();
            tmpPawns.Clear();
        }

        private static bool IsIdle(Pawn p)
        {
            Job job = p.CurJob;
            return job == null || job.def == JobDefOf.Wait_Wander || job.def == JobDefOf.GotoWander
                || job.def == JobDefOf.Wait;
        }

        private static bool HeadingTo(Pawn p, Thing stand, float settleSq)
        {
            Job job = p.CurJob;
            return job != null && job.def == JobDefOf.Goto && job.targetA.IsValid
                && (job.targetA.Cell - stand.Position).LengthHorizontalSquared <= settleSq;
        }

        private bool TrySendToStand(Pawn p, Thing stand, RM_StallMobExtension ext)
        {
            if (!CellFinder.TryFindRandomCellNear(stand.Position, map, UnityEngine.Mathf.CeilToInt(ext.settleRadius),
                    c => c != stand.Position && c.Standable(map) && p.CanReach(c, PathEndMode.OnCell, Danger.Some),
                    out IntVec3 dest))
            {
                return false;
            }
            Job job = JobMaker.MakeJob(JobDefOf.Goto, dest);
            job.locomotionUrgency = LocomotionUrgency.Walk;
            p.jobs.StartJob(job, JobCondition.InterruptForced);
            RM_Flight.TryLaunch(p);
            return true;
        }
    }

    public static class RM_Flight
    {
        // Real 1.6 flight (Pawn_FlightTracker, decompiled): StartFlying only
        // takes off when CanFlyNow (has MaxFlightTime, off cooldown, not
        // already up). The job must be marked flying or the tracker's
        // Notify_JobStarted on the NEXT job lands it; FlightTick clears the
        // flag itself once grounded. Call AFTER StartJob, never before:
        // StartJob's Notify_JobStarted would ForceLand a pawn already up.
        public static void TryLaunch(Pawn p)
        {
            Pawn_FlightTracker flight = p.flight;
            if (flight == null || !flight.CanFlyNow)
            {
                return;
            }
            flight.StartFlying();
            if (flight.Flying && p.CurJob != null)
            {
                p.CurJob.flying = true;
            }
        }
    }
}
