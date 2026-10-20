// Verse-free kernel of the Weather Suite: the great-circle arc from the substellar point, the terminator and nightside band tests (which share
// one dividing line and never overlap), and the maximised-aurora colour channel arithmetic.
// WeatherGeometryUtility and GameCondition_DarkAuroraMax call these with the same expressions;
// SelfTest/WeatherFuzz.cs compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib (a `using Verse;` here breaks the
// self-test build, which is the guard rail).
using System;
using System.Collections.Generic;

namespace RimMandrake.StarWars.WeatherSuite
{
    public static class RM_WeatherKernel
    {
        public const float Deg2Rad = 0.0174532924f, Rad2Deg = 57.29578f;
        /// <summary>What an invalid tile reads as: in no band.</summary>
        public const float NoArc = -1f;

        /// <summary>Great-circle arc in degrees between two lat/lon points (all degrees).</summary>
        public static float ArcDegrees(float latDeg, float lonDeg, float lat0Deg, float lon0Deg)
        {
            float lat = latDeg * Deg2Rad, lon = lonDeg * Deg2Rad, lat0 = lat0Deg * Deg2Rad, lon0 = lon0Deg * Deg2Rad;
            float cosArc = (float)(Math.Sin(lat0) * Math.Sin(lat) + Math.Cos(lat0) * Math.Cos(lat) * Math.Cos(lon - lon0));
            cosArc = cosArc < -1f ? -1f : cosArc > 1f ? 1f : cosArc;
            return (float)Math.Acos(cosArc) * Rad2Deg;
        }

        /// <summary>The permanent storm wall: inside [min, max] inclusive.</summary>
        public static bool InTerminatorBand(float arc, float min, float max)
        {
            return arc >= min && arc <= max;
        }

        /// <summary>The dark side past the wall: strictly beyond the nightside edge, so a tile exactly on a shared edge is in the wall only.</summary>
        public static bool InNightsideBand(float arc, float nightsideMin)
        {
            return arc > nightsideMin;
        }

        public const float VanillaSkySaturation = 0.075f, VanillaOverlaySaturation = 0.025f, VanillaBrightness = 0.73f;

        /// <summary>One channel of a maximised aurora tint: lerp(white, channel, saturation) x brightness, never past pure white and never
        /// darker than the vanilla aurora renders the same channel (a high saturation with a low brightness would otherwise zero a channel).</summary>
        public static float TintChannel(float channel, float saturation, float brightness, float vanillaSaturation)
        {
            float v = (1f + (channel - 1f) * saturation) * brightness;
            float floor = VanillaChannel(channel, vanillaSaturation);
            if (v < floor) v = floor;
            return v > 1f ? 1f : v;
        }

        /// <summary>The same channel as the unmodified vanilla aurora renders it: lerp(white, channel, vanillaSaturation) x 0.73.</summary>
        public static float VanillaChannel(float channel, float vanillaSaturation)
        {
            return (1f + (channel - 1f) * vanillaSaturation) * VanillaBrightness;
        }

        // ── AURORA_LIGHT (2026-10-20): the perpetual aurora's LIGHT. A GameCondition's SkyTarget can only darken (SkyManager folds it in with
        // SkyTarget.LerpDarken: glow and every colour channel = min), so the light is applied AFTER the fold by a Harmony postfix, with these
        // numbers. ShimmerMin..1 is the aurora's breathing; Nightness fades the whole effect out between night (sun glow <= 0.1) and dusk (0.6).
        public const float ShimmerMin = 0.55f, NightGlowEdge = 0.1f, DuskGlowEdge = 0.6f;

        /// <summary>The aurora's brightness pulse in [ShimmerMin, 1]: two incommensurate sines, both sped up by activity (1 = slow drift).
        /// phase decorrelates two maps or two layers.</summary>
        public static float Shimmer(int ticks, float activity, float phase)
        {
            if (activity < 0f) activity = 0f;
            double a = ticks * activity * 0.0021 + phase, b = ticks * activity * 0.0057 + phase * 1.7;
            double s = 0.6 * Math.Sin(a) + 0.4 * Math.Sin(b);                 // -1..1
            return (float)(ShimmerMin + (1.0 - ShimmerMin) * 0.5 * (s + 1.0));
        }

        /// <summary>1 at night, 0 from dusk on: an aurora is not seen in daylight.</summary>
        public static float Nightness(float sunGlow)
        {
            float t = (sunGlow - NightGlowEdge) / (DuskGlowEdge - NightGlowEdge);
            t = t < 0f ? 0f : t > 1f ? 1f : t;
            return 1f - t;
        }

        /// <summary>One sky-colour channel under the aurora: the ordinary night channel darkened by `darkness` (0..1, the biome's "totally
        /// dark"), plus the aurora's coloured light (hue channel x light), clamped to 0..1. Both terms are scaled by nightness by the caller.</summary>
        public static float AuroraSkyChannel(float baseChannel, float hueChannel, float darkness, float light)
        {
            darkness = darkness < 0f ? 0f : darkness > 1f ? 1f : darkness;
            float v = baseChannel * (1f - darkness) + hueChannel * (light < 0f ? 0f : light);
            return v < 0f ? 0f : v > 1f ? 1f : v;
        }

        /// <summary>The outdoor ground-glow floor the aurora gives: groundGlow x shimmer x nightness, clamped to 0..MaxGroundGlow.</summary>
        public const float MaxGroundGlow = 0.6f;
        public static float GroundGlowFloor(float groundGlow, float shimmer, float nightness)
        {
            float v = groundGlow * shimmer * nightness;
            return v < 0f ? 0f : v > MaxGroundGlow ? MaxGroundGlow : v;
        }

        /// <summary>Vanilla PsychGlow: glow above this reads "Lit" (no darkness mood); the default ground glow stays below it ("totally dark").</summary>
        public const float PsychLitThreshold = 0.3f;
    }
}
