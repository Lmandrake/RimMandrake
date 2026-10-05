// Verse-free (the SelfTest compiles this file): per-build style stage 3, hose reels and hoses
// (design/RimMandrake/messyconduit_style_per_build_design.md section 5 stage 3, architecture B).
using System;
using RimMandrake.GimmeSomeSlack.Aerial;

namespace RimMandrake.GimmeSomeSlack.Hose
{
    /// <summary>
    /// The reel is its own building with its own style (CompStyleable, ThingStyleDefs RM_HoseReel_&lt;Look&gt; in
    /// Defs/Hose/RM_HoseReelStyles.xml); the hose it lays takes the REEL's look (design 2.3: "The hose takes the reel's
    /// style. A hose is not part of a power run"). Art naming (Transient/mc_style_art_report.md section 4): a piece shipped
    /// at Hose/&lt;Name&gt;.png has its look's version at Hose/Styles/&lt;Look&gt;/&lt;Name&gt;.png; Scrapper stays the root file. The
    /// strand shadow is shared by every look.
    /// </summary>
    public static class HoseStyles
    {
        public const string ReelDef = "RM_HoseReel";

        /// <summary>The defs StylePicker registers for stage 3 (beside AerialStyles.StyledDefs).</summary>
        public static readonly string[] StyledDefs = { ReelDef };

        public const string Root = "RimMandrake/GimmeSomeSlack/Hose/";
        public const string Scrapper = "Scrapper";

        /// <summary>The hose pieces drawn per look: strand flat / plump, binding wrap, coupling, nozzle, end cap, open mouth.</summary>
        public static readonly string[] Pieces = { "Strand_Flat", "Strand_Plump", "Binding", "Coupling_Bare", "Nozzle_Bare", "EndCap_Bare", "Mouth" };

        /// <summary>The reel's two images per look: stored (hose coiled on) and laid (empty drum, hose inlet). Graphic_HoseReel
        /// swaps them, finding "Reel_Deployed" beside the stored texPath, so each look's folder carries its own pair.</summary>
        public static readonly string[] ReelArt = { "Reel_PumpHookup", "Reel_Deployed" };

        /// <summary>Shared by every look (a soft dark band, no material in it).</summary>
        public const string SharedShadow = "Strand_Shadow";

        /// <summary>The folder a look's hose art lives in (an unknown look is Scrapper's root folder).</summary>
        public static string Folder(string look) =>
            look == Scrapper || !AerialStyles.IsLook(look) ? Root : Root + "Styles/" + look + "/";

        /// <summary>The texture path of one hose piece in one look.</summary>
        public static string PathFor(string look, string piece) => piece == SharedShadow ? Root + piece : Folder(look) + piece;

        /// <summary>The stored-reel texPath of a look's ThingStyleDef.</summary>
        public static string ReelTexPath(string look) => Folder(look) + ReelArt[0];

        /// <summary>The ThingStyleDef defName of the reel in a look: "RM_HoseReel_Industrial".</summary>
        public static string StyleDefName(string look) => AerialStyles.StyleDefName(ReelDef, look);

        /// <summary>
        /// The look a hose draws in. The reel's look (its stored style, or for a legacy unstyled reel the default look it
        /// draws in, as StylePicker.LookOfThing answers); never the global setting when the reel has a look of its own.
        /// A reel look that is not one of the four falls to the default look, then to Scrapper.
        /// </summary>
        public static string HoseLook(string reelLook, string defaultLook)
        {
            if (AerialStyles.IsLook(reelLook)) return reelLook;
            return AerialStyles.IsLook(defaultLook) ? defaultLook : Scrapper;
        }

        /// <summary>Only Scrapper's binding is sack cloth, so only it takes the "aged cloth" brown tint; the other looks'
        /// wraps (rubber, steel, alloy) are drawn in their own colour (still darkened by the wet tint).</summary>
        public static bool AgedClothWrap(string look) => look == Scrapper;

        /// <summary>Index of a look in AerialStyles.Looks (menu order), -1 for none.</summary>
        public static int LookIndex(string look) => look == null ? -1 : Array.IndexOf(AerialStyles.Looks, look);
    }
}
