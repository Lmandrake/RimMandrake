// PIT_SPIKES_FIX_OVER_WALL_AND_SUBMERGE (owner 2026-10-24: "They should not be showing drawn over the paler walls, right?
// ... They should be shown as submerged rapidly."). Offline checks on RM_SpikeDrawMath: every laid stake stays on the floor
// the pit's walls leave visible (the bands are recomputed here from RM_WallFaceMath, not from FloorRect), the water fade,
// the stake library, and parity with the Python mirror (Tools/fw_scenes_spikes.py) that renders the owner's sheet.
// Each case has a can-fail. NOT proven here: the mesh on screen in a live pit (Building_RM_Spikes.DrawAt); live check owed.
using System;
using System.Collections.Generic;
using System.IO;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class SpikeDrawChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>The wall bands of a cell as RM_ExcavationWalls draws them dry (face and outline), as (x0, z0, x1, z1)
        /// rects; a stake quad overlapping any of them is drawn over the wall.</summary>
        private static List<float[]> Bands(int d, int n, int s, int w, int e, bool faces, bool outline)
        {
            var b = new List<float[]>();
            if (!faces) return b;
            float h = RM_WallFaceMath.NorthFaceHeight(RM_WallFaceMath.ExposedDrop(d, n, 0));
            float ww = RM_WallFaceMath.SideFaceWidth(RM_WallFaceMath.ExposedDrop(d, w, 0));
            float ew = RM_WallFaceMath.SideFaceWidth(RM_WallFaceMath.ExposedDrop(d, e, 0));
            if (h > 0) b.Add(new[] { 0f, 1f - h, 1f, 1f });
            if (ww > 0) b.Add(new[] { 0f, 0f, ww, 1f });
            if (ew > 0) b.Add(new[] { 1f - ew, 0f, 1f, 1f });
            if (outline)
            {
                if (d - s > 0) b.Add(new[] { 0f, 0f, 1f, RM_WallFaceMath.SouthLining(d - s) });
                if (d - n > 0) b.Add(new[] { 0f, 1f - RM_WallFaceMath.RimLine, 1f, 1f });
                if (d - w > 0) b.Add(new[] { 0f, 0f, RM_WallFaceMath.SideLine, 1f });
                if (d - e > 0) b.Add(new[] { 1f - RM_WallFaceMath.SideLine, 0f, 1f, 1f });
            }
            return b;
        }

        private static bool Overlaps(float[] q, float[] band) =>
            q[0] < band[2] - 1e-5f && q[0] + q[2] > band[0] + 1e-5f && q[1] < band[3] - 1e-5f && q[1] + q[3] > band[1] + 1e-5f;

        /// <summary>The number of stake quads of a layout that overlap a wall band (0 = clean).</summary>
        private static int OverWall(List<float> quads, List<float[]> bands)
        {
            int bad = 0;
            for (int i = 0; i < quads.Count; i += RM_SpikeDrawMath.Out)
            {
                var q = new[] { quads[i], quads[i + 1], quads[i + 2], quads[i + 3] };
                foreach (float[] band in bands)
                {
                    if (Overlaps(q, band)) { bad++; break; }
                }
            }
            return bad;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Spikes_never_over_the_wall_any_neighbours", () =>
            {
                int layouts = 0, stakes = 0;
                var quads = new List<float>();
                int[] levels = { 0, 2, 4, 5, 6, 8, 12 };
                for (int v = 0; v < RM_SpikeStakes.Variants.Length; v++)
                foreach (int d in new[] { 4, 6, 8 })
                foreach (int n in levels)
                foreach (int s in levels)
                foreach (int w in levels)
                foreach (int e in levels)
                for (int flags = 0; flags < 3; flags++)
                {
                    bool faces = flags != 2, outline = flags == 0;
                    RM_SpikeDrawMath.FloorRect(d, n, s, w, e, faces, outline, out float x0, out float z0, out float x1, out float z1);
                    int seed = d * 7919 + n * 31 + s * 17 + w * 5 + e;
                    int k = RM_SpikeDrawMath.Layout(v, seed, x0, z0, x1, z1, quads);
                    Assert(k * RM_SpikeDrawMath.Out == quads.Count, "Layout's count matches its output");
                    Assert(k > 0, "a 2 m+ pit floor always gets stakes: d" + d + " n" + n + " s" + s + " w" + w + " e" + e);
                    int bad = OverWall(quads, Bands(d, n, s, w, e, faces, outline));
                    Assert(bad == 0, bad + " stakes over the wall: v" + v + " d" + d + " n" + n + " s" + s + " w" + w + " e" + e + " flags" + flags);
                    for (int i = 0; i < quads.Count; i += RM_SpikeDrawMath.Out)
                    {
                        Assert(quads[i] >= 0f && quads[i + 1] >= 0f && quads[i] + quads[i + 2] <= 1f && quads[i + 1] + quads[i + 3] <= 1f,
                            "stake inside its cell");
                    }
                    layouts++;
                    stakes += k;
                }
                Assert(layouts > 1000 && stakes > layouts * 10, "sweep covered " + layouts + " layouts / " + stakes + " stakes");
                // can-fail: the shipped drawing (the whole sprite on the 1x1 cell) is over the far wall of a D4 pit
                var whole = new List<float> { 0f, 0f, 1f, 1f, 0f, 0f, 1f, 1f };
                Assert(OverWall(whole, Bands(8, 0, 8, 8, 8, true, true)) == 1, "can-fail: the old whole-cell sprite reads as over the wall");
            });

            Case("Spikes_fill_the_open_floor_at_the_art_density", () =>
            {
                var quads = new List<float>();
                for (int v = 0; v < RM_SpikeStakes.Variants.Length; v++)
                {
                    RM_SpikeDrawMath.FloorRect(8, 8, 8, 8, 8, true, true, out float x0, out float z0, out float x1, out float z1);
                    Assert(x0 == 0f && z0 == 0f && x1 == 1f && z1 == 1f, "open floor (no walls) is the whole cell");
                    int k = RM_SpikeDrawMath.Layout(v, 99, x0, z0, x1, z1, quads);
                    float want = 1f / (RM_SpikeStakes.Pitch[v, 0] * RM_SpikeStakes.Pitch[v, 1]);
                    Assert(k > want * 0.7f && k < want * 1.3f, "variant " + v + ": " + k + " stakes on an open cell, art density " + want.ToString("0.0"));
                    // the far-first order: z never rises down the list
                    for (int i = RM_SpikeDrawMath.Out; i < quads.Count; i += RM_SpikeDrawMath.Out)
                    {
                        Assert(quads[i + 1] <= quads[i + 1 - RM_SpikeDrawMath.Out], "stakes sorted far (north) first");
                    }
                }
                // can-fail: a rect smaller than the margins lays nothing
                Assert(RM_SpikeDrawMath.Layout(0, 1, 0.4f, 0.4f, 0.41f, 0.9f, quads) == 0 && quads.Count == 0, "can-fail: no room, no stakes");
            });

            Case("Spikes_submerge_fast", () =>
            {
                Assert(RM_SpikeDrawMath.SubmergedAlpha(0) == 1f, "dry: fully drawn");
                Assert(Math.Abs(RM_SpikeDrawMath.SubmergedAlpha(1) - 0.25f) < 1e-6f, "0.5 m: a quarter");
                Assert(RM_SpikeDrawMath.SubmergedAlpha(2) == 0f && RM_SpikeDrawMath.SubmergedAlpha(3) == 0f && RM_SpikeDrawMath.SubmergedAlpha(40) == 0f,
                    "gone from 1 m");
                Assert(RM_SpikeDrawMath.SubmergedAlpha(-1) == 1f, "a negative fill reads as dry");
                // can-fail: a linear fade would still show a half-strength bed under 0.5 m
                Assert(RM_SpikeDrawMath.SubmergedAlpha(1) < 0.5f, "can-fail: faster than linear");
            });

            Case("Spikes_variant_from_texture_name", () =>
            {
                Assert(RM_SpikeDrawMath.VariantOf("RM_Spikes_a") == 0 && RM_SpikeDrawMath.VariantOf("RM_Spikes_c") == 2, "a..c");
                Assert(RM_SpikeDrawMath.VariantOf("RM_Spikes_z") == -1 && RM_SpikeDrawMath.VariantOf("RM_Spikes") == -1
                    && RM_SpikeDrawMath.VariantOf(null) == -1, "can-fail: an unknown name falls back");
                for (int v = 0; v < RM_SpikeStakes.Variants.Length; v++)
                {
                    float[] lib = RM_SpikeStakes.Stakes[v];
                    Assert(lib.Length >= 10 * RM_SpikeStakes.Stride && lib.Length % RM_SpikeStakes.Stride == 0, "variant " + v + " has a stake library");
                    for (int i = 0; i < lib.Length; i += RM_SpikeStakes.Stride)
                    {
                        Assert(lib[i] > 0f && lib[i + 1] > 0.1f && lib[i + 1] < 0.25f && lib[i + 4] > lib[i + 2] && lib[i + 5] > lib[i + 3],
                            "a stake is one stake (0.1..0.25 cell tall) with a real UV box");
                    }
                }
            });

            Case("Spikes_parity_fixture_matches_python", () =>
            {
                // Tools/fw_scenes_spikes.py PARITY_HASHES / PARITY_LAYOUT; selftest_fw_offline_art.py asserts the same numbers.
                Assert(RM_SpikeDrawMath.Hash(0, 0) == 0u && RM_SpikeDrawMath.Hash(12345, 7) == 2836592880u
                    && RM_SpikeDrawMath.Hash(-3, 99) == 1249282371u, "hash parity");
                var quads = new List<float>();
                int k = RM_SpikeDrawMath.Layout(1, 42, 0.04f, 0.065f, 0.96f, 0.5f, quads);
                Assert(k == 26, "layout count parity: " + k);
                float[] first = { 0.343608f, 0.317331f, 0.046875f, 0.152344f, 0.375000f, 0.632812f, 0.421875f, 0.937500f };
                float[] last = { 0.890793f, 0.075f, 0.050781f, 0.164062f, 0.281250f, 0.609375f, 0.332031f, 0.937500f };
                int o = (k - 1) * RM_SpikeDrawMath.Out;
                for (int i = 0; i < RM_SpikeDrawMath.Out; i++)
                {
                    Assert(Math.Abs(quads[i] - first[i]) < 1e-4f, "first quad [" + i + "] " + quads[i] + " vs python " + first[i]);
                    Assert(Math.Abs(quads[o + i] - last[i]) < 1e-4f, "last quad [" + i + "] " + quads[o + i] + " vs python " + last[i]);
                }
            });
        }
    }
}
