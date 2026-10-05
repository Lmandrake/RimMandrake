// Owner review round 7 (2026-10-04), station 42: "pipe does NOT hook up properly to the next reel station". The round-6
// relay hose ended on the MIDPOINT of the intake cell's shared edge: from the west that is 0.45 cell below the reel art's
// one brass inlet and 0.29 cell inside its face, so the coupling floated beside the pump base. The drawn end now sits on
// the drawn reel (HoseRelay.DrawnEnd + ReelIntakeGeometry, measured from all four looks' stored and laid art), within
// HoseRelay.EndTolerance of the footprint edge, and the hose's last stretch runs straight along the intake's axis.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.GimmeSomeSlack.Hose;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class ReviewRound7Checks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "review7: " + msg);

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

            // west: both west cells couple to the art's one brass inlet, at its height (centre z - ~0.06), face 0.24-0.31 outside
            int west = 0, wt = 0;
            double r6Miss = 99;
            foreach (string look in ReelIntakeGeometry.Looks)
                foreach (bool deployed in new[] { false, true })
                {
                    wt++;
                    V2 lo = HoseRelay.DrawnEnd(relay, new Cell(9, 10), look, deployed, out _);
                    V2 hi = HoseRelay.DrawnEnd(relay, new Cell(9, 11), look, deployed, out _);
                    if (V2.Dist(lo, hi) < 1e-9 && Math.Abs(lo.Z - relay.Centre.Z) < 0.15 && lo.X < relay.X0 - 0.2) west++;
                    r6Miss = Math.Min(r6Miss, V2.Dist(HoseRelay.IntakePoint(relay, new Cell(9, 10)), lo));
                }
            Check(west == wt, "from the west both cells couple to the art's brass inlet (its height, its face outside the edge) (" + west + "/" + wt + ")");
            Check(r6Miss > 0.4, "can-fail: round 6's end (the lower west cell's edge midpoint) misses the inlet by >= " + r6Miss.ToString("0.00") +
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
            Check(ab.X == 32 && inward.X == 1 && lay.Ok && V2.Dist(lay.Flat[lay.Flat.Count - 1], e) < 1e-6 && Math.Abs(e.Z - B.Centre.Z) < 0.15 &&
                  e.X < B.X0 && e.X > B.X0 - HoseRelay.EndTolerance,
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
        }
    }
}
