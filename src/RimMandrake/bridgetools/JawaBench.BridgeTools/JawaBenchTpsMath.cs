// JawaBenchTpsMath.cs - the pure maths of the TPS record (BRIDGE_TPS_REGULAR_REPORT_1).
//
// ⛔ NO Verse, NO UnityEngine, NO HarmonyLib in this file. It is compiled TWICE: into the
// companion, and on its own into a throwaway console exe by
// src/RimMandrake/Utils/selftest_tps_record.py, which checks it against the Python port in
// src/RimMandrake/Utils/tps_record.py on the same vectors. A Verse reference here breaks that
// offline selftest, which is the only proof these numbers mean what the doc says.
//
// Doc: design/RimMandrake/tps_record.md

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchTpsMath
    {
        /// <summary>One sample per this many REAL seconds (Time.realtimeSinceStartup).</summary>
        public const float CadenceSeconds = 5f;

        /// <summary>A window longer than this spanned a load/menu, not play: dropped, not recorded.</summary>
        public const float MaxWindowSeconds = 60f;

        /// <summary>Vanilla: TickManager.CurTimePerTick = 1 / (60 * TickRateMultiplier).</summary>
        public const float TicksPerSecondAtSpeed1 = 60f;

        /// <summary>A window paused for at least this share of its frames is a PAUSED sample.</summary>
        public const float PausedShare = 0.5f;

        /// <summary>Record file rotates to tps.1.jsonl past this size; disk use is at most 2x.</summary>
        public const long RotateBytes = 1024L * 1024L;

        /// <summary>In-memory ring for the [Tool]: 720 x 5 s = the last hour.</summary>
        public const int RingCapacity = 720;

        /// <summary>Sustained = this many consecutive eligible samples (6 x 5 s = 30 s).</summary>
        public const int SustainedSamples = 6;
        public const float LowRatio = 0.6f;
        public const float HighRatio = 1.15f;

        public const string StateRun = "run";
        public const string StatePaused = "paused";
        public const string StateMixed = "mixed";

        public struct Sample
        {
            public float Tps;      // dTicks / dReal
            public float Target;   // 60 * multiplier at window end
            public float Ratio;    // Tps / Target, NaN when Target == 0
            public float PausedFrac;
            public string State;   // run | paused | mixed
        }

        /// <summary>
        /// The whole sampler judgement for one window. <paramref name="speedChanged"/> is true when
        /// the time-speed setting differed anywhere inside the window: its multiplier is ambiguous,
        /// so the sample is recorded but never judged (state "mixed").
        /// </summary>
        public static Sample Compute(int dTicks, float dReal, int frames, int pausedFrames,
                                     float multiplier, bool speedChanged)
        {
            var s = new Sample();
            s.Tps = dReal > 0f ? dTicks / dReal : 0f;
            s.Target = TicksPerSecondAtSpeed1 * multiplier;
            s.Ratio = s.Target > 0f ? s.Tps / s.Target : float.NaN;
            s.PausedFrac = frames > 0 ? (float)pausedFrames / frames : 0f;
            if (multiplier <= 0f || s.PausedFrac >= PausedShare) s.State = StatePaused;
            else if (speedChanged) s.State = StateMixed;
            else s.State = StateRun;
            return s;
        }

        /// <summary>Should a window of this length be recorded at all?</summary>
        public static bool WindowUsable(float dReal, int dTicks)
        {
            return dReal > 0f && dReal <= MaxWindowSeconds && dTicks >= 0;
        }

        public static float Median(IList<float> xs)
        {
            if (xs == null || xs.Count == 0) return float.NaN;
            var a = xs.OrderBy(x => x).ToArray();
            int n = a.Length;
            return n % 2 == 1 ? a[n / 2] : (a[n / 2 - 1] + a[n / 2]) / 2f;
        }

        /// <summary>
        /// "low" / "high" when the LAST <see cref="SustainedSamples"/> eligible (state run) ratios are
        /// all below <see cref="LowRatio"/> / above <see cref="HighRatio"/>; "ok" otherwise;
        /// "unknown" when there are fewer eligible samples than that.
        /// </summary>
        public static string Sustained(IList<float> runRatios)
        {
            if (runRatios == null || runRatios.Count < SustainedSamples) return "unknown";
            var tail = runRatios.Skip(runRatios.Count - SustainedSamples).ToList();
            if (tail.All(r => r < LowRatio)) return "low";
            if (tail.All(r => r > HighRatio)) return "high";
            return "ok";
        }

        /// <summary>Rotate before appending a line that would push the file past the cap.</summary>
        public static bool ShouldRotate(long currentBytes, long lineBytes)
        {
            return currentBytes > 0 && currentBytes + lineBytes > RotateBytes;
        }

        public static string F(float v, int places)
        {
            if (float.IsNaN(v) || float.IsInfinity(v)) return "null";
            return Math.Round(v, places).ToString("0.####", CultureInfo.InvariantCulture);
        }
    }
}
