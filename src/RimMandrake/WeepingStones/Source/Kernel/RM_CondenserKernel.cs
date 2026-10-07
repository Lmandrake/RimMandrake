// Verse-free kernel of the walking condenser (RM_CompWalkingCondenser) and the ancient condenser plant: the seasonal
// phase machine (Settled -> Waiting -> Walking -> Settled), the pool's growth radius, the drying schedule, and the water
// accumulator. The comps call these with the same expressions; SelfTest/WeepingStonesFuzz.cs compiles this file alone,
// so it must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.WeepingStones
{
    public enum RM_CondenserPhase : byte { Settled, Waiting, Walking, Gone }

    public struct CondenserState
    {
        public RM_CondenserPhase phase;
        public int phaseStartTick;
        public int settleTick;
        public int poolRadius;
        public bool drying;
        public int dryStartTick;
        public int dryStartCount;   // pool cells when drying began (-1 = unknown: an old save)
    }

    [Flags]
    public enum CondenserAct { None = 0, Grow = 1, BeginWaiting = 2, BeginWalking = 4, Arrived = 8, IssueGoto = 16, StepDry = 32, NoSite = 64, StartedDrying = 128 }

    public static class RM_CondenserKernel
    {
        public const int StepTicks = 250;           // the comp's hand-gated cadence
        public const float ArriveDistance = 3f;

        // ---- pool growth --------------------------------------------------------------------------
        // radius += floor(perStep) + (Chance(frac(perStep)) ? 1 : 0), from at least 1, capped; roll() is Rand.Value.
        public static int GrowRadius(int poolRadius, int maxRadius, float growDays, int ticksPerDay, Func<float> roll)
        {
            if (poolRadius >= maxRadius) return poolRadius;
            float stepsTotal = growDays * ticksPerDay / (float)StepTicks;
            float perStep = maxRadius / Math.Max(1f, stepsTotal);
            float frac = perStep % 1f;
            bool extra = frac > 0f && (frac >= 1f || roll() < frac);
            return Math.Min(maxRadius, Math.Max(poolRadius, 1) + (extra ? 1 : 0) + (int)Math.Floor(perStep));
        }

        // ---- drying schedule -----------------------------------------------------------------------
        // The most cells that may remain `now`, falling linearly from startCount to 0 over dryDays. Never instant.
        public static int DryKeep(int startCount, int startTick, int now, float dryDays, int ticksPerDay)
        {
            double total = (double)dryDays * ticksPerDay;
            if (total <= 0.0) return 0;
            double frac = (now - startTick) / total;
            if (frac >= 1.0) return 0;
            if (frac <= 0.0) return startCount;
            return (int)Math.Ceiling(startCount * (1.0 - frac));
        }

        // Begin drying (a no-op if already drying or there is no pool). Returns whether it began.
        public static bool StartDrying(ref CondenserState s, int now, int cellCount)
        {
            if (s.drying || cellCount == 0) return false;
            s.drying = true;
            s.dryStartTick = now;
            s.dryStartCount = cellCount;
            return true;
        }

        // How many cells to restore this step; also adopts an old save's missing start count.
        public static int DryRestore(ref CondenserState s, int now, int cellCount, float dryDays, int ticksPerDay)
        {
            if (s.dryStartCount < 0) { s.dryStartCount = cellCount; s.dryStartTick = now; }
            int keep = DryKeep(Math.Max(s.dryStartCount, cellCount), s.dryStartTick, now, dryDays, ticksPerDay);
            return Math.Max(0, cellCount - keep);
        }

        // ---- the phase machine ---------------------------------------------------------------------
        // One enabled CompTick (already on the 250-tick cadence). siteAvailable() picks a random walking site (engine);
        // materialise(radius) paints the pool out to that radius and returns the pool's cell count afterwards - the pool
        // grows BEFORE the season check so a crab that starts waiting this tick dries the cells it has just grown.
        public static CondenserAct Tick(ref CondenserState s, ref bool targetValid, int now, int seasonTicks, int ticksPerDay,
                                         float distToTarget, bool crabHasGotoJob, int poolCellCount,
                                         int maxRadius, float growDays, Func<float> roll, Func<int, int> materialise, Func<bool> siteAvailable)
        {
            CondenserAct a = CondenserAct.None;
            switch (s.phase)
            {
                case RM_CondenserPhase.Settled:
                    if (!s.drying)
                    {
                        a |= CondenserAct.Grow;
                        if (s.poolRadius < maxRadius)
                        {
                            s.poolRadius = GrowRadius(s.poolRadius, maxRadius, growDays, ticksPerDay, roll);
                            poolCellCount = materialise(s.poolRadius);
                        }
                    }
                    if (now - s.settleTick >= seasonTicks)
                    {
                        s.phase = RM_CondenserPhase.Waiting; s.phaseStartTick = now;
                        targetValid = false;
                        a |= CondenserAct.BeginWaiting;
                        if (StartDrying(ref s, now, poolCellCount)) a |= CondenserAct.StartedDrying;
                    }
                    break;
                case RM_CondenserPhase.Waiting:
                    if (now - s.phaseStartTick >= ticksPerDay)
                    {
                        s.phase = RM_CondenserPhase.Walking; s.phaseStartTick = now;
                        a |= CondenserAct.BeginWalking;
                        if (!targetValid) targetValid = siteAvailable();
                        if (targetValid) a |= CondenserAct.IssueGoto;
                        else { s.phase = RM_CondenserPhase.Settled; s.settleTick = now; s.poolRadius = 0; a |= CondenserAct.NoSite; }
                    }
                    break;
                case RM_CondenserPhase.Walking:
                    a |= CondenserAct.StepDry;
                    if (!targetValid || distToTarget < ArriveDistance || now - s.phaseStartTick > 3 * ticksPerDay)
                    {
                        // Arrived: any pool cells still drying keep drying where the crab left them.
                        s.phase = RM_CondenserPhase.Settled; s.settleTick = now; s.poolRadius = 0;
                        s.drying = poolCellCount > 0;
                        a |= CondenserAct.Arrived;
                    }
                    else if (!crabHasGotoJob)
                    {
                        a |= CondenserAct.IssueGoto;
                    }
                    break;
            }
            if (s.drying && s.phase != RM_CondenserPhase.Walking) a |= CondenserAct.StepDry;
            return a;
        }

        // ---- the ancient condenser plant -----------------------------------------------------------
        // Water accumulates 250 ticks per rare tick; at the interval it resets and (if under the cap) makes `litres`.
        public static bool WaterDue(ref int acc, int tickRare, int intervalTicks)
        {
            acc += tickRare;
            if (acc < intervalTicks) return false;
            acc = 0;
            return true;
        }
        public static bool WaterSpawns(int have, int cap) { return have < cap; }
    }
}
