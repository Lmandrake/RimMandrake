using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // Owner ruling 2026-10-15, by card (Transient/phase0_p3_questions.md Q1): "Both twitch". Design:
    // design/RimMandrake/tentacle_twitch_design_2026-10-15.md.
    //
    // The twitch itself is vanilla (Verse.PawnRenderNodeProperties_Spastic). What vanilla lacks is a way to size an
    // animal's attachment nodes by its life stage: a node's size comes from its props (drawSize, drawData.scale), never
    // from PawnKindLifeStage.bodyGraphicData.drawSize, so a baby zhool would wear an adult's tentacles.
    //
    // This hooks the engine's own PawnRenderSubWorker point (PawnRenderNodeProperties.subworkerClasses; called by
    // PawnRenderNode.GetTransform after the worker) and multiplies the node's scale by
    //     current life stage body drawSize / adult (last) life stage body drawSize.
    // Put it on an invisible parent node: PawnRenderTree.TryGetMatrix composes every ancestor's transform, so the
    // children's sizes AND their attach offsets shrink together about the parent's origin.
    //
    //   <li>
    //     <debugLabel>TentacleRig</debugLabel>
    //     <useGraphic>false</useGraphic>
    //     <subworkerClasses><li>RimMandrake.EnvironmentalHazards.PawnRenderSubWorker_KindLifeStageScale</li></subworkerClasses>
    //     <children> ... the twitching nodes, positioned for the ADULT ... </children>
    //   </li>
    //
    // Factor 1 (no change) whenever the answer is not knowable: no kind, fewer than two life stages, a stage without
    // bodyGraphicData, or a non-positive adult drawSize. Reads only; allocates nothing; no state.
    public class PawnRenderSubWorker_KindLifeStageScale : PawnRenderSubWorker
    {
        public override void TransformScale(PawnRenderNode node, PawnDrawParms parms, ref Vector3 scale)
        {
            float f = FactorFor(parms.pawn);
            if (f == 1f)
            {
                return;
            }
            scale.x *= f;
            scale.z *= f;
        }

        public static float FactorFor(Pawn pawn)
        {
            List<PawnKindLifeStage> stages = pawn?.kindDef?.lifeStages;
            if (stages == null || stages.Count < 2)
            {
                return 1f;
            }
            GraphicData adult = stages[stages.Count - 1]?.bodyGraphicData;
            GraphicData current = pawn.ageTracker?.CurKindLifeStage?.bodyGraphicData;
            if (adult == null || current == null)
            {
                return 1f;
            }
            return Ratio(current.drawSize.x, adult.drawSize.x);
        }

        // Pure kernel: the scale a stage drawn at currentDrawSize gets relative to the adult's adultDrawSize.
        public static float Ratio(float currentDrawSize, float adultDrawSize)
        {
            if (!(adultDrawSize > 0f) || !(currentDrawSize > 0f))
            {
                return 1f;
            }
            return currentDrawSize / adultDrawSize;
        }
    }
}
