using System;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>
    /// LIQUID_BOTTLE_LOOP_1, the "use" half. Runs whenever a filled bottle
    /// is eaten/drunk by ANY route -- plain vanilla nutrition, a mod's own
    /// thirst need, a caravan meal tick -- because it hangs off
    /// IngestibleProperties.outcomeDoers, the one vanilla extension point
    /// every ingestion path already calls through Thing.Ingested. That is
    /// what "drinkable-agnostic" means in practice: this class never checks
    /// for DBH, and DBH's own drinkable registration (LIQUID_THIRST_CHAIN_1)
    /// stays free to layer its own hydration/thirst effects on the SAME
    /// ingestion without this doer knowing it exists.
    ///
    /// Same shape as the local precedent, GelatinousSlime's
    /// IngestionOutcomeDoer_SlimeDose (Source/SlimeIngestion.cs) -- a try/
    /// catch around the whole body, because an outcome doer throwing must
    /// never turn "drank a bottle" into a stuck job.
    ///
    /// Only wired onto bottled rows with a thirstQuality set (fresh/salt/
    /// toxic/brine water, generate_liquid_suite.py's own gate) -- boiling,
    /// icy, acid, tar and propane bottles carry no ingestible block at all,
    /// so this class is never called for them. "Use" for those (revert-on-
    /// bottle, industrial consumption) is separate, unbuilt work, not a case
    /// this doer silently mishandles.
    /// </summary>
    public class IngestionOutcomeDoer_BottleResidue : IngestionOutcomeDoer
    {
        protected override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
        {
            try
            {
                if (pawn == null || ingested?.def == null)
                {
                    return;
                }
                RM_BottledLiquidExtension ext = ingested.def.GetModExtension<RM_BottledLiquidExtension>();
                if (ext == null || ext.liquid == null)
                {
                    // Not one of our bottles, or a bottle def with no
                    // recorded content (should never happen -- a filled
                    // bottle always carries `liquid`) -- leave nothing
                    // behind rather than guess.
                    return;
                }

                ThingDef residueDef = RimMandrakeFlowWorksSettings.bottleDirtyStageEnabled
                    ? RimMandrakeFlowWorks_DefOf.RM_BottleDirty
                    : RimMandrakeFlowWorks_DefOf.RM_BottleEmpty;
                if (residueDef == null)
                {
                    return;
                }

                Map map = pawn.MapHeld;
                if (map == null)
                {
                    return;
                }

                Thing residue = ThingMaker.MakeThing(residueDef);
                residue.stackCount = Math.Max(1, ingestedCount);

                if (pawn.Spawned && pawn.inventory != null
                    && pawn.inventory.innerContainer.TryAdd(residue))
                {
                    return;
                }
                GenPlace.TryPlaceThing(residue, pawn.PositionHeld, map, ThingPlaceMode.Near);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.FlowWorks] bottle residue outcome failed: " + e.Message, 0x8077E5);
            }
        }
    }
}
