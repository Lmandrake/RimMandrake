using LudeonTK;
using Verse;

namespace RimMandrake.FloodedCanyon
{
    // Bridge/dev-mode reachable test surface, same pattern as the sibling
    // FluidCanals mod's own FluidCanalsDebugActions: a live proof of the
    // flood cycle should not depend on waiting out floodPeriodDays
    // (20 in-game days by default) in real time.
    public static class RM_FloodedCanyonDebugActions
    {
        private const string CAT = "RMFloodedCanyon";

        [DebugAction(CAT, "Arm chime + flood soon (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ArmSoon()
        {
            Map map = Find.CurrentMap;
            if (map == null) return;
            RM_MapComponent_CanyonFlood comp = map.GetComponent<RM_MapComponent_CanyonFlood>();
            if (comp == null) { Log.Error("[RMFloodedCanyonDebug] no RM_MapComponent_CanyonFlood on this map."); return; }
            comp.DebugArmFloodSoon();
            Log.Message("[RMFloodedCanyonDebug] chime armed for next tick. " + comp.DebugStateReport());
        }

        [DebugAction(CAT, "Start flood NOW (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void StartNow()
        {
            Map map = Find.CurrentMap;
            if (map == null) return;
            RM_MapComponent_CanyonFlood comp = map.GetComponent<RM_MapComponent_CanyonFlood>();
            if (comp == null) { Log.Error("[RMFloodedCanyonDebug] no RM_MapComponent_CanyonFlood on this map."); return; }
            comp.DebugStartFloodNow();
            Log.Message("[RMFloodedCanyonDebug] flood forced. " + comp.DebugStateReport());
        }

        [DebugAction(CAT, "Report flood state (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void Report()
        {
            Map map = Find.CurrentMap;
            if (map == null) return;
            RM_MapComponent_CanyonFlood comp = map.GetComponent<RM_MapComponent_CanyonFlood>();
            if (comp == null) { Log.Error("[RMFloodedCanyonDebug] no RM_MapComponent_CanyonFlood on this map."); return; }
            Log.Message("[RMFloodedCanyonDebug] " + comp.DebugStateReport());
        }
    }
}
