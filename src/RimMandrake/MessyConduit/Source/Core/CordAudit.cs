// Messy Conduit core: Verse-free (see CordMath.cs header).
// Art-fit audit (polish pass 2026-10-02): reads LAID pieces and the graph only and reports whether the
// shipped art fits the cords: junction arms along the arriving cords, plugs into their machines, stubs
// on the face, dead ends limp, live ends straight. Shared by the offline SelfTest and the live probe
// ("artfit"), so the same property is proven offline and in the running game.
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.MessyConduit.Core
{
    public sealed class ArtFitResult
    {
        public int Junctions, JunctionFaults, PlugEnds, PlugFaults, Stubs, StubFaults, DeadEnds, DeadFaults, LiveEnds, LiveFaults;
        public List<double> DeadOffLine = new List<double>(), LiveArrivalDeg = new List<double>();
        public List<string> Messages = new List<string>();
        /// <summary>Piles (owner review 2026-10-04 B2/B13): connectors in tangles, strips anywhere, cable ends in a pile that
        /// land on no connector port, connectors with fewer than two cables plugged in, rock holes drawn unforeshortened.</summary>
        public int Piles, PileConnectors, PileJunctions, Strips, PileLooseEnds, PileIdleConnectors, FlatRockHoles, FlatWallPlates;
        public int Faults => JunctionFaults + PlugFaults + StubFaults + DeadFaults + LiveFaults + PileLooseEnds + PileIdleConnectors + FlatRockHoles + FlatWallPlates;
    }

    public static class CordAudit
    {
        
        // Art geometry measured from the shipped PNGs (Textures/RimMandrake/MessyConduit), in canvas units
        // (1 = the decal's full side), independent of the builder (CordBuilder keeps its own copies):
        //   Junction_Tape: a T, arms along art +X, -X and -Z; the arms meet 0.152 above the canvas centre.
        //   Junction_Tin:  a cross, four arms, meeting at the centre.
        //   StubWall / StubRock: placed and judged by WallMount (round 4).
        //   Plug: cord along -X, the head's face at +0.46 X.
        private static readonly double[] TapeArms = { 0, Math.PI, -Math.PI / 2 };
        private static readonly double[] TinArms = { 0, Math.PI / 2, Math.PI, -Math.PI / 2 };
        private const double TapeAnchorZ = 0.152, PlugFace = 0.46;

        internal static double AngDiff(double a, double b)
        {
            double d = (a - b) % (2 * Math.PI);
            if (d < -Math.PI) d += 2 * Math.PI;
            if (d > Math.PI) d -= 2 * Math.PI;
            return Math.Abs(d);
        }

        internal static V2 Dir(double a) => new V2(Math.Cos(a), Math.Sin(a));
        internal static V2 Rot(V2 v, double a) => new V2(v.X * Math.Cos(a) - v.Z * Math.Sin(a), v.X * Math.Sin(a) + v.Z * Math.Cos(a));
        internal static double Ang(V2 v) => Math.Atan2(v.Z, v.X);
        private const double Deg = Math.PI / 180;

        /// <summary>The strand's end nearer to p, the arrival direction over its last 0.12 cell, and
        /// the strand reversed so that end is last.</summary>
        internal static List<V2> EndAt(List<V2> pts, V2 p)
        {
            var q = new List<V2>(pts);
            if (V2.Dist(q[0], p) < V2.Dist(q[q.Count - 1], p)) q.Reverse();
            return q;
        }

        internal static V2 PointBack(List<V2> q, double back)
        {
            double acc = 0;
            for (int i = q.Count - 1; i > 0; i--)
            {
                acc += V2.Dist(q[i], q[i - 1]);
                if (acc >= back) return q[i - 1];
            }
            return q[0];
        }

        /// <summary>How much the cord turns over its last stretch: the angle between its direction
        /// arriving at the tip (last 0.1 cell) and its direction 0.45-0.6 cell back. Near 0 for a cord
        /// that runs straight out to its tip; large for one whose end curls over and lies limp.</summary>
        internal static double TipTurn(List<V2> q)
        {
            V2 e = q[q.Count - 1];
            return AngDiff(Ang(e - PointBack(q, 0.1)), Ang(PointBack(q, 0.45) - PointBack(q, 0.6)));
        }

        internal static IEnumerable<CordStrand> StrandsAt(List<LaidPiece> ps, CordNode nd) =>
            ps.Where(p => p.EndA != null && (p.EndA == nd.OracleName + ":" + nd.Cell.X + "," + nd.Cell.Z || p.EndB == nd.OracleName + ":" + nd.Cell.X + "," + nd.Cell.Z))
              .SelectMany(p => p.Strands.Where(s => !s.OverFace));

        public static ArtFitResult ArtFit(CordGraph g, List<LaidPiece> ps, Func<Cell, bool> isLive)
        {
            var R = new ArtFitResult();
            List<CordDecal> decals = ps.SelectMany(p => p.Decals).ToList();
            // (1) T/X junctions: the art's junction point on the node, an arm along every arriving cord,
            //     every cord ending at an arm's tip and arriving along it
            int jn = 0, jbad = 0;
            var jmsg = new List<string>();
            foreach (CordNode nd in g.Nodes.Values.Where(n => n.Type == NodeType.Junction && !n.IsBlob))
            {
                jn++;
                CordDecal? best = null;
                double bd = 9;
                foreach (CordDecal d in decals.Where(x => x.Kind == DecalKind.JunctionTape || x.Kind == DecalKind.JunctionTin))
                {
                    V2 anchor = d.Pos + Rot(new V2(0, d.Kind == DecalKind.JunctionTape ? TapeAnchorZ : 0) * d.Scale, d.Angle);
                    double dd = V2.Dist(anchor, nd.Pos);
                    if (dd < bd) { bd = dd; best = d; }
                }
                if (best == null || bd > 0.03) { jbad++; jmsg.Add($"{nd.Cell} art junction point {bd:0.00} off the node"); continue; }
                double[] arms = (best.Value.Kind == DecalKind.JunctionTape ? TapeArms : TinArms).Select(a => a + best.Value.Angle).ToArray();
                foreach (CordStrand s in StrandsAt(ps, nd))
                {
                    List<V2> q = EndAt(s.Pts, nd.Pos);
                    V2 e = q[q.Count - 1];
                    double r = V2.Dist(e, nd.Pos);
                    double armErr = arms.Min(a => AngDiff(a, Ang(e - nd.Pos)));
                    V2 arm = Dir(arms.OrderBy(a => AngDiff(a, Ang(e - nd.Pos))).First());
                    double arrive = AngDiff(Ang(e - PointBack(q, 0.12)), Ang(-arm));
                    if (r < 0.3 || r > 0.5 || armErr > 8 * Deg || arrive > 20 * Deg)
                    {
                        jbad++;
                        jmsg.Add($"{nd.Cell} cord end r={r:0.00} armErr={armErr / Deg:0}deg arrive={arrive / Deg:0}deg");
                    }
                }
            }
            R.Junctions = jn; R.JunctionFaults = jbad; R.Messages.AddRange(jmsg);
            // (4) plugs: the head points into the machine and lands inside its footprint
            int pbad = 0, pn = 0;
            var pmsg = new List<string>();
            foreach (CordNode nd in g.Nodes.Values.Where(n => n.IsMachine && n.Machine != null))
            {
                MachineInfo m = nd.Machine;
                foreach (CordStrand s in StrandsAt(ps, nd))
                {
                    pn++;
                    // the end nearer the machine's FOOTPRINT (a cord run on under the art, B10, ends inside it)
                    double RectD(V2 v) => Math.Max(Math.Max(m.X0 - v.X, v.X - (m.X0 + m.W)), Math.Max(m.Z0 - v.Z, v.Z - (m.Z0 + m.H)));
                    List<V2> q = new List<V2>(s.Pts);
                    if (RectD(q[0]) < RectD(q[q.Count - 1])) q.Reverse();
                    V2 e = q[q.Count - 1];
                    CordDecal? plug = decals.Where(d => d.Kind == DecalKind.Plug).OrderBy(d => V2.Dist(d.Pos, e)).Cast<CordDecal?>().FirstOrDefault();
                    if (plug == null || V2.Dist(plug.Value.Pos, e) > 0.3) { pbad++; pmsg.Add($"{nd.Cell} no plug at the cord end"); continue; }
                    V2 head = plug.Value.Pos + Dir(plug.Value.Angle) * (PlugFace * plug.Value.Scale);
                    bool inside = head.X > m.X0 && head.X < m.X0 + m.W && head.Z > m.Z0 && head.Z < m.Z0 + m.H;
                    double axis = Math.Min(AngDiff(plug.Value.Angle % (Math.PI / 2), 0), AngDiff(plug.Value.Angle % (Math.PI / 2), Math.PI / 2));
                    double arrive = AngDiff(Ang(e - PointBack(q, 0.12)), plug.Value.Angle);
                    if (!inside || axis > 3 * Deg || arrive > 25 * Deg)
                    {
                        pbad++;
                        pmsg.Add($"{nd.Cell} plug head {head} inside={inside} axisErr={axis / Deg:0} arrive={arrive / Deg:0}");
                    }
                }
            }
            R.PlugEnds = pn; R.PlugFaults = pbad; R.Messages.AddRange(pmsg);
            // (3) wall/rock stubs (round 4, WallMount): the plate/hole lies along the cord, starts at the face line and is
            //     mounted ON the wall (OnFace): nothing on the open floor, nothing deeper than its face allows
            int sbad = 0, sn = 0;
            foreach (CordNode nd in g.Nodes.Values.Where(n => n.Type == NodeType.StubWall || n.Type == NodeType.StubRock))
            {
                sn++;
                DecalKind k = nd.Type == NodeType.StubWall ? DecalKind.StubWall : DecalKind.StubRock;
                CordDecal? d = decals.Where(x => x.Kind == k).OrderBy(x => V2.Dist(x.Pos, nd.Face)).Cast<CordDecal?>().FirstOrDefault();
                if (d == null) { sbad++; continue; }
                WallMount.DepthSpan(d.Value, nd.Face, nd.Into, out double near, out double far);
                double lateral = Math.Abs((d.Value.Pos.X - nd.Face.X) * nd.Into.Z - (d.Value.Pos.Z - nd.Face.Z) * nd.Into.X);
                if (AngDiff(d.Value.Angle, Ang(nd.Into)) > 3 * Deg || near > 0.05 || lateral > 0.1)
                {
                    sbad++;
                    R.Messages.Add($"stub {nd.Cell} angle {d.Value.Angle / Deg:0} want {Ang(nd.Into) / Deg:0}, starts {near:0.00} past the face, {lateral:0.00} off its line");
                }
                if (!WallMount.OnFace(d.Value, nd.Face, nd.Into))
                {
                    if (k == DecalKind.StubWall) R.FlatWallPlates++; else R.FlatRockHoles++;
                    R.Messages.Add($"stub {nd.Cell} {k} not ON its {WallMount.FaceOf(nd.Into)} face: depth {near:0.00}..{far:0.00}, allowed 0..{WallMount.MaxDepth(WallMount.FaceOf(nd.Into)):0.00}");
                }
            }
            R.Stubs = sn; R.StubFaults = sbad;
            // (5) dead ends lie visibly limp: the tip has fallen sideways off the conduit's line and the
            //     end curls over; live ends stick straight out of the conduit end along its direction
            var dead = new List<double>();
            var liv = new List<double>();
            int dbad = 0, lbad = 0;
            foreach (CordNode nd in g.Nodes.Values.Where(n => n.Type == NodeType.Terminal))
            {
                V2 o = new V2(nd.Out.X, nd.Out.Z).Norm();
                foreach (CordStrand s in StrandsAt(ps, nd))
                {
                    List<V2> q = EndAt(s.Pts, nd.Pos);
                    if (Geo.Length(q) < 1.0) continue;
                    V2 e = q[q.Count - 1];
                    double side = Math.Abs((e - nd.Pos).X * o.Z - (e - nd.Pos).Z * o.X);
                    double turn = TipTurn(q) / Deg;
                    if (isLive(nd.Cell))
                    {
                        double arrive = AngDiff(Ang(e - PointBack(q, 0.1)), Ang(o)) / Deg;
                        liv.Add(arrive);
                        if (V2.Dist(e, nd.Pos) > 0.08 || arrive > 15 || turn > 15)
                        {
                            lbad++;
                            R.Messages.Add($"live end {nd.Cell} off {V2.Dist(e, nd.Pos):0.00} arrive {arrive:0} turn {turn:0}");
                        }
                    }
                    else
                    {
                        dead.Add(side);
                        if (side < 0.22 || turn < 50) dbad++;
                    }
                }
            }
            // (6) piles: every cable end sits on a connector port; every connector has >= 2 cables plugged in
            foreach (LaidPiece p in ps.Where(x => x.Key != null && x.Key.StartsWith("tangle:")))
            {
                R.Piles++;
                List<CordDecal> cons = p.Decals.Where(d => d.Kind == DecalKind.JunctionTin || d.Kind == DecalKind.JunctionTape ||
                                                         d.Kind == DecalKind.PowerStrip || d.Kind == DecalKind.PowerStripDark).ToList();
                R.PileConnectors += cons.Count;
                R.PileJunctions += cons.Count(d => d.Kind == DecalKind.JunctionTin || d.Kind == DecalKind.JunctionTape);
                List<CordBuilder.PilePort> ports = CordBuilder.PortsOf(cons);
                var perCon = new int[cons.Count];
                foreach (CordStrand s in p.Strands)
                    foreach (V2 e in new[] { s.Pts[0], s.Pts[s.Pts.Count - 1] })
                    {
                        int best = -1; double bd = 0.06;
                        for (int i = 0; i < ports.Count; i++) { double dd = V2.Dist(ports[i].Tip, e); if (dd < bd) { bd = dd; best = i; } }
                        if (best < 0) R.PileLooseEnds++; else perCon[ports[best].Connector]++;
                    }
                int idle = perCon.Count(c => c < 2);
                R.PileIdleConnectors += idle;
                if (idle > 0) R.Messages.Add($"{p.Key}: {idle} of {cons.Count} connectors with < 2 cables plugged in");
            }
            R.Strips = ps.Sum(p => p.Decals.Count(d => d.Kind == DecalKind.PowerStrip || d.Kind == DecalKind.PowerStripDark));
            R.DeadEnds = dead.Count; R.DeadFaults = dbad; R.DeadOffLine = dead;
            R.LiveEnds = liv.Count; R.LiveFaults = lbad; R.LiveArrivalDeg = liv;
            return R;
        }
    }
}
