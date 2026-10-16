using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.Shared.StylePicker;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>
    /// Per-build style for the overhead-line anchors (design/RimMandrake/messyconduit_style_per_build_design.md,
    /// architecture B, stage 1). The look is stored on each building in the engine's own style field (CompStyleable), as
    /// one of the ThingStyleDefs in Defs/Aerial/RM_AerialStyles.xml; the engine carries it blueprint -> frame -> building
    /// -> minified -> save and draws the style's graphic by itself. This class adds only:
    ///   * the build button's 4-item menu (<see cref="Patch_DesignatorBuild_ProcessInput"/>), remembering the last pick
    ///     per button for the session, starting from the "default style" Mod Setting (key `style`, unchanged);
    ///   * the designator's style getter for our defs (<see cref="Patch_DesignatorBuild_StyleGetter"/>): vanilla honours a
    ///     pick only in Ideology's classic mode; ours honours it in every mode, and a "Copy" carries the copied look;
    ///   * legacy: a building with no stored style READS as the default look's style (<see cref="Patch_Thing_StyleDef"/>),
    ///     never written to the save, so an older save looks exactly as it did and keeps no new data;
    ///   * a guard on Frame.CompleteConstruction, which copies the style only when the worker has an ideoligion.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class StylePicker
    {
        /// <summary>The shared def-agnostic picker (_Shared/StylePicker), this assembly's own instance.</summary>
        internal static readonly StylePickerCore Core =
            new StylePickerCore("[GimmeSomeSlack]", AerialStyles.Looks, () => DefaultLook, AerialStyles.Resolve);
        /// <summary>State read: style defs missing at startup (each a config error, not a silent fallback).</summary>
        public static List<string> Missing => Core.Missing;
        /// <summary>State read: picks made through the menu or the probe this session.</summary>
        public static int picks => Core.picks;

        static StylePicker()
        {
            // the hose reel registers with FlowWorks' own picker since the hose port (FlowWorks/Source/Hose/HoseLook.cs)
            Core.Register(AerialStyles.StyledDefs, AerialStyles.StyleDefName);
            InjectBracketOffsets();       // GSS-only bootstrap, after registration (G2.3)
            StyleIndex.core = Core;
        }

        public static bool IsStyled(ThingDef d) => Core.IsStyled(d);
        public static ThingStyleDef StyleFor(ThingDef d, string look) => Core.StyleFor(d, look);
        public static string LookOfStyle(ThingStyleDef s) => Core.LookOfStyle(s);

        /// <summary>The default look: the Mod Setting `style` (now "what new buttons start on and how unstyled poles draw").</summary>
        public static string DefaultLook => AerialMaterials.LookOf(GimmeSomeSlackSettings.style);

        /// <summary>The style stored on the thing itself (null for a legacy, unstyled building).</summary>
        public static ThingStyleDef RawStyle(Thing t) => StylePickerCore.RawStyle(t);

        /// <summary>The look the thing draws in: its stored style's look, else the default look.</summary>
        public static string LookOfThing(Thing t) => Core.LookOfThing(t);

        public static string LastPicked(ThingDef d) => Core.LastPicked(d);

        /// <summary>The style our getter hands the designator now (AerialStyles.Resolve on this button's state).</summary>
        public static ThingStyleDef Resolve(Designator_Build des) => Core.Resolve(des);

        /// <summary>A menu pick (also the probe's "style:" verb, so the live check drives this same code).</summary>
        public static void Pick(Designator_Build des, string look) => Core.Pick(des, look);

        public static void ClearPicks() => Core.ClearPicks();

        public static List<FloatMenuOption> MenuFor(Designator_Build des) => Core.MenuFor(des);

        /// <summary>The graphic data the thing is drawn with (its style's when it has one, which includes the legacy default):
        /// a wall bracket's per-facing draw offset comes from here, so the wire lands on the drawn insulator.</summary>
        public static GraphicData GraphicDataOf(Thing t) => t?.StyleDef?.graphicData ?? t?.def?.graphicData;

        private static readonly string[] RotNames = { "North", "East", "South", "West" };

        /// <summary>Round 2's per-look plate-on-the-wall offsets (AerialMath.BracketDrawOffset over the measured
        /// BracketGeometryTable), written into each bracket STYLE def's own GraphicData (and its blueprint copy): our own
        /// defs, fixed per look, never the shared ThingDef.</summary>
        private static void InjectBracketOffsets()
        {
            ThingDef br = DefDatabase<ThingDef>.GetNamedSilentFail("RM_AerialWallBracket");
            foreach (string look in AerialStyles.Looks)
            {
                ThingStyleDef s = StyleFor(br, look);
                if (s?.graphicData == null) continue;
                foreach (GraphicData gd in new[] { s.graphicData, s.blueprintGraphicData })
                {
                    if (gd == null) continue;
                    gd.drawOffsetNorth = AerialMaterials.BracketDrawOffset(look, 0) ?? gd.drawOffsetNorth;
                    gd.drawOffsetEast = AerialMaterials.BracketDrawOffset(look, 1) ?? gd.drawOffsetEast;
                    gd.drawOffsetSouth = AerialMaterials.BracketDrawOffset(look, 2) ?? gd.drawOffsetSouth;
                    gd.drawOffsetWest = AerialMaterials.BracketDrawOffset(look, 3) ?? gd.drawOffsetWest;
                }
            }
        }

        public static string RotName(int r) => RotNames[r & 3];
    }

    /// <summary>Lock-free fast path for the hot Thing.StyleDef postfix: null until StylePicker has run. The flags array is the
    /// shared core's; ConduitStylePicker adds its conduit defs into the same array.</summary>
    public static class StyleIndex
    {
        internal static StylePickerCore core;

        public static bool[] styled => core?.styled;

        public static bool Is(ThingDef d) => core != null && core.IsIndexed(d);
    }

    /// <summary>The build button opens the 4-style menu (the way walls ask for a material), after vanilla selected it.</summary>
    [RimMandrake.Shared.PatchFeature("Overhead lines: anchor looks", typeof(AerialSettings), "enabled")]
    [HarmonyPatch(typeof(Designator_Build), nameof(Designator_Build.ProcessInput))]
    internal static class Patch_DesignatorBuild_ProcessInput
    {
        private static void Postfix(Designator_Build __instance) => StyleIndex.core?.ProcessInputPostfix(__instance, 0x5E1E01);
    }

    /// <summary>For our defs the designator's style is the picked (or copied) look in EVERY game mode. DesignateSingleCell
    /// reads this getter for both the blueprint and the god-mode building, and ThingStyleDefForPreview (the button icon).</summary>
    [RimMandrake.Shared.PatchFeature("Overhead lines: anchor looks", typeof(AerialSettings), "enabled")]
    [HarmonyPatch(typeof(Designator_Build), nameof(Designator_Build.ThingStyleDefNonPreceptSource), MethodType.Getter)]
    internal static class Patch_DesignatorBuild_StyleGetter
    {
        private static void Postfix(Designator_Build __instance, ref ThingStyleDef __result) => StyleIndex.core?.StyleGetterPostfix(__instance, ref __result);
    }

    /// <summary>A "Copy" of one of our buildings/frames/blueprints always carries its look: Blueprint_Build passes its own
    /// styleOverridden (usually false) where Building/Frame/Blueprint_Install pass true.</summary>
    [RimMandrake.Shared.PatchFeature("Overhead lines: anchor looks", typeof(AerialSettings), "enabled")]
    [HarmonyPatch(typeof(BuildCopyCommandUtility), nameof(BuildCopyCommandUtility.BuildCopyCommand))]
    internal static class Patch_BuildCopyCommand_CarryStyle
    {
        private static void Prefix(BuildableDef buildable, ThingStyleDef style, ref bool styleOverridden) => StyleIndex.core?.CopyPrefix(buildable, style, ref styleOverridden);
    }

    /// <summary>Legacy: an anchor with no stored style reads as the default look's style, so it draws (Thing.Graphic), copies
    /// and is probed in that look. Only the getter answers; CompStyleable's saved field stays null, so an older save is not
    /// changed by loading it. Hot path: one array read for every other thing.</summary>
    [RimMandrake.Shared.PatchFeature("Overhead lines: anchor looks", typeof(AerialSettings), "enabled")]
    [HarmonyPatch(typeof(Thing), nameof(Thing.StyleDef), MethodType.Getter)]
    internal static class Patch_Thing_StyleDef
    {
        private static void Postfix(Thing __instance, ref ThingStyleDef __result) => StyleIndex.core?.StyleDefPostfix(__instance, ref __result);
    }

    /// <summary>Frame.CompleteConstruction copies the frame's style only when GetIdeoForStyle(worker) != null (decompiled
    /// 1.6): a worker with no ideoligion would drop the picked look. Re-apply it on our defs.</summary>
    [RimMandrake.Shared.PatchFeature("Overhead lines: anchor looks", typeof(AerialSettings), "enabled")]
    [HarmonyPatch(typeof(Frame), nameof(Frame.CompleteConstruction))]
    internal static class Patch_Frame_KeepStyle
    {
        /// <summary>State read: built things whose style this guard had to restore.</summary>
        public static int restored => StyleIndex.core?.restored ?? 0;

        private static void Prefix(Frame __instance, out StylePickerCore.FrameState __state) => __state = StyleIndex.core?.FramePrefix(__instance);

        private static void Postfix(StylePickerCore.FrameState __state) => StyleIndex.core?.FramePostfix(__state);
    }
}
