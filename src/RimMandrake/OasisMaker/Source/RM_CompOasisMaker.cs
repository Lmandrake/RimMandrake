using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.OasisMaker
{
    public class CompProperties_OasisMaker : CompProperties
    {
        public CompProperties_OasisMaker()
        {
            compClass = typeof(RM_CompOasisMaker);
        }
    }

    /// <summary>
    /// OASIS_MAKER_BUILD_1 §2. The whole machine: no power, no fuel, no
    /// MapComponent — everything is scribed on this comp and dies with the
    /// building, per spec ("Power/fuel: NONE"; "no MapComponent needed").
    ///
    /// RING MODEL (spec §2/§3, my own bucketing choice documented here since
    /// the spec describes the fiction, not the cell math): rings are bucketed
    /// by Chebyshev (square) distance from the building's footprint center,
    /// not Euclidean — deterministic, cheap, and "ring-by-ring" reads fine as
    /// a diamond/square rather than a perfect circle for a first landing.
    /// Ring 0 is the pool zone (distance 0-1, the "3x3-ish" §2 describes);
    /// ring r>=1 is the single-cell-wide band at distance r+1. currentRing
    /// counts 0-based; the inspect string adds 1 so player-facing numbering
    /// matches the spec's "ring 1" language for the innermost ring.
    ///
    /// A ring is climbed by a RING-WIDE synchronized step counter, not
    /// per-cell timers: spec's "ring r starts only when ring r-1 is fully
    /// climbed" reads as ring-level progression, and no per-cell state needs
    /// scribing this way — a cell's own current TerrainDef (read live off
    /// map.terrainGrid) IS its progress. This also makes "only natural loose
    /// terrains convert" free: a cell whose current terrain is not in the
    /// ladder (stone, a constructed floor, existing water) is simply never
    /// eligible to advance, no extra guard needed.
    /// </summary>
    public class RM_CompOasisMaker : ThingComp
    {
        // Margin ladder terminates at SoilRich; pool ladder pushes on to a
        // real WaterShallow pool. Both confirmed real Core TerrainDefs
        // (defs.sqlite, 2026-09-24). SoftSand is folded onto Sand's rung.
        // (the ladders themselves live in RM_OasisKernel so the offline fuzz walks the SAME rungs)

        public RM_OasisMakerState state = RM_OasisMakerState.Dormant;
        private int ticksInState;
        private int currentRing;
        private int ringRungsClimbed;
        private int rungProgressTicks;

        // Locked in the moment Attuning completes (§3: "placement is key" —
        // a one-time commitment, not continuously rescaled by later terrain
        // changes near the machine).
        private bool qualityLocked;
        private int lockedRadiusCap;
        private float lockedSpeedMultiplier;

        private const int RareTickInterval = RM_OasisKernel.RareTickInterval;

        public override void CompTickRare()
        {
            base.CompTickRare();
            // The state machine, the one-time quality lock and "nothing converts while invalid" are RM_OasisKernel.Step (offline-fuzzed).
            // Spec §2: losing shade/rock drops Attuning/Working back to Dormant; currentRing, ringRungsClimbed and rungProgressTicks are
            // scribed, so regaining validity resumes exactly where it stopped ("it never un-makes anything"). A re-attune must NOT re-roll
            // lockedRadiusCap/lockedSpeedMultiplier (qualityLocked guards that: only the first Attuning->Working locks).
            RM_OasisKernel.Step(ref state, ref ticksInState, RM_OasisMakerSettings.masterEnabled, parent.Spawned, ValidNow,
                RM_OasisMakerSettings.attuningDays, GenDate.TicksPerDay, ref qualityLocked, LockQuality, currentRing, lockedRadiusCap, out bool grow);
            if (grow)
            {
                AdvanceGrowth(RareTickInterval);
            }
        }

        private bool ValidNow()
        {
            if (parent.Map == null)
            {
                return false;
            }
            RM_OasisPlacementScorer.Score score = RM_OasisPlacementScorer.ScoreAt(parent.Map, CenterCell);
            return score.MeetsFloor();
        }

        private IntVec3 CenterCell => parent.OccupiedRect().CenterCell;

        private void LockQuality()
        {
            RM_OasisPlacementScorer.Score score = RM_OasisPlacementScorer.ScoreAt(parent.Map, CenterCell);
            float quality = score.Quality01();
            lockedRadiusCap = RM_OasisKernel.RadiusCap(RM_OasisMakerSettings.minRadiusCap, RM_OasisMakerSettings.maxRadiusCap, quality);
            lockedSpeedMultiplier = RM_OasisKernel.SpeedMultiplier(quality);
            qualityLocked = true;
        }

        private void AdvanceGrowth(int deltaTicks)
        {
            RM_OasisKernel.AdvanceGrowth(ref rungProgressTicks, ref currentRing, ref ringRungsClimbed, deltaTicks, lockedSpeedMultiplier, lockedRadiusCap,
                RM_OasisMakerSettings.baseRingDays, RM_OasisMakerSettings.ringGrowthFactor, GenDate.TicksPerDay,
                ring => AdvanceRingOneRung(ring));
        }

        /// Advances every eligible cell in the given ring band by exactly one
        /// rung of the given ladder. "Eligible" = current terrain matches a
        /// non-terminal rung of THIS ladder; anything else (stone, a
        /// constructed floor, water outside the pool zone, or a cell that
        /// already reached the ladder's terminal terrain) is silently
        /// skipped — that skip IS "only natural loose terrains convert."
        private void AdvanceRingOneRung(int ringIndex)
        {
            Map map = parent.Map;
            if (map == null)
            {
                return;
            }
            IntVec3 center = CenterCell;
            RM_OasisKernel.RingBand(ringIndex, out int lo, out int hi);
            for (int dz = -hi; dz <= hi; dz++)
            {
                for (int dx = -hi; dx <= hi; dx++)
                {
                    int chebyshev = System.Math.Max(System.Math.Abs(dx), System.Math.Abs(dz));
                    if (chebyshev < lo || chebyshev > hi)
                    {
                        continue;
                    }
                    IntVec3 cell = new IntVec3(center.x + dx, center.y, center.z + dz);
                    if (!cell.InBounds(map))
                    {
                        continue;
                    }
                    AdvanceCell(map, cell, ringIndex);
                }
            }
        }

        private static void AdvanceCell(Map map, IntVec3 cell, int ringIndex)
        {
            TerrainDef current = map.terrainGrid.TerrainAt(cell);
            if (current == null)
            {
                return;
            }
            string nextName = RM_OasisKernel.NextTerrain(ringIndex, current.defName);
            if (nextName == null)
            {
                return; // ineligible origin, or already at/past this ladder's terminal rung
            }
            TerrainDef next = DefDatabase<TerrainDef>.GetNamed(nextName, errorOnFail: false);
            if (next == null)
            {
                return;
            }
            map.terrainGrid.SetTerrain(cell, next);
            if (next.defName == "WaterShallow")
            {
                RM_OasisPoolIntegration.NotifyPoolCellCreated(map, cell);
            }
        }

        public override string CompInspectStringExtra()
        {
            StringBuilder sb = new StringBuilder();
            switch (state)
            {
                case RM_OasisMakerState.Dormant:
                    sb.Append("Dormant. It is waiting for cold stone and shade.");
                    break;
                case RM_OasisMakerState.Attuning:
                    sb.Append("Attuning. Something is waking, slowly.");
                    break;
                case RM_OasisMakerState.Working:
                    if (currentRing >= lockedRadiusCap)
                    {
                        sb.Append("The oasis is made.");
                    }
                    else
                    {
                        sb.Append("Working: ring " + (currentRing + 1) + " of " + lockedRadiusCap + ".");
                    }
                    break;
            }
            return sb.ToString();
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref state, "oasisState", RM_OasisMakerState.Dormant);
            Scribe_Values.Look(ref ticksInState, "ticksInState", 0);
            Scribe_Values.Look(ref currentRing, "currentRing", 0);
            Scribe_Values.Look(ref ringRungsClimbed, "ringRungsClimbed", 0);
            Scribe_Values.Look(ref rungProgressTicks, "rungProgressTicks", 0);
            Scribe_Values.Look(ref qualityLocked, "qualityLocked", false);
            Scribe_Values.Look(ref lockedRadiusCap, "lockedRadiusCap", 0);
            Scribe_Values.Look(ref lockedSpeedMultiplier, "lockedSpeedMultiplier", 0f);
        }
    }
}
