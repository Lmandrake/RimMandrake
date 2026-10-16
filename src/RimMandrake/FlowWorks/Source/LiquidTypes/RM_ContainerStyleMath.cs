// LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS (owner 2026-10-16: "They too should have the four styles of art."; approved by
// card: material colour on the TRIM only, body keeps its painted style, liquid shows in the masked window).
// Verse-free on purpose: compiled straight into the offline SelfTest (Source/SelfTest/ContainerStyleChecks.cs).
// Design: design/RimMandrake/liquid_containers_four_styles_2026-10-16.md.
namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>The rules behind a bottle, bucket or barrel's look: which of the four styles it wears, the def and
    /// texture that style names, and the window colours of an empty or dirty container. The sprite carries a
    /// CutoutComplex mask: red = the liquid window (DrawColor), green = the trim (DrawColorTwo = the material), black =
    /// painted and never tinted.</summary>
    public static class RM_ContainerStyleMath
    {
        /// <summary>Menu order, the same four looks as the hoses, pipes and tanks (Scrapper is the owner's "Junker").</summary>
        public static readonly string[] Looks = { "Scrapper", "Industrial", "Modern", "Futuristic" };

        public static readonly string[] Sizes = { "Bottle", "Bucket", "Barrel" };

        /// <summary>What anything with no style picked falls back to: the generic water bottle.</summary>
        public const string FallbackLook = "Industrial";

        public static bool IsLook(string look)
        {
            if (look == null)
            {
                return false;
            }
            for (int i = 0; i < Looks.Length; i++)
            {
                if (Looks[i] == look)
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>ThingStyleDef defName for a size ("Bottle"/"Bucket"/"Barrel") and look.</summary>
        public static string StyleDefName(string size, string look) => "RM_" + size + "_" + look;

        public static string TexPath(string size, string look) => "Things/Item/Resource/FlowWorks/" + look + "/RM_" + size;

        /// <summary>The look a style defName names, or null when it is not one of ours.</summary>
        public static string LookOfStyleDefName(string defName)
        {
            if (defName == null || !defName.StartsWith("RM_"))
            {
                return null;
            }
            int us = defName.LastIndexOf('_');
            if (us < 3)
            {
                return null;
            }
            string look = defName.Substring(us + 1);
            string size = defName.Substring(3, us - 3);
            bool knownSize = false;
            for (int i = 0; i < Sizes.Length; i++)
            {
                if (Sizes[i] == size)
                {
                    knownSize = true;
                }
            }
            return knownSize && IsLook(look) ? look : null;
        }

        /// <summary>The style a container made by (or found with) a faction of this tech level wears when nobody picked
        /// one: tribes scavenge, industrial colonies use plain bottles, spacers buy soda, the ultra-tech carry canteens.
        /// Takes the TechLevel NAME so this stays Verse-free; unknown or Undefined reads the fallback.</summary>
        public static string LookForTech(string techLevel)
        {
            switch (techLevel)
            {
                case "Animal":
                case "Neolithic":
                case "Medieval":
                    return "Scrapper";
                case "Industrial":
                    return "Industrial";
                case "Spacer":
                    return "Modern";
                case "Ultra":
                case "Archotech":
                    return "Futuristic";
                default:
                    return FallbackLook;
            }
        }

        /// <summary>Window colour (r, g, b) of an EMPTY container: pale clear glass, so the window reads empty.</summary>
        public static readonly float[] EmptyWindow = { 0.86f, 0.90f, 0.93f };

        /// <summary>Window colour (r, g, b) of a DIRTY container: grime brown.</summary>
        public static readonly float[] DirtyWindow = { 0.46f, 0.38f, 0.27f };

        /// <summary>Two stacks of containers may merge only when their looks agree. An unstyled incoming stack is
        /// absorbed into a styled one (it takes the stack's look); a styled stack is never swallowed by an unstyled one.</summary>
        public static bool MayStack(string thisLook, string otherLook)
        {
            if (otherLook == null)
            {
                return true;
            }
            return thisLook == otherLook;
        }
    }
}
