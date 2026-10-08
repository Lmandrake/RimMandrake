using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // A second PeriodicAreaAttack aura on the same HediffDef. The engine's HediffDef.ConfigErrors rejects two
    // comps with the same compClass, so the second aura declares this subclass pair instead. Behaviour is
    // identical to the base comp (Props casts to the base properties type), and code that scans a hediff's
    // comps with `is HediffCompProperties_PeriodicAreaAttack` still matches it.
    public class HediffCompProperties_PeriodicAreaAttackSecondary : HediffCompProperties_PeriodicAreaAttack
    {
        public HediffCompProperties_PeriodicAreaAttackSecondary()
        {
            compClass = typeof(HediffComp_PeriodicAreaAttackSecondary);
        }
    }

    public class HediffComp_PeriodicAreaAttackSecondary : HediffComp_PeriodicAreaAttack
    {
        protected override string SaveKey => "ticksUntilBurstSecondary";
    }
}
