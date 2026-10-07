using System;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_SKELETONS_REMAINDER_1 §2 — "the dunes engine's migration buries a ribcage to its
    // top arcs and later strips it clean" (stillsand_turn3_development_2026-09-30.md §3.1).
    //
    // Pure logic, System.Math only, so the offline selftest (Source/SkeletonSelfTest) compiles this
    // exact file. Building_GiantSkeleton feeds it the sand depths under its footprint
    // (Verse.SandGrid, which the MovingDunes engine writes) and applies the answer.
    //
    // Hysteresis: a ribcage buries when the mean drift over its footprint reaches BuryAt and is only
    // stripped again when it falls to StripAt, so a dune hovering at one depth cannot flicker it.
    // Numbers are PROVISIONAL (no live dune-depth distribution measured yet).
    // ════════════════════════════════════════════════════════════════════
    public static class RM_SkeletonBurialLogic
    {
        public const float BuryAt = 0.6f;
        public const float StripAt = 0.3f;

        /// <summary>Mean of the sampled depths; 0 for none (no sand grid = never buried).</summary>
        public static float MeanDepth(float[] depths)
        {
            if (depths == null || depths.Length == 0)
            {
                return 0f;
            }
            double sum = 0;
            for (int i = 0; i < depths.Length; i++)
            {
                float d = depths[i];
                if (float.IsNaN(d))
                {
                    continue;
                }
                sum += Math.Max(0f, Math.Min(1f, d));
            }
            return (float)(sum / depths.Length);
        }

        /// <summary>The next buried state given the current one and the mean drift depth.</summary>
        public static bool NextBuried(bool buried, float meanDepth, float buryAt = BuryAt, float stripAt = StripAt)
        {
            if (stripAt >= buryAt)
            {
                // a misconfigured band degrades to a plain threshold rather than sticking
                return meanDepth >= buryAt;
            }
            if (!buried)
            {
                return meanDepth >= buryAt;
            }
            return meanDepth > stripAt;
        }

        /// <summary>How sand-coloured the bone is drawn: 0 clean, 1 fully drifted. Buried ribs read
        /// at least half sand; a clean skeleton shows a faint drift line only above StripAt.</summary>
        public static float SandTint(bool buried, float meanDepth)
        {
            float d = Math.Max(0f, Math.Min(1f, meanDepth));
            if (buried)
            {
                return 0.5f + 0.5f * d;
            }
            return d <= StripAt ? 0f : 0.5f * (d - StripAt) / (BuryAt - StripAt);
        }

        /// <summary>The inspect line for the drift state.</summary>
        public static string DriftLine(bool buried, float meanDepth)
        {
            if (buried)
            {
                return "Buried to its top arcs in drift. The bone harp is silent until the dunes strip it.";
            }
            if (meanDepth > StripAt)
            {
                return "Half under drift (" + Math.Round(meanDepth * 100f) + "% sand).";
            }
            return null;
        }
    }
}
