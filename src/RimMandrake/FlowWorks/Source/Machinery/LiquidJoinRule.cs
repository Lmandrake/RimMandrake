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
        /// TANK_FLANGE_FIX_HOVERS_MID_PIPE (live 2026-10-22, map C C3 north: a pipe entering the universal tank from the south drew
        /// its flange on the footprint edge, ~0.46 cell below the drawn skid, mid-pipe): the flange of a pipe cell joining a tank
        /// on side (dx, dz) sits with its face where the pipe's centre line meets the tank's DRAWN outline, <paramref name="inset"/>
        /// cells inward from the shared footprint edge (TankArtEdges; negative = the art overhangs the pipe cell). Offset from the
        /// pipe cell's centre, and the angle (as <see cref="Flange"/>). False = the face lies at or beyond the pipe cell's far side:
        /// the sprite covers the whole pipe cell there, so there is no visible join to fit.
        /// </summary>
        public static bool FlangeOnArt(int dx, int dz, double inset, out double ox, out double oz, out double angleDeg)
        {
            Flange(dx, dz, out ox, out oz, out angleDeg);
            double face = 0.5 + inset;   // from the pipe cell's centre, along (dx, dz)
            if (face <= -0.5 + 1e-9) return false;
            double c = face - FlangeSize / 2;
            ox = dx * c;
            oz = dz * c;
            return true;
        }

        /// <summary>TANK_FLANGE_FIX_HOVERS_MID_PIPE: with the under-run to the centre switched off, the pipe's arm ends on the shared
        /// edge, short of a drawn outline set <paramref name="inset"/> cells in: the straight piece from the edge on to that outline
        /// (null when the outline is on or outside the edge).</summary>
        public static double[] ReachStub(int cx, int cz, int dx, int dz, double inset)
        {
            if (Math.Abs(dx) + Math.Abs(dz) != 1) throw new ArgumentException("a reach enters from a cardinal side");
            if (inset <= 1e-9) return null;
            double ex = cx + 0.5 + dx * 0.5, ez = cz + 0.5 + dz * 0.5;
            return new[] { ex, ez, ex + dx * inset, ez + dz * inset };
        }

        /// <summary>C1_TANK_STUB_PRUNE_PIPE_TO_NOWHERE (map R C1, 2026-10-22: a dead-end L under the tall tank beside the trunk): a
        /// pipe touching a footprint across a corner draws its <see cref="CornerStub"/> elbow only when it is not already joined
        /// through a pipe on either cell between it and that corner (<paramref name="pipeBesideX"/> = a pipe on (cx + dx, cz),
        /// <paramref name="pipeBesideZ"/> = on (cx, cz + dz)): that neighbour shares an edge with the footprint and draws the join,
        /// so the elbow would be a second, dead-end run under see-through art.</summary>
        public static bool CornerStubWanted(bool pipeBesideX, bool pipeBesideZ) => !pipeBesideX && !pipeBesideZ;

        /// <summary>SCRAPPER_PIPE_REDRAW_ASKED_TWICE_NOW (owner live 2026-10-23, "bad art alignment"): a fixture built ON a pipe
        /// (<paramref name="onPipeFixture"/>, PlaceWorker_RM_OnPipe: a sprinkler head) with the pipe still on its cell
        /// (<paramref name="pipeOnItsCell"/>) is part of the run, so the pipes beside it draw no end flange toward it (measured:
        /// those flanges were the dark bands across a run either side of every head) and the pipe under it is not hidden.</summary>
        public static bool JoinsAsPartner(bool onPipeFixture, bool pipeOnItsCell) => !(onPipeFixture && pipeOnItsCell);

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

        /// <summary>
        /// PIPE_JOINS_REDRAW_RISER_ELBOW_AND_COLLAR (owner 2026-10-24: "joins look horrible ... The collar by the tank is
        /// superimposed and odd. the corner has no treatment at all in the north. In the south there is a crude "cap" graphic").
        /// A pipe cell (cx, cz) beside a 2x2 universal tank on its west or east (dx = +1: the tank is east) meets the tank's
        /// drawn port at mid-height (<paramref name="portZ"/>, TankPortGeometry.PortPoint), not at the cell's centre row. The
        /// pipe bends onto that height in the bore's own cross-section (a strip of the straight tile, StripQuads) instead of
        /// square straights and a flange laid over the nozzle. <paramref name="mask"/> = the cell's linked-atlas mask (Up 1,
        /// Right 2, Down 4, Left 8; the link patch leaves the tank's side out). Three cases (laid out offline first,
        /// Tools/fw_scenes_pipejoins.py riser_after, judged on its sheets):
        ///   Gentle  -- the cell carries only this run (mask = the side away from the tank, or nothing): no cell tile; one S
        ///              bend from the far edge onto the port's height;
        ///   Fitting -- the cell has an arm toward the port's row: the atlas's own tee/elbow, hub and all, drawn AT the port's
        ///              height (FittingMask, FittingZ); the cell keeps its own tile when it has other arms (PlainTile);
        ///   Elbow   -- otherwise: the cell's tile plus a half arm toward the port's row, cut where a quarter bend of radius
        ///              ElbowRadius turns it into the port (CellMask, shown between CropZ0 and CropZ1).
        /// Every case then runs on along the port's height from the shared edge to <paramref name="runToX"/> (the footprint's
        /// centre with the under-run on, else just under the drawn nozzle). Null when dx is not +1 / -1.
        /// </summary>
        public static RiserPlan RiserBend(int cx, int cz, int dx, int mask, double portZ, double runToX)
        {
            if (Math.Abs(dx) != 1) return null;
            double x = cx + 0.5, z = cz + 0.5, edge = x + dx * 0.5;
            int away = dx > 0 ? LinkLeft : LinkRight, into = dx > 0 ? LinkRight : LinkLeft;
            mask &= ~into;   // a link toward the tank (vanilla linking to a pipe under it) is the riser itself, not an arm
            int sg = portZ > z ? 1 : -1;
            int vert = sg > 0 ? LinkUp : LinkDown, opp = sg > 0 ? LinkDown : LinkUp;
            var plan = new RiserPlan { CellMask = -1, FittingMask = -1, CropZ0 = cz, CropZ1 = cz + 1, Path = new System.Collections.Generic.List<double[]>() };
            double[] run = { 0, edge, portZ, runToX, portZ };
            if (mask == away || mask == 0)
            {
                plan.Kind = RiserKind.Gentle;
                plan.Path.AddRange(SBend(x - dx * 0.5, z, edge, portZ));
            }
            else if ((mask & vert) != 0)
            {
                plan.Kind = RiserKind.Fitting;
                int rest = mask & ~vert;
                plan.PlainTile = rest != 0;
                if (rest != 0) plan.CellMask = mask;
                plan.FittingMask = vert | into | (rest != 0 ? opp : 0);
                plan.FittingZ = portZ;
            }
            else
            {
                plan.Kind = RiserKind.Elbow;
                plan.CellMask = mask | vert;
                double z0 = portZ - sg * ElbowRadius;
                if (sg > 0) plan.CropZ1 = z0; else plan.CropZ0 = z0;
                double ccx = x + dx * ElbowRadius;
                plan.Path.Add(new double[] { 1, ccx, z0, ElbowRadius, dx > 0 ? 180 : 0, -dx * sg * 90 });
                plan.Path.Add(new double[] { 0, ccx, portZ, edge, portZ });
            }
            plan.Path.Add(run);
            return plan;
        }

        public const int LinkUp = 1, LinkRight = 2, LinkDown = 4, LinkLeft = 8;

        /// <summary>True when the path <paramref name="path"/> ends west of where it starts (a riser into a tank on the pipe's
        /// west): StripQuads' "left of travel" is then south, so the strip swaps its two rims to keep the tile's north up.</summary>
        public static bool TravelsWest(System.Collections.Generic.List<double[]> path)
        {
            if (path == null || path.Count == 0) return false;
            SegmentAt(path[0], 0, out double x0, out _, out _, out _);
            SegmentAt(path[path.Count - 1], 1, out double x1, out _, out _, out _);
            return x1 < x0;
        }

        /// <summary>The quarter bend's radius where an elbow riser turns into the port (cell units).</summary>
        public const double ElbowRadius = 0.22;

        /// <summary>Half the width of a bent strip: the bore is 0.136 cell wide in every look (measured), plus its rim shadow.</summary>
        public const double BoreHalf = 0.12;

        /// <summary>With the under-run off, how far a riser runs on past the shared edge, under the tank's drawn nozzle.</summary>
        public const double UnderNozzle = 0.15;

        public enum RiserKind { Gentle, Fitting, Elbow }

        /// <summary>RiserBend's answer. Path segments: {0, x0, z0, x1, z1} a line; {1, cx, cz, r, a0, sweep} an arc (degrees,
        /// counter-clockwise from east), in travel order from the pipe cell into the tank.</summary>
        public sealed class RiserPlan
        {
            public RiserKind Kind;
            /// <summary>The cell's own tile is drawn as the plain linked atlas would draw it (the Print skip leaves it).</summary>
            public bool PlainTile;
            /// <summary>The atlas tile the riser draws on the cell itself (Elbow: cropped to CropZ0..CropZ1); -1 none.</summary>
            public int CellMask;
            public double CropZ0, CropZ1;
            /// <summary>The atlas tile drawn centred at (cell x, FittingZ) (Fitting); -1 none.</summary>
            public int FittingMask;
            public double FittingZ;
            public System.Collections.Generic.List<double[]> Path;
        }

        /// <summary>Two equal arcs from (x0, z0) heading along x to (x1, z1) heading along x; a line when level.</summary>
        public static System.Collections.Generic.List<double[]> SBend(double x0, double z0, double x1, double z1)
        {
            var list = new System.Collections.Generic.List<double[]>();
            double w = x1 - x0, h = z1 - z0;
            if (Math.Abs(h) < 1e-6) { list.Add(new double[] { 0, x0, z0, x1, z1 }); return list; }
            int sx = w > 0 ? 1 : -1, sz = h > 0 ? 1 : -1;
            double th = 2 * Math.Atan2(Math.Abs(h), Math.Abs(w));
            double r = Math.Abs(w) / (2 * Math.Sin(th));
            double a0 = sx > 0 ? -90 * sz : 180 + 90 * sz;
            double sweep = sz * sx * th * 180 / Math.PI;
            double midX = x0 + sx * r * Math.Sin(th), midZ = z0 + sz * r * (1 - Math.Cos(th));
            double c2x = x1, c2z = z1 - sz * r;
            list.Add(new double[] { 1, x0, z0 + sz * r, r, a0, sweep });
            list.Add(new double[] { 1, c2x, c2z, r, Math.Atan2(midZ - c2z, midX - c2x) * 180 / Math.PI, -sweep });
            return list;
        }

        /// <summary>A point and unit heading along one path segment at fraction f.</summary>
        public static void SegmentAt(double[] seg, double f, out double px, out double pz, out double tx, out double tz)
        {
            if (seg[0] == 0)
            {
                double len = Math.Sqrt((seg[3] - seg[1]) * (seg[3] - seg[1]) + (seg[4] - seg[2]) * (seg[4] - seg[2]));
                px = seg[1] + (seg[3] - seg[1]) * f; pz = seg[2] + (seg[4] - seg[2]) * f;
                tx = len > 0 ? (seg[3] - seg[1]) / len : 1; tz = len > 0 ? (seg[4] - seg[2]) / len : 0;
                return;
            }
            double a = (seg[4] + seg[5] * f) * Math.PI / 180, s = Math.Sign(seg[5]);
            px = seg[1] + seg[3] * Math.Cos(a); pz = seg[2] + seg[3] * Math.Sin(a);
            tx = -Math.Sin(a) * s; tz = Math.Cos(a) * s;
        }

        public static double SegmentLength(double[] seg) => seg[0] == 0
            ? Math.Sqrt((seg[3] - seg[1]) * (seg[3] - seg[1]) + (seg[4] - seg[2]) * (seg[4] - seg[2]))
            : Math.Abs(seg[5]) * Math.PI / 180 * seg[3];

        /// <summary>One quad of a bent strip: corners in print order (start right, start left, end left, end right) as
        /// x, z pairs, and its slice of the straight east-west tile along the run (U0..U1, within one tile).</summary>
        public struct StripQuad
        {
            public double X0, Z0, X1, Z1, X2, Z2, X3, Z3, U0, U1;
        }

        /// <summary>
        /// The straight tile's cross-section carried along a path, as the offline compositor draws it (fw_compositor
        /// Scene.strip): u = distance along the path (wrapped to the tile, so a quad never spans a tile seam), the tile's north
        /// side on the LEFT of travel, halfW either side. Arcs are cut into steps of at most 8 degrees.
        /// </summary>
        public static System.Collections.Generic.List<StripQuad> StripQuads(System.Collections.Generic.List<double[]> path, double halfW)
        {
            var quads = new System.Collections.Generic.List<StripQuad>();
            if (path == null) return quads;
            double s = 0;
            foreach (double[] seg in path)
            {
                double len = SegmentLength(seg);
                if (len < 1e-9) continue;
                int steps = seg[0] == 0 ? 1 : Math.Max(1, (int)Math.Ceiling(Math.Abs(seg[5]) / 8.0));
                var fs = new System.Collections.Generic.List<double>();
                for (int k = 0; k <= steps; k++) fs.Add((double)k / steps);
                // a cut at every whole tile length along the run
                for (double w = Math.Floor(s) + 1; w < s + len - 1e-9; w += 1) fs.Add((w - s) / len);
                fs.Sort();
                for (int k = 0; k + 1 < fs.Count; k++)
                {
                    double fa = fs[k], fb = fs[k + 1];
                    if (fb - fa < 1e-9) continue;
                    double sa = s + fa * len, sb = s + fb * len, tile = Math.Floor(sa + 1e-9);
                    SegmentAt(seg, fa, out double ax, out double az, out double atx, out double atz);
                    SegmentAt(seg, fb, out double bx, out double bz, out double btx, out double btz);
                    // left of travel = heading turned a quarter counter-clockwise (-tz, tx)
                    quads.Add(new StripQuad
                    {
                        X0 = ax + atz * halfW, Z0 = az - atx * halfW,
                        X1 = ax - atz * halfW, Z1 = az + atx * halfW,
                        X2 = bx - btz * halfW, Z2 = bz + btx * halfW,
                        X3 = bx + btz * halfW, Z3 = bz - btx * halfW,
                        U0 = sa - tile, U1 = Math.Min(1.0, sb - tile)
                    });
                }
                s += len;
            }
            return quads;
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
