using RimWorld;

namespace RimMandrake.EnvironmentalHazards
{
    // ROT_SPORECLOUD_PORT_1. RUT_SporeCloud.xml (IncidentDef, RimUtinni
    // RotSporeKit) now fires GameCondition_EnvironmentalWeather through this
    // rather than the bare vanilla RimWorld.IncidentWorker_MakeGameCondition
    // — same one-line addition RUT_IncidentWorker_Breaklight already made for
    // exactly the same reason (MOD_OPTIONS_RETROFIT_1: a rare incident-fired
    // event has no other on/off hook to hang a mod-option toggle off of).
    //
    // RUT_-prefixed content class in the shared EnvironmentalHazards
    // assembly, same posture as RUT_IncidentWorker_Breaklight/
    // RUT_IncidentWorker_SteamDevil/RUT_IncidentWorker_ContagionProbe.
    public class RUT_IncidentWorker_SporeCloud : IncidentWorker_MakeGameCondition
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!RM_EnvironmentalHazardsSettings.sporeCloudEnabled)
            {
                return false; // mod option: spore cloud event disabled
            }

            return base.CanFireNowSub(parms);
        }
    }
}
