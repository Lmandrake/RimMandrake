using System.Collections.Generic;
using Verse;

namespace RimMandrake.LoreStages
{
    // One def field this ladder rewrites, with its rungs.
    //
    // The addressing is (defType, defName, field) and not a Def cross-reference,
    // deliberately: a ladder may name defs from mods that are not loaded, and
    // DirectXmlCrossRefLoader would turn a missing one into a red error at
    // startup rather than a skipped row. LoreStageApplier resolves by name at
    // apply time and warns once per missing target instead.
    public class LoreStageTarget
    {
        // Type name as written in the def XML's root tag: "BiomeDef",
        // "ThingDef", "HediffDef", or a namespace-qualified name for a modded
        // Def subclass. Resolved through GenTypes, same as the def loader.
        public string defType;

        // defName of the target def.
        public string defName;

        // The public instance string field to rewrite. "description" and
        // "settleWarning" are the surfaces the feasibility trace verified as
        // live-read; "label" works too but see LoreStageApplier for the extra
        // cache it drags in.
        public string field = "description";

        // The rungs, in any order. LoreStageApplier picks the HIGHEST rung
        // whose stage is <= the ladder's current stage; gaps are legal and mean
        // "this field does not change at that rung".
        public List<LoreStageText> stages = new List<LoreStageText>();
    }
}
