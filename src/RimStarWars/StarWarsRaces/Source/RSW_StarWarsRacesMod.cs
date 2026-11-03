using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Races
{
    public class RSW_StarWarsRacesSettings : ModSettings
    {
        public static bool hideFacialAnimationFace = true;
        public static bool geonosianHiveEnabled = true;
        public static bool bothanWrenduiFurEnabled = true;
        public static bool abednedoTunnelBornEnabled = true;

        /// <summary>The switch a species condition names in its XML `setting` field. An unknown or empty name reads
        /// ON, so a typo in a def can never silently disable a mechanic; selftest_species_character_genes checks
        /// that every name used in the defs is one of these.</summary>
        public static bool SpeciesMechanicOn(string setting)
        {
            switch (setting)
            {
                case "geonosianHiveEnabled": return geonosianHiveEnabled;
                case "bothanWrenduiFurEnabled": return bothanWrenduiFurEnabled;
                case "abednedoTunnelBornEnabled": return abednedoTunnelBornEnabled;
                default: return true;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref hideFacialAnimationFace, "hideFacialAnimationFace", true);
            Scribe_Values.Look(ref geonosianHiveEnabled, "geonosianHiveEnabled", true);
            Scribe_Values.Look(ref bothanWrenduiFurEnabled, "bothanWrenduiFurEnabled", true);
            Scribe_Values.Look(ref abednedoTunnelBornEnabled, "abednedoTunnelBornEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Facial Animation", RimMandrake.Shared.SettingScope.Now, new[] { "hideFacialAnimationFace" }))
            {
                list.CheckboxLabeled("Keep Facial Animation's face off our species", ref hideFacialAnimationFace,
                    "Shipped default: ON. Our Star Wars species wear painted heads; with the Facial Animation mod installed, "
                  + "its animated eyes and mouth would draw over the painting. On: Facial Animation skips every xenotype "
                  + "listed in RSW_FacialAnimationOptOut, whatever its own settings say. Off: Facial Animation's own "
                  + "settings decide. Does nothing without Facial Animation. A pawn already on the map picks up the change "
                  + "when its graphics next refresh (for example on reload).");
                list.GapLine();
            }

            if (Group(list, "Species character", RimMandrake.Shared.SettingScope.Now,
                    new[] { "geonosianHiveEnabled", "bothanWrenduiFurEnabled", "abednedoTunnelBornEnabled" }))
            {
                list.CheckboxLabeled("Geonosian: hive-minded", ref geonosianHiveEnabled,
                    "Shipped default: ON. Geonosians work and research faster with two or more other Geonosians within "
                  + "15 cells, and slower when no other Geonosian is on the map. Off: the gene does nothing (it replaced "
                  + "their old terrible-social aptitude, which does not come back).");
                list.CheckboxLabeled("Bothan: mood-showing fur", ref bothanWrenduiFurEnabled,
                    "Shipped default: ON. A content Bothan (mood 65% or more) negotiates, trades and persuades better; an "
                  + "unhappy one (below 30%) is given away by its fur and does all three worse. Off: the gene does nothing "
                  + "(it replaced their old strong-social aptitude, which does not come back).");
                list.CheckboxLabeled("Abednedo: tunnel-born", ref abednedoTunnelBornEnabled,
                    "Shipped default: ON. Abednedo mine and build faster under an overhead-mountain roof, a nod to their "
                  + "underground ancestry. Off: the gene does nothing (it replaced their old strong-construction "
                  + "aptitude, which does not come back).");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 12f;
            list.End();
            Widgets.EndScrollView();
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 600f;

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field
        // initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RSW_StarWarsRacesSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RSW_StarWarsRacesSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10).</summary>
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
    }

    public class RSW_StarWarsRacesMod : Mod
    {
        public const string HarmonyId = "mandrake.rsw.starwarsraces";
        public static RSW_StarWarsRacesSettings settings;

        public RSW_StarWarsRacesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_StarWarsRacesSettings>();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony(HarmonyId), Assembly.GetExecutingAssembly(), "RimMandrake.StarWarsRaces");
        }

        public override string SettingsCategory()
        {
            return "Star Wars Races";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
