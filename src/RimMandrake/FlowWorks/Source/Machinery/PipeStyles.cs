// Verse-free (the SelfTest compiles this file): the rigid universal pipe's per-build looks
// (owner rulings 2026-10-11 #1 and #8, design/RimMandrake/gss_flowworks_rulings_2026-10-11.md).
using System;

namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>
    /// The rigid universal pipe (RM_UniversalPipe) takes one of the same four looks as Gimme Some Slack's wires and FlowWorks'
    /// hose reel, picked on the build button through the SAME shared picker (_Shared/StylePicker/StylePickerCore.cs, owner
    /// 2026-10-11: "Support the different art styles as we did for the wires, using the same interface"). Each look is a
    /// ThingStyleDef RM_UniversalPipe_&lt;Look&gt; (Defs/Machinery/RM_UniversalPipeStyles.xml) whose graphicData is a Basic-linked
    /// atlas, so a run joins up in its look. A pipe with no stored style draws in the default look (pipeDefaultLook) and is
    /// never written: every pipe built before the looks existed keeps working.
    /// </summary>
    public static class PipeStyles
    {
        public const string PipeDef = "RM_UniversalPipe";

        /// <summary>Menu order: the wires' and the hose reel's (Scrapper, Industrial, Modern, Futuristic).</summary>
        public static readonly string[] Looks = { "Scrapper", "Industrial", "Modern", "Futuristic" };

        public const string Scrapper = "Scrapper";

        public static bool IsLook(string look) => look != null && Array.IndexOf(Looks, look) >= 0;

        /// <summary>The defs PipeLook registers with the shared style picker.</summary>
        public static readonly string[] StyledDefs = { PipeDef };

        /// <summary>The four liquid tanks take the same four looks (owner 2026-10-14, TANK_TALL_BUILD_TWICE_THE_DRINK: "They should
        /// have the same four variant styles as Gimme Some Slack."). Registered by PipeLook only once their style defs
        /// (RM_LiquidTankStyles.xml, ThingStyleDef &lt;Tank&gt;_&lt;Look&gt;) are loaded, so the build button grows the menu the moment
        /// the art is installed and never logs a missing style before it.</summary>
        /// <summary>The river weir takes the same four looks (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS, owner 2026-10-16).</summary>
        public const string WeirDef = "RM_BankWeir";

        public static readonly string[] TankDefs = { "RM_LiquidTank", "RM_LiquidTankTall", "RM_UniversalCargoTank", "RM_UniversalCargoTankXTall" };

        /// <summary>A tank look's owned art (texPath, no extension): RimMandrake/FlowWorks/Tank/&lt;Look&gt;/&lt;TankDef&gt;.</summary>
        public static string TankTexPath(string tankDef, string look) => "RimMandrake/FlowWorks/Tank/" + DefaultLook(look) + "/" + tankDef;

        /// <summary>"RM_UniversalPipe_Industrial".</summary>
        public static string StyleDefName(string defName, string look) => defName + "_" + look;

        /// <summary>Same rule as the wires and the reel: a copy builds the copied look (an unstyled copy builds the default),
        /// else the button's last pick, else the default look.</summary>
        public static string Resolve(string lastPicked, string defaultLook, bool styleOverridden, string copiedLook)
        {
            if (styleOverridden) return IsLook(copiedLook) ? copiedLook : defaultLook;
            return IsLook(lastPicked) ? lastPicked : defaultLook;
        }

        /// <summary>The default look a setting value names (an unknown value reads Scrapper).</summary>
        public static string DefaultLook(string setting) => IsLook(setting) ? setting : Scrapper;

        /// <summary>Where a look's owned art is installed (texPath, no extension): the linked atlas and the menu icon.</summary>
        public const string Root = "RimMandrake/FlowWorks/Pipe/";
        public static string AtlasPath(string look) => Root + DefaultLook(look) + "/UniversalPipe_Atlas";
        public static string IconPath(string look) => Root + DefaultLook(look) + "/UniversalPipe_MenuIcon";
    }
}
