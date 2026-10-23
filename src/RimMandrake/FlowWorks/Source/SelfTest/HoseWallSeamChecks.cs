// HOSE_CLEAR_FIX_WALL_SEAM_LOOPHOLE + HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS (owner 2026-10-22: "We MUST fix the "goes under walls"
// problem"). Offline checks on the hose's wall test with an INDEPENDENT ruler: every wall assertion the hose suites carried over
// from Gimme Some Slack (HoseSelfTest.WallHits, HoseFuzz's "runs through a wall") measures with HoseMath.WallDepth itself, so
// when WallDepth read "distance to the edge of the sample's OWN cell" (9e9f153d4e, GSS round 4) a hose lying on the seam
// between two wall cells read depth ~0 and every one of those tests passed with it. The ruler here is the distance from the
// sample to the nearest WALKABLE cell box, written out in this file (the same quantity as CordWorld.Clearance, which the GSS
// cords have always used), so it cannot share a blind spot with the code under test.
//  S1 a straight hose along a seam through a one-cell-thick wall is refused (red on the per-cell rule);
//  S2 the two grazes the tolerance exists for still pass: a string-pulled line touching a wall corner, and one running along a
//     wall's face;
//  S3 the metric itself: WallDepth > ClipTolerance exactly when the independent depth is, over random points in random worlds;
//  S4 re-plans: the walkthrough's C3-north scene (reel o1 at (19,42), wall x=22 with its gap at z=42-43, free end (35,27)) and
//     a sweep of one-thick walls with one gap, each laid from a west-facing 2x2 reel with the straight lead-out: no laid pose
//     (flat or plump) has a sample deeper than CrossDepth (0.12, the hose's half-width) inside a wall by the independent ruler.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseWallSeamChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>Independent ruler: 0 on a walkable cell, else the distance from q to the nearest walkable cell box (3 when
        /// none lies within two cells).</summary>
        internal static double Depth(CordWorld w, V2 q)
        {
            Cell c = q.Floor;
            if (w.IsWalkable(c)) return 0;
            double best = 3;
            for (int dz = -2; dz <= 2; dz++)
                for (int dx = -2; dx <= 2; dx++)
                {
                    var n = new Cell(c.X + dx, c.Z + dz);
                    if (!w.IsWalkable(n)) continue;
                    double ex = Math.Max(Math.Max(n.X - q.X, 0), q.X - (n.X + 1));
                    double ez = Math.Max(Math.Max(n.Z - q.Z, 0), q.Z - (n.Z + 1));
                    best = Math.Min(best, Math.Sqrt(ex * ex + ez * ez));
                }
            return best;
        }

        /// <summary>Samples (every 0.02 cell, the first and last 0.5 cell skipped like HoseMath.Clear) deeper than
        /// ClipTolerance inside a wall by the independent ruler.</summary>
        internal static int DeepSamples(CordWorld w, IList<V2> pts, out V2 first) => DeepSamples(w, pts, HoseMath.ClipTolerance, false, out first);

        /// <summary>As above, deeper than <paramref name="tol"/>; wallsOnly counts only BlockKind.Wall cells (not the reel's own
        /// footprint, which LayFrom marks Device and the hose leaves from).</summary>
        internal static int DeepSamples(CordWorld w, IList<V2> pts, double tol, bool wallsOnly, out V2 first)
        {
            first = default;
            int hits = 0;
            double[] s = Geo.CumLen(pts);
            double L = s[s.Length - 1];
            for (int i = 1; i < pts.Count; i++)
            {
                double d = s[i] - s[i - 1];
                int k = Math.Max(1, (int)Math.Ceiling(d / 0.02));
                for (int j = 0; j < k; j++)
                {
                    double at = s[i - 1] + d * j / k;
                    if (at < 0.5 || L - at < 0.5) continue;
                    V2 q = pts[i - 1] + (pts[i] - pts[i - 1]) * (j / (double)k);
                    if (wallsOnly && w.BlockAt(q.Floor) != BlockKind.Wall) continue;
                    if (Depth(w, q) > tol) { if (hits == 0) first = q; hits++; }
                }
            }
            return hits;
        }

        private static CordWorld WallColumn(int W, int H, int x, int z0, int z1, params int[] gaps)
        {
            var w = new CordWorld(W, H);
            for (int z = z0; z <= z1; z++) if (!gaps.Contains(z)) w.SetBlocked(new Cell(x, z), BlockKind.Wall);
            return w;
        }

        /// <summary>S4's bar: a sample this deep inside a wall (by the independent ruler) is the hose's own half-width through
        /// the wall, a crossing; shallower is the corner/face graze HoseMath.Clear samples at 0.05 and allows to 0.06.</summary>
        public const double CrossDepth = 0.12;

        public static void Run(Action<string, Action> Case)
        {
            Case("HoseWall_S1_hose_on_a_seam_between_two_wall_cells_is_refused", () =>
            {
                var w = WallColumn(40, 20, 22, 2, 17);
                var seam = new List<V2> { new V2(18.5, 10.0), new V2(26.5, 10.0) };
                Assert(DeepSamples(w, seam, out _) > 0, "can-fail: the independent ruler must see the seam line inside the wall");
                Assert(!HoseMath.SegmentClear(w, seam[0], seam[1]), "SegmentClear passed a hose along z=10.0 through walls (22,9)/(22,10)");
                Assert(!HoseMath.Clear(w, seam), "Clear passed a hose along z=10.0 through walls (22,9)/(22,10)");
                // the live instrument (HoseProbe census "wallCross", proof_hose.py HW1) counts it
                Assert(HoseMath.WallCrossings(w, seam, out Cell wc) > 0 && wc.X == 22, "WallCrossings missed the seam crossing (first " + wc + ")");
                // a nearly flat line (the shaped return leg of the walkthrough's reel o1) is refused too
                Assert(!HoseMath.Clear(w, new List<V2> { new V2(18.3, 9.97), new V2(26.4, 10.04) }), "Clear passed a near-seam line through the wall");
                // and a horizontal wall crossed on its vertical seam
                var w2 = new CordWorld(20, 40);
                for (int x = 2; x <= 17; x++) w2.SetBlocked(new Cell(x, 22), BlockKind.Wall);
                Assert(!HoseMath.SegmentClear(w2, new V2(10.0, 18.5), new V2(10.0, 26.5)), "SegmentClear passed a hose along x=10.0 through walls (9,22)/(10,22)");
            });

            Case("HoseWall_S2_corner_and_face_grazes_still_pass", () =>
            {
                var w = new CordWorld(12, 12);
                w.SetBlocked(new Cell(5, 5), BlockKind.Wall);
                Assert(HoseMath.SegmentClear(w, new V2(3.0, 9.0), new V2(9.0, 3.0)), "a line touching only the corner (6,6) of a lone wall cell was refused");
                var col = WallColumn(40, 20, 22, 2, 17);
                Assert(HoseMath.SegmentClear(col, new V2(22.0, 4.0), new V2(22.0, 15.0)), "a line along the west face of a wall (x=22.0) was refused");
                Assert(HoseMath.SegmentClear(col, new V2(21.5, 1.5), new V2(23.5, 1.5)), "a line past the wall's end was refused");
                Assert(HoseMath.WallCrossings(w, new List<V2> { new V2(3.0, 9.0), new V2(9.0, 3.0) }, out _) == 0
                    && HoseMath.WallCrossings(col, new List<V2> { new V2(22.0, 4.0), new V2(22.0, 15.0) }, out _) == 0,
                    "WallCrossings counted a corner or face graze as a crossing");
                // can-fail: a line one cell into the wall is refused
                Assert(!HoseMath.SegmentClear(col, new V2(22.5, 4.0), new V2(22.5, 15.0)), "can-fail: a line down the middle of the wall passed");
            });

            Case("HoseWall_S3_WallDepth_agrees_with_the_independent_ruler", () =>
            {
                var r = new Random(20261022);
                int n = 0, bad = 0;
                string firstBad = null;
                for (int k = 0; k < 60; k++)
                {
                    var w = new CordWorld(14, 14);
                    for (int b = 0; b < 30; b++) w.SetBlocked(new Cell(r.Next(14), r.Next(14)), BlockKind.Wall);
                    for (int i = 0; i < 400; i++)
                    {
                        // a third of the points on a cell seam or corner, where the per-cell rule read 0
                        double x = 2 + r.NextDouble() * 10, z = 2 + r.NextDouble() * 10;
                        int m = i % 3;
                        if (m == 1) z = Math.Round(z) + (r.NextDouble() - 0.5) * 0.1;
                        if (m == 2) { x = Math.Round(x); z = Math.Round(z); }
                        var q = new V2(x, z);
                        n++;
                        bool want = Depth(w, q) > HoseMath.ClipTolerance, got = HoseMath.WallDepth(w, q) > HoseMath.ClipTolerance;
                        if (want != got) { bad++; if (firstBad == null) firstBad = q + " ruler " + Depth(w, q).ToString("0.000") + " WallDepth " + HoseMath.WallDepth(w, q).ToString("0.000"); }
                    }
                }
                Assert(bad == 0, bad + "/" + n + " points where WallDepth disagrees with the distance to the nearest walkable cell, first " + firstBad);
            });

            Case("HoseWall_S4_replanned_lays_never_cross_a_wall", () =>
            {
                var fails = new List<string>();
                int laid = 0;
                void Try(string name, CordWorld w, HoseReelRect reel, Cell far, double maxLen, ulong seed)
                {
                    // as RM_MapComponent_Hoses.LayFrom: the nozzled reel's own footprint is solid to its own hose
                    for (int x = reel.X0; x < reel.X0 + reel.W; x++) for (int z = reel.Z0; z < reel.Z0 + reel.H; z++) w.SetBlocked(new Cell(x, z), BlockKind.Device);
                    var p = new HoseShapeParams { MaxLength = maxLen };
                    HoseLay lay = HoseMath.LayAlong(w, reel.Mouth, new List<Cell>(), far.Centre, p, seed, null, reel.Outward);
                    if (!lay.Ok) return;
                    laid++;
                    foreach (var (pose, what) in new[] { (lay.Flat, "flat"), (lay.Plump, "plump") })
                    {
                        int h = DeepSamples(w, pose, CrossDepth, true, out V2 at);
                        if (h > 0) fails.Add(name + " " + what + ": " + h + " samples inside a wall, first " + at);
                    }
                }
                // the walkthrough's C3 north (RM_fw_walkthrough_20261022b map C, hose_audit.md D1): wall x=22 z 22..41 and 44..60
                {
                    var w = new CordWorld(60, 70);
                    for (int z = 22; z <= 60; z++) if (z != 42 && z != 43) w.SetBlocked(new Cell(22, z), BlockKind.Wall);
                    for (ulong s = 1; s <= 12; s++) Try("C3north seed " + s, w, new HoseReelRect(18, 42, 2, 2), new Cell(35, 27), 40, s);
                }
                // a sweep: one-thick walls (vertical and horizontal) with one gap, reel west/south of it, end beyond
                var r = new Random(4222);
                for (int k = 0; k < 160; k++)
                {
                    int W = 40, H = 40;
                    var w = new CordWorld(W, H);
                    bool vertical = k % 2 == 0;
                    int line = r.Next(17, 23), gap = r.Next(8, 32);
                    for (int t = 4; t < 36; t++) if (t != gap && t != gap + 1)
                            w.SetBlocked(vertical ? new Cell(line, t) : new Cell(t, line), BlockKind.Wall);
                    int a = r.Next(8, 30);
                    var reel = vertical ? new HoseReelRect(line - r.Next(3, 7), a, 2, 2) : new HoseReelRect(a, line - r.Next(3, 7), 2, 2);
                    reel.Rot = r.Next(4);
                    var far = vertical ? new Cell(line + r.Next(3, 12), r.Next(6, 34)) : new Cell(r.Next(6, 34), line + r.Next(3, 12));
                    Try("sweep " + k + " (" + (vertical ? "x=" : "z=") + line + " gap " + gap + ")", w, reel, far, 45, (ulong)(k + 1));
                }
                Assert(laid >= 40, "can-fail: only " + laid + " lays succeeded; the sweep proves nothing");
                Assert(fails.Count == 0, fails.Count + " laid poses cross a wall (of " + laid + " laid): " + string.Join(" | ", fails.Take(4)));
            });
        }
    }
}
