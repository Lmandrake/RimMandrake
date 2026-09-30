using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// LONGSHADE_BEDAZZLE_MECHANICS_1 part 2 — "Mirrak hide is the deepest
    /// shade cloth, feeding SHADE_GEAR_FAMILY_1" (item spec). A MARKER on a
    /// stuff ThingDef: a shade-casting thing made from this stuff casts
    /// deeper shade, by <see cref="shadeBonus"/> added to the caster's own
    /// shade value (clamped to 1).
    ///
    /// Nothing in this assembly reads it yet, deliberately: the shade-casting
    /// gear (parasol, shade tent, sun shield) and the grid's stuffed-caster
    /// read are SHADE_GEAR_FAMILY_1's scope. The marker ships now so the hide
    /// def is complete and that item reads a field rather than a defName.
    /// </summary>
    public class RM_ShadeClothExtension : DefModExtension
    {
        public float shadeBonus = 0.25f;
    }
}
