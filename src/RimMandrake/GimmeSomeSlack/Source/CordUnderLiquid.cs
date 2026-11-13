using System;
using System.Collections.Generic;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack
{
    /// <summary>
    /// RIMMANDRAKE_SINK_HOSES_AND_OVERLAYS_TORCHES_BURN_IN_TAR (owner 2026-11-12: "The wires are also above the items and
    /// furniture otherwise"): a cord lying on the floor of a FlowWorks pit is seen through the liquid over it by FlowWorks' one
    /// under-liquid law, at the height it runs at (the pit floor). FlowWorks is optional: its RM_SubmergeDraw.FloorSeen is
    /// found by name once; without it every cord shows whole. A cord under liquid does not ripple in the wind
    /// (RM_MapComponent_CordGraph.RipplesNow), so it is printed by SectionLayer_RM_MessyCords, which fades it here.
    /// </summary>
    internal static class CordUnderLiquid
    {
        /// <summary>Alpha steps a faded cord material is cached at.</summary>
        public const int Steps = 16;

        private static Func<Map, int, int, float> floorSeen;
        private static bool resolved;
        private static readonly Dictionary<long, Material> faded = new Dictionary<long, Material>();

        /// <summary>How much of a cord on the floor at (<paramref name="x"/>, <paramref name="z"/>) shows (1 without FlowWorks).</summary>
        public static float SeenAt(Map map, double x, double z)
        {
            if (!resolved)
            {
                resolved = true;
                System.Reflection.MethodInfo m = AccessTools.Method("RimMandrake.FlowWorks.RM_SubmergeDraw:FloorSeen", new[] { typeof(Map), typeof(int), typeof(int) });
                if (m != null && m.ReturnType == typeof(float))
                {
                    floorSeen = (Func<Map, int, int, float>)Delegate.CreateDelegate(typeof(Func<Map, int, int, float>), m);
                }
            }
            if (floorSeen == null || map == null)
            {
                return 1f;
            }
            float a = floorSeen(map, (int)Math.Floor(x), (int)Math.Floor(z));
            return a < 0f ? 0f : a > 1f ? 1f : a;
        }

        /// <summary>The cached alpha step of what shows at (<paramref name="x"/>, <paramref name="z"/>): Steps = whole, 0 = hidden.</summary>
        public static int StepAt(Map map, double x, double z) => (int)(SeenAt(map, x, z) * Steps + 0.5f);

        /// <summary><paramref name="mat"/> at alpha <paramref name="q"/>/Steps (same texture, shader and queue); the material
        /// itself when whole; null when hidden or texture-less.</summary>
        public static Material Faded(Material mat, int q)
        {
            if (mat == null || q >= Steps)
            {
                return mat;
            }
            if (q <= 0 || mat.mainTexture == null)
            {
                return null;
            }
            long key = ((long)mat.GetInstanceID() << 8) | (long)q;
            if (faded.TryGetValue(key, out Material m) && m != null)
            {
                return m;
            }
            Color c = mat.color;
            m = MaterialPool.MatFrom(new MaterialRequest(mat.mainTexture, mat.shader, new Color(c.r, c.g, c.b, c.a * q / Steps))
                { renderQueue = mat.renderQueue });
            if (CordMaterials.IsLod(mat)) CordMaterials.AlsoLod(m);   // drawn far out only, like the strand it copies
            faded[key] = m;
            return m;
        }
    }
}
