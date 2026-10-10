using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.WeepingStones
{
    // ════════════════════════════════════════════════════════════════════
    // STOCKED_POOL_BUILD_1 — Mod Settings.
    // Precedent: src/RimMandrake/DivingInteraction/Source/RM_DivingSettings.cs.
    //
    // MOD_OPTIONS_RETROFIT_1 doctrine (CLAUDE.md "Every mod ships superb Mod
    // Settings"): defaults = shipped behavior, all-off degrades gracefully.
    // Wave 4 (STOCKED_POOL_BUILD_1) lands HARVEST, CULL, the vhorrin
    // emergence trigger and the vizhik escape event — the husbandry loop
    // (STOCK/FEED/HARVEST/OVERDRAW/CULL/RECAPTURE) is now playable end to
    // end, so the default flips to true per this file's own prior note.
    // ════════════════════════════════════════════════════════════════════
    public class RM_WeepingStonesSettings : ModSettings
    {
        public static bool stockedPoolsEnabled = true;

        // Multiplier on both vhorrin emergence chances (crowded 0.02, crashed 0.01 per pulse). 0-3.
        public static float vhorrinOddsMultiplier = 1f;

        // Per-pulse chance that a stocked vizhik escapes its pen. Shipped 0.05. 0-0.25.
        public static float vizhikEscapeChance = 0.05f;

        // WEEPINGSTONES_WALKING_CONDENSER_1: master switch and season length (days) for the walking condenser.
        public static bool condenserEnabled = true;
        public static float condenserSeasonDays = 15f;

        // WEEPINGSTONES_CONDENSER_QUESTS_1: the two optional condenser quests (capture for a collector / keep it free). Read live at offer time.
        public static bool condenserQuestsEnabled = true;

        // WEEPINGSTONES_DEWSILK_COCOON_1: tamed mirrik leave dewsilk cocoons. Read once at startup.
        public static bool dewsilkEnabled = true;

        // WEEPINGSTONES_OASIS_MUTATOR_FLORA_1: our oases grow the biome's own blade flora instead of Earth palms/grasses. Read live.
        public static bool oasisNativeFloraEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref stockedPoolsEnabled, "stockedPoolsEnabled", true);
            Scribe_Values.Look(ref vhorrinOddsMultiplier, "vhorrinOddsMultiplier", 1f);
            Scribe_Values.Look(ref vizhikEscapeChance, "vizhikEscapeChance", 0.05f);
            Scribe_Values.Look(ref condenserEnabled, "condenserEnabled", true);
            Scribe_Values.Look(ref condenserSeasonDays, "condenserSeasonDays", 15f);
            Scribe_Values.Look(ref condenserQuestsEnabled, "condenserQuestsEnabled", true);
            Scribe_Values.Look(ref dewsilkEnabled, "dewsilkEnabled", true);
            Scribe_Values.Look(ref oasisNativeFloraEnabled, "oasisNativeFloraEnabled", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_WeepingStonesSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_WeepingStonesSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): the pool-pen jobs, designator, work givers and the walking condenser's tick read their switches every time they run, so those are [now]; the vhorrin and vizhik chances, the condenser season length and the quest offer are read on the pool pulse, at the crab's next move and at quest offer time, so [next pulse]; dewsilk is read once at startup so [next game start]; the oasis flora is read by the tile mutator when a map is generated so [new maps only] and labelled worldgen-affecting.</summary>
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

            if (Group(list, "Stocked pools", RimMandrake.Shared.SettingScope.Now, new[] { "stockedPoolsEnabled" }))
            {
                list.CheckboxLabeled("Stocked pools enabled", ref stockedPoolsEnabled,
                    "Master switch for the Weeping Stones' stocked-pool husbandry kit - the "
                  + "nasty, over-active fish and alien-beast catches, pen zones, and the mood "
                  + "economy around eating them. Gates the pool-pen zone designator, its "
                  + "per-pool bookkeeping, and the STOCK/FEED/HARVEST/CULL jobs. On by default: "
                  + "the full loop is built. Wild fishing (the ruled gentle six) and the "
                  + "bestiary/cuisine content itself are never affected by this setting.");
                list.GapLine();
            }

            if (Group(list, "Vhorrin and vizhik odds", RimMandrake.Shared.SettingScope.NextPulse, new[] { "vhorrinOddsMultiplier", "vizhikEscapeChance" }))
            {
                list.Label("Vhorrin odds: " + vhorrinOddsMultiplier.ToString("0.00") + "x (shipped 1.00x)",
                    -1f, (TipSignal?)("How likely a crowded or crashed pool is to breed a vhorrin. At 0 an "
                       + "overcrowded or starved pen never produces one; at 3 it is three times as "
                       + "likely each pulse. A pen is checked about every 2500 ticks."));
                vhorrinOddsMultiplier = Mathf.Round(list.Slider(vhorrinOddsMultiplier, 0f, 3f) * 20f) / 20f;

                list.Label("Vizhik escape chance: " + vizhikEscapeChance.ToString("0.000")
                           + " per pulse (shipped 0.050)",
                    -1f, (TipSignal?)("Chance each pulse that one stocked vizhik slips its pen and goes wild. "
                       + "At 0 nothing ever escapes; at 0.25 a pen leaks constantly."));
                vizhikEscapeChance = Mathf.Round(list.Slider(vizhikEscapeChance, 0f, 0.25f) * 200f) / 200f;
                list.GapLine();
            }

            if (Group(list, "Walking condenser", RimMandrake.Shared.SettingScope.Now, new[] { "condenserEnabled" }))
            {
                list.CheckboxLabeled("Walking condenser enabled", ref condenserEnabled,
                    "The oldest gorrask, a unique stone-crab carrying a running condenser. While it is settled a "
                  + "pool and the water truce form round it; it moves on each season. Off: it spawns nowhere, and any "
                  + "pool it already made dries back.");
                list.GapLine();
            }

            if (Group(list, "Condenser season length", RimMandrake.Shared.SettingScope.NextPulse, new[] { "condenserSeasonDays" }))
            {
                list.Label("Condenser season: " + condenserSeasonDays.ToString("0") + " days (shipped 15)",
                    -1f, (TipSignal?)("How long the gorrask stays settled before it moves on. 15 is one vanilla quadrum."));
                condenserSeasonDays = Mathf.Round(list.Slider(condenserSeasonDays, 3f, 30f));
                list.GapLine();
            }

            if (Group(list, "Condenser quests", RimMandrake.Shared.SettingScope.NextPulse, new[] { "condenserQuestsEnabled" }))
            {
                list.CheckboxLabeled("Condenser quests offered", ref condenserQuestsEnabled,
                    "Two optional quests about the old gorrask: a wealthy collector pays to have it subdued and taken away alive "
                  + "(the moving oasis ends), or settlers ask you to keep it alive through a season while trophy hunters come for it. "
                  + "Taking one withdraws the other. Off: neither is offered; quests already running finish normally.");
                list.GapLine();
            }

            if (Group(list, "Dewsilk cocoons", RimMandrake.Shared.SettingScope.Now, new[] { "dewsilkEnabled" }, "[next game start]"))
            {
                list.CheckboxLabeled("Dewsilk cocoons enabled (applies next launch)", ref dewsilkEnabled,
                    "Tamed mirrik leave dewsilk cocoons that colonists gather like wool and spin into dewsilk cloth at a tailor bench. "
                  + "Off: mirrik yield nothing. Read once when the game starts, so a change needs a restart.");
                list.GapLine();
            }

            if (Group(list, "Native oasis flora (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "oasisNativeFloraEnabled" }))
            {
                list.CheckboxLabeled("Native oasis flora", ref oasisNativeFloraEnabled,
                    "On a Weeping Stones oasis, the oasis mutator grows the biome's own blade flora (dewblade, bladderquill, steamfrond, dripfringe) "
                  + "instead of Earth palms and grasses. Vanilla desert oases are never affected. Off: our oases grow vanilla palms and grass. "
                  + "Takes effect for maps generated afterwards.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_WeepingStonesMod : Mod
    {
        public static RM_WeepingStonesSettings settings;

        public RM_WeepingStonesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WeepingStonesSettings>();
        }

        public override string SettingsCategory()
        {
            return "Weeping Stones: Stocked Pool";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
