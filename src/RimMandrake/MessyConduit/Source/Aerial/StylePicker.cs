using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit.Aerial
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
        private static readonly Dictionary<ThingDef, ThingStyleDef[]> byDef = new Dictionary<ThingDef, ThingStyleDef[]>();
        private static readonly Dictionary<ThingStyleDef, string> lookOf = new Dictionary<ThingStyleDef, string>();
        private static readonly Dictionary<ThingDef, string> lastPicked = new Dictionary<ThingDef, string>();
        /// <summary>State read: style defs missing at startup (each a config error, not a silent fallback).</summary>
        public static readonly List<string> Missing = new List<string>();
        /// <summary>State read: picks made through the menu or the probe this session.</summary>
        public static int picks;

        static StylePicker()
        {
            foreach (string dn in AerialStyles.StyledDefs)
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(dn);
                if (d == null) { Missing.Add(dn); continue; }
                var arr = new ThingStyleDef[AerialStyles.Looks.Length];
                for (int i = 0; i < arr.Length; i++)
                {
                    string sn = AerialStyles.StyleDefName(dn, AerialStyles.Looks[i]);
                    arr[i] = DefDatabase<ThingStyleDef>.GetNamedSilentFail(sn);
                    if (arr[i] == null) { Missing.Add(sn); continue; }
                    lookOf[arr[i]] = AerialStyles.Looks[i];
                }
                byDef[d] = arr;
            }
            foreach (string m in Missing) Log.Error("[MessyConduit] style def missing: " + m);
            InjectBracketOffsets();
            var styled = new bool[DefDatabase<ThingDef>.DefCount + 16];
            foreach (ThingDef d in byDef.Keys) if (d.index < styled.Length) styled[d.index] = true;
            StyleIndex.styled = styled;
        }

        public static bool IsStyled(ThingDef d) => d != null && byDef.ContainsKey(d);

        public static ThingStyleDef StyleFor(ThingDef d, string look)
        {
            if (d == null || !byDef.TryGetValue(d, out ThingStyleDef[] arr)) return null;
            int i = Array.IndexOf(AerialStyles.Looks, look);
            return i >= 0 ? arr[i] : null;
        }

        public static string LookOfStyle(ThingStyleDef s) => s != null && lookOf.TryGetValue(s, out string l) ? l : null;

        /// <summary>The default look: the Mod Setting `style` (now "what new buttons start on and how unstyled poles draw").</summary>
        public static string DefaultLook => AerialMaterials.LookOf(MessyConduitSettings.style);

        /// <summary>The style stored on the thing itself (null for a legacy, unstyled building).</summary>
        public static ThingStyleDef RawStyle(Thing t) => (t as ThingWithComps)?.compStyleable?.styleDef;

        /// <summary>The look the thing draws in: its stored style's look, else the default look.</summary>
        public static string LookOfThing(Thing t) => LookOfStyle(RawStyle(t)) ?? DefaultLook;

        public static string LastPicked(ThingDef d) => d != null && lastPicked.TryGetValue(d, out string l) ? l : null;

        /// <summary>The style our getter hands the designator now (AerialStyles.Resolve on this button's state).</summary>
        public static ThingStyleDef Resolve(Designator_Build des)
        {
            ThingDef d = des?.PlacingDef as ThingDef;
            if (!IsStyled(d)) return null;
            string look = AerialStyles.Resolve(LastPicked(d), DefaultLook, des.styleOverridden, LookOfStyle(des.styleDef));
            return StyleFor(d, look);
        }

        /// <summary>A menu pick (also the probe's "style:" verb, so the live check drives this same code): remember it for
        /// this button and leave any "Copy" state, so the getter answers the pick.</summary>
        public static void Pick(Designator_Build des, string look)
        {
            ThingDef d = des?.PlacingDef as ThingDef;
            if (!IsStyled(d) || !AerialStyles.IsLook(look)) return;
            lastPicked[d] = look;
            des.styleOverridden = false;
            des.styleDef = StyleFor(d, look);
            picks++;
        }

        public static void ClearPicks() => lastPicked.Clear();

        public static List<FloatMenuOption> MenuFor(Designator_Build des)
        {
            var list = new List<FloatMenuOption>();
            ThingDef d = des.PlacingDef as ThingDef;
            string cur = LookOfStyle(Resolve(des));
            foreach (string look in AerialStyles.Looks)
            {
                ThingStyleDef s = StyleFor(d, look);
                if (s == null) continue;
                string l = look;
                string label = look + (look == cur ? " (current)" : "") + (look == DefaultLook ? " - default" : "");
                list.Add(new FloatMenuOption(label, () => Pick(des, l), s.UIIcon ?? (Texture2D)Widgets.GetIconFor(d, null, s), Color.white));
            }
            return list;
        }

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

    /// <summary>Lock-free fast path for the hot Thing.StyleDef postfix: null until StylePicker has run.</summary>
    public static class StyleIndex
    {
        public static bool[] styled;

        public static bool Is(ThingDef d)
        {
            bool[] a = styled;
            return a != null && d != null && d.index < a.Length && a[d.index];
        }
    }

    /// <summary>The build button opens the 4-style menu (the way walls ask for a material), after vanilla selected it.</summary>
    [HarmonyPatch(typeof(Designator_Build), nameof(Designator_Build.ProcessInput))]
    internal static class Patch_DesignatorBuild_ProcessInput
    {
        private static void Postfix(Designator_Build __instance)
        {
            try
            {
                if (!StylePicker.IsStyled(__instance.PlacingDef as ThingDef)) return;
                if (Find.DesignatorManager.SelectedDesignator != __instance) return;     // vanilla refused (CheckCanInteract)
                List<FloatMenuOption> opts = StylePicker.MenuFor(__instance);
                if (opts.Count > 0) Find.WindowStack.Add(new FloatMenu(opts));
            }
            catch (Exception ex) { Log.ErrorOnce("[MessyConduit] style menu: " + ex, 0x5E1E01); }
        }
    }

    /// <summary>For our defs the designator's style is the picked (or copied) look in EVERY game mode. DesignateSingleCell
    /// reads this getter for both the blueprint and the god-mode building, and ThingStyleDefForPreview (the button icon).</summary>
    [HarmonyPatch(typeof(Designator_Build), nameof(Designator_Build.ThingStyleDefNonPreceptSource), MethodType.Getter)]
    internal static class Patch_DesignatorBuild_StyleGetter
    {
        private static void Postfix(Designator_Build __instance, ref ThingStyleDef __result)
        {
            if (__instance.sourcePrecept != null || !StyleIndex.Is(__instance.PlacingDef as ThingDef)) return;
            __result = StylePicker.Resolve(__instance) ?? __result;
        }
    }

    /// <summary>A "Copy" of one of our buildings/frames/blueprints always carries its look: Blueprint_Build passes its own
    /// styleOverridden (usually false) where Building/Frame/Blueprint_Install pass true.</summary>
    [HarmonyPatch(typeof(BuildCopyCommandUtility), nameof(BuildCopyCommandUtility.BuildCopyCommand))]
    internal static class Patch_BuildCopyCommand_CarryStyle
    {
        private static void Prefix(BuildableDef buildable, ThingStyleDef style, ref bool styleOverridden)
        {
            if (style != null && StyleIndex.Is(buildable as ThingDef)) styleOverridden = true;
        }
    }

    /// <summary>Legacy: an anchor with no stored style reads as the default look's style, so it draws (Thing.Graphic), copies
    /// and is probed in that look. Only the getter answers; CompStyleable's saved field stays null, so an older save is not
    /// changed by loading it. Hot path: one array read for every other thing.</summary>
    [HarmonyPatch(typeof(Thing), nameof(Thing.StyleDef), MethodType.Getter)]
    internal static class Patch_Thing_StyleDef
    {
        private static void Postfix(Thing __instance, ref ThingStyleDef __result)
        {
            if (__result != null || !StyleIndex.Is(__instance.def)) return;
            __result = StylePicker.StyleFor(__instance.def, StylePicker.DefaultLook);
        }
    }

    /// <summary>Frame.CompleteConstruction copies the frame's style only when GetIdeoForStyle(worker) != null (decompiled
    /// 1.6): a worker with no ideoligion would drop the picked look. Re-apply it on our defs.</summary>
    [HarmonyPatch(typeof(Frame), nameof(Frame.CompleteConstruction))]
    internal static class Patch_Frame_KeepStyle
    {
        internal sealed class St { public ThingStyleDef Style; public IntVec3 Pos; public Map Map; public ThingDef Def; }

        /// <summary>State read: built things whose style this guard had to restore.</summary>
        public static int restored;

        private static void Prefix(Frame __instance, out St __state)
        {
            __state = null;
            if (!(__instance.def.entityDefToBuild is ThingDef d) || !StyleIndex.Is(d)) return;
            ThingStyleDef s = StylePicker.RawStyle(__instance);
            if (s != null) __state = new St { Style = s, Pos = __instance.Position, Map = __instance.Map, Def = d };
        }

        private static void Postfix(St __state)
        {
            if (__state?.Map == null) return;
            foreach (Thing t in __state.Pos.GetThingList(__state.Map))
            {
                if (t.def != __state.Def || StylePicker.RawStyle(t) != null) continue;
                t.StyleDef = __state.Style;
                t.DirtyMapMesh(t.Map);
                restored++;
            }
        }
    }
}
