using System.Reflection;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Inhabited
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Inhabited.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // Two live-play mechanics this exposes:
    //   1. InhabitedFateWorker — a visited inhabited place can end up
    //      Looted/Abandoned/Robbed/Harmed etc. depending on what happened
    //      while the player was there (fire, hostility, casualties, stock
    //      gone missing). Master toggle plus the "robbed" threshold.
    //   2. Patch_QuestGen_Pawns_GeneratePawn (Patch_BeggarsFromPool) —
    //      substitutes displaced-pool people (survivors of places the
    //      player wrecked) for the game's randomly generated Beggars quest
    //      pawns. Master toggle only; there is no tunable number here.
    //
    // NOT exposed: the GenSteps that place a cast/stock on a map
    // (GenStep_InhabitedCast/GenStep_InhabitedStock) — those only act when
    // a WorldObject_Inhabited already sits on the tile (itself authored,
    // not mod-settings territory), and short-circuiting them risks leaving
    // that world object's castInstantiated/roster bookkeeping in a state
    // nothing else expects. Per this item's own "safest coarse gate" rule,
    // better to leave map population alone than guess at that risk.
    // ════════════════════════════════════════════════════════════════════
    public class RM_InhabitedSettings : ModSettings
    {
        public static bool fateEnabled = true;
        public static float robbedFraction = 0.5f;
        public static bool beggarsFromPoolEnabled = true;

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref fateEnabled, "fateEnabled", true);
            Scribe_Values.Look(ref robbedFraction, "robbedFraction", 0.5f);
            Scribe_Values.Look(ref beggarsFromPoolEnabled, "beggarsFromPoolEnabled", true);
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            RimMandrake.Shared.PatchApplier.DrawNotice(list);

            if (Group(list, "Visited places can break", RimMandrake.Shared.SettingScope.Now, new[] { "fateEnabled" }))
            {
                list.CheckboxLabeled("Visited places can break", ref fateEnabled,
                    "An inhabited place you visit can end up looted, abandoned, robbed or harmed "
                  + "depending on what happens there while you're on the map (fire, hostility, "
                  + "casualties, missing stock). Off: a visited place is never marked broken.");
                list.GapLine();
            }

            if (Group(list, "Robbed threshold", RimMandrake.Shared.SettingScope.NextPulse, new[] { "robbedFraction" }))
            {
                list.Label("Stock missing threshold: " + (robbedFraction * 100f).ToString("0") + "%");
                list.Label("If less than this share of a place's stock is still lying around when you leave, it counts as robbed.");
                robbedFraction = list.Slider(robbedFraction, 0.1f, 0.9f);
                list.GapLine();
            }

            if (Group(list, "Beggars from displaced people", RimMandrake.Shared.SettingScope.NextPulse, new[] { "beggarsFromPoolEnabled" }))
            {
                list.CheckboxLabeled("Beggars can be displaced people", ref beggarsFromPoolEnabled,
                    "The strangers who show up begging at your gate can be people from a place you "
                  + "wrecked earlier, recognisable by name. Off: beggars are always ordinary, "
                  + "freshly generated strangers.");
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
            foreach (FieldInfo f in typeof(RM_InhabitedSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_InhabitedSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }
    }

    public class RM_InhabitedMod : Mod
    {
        public static RM_InhabitedSettings settings;

        public RM_InhabitedMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_InhabitedSettings>();
        }

        public override string SettingsCategory()
        {
            return "Inhabited";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
