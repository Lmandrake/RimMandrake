using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.LanternDeeps
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Lantern Deeps.
    //
    // The mod's only runtime mechanism is GenStep_ScatterCavePortal, a
    // WORLDGEN-AFFECTING step (new maps only): it scatters a Lantern Deep
    // cave-mouth onto a qualifying ≤ -40°C biome at a flat per-map chance
    // (LANTERN_DEEPS_INJECTION_1's own comment: "FOUNDRY's placeholder pick
    // pending the owner's actual density call"). Exposed here as a master
    // toggle plus a multiplier on that chance, default 1x = shipped rate.
    public class LanternDeepsSettings : ModSettings
    {
        public static bool emergenceEnabled = true;
        public static float emergenceChanceMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref emergenceEnabled, "emergenceEnabled", true);
            Scribe_Values.Look(ref emergenceChanceMultiplier, "emergenceChanceMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Lantern Deep emergence (affects new maps only)");
            list.CheckboxLabeled("Cave portal can emerge", ref emergenceEnabled,
                "Off: no new map on a qualifying deep-cold biome ever grows a Lantern Deep mouth. "
              + "A map that already exists is never retroactively changed.");
            if (emergenceEnabled)
            {
                list.Label("Emergence chance: " + emergenceChanceMultiplier.ToString("0.00")
                    + "x the base rate (shipped default: 8% of qualifying maps)");
                emergenceChanceMultiplier = list.Slider(emergenceChanceMultiplier, 0f, 3f);
            }

            list.End();
        }
    }

    public class LanternDeepsMod : Mod
    {
        public static LanternDeepsSettings settings;

        public LanternDeepsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<LanternDeepsSettings>();
        }

        public override string SettingsCategory() => "Lantern Deeps";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
