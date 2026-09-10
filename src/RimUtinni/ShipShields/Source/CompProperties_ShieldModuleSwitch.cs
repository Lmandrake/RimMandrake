using System.Collections.Generic;
using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    public class CompProperties_ShieldModuleSwitch : CompProperties
    {
        public ShieldFieldMode defaultMode = ShieldFieldMode.Bubble;
        public List<ShieldModuleMapping> moduleMappings = new List<ShieldModuleMapping>();

        public CompProperties_ShieldModuleSwitch()
        {
            compClass = typeof(CompShieldModuleSwitch);
        }
    }
}
