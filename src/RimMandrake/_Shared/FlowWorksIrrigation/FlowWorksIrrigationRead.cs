using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.Shared
{
    // ════════════════════════════════════════════════════════════════════
    // THE ONE IRRIGATION RULE, read reflection-soft from FlowWorks (source-linked into each mod that waters with it:
    // ExplosiveGrowth's soak, Pyrelands' ash field). FlowWorks' own header names it: "irrigation wants a per-cell soak map".
    //
    //   A FlowWorks DUG cell (depthGrid != 0) holding fluid (fillGrid != 0) waters ITSELF and its 8 neighbours, when the
    //   excavation's active fluid is one the caller accepts. Natural liquid (rivers, lakes) reads through as SUPERDEEP with
    //   depth-grid 0 and is deliberately NOT irrigation.
    //
    // FlowWorks is never a dependency: with it absent, TryGrids returns false and the route is silent.
    // ════════════════════════════════════════════════════════════════════
    public static class FlowWorksIrrigationRead
    {
        private static bool resolved;
        private static Type excavationType;
        private static FieldInfo depthGridField, fillGridField;
        private static PropertyInfo activeFluidProp;

        public static bool Available
        {
            get { Resolve(); return excavationType != null; }
        }

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            try
            {
                excavationType = AccessTools.TypeByName("RimMandrake.FlowWorks.RM_MapComponent_Excavation");
                if (excavationType != null)
                {
                    depthGridField = AccessTools.Field(excavationType, "depthGrid");
                    fillGridField = AccessTools.Field(excavationType, "fillGrid");
                    activeFluidProp = AccessTools.Property(excavationType, "ActiveFluid");
                }
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake] FlowWorks irrigation reflection failed; irrigation reads disabled: " + e.Message);
                excavationType = null;
            }
        }

        /// <summary>The map's FlowWorks dig and fill grids (same length), or false when FlowWorks is absent, the map has no
        /// excavation component, or its active fluid is not accepted (a null fluid set accepts any).</summary>
        public static bool TryGrids(Map map, ICollection<string> acceptedFluids, out byte[] depth, out byte[] fill)
        {
            depth = null;
            fill = null;
            Resolve();
            if (excavationType == null || map == null) return false;
            MapComponent ex = null;
            List<MapComponent> list = map.components;
            for (int i = 0; i < list.Count; i++)
            {
                if (list[i] != null && excavationType.IsInstanceOfType(list[i])) { ex = list[i]; break; }
            }
            if (ex == null) return false;
            if (!(depthGridField?.GetValue(ex) is byte[] d) || !(fillGridField?.GetValue(ex) is byte[] f) || d.Length != f.Length) return false;
            if (acceptedFluids != null && activeFluidProp?.GetValue(ex) is Def fluid && !acceptedFluids.Contains(fluid.defName)) return false;
            depth = d;
            fill = f;
            return true;
        }

        /// <summary>The cell rule: a dug cell holding fluid irrigates itself and its 8 neighbours.</summary>
        public static bool IsSource(byte[] depth, byte[] fill, int index)
        {
            return depth[index] != 0 && fill[index] != 0;
        }

        /// <summary>Call `water` on the source cell and each in-bounds neighbour.</summary>
        public static void ForWatered(Map map, IntVec3 source, Action<IntVec3> water)
        {
            water(source);
            for (int d = 0; d < 8; d++)
            {
                IntVec3 nb = source + GenAdj.AdjacentCells[d];
                if (nb.InBounds(map)) water(nb);
            }
        }
    }
}
