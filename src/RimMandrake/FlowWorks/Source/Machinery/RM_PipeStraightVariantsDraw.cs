using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>SCRAPPER_PIPE_REDRAW_ASKED_TWICE_NOW: a straight universal-pipe cell whose look ships a straights sheet draws one
    /// of its variants, picked by <see cref="PipeStraightVariants.Pick"/> from the cell alone (stable across redraws, loads and
    /// saves; nothing stored). Every other cell, look and graphic prints exactly as vanilla Graphic_Linked does (the prefix
    /// returns true). The variant prints the same 1x1 plane at the same centre as vanilla, with UVs into the sheet instead of the
    /// atlas, in the atlas material's shader and colour, then the shadow as vanilla does.</summary>
    [RimMandrake.Shared.PatchFeature("Universal pipe: straight-run variants", typeof(RM_MachinerySettings), "pipeStraightVariants")]
    [HarmonyPatch(typeof(Graphic_Linked), nameof(Graphic_Linked.Print))]
    internal static class Patch_Pipe_StraightVariants
    {
        private static readonly Dictionary<string, Texture2D> sheets = new Dictionary<string, Texture2D>();
        private static readonly Dictionary<(Texture2D, Material), Material> mats = new Dictionary<(Texture2D, Material), Material>();
        private static readonly float[] uv = new float[8];
        private static readonly Vector2[] uvs = new Vector2[4];

        /// <summary>State read: variant planes printed since load (probe / live look).</summary>
        public static int printed;

        private static bool Prefix(Graphic_Linked __instance, SectionLayer layer, Thing thing, float extraRotation)
        {
            if (!RM_MachinerySettings.pipeStraightVariants || thing == null || extraRotation != 0f || !thing.Spawned
                || !RM_LiquidNet.IsPipe(thing)) return true;
            Graphic sub = __instance.SubGraphic;
            string sheetPath = PipeStraightVariants.SheetPathFor(sub?.path);
            if (sheetPath == null) return true;
            IntVec3 c = thing.Position;
            int mask = 0;
            if (__instance.ShouldLinkWith(c + IntVec3.North, thing)) mask |= 1;
            if (__instance.ShouldLinkWith(c + IntVec3.East, thing)) mask |= 2;
            if (__instance.ShouldLinkWith(c + IntVec3.South, thing)) mask |= 4;
            if (__instance.ShouldLinkWith(c + IntVec3.West, thing)) mask |= 8;
            if (!PipeStraightVariants.IsStraight(mask)) return true;
            int k = PipeStraightVariants.Pick(c.x, c.z);
            if (k == 0) return true;
            Material m = VariantMat(sheetPath, sub.MatSingleFor(thing));
            if (m == null) return true;
            PipeStraightVariants.Uvs(k, mask == 10, uv);
            for (int i = 0; i < 4; i++) uvs[i] = new Vector2(uv[2 * i], uv[2 * i + 1]);
            Printer_Plane.PrintPlane(layer, thing.TrueCenter(), Vector2.one, m, 0f, false, uvs);
            __instance.ShadowGraphic?.Print(layer, thing, 0f);   // as vanilla Graphic_Linked.Print (no pipe look casts one today)
            printed++;
            return false;
        }

        /// <summary>The look's straights sheet in the atlas material's shader and colour; null when the look ships no sheet.</summary>
        private static Material VariantMat(string sheetPath, Material atlas)
        {
            if (atlas == null) return null;
            if (!sheets.TryGetValue(sheetPath, out Texture2D tex))
            {
                tex = ContentFinder<Texture2D>.Get(sheetPath, false);
                sheets[sheetPath] = tex;
            }
            if (tex == null) return null;
            if (!mats.TryGetValue((tex, atlas), out Material m))
            {
                m = MaterialPool.MatFrom(new MaterialRequest(tex, atlas.shader, atlas.color));
                mats[(tex, atlas)] = m;
            }
            return m;
        }
    }
}
