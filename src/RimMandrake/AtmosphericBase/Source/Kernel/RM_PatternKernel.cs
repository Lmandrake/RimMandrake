// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 pattern grammar -- design/RimMandrake/atmospheric_base_god_patterns_2026-10-24.md §1, §4.
//
// A pattern is a stack of LAYERS. Each layer is one PRIMITIVE with params and a slice of the palette (entries lo~hi); it
// returns a palette INDEX or Pass (-1), never a colour (L4). Layers combine bottom-up by Over (a non-pass layer replaces
// what is below) or Max (the higher index wins: flaring crossings). Rule (§4): a new pattern is XML; only a new
// primitive is C#. The closed vocabulary lives here; a C# mod may add one through RM_Primitives.Register.
//
// Every primitive implements Index (pure in (layer, ctx, t), like the old PaletteIndex) and NextChange (the earliest
// time after t at which Index MAY change: never later than the true change, so the update-on-change engine B can
// sleep until then; +Infinity = never). The evaluator below is the clean seam B replaces the 10 Hz inner loop behind.
// No game types: the selftest drives every function here directly.
using System;
using System.Collections.Generic;
using System.Globalization;

namespace RimMandrake.AtmosphericBase
{
    public enum RM_Primitive { Steady = 0, Breath, Spark, Tide, Ripple, Sweep, Procession, Coil, Tell, Count }
    public enum RM_Combine { Over = 0, Max }
    public enum RM_Seed { Anchor = 0, Fixture, Hull }
    public enum RM_Direction { Out = 0, In }
    public enum RM_Fill { Shell = 0, Bloom }
    public enum RM_SweepField { Axis = 0, Turn, Toward }
    public enum RM_Scope { Room = 0, Field, Fixture }
    /// <summary>§1 cost classes under engine B: Still (no events at steady state), Light, Front, Heavy, Drawn.</summary>
    public enum RM_CostClass { Still = 0, Light, Front, Heavy, Drawn }

    /// <summary>One layer as authored in XML (a &lt;layers&gt; &lt;li&gt;). Plain public fields so RimWorld's loader and the
    /// selftest's reflection loader fill it the same way. Unused params are ignored by primitives that do not read them.</summary>
    public class RM_Layer
    {
        public RM_Primitive primitive = RM_Primitive.Steady;
        public RM_Combine combine = RM_Combine.Over;
        public string entries;              // "lo~hi" or "k"; null = the whole palette
        public float period = 120f;         // Breath: one up-and-back. Spark: the slot. Tide/Ripple/Sweep: one cycle.
        public RM_Scope scope = RM_Scope.Room;
        public float phaseSpread = 1f;      // Breath: 0 = all units in sync, 1 = phases spread over the whole cycle
        public float rise = 2f;             // Spark: one rise-and-fall, seconds
        public int oneIn = 2;               // Spark: a fixture sparks in 1 of this many slots
        public RM_Anchor anchor = RM_Anchor.Core;   // Tide: the room the flood starts from (step-4 anchors)
        public float ragged = 0.04f;        // Tide: per-room jitter of the front, 0-0.2 of the base's reach
        public float band = 1f;             // Tide: rooms (door hops) between the front's first step and its full entry
        public float hold = 0.1f;           // Tide: fraction of the period the water stands at full flood and at full ebb
        public float low = 0f, high = 1f;   // Tide: how far the ebb and the flood reach, 0-1 of the base
        public RM_Seed seed = RM_Seed.Anchor;       // Ripple: where the ring starts (Anchor uses `anchor`; Hull = the rim)
        public RM_Direction direction = RM_Direction.Out;   // Ripple: out from the seed, or in to it
        public RM_Fill fill = RM_Fill.Shell;        // Ripple: a thin ring, or an area that grows, holds and recedes
        public float speed = 0.5f;          // Ripple: door hops per second
        public float width = 1f;            // Ripple: the ring's (or the bloom edge's) thickness in hops
        public float holdSeconds = 4f;      // Ripple bloom: how long the full bloom stands
        public bool oneShot;                // Ripple: one wave at t = 0 (the pattern's start), never repeated
        public RM_SweepField field = RM_SweepField.Axis;    // Sweep: what the wave runs along
        public float angle = 270f;          // Sweep axis: the direction the wave travels, degrees (270 = falling, -z)
        public float lit = 0.25f;           // Sweep: the fraction of the period a fixture spends in the wave

        [NonSerialized] private int lo = -2, hi = -2;

        public int Lo(int n) { Resolve(n); return lo; }
        public int Hi(int n) { Resolve(n); return hi; }

        private void Resolve(int n)
        {
            if (lo != -2) return;
            if (!RM_PatternKernel.TryParseEntries(entries, n, out lo, out hi)) { lo = 0; hi = Math.Max(0, n - 1); }
        }

        /// <summary>Forget the resolved entries (a palette size changed under it; tests only).</summary>
        public void Reset() { lo = hi = -2; }
    }

    /// <summary>What a primitive may know about one fixture at one evaluation. group = its room id (-1 = none).
    /// graph / node / fixtures / slot are the step-4 substrate (null / -1 when the caller has none: the room-local
    /// primitives never read them, and a graph primitive with no graph treats every fixture as one room).</summary>
    public struct RM_PatternCtx
    {
        public int emitter;
        public int group;
        public RM_RoomGraph graph;
        public int node;
        public RM_FixtureSet fixtures;
        public int slot;

        public static RM_PatternCtx Of(int emitter, int group, RM_RoomGraph graph, RM_FixtureSet fixtures)
        {
            return new RM_PatternCtx
            {
                emitter = emitter, group = group, graph = graph,
                node = graph != null ? graph.Node(group) : -1,
                fixtures = fixtures, slot = fixtures != null ? fixtures.Slot(emitter) : -1,
            };
        }
    }

    public interface RM_IPrimitive
    {
        RM_CostClass Cost(RM_Layer l);
        /// <summary>A palette index in [0, n), or RM_PatternKernel.Pass.</summary>
        int Index(RM_Layer l, int n, ref RM_PatternCtx c, double t);
        /// <summary>Earliest t' &gt; t at which Index may change; never later than the true change.</summary>
        double NextChange(RM_Layer l, int n, ref RM_PatternCtx c, double t);
        void Errors(RM_Layer l, int n, List<string> e);
    }

    public static class RM_Primitives
    {
        private static readonly Dictionary<RM_Primitive, RM_IPrimitive> table = new Dictionary<RM_Primitive, RM_IPrimitive>
        {
            { RM_Primitive.Steady, new RM_SteadyPrimitive() },
            { RM_Primitive.Breath, new RM_BreathPrimitive() },
            { RM_Primitive.Spark, new RM_SparkPrimitive() },
            { RM_Primitive.Tide, new RM_TidePrimitive() },
            { RM_Primitive.Ripple, new RM_RipplePrimitive() },
            { RM_Primitive.Sweep, new RM_SweepPrimitive() },
        };

        public static RM_IPrimitive Get(RM_Primitive p) => table.TryGetValue(p, out RM_IPrimitive x) ? x : null;
        public static bool Built(RM_Primitive p) => table.ContainsKey(p);
        /// <summary>The workerClass-style door (§4): a C# mod supplies or replaces one primitive's implementation.</summary>
        public static void Register(RM_Primitive p, RM_IPrimitive impl) { if (impl != null) table[p] = impl; }
    }

    public static class RM_PatternKernel
    {
        public const int Pass = -1;
        public const double Never = double.PositiveInfinity;

        public static bool TryParseEntries(string s, int n, out int lo, out int hi)
        {
            lo = 0; hi = Math.Max(0, n - 1);
            if (string.IsNullOrEmpty(s)) return true;
            string[] p = s.Split('~');
            if (p.Length > 2) return false;
            if (!int.TryParse(p[0].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out lo)) return false;
            hi = lo;
            if (p.Length == 2 && !int.TryParse(p[1].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out hi)) return false;
            return true;
        }

        /// <summary>The old one-pattern scheme as one layer (§4 backward compatibility): bit-identical by construction.</summary>
        public static RM_Layer[] LegacyLayers(RM_SchemeData s)
        {
            switch (s.pattern)
            {
                case RM_PatternKind.RoomBreath:
                    return new[] { new RM_Layer { primitive = RM_Primitive.Breath, scope = RM_Scope.Room, phaseSpread = 1f, period = s.massPeriodSeconds } };
                case RM_PatternKind.Sparks:
                    return new[] { new RM_Layer { primitive = RM_Primitive.Spark, period = s.massPeriodSeconds, rise = s.sparkSeconds, oneIn = s.sparkOneIn } };
                default:
                    return new[] { new RM_Layer { primitive = RM_Primitive.Steady, entries = "0" } };
            }
        }

        public static void LayerErrors(RM_Layer[] layers, int n, List<string> e)
        {
            if (layers == null || layers.Length == 0) { e.Add("a scheme needs at least one layer"); return; }
            for (int i = 0; i < layers.Length; i++)
            {
                RM_Layer l = layers[i];
                string at = "layers[" + i + "] (" + (l == null ? "null" : l.primitive.ToString()) + "): ";
                if (l == null) { e.Add(at + "is empty"); continue; }
                RM_IPrimitive p = RM_Primitives.Get(l.primitive);
                if (p == null) { e.Add(at + "primitive " + l.primitive + " is not built yet"); continue; }
                if (!TryParseEntries(l.entries, n, out int lo, out int hi)) e.Add(at + "entries '" + l.entries + "' is not 'lo~hi' or 'k'");
                else if (lo < 0 || hi >= n || lo > hi) e.Add(at + "entries " + lo + "~" + hi + " fall outside the palette 0~" + (n - 1));
                if (!Enum.IsDefined(typeof(RM_Combine), l.combine)) e.Add(at + "combine is not Over or Max");
                var pe = new List<string>();
                p.Errors(l, n, pe);
                foreach (string x in pe) e.Add(at + x);
            }
        }

        /// <summary>True when some layer moves (L8: a chosen dark must carry motion).</summary>
        public static bool AnyMotion(RM_Layer[] layers)
        {
            if (layers == null) return false;
            foreach (RM_Layer l in layers) if (l != null && l.primitive != RM_Primitive.Steady) return true;
            return false;
        }

        public static RM_CostClass Cost(RM_Layer[] layers)
        {
            RM_CostClass c = RM_CostClass.Still;
            if (layers == null) return c;
            foreach (RM_Layer l in layers)
            {
                RM_IPrimitive p = l == null ? null : RM_Primitives.Get(l.primitive);
                if (p != null && p.Cost(l) > c) c = p.Cost(l);
            }
            return c;
        }
    }

    /// <summary>The evaluator: (scheme, fixture, time) -> palette index. The 10 Hz loop calls Index; engine B calls
    /// NextChange and sleeps until then. Both read only the scheme and the ctx.</summary>
    public static class RM_PatternEvaluator
    {
        public static int Index(RM_SchemeData s, ref RM_PatternCtx c, double t, bool flasher)
        {
            int n = s.Count;
            if (n <= 1) return 0;
            if (flasher) return FlasherIndex(s, c.emitter, t);
            RM_Layer[] layers = s.layers ?? RM_PatternKernel.LegacyLayers(s);
            int v = RM_PatternKernel.Pass;
            foreach (RM_Layer l in layers)
            {
                RM_IPrimitive p = l == null ? null : RM_Primitives.Get(l.primitive);
                if (p == null) continue;
                int x = p.Index(l, n, ref c, t);
                if (x == RM_PatternKernel.Pass) continue;
                v = (l.combine == RM_Combine.Max && v != RM_PatternKernel.Pass) ? Math.Max(v, x) : x;
            }
            return v == RM_PatternKernel.Pass ? 0 : v;
        }

        public static double NextChange(RM_SchemeData s, ref RM_PatternCtx c, double t, bool flasher)
        {
            int n = s.Count;
            if (n <= 1) return RM_PatternKernel.Never;
            if (flasher)
            {
                double fp = s.flasherPeriodSeconds;
                double u = t / fp + RM_SchemeKernel.Frac01(c.emitter, 3) * n;
                return NextStep(u, fp, t);
            }
            RM_Layer[] layers = s.layers ?? RM_PatternKernel.LegacyLayers(s);
            double best = RM_PatternKernel.Never;
            foreach (RM_Layer l in layers)
            {
                RM_IPrimitive p = l == null ? null : RM_Primitives.Get(l.primitive);
                if (p == null) continue;
                double x = p.NextChange(l, n, ref c, t);
                if (x < best) best = x;
            }
            return best;
        }

        public static int FlasherIndex(RM_SchemeData s, int emitter, double t)
        {
            int n = s.Count;
            long fstep = (long)Math.Floor(t / s.flasherPeriodSeconds + RM_SchemeKernel.Frac01(emitter, 3) * n);
            return (int)(fstep % n);
        }

        /// <summary>u = t/unit + offset steps along an integer lattice; the time of the next lattice crossing after t.
        /// Nudged down one ulp-scale so it is never LATER than the crossing floor() will see.</summary>
        public static double NextStep(double u, double unitSeconds, double t)
        {
            double k = Math.Floor(u) + 1.0;
            double next = t + (k - u) * unitSeconds;
            double eps = Math.Max(1e-9, Math.Abs(next) * 1e-12);
            return Math.Max(next - eps, t + Math.Max(1e-9, Math.Abs(t) * 1e-15));
        }
    }

    // ---------------------------------------------------------------- P0 STEADY: entry lo, held. Cost Still.
    public sealed class RM_SteadyPrimitive : RM_IPrimitive
    {
        public RM_CostClass Cost(RM_Layer l) => RM_CostClass.Still;
        public int Index(RM_Layer l, int n, ref RM_PatternCtx c, double t) => l.Lo(n);
        public double NextChange(RM_Layer l, int n, ref RM_PatternCtx c, double t) => RM_PatternKernel.Never;
        public void Errors(RM_Layer l, int n, List<string> e) { }
    }

    // ---------------------------------------------------------------- P1 BREATH (was RoomBreath). Cost Light.
    // Each scope unit walks lo..hi..lo on its own phase. Bit-identical to the old RoomBreath at scope Room, spread 1.
    public sealed class RM_BreathPrimitive : RM_IPrimitive
    {
        public RM_CostClass Cost(RM_Layer l) => RM_CostClass.Light;

        private static double U(RM_Layer l, ref RM_PatternCtx c, double t)
        {
            int unit = l.scope == RM_Scope.Room ? c.group : l.scope == RM_Scope.Fixture ? c.emitter : 0;
            double phase = l.scope == RM_Scope.Field ? 0.0 : RM_SchemeKernel.Frac01(unit, 1);
            if (l.phaseSpread != 1f) phase *= l.phaseSpread;   // spread 1 keeps the old arithmetic exactly
            return t / l.period + phase;
        }

        public int Index(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            int lo = l.Lo(n), m = l.Hi(n) - lo + 1;
            if (m <= 1) return lo;
            int len = 2 * m - 2;
            long step = (long)Math.Floor(U(l, ref c, t) * len);
            return lo + RM_SchemeKernel.PingPong(m, (int)(step % len));
        }

        public double NextChange(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            int m = l.Hi(n) - l.Lo(n) + 1;
            if (m <= 1) return RM_PatternKernel.Never;
            int len = 2 * m - 2;
            return RM_PatternEvaluator.NextStep(U(l, ref c, t) * len, l.period / len, t);
        }

        public void Errors(RM_Layer l, int n, List<string> e)
        {
            if (!(l.period > 0f)) e.Add("period must be > 0");
            if (l.phaseSpread < 0f || l.phaseSpread > 1f) e.Add("phaseSpread must lie in 0-1");
        }
    }

    // ---------------------------------------------------------------- P2 SPARK (was Sparks). Cost Light.
    // Each fixture rests at lo; in 1 of oneIn slots it rises lo..hi..lo over `rise` s. Bit-identical to the old Sparks.
    public sealed class RM_SparkPrimitive : RM_IPrimitive
    {
        public RM_CostClass Cost(RM_Layer l) => RM_CostClass.Light;

        public int Index(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            int lo = l.Lo(n), m = l.Hi(n) - lo + 1;
            double p = l.period;
            double shifted = t + RM_SchemeKernel.Frac01(c.emitter, 2) * p;
            long slot = (long)Math.Floor(shifted / p);
            if (RM_SchemeKernel.Mix(c.emitter, unchecked((int)slot)) % (uint)l.oneIn != 0) return lo;
            double within = shifted - slot * p;
            if (within >= l.rise) return lo;
            int len = 2 * m - 1;
            int k = Math.Min(len - 1, (int)Math.Floor(within / l.rise * len));
            return lo + (k < m ? k : len - 1 - k);
        }

        public double NextChange(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            int m = l.Hi(n) - l.Lo(n) + 1;
            if (m <= 1) return RM_PatternKernel.Never;
            double p = l.period;
            double shifted = t + RM_SchemeKernel.Frac01(c.emitter, 2) * p;
            long slot = (long)Math.Floor(shifted / p);
            double within = shifted - slot * p;
            double slotEnd = RM_PatternEvaluator.NextStep(shifted / p, p, t);
            bool sparking = RM_SchemeKernel.Mix(c.emitter, unchecked((int)slot)) % (uint)l.oneIn == 0;
            if (!sparking || within >= l.rise) return slotEnd;
            int len = 2 * m - 1;
            return Math.Min(slotEnd, RM_PatternEvaluator.NextStep(within / l.rise * len, l.rise / len, t));
        }

        public void Errors(RM_Layer l, int n, List<string> e)
        {
            if (!(l.period > 0f)) e.Add("period (the slot) must be > 0");
            if (!(l.rise > 0f) || l.rise > l.period) e.Add("rise must be > 0 and fit inside period");
            if (l.oneIn < 1) e.Add("oneIn must be >= 1");
        }
    }
}
