// ANOMALY_EVENTS_SUPPRESS_UTINNI_1 (owner, question card 2026-10-08): no Void Monolith in the Utinni scenario.
// Anomaly incidents are disabled by ScenPart_DisableIncident in Scenario_Utinni.xml; the monolith (and therefore
// the EndGame_VoidMonolith / EndGame_VoidAwakening quests it alone starts) is not an incident, so it is skipped here.
// Skipping the SPAWN (not GameComponent_Anomaly.GenerateMonolith) keeps monolith-level gates on Anomaly content shut.
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RuthlessPursuingMechanoids
{
    public static class UtinniAnomalyScope
    {
        public const string ScenarioDefName = "RUT_Jawa_UtinniStart";

        public static bool UtinniScenarioActive()
        {
            Scenario active = Find.Scenario;
            if (active == null) return false;
            ScenarioDef def = DefDatabase<ScenarioDef>.GetNamedSilentFail(ScenarioDefName);
            if (def?.scenario == null) return false;
            return active == def.scenario || active.name == def.scenario.name;
        }
    }

    [HarmonyPatch]
    internal static class GenStep_Monolith_GenerateMonolith_Utinni
    {
        private static MethodBase TargetMethod() => AccessTools.Method(typeof(GenStep_Monolith), "GenerateMonolith");

        // a renamed target after a game update skips the patch instead of throwing out of PatchAll
        private static bool Prepare() => TargetMethod() != null;

        private static bool Prefix() => !UtinniAnomalyScope.UtinniScenarioActive();
    }
}
