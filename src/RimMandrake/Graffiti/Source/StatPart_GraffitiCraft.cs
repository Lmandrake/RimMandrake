using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Graffiti
{
    /// <summary>A mark's Beauty is its painter's craft (RM_GraffitiKernel.CraftBeauty), not its def's base: the number every reader of the stat
    /// gets, the room's beauty and the stat line alike, says what the wall shows. Owner, 2026-11-07: "a poor artist will paint such a bad
    /// graffiti mark that it is ugly ... a highly skilled artist is actually making art. It is beautiful". Added to Beauty at startup.</summary>
    public class StatPart_GraffitiCraft : StatPart
    {
        public override void TransformValue(StatRequest req, ref float val)
        {
            if (req.Thing is Filth_Mark m && m.hasCraft) val = m.NetBeauty;
        }

        public override string ExplanationPart(StatRequest req)
        {
            if (!(req.Thing is Filth_Mark m) || !m.hasCraft) return null;
            return "Painted with " + m.CraftLabel + " craft" + (m.defaced ? ", then crossed out" : "") + ": " + m.NetBeauty.ToString("+0.#;-0.#;0");
        }
    }

    [StaticConstructorOnStartup]
    internal static class StatPart_GraffitiCraft_Install
    {
        static StatPart_GraffitiCraft_Install()
        {
            StatDef beauty = StatDefOf.Beauty;
            if (beauty.parts == null) beauty.parts = new List<StatPart>();
            beauty.parts.Add(new StatPart_GraffitiCraft { parentStat = beauty });
        }
    }
}
