// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 pattern grammar: the front primitives over the step-4 graph substrate
// (design/RimMandrake/atmospheric_base_god_patterns_2026-10-24.md §1 P3 TIDE, P4 RIPPLE, P5 SWEEP).
using System;
using System.Collections.Generic;

namespace RimMandrake.AtmosphericBase
{
    // ---------------------------------------------------------------- P3 TIDE (proposal A). Cost Front.
    // Every fixture gets a stable position u in the base: its room's door-distance shell from `anchor`, a per-room tie-break
    // inside the shell (equal-distance rooms never flip together) and `ragged` per-room jitter. A water level theta(t)
    // floods from the anchor outward and ebbs back once per period, standing for `hold` at each end. A fixture is lo while
    // the water is short of it and climbs to hi over the next `band` shells behind the front.
    // Hysteresis is structural: theta is monotone within each half, so a fixture crosses each level exactly once on the
    // flood and once on the ebb -- it can never chatter at the front, and a turn of the tide flips nothing by itself.
    // With one room (or no graph) the shell is the whole base and the tie-break is the fixture's angle about the
    // fixtures' centroid, so the tide degenerates to a sweep round the room (the design's "TIDE degenerates to WEDGE").
    public sealed class RM_TidePrimitive : RM_IPrimitive
    {
        public const float MinPeriod = 240f;

        public RM_CostClass Cost(RM_Layer l) => RM_CostClass.Front;

        /// <summary>The fixture's place on the tide's axis, in about [-ragged/2, 1 + ragged/2].</summary>
        public static double Position(RM_Layer l, ref RM_PatternCtx c)
        {
            RM_RoomGraph g = c.graph;
            double jit = l.ragged * (RM_SchemeKernel.Frac01(c.node >= 0 && g != null ? g.roomIds[c.node] : c.emitter, 8) - 0.5);
            if (g == null || g.Count <= 1 || g.MaxDistance(l.anchor) == 0)
            {
                double tie;
                RM_FixtureSet f = c.fixtures;
                if (f != null && c.slot >= 0 && f.Count > 1)
                {
                    double a = Math.Atan2(f.z[c.slot] - f.cz, f.x[c.slot] - f.cx) / (2 * Math.PI);
                    tie = a < 0 ? a + 1 : a;
                }
                else tie = RM_SchemeKernel.Frac01(c.emitter, 7);
                jit = l.ragged * (RM_SchemeKernel.Frac01(c.emitter, 8) - 0.5);
                return 0.05 + 0.9 * tie + jit;
            }
            int shells = g.MaxDistance(l.anchor) + 2;          // the rooms' shells plus one for outdoors
            int d = g.Distance(l.anchor, c.node);
            double t = RM_SchemeKernel.Frac01(c.node >= 0 ? g.roomIds[c.node] : c.emitter, 7);
            return (d + 0.15 + 0.7 * t) / shells + jit;
        }

        private static int Shells(RM_Layer l, ref RM_PatternCtx c)
        {
            RM_RoomGraph g = c.graph;
            return g == null || g.Count <= 1 || g.MaxDistance(l.anchor) == 0 ? 1 : g.MaxDistance(l.anchor) + 2;
        }

        /// <summary>The water's span: from short of every position to past every position plus the band, so full ebb is
        /// lo everywhere and full flood is hi everywhere; low / high cut it.</summary>
        private static void Range(RM_Layer l, ref RM_PatternCtx c, out double a, out double b)
        {
            double lo = -l.ragged / 2.0 - 0.01, hi = 1.0 + l.ragged / 2.0 + 0.01 + l.band / Shells(l, ref c);
            a = lo + l.low * (hi - lo);
            b = lo + l.high * (hi - lo);
        }

        /// <summary>The water level at t: flood over (0.5 - hold) of the period on a half-cosine, stand, ebb, stand.</summary>
        public static double Theta(RM_Layer l, ref RM_PatternCtx c, double t)
        {
            Range(l, ref c, out double a, out double b);
            double x = t / l.period; x -= Math.Floor(x);
            double f = 0.5 - l.hold;
            double q;
            if (x < f) q = 0.5 - 0.5 * Math.Cos(Math.PI * x / f);
            else if (x < 0.5) q = 1;
            else if (x < 0.5 + f) q = 0.5 + 0.5 * Math.Cos(Math.PI * (x - 0.5) / f);
            else q = 0;
            return a + (b - a) * q;
        }

        /// <summary>Band width per entry step, in position units.</summary>
        private static double Step(RM_Layer l, ref RM_PatternCtx c, int k)
        {
            if (k <= 1) return 0;
            return l.band / Shells(l, ref c) / (k - 1);
        }

        public int Index(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            int lo = l.Lo(n), k = l.Hi(n) - lo;
            if (k <= 0) return lo;
            double u = Position(l, ref c), th = Theta(l, ref c, t);
            if (th <= u) return lo;
            if (k == 1) return lo + 1;
            double w = Step(l, ref c, k);
            return lo + (int)Math.Min(k, 1 + Math.Floor((th - u) / w));
        }

        public double NextChange(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            int lo = l.Lo(n), k = l.Hi(n) - lo;
            if (k <= 0) return RM_PatternKernel.Never;
            Range(l, ref c, out double a, out double b);
            if (!(b > a)) return RM_PatternKernel.Never;
            double u = Position(l, ref c), w = Step(l, ref c, k), P = l.period, f = 0.5 - l.hold;
            double c0 = Math.Floor(t / P) * P, best = RM_PatternKernel.Never;
            for (int j = 0; j < k; j++)
            {
                double lev = u + j * w;
                if (!(lev > a && lev < b)) continue;              // a level the water never reaches or never leaves
                double q = (lev - a) / (b - a);
                double xf = f * Math.Acos(1 - 2 * q) / Math.PI;   // flood crosses upward
                double xe = 0.5 + f * Math.Acos(2 * q - 1) / Math.PI;  // ebb crosses downward
                for (int cyc = 0; cyc < 2; cyc++)
                {
                    double tf = c0 + cyc * P + xf * P, te = c0 + cyc * P + xe * P;
                    if (tf > t && tf < best) best = tf;
                    if (te > t && te < best) best = te;
                }
            }
            if (double.IsInfinity(best)) return best;
            double eps = Math.Max(1e-9, Math.Abs(best) * 1e-12);
            return Math.Max(best - eps, t + Math.Max(1e-9, Math.Abs(t) * 1e-15));
        }

        public void Errors(RM_Layer l, int n, List<string> e)
        {
            if (!(l.period >= MinPeriod)) e.Add("a tide's period must be at least " + MinPeriod + " s (it is a slow front, §1 P3)");
            if (l.ragged < 0f || l.ragged > 0.2f) e.Add("ragged must lie in 0-0.2");
            if (!(l.band > 0f)) e.Add("band must be > 0");
            if (l.hold < 0f || l.hold > 0.4f) e.Add("hold must lie in 0-0.4");
            if (l.low < 0f || l.high > 1f || !(l.low < l.high)) e.Add("low and high must satisfy 0 <= low < high <= 1");
            if (!Enum.IsDefined(typeof(RM_Anchor), l.anchor)) e.Add("anchor is not a known anchor");
        }
    }
    /// <summary>Shared by the fronts: a rise-and-fall over m entries as len = 2m-1 slots (lo..hi..lo), as Spark does.</summary>
    internal static class RM_Front
    {
        public static int Tri(int m, int k) { int len = 2 * m - 1; return k < m ? k : len - 1 - k; }

        public static double Nudge(double next, double t)
        {
            if (double.IsInfinity(next)) return next;
            double eps = Math.Max(1e-9, Math.Abs(next) * 1e-12);
            return Math.Max(next - eps, t + Math.Max(1e-9, Math.Abs(t) * 1e-15));
        }

        /// <summary>Angle of fixture slot about the set's centroid, 0-1; or a stable hash when there is no set.</summary>
        public static double Angle01(ref RM_PatternCtx c, int salt)
        {
            RM_FixtureSet f = c.fixtures;
            if (f == null || c.slot < 0 || f.Count < 2) return RM_SchemeKernel.Frac01(c.emitter, salt);
            double a = Math.Atan2(f.z[c.slot] - f.cz, f.x[c.slot] - f.cx) / (2 * Math.PI);
            return a < 0 ? a + 1 : a;
        }
    }

    // ---------------------------------------------------------------- P4 RIPPLE. Cost Front.
    // A ring out from (or in to) a seed by door-distance: Shell = a thin ring rising and falling as it passes (a landfall),
    // Bloom = the lit area grows to the whole base, stands holdSeconds, recedes. Once per period, or once at t = 0.
    // Rooms ripple as units (graph distance, the design's property: monotone in graph distance).
    public sealed class RM_RipplePrimitive : RM_IPrimitive
    {
        public RM_CostClass Cost(RM_Layer l) => RM_CostClass.Front;

        /// <summary>The fixture's distance r from the seed and the reach rmax (one past the farthest room).</summary>
        public static void Distances(RM_Layer l, ref RM_PatternCtx c, out double r, out double rmax)
        {
            RM_RoomGraph g = c.graph;
            r = 0; rmax = 0;
            if (g == null || g.Count == 0) return;
            bool done = false;
            if (l.seed == RM_Seed.Fixture && c.fixtures != null)
            {
                int ss = c.fixtures.SeedSlot();
                int sn = ss >= 0 ? g.Node(c.fixtures.room[ss]) : -1;
                if (sn >= 0)
                {
                    int[] f = g.FieldFrom(sn);
                    rmax = f[g.Count] + 1;
                    r = c.node >= 0 && f[c.node] != RM_RoomGraph.Unreached ? f[c.node] : rmax;
                    done = true;
                }
            }
            if (!done)
            {
                RM_Anchor a = l.seed == RM_Seed.Hull ? RM_Anchor.Threshold : l.anchor;
                rmax = g.MaxDistance(a) + 1;
                r = g.Distance(a, c.node);
            }
            if (l.direction == RM_Direction.In) r = rmax - r;
        }

        private static double Grow(RM_Layer l, double rmax) => (rmax + l.width) / l.speed;

        /// <summary>The front's reach at tau into the cycle (Shell: the ring's leading edge; Bloom: the lit radius).</summary>
        private static double Reach(RM_Layer l, double rmax, double tau)
        {
            if (l.fill == RM_Fill.Shell) return l.speed * tau;
            double tg = Grow(l, rmax), h = l.holdSeconds;
            if (tau < tg) return l.speed * tau;
            if (tau < tg + h) return rmax + l.width;
            if (tau < 2 * tg + h) return rmax + l.width - l.speed * (tau - tg - h);
            return 0;
        }

        private static int At(RM_Layer l, int lo, int k, double r, double rmax, double tau)
        {
            double L = Reach(l, rmax, tau);
            if (l.fill == RM_Fill.Shell)
            {
                int m = k + 1, len = 2 * m - 1;
                double u = (L - r) / l.width * len;
                if (u < 0 || u >= len) return lo;
                return lo + RM_Front.Tri(m, (int)Math.Floor(u));
            }
            if (L <= r) return lo;
            return lo + (int)Math.Min(k, 1 + Math.Floor((L - r) / (l.width / k)));
        }

        /// <summary>Every tau within one cycle at which the index can change, ascending.</summary>
        private static List<double> Crossings(RM_Layer l, int k, double r, double rmax)
        {
            var x = new List<double>();
            if (l.fill == RM_Fill.Shell)
            {
                int len = 2 * (k + 1) - 1;
                for (int j = 1; j < len; j++) x.Add((r + j * l.width / len) / l.speed);
            }
            else
            {
                double tg = Grow(l, rmax), w = l.width / k;
                for (int j = 0; j < k; j++)
                {
                    double lev = r + j * w;
                    x.Add(lev / l.speed);
                    x.Add(tg + l.holdSeconds + (rmax + l.width - lev) / l.speed);
                }
                x.Sort();
            }
            return x;
        }

        private static double Tau(RM_Layer l, double t, out double cycleStart)
        {
            if (l.oneShot) { cycleStart = 0; return t; }
            cycleStart = Math.Floor(t / l.period) * l.period;
            return t - cycleStart;
        }

        public int Index(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            int lo = l.Lo(n), k = l.Hi(n) - lo;
            if (k <= 0) return lo;
            if (l.oneShot && t < 0) return lo;
            Distances(l, ref c, out double r, out double rmax);
            return At(l, lo, k, r, rmax, Tau(l, t, out _));
        }

        public double NextChange(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            int lo = l.Lo(n), k = l.Hi(n) - lo;
            if (k <= 0) return RM_PatternKernel.Never;
            Distances(l, ref c, out double r, out double rmax);
            if (l.oneShot && t < 0) t = 0;
            double tau = Tau(l, t, out double c0);
            double cap = l.oneShot ? double.PositiveInfinity : l.period;
            List<double> xs = Crossings(l, k, r, rmax);
            foreach (double x in xs)
                if (x > tau && x < cap) return RM_Front.Nudge(c0 + x, t);
            if (l.oneShot) return RM_PatternKernel.Never;
            double end = c0 + l.period;
            if (At(l, lo, k, r, rmax, tau) != lo) return RM_Front.Nudge(end, t);   // a wave cut off by the next cycle
            foreach (double x in xs) if (x < l.period) return RM_Front.Nudge(end + x, t);
            return RM_PatternKernel.Never;
        }

        public void Errors(RM_Layer l, int n, List<string> e)
        {
            if (!(l.speed > 0f)) e.Add("speed must be > 0 hops/s");
            if (!(l.width > 0f)) e.Add("width must be > 0 hops");
            if (l.holdSeconds < 0f) e.Add("holdSeconds must be >= 0");
            if (!l.oneShot && !(l.period > 0f)) e.Add("period must be > 0 (or set oneShot)");
        }
    }

    // ---------------------------------------------------------------- P5 SWEEP. Cost Front.
    // A wave along a direction field, one pass per period: Axis (a projection of the fixtures' positions at `angle`:
    // ash falling), Turn (the angle about the fixtures' centroid: a lighthouse beam) or Toward (from the deepest room out
    // through the doors to outdoors: every wave runs outward, never back). A fixture spends `lit` of the period in the
    // wave, rising lo..hi..lo.
    // pauseChance/pause: a pass (period + pause s of wall time) stops at a hashed point and holds `pause` s with that
    // chance; a pass that does not stop runs evenly over the same wall time, so the passes never drift. accelerate
    // (-1..1) warps each pass monotonically: w(x) = x + a x (x - 1), slow start and fast finish when a > 0.
    public sealed class RM_SweepPrimitive : RM_IPrimitive
    {
        public RM_CostClass Cost(RM_Layer l) => RM_CostClass.Front;

        /// <summary>Where along the field the fixture sits, 0-1 (the wave reaches 0 first).</summary>
        public static double Along(RM_Layer l, ref RM_PatternCtx c)
        {
            switch (l.field)
            {
                case RM_SweepField.Turn:
                    return RM_Front.Angle01(ref c, 12);
                case RM_SweepField.Toward:
                {
                    RM_RoomGraph g = c.graph;
                    if (g == null || g.Count == 0) return RM_SchemeKernel.Frac01(c.emitter, 12);
                    int dm = g.MaxDistance(RM_Anchor.Threshold);
                    if (c.node < 0 || c.node >= g.Count) return (dm + 1.0) / (dm + 2.0);
                    // a room no threshold room reaches (an island) has no depth: it is lit last, after outdoors, every
                    // time -- never ahead of the deepest reachable room (review R1)
                    if (g.Field(RM_Anchor.Threshold)[c.node] == RM_RoomGraph.Unreached) return (dm + 1.5) / (dm + 2.0);
                    return (dm - g.Distance(RM_Anchor.Threshold, c.node)) / (dm + 2.0);
                }
                default:
                {
                    RM_FixtureSet f = c.fixtures;
                    if (f == null || c.slot < 0 || f.Count < 2) return RM_SchemeKernel.Frac01(c.emitter, 12);
                    KeyValuePair<float, float> e = f.Extent(l.angle);
                    double span = e.Value - e.Key;
                    return span > 1e-6 ? 0.999 * (f.Project(c.slot, l.angle) - e.Key) / span : 0;
                }
            }
        }

        private static bool Warped(RM_Layer l) => l.pauseChance > 0f || l.accelerate != 0f;
        private static double Cycle(RM_Layer l) => l.period + (l.pauseChance > 0f ? Math.Max(0f, l.pause) : 0f);

        /// <summary>Does pass k stop, and where (0.15-0.85 of the pass, in front seconds)?</summary>
        private static bool Stops(RM_Layer l, long k, out double at)
        {
            at = l.period * (0.15 + 0.7 * RM_SchemeKernel.Frac01((int)(k & 0x7fffffff), 41));
            return l.pauseChance > 0f && RM_SchemeKernel.Frac01((int)(k & 0x7fffffff), 43) < l.pauseChance;
        }

        private static double Warp(double x, double a) => x + a * x * (x - 1);

        private static double Unwarp(double w, double a)
        {
            if (Math.Abs(a) < 1e-9) return w;
            double b = 1 - a, disc = b * b + 4 * a * w;
            return Math.Min(1, Math.Max(0, (-b + Math.Sqrt(Math.Max(0, disc))) / (2 * a)));
        }

        /// <summary>The wave's position at wall time t, in passes (non-decreasing; = t / period when not warped).</summary>
        public static double Passes(RM_Layer l, double t)
        {
            if (!Warped(l)) return t / l.period;
            double cyc = Cycle(l), k = Math.Floor(t / cyc), s = t - k * cyc, tau;
            if (Stops(l, (long)k, out double at)) tau = s < at ? s : s < at + l.pause ? at : s - l.pause;
            else tau = s * l.period / cyc;
            return k + Warp(Math.Min(1, tau / l.period), l.accelerate);
        }

        /// <summary>The earliest wall time at which Passes reaches p.</summary>
        public static double TimeOf(RM_Layer l, double p)
        {
            if (!Warped(l)) return p * l.period;
            double k = Math.Floor(p), cyc = Cycle(l);
            double tau = Unwarp(p - k, l.accelerate) * l.period;
            double s = Stops(l, (long)k, out double at) ? (tau <= at + 1e-9 ? Math.Min(tau, at) : tau + l.pause) : tau * cyc / l.period;
            return k * cyc + s;
        }

        private static double U(RM_Layer l, ref RM_PatternCtx c, double t, int len)
        {
            double phi = Passes(l, t) - Along(l, ref c);
            phi -= Math.Floor(phi);
            return phi / l.lit * len;
        }

        public int Index(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            int lo = l.Lo(n), m = l.Hi(n) - lo + 1;
            if (m <= 1) return lo;
            int len = 2 * m - 1;
            double u = U(l, ref c, t, len);
            return u >= len ? lo : lo + RM_Front.Tri(m, (int)Math.Floor(u));
        }

        public double NextChange(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            int lo = l.Lo(n), m = l.Hi(n) - lo + 1;
            if (m <= 1) return RM_PatternKernel.Never;
            int len = 2 * m - 1;
            // in double: float lit * period lost ~1e-7 per unit, and a dark gap of ~150 units (lit 0.02) put the
            // predicted rise micro-seconds early (review R1, found by the island test)
            if (Warped(l))
            {
                // u to the next unit boundary, in passes, then through the (monotone) warp back to wall time
                double uu = U(l, ref c, t, len), lt = l.lit, uc = len / lt;
                double target = uu < 1 ? 1 : uu < len - 1 ? Math.Floor(uu) + 1 : uc + 1;
                double tw = TimeOf(l, Passes(l, t) + (target - uu) * lt / len);
                return Math.Max(tw - Math.Max(1e-9, Math.Abs(tw) * 1e-12), t + 1e-9);
            }
            double lit = l.lit, u = U(l, ref c, t, len), unit = lit * l.period / len, ucycle = len / lit;
            if (u < 1) return RM_Front.Nudge(t + (1 - u) * unit, t);
            if (u < len - 1) return RM_PatternEvaluator.NextStep(u, unit, t);
            return RM_Front.Nudge(t + (ucycle - u + 1) * unit, t);
        }

        public void Errors(RM_Layer l, int n, List<string> e)
        {
            if (!(l.period > 0f)) e.Add("period must be > 0");
            if (!(l.lit > 0f) || l.lit > 1f) e.Add("lit must lie in (0, 1]");
            if (float.IsNaN(l.angle) || float.IsInfinity(l.angle)) e.Add("angle must be a number of degrees");
            if (!(l.pauseChance >= 0f && l.pauseChance <= 1f)) e.Add("pauseChance must lie in 0-1");
            if (l.pauseChance > 0f && !(l.pause > 0f)) e.Add("pauseChance needs pause > 0 s");
            if (!(l.accelerate >= -1f && l.accelerate <= 1f)) e.Add("accelerate must lie in -1..1 (beyond, the wave would run back)");
        }
    }
}
