using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F1 spike. Attach to a PawnKindDef to exempt it
    // from RUT_MapComponent_TheTenant's strike roll — "nothing native
    // drinks at the pools" (the_fever_wood.md §5). Without this marker, a
    // roster spawn idling or pathing near registered water would be exposed
    // like any other pawn; the exemption is what makes §5's claim true by
    // construction rather than by every idle-behavior author remembering
    // to avoid the water tag.
    public class RM_TenantTruceExtension : DefModExtension
    {
    }
}
