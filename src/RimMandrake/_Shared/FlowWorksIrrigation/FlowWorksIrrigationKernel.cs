using System;
using System.Collections.Generic;

namespace RimMandrake.Shared
{
    /// <summary>
    /// The engine-free half of FlowWorksIrrigationRead (no Verse, no Harmony), so an offline selftest compiles THIS file
    /// (Pyrelands/Source/SelfTest/Fuzz). FLOWWORKS_IRRIGATION_PER_CELL_FLUID (2026-10-15): FlowWorks records the liquid PER CELL
    /// (fluidGrid: 0 = unrecorded, else 1 + an index into fluidPalette; an unrecorded cell or a null palette entry takes the map's
    /// ActiveFluid, exactly as RM_MapComponent_Excavation reads `FluidAt(c) ?? ActiveFluid`). The old reader checked only the
    /// map-wide ActiveFluid, so a canal of tar or oil on a water map watered crops as water.
    /// </summary>
    public static class FlowWorksIrrigationKernel
    {
        /// <summary>Per palette key (index k-1), whether the caller accepts that liquid. A null palette entry is the map default.
        /// A null accepted set accepts every liquid.</summary>
        public static bool[] AcceptedKeys(IList<string> paletteDefNames, ICollection<string> accepted, bool defaultAccepted)
        {
            int n = paletteDefNames?.Count ?? 0;
            var keys = new bool[n];
            for (int i = 0; i < n; i++)
            {
                string name = paletteDefNames[i];
                keys[i] = name == null ? defaultAccepted : (accepted == null || accepted.Contains(name));
            }
            return keys;
        }

        /// <summary>Whether the map default (ActiveFluid) is accepted. A null accepted set accepts any; a null default (no FlowWorks
        /// fluid resolved) is accepted only by a null set.</summary>
        public static bool DefaultAccepted(string activeFluidDefName, ICollection<string> accepted)
        {
            return accepted == null || (activeFluidDefName != null && accepted.Contains(activeFluidDefName));
        }

        /// <summary>The cell rule: a DUG cell (depth != 0) holding liquid (fill != 0) of an accepted kind irrigates itself and its 8
        /// neighbours. fluidKey 0, or a key past the palette, is the map default.</summary>
        public static bool IsSource(byte depth, byte fill, int fluidKey, bool[] keyAccepted, bool defaultAccepted)
        {
            if (depth == 0 || fill == 0)
            {
                return false;
            }
            if (fluidKey <= 0 || keyAccepted == null || fluidKey > keyAccepted.Length)
            {
                return defaultAccepted;
            }
            return keyAccepted[fluidKey - 1];
        }

        /// <summary>True when no cell can ever be a source (nothing accepted at all), so a reader may skip the map.</summary>
        public static bool NothingAccepted(bool[] keyAccepted, bool defaultAccepted)
        {
            if (defaultAccepted) return false;
            if (keyAccepted != null) for (int i = 0; i < keyAccepted.Length; i++) if (keyAccepted[i]) return false;
            return true;
        }
    }
}
