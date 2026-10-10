using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.StructureInjections
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for StructureInjections.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // This mod's only live mechanism is GenStep_RimplacePlan.Generate() -
    // it replays a compiled rimplace BuildPlan onto a freshly generated
    // map (foundation/terrain/things/runs/roof/pawns). There is exactly
    // one master switch worth exposing: whether the whole replay runs at
    // all. It is inherently WORLDGEN-AFFECTING (mapgen time only) - there
    // is no live-play tick or patch in this assembly to gate separately.
    // No other tunable number exists in the mechanism: SeedPart is a fixed
    // RNG-stream identifier, not a gameplay magnitude, and every placement
    // coordinate/defName comes from the plan file itself, not a hardcoded
    // constant here.
    // ════════════════════════════════════════════════════════════════════
    public class RM_StructureInjectionsSettings : ModSettings
    {
        public static bool enabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_StructureInjectionsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_StructureInjectionsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

            // Scope audited: read once per map in GenStep_RimplacePlan.Generate (and the Whisper no-op step), i.e. at map generation.
            if (Group(list, "Structure injection templates (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "enabled" }))
            {
                list.CheckboxLabeled("Structure injection templates enabled", ref enabled,
                    "Replays authored building templates (foundation, terrain, machines, roofs, and "
                  + "sometimes a pawn/corpse) onto freshly generated maps that call for one - things "
                  + "like the moisture farm layout. Off: those maps generate with none of the template "
                  + "applied, as if this mod's templates did not exist. Never affects a map that has "
                  + "already been generated.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_StructureInjectionsMod : Mod
    {
        public static RM_StructureInjectionsSettings settings;

        public RM_StructureInjectionsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_StructureInjectionsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Structure Injections";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
