using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// WASTELAND_RADIOTHERMAL_SOLITARY_1. Plain vanilla CompHeatPusher
    /// (RimSage-verified against RimWorld 1.6's own Source/Verse/
    /// CompHeatPusher.cs: it reads only Thing-level members —
    /// SpawnedOrAnyParentSpawned, AmbientTemperature, PositionHeld,
    /// MapHeld — nothing Building-only, so it attaches cleanly to a Pawn
    /// ThingDef with no bespoke comp needed) with one thing added: a mod
    /// settings gate, so this kit's "every mod ships superb Mod Settings"
    /// rule covers a pawn that pushes ambient heat the same way it covers
    /// every other mechanism in this assembly.
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
        public override bool ShouldPushHeatNow => RM_CreatureBehaviorsSettings.ambientHeatPusherEnabled && base.ShouldPushHeatNow;
    }
}
