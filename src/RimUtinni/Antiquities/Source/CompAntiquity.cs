using Verse;

namespace RimMandrake.Utinni.Antiquities
{
    public class CompProperties_Antiquity : CompProperties
    {
        public CompProperties_Antiquity()
        {
            compClass = typeof(CompAntiquity);
        }
    }

    // Non-destructive by design (design doc section 4.2: "spent for
    // knowledge but intact for silver") -- reading only ever flips this
    // flag. No per-instance narrative text field yet: the four-axis
    // generator (section 4.3) is ANTIQUITIES_TREE_BUILD_1 slice 2, not
    // built here.
    public class CompAntiquity : ThingComp
    {
        public bool catalogued;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref catalogued, "catalogued", defaultValue: false);
        }

        public override string CompInspectStringExtra()
        {
            return catalogued
                ? "RUT_Antiquity_Catalogued".Translate()
                : "RUT_Antiquity_Uncatalogued".Translate();
        }
    }
}
