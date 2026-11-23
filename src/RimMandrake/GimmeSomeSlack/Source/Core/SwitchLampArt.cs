// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// The switch lamp's pixels (RIMMANDRAKE_LIGHT_SLACK_SWITCH_GREEN_RED_DARK_WHEN_UNPOWERED). Drawn in code, not a texture file: the switch
// is printed into the map mesh (drawerType MapMeshOnly) in five looks with up to 15 stub variants each, so a lamp baked into the art
// would multiply those files by three states and re-print a section on every power change. A small lamp drawn every frame over any
// look reads the state now. SwitchLightDraw makes Unity textures from these bytes; the offline mock (tools/switch_lamp_mock.py, via
// the SelfTest's --switchlamp-dump) composes the very same bytes, so what the art judge saw is what the game draws.
using System;

namespace RimMandrake.GimmeSomeSlack.Core
{
    public static class SwitchLampArt
    {
        /// <summary>Pixels a side of each lamp texture.</summary>
        public const int Px = 32;
        /// <summary>The lamp's centre from the switch's centre, in cells (+z up the screen): the lower-left of the body, on the body of
        /// every look and clear of every lever and handle (the art judge's repair, 2026-11-20: over the Industrial LED it hid that look's
        /// open handle).</summary>
        public const float OffX = -0.125f, OffZ = -0.13f;
        /// <summary>Lens and halo sizes, in cells: half the size at his walk of 2026-11-22 (0.16 and 0.52), which read "twice as large in radius as it should be and
        /// quite obnoxious" (RIMMANDRAKE_SHRINK_SLACK_SWITCH_LIGHT_TWICE_TOO_WIDE_AT_HIS_WALK).</summary>
        public const float LensCells = 0.08f, HaloCells = 0.26f;
        /// <summary>The sizes he saw at that walk, for the check that the light stays at half of them (SwitchLightChecks).</summary>
        public const float WalkLensCells = 0.16f, WalkHaloCells = 0.52f;
        /// <summary>The Industrial look's closed art bakes a small green LED (texture pixel 53.5, 51 of 128) that would glow on an
        /// unpowered switch beside a dark lamp. An unlit cap this size covers it on that look's closed art.</summary>
        public const float LedX = -0.082f, LedZ = 0.10f, LedCapCells = 0.06f;

        private static readonly byte[][] LensRgb =
        {
            // Dark: an unlit lens, smoked glass         Green                               Red
            new byte[] { 92, 98, 92, 30, 34, 30 }, new byte[] { 205, 255, 185, 30, 205, 60 }, new byte[] { 255, 200, 180, 220, 35, 28 },
        };
        private static readonly byte[][] HaloRgb = { null, new byte[] { 70, 255, 95 }, new byte[] { 255, 60, 40 } };

        private static float Clamp01(float v) => v < 0f ? 0f : v > 1f ? 1f : v;

        /// <summary>RGBA32, row 0 at the bottom (Unity's LoadRawTextureData order): a round lens with a dark bezel and a small glint.</summary>
        public static byte[] Lens(SwitchLamp lamp)
        {
            byte[] c = LensRgb[(int)lamp];
            var o = new byte[Px * Px * 4];
            float h = Px / 2f;
            for (int y = 0; y < Px; y++)
                for (int x = 0; x < Px; x++)
                {
                    float dx = (x + 0.5f - h) / h, dy = (y + 0.5f - h) / h, r = (float)Math.Sqrt(dx * dx + dy * dy);
                    float a = Clamp01((1f - r) * h);                        // anti-aliased outer edge
                    float R, G, B;
                    if (r > 0.74f) { R = G = B = 18f; }                      // the bezel
                    else
                    {
                        float t = (float)Math.Pow(r / 0.74f, 1.4);         // bright centre to the lens's base colour
                        R = c[0] + (c[3] - c[0]) * t; G = c[1] + (c[4] - c[1]) * t; B = c[2] + (c[5] - c[2]) * t;
                        float gx = dx + 0.28f, gy = dy - 0.30f, g = Clamp01(1f - (float)Math.Sqrt(gx * gx + gy * gy) / 0.20f);
                        float k = lamp == SwitchLamp.Dark ? 0.35f : 0.75f;  // the glint: dim on an unlit lens
                        R += (255f - R) * g * k; G += (255f - G) * g * k; B += (255f - B) * g * k;
                    }
                    int i = (y * Px + x) * 4;
                    o[i] = (byte)R; o[i + 1] = (byte)G; o[i + 2] = (byte)B; o[i + 3] = (byte)(255f * a);
                }
            return o;
        }

        /// <summary>RGBA32 additive glow around a lit lens; null for Dark (an unpowered switch has no glow).</summary>
        public static byte[] Halo(SwitchLamp lamp)
        {
            byte[] c = HaloRgb[(int)lamp];
            if (c == null) return null;
            var o = new byte[Px * Px * 4];
            float h = Px / 2f;
            for (int y = 0; y < Px; y++)
                for (int x = 0; x < Px; x++)
                {
                    float dx = (x + 0.5f - h) / h, dy = (y + 0.5f - h) / h, r = (float)Math.Sqrt(dx * dx + dy * dy);
                    float a = r >= 1f ? 0f : 0.85f * (1f - r) * (1f - r);
                    int i = (y * Px + x) * 4;
                    o[i] = c[0]; o[i + 1] = c[1]; o[i + 2] = c[2]; o[i + 3] = (byte)(255f * a);
                }
            return o;
        }
    }
}
