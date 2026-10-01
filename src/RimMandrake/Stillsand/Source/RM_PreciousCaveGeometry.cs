using System;
using System.Collections.Generic;

namespace RimMandrake.Stillsand
{
    // STILLSAND_PRECIOUS_CAVES_1 — the pure geometry of the rare rock and its cave.
    //
    // System.Math only, no Verse/Unity, so the offline selftest
    // (Source/SelfTest, run by src/RimMandrake/Utils/selftest_precious_caves.py)
    // compiles THIS file and exercises the real code, not a copy of it.
    //
    // Grids are row-major bool[] (index = z * width + x), x = east, z = north,
    // matching RimWorld's IntVec3 map space. Directions are map-space unit
    // vectors (dx east, dz north).
    public static class RM_PreciousCaveGeometry
    {
        private static readonly string[] Compass =
        {
            "north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west",
        };

        /// <summary>Eight-point compass word for a map-space offset (x east, z north).
        /// A zero offset reads as "centre".</summary>
        public static string CompassWord(double dx, double dz)
        {
            if (Math.Abs(dx) < 1e-9 && Math.Abs(dz) < 1e-9)
            {
                return "centre";
            }
            double deg = Math.Atan2(dx, dz) * 180.0 / Math.PI; // clockwise from north
            if (deg < 0)
            {
                deg += 360.0;
            }
            int idx = (int)Math.Floor((deg + 22.5) / 45.0) % 8;
            return Compass[idx];
        }

        /// <summary>Semi-axes of an area-preserving yardang: area ≈ π·a·b with a = aspect·b.</summary>
        public static void YardangAxes(int area, double aspect, out double a, out double b)
        {
            aspect = Math.Max(1.0, aspect);
            a = Math.Sqrt(Math.Max(1, area) * aspect / Math.PI);
            b = a / aspect;
        }

        /// <summary>True when an offset (du along the wind, downwind positive;
        /// dv across it) lies inside the yardang. The ellipse tapers downwind:
        /// a blunt head facing into the wind and a narrowing tail, the shape
        /// wind-carved rock takes. taper 0 is a plain ellipse.</summary>
        public static bool InYardang(double du, double dv, double a, double b, double taper)
        {
            if (a <= 0 || b <= 0)
            {
                return false;
            }
            double u = du / a;
            if (u < -1 || u > 1)
            {
                return false;
            }
            double width = b * (1.0 - taper * Math.Max(0.0, u));
            if (width <= 0)
            {
                return false;
            }
            double v = dv / width;
            return u * u + v * v <= 1.0;
        }

        /// <summary>For every rock cell, its 8-neighbour (Chebyshev) step distance to the
        /// nearest non-rock cell (or to the map edge, which counts as open). Non-rock cells
        /// are 0. Chebyshev, not Manhattan: Chebyshev never exceeds the Euclidean distance,
        /// so a round chamber of radius depth-2 cannot breach the rock diagonally.</summary>
        public static int[] DepthMap(bool[] rock, int w, int h)
        {
            int[] depth = new int[w * h];
            Queue<int> q = new Queue<int>();
            for (int z = 0; z < h; z++)
            {
                for (int x = 0; x < w; x++)
                {
                    int i = z * w + x;
                    if (!rock[i])
                    {
                        depth[i] = 0;
                        q.Enqueue(i);
                    }
                    else if (x == 0 || z == 0 || x == w - 1 || z == h - 1)
                    {
                        depth[i] = 1;
                        q.Enqueue(i);
                    }
                    else
                    {
                        depth[i] = int.MaxValue;
                    }
                }
            }
            while (q.Count > 0)
            {
                int i = q.Dequeue();
                int x = i % w;
                int z = i / w;
                int d = depth[i] + 1;
                for (int oz = -1; oz <= 1; oz++)
                {
                    for (int ox = -1; ox <= 1; ox++)
                    {
                        int nx = x + ox;
                        int nz = z + oz;
                        if ((ox != 0 || oz != 0) && nx >= 0 && nz >= 0 && nx < w && nz < h)
                        {
                            Relax(nz * w + nx);
                        }
                    }
                }

                void Relax(int j)
                {
                    if (rock[j] && depth[j] > d)
                    {
                        depth[j] = d;
                        q.Enqueue(j);
                    }
                }
            }
            return depth;
        }

        /// <summary>The cell of the given component deepest inside the rock; ties go to
        /// the one nearest the component's centroid. Returns -1 for an empty list.</summary>
        public static int DeepestCell(IList<int> cells, int[] depth, int w)
        {
            if (cells == null || cells.Count == 0)
            {
                return -1;
            }
            double cx = 0, cz = 0;
            for (int k = 0; k < cells.Count; k++)
            {
                cx += cells[k] % w;
                cz += cells[k] / w;
            }
            cx /= cells.Count;
            cz /= cells.Count;
            int best = -1;
            int bestDepth = -1;
            double bestDist = double.MaxValue;
            for (int k = 0; k < cells.Count; k++)
            {
                int i = cells[k];
                int d = depth[i];
                double ddx = i % w - cx;
                double ddz = i / w - cz;
                double dist = ddx * ddx + ddz * ddz;
                if (d > bestDepth || (d == bestDepth && dist < bestDist))
                {
                    best = i;
                    bestDepth = d;
                    bestDist = dist;
                }
            }
            return best;
        }

        /// <summary>Chamber radius for a rock of this many cells whose deepest cell is
        /// `depthAtCentre` from open ground: sized to the rock (≈ √area / 5), never
        /// thinner than a 1-cell rock rim, clamped to [minR, maxR]. 0 means the rock
        /// is too thin to hold a chamber at all.</summary>
        public static int ChamberRadius(int area, int depthAtCentre, int minR, int maxR)
        {
            int bySize = (int)Math.Round(Math.Sqrt(Math.Max(0, area)) / 5.0);
            int byDepth = depthAtCentre - 2; // keep at least one cell of rock rim
            int r = Math.Min(Math.Min(bySize, byDepth), maxR);
            if (r < minR)
            {
                r = byDepth >= minR ? minR : 0;
            }
            return Math.Max(0, r);
        }

        /// <summary>Marches from (cx, cz) along (dx, dz) and returns the rock cells the
        /// ray crosses until it first leaves the rock (the tunnel), and the first open
        /// cell beyond it (the mouth's outside step). False when the ray reaches the
        /// map edge still inside rock, or never meets rock-then-open.</summary>
        public static bool RayToOpen(bool[] rock, int w, int h, int cx, int cz, double dx, double dz,
            List<int> tunnel, out int exit)
        {
            tunnel.Clear();
            exit = -1;
            double len = Math.Sqrt(dx * dx + dz * dz);
            if (len < 1e-9)
            {
                return false;
            }
            dx /= len;
            dz /= len;
            int last = -1;
            int maxSteps = (w + h) * 4;
            for (int s = 0; s <= maxSteps; s++)
            {
                double t = s * 0.5;
                int x = (int)Math.Round(cx + dx * t);
                int z = (int)Math.Round(cz + dz * t);
                if (x < 0 || z < 0 || x >= w || z >= h)
                {
                    return false;
                }
                int i = z * w + x;
                if (i == last)
                {
                    continue;
                }
                last = i;
                if (rock[i])
                {
                    tunnel.Add(i);
                }
                else if (s > 0)
                {
                    exit = i;
                    return true;
                }
            }
            return false;
        }

        /// <summary>The shade-face mouth: tries the shadow direction first, then fans out
        /// ±15° steps up to ±75°, so the mouth always opens on the side away from the
        /// sun (dot with the shadow direction stays positive). Returns the angle used
        /// (degrees off the shadow direction), or NaN when no ray reaches open ground.</summary>
        public static double ShadeMouth(bool[] rock, int w, int h, int cx, int cz, double sdx, double sdz,
            List<int> tunnel, out int exit)
        {
            double[] fan = { 0, 15, -15, 30, -30, 45, -45, 60, -60, 75, -75 };
            for (int k = 0; k < fan.Length; k++)
            {
                double r = fan[k] * Math.PI / 180.0;
                double c = Math.Cos(r);
                double s = Math.Sin(r);
                double dx = sdx * c - sdz * s;
                double dz = sdx * s + sdz * c;
                if (RayToOpen(rock, w, h, cx, cz, dx, dz, tunnel, out exit))
                {
                    return fan[k];
                }
            }
            tunnel.Clear();
            exit = -1;
            return double.NaN;
        }

        /// <summary>Weighted pick: index whose cumulative weight first exceeds roll01·total.
        /// Non-positive weights never win. -1 when nothing has weight.</summary>
        public static int WeightedPick(IList<double> weights, double roll01)
        {
            double total = 0;
            for (int i = 0; i < weights.Count; i++)
            {
                if (weights[i] > 0)
                {
                    total += weights[i];
                }
            }
            if (total <= 0)
            {
                return -1;
            }
            double target = Math.Min(Math.Max(roll01, 0.0), 0.999999999) * total;
            double acc = 0;
            int lastPositive = -1;
            for (int i = 0; i < weights.Count; i++)
            {
                if (weights[i] <= 0)
                {
                    continue;
                }
                lastPositive = i;
                acc += weights[i];
                if (target < acc)
                {
                    return i;
                }
            }
            return lastPositive;
        }
    }
}
