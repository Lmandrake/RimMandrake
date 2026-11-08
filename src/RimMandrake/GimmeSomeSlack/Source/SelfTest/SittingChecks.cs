// The owner's live sitting of 2026-11-08 (12:20 PM): "The modern cable is a bit of a mess. Interestingly, the industrial and scrapper look
// much better and bend appropriately. ... Items should connect to the bottom of a power pole (beneath its base), not run a line up to the
// top of the power pole. ... The massive tangle shown for the grid is indeed a bit excessive. I did want a tangled rats-nest of wires, but
// that's overkill. The top of power poles shows needless kinks in the wires where they connect too."
// Each row was written failing on the code he saw, on the colony worlds the live probe dumped that sitting (sitting_ba_*.json).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class SittingChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "sitting-20261108: " + msg);

        private static readonly DecalKind[] Connectors = { DecalKind.JunctionTin, DecalKind.JunctionTape, DecalKind.PowerStrip, DecalKind.PowerStripDark };

        internal static void Run()
        {
            Lay("Modern", out CordWorld wm, out List<LaidPiece> modern);
            Lay("Scrapper", out CordWorld ws, out List<LaidPiece> scrapper);
            if (modern == null || scrapper == null) { Check(false, "the sitting's worlds (sitting_ba_Modern/Scrapper.json) beside the self-test"); return; }

            // WHY Modern was worse: every socket of a strip faced one side, so a cord from behind or off the free end swung round the strip and
            // hooked into its plug ("<" hooks, plugs facing away from their cords: 13 of 39 socket ends turned past 100 degrees in the last 1.2 cells)
            List<double> turns = SocketTurns(modern);
            Check(turns.Count >= 20, $"the Modern colony plugs at least 20 strip sockets (instrument sees them: {turns.Count})");
            // the strict rows (owner 2026-11-08 round 2: "Do NOT relax any bar to pass"): past 100 degrees in the last 1.2 cells of cord into a plug, the tied
            // strain-relief loop left out (a loop is the owner's own answer, its turn is not a hook), no more than 3 (was 13 of 39)
            int wrapped = turns.Count(t => t > 100);
            Check(wrapped <= 3, $"Modern: a strip socket's cord hooks (past 100 degrees in its last 1.2 cells outside a tied loop) at most 3 times (was 13 of 39): {wrapped} of {turns.Count}");
            var bm = new CordShapeAudit.BendTally();
            foreach (LaidPiece p in modern) foreach (CordStrand s in p.Strands) bm.Add(wm, p, s);
            int sock = bm.ByWhy.TryGetValue("socket", out int k) ? k : 0;
            // the Gamma corners at the plug tail the audit excused as 'socket' (105-139 degrees) are what the owner ruled out: goal 3 (Scrapper 1)
            Check(sock <= 3, $"Modern: bends excused as 'socket' no more than 3 (was 9; Scrapper 1): {sock}");
            // the plug exit (round 2, 3): straight for a stiff length off the plug, a bend there only where a wall or object forces it
            (int stiffBad, int ends) = StiffExits(wm, modern);
            Check(ends >= 20 && stiffBad <= 3, $"Modern: a cord leaves its strip plug straight (first {CordPlugExit.StiffLen} cell within {CordPlugExit.StiffTol} degrees) unless a wall or object stands within {CordPlugExit.StiffNear}: {stiffBad} of {ends} do not");
            // a strain-relief loop is small, closed, and tied where it crosses itself
            (int loops, int badLoops, int tiesDrawn) = Loops(modern);
            Check(badLoops == 0 && tiesDrawn == loops, $"Modern: each strain-relief loop is {CordPlugExit.LoopDiaMin}-{CordPlugExit.LoopDiaMax} cell across and wears its tie band: {loops} loops, {badLoops} off size, {tiesDrawn} ties drawn");
            Console.WriteLine($"  Modern socket ends: {turns.Count}, past 100: {wrapped}, past 150: {turns.Count(t => t > 150)}, socket-excused bends {sock}, loops {loops}");

            // the grid's heap: "a tangled rats-nest of wires, but that's overkill" (Modern 14 cables and 7 strips, the junction looks 22-23 and 13 boxes)
            foreach ((string look, List<LaidPiece> ps) in new[] { ("Modern", modern), ("Scrapper", scrapper) })
            {
                List<LaidPiece> heaps = ps.Where(p => p.EndA == null && (p.Key ?? "").StartsWith("tangle:", StringComparison.Ordinal)).ToList();
                Check(heaps.Count >= 1, $"{look}: the colony has its grid heap (instrument sees it: {heaps.Count})");
                foreach (LaidPiece h in heaps)
                {
                    int strands = h.Strands.Count, cons = h.Decals.Count(d => Connectors.Contains(d.Kind));
                    Console.WriteLine($"  heap {look} {h.Key}: {strands} cables, {cons} connectors");
                    Check(strands <= 10 && cons <= 6 && strands >= 3 && cons >= 1,
                          $"{look} {h.Key}: a rats-nest, not overkill: 3..10 cables and 1..6 connectors, got {strands} cables, {cons} connectors");
                }
            }

            // pole tops: "needless kinks in the wires where they connect" are the drip loops at each insulator
            Check(!AerialMath.DripLoopsDefault, "drip loops at the insulators are off by default (they kinked every wire at a pole top)");
            PoleTops();
            JointNib();

            FootDrop();
            MastFoot();
        }

        /// <summary>The owner's pole photo: a line comes in straight, rests on the insulator and goes out straight; it sags only mid-span.
        /// The plain span curve (drip off) once left every insulator 13 deg off its chord, a 25 deg V on top of a straight pole.</summary>
        private static void PoleTops()
        {
            static double Deg(P2 u, P2 v) => Math.Abs(Math.Atan2(u.X * v.Z - u.Z * v.X, u.X * v.X + u.Z * v.Z)) * 180 / Math.PI;
            static P2 Seg(P2 p, P2 q) => new P2(q.X - p.X, q.Z - p.Z);
            double worstKink = 0, worstOff = 0, sagErr = 0;
            foreach ((double la, double lb, double dirDeg) in new[] { (8.0, 8.0, 0.0), (4.0, 12.0, 0.0), (3.0, 3.0, 0.0), (8.0, 8.0, 45.0), (6.0, 10.0, 20.0) })
            {
                double r = dirDeg * Math.PI / 180;
                var pole = new P2(20, 20);
                var a = new P2(pole.X - la * Math.Cos(r), pole.Z - la * Math.Sin(r));
                var b = new P2(pole.X + lb * Math.Cos(r), pole.Z + lb * Math.Sin(r));
                List<P2> c1 = AerialMath.SpanCurve(a, pole, 0.06), c2 = AerialMath.SpanCurve(pole, b, 0.06);
                worstKink = Math.Max(worstKink, Deg(Seg(c1[c1.Count - 2], c1[c1.Count - 1]), Seg(c2[0], c2[1])));
                worstOff = Math.Max(worstOff, Math.Max(Deg(Seg(pole, b), Seg(c2[0], c2[1])), Deg(Seg(a, pole), Seg(c1[c1.Count - 2], c1[c1.Count - 1]))));
                double mid = 0.06 * lb, low = c2.Max(p => (pole.Z + (b.Z - pole.Z) * AerialMath.ProjectT(pole, b, p)) - p.Z);
                if (dirDeg == 0) sagErr = Math.Max(sagErr, Math.Abs(low - mid));
            }
            Check(worstKink <= 3, $"pole top: two spans through a straight pole meet within 3 deg (was 25 deg): {worstKink:0.0}");
            Check(worstOff <= 1.5, $"pole top: the wire leaves the insulator along its chord, within 1.5 deg (was 13 deg): {worstOff:0.0}");
            Check(sagErr < 0.02, $"pole top: the mid-span sag is unchanged (sag factor x length): off by {sagErr:0.000}");
        }

        /// <summary>Shot 121523's cusp: the lab's Modern cord junction:179,103 -> consumer:179,103 ran on past its plug point and back (a 0.16-cell
        /// nib, turns 86 and 139 deg, the same at one machine in each played colony) before its run on under the art set off and crossed it.</summary>
        private static void JointNib()
        {
            var body = new List<V2> { new V2(179.08, 101.40), new V2(179.08, 101.28), new V2(177.92, 101.27), new V2(177.92, 101.23), new V2(177.92, 101.19), new V2(178.08, 101.18) };
            var ext = new List<V2> { new V2(178.04, 101.22), new V2(178.01, 101.25), new V2(177.97, 101.29), new V2(177.87, 101.39), new V2(177.70, 101.50), new V2(177.50, 101.50) };
            List<V2> o = CordBuilder.CutJointLoop(new List<V2>(body), ext);
            double worst = 0;
            for (int i = 1; i + 1 < o.Count; i++)
            {
                V2 u = o[i] - o[i - 1], v = o[i + 1] - o[i];
                if (u.Len < 1e-9 || v.Len < 1e-9 || V2.Dist(o[i], body[body.Count - 1]) > 0.4) continue;   // the joint, not the lab cord's own corner at 179.08
                worst = Math.Max(worst, Math.Abs(Math.Atan2(u.X * v.Z - u.Z * v.X, u.X * v.X + u.Z * v.Z)) * 180 / Math.PI);
            }
            bool selfCross = false;
            for (int i = 0; i + 1 < o.Count; i++)
                for (int j = i + 2; j + 1 < o.Count; j++)
                    if (CordShape.Cross(o[i], o[i + 1], o[j], o[j + 1], out V2 _)) selfCross = true;
            Check(!selfCross && worst < 80 && V2.Dist(o[o.Count - 1], ext[ext.Count - 1]) < 1e-9,
                  $"121523 nib: the cord into a machine stops where its run on under the art crosses it (no self-crossing {!selfCross}, sharpest turn by the joint {worst:0} deg < 80, ends on the centroid)");
            var clean = new List<V2> { new V2(180, 101.5), new V2(179, 101.5), new V2(178.08, 101.5) };
            Check(CordBuilder.CutJointLoop(new List<V2>(clean), ext).Count == clean.Count + ext.Count, "a cord with no nib keeps every point");
        }

        private static void Lay(string look, out CordWorld w, out List<LaidPiece> ps)
        {
            w = null; ps = null;
            string path = Path.Combine(AppContext.BaseDirectory, "sitting_ba_" + look + ".json");
            if (!File.Exists(path)) return;
            using JsonDocument doc = JsonDocument.Parse(File.ReadAllText(path));
            w = LabWorld.Read(doc.RootElement, out BuildOptions opt, out HashSet<Cell> live);
            ps = new CordBuilder().Build(w, opt, c => live.Contains(c));
        }

        /// <summary>Each strip-socket plug (a Plug decal at the pile plug scale on a laid cord, not a heap's own) with the strand end it takes: the strand,
        /// and whether the plug is at its last point.</summary>
        private static IEnumerable<(CordStrand s, bool atEnd, CordDecal plug)> SocketEnds(List<LaidPiece> ps)
        {
            foreach (LaidPiece p in ps)
            {
                if ((p.EndA ?? p.Key ?? "").StartsWith("tangle", StringComparison.Ordinal)) continue;
                foreach (CordDecal d in p.Decals.Where(d => d.Kind == DecalKind.Plug && Math.Abs(d.Scale - CordBuilder.PilePlugScale) < 1e-3))
                {
                    CordStrand best = null;
                    bool bestEnd = false;
                    double bd = double.MaxValue;
                    foreach (CordStrand s in p.Strands)
                    {
                        if (s.Pts == null || s.Pts.Count < 3) continue;
                        foreach (bool atEnd in new[] { false, true })
                        {
                            double dd = V2.Dist(atEnd ? s.Pts[s.Pts.Count - 1] : s.Pts[0], d.Pos);
                            if (dd < bd) { bd = dd; best = s; bestEnd = atEnd; }
                        }
                    }
                    if (best != null) yield return (best, bestEnd, d);
                }
            }
        }

        /// <summary>Each strip-socket plug: the cord's total turn over the last 1.2 cells into it outside a tied strain-relief loop, in degrees
        /// (gss_sitting/tools/strip_ends.py, the instrument that found the hooks; the loop's own turn is skipped and the window runs on past it).</summary>
        private static List<double> SocketTurns(List<LaidPiece> ps)
        {
            var o = new List<double>();
            foreach ((CordStrand s, bool atEnd, CordDecal _) in SocketEnds(ps))
            {
                double[] cum = Geo.CumLen(s.Pts);
                int n = s.Pts.Count;
                // walk from the plug outward: index of the k-th point from the plug
                int Ix(int k) => atEnd ? n - 1 - k : k;
                double acc = 0, tot = 0, prev = double.NaN;
                for (int k = 0; k + 1 < n && acc < 1.2; k++)
                {
                    V2 a0 = s.Pts[Ix(k)], a1 = s.Pts[Ix(k + 1)];
                    double a = Math.Atan2(a1.Z - a0.Z, a1.X - a0.X);
                    bool inTie = CordShapeAudit.InTie(s.Ties, cum[Ix(k)]);
                    if (!double.IsNaN(prev) && !inTie) { double da = a - prev; while (da > Math.PI) da -= 2 * Math.PI; while (da < -Math.PI) da += 2 * Math.PI; tot += da; }
                    prev = a;
                    if (!inTie) acc += V2.Dist(a0, a1);
                }
                o.Add(Math.Abs(tot) * 180 / Math.PI);
            }
            return o;
        }

        /// <summary>How many strip-socket cords bend more than <see cref="CordPlugExit.StiffTol"/> in their first <see cref="CordPlugExit.StiffLen"/> cell off the plug with no wall
        /// or object (another machine) within <see cref="CordPlugExit.StiffNear"/> of the plug, of how many.</summary>
        private static (int bad, int n) StiffExits(CordWorld w, List<LaidPiece> ps)
        {
            int bad = 0, n = 0;
            var seen = new List<string>();
            foreach ((CordStrand s, bool atEnd, CordDecal plug) in SocketEnds(ps))
            {
                List<V2> q = atEnd ? Enumerable.Reverse(s.Pts).ToList() : s.Pts;
                q = Geo.Resample(q, 0.05);
                if (q.Count < 6) continue;
                n++;
                // the turn at each point up to StiffLen of cord off the plug (the point's own arc, as CordPlugExit judges it)
                double tot = 0, at = 0;
                for (int i = 1; i + 1 < q.Count; i++)
                {
                    V2 u = q[i] - q[i - 1], v = q[i + 1] - q[i];
                    at += u.Len;
                    if (at > CordPlugExit.StiffLen + 1e-6) break;
                    tot += Math.Atan2(u.X * v.Z - u.Z * v.X, u.X * v.X + u.Z * v.Z);
                }
                V2 t = q[0];
                double wall = w.Clearance(t);
                foreach (MachineInfo m in w.Machines) wall = Math.Min(wall, CordShapeAudit.RectDist(m.X0, m.Z0, m.W, m.H, t));
                if (Math.Abs(tot) * 180 / Math.PI > CordPlugExit.StiffTol && wall > CordPlugExit.StiffNear) { bad++; if (seen.Count < 6) seen.Add($"({plug.Pos.X:0.00},{plug.Pos.Z:0.00}) {Math.Abs(tot) * 180 / Math.PI:0}deg"); }
            }
            if (seen.Count > 0) Console.WriteLine("  stiff exits bent: " + string.Join("; ", seen));
            return (bad, n);
        }

        /// <summary>The tied strain-relief loops on the colony's cords: how many, how many are not 0.30-0.42 cell across, how many wear a tie band decal at their crossing.</summary>
        private static (int loops, int bad, int tied) Loops(List<LaidPiece> ps)
        {
            int loops = 0, bad = 0, tied = 0;
            foreach (LaidPiece p in ps)
                foreach (CordStrand s in p.Strands)
                {
                    if (s.Ties == null || s.Pts == null) continue;
                    double[] cum = Geo.CumLen(s.Pts);
                    foreach (CordTie t in s.Ties)
                    {
                        loops++;
                        var lp = new List<V2>();
                        for (int i = 0; i < s.Pts.Count; i++) if (cum[i] >= t.S0 - 1e-6 && cum[i] <= t.S1 + 1e-6) lp.Add(s.Pts[i]);
                        double dia = 0;
                        foreach (V2 a in lp) foreach (V2 b in lp) dia = Math.Max(dia, V2.Dist(a, b));
                        if (dia < CordPlugExit.LoopDiaMin - 0.01 || dia > CordPlugExit.LoopDiaMax + 0.01) bad++;
                        if (p.Decals.Any(d => d.Kind == DecalKind.CableTie && V2.Dist(d.Pos, t.At) < 0.05)) tied++;
                    }
                }
            return (loops, bad, tied);
        }

        /// <summary>A device's lead to a pole or mast starts on the ground at the pole's foot (121837, 121857: it hung from the crossarm).</summary>
        private static void FootDrop()
        {
            var basePt = new P2(20.5, 20.5);
            int n = 0, footed = 0, low = 0, reached = 0;
            foreach (P2 dev in new[] { new P2(24.5, 20.5), new P2(16.5, 22.5), new P2(20.5, 16.5), new P2(23.5, 24.5), new P2(21.2, 20.9) })
                for (int seed = 0; seed < 6; seed++)
                {
                    FallenLay l = AerialMath.LayFootDrop(basePt, dev, 1000 + 37 * seed, (x, z) => true);
                    n++;
                    if (l == null || l.Pts.Count < 2) continue;
                    if (P2.Dist(l.Pts[0], basePt) < 0.05 && l.GroundFrom == 0) footed++;
                    if (l.Pts.All(q => q.Z <= Math.Max(basePt.Z, dev.Z) + 0.6)) low++;
                    if (P2.Dist(l.Pts[l.Pts.Count - 1], dev) < 0.05) reached++;
                }
            Check(footed == n, $"a pole's lead to a device starts at the pole's foot, on the ground: {footed} of {n}");
            Check(low == n, $"a pole's lead never climbs toward the crossarm: {low} of {n}");
            Check(reached == n, $"a pole's lead ends at its device: {reached} of {n}");
            FallenLay walled = AerialMath.LayFootDrop(basePt, new P2(24.5, 20.5), 7, (x, z) => x != 22);
            Check(walled != null && P2.Dist(walled.Pts[0], basePt) < 0.05 && walled.GroundFrom == 0, "with a wall between, the lead still lies from the foot (under the wall)");
        }

        /// <summary>A floor cord to a mast (a Transmitter with Foot) from a run beside it ends under its foot, not at the cell's side (121837:
        /// a Futuristic cord into the mast's side box, mid-height).</summary>
        private static void MastFoot()
        {
            int bad = 0, n = 0;
            var seen = new List<string>();
            foreach (int side in new[] { -1, 1 })
                foreach (PileArt look in new[] { PileArt.Strips, PileArt.Junctions })
                {
                    var w = new CordWorld(30, 24);
                    int mx = 15, mz = 12;
                    w.SetBlocked(new Cell(mx, mz), BlockKind.Device);
                    int hx = mx + side;
                    for (int z = 6; z <= 18; z++) w.SetConduit(new Cell(hx, z));
                    for (int x = Math.Min(hx, hx + 8 * side); x <= Math.Max(hx, hx + 8 * side); x++) w.SetConduit(new Cell(x, 6));
                    var mast = new MachineInfo { Id = "mast", Kind = MachineKind.Transmitter, X0 = mx, Z0 = mz, Foot = true, Hookups = new List<Cell> { new Cell(hx, mz) } };
                    w.Machines.Add(mast);
                    var lamp = new MachineInfo { Id = "lamp", Kind = MachineKind.Consumer, X0 = hx + 8 * side, Z0 = 7, Hookups = new List<Cell> { new Cell(hx + 8 * side, 6) } };
                    w.SetBlocked(new Cell(lamp.X0, lamp.Z0), BlockKind.Device);
                    w.Machines.Add(lamp);
                    List<LaidPiece> ps = new CordBuilder().Build(w, new BuildOptions { Pile = look, Seed = 3, SlideUnder = true }, c => true);
                    V2 c = new V2(mx + 0.5, mz + 0.5);
                    foreach (LaidPiece p in ps)
                        foreach (CordStrand s in p.Strands)
                        {
                            if (s.Pts == null || s.Pts.Count < 2) continue;
                            foreach (V2 e in new[] { s.Pts[0], s.Pts[s.Pts.Count - 1] })
                            {
                                if (V2.Dist(e, c) > 0.9) continue;   // a cord end at the mast (a junction on the run beside it is a cell off)
                                n++;
                                if (!(e.Z <= mz + 0.3 && Math.Abs(e.X - (mx + 0.5)) <= 0.3)) { bad++; if (seen.Count < 4) seen.Add($"{look} {p.EndA}-{p.EndB} ({e.X:0.00},{e.Z:0.00})"); }
                            }
                        }
                }
            Check(n >= 2, $"the mast scenes lay a cord to the mast (instrument sees it: {n})");
            Check(bad == 0, $"a floor cord to a mast ends under its foot (x within 0.3 of its middle, no higher than 0.3 into its cell): {bad} of {n} do not {string.Join("; ", seen)}");
        }
    }
}
