using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.FungalSoilTrade
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Fungal Soil Trade.
    //
    // Named *Options*Mod rather than *FungalSoilTradeMod* on purpose: that
    // name is already taken by the [StaticConstructorOnStartup] Harmony
    // bootstrap class in MapComponent_RotFungalDistress.cs.
    //
    // Gates the two real runtime mechanics found in this mod's Source:
    //   1. GenStep_ScatterFungalGround — WORLDGEN-AFFECTING (new maps only):
    //      whether a Rot map generates mineable fungal soil at all.
    //   2. MapComponent_RotFungalDistress — the distress-and-defenders loop
    //      that fires when a player mines that soil; master on/off plus the
    //      build/decay rate constants as sliders, defaults = shipped values.
    public class FungalSoilTradeSettings : ModSettings
    {
        public static bool scatterEnabled = true;
        public static bool distressEnabled = true;
        public static float distressBuildRateMultiplier = 1f;
        public static float distressDecayRateMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref scatterEnabled, "scatterEnabled", true);
            Scribe_Values.Look(ref distressEnabled, "distressEnabled", true);
            Scribe_Values.Look(ref distressBuildRateMultiplier, "distressBuildRateMultiplier", 1f);
            Scribe_Values.Look(ref distressDecayRateMultiplier, "distressDecayRateMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Fungal ground on the Rot (affects new maps only)");
            list.CheckboxLabeled("Scatter mineable fungal ground", ref scatterEnabled,
                "Off: no new Rot (Mycotic Jungle) map generates fungal soil knots to dig. "
              + "A map that already exists is never retroactively changed.");
            list.GapLine();

            list.Label("Fungal distress (mining the Rot's soil)");
            list.CheckboxLabeled("Distress and defenders enabled", ref distressEnabled,
                "Off: digging fungal soil never angers the mycelial network — no distress builds "
              + "and nothing is ever summoned to defend it.");
            if (distressEnabled)
            {
                list.Label("Distress build rate: " + distressBuildRateMultiplier.ToString("0.00") + "x");
                list.Label("How fast digging fungal soil builds distress toward a defender response.");
                distressBuildRateMultiplier = list.Slider(distressBuildRateMultiplier, 0f, 3f);

                list.Label("Distress decay rate: " + distressDecayRateMultiplier.ToString("0.00") + "x");
                list.Label("How fast distress fades away once digging stops.");
                distressDecayRateMultiplier = list.Slider(distressDecayRateMultiplier, 0.25f, 3f);
            }

            list.End();
        }
    }

    public class FungalSoilTradeOptionsMod : Mod
    {
        public static FungalSoilTradeSettings settings;

        public FungalSoilTradeOptionsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<FungalSoilTradeSettings>();
        }

        public override string SettingsCategory() => "Fungal Soil Trade";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
