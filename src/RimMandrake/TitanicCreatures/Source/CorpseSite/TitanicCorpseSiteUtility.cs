using RimWorld;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    public static class TitanicCorpseSiteUtility
    {
        /// <summary>
        /// Replaces a T3 titan's ordinary single-cell Corpse with the
        /// multi-cell Building_TitanicCorpseSite landmark, carrying over the
        /// exact yield vanilla would have produced (this pawn's real
        /// MeatAmount/LeatherAmount stats and race defs, not a guessed
        /// constant) so the site's harvest pool matches what this specific
        /// creature would have butchered for.
        /// </summary>
        public static void ConvertToSite(Corpse corpse, Map map)
        {
            Pawn inner = corpse.InnerPawn;
            if (inner == null)
            {
                return;
            }
            IntVec3 pos = corpse.Position;
            string label = inner.LabelCap;
            ThingDef meatDef = inner.RaceProps.meatDef;
            int meatTotal = meatDef != null ? GenMath.RoundRandom(inner.GetStatValue(StatDefOf.MeatAmount)) : 0;
            ThingDef leatherDef = inner.RaceProps.leatherDef;
            int leatherTotal = leatherDef != null ? GenMath.RoundRandom(inner.GetStatValue(StatDefOf.LeatherAmount)) : 0;

            // Remove the ordinary corpse first - never an instant meat pile
            // sitting there alongside the landmark (ruling #4).
            corpse.Destroy();

            var site = (Building_TitanicCorpseSite)ThingMaker.MakeThing(RM_TitanicCreaturesDefOf.RM_TitanicCorpseSite);
            site.Setup(label, meatDef, meatTotal, leatherDef, leatherTotal);
            GenSpawn.Spawn(site, pos, map, WipeMode.VanishOrMoveAside);
        }
    }
}
