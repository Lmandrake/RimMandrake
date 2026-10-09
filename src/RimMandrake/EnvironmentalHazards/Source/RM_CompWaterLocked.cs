using System;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    //   <li Class="RimMandrake.EnvironmentalHazards.CompProperties_WaterLocked">
    //     <checkIntervalTicks>60</checkIntervalTicks>
    //   </li>
    //
    // WARDEN_MOTHER_BEFRIENDING_1: "the whole mechanism is the waterline" —
    // the one genuinely new mechanism that item's own text names. Nothing in
    // this repo (or in vanilla — MEASURED against the decompiled engine
    // before writing this: Verse.TraverseMode has no water-only mode,
    // Verse.RaceProperties.waterCellCost only ever makes water CHEAPER for a
    // waterSeeker race, it never makes land impassable) restricts a pawn to
    // water terrain before this.
    //
    // Deliberately NOT a pathfinder-level constraint. RimWorld does expose a
    // real seam for that (Verse.PathRequest.IPathGridCustomizer, a
    // NativeArray<ushort> per-cell cost-offset grid a caller can hand to
    // PathFinder.FindPath), but building and validating a native cost-grid
    // override blind is exactly the class of silent, hard-to-verify failure
    // this project's own instructions warn hardest against — and this
    // item's own "Watch out" section explicitly flags "whether a pawn's
    // pathing can be constrained to a terrain set at all" and "whether a
    // bodySize this large paths through shallow water without breaking" as
    // UNMEASURABLE without a live Desktop pass. A wrong pathfinder patch
    // risks breaking movement for every OTHER pawn on the map, not just this
    // one.
    //
    // Instead, three cooperating, individually low-risk, offline-verifiable
    // pieces reach the same behaviour for THIS pawn alone:
    //   1. RM_JobGiver_AnchorWander's own wanderDestValidator (a real,
    //      documented per-instance hook on vanilla's own JobGiver_Wander,
    //      Verse/AI/JobGiver_Wander.cs) never offers a non-water wander
    //      destination.
    //   2. RM_JobGiver_AnchorDefense.ExtraTargetValidator (the same kind of
    //      documented per-instance hook on JobGiver_AIFightEnemy) refuses a
    //      target whose own cell is neither water nor adjacent to water.
    //   3. THIS comp is the backstop, and the only piece that can catch a
    //      case (1)/(2) do not: a target dragged/knocked onto land, a
    //      melee chase whose path briefly touches a shoreline land cell, or
    //      a bad initial placement. Every checkIntervalTicks, if the pawn's
    //      own current cell is not water, it is stopped dead and its job
    //      ended — so she can never be found IDLING on dry ground, which is
    //      this item's own verify bullet in the strongest form buildable
    //      without a live game to test against.
    //
    // What this does NOT guarantee, and must never be reported as MEASURED:
    // that a computed path never crosses a single land cell mid-route to
    // reach a shoreline attack target before this comp's next check fires.
    // Closing that gap for real needs the pathfinder-level customizer
    // above, which needs the Desktop — filed as
    // WARDEN_MOTHER_PATHFINDER_VERIFY_1.
    public class CompProperties_WaterLocked : CompProperties
    {
        public int checkIntervalTicks = 60;

        public CompProperties_WaterLocked()
        {
            compClass = typeof(RM_CompWaterLocked);
        }
    }

    public class RM_CompWaterLocked : ThingComp
    {
        public CompProperties_WaterLocked Props => (CompProperties_WaterLocked)props;

        // Not saved: after a load the next land check simply issues a fresh recovery walk.
        private Job recoveryJob;

        private const int RecoverySearchRadius = 40;   // PROVISIONAL (auto-decided 2026-10-09, WARDEN_MOTHER_LAND_RECOVERY_1)
        private const int RecoveryReachChecks = 12;    // reachability probes per search, nearest water first

        private static bool HeadedForWater(Pawn pawn)
        {
            if (pawn.pather == null || !pawn.pather.Moving)
            {
                return false;
            }
            LocalTargetInfo dest = pawn.pather.Destination;
            return dest.IsValid && IsWaterCell(dest.Cell, pawn.Map);
        }

        private static bool TryFindRecoveryCell(Pawn pawn, out IntVec3 found)
        {
            found = IntVec3.Invalid;
            Map map = pawn.Map;
            int probes = 0;
            int max = GenRadial.NumCellsInRadius(RecoverySearchRadius);
            for (int i = 1; i < max; i++)
            {
                IntVec3 c = pawn.Position + GenRadial.RadialPattern[i];
                if (!IsWaterCell(c, map) || !c.Standable(map))
                {
                    continue;
                }
                if (pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
                {
                    found = c;
                    return true;
                }
                if (++probes >= RecoveryReachChecks)
                {
                    return false;
                }
            }
            return false;
        }

        public static bool IsWaterCell(IntVec3 cell, Map map)
        {
            if (map == null || !cell.InBounds(map))
            {
                return false;
            }

            TerrainDef terrain = map.terrainGrid.TerrainAt(cell);
            return terrain != null && terrain.IsWater;
        }

        public override void CompTick()
        {
            base.CompTick();

            if (!(parent is Pawn pawn) || !pawn.Spawned || pawn.Dead || pawn.Map == null)
            {
                return;
            }

            if (!parent.IsHashIntervalTick(Math.Max(1, Props.checkIntervalTicks)))
            {
                return;
            }

            if (IsWaterCell(pawn.Position, pawn.Map))
            {
                return;
            }

            // WARDEN_MOTHER_LAND_RECOVERY_1 PROVISIONAL (auto-decided 2026-10-09): the old backstop stopped her
            // dead every check, including the walk that would have taken her back, so she could be frozen on land
            // for good. Now a walk already headed for water (ours or any other) is left alone, and anything else
            // is replaced by a walk to the nearest reachable water cell.
            if (RM_EnvironmentalHazardsSettings.waterLockedRecoveryWalk)
            {
                if (pawn.jobs?.curJob != null && (pawn.jobs.curJob == recoveryJob || HeadedForWater(pawn)))
                {
                    return;
                }
                if (TryFindRecoveryCell(pawn, out IntVec3 water))
                {
                    pawn.pather?.StopDead();
                    recoveryJob = JobMaker.MakeJob(JobDefOf.Goto, water);
                    recoveryJob.locomotionUrgency = LocomotionUrgency.Jog;
                    pawn.jobs?.StartJob(recoveryJob, JobCondition.InterruptForced);
                    return;
                }
            }

            // Found on dry ground with no way back (or recovery switched off) — stop her right there rather
            // than let her continue walking further inland toward whatever job she was mid-executing.
            pawn.pather?.StopDead();
            if (pawn.jobs?.curJob != null)
            {
                pawn.jobs.EndCurrentJob(JobCondition.InterruptForced, startNewJob: false);
            }
        }
    }
}
