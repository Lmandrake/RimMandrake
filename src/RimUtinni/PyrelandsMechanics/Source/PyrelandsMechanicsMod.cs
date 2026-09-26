using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// MOD_OPTIONS_RETROFIT_1 — Mod Settings for the campaign-specific remainder
    /// of the Pyrelands igniter kit, after PYRELANDS_RM_MOD_BUILD_1 §6 absorbed
    /// the franchise-free two-thirds (the burn-line, the fire clock, the
    /// fire-hawk and the furnace-beast's thermal circuit) into
    /// mandrake.rm.pyrelands's own RM_PyrelandsSettings.
    ///
    /// What is left here names the Deep Desert Tribes — a campaign faction —
    /// and cannot move to the franchise-free tier: arson-justice, the flame
    /// harvest, and the fire rite.
    /// </summary>
    public class PyrelandsMechanicsSettings : ModSettings
    {
        // ---- Master switches, one per mechanism -----------------------------
        public static bool arsonJusticeEnabled = true;
        public static bool flameHarvestEnabled = true;

        // DEEP_TRIBES_FIRE_RITE_1. Off means the fire clock lights every front
        // itself, exactly as it did before this mechanism existed — which is what
        // "all-off degrades gracefully" means here.
        public static bool fireRiteEnabled = true;

        // ---- Tunables ---------------------------------------------------------
        public static float arsonDebtRaidThreshold = RimMandrake.Pyrelands.PyrelandsTuning.ArsonDebtRaidThreshold;
        public static int flameHarvestMinFires = RimMandrake.Pyrelands.PyrelandsTuning.FlameHarvestMinFires;
        public static float fireRiteFraction = RimMandrake.Pyrelands.PyrelandsTuning.FireRiteFraction;
        public static int fireRiteGroupMin = RimMandrake.Pyrelands.PyrelandsTuning.FireRiteGroupMin;
        public static int fireRiteGroupMax = RimMandrake.Pyrelands.PyrelandsTuning.FireRiteGroupMax;
        public static float fireRiteHarvestHours = RimMandrake.Pyrelands.PyrelandsTuning.FireRiteHarvestHours;
        public static int fireRiteCarryPerPawn = RimMandrake.Pyrelands.PyrelandsTuning.FireRiteCarryPerPawn;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref arsonJusticeEnabled, "arsonJusticeEnabled", true);
            Scribe_Values.Look(ref flameHarvestEnabled, "flameHarvestEnabled", true);
            Scribe_Values.Look(ref fireRiteEnabled, "fireRiteEnabled", true);

            Scribe_Values.Look(ref fireRiteFraction, "fireRiteFraction", RimMandrake.Pyrelands.PyrelandsTuning.FireRiteFraction);
            Scribe_Values.Look(ref fireRiteGroupMin, "fireRiteGroupMin", RimMandrake.Pyrelands.PyrelandsTuning.FireRiteGroupMin);
            Scribe_Values.Look(ref fireRiteGroupMax, "fireRiteGroupMax", RimMandrake.Pyrelands.PyrelandsTuning.FireRiteGroupMax);
            Scribe_Values.Look(ref fireRiteHarvestHours, "fireRiteHarvestHours", RimMandrake.Pyrelands.PyrelandsTuning.FireRiteHarvestHours);
            Scribe_Values.Look(ref fireRiteCarryPerPawn, "fireRiteCarryPerPawn", RimMandrake.Pyrelands.PyrelandsTuning.FireRiteCarryPerPawn);

            Scribe_Values.Look(ref arsonDebtRaidThreshold, "arsonDebtRaidThreshold", RimMandrake.Pyrelands.PyrelandsTuning.ArsonDebtRaidThreshold);
            Scribe_Values.Look(ref flameHarvestMinFires, "flameHarvestMinFires", RimMandrake.Pyrelands.PyrelandsTuning.FlameHarvestMinFires);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("The Tribes answer the burn");
            list.CheckboxLabeled("Arson-justice raids", ref arsonJusticeEnabled,
                "Off: the Tribes never raid over an unplanned burn, however much arson "
              + "debt the colony racks up.");
            list.Label("Arson debt before a raid: " + arsonDebtRaidThreshold.ToString("0"));
            arsonDebtRaidThreshold = list.Slider(arsonDebtRaidThreshold, 100f, 2000f);
            list.Gap();
            list.CheckboxLabeled("Flame-harvest visits", ref flameHarvestEnabled,
                "Off: the Tribes never send a peaceful party to walk a live burn-line.");
            list.Label("Minimum standing fires to draw a visit: " + flameHarvestMinFires);
            flameHarvestMinFires = Mathf.RoundToInt(list.Slider(flameHarvestMinFires, 1f, 50f));
            list.GapLine();

            list.Label("The Deep Tribes' fire rite");
            list.CheckboxLabeled("The Tribes sometimes light the burn themselves", ref fireRiteEnabled,
                "On (shipped): some of the fire clock's burns arrive as a rite — a small Deep "
              + "Tribes party walks onto the map, torches the grass where they stand, works the "
              + "burn for scorch-fruit and leaves with it. Off: the clock lights every front "
              + "itself and the Tribes never come for it. Either way the burn happens on "
              + "schedule (mandrake.rm.pyrelands' own fire clock); this only changes whose hand "
              + "is on it.");
            list.Label("Rites instead of plain fronts: " + (fireRiteFraction * 100f).ToString("0") + "%");
            fireRiteFraction = list.Slider(fireRiteFraction, 0f, 1f);
            list.Label("Party size: " + fireRiteGroupMin + " to " + fireRiteGroupMax);
            fireRiteGroupMin = Mathf.RoundToInt(list.Slider(fireRiteGroupMin, 1f, 12f));
            fireRiteGroupMax = Mathf.RoundToInt(list.Slider(fireRiteGroupMax, 1f, 12f));
            if (fireRiteGroupMax < fireRiteGroupMin)
            {
                fireRiteGroupMax = fireRiteGroupMin;
            }
            list.Label("They work the burn for " + fireRiteHarvestHours.ToString("0.0") + " in-game hours");
            fireRiteHarvestHours = list.Slider(fireRiteHarvestHours, 1f, 24f);
            // The number that is the experience. A party of 3-5 at the shipped 25
            // walks off with 75-125 scorch fruit a rite, every 6-12 days - they are
            // a competing harvester on the player's own resource, not set dressing.
            // (PYRELANDS_FIRE_RITE_TAKE_TUNING_1). 0 is a lawful setting: they still
            // come, still light it, and take nothing.
            list.Label("Each harvester carries off " + fireRiteCarryPerPawn + " scorch fruit ("
                     + (fireRiteCarryPerPawn * fireRiteGroupMin) + "-"
                     + (fireRiteCarryPerPawn * fireRiteGroupMax) + " a rite)");
            fireRiteCarryPerPawn = Mathf.RoundToInt(list.Slider(fireRiteCarryPerPawn, 0f, 100f));

            list.End();
        }
    }

    public class PyrelandsMechanicsMod : Mod
    {
        public static PyrelandsMechanicsSettings settings;

        public PyrelandsMechanicsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<PyrelandsMechanicsSettings>();

            // PYRELANDS_RM_MOD_BUILD_1 §6 — fill in RM_Pyrelands' fire-rite hook
            // so its franchise-free fire clock can offer this mod's Deep Tribes
            // rite a chance to intercept a scheduled front. Left null (never
            // set) on a franchise-free world where this mod is not loaded at
            // all — that is the "all-off degrades to the plain front" case.
            RimMandrake.Pyrelands.PyrelandsFireRiteHook.TrySend = PyrelandsFireRite.TrySend;
        }

        public override string SettingsCategory()
        {
            return "Pyrelands Mechanics";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
