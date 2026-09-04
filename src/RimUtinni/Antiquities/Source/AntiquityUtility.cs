using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.Antiquities
{
    public static class AntiquityUtility
    {
        // Order matters: this IS the LANGUAGE -> RELIGION -> CULTURE ->
        // CARTOGRAPHY -> VOICE chain from design/Jawa/antiquities_design.md
        // section 3, and every stage's own <prerequisites> already encodes
        // the same order in the def data -- this array just gives C# a
        // cheap way to ask "what's next" without walking prerequisites.
        public static ResearchProjectDef[] Stages => new[]
        {
            ResearchProjectDefOf_Antiquities.RUT_Antiq_Language,
            ResearchProjectDefOf_Antiquities.RUT_Antiq_Religion,
            ResearchProjectDefOf_Antiquities.RUT_Antiq_Culture,
            ResearchProjectDefOf_Antiquities.RUT_Antiq_Cartography,
            ResearchProjectDefOf_Antiquities.RUT_Antiq_Voice,
        };

        // The reading job always advances whichever stage is next in the
        // fixed chain, regardless of what (if anything) the player has
        // selected in the research UI -- these projects are gated off
        // vanilla bench-hours entirely (RUT_Antiquities_Research.xml's own
        // comment), so "currentProj" is not a meaningful concept for them.
        public static ResearchProjectDef CurrentStage()
        {
            return Stages.FirstOrDefault(s => s != null && !s.IsFinished);
        }

        // Design doc section 4.2's "yield curve": LANGUAGE completing is
        // the one hard threshold that halves read duration and unlocks the
        // key-text chance at all.
        public static bool LanguageDone => ResearchProjectDefOf_Antiquities.RUT_Antiq_Language?.IsFinished ?? false;

        // "Later stages raise the key-text rate" (doc) names no numbers.
        // Assumption recorded here and in the item file: +5% per stage
        // completed past LANGUAGE, capped at 50% in JobDriver_
        // ExamineAntiquity -- open to retuning once slice 9's actual pacing
        // work happens.
        public static int StagesCompletedBeyondLanguage()
        {
            return Stages.Skip(1).Count(s => s != null && s.IsFinished);
        }
    }
}
