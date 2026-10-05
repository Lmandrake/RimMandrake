// Verse-free (the SelfTest compiles this file): the per-build style rules of design
// design/RimMandrake/messyconduit_style_per_build_design.md (architecture B, stage 1: poles alone).
using System;
using System.Collections.Generic;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>
    /// The four looks a pole can be built in, how their ThingStyleDefs are named, and the two rules stage 1 needs:
    /// what style the build button hands the designator (<see cref="Resolve"/>); which look a span between two poles draws in
    /// is stage 2's run rule (ConduitStyles.SpanLook: the larger run wins, a tie goes to the older). The look rides the engine's own per-building style field (CompStyleable).
    /// </summary>
    public static class AerialStyles
    {
        /// <summary>Menu order (owner brief 2026-10-04): Scrapper, Industrial, Modern, Futuristic.</summary>
        public static readonly string[] Looks = { "Scrapper", "Industrial", "Modern", "Futuristic" };

        /// <summary>The anchors styled in stage 1.</summary>
        public static readonly string[] StyledDefs = { "RM_AerialMast", "RM_AerialLampMast", "RM_AerialWallBracket" };

        public static bool IsLook(string look) => look != null && Array.IndexOf(Looks, look) >= 0;

        /// <summary>The ThingStyleDef defName for an anchor def in a look: "RM_AerialMast_Industrial".</summary>
        public static string StyleDefName(string defName, string look) => defName + "_" + look;

        /// <summary>The look a style defName carries (its suffix), or null when it is not one of ours.</summary>
        public static string LookOfStyleDefName(string styleDefName)
        {
            if (string.IsNullOrEmpty(styleDefName)) return null;
            int i = styleDefName.LastIndexOf('_');
            if (i <= 0) return null;
            string look = styleDefName.Substring(i + 1);
            string def = styleDefName.Substring(0, i);
            return IsLook(look) && Array.IndexOf(StyledDefs, def) >= 0 ? look : null;
        }

        /// <summary>
        /// The look the build button hands to the blueprint / god-mode building (our replacement for vanilla's
        /// ThingStyleDefNonPreceptSource on our defs, which only honours a pick in Ideology's classic mode):
        ///   * a copy ("Copy" gizmo: styleOverridden with a style) builds the copied look, in every game mode;
        ///   * a copy of an unstyled (legacy) building builds the default look, which is how that building draws;
        ///   * otherwise the look last picked on this button's menu, else the default look (the Mod Setting).
        /// </summary>
        public static string Resolve(string lastPicked, string defaultLook, bool styleOverridden, string copiedLook)
        {
            if (styleOverridden) return IsLook(copiedLook) ? copiedLook : defaultLook;
            return IsLook(lastPicked) ? lastPicked : defaultLook;
        }

        /// <summary>Vanilla's rule (Designator_Build.ThingStyleDefNonPreceptSource, decompiled 1.6) for our defs, which no
        /// ideoligion styles: the pick counts only in classic mode with styleOverridden, else the ideo's style (none).
        /// Kept as the selftest's can-fail: without our getter the picked look never reaches the building.</summary>
        public static string VanillaResolve(bool classicMode, bool styleOverridden, string designatorStyleLook) =>
            classicMode && styleOverridden ? designatorStyleLook : null;

        /// <summary>The key both geometry tables use: "Look/defName" (PoleGeometryTable) or "Look/RotName" (brackets).</summary>
        public static string GeomKey(string look, string what) => look + "/" + what;

        /// <summary>A per-look table lookup with an explicit miss (no silent fallback to another look's numbers).</summary>
        public static bool TryLookup<T>(Dictionary<string, T> table, string look, string what, out T v)
        {
            v = default(T);
            return table != null && IsLook(look) && table.TryGetValue(GeomKey(look, what), out v);
        }
    }
}
