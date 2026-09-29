using System.Collections.Generic;
using System.Linq;
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

        // GREENTIDE_FEVER_SPECIALISTS_1, U2's answer. MEASURED via RimSage
        // 2026-09-29: Pawn.GetDisabledWorkTypes() (Verse/Pawn.cs) aggregates
        // disabled work types only from mutant state, backstory, traits, mech
        // race props, health.DisabledWorkTypes, royal titles, Ideology role,
        // Biotech genes, QuestPart_WorkDisabled, guest state and life-stage
        // settings - there is no "a Hediff disables/requires a work type" hook
        // anywhere in that list, so a literal hard work-type lock does not
        // exist to hang this off. This project also has no existing caravan/
        // expedition-leadership role system to hook a hard lock into instead
        // (grepped src/RimMandrake for "expedition"/"caravan lead"/
        // "forward camp" - nothing found).
        //
        // ⇒ The gate is disease resistance on re-exposure, reusing this
        // existing victim-selection machinery rather than inventing a new
        // gate: a pawn already carrying RM_FeverMark is dropped from the
        // ambient Frenzy incident's candidate pool outright. "Unmarked pawns
        // can still go — they just get sick, and the marked ones don't" is
        // the item's own words for exactly this.
        protected override IEnumerable<Pawn> PotentialVictimCandidates(IIncidentTarget target)
        {
            IEnumerable<Pawn> candidates = base.PotentialVictimCandidates(target);
            if (!RM_GreentideSettings.feverMarkGrantsImmunity)
            {
                return candidates;
            }
            return candidates.Where((Pawn p) => p.health?.hediffSet == null || !p.health.hediffSet.HasHediff(RM_DefOf.RM_FeverMark));
        }
    }
}
