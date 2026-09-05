using System.Collections.Generic;
using Verse;

namespace RimMandrake.Aftermath
{
    // design/Jawa/proposals/plot_mechanisms_wave.md §2.1 rule 2's "the
    // alliance table" - v1's fiction-only hostilities given one mechanism.
    // `a` is the faction whose defeat/rout triggers the ally's arrival,
    // `b` is the ally who comes. Directional as authored (Junkers <-
    // Enclaves is explicitly one-way in the doc); `weight` is unused by
    // AftermathRuleRunner's current (first-match) implementation and exists
    // for a future multi-candidate pick.
    public class RM_AlliancePairDef : Def
    {
        public string a;
        public string b;
        public float weight = 1f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (string.IsNullOrEmpty(a) || string.IsNullOrEmpty(b))
                yield return "RM_AlliancePairDef " + defName + ": both a and b (FactionDef defNames) are required.";
        }
    }
}
