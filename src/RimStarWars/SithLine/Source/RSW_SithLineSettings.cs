using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.SithLine
{
    /// <summary>
    /// SANGUOPHAGE_KEPT_UNREACHABLE_1 — Mod Settings (design §5; owner 2026-09-12: every mod ships superb settings).
    /// Defaults are the shipped behaviour. All-off degrades to "vanilla sanguophage", never to a broken state.
    /// Nothing here affects worldgen.
    /// </summary>
    public class RSW_SithLineSettings : ModSettings
    {
        // --- applied while the defs load (next game start) ---
        public static bool reskinText = true;
        public static bool vanillaQuestsOff = true;
        public static bool sithBuildingsUnbuildable = true;

        // --- runtime ---
        public static bool neverRecruitable = true;
        public static bool blockXenogermAbsorb = true;
        public static bool inquisitorRaids = true;
        public static float inquisitorRaidChance = RSW_SithLineKernel.DefaultRaidChance;
        public static float inquisitorRaidMinPoints = RSW_SithLineKernel.DefaultRaidMinPoints;
        public static bool inquisitorDefenders = true;
        public static float inquisitorDefenderChance = RSW_SithLineKernel.DefaultDefenderChance;
        public static bool lairRumours = true;
        public static float lairRumourWeight = RSW_SithLineKernel.DefaultRumourWeight;
        public static float lairRefireDays = RSW_SithLineKernel.DefaultRefireDays;
        public static int lairSearchRadius = RSW_SithLineKernel.DefaultSearchRadius;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref reskinText, "reskinText", true);
            Scribe_Values.Look(ref vanillaQuestsOff, "vanillaQuestsOff", true);
            Scribe_Values.Look(ref sithBuildingsUnbuildable, "sithBuildingsUnbuildable", true);
            Scribe_Values.Look(ref neverRecruitable, "neverRecruitable", true);
            Scribe_Values.Look(ref blockXenogermAbsorb, "blockXenogermAbsorb", true);
            Scribe_Values.Look(ref inquisitorRaids, "inquisitorRaids", true);
            Scribe_Values.Look(ref inquisitorRaidChance, "inquisitorRaidChance", RSW_SithLineKernel.DefaultRaidChance);
            Scribe_Values.Look(ref inquisitorRaidMinPoints, "inquisitorRaidMinPoints", RSW_SithLineKernel.DefaultRaidMinPoints);
            Scribe_Values.Look(ref inquisitorDefenders, "inquisitorDefenders", true);
            Scribe_Values.Look(ref inquisitorDefenderChance, "inquisitorDefenderChance", RSW_SithLineKernel.DefaultDefenderChance);
            Scribe_Values.Look(ref lairRumours, "lairRumours", true);
            Scribe_Values.Look(ref lairRumourWeight, "lairRumourWeight", RSW_SithLineKernel.DefaultRumourWeight);
            Scribe_Values.Look(ref lairRefireDays, "lairRefireDays", RSW_SithLineKernel.DefaultRefireDays);
            Scribe_Values.Look(ref lairSearchRadius, "lairSearchRadius", RSW_SithLineKernel.DefaultSearchRadius);
        }

        // Shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RSW_SithLineSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RSW_SithLineSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 900f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

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
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Sith reskin and closed routes", RimMandrake.Shared.SettingScope.Now, new[] { "reskinText", "vanillaQuestsOff", "sithBuildingsUnbuildable" }, "[next game start]"))
            {
                list.CheckboxLabeled("Sith names and text (restart)", ref reskinText,
                    "Shipped default: ON. The sanguophage, its faction, its genes, abilities and buildings read as the Sith adept line "
                  + "(Force drain, dark trance, Sith sarcophagus). Off: vanilla names. Shared machinery the Anzati also use "
                  + "(the deathrest need, hemogen packs, thoughts) keeps its vanilla name either way. Applied when the game starts.");
                list.CheckboxLabeled("Vanilla sanguophage quests and scenario stay off (restart)", ref vanillaQuestsOff,
                    "Shipped default: ON. The 'host a sanguophage meeting' and 'sanguophage ship' quests never offer, and the "
                  + "Sanguophage start is hidden; Sith adepts carry no gene implanter; the Sith are a permanent enemy. WARNING: "
                  + "turning this off brings back quests whose reward is turning one of your colonists into a sanguophage. "
                  + "Applied when the game starts.");
                list.CheckboxLabeled("Sith buildings cannot be built or reinstalled (restart)", ref sithBuildingsUnbuildable,
                    "Shipped default: ON. The Sith sarcophagus and its five bound devices have no build command, cannot be "
                  + "minified and are never claimed; deconstructing a looted one still pays out. The Anzati keep their own "
                  + "buildable casket. Off: vanilla building rules. Applied when the game starts.");
                list.GapLine();
            }

            if (Group(list, "Never one of yours", RimMandrake.Shared.SettingScope.Now, new[] { "neverRecruitable", "blockXenogermAbsorb" }))
            {
                list.CheckboxLabeled("Sith adepts are never recruitable", ref neverRecruitable,
                    "Shipped default: ON. A Sith adept is unwaveringly loyal (brainwipe cannot change it), cannot be enslaved, "
                  + "and no recruit, quest or other route moves one into your faction. Capture, imprisonment, hemogen farming, "
                  + "execution and gene extraction stay allowed. Off: vanilla rules.");
                list.CheckboxLabeled("A Sith adept's xenogerm cannot be absorbed", ref blockXenogermAbsorb,
                    "Shipped default: ON. Sith adepts carry no gene implanter; this also closes 'absorb xenogerm' on an older or "
                  + "dev-spawned one that still has it, so the line never spreads to your people. Off: vanilla.");
                list.GapLine();
            }

            if (Group(list, "Inquisitors in the Galactic Empire", RimMandrake.Shared.SettingScope.Now, new[] { "inquisitorRaids", "inquisitorRaidChance", "inquisitorRaidMinPoints", "inquisitorDefenders", "inquisitorDefenderChance" }))
            {
                list.CheckboxLabeled("Inquisitors join Empire raids", ref inquisitorRaids,
                    "Shipped default: ON. A rare Sith inquisitor joins a Galactic Empire raid: at most one per raid, only above the "
                  + "points floor. Never in traders or visitors.");
                if (inquisitorRaids)
                {
                    list.Label("Raid chance: " + (inquisitorRaidChance * 100f).ToString("0") + "%");
                    inquisitorRaidChance = RSW_SithLineKernel.ClampChance(list.Slider(inquisitorRaidChance, 0f, 1f));
                    list.Label("Raid minimum points: " + inquisitorRaidMinPoints.ToString("0"));
                    inquisitorRaidMinPoints = list.Slider(inquisitorRaidMinPoints, 0f, 10000f);
                }
                list.CheckboxLabeled("Inquisitors defend Empire settlements", ref inquisitorDefenders,
                    "Shipped default: ON. When you assault a Galactic Empire base, one inquisitor may stand among the defenders.");
                if (inquisitorDefenders)
                {
                    list.Label("Defender chance: " + (inquisitorDefenderChance * 100f).ToString("0") + "%");
                    inquisitorDefenderChance = RSW_SithLineKernel.ClampChance(list.Slider(inquisitorDefenderChance, 0f, 1f));
                }
                list.GapLine();
            }

            if (Group(list, "The Abyss lair", RimMandrake.Shared.SettingScope.Now, new[] { "lairRumours", "lairRumourWeight", "lairRefireDays", "lairSearchRadius" }))
            {
                list.CheckboxLabeled("Rumours of a Sith lair in the Abyss", ref lairRumours,
                    "Shipped default: ON. Rarely, a whisper of the Dark points to a hidden sanctum in the Abyss near one of "
                  + "your maps: one lone Sith adept in dark trance among their devices, and a loot shelf. Never more than "
                  + "one open lair. Needs an Abyss tile within range. Off: the rumour never offers.");
                if (lairRumours)
                {
                    list.Label("Rumour weight: " + lairRumourWeight.ToString("0.00"));
                    lairRumourWeight = list.Slider(lairRumourWeight, 0f, 2f);
                    list.Label("Days before another rumour: " + lairRefireDays.ToString("0"));
                    lairRefireDays = list.Slider(lairRefireDays, 0f, 360f);
                    list.Label("Search radius (world tiles): " + lairSearchRadius);
                    lairSearchRadius = (int)list.Slider(lairSearchRadius, 1f, 40f);
                }
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RSW_SithLineMod : Mod
    {
        public static RSW_SithLineSettings Settings;

        public RSW_SithLineMod(ModContentPack content) : base(content)
        {
            // Constructed before the XML patches run, so RSW_PatchOperationSithSetting reads the player's real choices.
            Settings = GetSettings<RSW_SithLineSettings>();
        }

        public override string SettingsCategory() => "RimMandrake: SW — Sith Line";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            Settings.DoWindowContents(inRect);
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            RSW_SithLineStartup.ApplyLairTuning();
        }
    }
}
