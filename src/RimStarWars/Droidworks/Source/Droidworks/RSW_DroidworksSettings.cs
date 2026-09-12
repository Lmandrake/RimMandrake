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

        private Vector2 scrollPosition;
        private float lastContentHeight = 2000f;

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

        public static void ResetToDefaults()
        {
            boltSuppressesMentalBreaks = true;
            boltResentment = true;
            boltResentmentRate = 1f;
            boltShear = true;
            boltShearChance = 1f;
            boltRebellion = true;
            boltRebellionThreshold = 0.6f;
            boltMoodPenalty = true;
            boltMoodRadius = 12f;

            powerNeed = true;
            powerDrainRate = 1f;
            chargeRate = 1f;
            powerDownWhenEmpty = true;

            ionShutdown = true;
            ionShutdownThreshold = 0.5f;

            detonation = true;
            detonationSize = 1f;

            wipeStumble = true;
            wipeStumbleChance = 1f;
            wipeQuirks = true;
            wipeQuirkChance = 0.6f;

            wildDroidCrash = true;

            headDrop = true;
            partDrop = true;
            partDropChance = 0.6f;

            personalityDrift = true;
            driftTime = 1f;

            protocolTrade = true;
            protocolTradePerSide = 0.06f;

            huttCaptivesBolted = true;
        }

        public void DoWindowContents(Rect inRect)
        {
            Rect viewRect = new Rect(0f, 0f, inRect.width - 24f, lastContentHeight);
            Widgets.BeginScrollView(inRect, ref scrollPosition, viewRect);

            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width };
            list.Begin(viewRect);

            // ── Restraining bolts ──────────────────────────────────────────
            Header(list, "Restraining bolts");
            list.CheckboxLabeled("Bolts stop a droid breaking down", ref boltSuppressesMentalBreaks,
                "A droid wearing a restraining bolt never has a mental break. "
              + "Off: a bolted droid breaks down like anyone else.");
            list.CheckboxLabeled("Bolted droids build up resentment", ref boltResentment,
                "A thinking droid quietly resents the bolt for as long as it wears one, and never "
              + "forgets once the bolt comes off. Off: no resentment is ever recorded.");
            if (boltResentment)
            {
                list.Label("   How fast resentment builds: " + Multiplier(boltResentmentRate));
                boltResentmentRate = list.Slider(boltResentmentRate, 0.25f, 3f);
            }
            list.Gap();
            list.CheckboxLabeled("Bolts can be knocked off in a fight", ref boltShear,
                "A hit landing on a bolted droid can snap the bolt clean off. "
              + "Off: a bolt only ever comes off deliberately, at a bench.");
            if (boltShear)
            {
                list.Label("   How easily a bolt snaps off: " + Multiplier(boltShearChance));
                boltShearChance = list.Slider(boltShearChance, 0.25f, 3f);
            }
            list.Gap();
            list.CheckboxLabeled("A freed droid can turn on you", ref boltRebellion,
                "Take the bolt off a droid that has resented it long enough and it goes berserk. "
              + "Off: removing a bolt is always safe.");
            if (boltRebellion)
            {
                list.Label("   Resentment needed before it turns: "
                    + boltRebellionThreshold.ToStringPercent("0") + " (default 60%)");
                boltRebellionThreshold = list.Slider(boltRebellionThreshold, 0.1f, 1f);
            }
            list.Gap();
            list.CheckboxLabeled("People are unsettled by bolted droids nearby", ref boltMoodPenalty,
                "A mood penalty for anyone standing near a droid in a restraining bolt. "
              + "Off: nobody minds.");
            if (boltMoodPenalty)
            {
                list.Label("   How far that carries: " + boltMoodRadius.ToString("0") + " tiles (default 12)");
                boltMoodRadius = list.Slider(boltMoodRadius, 2f, 30f);
            }
            list.GapLine();

            // ── Power and charging ─────────────────────────────────────────
            Header(list, "Power and charging");
            list.CheckboxLabeled("Droids run on stored power", ref powerNeed,
                "Droids carry a power bar that drains and has to be topped up at a charger. "
              + "Off: droids never need charging at all, and the power bar disappears.");
            if (powerNeed)
            {
                list.Label("   How fast power drains: " + Multiplier(powerDrainRate));
                powerDrainRate = list.Slider(powerDrainRate, 0.25f, 3f);
                list.Label("   How fast chargers refill it: " + Multiplier(chargeRate));
                chargeRate = list.Slider(chargeRate, 0.25f, 3f);
                list.CheckboxLabeled("   A flat droid shuts down", ref powerDownWhenEmpty,
                    "Run the bar to empty and the droid powers down until somebody reboots it. "
                  + "Off: an empty droid just keeps going on fumes.");
            }
            list.GapLine();

            // ── Ion ────────────────────────────────────────────────────────
            Header(list, "Ion hits shut a droid down");
            list.CheckboxLabeled("Ion damage powers a droid down for good", ref ionShutdown,
                "Enough ion damage and the droid does not wobble back up - it stays off until "
              + "somebody reboots it. Off: ion just stuns, and the droid recovers by itself.");
            if (ionShutdown)
            {
                list.Label("   Ion charge needed to shut it down: "
                    + ionShutdownThreshold.ToStringPercent("0") + " (default 50%)");
                ionShutdownThreshold = list.Slider(ionShutdownThreshold, 0.1f, 1f);
            }
            list.GapLine();

            // ── Detonation ─────────────────────────────────────────────────
            Header(list, "Droids blow up when destroyed");
            list.CheckboxLabeled("Destroyed droids can detonate", ref detonation,
                "A droid killed with charge still in it goes up. A drained wreck never does. "
              + "Off: droids never explode.");
            if (detonation)
            {
                list.Label("   Size of the blast: " + Multiplier(detonationSize));
                detonationSize = list.Slider(detonationSize, 0.25f, 3f);
            }
            list.GapLine();

            // ── Memory wipe ────────────────────────────────────────────────
            Header(list, "After a memory wipe");
            list.CheckboxLabeled("A wiped droid blunders about for a week", ref wipeStumble,
                "It drops what it was doing and wanders off mid-job while it relearns its body. "
              + "Off: a wiped droid works normally straight away.");
            if (wipeStumble)
            {
                list.Label("   How often it loses the thread: " + Multiplier(wipeStumbleChance));
                wipeStumbleChance = list.Slider(wipeStumbleChance, 0.25f, 3f);
            }
            list.Gap();
            list.CheckboxLabeled("Wipes leave permanent damage", ref wipeQuirks,
                "Each wipe can leave a hardware quirk that never goes away and stacks with the last. "
              + "Off: a wipe costs nothing lasting.");
            if (wipeQuirks)
            {
                list.Label("   Chance a wipe leaves one: "
                    + wipeQuirkChance.ToStringPercent("0") + " (default 60%)");
                wipeQuirkChance = list.Slider(wipeQuirkChance, 0f, 1f);
            }
            list.GapLine();

            // ── Wild droids ────────────────────────────────────────────────
            Header(list, "Wild droids");
            list.CheckboxLabeled("Crashed droids wander in off the desert", ref wildDroidCrash,
                "An ownerless droid that has been out there too long walks onto the map and attacks "
              + "anything it sees - down it, take it prisoner, and a wild-keyed spike can claim it. "
              + "Off: the event never fires.");
            list.GapLine();

            // ── Salvage ────────────────────────────────────────────────────
            Header(list, "Salvage from a dead droid");
            list.CheckboxLabeled("Droids drop their head", ref headDrop,
                "A destroyed droid leaves its head, carrying who it was. "
              + "Off: no heads drop.");
            list.CheckboxLabeled("Droids drop spare parts", ref partDrop,
                "Legs, manipulators, sensors and the rest, rolled one at a time. "
              + "Off: no parts drop.");
            if (partDrop)
            {
                list.Label("   Chance for each part: "
                    + partDropChance.ToStringPercent("0") + " (default 60%)");
                partDropChance = list.Slider(partDropChance, 0f, 1f);
            }
            list.GapLine();

            // ── Drift ──────────────────────────────────────────────────────
            Header(list, "Droids become people");
            list.CheckboxLabeled("Long-unwiped droids grow a personality", ref personalityDrift,
                "A droid left unwiped for years picks up habits of its own, and the first one wakes "
              + "a programmable droid into a thinking one. A wipe takes it all back. "
              + "Off: a droid is the same droid forever.");
            if (personalityDrift)
            {
                list.Label("   How long that takes: " + Multiplier(driftTime)
                    + " (default: first habit at 2 years)");
                driftTime = list.Slider(driftTime, 0.25f, 3f);
            }
            list.GapLine();

            // ── Trade ──────────────────────────────────────────────────────
            Header(list, "Protocol droids and trade");
            list.CheckboxLabeled("Protocol droids shift trade prices", ref protocolTrade,
                "Bring one and prices move your way; turn up without one against a trader who has "
              + "one and they move against you. Off: prices are whatever they would normally be.");
            if (protocolTrade)
            {
                list.Label("   Price shift per side: "
                    + protocolTradePerSide.ToStringPercent("0.0") + " (default 6%)");
                protocolTradePerSide = list.Slider(protocolTradePerSide, 0f, 0.25f);
            }
            list.GapLine();

            // ── Hutt captives ──────────────────────────────────────────────
            Header(list, "Hutt captives");
            list.CheckboxLabeled("Hutt debtor droids arrive already bolted", ref huttCaptivesBolted,
                "Droids bought off a Hutt trader come wearing a restraining bolt and carrying however "
              + "much resentment their time in hock earned. Off: they are sold like ordinary stock.");
            list.GapLine();

            if (list.ButtonText("Reset everything to defaults"))
            {
                ResetToDefaults();
            }

            lastContentHeight = list.CurHeight + 24f;
            list.End();
            Widgets.EndScrollView();
        }

        private static void Header(Listing_Standard list, string text)
        {
            Text.Font = GameFont.Medium;
            list.Label(text);
            Text.Font = GameFont.Small;
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
