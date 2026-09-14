using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FORGE_MECHANICS_1 F1 build pass (forge_kit_spec.md "F1. The closed
    // boiling rain" / "flash-interval growth"). Generic, reusable shape
    // (same posture as RM_MapComponent_GradientAxis): records one active
    // window [windowStartTick, windowEndTick) and answers InFlashWindow()
    // for any consumer. RM_GameCondition_WeatherPulse is the one writer
    // (calls StartWindow at burst start); RUT_Plant_FlashFlora is the
    // Forge's own reader, but nothing in this file names the Forge.
    //
    // Every RimWorld map auto-instantiates every MapComponent subclass that
    // has a (Map) constructor (Verse/Map.cs's FillComponents, confirmed
    // this pass against the decompile) — no Def or XML wiring needed for
    // the component itself. A map whose biome never attaches
    // RM_GameCondition_WeatherPulse simply never gets StartWindow called,
    // and InFlashWindow() answers false forever, which is the correct
    // "nothing here uses this" answer.
    public class RM_MapComponent_FlashCycle : MapComponent
    {
        private int windowStartTick = -1;
        private int windowEndTick = -1;

        public RM_MapComponent_FlashCycle(Map map)
            : base(map)
        {
        }

        // Called by a burst-driving condition at burst start. durationTicks
        // is the WHOLE flash window's own length (may outlast the burst
        // weather itself — see WeatherPulseExtension.
        // flashWindowHoursAfterBurstStart), not the burst weather's own,
        // shorter duration.
        public void StartWindow(int startTick, int durationTicks)
        {
            windowStartTick = startTick;
            windowEndTick = startTick + (durationTicks < 1 ? 1 : durationTicks);
        }

        public bool InFlashWindow()
        {
            if (windowStartTick < 0 || Find.TickManager == null)
            {
                return false;
            }

            int now = Find.TickManager.TicksGame;
            return now >= windowStartTick && now < windowEndTick;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref windowStartTick, "flashWindowStartTick", -1);
            Scribe_Values.Look(ref windowEndTick, "flashWindowEndTick", -1);
        }
    }
}
