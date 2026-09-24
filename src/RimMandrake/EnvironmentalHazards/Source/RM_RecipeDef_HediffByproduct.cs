using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_GASLIGHT_1 (item spec §1). Generic (not Sump-specific) pairing
    // for RM_Recipe_RemoveHediffWithByproduct: a plain RecipeDef has nowhere
    // to hang "and also spawn this many of that Thing on success," so this
    // subclass adds exactly that, reusable by any future hediff-removal
    // recipe that should leave a physical byproduct behind — not hardcoded
    // to tar/acid/gas at all. `<RecipeDef Class="...">` is ordinary Def
    // subclassing, the same mechanism this repo already uses for
    // RM_LotteryTableDef.
    public class RM_RecipeDef_HediffByproduct : RecipeDef
    {
        // The Thing spawned when the hediff is actually removed. Null means
        // no byproduct — a plain Recipe_RemoveHediffWithByproduct recipe
        // with this unset behaves exactly like vanilla Recipe_RemoveHediff.
        public ThingDef byproductDef;

        // How many of byproductDef spawn per successful removal.
        public IntRange byproductCountRange = IntRange.One;

        // Chance (0..1) the byproduct spawns at all on a successful removal
        // — kept separate from surgerySuccessChanceFactor, which already
        // governs whether the removal itself succeeds; this only governs
        // whether the reaction happens to also yield something once it has.
        public float byproductChance = 1f;
    }
}
