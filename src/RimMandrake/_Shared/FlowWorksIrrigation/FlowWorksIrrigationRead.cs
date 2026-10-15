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
    //   A FlowWorks DUG cell (depthGrid != 0) holding fluid (fillGrid != 0) waters ITSELF and its 8 neighbours, when THAT
    //   CELL's liquid (fluidGrid + fluidPalette; an unrecorded cell takes the map's ActiveFluid) is one the caller accepts.
    //   FLOWWORKS_IRRIGATION_PER_CELL_FLUID (2026-10-15): the old read checked one map-wide ActiveFluid, so a tar or oil canal
    //   on a water map watered crops as water. The per-cell rule is FlowWorksIrrigationKernel (engine-free, selftested).
    //   Natural liquid (rivers, lakes) reads through as SUPERDEEP with depth-grid 0 and is deliberately NOT irrigation.
    //
    // FlowWorks is never a dependency: with it absent, TryGrids returns false and the route is silent.
    // ════════════════════════════════════════════════════════════════════
    public static class FlowWorksIrrigationRead
    {
        private static bool resolved;
        private static Type excavationType;
        private static FieldInfo depthGridField, fillGridField, fluidGridField, fluidPaletteField;
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
                    // Per-cell identity (LIQUID_BODY_FLUID_IDENTITY_1). Absent on an older FlowWorks: every cell then takes ActiveFluid.
                    fluidGridField = AccessTools.Field(excavationType, "fluidGrid");
                    fluidPaletteField = AccessTools.Field(excavationType, "fluidPalette");
                    activeFluidProp = AccessTools.Property(excavationType, "ActiveFluid");
                }
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake] FlowWorks irrigation reflection failed; irrigation reads disabled: " + e.Message);
                excavationType = null;
            }
        }

        /// <summary>One map's irrigation read: the FlowWorks grids plus which liquids the caller accepts, per cell.</summary>
        public sealed class Grids
        {
            internal byte[] depth, fill, fluid;
            internal bool[] keyAccepted;
            internal bool defaultAccepted;

            public int Length => depth.Length;

            /// <summary>The cell rule: a dug cell holding an accepted liquid irrigates itself and its 8 neighbours.</summary>
            public bool IsSource(int index)
            {
                int key = fluid != null && fluid.Length == depth.Length ? fluid[index] : 0;
                return FlowWorksIrrigationKernel.IsSource(depth[index], fill[index], key, keyAccepted, defaultAccepted);
            }
        }

        /// <summary>The map's FlowWorks irrigation read, or false when FlowWorks is absent, the map has no excavation component, or
        /// no liquid on it is accepted (a null accepted set accepts any). Acceptance is decided PER CELL by Grids.IsSource.</summary>
        public static bool TryGrids(Map map, ICollection<string> acceptedFluids, out Grids grids)
        {
            grids = null;
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
            string active = (activeFluidProp?.GetValue(ex) as Def)?.defName;
            bool defaultOk = FlowWorksIrrigationKernel.DefaultAccepted(active, acceptedFluids);
            byte[] fl = fluidGridField?.GetValue(ex) as byte[];
            List<string> names = new List<string>();
            if (fl != null && fluidPaletteField?.GetValue(ex) is System.Collections.IList palette)
            {
                for (int i = 0; i < palette.Count; i++) names.Add((palette[i] as Def)?.defName);
            }
            bool[] keys = FlowWorksIrrigationKernel.AcceptedKeys(names, acceptedFluids, defaultOk);
            if (FlowWorksIrrigationKernel.NothingAccepted(keys, defaultOk)) return false;
            grids = new Grids { depth = d, fill = f, fluid = fl != null && fl.Length == d.Length ? fl : null, keyAccepted = keys, defaultAccepted = defaultOk };
            return true;
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
