using System.Reflection;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimMandrake.EnvironmentalHazards;
using UnityEngine;
using Verse;

namespace RimMandrake.Wreckage
{
    // SALVAGE_WRECKAGE_EVERYWHERE_1, design §6: the loot rows (slice 1) and the
    // wreck-field rows (slice 3: master, density, one checkbox per field key) and the
    // fresh-wreck-falls row (step 5, §3e) and the hazards row (the salvager's dose).
    // Defaults = shipped behaviour; all off = vanilla ShipChunk salvage.
    public class RM_WreckageSettings : ModSettings
    {
        public static bool salvageLoot = true;
        public static float lootGenerosity = 1f;      // PROVISIONAL range 0.25-3 (design §6)
        public static bool skillScalesRare = true;
        public static bool wreckFields = true;
        public static float wreckDensity = 1f;        // PROVISIONAL range 0-3 (design §6), new maps only
        // Field keys switched OFF, comma-separated (a plain string so the bridge's settings
        // tool can flip one field without a per-biome bool). Empty = every field on.
        public static string disabledFields = "";
        // Design §6 "Fresh wreck falls": off, no RM_IncidentWorker_WreckFall incident fires.
        public static bool wreckFalls = true;

        // Design §6 "Wreck hazards": off, careful salvage never doses the salvager
        // (RM_CompSalvageLoot.ApplyHazard). The wrecks and their loot remain.
        public static bool wreckHazards = true;

        public static bool SalvageLootActive => salvageLoot;

        public static bool FieldDisabled(string key)
        {
            return RM_WreckageKernel.FieldDisabled(disabledFields, key);
        }

        // A field runs when the master is on, its own key is not switched off here, and the
        // owning biome mod (if it registered a gate under the bare key) has its biome on.
        public static bool FieldActive(string key)
        {
            return wreckFields && !key.NullOrEmpty() && RM_WreckageKernel.FieldActive(true, key, disabledFields, RM_MechanicGates.Enabled(key));
        }

        public static void SetFieldEnabled(string key, bool on)
        {
            disabledFields = RM_WreckageKernel.SetFieldEnabled(disabledFields, key, on);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref salvageLoot, "salvageLoot", true);
            Scribe_Values.Look(ref lootGenerosity, "lootGenerosity", 1f);
            Scribe_Values.Look(ref skillScalesRare, "skillScalesRare", true);
            Scribe_Values.Look(ref wreckFields, "wreckFields", true);
            Scribe_Values.Look(ref wreckDensity, "wreckDensity", 1f);
            Scribe_Values.Look(ref disabledFields, "disabledFields", "");
            Scribe_Values.Look(ref wreckFalls, "wreckFalls", true);
            Scribe_Values.Look(ref wreckHazards, "wreckHazards", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_WreckageSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int) || f.FieldType == typeof(string))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_WreckageSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

        // One switch per wreck-field key (the keys come from the GenStepDefs, so the list is dynamic). Kept out of the
        // group block so the block lists only Scribed names.
        private static void DrawFieldToggles(Listing_Standard list)
        {
            foreach (string key in RM_GenStep_WreckField.AllFields().Select(f => f.settingsKey)
                         .Where(k => !k.NullOrEmpty()).Distinct().OrderBy(k => k))
            {
                bool on = !FieldDisabled(key);
                bool was = on;
                list.CheckboxLabeled("RM_Wreckage_Setting_Field".Translate(key), ref on,
                    "RM_Wreckage_Setting_Field_Tip".Translate(key));
                if (on != was)
                {
                    SetFieldEnabled(key, on);
                }
            }
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

            // Scopes audited per read site: loot, generosity, skill scaling and hazards are read each time a wreck is salvaged (now);
            // fields, density and the per-field switches are read by the wreck-field GenStep while a map generates; the fresh-wreck
            // incident gate is read whenever that incident is rolled.
            if (Group(list, "Salvage loot", RimMandrake.Shared.SettingScope.Now, new[] { "salvageLoot", "lootGenerosity", "skillScalesRare" }))
            {
                list.CheckboxLabeled("RM_Wreckage_Setting_SalvageLoot".Translate(), ref salvageLoot,
                    "RM_Wreckage_Setting_SalvageLoot_Tip".Translate());
                list.Label("RM_Wreckage_Setting_Generosity".Translate(lootGenerosity.ToStringPercent()));
                lootGenerosity = Mathf.Round(list.Slider(lootGenerosity, 0.25f, 3f) * 20f) / 20f;
                list.CheckboxLabeled("RM_Wreckage_Setting_SkillScales".Translate(), ref skillScalesRare,
                    "RM_Wreckage_Setting_SkillScales_Tip".Translate());
                list.GapLine();
            }

            if (Group(list, "Wreck fields (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "wreckFields", "wreckDensity", "disabledFields" }))
            {
                list.CheckboxLabeled("RM_Wreckage_Setting_WreckFields".Translate(), ref wreckFields,
                    "RM_Wreckage_Setting_WreckFields_Tip".Translate());
                list.Label("RM_Wreckage_Setting_Density".Translate(wreckDensity.ToStringPercent()));
                wreckDensity = Mathf.Round(list.Slider(wreckDensity, 0f, 3f) * 20f) / 20f;
                DrawFieldToggles(list);
                list.GapLine();
            }

            if (Group(list, "Fresh wreck falls", RimMandrake.Shared.SettingScope.NextPulse, new[] { "wreckFalls" }))
            {
                list.CheckboxLabeled("RM_Wreckage_Setting_WreckFalls".Translate(), ref wreckFalls,
                    "RM_Wreckage_Setting_WreckFalls_Tip".Translate());
                list.GapLine();
            }

            if (Group(list, "Wreck hazards", RimMandrake.Shared.SettingScope.Now, new[] { "wreckHazards" }))
            {
                list.CheckboxLabeled("RM_Wreckage_Setting_Hazards".Translate(), ref wreckHazards,
                    "RM_Wreckage_Setting_Hazards_Tip".Translate());
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_WreckageMod : Mod
    {
        public static RM_WreckageSettings settings;

        public RM_WreckageMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WreckageSettings>();
            // Composed beside EnvironmentalHazards in mandrake.rm.biomes, so
            // the shared gate registry is always co-present (the same reasoning
            // as RM_TerminalBiomesMod's unconditional registration).
            RegisterMechanicGates();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.wreckage"), typeof(RM_WreckageMod).Assembly, "RimMandrake.Wreckage");
        }

        [MethodImpl(MethodImplOptions.NoInlining)]
        private static void RegisterMechanicGates()
        {
            RM_MechanicGates.Register("Wreckage.loot", () => RM_WreckageSettings.salvageLoot);
            RM_MechanicGates.Register("Wreckage.skillScalesRare", () => RM_WreckageSettings.skillScalesRare);
            RM_MechanicGates.Register("Wreckage.fields", () => RM_WreckageSettings.wreckFields);
            RM_MechanicGates.Register("Wreckage.falls", () => RM_WreckageSettings.wreckFalls);
            RM_MechanicGates.Register("Wreckage.hazards", () => RM_WreckageSettings.wreckHazards);
            // Per-field keys and their aliases (Scald.S6) need the GenStepDefs:
            // RM_WreckFieldStartup registers them after def load.
        }

        public override string SettingsCategory()
        {
            return "RM_Wreckage_SettingsCategory".Translate();
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
