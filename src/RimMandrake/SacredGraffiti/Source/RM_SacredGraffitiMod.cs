using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.SacredGraffiti
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for SacredGraffiti.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // The one runtime mechanism this assembly ships is
    // RitualOutcomeEffectWorker_PlaceSacredMark.ApplyExtraOutcome, which
    // spawns def.filthCountToSpawn.RandomInRange sacred-mark filth on a
    // POSITIVE ritual outcome. Two things worth exposing: a master on/off
    // (a favorable ritual just grants its ordinary vanilla outcome, no mark),
    // and a count multiplier on however many marks a god's own
    // RitualOutcomeEffectDef asks for.
    // ════════════════════════════════════════════════════════════════════
    public class RM_SacredGraffitiSettings : ModSettings
    {
        public static bool sacredMarkEnabled = true;
        public static float markCountMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref sacredMarkEnabled, "sacredMarkEnabled", true);
            Scribe_Values.Look(ref markCountMultiplier, "markCountMultiplier", 1f);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_SacredGraffitiSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_SacredGraffitiSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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
                ? " changes take effect the next time the game starts"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards"
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

            // Scope audited: both settings are read each time a ritual resolves (SacredGraffiti.cs), so they land now.
            if (Group(list, "Sacred marks from rituals", RimMandrake.Shared.SettingScope.Now, new[] { "sacredMarkEnabled", "markCountMultiplier" }))
            {
                list.CheckboxLabeled("Sacred marks from rituals", ref sacredMarkEnabled,
                    "A favorable ritual outcome can leave a devotional wall-mark behind. "
                  + "Off: the ritual's ordinary reward still happens, just never a mark.");
                list.Label("Mark count: " + markCountMultiplier.ToString("0.00") + "x how many a ritual would place");
                markCountMultiplier = list.Slider(markCountMultiplier, 0.25f, 3f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_SacredGraffitiMod : Mod
    {
        public static RM_SacredGraffitiSettings settings;

        public RM_SacredGraffitiMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_SacredGraffitiSettings>();
        }

        public override string SettingsCategory()
        {
            return "Sacred Graffiti";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
