// Verse-free (the SelfTest compiles this file): where a liquid join draws its fitting
// (HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY, design/RimMandrake/liquid_connections_visuals_2026-10-16.md).
using System;

namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>
    /// Owner 2026-10-16: "when you place a tank, reel, or pump next to each other some kind of connection should be visually
    /// apparent ... The pipe needs connectors that show where it's connecting. Same thing if you build a pipe alongside a
    /// tank but not under it." The geometry of those fittings, in cell units (a cell spans [x, x+1)). The draw side is
    /// RM_LiquidJoins (SectionLayer_RM_LiquidJoins, the hose-port fittings, the pipe-link patch).
    /// </summary>
    public static class LiquidJoinRule
    {
        /// <summary>Drawn size of a pipe-end flange, cells (the sheet's flange row: 128 px canvas = 0.5 cell).</summary>
        public const double FlangeSize = 0.5;
        /// <summary>Drawn size of the hose saddle on a pipe cell, cells (one cell square, the pipe across its middle).</summary>
        public const double SaddleLength = 1.0, SaddleWidth = 1.0;

        /// <summary>The flange of a pipe cell joining the neighbour on side (dx, dz) (a unit cardinal): its centre, offset from the
        /// pipe cell's centre, sits so the flange's face (the canvas's right edge) lies ON the shared cell edge, and its angle
        /// (degrees, counter-clockwise from east, the direction the flange faces).</summary>
        public static void Flange(int dx, int dz, out double ox, out double oz, out double angleDeg)
        {
            if (Math.Abs(dx) + Math.Abs(dz) != 1) throw new ArgumentException("a flange faces a cardinal side");
            double r = 0.5 - FlangeSize / 2;
            ox = dx * r;
            oz = dz * r;
            angleDeg = dx == 1 ? 0 : dz == 1 ? 90 : dx == -1 ? 180 : 270;
        }

        /// <summary>
        /// Two footprints (min corner and size, cells) that share an edge (touch cardinally along at least one cell): the
        /// midpoint of the shared segment (world cell units) and the side (unit, from a toward b). False when they overlap,
        /// are apart, or touch only at a corner (a diagonal touch attaches a machine to a tank but has no edge to draw on).
        /// </summary>
        public static bool SharedEdge(int ax, int az, int aw, int ah, int bx, int bz, int bw, int bh,
                                      out double mx, out double mz, out int sx, out int sz)
        {
            mx = mz = 0;
            sx = sz = 0;
            int zlo = Math.Max(az, bz), zhi = Math.Min(az + ah, bz + bh);
            int xlo = Math.Max(ax, bx), xhi = Math.Min(ax + aw, bx + bw);
            if (zhi > zlo && ax + aw == bx) { sx = 1; mx = bx; mz = (zlo + zhi) / 2.0; return true; }
            if (zhi > zlo && bx + bw == ax) { sx = -1; mx = ax; mz = (zlo + zhi) / 2.0; return true; }
            if (xhi > xlo && az + ah == bz) { sz = 1; mz = bz; mx = (xlo + xhi) / 2.0; return true; }
            if (xhi > xlo && bz + bh == az) { sz = -1; mz = az; mx = (xlo + xhi) / 2.0; return true; }
            return false;
        }

        /// <summary>The hose thickness the design proposes (owner 2026-10-16: "shrink the tube diameter a bit to make it less
        /// fire-hydrant-thick"): 0.65 x today's visible width = 0.25 cell flat / 0.30 plump against the rigid pipe's 0.23.
        /// NOT shipped: RM_HoseSettings.thickness stays 1 until he rules on the sheet.</summary>
        public const double ProposedHoseThickness = 0.65;
    }
}
