using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// MOD_OPTIONS_RETROFIT_1 — Mod Settings for the Pyrelands igniter kit.
    ///
    /// House style: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs.
    ///
    /// Six live mechanisms (see About.xml's own numbered list), each gated by its
    /// own on/off switch below, plus sliders for the real numbers a player would
    /// actually want to retune. Defaults are copied straight from PyrelandsTuning's
    /// shipped consts, so nothing about day-one behavior changes.
    ///
    /// NOT worldgen-affecting: every mechanism here is a live MapComponent tick,
    /// ThingComp, JobGiver or IncidentWorker gate. Nothing here runs at map
    /// generation time.
    /// </summary>
    public class PyrelandsMechanicsSettings : ModSettings
    {
        // ---- Master switches, one per mechanism -----------------------------
        public static bool standingBurnReseedEnabled = true;
        public static bool fireHawkSpreadEnabled = true;
        public static bool furnaceWarmthAuraEnabled = true;
        public static bool furnaceBedIgnitionEnabled = true;
        public static bool arsonJusticeEnabled = true;
        public static bool flameHarvestEnabled = true;

        // PYRELANDS_FIRE_CADENCE_1
        public static bool fireFrontEnabled = true;
        public static bool fireFrontLetterEnabled = true;

        // DEEP_TRIBES_FIRE_RITE_1. Off means the fire clock lights every front
        // itself, exactly as it did before this mechanism existed — which is what
        // "all-off degrades gracefully" means here.
        public static bool fireRiteEnabled = true;

        // FURNACEBEAST_THERMAL_CYCLE_1
        public static bool furnaceHeatImmunityEnabled = true;
        public static bool furnaceThermalChargeEnabled = true;
        public static bool furnaceFireSeekingEnabled = true;
        public static bool furnaceThornvineDietEnabled = true;

        // ---- Tunables ---------------------------------------------------------
        public static float furnaceBedIgnitionChance = PyrelandsTuning.FurnaceBedIgnitionChance;
        public static int fireHawkCooldownTicks = PyrelandsTuning.FireHawkCooldownTicks;
        public static float arsonDebtRaidThreshold = PyrelandsTuning.ArsonDebtRaidThreshold;
        public static int flameHarvestMinFires = PyrelandsTuning.FlameHarvestMinFires;
        public static float furnaceAuraRadius = PyrelandsTuning.FurnaceAuraRadius;
        public static float fireFrontMinDays = PyrelandsTuning.FireFrontMinDays;
        public static float fireFrontMaxDays = PyrelandsTuning.FireFrontMaxDays;
        public static int fireFrontWidthCells = PyrelandsTuning.FireFrontWidthCells;
        public static float fireRiteFraction = PyrelandsTuning.FireRiteFraction;
        public static int fireRiteGroupMin = PyrelandsTuning.FireRiteGroupMin;
        public static int fireRiteGroupMax = PyrelandsTuning.FireRiteGroupMax;
        public static float fireRiteHarvestHours = PyrelandsTuning.FireRiteHarvestHours;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref standingBurnReseedEnabled, "standingBurnReseedEnabled", true);
            Scribe_Values.Look(ref fireHawkSpreadEnabled, "fireHawkSpreadEnabled", true);
            Scribe_Values.Look(ref furnaceWarmthAuraEnabled, "furnaceWarmthAuraEnabled", true);
            Scribe_Values.Look(ref furnaceBedIgnitionEnabled, "furnaceBedIgnitionEnabled", true);
            Scribe_Values.Look(ref arsonJusticeEnabled, "arsonJusticeEnabled", true);
            Scribe_Values.Look(ref flameHarvestEnabled, "flameHarvestEnabled", true);
            Scribe_Values.Look(ref fireFrontEnabled, "fireFrontEnabled", true);
            Scribe_Values.Look(ref fireFrontLetterEnabled, "fireFrontLetterEnabled", true);
            Scribe_Values.Look(ref furnaceHeatImmunityEnabled, "furnaceHeatImmunityEnabled", true);
            Scribe_Values.Look(ref furnaceThermalChargeEnabled, "furnaceThermalChargeEnabled", true);
            Scribe_Values.Look(ref furnaceFireSeekingEnabled, "furnaceFireSeekingEnabled", true);
            Scribe_Values.Look(ref furnaceThornvineDietEnabled, "furnaceThornvineDietEnabled", true);

            Scribe_Values.Look(ref fireFrontMinDays, "fireFrontMinDays", PyrelandsTuning.FireFrontMinDays);
            Scribe_Values.Look(ref fireFrontMaxDays, "fireFrontMaxDays", PyrelandsTuning.FireFrontMaxDays);
            Scribe_Values.Look(ref fireFrontWidthCells, "fireFrontWidthCells", PyrelandsTuning.FireFrontWidthCells);

            Scribe_Values.Look(ref fireRiteEnabled, "fireRiteEnabled", true);
            Scribe_Values.Look(ref fireRiteFraction, "fireRiteFraction", PyrelandsTuning.FireRiteFraction);
            Scribe_Values.Look(ref fireRiteGroupMin, "fireRiteGroupMin", PyrelandsTuning.FireRiteGroupMin);
            Scribe_Values.Look(ref fireRiteGroupMax, "fireRiteGroupMax", PyrelandsTuning.FireRiteGroupMax);
            Scribe_Values.Look(ref fireRiteHarvestHours, "fireRiteHarvestHours", PyrelandsTuning.FireRiteHarvestHours);

            Scribe_Values.Look(ref furnaceBedIgnitionChance, "furnaceBedIgnitionChance", PyrelandsTuning.FurnaceBedIgnitionChance);
            Scribe_Values.Look(ref fireHawkCooldownTicks, "fireHawkCooldownTicks", PyrelandsTuning.FireHawkCooldownTicks);
            Scribe_Values.Look(ref arsonDebtRaidThreshold, "arsonDebtRaidThreshold", PyrelandsTuning.ArsonDebtRaidThreshold);
            Scribe_Values.Look(ref flameHarvestMinFires, "flameHarvestMinFires", PyrelandsTuning.FlameHarvestMinFires);
            Scribe_Values.Look(ref furnaceAuraRadius, "furnaceAuraRadius", PyrelandsTuning.FurnaceAuraRadius);
        }

        public void DoWindowContents(Rect inRect)
        {
            // Three columns: the kit grew past one screen when the fire clock and
            // the furnace-beast's capacitor landed, and past two when the Deep
            // Tribes' fire rite did.
            Listing_Standard list = new Listing_Standard { ColumnWidth = (inRect.width - 51f) / 3f };
            list.Begin(inRect);

            list.Label("The standing burn");
            list.CheckboxLabeled("The biome re-seeds its own burn", ref standingBurnReseedEnabled,
                "Off: if every fire on a Pyrelands map goes out, it stays out — the biome "
              + "no longer lights a fresh smoulder after two quiet days.");
            list.Gap();
            list.CheckboxLabeled("The biome's fire clock", ref fireFrontEnabled,
                "On (shipped): a line of grass goes up every few days on a Pyrelands map, "
              + "whatever else is burning. Off: fires only ever arrive from lightning, "
              + "animals and the re-seed above — which makes a burn a rare event rather "
              + "than the biome's weather.");
            list.Label("A front every " + fireFrontMinDays.ToString("0.0")
                     + " to " + fireFrontMaxDays.ToString("0.0") + " days");
            fireFrontMinDays = list.Slider(fireFrontMinDays, 0.5f, 15f);
            fireFrontMaxDays = list.Slider(fireFrontMaxDays, 0.5f, 30f);
            if (fireFrontMaxDays < fireFrontMinDays)
            {
                fireFrontMaxDays = fireFrontMinDays;
            }
            list.Label("Front width: " + fireFrontWidthCells + " cells");
            fireFrontWidthCells = Mathf.RoundToInt(list.Slider(fireFrontWidthCells, 1f, 31f));
            list.Gap();
            list.CheckboxLabeled("Announce each front with a letter", ref fireFrontLetterEnabled,
                "Off: the fire clock still runs, silently. The re-seed above is never "
              + "announced either way.");
            list.GapLine();

            list.Label("The fire-hawk's twig");
            list.CheckboxLabeled("Fire-hawks carry embers", ref fireHawkSpreadEnabled,
                "Off: fire-hawks never spread fire from an existing burn (they still can't "
              + "start one from nothing either way).");
            list.Label("Cooldown between sorties: " + (fireHawkCooldownTicks / 2500f).ToString("0.0") + " in-game hours");
            fireHawkCooldownTicks = Mathf.RoundToInt(list.Slider(fireHawkCooldownTicks / 2500f, 0.5f, 24f) * 2500f);
            list.GapLine();

            list.NewColumn();

            list.Label("The furnace-beast's thermal circuit");
            list.CheckboxLabeled("Total fire and heat immunity", ref furnaceHeatImmunityEnabled,
                "On (shipped): a furnace-beast takes zero damage from every heat-category "
              + "attack — flame, burn, incendiary, plasma. Off: it falls back to its very "
              + "high XML heat armour, which is a good roll rather than a guarantee. It "
              + "cannot catch fire either way (its flammability is zero).");
            list.Gap();
            list.CheckboxLabeled("Heat charge and bleed", ref furnaceThermalChargeEnabled,
                "On (shipped): the beast banks heat in hot air and near fire, and bleeds it "
              + "back out in the cold, pushing warmth around itself in proportion to what it "
              + "is carrying. Off: no capacitor, no charge readout, and no radiant push — "
              + "its flat heat-pusher and the aura below are unaffected.");
            list.Gap();
            list.CheckboxLabeled("Walks into the burn to charge", ref furnaceFireSeekingEnabled,
                "On (shipped): an under-charged beast walks toward a burn on its map, and a "
              + "full one steps back off it. Off: it ignores fire entirely.");
            list.Gap();
            list.CheckboxLabeled("Eats thornvine", ref furnaceThornvineDietEnabled,
                "On (shipped): a hungry furnace-beast will strip a thornvine patch — it is "
              + "one of the only things that will. Off: thornvine is left alone by everything "
              + "again.");
            list.Gap();
            list.CheckboxLabeled("Open-field warmth aura", ref furnaceWarmthAuraEnabled,
                "Off: standing near a furnace-beast in the open no longer widens cold "
              + "tolerance or narrows heat tolerance. The beast's enclosed-space heat "
              + "pusher (a vanilla comp) is unaffected either way.");
            list.Label("Aura radius: " + furnaceAuraRadius.ToString("0.0") + " cells");
            furnaceAuraRadius = list.Slider(furnaceAuraRadius, 1f, 15f);
            list.Gap();
            list.CheckboxLabeled("Bed-down ignition", ref furnaceBedIgnitionEnabled,
                "Off: a furnace-beast never smoulders the ground it slept on, tamed or wild.");
            list.Label("Chance per real rest: " + (furnaceBedIgnitionChance * 100f).ToString("0") + "%");
            furnaceBedIgnitionChance = list.Slider(furnaceBedIgnitionChance, 0f, 1f);
            list.NewColumn();

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
              + "schedule; this only changes whose hand is on it.");
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

            list.End();
        }
    }

    public class PyrelandsMechanicsMod : Mod
    {
        public static PyrelandsMechanicsSettings settings;

        public PyrelandsMechanicsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<PyrelandsMechanicsSettings>();
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
