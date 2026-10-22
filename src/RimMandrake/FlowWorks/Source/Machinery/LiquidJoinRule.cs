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

        /// <summary>
        /// PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE (owner 2026-10-18: "draw pipes as though they are connected into the centers of all
        /// pipe-receiving items even if the actual pipe ends at the edge of their graphic (so that it appears to continue beneath
        /// them through any transparent boundaries they might have)"). A pipe or hose end on cell (cx, cz) joining the building
        /// on its side (dx, dz) (a unit cardinal), whose footprint is (bx, bz, bw, bh): the polyline (world cell units) the
        /// run continues along beneath the building -- from the shared edge's midpoint in front of the end, straight in to the
        /// depth of the footprint's centre, then sideways to the centre when the end is off the centre line (a multi-cell
        /// footprint). 2 points when the end faces the centre (always for a 1x1), 3 otherwise. Null when (cx, cz) + (dx, dz)
        /// is not inside the footprint (the end does not face it).
        /// </summary>
        public static double[] CentreStub(int cx, int cz, int dx, int dz, int bx, int bz, int bw, int bh)
        {
            if (Math.Abs(dx) + Math.Abs(dz) != 1) throw new ArgumentException("a stub enters from a cardinal side");
            int nx = cx + dx, nz = cz + dz;
            if (nx < bx || nx >= bx + bw || nz < bz || nz >= bz + bh) return null;
            double ex = cx + 0.5 + dx * 0.5, ez = cz + 0.5 + dz * 0.5;
            double mx = bx + bw / 2.0, mz = bz + bh / 2.0;
            double kx = dx != 0 ? mx : ex, kz = dz != 0 ? mz : ez;
            bool bend = Math.Abs(kx - mx) > 1e-9 || Math.Abs(kz - mz) > 1e-9;
            return bend ? new[] { ex, ez, kx, kz, mx, mz } : new[] { ex, ez, mx, mz };
        }

        /// <summary>
        /// He typed 2026-10-20: <i>"A solid pipe must only be adjacent and is then drawn undernead to the center of the object
        /// as ruled previously."</i> The corner case of <see cref="CentreStub"/>: a pipe on (cx, cz) that touches the footprint
        /// (bx, bz, bw, bh) ONLY across a corner, (dx, dz) a unit diagonal. Pipes run square, so the stub is an elbow: out of the
        /// pipe cell's east/west edge to the column of the diagonal cell, then straight into the footprint to the depth of its
        /// centre, then sideways to the centre. Null when the diagonal cell is not in the footprint, or when the pipe also
        /// touches it along an edge (CentreStub draws that one).
        /// </summary>
        public static double[] CornerStub(int cx, int cz, int dx, int dz, int bx, int bz, int bw, int bh)
        {
            if (Math.Abs(dx) != 1 || Math.Abs(dz) != 1) throw new ArgumentException("a corner stub enters from a diagonal");
            bool In(int x, int z) => x >= bx && x < bx + bw && z >= bz && z < bz + bh;
            if (!In(cx + dx, cz + dz) || In(cx + dx, cz) || In(cx, cz + dz)) return null;
            double ex = cx + 0.5 + dx * 0.5, ez = cz + 0.5;
            double colX = cx + dx + 0.5;
            double mx = bx + bw / 2.0, mz = bz + bh / 2.0;
            var pts = new System.Collections.Generic.List<double> { ex, ez, colX, ez, colX, mz };
            if (Math.Abs(colX - mx) > 1e-9) { pts.Add(mx); pts.Add(mz); }
            return pts.ToArray();
        }

        /// <summary>One straight axis-aligned piece of a stub, drawn as a plane of the pipe's straight atlas tile: centre, its
        /// length along the run (at most 1 cell, the tile's own length) and whether the run is east-west. U0/U1 crop the
        /// tile along the run so a piece shorter than a cell shows a slice, not a squashed tile.</summary>
        public struct StubPiece
        {
            public double X, Z, Length, U0, U1;
            public bool EastWest;
        }

        /// <summary>Cut a stub polyline (CentreStub's output) into pieces of at most one cell, each a straight tile slice. A
        /// zero-length leg yields nothing.</summary>
        public static System.Collections.Generic.List<StubPiece> StubPieces(double[] poly)
        {
            var list = new System.Collections.Generic.List<StubPiece>();
            if (poly == null) return list;
            for (int i = 0; i + 3 < poly.Length; i += 2)
            {
                double ax = poly[i], az = poly[i + 1], bx = poly[i + 2], bz = poly[i + 3];
                double len = Math.Abs(bx - ax) + Math.Abs(bz - az);
                if (len < 1e-9) continue;
                bool ew = Math.Abs(bz - az) < 1e-9;
                double ux = (bx - ax) / len, uz = (bz - az) / len;
                double done = 0;
                while (done < len - 1e-9)
                {
                    double l = Math.Min(1.0, len - done);
                    double mid = done + l / 2;
                    list.Add(new StubPiece { X = ax + ux * mid, Z = az + uz * mid, Length = l, U0 = 0.5 - l / 2, U1 = 0.5 + l / 2, EastWest = ew });
                    done += l;
                }
            }
            return list;
        }
    }
}
