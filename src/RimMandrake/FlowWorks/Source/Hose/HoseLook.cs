using HarmonyLib;
using RimMandrake.Shared;
using RimMandrake.Shared.StylePicker;
using RimWorld;
using System.Collections.Generic;
using Verse;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// The hose reel's per-build look (hose port step 2, design v2 §5.2 / FINAL §3.8): FlowWorks' own instance of the shared
    /// def-agnostic style picker (_Shared/StylePicker/StylePickerCore.cs), registering only RM_HoseReel, with FlowWorks' own
    /// default-look setting (RM_HoseSettings.defaultLook). The look is stored on each reel in the engine's style field; a reel
    /// with no stored style draws in the default look and is never written. GimmeSomeSlack is not read at all.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class HoseLook
    {
        internal static readonly StylePickerCore Core =
            new StylePickerCore("[FlowWorks]", HoseStyles.Looks, () => DefaultLook, HoseStyles.Resolve);

        static HoseLook()
        {
            Core.Register(HoseStyles.StyledDefs, HoseStyles.StyleDefName);
            HoseStyleIndex.core = Core;
        }

        /// <summary>State read: style defs missing at startup.</summary>
        public static List<string> Missing => Core.Missing;
        public static int picks => Core.picks;

        /// <summary>The look of a reel built without a picked style: FlowWorks' own setting (an unknown value reads Scrapper).</summary>
        public static string DefaultLook => HoseStyles.IsLook(RM_HoseSettings.defaultLook) ? RM_HoseSettings.defaultLook : HoseStyles.Scrapper;

        public static bool IsStyled(ThingDef d) => Core.IsStyled(d);
        public static ThingStyleDef StyleFor(ThingDef d, string look) => Core.StyleFor(d, look);
        public static string LookOfStyle(ThingStyleDef s) => Core.LookOfStyle(s);
        public static ThingStyleDef RawStyle(Thing t) => StylePickerCore.RawStyle(t);
        public static string LookOfThing(Thing t) => Core.LookOfThing(t);
        public static string LastPicked(ThingDef d) => Core.LastPicked(d);
        public static ThingStyleDef Resolve(Designator_Build des) => Core.Resolve(des);
        public static void Pick(Designator_Build des, string look) => Core.Pick(des, look);
        public static void ClearPicks() => Core.ClearPicks();
        public static List<FloatMenuOption> MenuFor(Designator_Build des) => Core.MenuFor(des);
    }

    /// <summary>Null until HoseLook has run, so the hot patches never trigger HoseLook's static constructor early.</summary>
    internal static class HoseStyleIndex
    {
        internal static StylePickerCore core;
    }

    [PatchFeature("Flexible hoses: reel look picker", typeof(RM_HoseSettings), nameof(RM_HoseSettings.enabled))]
    [HarmonyPatch(typeof(Designator_Build), nameof(Designator_Build.ProcessInput))]
    internal static class Patch_Hose_DesignatorBuild_ProcessInput
    {
        private static void Postfix(Designator_Build __instance)
        {
            if (RM_HoseSettings.enabled) HoseStyleIndex.core?.ProcessInputPostfix(__instance, 0x5E1E71);
        }
    }

    [PatchFeature("Flexible hoses: reel look picker", typeof(RM_HoseSettings), nameof(RM_HoseSettings.enabled))]
    [HarmonyPatch(typeof(Designator_Build), nameof(Designator_Build.ThingStyleDefNonPreceptSource), MethodType.Getter)]
    internal static class Patch_Hose_DesignatorBuild_StyleGetter
    {
        private static void Postfix(Designator_Build __instance, ref ThingStyleDef __result) => HoseStyleIndex.core?.StyleGetterPostfix(__instance, ref __result);
    }

    [PatchFeature("Flexible hoses: reel look picker", typeof(RM_HoseSettings), nameof(RM_HoseSettings.enabled))]
    [HarmonyPatch(typeof(BuildCopyCommandUtility), nameof(BuildCopyCommandUtility.BuildCopyCommand))]
    internal static class Patch_Hose_BuildCopyCommand_CarryStyle
    {
        private static void Prefix(BuildableDef buildable, ThingStyleDef style, ref bool styleOverridden) => HoseStyleIndex.core?.CopyPrefix(buildable, style, ref styleOverridden);
    }

    /// <summary>Legacy: a reel with no stored style reads as the default look's style (hot path: one array read).</summary>
    [PatchFeature("Flexible hoses: reel look picker", typeof(RM_HoseSettings), nameof(RM_HoseSettings.enabled))]
    [HarmonyPatch(typeof(Thing), nameof(Thing.StyleDef), MethodType.Getter)]
    internal static class Patch_Hose_Thing_StyleDef
    {
        private static void Postfix(Thing __instance, ref ThingStyleDef __result) => HoseStyleIndex.core?.StyleDefPostfix(__instance, ref __result);
    }

    /// <summary>Frame.CompleteConstruction keeps the frame's style only for an ideo worker; re-apply it on the reel.</summary>
    [PatchFeature("Flexible hoses: reel look picker", typeof(RM_HoseSettings), nameof(RM_HoseSettings.enabled))]
    [HarmonyPatch(typeof(Frame), nameof(Frame.CompleteConstruction))]
    internal static class Patch_Hose_Frame_KeepStyle
    {
        public static int restored => HoseStyleIndex.core?.restored ?? 0;

        private static void Prefix(Frame __instance, out StylePickerCore.FrameState __state) => __state = HoseStyleIndex.core?.FramePrefix(__instance);

        private static void Postfix(StylePickerCore.FrameState __state) => HoseStyleIndex.core?.FramePostfix(__state);
    }
}
