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

        [DebugAction(CAT, "Recede flood NOW (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void RecedeNow()
        {
            Map map = Find.CurrentMap;
            if (map == null) return;
            RM_MapComponent_CanyonFlood comp = map.GetComponent<RM_MapComponent_CanyonFlood>();
            if (comp == null) { Log.Error("[RMFloodedCanyonDebug] no RM_MapComponent_CanyonFlood on this map."); return; }
            comp.DebugRecedeSoon();
            Log.Message("[RMFloodedCanyonDebug] recede armed for next tick. " + comp.DebugStateReport());
        }

        // CRACKEDLANDS_MECHANICS_BUILD_1 verify: a STATE read of the seams on
        // the map (count per tier), so "fresh seams after a recede" is a
        // before/after number, never a screenshot hunt.
        [DebugAction(CAT, "Report fossil seams (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ReportSeams()
        {
            Map map = Find.CurrentMap;
            if (map == null) return;
            int imp = map.listerThings.ThingsOfDef(RM_FloodedCanyonDefOf.RM_FossilSeam_Impression).Count;
            int skel = map.listerThings.ThingsOfDef(RM_FloodedCanyonDefOf.RM_FossilSeam_Skeleton).Count;
            int uniq = map.listerThings.ThingsOfDef(RM_FloodedCanyonDefOf.RM_FossilSeam_Unique).Count;
            Log.Message("[RMFloodedCanyonDebug] fossil seams: impression=" + imp + " skeleton=" + skel
                + " unique=" + uniq + " biome=" + map.Biome.defName);
        }
    }
}
