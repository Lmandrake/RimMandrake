// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 pattern grammar: the front primitives over the step-4 graph substrate
// (design/RimMandrake/atmospheric_base_god_patterns_2026-10-24.md §1 P3 TIDE; P4 RIPPLE and P5 SWEEP join in step 6).
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
}
