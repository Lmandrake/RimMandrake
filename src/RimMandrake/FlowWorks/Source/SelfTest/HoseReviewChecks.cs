using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    /// <summary>Hose cases moved from GimmeSomeSlack/Source/SelfTest/ReviewRound6Checks.cs (draw order, hose length, relay) at the hose port (step 2); unchanged, same message prefix.</summary>
    internal static class HoseReview6
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "review6: " + msg);
        private static bool Near(double a, double b, double eps = 1e-4) => Math.Abs(a - b) < eps;

        // ---------------------------------------------------------------- draw order
        private static bool OverheadAboveGround(int hoseQ, int clampQ, int overheadQ, double hoseTop, double spanAlt, double topAlt) =>
            overheadQ > hoseQ && overheadQ > clampQ && spanAlt > hoseTop && topAlt > hoseTop;
        private static void Draw()
        {
            foreach (int strand in new[] { 3000, 2950, 3100 })
            {
                int h = DrawOrder.HoseQueue(strand), c = DrawOrder.TapClampQueue(strand), o = DrawOrder.OverheadQueue(strand);
                double top = DrawOrder.HoseTopAltitude(HoseMath.CrossBand, HoseMath.CrossRanks);
                Check(OverheadAboveGround(h, c, o, top, DrawOrder.SpanAltitude, DrawOrder.TopAltitude),
                    "strand queue " + strand + ": overhead queue " + o + " > hose " + h + " and clamp " + c + "; span alt " +
                    DrawOrder.SpanAltitude.ToString("0.000") + " and head alt " + DrawOrder.TopAltitude.ToString("0.000") + " > hose top " + top.ToString("0.000"));
                Check(h > strand + 2, "strand queue " + strand + ": the hose still draws over the cord faces (strand + 2)");
            }
            // vanilla's numbers (RimSage, Verse.Altitudes): PawnState+5 inc = 25*0.36585367 + 5*0.03658537
            Check(Near(DrawOrder.SpanAltitude, 9.32927) && Near(DrawOrder.Alt(DrawOrder.LayerConduits), 1.82927),
                "altitudes are vanilla's: span " + DrawOrder.SpanAltitude.ToString("0.00000") + ", Conduits " + DrawOrder.Alt(DrawOrder.LayerConduits).ToString("0.00000"));
            Check(DrawOrder.HoseTopAltitude(HoseMath.CrossBand, HoseMath.CrossRanks) < DrawOrder.Alt(DrawOrder.LayerHose + 1),
                "the top hose band stays below the next altitude layer (DoorMoveable)");
            // 2026-10-05: the hose's lowest piece (its own shadow strip, 0.0004 under the strand) sits above vanilla's sun-shadow
            // quads, so its depth pre-pass hides wall shadows (owner screenshot: hard rectangles across the hose)
            Check(DrawOrder.Alt(DrawOrder.LayerHose) + DrawOrder.HoseBaseLift - 0.0008 > DrawOrder.Alt(DrawOrder.LayerShadows),
                "the hose band sits above the Shadows layer");
            // can-fail: round 5 -- the span cable and pole heads were plain Transparent (queue 3000), the hose 3003
            Check(!OverheadAboveGround(3003, 3004, 3000, DrawOrder.HoseTopAltitude(HoseMath.CrossBand, HoseMath.CrossRanks), DrawOrder.SpanAltitude, DrawOrder.TopAltitude),
                "can-fail: the round-5 queues (overhead 3000 < hose 3003) are caught although the altitudes were right");
        }
        // ---------------------------------------------------------------- hose length
        private static CordWorld Open(int w, int h) => new CordWorld(w, h);
        private static void Length()
        {
            Check(Near(HoseMath.DefaultMaxLength, 40), "the shipped hose length is 40 cells (" + HoseMath.DefaultMaxLength + ")");
            var cases = new[] { (30.0, 0, 40.0), (36.0, 0, 36.0), (20.0, 0, 20.0), (30.0, 1, 30.0), (40.0, 1, 40.0), (55.0, 1, 55.0) };
            int ok = cases.Count(c => Near(HoseMath.MigrateMaxLength(c.Item1, c.Item2), c.Item3));
            Check(ok == cases.Length, "settings migration: an untouched old default 30 -> 40, every chosen length kept (" + ok + "/" + cases.Length + ")");
            int naive = cases.Count(c => Near(HoseMath.DefaultMaxLength, c.Item3));
            Check(naive < cases.Length, "can-fail: 'always the new default' is right in only " + naive + "/" + cases.Length + " (it throws away a chosen 36)");
            CordWorld w = Open(80, 20);
            var reel = new Cell(2, 10);
            Check(HoseMath.CheckInstall(w, reel, new Cell(2 + 38, 10), HoseMath.DefaultMaxLength) == null,
                "a 38-cell straight run fits a 40-cell hose (38 x 1.05 = 39.9)");
            Check(HoseMath.CheckInstall(w, reel, new Cell(2 + 39, 10), HoseMath.DefaultMaxLength) == "route too long",
                "a 39-cell run does not (39 x 1.05 = 40.95): the 5% margin stays");
            Check(HoseMath.CheckInstall(w, reel, new Cell(2 + 38, 10), HoseMath.OldDefaultMaxLength) != null,
                "can-fail: the old 30-cell hose refuses the 38-cell run");
        }
        // ---------------------------------------------------------------- relay
        private static void Relay()
        {
            var r = new HoseReelRect(10, 10, 2, 2);
            List<Cell> ins = HoseRelay.IntakeCells(r);
            bool sides = ins.Count == 8 && ins.All(c => !r.Contains(c)) &&
                         ins.All(c => (c.X >= 10 && c.X <= 11) != (c.Z >= 10 && c.Z <= 11));      // exactly one axis inside: a side, not a corner
            Check(sides, "a 2x2 reel has 8 intake cells, all across a side edge, none inside, no corner (" + ins.Count + ")");
            CordWorld w = Open(60, 40);
            Func<Cell, bool> walk = c => w.InBounds(c) && w.IsWalkable(c);
            Check(HoseRelay.TryIntake(r, new V2(0, 10.6), walk, out Cell west) && west.X == 9 && HoseRelay.SideInto(r, west).X == 1,
                "a hose from the west ends on the relay's west side (" + west.X + "," + west.Z + ")");
            V2 p = HoseRelay.IntakePoint(r, west);
            Check(Near(p.X, 10) && p.Z > 10 && p.Z < 12, "the hose end sits ON the relay's edge (" + p.X + "," + p.Z + ")");
            w.SetBlocked(new Cell(9, 10), BlockKind.Wall);
            w.SetBlocked(new Cell(9, 11), BlockKind.Wall);
            Check(HoseRelay.TryIntake(r, new V2(0, 10.6), walk, out Cell other) && other.X != 9,
                "west side walled: the hose takes the next nearest free side (" + other.X + "," + other.Z + ")");
            var all = new List<HoseReelRect> { new HoseReelRect(0, 10, 2, 2), r, new HoseReelRect(30, 10, 2, 2) };
            Check(HoseRelay.RelayOf(new Cell(12, 10), all, 0) == 1 && HoseRelay.RelayOf(new Cell(12, 12), all, 0) == -1 &&
                  HoseRelay.RelayOf(new Cell(2, 10), all, 0) == -1,
                "a free end on an intake feeds that reel; a corner cell or its own reel's side feeds nothing");
            // loops: 0 -> 1 -> 2 ; laying 2 -> 0 closes a ring, 2 -> 3 does not
            int[] next = { 1, 2, -1, -1 };
            Check(HoseRelay.WouldLoop(2, 0, i => next[i]) && !HoseRelay.WouldLoop(2, 3, i => next[i]) && !HoseRelay.WouldLoop(3, 0, i => next[i]),
                "a chain may not loop back (2->0 refused, 2->3 and 3->0 fine)");
            Check(HoseRelay.Chain(0, i => next[i]).SequenceEqual(new[] { 0, 1, 2 }), "the chain from the first reel runs 0, 1, 2");
            int[] ring = { 1, 0 };
            Check(HoseRelay.Chain(0, i => ring[i]).Count == 2, "can-fail: a ring (if one were ever saved) stops, it does not spin");
            // the review station: three 2x2 reels in a row, 32 cells apart -- 64+ cells end to end, beyond one 40-cell hose
            CordWorld f = Open(100, 20);
            var A = new HoseReelRect(1, 8, 2, 2);
            var B = new HoseReelRect(33, 8, 2, 2);
            var C = new HoseReelRect(65, 8, 2, 2);
            Func<Cell, bool> fw = c => f.InBounds(c) && f.IsWalkable(c);
            HoseRelay.TryIntake(B, A.Mouth, fw, out Cell ab);
            HoseRelay.TryIntake(C, B.Mouth, fw, out Cell bc);
            string w1 = HoseMath.CheckInstall(f, A, ab, HoseMath.DefaultMaxLength), w2 = HoseMath.CheckInstall(f, B, bc, HoseMath.DefaultMaxLength);
            Check(w1 == null && w2 == null, "relay station: hose 1 (A -> B intake " + ab.X + "," + ab.Z + ") and hose 2 (B -> C intake " + bc.X + "," + bc.Z + ") each fit 40 cells: " + (w1 ?? "ok") + " / " + (w2 ?? "ok"));
            HoseRelay.TryIntake(C, A.Mouth, fw, out Cell ac);
            Check(HoseMath.CheckInstall(f, A, ac, HoseMath.DefaultMaxLength) != null && V2.Dist(A.Mouth, C.Centre) > HoseMath.DefaultMaxLength,
                "can-fail: one hose cannot reach the far reel (" + V2.Dist(A.Mouth, C.Centre).ToString("0.0") + " cells): only the chain does");
        }

        public static void Run()
        {
            Draw();
            Length();
            Relay();
        }
    }

    /// <summary>Hose cases moved from GimmeSomeSlack/Source/SelfTest/ReviewRound7Checks.cs (station 42 relay hookup) at the hose port (step 2); unchanged, same message prefix.</summary>
    internal static class HoseReview7
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "review7: " + msg);
        private static bool Near(double a, double b, double eps = 1e-4) => Math.Abs(a - b) < eps;

        private static double TailAngleDeg(IList<V2> P, V2 inward, double back)
        {
            V2 t = (P[P.Count - 1] - HoseMath.PointBack(P, back)).Norm();
            return Math.Acos(Math.Max(-1, Math.Min(1, t.X * inward.X + t.Z * inward.Z))) * 180 / Math.PI;
        }
        /// <summary>Every look, both arts, every one of the 8 intake cells (all four sides): the drawn end lies on the
        /// footprint edge within tolerance, inside that edge's span, and the coupling points into the reel.</summary>
        private static void EndsOnEdge()
        {
            var relay = new HoseReelRect(10, 10, 2, 2);
            int total = 0, ok = 0;
            string worst = "";
            double worstOff = 0;
            var sidesSeen = new HashSet<string>();
            foreach (string look in ReelIntakeGeometry.Looks)
                foreach (bool deployed in new[] { false, true })
                    foreach (Cell intake in HoseRelay.IntakeCells(relay))
                    {
                        total++;
                        V2 e = HoseRelay.DrawnEnd(relay, intake, look, deployed, out V2 inward);
                        Cell into = HoseRelay.SideInto(relay, intake);
                        double off = HoseRelay.EdgeOffset(relay, inward, e, out bool within);
                        bool good = Math.Abs(off) <= HoseRelay.EndTolerance && within && inward.X == into.X && inward.Z == into.Z;
                        if (good) ok++;
                        sidesSeen.Add(into.X + "," + into.Z);
                        if (Math.Abs(off) > Math.Abs(worstOff)) { worstOff = off; worst = look + (deployed ? " laid " : " stored ") + intake.X + "," + intake.Z; }
                    }
            Check(ok == total && total == 64 && sidesSeen.Count == 4,
                "every look x art x intake cell (all 4 sides): the drawn end lies on the footprint edge within " + HoseRelay.EndTolerance +
                " cell, inside the edge, coupling pointing in (" + ok + "/" + total + ", worst " + worstOff.ToString("0.000") + " at " + worst + ")");

            // west: both west cells couple to the art's one nozzle, which is the laid hose's outlet tip too (one measured nozzle)
            int west = 0, wt = 0;
            double r6Miss = 99;
            foreach (string look in ReelIntakeGeometry.Looks)
                foreach (bool deployed in new[] { false, true })
                {
                    wt++;
                    V2 lo = HoseRelay.DrawnEnd(relay, new Cell(9, 10), look, deployed, out _);
                    V2 hi = HoseRelay.DrawnEnd(relay, new Cell(9, 11), look, deployed, out _);
                    ReelIntakeGeometry.OutletTip(look, deployed, out double tdx, out double tdz);
                    if (V2.Dist(lo, hi) < 1e-9 && V2.Dist(lo, relay.Centre + new V2(tdx, tdz)) < 0.06) west++;
                    r6Miss = Math.Min(r6Miss, V2.Dist(HoseRelay.IntakePoint(relay, new Cell(9, 10)), lo));
                }
            Check(west == wt, "from the west both cells couple to the art's measured nozzle (its height, its face) (" + west + "/" + wt + ")");
            Check(r6Miss > 0.05, "can-fail: round 6's end (the lower west cell's edge midpoint) misses the inlet by >= " + r6Miss.ToString("0.00") +
                " cell in every look -- the floating coupling of the station-42 shot");
        }
        /// <summary>A hose laid onto a relay from each of the four sides, in every look: it ends exactly on the drawn end,
        /// its last 0.5 cell (flat and plump) runs along the intake axis, and it stays clear.</summary>
        private static void LaysIntoEverySide()
        {
            var B = new HoseReelRect(40, 40, 2, 2);
            var feeders = new[] { ("west", new HoseReelRect(14, 40, 2, 2)), ("east", new HoseReelRect(66, 40, 2, 2)),
                                  ("north", new HoseReelRect(40, 66, 2, 2)), ("south", new HoseReelRect(40, 14, 2, 2)) };
            int total = 0, ok = 0, bent = 0;
            string fails = "";
            var w = new CordWorld(90, 90);
            Func<Cell, bool> walk = c => w.InBounds(c) && w.IsWalkable(c) && !B.Contains(c);
            foreach (var (name, A) in feeders)
                foreach (string look in ReelIntakeGeometry.Looks)
                {
                    total++;
                    if (!HoseRelay.TryIntake(B, A.Mouth, walk, out Cell intake)) { fails += " " + name + ":no intake"; continue; }
                    V2 e = HoseRelay.DrawnEnd(B, intake, look, true, out V2 inward);
                    HoseLay lay = HoseMath.Lay(w, A.Mouth, e, new HoseShapeParams(), 7, inward);
                    Cell into = HoseRelay.SideInto(B, intake);
                    V2 expect = name == "west" ? new V2(1, 0) : name == "east" ? new V2(-1, 0) : name == "north" ? new V2(0, -1) : new V2(0, 1);
                    bool good = lay.Ok && V2.Dist(lay.Flat[lay.Flat.Count - 1], e) < 1e-6 && V2.Dist(lay.Plump[lay.Plump.Count - 1], e) < 1e-6 &&
                                TailAngleDeg(lay.Flat, inward, 0.5) < 3 && TailAngleDeg(lay.Plump, inward, 0.5) < 3 &&
                                inward.X == expect.X && inward.Z == expect.Z && into.X == (int)expect.X && into.Z == (int)expect.Z &&
                                HoseMath.Clear(w, lay.Flat) && HoseMath.Clear(w, lay.Plump);
                    if (good) ok++;
                    else fails += " " + name + "/" + look + (lay.Ok ? " tail " + TailAngleDeg(lay.Flat, inward, 0.5).ToString("0.0") : " " + lay.Reason);
                    // can-fail: the same hose laid with no end direction (round 6) does not meet the coupling's axis
                    HoseLay plain = HoseMath.Lay(w, A.Mouth, e, new HoseShapeParams(), 7);
                    if (plain.Ok && TailAngleDeg(plain.Flat, inward, 0.5) >= 3) bent++;
                }
            Check(ok == total && total == 16, "a hose onto a relay from W, E, N and S in every look ends on the drawn inlet/outline, its last 0.5 cell " +
                "straight along the intake (< 3 deg, flat and plump), clear (" + ok + "/" + total + (fails.Length > 0 ? ":" + fails : "") + ")");
            Check(bent > 0, "can-fail: without the end direction the last stretch follows the lay's curve, off the intake axis (" + bent + "/" + total + " lays)");
        }
        /// <summary>The station-42 geometry (three reels in a row, the hose comes in from the west): the end is on the
        /// relay's west inlet, not the lower west cell's edge midpoint.</summary>
        private static void Station42()
        {
            var A = new HoseReelRect(1, 8, 2, 2);
            var B = new HoseReelRect(33, 8, 2, 2);
            var w = new CordWorld(100, 20);
            Func<Cell, bool> walk = c => w.InBounds(c) && w.IsWalkable(c) && !B.Contains(c);
            HoseRelay.TryIntake(B, A.Mouth, walk, out Cell ab);
            V2 e = HoseRelay.DrawnEnd(B, ab, "Scrapper", true, out V2 inward);
            HoseLay lay = HoseMath.Lay(w, A.Mouth, e, new HoseShapeParams { MaxLength = HoseMath.DefaultMaxLength }, 11, inward);
            ReelIntakeGeometry.OutletTip("Scrapper", true, out double sdx, out double sdz);
            Check(ab.X == 32 && inward.X == 1 && lay.Ok && V2.Dist(lay.Flat[lay.Flat.Count - 1], e) < 1e-6 && V2.Dist(e, B.Centre + new V2(sdx, sdz)) < 0.06 &&
                  Math.Abs(e.X - B.X0) < HoseRelay.EndTolerance,
                "station 42: A's hose ends on B's west brass inlet (" + e.X.ToString("0.00") + "," + e.Z.ToString("0.00") + "; B footprint " + B.X0 + ".." + (B.X0 + 2) +
                ", " + B.Z0 + ".." + (B.Z0 + 2) + ")");
        }

        /// <summary>The wire width the hose ratio reads is the cord code's current strand (0.08, cords round 5).</summary>
        private static void WireWidth()
        {
            Check(Math.Abs(HoseMath.WireVisibleWidth - 0.08 * 25.0 / 32.0) < 1e-9,
                "HoseMath.WireVisibleWidth follows the 0.08 strand (" + HoseMath.WireVisibleWidth.ToString("0.0000") + ")");
        }

        public static void Run()
        {
            EndsOnEdge();
            LaysIntoEverySide();
            Station42();
            WireWidth();
            HoseJointChecks.Run();   // HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES: the joint check's offline half (below)
        }
    }

    /// <summary>Hose cases moved from GimmeSomeSlack/Source/SelfTest/PileLookChecks.cs (rule 3: hoses) at the hose port (step 2); unchanged, same message prefix.</summary>
    internal static class HosePileLook
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "pilelook: " + msg);
        private static bool Near(double a, double b, double eps = 1e-4) => Math.Abs(a - b) < eps;

        private static List<V2> Line(V2 a, V2 b, double step = 0.1)
        {
            int n = Math.Max(2, (int)Math.Ceiling(V2.Dist(a, b) / step) + 1);
            var o = new List<V2>(n);
            for (int i = 0; i < n; i++) o.Add(a + (b - a) * (i / (double)(n - 1)));
            return o;
        }
        private static HoseLay Straight(V2 a, V2 b, params int[] joints)
        {
            List<V2> p = Line(a, b);
            var lay = new HoseLay { Ok = true, Flat = p, Plump = new List<V2>(p), Centre = new List<V2>(p) };
            lay.Joints = joints.ToList();
            lay.Couplings = new List<V2> { p[0] };
            foreach (int j in joints) lay.Couplings.Add(p[j]);
            lay.Couplings.Add(p[p.Count - 1]);
            return lay;
        }
        private static void HoseRule3()
        {
            const double vis = 0.3;
            // A (older, id 1) runs west-east along z=5; B (newer, id 2) runs north-south and ENDS on A's body at (5,5).
            // Thing-id order puts B over A, so B's end coupling would lie on top of A: the layering must put B beneath.
            HoseLay A = Straight(new V2(0, 5), new V2(10, 5));
            HoseLay B = Straight(new V2(5, 12), new V2(5, 5.02));
            var raw = new List<HoseMath.LayeredHose> { new HoseMath.LayeredHose { Id = 1, Lay = A }, new HoseMath.LayeredHose { Id = 2, Lay = B } };
            var naive = new Dictionary<int, int> { { 1, 0 }, { 2, 1 } };
            int before = HoseMath.FittingsOnTop(raw, naive, null, vis).Count;
            Check(before >= 1, $"rule 3 can fail: thing-id order alone leaves {before} fitting(s) on top of a hose (want >= 1)");
            HoseMath.Layering L = HoseMath.Layer(raw, vis);
            List<string> after = HoseMath.FittingsOnTop(raw, L.Rank, L.Joints, vis);
            foreach (string f in after.Take(4)) Console.WriteLine("    " + f);
            Check(after.Count == 0 && L.Rank[2] < L.Rank[1], $"rule 3 (end): B's end on A's body -> B ranked {L.Rank[2]} under A {L.Rank[1]}, {after.Count} fittings on top (want 0)");

            // joiner: C (older) runs north-south through x=5; D (newer) crosses it with a joiner right on the crossing.
            HoseLay C = Straight(new V2(5, 0), new V2(5, 10));
            HoseLay D = Straight(new V2(0, 4), new V2(10, 4), 50);   // sample 50 of 101 = (5,4): on C
            var jr = new List<HoseMath.LayeredHose> { new HoseMath.LayeredHose { Id = 1, Lay = C }, new HoseMath.LayeredHose { Id = 2, Lay = D } };
            int jb = HoseMath.FittingsOnTop(jr, new Dictionary<int, int> { { 1, 0 }, { 2, 1 } }, null, vis).Count;
            Check(jb >= 1, $"rule 3 can fail: a joiner on a crossing reads on top ({jb} fittings)");
            HoseMath.Layering JL = HoseMath.Layer(jr, vis);
            List<string> ja = HoseMath.FittingsOnTop(jr, JL.Rank, JL.Joints, vis);
            Check(ja.Count == 0 && JL.Joints[2].Count == 0, $"rule 3 (joiner): the crossing joiner is dropped ({JL.Joints[2].Count} kept), {ja.Count} fittings on top (want 0)");
            // a joiner clear of every other hose is kept
            HoseLay E = Straight(new V2(0, 8), new V2(10, 8), 20);
            var kr = new List<HoseMath.LayeredHose> { new HoseMath.LayeredHose { Id = 1, Lay = C }, new HoseMath.LayeredHose { Id = 2, Lay = E } };
            HoseMath.Layering KL = HoseMath.Layer(kr, vis);
            Check(KL.Joints[2].Count == 1 && KL.Rank[2] > KL.Rank[1], $"rule 3: a joiner clear of other hoses is kept ({KL.Joints[2].Count}) and thing-id order stands");

            // a cycle (each hose's end on the other) cannot be satisfied by order: it must still return a total order
            HoseLay F = Straight(new V2(0, 0), new V2(6, 0));
            HoseLay G = Straight(new V2(3, -3), new V2(3, 0.02));
            HoseLay F2 = Straight(new V2(3, 0.02), new V2(3, 3));   // G ends and F2 starts on F's body, and on each other's end
            var cy = new List<HoseMath.LayeredHose> { new HoseMath.LayeredHose { Id = 1, Lay = F }, new HoseMath.LayeredHose { Id = 2, Lay = G }, new HoseMath.LayeredHose { Id = 3, Lay = F2 } };
            HoseMath.Layering CL = HoseMath.Layer(cy, vis);
            Check(CL.Rank.Values.Distinct().Count() == 3 && CL.Rank.Values.Min() == 0 && CL.Rank.Values.Max() == 2,
                  $"rule 3: layering is a total order 0..n-1 ({string.Join(",", CL.Rank.Select(kv => kv.Key + ":" + kv.Value))})");
            Console.WriteLine($"  pilelook hoses: end case rank B {L.Rank[2]} / A {L.Rank[1]}; joiner case kept {JL.Joints[2].Count}; before {before}+{jb} on top, after {after.Count}+{ja.Count}");
        }

        public static void Run()
        {
            HoseRule3();
        }
    }

    /// <summary>Hose cases moved from GimmeSomeSlack/Source/SelfTest/GptReadFixChecks.cs (B4, B10, B11, B13, B5 lead-out, B2/B3 lay length) at the hose port (step 2); unchanged, same message prefix.</summary>
    internal static class HoseGptFix
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "gptfix: " + msg);
        private static bool Near(double a, double b, double eps = 1e-4) => Math.Abs(a - b) < eps;

        private static double MinBendUpTo(IList<V2> X, double upTo) => HoseMath.MinBendRadiusUpTo(X, HoseMath.EndSkip, upTo);
        /// <summary>B5, owner decision by question card 2026-10-06 (straight lead-out).</summary>
        private static void LeadOut()
        {
            // Dubins: lands on the target pose, never tighter than R, for every heading pair round a circle of targets
            int bad = 0, n = 0;
            for (int i = 0; i < 12; i++)
                for (int k = 0; k < 8; k++)
                {
                    double ang = i * Math.PI / 6, hk = k * Math.PI / 4;
                    var p1 = new V2(3 * Math.Cos(ang), 3 * Math.Sin(ang));
                    var h1 = new V2(Math.Cos(hk), Math.Sin(hk));
                    List<V2> d = HoseMath.Dubins(new V2(0, 0), new V2(-1, 0), p1, h1, 1.2, 0.0625);
                    n++;
                    if (d == null) { bad++; continue; }
                    var pl = new List<V2> { new V2(0, 0) }; pl.AddRange(d);
                    V2 last = pl[pl.Count - 1] - pl[pl.Count - 2];
                    if (V2.Dist(pl[pl.Count - 1], p1) > 1e-3 || Math.Abs(last.Norm().X - h1.X) + Math.Abs(last.Norm().Z - h1.Z) > 0.08 || HoseMath.MinBendRadius(pl, 0) < 1.2 * 0.97) bad++;
                }
            Check(bad == 0, "B5 Dubins lands on the pose and holds the radius in " + (n - bad) + "/" + n + " cases");
            // the old worst fuzz case (seed 2: a U-turn out of a west nozzle to a target behind and below): now straight, then round
            var c = HoseFuzz.MakeHose(2, null);
            var prm = new HoseShapeParams { MinBendRadius = c.MinR, MaxLength = c.MaxLen, Slack = 1.0, PlumpAmount = 1.0 };
            HoseLay lay = HoseMath.Lay(c.W, c.Reel.Mouth, c.Target.Centre, prm, c.Seed, null, c.Reel.Outward);
            Check(lay.Ok && lay.Outlet && lay.LeadOutLen > 0, "B5 seed 2 lays with a lead-out (" + (lay.Reason ?? "ok") + ")");
            if (lay.Ok)
            {
                double S = HoseMath.LeadOutStraight(prm);
                double off = 0;
                double[] cs = Geo.CumLen(lay.Flat);
                for (int i = 0; i < lay.Flat.Count && cs[i] <= S; i++) off = Math.Max(off, Math.Abs(lay.Flat[i].Z - c.Reel.Mouth.Z));
                Check(off < 1e-6 && lay.Flat[1].X < c.Reel.Mouth.X, "B5 the first " + S.ToString("0.0") + " cells run dead straight out of the nozzle (off-line " + off.ToString("0.000") + ")");
                double mb = Math.Min(MinBendUpTo(lay.Flat, lay.LeadOutLen), MinBendUpTo(lay.Plump, lay.LeadOutLen));
                Check(mb >= c.MinR * 0.95, "B5 seed 2 lead-out bend " + mb.ToString("0.00") + " >= 0.95 x " + c.MinR.ToString("0.0") + " (was 0.33 with the 2R position blend)");
                // can-fail: the retired 2R position blend on the same flat hose bends far tighter
                var bent = new List<V2>(lay.Flat.Take(3)); bent.AddRange(new[] { lay.Flat[3] + new V2(0, 0.4) }); bent.AddRange(lay.Flat.Skip(4));
                Check(MinBendUpTo(bent, lay.LeadOutLen) < c.MinR * 0.95, "B5 can-fail: a kinked lead-out reads under the bar");
            }
            // a wall hard against the nozzle: refused with the reason, never laid without the lead-out
            var w = new CordWorld(30, 20);
            var reel = new HoseReelRect(10, 8, 2, 2);
            for (int z = 0; z < 20; z++) w.SetBlocked(new Cell(9, z), BlockKind.Wall);
            HoseLay blocked = HoseMath.Lay(w, reel.Mouth, new Cell(20, 9).Centre, new HoseShapeParams { MinBendRadius = 1.2 }, 7, null, reel.Outward);
            Check(!blocked.Ok && blocked.Reason == HoseMath.LeadOutBlocked, "B5 wall against the nozzle: refused '" + (blocked.Reason ?? "laid") + "'");
            HoseLay open = HoseMath.Lay(new CordWorld(30, 20), reel.Mouth, new Cell(20, 9).Centre, new HoseShapeParams { MinBendRadius = 1.2 }, 7, null, reel.Outward);
            Check(open.Ok && open.LeadOutLen > 0, "B5 can-fail: the same reel with the wall gone lays (" + (open.Reason ?? "ok") + ")");
        }
        /// <summary>B3: a laid hose is never longer than the hose; B2: the install check judges the shortest route.</summary>
        private static void LayLength()
        {
            // seed 13 was the G1 reproducer (hose 11.6 laid 12.70 out of the outlet)
            var c = HoseFuzz.MakeHose(13, null);
            var prm = new HoseShapeParams { MinBendRadius = c.MinR, MaxLength = c.MaxLen, Slack = 1.0, PlumpAmount = 1.0 };
            HoseLay lay = HoseMath.Lay(c.W, c.Reel.Mouth, c.Target.Centre, prm, c.Seed, null, c.Reel.Outward);
            Check(!lay.Ok || Math.Max(lay.FlatLen, lay.PlumpLen) <= c.MaxLen + 1e-6, "B3 seed 13 laid " + (lay.Ok ? Math.Max(lay.FlatLen, lay.PlumpLen).ToString("0.00") : "refused: " + lay.Reason) + " within the hose " + c.MaxLen.ToString("0.00"));
            var big = new HoseShapeParams { MinBendRadius = c.MinR, MaxLength = double.PositiveInfinity, Slack = 1.0, PlumpAmount = 1.0 };
            HoseLay free = HoseMath.Lay(c.W, c.Reel.Mouth, c.Target.Centre, big, c.Seed, null, c.Reel.Outward);
            Check(free.Ok && Math.Max(free.FlatLen, free.PlumpLen) > c.MaxLen, "B3 can-fail: with no length cap the same lay runs " + (free.Ok ? Math.Max(free.FlatLen, free.PlumpLen).ToString("0.00") : "-") + ", over " + c.MaxLen.ToString("0.00"));
            Check(HoseMath.Overlong(new HoseLay { FlatLen = 12.7, PlumpLen = 12 }, 11.6) && !HoseMath.Overlong(new HoseLay { FlatLen = 11.5, PlumpLen = 11 }, 11.6), "B3 Overlong reads the longer pose");
        }

        public static void Run()
        {
            // B4: the reel's port cache starts at int.MinValue and must read as stale, not fresh
            Check(!HoseLive.CacheFresh(0, int.MinValue, 60), "B4 never-read port cache is stale at tick 0");
            Check(!HoseLive.CacheFresh(123456, int.MinValue, 60), "B4 never-read port cache is stale later in the game");
            Check(HoseLive.CacheFresh(100, 70, 60) && !HoseLive.CacheFresh(130, 70, 60), "B4 a read 30 ticks ago is fresh, 60 ago is not");

            // B11: with auto-resume off, NO interrupted order (Deploy, Move, Retract) on a dropped hose resumes unforced
            bool any = false;
            foreach (HosePendingOrder o in new[] { HosePendingOrder.Deploy, HosePendingOrder.Move, HosePendingOrder.Retract })
                any |= HoseOrderRules.MayResume(HoseCarryState.Dropped, o, false, false);
            Check(!any, "B11 auto-resume off: no dropped order resumes unforced");
            Check(HoseOrderRules.MayResume(HoseCarryState.Dropped, HosePendingOrder.Move, true, false) && HoseOrderRules.MayResume(HoseCarryState.Dropped, HosePendingOrder.Retract, false, true)
                  && HoseOrderRules.MayResume(HoseCarryState.Laid, HosePendingOrder.Move, false, false), "B11 forced, setting on, or a laid (not dropped) hose still go");
            Check(!HoseOrderRules.MayResume(HoseCarryState.Dropped, HosePendingOrder.Move, false, false), "B11 a dropped Move stays put unforced (the old rule gated Deploy only and resumed it)");
            // B13: a path failure on the current order clears it (before or after the grab); anything else keeps it
            Check(!HoseOrderRules.KeepOrderAfterJob(true, true) && HoseOrderRules.KeepOrderAfterJob(false, true) && HoseOrderRules.KeepOrderAfterJob(true, false),
                  "B13 path failure on the current order clears it; a draft or a newer order keeps it");
            // B10: A (0) has a pending order onto B (1), nothing is laid; B's order onto A must read as a loop
            int[] laidNext = { -1, -1 }, pendNext = { 1, -1 };
            bool[] pend = { true, false };
            Check(HoseRelay.WouldLoop(1, 0, i => HoseRelay.IntendedNext(laidNext[i], pend[i], pendNext[i])), "B10 two pending orders A->B, B->A read as a loop");
            Check(!HoseRelay.WouldLoop(1, 0, i => laidNext[i]), "B10 can-fail: following laid hoses only, the ring is missed");
            LeadOut();
            LayLength();
            ScenicRoute();
        }

        /// <summary>HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE (owner 2026-10-17, water scene S3: "It should prefer to NOT pass
        /// through the reel but go around on the bare ground"). The S3 rig: a 2x2 reel whose nozzle faces west, a pump cell
        /// beside it, the free end to the EAST. The live hose world costed the reel's own cells 0 (PassThroughOnly reads as
        /// walkable), so the lay U-turned out of the nozzle straight back over the drum. Planned (Lay) and walked (LayAlong)
        /// lays must both stay off the footprint; can-fail: the same world with the reel uncosted (the old live world) crosses.</summary>
        private static void ScenicRoute()
        {
            // the S3 rig (water_scenes_walk.s3_geom, shifted): reel B (hose out), the pump on the row above it, reel A above that
            var reel = new HoseReelRect(20, 8, 2, 2);
            var reelA = new HoseReelRect(20, 11, 2, 2);
            Cell pump = new Cell(20, 10), end = new Cell(26, 10);
            CordWorld Rig(bool costed)
            {
                var w = new CordWorld(44, 24);
                if (costed)
                {
                    foreach (HoseReelRect r in new[] { reel, reelA })
                        for (int x = r.X0; x < r.X0 + 2; x++) for (int z = r.Z0; z < r.Z0 + 2; z++) w.SetExtraCost(new Cell(x, z), HoseMath.BuildingCrossCost);
                    w.SetExtraCost(pump, HoseMath.BuildingCrossCost);
                }
                return w;
            }
            CordWorld rig = Rig(true);
            // points of the laid hose on a reel or the pump, clear of the nozzle (the mouth sits 0.02 inside the reel's west cell)
            int OnRig(HoseLay lay) => lay.Ok ? lay.Flat.Count(q => V2.Dist(q, reel.Mouth) > 0.3 && rig.ExtraCost(q.Floor) >= HoseMath.BuildingCrossCost) : -1;
            var prm = new HoseShapeParams { MinBendRadius = 1.2, MaxLength = 40 };
            HoseLay planned = HoseMath.Lay(Rig(true), reel.Mouth, end.Centre, prm, 7, null, reel.Outward);
            HoseLay old = HoseMath.Lay(Rig(false), reel.Mouth, end.Centre, prm, 7, null, reel.Outward);
            Check(planned.Ok && OnRig(planned) == 0, "scenic: a planned hose from the west nozzle to an east end goes round the reels and pump (" + (planned.Reason ?? "laid") + ", " + OnRig(planned) + " points on them)");
            Check(old.Ok && OnRig(old) > 0, "scenic can-fail: with the rig uncosted (the old live world) the same lay crosses it (" + OnRig(old) + " points)");
            // the walked hose: the carrier starts on the reel's east cell and walks straight east (the start cell is the trail's)
            var walk = new List<Cell>();
            for (int x = 21; x <= end.X; x++) walk.Add(new Cell(x, 9));
            walk.Add(end);
            HoseLay carried = HoseMath.LayAlong(Rig(true), reel.Mouth, walk, end.Centre, prm, 7, null, reel.Outward);
            HoseLay carriedOld = HoseMath.LayAlong(Rig(false), reel.Mouth, walk, end.Centre, prm, 7, null, reel.Outward);
            Check(carried.Ok && OnRig(carried) == 0, "scenic: a carried hose walked east from the reel goes round it too (" + (carried.Reason ?? "laid") + ", " + OnRig(carried) + " points on the rig)");
            Check(carriedOld.Ok && OnRig(carriedOld) > 0, "scenic can-fail: the same walk with the rig uncosted crosses it (" + OnRig(carriedOld) + " points)");
            // a cost, never a block: a reel walled in on both sides is still crossed when there is no other way
            CordWorld boxed = Rig(true);
            for (int x = 0; x < 44; x++) { boxed.SetBlocked(new Cell(x, 7), BlockKind.Wall); boxed.SetBlocked(new Cell(x, 10), BlockKind.Wall); }
            HoseLay forced = HoseMath.Lay(boxed, reel.Mouth, new Cell(14, 9).Centre, prm, 7, null, reel.Outward);
            Check(forced.Ok, "scenic: the cost never blocks (a hose with no way round still lays: " + (forced.Reason ?? "laid") + ")");
            Check(HoseMath.SegmentAvoidsBuildings(Rig(true), new V2(17, 7.5), new V2(25, 7.5)) && !HoseMath.SegmentAvoidsBuildings(Rig(true), new V2(17, 9), new V2(25, 9)),
                "scenic: a straight shortcut across the drum is refused, one past it is not");
            // the live hose world (Verse-bound, not compiled here): World() and LiveCellSig must cost a reel/pump (and, since
            // HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK, any walk-over building drawn above the hose) the same
            string mc = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
            Check(System.Text.RegularExpressions.Regex.IsMatch(mc, @"WalkableFast\(idx\)\) \{ if \(CostsAsBuilding\(ed\)\) cw\.SetExtraCost\(cell, HoseMath\.BuildingCrossCost\); continue; \}")
                  && System.Text.RegularExpressions.Regex.IsMatch(mc, @"WalkableFast\(idx\)\) \{ if \(CostsAsBuilding\(ed\)\) extra = HoseMath\.BuildingCrossCost; \}")
                  && System.Text.RegularExpressions.Regex.IsMatch(mc, @"CostsAsBuilding\(Building ed\) =>\s+ed != null && \(IsRig\(ed\) \|\| DrawsOverHose\(ed\)\)")
                  && System.Text.RegularExpressions.Regex.IsMatch(mc, @"IsRig\(Building ed\) =>\s+ed != null && \(CompHoseReelOf\(ed\) != null \|\| ed is [\w.]*Building_LiquidPump\)"),
                "scenic: the live hose world and its per-cell signature both cost a reel, a pump or a walk-over building drawn above the hose BuildingCrossCost");
        }
    }

    /// <summary>
    /// HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES (owner 2026-10-22, the walkthrough: "I can't even tell what's going on here with
    /// the connnectors. Just look at them! Obviously not even checked before showing us."). The JOINT CHECK's offline half: every
    /// joint the draw code makes, for every look, art and facing, ends ON the fitting it must meet (HoseJoints.Tolerance) or
    /// runs in under a building to its centre; never on the shared edge in air. The art half is validation_hose_offline.py HO9
    /// (each drawn piece's face and bands = the constants used here); the live half is HoseProbe "joints"
    /// (northstar/joint_check.py), which measures the drawn pose of every hose on a map.
    /// </summary>
    internal static class HoseJointChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "joints: " + msg);
        private static readonly Cell[] Sides = { new Cell(1, 0), new Cell(0, 1), new Cell(-1, 0), new Cell(0, -1) };

        private static bool InRect(HoseReelRect r, V2 p, double e = 1e-6) =>
            p.X >= r.X0 - e && p.X <= r.X0 + r.W + e && p.Z >= r.Z0 - e && p.Z <= r.Z0 + r.H + e;

        /// <summary>Every sample of the path lies in the port's cell or under the reel: nothing of it hangs in air beside them.</summary>
        private static bool Covered(HoseReelRect r, Cell contact, IList<V2> path)
        {
            for (int i = 1; i < path.Count; i++)
            {
                V2 a = path[i - 1], b = path[i];
                int n = Math.Max(1, (int)Math.Ceiling(V2.Dist(a, b) / 0.05));
                for (int k = 0; k <= n; k++)
                {
                    V2 q = a + (b - a) * (k / (double)n);
                    // the jog onto the nozzle's line may cross the port cell's side edge by the tip's measured offset (<= 0.44, the redrawn
                    // ground-level outlet, Modern west), still along the pipe/port it leaves: 0.45 along the reel's edge, Tolerance across it
                    bool alongX = contact.Z >= r.Z0 + r.H || contact.Z < r.Z0;   // a north/south port: its edge runs along x
                    bool inPort = q.X >= contact.X - (alongX ? 0.45 : HoseJoints.Tolerance) && q.X <= contact.X + 1 + (alongX ? 0.3 : HoseJoints.Tolerance)
                                  && q.Z >= contact.Z - (alongX ? HoseJoints.Tolerance : 0.45) && q.Z <= contact.Z + 1 + (alongX ? HoseJoints.Tolerance : 0.3);
                    if (!InRect(r, q, HoseJoints.Tolerance) && !inPort) return false;
                }
            }
            return true;
        }

        /// <summary>The joint rule a feed must obey: it starts on the port's centre line and ends either on the nozzle's coupling
        /// (with the coupling face on the tip) or at the reel's centre, every sample covered.</summary>
        internal static bool FeedOk(HoseReelRect r, Cell contact, IList<V2> path, bool onNozzle, V2 face, V2 tip, out string why)
        {
            why = null;
            if (path.Count < 2) { why = "empty"; return false; }
            if (!HoseJoints.Meets(path[0], contact.Centre, out double g0)) { why = "starts " + g0.ToString("0.000") + " off the port's centre"; return false; }
            V2 last = path[path.Count - 1];
            if (onNozzle)
            {
                if (!HoseJoints.Meets(face, tip, out double gf) && gf > HoseReelRect.NozzleSeat + HoseJoints.Tolerance) { why = "coupling face " + gf.ToString("0.000") + " off the nozzle tip"; return false; }
                if (V2.Dist(last, face) > 0.05 + HoseJoints.Tolerance) { why = "hose stops " + V2.Dist(last, face).ToString("0.000") + " short of its coupling"; return false; }
            }
            else if (!HoseJoints.Meets(last, r.Centre, out double gc)) { why = "ends " + gc.ToString("0.000") + " from the reel's centre (no fitting there)"; return false; }
            if (!Covered(r, contact, path)) { why = "runs through air outside the port cell and the reel"; return false; }
            return true;
        }

        private static void Feeds()
        {
            int total = 0, ok = 0, nozzle = 0;
            string first = null;
            foreach (string look in ReelIntakeGeometry.Looks)
                for (int rot = 0; rot < 4; rot++)
                    foreach (bool laid in new[] { false, true })
                        foreach (Cell s in Sides)
                        {
                            var r = new HoseReelRect(10, 10, 2, 2) { Look = look, Rot = rot };
                            foreach (Cell e in r.EdgeCells(s))
                            {
                                Cell contact = e + s;
                                total++;
                                List<V2> path = HoseJoints.ReelFeed(r, s, contact, laid, out bool onN, out V2 face, out V2 axis);
                                V2 outw = r.Outward.Value;
                                bool front = Math.Abs(outw.X - s.X) < 1e-9 && Math.Abs(outw.Z - s.Z) < 1e-9;
                                if (onN) nozzle++;
                                bool good = FeedOk(r, contact, path, onN, face, HoseJoints.StoredNozzleTip(r), out string why) && onN == (front && !laid)
                                            && (!onN || (Math.Abs(axis.X + s.X) < 1e-9 && Math.Abs(axis.Z + s.Z) < 1e-9));
                                if (good) ok++;
                                else if (first == null) first = look + " rot" + rot + (laid ? " laid" : " stored") + " side " + s.X + "," + s.Z + ": " + (why ?? "nozzle rule");
                            }
                        }
            Check(ok == total && total == 256 && nozzle == 32,
                "every look x facing x art x port side x edge cell: the reel link ends ON the nozzle coupling (port in front of a stored reel) or "
                + "under the reel at its centre, starts on the port's centre line, never in air (" + ok + "/" + total + ", " + nozzle + " on the nozzle"
                + (first != null ? "; first bad: " + first : "") + ")");

            // can-fail: the pre-fix link (HosePortRule.Feed: edge cell + 0.25 to the port, coupling on the shared edge) is refused
            var r0 = new HoseReelRect(10, 10, 2, 2) { Look = "Scrapper", Rot = 3 };
            var side = new Cell(1, 0);
            Cell touch = r0.EdgeCells(side)[0];
            HosePortRule.Feed(touch, side, out V2 from, out V2 to, out V2 cp);
            bool oldRefused = !FeedOk(r0, touch + side, new List<V2> { to, from }, false, default(V2), default(V2), out string oldWhy);
            Check(oldRefused, "can-fail: the old behind-the-crank stub (ends 0.25 into the edge cell, coupling on the edge) is refused (" + oldWhy + ")");
        }

        private static void NozzleCouplings()
        {
            int total = 0, ok = 0;
            double worst = 0;
            foreach (string look in ReelIntakeGeometry.Looks)
                for (int rot = 0; rot < 4; rot++)
                {
                    var r = new HoseReelRect(10, 10, 2, 2) { Look = look, Rot = rot };
                    V2 face = HoseJoints.NozzleCoupling(r, out V2 inw);
                    total++;
                    double size = HoseMath.FittingSize(HoseMath.VisibleWidth(1, 1), HoseMath.PieceBand, HoseMath.CouplingMax);
                    V2 c = HoseJoints.FittingCentre(face, inw, -HoseMath.JoinerFace, size);
                    double drawnGap = V2.Dist(HoseJoints.CouplingFace(c, inw, size), r.NozzleTip);
                    worst = Math.Max(worst, drawnGap);
                    // the face is seated NozzleSeat into the tip, pointing into the reel, and the fitting's drawn face lands there
                    if (drawnGap <= HoseReelRect.NozzleSeat + HoseJoints.Tolerance && inw.X * r.Outward.Value.X + inw.Z * r.Outward.Value.Z < -0.999) ok++;
                }
            Check(ok == total && total == 16, "laid hose: the reel-end coupling's drawn face meets the measured nozzle tip, every look x facing (" + ok + "/" + total
                + ", worst " + worst.ToString("0.000") + " cell incl. the " + HoseReelRect.NozzleSeat + " seat)");
        }

        private static void TankPorts()
        {
            int total = 0, ok = 0;
            foreach (string look in TankPortGeometry.Looks)
                foreach (int sx in new[] { 1, -1 })
                {
                    total++;
                    TankPortGeometry.PortPoint(look, 20, 20, 2, 2, sx, 0, out V2 port);
                    var axis = new V2(sx, 0);
                    // DrawEnds: the hose is bent to port - axis/2 (EndOnPort), the coupling's end at that + axis/2, face -> port
                    V2 end = port - axis * 0.5 + axis * 0.5;
                    double size = 1.5 * HoseMath.FittingSize(HoseMath.VisibleWidth(0, 1), HoseMath.PieceBand, HoseMath.CouplingMax);
                    V2 c = HoseJoints.FittingCentre(end, axis, -HoseMath.JoinerFace, size);
                    if (HoseJoints.Meets(HoseJoints.CouplingFace(c, axis, size), port, out _) && Math.Abs(port.X - (sx > 0 ? 20 : 22)) < 1e-9) ok++;
                }
            Check(ok == total && total == 8, "hose end on a 2x2 tank: the widened coupling's drawn face lands on the measured flange, both sides, every look (" + ok + "/" + total + ")");
        }

        /// <summary>JOINT_GATE_HARDEN_TRUST_THE_DRAWN_BOX: the drawn collar's opaque box covers the nozzle tip / tank flange for the
        /// couplings the draw places, and a collar stopping short of the tip (audit D9) or beside the port reads as a gap.</summary>
        private static void CollarBoxes()
        {
            int total = 0, ok = 0, caught = 0;
            double size = HoseMath.FittingSize(HoseMath.VisibleWidth(1, 1), HoseMath.PieceBand, HoseMath.CouplingMax);
            foreach (string look in ReelIntakeGeometry.Looks)
                for (int rot = 0; rot < 4; rot++)
                {
                    var r = new HoseReelRect(10, 10, 2, 2) { Look = look, Rot = rot };
                    V2 face = HoseJoints.NozzleCoupling(r, out V2 inw);
                    V2 c = HoseJoints.FittingCentre(face, inw, -HoseMath.JoinerFace, size);
                    total++;
                    if (HoseJoints.CollarBoxGap(c, inw, size, HoseMath.CouplingMax, r.NozzleTip) <= HoseJoints.Tolerance) ok++;
                    // D9: the collar drawn 0.2 cell back from where it belongs (out along the hose) stops short of the tip
                    if (HoseJoints.CollarBoxGap(c - inw * 0.2, inw, size, HoseMath.CouplingMax, r.NozzleTip) > HoseJoints.Tolerance) caught++;
                }
            Check(ok == total && total == 16, "the reel-end collar as drawn covers the measured nozzle tip, every look x facing (" + ok + "/" + total + ")");
            Check(caught == total, "can-fail: a collar drawn 0.2 cell short of the nozzle (audit D9) is a gap in the box test (" + caught + "/" + total + ")");

            int tt = 0, tok = 0, side = 0;
            foreach (string look in TankPortGeometry.Looks)
                foreach (int sx in new[] { 1, -1 })
                {
                    tt++;
                    TankPortGeometry.PortPoint(look, 20, 20, 2, 2, sx, 0, out V2 port);
                    var axis = new V2(sx, 0);
                    double s = 1.5 * HoseMath.FittingSize(HoseMath.VisibleWidth(0, 1), HoseMath.PieceBand, HoseMath.CouplingMax);
                    V2 c = HoseJoints.FittingCentre(port, axis, -HoseMath.JoinerFace, s);
                    if (HoseJoints.CollarBoxGap(c, axis, s, HoseMath.CouplingMax, port) <= HoseJoints.Tolerance) tok++;
                    if (HoseJoints.CollarBoxGap(c + new V2(0, 0.4), axis, s, HoseMath.CouplingMax, port) > HoseJoints.Tolerance) side++;
                }
            Check(tok == tt && tt == 8, "the port-end collar as drawn covers the tank's measured flange, both sides, every look (" + tok + "/" + tt + ")");
            Check(side == tt, "can-fail: a collar 0.4 cell beside the flange (audit D8's kink) is a gap (" + side + "/" + tt + ")");
        }

        /// <summary>HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK / HOSE_CROSSING_FIX_FLAT_AS_A_PANCAKE: the over-draw spans.</summary>
        private static void OverDraw()
        {
            var line = new List<V2> { new V2(0, 0.5), new V2(10, 0.5) };
            List<double[]> one = HoseOverDraw.Spans(line, c => c.X == 4, HoseOverDraw.BuildingMargin);
            bool spanOk = one.Count == 1 && Math.Abs(one[0][0] - 3.7) < 0.06 && Math.Abs(one[0][1] - 5.3) < 0.06;
            Check(spanOk, "a hose across one building cell (x 4) is redrawn over [3.7, 5.3] (cell + the sprite margin) ("
                + string.Join(" ", one.Select(s => s[0].ToString("0.00") + "-" + s[1].ToString("0.00"))) + ")");
            List<V2> part = one.Count == 1 ? HoseOverDraw.Slice(line, one[0][0], one[0][1]) : new List<V2>();
            Check(part.Count >= 2 && Math.Abs(part[0].X - one[0][0]) < 1e-9 && Math.Abs(part[part.Count - 1].X - one[0][1]) < 1e-9,
                "the redrawn stretch is the pose cut exactly to the span");
            Check(HoseOverDraw.Covers(one, 4.5) && !HoseOverDraw.Covers(one, 2.0), "Covers: inside the span yes, before it no");
            List<double[]> two = HoseOverDraw.Spans(line, c => c.X == 4 || c.X == 5, HoseOverDraw.BuildingMargin);
            List<double[]> apart = HoseOverDraw.Spans(line, c => c.X == 2 || c.X == 7, HoseOverDraw.BuildingMargin);
            Check(two.Count == 1 && apart.Count == 2, "adjacent building cells merge into one stretch, separate ones stay two (" + two.Count + ", " + apart.Count + ")");
            Check(HoseOverDraw.Spans(line, c => false, HoseOverDraw.BuildingMargin).Count == 0, "no building on the way, nothing redrawn");

            var up = new List<V2> { new V2(0, 5), new V2(10, 5) };
            var cross = new List<IList<V2>> { new List<V2> { new V2(5, 0), new V2(5, 10) } };
            List<double[]> cs = HoseOverDraw.CrossSpans(up, cross, 0.2, 0.25);
            Check(cs.Count == 1 && Math.Abs(cs[0][0] - 4.55) < 0.06 && Math.Abs(cs[0][1] - 5.45) < 0.06,
                "a hose crossing another square on casts its crossing shadow over [4.55, 5.45] (overlap +- margin) ("
                + string.Join(" ", cs.Select(s => s[0].ToString("0.00") + "-" + s[1].ToString("0.00"))) + ")");
            var far = new List<IList<V2>> { new List<V2> { new V2(0, 7), new V2(10, 7) } };
            Check(HoseOverDraw.CrossSpans(up, far, 0.2, 0.25).Count == 0, "a hose 2 cells away is not crossed: no crossing shadow");
            List<double[]> point = HoseOverDraw.SpansWhere(up, p => Math.Abs(p.X - 5) < 1e-9, 0);
            Check(point.Count == 1 && HoseOverDraw.Covers(point, 5) && V2.Dist(HoseOverDraw.PointAtArc(up, 0.5 * (point[0][0] + point[0][1])), new V2(5, 5)) < 1e-9,
                "a single touching sample with no margin is still a (zero-length) span the probe can test, and its point is on the hose");

            // the redrawn stretch sits above the Building layer and its top below Item, and the planner prices the buildings
            double yo = DrawOrder.Alt(HoseOverDraw.OverBuildingLayer) + DrawOrder.HoseBaseLift, top = yo + HoseMath.CrossBand * HoseMath.CrossRanks + DrawOrder.HoseFittingLift + 0.0005;
            Check(yo > DrawOrder.Alt(15 + 1) && top < DrawOrder.Alt(18), "the over-building stretch draws above Building (15) and BuildingBelowTop, its top under Item (18): "
                + yo.ToString("0.0000") + ".." + top.ToString("0.0000"));
            string src = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
            Check(src.Contains("ed != null && (IsRig(ed) || DrawsOverHose(ed))") && src.Contains("DrawOverBuildings(cur,") && src.Contains("DrawCrossShadow(r, cur,"),
                "revert guard (source text): the hose world costs walk-over buildings drawn above the hose, and the draw redraws/shadows over them");
        }

        public static void Run()
        {
            Feeds();
            NozzleCouplings();
            TankPorts();
            CollarBoxes();
            OverDraw();
        }
    }
}
