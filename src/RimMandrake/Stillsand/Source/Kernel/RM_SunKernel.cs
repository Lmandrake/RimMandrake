using System;
using System.Collections.Generic;

namespace RimMandrake.Stillsand
{
    // Verse-free sun-fed work and thumper decisions: the sun factor a sun-powered table works at (RM_SunPowered.cs), the
    // solar still's progress per rare tick and its corpse yield (RM_SolarStill.cs), and the thumper's beat clock and call
    // selection (RM_Thumper.cs). The mod calls these with the same expressions; the offline fuzz drives them.

    public enum RM_SunReason { None, NotSpawned, Roofed, Blotted, NoSun, InShade, TooLow }

    public struct RM_CallCand
    {
        public int id;
        public int distSq;
        public bool player, downed, cantMove, busyHunting;
    }

    public static class RM_SunKernel
    {
        /// <summary>Sun intensity 0..1: the pinned sun's elevation (NaN = 0), else the celestial glow.</summary>
        public static float Intensity(bool pinnedActive, float elevationDeg, float glow)
        {
            if (pinnedActive)
            {
                if (float.IsNaN(elevationDeg))
                {
                    return 0f;
                }
                return Clamp01((float)Math.Sin(elevationDeg * 0.01745329f));
            }
            return Clamp01(glow);
        }

        public static float Clamp01(float v) { return v < 0f ? 0f : v > 1f ? 1f : v; }

        /// <summary>The factor a sun-powered thing works at, and why it is zero or low.</summary>
        public static float Factor(bool spawned, bool roofed, bool noSunWeather, float sun, float shade, out RM_SunReason reason)
        {
            reason = RM_SunReason.None;
            if (!spawned)
            {
                reason = RM_SunReason.NotSpawned;
                return 0f;
            }
            if (roofed)
            {
                reason = RM_SunReason.Roofed;
                return 0f;
            }
            if (noSunWeather)
            {
                reason = RM_SunReason.Blotted;
                return 0f;
            }
            if (sun <= 0f)
            {
                reason = RM_SunReason.NoSun;
                return 0f;
            }
            float sh = Clamp01(shade);
            float f = sun * (1f - sh);
            if (sh >= 0.5f)
            {
                reason = RM_SunReason.InShade;
            }
            else if (f < 0.3f)
            {
                reason = RM_SunReason.TooLow;
            }
            return f;
        }

        public static bool CanWork(bool enabled, float factor, float minSunFactor)
        {
            return enabled && factor >= minSunFactor;
        }

        public static float WorkSpeed(bool scaleWorkSpeed, float factor, float workSpeedAtFullSun, float multiplier)
        {
            if (!scaleWorkSpeed)
            {
                return 1f;
            }
            return Math.Max(0.05f, factor) * workSpeedAtFullSun * multiplier;
        }

        /// <summary>The still's rate: zero unless it can work; sun x slider x the pearl lens.</summary>
        public static float StillRate(bool canWork, float sunFactor, float rateMultiplier, bool hasPearlLens, float pearlFactor)
        {
            if (!canWork)
            {
                return 0f;
            }
            float f = sunFactor * rateMultiplier;
            if (hasPearlLens)
            {
                f *= pearlFactor;
            }
            return f;
        }

        /// <summary>One CompTickRare of the still. No feed resets the cycle; no rate holds it; a full cycle fires once and
        /// restarts from zero.</summary>
        public static float StillStep(float progress, bool hasFeed, float rate, int stepTicks, int ticksPerCycle, out bool fired)
        {
            fired = false;
            if (!hasFeed)
            {
                return 0f;
            }
            if (rate <= 0f)
            {
                return progress;
            }
            progress += stepTicks * rate / Math.Max(1, ticksPerCycle);
            if (progress < 1f)
            {
                return progress;
            }
            fired = true;
            return 0f;
        }

        public static int CorpseLitres(float bodySize, float litresPerBodySize)
        {
            return Math.Max(1, (int)Math.Round(bodySize * litresPerBodySize));
        }

        // ------------------------------------------------------------ mirror beam

        /// <summary>A pawn caster's (the muurrok's) sun: nothing roofed or under a no-sun weather, else the glow when at least minGlow.</summary>
        public static float BeamSunPawn(bool roofed, bool blotted, float glow, float minSunGlow)
        {
            if (roofed || blotted)
            {
                return 0f;
            }
            return glow < minSunGlow ? 0f : Clamp01(glow);
        }

        /// <summary>A turret caster's sun: the table sun factor, or nothing below minGlow.</summary>
        public static float BeamSunTurret(float factor, float minSunGlow)
        {
            return factor < minSunGlow ? 0f : Clamp01(factor);
        }

        /// <summary>Damage of one beam hit: the total spread over the swept cells, or the damage def's default, times the sun.</summary>
        public static float BeamDamage(float beamTotalDamage, int pathCellCount, float defaultDamage, float factor)
        {
            return beamTotalDamage > 0f ? beamTotalDamage / Math.Max(1, pathCellCount) * factor : defaultDamage * factor;
        }

        // ------------------------------------------------------------ thumper

        public static bool BeatDue(bool enabled, int now, int lastBeatTick, int beatIntervalTicks, bool hasFuel)
        {
            return enabled && !(now - lastBeatTick < beatIntervalTicks) && hasFuel;
        }

        /// <summary>Which swimmers a beat calls, nearest first (the caller sorts): wild, up, able to move, not already
        /// hunting, outside the arrival radius, with somewhere to go; at most `max`. Returns indices into `ordered`.</summary>
        public static List<int> SelectCalls(IList<RM_CallCand> ordered, int max, int arriveRadius, Func<int, bool> hasDest)
        {
            var called = new List<int>();
            for (int i = 0; i < ordered.Count && called.Count < max; i++)
            {
                RM_CallCand c = ordered[i];
                if (c.player || c.downed || c.cantMove)
                {
                    continue;
                }
                if (c.busyHunting)
                {
                    continue;
                }
                if (c.distSq <= arriveRadius * arriveRadius)
                {
                    continue;
                }
                if (!hasDest(i))
                {
                    continue;
                }
                called.Add(i);
            }
            return called;
        }
    }
}
