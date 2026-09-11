using RimWorld;
using Verse;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// One place that answers "who are the fire-farmers", so the two incident
    /// workers cannot drift apart.
    ///
    /// 🔑 The Deep Desert Tribes are NOT a def of ours. They are vanilla's
    /// FactionDef TribeCivil, reskinned in place by
    /// src/RimUtinni/UtinniPatches/Patches/DeepDesertTribes.xml (which replaces
    /// that def's label with "Deep Desert Tribes" and adds the campaign's group
    /// makers). Reading the defName off that patch is why this file guesses
    /// nothing. If the campaign ever gives the Tribes their own FactionDef, this
    /// is the single line that changes.
    /// </summary>
    internal static class PyrelandsFactions
    {
        /// <summary>The Tribes as they exist in this save, or null — a world can
        /// legitimately have been generated without them, and a defeated or
        /// temporary faction cannot farm or raid anything.</summary>
        internal static Faction TribesOrNull()
        {
            Faction f = Find.FactionManager?.FirstFactionOfDef(PyrelandsMechanicsDefOf.TribeCivil);
            if (f == null || f.defeated || f.temporary || f.IsPlayer)
            {
                return null;
            }
            return f;
        }
    }
}
