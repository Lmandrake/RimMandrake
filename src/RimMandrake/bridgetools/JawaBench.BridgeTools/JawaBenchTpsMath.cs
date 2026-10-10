// JawaBenchTpsMath.cs - the pure maths of the TPS record (BRIDGE_TPS_REGULAR_REPORT_1,
// BRIDGE_TPS_CAPTURE_FIXES_1).
//
// ⛔ NO Verse, NO UnityEngine, NO HarmonyLib in this file. It is compiled TWICE: into the
// companion, and on its own into a throwaway console exe by
// src/RimMandrake/Utils/selftest_tps_record.py, which replays frame TRACES through it and checks
// every answer against the Python port in src/RimMandrake/Utils/tps_record.py. A Verse reference
// here breaks that offline selftest, which is the only proof these numbers mean what the doc says.
//
// WINDOW SEMANTICS (the review fix, item 3)
//   The engine (Verse.TickManager.TickManagerUpdate, decompiled 1.6) adds the frame's real time to
//   realTimeToTickThrough only when NOT paused, then ticks at the multiplier it reads THAT frame,
//   and zeroes any unspent credit. So the real interval between two frames' PRE-tick observations
//   is ticked under the state observed at the later frame, before its tick work. The accumulator
//   integrates expected ticks = 60 x multiplier x interval over exactly those intervals:
//     * paused intervals add paused time, never expected ticks (partial pauses no longer dilute);
//     * a Superfast 6x/12x flip or forced-normal-speed is integrated frame by frame, so the
//       endpoint multiplier is never applied to the whole window;
//     * time spent in an IDENTIFIED long event or save (measured by the sampler and passed in as
//       `explained`) is excluded from expected ticks and reported separately;
//     * UNEXPLAINED gaps are NEVER subtracted: a recovered 90 s stall stays in expected ticks,
//       drags the ratio down, and is returned as an incident (no 60 s discard any more) - including a
//       gap across a pause/speed change, which counts at the HIGH end of the two states (expectedLo /
//       ratioHi carry the other end);
//     * a multiplier change inside the tick loop (pre != post) and a state change across a long
//       blocked gap are AMBIGUOUS and counted as such; a window that is mostly ambiguous is "mixed".
//
// Doc: design/RimMandrake/tps_record.md

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchTpsMath
    {
        /// <summary>One window per this many REAL seconds (Stopwatch time).</summary>
        public const double CadenceSeconds = 5.0;

        /// <summary>A frame interval longer than this is a GAP and is recorded as an incident.</summary>
        public const double GapSeconds = 2.0;

        /// <summary>A gap at least this share explained (long event / save) is "longevent", else "stall".</summary>
        public const double ExplainedShare = 0.8;

        /// <summary>Vanilla: TickManager.CurTimePerTick = 1 / (60 * TickRateMultiplier).</summary>
        public const double TicksPerSecondAtSpeed1 = 60.0;

        /// <summary>Window state thresholds, as shares of the window's real time (time, not frames).</summary>
        public const double PausedShare = 0.5;
        public const double StallShare = 0.5;
        public const double LongEventShare = 0.5;
        /// <summary>Ambiguous seconds at or above this share of running seconds make the window "mixed".</summary>
        public const double MixedShare = 0.25;

        /// <summary>Engine: TickManagerUpdate stops ticking after this much tick work in one frame.</summary>
        public const double FrameBudgetSeconds = 0.045454544;

        /// <summary>At most this many gap incidents are carried per window (the rest are counted).</summary>
        public const int MaxGapsPerWindow = 8;

        /// <summary>Record segments: a new file past this size. Rotation never moves or deletes the live file.</summary>
        public const long SegmentBytes = 2L * 1024L * 1024L;
        /// <summary>Files are kept at least this long ...</summary>
        public const double RetentionDays = 7.0;
        /// <summary>... unless the directory would exceed this cap; then the OLDEST non-current files go first.</summary>
        public const long RetentionBytes = 256L * 1024L * 1024L;
        /// <summary>Same rule for archived Player.logs, with their own cap.</summary>
        public const long LogRetentionBytes = 1024L * 1024L * 1024L;

        /// <summary>Writer queue bound: a line beyond it is DROPPED and counted, never blocks the game.</summary>
        public const int QueueCapacity = 4096;

        /// <summary>Watchdog thread: main-thread silence longer than this is written down, then every repeat.</summary>
        public const double SilenceSeconds = 10.0;
        public const double SilenceRepeatSeconds = 30.0;

        /// <summary>In-memory ring for the [Tool]: 720 x 5 s = the last hour.</summary>
        public const int RingCapacity = 720;

        /// <summary>Sustained = this many CONTIGUOUS run windows (6 x 5 s = 30 s).</summary>
        public const int SustainedSamples = 6;
        public const double LowRatio = 0.6;
        public const double HighRatio = 1.15;

        public const string StateRun = "run";
        public const string StatePaused = "paused";
        public const string StateMixed = "mixed";
        public const string StateStall = "stall";
        public const string StateLongEvent = "longevent";

        public struct Gap
        {
            public double Start;      // Stopwatch seconds at the frame before the gap
            public double Seconds;    // the whole interval
            public double Explained;  // of which identified long event / save
            public bool Paused;       // state observed after the gap
            public double Mult;
            public bool Ambiguous;    // state changed across the gap
            public string Kind => Explained >= ExplainedShare * Seconds ? StateLongEvent : StateStall;
        }

        public sealed class Window
        {
            public double DReal, RunS, PausedS, ExplainedS, StallS, AmbigS, Expected, ExpectedLo, GapMaxS, SimS, SimMaxS;
            public int DTicks, Frames, PausedFrames, Transitions, CapFrames, BudgetFrames, GapsDropped;
            public double MultMin, MultMax, MultEnd;
            public bool PausedEnd;
            public List<Gap> Gaps = new List<Gap>();

            public double Tps => RunS > 0 ? DTicks / RunS : 0.0;            // ticks per RUNNING second
            public double TpsWall => DReal > 0 ? DTicks / DReal : 0.0;      // raw: ticks per wall second
            public double Target => RunS > 0 ? Expected / RunS : 0.0;       // time-weighted 60 x mult
            public double Ratio => Expected > 0 ? DTicks / Expected : double.NaN;
            /// <summary>Upper ratio bound: ticks over the LOW end of the expected range (an unexplained gap across
            /// a state change has an uncertain multiplier; Expected takes the high end, never omits it).</summary>
            public double RatioHi => ExpectedLo > 0 ? DTicks / ExpectedLo : double.NaN;
            public double PausedFrac => DReal > 0 ? PausedS / DReal : 0.0;
            public double SimShare => DReal > 0 ? SimS / DReal : 0.0;

            public string State
            {
                get
                {
                    if (DReal <= 0) return StatePaused;
                    if (ExplainedS >= LongEventShare * DReal) return StateLongEvent;
                    if (StallS >= StallShare * DReal) return StateStall;
                    if (PausedS >= PausedShare * DReal || Expected <= 0) return StatePaused;
                    if (AmbigS >= MixedShare * RunS) return StateMixed;
                    return StateRun;
                }
            }
        }

        /// <summary>
        /// Pure frame-trace accumulator. The sampler calls Pre() in a Harmony PREFIX on
        /// TickManager.TickManagerUpdate (state before tick work) and Post() in the POSTFIX.
        /// Post() returns a closed window once CadenceSeconds of intervals have accumulated.
        /// Everything is in seconds of a monotonic clock supplied by the caller.
        /// </summary>
        public sealed class FrameAccumulator
        {
            public bool Open { get; private set; }
            private bool _needTick0;
            private double _tPrev, _t0;
            private int _tick0, _ticksPre;
            private bool _pausedPrev, _pausedPre;
            private double _multPrev, _multPre, _lastRunDt;
            private Window _w = new Window();

            public void Reset() { Open = false; _w = new Window(); }

            /// <summary>State before tick work. Returns the gap this frame closed, if it was one.</summary>
            public Gap? Pre(double now, bool paused, double mult, int ticksBefore, double explained)
            {
                _ticksPre = ticksBefore;
                _pausedPre = paused;
                _multPre = mult;
                _lastRunDt = 0;
                if (!Open)
                {
                    Open = true; _needTick0 = true;
                    _tPrev = now; _t0 = now;
                    _pausedPrev = paused; _multPrev = mult;
                    _w = new Window { MultMin = double.MaxValue, MultMax = double.MinValue };
                    return null;
                }
                double dt = now - _tPrev;
                if (dt < 0) dt = 0;
                double ex = explained < 0 ? 0 : (explained > dt ? dt : explained);
                double r = dt - ex;
                bool transition = paused != _pausedPrev || (!paused && !_pausedPrev && mult != _multPrev);
                bool gap = dt > GapSeconds;
                var w = _w;
                w.Frames++;
                w.DReal += dt;
                w.ExplainedS += ex;
                if (dt > w.GapMaxS) w.GapMaxS = dt;
                if (transition) w.Transitions++;
                if (gap) w.StallS += r;
                if (gap && transition)
                {
                    // MUST 5: the state changed somewhere inside an unexplained gap, so which multiplier (or pause)
                    // governed it is unknown. The time is KEPT: expected takes the HIGH end of the two states,
                    // ExpectedLo the low end, and the seconds are ambiguous. Never dropped from the denominator.
                    w.AmbigS += r;
                    double before = _pausedPrev ? 0.0 : _multPrev, after = paused ? 0.0 : mult;
                    double hi = Math.Max(before, after), lo = Math.Min(before, after);
                    if (hi > 0)
                    {
                        w.RunS += r;
                        w.Expected += TicksPerSecondAtSpeed1 * hi * r;
                        w.ExpectedLo += TicksPerSecondAtSpeed1 * lo * r;
                        _lastRunDt = r;
                        if (hi < w.MultMin) w.MultMin = hi;
                        if (hi > w.MultMax) w.MultMax = hi;
                    }
                    else { w.PausedS += r; w.PausedFrames++; }
                }
                else if (paused) { w.PausedS += r; w.PausedFrames++; }
                else
                {
                    w.RunS += r;
                    w.Expected += TicksPerSecondAtSpeed1 * mult * r;
                    w.ExpectedLo += TicksPerSecondAtSpeed1 * mult * r;
                    _lastRunDt = r;
                    if (mult < w.MultMin) w.MultMin = mult;
                    if (mult > w.MultMax) w.MultMax = mult;
                }
                Gap? g = null;
                if (gap)
                {
                    var gg = new Gap { Start = _tPrev, Seconds = dt, Explained = ex, Paused = paused, Mult = mult, Ambiguous = transition };
                    if (w.Gaps.Count < MaxGapsPerWindow) w.Gaps.Add(gg); else w.GapsDropped++;
                    g = gg;
                }
                _tPrev = now;
                _pausedPrev = paused;
                _multPrev = mult;
                return g;
            }

            /// <summary>After tick work. Returns a closed window when the cadence has elapsed.</summary>
            public Window Post(double multAfter, int ticksAfter, double simSeconds)
            {
                if (!Open) return null;
                if (_needTick0) { _needTick0 = false; _tick0 = ticksAfter; return null; }
                var w = _w;
                w.SimS += simSeconds;
                if (simSeconds > w.SimMaxS) w.SimMaxS = simSeconds;
                if (!_pausedPre)
                {
                    int done = ticksAfter - _ticksPre;
                    if (_multPre > 0 && done >= 2 * _multPre) w.CapFrames++;
                    if (simSeconds > FrameBudgetSeconds) w.BudgetFrames++;
                    if (multAfter != _multPre) { w.AmbigS += _lastRunDt; w.Transitions++; }
                }
                _multPrev = multAfter;    // the next interval starts under the post-tick multiplier
                if (_tPrev - _t0 < CadenceSeconds) return null;
                w.DTicks = ticksAfter - _tick0;
                if (w.DTicks < 0) w.DTicks = 0;
                w.MultEnd = multAfter;
                w.PausedEnd = _pausedPre;
                if (w.MultMin == double.MaxValue) { w.MultMin = 0; w.MultMax = 0; }
                _t0 = _tPrev;
                _tick0 = ticksAfter;
                _w = new Window { MultMin = double.MaxValue, MultMax = double.MinValue };
                return w;
            }
        }

        public static double Median(IList<double> xs)
        {
            if (xs == null || xs.Count == 0) return double.NaN;
            var a = xs.OrderBy(x => x).ToArray();
            int n = a.Length;
            return n % 2 == 1 ? a[n / 2] : (a[n / 2 - 1] + a[n / 2]) / 2.0;
        }

        /// <summary>
        /// "low" / "high" when the LAST <see cref="SustainedSamples"/> ratios of an UNBROKEN streak of
        /// run windows are all below / above the bounds; "ok" otherwise; "unknown" when the streak is
        /// shorter. The caller breaks the streak on any non-run window, game change or coverage gap.
        /// </summary>
        public static string Sustained(IList<double> streak)
        {
            if (streak == null || streak.Count < SustainedSamples) return "unknown";
            var tail = streak.Skip(streak.Count - SustainedSamples).ToList();
            if (tail.All(r => r < LowRatio)) return "low";
            if (tail.All(r => r > HighRatio)) return "high";
            return "ok";
        }

        /// <summary>Start a new segment before appending a line that would push this one past the cap.</summary>
        public static bool ShouldRotate(long currentBytes, long lineBytes)
        {
            return currentBytes > 0 && currentBytes + lineBytes > SegmentBytes;
        }

        /// <summary>Segment file name: start time, session, pid, segment number. Sorts by time.</summary>
        public static string SegmentName(DateTime startUtc, string session, int pid, int segment)
        {
            return "tps_" + startUtc.ToString("yyyyMMdd'T'HHmmss'Z'", CultureInfo.InvariantCulture) + "_" + session + "_" +
                   pid.ToString(CultureInfo.InvariantCulture) + "_" + segment.ToString("D3", CultureInfo.InvariantCulture) + ".jsonl";
        }

        /// <summary>
        /// Which files to delete. Never a current-session file. First everything older than
        /// <see cref="RetentionDays"/>; then, while the rest exceeds <paramref name="capBytes"/>, the oldest.
        /// Inputs are parallel arrays; returns indices, oldest first.
        /// </summary>
        public static List<int> PlanRetention(IList<long> bytes, IList<double> ageDays, IList<bool> current, long capBytes)
        {
            var del = new List<int>();
            var order = Enumerable.Range(0, bytes.Count).OrderByDescending(i => ageDays[i]).ThenBy(i => i).ToList();
            long total = 0;
            foreach (int i in order) total += bytes[i];
            foreach (int i in order)
            {
                if (current[i]) continue;
                if (ageDays[i] > RetentionDays || total > capBytes)
                {
                    del.Add(i);
                    total -= bytes[i];
                }
            }
            return del;
        }

        public static string F(double v, int places)
        {
            if (double.IsNaN(v) || double.IsInfinity(v)) return "null";
            string s = Math.Round(v, places, MidpointRounding.AwayFromZero).ToString("0.####", CultureInfo.InvariantCulture);
            return s == "-0" ? "0" : s;
        }

        /// <summary>The window's JSON fields (no braces), shared by the record line and the selftest.</summary>
        public static string WindowFields(Window w)
        {
            var sb = new StringBuilder(400);
            sb.Append("\"state\":\"").Append(w.State).Append('"')
              .Append(",\"dReal\":").Append(F(w.DReal, 3))
              .Append(",\"dTicks\":").Append(w.DTicks)
              .Append(",\"ratio\":").Append(F(w.Ratio, 3))
              .Append(",\"tps\":").Append(F(w.Tps, 2))
              .Append(",\"tpsWall\":").Append(F(w.TpsWall, 2))
              .Append(",\"target\":").Append(F(w.Target, 2))
              .Append(",\"expected\":").Append(F(w.Expected, 1))
              .Append(",\"expectedLo\":").Append(F(w.ExpectedLo, 1))
              .Append(",\"ratioHi\":").Append(F(w.RatioHi, 3))
              .Append(",\"runS\":").Append(F(w.RunS, 3))
              .Append(",\"pausedS\":").Append(F(w.PausedS, 3))
              .Append(",\"explainedS\":").Append(F(w.ExplainedS, 3))
              .Append(",\"stallS\":").Append(F(w.StallS, 3))
              .Append(",\"ambigS\":").Append(F(w.AmbigS, 3))
              .Append(",\"pausedFrac\":").Append(F(w.PausedFrac, 3))
              .Append(",\"multMin\":").Append(F(w.MultMin, 2))
              .Append(",\"multMax\":").Append(F(w.MultMax, 2))
              .Append(",\"mult\":").Append(F(w.MultEnd, 2))
              .Append(",\"transitions\":").Append(w.Transitions)
              .Append(",\"frames\":").Append(w.Frames)
              .Append(",\"fps\":").Append(F(w.DReal > 0 ? w.Frames / w.DReal : 0.0, 1))
              .Append(",\"gapMaxMs\":").Append(F(w.GapMaxS * 1000.0, 1))
              .Append(",\"gaps\":").Append(w.Gaps.Count + w.GapsDropped)
              .Append(",\"simMs\":").Append(F(w.SimS * 1000.0, 1))
              .Append(",\"simMaxMs\":").Append(F(w.SimMaxS * 1000.0, 1))
              .Append(",\"simShare\":").Append(F(w.SimShare, 3))
              .Append(",\"capFrames\":").Append(w.CapFrames)
              .Append(",\"budgetFrames\":").Append(w.BudgetFrames);
            return sb.ToString();
        }

        /// <summary>A JSON string literal (or null). The writer's Json delegates here.</summary>
        public static string Json(string s)
        {
            if (s == null) return "null";
            var sb = new StringBuilder(s.Length + 2);
            sb.Append('"');
            foreach (char c in s)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < 0x20) sb.Append("\\u").Append(((int)c).ToString("x4")); else sb.Append(c);
                        break;
                }
            }
            return sb.Append('"').ToString();
        }

        /// <summary>
        /// The whole `incident` row body: the gap, what the sampler knows about it, and the watchdog's
        /// context fields (passed in). Composed here, not in the sampler, so the selftest can parse the
        /// PRODUCTION composition strictly.
        /// </summary>
        public static string IncidentFields(Gap g, string quietPhase, double prevSimS, int gcDelta, double saveTotalS,
                                            string lastSave, string contextFields)
        {
            return "\"type\":\"" + g.Kind + "\"," + GapFields(g) +
                   ",\"quietPhase\":" + Json(quietPhase) + ",\"prevSimS\":" + F(prevSimS, 3) +
                   ",\"gcDelta\":" + gcDelta +
                   ",\"saveTotalS\":" + F(saveTotalS, 3) + ",\"lastSave\":" + Json(lastSave) +
                   "," + contextFields;
        }

        /// <summary>One gap incident's JSON fields (no braces). `multAfter` is the multiplier observed after the
        /// gap; the incident's `mult` (from the watchdog context) is the cached one from BEFORE it.
        /// ⛔ Never emit an envelope key (seq/utc/mono/session/kind) or a context key here: a duplicate key
        /// is silently resolved to the last value by most JSON readers.</summary>
        public static string GapFields(Gap g)
        {
            return "\"gapS\":" + F(g.Seconds, 3) + ",\"explainedS\":" + F(g.Explained, 3) +
                   ",\"unexplainedS\":" + F(g.Seconds - g.Explained, 3) + ",\"pausedAfter\":" + (g.Paused ? "true" : "false") +
                   ",\"multAfter\":" + F(g.Mult, 2) + ",\"ambiguous\":" + (g.Ambiguous ? "true" : "false");
        }
    }
}
