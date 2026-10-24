// HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS (owner 2026-10-23 22:15 and 22:25). The DRAWN hose centreline of three hard stations,
// measured by HoseCurveMetrics (a ruler that never calls the code it measures) against design/RimMandrake/
// flowworks_hose_geometry_g2_2026-10-23.md section 1: position (R1), slope along every fitting's axis (R2), curvature 0 at a
// straight lead and continuous everywhere (R3), |k| <= 1/MinBendRadius with the ends included (R4), two hoses on one fitting each on
// its own axis (R5) and length conserved between the slack and the charged pose (R6). The scenes ARE the review_map stations
// hose_hard_bends / hose_hard_maze / hose_hard_fittings (same local cells, Utils/review_map.py), laid as
// RM_MapComponent_Hoses.LayFrom does and drawn as DrawAll does (HoseMath.DrawnPose, then the mate as Mated does).
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseCurveChecks
    {
        internal const int Ox = 10, Oz = 10;
        internal const string Look = "Industrial";
        internal const int T = 30;

        /// <summary>One reel of a station, local cells. Dir = the nozzle's facing; End = the free end cell; Tank / Relay = the
        /// end couples to that tank's port or that reel's intake.</summary>
        internal sealed class Reel
        {
            public string Name;
            public int X, Z;
            public Cell Dir;
            public Cell End;
            public double MaxLength = 40;
            public string Tank;      // name of the station tank the end couples to
            public string RelayTo;   // name of the station reel the end feeds
            public bool MayRefuse;   // a refusal with a reason is the pass (no legal route at MinBendRadius)
            public string FedBy;     // set by the station: the reel that feeds this one
            internal HoseReelRect Rect;
        }

        internal sealed class Station
        {
            public string Name;
            public int W = 20, H = 16;
            public List<Cell> Walls = new List<Cell>();
            public Dictionary<string, (int x, int z)> Tanks = new Dictionary<string, (int, int)>();
            public List<Reel> Reels = new List<Reel>();
        }

        private static List<Cell> Row(int z, int x0, int x1) { var o = new List<Cell>(); for (int x = x0; x <= x1; x++) o.Add(new Cell(x, z)); return o; }
        private static List<Cell> Col(int x, int z0, int z1) { var o = new List<Cell>(); for (int z = z0; z <= z1; z++) o.Add(new Cell(x, z)); return o; }

        /// <summary>The three stations (local cells; review_map.py places the same layouts).</summary>
        internal static List<Station> Stations()
        {
            List<Station> all = StationsUnframed();
            // every station is walled in (review_map.py builds the same frame): without it the planner walks round the outside
            // of the maze (measured: serpentine 23.9 cells against ~55 inside)
            foreach (Station st in all)
            {
                st.Walls.AddRange(Row(-1, -1, st.W)); st.Walls.AddRange(Row(st.H, -1, st.W));
                st.Walls.AddRange(Col(-1, 0, st.H - 1)); st.Walls.AddRange(Col(st.W, 0, st.H - 1));
            }
            return all;
        }

        private static List<Station> StationsUnframed()
        {
            var s1 = new Station { Name = "hose_hard_bends" };
            s1.Reels.Add(new Reel { Name = "uturn", X = 3, Z = 10, Dir = new Cell(1, 0), End = new Cell(1, 10) });
            s1.Reels.Add(new Reel { Name = "sbend", X = 7, Z = 1, Dir = new Cell(0, 1), End = new Cell(10, 8) });
            s1.Tanks["t1"] = (9, 6);
            s1.Reels.Add(new Reel { Name = "short", X = 16, Z = 5, Dir = new Cell(-1, 0), End = new Cell(11, 7), Tank = "t1" });
            // a 1-wide L corridor below a south-facing reel: no legal bend at R = 1.2, so a refusal with its reason passes
            s1.Walls.AddRange(Col(0, 0, 3)); s1.Walls.AddRange(Col(2, 1, 3)); s1.Walls.AddRange(Row(2, 3, 6)); s1.Walls.AddRange(Row(0, 1, 6));
            s1.Reels.Add(new Reel { Name = "corridor", X = 0, Z = 4, Dir = new Cell(0, -1), End = new Cell(5, 1), MayRefuse = true });

            var s2 = new Station { Name = "hose_hard_maze" };
            // a 3-wide serpentine, three 180-degree turns inside x 0..12 (a 2-wide channel cannot hold a 2 x Rmin = 2.4 U-turn)
            s2.Walls.AddRange(Row(11, 0, 9)); s2.Walls.AddRange(Row(7, 3, 12)); s2.Walls.AddRange(Row(3, 0, 9)); s2.Walls.AddRange(Col(13, 0, 15));
            s2.Reels.Add(new Reel { Name = "serpentine", X = 0, Z = 13, Dir = new Cell(1, 0), End = new Cell(2, 1), MaxLength = 70 });
            // a long straight-ish run: the slack drape must stay smooth and the charged hose keep its length
            s2.Reels.Add(new Reel { Name = "slackrun", X = 16, Z = 14, Dir = new Cell(0, -1), End = new Cell(17, 0) });

            var s3 = new Station { Name = "hose_hard_fittings", W = 22 };
            // two hose ends meeting at 90 degrees (mate, HoseSpliceMath)
            s3.Reels.Add(new Reel { Name = "mateA", X = 0, Z = 10, Dir = new Cell(1, 0), End = new Cell(6, 11) });
            s3.Reels.Add(new Reel { Name = "mateB", X = 6, Z = 4, Dir = new Cell(0, 1), End = new Cell(6, 10) });
            // a relay chain: feed into the relay's nozzle side (the owner's screenshot 221228), the relay's own hose behind it
            s3.Reels.Add(new Reel { Name = "feed", X = 0, Z = 1, Dir = new Cell(1, 0), End = new Cell(5, 2), RelayTo = "relay" });
            s3.Reels.Add(new Reel { Name = "relay", X = 6, Z = 1, Dir = new Cell(-1, 0), End = new Cell(12, 3) });
            // one tank fed on both faces: straight on from the east, from the side (north) on the west
            s3.Tanks["t2"] = (11, 7);
            s3.Reels.Add(new Reel { Name = "tankE", X = 19, Z = 7, Dir = new Cell(-1, 0), End = new Cell(13, 8), Tank = "t2" });
            s3.Reels.Add(new Reel { Name = "tankW", X = 8, Z = 12, Dir = new Cell(0, -1), End = new Cell(10, 7), Tank = "t2" });
            foreach (Reel r in s3.Reels) if (r.RelayTo != null) s3.Reels.First(q => q.Name == r.RelayTo).FedBy = r.Name;
            return new List<Station> { s1, s2, s3 };
        }

        internal static HoseReelRect Facing(int x0, int z0, Cell dir)
        {
            for (int rot = 0; rot < 4; rot++)
            {
                var r = new HoseReelRect(x0, z0, 2, 2) { Rot = rot };
                if (r.Outward.HasValue && r.Outward.Value.X * dir.X + r.Outward.Value.Z * dir.Z > 0.9) return r;
            }
            throw new Exception("no reel facing " + dir.X + "," + dir.Z);
        }

        /// <summary>The station's world as RM_MapComponent_Hoses.World() builds it: walls and tanks impassable, other reels a
        /// crossing cost.</summary>
        internal static CordWorld World(Station st)
        {
            var w = new CordWorld(Ox + st.W + 10, Oz + st.H + 10);
            foreach (Cell c in st.Walls) w.SetBlocked(new Cell(c.X + Ox, c.Z + Oz), BlockKind.Wall);
            foreach (var t in st.Tanks.Values)
                for (int x = 0; x < 2; x++) for (int z = 0; z < 2; z++) w.SetBlocked(new Cell(t.x + x + Ox, t.z + z + Oz), BlockKind.Wall);
            foreach (Reel r in st.Reels)
            {
                r.Rect = Facing(r.X + Ox, r.Z + Oz, r.Dir);
                for (int x = 0; x < 2; x++) for (int z = 0; z < 2; z++) w.SetExtraCost(new Cell(r.Rect.X0 + x, r.Rect.Z0 + z), HoseMath.BuildingCrossCost);
            }
            return w;
        }

        /// <summary>A laid and drawn reel of a station.</summary>
        internal sealed class Drawn
        {
            public string Station, Reel, PoseName;
            public HoseLay Lay;
            public List<V2> Pts;
            public HoseCurveMetrics.EndSpec Start, End;
            public bool Fed, MayRefuse;
            public double RefLen;
            public string Diag;
            /// <summary>Why this open end did not couple to the open end beside it (null = it did, or has no partner).</summary>
            public string NoMate;
            public HoseCurveMetrics.Report Rep;
        }

        internal static readonly (string name, double e, int since)[] Poses =
            { ("flat", 0, int.MaxValue / 2), ("plump", 1, int.MaxValue / 2), ("filling", 0.5, 15), ("settling", 1, 45) };

        /// <summary>Every reel of every station laid as LayFrom does, then drawn in every pose as DrawAll does.</summary>
        internal static List<Drawn> DrawAll()
        {
            var o = new List<Drawn>();
            var p = new HoseShapeParams();
            double kmax = 1 / Math.Max(0.45, p.MinBendRadius);
            double vis = HoseMath.VisibleWidth(1, p.PlumpAmount);
            foreach (Station st in Stations())
            {
                CordWorld w = World(st);
                var lays = new Dictionary<string, (HoseLay lay, V2? portAt, V2 portAxis, HoseCurveMetrics.EndSpec end, HoseCurveMetrics.EndSpec start)>();
                ulong seed = 1;
                foreach (Reel r in st.Reels)
                {
                    var far = new Cell(r.End.X + Ox, r.End.Z + Oz);
                    V2 end = far.Centre;
                    V2? inward = null;
                    V2? portAt = null;
                    V2 portAxis = default;
                    HoseCurveMetrics.EndSpec es = HoseCurveMetrics.EndSpec.Free(end, "free");
                    if (r.RelayTo != null)
                    {
                        Reel relay = st.Reels.First(q => q.Name == r.RelayTo);
                        end = HoseRelay.DrawnEnd(relay.Rect, far, Look, true, out V2 d);
                        inward = d;
                        es = HoseCurveMetrics.EndSpec.Fitting(end, -d, HoseRelay.EndStraight, "relay-intake");
                    }
                    else if (r.Tank != null)
                    {
                        var t = st.Tanks[r.Tank];
                        int bx = t.x + Ox, bz = t.z + Oz;
                        int sx = far.X < bx ? 1 : far.X >= bx + 2 ? -1 : 0, sz = sx != 0 ? 0 : far.Z < bz ? 1 : -1;
                        if (!TankPortGeometry.HosePort("RM_LiquidTank", Look, bx, bz, 2, 2, far.X, far.Z, sx, sz, out V2 port))
                            throw new Exception(st.Name + "/" + r.Name + ": end cell is not on a tank port face");
                        portAt = port;
                        portAxis = new V2(sx, sz);
                        es = HoseCurveMetrics.EndSpec.Fitting(port - portAxis * 0.5, -portAxis, HoseRelay.EndStraight, "tank-port");
                    }
                    // LayFrom: an unfed nozzled reel's own footprint is solid and its hose leaves along Outward
                    V2? outward = r.FedBy == null ? r.Rect.Outward : null;
                    var held = new List<Cell>();
                    if (outward.HasValue)
                        for (int x = 0; x < 2; x++) for (int z = 0; z < 2; z++) { var c = new Cell(r.Rect.X0 + x, r.Rect.Z0 + z); held.Add(c); w.SetBlocked(c, BlockKind.Device); }
                    var sp = new HoseShapeParams { MaxLength = r.MaxLength };
                    HoseLay lay;
                    ulong sd = seed++;
                    // step 3: a tank-port end is laid onto the port's axis as EnsureLay does (HoseMath.PortLay)
                    try { lay = HoseMath.PortLay((e1, in1) => HoseMath.LayAlong(w, r.Rect.Mouth, new List<Cell>(), e1, sp, sd, in1, outward), end, inward, portAt, portAxis); }
                    finally { foreach (Cell c in held) { w.SetBlocked(c, BlockKind.None); w.SetExtraCost(c, HoseMath.BuildingCrossCost); } }
                    // the nozzle's straight run is owed by every reel (R2), the fed relay's included (KNOWN: it shares the nozzle)
                    V2 ax = r.Rect.Outward ?? new V2(r.Dir.X, r.Dir.Z);
                    var ss = HoseCurveMetrics.EndSpec.Fitting(r.Rect.Mouth, ax, HoseReelRect.OutletStraight, "nozzle");
                    lays[r.Name] = (lay, portAt, portAxis, es, ss);
                }
                // mates: open free ends within one cell of each other (RefreshMates), solved on the flat lays
                var mates = new Dictionary<string, (HoseSpliceMath.Mate m, bool isA)>();
                var unmated = new Dictionary<string, string>();
                var names = st.Reels.Where(r => r.Tank == null && r.RelayTo == null && lays[r.Name].lay.Ok).Select(r => r.Name).ToList();
                for (int i = 0; i < names.Count; i++)
                    for (int j = i + 1; j < names.Count; j++)
                    {
                        Reel a = st.Reels.First(q => q.Name == names[i]), b = st.Reels.First(q => q.Name == names[j]);
                        if (mates.ContainsKey(a.Name) || mates.ContainsKey(b.Name)) continue;
                        if (Math.Max(Math.Abs(a.End.X - b.End.X), Math.Abs(a.End.Z - b.End.Z)) > 1) continue;
                        List<V2> A = lays[a.Name].lay.Flat, B = lays[b.Name].lay.Flat;
                        HoseSpliceMath.Mate m = HoseSpliceMath.MatePair(A, B, A[A.Count - 1], kmax, vis, out _, out _,
                            lays[a.Name].lay.Lead0, lays[b.Name].lay.Lead0);
                        if (m == null)
                        {
                            // two open ends within a cell of each other must couple (RefreshMates); none fitting is a failure
                            unmated[a.Name] = unmated[b.Name] = "no mate fits with " + b.Name + "/" + a.Name + " (length and start leads kept): " + HoseClothoid.TailWhy;
                            continue;
                        }
                        mates[a.Name] = (m, true);
                        mates[b.Name] = (m, false);
                    }
                foreach (Reel r in st.Reels)
                {
                    var L = lays[r.Name];
                    foreach (var pose in Poses)
                    {
                        var d = new Drawn { Station = st.Name, Reel = r.Name, PoseName = pose.name, Lay = L.lay, Start = L.start, End = L.end,
                            Fed = r.FedBy != null, MayRefuse = r.MayRefuse, NoMate = unmated.TryGetValue(r.Name, out string nm) ? nm : null };
                        o.Add(d);
                        if (!L.lay.Ok) continue;
                        List<V2> pts = HoseMath.DrawnPose(L.lay, pose.e, pose.since, T, p.PlumpAmount, L.portAt, L.portAxis);
                        if (mates.TryGetValue(r.Name, out var mm))
                        {
                            List<V2> q = HoseSpliceMath.MateEnd(pts, mm.m, mm.isA, kmax, vis, L.lay.Lead0);
                            if (q == null) d.Diag = "MateEnd null: " + HoseClothoid.TailWhy;
                            else pts = q;
                            V2 ax = mm.isA ? mm.m.Axis : -mm.m.Axis;
                            d.End = HoseCurveMetrics.EndSpec.Fitting(mm.m.C, -ax, HoseSpliceMath.CouplingStraight(vis), "mate");
                        }
                        d.Pts = pts;
                        d.RefLen = L.lay.FlatLen;
                        d.Rep = HoseCurveMetrics.Measure(pts, d.Start, d.End, kmax, mates.ContainsKey(r.Name) && !HoseMath.G2On ? 0 : d.RefLen);
                    }
                }
            }
            return o;
        }

        /// <summary>A KNOWN owner item (design section 7): the fed relay's own hose leaves the nozzle its feed couples into.</summary>
        internal static bool KnownOnly(Drawn d) => d.Fed && d.Rep != null && d.Rep.Fails.All(f => f.StartsWith("R2-start") || f.StartsWith("R3-start"));

        /// <summary>The clothoid solver's running cost: solves, iterations, mean and total time.</summary>
        internal static string SolverCost()
        {
            double ms = HoseClothoid.Ticks * 1000.0 / System.Diagnostics.Stopwatch.Frequency;
            return $"clothoid solver: {HoseClothoid.Solves} solves, {HoseClothoid.Iters} iterations, {ms:F0} ms total, "
                + $"{(HoseClothoid.Solves > 0 ? ms / HoseClothoid.Solves : 0):F2} ms/solve; feasible {HoseClothoid.Feasibles} "
                + $"({HoseClothoid.FeasIters} it, {HoseClothoid.FeasTicks * 1000.0 / System.Diagnostics.Stopwatch.Frequency:F0} ms)"
                + $"; lays fitted {HoseMath.G2Done}/{HoseMath.G2Tried}";
        }

        internal static void Run(Action<string, Action> Case)
        {
            HoseClothoidChecks.Run(Case);
            List<Drawn> all = DrawAll();
            double kmax = 1 / Math.Max(0.45, new HoseShapeParams().MinBendRadius);
            foreach (Drawn d in all)
            {
                string id = $"HoseCurve {d.Station}/{d.Reel}/{d.PoseName}";
                Case(id, () =>
                {
                    if (!d.Lay.Ok)
                    {
                        if (d.MayRefuse && !string.IsNullOrEmpty(d.Lay.Reason)) return;
                        throw new Exception("refused: " + (d.Lay.Reason ?? "(no reason)"));
                    }
                    if (d.NoMate != null) throw new Exception(d.NoMate);
                    if (d.MayRefuse && !d.Rep.Ok) throw new Exception("laid through a sub-Rmin corridor: " + d.Rep.Line());
                    if (!d.Rep.Ok && !KnownOnly(d)) throw new Exception(d.Rep.Line() + (d.Lay.G2 ? " [g2" + (d.Lay.Rerouted ? " re-routed" : "") + "]" : " [shaped: " + d.Lay.G2Why + "]") + (d.Lay.PortWhy != null ? " {port: " + d.Lay.PortWhy + "}" : "") + (d.Diag != null ? " {" + d.Diag + "}" : ""));
                });
            }
            // R5 + splice: a mated pair is ONE curve through its coupling (A then B reversed)
            foreach (var g in all.Where(d => d.End.Name == "mate" || d.NoMate != null).GroupBy(d => d.Station + "/" + d.PoseName))
            {
                var pair = g.ToList();
                if (pair.Count != 2) continue;
                Case($"HoseCurve splice {g.Key}", () =>
                {
                    if (pair[0].NoMate != null) throw new Exception(pair[0].NoMate);
                    HoseCurveMetrics.Report r = HoseCurveMetrics.Splice(pair[0].Pts, pair[1].Pts, pair[0].Start, pair[1].Start, kmax, out double seam);
                    if (!r.Ok) throw new Exception($"seam {seam:0.000} " + r.Line());
                });
            }
        }

        /// <summary>Every case's numbers, one line each (the before/after record of design section 6).</summary>
        internal static void Report(string path)
        {
            var sb = new StringBuilder();
            foreach (Drawn d in DrawAll())
            {
                sb.Append($"{d.Station}/{d.Reel}/{d.PoseName}: ");
                if (!d.Lay.Ok) sb.Append("REFUSED " + d.Lay.Reason + (d.MayRefuse ? " (pass)" : "") + $" pathLen {d.Lay.PathLen:0.00}");
                else sb.Append((d.NoMate != null ? "FAIL (" + d.NoMate + ") " : d.Rep.Ok ? "PASS " : KnownOnly(d) ? "KNOWN " : "FAIL ") + d.Rep.Line() + (d.Lay.G2 ? " [g2" + (d.Lay.Rerouted ? " re-routed" : "") + "]" : " [shaped: " + d.Lay.G2Why + "]") + (d.Lay.PortWhy != null ? " {port: " + d.Lay.PortWhy + "}" : ""));
                sb.Append('\n');
            }
            System.IO.File.WriteAllText(path, sb.ToString());
        }

        /// <summary>The drawn polylines as JSON (the preview renderer reads it): stations, walls, tanks, reels, every pose.</summary>
        internal static void Dump(string path)
        {
            var ci = CultureInfo.InvariantCulture;
            var sb = new StringBuilder("{\"stations\":[");
            List<Drawn> all = DrawAll();
            bool firstSt = true;
            foreach (Station st in Stations())
            {
                World(st);
                if (!firstSt) sb.Append(',');
                firstSt = false;
                sb.Append("{\"name\":\"").Append(st.Name).Append("\",\"w\":").Append(st.W).Append(",\"h\":").Append(st.H).Append(",\"ox\":").Append(Ox).Append(",\"oz\":").Append(Oz);
                sb.Append(",\"walls\":[").Append(string.Join(",", st.Walls.Select(c => $"[{c.X},{c.Z}]"))).Append(']');
                sb.Append(",\"tanks\":[").Append(string.Join(",", st.Tanks.Values.Select(t => $"[{t.x},{t.z}]"))).Append(']');
                sb.Append(",\"reels\":[").Append(string.Join(",", st.Reels.Select(r => $"{{\"name\":\"{r.Name}\",\"x\":{r.X},\"z\":{r.Z},\"end\":[{r.End.X},{r.End.Z}]}}"))).Append(']');
                sb.Append(",\"drawn\":[");
                bool first = true;
                foreach (Drawn d in all.Where(q => q.Station == st.Name))
                {
                    if (!first) sb.Append(',');
                    first = false;
                    sb.Append("{\"reel\":\"").Append(d.Reel).Append("\",\"pose\":\"").Append(d.PoseName).Append("\",\"ok\":").Append(d.Lay.Ok ? "true" : "false");
                    sb.Append(",\"verdict\":\"").Append(!d.Lay.Ok ? "REFUSED" : d.Rep.Ok ? "PASS" : KnownOnly(d) ? "KNOWN" : "FAIL").Append('"');
                    if (d.Rep != null) sb.Append(",\"line\":\"").Append(d.Rep.Line().Replace("\"", "'")).Append('"');
                    sb.Append(",\"pts\":[");
                    if (d.Pts != null) sb.Append(string.Join(",", d.Pts.Select(v => "[" + (v.X - Ox).ToString("0.####", ci) + "," + (v.Z - Oz).ToString("0.####", ci) + "]")));
                    sb.Append("]}");
                }
                sb.Append("]}");
            }
            sb.Append("]}");
            System.IO.File.WriteAllText(path, sb.ToString());
        }
    }
}
