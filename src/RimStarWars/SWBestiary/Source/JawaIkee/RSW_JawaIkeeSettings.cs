using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.JawaIkee
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for the Ikee thought worker.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs.
    //
    // This assembly (Assemblies/JawaIkee.dll) ships inside the SWBestiary
    // mod folder but is a SEPARATE, unmerged DLL from the Livestock one
    // (RimMandrakeLivestockRSW.dll, its own RSW_LivestockSettings) — see
    // SWBestiary/About.xml's own "left in place, unmerged" notes for both.
    // Two settings entries under one packageId is the honest shape of that:
    // this one is titled distinctly so it reads as SWBestiary's Ikee slice,
    // not a whole second mod.
    //
    // One runtime mechanic here: ThoughtWorker_IkeeNearby. Its per-thought
    // radius and tolerant-xenotype list are already def-editable via
    // IkeeToleranceExtension in XML — that is the right place for a design
    // call, not a global settings duplicate — so the only thing worth a
    // player-facing toggle is turning the whole mood effect off.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_JawaIkeeSettings : ModSettings
    {
        public static bool ikeeThoughtEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ikeeThoughtEnabled, "ikeeThoughtEnabled", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RSW_JawaIkeeSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RSW_JawaIkeeSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): the thought worker reads the switch each time the thought is evaluated; nothing is read at map or world generation, so it is [now].</summary>
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
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Ikee mood effect", RimMandrake.Shared.SettingScope.Now, new[] { "ikeeThoughtEnabled" }))
            {
                list.CheckboxLabeled("\"The ikee is watching me\" mood effect", ref ikeeThoughtEnabled,
                    "Pawns near an ikee get a mood thought: comforted if their xenotype is one that "
                  + "keeps creepy pets, unsettled otherwise. Off: the ikee has no mood effect on "
                  + "anyone.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RSW_JawaIkeeMod : Mod
    {
        public static RSW_JawaIkeeSettings settings;

        public RSW_JawaIkeeMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_JawaIkeeSettings>();
        }

        public override string SettingsCategory()
        {
            return "SW Bestiary: Ikee";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
