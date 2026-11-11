using System;
using System.Collections.Generic;
using System.Linq;

// TANK_DEBUG_BUILD_FILL_AT_WILL. Verse-free on purpose: compiled into the offline SelfTest (SelfTest/TankDebugChecks.cs).
namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>God-mode tank fill / empty: the pure rules. Fill REPLACES whatever a tank held (a container holding another liquid
    /// is overwritten, the old contents are recorded as removed); fill amount = capacity exactly. Every debug add / remove is a
    /// recorded source / sink, shown in the L0 ledger line as dbgAdded / dbgRemoved (session, decilitres).</summary>
    public static class RM_TankDebugMath
    {
        public const string DefaultLiquidDefName = "RM_Liquid_FreshWater";

        /// <summary>Picker order: the default (water) first, the rest alphabetical; unknown default = plain alphabetical.</summary>
        public static List<string> PickerOrder(IEnumerable<string> defNames)
        {
            List<string> all = defNames.Where(n => !string.IsNullOrEmpty(n)).Distinct().OrderBy(n => n, StringComparer.Ordinal).ToList();
            if (all.Remove(DefaultLiquidDefName)) all.Insert(0, DefaultLiquidDefName);
            return all;
        }

        /// <summary>Units a "fill to max" leaves in a tank: its capacity, never negative.</summary>
        public static int FillUnits(int capacity) => capacity > 0 ? capacity : 0;

        public static long DebugAddedUnits;
        public static long DebugRemovedUnits;

        /// <summary>Record a fill: <paramref name="had"/> units were overwritten (sink), the tank now holds <paramref name="now"/> (source).</summary>
        public static void RecordFill(int had, int now)
        {
            DebugRemovedUnits += Math.Max(0, had);
            DebugAddedUnits += Math.Max(0, now);
        }

        public static void RecordEmpty(int had) => DebugRemovedUnits += Math.Max(0, had);
    }
}
