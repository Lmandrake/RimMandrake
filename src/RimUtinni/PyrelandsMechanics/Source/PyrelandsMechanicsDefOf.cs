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
    ///
    /// PYRELANDS_RM_MOD_BUILD_1 §6: RUT_FireHawkCarryEmber (JobDef) and
    /// RUT_FurnaceWarmth (HediffDef) were absorbed into mandrake.rm.pyrelands
    /// (renamed RM_FireHawkCarryEmber/RM_FurnaceWarmth — see that mod's own
    /// RimMandrake.Pyrelands.PyrelandsMechanicsDefOf) because both are
    /// franchise-free. TribeCivil and RUT_RiteHarvest name campaign content
    /// and stay here.
    /// </summary>
    [DefOf]
    public static class PyrelandsMechanicsDefOf
    {
        public static FactionDef TribeCivil;

        /// <summary>DEEP_TRIBES_FIRE_RITE_1 — the duty the rite party works the
        /// burn under. Defs/DutyDefs/RUT_PyrelandsDuties.xml.</summary>
        public static DutyDef RUT_RiteHarvest;

        static PyrelandsMechanicsDefOf() =>
            DefOfHelper.EnsureInitializedInCtor(typeof(PyrelandsMechanicsDefOf));
    }
}
