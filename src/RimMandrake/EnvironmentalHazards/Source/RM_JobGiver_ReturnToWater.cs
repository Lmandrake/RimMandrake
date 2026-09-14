using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M3 build (miasma_kit_spec.md M3: "stranded creatures
    // path toward the nearest channel when their pool drops below a size
    // threshold — a simple JobGiver (return-to-water) on the stranded
    // kinds"). This item's own M3 assignment: "Attempt this for real" — this
    // IS the real job, not a stub; RM_MapComponent_StrandingPools' own
    // despawn-at-pool-death fallback only ever catches what this JobGiver
    // could not resolve before a pool fully dried.
    //
    // Same shape as this repo's own RM_JobGiver_SeekShade /
    // RM_JobGiver_SeekMarkedTerrain (CreatureBehaviors): inserted GLOBALLY
    // for every animal in the game via RM_ThinkTree_StrandingBehaviors's
    // insertTag="Animal_PreMain" (vanilla's own Verse.AI.
    // ThinkNode_SubtreesByTag extension point, that file's own header
    // already verifies the mechanism) rather than wired into any specific
    // PawnKindDef's own ThinkTreeDef — required here specifically because
    // M3's placeholder spawn uses an EXISTING, unmodified shipped
    // PawnKindDef (see RUT_Miasma.xml's own comment) whose ThinkTreeDef this
    // item must not touch. TryGiveJob below no-ops instantly for the
    // overwhelming majority of pawns — anyone RM_MapComponent_
    // StrandingPools.TryGetPoolFor does not recognize as a tracked stranded
    // occupant, which is every pawn this mechanism never spawned.
    public class RM_JobGiver_ReturnToWater : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_EnvironmentalHazardsSettings.strandingPoolsEnabled)
            {
                return null;
            }

            Map map = pawn.Map;
            if (map == null)
            {
                return null;
            }

            RM_MapComponent_StrandingPools pools = map.GetComponent<RM_MapComponent_StrandingPools>();
            if (pools == null || !pools.TryGetPoolFor(pawn, out RM_StrandingPool pool))
            {
                return null;
            }

            RM_StrandingPoolsExtension ext = map.Biome != null ? map.Biome.GetModExtension<RM_StrandingPoolsExtension>() : null;
            if (ext == null || pool.cells.Count > ext.poolSizeThreshold)
            {
                return null; // pool still healthy — no rush yet (or config missing entirely)
            }

            if (!pools.TryFindNearestChannelCell(pawn, ext.searchRadius, out IntVec3 target))
            {
                return null; // no reachable channel within range — the decay-side despawn fallback covers this
            }

            return JobMaker.MakeJob(JobDefOf.Goto, target);
        }
    }
}
