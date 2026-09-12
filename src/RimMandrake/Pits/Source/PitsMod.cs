using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Pits
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Pits (covered_pit_traps_spec.md).
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields read
    // from everywhere, Scribe_Values in ExposeData, a DoWindowContents helper
    // called from the Mod subclass).
    //
    // Every default here is the CURRENT SHIPPED value already hardcoded
    // elsewhere in this mod (Building_OpenPit.FallDamagePerMassKg,
    // PitEscapeUtility.StruggleIntervalTicks/EscapeChance,
    // PitDepthTierExtensions.WorkPerAdditionalStage, Building_PitCell's
    // ApplyExposure rates) — turning every toggle on and every slider to 1x
    // reproduces exactly what the mod did before this file existed.
    //
    // Nothing here touches worldgen: every mechanic gated below is live-play
    // (a tick, a struggle roll, a dig job), so no "affects new maps only"
    // labeling is needed anywhere on this screen.
    // ════════════════════════════════════════════════════════════════════
    public class PitsSettings : ModSettings
    {
        // --- Covered pit trap trigger (CompPitCoverTrigger / Building_OpenPit.Spring) ---
        public static bool trapTriggerEnabled = true;
        public static float trapSensitivityMultiplier = 1f;

        // --- Fall damage on capture (Building_OpenPit.Spring) ---
        public static bool fallDamageEnabled = true;
        public static float fallDamageMultiplier = 1f;

        // --- Struggle clock (Building_OpenPit.Tick / RunStruggleInterval) ---
        public static float struggleIntervalHours = 1f; // was the const StruggleIntervalTicks = 2500 (= 1 hour)
        public static bool escapeEnabled = true;
        public static float escapeChanceMultiplier = 1f;

        // --- Dig-deeper pacing (PitDepthTierExtensions.WorkPerAdditionalStage) ---
        public static float digWorkMultiplier = 1f;

        // --- Pit Cell exposure (Building_PitCell.ApplyExposure) ---
        public static bool pitCellExposureEnabled = true;
        public static float pitCellExposureMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref trapTriggerEnabled, "trapTriggerEnabled", true);
            Scribe_Values.Look(ref trapSensitivityMultiplier, "trapSensitivityMultiplier", 1f);
            Scribe_Values.Look(ref fallDamageEnabled, "fallDamageEnabled", true);
            Scribe_Values.Look(ref fallDamageMultiplier, "fallDamageMultiplier", 1f);
            Scribe_Values.Look(ref struggleIntervalHours, "struggleIntervalHours", 1f);
            Scribe_Values.Look(ref escapeEnabled, "escapeEnabled", true);
            Scribe_Values.Look(ref escapeChanceMultiplier, "escapeChanceMultiplier", 1f);
            Scribe_Values.Look(ref digWorkMultiplier, "digWorkMultiplier", 1f);
            Scribe_Values.Look(ref pitCellExposureEnabled, "pitCellExposureEnabled", true);
            Scribe_Values.Look(ref pitCellExposureMultiplier, "pitCellExposureMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Covered pit trap trigger");
            list.CheckboxLabeled("Cover springs when enough mass crosses it", ref trapTriggerEnabled,
                "Off: an armed cover never springs on its own. Arming/disarming and the pit "
              + "itself still work — nothing ever falls in on its own while this is off.");
            if (trapTriggerEnabled)
            {
                list.Label("Trigger sensitivity: " + trapSensitivityMultiplier.ToString("0.00")
                    + "x (multiplies each cover tier's weight rating)");
                trapSensitivityMultiplier = list.Slider(trapSensitivityMultiplier, 0.25f, 3f);
            }
            list.GapLine();

            list.Label("Fall damage");
            list.CheckboxLabeled("Falling into a pit deals damage", ref fallDamageEnabled,
                "Off: a captured pawn is still pinned and held, just unhurt by the fall itself.");
            if (fallDamageEnabled)
            {
                list.Label("Fall damage multiplier: " + fallDamageMultiplier.ToString("0.00") + "x");
                fallDamageMultiplier = list.Slider(fallDamageMultiplier, 0f, 3f);
            }
            list.GapLine();

            list.Label("Held pawns / struggle clock");
            list.Label("Struggle check interval: " + struggleIntervalHours.ToString("0.00")
                + " in-game hours (also paces poison/drowning buildup for held pawns)");
            struggleIntervalHours = list.Slider(struggleIntervalHours, 0.25f, 4f);
            list.CheckboxLabeled("Held pawns can attempt to escape", ref escapeEnabled,
                "Off: occupants stay pinned until you release them — no escape rolls, but "
              + "floor-fitting effects (poison, drowning) still run on schedule.");
            if (escapeEnabled)
            {
                list.Label("Escape chance multiplier: " + escapeChanceMultiplier.ToString("0.00") + "x");
                escapeChanceMultiplier = list.Slider(escapeChanceMultiplier, 0.25f, 3f);
            }
            list.GapLine();

            list.Label("Digging deeper");
            list.Label("Dig-deeper work multiplier: " + digWorkMultiplier.ToString("0.00")
                + "x (Deep/Chasm dig sites only — a Shallow site is done at placement)");
            digWorkMultiplier = list.Slider(digWorkMultiplier, 0.25f, 3f);
            list.GapLine();

            list.Label("Pit Cell (gated prisoner holding)");
            list.CheckboxLabeled("Captives accrue exposure", ref pitCellExposureEnabled,
                "Off: an assigned captive's condition never drifts from the gate being open "
              + "or closed — feeding and assignment still work.");
            if (pitCellExposureEnabled)
            {
                list.Label("Exposure rate multiplier: " + pitCellExposureMultiplier.ToString("0.00") + "x");
                pitCellExposureMultiplier = list.Slider(pitCellExposureMultiplier, 0.25f, 3f);
            }

            list.End();
        }
    }

    public class PitsMod : Mod
    {
        public static PitsSettings settings;

        public PitsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<PitsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Pits";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
