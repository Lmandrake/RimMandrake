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
        /// <summary>PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 4: what this anchor's spans carry. Power (default) joins power
        /// nets; Pipe (FlowWorks' pipe pole) never touches power and links only to other pipe anchors.</summary>
        public AerialLineKind lineKind = AerialLineKind.Power;
        /// <summary>Span cable width, cells; 0 = the look's wire width (AerialMaterials.WidthOf).</summary>
        public float spanWidth;
        /// <summary>Art-contract path of the span texture, "{look}" replaced by the anchor's look. Looked up SILENTLY: until
        /// the art is installed the span draws the look's wire as a stand-in (no def names an uninstalled path).</summary>
        public string spanTexPath;
    }
}
