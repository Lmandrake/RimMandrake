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

        // ---- Tunables ---------------------------------------------------------
        public static float furnaceBedIgnitionChance = PyrelandsTuning.FurnaceBedIgnitionChance;
        public static int fireHawkCooldownTicks = PyrelandsTuning.FireHawkCooldownTicks;
        public static float arsonDebtRaidThreshold = PyrelandsTuning.ArsonDebtRaidThreshold;
        public static int flameHarvestMinFires = PyrelandsTuning.FlameHarvestMinFires;
        public static float furnaceAuraRadius = PyrelandsTuning.FurnaceAuraRadius;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref standingBurnReseedEnabled, "standingBurnReseedEnabled", true);
            Scribe_Values.Look(ref fireHawkSpreadEnabled, "fireHawkSpreadEnabled", true);
            Scribe_Values.Look(ref furnaceWarmthAuraEnabled, "furnaceWarmthAuraEnabled", true);
            Scribe_Values.Look(ref furnaceBedIgnitionEnabled, "furnaceBedIgnitionEnabled", true);
            Scribe_Values.Look(ref arsonJusticeEnabled, "arsonJusticeEnabled", true);
            Scribe_Values.Look(ref flameHarvestEnabled, "flameHarvestEnabled", true);

            Scribe_Values.Look(ref furnaceBedIgnitionChance, "furnaceBedIgnitionChance", PyrelandsTuning.FurnaceBedIgnitionChance);
            Scribe_Values.Look(ref fireHawkCooldownTicks, "fireHawkCooldownTicks", PyrelandsTuning.FireHawkCooldownTicks);
            Scribe_Values.Look(ref arsonDebtRaidThreshold, "arsonDebtRaidThreshold", PyrelandsTuning.ArsonDebtRaidThreshold);
            Scribe_Values.Look(ref flameHarvestMinFires, "flameHarvestMinFires", PyrelandsTuning.FlameHarvestMinFires);
            Scribe_Values.Look(ref furnaceAuraRadius, "furnaceAuraRadius", PyrelandsTuning.FurnaceAuraRadius);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("The standing burn");
            list.CheckboxLabeled("The biome re-seeds its own burn", ref standingBurnReseedEnabled,
                "Off: if every fire on a Pyrelands map goes out, it stays out — the biome "
              + "no longer lights a fresh smoulder after two quiet days.");
            list.GapLine();

            list.Label("The fire-hawk's twig");
            list.CheckboxLabeled("Fire-hawks carry embers", ref fireHawkSpreadEnabled,
                "Off: fire-hawks never spread fire from an existing burn (they still can't "
              + "start one from nothing either way).");
            list.Label("Cooldown between sorties: " + (fireHawkCooldownTicks / 2500f).ToString("0.0") + " in-game hours");
            fireHawkCooldownTicks = Mathf.RoundToInt(list.Slider(fireHawkCooldownTicks / 2500f, 0.5f, 24f) * 2500f);
            list.GapLine();

            list.Label("The furnace-beast's thermal circuit");
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
            list.GapLine();

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
