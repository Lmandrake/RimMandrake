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

    // WARSCAR_PILGRIM_JOURNAL_ANTIQUITY_1: a sibling comp on an antiquity that
    // wants to know when the Reading Station catalogues it (the pilgrim's
    // journal moves the Scarlands lore ladder this way -- one item route for
    // both lore systems, never a second read job). Called once, after the
    // catalogued flag is set. An antiquity carrying a listener stays readable
    // after VOICE is finished: it still has something to teach.
    public interface IAntiquityCatalogueListener
    {
        void Notify_Catalogued(Pawn reader);
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
