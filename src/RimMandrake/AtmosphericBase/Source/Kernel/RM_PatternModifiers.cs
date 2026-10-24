// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 step 10 -- the phrase modifiers (design atmospheric_base_god_patterns_2026-10-24.md
// §1.2), kernel only.
//   M1 ECHO and M2 APPROACH are layer fields, applied by the evaluator around any primitive (RM_Modifiers below), so
//   they need no primitive of their own and every primitive's NextChange stays the source of truth.
//   M3 SCAR and M4 HUSH act on a fixture across moods and over time, so the compositor applies them; the rules live
//   here (RM_Scar, RM_Hush) so the selftest drives exactly what the compositor runs.
// Pure C#: no Verse, no Unity.
using System;
using System.Collections.Generic;

namespace RimMandrake.AtmosphericBase
{
    public enum RM_Withdraw { Slow, Fast }

    public static class RM_Modifiers
    {
        public const float EchoJitter = 0.2f;   // design M1: delay jitters +-20% per answering room

        public static bool Any(RM_Layer l) => l.echo > 0f || l.reach > 0;

        /// <summary>M1: how long after the caller this fixture's room replays the layer. 0 = the calling wing (rooms an
        /// even number of doors from the anchor, outdoors, and anything with no graph). Answering rooms sit an odd number
        /// of doors out; the wing nearest the caller answers first (distance 1 after one delay, 3 after two, ...).</summary>
        public static double EchoDelay(RM_Layer l, ref RM_PatternCtx c)
        {
            if (!(l.echo > 0f) || c.graph == null || c.node < 0 || c.node >= c.graph.Count) return 0;
            int d = c.graph.Distance(l.anchor, c.node);
            if (d >= RM_RoomGraph.Unreached || (d & 1) == 0) return 0;
            double jitter = 1.0 + EchoJitter * (2.0 * RM_SchemeKernel.Frac01(c.group, 23) - 1.0);
            return l.echo * jitter * ((d + 1) / 2);
        }

        // ---- M2 APPROACH: once every `approachEvery` s the front advances `reach` door hops at `speed` hops/s, holds
        // `pause` s, then withdraws (Slow: three times the advance; Fast: a third of it). A room is in the layer while the
        // front stands beyond it; outside, the layer is Pass (the layers below show).
        public static double AdvanceSeconds(RM_Layer l) => l.reach / (double)l.speed;
        public static double WithdrawSeconds(RM_Layer l) => AdvanceSeconds(l) * (l.withdraw == RM_Withdraw.Slow ? 3.0 : 1.0 / 3.0);

        /// <summary>The front's reach in hops at t (0..reach): the envelope the selftest checks.</summary>
        public static double Front(RM_Layer l, double t)
        {
            double e = l.approachEvery, u = t - Math.Floor(t / e) * e, a = AdvanceSeconds(l), w = WithdrawSeconds(l);
            if (u < a) return l.reach * u / a;
            if (u < a + l.pause) return l.reach;
            if (u < a + l.pause + w) return l.reach * (1.0 - (u - a - l.pause) / w);
            return 0;
        }

        /// <summary>The window, in cycle seconds, in which a room `d` hops out is inside the front: (enter, leave).</summary>
        private static bool Window(RM_Layer l, int d, out double enter, out double leave)
        {
            enter = leave = 0;
            if (d < 0 || d >= l.reach) return false;
            double a = AdvanceSeconds(l), w = WithdrawSeconds(l);
            enter = a * d / l.reach;
            leave = a + l.pause + w * (1.0 - d / (double)l.reach);
            return true;
        }

        private static int Hops(RM_Layer l, ref RM_PatternCtx c)
        {
            if (c.graph == null || c.graph.Count == 0) return 0;
            if (c.node < 0 || c.node >= c.graph.Count) return RM_RoomGraph.Unreached;
            return c.graph.Distance(l.anchor, c.node);
        }

        public static bool Inside(RM_Layer l, ref RM_PatternCtx c, double t)
        {
            if (l.reach <= 0) return true;
            if (!Window(l, Hops(l, ref c), out double enter, out double leave)) return false;
            double e = l.approachEvery, u = t - Math.Floor(t / e) * e;
            return u > enter && u < leave;
        }

        /// <summary>The next time after t the room enters or leaves the front (never later than the true change).</summary>
        private static double NextEdge(RM_Layer l, ref RM_PatternCtx c, double t)
        {
            if (!Window(l, Hops(l, ref c), out double enter, out double leave)) return RM_PatternKernel.Never;
            double e = l.approachEvery, k = Math.Floor(t / e), u = t - k * e;
            double next = u < enter ? enter : u < leave ? leave : e + enter;
            return RM_Front.Nudge(k * e + next, t);
        }

        public static int Index(RM_IPrimitive p, RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            if (!Inside(l, ref c, t)) return RM_PatternKernel.Pass;
            double d = EchoDelay(l, ref c);
            int x = p.Index(l, n, ref c, t - d);
            if (d > 0 && l.echoInvert && x != RM_PatternKernel.Pass) x = l.Lo(n) + l.Hi(n) - x;
            return x;
        }

        public static double NextChange(RM_IPrimitive p, RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            double edge = l.reach > 0 ? NextEdge(l, ref c, t) : RM_PatternKernel.Never;
            if (!Inside(l, ref c, t)) return edge;
            double d = EchoDelay(l, ref c);
            double x = p.NextChange(l, n, ref c, t - d);
            if (!double.IsPositiveInfinity(x)) x = Math.Max(x + d, t + 1e-9);
            return Math.Min(x, edge);
        }

        public static void Errors(RM_Layer l, int n, List<string> e)
        {
            if (l.echo < 0f || float.IsNaN(l.echo)) e.Add("echo must be >= 0 s (0 = no echo)");
            if (l.echoInvert && !(l.echo > 0f)) e.Add("echoInvert needs echo > 0");
            if (l.reach < 0) e.Add("reach must be >= 0 hops (0 = no approach)");
            if (l.reach > 0)
            {
                if (l.primitive != RM_Primitive.Tide && l.primitive != RM_Primitive.Ripple && l.primitive != RM_Primitive.Sweep
                    && l.primitive != RM_Primitive.Procession)
                    e.Add("reach (approach) shapes a front primitive only (Tide, Ripple, Sweep, Procession)");
                if (!(l.speed > 0f)) e.Add("approach needs speed > 0 hops/s");
                if (l.pause < 0f) e.Add("pause must be >= 0 s");
                else if (l.speed > 0f && AdvanceSeconds(l) + l.pause + WithdrawSeconds(l) > l.approachEvery)
                    e.Add("approach (advance + pause + withdraw) is longer than approachEvery");
            }
        }
    }

    /// <summary>M3 SCAR: a fixture that changed hands keeps the previous owner on its lowest entry for `linger` s.</summary>
    public static class RM_Scar
    {
        public const float MaxLinger = 30f;   // design M3: linger <= 30 s, except a scheme that keeps (Rekko, §2.5)

        public static float Linger(float linger, bool keeps) => linger <= 0f ? 0f : keeps ? linger : Math.Min(linger, MaxLinger);

        /// <summary>True when the fixture shows the previous owner now: within the linger, and the new owner's pattern sits
        /// on its lowest entry (so the old rhythm shows through the new one's low moments, never over its peaks).</summary>
        public static bool ShowsPrevious(int newIdx, int newLowest, double sinceFlip, float linger, bool keeps)
        {
            float lg = Linger(linger, keeps);
            return lg > 0f && sinceFlip >= 0 && sinceFlip < lg && newIdx == newLowest;
        }
    }

    /// <summary>M4 HUSH: one room's layers narrow to one held mid entry over `settle` s, hold, then recover over settle.
    /// Coloured and one room (never the Narrator's white ship-wide HOLD). A dark room keeps one ember (L8).</summary>
    public static class RM_Hush
    {
        /// <summary>0 = no hush, 1 = fully hushed. Rises over settle, holds, falls over settle.</summary>
        public static double Weight(double since, float settle, float hold)
        {
            if (since < 0) return 0;
            double s = Math.Max(1e-6, settle);
            if (since < s) return since / s;
            if (since < s + hold) return 1;
            if (since < 2 * s + hold) return 1 - (since - s - hold) / s;
            return 0;
        }

        public static bool Over(double since, float settle, float hold) => since >= 2.0 * Math.Max(1e-6, settle) + hold;

        /// <summary>The held entry: the palette's middle, or when that is black, the lowest lit entry (the ember).</summary>
        public static int Mid(RM_SchemeData d)
        {
            int n = d.Count;
            if (n == 0) return 0;
            int mid = (n - 1) / 2;
            if (d.r[mid] + d.g[mid] + d.b[mid] > 0) return mid;
            for (int i = 0; i < n; i++) if (d.r[i] + d.g[i] + d.b[i] > 0) return i;
            return 0;
        }

        /// <summary>Narrow idx toward the held entry by w; monotone in w (never overshoots, never turns back). In a dark
        /// hush (the held entry is the ember above a black entry 0), only the room's keeper holds the ember; the rest
        /// settle to black.</summary>
        public static int Apply(int idx, int held, double w, bool darkRoom, bool keeper)
        {
            int target = darkRoom && !keeper ? 0 : held;
            if (w <= 0) return idx;
            if (w >= 1) return target;
            return (int)Math.Round(idx + (target - idx) * w, MidpointRounding.AwayFromZero);
        }
    }
}
