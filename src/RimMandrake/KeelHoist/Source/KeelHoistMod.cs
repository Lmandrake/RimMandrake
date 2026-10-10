using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.KeelHoist
{
    // HOIST_SHIP_PART_BUILD_1 (design/RimMandrake/ship_cargo_hoist_design_2026-10-01.md §2, RULED 2026-10-01).
    // Every toggle degrades to "the hoist simply does less", never to an error.
    public class KeelHoistSettings : ModSettings
    {
        public static bool masterEnabled = true;
        public static bool requireGravEngine = true;
        public static bool tetherLock = true;
        public static bool colonistsMayRide = true;
        public static bool downedStrangersAndBeasts = true;
        public static bool openLineMeter = true;
        public static float cycleTimeMultiplier = 1f;
        public static float cableRange = 14f;
        public static float restraintHours = 24f;
        // HUTT_SLAVE_PIT_SITE_BUILD_1: buyer pits (the Hutt slave pit is the first).
        public static bool pitSales = true;
        public static float pitPriceMultiplier = 0.6f;
        public static bool pitArenaHints = true;
        public static float arenaFighterBonus = 1.3f;
        public static bool pitSites = true;
        // HUTT_LOTTERY_CHUTE_BUILD_1: the chance chute.
        public static bool chuteEnabled = true;
        public static float chuteHouseCut = 0.15f;
        public static float chuteJackpotChance = 0.08f;
        public static float chuteBustChance = 0.1f;
        public static float chuteHours = 6f;

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref requireGravEngine, "requireGravEngine", true);
            Scribe_Values.Look(ref tetherLock, "tetherLock", true);
            Scribe_Values.Look(ref colonistsMayRide, "colonistsMayRide", true);
            Scribe_Values.Look(ref downedStrangersAndBeasts, "downedStrangersAndBeasts", true);
            Scribe_Values.Look(ref openLineMeter, "openLineMeter", true);
            Scribe_Values.Look(ref cycleTimeMultiplier, "cycleTimeMultiplier", 1f);
            Scribe_Values.Look(ref cableRange, "cableRange", 14f);
            Scribe_Values.Look(ref restraintHours, "restraintHours", 24f);
            Scribe_Values.Look(ref pitSales, "pitSales", true);
            Scribe_Values.Look(ref pitPriceMultiplier, "pitPriceMultiplier", 0.6f);
            Scribe_Values.Look(ref pitArenaHints, "pitArenaHints", true);
            Scribe_Values.Look(ref arenaFighterBonus, "arenaFighterBonus", 1.3f);
            Scribe_Values.Look(ref pitSites, "pitSites", true);
            Scribe_Values.Look(ref chuteEnabled, "chuteEnabled", true);
            Scribe_Values.Look(ref chuteHouseCut, "chuteHouseCut", 0.15f);
            Scribe_Values.Look(ref chuteJackpotChance, "chuteJackpotChance", 0.08f);
            Scribe_Values.Look(ref chuteBustChance, "chuteBustChance", 0.1f);
            Scribe_Values.Look(ref chuteHours, "chuteHours", 6f);
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 1200f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Hoist switches and safety", RimMandrake.Shared.SettingScope.Now, new[] { "masterEnabled", "requireGravEngine", "tetherLock", "colonistsMayRide", "downedStrangersAndBeasts", "openLineMeter" }))
            {
                list.CheckboxLabeled("Keel hoist enabled", ref masterEnabled,
                    "Shipped default: ON. Off: a keel hoist cannot lower its cable, take cargo or raise its cradle. "
                  + "Anything already in transit still arrives.");
                list.CheckboxLabeled("Only buildable on a gravship", ref requireGravEngine,
                    "Shipped default: ON. The hoist must stand on substructure of a map that carries a grav engine. "
                  + "Off: buildable anywhere (it still needs research and power).");
                list.CheckboxLabeled("Tether lock (safety rule)", ref tetherLock,
                    "Shipped default: ON. The ship refuses to launch while any keel hoist on its substructure has its "
                  + "cable down. Off: the ship may launch, and a hoist whose cable was down simply reels in on arrival.");
                list.CheckboxLabeled("Colonists may ride the cradle awake", ref colonistsMayRide,
                    "Shipped default: ON (owner ruling 2026-10-01). Off: only cargo, animals, prisoners and the downed ride.");
                list.CheckboxLabeled("Downed strangers and wild beasts can be lowered (arrive captured)", ref downedStrangersAndBeasts,
                    "Shipped default: ON. A downed stranger arrives as your prisoner; a downed wild animal arrives in the "
                  + "restraint cradle, bound for the hours set below. Off: only what a vanilla portal sends.");
                list.CheckboxLabeled("Open Line meter", ref openLineMeter,
                    "Shipped default: ON. A per-map count that rises every hour a cable is down and slowly falls when "
                  + "reeled in. It never limits what the hoist carries; sites will read it later.");
                list.GapLine();
            }

            if (Group(list, "Cycle time and cable reach", RimMandrake.Shared.SettingScope.Now, new[] { "cycleTimeMultiplier", "cableRange" }))
            {
                list.Label("Cycle time multiplier: " + cycleTimeMultiplier.ToStringPercent());
                cycleTimeMultiplier = list.Slider(cycleTimeMultiplier, 0.25f, 4f);
                list.Label("Cable reach (cells): " + Mathf.RoundToInt(cableRange));
                cableRange = Mathf.Round(list.Slider(cableRange, 4f, 40f));
                list.GapLine();
            }

            if (Group(list, "Restraint cradle (applies to the next beast lowered)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "restraintHours" }))
            {
                list.Label("Restraint cradle holds a wild beast for (hours): " + Mathf.RoundToInt(restraintHours));
                restraintHours = Mathf.Round(list.Slider(restraintHours, 1f, 72f));
                list.GapLine();
            }

            if (Group(list, "Buyer pits", RimMandrake.Shared.SettingScope.Now, new[] { "pitSales", "pitPriceMultiplier", "pitArenaHints", "arenaFighterBonus" }))
            {
                list.CheckboxLabeled("Buyer pits pay for what is lowered in", ref pitSales,
                    "Shipped default: ON. At a pit whose keepers buy (the Hutt slave pit), a slave, prisoner or beast "
                  + "lowered in is sold and the silver comes up the cable. Off: the pit takes them and pays nothing.");
                list.Label("Pit price, share of market value: " + pitPriceMultiplier.ToStringPercent());
                pitPriceMultiplier = list.Slider(pitPriceMultiplier, 0.1f, 2f);
                list.CheckboxLabeled("Arena weeks (fighters fetch more)", ref pitArenaHints,
                    "Shipped default: ON. One week in two the pit's arena is short of fighters, and a fighter (melee 8+, "
                  + "or a beast of combat power 100+) sells for the bonus below.");
                list.Label("Arena fighter bonus: x" + arenaFighterBonus.ToString("0.00"));
                arenaFighterBonus = list.Slider(arenaFighterBonus, 1f, 3f);
                list.GapLine();
            }

            if (Group(list, "Buyer pit sites (offered by quests)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "pitSites" }))
            {
                list.CheckboxLabeled("Buyer pit sites may be offered", ref pitSites,
                    "Shipped default: ON. Quests may offer a buyer pit site (the Hutt slave pit) a few tiles away. "
                  + "Off: no new site is offered; existing ones stay.");
                list.GapLine();
            }

            if (Group(list, "Chance chute", RimMandrake.Shared.SettingScope.Now, new[] { "chuteEnabled" }))
            {
                list.CheckboxLabeled("Chance chute takes stakes", ref chuteEnabled,
                    "Shipped default: ON. At a house's chance chute (the Hutt slave pit site) you lower a stake (goods, "
                  + "slaves or beasts); hours later a crate of similar value comes up. Off: the chute refuses stakes.");
                list.GapLine();
            }

            if (Group(list, "Chance chute odds (applied at the next roll)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "chuteHouseCut", "chuteJackpotChance", "chuteBustChance", "chuteHours" }))
            {
                list.Label("House cut of every stake: " + chuteHouseCut.ToStringPercent()
                           + "  (shipped odds return about 86% of a stake on average; a low cut with a high jackpot chance can tip it past 100%)");
                chuteHouseCut = list.Slider(chuteHouseCut, 0.02f, 0.5f);
                list.Label("Jackpot chance (crate x3): " + chuteJackpotChance.ToStringPercent());
                chuteJackpotChance = list.Slider(chuteJackpotChance, 0f, 0.3f);
                list.Label("Bust chance (crate x0.3): " + chuteBustChance.ToStringPercent());
                chuteBustChance = list.Slider(chuteBustChance, 0f, 0.5f);
                list.Label("Hours until the crate comes up: " + Mathf.RoundToInt(chuteHours));
                chuteHours = Mathf.Round(list.Slider(chuteHours, 1f, 24f));
                list.GapLine();
            }

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field
        // initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(KeelHoistSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(KeelHoistSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): switches, safety, cycle, reach, pit sales and
        /// chute stakes are read in gizmo/job/transit code (now); the restraint hours, pit-site offer and chute odds are read when
        /// the beast is lowered, the quest offers a site or the chute rolls (next pulse).</summary>
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

    public class KeelHoistMod : Mod
    {
        public const string HarmonyId = "mandrake.rm.keelhoist";
        public static KeelHoistSettings settings;

        public KeelHoistMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<KeelHoistSettings>();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony(HarmonyId), Assembly.GetExecutingAssembly(), "RimMandrake.KeelHoist");
        }

        public override string SettingsCategory() => "Keel Hoist";

        public override void DoSettingsWindowContents(Rect inRect) => settings.DoWindowContents(inRect);
    }

    [DefOf]
    public static class KeelHoistDefOf
    {
        public static ThingDef RM_KeelHoist;
        public static HediffDef RM_HoistRestraint;

        static KeelHoistDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(KeelHoistDefOf));
        }
    }
}
