// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// The live cut end's lay (RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN, owner 2026-11-16: "Use Fable to solve this once and for all").
// Three bars meet where a cord leaves a conduit end and becomes a whipping live end: the live run leaves the conduit end straight (CordAudit,
// 15 degrees over 0.6 cell), the join never bends under radius 0.10 on any frame of the whip (StubJoins.LiveEnds), the whipping tail is 0.7 to
// 1.15 cells (LaneAChecks). They were held by easing the laid corner and tuning what it kept (eight constants; worst radius 0.101 against
// 0.10 on the suite's 36 tails, and 3,935 of 30,768 live ends failing over the worlds the suite never built).
//
// Solved offline first (src/RimMandrake/Utils/mockups/messy_conduit/live_end_lay.py, live_end_sweep.py; this file is its port). Two things were
// really one thing described twice, and the bars now hold by construction:
//   the whip and the laid cord   CordMotion.Whip bends the tail with a travelling curvature, the laid curvature plus the wave never past
//                                1 / BendR: every frame of every seed is BendR or wider. No lay can be pinched by the whip.
//   the cut lead's join          BlendCutRun's Dubins join and the live-join easing are one lay, here, run last: the straight run (Run), joined
//                                to the cord by a Dubins path of radius BendR or wider, the whip's joint set on the cord as finally laid.
// The owner's order for the join (2026-11-16, by picture, "C, then B, then D in decreasing preference"): a broad lazy bend, then a small round
// hook where the broad one has no room, then his wire-tied loop. The tied loops are devices: tried only after every bare join has failed.
// No number here is tuned to a check: each is a bar's own number, or a bar's number with a stated margin.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    internal static class CordLiveEnd
    {
        /// <summary>The builder's sample step, cells.</summary>
        public const double Step = 0.05;
        /// <summary>The straight run out of the conduit end: the straight bar reads the heading up to the first sample at or past 0.6 back.</summary>
        public const double Run = 0.6 + Step;
        /// <summary>The tightest bend a live end's lay or whip may make: twice the pinch bar.</summary>
        public const double BendR = 2 * StubJoins.MinBendR;
        /// <summary>Radii the bend bar passes anywhere (BlendCutRun's: under 90 degrees a cell).</summary>
        internal static readonly double[] BroadR = { 0.7, 0.85, 1.0, 0.66 };
        /// <summary>Tighter joins: taken only where the bend bar allows the bend they make (under 90 degrees, a cut end's own first cell, a wall).</summary>
        internal static readonly double[] TightR = { 0.5, 0.4, 0.3, 0.25, BendR };
        /// <summary>The tied loop's radii (CordPlugExit's: the owner's "about 0.3-0.4 cell" across).</summary>
        internal static readonly double[] LoopR = { 0.19, 0.17 };
        /// <summary>The far fitting's own run a join never reaches into (BlendCutRun.BlendTail), and a fitting's straight bit.</summary>
        public const double FarKeep = 0.5, FarStiff = 0.15;
        /// <summary>The whip's joint and a service loop stay this far off the far fitting's tip: the slope rule reads the cord's heading over 0.08 there
        /// (CordEndAudit.SlopeChord), one sample past it.</summary>
        public const double FitOff = 0.10;
        /// <summary>The whip bar (0.7 to 1.15) with a sample to spare at each end.</summary>
        public const double TailMin = 0.7 + Step, TailMax = 1.15 - Step;
        /// <summary>Half the straight bar's 15 degrees (a join's own run is dead straight), and how near the conduit end the tip must be (CordAudit's 0.08).</summary>
        public const double StraightDeg = 7.5, TipOff = 0.08;

        internal enum Kind { Kept, Join, TurnLoop, Still, None }

        internal sealed class Result
        {
            public List<V2> Pts;
            /// <summary>Points at the end of Pts that whip (0 = none).</summary>
            public int Count;
            public Kind Kind;
            public double R;
            /// <summary>Tied loops, arcs along Pts from Pts[0].</summary>
            public List<CordTie> Ties;
            public bool Device => Kind == Kind.TurnLoop;
            /// <summary>What the lay was told of the far end (the sweep check reads a still end again with these).</summary>
            public bool FarCut;
            public double FarOff;
            public V2 Tip, Out;
        }

        /// <summary>What a cord's surroundings are for the lay: where a point may lie, and how many faults the cord bars count on a whole cord
        /// (unforced bends with these ties left out, and folds): a join never adds one.</summary>
        internal sealed class Site
        {
            /// <summary>The strand's declared length limit (CordBuilder.LengthLimit, the builder's one rule on how long a cord may be; the fuzz
            /// holds every strand to it). The lay had a cap of its own, 2.5 cells of growth borrowed from BlendCutRun: that second rule alone left
            /// 21 of 288 close fittings unlaid (RIMMANDRAKE_LAY_SLACK_CLOSE_FITTINGS_TWENTY_ONE_UNLAID).</summary>
            public double MaxLen = double.MaxValue;
            /// <summary>Whether a point lies on the far fitting's own body (a box, plate, strip or heap: within the builder's keep-off of its node's
            /// point; a machine: its footprint): once a join has left its far fitting it never comes back over it. Null: no body (a far cut end).</summary>
            public Func<V2, bool> OnFar;
            public Func<V2, bool> Clear;
            /// <summary>Whether a point lies in a doorway. A join goes through one only on the end's own line, straight (a cord through a door
            /// crosses it once, and a cut end in the cell past a door has its run's line through that door). Null: no doors.</summary>
            public Func<V2, bool> Door;
            public Func<List<V2>, List<CordTie>, int> Bends, Kinks;
            /// <summary>How many extra lines the cord draws at a door (CordShape.RingReturns: the owner, 2026-11-07, three cables out of a doorway
            /// to one end): a join never adds one. Null: not read.</summary>
            public Func<List<V2>, int> DoorReturns;
        }

        /// <summary>How long the whipping tail is: WhipLen of cord; never into the far fitting's stiff bit; when the far end is a cut end too, never
        /// more than half the cord (its tail has the other half); never into a tied loop (a tie holds the cord still).</summary>
        internal static double TailLimit(List<V2> P, List<CordTie> ties, bool farCut, double farOff = FitOff)
        {
            double L = Geo.Length(P), limit = Math.Min(CordMotion.WhipLen, farCut ? L * 0.5 : L - farOff);
            if (ties != null) foreach (CordTie t in ties) limit = Math.Min(limit, L - t.S1);
            return limit;
        }

        /// <summary>P with a point of its own exactly where the whip's joint is; the tail's point count. The tail is then exactly TailLimit long
        /// whatever the cord's sampling (the count was taken at EndDecor, before later passes moved the points).</summary>
        internal static List<V2> SetJoint(List<V2> P, List<CordTie> ties, bool farCut, double farOff, out int count)
        {
            count = 0;
            if (P.Count < 3) return P;
            double[] cl = Geo.CumLen(P);
            double L = cl[cl.Length - 1], limit = TailLimit(P, ties, farCut, farOff);
            if (limit < 3 * Step) return P;
            double s = L - limit;
            int i = 0;
            while (i < P.Count && cl[i] < s - 1e-9) i++;
            if (i < P.Count && Math.Abs(cl[i] - s) < 1e-6) { count = P.Count - i; return P; }
            if (i <= 0 || i >= P.Count) return P;
            double d = cl[i] - cl[i - 1];
            V2 x = d < 1e-12 ? P[i] : P[i - 1] + (P[i] - P[i - 1]) * ((s - cl[i - 1]) / d);
            var R = new List<V2>(P.Count + 1);
            R.AddRange(P.GetRange(0, i));
            R.Add(x);
            R.AddRange(P.GetRange(i, P.Count - i));
            count = R.Count - i;
            return R;
        }

        /// <summary>The tightest laid bend in the pinch bar's window: the last 0.4 cell before the joint (StubJoins.LiveEnds' lead) and the tail.</summary>
        internal static double WindowRadius(List<V2> P, int count)
        {
            double[] cl = Geo.CumLen(P);
            double s0 = cl[P.Count - count] - 0.4 - Step;
            int i0 = 0;
            while (i0 < P.Count - 1 && cl[i0 + 1] < s0) i0++;
            return StubJoins.MinRadius(P.GetRange(i0, P.Count - i0));
        }

        /// <summary>A fold in the pinch window. The radius read takes three points on one line as straight, and a cord doubled back exactly on
        /// itself is three points on one line: the corner read (CordShapeAudit.Corners) sees it.</summary>
        internal static bool WindowFolds(List<V2> P, int count)
        {
            double[] cl = Geo.CumLen(P);
            double s0 = cl[P.Count - count] - 0.4 - Step;
            int i0 = 0;
            while (i0 < P.Count - 1 && cl[i0 + 1] < s0) i0++;
            return CordShapeAudit.Corners(P.GetRange(i0, P.Count - i0)).Count > 0;
        }

        /// <summary>'' or the letters that fail, each a bar's own reading with room to spare: S the run dead straight to the conduit end (read on
        /// every lead, not only a cell or more); T the tail TailMin to TailMax; P every laid bend in the pinch window BendR or wider (a tied loop's
        /// own arc at its own radius).</summary>
        internal static string Bars(List<V2> P, V2 tip, V2 outDir, int count, List<CordTie> ties, double bendR = BendR, bool still = false,
                                    double deg = StraightDeg, double tailLo = TailMin, double tailHi = TailMax)
        {
            string bad = "";
            V2 e = P[P.Count - 1];
            double arrive = CordAudit.AngDiff(CordAudit.Ang(e - CordAudit.PointBack(P, 0.1)), CordAudit.Ang(outDir)) * 180 / Math.PI;
            if (arrive > deg || CordAudit.TipTurn(P) * 180 / Math.PI > deg || V2.Dist(e, tip) > TipOff) bad += "S";
            if (still)
            {
                // a cord that lies still: no tail to read; its last cell and a half (the window a whip would have had) is still laid round
                int c = Math.Min(P.Count - 1, CordBuilder.TailCount(P, false, CordMotion.WhipLen));
                return c >= 3 && (WindowRadius(P, c) < bendR * 0.98 || WindowFolds(P, c)) ? bad + "P" : bad;
            }
            if (count <= 0) return bad + "T";
            double tail = Geo.Length(P.GetRange(P.Count - count, count));
            if (tail < tailLo - 1e-9 || tail > tailHi + 1e-9) bad += "T";
            double need = bendR;
            if (ties != null && ties.Count > 0)
            {
                double[] cl = Geo.CumLen(P);
                double win0 = cl[P.Count - count] - 0.4 - Step;
                if (ties.Any(t => t.S1 > win0)) need = Math.Min(need, LoopR.Min());
            }
            if (WindowRadius(P, count) < need * 0.98 || WindowFolds(P, count)) bad += "P";
            return bad;
        }

        private static V2 PointAt(List<V2> P, double[] cl, double s, out int i)
        {
            i = 0;
            while (i < P.Count && cl[i] < s) i++;
            if (i <= 0) { i = 0; return P[0]; }
            if (i >= P.Count) { i = P.Count - 1; return P[P.Count - 1]; }
            double d = cl[i] - cl[i - 1];
            return d < 1e-12 ? P[i] : P[i - 1] + (P[i] - P[i - 1]) * ((s - cl[i - 1]) / d);
        }

        /// <summary>The cord's heading as it ARRIVES at J: from the last point of the kept cord that is not J itself. (At a vertex where the cord
        /// turns, the mean of the headings either side is neither: a join leaving on it kinked the cord at J, and every join from a fitting's stiff
        /// bit was then refused as a corner.)</summary>
        private static double HeadingInto(List<V2> head, V2 J, List<V2> P, int i)
        {
            for (int k = head.Count - 1; k >= 0; k--)
                if (V2.Dist(J, head[k]) > 1e-6) { V2 d = J - head[k]; return Math.Atan2(d.Z, d.X); }
            V2 a = P[Math.Max(0, i - 1)], b = P[Math.Min(P.Count - 1, i + 1)];
            return Math.Atan2(b.Z - a.Z, b.X - a.X);
        }

        /// <summary>Whether a join, once it has left its far fitting, comes back over that fitting's body.</summary>
        private static bool OverFarBody(IEnumerable<V2> path, Site site)
        {
            if (site.OnFar == null) return false;
            bool left = false;
            foreach (V2 q in path)
            {
                if (!site.OnFar(q)) left = true;
                else if (left) return true;
            }
            return false;
        }

        /// <summary>Whether a new join comes back across the straight live run (or within a cord's width of it).</summary>
        private static bool CrossesRun(List<V2> path, V2 A, V2 T, int skipLast)
        {
            V2 u = (T - A).Norm();
            double ln = V2.Dist(A, T);
            for (int k = 0; k < path.Count - skipLast; k++)
            {
                V2 q = path[k] - A;
                double al = q.X * u.X + q.Z * u.Z, ac = Math.Abs(q.X * u.Z - q.Z * u.X);
                if (al > 0.1 && al < ln + 0.1 && ac < 0.12) return true;
            }
            return false;
        }

        private struct Cand { public double Cost, R, SJ; public CordShape.Dubins.Path Dp; public V2 J; public int I; public double HJ; }

        /// <summary>Lays the live end of P (read toward the cut end at <paramref name="tip"/>, the conduit running <paramref name="outDir"/>).
        /// Kept: the cord as handed already holds the bars with margin. Join: the straight run joined by a Dubins path. TurnLoop: a join that comes
        /// right round at the tied loop's radius, tied where it crosses itself. Still: the cord has no room for a whipping tail, it is returned as
        /// handed and does not whip. None: nothing holds, the cord is returned as handed (its joint still set).
        /// <paramref name="farCut"/>: the far end is a live cut end too (two tails share the cord); <paramref name="farOff"/>: the cord at the far
        /// end the tail and a join never enter (a fitting's stiff bit, a live end's run, a dead end's limp curl).</summary>
        internal static Result Lay(List<V2> P0, V2 tip, V2 outDir, Site site, List<CordTie> ties0, bool farCut, double farOff = FitOff, bool allowDevice = true)
        {
            Result r = LayCore(P0, tip, outDir, site, ties0, farCut, farOff, allowDevice);
            r.FarCut = farCut; r.FarOff = farOff; r.Tip = tip; r.Out = outDir.Norm();
            // a cord laid to lie still that could whip after all, whips: only a cord with no tail that holds the bars lies still
            if (r.Kind == Kind.Still && WouldWhip(r, out List<V2> pts, out int cnt)) { r.Pts = pts; r.Count = cnt; r.Kind = Kind.Join; }
            return r;
        }

        /// <summary>Whether a cord returned as lying still holds every bar with a whipping tail set on it (then it must whip: the owner's "a2, and
        /// where it does not apply then c").</summary>
        internal static bool WouldWhip(Result r, out List<V2> pts, out int cnt)
        {
            pts = SetJoint(new List<V2>(r.Pts), r.Ties, r.FarCut, r.FarOff, out cnt);
            V2 T = V2.Dist(pts[pts.Count - 1], r.Tip) <= TipOff ? pts[pts.Count - 1] : r.Tip;
            return Bars(pts, T, r.Out, cnt, r.Ties) == "";
        }

        private static Result LayCore(List<V2> P0, V2 tip, V2 outDir, Site site, List<CordTie> ties0, bool farCut, double farOff, bool allowDevice)
        {
            var ties = ties0 == null ? new List<CordTie>() : new List<CordTie>(ties0);
            V2 o = outDir.Norm();
            V2 T = V2.Dist(P0[P0.Count - 1], tip) <= TipOff ? P0[P0.Count - 1] : tip;
            List<V2> P = SetJoint(new List<V2>(P0), ties, farCut, farOff, out int cnt0);
            string bad0 = Bars(P, T, o, cnt0, ties);
            var kept = new Result { Pts = P, Count = cnt0, Kind = Kind.Kept, Ties = ties };
            if (bad0 == "") return kept;
            double[] cum = Geo.CumLen(P);
            double Lold = cum[cum.Length - 1], ho = Math.Atan2(o.Z, o.X);
            V2 A = T - o * Run;
            int runN = (int)Math.Round(Run / Step);
            var run = new List<V2>(runN);
            for (int k = 1; k <= runN; k++) run.Add(A + (T - A) * (k / (double)runN));
            int oldBends = site.Bends(P, ties), oldKinks = site.Kinks(P, ties), oldDoor = site.DoorReturns == null ? 0 : site.DoorReturns(P);
            double tieEnd = ties.Count > 0 ? ties.Max(t => t.S1) : 0;
            // where the old cord may be left: past the far fitting's own run and its tied loops (a far cut end's own straight run stays as laid);
            // a short cord is laid whole from the fitting's stiff bit
            double loKeep = Math.Max(Math.Max(FarKeep, farOff), tieEnd + 0.1);
            if (farCut) loKeep = Math.Max(Run, tieEnd + 0.1);
            // every place the old cord may be left: a tenth of a cell apart over the four cells before the run, half a cell apart beyond, back to
            // the far fitting's own run; and the whole cord from the fitting's stiff bit. (Joins were tried only within four cells of the run, and
            // whole only on a cord under three cells: on a long slack cord to a fitting a cell away, no join near the end keeps off that fitting.)
            var joins = new List<double>();
            for (double s = Lold - Run - 0.2; s >= loKeep - 1e-9; s -= Lold - s <= Run + 4.0 ? 0.1 : 0.5) joins.Add(s);
            if ((joins.Count == 0 || joins[joins.Count - 1] > loKeep + 0.05) && Lold - loKeep > 0.2) joins.Add(loKeep);
            if (tieEnd == 0 && !farCut && farOff <= FarStiff) joins.Add(FarStiff);
            bool still = false;      // the second round: a cord with no room for a tail is laid to lie still
            Result Judge(List<V2> R, List<CordTie> newTies, Kind kind, double r, out string bad)
            {
                int cnt = 0;
                if (!still) R = SetJoint(R, newTies, farCut, farOff, out cnt);
                bad = Bars(R, T, o, cnt, newTies, BendR, still);
                if (bad != "") return null;
                if (site.Bends(R, newTies) > oldBends) { bad = "B"; return null; }
                if (site.Kinks(R, newTies) > oldKinks) { bad = "K"; return null; }
                if (site.DoorReturns != null && site.DoorReturns(R) > oldDoor) { bad = "D"; return null; }
                return new Result { Pts = R, Count = cnt, Kind = still ? Kind.Still : kind, R = r, Ties = newTies };
            }

            Result Attempt(double[] radii, bool tieLoops, bool overRun = false)
            {
                // every join of these radii (one class, broad or tight): the one that disturbs the cord least first (cord laid again plus length
                // gained or lost), the broader bend between equals. Broadest-first drew rings a cell across on a one-cell stub's three strands
                var cands = new List<Cand>();
                var all = new List<CordShape.Dubins.Path>(6);
                foreach (double r in radii)
                    foreach (double sJ in joins)
                    {
                        V2 J = PointAt(P, cum, sJ, out int i);
                        List<V2> head = P.GetRange(0, i);
                        double hJ = HeadingInto(head, J, P, i), old = Lold - sJ - Run;
                        foreach (CordShape.Dubins.Path dp in CordShape.Dubins.All(J, hJ, A, ho, r, all))
                        {
                            if (sJ + dp.Len + Run > site.MaxLen) continue;
                            // the rod bar: a join's straight, with the run when it runs on into it
                            if (dp.Word < 4 && dp.P * r + (dp.Q * r < Step ? Run : 0) > CordShapeAudit.RodLen - 2 * Step) continue;
                            cands.Add(new Cand { Cost = Math.Round((Lold - sJ) + Math.Abs(dp.Len - old), 1), R = r, SJ = sJ, Dp = dp, J = J, I = i, HJ = hJ });
                        }
                    }
                foreach (Cand c in cands.OrderBy(x => x.Cost).ThenBy(x => -x.R).ThenBy(x => -x.SJ))
                {
                    List<V2> arc = CordShape.Dubins.Sample(c.J, c.HJ, c.Dp, Step);
                    if (arc.Count == 0) continue;
                    arc[arc.Count - 1] = A;
                    if (!arc.All(site.Clear) || !run.All(site.Clear)) continue;
                    // through a doorway only on the run's own line
                    if (site.Door != null && arc.Any(q => site.Door(q) && Math.Abs((q.X - A.X) * o.Z - (q.Z - A.Z) * o.X) > Step)) continue;
                    var join = new List<V2>(arc.Count + 1) { c.J };
                    join.AddRange(arc);
                    if (!overRun && CrossesRun(join, A, T, 3)) continue;
                    if (OverFarBody(join.Concat(run), site)) continue;
                    var R = new List<V2>(c.I + arc.Count + run.Count + 1);
                    R.AddRange(P.GetRange(0, c.I));
                    R.AddRange(join);
                    R.AddRange(run);
                    var newTies = new List<CordTie>(ties);
                    if (tieLoops)
                    {
                        // the tie binds where the cord crosses itself: only a path that comes right round is a tied loop, and it leaves no other
                        // bend of that radius untied
                        string w = CordShape.Dubins.WordOf(c.Dp);
                        double[] part = { c.Dp.T, c.Dp.P, c.Dp.Q };
                        double acc = c.SJ, loose = 0;
                        bool got = false;
                        for (int k = 0; k < 3; k++)
                        {
                            if (w[k] != 'S' && part[k] >= 300 * Math.PI / 180)
                            {
                                V2 at = PointAt(R, Geo.CumLen(R), acc, out int _);
                                newTies.Add(new CordTie { S0 = acc, S1 = acc + part[k] * c.R, At = at, Angle = c.HJ + Math.PI / 2 });
                                got = true;
                            }
                            else if (w[k] != 'S') loose += part[k];
                            acc += part[k] * c.R;
                        }
                        if (!got || loose > 100 * Math.PI / 180) continue;
                    }
                    Result res = Judge(R, newTies, tieLoops ? Kind.TurnLoop : Kind.Join, c.R, out string _);
                    if (res != null) return res;
                }
                return null;
            }

            // "a join never comes back across its own live run" was the lay's own rule, not a bar: a fitting within a cell of the conduit end, beside
            // or ahead of it, has no other way round to the run's start. Such a join is taken only after every join that keeps off the run
            Result got = Attempt(BroadR, false) ?? Attempt(TightR, false) ?? Attempt(BroadR, false, true) ?? Attempt(TightR, false, true);
            // no join holds: a handed cord already as round as the tied loop itself is kept, a device could not better it
            if (got == null && Bars(P, T, o, cnt0, ties, LoopR.Min()) == "") return kept;
            if (got == null && allowDevice) got = Attempt(LoopR, true);
            if (got != null) return got;
            // no lay with the lay's own margins: the cord as handed, when it holds the three bars as the bars themselves read them (15 degrees,
            // a tail of 0.7 to 1.15, no bend under the pinch bar), keeps its lay and its whip. (A cord that crosses blocked ground a fifth of a
            // cell behind its end has no join to take: it was returned as handed with its whip taken away, random world 257.)
            if (Bars(P, T, o, cnt0, ties, StubJoins.MinBendR / 0.98, false, 15, 0.7, 1.15) == "") return kept;
            // the owner, 2026-11-16 (by picture, of a cut end right in front of its fitting): "a2, and where it does not apply then c": a cord
            // no lay can give a whipping tail lies still and only sparks. It is still laid straight out of the conduit end: as handed when that
            // holds, else by the same joins
            if (Bars(P0, T, o, 0, ties, LoopR.Min(), still: true) == "") return new Result { Pts = new List<V2>(P0), Count = 0, Kind = Kind.Still, Ties = ties };
            still = true;
            P = new List<V2>(P0);
            cum = Geo.CumLen(P);
            got = Attempt(BroadR, false) ?? Attempt(TightR, false) ?? Attempt(BroadR, false, true) ?? Attempt(TightR, false, true);
            if (got != null) return got;
            // nothing holds: the cord is returned as handed, its joint set
            return new Result { Pts = SetJoint(new List<V2>(P0), ties, farCut, farOff, out int cntNone), Count = cntNone, Kind = Kind.None, Ties = ties };
        }
    }
}
