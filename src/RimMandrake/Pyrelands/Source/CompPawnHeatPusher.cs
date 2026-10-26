using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// HEATPUSHER_FIX_PAWN_DOUBLE_PUSH: vanilla CompHeatPusher on a pawn, pushing heatPerSecond once instead of twice.
    ///
    /// Vanilla CompHeatPusher (decompiled 1.6, Verse/CompHeatPusher.cs) pushes from BOTH CompTick (heatPerSecond every
    /// 60 ticks) and CompTickRare (heatPerSecond x 4.1666 every 250 ticks), on the assumption that a thing runs only the
    /// one ticker its tickerType names. A pawn runs both: Pawn.Tick calls TickRare on hash interval 250, and
    /// ThingWithComps.TickRare calls every CompTickRare. So the furnace-beast's heatPerSecond 18 heated a room at ~36.
    /// CompTick alone is the full heatPerSecond, so on a pawn the rare push is skipped; on anything else it is vanilla.
    ///
    /// The furnace-beast's settings gate stays where it was (FurnaceWarmthField.Postfix_ShouldPushHeatNow on the
    /// CompHeatPusher getter), which this class reaches through base.ShouldPushHeatNow.
    /// </summary>
    public class CompPawnHeatPusher : CompHeatPusher
    {
        public override void CompTickRare()
        {
            if (parent is Pawn)
            {
                return;
            }
            base.CompTickRare();
        }
    }
}
