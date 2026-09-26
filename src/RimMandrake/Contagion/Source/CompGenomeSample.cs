using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_GENOME_ORGAN_GROWING_1. Carried by RM_GenomeSample — records
    // WHO the tissue was drawn from so the later injection (AmoebaHostUtility)
    // can stamp the identity onto the amoeba's gestation hediff, and from
    // there onto the finished organs (CompGenomeMatched). This is what makes
    // "matched to that individual" real rather than flavour text: the source
    // pawn's identity survives sample -> gestation -> organ end to end.
    public class CompProperties_GenomeSample : CompProperties
    {
        public CompProperties_GenomeSample()
        {
            compClass = typeof(CompGenomeSample);
        }
    }

    public class CompGenomeSample : ThingComp
    {
        public int sourcePawnID = -1;
        public string sourcePawnName = "";

        public void SetSource(int id, string name)
        {
            sourcePawnID = id;
            sourcePawnName = name.NullOrEmpty() ? "unknown" : name;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref sourcePawnID, "rmGenomeSourceID", -1);
            Scribe_Values.Look(ref sourcePawnName, "rmGenomeSourceName", "");
        }

        public override string CompInspectStringExtra()
        {
            if (sourcePawnID < 0 || sourcePawnName.NullOrEmpty())
            {
                return null;
            }
            return "Genome source: " + sourcePawnName;
        }
    }
}
