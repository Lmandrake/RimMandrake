// Verse-free kernel of the Weather Suite: the great-circle arc from the substellar point, the terminator and nightside band tests (which share
// one dividing line and never overlap), the maximised-aurora colour channel arithmetic, and the instrument's top-N forecast percentages.
// WeatherGeometryUtility, GameCondition_DarkAuroraMax and CompForecaster call these with the same expressions;
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

        /// <summary>Top-N share of the whole forecast, as percentages of the total of ALL weights, best first. Weights must be positive.</summary>
        public static List<KeyValuePair<int, float>> TopShares(IList<float> weights, int n)
        {
            var idx = new List<int>();
            float total = 0f;
            for (int i = 0; i < weights.Count; i++) { if (weights[i] > 0f) { idx.Add(i); total += weights[i]; } }
            idx.Sort((a, b) => { int c = weights[b].CompareTo(weights[a]); return c != 0 ? c : a.CompareTo(b); });
            var res = new List<KeyValuePair<int, float>>();
            for (int i = 0; i < Math.Min(n, idx.Count); i++)
                res.Add(new KeyValuePair<int, float>(idx[i], total > 0f ? weights[idx[i]] / total * 100f : 0f));
            return res;
        }
    }
}
