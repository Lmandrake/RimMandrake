using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_LIGHT_ECONOMY_1 §4.4. RM_WellChart: "drawn fresh by the
    // well-keeper" at the moment of purchase — the forecast text is a
    // snapshot (RM_MapComponent_WellLedger.RollForecastText(), captured
    // once here), not a live feed. "Accurate for ~a week and then it is a
    // picture of a sea that no longer exists" — the inspect text says so
    // once stale; nothing else punishes keeping one.
    public class RM_CompProperties_WellChart : CompProperties
    {
        public RM_CompProperties_WellChart()
        {
            compClass = typeof(RM_Comp_WellChart);
        }
    }

    public class RM_Comp_WellChart : ThingComp
    {
        private const int StalenessTicks = 7 * 60000;

        private int creationTick = -1;
        private string forecastText;

        public RM_CompProperties_WellChart Props => (RM_CompProperties_WellChart)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref creationTick, "rmWellChartCreationTick", -1);
            Scribe_Values.Look(ref forecastText, "rmWellChartForecastText");
        }

        public override void PostPostMake()
        {
            base.PostPostMake();
            Capture();
        }

        // Public so a future Compact dialog can re-draw the chart explicitly
        // (e.g. buying a fresh one hands over the same item re-captured)
        // rather than always minting a new ThingDef instance.
        public void Capture()
        {
            creationTick = Find.TickManager.TicksGame;
            Map map = parent.MapHeld;
            RM_MapComponent_WellLedger ledger = map != null ? RM_MapComponent_WellLedger.GetFor(map) : null;
            forecastText = ledger != null ? ledger.RollForecastText() : "RM_TwilightChart_NoData".Translate();
        }

        public bool IsStale()
        {
            return creationTick >= 0 && Find.TickManager.TicksGame - creationTick > StalenessTicks;
        }

        public override string CompInspectStringExtra()
        {
            if (creationTick < 0)
            {
                return null;
            }
            if (!RM_TerminalBiomesSettings.twilightChartsAgeEnabled)
            {
                return forecastText;
            }
            return IsStale()
                ? "RM_WellChart_Stale".Translate()
                : forecastText;
        }
    }
}
