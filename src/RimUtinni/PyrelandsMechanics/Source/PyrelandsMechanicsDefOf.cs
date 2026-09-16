using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// PYRELANDS_MECHANICS_1's own defs, resolved once at startup rather than by
    /// DefDatabase lookup in a tick path.
    ///
    /// TribeCivil is NOT ours and is NOT a guess: the Deep Desert Tribes are a
    /// reskin of the vanilla FactionDef TribeCivil — see
    /// src/RimUtinni/UtinniPatches/Patches/DeepDesertTribes.xml, which patches
    /// that def's label to "Deep Desert Tribes". The sheet's fire-farmers and
    /// fire-raiders (the_pyrelands.md §8) are therefore that faction.
    /// </summary>
    [DefOf]
    public static class PyrelandsMechanicsDefOf
    {
        public static JobDef RUT_FireHawkCarryEmber;
        public static HediffDef RUT_FurnaceWarmth;
        public static FactionDef TribeCivil;

        /// <summary>DEEP_TRIBES_FIRE_RITE_1 — the duty the rite party works the
        /// burn under. Defs/DutyDefs/RUT_PyrelandsDuties.xml.</summary>
        public static DutyDef RUT_RiteHarvest;

        static PyrelandsMechanicsDefOf() =>
            DefOfHelper.EnsureInitializedInCtor(typeof(PyrelandsMechanicsDefOf));
    }
}
