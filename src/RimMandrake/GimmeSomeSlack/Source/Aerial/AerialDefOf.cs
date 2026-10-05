using RimWorld;
using Verse;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    [DefOf]
    public static class AerialDefOf
    {
        /// <summary>Dirties the ground layer (span shadows, fallen cords) of the section owning a changed span.</summary>
        public static MapMeshFlagDef RM_AerialLines;
        public static ThingDef RM_AerialMast;
        public static ThingDef RM_AerialLampMast;
        public static ThingDef RM_AerialWallBracket;
        public static ThingDef RM_PowerTapClamp;

        static AerialDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(AerialDefOf));
    }

    /// <summary>Per-def anchor parameters (Defs/Aerial/RM_AerialAnchors.xml).</summary>
    public class AerialAnchorExtension : DefModExtension
    {
        public int maxLinks = 4;
        /// <summary>Insulator height above the base, cells of screen z (top-down fake height).</summary>
        public float attachZ = 1.15f;
        /// <summary>Lateral spread of the insulators, cells.</summary>
        public float insulatorSpread = 0.18f;
        /// <summary>The mast head drawn ABOVE pawns at the span altitude (null: none, e.g. the wall bracket).</summary>
        public string topTexPath;
        public float topOffsetZ = 1.0f;
    }
}
