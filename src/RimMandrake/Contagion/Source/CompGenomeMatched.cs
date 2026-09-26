using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_GENOME_ORGAN_GROWING_1. Added by a Patch (Patches/
    // OrganGenomeComps.xml) onto the four vanilla harvestable organ ThingDefs
    // (Kidney, Liver, Lung, Heart) — NOT onto a new organ ThingDef of our own.
    // That choice is deliberate: a new ThingDef would not be accepted by
    // vanilla's existing "install kidney/liver/lung/heart" recipes, whose
    // ingredient filters name the exact vanilla defName. Attaching a comp
    // instead keeps every organ this mechanic produces a REAL, mechanically
    // ordinary vanilla organ (sellable, installable via the stock surgery) —
    // the item's own ruling that output can be "ordinary sellable vanilla
    // organs, since it is not repeatable" — while still carrying the source
    // pawn's identity for the "matched to that individual" fiction. An organ
    // with no data set (every vanilla-spawned Kidney/Liver/Lung/Heart in the
    // game) is a complete no-op: CompInspectStringExtra returns null and
    // nothing else on the comp ever runs.
    public class CompProperties_GenomeMatched : CompProperties
    {
        public CompProperties_GenomeMatched()
        {
            compClass = typeof(CompGenomeMatched);
        }
    }

    public class CompGenomeMatched : ThingComp
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
            Scribe_Values.Look(ref sourcePawnID, "rmGenomeMatchID", -1);
            Scribe_Values.Look(ref sourcePawnName, "rmGenomeMatchName", "");
        }

        public override string CompInspectStringExtra()
        {
            if (sourcePawnID < 0 || sourcePawnName.NullOrEmpty())
            {
                return null;
            }
            return "Grown from " + sourcePawnName + "'s genome in a Contagion amoeba host.";
        }
    }
}
