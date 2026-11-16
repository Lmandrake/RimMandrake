// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// RIMMANDRAKE_FIX_SLACK_CORD_ENDS_OWNER_CAUGHT_TWO (owner live look 2026-11-16): two readings of LAID pieces and the graph, shared by the
// offline SelfTest (SelfTest/CordEndKindChecks.cs, generated scenes) and the live probe ("endkind:"), so one instrument judges both:
//   Ends    every cord end is ONE kind, a fitting or a loose end, never both at one point; a fitted end throws no sparks
//   Slopes  at every junction box arm and power switch stub a cord takes, the cord crosses the stub's tip on the stub's line and slope
//           (owner 2026-11-09 8:10 AM, "Match position AND slope ... where your adapter plug ENDS"); no box arm drawn without its cord
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    internal static class CordEndAudit
    {
        /// <summary>How far (cells) from an end's anchor a decal, tail or spark still belongs to that end.</summary>
        /// (a wall plate lies within 0.2 of its face, the old hanging wire's fray 0.3 out; a machine's plug on a one-cell lead to a conduit end is
        /// 0.5 from that end, and is the OTHER end of its cord)
        public const double EndRadius = 0.4;
        /// <summary>The slope rule's tolerance: a cord crossing a stub's tip heads within this of the stub's line.</summary>
        public const double SlopeMaxDeg = 12;
        /// <summary>...and crosses the tip this close (cells) to the stub's axis (the strand jitter is 0.03 a strand).</summary>
        public const double PosMax = 0.07;
        /// <summary>The chord (cells along the cord, from the tip outward) the heading is read over.</summary>
        public const double SlopeChord = 0.08;
        /// <summary>Where the power switch's stubs end (cells from the cell centre), read off the four looks' PowerSwitch PNGs
        /// (opaque tips 54-58 px of 64, drawSize 1): the tip a cord must leave from.</summary>
        public const double SwitchStubTip = 0.43;

        internal static readonly DecalKind[] Fitting = { DecalKind.Plug, DecalKind.PlugTop, DecalKind.WallOutlet, DecalKind.StubWall, DecalKind.StubRock,
                                                          DecalKind.PowerStrip, DecalKind.PowerStripDark, DecalKind.JunctionTin, DecalKind.JunctionTape };
        internal static readonly DecalKind[] Loose = { DecalKind.FrayLive, DecalKind.FrayDead };

        // ------------------------------------------------------------------ the ends rule
        internal sealed class EndRead
        {
            public int Ends, Both, None, FitSparks, FitTails, TerminalsFitted, WallTerminalsFitted, StubsLoose;
            public readonly List<string> Bad = new List<string>();
        }

        /// <summary>Every end of the graph (a wall/rock stub's face, a conduit end's point): what is drawn there.</summary>
        internal static EndRead Ends(CordGraph g, List<LaidPiece> ps, string scene, Func<V2, bool> keep = null)
        {
            var r = new EndRead();
            foreach (CordNode nd in g.Nodes.Values)
            {
                bool stub = nd.Type == NodeType.StubWall || nd.Type == NodeType.StubRock;
                bool term = nd.Type == NodeType.Terminal && !nd.Seam;
                if (!stub && !term) continue;
                V2 at = stub ? nd.Face : nd.Pos;
                if (keep != null && !keep(at)) continue;
                List<LaidPiece> mine = ps.Where(p => p.Strands.Any(s => s.Pts != null && s.Pts.Count > 1 && !s.OverFace
                    && (V2.Dist(s.Pts[0], at) < EndRadius + 0.2 || V2.Dist(s.Pts[s.Pts.Count - 1], at) < EndRadius + 0.2))).ToList();
                if (mine.Count == 0) continue;
                r.Ends++;
                int fit = mine.Sum(p => p.Decals.Count(d => Fitting.Contains(d.Kind) && V2.Dist(d.Pos, at) <= EndRadius));
                int loose = mine.Sum(p => p.Decals.Count(d => Loose.Contains(d.Kind) && V2.Dist(d.Pos, at) <= EndRadius));
                int tails = mine.Sum(p => p.Strands.Count(s => s.OverFace && s.Lifted && s.Pts != null && s.Pts.Count > 0 && V2.Dist(s.Pts[0], at) <= EndRadius));
                int sparks = mine.Sum(p => p.Ends.Count(e => V2.Dist(e.Tip, at) <= EndRadius));
                string where = $"{scene} {nd.Type}{(nd.WallTerminal ? "(ends in wall)" : "")}@{nd.Cell}";
                if (fit > 0 && (loose > 0 || tails > 0))
                {
                    r.Both++;
                    string what = string.Join(" ", mine.SelectMany(p => p.Decals).Where(d => (Fitting.Contains(d.Kind) || Loose.Contains(d.Kind)) && V2.Dist(d.Pos, at) <= EndRadius)
                                                       .Select(d => $"{d.Kind}@{V2.Dist(d.Pos, at):0.00}"));
                    r.Bad.Add($"{where}: {fit} fitting(s) AND {loose} loose end(s), {tails} hanging tail(s) at one point [{what}]");
                }
                if (fit > 0 && sparks > 0) { r.FitSparks++; r.Bad.Add($"{where}: a fitted end throws sparks ({sparks})"); }
                if (fit > 0 && tails > 0) r.FitTails++;
                if (fit == 0 && loose == 0) { r.None++; r.Bad.Add($"{where}: drawn as nothing (no fitting, no loose end)"); }
                if (term && fit > 0) { r.TerminalsFitted++; r.Bad.Add($"{where}: a conduit end wears a fitting"); }
                if (stub && nd.WallTerminal && fit > 0) { r.WallTerminalsFitted++; r.Bad.Add($"{where}: a run that ends inside the wall is drawn plugged in"); }
                if (stub && !nd.WallTerminal && loose > 0) { r.StubsLoose++; r.Bad.Add($"{where}: a cord through the wall frays at its entry"); }
            }
            return r;
        }

        // ------------------------------------------------------------------ the slope rule
        internal sealed class SlopeRead
        {
            public int Arms, Taken, Empty, EmptyAllowed, OffLine, OffSlope, Short;
            public double WorstDeg, WorstPos;
            public readonly List<string> Bad = new List<string>();
        }

        internal static V2 Rot(V2 v, double a) => new V2(v.X * Math.Cos(a) - v.Z * Math.Sin(a), v.X * Math.Sin(a) + v.Z * Math.Cos(a));
        private static double Cross(V2 a, V2 b) => a.X * b.Z - a.Z * b.X;
        private static double Dot(V2 a, V2 b) => a.X * b.X + a.Z * b.Z;

        /// <summary>One connector: its meeting point, the arm directions, the arm length to the tip, and whether empty arms are art.</summary>
        internal sealed class Fitted { public string Name; public V2 M; public List<V2> Arms; public double Tip; public bool EmptyOk; }

        /// <summary>Every junction box (posed from its decal alone) and every power switch in the scene.</summary>
        internal static List<Fitted> Connectors(CordWorld w, CordGraph g, List<LaidPiece> ps)
        {
            var o = new List<Fitted>();
            var devStubs = g.Nodes.Values.Where(n => n.Type == NodeType.StubDevice).Select(n => n.Face).ToList();
            foreach (LaidPiece p in ps)
                foreach (CordDecal d in p.Decals)
                {
                    if (d.Kind != DecalKind.JunctionTin && d.Kind != DecalKind.JunctionTape) continue;
                    // both arts: arms 55.5 px of 128 from the meeting point at JunctionScale 1.15 (selftest_gss_junction_necks.py SLOTS)
                    double tip = 55.5 / 128.0 * d.Scale;
                    if (d.Kind == DecalKind.JunctionTin)
                        o.Add(new Fitted { Name = $"box X@({d.Pos.X:0.0},{d.Pos.Z:0.0})", M = d.Pos, Tip = tip,
                                           Arms = Enumerable.Range(0, 4).Select(k => Rot(new V2(1, 0), d.Angle + k * Math.PI / 2)).ToList(),
                                           EmptyOk = devStubs.Any(f => V2.Dist(f, d.Pos) < 0.5) });
                    else
                    {
                        V2 m = d.Pos + Rot(new V2(0, CordBuilder.TapeAnchorZ * d.Scale), d.Angle);
                        o.Add(new Fitted { Name = $"box T@({m.X:0.0},{m.Z:0.0})", M = m, Tip = tip,
                                           Arms = new[] { new V2(1, 0), new V2(-1, 0), new V2(0, -1) }.Select(a => Rot(a, d.Angle)).ToList() });
                    }
                }
            foreach (MachineInfo m in w.Machines.Where(m => m.SidePorts))
                o.Add(new Fitted { Name = "switch " + m.Id, M = new V2(m.X0 + 0.5, m.Z0 + 0.5), Tip = SwitchStubTip, EmptyOk = true,
                                   Arms = new[] { new V2(1, 0), new V2(-1, 0), new V2(0, 1), new V2(0, -1) }.ToList() });
            return o;
        }

        /// <summary>Where a strand that ends at a connector first crosses the tip circle, walking out from its end; and its heading there.</summary>
        private static bool Crossing(List<V2> P, bool fromStart, V2 M, double R, out V2 x, out V2 head)
        {
            x = default(V2); head = default(V2);
            int n = P.Count;
            V2 At(int k) => fromStart ? P[k] : P[n - 1 - k];
            int i = 0;
            if (V2.Dist(At(0), M) >= R)
                x = At(0);
            else
            {
                for (i = 1; i < n && V2.Dist(At(i), M) < R; i++) { }
                if (i >= n) return false;
                V2 a = At(i - 1), b = At(i);
                double lo = 0, hi = 1;
                for (int it = 0; it < 30; it++) { double mid = (lo + hi) / 2; if (V2.Dist(a + (b - a) * mid, M) < R) lo = mid; else hi = mid; }
                x = a + (b - a) * hi;
            }
            // heading: the chord from the crossing to the point SlopeChord further along the cord
            double acc = 0;
            V2 prev = x;
            for (int k = Math.Max(i, 1); k < n; k++)
            {
                V2 q = At(k);
                double s = V2.Dist(prev, q);
                if (acc + s >= SlopeChord) { V2 y = prev + (q - prev) * ((SlopeChord - acc) / Math.Max(s, 1e-9)); head = (y - x).Norm(); return true; }
                acc += s; prev = q;
            }
            if (V2.Dist(prev, x) < 1e-6) return false;
            head = (prev - x).Norm();
            return true;
        }

        internal static SlopeRead Slopes(CordWorld w, CordGraph g, List<LaidPiece> ps, string scene, Func<V2, bool> keep = null)
        {
            var r = new SlopeRead();
            List<CordStrand> strands = ps.SelectMany(p => p.Strands).Where(s => !s.OverFace && s.Pts != null && s.Pts.Count > 1).ToList();
            var owner = new Dictionary<CordStrand, LaidPiece>();
            foreach (LaidPiece p in ps) foreach (CordStrand s in p.Strands) owner[s] = p;
            List<Fitted> all = Connectors(w, g, ps);
            foreach (Fitted f in all)
            {
                if (keep != null && !keep(f.M)) continue;
                var taken = new HashSet<int>();
                foreach (CordStrand s in strands)
                    foreach (bool atStart in new[] { true, false })
                    {
                        V2 e = atStart ? s.Pts[0] : s.Pts[s.Pts.Count - 1];
                        if (V2.Dist(e, f.M) > f.Tip + 0.25) continue;
                        // an end belongs to the connector it is nearest (two boxes a cell apart share one short cord)
                        if (all.Any(o => o != f && V2.Dist(e, o.M) < V2.Dist(e, f.M))) continue;
                        if (!Crossing(s.Pts, atStart, f.M, f.Tip, out V2 x, out V2 head)) continue;
                        V2 dir = (x - f.M).Norm();
                        int arm = Enumerable.Range(0, f.Arms.Count).OrderByDescending(k => Dot(dir, f.Arms[k])).First();
                        V2 u = f.Arms[arm];
                        taken.Add(arm);
                        r.Taken++;
                        double gap = V2.Dist(e, f.M) - f.Tip;
                        double off = Math.Abs(Cross(x - f.M, u));
                        double deg = Math.Acos(Math.Max(-1, Math.Min(1, Dot(head, u)))) * 180 / Math.PI;
                        r.WorstDeg = Math.Max(r.WorstDeg, deg); r.WorstPos = Math.Max(r.WorstPos, off);
                        string at = $"{scene} {f.Name} arm ({u.X:0.##},{u.Z:0.##}) cord {owner[s].EndA}|{owner[s].EndB} {Geo.Length(s.Pts):0.00} long";
                        if (gap > 0.03) { r.Short++; r.Bad.Add($"{at}: the cord stops {gap:0.00} short of the stub's tip"); }
                        else if (off > PosMax) { r.OffLine++; r.Bad.Add($"{at}: the cord crosses the tip {off:0.00} off the stub's line"); }
                        else if (deg > SlopeMaxDeg) { r.OffSlope++; r.Bad.Add($"{at}: the cord leaves the tip {deg:0} deg off the stub's slope"); }
                    }
                // an arm also has its cord when one lies along it under the arm (a cord between two fittings a cell apart ends nearer the other)
                for (int k = 0; k < f.Arms.Count; k++)
                    if (!taken.Contains(k) && strands.Any(s => s.Pts.Any(q =>
                        {
                            double along = Dot(q - f.M, f.Arms[k]);
                            return along > 0.5 * f.Tip && along < f.Tip && Math.Abs(Cross(q - f.M, f.Arms[k])) < PosMax;
                        })))
                        taken.Add(k);
                r.Arms += f.Arms.Count;
                int empty = f.Arms.Count - taken.Count;
                if (empty <= 0) continue;
                if (f.EmptyOk) r.EmptyAllowed += empty;
                else
                {
                    r.Empty += empty;
                    string near = string.Join(" ", strands.SelectMany(s => new[] { s.Pts[0], s.Pts[s.Pts.Count - 1] }).Where(q => V2.Dist(q, f.M) < 1.3).Select(q => $"({q.X:0.00},{q.Z:0.00})"));
                    string free = string.Join(" ", Enumerable.Range(0, f.Arms.Count).Where(k => !taken.Contains(k)).Select(k => $"({f.Arms[k].X:0},{f.Arms[k].Z:0})"));
                    r.Bad.Add($"{scene} {f.Name}: {empty} arm(s) {free} drawn with no cord on them; cord ends near: {near}");
                }
            }
            return r;
        }
    }
}
