using RimWorld;
using Verse;

namespace RimMandrake.TheForge
{
    // FORGE_CYCLE_MECHANICS_1 — the sealed look (the dhokkur as a hill of
    // banked obsidian, the dhuvvox as an ash nodule).
    //
    // Vanilla already has a per-state body graphic: PawnKindLifeStage.
    // stationaryGraphicData, served by PawnRenderNode_AnimalPart_Body.
    // StateGraphicsFor under GraphicStateDefOf.Stationary. Stock
    // PawnRenderNodeWorker_AnimalBody picks that state whenever the pawn is
    // simply not moving (Pawn.DrawNonHumanlikeStationaryGraphic), which is
    // wrong here — an awake dhokkur standing still must not turn into a
    // hill. This worker narrows it: Stationary only while
    // RM_CompForgeCycleDormancy reports the pawn sealed, the normal body
    // otherwise. Read per draw (PawnRenderNodeWorker.GetGraphic), so no cache
    // to invalidate beyond the comp's own SetAllGraphicsDirty.
    public class RM_PawnRenderNodeWorker_DormantBody : PawnRenderNodeWorker_AnimalBody
    {
        protected override GraphicStateDef GetGraphicState(PawnRenderNode node, PawnDrawParms parms)
        {
            GraphicStateDef state = base.GetGraphicState(node, parms);
            Pawn pawn = parms.pawn;
            RM_CompForgeCycleDormancy dormancy = pawn != null ? pawn.TryGetComp<RM_CompForgeCycleDormancy>() : null;
            bool sealedNow = dormancy != null && dormancy.IsSealed && !pawn.Dead;

            if (sealedNow && node.tree.currentAnimation == null && pawn.ageTracker.CurKindLifeStage.stationaryGraphicData != null)
            {
                return GraphicStateDefOf.Stationary;
            }
            if (state == GraphicStateDefOf.Stationary)
            {
                // Standing still while awake: the ordinary body.
                return null;
            }
            return state;
        }
    }
}
