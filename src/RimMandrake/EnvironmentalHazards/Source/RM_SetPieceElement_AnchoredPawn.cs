using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M6 build (miasma_kit_spec.md M6): spawns "one
    // warden-mother pawn" and calls RM_CompTerritorialAnchor.SetAnchor() on
    // it. Built GENERICALLY per this item's own instruction: pawnKind is an
    // XML field, never hardcoded, since sump_kit_spec.md's own S3 (tar-
    // beast placement) names RM_GenStep_PlacedSetPieces as its identical
    // hard prerequisite and may want this exact "spawn a pawn and anchor it
    // to the site" shape for its own dormant beast — confirmed not already
    // built anywhere: SUMP_MECHANICS_1.md's own S1 spike pass explicitly
    // says S3/S4 are "BLOCKED on RM_GenStep_PlacedSetPieces, confirmed
    // still unbuilt" as of this same day, so this is genuinely the first
    // build of the shape, not a duplicate.
    //
    // Faction is always null (true wildlife) — matches the spec's own "zero
    // biome wild-spawn commonality; the GenStep is their only entry."
    public class RM_SetPieceElement_AnchoredPawn : RM_SetPieceElement
    {
        public PawnKindDef pawnKind;

        // Optional. When set, the spawned pawn anchors to whichever Thing
        // of this def is found at `loc` (typically a marker element listed
        // earlier in the same GenStepDef's `elements`, sharing the same
        // scattered site) — anchoring to the actual Thing, not just its
        // cell, is what lets RM_CompTerritorialAnchor.Notify_Killed later
        // reach that Thing's own comps (the despoiled-memory mechanic reads
        // this). When null/not found, the pawn still anchors to `loc`
        // itself (a valid LocalTargetInfo), same functional radius, just
        // with no Thing for a death-listener comp to be found on.
        public ThingDef anchorMarkerDef;

        public override void SpawnAt(IntVec3 loc, Map map, GenStepParams parms)
        {
            if (pawnKind == null)
            {
                Log.Error("[RM EnvironmentalHazards] RM_SetPieceElement_AnchoredPawn has no pawnKind "
                    + "configured — spawning nothing at " + loc + ".");
                return;
            }

            PawnGenerationRequest request = new PawnGenerationRequest(
                pawnKind,
                null,
                PawnGenerationContext.NonPlayer,
                forceGenerateNewPawn: true,
                canGeneratePawnRelations: false);
            Pawn pawn = PawnGenerator.GeneratePawn(request);
            GenSpawn.Spawn(pawn, loc, map);

            RM_CompTerritorialAnchor anchorComp = pawn.TryGetComp<RM_CompTerritorialAnchor>();
            if (anchorComp == null)
            {
                // Expected, not a bug: a placeholder PawnKindDef wired in
                // ahead of the roster pass (this item's own explicit scope
                // line — "the warden/juvenile PawnKindDefs are roster
                // content ... this kit ships the scatterer and the marker")
                // does not carry CompProperties_TerritorialAnchor. The real
                // warden ThingDef the roster pass authors is what adds it.
                Log.WarningOnce(
                    "[RM EnvironmentalHazards] RM_SetPieceElement_AnchoredPawn spawned " + pawnKind.defName
                    + " with no RM_CompTerritorialAnchor comp — it will not stay anchored to " + loc
                    + " (expected for a wiring-placeholder PawnKindDef; the real content's ThingDef must "
                    + "carry CompProperties_TerritorialAnchor).",
                    pawnKind.shortHash ^ 0x4E1C);
                return;
            }

            LocalTargetInfo anchorTarget = new LocalTargetInfo(loc);
            if (anchorMarkerDef != null)
            {
                List<Thing> here = loc.GetThingList(map);
                for (int i = 0; i < here.Count; i++)
                {
                    if (here[i].def == anchorMarkerDef)
                    {
                        anchorTarget = new LocalTargetInfo(here[i]);
                        break;
                    }
                }
            }

            anchorComp.SetAnchor(anchorTarget);
        }
    }
}
