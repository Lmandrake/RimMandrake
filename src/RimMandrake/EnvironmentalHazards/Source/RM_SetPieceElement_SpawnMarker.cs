using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M6 build (miasma_kit_spec.md M6): "a named area
    // marker (RUT_CrecheMarker invisible building holding the site
    // identity; gives the 'mapped and named' ground)". Generic on the
    // marker ThingDef itself (not hardcoded to RUT_CrecheMarker) for the
    // same reason RM_SetPieceElement_AnchoredPawn is generic on
    // PawnKindDef: sump_kit_spec.md's own S3 (tar-beast placement) names
    // the identical shared scatterer as its hard prerequisite and may want
    // its own marker Thing spawned the same way.
    public class RM_SetPieceElement_SpawnMarker : RM_SetPieceElement
    {
        public ThingDef markerDef;

        public override void SpawnAt(IntVec3 loc, Map map, GenStepParams parms)
        {
            if (markerDef == null)
            {
                Log.Error("[RM EnvironmentalHazards] RM_SetPieceElement_SpawnMarker from def "
                    + "(no defName available on this element type) has no markerDef configured — "
                    + "spawning nothing at " + loc + ".");
                return;
            }

            Thing marker = ThingMaker.MakeThing(markerDef);
            GenSpawn.Spawn(marker, loc, map);
        }
    }
}
