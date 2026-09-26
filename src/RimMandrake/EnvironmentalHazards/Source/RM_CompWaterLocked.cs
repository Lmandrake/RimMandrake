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

            // Found on dry ground — stop her right there rather than let her
            // continue walking further inland toward whatever job she was
            // mid-executing.
            pawn.pather?.StopDead();
            if (pawn.jobs?.curJob != null)
            {
                pawn.jobs.EndCurrentJob(JobCondition.InterruptForced, startNewJob: false);
            }
        }
    }
}
