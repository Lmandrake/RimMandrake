using System.Reflection;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.GizkaStowaway
{
    /// <summary>
    /// GIZKA_TRIBBLE_ADAPTATION_1 — Mod Settings, per draft §5 and
    /// MOD_OPTIONS_RETROFIT_1 (owner, 2026-09-12): a real settings screen, not
    /// a stub and not a constants file. Defaults equal the shipped design;
    /// all-off degrades gracefully (every feature gates at the comp or
    /// component level, so nothing NREs and no def is orphaned — the creature
    /// itself belongs to the donor mod and no toggle here touches it).
    ///
    /// Nothing in here affects worldgen. The doctrine asks that
    /// worldgen-affecting toggles be labelled as such; there are none, and the
    /// window says so.
    /// </summary>
    public class RSW_GizkaSettings : ModSettings
    {
        // --- master ---
        public static bool stowawayEventsEnabled = true;

        // --- discovery ---
        public static float discoveryFrequency = 1.0f;   // multiplies the per-trigger chance
        public static bool triggerGravship = true;
        public static bool triggerSalvage = true;
        public static bool triggerTrade = true;
        public static bool triggerQuest = true;

        // --- the turn ---
        public static float breedingRate = 1.0f;          // >1 = faster; divides the interval
        public static int populationCap = 22;
        public static bool chewingEnabled = true;

        // --- exits ---
        public static bool cullGuiltEnabled = true;

        // --- the creature itself (owner ruling, 2026-09-17) ---
        // Multiplies the ALREADY-PATCHED donor baseline in
        // Patches/RSW_GizkaDonorPatches.xml. 1.0 ships the patched numbers as
        // written; this slider is how a player who finds a planet made of
        // gizka tiresome gets their world back without unsubscribing anything.
        public static float globalBreedingRate = 1.0f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref stowawayEventsEnabled, "stowawayEventsEnabled", true);
            Scribe_Values.Look(ref discoveryFrequency, "discoveryFrequency", 1.0f);
            Scribe_Values.Look(ref triggerGravship, "triggerGravship", true);
            Scribe_Values.Look(ref triggerSalvage, "triggerSalvage", true);
            Scribe_Values.Look(ref triggerTrade, "triggerTrade", true);
            Scribe_Values.Look(ref triggerQuest, "triggerQuest", true);
            Scribe_Values.Look(ref breedingRate, "breedingRate", 1.0f);
            Scribe_Values.Look(ref populationCap, "populationCap", 22);
            Scribe_Values.Look(ref chewingEnabled, "chewingEnabled", true);
            Scribe_Values.Look(ref cullGuiltEnabled, "cullGuiltEnabled", true);
            Scribe_Values.Look(ref globalBreedingRate, "globalBreedingRate", 1.0f);
        }


        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RSW_GizkaSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RSW_GizkaSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

            if (Group(list, "Gizka stowaway events", RimMandrake.Shared.SettingScope.Now, new[] { "stowawayEventsEnabled" }))
            {
                list.CheckboxLabeled("Gizka stowaway events", ref stowawayEventsEnabled,
                    "The whole found-aboard feature: discovery, breeding, escalation and the gizka-chewed breakdowns. Off: gizka remain ordinary fauna and nothing in this mod happens. The creature and its art belong to Star Wars Animal Collection and are untouched either way.");
                list.GapLine();
            }

            if (Group(list, "Discovery", RimMandrake.Shared.SettingScope.Now, new[] { "discoveryFrequency", "triggerGravship", "triggerSalvage", "triggerTrade", "triggerQuest" }))
            {
                list.Label((TaggedString)("How often one turns up: " + discoveryFrequency.ToString("0.00") + "x"), -1f, "Multiplies the per-trigger chance, read each time a trigger fires.");
                discoveryFrequency = list.Slider(discoveryFrequency, 0f, 3f);
                list.CheckboxLabeled("...when a gravship lands", ref triggerGravship,
                    "Something has been living in the hold. This is the flagship moment; turning it off leaves the other three routes intact.");
                list.CheckboxLabeled("...when wreckage is deconstructed", ref triggerSalvage,
                    "It hopped out of the wreck.");
                list.CheckboxLabeled("...when a trade completes", ref triggerTrade,
                    "Crate three was not empty.");
                list.CheckboxLabeled("...when a quest is completed", ref triggerQuest,
                    "The free gift nobody asked for. The classic scam, inbound.");
                list.GapLine();
            }

            if (Group(list, "The turn: breeding and cap", RimMandrake.Shared.SettingScope.Now, new[] { "breedingRate", "populationCap" }))
            {
                list.Label((TaggedString)("Stowaway breeding rate: " + breedingRate.ToString("0.00") + "x"), -1f, "The default is a season-long slow burn on purpose. Stowaway-lineage gizka only breed while fed AND warm; cold or hunger stalls them entirely.");
                breedingRate = list.Slider(breedingRate, 0.1f, 5f);
                list.Label((TaggedString)("Population cap (per map): " + populationCap.ToString()), -1f, "Breeding stops dead at this number, and slows as it is approached. The infestation stage bands are fractions of it.");
                populationCap = (int)list.Slider(populationCap, 4f, 80f);
                list.GapLine();
            }

            if (Group(list, "The turn: chewing and guilt", RimMandrake.Shared.SettingScope.Now, new[] { "chewingEnabled", "cullGuiltEnabled" }))
            {
                list.CheckboxLabeled("Gizka chew wiring (breakdowns)", ref chewingEnabled,
                    "From the Infestation stage on, powered buildings sharing a room with stowaway gizka break down early, and the letter names the cause. Off: they stay cute and they still breed, but they stop sabotaging anything.");
                list.CheckboxLabeled("Culling them weighs on colonists", ref cullGuiltEnabled,
                    "A small, stacking mood memory for anyone who watched. Vanilla already charges for bonded animals; this is the charge for the rest of the swarm, and it is what keeps the humane exits competitive with the knife.");
                list.GapLine();
            }

            if (Group(list, "The creature itself (every gizka)", RimMandrake.Shared.SettingScope.Now, new[] { "globalBreedingRate" }))
            {
                list.Label((TaggedString)("Global gizka breeding rate: " + globalBreedingRate.ToString("0.00") + "x"), -1f, "Gizka breed fast everywhere in the world, wild, bought or traded, not only the stowaway lineage. This scales that, and applies even with stowaway events off. It is written into the defs when the settings window closes (or on the button below).");
                globalBreedingRate = list.Slider(globalBreedingRate, 0.1f, 3f);
                if (list.ButtonText("Apply creature breeding rate now"))
                {
                    RSW_GizkaDonorTuning.Apply();
                }
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }

        private static string Multiplier(float value) =>
            value.ToString("0.00") + "x" + (Mathf.Approximately(value, 1f) ? " (default)" : "");
    }

    public class RSW_GizkaStowawayMod : Mod
    {
        public static RSW_GizkaSettings Settings;

        public RSW_GizkaStowawayMod(ModContentPack content) : base(content)
        {
            Settings = GetSettings<RSW_GizkaSettings>();
        }

        public override string SettingsCategory() => "RimMandrake: SW — Gizka Stowaway";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            Settings.DoWindowContents(inRect);
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            RSW_GizkaDonorTuning.Apply();
        }
    }

    /// <summary>
    /// Owner ruling, 2026-09-17: "ensure that the gizka creature itself does
    /// have that crazy reproduction rate everywhere in the world."
    ///
    /// The shipped numbers are the XML patch in
    /// Patches/RSW_GizkaDonorPatches.xml — that is what a player gets with no
    /// settings touched, and it applies to every gizka anywhere, however it
    /// arrived. This class exists only so the slider can scale that baseline
    /// at runtime. It CAPTURES the post-patch values once and always rescales
    /// from the capture, never from the current value, so repeated applies do
    /// not compound (the trap that turns a 1.2x slider nudged five times into
    /// a 2.5x world).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class RSW_GizkaDonorTuning
    {
        /// <summary>
        /// One gizka's worth of live def fields plus the baseline they had
        /// when this mod first saw them.
        /// </summary>
        private class Tuned
        {
            public RimWorld.CompProperties_EggLayer eggLayer;
            public float baseEggLayIntervalDays;
            public IntRange baseEggCountRange;

            public RaceProperties race;
            public float baseMateMtbHours;

            public RimWorld.CompProperties_Hatcher hatcher;
            public float baseHatcherDays;
        }

        private static bool captured;
        private static readonly List<Tuned> tuned = new List<Tuned>();

        // BOTH gizka, deliberately: the donor's `Gizka` and SWBestiary's ported
        // `RSW_Gizka` (MLIE_FAUNA_ABSORPTION_1 Pass 12) are live at the same
        // time, and the port exists so the donor can one day be retired. A
        // slider that moved only one of them would quietly stop working on
        // that day. Pairs are (creature defName, fertilized-egg defName).
        private static readonly string[,] GizkaDefNames =
        {
            { "Gizka", "EggGizkaFertilized" },
            { "RSW_Gizka", "RSW_EggGizkaFertilized" }
        };

        static RSW_GizkaDonorTuning()
        {
            Apply();
        }

        private static void Capture()
        {
            if (captured) return;
            captured = true;

            for (int i = 0; i < GizkaDefNames.GetLength(0); i++)
            {
                ThingDef gizka = DefDatabase<ThingDef>.GetNamedSilentFail(GizkaDefNames[i, 0]);
                if (gizka == null) continue;   // that copy is not installed

                Tuned t = new Tuned();

                t.race = gizka.race;
                if (t.race != null) t.baseMateMtbHours = t.race.mateMtbHours;

                if (gizka.comps != null)
                {
                    foreach (CompProperties cp in gizka.comps)
                    {
                        if (cp is RimWorld.CompProperties_EggLayer el)
                        {
                            t.eggLayer = el;
                            t.baseEggLayIntervalDays = el.eggLayIntervalDays;
                            t.baseEggCountRange = el.eggCountRange;
                            break;
                        }
                    }
                }

                ThingDef egg = DefDatabase<ThingDef>.GetNamedSilentFail(GizkaDefNames[i, 1]);
                if (egg?.comps != null)
                {
                    foreach (CompProperties cp in egg.comps)
                    {
                        if (cp is RimWorld.CompProperties_Hatcher h)
                        {
                            t.hatcher = h;
                            t.baseHatcherDays = h.hatcherDaystoHatch;
                            break;
                        }
                    }
                }

                tuned.Add(t);
            }
        }

        public static void Apply()
        {
            Capture();

            float mult = RSW_GizkaSettings.globalBreedingRate;
            if (mult <= 0.01f) mult = 0.01f;

            foreach (Tuned t in tuned)
            {
                if (t.eggLayer != null)
                {
                    t.eggLayer.eggLayIntervalDays = t.baseEggLayIntervalDays / mult;
                    t.eggLayer.eggCountRange = new IntRange(
                        Mathf.Max(1, Mathf.RoundToInt(t.baseEggCountRange.min * mult)),
                        Mathf.Max(1, Mathf.RoundToInt(t.baseEggCountRange.max * mult)));
                }
                if (t.race != null && t.baseMateMtbHours > 0f)
                {
                    t.race.mateMtbHours = t.baseMateMtbHours / mult;
                }
                if (t.hatcher != null)
                {
                    t.hatcher.hatcherDaystoHatch = t.baseHatcherDays / mult;
                }
            }
        }
    }
}
