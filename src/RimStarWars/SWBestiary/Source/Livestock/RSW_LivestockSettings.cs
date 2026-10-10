using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Livestock
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for the SWBestiary Livestock
    // assembly (RimMandrakeLivestockRSW.dll).
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs.
    //
    // Ships inside the SWBestiary mod folder but as its own, unmerged DLL —
    // see RSW_JawaIkeeSettings.cs's header for why this is a second
    // settings entry rather than one shared with Ikee.
    //
    // Two runtime mechanics live here (the light-aversion comp moved to the Abyss mod with
    // the skarnix, ABYSS_INVENTED_CREATURES_TO_RM_1):
    //   1. CompKilnBelly — Onnik's feed-cycle kiln (3 spaced doses -> good
    //      batch; rushed dump -> cracked batch; underfed -> kiln cools).
    //      The dose counts/windows are per-def CompProperties (a species
    //      design call, left in XML); the one number worth a global slider
    //      is the reheat/cooldown length between batches.
    //   2. CompMoornakGrief — moornak's self-tame / hidden grief-ledger /
    //      colony-wide unsettled hediff / 30-day manhunter-release timer
    //      (LIVESTOCK_STARTER_TRIO_1, 2026-09-19). Per-def numbers (self-
    //      tame MTB, grief charge, release delay) stay in XML; only the
    //      master on/off and the release-timer multiplier are global
    //      sliders, since a player wants a coarse "is this hazard active"
    //      knob without spoiling the hidden mechanism's exact numbers.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_LivestockSettings : ModSettings
    {
        public static bool kilnBellyEnabled = true;
        public static float kilnCooldownMultiplier = 1f;

        public static bool moornakGriefEnabled = true;
        public static float moornakReleaseDelayMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref kilnBellyEnabled, "kilnBellyEnabled", true);
            Scribe_Values.Look(ref kilnCooldownMultiplier, "kilnCooldownMultiplier", 1f);
            Scribe_Values.Look(ref moornakGriefEnabled, "moornakGriefEnabled", true);
            Scribe_Values.Look(ref moornakReleaseDelayMultiplier, "moornakReleaseDelayMultiplier", 1f);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RSW_LivestockSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RSW_LivestockSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): the kiln and grief switches are read by the comps' tick and dose handlers each time they run, so [now]; the kiln cooldown multiplier is read when a batch fires and the moornak release delay when the next release is scheduled, so [next pulse]. Nothing is read at map or world generation.</summary>
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

            if (Group(list, "Kiln-belly feed cycle (Onnik)", RimMandrake.Shared.SettingScope.Now, new[] { "kilnBellyEnabled" }))
            {
                list.CheckboxLabeled("Kiln-belly enabled", ref kilnBellyEnabled,
                    "Feeding kiln clay in three spaced doses fires a batch of ceramicware; a rushed "
                  + "dump fires a worthless cracked batch; going too long between doses cools the "
                  + "kiln and loses progress. Off: feeding does nothing special - no batches, no "
                  + "lost progress, no errors.");
                list.GapLine();
            }

            if (Group(list, "Kiln batch cooldown", RimMandrake.Shared.SettingScope.NextPulse, new[] { "kilnCooldownMultiplier" }))
            {
                list.Label("Batch cooldown: " + kilnCooldownMultiplier.ToString("0.00")
                    + "x (default is 4 in-game days between batches)");
                kilnCooldownMultiplier = list.Slider(kilnCooldownMultiplier, 0.25f, 3f);
                list.GapLine();
            }

            if (Group(list, "Moornak grief hazard", RimMandrake.Shared.SettingScope.Now, new[] { "moornakGriefEnabled" }))
            {
                list.CheckboxLabeled("Moornak grief hazard enabled", ref moornakGriefEnabled,
                    "A moornak can self-tame onto the colony, unsettles everyone while it is present, "
                  + "and periodically releases what it has absorbed. Off: it behaves as an ordinary, "
                  + "harmless animal - no self-taming, no mood effect, no release.");
                list.GapLine();
            }

            if (Group(list, "Moornak release timer", RimMandrake.Shared.SettingScope.NextPulse, new[] { "moornakReleaseDelayMultiplier" }))
            {
                list.Label("Release timer: " + moornakReleaseDelayMultiplier.ToString("0.00")
                    + "x (default is 30 in-game days between releases)");
                moornakReleaseDelayMultiplier = list.Slider(moornakReleaseDelayMultiplier, 0.25f, 3f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RSW_LivestockMod : Mod
    {
        public static RSW_LivestockSettings settings;

        public RSW_LivestockMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_LivestockSettings>();
        }

        public override string SettingsCategory()
        {
            return "SW Bestiary: Livestock";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
