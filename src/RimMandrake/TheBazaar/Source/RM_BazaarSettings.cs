using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.Bazaar
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 / "every mod ships Mod Settings". The rule this
    // file follows: a toggle lands in the same slice as the mechanic it
    // gates, never ahead of it. BAZAAR_PRICE_ENGINE_1 (slice 2) adds the
    // economy and intel toggles below because their mechanics now exist
    // (RM_BazaarEconomy, the GetPriceFor postfix, the intel gates). Haggle,
    // crit spoils, banter, broker tab, wishlist flash and grid density
    // (design §7) still arrive with their own slices.
    //
    // Defaults = shipped behaviour. All economy/intel off = vanilla prices
    // and a plain grid.
    // ════════════════════════════════════════════════════════════════════
    public class RM_BazaarSettings : ModSettings
    {
        /// <summary>Master switch for the settlement price economy. Off =
        /// flat ×1.0 everywhere: the GetPriceFor postfix returns at its
        /// first check, and intel columns read "no data".</summary>
        public static bool economyEnabled = true;

        /// <summary>Seed settlements that no authored rule touches from a
        /// stable hash of (faction, biome, tile) — mild locality on public
        /// worlds with no authored tags (owner-ruled, design §3). Authored
        /// rules always win over it on the keys they set.</summary>
        public static bool proceduralLocality = true;

        /// <summary>Intel L1 — price vs typical (Social 3+).</summary>
        public static bool intelPriceContext = true;

        /// <summary>Intel L2 — good-deal outlier badges (Social 5+).</summary>
        public static bool intelGoodDeals = true;

        /// <summary>Intel L3 — local economy (Social 7+).</summary>
        public static bool intelLocalEconomy = true;

        /// <summary>Intel L4 — scarcity from the trader-visit log (Social 9+).</summary>
        public static bool intelScarcity = true;

        /// <summary>Protocol-droid modules (D1..D4) unlock their layers. Off
        /// = modules are inert items; Social layers are unaffected.</summary>
        public static bool intelModules = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref economyEnabled, "economyEnabled", true);
            Scribe_Values.Look(ref proceduralLocality, "proceduralLocality", true);
            Scribe_Values.Look(ref intelPriceContext, "intelPriceContext", true);
            Scribe_Values.Look(ref intelGoodDeals, "intelGoodDeals", true);
            Scribe_Values.Look(ref intelLocalEconomy, "intelLocalEconomy", true);
            Scribe_Values.Look(ref intelScarcity, "intelScarcity", true);
            Scribe_Values.Look(ref intelModules, "intelModules", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_BazaarSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_BazaarSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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
                ? " changes take effect the next time the game starts or a save loads"
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

            // Scopes audited per read site. Every setting is read live (the GetPriceFor postfix, the world-component drift tick, the
            // intel gates on window open), none at map or world generation. BUT RM_BazaarSession.Current is only set by
            // RM_Window_Bazaar, which nothing opens yet (no WindowStack.Add intercept), so the price postfix and the intel gates
            // never run in play: all seven settings are dead until BAZAAR_WINDOW_GRID_1 wires the window.
            if (Group(list, "Price economy (not wired yet: changes nothing in play)", RimMandrake.Shared.SettingScope.Now, new[] { "economyEnabled" }))
            {
                list.Label("The Bazaar trade window is not opened by anything yet, so the price postfix never runs and this has no visible effect until it is wired.");
                list.CheckboxLabeled("Dynamic settlement prices", ref economyEnabled,
                    "Each settlement prices goods by what it has and lacks (a desert town pays more for water), "
                    + "drifting day to day within x0.25-x4.0. Applies ONLY inside The Bazaar's trade window; "
                    + "colony wealth, raid points and caravan values are never touched. Off = vanilla prices.");
                list.GapLine();
            }

            if (Group(list, "Locality of untagged settlements (not wired yet)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "proceduralLocality" }))
            {
                list.Label("Same as above: nothing reads the prices in play yet.");
                list.CheckboxLabeled("Procedural locality for untagged settlements", ref proceduralLocality,
                    "Settlements no authored rule describes get a mild, stable local price character from their "
                    + "faction, biome and tile. Off = those settlements trade at x1.0. Takes effect for settlements "
                    + "first seen after the change.");
                list.GapLine();
            }

            if (Group(list, "Trade intel by Social skill (not wired yet)", RimMandrake.Shared.SettingScope.Now, new[] { "intelPriceContext", "intelGoodDeals", "intelLocalEconomy", "intelScarcity" }))
            {
                list.Label("Intel is evaluated per open Bazaar window; there is none yet, so these have no visible effect.");
                list.CheckboxLabeled("L1 price context (Social 3+)", ref intelPriceContext,
                    "Shows each good's price against what is typical here.");
                list.CheckboxLabeled("L2 good-deal badges (Social 5+)", ref intelGoodDeals,
                    "Flags prices far from typical, in either direction.");
                list.CheckboxLabeled("L3 local economy (Social 7+)", ref intelLocalEconomy,
                    "Shows what this settlement pays relative to the norm.");
                list.CheckboxLabeled("L4 scarcity (Social 9+)", ref intelScarcity,
                    "Flags goods only this trader has carried recently.");
                list.GapLine();
            }

            if (Group(list, "Protocol-droid intel modules (not wired yet)", RimMandrake.Shared.SettingScope.Now, new[] { "intelModules" }))
            {
                list.CheckboxLabeled("Protocol-droid intel modules", ref intelModules,
                    "Modules fitted to a functional protocol droid in the party (or at a comms console) unlock "
                    + "deeper intel. Off = modules do nothing.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_BazaarMod : Mod
    {
        public static RM_BazaarSettings settings;

        public RM_BazaarMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_BazaarSettings>();
        }

        public override string SettingsCategory() => "The Bazaar";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
