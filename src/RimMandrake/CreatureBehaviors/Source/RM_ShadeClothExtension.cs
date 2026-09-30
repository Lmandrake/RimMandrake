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
    /// Read by RM_ShadeGear.StuffBonus (SHADE_GEAR_FAMILY_1): a parasol,
    /// shade tent or sun shield made from this stuff casts
    /// shadeDepth + shadeBonus, before the heat-kind factor.
    /// </summary>
    public class RM_ShadeClothExtension : DefModExtension
    {
        public float shadeBonus = 0.25f;
    }
}
