using Verse;

namespace RimMandrake.Pits
{
    public class CompProperties_PitFitting : CompProperties
    {
        public PitFittingType fittingType = PitFittingType.Bare;

        // Spiked: flat blunt-equivalent lethal damage added to the ordinary
        // fall damage on capture.
        public float spikeDamage = 25f;

        // Poison: toxin severity added per struggle interval while held.
        public float poisonSeverityPerInterval = 0.02f;

        // Oubliette: EMP damage applied once on capture (vanilla
        // DamageDefOf.EMP - the same damage type vanilla EMP grenades use to
        // stun mechanoids).
        public float oublietteEmpDamage = 40f;

        public CompProperties_PitFitting()
        {
            compClass = typeof(CompPitFitting);
        }
    }
}
