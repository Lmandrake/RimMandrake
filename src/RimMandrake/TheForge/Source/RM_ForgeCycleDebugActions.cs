using LudeonTK;
using Verse;

namespace RimMandrake.TheForge
{
    // FORGE_CYCLE_MECHANICS_1 — the quicktest surface. The item's criterion
    // is "full cycle observable in a quicktest via state reads"; a real
    // cycle runs ~5 in-game days, so these step it deterministically and
    // print the counters (phase, crust cells, gardens, melt losses). Same
    // pattern as RM_FloodedCanyonDebugActions.
    public static class RM_ForgeCycleDebugActions
    {
        private const string CAT = "RMTheForge";

        [DebugAction(CAT, "Forge cycle: report state (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void Report()
        {
            RM_GameCondition_ForgeCycle cycle = RM_ForgeCycleUtility.CycleOn(Find.CurrentMap);
            if (cycle == null)
            {
                Log.Message("[RMTheForgeDebug] no RM_GameCondition_ForgeCycle active on this map.");
                return;
            }
            Log.Message("[RMTheForgeDebug] " + cycle.DebugStateReport());
        }

        [DebugAction(CAT, "Forge cycle: advance one phase (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void Advance()
        {
            RM_GameCondition_ForgeCycle cycle = RM_ForgeCycleUtility.CycleOn(Find.CurrentMap);
            if (cycle == null)
            {
                Log.Error("[RMTheForgeDebug] no RM_GameCondition_ForgeCycle active on this map.");
                return;
            }
            cycle.DebugAdvancePhase();
            Log.Message("[RMTheForgeDebug] advanced. " + cycle.DebugStateReport());
        }
    }
}
