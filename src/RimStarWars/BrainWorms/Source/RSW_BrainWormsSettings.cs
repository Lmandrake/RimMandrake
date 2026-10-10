using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.BrainWorms
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Geonosian Brain Worms.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields read
    // from everywhere, Scribe_Values in ExposeData, a DoWindowContents helper
    // called from the Mod subclass).
    //
    // Gates two of the three runtime infection vectors named in About.xml —
    // the salvaged-cargo incident and the weaponized-egg mortar shell. The
    // third vector (ruin dungeon egg clusters) is loot-table/def placement,
    // not a runtime mechanism this assembly can gate.
    //
    // 🔴 OWNER RULING, PERMANENT, VERBATIM: "Never corpse-walker. Too gross."
    // This file adds NO setting that could let a dead host be puppeted, and
    // does not touch the living-host refusal in CompRSWWormBurrow.IsValidHost
    // or the death guards in HediffComp_BrainWormPuppeteer. Whoever edits this
    // settings screen next: do not add one either.
    //
    // The cold-kill slider deliberately has no zero/off value (floor 0.25x) —
    // per the item spec, an on/off here would strand the intended "escape via
    // cold" design; only the RATE may be tuned, never disabled outright.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_BrainWormsSettings : ModSettings
    {
        public static bool cargoIncidentEnabled = true;
        public static bool eggProjectileEnabled = true;

        // 1.0 = shipped default (severityPerDay 0.14, ~2.5d latent + ~3d influenced).
        public static float progressionSpeedMultiplier = 1f;

        // 1.0 = shipped default (dies after ticksBelowBeforeDeath, ~1 hour below
        // freezing). Never allowed to reach "never dies" — see class comment.
        public static float coldKillRateMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref cargoIncidentEnabled, "cargoIncidentEnabled", true);
            Scribe_Values.Look(ref eggProjectileEnabled, "eggProjectileEnabled", true);
            Scribe_Values.Look(ref progressionSpeedMultiplier, "progressionSpeedMultiplier", 1f);
            Scribe_Values.Look(ref coldKillRateMultiplier, "coldKillRateMultiplier", 1f);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RSW_BrainWormsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RSW_BrainWormsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): the cargo incident is gated in its worker when the storyteller rolls it, so [next pulse]; the egg shell switch is read on impact, the progression multiplier in SeverityChangePerDay and the cold-kill multiplier on each cold scan, so those are [now]. Nothing is read at map or world generation.</summary>
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

            if (Group(list, "Salvaged cargo pod incident", RimMandrake.Shared.SettingScope.NextPulse, new[] { "cargoIncidentEnabled" }))
            {
                list.CheckboxLabeled("Salvaged cargo pod incident", ref cargoIncidentEnabled,
                    "A crashed cargo pod incident can carry a hidden egg cluster. Off: this "
                  + "incident never fires. The ruin dungeon egg clusters (a loot table, not "
                  + "runtime code) are unaffected by any setting here.");
                list.GapLine();
            }

            if (Group(list, "Egg mortar shells", RimMandrake.Shared.SettingScope.Now, new[] { "eggProjectileEnabled" }))
            {
                list.CheckboxLabeled("Weaponized egg mortar shells spawn worms", ref eggProjectileEnabled,
                    "A brain worm egg shell fired from a mortar bursts into loose worms on "
                  + "impact. Off: the shell still exists and can still be loaded and fired - "
                  + "it just lands inert, no worms.");
                list.GapLine();
            }

            if (Group(list, "Infection progression speed", RimMandrake.Shared.SettingScope.Now, new[] { "progressionSpeedMultiplier" }))
            {
                list.Label("Infection progression speed: " + progressionSpeedMultiplier.ToString("0.00") + "x");
                list.Label("Multiplies how fast a latent infection advances toward influenced "
                  + "and then puppeted while the host stays warm. Does not change the cold cure.");
                progressionSpeedMultiplier = list.Slider(progressionSpeedMultiplier, 0.1f, 4f);
                list.GapLine();
            }

            if (Group(list, "Cold-kill rate", RimMandrake.Shared.SettingScope.Now, new[] { "coldKillRateMultiplier" }))
            {
                list.Label("Cold-kill rate (loose worms and eggs): " + coldKillRateMultiplier.ToString("0.00") + "x");
                list.Label("Multiplies how fast a below-freezing worm or egg item dies of cold. "
                  + "Floored above zero by design - cold is the intended way to deal with a "
                  + "loose worm or a carried egg, and this mod will not let that be switched off.");
                coldKillRateMultiplier = list.Slider(coldKillRateMultiplier, 0.25f, 4f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RSW_BrainWormsMod : Mod
    {
        public static RSW_BrainWormsSettings settings;

        public RSW_BrainWormsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_BrainWormsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Geonosian Brain Worms";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
