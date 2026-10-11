using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    /// <summary>The hose and trail families of GSS's seeded action-sequence fuzz (design/RimMandrake/gss_offline_fuzz_B.md),
    /// moved from GimmeSomeSlack/Source/SelfTest/GssFuzz.cs at the hose port (step 2) with the plumbing they need.</summary>
    internal static class HoseFuzz
    {
        internal sealed class Tally { public string Name; public long Cases, Steps, Failures; public double Seconds; public string Extra = ""; }

        internal static List<T> Shrink<T>(List<T> acts, Func<List<T>, bool> fails)
        {
            var cur = new List<T>(acts);
            int chunk = Math.Max(1, cur.Count / 2);
            while (true)
            {
                bool any = false;
                for (int i = 0; i < cur.Count;)
                {
                    int n = Math.Min(chunk, cur.Count - i);
                    var cand = new List<T>(cur);
                    cand.RemoveRange(i, n);
                    if (fails(cand)) { cur = cand; any = true; } else i += n;
                }
                if (chunk == 1 && !any) break;
                if (!any) chunk = Math.Max(1, chunk / 2);
            }
            return cur;
        }

        private static string Tag(string msg) { int i = msg.IndexOf(':'); return i < 0 ? msg : msg.Substring(0, i); }
        private static bool Finite(double d) => !double.IsNaN(d) && !double.IsInfinity(d);
        private static bool Finite(V2 p) => Finite(p.X) && Finite(p.Z);
        private static string Where(string fam, long seed, IEnumerable<object> acts, string msg) =>
            fam + " seed " + seed + ": " + msg + " | " + string.Join(" ", acts.Select(a => a.ToString()));
        private static string Arg(string[] args, string name) { int i = Array.IndexOf(args, name); return i >= 0 && i + 1 < args.Length ? args[i + 1] : null; }

        private static void Report(Tally t, List<string> fails)
        {
            Program.Check(t.Failures == 0, "fuzz " + t.Name + ": " + t.Cases + " cases, " + t.Steps + " steps, " + t.Failures + " failure(s)");
            Console.WriteLine("  fuzz " + t.Name.PadRight(7) + t.Cases.ToString().PadLeft(7) + " cases " + t.Steps.ToString().PadLeft(9) + " steps " + t.Seconds.ToString("0.00").PadLeft(7) + " s" + t.Extra);
            foreach (string k in fails.Where(f => f.StartsWith("KNOWNGAP "))) Console.WriteLine("    " + k.Substring(9));
            foreach (var g in fails.Where(f => !f.StartsWith("KNOWNGAP ")).GroupBy(f => { string k = System.Text.RegularExpressions.Regex.Replace(f, "^[a-z]+ seed [0-9]+: ", ""); k = System.Text.RegularExpressions.Regex.Replace(k, "[0-9]+(\\.[0-9]+)?", "#"); int cut = k.IndexOf(" | "); if (cut >= 0) k = k.Substring(0, cut); return k.Length > 70 ? k.Substring(0, 70) : k; }).OrderByDescending(g => g.Count()))
                Console.WriteLine("    " + g.Count() + " x " + g.Key + "   first: " + g.First());
        }

        // ================================================================== HOSE
        internal sealed class HoseCase
        {
            public CordWorld W; public HoseReelRect Reel; public Cell Target; public double MaxLen; public double MinR; public ulong Seed;
            public int Walls;
            public override string ToString() => "reel(" + Reel.X0 + "," + Reel.Z0 + ") -> " + Target + " max " + MaxLen.ToString("0.0") + " minR " + MinR.ToString("0.0") + " walls " + Walls;
        }

        internal static HoseCase MakeHose(long seed, List<Cell> wallsOverride = null)
        {
            CordRng r = CordRng.Of("gssfuzz-hose", seed);
            int W = r.Int(18, 40), H = r.Int(14, 30);
            var w = new CordWorld(W, H);
            var hc = new HoseCase { W = w, MaxLen = r.Range(10, 60), MinR = new[] { 0.6, 1.2, 1.2, 2.0 }[r.Int(0, 3)], Seed = (ulong)seed };
            var reel = new HoseReelRect(r.Int(3, W - 8), r.Int(3, H - 8), 2, 2);
            if (r.Chance(0.15)) reel = new HoseReelRect(reel.X0, reel.Z0, 1, 1);
            hc.Reel = reel;
            double reach = Math.Min(hc.MaxLen, 25);
            int tx = (int)Math.Round(reel.Centre.X + r.Range(-reach, reach) * 0.8), tz = (int)Math.Round(reel.Centre.Z + r.Range(-reach, reach) * 0.8);
            hc.Target = new Cell(Math.Max(0, Math.Min(W - 1, tx)), Math.Max(0, Math.Min(H - 1, tz)));
            if (wallsOverride != null) { foreach (Cell c in wallsOverride) w.SetBlocked(c, BlockKind.Wall); hc.Walls = wallsOverride.Count; }
            else
            {
                int blobs = r.Int(0, 7);
                for (int k = 0; k < blobs; k++)
                {
                    int x0 = r.Int(0, W - 1), z0 = r.Int(0, H - 1), bw = r.Int(1, 8), bh = r.Int(1, 3);
                    if (r.Chance(0.5)) { int t = bw; bw = bh; bh = t; }
                    var kind = r.Chance(0.7) ? BlockKind.Wall : BlockKind.Water;
                    for (int z = z0; z < Math.Min(H, z0 + bh); z++) for (int x = x0; x < Math.Min(W, x0 + bw); x++) { w.SetBlocked(new Cell(x, z), kind); hc.Walls++; }
                }
                for (int k = r.Int(0, 6); k > 0; k--) w.SetExtraCost(new Cell(r.Int(0, W - 1), r.Int(0, H - 1)), 1.5f);
            }
            // the reel's footprint and the cells round it are open ground
            for (int z = reel.Z0 - 2; z < reel.Z0 + reel.H + 2; z++) for (int x = reel.X0 - 2; x < reel.X0 + reel.W + 2; x++) if (w.InBounds(new Cell(x, z))) w.SetBlocked(new Cell(x, z), BlockKind.None);
            return hc;
        }

        private static string FiniteList(IList<V2> pts, string what)
        {
            foreach (V2 p in pts) if (!Finite(p)) return what + " has a non-finite point";
            return null;
        }

        /// <summary>Why the hose lays the route check passed were refused, per mode (printed with the hose family).</summary>
        internal static readonly Dictionary<string, int> RefuseWhy = new Dictionary<string, int>();

        internal static string RunHose(long seed, List<Cell> wallsOverride, ref long steps, out int laidOk, out int fellBack, bool outlet = true, List<string> gaps = null)
        {
            laidOk = fellBack = 0;
            string mode = outlet ? "[outlet]" : "[free]";
            HoseCase c = MakeHose(seed, wallsOverride);
            CordWorld w = c.W;
            string why = HoseMath.CheckInstall(w, c.Reel, c.Target, c.MaxLen);
            steps++;
            // install verdict vs an independent unbounded route read
            Cell start = c.Reel.StartCellToward(c.Target);
            bool inb = w.InBounds(c.Target), fitsStraight = V2.Dist(c.Reel.Centre, c.Target.Centre) <= c.MaxLen;
            if (inb && !c.Reel.Contains(c.Target) && fitsStraight && w.IsWalkable(c.Target))
            {
                List<Cell> full = HoseMath.RouteCells(w, start, c.Target, -1, false);   // B2: install judges the SHORTEST route
                bool capped = HoseMath.LastRouteCapped;
                double need = -1;
                if (full != null)
                {
                    var pts = HoseMath.RoutePulled(w, c.Reel, c.Target, -1, false);
                    need = pts == null ? -1 : Geo.Length(pts) * HoseMath.RouteMargin;
                }
                steps++;
                if (!capped)
                {
                    if (full == null && why != "no route") return "install: unbounded search finds no route but CheckInstall said " + (why ?? "ok");
                    if (full != null && need <= c.MaxLen && why != null) return "install: route needs " + need.ToString("0.00") + " <= " + c.MaxLen.ToString("0.00") + " but CheckInstall said '" + why + "' (the length-bounded search missed a route that fits)";
                    if (full != null && need > c.MaxLen && why == null) return "install: route needs " + need.ToString("0.00") + " > " + c.MaxLen.ToString("0.00") + " but CheckInstall allowed it";
                }
            }
            if (why != null) return null;

            var p = new HoseShapeParams { MinBendRadius = c.MinR, MaxLength = c.MaxLen, Slack = 1.0, PlumpAmount = 1.0 };
            V2 a = c.Reel.Mouth, b = c.Target.Centre;
            V2? outward = outlet ? c.Reel.Outward : (V2?)null;
            HoseLay lay = HoseMath.Lay(w, a, b, p, c.Seed, null, outward);
            steps++;
            HoseLay lay2 = HoseMath.Lay(w, a, b, p, c.Seed, null, outward);
            if (lay.Ok != lay2.Ok || (lay.Ok && !lay.Flat.SequenceEqual(lay2.Flat))) return "hose" + mode + ": Lay twice with one seed gave different hoses";
            if (!lay.Ok) { lock (RefuseWhy) { RefuseWhy.TryGetValue(mode + " " + lay.Reason, out int rn); RefuseWhy[mode + " " + lay.Reason] = rn + 1; } return null; }     // an install the route check passed but the lay refused: the reel retracts with the reason (CheckReplan), not a fault
            laidOk = 1; if (lay.FellBack) fellBack = 1;
            string bad = FiniteList(lay.Flat, "Flat") ?? FiniteList(lay.Plump, "Plump") ?? FiniteList(lay.Centre, "Centre");
            if (bad != null) return "hose" + mode + ": " + bad;
            if (V2.Dist(lay.Flat[0], a) > 1e-3 || V2.Dist(lay.Flat[lay.Flat.Count - 1], b) > 1e-3) return "hose" + mode + ": endpoints not attached (flat " + lay.Flat[0] + " .. " + lay.Flat[lay.Flat.Count - 1] + " vs " + a + " .. " + b + ")";
            if (V2.Dist(lay.Plump[0], a) > 1e-3 || V2.Dist(lay.Plump[lay.Plump.Count - 1], b) > 1e-3) return "hose" + mode + ": plump endpoints not attached";
            // KNOWN GAPS: design invariants the shipped code does not hold. Each is tallied with its first shrunk reproducer
            // (design/RimMandrake/gss_offline_fuzz_B.md) and does not fail the run; a gross version of each is still asserted below.
            double bigger = Math.Max(lay.FlatLen, lay.PlumpLen);
            // length: the hose is never longer than the hose. The nozzled 2x2 reel's outlet run (the game always lays it outward) is planned
            // from 1.6 + 2 radii past the mouth, a lead CheckInstall's route length does not count; in free mode a walled corridor overran by 3%.
            // G1 FIXED 2026-10-06 (GPT B3): LayOn retries an overlong lay with no slack and otherwise refuses it -- asserted
            if (bigger > c.MaxLen + 1e-6) return "hose" + mode + ": G1 laid hose longer than the hose: " + bigger.ToString("0.00") + " > " + c.MaxLen.ToString("0.00");
            if (bigger > c.MaxLen * 1.6 + 1) return "hose" + mode + ": laid length " + bigger.ToString("0.00") + " is wildly over the hose " + c.MaxLen.ToString("0.0");
            // plump is the flat hose pulled toward its centreline: shorter, give or take resampling noise
            if (lay.PlumpLen > lay.FlatLen * 1.01 + 0.1) gaps?.Add("G4 plump hose longer than flat: " + lay.PlumpLen.ToString("0.00") + " vs " + lay.FlatLen.ToString("0.00"));
            if (lay.PlumpLen > lay.FlatLen * 1.25 + 0.5) return "hose" + mode + ": plump (" + lay.PlumpLen.ToString("0.00") + ") much longer than flat (" + lay.FlatLen.ToString("0.00") + ")";
            if (!HoseMath.Clear(w, lay.Flat)) return "hose" + mode + ": flat hose runs through a wall";
            if (!HoseMath.Clear(w, lay.Plump)) return "hose" + mode + ": plump hose runs through a wall";
            if (lay.Flat.Count != lay.Plump.Count) return "hose" + mode + ": flat/plump sample counts differ";
            if (!lay.FellBack)
            {
                // leaving the nozzle west and turning back east is a U-turn inside the blend zone (OutletLead cells from the mouth)
                double skip = outlet ? HoseMath.OutletLead(p) + 0.5 : HoseMath.EndSkip;
                double bf = HoseMath.MinBendRadius(lay.Flat, skip), bp = HoseMath.MinBendRadius(lay.Plump, skip);
                // G2 FIXED 2026-10-06 (owner decision by question card: straight lead-out): the lead-out (straight run + Dubins
                // join) never bends under the minimum -- asserted over the lead-out section of both poses
                if (outlet && outward.HasValue)
                {
                    double lo = LeadOutBend(lay.Flat, lay.LeadOutLen), lp = LeadOutBend(lay.Plump, lay.LeadOutLen);
                    if (lay.LeadOutLen <= 0) return "hose" + mode + ": outlet lay has no lead-out";
                    if (Math.Min(lo, lp) < c.MinR * 0.95) return "hose" + mode + ": G2 lead-out bends under the minimum: " + Math.Min(lo, lp).ToString("0.00") + " < " + c.MinR.ToString("0.0");
                    if (lay.MinBendFlat < c.MinR * 0.95) gaps?.Add("G2 bend tighter than the hose may bend (outlet lay, outside the lead-out): " + lay.MinBendFlat.ToString("0.00") + " < " + c.MinR.ToString("0.0"));
                }
                if (gaps != null && BendCollect) OutletBendProbe(seed, outlet, lay, p, c.MinR, a, b, outward);
                if (Math.Min(bf, bp) < c.MinR * 0.95) gaps?.Add("G3 bend beyond the blend under 95% of minR: " + Math.Min(bf, bp).ToString("0.00") + " < " + c.MinR.ToString("0.0"));
                if (Math.Min(bf, bp) < c.MinR * 0.1) return "hose" + mode + ": bend radius " + Math.Min(bf, bp).ToString("0.00") + " beyond the outlet blend is under a tenth of " + c.MinR.ToString("0.0");
                if (HoseMath.SelfIntersects(lay.Flat)) gaps?.Add("G5 flat hose crosses itself (design: no loops)");
            }
            // the joints index real samples, ascending, never at an end
            int prev = 0;
            foreach (int j in lay.Joints) { if (j <= prev || j >= lay.Flat.Count - 1) return "hose" + mode + ": joint index " + j + " out of order or at an end"; prev = j; }
            return null;
        }

        /// <summary>Min discrete bend radius over the lead-out section [EndSkip, leadLen] of a pose (same measure as MinBendRadius).</summary>
        internal static double LeadOutBend(IList<V2> X, double leadLen)
        {
            double[] s = Geo.CumLen(X);
            double best = 99;
            for (int i = 1; i < X.Count - 1; i++)
            {
                if (s[i] < HoseMath.EndSkip || s[i] > leadLen) continue;
                double th = CordLayer.Turn(X[i - 1], X[i], X[i + 1]);
                double seg = 0.5 * (V2.Dist(X[i - 1], X[i]) + V2.Dist(X[i], X[i + 1]));
                if (th > 1e-9) best = Math.Min(best, seg / th);
            }
            return best;
        }

        // ================================================================== G2 LOCATOR (2026-10-06, live hose FAILs vs fuzz G2)
        /// <summary>One laid, non-fallback hose's bend profile: where the tightest bend sits and how far the hose has to turn
        /// across the outlet blend. Collected per seed for both modes; the hose driver prints the comparison.</summary>
        internal sealed class BendRec { public long Seed; public double MinR, MinBend, SAt, Straight, BlendEnd, TurnDeg, BackDeg; public string Zone; }
        internal static bool BendCollect;
        internal static readonly List<BendRec> BendOutlet = new List<BendRec>();
        internal static readonly Dictionary<long, double> BendFree = new Dictionary<long, double>();

        /// <summary>MinBendRadius with the arc position of the minimum (same discrete radius, same skip).</summary>
        internal static double MinBendAt(IList<V2> X, double skip, out double sAt)
        {
            double[] s = Geo.CumLen(X);
            double L = s[s.Length - 1], best = 99; sAt = -1;
            for (int i = 1; i < X.Count - 1; i++)
            {
                if (s[i] < skip || s[i] > L - skip) continue;
                double th = CordLayer.Turn(X[i - 1], X[i], X[i + 1]);
                double seg = 0.5 * (V2.Dist(X[i - 1], X[i]) + V2.Dist(X[i], X[i + 1]));
                if (th > 1e-9 && seg / th < best) { best = seg / th; sAt = s[i]; }
            }
            return best;
        }

        /// <summary>Unit heading of polyline X at arc length t (the segment containing t).</summary>
        internal static V2 HeadingAt(IList<V2> X, double t)
        {
            double[] s = Geo.CumLen(X);
            for (int i = 1; i < X.Count; i++)
                if (s[i] >= t || i == X.Count - 1) { V2 d = X[i] - X[i - 1]; double l = Math.Sqrt(d.X * d.X + d.Z * d.Z); return l > 1e-9 ? d * (1 / l) : new V2(1, 0); }
            return new V2(1, 0);
        }

        private static double AngleDeg(V2 u, V2 v)
        {
            double d = Math.Max(-1, Math.Min(1, u.X * v.X + u.Z * v.Z));
            return Math.Acos(d) * 180 / Math.PI;
        }

        private static void OutletBendProbe(long seed, bool outlet, HoseLay lay, HoseShapeParams p, double minR, V2 a, V2 b, V2? outward)
        {
            if (!outlet) { BendFree[seed] = Math.Min(HoseMath.MinBendRadius(lay.Flat, HoseMath.EndSkip), HoseMath.MinBendRadius(lay.Plump, HoseMath.EndSkip)); return; }
            if (!outward.HasValue) return;
            double st = HoseMath.LeadOutStraight(p), bl = Math.Max(0, lay.LeadOutLen - st);   // 2026-10-06: the straight lead-out, then its join
            double mb = MinBendAt(lay.Flat, HoseMath.EndSkip, out double sAt);
            V2 h = HeadingAt(lay.Flat, st + bl + 0.25);
            V2 ab = b - a; double lab = Math.Sqrt(ab.X * ab.X + ab.Z * ab.Z);
            BendOutlet.Add(new BendRec
            {
                Seed = seed, MinR = minR, MinBend = mb, SAt = sAt, Straight = st, BlendEnd = st + bl,
                TurnDeg = AngleDeg(outward.Value, h),
                BackDeg = lab > 1e-9 ? AngleDeg(outward.Value, ab * (1 / lab)) : 0,
                Zone = sAt < 0 ? "none" : sAt <= st ? "straight" : sAt <= st + bl + 0.25 ? "blend" : "beyond",
            });
        }

        /// <summary>GPT source read 2026-10-06 finding B2 (gss_gpt_source_read_2026-10-06.md): RouteCells minimises step + ExtraCost
        /// while CheckInstall judges the route it returns by LENGTH, so a fitting route through costly cells (the hose world
        /// charges water 3/cell) can lose to a cheaper, longer dry detour that does not fit. A fixed scene: a 3-wide watery
        /// corridor straight to the target (fits) and a dry tunnel the long way round (too long). Tallied, never failed.</summary>
        internal static List<string> CostVsLengthProbe()
        {
            var o = new List<string>();
            // rock from x 6 to 30 except the corridor (z 9-11) and a dry tunnel at z 19: the dry way is ~44 cells, inside
            // the search bound (1.5 x 32 / 1.05 + 4 = 49.7) but longer than the hose
            // a dog-legged corridor (so string-pulling the dry route cannot cut back through it) of costly cells, and a dry
            // tunnel at z 25 the long way round: inside the search bound (1.5 x 40 / 1.05 + 4 = 61) but longer than the hose
            bool Corridor(int x, int z) => (x >= 6 && x <= 18 && z >= 9 && z <= 11) || (x >= 16 && x <= 18 && z >= 9 && z <= 17) || (x >= 16 && x <= 30 && z >= 15 && z <= 17);
            CordWorld Rocky() { var cw = new CordWorld(50, 30); for (int x = 6; x <= 30; x++) for (int z = 0; z < 30; z++) if (!Corridor(x, z) && z != 25) cw.SetBlocked(new Cell(x, z), BlockKind.Rock); return cw; }
            CordWorld w = Rocky();
            for (int x = 6; x <= 30; x++) for (int z = 0; z < 30; z++) if (Corridor(x, z)) w.SetExtraCost(new Cell(x, z), 3f);
            var reel = new HoseReelRect(3, 10, 1, 1);
            var target = new Cell(32, 10);
            const double hose = 40;
            string why = HoseMath.CheckInstall(w, reel, target, hose);
            CordWorld dry = Rocky();
            double waterLen = HoseMath.RouteLength(dry, reel, target);          // same walls, no cost: the corridor's own length
            double chosen = HoseMath.RouteLength(w, reel, target);
            List<Cell> cp = HoseMath.RouteCells(w, reel.StartCellToward(target), target, -1);
            string pathNote = cp == null ? "no path" : cp.Count + " cells, " + cp.Count(q => q.Z >= 20) + " in the dry tunnel stretch, extra cost " + cp.Sum(q => w.ExtraCost(q)).ToString("0");
            bool gap = why == "route too long" && waterLen > 0 && waterLen * HoseMath.RouteMargin <= hose;
            Program.Check(!gap && why == null, "fuzz G6 (GPT B2 fixed): a 37.4-cell costly corridor fits a 40-cell hose and is allowed (CheckInstall said '" + (why ?? "ok") + "')");
            // can-fail: the cost-first route (what the old CheckInstall judged) is the long dry detour that does not fit
            Program.Check(chosen * HoseMath.RouteMargin > hose, "fuzz G6 can-fail: the cost-first route still reads too long (" + (chosen * HoseMath.RouteMargin).ToString("0.0") + ")");
            o.Add("G6 (cost vs length, GPT B2, FIXED 2026-10-06): " + (gap ? "REPRODUCED" : "not reproduced") + ": hose " + hose.ToString("0") + ", the corridor route needs " +
                  (waterLen * HoseMath.RouteMargin).ToString("0.0") + " (fits) but the search returns a " + (chosen * HoseMath.RouteMargin).ToString("0.0") +
                  "-cell route (" + pathNote + ") and CheckInstall says '" + (why ?? "ok") + "'");
            return o;
        }

        /// <summary>The G2 hypothesis test (live: 9 matrix hose FAILs, bend ~0.19 vs 1.14; fuzz: 965/1445 outlet cases): is the
        /// tight bend IN the outlet blend, does the same case laid without the outlet bend fine, and does the turn the blend
        /// must make predict it (a blend of length bl turning theta cannot hold a radius above bl / theta).</summary>
        internal static List<string> OutletBendReport()
        {
            var o = new List<string>();
            var bad = BendOutlet.Where(r => r.MinBend < r.MinR * 0.95).ToList();
            var good = BendOutlet.Where(r => r.MinBend >= r.MinR * 0.95).ToList();
            if (BendOutlet.Count == 0) return o;
            int inBlend = bad.Count(r => r.Zone == "blend"), inStraight = bad.Count(r => r.Zone == "straight"), beyond = bad.Count(r => r.Zone == "beyond");
            var paired = bad.Where(r => BendFree.ContainsKey(r.Seed)).ToList();
            int freeOk = paired.Count(r => BendFree[r.Seed] >= r.MinR * 0.95);
            double Med(IEnumerable<double> xs) { var l = xs.OrderBy(x => x).ToList(); return l.Count == 0 ? double.NaN : l[l.Count / 2]; }
            int boundHolds = bad.Count(r => r.TurnDeg > 1 && r.MinBend <= (r.BlendEnd - r.Straight) / (r.TurnDeg * Math.PI / 180) + 1e-6);
            o.Add("G2 locator: " + bad.Count + "/" + BendOutlet.Count + " outlet lays bend under 95% of minR; tightest bend in the straight run " + inStraight +
                  ", in the blend " + inBlend + ", beyond it " + beyond);
            o.Add("G2 locator: same seed laid WITHOUT the outlet bends within 95% of minR in " + freeOk + "/" + paired.Count + " of those (2x2 reels)");
            o.Add("G2 locator: turn across the blend (outward vs heading after it) median " + Med(bad.Select(r => r.TurnDeg)).ToString("0") + " deg failing vs " +
                  Med(good.Select(r => r.TurnDeg)).ToString("0") + " deg passing; target bearing from outward median " + Med(bad.Select(r => r.BackDeg)).ToString("0") +
                  " deg failing vs " + Med(good.Select(r => r.BackDeg)).ToString("0") + " passing; radius <= blend/turn in " + boundHolds + "/" + bad.Count);
            var worst = bad.OrderBy(r => r.MinBend / r.MinR).FirstOrDefault();
            if (worst != null) o.Add("G2 locator worst: seed " + worst.Seed + " bend " + worst.MinBend.ToString("0.00") + " at s=" + worst.SAt.ToString("0.00") +
                                     " (straight to " + worst.Straight.ToString("0.0") + ", blend to " + worst.BlendEnd.ToString("0.0") + "), turn " + worst.TurnDeg.ToString("0") + " deg, minR " + worst.MinR.ToString("0.0"));
            return o;
        }

        // ================================================================== TRAIL (carry machine)
        internal struct TAct
        {
            public int Kind, X, Z; public double Amt;
            public static readonly string[] Names = { "Grab", "Step", "SetDown", "Interrupt", "PickUp", "Wind", "WindBy", "WindInt", "Replan", "ReelGone", "DevLay", "DevReelIn" };
            public override string ToString() => Names[Kind] + (Kind == 1 ? "(" + X + "," + Z + ")" : Kind == 6 ? "(" + Amt.ToString("0.0") + ")" : Kind == 8 || Kind == 10 ? "(n" + X + ")" : "");
        }

        private static CordWorld TrailWorld(long seed, out Cell reel, out double maxLen)
        {
            CordRng r = CordRng.Of("gssfuzz-trail", seed);
            var w = new CordWorld(36, 24);
            for (int k = r.Int(3, 10); k > 0; k--)
            {
                int x0 = r.Int(2, 33), z0 = r.Int(1, 22), bw = r.Int(1, 6), bh = r.Int(1, 3);
                if (r.Chance(0.5)) { int t = bw; bw = bh; bh = t; }
                for (int z = z0; z < Math.Min(24, z0 + bh); z++) for (int x = x0; x < Math.Min(36, x0 + bw); x++) w.SetBlocked(new Cell(x, z), BlockKind.Wall);
            }
            reel = new Cell(r.Int(4, 8), r.Int(8, 14));
            for (int z = reel.Z - 2; z <= reel.Z + 2; z++) for (int x = reel.X - 2; x <= reel.X + 2; x++) w.SetBlocked(new Cell(x, z), BlockKind.None);
            maxLen = r.Range(8, 45);
            return w;
        }

        private static List<TAct> GenTrail(long seed, int n)
        {
            CordRng r = CordRng.Of("gssfuzz-tacts", seed);
            var l = new List<TAct>();
            int[] wt = { 4, 60, 4, 4, 5, 4, 12, 3, 3, 1, 2, 2 };
            int total = wt.Sum();
            for (int i = 0; i < n; i++)
            {
                int pick = r.Int(0, total - 1), k = 0;
                while (pick >= wt[k]) { pick -= wt[k]; k++; }
                l.Add(new TAct { Kind = k, X = r.Int(-1, 1), Z = r.Int(-1, 1), Amt = r.Range(0.2, 8) });
                if (k == 8 || k == 10) l[l.Count - 1] = new TAct { Kind = k, X = r.Int(1, 70), Amt = 0 };
            }
            return l;
        }

        private static bool Legal(CordWorld w, Cell from, Cell to)
        {
            if (!w.IsWalkable(to)) return false;
            return to.X == from.X || to.Z == from.Z || (w.IsWalkable(new Cell(to.X, from.Z)) && w.IsWalkable(new Cell(from.X, to.Z)));
        }

        internal static string RunTrail(long seed, List<TAct> acts, ref long steps)
        {
            CordWorld w = TrailWorld(seed, out Cell reel, out double maxLen);
            V2 mouth = reel.Centre;
            var m = new HoseCarryMachine(w, mouth, maxLen);
            Cell cur = reel;
            double windStart = 0;
            for (int i = 0; i < acts.Count; i++)
            {
                TAct a = acts[i];
                HoseCarryState before = m.State;
                double lenBefore = m.State == HoseCarryState.Stored ? 0 : m.Trail.PulledLength(w);
                int cellsBefore = m.Trail.Cells.Count;
                double woundBefore = m.Wound;
                switch (a.Kind)
                {
                    case 0: if (m.Grab(reel)) cur = reel; break;
                    case 1:
                        {
                            var n = new Cell(cur.X + a.X, cur.Z + a.Z);
                            if (m.State == HoseCarryState.Carrying && Legal(w, cur, n)) { m.CarrierStep(n); if (m.State == HoseCarryState.Carrying) cur = n; }
                            break;
                        }
                    case 2: m.SetDown(); break;
                    case 3: m.Interrupt(); break;
                    case 4: if (m.PickUp()) cur = m.Trail.Last; break;
                    case 5: if (m.BeginWind()) windStart = lenBefore; break;
                    case 6: m.WindBy(a.Amt); break;
                    case 7: m.WindInterrupt(); break;
                    case 8: m.Replan(Row(reel, w, a.X)); break;
                    case 9: m.ReelGone(); break;
                    case 10: m.DevLay(Row(reel, w, a.X)); break;
                    case 11: m.DevReelIn(); break;
                }
                steps++;
                string inv = m.Invariant();
                if (inv != null) return "trail: invariant broken: " + inv + " (step " + i + ")";
                if (m.State != HoseCarryState.Stored)
                {
                    List<V2> pulled = m.Trail.Pulled(w);
                    string bad = FiniteList(pulled, "Pulled");
                    if (bad != null) return "trail: " + bad;
                    if (V2.Dist(pulled[0], mouth) > 1e-9) return "trail: pulled hose is detached from the reel mouth";
                    if (V2.Dist(pulled[pulled.Count - 1], m.Trail.Last.Centre) > 1e-9) return "trail: pulled hose does not reach the end cell";
                    if (m.Trail.Cells.Distinct().Count() != m.Trail.Cells.Count) return "trail: a cell appears twice on the trail";
                    if (!HoseMath.Clear(w, pulled, 0)) return "trail: the pulled hose runs through a wall (" + string.Join(" ", m.Trail.Cells.Take(14)) + ")";
                }
                // length conservation: stepping never lengthens a Carrying hose past the hose; winding only ever shortens
                if (a.Kind == 1 && before == HoseCarryState.Carrying && m.Trail.Cells.Count > 0 && m.State != HoseCarryState.Stored && m.Trail.PulledLength(w) > maxLen + 1e-9) return "trail: stepping stretched the hose past its length";
                if (a.Kind == 6 && before == HoseCarryState.Retracting)
                {
                    if (m.State == HoseCarryState.Retracting)
                    {
                        if (m.Wound < woundBefore - 1e-12) return "trail: wound length went backwards";
                        List<V2> drawn = HoseTrail.Clip(m.Trail.Pulled(w), m.Wound);
                        double want = Math.Max(0, lenBefore - m.Wound);
                        if (Math.Abs(Geo.Length(drawn) - want) > 1e-6) return "trail: wound " + m.Wound.ToString("0.00") + " of " + lenBefore.ToString("0.00") + " leaves " + Geo.Length(drawn).ToString("0.000") + " drawn, want " + want.ToString("0.000");
                        if (V2.Dist(drawn[0], mouth) > 1e-9) return "trail: the wound hose lost its reel end";
                    }
                    else if (m.State != HoseCarryState.Stored) return "trail: winding moved a Retracting hose to " + m.State;
                }
                if (a.Kind == 7 && before == HoseCarryState.Retracting && m.State == HoseCarryState.Dropped)
                {
                    double after = m.Trail.PulledLength(w);
                    if (m.Trail.Cells.Count > 1 && after > lenBefore - woundBefore + 1e-9) return "trail: interrupted wind kept " + after.ToString("0.00") + " but " + woundBefore.ToString("0.00") + " of " + lenBefore.ToString("0.00") + " was wound";
                    if (after > lenBefore + 1e-9) return "trail: interrupted wind lengthened the hose";
                    _ = windStart;
                }
            }
            return null;
        }

        private static List<Cell> Row(Cell reel, CordWorld w, int n)
        {
            var l = new List<Cell>();
            for (int i = 0; i <= n; i++) { var c = new Cell(reel.X + i, reel.Z); if (!w.IsWalkable(c)) break; l.Add(c); }
            return l;
        }


        public static void Run(string[] args)
        {
            double scale = double.Parse(Arg(args, "--fuzz-scale") ?? "1", System.Globalization.CultureInfo.InvariantCulture);
            if (scale <= 0) return;
            string only = Arg(args, "--fuzz-only");
            string one = Arg(args, "--fuzz-seed");
            int Cases(int n) => Math.Max(1, (int)Math.Round(n * scale));
            var all = Stopwatch.StartNew();
            var tallies = new List<Tally>();
            BendOutlet.Clear(); BendFree.Clear();
            if (only == null || only == "hose")
            {
                var t = new Tally { Name = "hose" }; var fails = new List<string>();
                var sw = Stopwatch.StartNew();
                int n = one != null ? 1 : Cases(1500), laid = 0, fb = 0;
                var gapCount = new Dictionary<string, int>(); var gapFirst = new Dictionary<string, (long, bool, string)>(); var laidModes = new int[2];
                for (int k = 0; k < n; k++)
                {
                    long seed = one != null ? long.Parse(one) : k + 1;
                    long steps = 0;
                    foreach (bool outlet in new[] { true, false })
                    {
                        if (!outlet && MakeHose(seed).Reel.W != 2) continue;     // a 1x1 reel has no outlet: the second mode would repeat the first
                        var gl = new List<string>();
                        BendCollect = true;
                        string msg = RunHose(seed, null, ref steps, out int ok, out int f, outlet, gl);
                        BendCollect = false;
                        laid += ok; fb += f;
                        t.Cases++; t.Steps += steps; steps = 0;
                        if (ok == 1) laidModes[outlet ? 0 : 1]++;
                        foreach (string g in gl.Select(x => x.Substring(0, 2)).Distinct())
                        {
                            gapCount.TryGetValue(g + (outlet ? "o" : "f"), out int gc); gapCount[g + (outlet ? "o" : "f")] = gc + 1;
                            if (!gapFirst.ContainsKey(g + (outlet ? "o" : "f"))) gapFirst[g + (outlet ? "o" : "f")] = (seed, outlet, gl.First(x => x.StartsWith(g)));
                        }
                        if (msg == null) continue;
                        t.Failures++;
                        string tag = Tag(msg);
                        // shrink the wall set: reproduce the exact walls, then delete them while the same fault remains
                        HoseCase hc = MakeHose(seed);
                        var walls = new List<Cell>();
                        for (int z = 0; z < hc.W.Height; z++) for (int x = 0; x < hc.W.Width; x++) if (!hc.W.IsWalkable(new Cell(x, z))) walls.Add(new Cell(x, z));
                        long d2 = 0;
                        List<Cell> min = Shrink(walls, c => { string m2 = RunHose(seed, c, ref d2, out _, out _, outlet); return m2 != null && Tag(m2) == tag; });
                        string m3 = RunHose(seed, min, ref d2, out _, out _, outlet);
                        fails.Add("hose seed " + seed + ": " + (m3 ?? msg) + " | " + MakeHose(seed, min) + " | walls " + string.Join(" ", min.Take(20).Select(c => c.ToString())));
                    }
                }
                // each known gap: how often, and its first reproducer shrunk to the fewest walls that still show it
                var gapLines = new List<string>();
                foreach (var kv in gapCount.OrderBy(k => k.Key))
                {
                    (long gseed, bool go, string gmsg) = gapFirst[kv.Key];
                    string cls = kv.Key.Substring(0, 2);
                    HoseCase hc = MakeHose(gseed);
                    var walls = new List<Cell>();
                    for (int z = 0; z < hc.W.Height; z++) for (int x = 0; x < hc.W.Width; x++) if (!hc.W.IsWalkable(new Cell(x, z))) walls.Add(new Cell(x, z));
                    long d2 = 0;
                    bool Has(List<Cell> ws) { var l2 = new List<string>(); RunHose(gseed, ws, ref d2, out _, out _, go, l2); return l2.Any(x => x.StartsWith(cls)); }
                    List<Cell> min = Shrink(walls, ws => Has(ws));
                    gapLines.Add("known gap " + kv.Key.Substring(0, 2) + (go ? " [outlet] " : " [free] ") + kv.Value + "/" + laidModes[go ? 0 : 1] + " laid: " + gmsg + "  (seed " + gseed + ", " + MakeHose(gseed, min) + (min.Count > 0 ? ", walls " + string.Join(" ", min.Take(12)) : "") + ")");
                }
                foreach (string gl in gapLines) fails.Add("KNOWNGAP " + gl);
                foreach (string gl in OutletBendReport()) fails.Add("KNOWNGAP " + gl);
                foreach (string gl in CostVsLengthProbe()) fails.Add("KNOWNGAP " + gl);
                foreach (var kv in RefuseWhy.OrderBy(k => k.Key)) fails.Add("KNOWNGAP refused after the route check " + kv.Key + ": " + kv.Value);
                sw.Stop(); t.Seconds = sw.Elapsed.TotalSeconds; t.Extra = "   (" + laid + " laid, " + fb + " via fallback, " + gapCount.Count + " known-gap class(es) tallied below)"; t.Failures -= 0;
                Report(t, fails); tallies.Add(t);
            }
            if (only == null || only == "trail")
            {
                var t = new Tally { Name = "trail" }; var fails = new List<string>();
                var sw = Stopwatch.StartNew();
                int n = one != null ? 1 : Cases(1500);
                var visited = new HashSet<HoseCarryState>();
                for (int k = 0; k < n; k++)
                {
                    long seed = one != null ? long.Parse(one) : k + 1;
                    CordRng cr = CordRng.Of("gssfuzz-tlen", seed);
                    List<TAct> acts = GenTrail(seed, cr.Int(20, 160));
                    long steps = 0;
                    string msg = RunTrail(seed, acts, ref steps);
                    t.Cases++; t.Steps += steps;
                    if (msg == null) continue;
                    t.Failures++;
                    string tag = Tag(msg);
                    long d2 = 0;
                    List<TAct> min = Shrink(acts, c => { string m2 = RunTrail(seed, c, ref d2); return m2 != null && Tag(m2) == tag; });
                    string m3 = RunTrail(seed, min, ref d2);
                    fails.Add(Where("trail", seed, min.Cast<object>(), m3 ?? msg));
                }
                sw.Stop(); t.Seconds = sw.Elapsed.TotalSeconds;
                Report(t, fails); tallies.Add(t);
            }
            all.Stop();
            Console.WriteLine("hose fuzz total: " + tallies.Sum(x => x.Cases) + " cases, " + tallies.Sum(x => x.Steps) + " steps, " + all.Elapsed.TotalSeconds.ToString("0.00") + " s");
        }
    }
}
