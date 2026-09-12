using Verse;

namespace RimMandrake.CreatureBehaviors
{
    public class RM_CompProperties_SenseWebNode : CompProperties
    {
        public RM_CompProperties_SenseWebNode()
        {
            compClass = typeof(RM_CompSenseWebNode);
        }
    }

    // WEBWORK_KIT_BUILD_1, mechanic 1 (webwork_kit_spec.md §1) — attach to any
    // web/anchor/gutter ThingDef to register/deregister its occupied cells
    // with the map's RM_MapComponent_SenseWeb. Registration is unconditional
    // (cheap dictionary bookkeeping); the mod-option gate lives in the
    // MapComponent's own scan, so toggling the option mid-game never leaves a
    // node stuck half-registered.
    //
    // Destroying or despawning the parent Thing automatically deregisters it
    // here via PostDeSpawn — this is the mechanism spec §5 calls "chewing
    // genuinely blinds the web locally": no explicit notify from
    // RM_JobGiver_ChewAnchors is needed, the comp lifecycle already does it.
    public class RM_CompSenseWebNode : ThingComp
    {
        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            Map map = parent.Map;
            if (map == null)
            {
                return;
            }
            RM_MapComponent_SenseWeb senseWeb = map.GetComponent<RM_MapComponent_SenseWeb>();
            senseWeb?.RegisterNode(parent);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            RM_MapComponent_SenseWeb senseWeb = map?.GetComponent<RM_MapComponent_SenseWeb>();
            senseWeb?.DeregisterNode(parent);
            base.PostDeSpawn(map, mode);
        }
    }
}
