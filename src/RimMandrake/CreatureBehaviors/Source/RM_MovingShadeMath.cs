using System;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // LONGSHADE_GPT_ENRICHMENT_1 §2 — "the gloomcast moves shade".
    //
    // The pure arithmetic of a MOVING shade caster: a living creature whose
    // body throws a shadow into RM_MapComponent_ShadeGrid's moving-shade
    // layer. System.Math only, like RM_SunHeatMath, so the offline selftest
    // (Source/SelfTest, Utils/selftest_sun_heat.py) compiles this exact file.
    //
    // The shadow is the creature's body footprint (a square of half-width
    // `radius` round its cell — the body itself is overhead) plus, when the
    // map has a sun vector, every footprint cell cast `length` cells along
    // it with RM_SunHeatMath.CastInto, the same shape every rock throws.
    // With no sun vector the footprint grows by one cell all round instead
    // (the grid's legacy isotropic ring, in spirit).
    //
    // Dirty rectangles: ShadowBounds gives the one rectangle a caster can
    // have written, so the grid clears only the OLD rectangle and writes
    // the NEW one when a caster moves — never a full-map pass.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_MovingShadeMath
    {
        /// <summary>The inclusive rectangle (clipped to the map) that
        /// CastBody can write for a caster at (cx, cz). Returns false when
        /// it lies wholly off the map.</summary>
        public static bool ShadowBounds(int width, int height, int cx, int cz, int radius,
            bool directional, float dirX, float dirZ, float length,
            out int minX, out int minZ, out int maxX, out int maxZ)
        {
            int r = Math.Max(0, radius);
            minX = cx - r;
            maxX = cx + r;
            minZ = cz - r;
            maxZ = cz + r;
            if (directional)
            {
                float norm = (float)Math.Sqrt(dirX * dirX + dirZ * dirZ);
                if (norm >= 1e-4f && length > 0f)
                {
                    // CastInto rounds each half-cell step, so allow one cell
                    // of slack past the exact tip.
                    int ex = (int)Math.Ceiling(Math.Abs(dirX / norm) * length) + 1;
                    int ez = (int)Math.Ceiling(Math.Abs(dirZ / norm) * length) + 1;
                    if (dirX > 0f) { maxX += ex; } else if (dirX < 0f) { minX -= ex; }
                    if (dirZ > 0f) { maxZ += ez; } else if (dirZ < 0f) { minZ -= ez; }
                }
            }
            else
            {
                minX--; minZ--; maxX++; maxZ++;
            }
            minX = Math.Max(0, minX);
            minZ = Math.Max(0, minZ);
            maxX = Math.Min(width - 1, maxX);
            maxZ = Math.Min(height - 1, maxZ);
            return minX <= maxX && minZ <= maxZ;
        }

        /// <summary>Writes one moving caster's shade into a row-major grid
        /// (index = z * width + x), keeping the max of what is there.
        /// depth (0..1) scales the whole shadow.</summary>
        public static void CastBody(float[] grid, int width, int height, int cx, int cz, int radius,
            bool directional, float dirX, float dirZ, float length, float tipShade, float depth)
        {
            if (depth <= 0f)
            {
                return;
            }
            int r = Math.Max(0, radius);
            float d = RM_SunHeatMath.Clamp01(depth);
            if (!directional)
            {
                RM_SunHeatMath.FillRect(grid, width, height, cx - r - 1, cz - r - 1, cx + r + 1, cz + r + 1, d);
                return;
            }
            RM_SunHeatMath.FillRect(grid, width, height, cx - r, cz - r, cx + r, cz + r, d);
            for (int z = cz - r; z <= cz + r; z++)
            {
                for (int x = cx - r; x <= cx + r; x++)
                {
                    if (x < 0 || z < 0 || x >= width || z >= height)
                    {
                        continue;
                    }
                    RM_SunHeatMath.CastInto(grid, width, height, x, z, dirX, dirZ, length, tipShade, d);
                }
            }
        }

        /// <summary>Zeroes an inclusive rectangle (a caster's old shadow).</summary>
        public static void ClearRect(float[] grid, int width, int height, int minX, int minZ, int maxX, int maxZ)
        {
            for (int z = Math.Max(0, minZ); z <= Math.Min(height - 1, maxZ); z++)
            {
                int row = z * width;
                for (int x = Math.Max(0, minX); x <= Math.Min(width - 1, maxX); x++)
                {
                    grid[row + x] = 0f;
                }
            }
        }
    }
}
