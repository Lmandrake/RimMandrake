// SUMP_SINKING_RITE_BUILD_1: the dig-find rider's counter. A dig-find Sinking sets it to the configured trap count; each
// trap roll on this map's RM_CompWorkedLottery shafts while it is above zero fizzles instead of arming (SinkingPatches.cs).
using Verse;

namespace RimMandrake.Utinni.Rites
{
    public class MapComponent_SinkingTraps : MapComponent
    {
        private int remaining;

        public MapComponent_SinkingTraps(Map map) : base(map) { }

        public static MapComponent_SinkingTraps For(Map map) => map?.GetComponent<MapComponent_SinkingTraps>();

        public int Remaining => remaining;

        public void Set(int count) { remaining = count < 0 ? 0 : count; }

        /// <summary>True when this trap roll fizzles (and spends one charge).</summary>
        public bool TryFizzle()
        {
            return SinkingKernel.FizzleTrap(ref remaining, RM_NinefoldSettings.sinkingTrapFizzleEnabled);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref remaining, "sinkingTrapsRemaining", 0);
        }
    }
}
