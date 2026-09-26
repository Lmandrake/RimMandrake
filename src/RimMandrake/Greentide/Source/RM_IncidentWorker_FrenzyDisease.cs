using RimWorld;
using Verse;

namespace RimMandrake.Greentide
{
    // GREENTIDE_FRENZY_DISEASE_1. The ambient version of "The Frenzy"
    // (RM_Greentide_FrenzyIncident.xml) uses this instead of the vanilla
    // IncidentWorker_DiseaseHuman directly so RM_GreentideSettings.frenzyEnabled
    // can disable the random-illness route without touching the biome's own
    // <diseases> list. The deliberate dose route (RM_IngestionOutcomeDoer_FrenzyDose)
    // is gated the same way, independently.
    public class RM_IncidentWorker_FrenzyDisease : IncidentWorker_DiseaseHuman
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!RM_GreentideSettings.frenzyEnabled)
            {
                return false;
            }
            return base.CanFireNowSub(parms);
        }
    }
}
