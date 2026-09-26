using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_GENOME_ORGAN_GROWING_1. Lives on the host amoeba (AA_RedGoo)
    // between injection and completion. Severity climbs via the standard
    // HediffCompProperties_SeverityPerDay comp declared on the HediffDef
    // (RM_AmoebaGestation.xml) — this class only carries the injected
    // identity across that time and fires the one-shot completion when the
    // comp's growth reaches maxSeverity.
    public class Hediff_AmoebaGestation : HediffWithComps
    {
        public int sourcePawnID = -1;
        public string sourcePawnName = "";

        private bool completed;

        public void Setup(int id, string name)
        {
            sourcePawnID = id;
            sourcePawnName = name.NullOrEmpty() ? "unknown" : name;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref sourcePawnID, "rmSourcePawnID", -1);
            Scribe_Values.Look(ref sourcePawnName, "rmSourcePawnName", "");
            Scribe_Values.Look(ref completed, "rmCompleted", false);
        }

        public override void PostTick()
        {
            base.PostTick();
            if (completed)
            {
                return;
            }
            if (Severity >= def.maxSeverity - 0.001f)
            {
                completed = true;
                AmoebaHostUtility.CompleteGestation(pawn, sourcePawnID, sourcePawnName);
            }
        }
    }
}
