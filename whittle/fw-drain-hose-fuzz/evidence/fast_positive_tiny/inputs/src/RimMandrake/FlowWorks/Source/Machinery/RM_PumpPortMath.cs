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

        /// <summary>HOSE_END_FIX_CELL_SHORT_OF_PORT / PUMP_PORT_FIX_ASSUMES_ONE_CELL: the port cell on <paramref name="side"/>
        /// (Rot4 order) of a pump whose footprint is (minX, minZ, w, h) and whose Position is (posX, posZ): Position walked
        /// out along the side's facing step to the first cell outside the footprint. For a 1x1 pump that is Position +
        /// FacingCell, as before; a 3x2 pumping station gets one port on each of its four sides, not only the south one.</summary>
        public static void PortCell(int minX, int minZ, int w, int h, int posX, int posZ, int side, out int x, out int z)
        {
            int dx = side == 1 ? 1 : side == 3 ? -1 : 0;
            int dz = side == 0 ? 1 : side == 2 ? -1 : 0;
            x = posX + dx;
            z = posZ + dz;
            if (dx == 0 && dz == 0) return;
            while (x >= minX && x < minX + w && z >= minZ && z < minZ + h)
            {
                x += dx;
                z += dz;
            }
        }

        /// <summary>The side (Rot4 order) whose port cell (<see cref="PortCell"/>) is (x, z), or -1: a corner, another lane
        /// of a long side, the footprint itself or further away.</summary>
        public static int SideOfPort(int minX, int minZ, int w, int h, int posX, int posZ, int x, int z)
        {
            for (int s = 0; s < 4; s++)
            {
                PortCell(minX, minZ, w, h, posX, posZ, s, out int px, out int pz);
                if (px == x && pz == z) return s;
            }
            return -1;
        }

        /// <summary><see cref="HoseMayTake(int, int, int[])"/> over a list, without copying it (HOSE_TICK_REBUILD_ZERO_ALLOC: the
        /// hose port gate reads the other ids into reused scratch).</summary>
        public static bool HoseMayTake(int side, int hoseId, System.Collections.Generic.List<int> otherHoseIdsOnSide)
        {
            if (side < 0)
            {
                return false;
            }
            if (otherHoseIdsOnSide != null)
            {
                for (int i = 0; i < otherHoseIdsOnSide.Count; i++)
                {
                    if (otherHoseIdsOnSide[i] != hoseId && otherHoseIdsOnSide[i] < hoseId)
                    {
                        return false;
                    }
                }
            }
            return true;
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
