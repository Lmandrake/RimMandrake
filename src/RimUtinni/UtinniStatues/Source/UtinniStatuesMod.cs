using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.UtinniStatues
{
    // UTINNI_STATUES_SKELETON_BUILD_1 + SHKAAR_FLAME_IDOL_BUILD_1 — Mod Settings, statue_mods_spec.md §1.5
    // (a) carving on/off, (c) Sh'kaar's idol burns, (b) Sumpgas fuels it (row shown only in the campaign).
    public class UtinniStatuesSettings : ModSettings
    {
        public static bool statuesCraftable = true;
        public static bool shkaarIdolBurns = true;
        public static bool sumpgasFuelsIdol = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref statuesCraftable, "statuesCraftable", true);
            Scribe_Values.Look(ref shkaarIdolBurns, "shkaarIdolBurns", true);
            Scribe_Values.Look(ref sumpgasFuelsIdol, "sumpgasFuelsIdol", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(UtinniStatuesSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(UtinniStatuesSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): the carving switch withdraws recipes and the idol fuel is swapped in a StaticConstructorOnStartup, so both are [next game start]; the burning-idol switch is read when a grand statue is dedicated (SetCarving), so [next pulse]. Nothing is read at map or world generation.</summary>
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

            if (Group(list, "Statue carving", RimMandrake.Shared.SettingScope.Now, new[] { "statuesCraftable" }, "[next game start]"))
            {
                list.CheckboxLabeled("Utinni statues can be carved", ref statuesCraftable,
                    "On: the sculptor's table offers the Utinni votive, statue and grand statue; once one is placed, "
                  + "its \"Dedicate\" button chooses which god or votive it honours. Off: the table stops offering "
                  + "them. Statues already made stay. Takes effect after a restart; not worldgen.");
                list.GapLine();
            }

            if (Group(list, "Sh'kaar's burning idol", RimMandrake.Shared.SettingScope.NextPulse, new[] { "shkaarIdolBurns" }))
            {
                list.CheckboxLabeled("Sh'kaar's idol burns", ref shkaarIdolBurns,
                    "On: dedicating a grand statue to Sh'kaar rebuilds it as a burning idol. It needs fuel, glows, and "
                  + "a flame rises from its sun-disc crown. Off: a new grand idol of Sh'kaar stays cold. An idol already "
                  + "burning keeps burning until rededicated.");
                list.GapLine();
            }

            if (Group(list, "Sumpgas fuels the idol", RimMandrake.Shared.SettingScope.Now, new[] { "sumpgasFuelsIdol" }, "[next game start]"))
            {
                if (ModsConfig.IsActive("mandrake.rut.patches"))
                {
                    list.CheckboxLabeled("Sumpgas fuels the idol", ref sumpgasFuelsIdol,
                        "On: the burning idol takes Sumpgas, the campaign's fuel. Off: it takes chemfuel. "
                      + "Takes effect after a restart.");
                }
                else
                {
                    list.Label("Only applies in the campaign (the Utinni patches mod is not loaded).");
                }
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class UtinniStatuesMod : Mod
    {
        public static UtinniStatuesSettings settings;

        public UtinniStatuesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<UtinniStatuesSettings>();
        }

        public override string SettingsCategory()
        {
            return "Utinni Statues";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }

    /// <summary>Applies "Utinni statues can be carved" OFF at startup: the statue recipes leave every
    /// workbench. Nothing else changes, so all-off is a mod that does nothing.</summary>
    [StaticConstructorOnStartup]
    public static class UtinniStatuesStartup
    {
        public static readonly int RecipesWithdrawn;

        static UtinniStatuesStartup()
        {
            ApplyIdolFuel();
            if (UtinniStatuesSettings.statuesCraftable)
            {
                return;
            }
            FieldInfo cache = typeof(ThingDef).GetField("allRecipesCached", BindingFlags.NonPublic | BindingFlags.Instance);
            foreach (RecipeDef r in DefDatabase<RecipeDef>.AllDefsListForReading)
            {
                ThingDef made = r.ProducedThingDef;
                if (made == null || made.GetCompProperties<CompProperties_StatuePicker>() == null)
                {
                    continue;
                }
                List<ThingDef> users = r.recipeUsers;
                if (users != null)
                {
                    foreach (ThingDef u in users)
                    {
                        u.recipes?.Remove(r);
                        cache?.SetValue(u, null);
                    }
                    users.Clear();
                }
                RecipesWithdrawn++;
            }
            Log.Message("[UtinniStatues] carving switched off: " + RecipesWithdrawn + " statue recipe(s) withdrawn.");
        }

        /// <summary>Statue spec §2.3/§1.5(b): in the campaign (mandrake.rut.patches loaded) the burning idol takes
        /// Sumpgas; otherwise, or with the setting off, the chemfuel filter in its XML stands (ruling R4).</summary>
        private static void ApplyIdolFuel()
        {
            ThingDef idol = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_StatueGrand_Shkaar");
            ThingDef sumpgas = DefDatabase<ThingDef>.GetNamedSilentFail("RM_TarGas");
            CompProperties_Refuelable fuel = idol?.GetCompProperties<CompProperties_Refuelable>();
            if (fuel == null || sumpgas == null || !UtinniStatuesSettings.sumpgasFuelsIdol)
            {
                return;
            }
            ThingFilter f = new ThingFilter();
            f.SetAllow(sumpgas, true);
            fuel.fuelFilter = f;
            fuel.fuelLabel = "Sumpgas";
            fuel.fuelGizmoLabel = "Sumpgas";
            fuel.outOfFuelMessage = "Idol of Sh'kaar out of Sumpgas";
        }
    }
}
