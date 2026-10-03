using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    /// <summary>ROT_SPORE_ALLERGY_PORT_1: vanilla disease workers plus the biome front's on/off and incidence factor.</summary>
    public class RM_IncidentWorker_SporeAllergyHuman : IncidentWorker_DiseaseHuman
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (parms.target is Map map && !RM_KitFronts.Enabled("sporeAllergy", map.Biome))
            {
                return false;
            }
            return base.CanFireNowSub(parms);
        }

        public override float ChanceFactorNow(IIncidentTarget target)
        {
            float f = base.ChanceFactorNow(target);
            return target is Map map ? f * RM_KitFronts.Factor("sporeAllergy", map.Biome) : f;
        }
    }

    public class RM_IncidentWorker_SporeAllergyAnimal : IncidentWorker_DiseaseAnimal
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (parms.target is Map map && !RM_KitFronts.Enabled("sporeAllergy", map.Biome))
            {
                return false;
            }
            return base.CanFireNowSub(parms);
        }

        public override float ChanceFactorNow(IIncidentTarget target)
        {
            float f = base.ChanceFactorNow(target);
            return target is Map map ? f * RM_KitFronts.Factor("sporeAllergy", map.Biome) : f;
        }
    }
}
