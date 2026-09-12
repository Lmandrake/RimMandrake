using System;
using System.Reflection;
using UnityEngine;
using Verse;
using RimWorld;

namespace RimMandrake.RustChrome
{
    // Tier 2 of ui_appearance_spec.md section 3: reflection-set Widgets' window/
    // section/option colour constants and InspectPaneUtility's tab-fill texture
    // once at startup. Every field below is `static readonly` (not `const`), so a
    // reflection SetValue after Widgets' own static constructor has already run
    // is legal and takes effect immediately - no Harmony, no patch, no draw code
    // touched. Field names verified against decompiled Verse.Widgets and
    // RimWorld.InspectPaneUtility (mcp__rimsage__read_csharp_symbol) before
    // writing this, per the project's standing "never guess a field name" rule.
    [StaticConstructorOnStartup]
    public static class RustChromeColors
    {
        // Palette per ui_appearance_spec.md section 3 Tier 2.
        private static readonly Color WindowFill = new Color(18f / 255f, 16f / 255f, 22f / 255f);
        private static readonly Color WindowBorder = new Color(122f / 255f, 72f / 255f, 48f / 255f);
        private static readonly Color SectionFill = new Color(38f / 255f, 32f / 255f, 30f / 255f);
        // Not named in the spec's colour list; chosen to sit between WindowFill and
        // SectionFill so an unselected option reads as recessed, not invisible.
        private static readonly Color SectionBorder = new Color(122f / 255f, 72f / 255f, 48f / 255f);
        private static readonly Color OptionUnselectedFill = new Color(28f / 255f, 24f / 255f, 24f / 255f);
        private static readonly Color OptionSelectedFill = new Color(0.42f, 0.32f, 0.16f);

        // MOD_OPTIONS_RETROFIT_1: vanilla's own values, captured before we ever
        // overwrite them, so the "theme enabled" toggle can put the game back to
        // stock colours exactly rather than guessing at Widgets' compiled defaults.
        private static Color vanillaWindowFill;
        private static Color vanillaWindowBorder;
        private static Color vanillaSectionFill;
        private static Color vanillaSectionBorder;
        private static Color vanillaOptionUnselectedFill;
        private static Color vanillaOptionSelectedFill;
        private static Texture2D vanillaInspectTabTex;
        private static bool captured;

        static RustChromeColors()
        {
            CaptureVanilla();
            // Settings' Mod subclass is constructed well before this
            // [StaticConstructorOnStartup] class runs, so the static field is
            // already populated; guard with the shipped-default (true) in case
            // load order ever changes.
            bool enabled = RustChromeMod.settings == null || RustChromeMod.settings.themeEnabled;
            Apply(enabled);
        }

        private static void CaptureVanilla()
        {
            if (captured) return;
            vanillaWindowFill = GetColorField(typeof(Widgets), "WindowBGFillColor");
            vanillaWindowBorder = GetColorField(typeof(Widgets), "WindowBGBorderColor");
            vanillaSectionFill = GetColorField(typeof(Widgets), "MenuSectionBGFillColor");
            vanillaSectionBorder = GetColorField(typeof(Widgets), "MenuSectionBGBorderColor");
            vanillaOptionUnselectedFill = GetColorField(typeof(Widgets), "OptionUnselectedBGFillColor");
            vanillaOptionSelectedFill = GetColorField(typeof(Widgets), "OptionSelectedBGFillColor");
            vanillaInspectTabTex = GetTexField(typeof(InspectPaneUtility), "InspectTabButtonFillTex");
            captured = true;
        }

        /// <summary>Applies the Rust &amp; Chrome palette (true) or restores vanilla's own colours (false). Safe to call repeatedly — e.g. live from the Mod Settings checkbox.</summary>
        public static void Apply(bool enabled)
        {
            CaptureVanilla();
            if (enabled)
            {
                SetColorField(typeof(Widgets), "WindowBGFillColor", WindowFill);
                SetColorField(typeof(Widgets), "WindowBGBorderColor", WindowBorder);
                SetColorField(typeof(Widgets), "MenuSectionBGFillColor", SectionFill);
                SetColorField(typeof(Widgets), "MenuSectionBGBorderColor", SectionBorder);
                SetColorField(typeof(Widgets), "OptionUnselectedBGFillColor", OptionUnselectedFill);
                SetColorField(typeof(Widgets), "OptionSelectedBGFillColor", OptionSelectedFill);
                SetTexField(typeof(InspectPaneUtility), "InspectTabButtonFillTex",
                    SolidColorMaterials.NewSolidColorTexture(WindowFill));
            }
            else
            {
                SetColorField(typeof(Widgets), "WindowBGFillColor", vanillaWindowFill);
                SetColorField(typeof(Widgets), "WindowBGBorderColor", vanillaWindowBorder);
                SetColorField(typeof(Widgets), "MenuSectionBGFillColor", vanillaSectionFill);
                SetColorField(typeof(Widgets), "MenuSectionBGBorderColor", vanillaSectionBorder);
                SetColorField(typeof(Widgets), "OptionUnselectedBGFillColor", vanillaOptionUnselectedFill);
                SetColorField(typeof(Widgets), "OptionSelectedBGFillColor", vanillaOptionSelectedFill);
                if (vanillaInspectTabTex != null)
                {
                    SetTexField(typeof(InspectPaneUtility), "InspectTabButtonFillTex", vanillaInspectTabTex);
                }
            }

            Log.Message("[RimMandrake.RustChrome] colour fields " + (enabled ? "set to theme." : "restored to vanilla."));
        }

        private static Color GetColorField(Type type, string fieldName)
        {
            FieldInfo field = type.GetField(fieldName, BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
            if (field == null)
            {
                Log.Error("[RimMandrake.RustChrome] field not found: " + type.FullName + "." + fieldName);
                return Color.white;
            }
            return (Color)field.GetValue(null);
        }

        private static Texture2D GetTexField(Type type, string fieldName)
        {
            FieldInfo field = type.GetField(fieldName, BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
            if (field == null)
            {
                Log.Error("[RimMandrake.RustChrome] field not found: " + type.FullName + "." + fieldName);
                return null;
            }
            return field.GetValue(null) as Texture2D;
        }

        private static void SetColorField(Type type, string fieldName, Color value)
        {
            FieldInfo field = type.GetField(fieldName, BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
            if (field == null)
            {
                Log.Error("[RimMandrake.RustChrome] field not found: " + type.FullName + "." + fieldName);
                return;
            }
            field.SetValue(null, value);
        }

        private static void SetTexField(Type type, string fieldName, Texture2D value)
        {
            FieldInfo field = type.GetField(fieldName, BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
            if (field == null)
            {
                Log.Error("[RimMandrake.RustChrome] field not found: " + type.FullName + "." + fieldName);
                return;
            }
            field.SetValue(null, value);
        }
    }
}
