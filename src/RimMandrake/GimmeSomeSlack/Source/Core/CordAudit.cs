// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// Art-fit audit (polish pass 2026-10-02): reads LAID pieces and the graph only and reports whether the
// shipped art fits the cords: junction arms along the arriving cords, plugs into their machines, stubs
// on the face, dead ends limp, live ends straight. Shared by the offline SelfTest and the live probe
// ("artfit"), so the same property is proven offline and in the running game.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    public sealed class ArtFitResult
    {
        public int Junctions, JunctionFaults, PlugEnds, PlugFaults, Stubs, StubFaults, DeadEnds, DeadFaults, LiveEnds, LiveFaults;
        public List<double> DeadOffLine = new List<double>(), LiveArrivalDeg = new List<double>();
        public List<string> Messages = new List<string>();
        /// <summary>Piles (owner review 2026-10-04 B2/B13): connectors in tangles, strips anywhere, cable ends in a pile that
        /// land on no connector port, connectors with fewer than two cables plugged in, rock holes drawn unforeshortened.</summary>
        public int JunctionStrips, Piles, PileConnectors, PileJunctions, Strips, PileLooseEnds, PileIdleConnectors, FlatRockHoles, FlatWallPlates;
        public int Faults => JunctionFaults + PlugFaults + StubFaults + DeadFaults + LiveFaults + PileLooseEnds + PileIdleConnectors + FlatRockHoles + FlatWallPlates;
    }

    public static class CordAudit
    {
        /// <summary>The floor rule's view of a laid strand (walk M2b; shared by the offline SelfTest and the live probe so the
        /// two instruments cannot drift apart again -- the probe counted the round-2/round-4 ends as faults until 2026-10-05).
        /// By design a strand's END runs may lie inside unwalkable cells: (round 2) a cord into a machine runs on under its
        /// art to the footprint centroid (CordBuilder.IntoArt); (round 4) a cord into a wall/rock face ends at its socket on
        /// a plate mounted ON that face, and a loose wire leaves that socket (WallMount: within SouthBand / SideBevel /
        /// NorthSliver of the face it is mounted on). Those end runs are trimmed off; any other vertex inside an unwalkable
        /// cell, anywhere in the strand, still counts.</summary>
        internal static List<V2> TrimUnderArt(CordWorld w, List<V2> pts)
        {
            bool OnFace(V2 p)
            {
                Cell c = p.Floor;
                if (!w.InBounds(c) || w.IsWalkable(c)) return false;
                double fx = p.X - Math.Floor(p.X), fz = p.Z - Math.Floor(p.Z), tol = 0.005;
                bool Open(int dx, int dz) { var n = new Cell(c.X + dx, c.Z + dz); return w.InBounds(n) && w.IsWalkable(n); }
                return Open(0, -1) && fz <= WallMount.SouthBand + tol || Open(0, 1) && 1 - fz <= WallMount.NorthSliver + tol ||
                       Open(-1, 0) && fx <= WallMount.SideBevel + tol || Open(1, 0) && 1 - fx <= WallMount.SideBevel + tol ||
                       Math.Min(Math.Min(fx, 1 - fx), Math.Min(fz, 1 - fz)) <= CordBuilder.PastFaceDepth + tol;
            }
            bool In(V2 p) => OnFace(p) || w.Machines.Any(m => p.X >= m.X0 && p.X < m.X0 + m.W && p.Z >= m.Z0 && p.Z < m.Z0 + m.H);
            int a = 0, b = pts.Count - 1;
            while (a < b && In(pts[a])) a++;
            while (b > a && In(pts[b])) b--;
            return pts.GetRange(a, b - a + 1);
        }

        
        // Art geometry measured from the shipped PNGs (Textures/RimMandrake/GimmeSomeSlack), in canvas units
        // (1 = the decal's full side), independent of the builder (CordBuilder keeps its own copies):
        //   Junction_Tape: a T, arms along art +X, -X and -Z; the arms meet 0.152 above the canvas centre.
        //   Junction_Tin:  a cross, four arms, meeting at the centre.
        //   StubWall / StubRock: placed and judged by WallMount (round 4).
        //   Plug: cord along -X, the head's face at +0.46 X.
        private static readonly double[] TapeArms = { 0, Math.PI, -Math.PI / 2 };
        private static readonly double[] TinArms = { 0, Math.PI / 2, Math.PI, -Math.PI / 2 };
        private const double TapeAnchorZ = 0.152, PlugFace = 0.46;
        /// <summary>The side-view plug's head face, art +X, in decal widths (Plug.png).</summary>
        internal const double PlugFaceU = PlugFace;
        //   PowerStrip (256x128): four sockets on art +Z, centres at these canvas-width X and -0.049 Z; its lead ends under the
        //   +X end cap at (0.39, -0.05). Copies of CordBuilder.StripHeads / StripHeadZ / StripLeadX / StripLeadZ: change in step.
        private static readonly double[] StripHeadX = { -0.328, -0.128, 0.065, 0.264 };
        private const double StripHeadZ = -0.049, StripLeadX = 0.39, StripLeadZ = -0.05, StripNodeReach = 0.15;

        /// <summary>Do the cords at a junction fit its strip? Read off the decal alone, not the builder's pose: each cord end
        /// lands on the lead's nub arriving along the strip, or on a socket with a plug on it arriving along that socket. A
        /// cord stopping short, or plugged nowhere, is a fault; so is a strip with no plugged cord.</summary>
        private static bool StripFits(CordDecal strip, IEnumerable<CordStrand> strands, List<CordDecal> decals, List<string> msg, Cell at)
        {
            V2 along = Dir(strip.Angle), side = along.Perp;
            V2 Art(double x, double z) => strip.Pos + along * (x * strip.Scale) + side * (z * strip.Scale);
            V2 lead = Art(StripLeadX, StripLeadZ);
            bool ok = true;
            int plugged = 0, leads = 0;
            foreach (CordStrand s in strands)
            {
                List<V2> q = EndAt(s.Pts, strip.Pos);
                V2 e = q[q.Count - 1];
                double arriveAng = Ang(e - PointBack(q, 0.1));
                if (V2.Dist(e, lead) < 0.08)
                {
                    leads++;
                    if (AngDiff(arriveAng, Ang(-along)) > 35 * Deg) { ok = false; msg.Add($"{at} lead arrives {AngDiff(arriveAng, Ang(-along)) / Deg:0}deg off the strip"); }
                    continue;
                }
                // round 3 (owner 2026-11-08 5:18 PM): its plug seen from above, seated ON a socket and covering it, the cord in the end of its
                // boot and arriving along the boot; a side-view plug lying against the strip's edge is the side entry he rejected
                int pi = decals.FindIndex(d => d.Kind == DecalKind.PlugTop && V2.Dist(d.Pos + Dir(d.Angle) * CordBuilder.PlugTopReach, e) < 0.03);
                if (pi < 0)
                {
                    ok = false;
                    msg.Add(decals.Any(d => d.Kind == DecalKind.Plug && V2.Dist(d.Pos, e) < 0.2) ? $"{at} side-entry plug at the strip's edge" : $"{at} a cord on a socket wears no plug");
                    continue;
                }
                CordDecal plug = decals[pi];
                double near = StripHeadX.Min(x => V2.Dist(plug.Pos, Art(x, StripHeadZ)));
                if (near > 0.02) { ok = false; msg.Add($"{at} plug {near:0.00} off every socket (socket uncovered)"); continue; }
                plugged++;
                if (AngDiff(arriveAng, plug.Angle + Math.PI) > 35 * Deg) { ok = false; msg.Add($"{at} cord arrives {AngDiff(arriveAng, plug.Angle + Math.PI) / Deg:0}deg off its plug's boot"); }
            }
            if (plugged == 0 || leads > 3) { ok = false; msg.Add($"{at} strip with {plugged} plugged cords, {leads} on its lead"); }
            return ok;
        }

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

        /// <summary>A copy of the strand, reversed if needed so that its end nearer to p is last.</summary>
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

        internal static ArtFitResult ArtFit(CordGraph g, List<LaidPiece> ps, Func<Cell, bool> isLive)
        {
            var R = new ArtFitResult();
            List<CordDecal> decals = ps.SelectMany(p => p.Decals).ToList();
            // (1) T/X junctions: the art's junction point on the node, an arm along every arriving cord,
            //     every cord ending at an arm's tip and arriving along it
            int jn = 0, jbad = 0;
            var jmsg = new List<string>();
            foreach (CordNode nd in g.Nodes.Values.Where(n => n.Type == NodeType.Junction))
            {
                jn++;
                // a Modern junction draws the long strip: every cord ends on a socket under its plug, or in the strip's own lead
                CordDecal? strip = decals.Where(x => x.Kind == DecalKind.PowerStrip || x.Kind == DecalKind.PowerStripDark)
                    .OrderBy(x => V2.Dist(x.Pos, nd.Pos)).Cast<CordDecal?>().FirstOrDefault();
                if (strip != null && V2.Dist(strip.Value.Pos, nd.Pos) < StripNodeReach)
                {
                    R.JunctionStrips++;
                    if (!StripFits(strip.Value, StrandsAt(ps, nd), decals, jmsg, nd.Cell)) jbad++;
                    continue;
                }
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
                    if (r < CordBuilder.ArmTuck * CordBuilder.JunctionScale - 0.12 || r > CordBuilder.ArmTuck * CordBuilder.JunctionScale + 0.1 || armErr > 8 * Deg || arrive > 20 * Deg)   // round 5: arms scale with the box
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
                    if (m.Kind == MachineKind.Lamp)
                    {
                        // The lamp hides its connector. Its cord must still reach the base;
                        // omitting a plug must not exempt a detached lamp lead.
                        V2 basePoint = m.Foot
                            ? new V2(m.X0 + m.W / 2.0, m.Z0 + CordBuilder.FootTuck)
                            : m.HasHome ? new V2(m.HomeX + 0.5, m.HomeZ + 0.5)
                            : new V2(m.X0 + m.W / 2.0, m.Z0 + m.H / 2.0);
                        if (V2.Dist(e, basePoint) > 0.03)
                        {
                            pbad++;
                            pmsg.Add($"{nd.Cell} lamp cord ends {V2.Dist(e, basePoint):0.000} from its base");
                        }
                        continue;
                    }
                    CordDecal? plug = decals.Where(d => d.Kind == DecalKind.Plug).OrderBy(d => V2.Dist(d.Pos, e)).Cast<CordDecal?>().FirstOrDefault();
                    if (plug == null || V2.Dist(plug.Value.Pos, e) > 0.3) { pbad++; pmsg.Add($"{nd.Cell} no plug at the cord end"); continue; }
                    V2 head = plug.Value.Pos + Dir(plug.Value.Angle) * (PlugFace * plug.Value.Scale);
                    bool inside = head.X > m.X0 && head.X < m.X0 + m.W && head.Z > m.Z0 && head.Z < m.Z0 + m.H;
                    // a wall-mounted device's cord runs on into the wall it hangs on (CordBuilder.IntoArt): the plug ends there
                    if (m.HasHome && head.X > m.HomeX && head.X < m.HomeX + 1 && head.Z > m.HomeZ && head.Z < m.HomeZ + 1) inside = true;
                    double ax = plug.Value.Angle % (Math.PI / 2);   // C# % keeps the sign: fold negatives into [0, pi/2)
                    if (ax < 0) ax += Math.PI / 2;
                    double axis = Math.Min(ax, Math.PI / 2 - ax);
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
                // round 3: a Modern wall entry is an outlet with a seated plug (WallMount.OutletDecal), judged as the plate it replaces
                CordDecal? d = decals.Where(x => x.Kind == k || (k == DecalKind.StubWall && x.Kind == DecalKind.WallOutlet)).OrderBy(x => V2.Dist(x.Pos, nd.Face)).Cast<CordDecal?>().FirstOrDefault();
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
            foreach (CordNode nd in g.Nodes.Values.Where(n => n.Type == NodeType.Terminal && !n.Seam))   // A3: a ring seam is no end
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

        /// <summary>An end within this of another strand's centreline lies ON it (drawn strand 0.08 wide: half 0.04 + a margin).</summary>
        public const double EndOnBodyReach = 0.06;
        /// <summary>An end with a connector decal (plug, junction, strip, wall/rock plate) this close is at a node.</summary>
        public const double EndNodeReach = 0.2;
        /// <summary>The arc of a strand within this of its own end is that strand's END, not its body.</summary>
        public const double BodyEndSkip = 0.2;

        /// <summary>
        /// MESSYCONDUIT_CABLE_PILE_LOOK_1 rule 2 (owner 2026-10-04: "make sure the cables don't look like separate cable
        /// lengths laying on each other, but one big flowing cable except where they go into nodes or power
        /// strips/joiners"). A strand END lying on a strand's BODY with no connector there reads as a loose length dropped
        /// on a cable. An end is exempt when a connector decal sits within <see cref="EndNodeReach"/>, when it dives under a
        /// barrier, when it is a wall-hanging tail, or when another strand's end meets it (the run continues). A frayed end
        /// is NOT a connector: a cut wire lying across another cable is exactly the look ruled out. Returns one line per
        /// fault; empty = clean.
        /// </summary>
        public static List<string> EndsOnBodies(List<LaidPiece> ps)
        {
            var faults = new List<string>();
            List<CordDecal> cons = ps.SelectMany(p => p.Decals).Where(d => d.Kind != DecalKind.FrayDead && d.Kind != DecalKind.FrayLive && d.Kind != DecalKind.CableTie).ToList();   // a tie band on a strain-relief loop joins nothing
            // a connector's centre and every port on it (junction arm tips, strip sockets): a cable plugged into an arm ends
            // a box-half away from the box's centre
            var nodes = cons.Select(d => d.Pos).Concat(CordBuilder.PortsOf(cons).Select(q => q.Tip)).ToList();
            var all = new List<(string key, CordStrand s, double[] cum)>();
            foreach (LaidPiece p in ps)
                foreach (CordStrand s in p.Strands)
                    if (s.Pts != null && s.Pts.Count >= 2) all.Add((p.Key, s, Geo.CumLen(s.Pts)));
            var ends = new List<V2>();
            foreach (var t in all) { ends.Add(t.s.Pts[0]); ends.Add(t.s.Pts[t.s.Pts.Count - 1]); }
            for (int i = 0; i < all.Count; i++)
            {
                var (key, s, _) = all[i];
                if (s.OverFace) continue;
                for (int side = 0; side < 2; side++)
                {
                    if (side == 0 ? s.DiveA : s.DiveB) continue;
                    V2 e = side == 0 ? s.Pts[0] : s.Pts[s.Pts.Count - 1];
                    if (nodes.Any(n => V2.Dist(n, e) < EndNodeReach)) continue;
                    // another strand's end meets this one: one cable continuing across a piece boundary
                    bool met = false;
                    for (int k = 0; k < ends.Count && !met; k++)
                        if (k != 2 * i + side && V2.Dist(ends[k], e) < EndOnBodyReach) met = true;
                    if (met) continue;
                    for (int j = 0; j < all.Count; j++)
                    {
                        var (okey, o, cum) = all[j];
                        double L = cum[cum.Length - 1];
                        // its own body counts too, past its own end run
                        double lo = BodyEndSkip, hi = L - BodyEndSkip;
                        if (j == i) { if (side == 0) lo = Math.Max(lo, 0.6); else hi = Math.Min(hi, L - 0.6); }
                        double d = BodyDist(o.Pts, cum, e, lo, hi);
                        if (d < EndOnBodyReach)
                        {
                            var nearL = ps.SelectMany(pp => pp.Decals).OrderBy(dd => V2.Dist(dd.Pos, e)).Take(1).ToList();
                            string nk = nearL.Count == 0 ? "none" : nearL[0].Kind + "@" + V2.Dist(nearL[0].Pos, e).ToString("0.00");
                            faults.Add($"{key}: strand end ({e.X:0.00},{e.Z:0.00}) lies on {(j == i ? "its own" : okey + "'s")} body ({d:0.000} from its centreline; nearest decal {nk})");
                            break;
                        }
                    }
                }
            }
            return faults;
        }

        /// <summary>Distance from <paramref name="e"/> to the part of polyline P whose arc length is within [lo, hi].</summary>
        private static double BodyDist(List<V2> P, double[] cum, V2 e, double lo, double hi)
        {
            double best = double.MaxValue;
            if (hi <= lo) return best;
            for (int k = 0; k + 1 < P.Count; k++)
            {
                if (cum[k + 1] < lo || cum[k] > hi) continue;
                V2 a = P[k], b = P[k + 1], ab = b - a;
                double len2 = ab.X * ab.X + ab.Z * ab.Z;
                double t = len2 < 1e-12 ? 0 : ((e.X - a.X) * ab.X + (e.Z - a.Z) * ab.Z) / len2;
                // the nearest point on the part of this segment inside [lo, hi], not a skip when the projection
                // falls outside it (Codex review 2026-11-09)
                double seg = cum[k + 1] - cum[k];
                double t0 = seg < 1e-12 ? 0 : Math.Max(0, (lo - cum[k]) / seg), t1 = seg < 1e-12 ? 1 : Math.Min(1, (hi - cum[k]) / seg);
                t = Math.Max(t0, Math.Min(t1, t));
                best = Math.Min(best, V2.Dist(a + ab * t, e));
            }
            return best;
        }
    }
}
