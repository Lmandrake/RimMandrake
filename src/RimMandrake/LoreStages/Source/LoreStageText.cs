using Verse;

namespace RimMandrake.LoreStages
{
    // One rung of one ladder for one def field: "at stage N and above (until a
    // higher rung takes over), this field reads THIS."
    //
    // Loaded by RimWorld's ordinary <li> list loading inside
    // LoreStageTarget.stages. There is deliberately NO LoadDataFromXmlCustom
    // anywhere in this mod: a custom loader that sees a bare <li> discards the
    // WHOLE enclosing def silently, and a lore table failing silently is the
    // exact failure this feature exists to avoid.
    public class LoreStageText
    {
        // The rung this text belongs to. Stage 0 is the shipped baseline and
        // normally needs no entry at all (LoreStageApplier snapshots the def's
        // pristine value at first touch); an explicit stage 0 entry OVERRIDES
        // that snapshot, which is the authoring escape hatch for "the shipped
        // text is not what we want players to read first".
        public int stage;

        // The replacement text. Multi-paragraph is legal and is how a staged
        // BiomeDef.settleWarning adds a paragraph: the engine's confirmation
        // joiner (SettlementProximityGoodwillUtility.CheckConfirmSettle) cannot
        // tell an embedded "\n\n" from a separate yielded paragraph.
        public string text;
    }
}
