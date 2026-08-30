using Verse;

namespace Droidworks
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
        public int chassisClass = 0;          // 0 labour 1 protocol 2 astromech 3 battle 4 heavy 5 probe 6 power
    }
}
