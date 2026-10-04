using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlameStatues
{
    // FLAME_STATUES_MOD_BUILD_1 — Mod Settings, statue_mods_spec.md §2.4. Defaults = shipped behaviour.
    // All off = plain sculptures with our art. The Helixien row arrives with step 7.
    public class FlameStatuesSettings : ModSettings
    {
        public static bool flamePoints = true;
        public static bool flecks = true;
        public static bool consumeFuel = true;
        public static bool qualityScaling = true;
        public static bool glow = true;
        public static float consumptionMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref flamePoints, "flamePoints", true);
            Scribe_Values.Look(ref flecks, "flecks", true);
            Scribe_Values.Look(ref consumeFuel, "consumeFuel", true);
            Scribe_Values.Look(ref qualityScaling, "qualityScaling", true);
            Scribe_Values.Look(ref glow, "glow", true);
            Scribe_Values.Look(ref consumptionMultiplier, "consumptionMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);
            list.CheckboxLabeled("Flames drawn", ref flamePoints,
                "On: a fuelled flame statue burns at every vent its carving has (palms, crown, shoulders). "
              + "Off: no flames are drawn and the statue does not light the room. Takes effect at once.");
            list.CheckboxLabeled("Fire-glow sparks", ref flecks,
                "On: burning vents throw small glowing puffs now and then. Off: flames only. Takes effect at once.");
            list.CheckboxLabeled("Statues use fuel", ref consumeFuel,
                "On: flame statues burn chemfuel and go dark when empty. Off: statues never run out. "
              + "Takes effect at once.");
            list.CheckboxLabeled("Better carving, bigger fire", ref qualityScaling,
                "On: an awful statue burns at half size, a legendary one at double, with sparks to match. "
              + "Off: every statue burns the same. Takes effect at once.");
            list.CheckboxLabeled("Statues light the room", ref glow,
                "On: a burning statue casts warm light. Off: flames are drawn but cast no light. "
              + "Takes effect within a few seconds.");
            list.Label("Fuel use: " + consumptionMultiplier.ToStringPercent(), -1f,
                new TipSignal("How fast flame statues burn fuel, against the shipped rate. Takes effect after a restart."));
            consumptionMultiplier = list.Slider(consumptionMultiplier, 0.25f, 4f);
            list.End();
        }
    }

    public class FlameStatuesMod : Mod
    {
        public static FlameStatuesSettings settings;

        public FlameStatuesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<FlameStatuesSettings>();
        }

        public override string SettingsCategory()
        {
            return "Flame Statues";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }

    /// <summary>Applies the fuel-use multiplier to every def carrying flame points (CompRefuelable reads its
    /// props' rate directly, so it is scaled once at startup).</summary>
    [StaticConstructorOnStartup]
    public static class FlameStatuesStartup
    {
        public static readonly List<string> Scaled = new List<string>();

        static FlameStatuesStartup()
        {
            float m = Mathf.Clamp(FlameStatuesSettings.consumptionMultiplier, 0.25f, 4f);
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (d.GetCompProperties<RM_CompProperties_FlamePoints>() == null)
                {
                    continue;
                }
                CompProperties_Refuelable fuel = d.GetCompProperties<CompProperties_Refuelable>();
                if (fuel == null)
                {
                    continue;
                }
                if (!Mathf.Approximately(m, 1f))
                {
                    fuel.fuelConsumptionRate *= m;
                }
                Scaled.Add(d.defName);
            }
            if (!Mathf.Approximately(m, 1f))
            {
                Log.Message("[FlameStatues] fuel use x" + m.ToString("0.##") + " on " + Scaled.Count + " statue def(s).");
            }
        }
    }
}
