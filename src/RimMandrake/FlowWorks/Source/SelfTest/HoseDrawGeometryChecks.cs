// HOSE_BEND_FIX_SHAVES_WALL_CORNERS + HOSE_LEADIN_FIX_STUB_IN_THE_CANAL (BENCH live round 2, 2026-10-23). The DRAWN hose, measured
// with rulers written out in this file, never with the functions under test:
//  D1 a laid hose's drawn BODY (centreline +- half its visible width) stays out of every wall cell: live, save d map C, wall x=110
//     z206-210, reel 104,207 facing east, laid to 115,208 -- the pose wrapped the wall's SW corner with its centreline 0.06 inside
//     the wall (HoseMath.Clear's graze tolerance), so the hose visibly shaved the corner. Ruler: distance from each drawn sample to
//     the nearest wall cell box.
//  D2 a hose coupled to a machine port from the SIDE (the port's straight lead-out cell is water): live, Kludged pumping station
//     150,190 south port 150,189, canal at 150,188, hose arriving from the east. The end fitting was drawn port-normal with its full
//     straight lead-in (coupling + 0.6-cell wrap), so it stuck out past the hose's join towards the canal. Ruler: the drawn fitting's
//     footprint along the port axis against the drawn hose's own extent there.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseDrawGeometryChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>Independent ruler: distance from q to the nearest Wall cell box within two cells (0 inside one, 3 when none).</summary>
        internal static double WallGap(CordWorld w, V2 q)
        {
            Cell c = q.Floor;
            double best = 3;
            for (int dz = -2; dz <= 2; dz++)
                for (int dx = -2; dx <= 2; dx++)
                {
                    var n = new Cell(c.X + dx, c.Z + dz);
                    if (w.BlockAt(n) != BlockKind.Wall) continue;
                    double ex = Math.Max(Math.Max(n.X - q.X, 0), q.X - (n.X + 1));
                    double ez = Math.Max(Math.Max(n.Z - q.Z, 0), q.Z - (n.Z + 1));
                    best = Math.Min(best, Math.Sqrt(ex * ex + ez * ez));
                }
            return best;
        }

        /// <summary>Deepest overlap (cells) of a drawn body of half-width <paramref name="half"/> into a wall, sampled every 0.02 cell
        /// (first and last 0.5 cell skipped: the ends sit on their reel / port); <paramref name="at"/> = where.</summary>
        internal static double BodyOverlap(CordWorld w, IList<V2> pts, double half, out V2 at) => BodyOverlap(w, pts, half, 0.5, out at);

        /// <summary>As above, the first <paramref name="startSkip"/> cells skipped (a nozzled reel's owner-ruled straight run).</summary>
        internal static double BodyOverlap(CordWorld w, IList<V2> pts, double half, double startSkip, out V2 at)
        {
            at = default;
            double worst = 0;
            double[] s = Geo.CumLen(pts);
            double L = s[s.Length - 1];
            for (int i = 1; i < pts.Count; i++)
            {
                double d = s[i] - s[i - 1];
                int k = Math.Max(1, (int)Math.Ceiling(d / 0.02));
                for (int j = 0; j < k; j++)
                {
                    double a = s[i - 1] + d * j / k;
                    if (a < startSkip || L - a < 0.5) continue;
                    V2 q = pts[i - 1] + (pts[i] - pts[i - 1]) * (j / (double)k);
                    double o = half - WallGap(w, q);
                    if (o > worst) { worst = o; at = q; }
                }
            }
            return worst;
        }

        private static HoseReelRect FacingEast(int x0, int z0)
        {
            for (int rot = 0; rot < 4; rot++)
            {
                var r = new HoseReelRect(x0, z0, 2, 2) { Rot = rot };
                if (r.Outward.HasValue && r.Outward.Value.X > 0.9) return r;
            }
            throw new Exception("no reel facing east");
        }

        /// <summary>The live scene of HOSE_BEND_FIX_SHAVES_WALL_CORNERS, laid as RM_MapComponent_Hoses.LayFrom does.</summary>
        internal static HoseLay WallScene(ulong seed, out CordWorld w)
        {
            w = new CordWorld(130, 230);
            for (int z = 206; z <= 210; z++) w.SetBlocked(new Cell(110, z), BlockKind.Wall);
            for (int x = 116; x <= 117; x++) for (int z = 208; z <= 209; z++) w.SetBlocked(new Cell(x, z), BlockKind.Device);   // the tank
            HoseReelRect reel = FacingEast(104, 207);
            for (int x = reel.X0; x < reel.X0 + reel.W; x++) for (int z = reel.Z0; z < reel.Z0 + reel.H; z++) w.SetBlocked(new Cell(x, z), BlockKind.Device);
            var p = new HoseShapeParams { MaxLength = 40 };
            return HoseMath.LayAlong(w, reel.Mouth, new List<Cell>(), new Cell(115, 208).Centre, p, seed, null, reel.Outward);
        }

        /// <summary>A sweep of wall-end scenes: a one-thick wall (vertical or horizontal) of random length, a 2x2 reel of random
        /// facing on one side near its end, the free end beyond it, so the hose bends round the wall's end.</summary>
        internal static IEnumerable<(string name, CordWorld w, HoseLay lay)> WallEndSweep(int n, bool nozzle)
        {
            var r = new Random(20261023);
            for (int k = 0; k < n; k++)
            {
                var w = new CordWorld(40, 40);
                bool vertical = k % 2 == 0;
                int line = r.Next(17, 23), t0 = r.Next(14, 20), t1 = t0 + r.Next(1, 8);
                for (int t = t0; t <= t1; t++) w.SetBlocked(vertical ? new Cell(line, t) : new Cell(t, line), BlockKind.Wall);
                int a = t0 + r.Next(-1, 3);
                var reel = vertical ? new HoseReelRect(line - r.Next(3, 7), a, 2, 2) : new HoseReelRect(a, line - r.Next(3, 7), 2, 2);
                reel.Rot = r.Next(4);
                int b = t0 + r.Next(-1, 3);
                var far = vertical ? new Cell(line + r.Next(2, 8), b) : new Cell(b, line + r.Next(2, 8));
                for (int x = reel.X0; x < reel.X0 + reel.W; x++) for (int z = reel.Z0; z < reel.Z0 + reel.H; z++) w.SetBlocked(new Cell(x, z), BlockKind.Device);
                var p = new HoseShapeParams { MaxLength = 40 };
                HoseLay lay = nozzle ? HoseMath.LayAlong(w, reel.Mouth, new List<Cell>(), far.Centre, p, (ulong)(k + 1), null, reel.Outward)
                                     : HoseMath.Lay(w, reel.Mouth, far.Centre, p, (ulong)(k + 1));
                yield return ("sweep " + k + (nozzle ? " nozzle" : " plain") + (vertical ? " x=" : " z=") + line + " " + t0 + ".." + t1, w, lay);
            }
        }

        /// <summary>Worst drawn-body overlap of a lay's flat and plump poses (flat half-width = flat hose, plump = full plump), the
        /// nozzle's straight run skipped when it has one.</summary>
        internal static double LayOverlap(CordWorld w, HoseLay lay, out V2 at)
        {
            double skip = lay.Outlet ? HoseMath.LeadOutStraight(new HoseShapeParams()) : 0.5;
            double of = BodyOverlap(w, lay.Flat, HoseMath.VisibleWidth(0, 1) / 2, skip, out V2 af), op = BodyOverlap(w, lay.Plump, HoseMath.VisibleWidth(1, 1) / 2, skip, out V2 ap);
            at = of >= op ? af : ap;
            return Math.Max(of, op);
        }

        /// <summary>Over a set of lays: how many laid, how many draw a body more than <see cref="Shave"/> into a wall, the worst.</summary>
        internal static (int laid, int bad, string worst) Count(IEnumerable<(string name, CordWorld w, HoseLay lay)> lays)
        {
            int laid = 0, bad = 0;
            double worst = 0;
            string worstAt = "none";
            foreach (var (name, w, lay) in lays)
            {
                if (!lay.Ok) continue;
                laid++;
                double o = LayOverlap(w, lay, out V2 at);
                if (o > Shave) bad++;
                if (o > worst) { worst = o; worstAt = name + " " + o.ToString("0.000") + " at " + at; }
            }
            return (laid, bad, worstAt);
        }

        private static double Along(V2 p, V2 o, V2 axis) => (p.X - o.X) * axis.X + (p.Z - o.Z) * axis.Z;

        /// <summary>Independent ruler for D2, re-derived from the draw constants (DrawEnds' Fitting: the coupling square of side
        /// size centred JoinerFace x size behind its face, the brass 0.03 x size behind that centre, the wrap ending 0.05 past the
        /// brass and running wrapLen back): how far the fitting reaches back along the axis beyond the drawn hose's own far edge
        /// over its last cell (0 = it does not).</summary>
        private static double Stub(IList<V2> pts, V2 face0, V2 axis, double vis, double size, V2 face, double wrapLen)
        {
            double[] s = Geo.CumLen(pts);
            double L = s[s.Length - 1], hoseBack = double.MaxValue;
            for (int i = 0; i < pts.Count; i++) if (L - s[i] <= 1.0) hoseBack = Math.Min(hoseBack, Along(pts[i], face0, axis) - vis / 2);
            double c = Along(face, face0, axis) - HoseMath.JoinerFace * size;
            double back = c - 0.5 * size;
            if (wrapLen > 1e-3) back = Math.Min(back, c - 0.03 * size + 0.05 - wrapLen);
            return Math.Max(0, hoseBack - back);
        }

        /// <summary>A drawn body this far over a wall is a visible shave (a hair under 2 px at 105 px a cell is not).</summary>
        public const double Shave = 0.02;

        internal static IEnumerable<(string, CordWorld, HoseLay)> LiveWallSeeds()
        {
            for (ulong seed = 1; seed <= 40; seed++) { HoseLay lay = WallScene(seed, out CordWorld w); yield return ("live wall seed " + seed, w, lay); }
        }

        /// <summary>Dev: `--hose-draw probe` prints D1's counts with the body rule off and on.</summary>
        public static void Probe()
        {
            foreach (bool on in new[] { false, true })
            {
                HoseMath.BodyRuleOn = on;
                try
                {
                    Console.WriteLine($"body rule {(on ? "ON" : "OFF")}: live {Count(LiveWallSeeds())} nozzle sweep {Count(WallEndSweep(200, true))} plain sweep {Count(WallEndSweep(200, false))}");
                }
                finally { HoseMath.BodyRuleOn = true; }
            }
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("HoseDraw_D1_a_bend_round_a_wall_end_never_shaves_its_corner", () =>
            {
                // can-fail: with the body rule off the lays are the pre-fix lays, and the ruler sees the live shave (measured
                // 2026-10-23: 25 of 40 seeds of the live scene, 53 of 172 nozzled sweep lays)
                (int laid, int bad, string worst) liveOff, sweepOff;
                HoseMath.BodyRuleOn = false;
                try { liveOff = Count(LiveWallSeeds()); sweepOff = Count(WallEndSweep(200, true)); }
                finally { HoseMath.BodyRuleOn = true; }
                Assert(liveOff.bad >= 10, "can-fail: with the body rule off only " + liveOff.bad + " of " + liveOff.laid + " live-scene lays shave the wall; the ruler is blind");
                var live = Count(LiveWallSeeds());
                Assert(live.laid == 40, "the live scene (wall x=110 z206-210, reel 104,207 east, end 115,208) laid only " + live.laid + " of 40 seeds");
                Assert(live.bad == 0, live.bad + " of 40 live-scene lays draw the hose over the wall's corner, worst " + live.worst);
                // the sweep: the residue (measured 6 of 172) is a nozzle pointed within ~2 cells of a wall end, where no join of
                // the hose's minimum radius clears it; each is the farthest-off join there is
                var sweep = Count(WallEndSweep(200, true));
                Assert(sweep.laid >= 150 && sweep.laid >= sweepOff.laid - 2, "the body rule cost lays: " + sweep.laid + " laid (off: " + sweepOff.laid + ")");
                Assert(sweepOff.bad >= 30, "can-fail: the off sweep shaves only " + sweepOff.bad + " walls");
                Assert(sweep.bad <= 6, sweep.bad + " of " + sweep.laid + " nozzled sweep lays shave a wall corner (off: " + sweepOff.bad + "), worst " + sweep.worst);
                var plain = Count(WallEndSweep(200, false));
                Assert(plain.laid >= 150 && plain.bad == 0, plain.bad + " of " + plain.laid + " plain (no nozzle) sweep lays shave a wall corner, worst " + plain.worst);
            });

            Case("HoseDraw_D2_a_port_met_from_the_side_draws_no_lead_in_stub", () =>
            {
                // the live hose (census: fellBack true, so it is drawn on its string-pulled plan, bbox top z 189.51) came up x=152 and
                // turned west along z=189.5 into the Kludged station's south port cell 150,189: a side arrival
                var live = Geo.Resample(new List<V2> { new V2(152.5, 186.5), new V2(152.5, 189.5), new V2(150.5, 189.5) }, HoseMath.Sample);
                Assert(HoseMath.SideArrival(live, new V2(0, 1)), "can-fail: the live hose's last stretch was not read as a side arrival");
                int cases = 0, legacyStubs = 0;
                var fails = new List<string>();
                foreach (double widen in new[] { 1.0, 1.5 })
                    foreach (double e in new[] { 0.0, 1.0 })
                        for (int rot = 0; rot < 4; rot++)
                            foreach (int from in new[] { 1, -1 })
                                foreach (bool straight in new[] { false, true })
                                {
                                    // axis = into the port; the hose runs along +-perp (side) or along axis (straight) into the end cell's centre
                                    var axis = new[] { new V2(0, 1), new V2(1, 0), new V2(0, -1), new V2(-1, 0) }[rot];
                                    var perp = new V2(-axis.Z, axis.X) * from;
                                    V2 end = new V2(150.5, 189.5);
                                    V2 dir = straight ? axis : perp;                     // heading of the hose's last stretch
                                    var pts = new List<V2>();
                                    for (int i = 24; i >= 0; i--) pts.Add(end - dir * (0.25 * i));
                                    double vis = HoseMath.VisibleWidth(e, 1);
                                    double size = HoseMath.FittingSize(vis, HoseMath.PieceBand, HoseMath.CouplingMax) * widen;
                                    V2 face0 = end + axis * 0.5;
                                    double size1 = size;
                                    bool side = HoseMath.PortFitting(pts, face0, axis, ref size1, vis, out V2 face, out double wrapLen);
                                    cases++;
                                    string tag = "widen " + widen + " e " + e + " axis " + axis + " from " + from + (straight ? " straight" : " side");
                                    if (side == straight) { fails.Add(tag + ": side arrival read " + side); continue; }
                                    if (straight)
                                    {
                                        if (V2.Dist(face, face0) > 1e-9 || Math.Abs(wrapLen - HoseMath.WrapLength) > 1e-9 || size1 != size) fails.Add(tag + ": a straight arrival's fitting changed");
                                        continue;
                                    }
                                    double stub = Stub(pts, face0, axis, vis, size1, face, wrapLen), legacy = Stub(pts, face0, axis, vis, size, face0, HoseMath.WrapLength);
                                    if (legacy > 0.1) legacyStubs++;
                                    if (stub > 0.01) fails.Add(tag + ": the fitting reaches " + stub.ToString("0.000") + " past the hose towards the blocked cell (legacy " + legacy.ToString("0.000") + ")");
                                    // the coupling still meets the port: its face at most a small slide into the building, never short of it
                                    double slide = (face.X - face0.X) * axis.X + (face.Z - face0.Z) * axis.Z;
                                    if (slide < -1e-9 || slide > 0.1 || Math.Abs((face.X - face0.X) * axis.Z - (face.Z - face0.Z) * axis.X) > 1e-9) fails.Add(tag + ": coupling face moved " + slide.ToString("0.000") + " along the axis");
                                    // and the join is still covered: the wrap (or, cut to nothing, the coupling) reaches the hose's centreline
                                    double front = Along(face - axis * ((HoseMath.JoinerFace + 0.03) * size1) + axis * 0.05, face0, axis);
                                    double cover = wrapLen > 1e-3 ? front - wrapLen : Along(face, face0, axis) - (HoseMath.JoinerFace + 0.5) * size1;
                                    if (size1 < 0.7 * size) fails.Add(tag + ": the coupling shrank to " + (size1 / size).ToString("0.00") + " of its size");
                                    if (cover > Along(end, face0, axis) + 1e-9) fails.Add(tag + ": nothing covers the hose's end at the join (cover from " + cover.ToString("0.000") + ")");
                                }
                Assert(legacyStubs == cases / 2, "can-fail: the old fitting (full lead-in at the cell edge) stuck out on only " + legacyStubs + " of " + cases / 2 + " side arrivals");
                Assert(fails.Count == 0, fails.Count + " of " + cases + " port fittings wrong: " + string.Join(" | ", fails.Take(4)));
            });
        }
    }
}
