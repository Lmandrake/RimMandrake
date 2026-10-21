namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>
    /// FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE (bar pump_hose_joins_at_side_port) — he typed 2026-10-20: <i>"No. a HOSE must
    /// connect at one of the four sides. A solid pipe must only be adjacent and is then drawn undernead to the center of the
    /// object as ruled previously."</i> A pump has four hose ports, one on each cardinal side; a hose (a reel's body or a laid
    /// hose's free end) couples only at a free port, one hose to a port (the lower thing id keeps it, so the verdict never
    /// flips with list order). Rigid pipes are NOT ports: they join a pump wherever they are adjacent (8-way, as for every
    /// machine: RM_LiquidNet) and draw under it to its centre. Verse-free; the SelfTest compiles this production file.
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

        /// <summary>May the hose <paramref name="hoseId"/> couple at the port on <paramref name="side"/>? Only at a side port
        /// (never a corner), and only if no other hose at that port has a lower id. A pipe beside the port does not take it.</summary>
        public static bool HoseMayTake(int side, int hoseId, int[] otherHoseIdsOnSide)
        {
            if (side < 0)
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
