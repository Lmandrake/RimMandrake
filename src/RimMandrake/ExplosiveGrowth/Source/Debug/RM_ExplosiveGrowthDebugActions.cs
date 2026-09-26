using LudeonTK;
using RimWorld;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    // Bridge/dev-mode test surface: a live proof of the charge cycle should not
    // depend on waiting for a flood.
    public static class RM_ExplosiveGrowthDebugActions
    {
        private const string CAT = "RMExplosiveGrowth";

        [DebugAction(CAT, "Soak 5x5 here", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void SoakHere()
        {
            Map map = Find.CurrentMap;
            IntVec3 center = UI.MouseCell();
            int n = ExplosiveGrowthAPI.SoakCells(map, GenRadial.RadialCellsAround(center, 2.9f, true), 0);
            Log.Message("[RMExplosiveGrowthDebug] soaked " + n + " cells around " + center);
        }

        [DebugAction(CAT, "Suppress r2 here", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void SuppressHere()
        {
            ExplosiveGrowthAPI.Suppress(Find.CurrentMap, UI.MouseCell(), 2, 60000);
        }

        [DebugAction(CAT, "Charge all charging plants to 0.9", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ChargeAll()
        {
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(Find.CurrentMap);
            Log.Message("[RMExplosiveGrowthDebug] raised " + (comp?.DebugForceCharge(0.9f) ?? 0) + " charges to 0.9");
        }

        [DebugAction(CAT, "Report state (current map)", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void Report()
        {
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(Find.CurrentMap);
            Log.Message("[RMExplosiveGrowthDebug] " + (comp?.DebugReport() ?? "no component on this map"));
        }

        [DebugAction(CAT, "Fire top of plant here", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void FireHere()
        {
            Map map = Find.CurrentMap;
            Plant p = UI.MouseCell().GetPlant(map);
            if (p == null) return;
            RM_TopResolver.Fire(p, RM_ExplosiveGrowthRegistry.For(p.def), RM_MapComponent_ExplosiveGrowth.For(map));
        }
    }
}
