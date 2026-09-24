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

    public enum RM_OasisMakerState : byte
    {
        Dormant,
        Attuning,
        Working,
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
        private static readonly string[] MarginLadder = { "Sand", "Gravel", "Soil", "SoilRich" };
        private static readonly string[] PoolLadder = { "Sand", "Gravel", "Soil", "Mud", "Marsh", "WaterShallow" };

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

        private const int RareTickInterval = 250;

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (!RM_OasisMakerSettings.masterEnabled || !parent.Spawned)
            {
                return;
            }

            switch (state)
            {
                case RM_OasisMakerState.Dormant:
                    if (ValidNow())
                    {
                        state = RM_OasisMakerState.Attuning;
                        ticksInState = 0;
                    }
                    break;

                case RM_OasisMakerState.Attuning:
                    if (!ValidNow())
                    {
                        // §2: losing shade/rock drops it back to Dormant;
                        // nothing converted yet at this stage, so there is
                        // nothing to preserve.
                        state = RM_OasisMakerState.Dormant;
                        ticksInState = 0;
                        break;
                    }
                    ticksInState += RareTickInterval;
                    if (ticksInState >= RM_OasisMakerSettings.attuningDays * GenDate.TicksPerDay)
                    {
                        // §2/§3: "a one-time commitment, not continuously
                        // rescaled by later terrain changes near the
                        // machine" (see the class doc comment and
                        // qualityLocked's own field). A machine that drops
                        // back to Dormant (losing shade/rock) and later
                        // re-attunes must NOT re-roll lockedRadiusCap/
                        // lockedSpeedMultiplier from whatever the site scores
                        // today — currentRing etc. persist across the cycle,
                        // so a re-lock could shrink the cap below progress
                        // already made and falsely read as "the oasis is
                        // made." Only the first Attuning->Working transition
                        // locks quality; qualityLocked itself was the
                        // intended guard for this and was previously never
                        // checked.
                        if (!qualityLocked)
                        {
                            LockQuality();
                        }
                        state = RM_OasisMakerState.Working;
                        ticksInState = 0;
                    }
                    break;

                case RM_OasisMakerState.Working:
                    if (!ValidNow())
                    {
                        // §2: "it never un-makes anything" — currentRing,
                        // ringRungsClimbed and rungProgressTicks are all
                        // scribed, so regaining validity later (Dormant ->
                        // Attuning -> Working again) resumes exactly here.
                        state = RM_OasisMakerState.Dormant;
                        ticksInState = 0;
                        break;
                    }
                    if (currentRing >= lockedRadiusCap)
                    {
                        return; // "The oasis is made."
                    }
                    AdvanceGrowth(RareTickInterval);
                    break;
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
            lockedRadiusCap = Mathf.RoundToInt(Mathf.Lerp(
                RM_OasisMakerSettings.minRadiusCap, RM_OasisMakerSettings.maxRadiusCap, quality));
            lockedSpeedMultiplier = Mathf.Lerp(0.5f, 1.5f, quality);
            qualityLocked = true;
        }

        private static string[] LadderForRing(int ringIndex) => ringIndex == 0 ? PoolLadder : MarginLadder;

        private static int RungsForRing(int ringIndex) => LadderForRing(ringIndex).Length - 1;

        private long RingDurationTicks(int ringIndex)
        {
            double days = RM_OasisMakerSettings.baseRingDays
                * System.Math.Pow(RM_OasisMakerSettings.ringGrowthFactor, ringIndex);
            return (long)(days * GenDate.TicksPerDay);
        }

        private long PerRungTicks(int ringIndex)
        {
            return System.Math.Max(1L, RingDurationTicks(ringIndex) / RungsForRing(ringIndex));
        }

        private void AdvanceGrowth(int deltaTicks)
        {
            rungProgressTicks += (int)(deltaTicks * lockedSpeedMultiplier);

            while (currentRing < lockedRadiusCap && rungProgressTicks >= PerRungTicks(currentRing))
            {
                rungProgressTicks -= (int)PerRungTicks(currentRing);
                AdvanceRingOneRung(currentRing, LadderForRing(currentRing));
                ringRungsClimbed++;

                if (ringRungsClimbed >= RungsForRing(currentRing))
                {
                    currentRing++;
                    ringRungsClimbed = 0;
                    rungProgressTicks = 0;
                }
            }
        }

        /// Advances every eligible cell in the given ring band by exactly one
        /// rung of the given ladder. "Eligible" = current terrain matches a
        /// non-terminal rung of THIS ladder; anything else (stone, a
        /// constructed floor, water outside the pool zone, or a cell that
        /// already reached the ladder's terminal terrain) is silently
        /// skipped — that skip IS "only natural loose terrains convert."
        private void AdvanceRingOneRung(int ringIndex, string[] ladder)
        {
            Map map = parent.Map;
            if (map == null)
            {
                return;
            }
            IntVec3 center = CenterCell;
            int lo = ringIndex == 0 ? 0 : ringIndex + 1;
            int hi = ringIndex == 0 ? 1 : ringIndex + 1;
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
                    AdvanceCell(map, cell, ladder);
                }
            }
        }

        private static void AdvanceCell(Map map, IntVec3 cell, string[] ladder)
        {
            TerrainDef current = map.terrainGrid.TerrainAt(cell);
            if (current == null)
            {
                return;
            }
            int idx = IndexInLadder(ladder, current);
            if (idx < 0 || idx >= ladder.Length - 1)
            {
                return; // ineligible origin, or already at/past this ladder's terminal rung
            }
            TerrainDef next = DefDatabase<TerrainDef>.GetNamed(ladder[idx + 1], errorOnFail: false);
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

        private static int IndexInLadder(string[] ladder, TerrainDef td)
        {
            string name = td.defName == "SoftSand" ? "Sand" : td.defName;
            for (int i = 0; i < ladder.Length; i++)
            {
                if (ladder[i] == name)
                {
                    return i;
                }
            }
            return -1;
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
