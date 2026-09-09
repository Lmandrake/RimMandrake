using RimWorld;
using Verse;

namespace RimMandrake.AnimalTheft
{
    [DefOf]
    public static class AnimalTheftDefOf
    {
        public static TrainableDef RM_Steal;
        public static JobDef RM_AnimalSteal;

        static AnimalTheftDefOf() =>
            DefOfHelper.EnsureInitializedInCtor(typeof(AnimalTheftDefOf));
    }
}
