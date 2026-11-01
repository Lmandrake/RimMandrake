using RimWorld;
using Verse;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // RAKATAN_STASIS_LOOT_BUILD_HELD_PROVISIONS (design/RimStarWars/cold_storage_line_2026-10-26.md §5):
    // RUT_StasisHeldProvisions, found in the Rakatan caskets of the frozen vault and the war lab. "Millennia old and
    // perfectly fresh. Eating it can give a *strange* thought or, rarely, a vision-flavoured inspiration."
    //
    // Each meal rolls on its own. With chance strangeChance the eater gains the `strange` memory, otherwise the
    // ordinary meal thoughts apply (the def's preferability). Separately, with chance visionChance, it tries a random
    // inspiration. The inspiration call is the one vanilla uses (IngestionOutcomeDoer_Psilocap,
    // CompAbilityEffect_GiveInspiration, and this repo's RM_HediffComp_PeriodicInspiration):
    // InspirationHandler.TryStartInspiration already refuses a pawn who is already inspired, blocked by a hediff, or
    // not eligible for that inspiration, so this class only rolls the chance and picks from vanilla's random pool.
    // There is no vanilla doer that gives an inspiration, so this class exists.
    public class IngestionOutcomeDoer_StasisHeld : IngestionOutcomeDoer
    {
        public ThoughtDef strange;
        public float strangeChance = 0.3f;
        public float visionChance = 0.05f;

        // Shown in the inspiration letter as the reason. RUT ships no Languages folder, so this is English.
        public string visionReason = "The stasis-held food tasted of somewhere that no longer exists.";

        protected override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
        {
            if (pawn == null || pawn.Dead)
            {
                return;
            }
            if (strange != null && pawn.needs?.mood != null && Rand.Chance(strangeChance))
            {
                pawn.needs.mood.thoughts.memories.TryGainMemory(strange);
            }
            InspirationHandler handler = pawn.mindState?.inspirationHandler;
            if (handler == null || handler.Inspired || !Rand.Chance(visionChance))
            {
                return;
            }
            InspirationDef def = handler.GetRandomAvailableInspirationDef();
            if (def != null)
            {
                handler.TryStartInspiration(def, visionReason);
            }
        }
    }
}
