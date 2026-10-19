// Seeded fuzz of big creatures against slots, thin walls and roofs (Kernel/RM_WallsSlotsKernel.cs,
// BIG_CREATURES_DESIGN_WALLS_AND_SLOTS phase 1). Oracles are written here from the design (§3, §4, §5, §7) and the owner's card
// answers of 2026-10-18, never from the kernel:
//   breadth   B = max(1, round(sqrt bs)) halves up, override wins; P = max(B, footprint); min squeeze ceil(P/2).
//   gap       S >= P walk, 0.5P <= S < P squeeze at 1 + (k-1)*2*(1 - S/P) (x2 at half width by his card), below: no gap.
//   table     §3's table cell for cell: body size -> B; lone/roofed wood and granite -> through / smash with the stated blow count;
//             holds at T >= B.
//   sandwich  §7 test 3 (X1): wood, air, wood, air, wood for B 4 is T 2, 585 HP, smashed, never broken layer by layer; five solid
//             wood cells hold; the same crossing approached diagonally measures the same (X8).
//   plug      §7 test 4 (X7) and rock: a crossing whose route digs rock is never broken; a wooden plug is wood.
//   monotone  §7 test 10: bigger never weaker, thicker never easier, roof never makes a wall weaker, rock never damaged.
//   restless  the meter stays in [0,1], rises only with a cause, falls without; the full rule and the calm detour gate.
//   trench    card 3: steps over a trench strictly narrower than B/4.
//   wallsdeterminism every family replays a seed identically.
using System;
using System.Collections.Generic;

namespace RimMandrake.HugeThings.SelfTest
{
    internal static class WallsSlotsFuzz
    {
        public static long Cases, Checks, Throughs, Smashes, Holds, Squeezes;

        private static void Check(bool ok, string msg)
        {
            Checks++;
            if (!ok) throw new Exception(msg);
        }

        private const float Wood = 195f, Granite = 510f;   // vanilla Wall 300 x stuff factor (wood 0.65, granite 1.7), MEASURED in the design §0

        private static int OracleB(double bs)
        {
            if (bs <= 0 || double.IsNaN(bs) || double.IsInfinity(bs)) return 1;
            // halves round up: find the integer n with (n - 0.5)^2 <= bs < (n + 0.5)^2
            int n = 1;
            while ((n + 0.5) * (n + 0.5) <= bs) n++;
            return n;
        }

        internal static string CaseBreadth(int seed)
        {
            var r = new Random(seed);
            double bs = r.NextDouble() * 120;
            if (r.Next(20) == 0) bs = new[] { 0.0, -1.0, double.NaN, 2.25, 6.25, 12.25, 20.25, 30.25 }[r.Next(8)];
            int ov = r.Next(5) == 0 ? r.Next(-2, 12) : 0;
            int b = WallsSlots.Breadth((float)bs, ov);
            int want = ov > 0 ? ov : OracleB((float)bs);
            Check(b == want, "Breadth(" + bs + "," + ov + ") = " + b + ", want " + want);
            int f = r.Next(0, 6);
            int p = WallsSlots.PassageWidth(b, f);
            Check(p == Math.Max(b, Math.Max(1, f)) && p >= b, "PassageWidth(" + b + "," + f + ") = " + p);
            Check(WallsSlots.MinSqueeze(p) == (p + 1) / 2 && 2 * WallsSlots.MinSqueeze(p) >= p, "MinSqueeze(" + p + ")");
            return b + ":" + p;
        }

        internal static string CaseGap(int seed)
        {
            var r = new Random(seed);
            int p = r.Next(1, 9), s = r.Next(0, 10);
            float k = r.Next(10) == 0 ? float.NaN : (float)(1 + r.NextDouble() * 3);
            float kk = float.IsNaN(k) ? 2f : k;
            GapBand band = WallsSlots.Gap(s, p);
            GapBand want = s >= p ? GapBand.Walk : (s >= 1 && s * 2 >= p ? GapBand.Squeeze : GapBand.TooNarrow);
            Check(band == want, "Gap(" + s + "," + p + ") = " + band + ", want " + want);
            float c = WallsSlots.SqueezeCost(s, p, k);
            if (want == GapBand.Walk) Check(c == 1f, "a walkable gap costs " + c);
            if (want == GapBand.TooNarrow) Check(float.IsPositiveInfinity(c), "a too-narrow gap has a finite squeeze cost " + c);
            if (want == GapBand.Squeeze)
            {
                double o = 1 + (kk - 1) * 2 * (1 - (double)s / p);
                Check(Math.Abs(c - o) < 1e-4, "SqueezeCost(" + s + "," + p + "," + k + ") = " + c + ", want " + o);
                Check(c >= 1f && c <= kk + 1e-4, "a squeeze is never cheaper than walking or dearer than the half-width cost");
                Squeezes++;
            }
            // His card: x2 at half width with the shipped default, and §4's own table.
            Check(Math.Abs(WallsSlots.SqueezeCost(1, 2, 2f) - 2f) < 1e-5 && Math.Abs(WallsSlots.SqueezeCost(2, 3, 2f) - 1.6667f) < 1e-3
                  && Math.Abs(WallsSlots.SqueezeCost(3, 4, 2f) - 1.5f) < 1e-5 && Math.Abs(WallsSlots.SqueezeCost(5, 6, 2f) - 1.3333f) < 1e-3
                  && Math.Abs(WallsSlots.SqueezeCost(3, 6, 2f) - 2f) < 1e-5, "§4's squeeze table");
            // A run: legal only straight, no cell below half width, cost the sum.
            int n = r.Next(1, 8);
            var slots = new int[n];
            for (int i = 0; i < n; i++) slots[i] = r.Next(0, p + 1);
            float tpc = (float)(5 + r.NextDouble() * 40);
            float run = WallsSlots.SqueezeRunTicks(slots, p, k, tpc);
            bool legal = true;
            double sum = 0;
            foreach (int sl in slots)
            {
                if (!(sl >= p || (sl >= 1 && 2 * sl >= p))) legal = false;
                else sum += tpc * (sl >= p ? 1 : 1 + (kk - 1) * 2 * (1 - (double)sl / p));
            }
            Check(legal ? Math.Abs(run - sum) < 1e-2 * Math.Max(1, sum) : run < 0, "SqueezeRunTicks legal=" + legal + " got " + run + " want " + sum);
            // straightness
            int sx = r.Next(4), len = r.Next(1, 6);
            int[] dxs = { 1, -1, 0, 0 }, dzs = { 0, 0, 1, -1 };
            var xs = new int[len];
            var zs = new int[len];
            for (int i = 0; i < len; i++) { xs[i] = 5 + dxs[sx] * i; zs[i] = 5 + dzs[sx] * i; }
            bool bend = len >= 3 && r.Next(2) == 0;
            if (bend) { xs[len - 1] += dzs[sx]; zs[len - 1] += dxs[sx]; }
            Check(WallsSlots.StraightCardinal(xs, zs) == !bend, "StraightCardinal bend=" + bend);
            return band + ":" + c.ToString("0.000");
        }

        private static int Blows(float hp, float blow) => (int)Math.Ceiling(hp / blow - 1e-6);

        /// <summary>§3's table, row by row: (body size, B, lone wood, roofed wood, lone granite, roofed granite). A string is
        /// "through" or a blow count.</summary>
        private static readonly object[][] Table =
        {
            new object[] { 4f, 2, "through", 8, 13, 20 },
            new object[] { 12f, 3, "through", "through", 9, 13 },
            new object[] { 15f, 4, "through", "through", 7, 10 },
            new object[] { 25f, 5, "through", "through", 6, 8 },
            new object[] { 32f, 6, "through", "through", "through", 7 },
            new object[] { 100f, 10, "through", "through", "through", "through" },
        };

        internal static string CaseTable(int seed)
        {
            var row = Table[seed % Table.Length];
            float bs = (float)row[0];
            int b = (int)row[1];
            Check(WallsSlots.Breadth(bs, 0) == b, "§3: body size " + bs + " is B " + b + ", kernel says " + WallsSlots.Breadth(bs, 0));
            float[] hp = { Wood, Wood, Granite, Granite };
            bool[] roof = { false, true, false, true };
            for (int i = 0; i < 4; i++)
            {
                float counted = WallsSlots.CountedHp(hp[i], roof[i], 1.5f);
                var info = WallsSlots.Analyze(b, new[] { 10 }, new[] { 10 }, new[] { counted }, 0, 1, 10, 5);
                Check(info.Thickness == 1 && info.Layers == 1 && Math.Abs(info.HpSum - counted) < 1e-3, "a lone wall cell is one layer");
                CrossVerdict v = WallsSlots.Decide(b, info.Thickness, info.HpSum, false, true, 1f, 100f);
                object want = row[2 + i];
                if (want is string)
                {
                    Check(v == CrossVerdict.BreakThrough, "§3 B " + b + " cell " + i + ": want through, got " + v);
                    Throughs++;
                }
                else
                {
                    Check(v == CrossVerdict.Smash, "§3 B " + b + " cell " + i + ": want smash, got " + v);
                    int blows = Blows(hp[i], WallsSlots.BlowDamage(b, roof[i], 20f, 2f / 3f));
                    Check(blows == (int)want, "§3 B " + b + " cell " + i + ": " + blows + " blows, want " + want);
                    Smashes++;
                }
            }
            // holds at T >= B, any material; one less than B never holds.
            var xs = new List<int>();
            var zs = new List<int>();
            var hs = new List<float>();
            for (int d = 0; d < b; d++) { xs.Add(10); zs.Add(10 + d); hs.Add(Wood); }
            var deep = WallsSlots.Analyze(b, xs.ToArray(), zs.ToArray(), hs.ToArray(), 0, 1, 10, 5);
            Check(deep.Thickness == b && WallsSlots.Decide(b, deep.Thickness, deep.HpSum, false, true, 1f, 100f) == CrossVerdict.Hold,
                  "B " + b + " behind " + b + " solid wood cells is not held");
            Holds++;
            if (b > 1)
            {
                Check(WallsSlots.Decide(b, b - 1, 1e9f, false, true, 1f, 100f) == CrossVerdict.Smash, "T = B - 1 held");
            }
            // card 4: the thrumbo class breaks thin walls by default; off, it only squeezes (holds at every wall).
            if (b == 2) Check(WallsSlots.Decide(2, 1, Wood, false, false, 1f, 100f) == CrossVerdict.Hold, "B 2 breaking off still broke");
            return b.ToString();
        }

        internal static string CaseSandwich(int seed)
        {
            var r = new Random(seed);
            // §7 test 3: B 4, layers of wood at depths 0, 2, 4, the body 4 wide (lateral cells 0..3), approached straight (z) or
            // diagonally. Air layers in between.
            int b = 4;
            bool diagonal = r.Next(2) == 0;
            int ox = r.Next(-30, 30), oz = r.Next(-30, 30);
            var xs = new List<int>();
            var zs = new List<int>();
            var hs = new List<float>();
            foreach (int d in new[] { 0, 2, 4 })
                for (int w = 0; w < (diagonal ? 7 : 4); w++) { xs.Add(ox + w); zs.Add(oz + d); hs.Add(Wood); }
            int dx = diagonal ? 1 : 0, dz = 1;
            var info = WallsSlots.Analyze(b, xs.ToArray(), zs.ToArray(), hs.ToArray(), dx, dz, ox + 1, oz - 3);
            Check(info.Thickness == 2, "sandwich T = " + info.Thickness + " (axis " + info.Axis + "), want 2 (diagonal " + diagonal + ")");
            Check(Math.Abs(info.HpSum - 3 * Wood) < 1e-3, "sandwich HP " + info.HpSum + ", want 585");
            Check(info.Layers == 3, "sandwich layers " + info.Layers);
            Check(WallsSlots.Decide(b, info.Thickness, info.HpSum, false, true, 1f, 100f) == CrossVerdict.Smash, "the sandwich is not smashed");
            // layers numbered from the creature outward
            for (int i = 0; i < xs.Count; i++)
                Check(info.LayerOf[i] == (zs[i] - oz) / 2, "layer of depth " + (zs[i] - oz) + " is " + info.LayerOf[i]);
            // five solid wood layers hold
            var sx = new List<int>();
            var sz = new List<int>();
            var sh = new List<float>();
            for (int d = 0; d < 5; d++)
                for (int w = 0; w < 4; w++) { sx.Add(ox + w); sz.Add(oz + d); sh.Add(Wood); }
            var solid = WallsSlots.Analyze(b, sx.ToArray(), sz.ToArray(), sh.ToArray(), dx, dz, ox + 1, oz - 3);
            Check(solid.Thickness >= 4 && WallsSlots.Decide(b, solid.Thickness, solid.HpSum, false, true, 1f, 100f) == CrossVerdict.Hold,
                  "five solid wood layers are not held (T " + solid.Thickness + ")");
            // a corridor's flanks along the travel direction are never read as one thin layer
            var fx = new List<int>();
            var fz = new List<int>();
            var fh = new List<float>();
            for (int d = 0; d < 8; d++) { fx.Add(ox); fz.Add(oz + d); fh.Add(Wood); fx.Add(ox + 3); fz.Add(oz + d); fh.Add(Wood); }
            var flank = WallsSlots.Analyze(b, fx.ToArray(), fz.ToArray(), fh.ToArray(), 0, 1, ox + 1, oz - 3);
            Check(flank.Thickness >= b, "corridor flanks along travel measured thin (T " + flank.Thickness + ")");
            return info.Thickness + ":" + solid.Thickness + ":" + flank.Thickness;
        }

        internal static string CasePlug(int seed)
        {
            var r = new Random(seed);
            int b = r.Next(2, 9), t = r.Next(1, 12);
            float hp = (float)(r.NextDouble() * 2000);
            bool b2 = r.Next(2) == 0;
            CrossVerdict v = WallsSlots.Decide(b, t, hp, true, b2, 1f, 100f);
            // rock (or a protected building) on the route: never broken. It is held if thick enough, else forbidden; never a break.
            Check(!WallsSlots.Breaks(v), "a crossing through rock gave " + v);
            Check(v == (t >= b ? CrossVerdict.Hold : CrossVerdict.Forbidden), "rock verdict " + v);
            // the plug itself, without rock on the route, is judged as wood
            CrossVerdict w = WallsSlots.Decide(b, 1, Wood, false, true, 1f, 100f);
            Check(b >= 2 && w == (Wood <= 100f * b ? CrossVerdict.BreakThrough : CrossVerdict.Smash), "a wooden plug is not wood: " + w);
            return v.ToString();
        }

        internal static string CaseMonotone(int seed)
        {
            var r = new Random(seed);
            int b = r.Next(1, 12), t = r.Next(0, 14);
            float hp = (float)(r.NextDouble() * 3000);
            float hold = (float)(0.5 + r.NextDouble() * 1.5), budget = (float)(25 + r.NextDouble() * 375);
            bool rock = r.Next(4) == 0, b2 = r.Next(2) == 0;
            int Strength(CrossVerdict v) => v == CrossVerdict.Open ? 0 : v == CrossVerdict.BreakThrough ? 1 : v == CrossVerdict.Smash ? 2 : 3;
            CrossVerdict v0 = WallsSlots.Decide(b, t, hp, rock, b2, hold, budget);
            // bigger never weaker: a bigger creature never meets a stronger verdict (the B 2 switch only weakens B 2)
            CrossVerdict vb = WallsSlots.Decide(b + 1, t, hp, rock, b2, hold, budget);
            if (b >= 2) Check(Strength(vb) <= Strength(v0), "B " + b + " -> " + (b + 1) + ": " + v0 + " -> " + vb);
            // thicker never easier
            CrossVerdict vt = WallsSlots.Decide(b, t + 1, hp + (float)(r.NextDouble() * 500), rock, b2, hold, budget);
            Check(Strength(vt) >= Strength(v0) || v0 == CrossVerdict.Open, "T " + t + " -> " + (t + 1) + ": " + v0 + " -> " + vt);
            // roof never makes a wall weaker: counted HP and blow damage
            float h1 = (float)(r.NextDouble() * 1000), f = (float)(r.NextDouble() * 4), g = (float)(r.NextDouble() * 1.5);
            Check(WallsSlots.CountedHp(h1, true, f) >= WallsSlots.CountedHp(h1, false, f), "a roof lowered counted HP");
            Check(WallsSlots.BlowDamage(b, true, 20f, g) <= WallsSlots.BlowDamage(b, false, 20f, g), "a roof raised blow damage");
            Check(WallsSlots.BlowDamage(b + 1, false, 20f, g) >= WallsSlots.BlowDamage(b, false, 20f, g), "a bigger creature hits softer");
            // the hold line ignores roof and material: it is a function of T and B only
            Check((WallsSlots.Decide(b, t, 0f, false, true, hold, budget) == CrossVerdict.Hold) == (WallsSlots.Decide(b, t, 1e6f, false, true, hold, budget) == CrossVerdict.Hold),
                  "HP moved the hold line");
            // StopsUpTo is the inverse of the hold line
            int up = WallsSlots.StopsUpTo(t, hold);
            if (up >= 2) Check(WallsSlots.Decide(up, t, 1e6f, false, true, hold, budget) == CrossVerdict.Hold, "StopsUpTo " + up + " is not held");
            if (t > 0) Check(WallsSlots.Decide(up + 1, t, 1e6f, false, true, hold, budget) != CrossVerdict.Hold || up + 1 <= 1, "StopsUpTo understates");
            // roofed wall: half the near cells on one side (X4)
            int ta = r.Next(0, 11), ra = r.Next(0, ta + 1), tb = r.Next(0, 11), rb = r.Next(0, tb + 1);
            Check(WallsSlots.RoofedWall(ra, ta, rb, tb) == ((ta > 0 && 2 * ra >= ta) || (tb > 0 && 2 * rb >= tb)), "RoofedWall");
            Check(!WallsSlots.RoofedWall(1, 10, 0, 10), "one roofed corner cell counts as a roof (X4)");
            // the rule is sub-behaviour of clearing
            Check(WallsSlots.Active(true, true, true, true) && !WallsSlots.Active(false, true, true, true) && !WallsSlots.Active(true, false, true, true)
                  && !WallsSlots.Active(true, true, false, true) && !WallsSlots.Active(true, true, true, false), "Active is not the four-way AND");
            // scrape cadence
            int last = r.Next(-1, 500), now = r.Next(0, 600);
            Check(WallsSlots.ScrapeDue(last, now) == (last < 0 || now < last || now - last >= 60), "ScrapeDue");
            return v0 + ":" + vb + ":" + vt;
        }

        internal static string CaseRestless(int seed)
        {
            var r = new Random(seed);
            float x = (float)(r.NextDouble() * 1.4 - 0.2);
            if (r.Next(20) == 0) x = float.NaN;
            bool conf = r.Next(2) == 0, need = r.Next(2) == 0;
            int dt = r.Next(0, 70000);
            float y = WallsSlots.RestlessStep(x, conf, need, dt);
            Check(y >= 0f && y <= 1f, "restlessness left [0,1]: " + y);
            float x0 = float.IsNaN(x) ? 0f : Math.Max(0f, Math.Min(1f, x));
            if (conf || need) Check(y >= x0 - 1e-6, "restlessness fell with a cause");
            else Check(y <= x0 + 1e-6, "restlessness rose without a cause");
            if ((conf || need) && dt >= 60000 / ((conf ? 1 : 0) + (need ? 1 : 0))) Check(y >= 1f - 1e-5, "a full day's cause did not fill it");
            int cells = r.Next(0, 400), p = r.Next(1, 7);
            bool edge = r.Next(3) == 0;
            Check(WallsSlots.Confined(cells, edge, p) == (!edge && cells > 0 && cells < 6 * p * p), "Confined");
            bool temper = r.Next(4) != 0, flee = r.Next(5) == 0, mental = r.Next(5) == 0, hunt = r.Next(5) == 0;
            float rr = (float)r.NextDouble() * 1.2f;
            bool full = WallsSlots.FullRule(temper, rr, flee, mental, hunt);
            Check(full == (!temper || rr >= 1f || flee || mental || hunt), "FullRule");
            bool reach = r.Next(2) == 0;
            float by = (float)(r.NextDouble() * 6000), th = (float)(r.NextDouble() * 1500), fac = (float)(1.5 + r.NextDouble() * 4.5);
            bool may = WallsSlots.MayBreak(full, reach, by, th, fac);
            bool want = full ? (!reach || (by > fac * th && by - th >= 240f)) : (reach && by > 6f * th && by - th >= 240f);
            Check(may == want, "MayBreak(full " + full + ", reach " + reach + ") = " + may);
            if (!full && !reach) Check(!may, "a calm creature breaks out for an unreachable goal");
            return y.ToString("0.0000") + ":" + may;
        }

        internal static string CaseTrench(int seed)
        {
            var r = new Random(seed);
            int b = r.Next(1, 16), w = r.Next(-1, 6);
            bool s = WallsSlots.StepsOverTrench(b, w);
            Check(s == (w > 0 && 4 * w < b), "StepsOverTrench(" + b + "," + w + ") = " + s);
            Check(!WallsSlots.StepsOverTrench(4, 1) && WallsSlots.StepsOverTrench(5, 1) && !WallsSlots.StepsOverTrench(8, 2) && WallsSlots.StepsOverTrench(9, 2),
                  "card 3: strictly narrower than B/4");
            int widest = WallsSlots.WidestTrenchSteppedOver(b);
            Check(widest == 0 ? !WallsSlots.StepsOverTrench(b, 1) : WallsSlots.StepsOverTrench(b, widest) && !WallsSlots.StepsOverTrench(b, widest + 1),
                  "WidestTrenchSteppedOver(" + b + ") = " + widest + " disagrees with StepsOverTrench");
            Check(WallsSlots.WidestTrenchSteppedOver(4) == 0 && WallsSlots.WidestTrenchSteppedOver(5) == 1 && WallsSlots.WidestTrenchSteppedOver(8) == 1
                  && WallsSlots.WidestTrenchSteppedOver(9) == 2, "can-fail: the stride edges are B 5 and B 9");
            return (s ? "1" : "0") + widest;
        }

        private static bool Family(string name, int n, int? one, Func<int, string> run)
        {
            int fails = 0, ran = 0;
            for (int i = 0; i < n; i++)
            {
                int seed = one ?? (i * 7919 + name.Length * 104729);
                Cases++;
                ran++;
                try
                {
                    run(seed);
                }
                catch (Exception e)
                {
                    if (fails++ < 5) Console.WriteLine("FAIL " + name + " seed " + seed + ": " + e.Message);
                }
                if (one.HasValue) break;
            }
            Console.WriteLine((fails == 0 && ran > 0 ? "PASS " : "FAIL ") + name + ": " + ran + " cases, " + fails + " failed");
            return fails == 0 && ran > 0;
        }

        public static readonly string[] Families = { "breadth", "gap", "table", "sandwich", "plug", "monotone", "restless", "trench", "wallsdeterminism" };

        public static bool Run(double scale, int? one, string only)
        {
            int N(int baseN) => Math.Max(scale > 0 ? 1 : 0, (int)(baseN * scale));
            bool ok = true;
            if (only == null || only == "breadth") ok &= Family("breadth", N(6000), one, CaseBreadth);
            if (only == null || only == "gap") ok &= Family("gap", N(6000), one, CaseGap);
            if (only == null || only == "table") ok &= Family("table", N(60), one, CaseTable);
            if (only == null || only == "sandwich") ok &= Family("sandwich", N(2000), one, CaseSandwich);
            if (only == null || only == "plug") ok &= Family("plug", N(3000), one, CasePlug);
            if (only == null || only == "monotone") ok &= Family("monotone", N(8000), one, CaseMonotone);
            if (only == null || only == "restless") ok &= Family("restless", N(6000), one, CaseRestless);
            if (only == null || only == "trench") ok &= Family("trench", N(2000), one, CaseTrench);
            if (only == null || only == "wallsdeterminism")
                ok &= Family("wallsdeterminism", N(300), one, s =>
                {
                    Check(CaseBreadth(s) == CaseBreadth(s) && CaseGap(s) == CaseGap(s) && CaseSandwich(s) == CaseSandwich(s)
                          && CaseMonotone(s) == CaseMonotone(s) && CaseRestless(s) == CaseRestless(s), "a seed replayed differently");
                    return "";
                });
            if (only == null && !one.HasValue && scale >= 1 && (Throughs == 0 || Smashes == 0 || Holds == 0 || Squeezes == 0))
            {
                Console.WriteLine("FAIL walls-and-slots fuzz is blind: throughs " + Throughs + ", smashes " + Smashes + ", holds " + Holds + ", squeezes " + Squeezes);
                ok = false;
            }
            Console.WriteLine("walls and slots fuzz: " + Cases + " cases, " + Checks + " checks; through " + Throughs + ", smash " + Smashes
                              + ", hold " + Holds + ", squeeze " + Squeezes);
            return ok;
        }
    }
}
