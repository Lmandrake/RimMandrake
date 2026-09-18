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
        public bool stowawayEventsEnabled = true;

        // --- discovery ---
        public float discoveryFrequency = 1.0f;   // multiplies the per-trigger chance
        public bool triggerGravship = true;
        public bool triggerSalvage = true;
        public bool triggerTrade = true;
        public bool triggerQuest = true;

        // --- the turn ---
        public float breedingRate = 1.0f;          // >1 = faster; divides the interval
        public int populationCap = 22;
        public bool chewingEnabled = true;

        // --- exits ---
        public bool cullGuiltEnabled = true;

        // --- the creature itself (owner ruling, 2026-09-17) ---
        // Multiplies the ALREADY-PATCHED donor baseline in
        // Patches/RSW_GizkaDonorPatches.xml. 1.0 ships the patched numbers as
        // written; this slider is how a player who finds a planet made of
        // gizka tiresome gets their world back without unsubscribing anything.
        public float globalBreedingRate = 1.0f;

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
    }

    public class RSW_GizkaStowawayMod : Mod
    {
        public static RSW_GizkaSettings Settings;

        public RSW_GizkaStowawayMod(ModContentPack content) : base(content)
        {
            Settings = GetSettings<RSW_GizkaSettings>();
        }

        public override string SettingsCategory() => "RimMandrake: SW — Gizka Stowaway";

        private Vector2 scrollPos = Vector2.zero;

        public override void DoSettingsWindowContents(Rect inRect)
        {
            // The content is taller than a settings window at 1080p, so it
            // scrolls rather than clipping the bottom rows off.
            Rect viewRect = new Rect(0f, 0f, inRect.width - 20f, 780f);
            Widgets.BeginScrollView(inRect, ref scrollPos, viewRect);

            Listing_Standard l = new Listing_Standard();
            l.Begin(viewRect);

            GUI.color = new Color(0.7f, 0.7f, 0.7f);
            l.Label("None of these settings affect world generation. All of them take effect immediately, in an ongoing game.");
            GUI.color = Color.white;
            l.GapLine();

            // ---------------- master ----------------
            l.CheckboxLabeled(
                "Gizka stowaway events",
                ref Settings.stowawayEventsEnabled,
                "The whole found-aboard feature: discovery, breeding, escalation and the gizka-chewed breakdowns.\n\nOff: gizka remain ordinary fauna and nothing in this mod happens. The creature and its art belong to Star Wars Animal Collection and are untouched either way.");

            bool on = Settings.stowawayEventsEnabled;

            l.Gap(6f);
            l.GapLine();
            l.Label("Discovery");

            if (on)
            {
                l.Label("How often one turns up: " + Settings.discoveryFrequency.ToString("0.00") + "x");
                Settings.discoveryFrequency = l.Slider(Settings.discoveryFrequency, 0f, 3f);

                l.CheckboxLabeled("  ...when a gravship lands", ref Settings.triggerGravship,
                    "Something has been living in the hold. This is the flagship moment; turning it off leaves the other three routes intact.");
                l.CheckboxLabeled("  ...when wreckage is deconstructed", ref Settings.triggerSalvage,
                    "It hopped out of the wreck.");
                l.CheckboxLabeled("  ...when a trade completes", ref Settings.triggerTrade,
                    "Crate three was not empty.");
                l.CheckboxLabeled("  ...when a quest is completed", ref Settings.triggerQuest,
                    "The free gift nobody asked for. The classic scam, inbound.");
            }
            else
            {
                GUI.color = new Color(0.6f, 0.6f, 0.6f);
                l.Label("  (disabled — stowaway events are off)");
                GUI.color = Color.white;
            }

            l.Gap(6f);
            l.GapLine();
            l.Label("The turn");

            if (on)
            {
                l.Label("Breeding rate: " + Settings.breedingRate.ToString("0.00") + "x");
                Settings.breedingRate = l.Slider(Settings.breedingRate, 0.1f, 5f);
                GUI.color = new Color(0.7f, 0.7f, 0.7f);
                l.Label("    The default is a season-long slow burn on purpose. Stowaway-lineage gizka only breed while fed AND warm; cold or hunger stalls them entirely.");
                GUI.color = Color.white;

                l.Label("Population cap (per map): " + Settings.populationCap);
                Settings.populationCap = Mathf.RoundToInt(l.Slider(Settings.populationCap, 4f, 80f));
                GUI.color = new Color(0.7f, 0.7f, 0.7f);
                l.Label("    Breeding stops dead at this number, and slows as it is approached. This is the ceiling that keeps the problem a problem instead of a crash.");
                GUI.color = Color.white;

                l.CheckboxLabeled("Gizka chew wiring (breakdowns)", ref Settings.chewingEnabled,
                    "From the Infestation stage on, powered buildings sharing a room with stowaway gizka break down early, and the letter names the cause.\n\nOff: they stay cute and they still breed, but they stop sabotaging anything.");

                l.CheckboxLabeled("Culling them weighs on colonists", ref Settings.cullGuiltEnabled,
                    "A small, stacking mood memory for anyone who watched. Vanilla already charges for bonded animals; this is the charge for the rest of the swarm, and it is what keeps the humane exits competitive with the knife.");
            }
            else
            {
                GUI.color = new Color(0.6f, 0.6f, 0.6f);
                l.Label("  (disabled — stowaway events are off)");
                GUI.color = Color.white;
            }

            l.Gap(6f);
            l.GapLine();
            l.Label("The creature itself");
            GUI.color = new Color(0.7f, 0.7f, 0.7f);
            l.Label("Gizka breed fast everywhere in the world — wild, bought or traded — not only the stowaway lineage. This scales that, and it applies even with the stowaway events switched off.");
            GUI.color = Color.white;
            l.Label("Global gizka breeding rate: " + Settings.globalBreedingRate.ToString("0.00") + "x");
            Settings.globalBreedingRate = l.Slider(Settings.globalBreedingRate, 0.1f, 3f);
            if (l.ButtonText("Apply creature breeding rate now"))
            {
                RSW_GizkaDonorTuning.Apply();
            }

            l.End();
            Widgets.EndScrollView();
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

            float mult = RSW_GizkaStowawayMod.Settings?.globalBreedingRate ?? 1f;
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
