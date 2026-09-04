using Verse;

namespace RimMandrake.Utinni.Antiquities
{
    // How many artifacts design/Jawa/antiquities_design.md section 3's table
    // says a stage needs (4/7/10/12/15). JobDriver_ExamineAntiquity divides
    // the stage's own baseCost by this to get the per-read progress amount,
    // so reading exactly that many artifacts and nothing else finishes the
    // node -- no separate "progress per read" number to keep in sync by hand.
    public class AntiquityStageExtension : DefModExtension
    {
        public int artifactsRequired = 1;
    }
}
