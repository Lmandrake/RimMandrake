using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.SWBestiary
{
    // ════════════════════════════════════════════════════════════════════
    // PORTED_BEAST_MECHANICS_REBUILD_1 — Mod Settings for the SWBestiary
    // BeastMechanics assembly (RimMandrakeBeastMechanicsRSW.dll), and the
    // Harmony instance the one prefix in this assembly is patched through.
    //
    // Precedent and reasoning for a separate settings entry rather than one
    // shared with Livestock/Ikee: RSW_LivestockSettings.cs's own header.
    // Three DLLs ship inside the SWBestiary folder and none of them
    // references the others, so each carries its own Mod class.
    //
    // Per the standing rule that every mod ships real Mod Settings:
    // defaults are the shipped behaviour, and every mechanic here degrades
    // gracefully when switched off (the creature simply keeps its stats and
    // loses the gimmick, which is exactly the state the port shipped in).
    // ════════════════════════════════════════════════════════════════════
    public class RSW_BeastMechanicsSettings : ModSettings
    {
        // Ferroclaw's steel diet: the comp, the eat job and the block on
        // seeking ordinary food all read this.
        public static bool metalEatingEnabled = true;

        // Voltmaw's plasma volley and cindermite's fuel spew: whether the
        // innate ability is granted at all. Already-granted abilities are
        // left alone, so turning this off stops new creatures gaining one.
        public static bool innateAbilitiesEnabled = true;

        // SHRUBLAND_SCRAPNEST_BIRDS_1 — the scrap-nest bird's hoarding drive:
        // the job giver, the nest-building fallback and the haul job all read
        // this. Off, the bird keeps every stat, its flight and its eggs and
        // simply stops collecting — and any nest already on the map stays put
        // and keeps restocking, because that half is a pure vanilla
        // CompProperties_Spawner this flag does not reach.
        public static bool scrapHoardingEnabled = true;

        // SCRAPNEST_BIRD_BASE_THEFT_1 — owner-ruled (2026-09-21, 2026-10-10:
        // "Yes they steal everything, and there are also stealing raids.").
        // ⚠️ PROVISIONAL defaults: the owner did not say on or off by default;
        // ON matches "they steal everything". See ScrapThiefFlock.cs.
        // Base theft: ambient scrap-nest birds also take hoardable items from
        // stockpiles, shelves and the home area. Off: they keep to loose scrap
        // outside the base, exactly as first shipped. Nests are never sited
        // inside the home area either way.
        public static bool scrapBirdBaseTheftEnabled = true;

        // Raiding flocks: the IncidentWorker_ScrapThiefFlock event. A flock in
        // a raid robs the base even with base theft off — the raid is the event.
        public static bool scrapThiefFlockEnabled = true;

        // The mutagenic norphea's toxin dependence (ToxinDependence.cs): the
        // need rises on polluted ground or with toxic buildup and falls
        // elsewhere, with a lethal withdrawal stage. Off: the need is held full.
        public static bool toxinDependenceEnabled = true;

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref metalEatingEnabled, "metalEatingEnabled", true);
            Scribe_Values.Look(ref innateAbilitiesEnabled, "innateAbilitiesEnabled", true);
            Scribe_Values.Look(ref scrapHoardingEnabled, "scrapHoardingEnabled", true);
            Scribe_Values.Look(ref scrapBirdBaseTheftEnabled, "scrapBirdBaseTheftEnabled", true);
            Scribe_Values.Look(ref scrapThiefFlockEnabled, "scrapThiefFlockEnabled", true);
            Scribe_Values.Look(ref toxinDependenceEnabled, "toxinDependenceEnabled", true);
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RSW_BeastMechanicsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RSW_BeastMechanicsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): metal eating, scrap hoarding, base theft and toxin dependence are read by job givers, patches and the need tick each time they run, so [now]; the innate ability is granted when a creature spawns, so changing it only matters for creatures that spawn afterwards: [next pulse]; the scrap-bird raid is checked when the storyteller next rolls it: [next pulse]. Nothing is read at map or world generation.</summary>
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
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Metal-eating creatures", RimMandrake.Shared.SettingScope.Now, new[] { "metalEatingEnabled" }))
            {
                list.CheckboxLabeled("Metal-eating creatures", ref metalEatingEnabled,
                    "The ferroclaw feeds on steel and steel slag instead of grazing, and digs slag up when a map has none. Off: it grazes like any other animal.");
                list.GapLine();
            }

            if (Group(list, "Innate creature abilities", RimMandrake.Shared.SettingScope.NextPulse, new[] { "innateAbilitiesEnabled" }))
            {
                list.CheckboxLabeled("Innate creature abilities", ref innateAbilitiesEnabled,
                    "The voltmaw fires a plasma volley and the cindermite sprays raw chemfuel. Off: neither gains its ranged attack. A creature that already has the ability keeps it.");
                list.GapLine();
            }

            if (Group(list, "Scrap-hoarding birds", RimMandrake.Shared.SettingScope.Now, new[] { "scrapHoardingEnabled", "scrapBirdBaseTheftEnabled" }))
            {
                list.CheckboxLabeled("Scrap-hoarding birds", ref scrapHoardingEnabled,
                    "Scrap-nest birds build nests in the wild and carry scrap, components and precious metals back to them. Off: they forage and fly like any other bird, no raiding flocks come, and existing nests still slowly accumulate scrap on their own.");
                list.CheckboxLabeled("Birds steal from your base", ref scrapBirdBaseTheftEnabled,
                    "Scrap-nest birds also take components, precious metals and steel out of your stockpiles, shelves and home area, and you get an alert when they do. The loot goes to a nest outside your base, never inside it. Off: they only take loose scrap lying outside your base.");
                list.GapLine();
            }

            if (Group(list, "Scrap-bird raids", RimMandrake.Shared.SettingScope.NextPulse, new[] { "scrapThiefFlockEnabled" }))
            {
                list.CheckboxLabeled("Scrap-bird raiding flocks", ref scrapThiefFlockEnabled,
                    "An event: a flock of scrap-nest birds flies into a colony where they live, robs it for half a day to a day, then leaves. Each theft raises an alert. A raiding flock steals from your base even when the base-theft option above is off. Off: the event never fires.");
                list.GapLine();
            }

            if (Group(list, "Toxin-dependent creatures", RimMandrake.Shared.SettingScope.Now, new[] { "toxinDependenceEnabled" }))
            {
                list.CheckboxLabeled("Toxin-dependent creatures", ref toxinDependenceEnabled,
                    "The mutagenic norphea needs polluted ground or toxic buildup to stay well, and sickens and can die in withdrawal on clean land. Off: its dependence is always satisfied.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RSW_BeastMechanicsMod : Mod
    {
        public RSW_BeastMechanicsMod(ModContentPack content) : base(content)
        {
            GetSettings<RSW_BeastMechanicsSettings>();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rsw.swbestiary.beastmechanics"), typeof(RSW_BeastMechanicsMod).Assembly, "RimStarWars.SWBestiary.BeastMechanics");
        }

        public override string SettingsCategory()
        {
            return "RimMandrake: SW — Bestiary (beast mechanics)";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            GetSettings<RSW_BeastMechanicsSettings>().DoWindowContents(inRect);
        }
    }
}
