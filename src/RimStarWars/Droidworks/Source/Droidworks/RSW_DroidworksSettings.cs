using System.Reflection;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Droidworks.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs — STATIC fields read
    // from everywhere, Scribe_Values in ExposeData, a DoWindowContents helper
    // called from the Mod subclass.
    //
    // 🔑 STATIC, because the readers are comps, hediff comps, incident workers,
    // Harmony patches and a StockGenerator — none of which have a handle on a
    // Mod instance, and several of which run before/outside any map.
    //
    // ⚠️ THIS CLASS IS READ FROM BOTH ASSEMBLIES THIS MOD SHIPS. The main
    // Droidworks.dll owns it; DroidworksBoltCore.dll (Source/BoltCore/) reads
    // boltSuppressesMentalBreaks through a ProjectReference added for exactly
    // that. Do not move or rename it without updating BoltCorePatches.cs.
    //
    // Defaults are the SHIPPED behaviour, every one of them — the numbers here
    // were lifted from the consts and HediffCompProperties defaults they now
    // replace, so an untouched settings screen changes nothing.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_DroidworksSettings : ModSettings
    {
        // ── Restraining bolts ──────────────────────────────────────────────
        public static bool boltSuppressesMentalBreaks = true;
        public static bool boltResentment = true;
        public static float boltResentmentRate = 1f;
        public static bool boltShear = true;
        public static float boltShearChance = 1f;
        public static bool boltRebellion = true;
        public static float boltRebellionThreshold = 0.6f;
        public static bool boltMoodPenalty = true;
        public static float boltMoodRadius = 12f;

        // ── Power and charging ─────────────────────────────────────────────
        public static bool powerNeed = true;
        public static float powerDrainRate = 1f;
        public static float chargeRate = 1f;
        public static bool powerDownWhenEmpty = true;

        // ── Ion hits shut a droid down ─────────────────────────────────────
        public static bool ionShutdown = true;
        public static float ionShutdownThreshold = 0.5f;

        // ── Detonation on death ────────────────────────────────────────────
        public static bool detonation = true;
        public static float detonationSize = 1f;

        // ── Memory wipe aftermath ──────────────────────────────────────────
        public static bool wipeStumble = true;
        public static float wipeStumbleChance = 1f;
        public static bool wipeQuirks = true;
        public static float wipeQuirkChance = 0.6f;

        // ── Wild droids ────────────────────────────────────────────────────
        public static bool wildDroidCrash = true;

        // ── Salvage from a dead droid ──────────────────────────────────────
        public static bool headDrop = true;
        public static bool partDrop = true;
        public static float partDropChance = 0.6f;

        // ── Personality drift ──────────────────────────────────────────────
        public static bool personalityDrift = true;
        public static float driftTime = 1f;

        // ── Protocol droids and trade ──────────────────────────────────────
        public static bool protocolTrade = true;
        public static float protocolTradePerSide = 0.06f;

        // ── Hutt captives ──────────────────────────────────────────────────
        public static bool huttCaptivesBolted = true;


        public override void ExposeData()
        {
            base.ExposeData();

            Scribe_Values.Look(ref boltSuppressesMentalBreaks, "boltSuppressesMentalBreaks", true, true);
            Scribe_Values.Look(ref boltResentment, "boltResentment", true, true);
            Scribe_Values.Look(ref boltResentmentRate, "boltResentmentRate", 1f, true);
            Scribe_Values.Look(ref boltShear, "boltShear", true, true);
            Scribe_Values.Look(ref boltShearChance, "boltShearChance", 1f, true);
            Scribe_Values.Look(ref boltRebellion, "boltRebellion", true, true);
            Scribe_Values.Look(ref boltRebellionThreshold, "boltRebellionThreshold", 0.6f, true);
            Scribe_Values.Look(ref boltMoodPenalty, "boltMoodPenalty", true, true);
            Scribe_Values.Look(ref boltMoodRadius, "boltMoodRadius", 12f, true);

            Scribe_Values.Look(ref powerNeed, "powerNeed", true, true);
            Scribe_Values.Look(ref powerDrainRate, "powerDrainRate", 1f, true);
            Scribe_Values.Look(ref chargeRate, "chargeRate", 1f, true);
            Scribe_Values.Look(ref powerDownWhenEmpty, "powerDownWhenEmpty", true, true);

            Scribe_Values.Look(ref ionShutdown, "ionShutdown", true, true);
            Scribe_Values.Look(ref ionShutdownThreshold, "ionShutdownThreshold", 0.5f, true);

            Scribe_Values.Look(ref detonation, "detonation", true, true);
            Scribe_Values.Look(ref detonationSize, "detonationSize", 1f, true);

            Scribe_Values.Look(ref wipeStumble, "wipeStumble", true, true);
            Scribe_Values.Look(ref wipeStumbleChance, "wipeStumbleChance", 1f, true);
            Scribe_Values.Look(ref wipeQuirks, "wipeQuirks", true, true);
            Scribe_Values.Look(ref wipeQuirkChance, "wipeQuirkChance", 0.6f, true);

            Scribe_Values.Look(ref wildDroidCrash, "wildDroidCrash", true, true);

            Scribe_Values.Look(ref headDrop, "headDrop", true, true);
            Scribe_Values.Look(ref partDrop, "partDrop", true, true);
            Scribe_Values.Look(ref partDropChance, "partDropChance", 0.6f, true);

            Scribe_Values.Look(ref personalityDrift, "personalityDrift", true, true);
            Scribe_Values.Look(ref driftTime, "driftTime", 1f, true);

            Scribe_Values.Look(ref protocolTrade, "protocolTrade", true, true);
            Scribe_Values.Look(ref protocolTradePerSide, "protocolTradePerSide", 0.06f, true);

            Scribe_Values.Look(ref huttCaptivesBolted, "huttCaptivesBolted", true, true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RSW_DroidworksSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RSW_DroidworksSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

            if (Group(list, "Restraining bolts: breaks and resentment", RimMandrake.Shared.SettingScope.Now, new[] { "boltSuppressesMentalBreaks", "boltResentment", "boltResentmentRate", "boltRebellion", "boltRebellionThreshold" }))
            {
                list.CheckboxLabeled("Bolts stop a droid breaking down", ref boltSuppressesMentalBreaks,
                    "A droid wearing a restraining bolt never has a mental break. Off: a bolted droid breaks down like anyone else.");
                list.CheckboxLabeled("Bolted droids build up resentment", ref boltResentment,
                    "A thinking droid quietly resents the bolt for as long as it wears one, and never forgets once the bolt comes off. Off: no resentment is ever recorded.");
                list.Label((TaggedString)("How fast resentment builds: " + Multiplier(boltResentmentRate)), -1f, "Only used while resentment is on.");
                boltResentmentRate = list.Slider(boltResentmentRate, 0.25f, 3f);
                list.CheckboxLabeled("A freed droid can turn on you", ref boltRebellion,
                    "Take the bolt off a droid that has resented it long enough and it goes berserk. Off: removing a bolt is always safe.");
                list.Label((TaggedString)("Resentment needed before it turns: " + boltRebellionThreshold.ToStringPercent("0") + " (default 60%)"), -1f, "Only used while rebellion is on.");
                boltRebellionThreshold = list.Slider(boltRebellionThreshold, 0.1f, 1f);
                list.GapLine();
            }

            if (Group(list, "Restraining bolts: fights and mood", RimMandrake.Shared.SettingScope.Now, new[] { "boltShear", "boltShearChance", "boltMoodPenalty", "boltMoodRadius" }))
            {
                list.CheckboxLabeled("Bolts can be knocked off in a fight", ref boltShear,
                    "A hit landing on a bolted droid can snap the bolt clean off. Off: a bolt only ever comes off deliberately, at a bench.");
                list.Label((TaggedString)("How easily a bolt snaps off: " + Multiplier(boltShearChance)), -1f, "Only used while shearing is on.");
                boltShearChance = list.Slider(boltShearChance, 0.25f, 3f);
                list.CheckboxLabeled("People are unsettled by bolted droids nearby", ref boltMoodPenalty,
                    "A mood penalty for anyone standing near a droid in a restraining bolt. Off: nobody minds.");
                list.Label((TaggedString)("How far that carries (tiles): " + boltMoodRadius.ToString("0") + " (default 12)"), -1f, "Only used while the mood penalty is on.");
                boltMoodRadius = list.Slider(boltMoodRadius, 2f, 30f);
                list.GapLine();
            }

            if (Group(list, "Droids run on stored power (reload)", RimMandrake.Shared.SettingScope.Now, new[] { "powerNeed" }, "[next game start]"))
            {
                list.CheckboxLabeled("Droids run on stored power", ref powerNeed,
                    "Droids carry a power bar that drains and has to be topped up at a charger. Off: droids never need charging and the power bar disappears. It is applied when a droid's needs are next recalculated (a hediff change, a birthday, a load), so reload to be sure.");
                list.GapLine();
            }

            if (Group(list, "Power drain and charging", RimMandrake.Shared.SettingScope.Now, new[] { "powerDrainRate", "chargeRate", "powerDownWhenEmpty" }))
            {
                list.Label((TaggedString)("How fast power drains: " + Multiplier(powerDrainRate)), -1f, "Read every need interval.");
                powerDrainRate = list.Slider(powerDrainRate, 0.25f, 3f);
                list.Label((TaggedString)("How fast chargers refill it: " + Multiplier(chargeRate)), -1f, "Read by the charger and the recharge job every tick they run.");
                chargeRate = list.Slider(chargeRate, 0.25f, 3f);
                list.CheckboxLabeled("A flat droid shuts down", ref powerDownWhenEmpty,
                    "Run the bar to empty and the droid powers down until somebody reboots it. Off: an empty droid just keeps going on fumes.");
                list.GapLine();
            }

            if (Group(list, "Ion hits shut a droid down", RimMandrake.Shared.SettingScope.Now, new[] { "ionShutdown", "ionShutdownThreshold" }))
            {
                list.CheckboxLabeled("Ion damage powers a droid down for good", ref ionShutdown,
                    "Enough ion damage and the droid stays off until somebody reboots it. Off: ion just stuns, and the droid recovers by itself.");
                list.Label((TaggedString)("Ion charge needed to shut it down: " + ionShutdownThreshold.ToStringPercent("0") + " (default 50%)"), -1f, "Only used while ion shutdown is on.");
                ionShutdownThreshold = list.Slider(ionShutdownThreshold, 0.1f, 1f);
                list.GapLine();
            }

            if (Group(list, "Droids blow up when destroyed", RimMandrake.Shared.SettingScope.Now, new[] { "detonation", "detonationSize" }))
            {
                list.CheckboxLabeled("Destroyed droids can detonate", ref detonation,
                    "A droid killed with charge still in it goes up. A drained wreck never does. Off: droids never explode.");
                list.Label((TaggedString)("Size of the blast: " + Multiplier(detonationSize)), -1f, "Only used while detonation is on.");
                detonationSize = list.Slider(detonationSize, 0.25f, 3f);
                list.GapLine();
            }

            if (Group(list, "After a memory wipe", RimMandrake.Shared.SettingScope.Now, new[] { "wipeStumble", "wipeStumbleChance", "wipeQuirks", "wipeQuirkChance" }))
            {
                list.CheckboxLabeled("A wiped droid blunders about for a week", ref wipeStumble,
                    "It drops what it was doing and wanders off mid-job while it relearns its body. Off: a wiped droid works normally straight away.");
                list.Label((TaggedString)("How often it loses the thread: " + Multiplier(wipeStumbleChance)), -1f, "Only used while stumbling is on.");
                wipeStumbleChance = list.Slider(wipeStumbleChance, 0.25f, 3f);
                list.CheckboxLabeled("Wipes leave permanent damage", ref wipeQuirks,
                    "Each wipe can leave a hardware quirk that never goes away and stacks with the last. Off: a wipe costs nothing lasting.");
                list.Label((TaggedString)("Chance a wipe leaves one: " + wipeQuirkChance.ToStringPercent("0") + " (default 60%)"), -1f, "Only used while quirks are on.");
                wipeQuirkChance = list.Slider(wipeQuirkChance, 0f, 1f);
                list.GapLine();
            }

            if (Group(list, "Wild droids", RimMandrake.Shared.SettingScope.Now, new[] { "wildDroidCrash" }))
            {
                list.CheckboxLabeled("Crashed droids wander in off the desert", ref wildDroidCrash,
                    "An ownerless droid that has been out there too long walks onto the map and attacks anything it sees. Off: the storyteller never picks the event.");
                list.GapLine();
            }

            if (Group(list, "Salvage from a dead droid", RimMandrake.Shared.SettingScope.Now, new[] { "headDrop", "partDrop", "partDropChance" }))
            {
                list.CheckboxLabeled("Droids drop their head", ref headDrop,
                    "A destroyed droid leaves its head, carrying who it was. Off: no heads drop.");
                list.CheckboxLabeled("Droids drop spare parts", ref partDrop,
                    "Legs, manipulators, sensors and the rest, rolled one at a time. Off: no parts drop.");
                list.Label((TaggedString)("Chance for each part: " + partDropChance.ToStringPercent("0") + " (default 60%)"), -1f, "Only used while parts drop.");
                partDropChance = list.Slider(partDropChance, 0f, 1f);
                list.GapLine();
            }

            if (Group(list, "Droids become people", RimMandrake.Shared.SettingScope.Now, new[] { "personalityDrift", "driftTime" }))
            {
                list.CheckboxLabeled("Long-unwiped droids grow a personality", ref personalityDrift,
                    "A droid left unwiped for years picks up habits of its own, and the first one wakes a programmable droid into a thinking one. A wipe takes it all back. Off: a droid is the same droid forever.");
                list.Label((TaggedString)("How long that takes: " + Multiplier(driftTime)), -1f, "First habit at 2 years by default.");
                driftTime = list.Slider(driftTime, 0.25f, 3f);
                list.GapLine();
            }

            if (Group(list, "Protocol droids and trade", RimMandrake.Shared.SettingScope.Now, new[] { "protocolTrade", "protocolTradePerSide" }))
            {
                list.CheckboxLabeled("Protocol droids shift trade prices", ref protocolTrade,
                    "Bring one and prices move your way; turn up without one against a trader who has one and they move against you. Off: prices are whatever they would normally be.");
                list.Label((TaggedString)("Price shift per side: " + protocolTradePerSide.ToStringPercent("0.0") + " (default 6%)"), -1f, "Only used while trade shifting is on.");
                protocolTradePerSide = list.Slider(protocolTradePerSide, 0f, 0.25f);
                list.GapLine();
            }

            if (Group(list, "Hutt captives (next stock)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "huttCaptivesBolted" }))
            {
                list.CheckboxLabeled("Hutt debtor droids arrive already bolted", ref huttCaptivesBolted,
                    "Droids bought off a Hutt trader come wearing a restraining bolt and carrying the resentment their time in hock earned. Applies to stock generated after the change; stock already on a trader keeps what it has. Off: they are sold like ordinary stock.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }

        private static string Multiplier(float value) =>
            value.ToString("0.00") + "x" + (Mathf.Approximately(value, 1f) ? " (default)" : "");
    }

    public class RSW_DroidworksMod : Mod
    {
        public static RSW_DroidworksSettings settings;

        public RSW_DroidworksMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_DroidworksSettings>();
        }

        public override string SettingsCategory() => "Droidworks";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
