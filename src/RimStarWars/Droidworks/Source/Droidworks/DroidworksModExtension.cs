using System.Linq;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// Per-race droid tuning, attached to the race ThingDef.
    /// energyDensity drives catastrophic detonation (state 5): radius and
    /// damage scale with CURRENT stored power x this, never def-time capacity
    /// ("POWER DENSITY explodes, not the fact it's a machine" - owner ruling).
    /// powerFallPerDay: combat droids ~1.0 (daily top-off), protocol ~0.033.
    /// </summary>
    public class DroidworksExtension : DefModExtension
    {
        public float powerFallPerDay = 0.33f;
        public float energyDensity = 0f;      // 0 = never detonates (state 5 unreachable)
        public bool deliberateDenyModule = false; // combat deny-your-parts package
        /// <summary>
        /// The extension that applies to a race: the LAST DroidworksExtension in the list. XML inheritance APPENDS a child's
        /// modExtensions after the parent's, so the race's own copy sorts after the family abstract's inherited one;
        /// GetModExtension&lt;T&gt;() returns the FIRST (the family's) and silently ignores a race-level override.
        /// </summary>
        public static DroidworksExtension OfRace(ThingDef def) =>
            def?.modExtensions?.OfType<DroidworksExtension>().LastOrDefault();

        public int chassisClass = 0;          // 0 labour 1 protocol 2 astromech 3 battle 4 heavy 5 probe 6 power 7 primitive
    }
}
