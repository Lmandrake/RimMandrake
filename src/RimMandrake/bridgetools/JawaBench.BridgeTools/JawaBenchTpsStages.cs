// JawaBenchTpsStages.cs - the pure accounting behind JawaBenchTpsProfiler (BRIDGE_TPS_REVIEW2_FIXES_1).
//
// ⛔ NO Verse, NO UnityEngine, NO HarmonyLib: compiled into the companion AND into the offline harness
// (bridgetools/TpsMathSelfTest), where Units*.cs replays hook sequences through it. The Harmony hooks in
// JawaBenchTpsProfiler.cs only read the clock and call in here.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;

namespace JawaBench.BridgeTools
{
    internal sealed class JawaBenchTpsStages
    {
        internal const int CTick = 0, CNormal = 1, CRare = 2, CLong = 3, CWorld = 4, CWorldPost = 5, CMapPre = 6,
            CMapPost = 7, CMapComp = 8, CGameComp = 9, N = 10;
        internal static readonly string[] Names =
            { "tick", "tl:Normal", "tl:Rare", "tl:Long", "world", "worldPost", "mapPre", "mapPost", "mapComp", "gameComp" };
        internal const int WorstTicks = 3;
        internal const double WorstTickSeconds = 0.030;

        private readonly long[] _count = new long[N];
        private readonly long[] _total = new long[N];
        private readonly long[] _max = new long[N];
        private readonly long[] _tickBase = new long[N];
        private readonly List<string> _worst = new List<string>();
        private readonly List<long> _worstMs = new List<long>();
        private long _hooks, _skipped;
        private readonly double _freq;

        internal JawaBenchTpsStages(double stopwatchFrequency) { _freq = stopwatchFrequency; }

        internal long Total(int c) => _total[c];
        internal long Count(int c) => _count[c];

        private double Ms(long ticks) => ticks * 1000.0 / _freq;

        internal void TickBegin() { Array.Copy(_total, _tickBase, N); }

        /// <summary>Close a stage timer. MUST 2: a start of 0 (the prefix never ran: skipped, threw, or another
        /// thread) or a clock that went backwards records NOTHING and is counted as profSkipped - never
        /// `now - 0`, which fabricated the whole process uptime as one stage.</summary>
        internal void End(int c, long start, long now)
        {
            if (c < 0 || c >= N) { _skipped++; return; }
            if (start <= 0 || now < start) { _skipped++; return; }
            long d = now - start;
            _count[c]++;
            _total[c] += d;
            if (d > _max[c]) _max[c] = d;
            _hooks++;
        }

        /// <summary>Close the whole-tick timer; the SAME duration feeds the total and the worst-tick record, and
        /// the tick id is the one the hook captured for THIS tick (SHOULD 1).</summary>
        internal void TickEnd(long start, long now, int ticksGame)
        {
            if (start <= 0 || now < start) { _skipped++; return; }
            End(CTick, start, now);
            long d = now - start;
            if ((double)d / _freq >= WorstTickSeconds) NoteWorst(d, ticksGame);
        }

        internal void CountSkip() { _skipped++; }

        private void NoteWorst(long d, int ticksGame)
        {
            long ms = (long)Ms(d);
            if (_worst.Count >= WorstTicks)
            {
                int min = 0;
                for (int i = 1; i < _worstMs.Count; i++) if (_worstMs[i] < _worstMs[min]) min = i;
                if (_worstMs[min] >= ms) return;
                _worst.RemoveAt(min);
                _worstMs.RemoveAt(min);
            }
            var delta = new long[N];
            for (int i = 0; i < N; i++) delta[i] = _total[i] - _tickBase[i];
            delta[CTick] = d;
            var ex = Exclusive(delta);
            var sb = new StringBuilder(220);
            sb.Append("{\"tg\":").Append(ticksGame).Append(",\"ms\":").Append(M.F(Ms(d), 1))
              .Append(",\"top\":\"").Append(Top(delta)).Append("\",\"stages\":{");
            bool first = true;
            for (int i = 0; i < N; i++)
            {
                if (ex[i] <= 0) continue;
                if (!first) sb.Append(',');
                first = false;
                sb.Append('"').Append(i == CTick ? "tickOther" : Names[i]).Append("\":").Append(M.F(Ms(ex[i]), 1));
            }
            sb.Append("}}");
            _worst.Add(sb.ToString());
            _worstMs.Add(ms);
        }

        /// <summary>How far the children exceed their parents (stopwatch ticks): tick vs its direct children, mapPost
        /// vs mapComp. Positive = the assumed call tree does not hold for this window (overlap, recursion,
        /// a timer outside its parent) and the exclusive split is INVALID (review item 12).</summary>
        private static long Overrun(long[] t)
        {
            long a = t[CNormal] + t[CRare] + t[CLong] + t[CWorld] + t[CWorldPost] + t[CMapPre] + t[CMapPost] + t[CGameComp] - t[CTick];
            long b = t[CMapComp] - t[CMapPost];
            return Math.Max(0, a) + Math.Max(0, b);
        }

        /// <summary>Exclusive stage times from inclusive totals: tick minus children, mapPost minus mapComp.</summary>
        private static long[] Exclusive(long[] t)
        {
            var x = (long[])t.Clone();
            x[CTick] = t[CTick] - t[CNormal] - t[CRare] - t[CLong] - t[CWorld] - t[CWorldPost] - t[CMapPre] - t[CMapPost] - t[CGameComp];
            x[CMapPost] = t[CMapPost] - t[CMapComp];
            if (x[CTick] < 0) x[CTick] = 0;
            if (x[CMapPost] < 0) x[CMapPost] = 0;
            return x;
        }

        private static string Top(long[] totals)
        {
            var x = Exclusive(totals);
            if (totals[CTick] <= 0) return "";
            int best = -1;
            for (int i = 0; i < N; i++) if (best < 0 || x[i] > x[best]) best = i;
            string name = best == CTick ? "tickOther" : Names[best];
            return name + " " + ((int)Math.Round(100.0 * x[best] / totals[CTick])).ToString(CultureInfo.InvariantCulture) + "%";
        }

        /// <summary>This window's attribution as JSON fields (no braces), then reset.</summary>
        internal string TakeWindowFields(double costPerPairSeconds)
        {
            var sb = new StringBuilder(600);
            sb.Append("\"attr\":{");
            for (int i = 0; i < N; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append('"').Append(Names[i]).Append("\":[").Append(_count[i]).Append(',')
                  .Append(M.F(Ms(_total[i]), 1)).Append(',').Append(M.F(Ms(_max[i]), 1)).Append(']');
            }
            sb.Append('}');
            sb.Append(",\"top\":\"").Append(Top(_total)).Append('"');
            sb.Append(",\"worst\":[").Append(string.Join(",", _worst.ToArray())).Append(']');
            long over = Overrun(_total);
            sb.Append(",\"attrValid\":").Append(over > 0 ? "false" : "true");
            if (over > 0) sb.Append(",\"attrOverMs\":").Append(M.F(Ms(over), 1));
            sb.Append(",\"profSkipped\":").Append(_skipped);
            sb.Append(",\"profHooks\":").Append(_hooks);
            sb.Append(",\"profEstMs\":").Append(M.F(_hooks * costPerPairSeconds * 1000.0, 2));
            Reset();
            return sb.ToString();
        }

        internal void Reset()
        {
            Array.Clear(_count, 0, N);
            Array.Clear(_total, 0, N);
            Array.Clear(_max, 0, N);
            _worst.Clear();
            _worstMs.Clear();
            _hooks = 0;
            _skipped = 0;
        }
    }
}
