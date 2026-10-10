using System.Reflection;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.UnfinishedLine
{
    // UNFINISHED_LINE_SPINE_COUNT_1 — Mod Settings for The Unfinished Line
    // (design/Jawa/proposals/droid_mass_production_quest_chain_2026-10-02.md §5). Only the
    // settings the spine and beat 1 read live here; each later beat adds its own.
    public class UnfinishedLineSettings : ModSettings
    {
        public static bool chainEnabled = true;
        public static int minEnclaveGoodwill = 20;
        public static int earliestDay = 30;
        public static int daysBetweenBeatsMin = 5;
        public static int daysBetweenBeatsMax = 10;
        public static int failuresAllowedPerBeat = 2;
        public static bool brokeredTruceEnabled = true;
        public static int ruinWildDroidsMax = 6;
        public static int freedWildDroidGoodwill = 4;
        public static bool coreBrokerEnabled = true;
        public static int coreBrokerWaitDays = 3;
        public static int coreSaleSilver = 2500;
        public static int coreSaleEmpireGoodwill = 15;
        // UNFINISHED_LINE_FIRSTLIGHT_BEAT_1
        public static float firstLightRunDays = 2f;
        public static float firstLightStrikeDelayHours = 6f;
        public static float firstLightHoldDays = 3f;
        // UNFINISHED_LINE_TITHE_BEAT_1 (all PROVISIONAL)
        public static float titheScale = 1f;
        public static int titheDeadlineDays = 20;
        public static int lendDays = 10;
        public static bool lendSkillGateEnabled = true;
        public static int lendMinCrafting = 8;
        public static int lendCraftingXp = 6000;
        // UNFINISHED_LINE_WORLD_FOUNDRY_1 (all PROVISIONAL)
        public static bool lineInWorldEnabled = true;
        public static float regrowthMaxFactor = 1.5f;
        public static int regrowthDaysToFull = 60;
        public static int stockFrames = 2;
        public static int stockPartSets = 2;
        public static int volunteerDays = 25;
        public static int volunteerCap = 6;
        public static int volunteerBetrayalGoodwill = 100;
        public static bool empireStrikesEnabled = true;
        public static float lineHeatPerDay = 1f;
        public static int strikeHeatThreshold = 30;
        // UNFINISHED_LINE_SITE_CHOICE_1 (all PROVISIONAL): extra goodwill on top of the envoy beat's +10 / +15
        public static bool siteChoiceEnabled = true;
        public static int siteAEnclaveDelta = 5;
        public static int siteAHiveDelta = 5;
        public static int siteCEnclaveDelta = 10;
        public static int siteCHiveDelta = -10;
        public static int siteDEnclaveDelta = -15;
        public static int siteDHiveDelta = 10;
        // UNFINISHED_LINE_SITE_BEATS_1 (PROVISIONAL): beats 4-5 read the chosen site
        public static bool siteBeatsEnabled = true;
        public static int siteAllyPoints = 300;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref chainEnabled, "chainEnabled", true);
            Scribe_Values.Look(ref minEnclaveGoodwill, "minEnclaveGoodwill", 20);
            Scribe_Values.Look(ref earliestDay, "earliestDay", 30);
            Scribe_Values.Look(ref daysBetweenBeatsMin, "daysBetweenBeatsMin", 5);
            Scribe_Values.Look(ref daysBetweenBeatsMax, "daysBetweenBeatsMax", 10);
            Scribe_Values.Look(ref failuresAllowedPerBeat, "failuresAllowedPerBeat", 2);
            Scribe_Values.Look(ref brokeredTruceEnabled, "brokeredTruceEnabled", true);
            Scribe_Values.Look(ref ruinWildDroidsMax, "ruinWildDroidsMax", 6);
            Scribe_Values.Look(ref freedWildDroidGoodwill, "freedWildDroidGoodwill", 4);
            Scribe_Values.Look(ref coreBrokerEnabled, "coreBrokerEnabled", true);
            Scribe_Values.Look(ref coreBrokerWaitDays, "coreBrokerWaitDays", 3);
            Scribe_Values.Look(ref coreSaleSilver, "coreSaleSilver", 2500);
            Scribe_Values.Look(ref coreSaleEmpireGoodwill, "coreSaleEmpireGoodwill", 15);
            Scribe_Values.Look(ref firstLightRunDays, "firstLightRunDays", 2f);
            Scribe_Values.Look(ref firstLightStrikeDelayHours, "firstLightStrikeDelayHours", 6f);
            Scribe_Values.Look(ref firstLightHoldDays, "firstLightHoldDays", 3f);
            Scribe_Values.Look(ref titheScale, "titheScale", 1f);
            Scribe_Values.Look(ref titheDeadlineDays, "titheDeadlineDays", 20);
            Scribe_Values.Look(ref lendDays, "lendDays", 10);
            Scribe_Values.Look(ref lendSkillGateEnabled, "lendSkillGateEnabled", true);
            Scribe_Values.Look(ref lendMinCrafting, "lendMinCrafting", 8);
            Scribe_Values.Look(ref lendCraftingXp, "lendCraftingXp", 6000);
            Scribe_Values.Look(ref lineInWorldEnabled, "lineInWorldEnabled", true);
            Scribe_Values.Look(ref regrowthMaxFactor, "regrowthMaxFactor", 1.5f);
            Scribe_Values.Look(ref regrowthDaysToFull, "regrowthDaysToFull", 60);
            Scribe_Values.Look(ref stockFrames, "stockFrames", 2);
            Scribe_Values.Look(ref stockPartSets, "stockPartSets", 2);
            Scribe_Values.Look(ref volunteerDays, "volunteerDays", 25);
            Scribe_Values.Look(ref volunteerCap, "volunteerCap", 6);
            Scribe_Values.Look(ref volunteerBetrayalGoodwill, "volunteerBetrayalGoodwill", 100);
            Scribe_Values.Look(ref empireStrikesEnabled, "empireStrikesEnabled", true);
            Scribe_Values.Look(ref lineHeatPerDay, "lineHeatPerDay", 1f);
            Scribe_Values.Look(ref strikeHeatThreshold, "strikeHeatThreshold", 30);
            Scribe_Values.Look(ref siteChoiceEnabled, "siteChoiceEnabled", true);
            Scribe_Values.Look(ref siteAEnclaveDelta, "siteAEnclaveDelta", 5);
            Scribe_Values.Look(ref siteAHiveDelta, "siteAHiveDelta", 5);
            Scribe_Values.Look(ref siteCEnclaveDelta, "siteCEnclaveDelta", 10);
            Scribe_Values.Look(ref siteCHiveDelta, "siteCHiveDelta", -10);
            Scribe_Values.Look(ref siteDEnclaveDelta, "siteDEnclaveDelta", -15);
            Scribe_Values.Look(ref siteDHiveDelta, "siteDHiveDelta", 10);
            Scribe_Values.Look(ref siteBeatsEnabled, "siteBeatsEnabled", true);
            Scribe_Values.Look(ref siteAllyPoints, "siteAllyPoints", 300);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(UnfinishedLineSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(UnfinishedLineSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1200f;
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

            if (Group(list, "The chain and its offer gate", RimMandrake.Shared.SettingScope.NextPulse, new[] { "chainEnabled", "minEnclaveGoodwill", "earliestDay" }))
            {
                list.CheckboxLabeled("Enable The Unfinished Line quest chain", ref chainEnabled,
                    "Off: the chain is never offered. A chain already running carries on. Nothing else changes. Read each time the spine checks whether to offer a beat.");
                list.Label((TaggedString)("Offer gate: Free Droid Enclave goodwill at least: " + minEnclaveGoodwill.ToString()), -1f, "Read when the offer is checked.");
                minEnclaveGoodwill = Mathf.RoundToInt(list.Slider(minEnclaveGoodwill, 0f, 75f));
                list.Label((TaggedString)("Offer gate: not before day: " + earliestDay.ToString()), -1f, "Read when the offer is checked.");
                earliestDay = Mathf.RoundToInt(list.Slider(earliestDay, 0f, 120f));
                list.GapLine();
            }

            if (Group(list, "Pacing and failure", RimMandrake.Shared.SettingScope.NextPulse, new[] { "daysBetweenBeatsMin", "daysBetweenBeatsMax", "failuresAllowedPerBeat" }))
            {
                list.Label((TaggedString)("Days between beats, shortest: " + daysBetweenBeatsMin.ToString()), -1f, "Read when the next beat is scheduled; a running wait keeps its date.");
                daysBetweenBeatsMin = Mathf.RoundToInt(list.Slider(daysBetweenBeatsMin, 1f, 30f));
                list.Label((TaggedString)("Days between beats, longest: " + daysBetweenBeatsMax.ToString()), -1f, "Never shorter than the shortest.");
                daysBetweenBeatsMax = Mathf.RoundToInt(list.Slider(daysBetweenBeatsMax, 1f, 30f));
                list.Label((TaggedString)("Failed attempts a beat may take before the chain breaks: " + failuresAllowedPerBeat.ToString()), -1f, "A failed beat is offered again; one failure past this number ends the chain. Read when a beat fails.");
                failuresAllowedPerBeat = Mathf.RoundToInt(list.Slider(failuresAllowedPerBeat, 0f, 5f));
                list.GapLine();
            }

            if (Group(list, "The Hive truce", RimMandrake.Shared.SettingScope.Now, new[] { "brokeredTruceEnabled" }))
            {
                list.CheckboxLabeled("The Enclaves broker a truce with the Hive", ref brokeredTruceEnabled,
                    "On: from the moment you accept the Hive's envoy until the chain ends, the Geonosian Foundry Hive is held at least neutral to you, so it does not raid while the chain runs. Harming the envoy breaks the truce and the chain. Off: the Hive stays as it is, and only the goodwill each beat earns moves it. Read when the envoy is accepted.");
                list.GapLine();
            }

            if (Group(list, "The Pattern Cores (beat 3)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "ruinWildDroidsMax", "freedWildDroidGoodwill", "coreBrokerEnabled", "coreBrokerWaitDays", "coreSaleSilver", "coreSaleEmpireGoodwill" }))
            {
                list.Label((TaggedString)("Most wild droids in the foundry ruin: " + ruinWildDroidsMax.ToString()), -1f, "Fewer at low threat points, at least 2. Read when the ruin site is generated.");
                ruinWildDroidsMax = Mathf.RoundToInt(list.Slider(ruinWildDroidsMax, 1f, 12f));
                list.Label((TaggedString)("Enclave goodwill per wild droid released unbolted: " + freedWildDroidGoodwill.ToString()), -1f, "Read when a droid is released.");
                freedWildDroidGoodwill = Mathf.RoundToInt(list.Slider(freedWildDroidGoodwill, 0f, 15f));
                list.CheckboxLabeled("A broker offers to buy the cores (the sell-out)", ref coreBrokerEnabled,
                    "On: once all three cores are at your colony, an Imperial salvage broker offers to buy them. Selling ends the whole chain and turns the Hive and the Enclaves hostile. Off: the cores go straight to the Enclaves and there is no betrayal path.");
                list.Label((TaggedString)("Days the broker waits for an answer: " + coreBrokerWaitDays.ToString()), -1f, "Read when the broker arrives.");
                coreBrokerWaitDays = Mathf.RoundToInt(list.Slider(coreBrokerWaitDays, 1f, 10f));
                list.Label((TaggedString)("Silver the broker pays: " + coreSaleSilver.ToString()), -1f, "Read when the offer is made and when you sell.");
                coreSaleSilver = Mathf.RoundToInt(list.Slider(coreSaleSilver, 0f, 10000f) / 100f) * 100;
                list.Label((TaggedString)("Empire goodwill for the sale: " + coreSaleEmpireGoodwill.ToString()), -1f, "Read when you sell.");
                coreSaleEmpireGoodwill = Mathf.RoundToInt(list.Slider(coreSaleEmpireGoodwill, 0f, 50f));
                list.GapLine();
            }

            if (Group(list, "First Light (beat 5)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "firstLightRunDays", "firstLightStrikeDelayHours", "firstLightHoldDays" }))
            {
                list.Label((TaggedString)("Length of the line's first run (days): " + firstLightRunDays.ToString("0.0")), -1f, "Captured when the beat starts.");
                firstLightRunDays = Mathf.Round(list.Slider(firstLightRunDays, 0.5f, 6f) * 2f) / 2f;
                list.Label((TaggedString)("Hours before the strike arrives: " + firstLightStrikeDelayHours.ToString("0")), -1f, "Captured when the beat starts.");
                firstLightStrikeDelayHours = Mathf.Round(list.Slider(firstLightStrikeDelayHours, 0f, 24f) * 1f) / 1f;
                list.Label((TaggedString)("Days the strike may hold your colony before the beat fails: " + firstLightHoldDays.ToString("0.0")), -1f, "Captured when the beat starts.");
                firstLightHoldDays = Mathf.Round(list.Slider(firstLightHoldDays, 1f, 10f) * 2f) / 2f;
                list.GapLine();
            }

            if (Group(list, "The Tithe and the Hands (beat 4)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "titheScale", "titheDeadlineDays", "lendDays", "lendSkillGateEnabled", "lendMinCrafting", "lendCraftingXp" }))
            {
                list.Label((TaggedString)("Tithe scale: " + titheScale.ToString("0.00") + "x (at 1x: " + LineTithe.BasePlasteel + " plasteel, " + LineTithe.BaseComponents + " components, " + LineTithe.BaseSteel + " steel, " + LineTithe.BaseUranium + " uranium)"), -1f, "Read when the tithe is worked out for the beat.");
                titheScale = Mathf.Round(list.Slider(titheScale, 0.25f, 3f) * 20f) / 20f;
                list.Label((TaggedString)("Days to load the Enclave shuttle with the tithe and the crafter: " + titheDeadlineDays.ToString()), -1f, "Captured when the beat starts.");
                titheDeadlineDays = Mathf.RoundToInt(list.Slider(titheDeadlineDays, 5f, 40f));
                list.Label((TaggedString)("Days the crafter works the line before coming home: " + lendDays.ToString()), -1f, "Captured when the beat starts.");
                lendDays = Mathf.RoundToInt(list.Slider(lendDays, 2f, 30f));
                list.CheckboxLabeled("The line asks for a skilled crafter", ref lendSkillGateEnabled,
                    "On: only a colonist with at least the Crafting level below may board the Enclave shuttle, and the beat is not offered while you have no such colonist. Off: any healthy colonist may go.");
                list.Label((TaggedString)("Lowest Crafting skill the line accepts: " + lendMinCrafting.ToString()), -1f, "Used while the skill gate is on.");
                lendMinCrafting = Mathf.RoundToInt(list.Slider(lendMinCrafting, 1f, 20f));
                list.Label((TaggedString)("Crafting experience the crafter brings home: " + lendCraftingXp.ToString()), -1f, "Read when the crafter returns.");
                lendCraftingXp = Mathf.RoundToInt(list.Slider(lendCraftingXp, 0f, 30000f) / 500f) * 500;
                list.GapLine();
            }

            if (Group(list, "The line in the world: regrowth and stock (affects the world)", RimMandrake.Shared.SettingScope.Now, new[] { "lineInWorldEnabled", "regrowthMaxFactor", "regrowthDaysToFull" }))
            {
                list.CheckboxLabeled("The line runs in the world", ref lineInWorldEnabled,
                    "AFFECTS THE WORLD (not map generation: it is read live). On: once the chain is finished, the Enclaves' settlements grow stronger over time, their traders sell Foundry-grade droid frames and part sets (never heads), free droids volunteer to join you, and the line's heat draws Imperial strikes. Off: finishing the chain changes only reputation and the story.");
                list.Label((TaggedString)("Enclave settlement defenders at full regrowth: " + regrowthMaxFactor.ToString("0.00") + "x"), -1f, "Multiplier at full regrowth.");
                regrowthMaxFactor = Mathf.Round(list.Slider(regrowthMaxFactor, 1f, 3f) * 20f) / 20f;
                list.Label((TaggedString)("Days of the line running to reach full regrowth: " + regrowthDaysToFull.ToString()), -1f, "");
                regrowthDaysToFull = Mathf.RoundToInt(list.Slider(regrowthDaysToFull, 10f, 240f));
                list.GapLine();
            }

            if (Group(list, "Foundry-grade stock and volunteers (affects the world)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "stockFrames", "stockPartSets", "volunteerDays", "volunteerCap", "volunteerBetrayalGoodwill" }))
            {
                list.Label((TaggedString)("Foundry-grade frames in each Enclave trader's stock: " + stockFrames.ToString()), -1f, "Read when a trader's stock is generated; stock already on a trader keeps what it has.");
                stockFrames = Mathf.RoundToInt(list.Slider(stockFrames, 0f, 6f));
                list.Label((TaggedString)("Foundry-grade part sets in each stock: " + stockPartSets.ToString()), -1f, "Leg, hand, sensor, motivator, servo, power cell. Read when stock is generated.");
                stockPartSets = Mathf.RoundToInt(list.Slider(stockPartSets, 0f, 6f));
                list.Label((TaggedString)("Days between volunteers while the Enclaves are your allies: " + (volunteerDays <= 0 ? "never (no volunteers)" : volunteerDays.ToString())), -1f, "0 means never. Read when the next volunteer is scheduled.");
                volunteerDays = Mathf.RoundToInt(list.Slider(volunteerDays, 0f, 60f));
                list.Label((TaggedString)("Most volunteers who will ever come: " + volunteerCap.ToString()), -1f, "Read live.");
                volunteerCap = Mathf.RoundToInt(list.Slider(volunteerCap, 1f, 20f));
                list.Label((TaggedString)("Enclave goodwill lost if you bolt or wipe a volunteer: " + volunteerBetrayalGoodwill.ToString()), -1f, "The line also stops running for you. Read when it happens.");
                volunteerBetrayalGoodwill = Mathf.RoundToInt(list.Slider(volunteerBetrayalGoodwill, 0f, 200f));
                list.GapLine();
            }

            if (Group(list, "Imperial Foundry strikes (affects the world)", RimMandrake.Shared.SettingScope.Now, new[] { "empireStrikesEnabled", "lineHeatPerDay", "strikeHeatThreshold" }))
            {
                list.CheckboxLabeled("Imperial Foundry strikes from line heat", ref empireStrikesEnabled,
                    "AFFECTS THE WORLD (read live). On: while the line runs, its heat rises every day; once it reaches the threshold below, an Imperial Foundry strike can come to your colony, and a strike cools the line back to zero. Off: no Foundry strikes.");
                list.Label((TaggedString)("Line heat per day: " + lineHeatPerDay.ToString("0.0")), -1f, "");
                lineHeatPerDay = Mathf.Round(list.Slider(lineHeatPerDay, 0f, 5f) * 10f) / 10f;
                list.Label((TaggedString)("Heat before a strike can come: " + strikeHeatThreshold.ToString()), -1f, "");
                strikeHeatThreshold = Mathf.RoundToInt(list.Slider(strikeHeatThreshold, 5f, 120f));
                list.GapLine();
            }

            if (Group(list, "Where the line stands (end of beat 2)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "siteChoiceEnabled", "siteAEnclaveDelta", "siteAHiveDelta", "siteCEnclaveDelta", "siteCHiveDelta", "siteDEnclaveDelta", "siteDHiveDelta", "siteBeatsEnabled", "siteAllyPoints" }))
            {
                list.CheckboxLabeled("Offer the choice of where the line stands", ref siteChoiceEnabled,
                    "On: a letter at the end of beat 2 lets you choose the foundry ruin, Enclave ground or the Ore Seams. Off: the ruin (A) is chosen for you. The line never stands at your colony. Read when the letter is due.");
                list.Label((TaggedString)("Foundry ruin: extra Enclave goodwill: " + siteAEnclaveDelta.ToString()), -1f, "Read when the site is chosen.");
                siteAEnclaveDelta = Mathf.RoundToInt(list.Slider(siteAEnclaveDelta, -30f, 30f));
                list.Label((TaggedString)("Foundry ruin: extra Hive goodwill: " + siteAHiveDelta.ToString()), -1f, "Read when the site is chosen.");
                siteAHiveDelta = Mathf.RoundToInt(list.Slider(siteAHiveDelta, -30f, 30f));
                list.Label((TaggedString)("Enclave ground: extra Enclave goodwill: " + siteCEnclaveDelta.ToString()), -1f, "Read when the site is chosen.");
                siteCEnclaveDelta = Mathf.RoundToInt(list.Slider(siteCEnclaveDelta, -30f, 30f));
                list.Label((TaggedString)("Enclave ground: extra Hive goodwill: " + siteCHiveDelta.ToString()), -1f, "Read when the site is chosen.");
                siteCHiveDelta = Mathf.RoundToInt(list.Slider(siteCHiveDelta, -30f, 30f));
                list.Label((TaggedString)("The Ore Seams: extra Enclave goodwill: " + siteDEnclaveDelta.ToString()), -1f, "Read when the site is chosen.");
                siteDEnclaveDelta = Mathf.RoundToInt(list.Slider(siteDEnclaveDelta, -30f, 30f));
                list.Label((TaggedString)("The Ore Seams: extra Hive goodwill: " + siteDHiveDelta.ToString()), -1f, "Read when the site is chosen.");
                siteDHiveDelta = Mathf.RoundToInt(list.Slider(siteDHiveDelta, -30f, 30f));
                list.CheckboxLabeled("Beats 4 and 5 follow the chosen site", ref siteBeatsEnabled,
                    "On: the crafter is lent to the faction that runs the chosen site, and that faction sends defenders to hold beside you when the strike comes. Off: beat 4 lends to the Hive and nobody helps in beat 5.");
                list.Label((TaggedString)("Allied defenders in beat 5 (points): " + siteAllyPoints.ToString()), -1f, "Read when the strike comes.");
                siteAllyPoints = Mathf.RoundToInt(list.Slider(siteAllyPoints, 100f, 1200f) / 50f) * 50;
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class UnfinishedLineMod : Mod
    {
        public static UnfinishedLineSettings settings;

        public UnfinishedLineMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<UnfinishedLineSettings>();
        }

        public override string SettingsCategory() => "The Unfinished Line";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }

    /// <summary>The two authored factions the chain sits between (faction_roster_v2.md). Looked up by
    /// defName, silently, so a list without the Utinni factions gets a chain that never offers rather
    /// than a load error.</summary>
    public static class LineFactions
    {
        public const string EnclavesDefName = "RUT_Jawa_FreeDroidEnclaves";
        public const string HiveDefName = "RUT_Jawa_GeonosianFoundryHive";
        public const string ShopRepairResearch = "RSW_DW_Research_ShopRepair";

        public static Faction Enclaves => Find(EnclavesDefName);

        public static Faction Hive => Find(HiveDefName);

        private static Faction Find(string defName)
        {
            FactionDef def = DefDatabase<FactionDef>.GetNamedSilentFail(defName);
            return def == null ? null : Verse.Find.FactionManager.FirstFactionOfDef(def);
        }

        /// <summary>The faction's settlement nearest <paramref name="tile"/> (any, if the tile is invalid).</summary>
        public static Settlement NearestSettlement(Faction f, PlanetTile tile)
        {
            if (f == null) return null;
            Settlement best = null;
            float bestDist = float.MaxValue;
            foreach (Settlement s in Verse.Find.WorldObjects.Settlements)
            {
                if (s.Faction != f) continue;
                float d = tile.Valid && tile.Layer == s.Tile.Layer ? Verse.Find.WorldGrid.ApproxDistanceInTiles(tile, s.Tile) : 0f;
                if (d < bestDist)
                {
                    best = s;
                    bestDist = d;
                }
            }
            return best;
        }
    }
}
