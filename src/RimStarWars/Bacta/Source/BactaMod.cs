using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Bacta
{
    /// <summary>
    /// Mod Settings per the standing rule (owner, 2026-09-12): a toggle per major mechanic, a
    /// slider wherever a number IS the experience, defaults equal to shipped behavior, and
    /// all-off degrading gracefully.
    ///
    /// All-off here leaves a powered cylinder that holds one pawn and does nothing to them —
    /// still buildable, still placeable, still ejects on command. Nothing errors, nothing
    /// disappears from a save.
    ///
    /// None of these settings affect worldgen. The tank is a live building comp; there is no
    /// generation-time behavior to label.
    /// </summary>
    public class BactaSettings : ModSettings
    {
        // ---- Master switches, one per mechanic -------------------------------------------
        public static bool healingEnabled = true;
        public static bool scarErasureEnabled = true;
        public static bool infectionAssistEnabled = true;
        public static bool suspendNeedsEnabled = true;
        public static bool autoEjectEnabled = true;

        /// <summary>
        /// Reserved for BACTA_REVIVAL_MECHANIC_1. Shipped OFF and inert: no code reads it yet,
        /// and the toggle exists so a player's choice survives the update that lands it.
        /// </summary>
        public static bool revivalEnabled = false;

        // ---- Tunables --------------------------------------------------------------------
        public static float woundHealPerDay = BactaTuning.WoundHealPerDay;
        public static float scarHealPerDay = BactaTuning.ScarHealPerDay;
        public static float immunityGainPerDay = BactaTuning.ImmunityGainPerDay;
        public static float fluidCostPerDay = BactaTuning.FluidCostPerDay;
        public static float tendQuality = BactaTuning.TendQuality;

        private Vector2 scrollPosition = Vector2.zero;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref healingEnabled, "healingEnabled", true);
            Scribe_Values.Look(ref scarErasureEnabled, "scarErasureEnabled", true);
            Scribe_Values.Look(ref infectionAssistEnabled, "infectionAssistEnabled", true);
            Scribe_Values.Look(ref suspendNeedsEnabled, "suspendNeedsEnabled", true);
            Scribe_Values.Look(ref autoEjectEnabled, "autoEjectEnabled", true);
            Scribe_Values.Look(ref revivalEnabled, "revivalEnabled", defaultValue: false);

            Scribe_Values.Look(ref woundHealPerDay, "woundHealPerDay", BactaTuning.WoundHealPerDay);
            Scribe_Values.Look(ref scarHealPerDay, "scarHealPerDay", BactaTuning.ScarHealPerDay);
            Scribe_Values.Look(ref immunityGainPerDay, "immunityGainPerDay", BactaTuning.ImmunityGainPerDay);
            Scribe_Values.Look(ref fluidCostPerDay, "fluidCostPerDay", BactaTuning.FluidCostPerDay);
            Scribe_Values.Look(ref tendQuality, "tendQuality", BactaTuning.TendQuality);
        }

        public void DoWindowContents(Rect inRect)
        {
            Rect viewRect = new Rect(0f, 0f, inRect.width - 20f, 780f);
            Widgets.BeginScrollView(inRect, ref scrollPosition, viewRect);

            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width };
            list.Begin(viewRect);

            list.Label("The fluid's work");
            list.CheckboxLabeled("Accelerated healing", ref healingEnabled,
                "Off: a bacta tank becomes a powered cylinder that holds one pawn and heals "
              + "nothing. It still builds, still takes an occupant, and still ejects on command.");
            if (healingEnabled)
            {
                list.Label("Wound healing: " + woundHealPerDay.ToString("0") + " severity per day per injury"
                    + "   (shipped: " + BactaTuning.WoundHealPerDay.ToString("0") + ")");
                woundHealPerDay = Mathf.Round(list.Slider(woundHealPerDay, 2f, 120f));

                list.Label("Wound tending quality applied on immersion: " + tendQuality.ToString("0.00"));
                tendQuality = list.Slider(tendQuality, 0f, 1f);
            }
            list.GapLine();

            list.Label("Scars and permanent injuries");
            list.CheckboxLabeled("Erase scars and permanent physical injuries", ref scarErasureEnabled,
                "Off: bacta closes fresh wounds but never fades an old scar or a permanent "
              + "injury. Missing limbs and organs are never regrown either way — bacta heals, "
              + "it does not regenerate.");
            if (scarErasureEnabled)
            {
                list.Label("Scar erasure: " + scarHealPerDay.ToString("0.0") + " severity per day"
                    + "   (shipped: " + BactaTuning.ScarHealPerDay.ToString("0.0") + ")");
                scarHealPerDay = list.Slider(scarHealPerDay, 0.2f, 20f);
            }
            list.GapLine();

            list.Label("Infections");
            list.CheckboxLabeled("Help fight treatable infections", ref infectionAssistEnabled,
                "Off: bacta does nothing at all for disease. On, it only helps where medicine "
              + "could have helped — an untendable illness runs its course in the tank exactly "
              + "as it would in a bed.");
            if (infectionAssistEnabled)
            {
                list.Label("Extra immunity gained: " + immunityGainPerDay.ToString("0.00") + " per day"
                    + "   (shipped: " + BactaTuning.ImmunityGainPerDay.ToString("0.00") + ")");
                immunityGainPerDay = list.Slider(immunityGainPerDay, 0f, 1f);
            }
            list.GapLine();

            list.Label("Fluid cost");
            list.Label("Bacta consumed: " + fluidCostPerDay.ToString("0.0") + " per day while healing"
                + "   (shipped: " + BactaTuning.FluidCostPerDay.ToString("0.0") + ")");
            fluidCostPerDay = list.Slider(fluidCostPerDay, 0f, 40f);
            list.Gap();

            list.Label("The occupant");
            list.CheckboxLabeled("Suspend hunger and tiredness while immersed", ref suspendNeedsEnabled,
                "On (shipped): the tank feeds and rests its occupant, so a multi-day immersion "
              + "does not starve them. Off: hunger and tiredness run normally inside the tank, "
              + "and a long immersion needs watching.");
            list.CheckboxLabeled("Eject automatically", ref autoEjectEnabled,
                "On (shipped): the occupant is let out when there is nothing left to heal, or "
              + "when the tank runs dry. Off: they stay in until ejected by hand.");
            list.GapLine();

            list.Label("Not yet built");
            list.CheckboxLabeled("Revive the recently dead", ref revivalEnabled,
                "Reserved. Bacta revival is a separate piece of work and no code reads this "
              + "switch yet; it is here so the choice survives the update that adds it.");

            list.End();
            Widgets.EndScrollView();
        }
    }

    public class BactaMod : Mod
    {
        public static BactaSettings settings;

        public BactaMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<BactaSettings>();
        }

        public override string SettingsCategory()
        {
            return "RimStarWars — Bacta";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
