using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// WASTELAND_RADIOTHERMAL_SOLITARY_1. Plain vanilla CompHeatPusher
    /// (RimSage-verified against RimWorld 1.6's own Source/Verse/
    /// CompHeatPusher.cs: it reads only Thing-level members —
    /// SpawnedOrAnyParentSpawned, AmbientTemperature, PositionHeld,
    /// MapHeld — nothing Building-only, so it attaches cleanly to a Pawn
    /// ThingDef with no bespoke comp needed) with two things added: a mod
    /// settings gate, so this kit's "every mod ships superb Mod Settings"
    /// rule covers a pawn that pushes ambient heat the same way it covers
    /// every other mechanism in this assembly; and no rare-tick push on a
    /// pawn, which runs CompTick AND CompTickRare and would heat twice.
    ///
    ///   <comps>
    ///     <li Class="CompProperties_HeatPusher">
    ///       <compClass>RimMandrake.CreatureBehaviors.RM_CompHeatPusherGated</compClass>
    ///       <heatPerSecond>30</heatPerSecond>
    ///       <heatPushMaxTemperature>24</heatPushMaxTemperature>
    ///     </li>
    ///   </comps>
    /// </summary>
    public class RM_CompHeatPusherGated : CompHeatPusher
    {
        // HEATPUSHER_FIX_PAWN_DOUBLE_PUSH: vanilla CompHeatPusher pushes from BOTH CompTick (every 60) and CompTickRare
        // (x4.17 per 250), assuming a thing runs one ticker. A pawn runs both (Pawn.Tick calls TickRare at hash 250), so
        // the rare push would double the heat. CompTick alone is the full heatPerSecond.
        public override void CompTickRare()
        {
            if (parent is Pawn)
            {
                return;
            }
            base.CompTickRare();
        }

        public override bool ShouldPushHeatNow => RM_CreatureBehaviorsSettings.ambientHeatPusherEnabled && base.ShouldPushHeatNow;
    }
}
