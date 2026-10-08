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

        // CRACKEDLANDS_GPT_ENRICHMENT_1 verify: the recede feast and the
        // floodline salvage as a state read (cohort / migrants / salvage
        // counts and their clocks), never a screenshot hunt.
        [DebugAction(CAT, "Report recede aftermath (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ReportAftermath()
        {
            Map map = Find.CurrentMap;
            if (map == null) return;
            RM_MapComponent_RecedeAftermath comp = map.GetComponent<RM_MapComponent_RecedeAftermath>();
            if (comp == null) { Log.Error("[RMFloodedCanyonDebug] no RM_MapComponent_RecedeAftermath on this map."); return; }
            Log.Message("[RMFloodedCanyonDebug] aftermath: " + comp.DebugStateReport());
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

        // CRACKEDLANDS_LEDGES_OF_MERCY_1 verify: a STATE read of the refuge
        // (cells, seekers, who is on a ledge or running for one), never a
        // screenshot hunt.
        [DebugAction(CAT, "Report ledge refuge (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ReportRefuge()
        {
            RM_MapComponent_LedgeRefuge comp = Find.CurrentMap?.GetComponent<RM_MapComponent_LedgeRefuge>();
            if (comp == null) { Log.Error("[RMFloodedCanyonDebug] no RM_MapComponent_LedgeRefuge on this map."); return; }
            Log.Message("[RMFloodedCanyonDebug] " + comp.DebugStateReport());
        }

        // Runs the worldgen ledge carver on the CURRENT map (any biome), so a
        // quicktest map gets real ledges, carvings and anchors without a new
        // world. Ignores the worldgen setting; prints what it cut and the
        // refuge state after.
        [DebugAction(CAT, "Carve mercy ledges now (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void CarveLedges()
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_LedgeRefuge comp = map?.GetComponent<RM_MapComponent_LedgeRefuge>();
            if (comp == null) { Log.Error("[RMFloodedCanyonDebug] no RM_MapComponent_LedgeRefuge on this map."); return; }
            RM_MercyLedges.Result r = RM_MercyLedges.Generate(map, null);
            Log.Message("[RMFloodedCanyonDebug] carved ledges=" + r.ledges + " ledgeCells=" + r.ledgeCells
                + " carvings=" + r.carvings + " anchorsPlaced=" + r.anchors + " " + comp.DebugStateReport());
        }

        // Test surface until a ledge def exists: nine standable dry cells
        // nearest the map centre become refuge cells.
        [DebugAction(CAT, "Mark debug refuge ledge at map centre (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void MarkRefuge()
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_LedgeRefuge comp = map?.GetComponent<RM_MapComponent_LedgeRefuge>();
            if (comp == null) { Log.Error("[RMFloodedCanyonDebug] no RM_MapComponent_LedgeRefuge on this map."); return; }
            int n = comp.DebugMarkRefugeNear(map.Center, 9);
            Log.Message("[RMFloodedCanyonDebug] marked=" + n + " " + comp.DebugStateReport());
        }

        [DebugAction(CAT, "Clear debug refuge ledges (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ClearRefuge()
        {
            RM_MapComponent_LedgeRefuge comp = Find.CurrentMap?.GetComponent<RM_MapComponent_LedgeRefuge>();
            if (comp == null) { Log.Error("[RMFloodedCanyonDebug] no RM_MapComponent_LedgeRefuge on this map."); return; }
            comp.DebugClearRefuge();
            Log.Message("[RMFloodedCanyonDebug] cleared " + comp.DebugStateReport());
        }

        // Test surface: makes every player animal on the map a "trained
        // animal" (Obedience, completed) so the refuge seek can be proven.
        [DebugAction(CAT, "Teach player animals Obedience (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void TeachObedience()
        {
            Map map = Find.CurrentMap;
            if (map == null) return;
            int n = 0;
            foreach (Pawn p in map.mapPawns.SpawnedPawnsInFaction(RimWorld.Faction.OfPlayer))
            {
                if (p.RaceProps.Animal && p.training != null)
                {
                    p.training.Train(RimWorld.TrainableDefOf.Obedience, null, complete: true);
                    n++;
                }
            }
            Log.Message("[RMFloodedCanyonDebug] taught=" + n);
        }
    }
}
