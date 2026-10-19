using RimWorld;
using Verse;

namespace RimMandrake.StarWars.JawaRules
{
    // RSW_Stinky social thought: a pawn with an intact nose who knows `other` dislikes `other`
    // when `other` carries the RSW_Stinky gene (StarWarsRaces). Port of Alpha Genes'
    // AlphaGenes.ThoughtWorker_Stinky (decompiled 2026-10-18, same logic) when that donor
    // was retired. The gene is looked up by name so this assembly loads without StarWarsRaces.
    public class ThoughtWorker_RSW_Stinky : ThoughtWorker
    {
        private static GeneDef stinky;
        private static BodyPartDef nose;
        private static bool looked;

        protected override ThoughtState CurrentSocialStateInternal(Pawn pawn, Pawn other)
        {
            if (!looked)
            {
                stinky = DefDatabase<GeneDef>.GetNamedSilentFail("RSW_Stinky");
                nose = DefDatabase<BodyPartDef>.GetNamedSilentFail("Nose");
                looked = true;
            }
            if (stinky == null || nose == null || other?.genes == null || !other.RaceProps.Humanlike
                || !RelationsUtility.PawnsKnowEachOther(pawn, other))
                return false;
            var noses = pawn.RaceProps.body.GetPartsWithDef(nose);
            if (noses.NullOrEmpty())
                return false;
            foreach (var part in noses)
                if (pawn.health.hediffSet.PartIsMissing(part))
                    return false;
            return other.genes.HasActiveGene(stinky) ? ThoughtState.ActiveAtStage(0) : (ThoughtState)false;
        }
    }
}
