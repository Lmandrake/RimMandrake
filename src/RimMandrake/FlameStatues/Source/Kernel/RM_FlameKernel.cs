// Verse-free kernel of the flame statues: the quality-to-flame-size table, the lit / shown / burning predicates, the fleck cadence,
// the per-point frame pick, the fuel-use multiplier and the "statues never run out" refill rule. RM_CompFlamePoints and
// FlameStatuesStartup call these with the same expressions; SelfTest/FlameStatuesFuzz.cs compiles this file alone. Keep it free of
// Verse/RimWorld/UnityEngine/HarmonyLib (a `using Verse;` here breaks the self-test build, which is the guard rail).
using System;

namespace RimMandrake.FlameStatues
{
    public static class RM_FlameKernel
    {
        public const float MinFuelMultiplier = 0.25f;
        public const float MaxFuelMultiplier = 4f;
        /// <summary>Never throw a fleck more often than this (ticks).</summary>
        public const int MinFleckInterval = 10;
        /// <summary>Each point is out of phase by this many ticks from the one before it.</summary>
        public const int PointPhase = 37;
        /// <summary>The fuel top-up and the glow re-poll run on this hash interval (ticks).</summary>
        public const int PollInterval = 250;
        /// <summary>Flame sizes by quality, Awful..Legendary, indexed by RimWorld's QualityCategory ordinal (PROVISIONAL tuning; the design's "half size .. double").</summary>
        public static readonly float[] QualityScales = { 0.5f, 0.7f, 1f, 1.2f, 1.4f, 1.7f, 2f };

        /// <summary>quality = QualityCategory ordinal (0 Awful .. 6 Legendary), -1 = no CompQuality.</summary>
        public static float QualityScale(bool compScalingEnabled, bool settingEnabled, int quality)
        {
            if (!compScalingEnabled || !settingEnabled || quality < 0) return 1f;
            if (quality >= QualityScales.Length) return 1f;
            return QualityScales[quality];
        }

        /// <summary>Fuel state only: no refuelable comp, or fuel in the tank, or fuel use switched off.</summary>
        public static bool Burning(bool hasRefuelable, bool hasFuel, bool consumeFuelSetting)
        {
            return !hasRefuelable || hasFuel || !consumeFuelSetting;
        }

        public static bool FlamesShown(bool burning, bool flamePointsSetting) { return burning && flamePointsSetting; }

        public static bool LitNow(bool burning, bool flamePointsSetting, bool glowSetting) { return glowSetting && flamePointsSetting && burning; }

        /// <summary>Ticks between two flecks of one point; 0 base interval means no flecks at all (returns 0).</summary>
        public static int FleckInterval(int baseInterval, float qualityScale)
        {
            if (baseInterval <= 0) return 0;
            return Math.Max(MinFleckInterval, (int)Math.Round(baseInterval / qualityScale));
        }

        /// <summary>Does point i throw a fleck on this tick?</summary>
        public static bool FleckDue(int ticksGame, int thingId, int pointIndex, int interval)
        {
            if (interval <= 0) return false;
            long phase = (long)ticksGame + thingId + (long)pointIndex * PointPhase;
            return phase % interval == 0;
        }

        public static float ClampFuelMultiplier(float m) { return Math.Min(Math.Max(m, MinFuelMultiplier), MaxFuelMultiplier); }

        /// <summary>The per-day fuel rate after the startup multiplier (1 leaves the def untouched).</summary>
        public static float ScaledFuelRate(float rate, float multiplier)
        {
            float m = ClampFuelMultiplier(multiplier);
            return Math.Abs(m - 1f) < 1e-6f ? rate : rate * m;
        }

        /// <summary>The animation tick of a statue: the game tick offset by its id so statues do not flicker in step.</summary>
        public static int AnimTicks(int ticksGame, int thingId) { return ticksGame + ((thingId ^ 0x80FD52) & 0x7FFFFFFF); }

        /// <summary>Which fire frame point i draws, always in [0, frameCount).</summary>
        public static int FrameIndex(int animTicks, int thingId, int pointIndex, int frameCount)
        {
            int step = animTicks / 15 + pointIndex * 7;
            int v = step ^ (thingId * 391 + pointIndex * 131);
            return (int)((uint)v & 0x7FFFFFFF) % frameCount;
        }

        /// <summary>Which radial jitter pattern entry point i uses, always in [0, patternLength).</summary>
        public static int JitterIndex(int animTicks, int pointIndex, int patternLength)
        {
            int step = animTicks / 15 + pointIndex * 7;
            return (int)((uint)(step + pointIndex * 3) & 0x7FFFFFFF) % patternLength;
        }

        /// <summary>"Statues never run out": top the tank up when fuel use is off, only on the poll tick and only while below capacity. Returns the amount to add (0 = nothing).</summary>
        public static float RefillAmount(bool consumeFuelSetting, bool hasRefuelable, bool pollTick, float fuel, float capacity)
        {
            if (consumeFuelSetting || !hasRefuelable || !pollTick) return 0f;
            return fuel < capacity ? capacity - fuel : 0f;
        }
    }
}
