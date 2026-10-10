using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.Graffiti
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Graffiti.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields
    // read from everywhere, Scribe_Values in ExposeData).
    //
    // Four things this exposes:
    //   1. Painting enabled — master switch for the graffiti-painting joy
    //      activity AND the mental-break painting spree (both funnel
    //      through JoyGiver_PaintGraffiti / JobGiver_GraffitiPaintingSpree,
    //      which simply hand back no job when off — the ThinkTree falls
    //      through to whatever else a pawn would otherwise do, same as any
    //      vanilla JobGiver returning null).
    //   2. Paint interval — how often (in ticks) a painting pawn leaves a
    //      fresh mark while working (JobDriver_PaintGraffiti's hardcoded
    //      250-tick PaintIntervalTicks).
    //   3. Viewer reaction — the mood/thought effect from noticing a mark
    //      nearby (ThoughtWorker_ViewedGraffitiMark).
    //   4. Breach-bias — raiders funneling their breach target toward a
    //      "Come And Take It" taunt mark (BreachBiasHookMod's Harmony
    //      postfix on BreachingGrid.FindBuildingToBreach).
    //
    // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 adds two more:
    //   5. Raid-exit tagging — a departing hostile pawn leaves its gang's
    //      own mark nearby (RaidExitTaggerMod's Harmony prefix on
    //      CaravanExitMapUtility.ExitMapAndCreateCaravan).
    //   6. Scrub protection — own-faction/Devotional marks skip the
    //      ambient home-area auto-clean scan (AutoCleanProtectionMod's
    //      Harmony prefix on WorkGiver_CleanFilth.HasJobOnThing); a
    //      player's explicit right-click "Clean now" always still works.
    // ════════════════════════════════════════════════════════════════════
    public class RM_GraffitiSettings : ModSettings
    {
        public static bool paintingEnabled = true;
        public static int paintIntervalTicks = 250;
        public static bool viewerReactionEnabled = true;
        public static bool breachBiasEnabled = true;
        public static bool raidExitTaggingEnabled = true;
        public static bool autoCleanProtectionEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref paintingEnabled, "paintingEnabled", true);
            Scribe_Values.Look(ref paintIntervalTicks, "paintIntervalTicks", 250);
            Scribe_Values.Look(ref viewerReactionEnabled, "viewerReactionEnabled", true);
            Scribe_Values.Look(ref breachBiasEnabled, "breachBiasEnabled", true);
            Scribe_Values.Look(ref raidExitTaggingEnabled, "raidExitTaggingEnabled", true);
            Scribe_Values.Look(ref autoCleanProtectionEnabled, "autoCleanProtectionEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Painting", RimMandrake.Shared.SettingScope.Now, new[] { "paintingEnabled", "paintIntervalTicks" }))
            {
                list.CheckboxLabeled("Graffiti painting", ref paintingEnabled,
                    "Pawns can paint graffiti marks on walls as a joy activity, and during "
                  + "the painting-spree mental break. Off: no pawn ever paints a mark.");
                list.Label("Paint interval: every " + paintIntervalTicks + " ticks while painting");
                paintIntervalTicks = (int)list.Slider(paintIntervalTicks, 60f, 1000f);
                list.GapLine();
            }

            if (Group(list, "Viewer reactions", RimMandrake.Shared.SettingScope.Now, new[] { "viewerReactionEnabled" }))
            {
                list.CheckboxLabeled("Viewer reactions to marks", ref viewerReactionEnabled,
                    "Pawns get a mood effect from noticing a graffiti mark nearby that reacts to them. "
                  + "Off: marks are purely decorative filth.");
                list.GapLine();
            }

            if (Group(list, "Raiders", RimMandrake.Shared.SettingScope.Now, new[] { "breachBiasEnabled", "raidExitTaggingEnabled" }))
            {
                list.CheckboxLabeled("Raiders lured to taunt marks", ref breachBiasEnabled,
                    "A \"Come And Take It\"-style taunt mark biases raiders to breach toward it. "
                  + "Off: raiders pick a breach target the ordinary (nearest) way.");
                list.CheckboxLabeled("Raiders tag on their way out", ref raidExitTaggingEnabled,
                    "A departing hostile pawn leaves its own gang's mark on a nearby wall. "
                  + "Off: raiders leave no marks when they exit the map.");
                list.GapLine();
            }

            if (Group(list, "Cleaning", RimMandrake.Shared.SettingScope.Now, new[] { "autoCleanProtectionEnabled" }))
            {
                list.CheckboxLabeled("Protect own/devotional marks from auto-clean", ref autoCleanProtectionEnabled,
                    "Your own faction's marks and Devotional marks are skipped by the ambient "
                  + "home-area clean scan. Off: every mark is fair game for ordinary cleaning. "
                  + "A player's explicit right-click \"Clean now\" always still works either way.");
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
            foreach (FieldInfo f in typeof(RM_GraffitiSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_GraffitiSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): every Graffiti setting is read by a job
        /// giver, work giver, job driver tick, thought worker or a Harmony prefix at the moment it fires, none at map generation, so all are [now].</summary>
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

    public class RM_GraffitiMod : Mod
    {
        public static RM_GraffitiSettings settings;

        public RM_GraffitiMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_GraffitiSettings>();
        }

        public override string SettingsCategory()
        {
            return "Graffiti";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
