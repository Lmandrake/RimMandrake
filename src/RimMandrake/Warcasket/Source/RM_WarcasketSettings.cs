using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.Warcasket
{
    // WARCASKET_SUIT_CLASS_1. MOD_OPTIONS_RETROFIT_1 doctrine: every
    // mechanic toggles independently, defaults = shipped behavior, off
    // degrades gracefully and never strands or harms anyone.
    public class RM_WarcasketSettings : ModSettings
    {
        public static bool masterEnabled = true;

        // The compound-failure mechanic (RM_CompWarcasketIntegrity). Off:
        // the suit still carries all its stats, it simply never fails.
        public static bool compoundFailureEnabled = true;

        // The general terrain-immersion hazard (RM_MapComponent_
        // HazardousTerrainImmersion). Off: deep/non-walkable water is
        // ordinary (if impassable-feeling) terrain again for everyone —
        // no RM_TerrainImmersionHazard is ever applied, and any already on
        // a saved map simply stops accruing/decays as normal.
        public static bool terrainImmersionEnabled = true;

        // WARCASKET_CASK_BAY_AND_SARCOPHAGI_1 (RM_Sarcophagus.cs). Off: a dead
        // wearer's sarcophagus suit is never sealed and no crack-open option
        // is offered; the suit strips like any apparel.
        public static bool sarcophagiEnabled = true;

        // RM_CompCaskShielding (RM_CaskBay.cs). Off: the cask bay is ordinary
        // cask-only storage; stored wastepacks dissolve and cores dose as
        // they would anywhere.
        public static bool caskBayShieldingEnabled = true;

        // RM_CompCoreDose. Off: a half-extracted core is inert cargo.
        public static bool coreDoseEnabled = true;

        // RM_GenStep_SealedCorpses (WARCASKET_JUNKER_KINDS_BUILD_1). Off: no sealed Junker corpses are
        // scattered at map generation; already-placed ones stay.
        public static bool sealedCorpseScatterEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref compoundFailureEnabled, "compoundFailureEnabled", true);
            Scribe_Values.Look(ref terrainImmersionEnabled, "terrainImmersionEnabled", true);
            Scribe_Values.Look(ref sarcophagiEnabled, "sarcophagiEnabled", true);
            Scribe_Values.Look(ref caskBayShieldingEnabled, "caskBayShieldingEnabled", true);
            Scribe_Values.Look(ref coreDoseEnabled, "coreDoseEnabled", true);
            Scribe_Values.Look(ref sealedCorpseScatterEnabled, "sealedCorpseScatterEnabled", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_WarcasketSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_WarcasketSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1200f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): every toggle is read live by a comp, a map
        /// component or the sarcophagus hooks ([now]) except the sealed-corpse scatter, which only a map-generation GenStep reads.</summary>
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
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards" : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Warcasket master switch", RimMandrake.Shared.SettingScope.Now, new[] { "masterEnabled" }))
            {
                list.CheckboxLabeled("Warcasket mechanics enabled", ref masterEnabled,
                    "Master switch. Off: warcaskets keep their base apparel stats (armor, insulation, "
                  + "vacuum/toxin resistance) but none of this mod's mechanics run at all (every toggle below is ignored as off).");
                list.GapLine();
            }

            if (Group(list, "Suit failure and hazardous water", RimMandrake.Shared.SettingScope.Now, new[] { "compoundFailureEnabled", "terrainImmersionEnabled" }))
            {
                list.CheckboxLabeled("Compound-failure rolls", ref compoundFailureEnabled,
                    "Shipped default: ON. Once two or more hazard classes (vacuum, extreme temperature, "
                  + "toxic terrain) are active against a warcasket's wearer at once, the suit can fail: "
                  + "its own HP takes damage and the wearer takes a tendable warcasket-breach injury. A "
                  + "single hazard alone never triggers this. Off: the suit's stat coverage is unchanged, "
                  + "it simply never fails.");
                list.CheckboxLabeled("Hazardous water/brine terrain", ref terrainImmersionEnabled,
                    "Shipped default: ON. Standing in deep or brine water too deep to walk through — not "
                  + "an ordinary ford or shallow margin, which is always safe — is dangerous without "
                  + "enough hazardous-terrain protection from worn apparel (a warcasket, or anything else "
                  + "carrying that stat). This is TERRAIN survival only: it never grants access to a sea "
                  + "floor, which stays reachable only through a gravship. Off: deep water is ordinary "
                  + "terrain again for everyone; nothing already accrued is affected beyond continuing to "
                  + "decay normally.");
                list.GapLine();
            }

            if (Group(list, "Sarcophagi", RimMandrake.Shared.SettingScope.Now, new[] { "sarcophagiEnabled" }))
            {
                list.CheckboxLabeled("Warcasket sarcophagi", ref sarcophagiEnabled,
                    "Shipped default: ON. A sarcophagus-variant warcasket (the adjusted warcasket) seals "
                  + "onto its wearer at death: ordinary stripping leaves it on the body, and a colonist "
                  + "must crack it open (right-click the corpse) to recover the suit, its welded tools "
                  + "and the half-extracted core. Off: the suit strips like any apparel and no salvage "
                  + "is added. Also required for the sealed-corpse scatter below.");
                list.GapLine();
            }

            if (Group(list, "Cask bay and core dose", RimMandrake.Shared.SettingScope.Now, new[] { "caskBayShieldingEnabled", "coreDoseEnabled" }))
            {
                list.CheckboxLabeled("Cask bay shielding", ref caskBayShieldingEnabled,
                    "Shipped default: ON. The lead-lined cask bay (a gravship hardpoint) stops stored "
                  + "toxic wastepacks from dissolving and stored half-extracted cores from dosing anyone. "
                  + "Off: the bay is ordinary cask-only storage.");
                list.CheckboxLabeled("Half-extracted core dose", ref coreDoseEnabled,
                    "Shipped default: ON. A loose half-extracted core doses nearby pawns with toxic "
                  + "buildup (toxic resistance and a warcasket's toxin rating both apply). Off: the "
                  + "core is inert cargo.");
                list.GapLine();
            }

            if (Group(list, "Sealed corpses on new maps (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "sealedCorpseScatterEnabled" }))
            {
                list.CheckboxLabeled("Sealed-corpse scatter", ref sealedCorpseScatterEnabled,
                    "Shipped default: ON. New maps (where a biome asks for it) scatter dead Junkers sealed in "
                  + "their adjusted warcaskets, ready to crack open. Off: none are placed; existing ones stay.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_WarcasketMod : Mod
    {
        public static RM_WarcasketSettings settings;

        public RM_WarcasketMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WarcasketSettings>();
        }

        public override string SettingsCategory()
        {
            return "Warcasket";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
