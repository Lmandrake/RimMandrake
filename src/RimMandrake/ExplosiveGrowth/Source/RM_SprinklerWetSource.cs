using System.Collections.Generic;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    /// <summary>
    /// SPRINKLER_HEADS_BUILD_PUMP_REQUIRED (design sprinklers_design_2026-10-16 §4, step 4): the "sprinkled" row of the one wet
    /// registry. A cell is wet while a FlowWorks sprinkler's last paid spray covers it (W3: continuous while it runs; GM1: dry
    /// within one pulse when it stops) and the plant accepts the sprayed liquid (T2). A fruiting crop spends the cell (EC3).
    /// Read reflection-soft through _Shared/FlowWorksSprinklerRead.cs; registered at startup through the RM_WetSources seam.
    /// </summary>
    public sealed class RM_SprinklerWetSource : IRM_WetSource
    {
        public string Key => "sprinkled";

        public bool Enabled => ExplosiveGrowthSettings.sprinklersEnabled && RimMandrake.Shared.FlowWorksSprinklerRead.Available;

        public bool WetFor(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now)
        {
            string key = RimMandrake.Shared.FlowWorksSprinklerRead.WetKey(comp.map, c);
            return key != null && accepts.Contains(key);
        }

        public bool Consume(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now)
            => RimMandrake.Shared.FlowWorksSprinklerRead.Spend(comp.map, c);
    }

    [StaticConstructorOnStartup]
    public static class RM_SprinklerWetSourceRegistration
    {
        static RM_SprinklerWetSourceRegistration()
        {
            RM_WetSources.Register(new RM_SprinklerWetSource());
        }
    }
}
