using LudeonTK;
using RimWorld;
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

        // FORGE_WHITE_PLUME_FRONTS_1 quicktest surface.
        [DebugAction(CAT, "Forge plumes: report (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void PlumeReport()
        {
            RM_MapComponent_PlumeFronts c = RM_MapComponent_PlumeFronts.Of(Find.CurrentMap);
            Log.Message("[RMTheForgeDebug] " + (c == null ? "no plume component" : c.DebugReport()));
        }

        [DebugAction(CAT, "Forge plumes: spawn a front on a crust cell (mouse cell if none) (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void PlumeSpawn()
        {
            RM_MapComponent_PlumeFronts c = RM_MapComponent_PlumeFronts.Of(Find.CurrentMap);
            if (c != null)
            {
                RM_GameCondition_ForgeCycle cycle = RM_ForgeCycleUtility.CycleOn(Find.CurrentMap);
                IntVec3 at = cycle != null && cycle.FrozenCellCount > 0 ? cycle.RandomFrozenCell() : UI.MouseCell();
                c.DebugSpawn(at);
            }
            PlumeReport();
        }

        // FORGE_SKY_PASTURES_1 quicktest surface (state reads only, no flight hunting).
        [DebugAction(CAT, "Forge sky: report (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void SkyReport()
        {
            RM_MapComponent_SkyPastures c = RM_MapComponent_SkyPastures.Of(Find.CurrentMap);
            Log.Message("[RMTheForgeDebug] " + (c == null ? "no sky component" : c.DebugReport()));
        }

        [DebugAction(CAT, "Forge sky: re-read the column field now (current map)",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void SkyPoll()
        {
            RM_MapComponent_SkyPastures c = RM_MapComponent_SkyPastures.Of(Find.CurrentMap);
            if (c != null)
            {
                c.PollNow();
            }
            SkyReport();
        }

        // FORGE_GPT_ENRICHMENT_1 quicktest surface.
        [DebugAction(CAT, "Spunstone: report knowledge",
            allowedGameStates = AllowedGameStates.Playing)]
        private static void SpunstoneReport()
        {
            RM_SpunstoneKnowledge k = RM_SpunstoneKnowledge.Get();
            ResearchProjectDef p = RM_TheForgeDefOf.RM_SpunstoneBonding;
            Log.Message("[RMTheForgeDebug] spunstone points=" + (k != null ? k.Points.ToString("0.##") : "null")
                + " revealed=" + (k != null && k.Revealed) + " projectHidden=" + p.IsHidden + " canStart=" + p.CanStartNow);
        }

        [DebugAction(CAT, "Spunstone: reveal now",
            allowedGameStates = AllowedGameStates.Playing)]
        private static void SpunstoneReveal()
        {
            RM_SpunstoneKnowledge k = RM_SpunstoneKnowledge.Get();
            if (k != null && !k.Revealed)
            {
                k.Reveal(null);
            }
            SpunstoneReport();
        }
    }
}
