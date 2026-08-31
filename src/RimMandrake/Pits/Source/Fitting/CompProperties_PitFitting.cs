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

        // Water: RM_PitDrowning severity added per struggle interval. This was a
        // hardcoded 1f, and RM_PitDrowning has lethalSeverity 1.0, so the FIRST
        // interval killed the occupant outright - measured live 2026-08-30, the
        // pit held a Corpse_Human after one roll and the hediff's own second
        // stage ("exhausted", minSeverity 0.6) was unreachable. 0.15 gives the
        // ~7-interval clock the two stages were written for.
        public float drowningSeverityPerInterval = 0.15f;

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
