namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>
    /// FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE — owner card 2026-10-20 (bar pump_port_takes_pipe_or_hose): "One port per side,
    /// either kind" (each side takes a pipe or a hose, not both). A pump has four ports, one on each cardinal side. A pipe joins
    /// a pump only on a side (or under it, where it runs on to a side); never across a corner. A hose couples to a side only
    /// when no pipe holds that side and no other hose already does (the lower thing id keeps it, so the verdict never flips
    /// with list order). Verse-free; the SelfTest compiles this production file.
    /// </summary>
    public static class RM_PumpPortMath
    {
        /// <summary>The side (Rot4 order: 0 north, 1 east, 2 south, 3 west) a neighbour at unit offset (dx, dz) from the pump
        /// sits on, or -1 when it is not on a side (a corner, the pump's own cell, or further away).</summary>
        public static int SideOf(int dx, int dz)
        {
            if (dx == 0 && dz == 1) return 0;
            if (dx == 1 && dz == 0) return 1;
            if (dx == 0 && dz == -1) return 2;
            if (dx == -1 && dz == 0) return 3;
            return -1;
        }

        /// <summary>Does a pipe cell at offset (dx, dz) from the pump join it? On a side, or under it (0, 0).</summary>
        public static bool PipeJoins(int dx, int dz)
        {
            return (dx == 0 && dz == 0) || SideOf(dx, dz) >= 0;
        }

        /// <summary>May the hose <paramref name="hoseId"/> couple on <paramref name="side"/>? Only on a side, never where a pipe
        /// already holds it, and only if no other hose on that side has a lower id.</summary>
        public static bool HoseMayTake(int side, bool pipeOnSide, int hoseId, int[] otherHoseIdsOnSide)
        {
            if (side < 0 || pipeOnSide)
            {
                return false;
            }
            if (otherHoseIdsOnSide != null)
            {
                for (int i = 0; i < otherHoseIdsOnSide.Length; i++)
                {
                    if (otherHoseIdsOnSide[i] != hoseId && otherHoseIdsOnSide[i] < hoseId)
                    {
                        return false;
                    }
                }
            }
            return true;
        }
    }
}
