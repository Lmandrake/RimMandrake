using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// PYRELANDS_RM_MOD_BUILD_1 §6 — the two defs absorbed from
    /// mandrake.rut.pyrelandsmechanics that are ours (franchise-free), renamed
    /// RUT_ -> RM_ at the move. The two that stayed campaign-specific
    /// (TribeCivil, RUT_RiteHarvest) remain on Utinni's own
    /// RimMandrake.Utinni.PyrelandsMechanics.PyrelandsMechanicsDefOf.
    /// </summary>
    [DefOf]
    public static class PyrelandsMechanicsDefOf
    {
        public static JobDef RM_FireHawkCarryEmber;
        public static HediffDef RM_FurnaceWarmth;

        // FURNACEBEAST_WORLD_MIGRATION_1 — the world leg's own WorldObjectDef.
        public static WorldObjectDef RM_FurnaceHerd;

        static PyrelandsMechanicsDefOf() =>
            DefOfHelper.EnsureInitializedInCtor(typeof(PyrelandsMechanicsDefOf));
    }
}
