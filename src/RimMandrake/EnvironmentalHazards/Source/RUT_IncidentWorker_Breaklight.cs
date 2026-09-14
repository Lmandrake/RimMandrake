using RimWorld;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M5 build (greentide_kit_spec.md "M5. Breaklight
    // — clarity as the disaster"). RUT_Breaklight.xml (IncidentDef) fires
    // through this rather than the bare vanilla
    // RimWorld.IncidentWorker_MakeGameCondition every other
    // GameCondition_EnvironmentalWeather-fired incident in this kit already
    // uses (RUT_Surge, RM_WS_DarkAurora) — the one-line addition is the mod
    // option gate: MOD_OPTIONS_RETROFIT_1 requires a master switch per
    // mechanism, and unlike a permanent biomeMapConditions lock (Scald's
    // steam, Miasma's haze, this kit's own Roil lock) there is no existing
    // toggle to hang this one off of, since a rare incident-fired event has
    // no other on/off hook.
    //
    // RUT_-prefixed despite living in mandrake.rm.environmentalhazards, same
    // precedent RUT_WeatherOverlay_ScaldSteam.cs already set in this same
    // folder: a biome-specific one-off class is named for its content, not
    // for the shared assembly it happens to compile into.
    public class RUT_IncidentWorker_Breaklight : IncidentWorker_MakeGameCondition
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
