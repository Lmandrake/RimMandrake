using System.Collections.Generic;
using System.Reflection;
// MOD_OPTIONS_RETROFIT_1 — Mod Settings for River Colors.
//
// House style: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs.
//
// The one mechanism (Patch_WorldDrawLayer_Paths_GeneratePaths) substitutes a
// per-tile gradient colour for the world map's river mesh. The three hardcoded
// anchor colours (headwater/jungle/terminus) are exposed as RGB sliders with a
// live swatch; a master toggle reverts to vanilla's single flat river colour.
// WORLDGEN-AFFECTING NOTE: none of this touches worldgen — it only repaints the
// planet-view river mesh. The colours are read when that layer is generated, which
// happens when the world is drawn afresh (a load), so every setting is labelled
// [next game start] on the screen.
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.RiverColors
{
    public class RiverColorsSettings : ModSettings
    {
        public static bool enabled = true;

        public static Color headwaterColor = new Color(0xE0 / 255f, 0x31 / 255f, 0x1C / 255f);
        public static Color jungleColor = new Color(0x7A / 255f, 0x7A / 255f, 0x2E / 255f);
        public static Color terminusColor = new Color(0x3D / 255f, 0x4A / 255f, 0x52 / 255f);

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref headwaterColor, "headwaterColor",
                new Color(0xE0 / 255f, 0x31 / 255f, 0x1C / 255f));
            Scribe_Values.Look(ref jungleColor, "jungleColor",
                new Color(0x7A / 255f, 0x7A / 255f, 0x2E / 255f));
            Scribe_Values.Look(ref terminusColor, "terminusColor",
                new Color(0x3D / 255f, 0x4A / 255f, 0x52 / 255f));
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int/Color setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RiverColorsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int) || f.FieldType == typeof(Color))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RiverColorsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): the river mesh colours are read when the planet-view river layer is generated (GeneratePaths prefix), which happens when the world is drawn afresh and not when a setting changes, and the on/off patch is applied at startup, so every setting is [next game start]. Nothing here touches worldgen: it only repaints the mesh.</summary>
        private static bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && RimMandrake.Shared.SettingsKitCore.Matches(n, searchQuery)) hit = true;
                if (!hit) return false;
            }
            bool open = searching || !collapsedSections.Contains(title);
            Text.Font = GameFont.Medium;
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            Text.Font = GameFont.Small;
            if (!open) return false;
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 400f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "River colouring", RimMandrake.Shared.SettingScope.Now, new[] { "enabled" }, "[next game start]"))
            {
                list.CheckboxLabeled("Colour rivers by position", ref enabled,
                    "Off: rivers draw with the game's own single flat colour, as if this mod "
                  + "were not installed. On by default. The planet-view river mesh is rebuilt "
                  + "when the world is drawn afresh (a load), not the moment a setting changes.");
                list.GapLine();
            }

            if (Group(list, "Gradient colours", RimMandrake.Shared.SettingScope.Now, new[] { "headwaterColor", "jungleColor", "terminusColor" }, "[next game start]"))
            {
                list.Label("Red at the headwaters, fading through this colour in the jungle "
                  + "reaches, ending in this colour at the dead-river termini.");
                ColorSection(list, "Headwater colour (red spore-toxin country)", ref headwaterColor);
                ColorSection(list, "Jungle colour (brackish green/brown)", ref jungleColor);
                ColorSection(list, "Terminus colour (toxic brown/blue salt flats)", ref terminusColor);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }

        private static void ColorSection(Listing_Standard list, string label, ref Color color)
        {
            list.Label(label);

            Rect row = list.GetRect(24f);
            Rect swatch = row.LeftPart(0.12f);
            Widgets.DrawBoxSolid(swatch, color);
            Widgets.DrawBox(swatch);

            float r = color.r, g = color.g, b = color.b;
            r = list.Slider(r, 0f, 1f);
            g = list.Slider(g, 0f, 1f);
            b = list.Slider(b, 0f, 1f);
            color = new Color(r, g, b);
            list.Gap();
        }
    }

    public class RiverColorsMod : Mod
    {
        public static RiverColorsSettings settings;

        public RiverColorsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RiverColorsSettings>();
        }

        public override string SettingsCategory()
        {
            return "River Colors";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
