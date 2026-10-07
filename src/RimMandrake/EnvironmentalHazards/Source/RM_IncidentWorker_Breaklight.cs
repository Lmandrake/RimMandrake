using RimWorld;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M5 (greentide_kit_spec.md "M5. Breaklight"). RM_Breaklight (IncidentDef,
    // mandrake.rm.greentide) fires through this instead of the bare vanilla
    // IncidentWorker_MakeGameCondition only to add the MOD_OPTIONS_RETROFIT_1 gate: a rare
    // incident has no other on/off hook. Renamed from RUT_ by GREENTIDE_BASE_PORT_BUILD_1
    // (free-tier content, free-tier name).
    public class RM_IncidentWorker_Breaklight : IncidentWorker_MakeGameCondition
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!RM_EnvironmentalHazardsSettings.breaklightEnabled)
            {
                return false; // mod option: Breaklight clearing event disabled
            }

            return base.CanFireNowSub(parms);
        }
    }
}
