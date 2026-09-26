using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ShokkweaveEconomy
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Shokkweave Economy.
    //
    // Pattern copied verbatim from
    // src/RimUtinni/FungalSoilTrade/Source/FungalSoilTradeOptions.cs — this
    // mod ships one runtime mechanic in Source: GenStep_ScatterWebworkSilk,
    // which scatters the two Webwork harvest nodes (RUT_Webwork_SilkKnot,
    // RUT_Webwork_Nest) onto RUT_Webwork maps only. WORLDGEN-AFFECTING (new
    // maps only, per that GenStep's own header). Default ON — matches
    // shipped behavior.
    public class ShokkweaveEconomySettings : ModSettings
    {
        public static bool scatterEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref scatterEnabled, "scatterEnabled", true);
        }

        public void DoWindowContents(UnityEngine.Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Webwork silk nodes (affects new maps only)");
            list.CheckboxLabeled("Scatter Webwork silk knots and nests", ref scatterEnabled,
                "Off: no new RUT_Webwork map generates the harvestable silk-knot or nest "
              + "scatter groups. A map that already exists is never retroactively changed. "
              + "This does not touch the sole-source shokkweave/hyperweave campaign ruling "
              + "itself (design/Jawa/worldbuilding/biomes/the_webwork.md §6 ban 4) — it only "
              + "gates whether this mod's own map-generation step runs.");

            list.End();
        }
    }

    public class ShokkweaveEconomyMod : Mod
    {
        public static ShokkweaveEconomySettings settings;

        public ShokkweaveEconomyMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<ShokkweaveEconomySettings>();
        }

        public override string SettingsCategory() => "Shokkweave Economy";

        public override void DoSettingsWindowContents(UnityEngine.Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
